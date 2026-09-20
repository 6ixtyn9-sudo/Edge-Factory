"""ml-fade research capture ledger — certification-independent evidence accrual.

This module implements the RESEARCH-ONLY capture ledger for the ml-meta /
ml-fade rule families. Its contract, in one place:

- INDEPENDENT OF CERTIFICATION. Rows are recorded for EVERY fixture the
  serve-time meta-model scores, whether or not any ml-meta/ml-fade rule is
  certified. Nothing here touches ``edges_consensus.json``, operational
  buckets, notifications, or auto-tickets.
- BET-TIME PROPERTIES. A row is frozen at FIRST capture: the parent
  selection, ``ml_p``, the derived fade selection, and the pre-match 1X2
  source quotes (forebet/zulubet) at capture time. Later re-runs may only
  refresh observational fields (``last_seen_at``, latest observed quotes,
  ``repriced_count``) — never the first-seen (bet-time) quote or the
  prediction itself.
- STABLE IDENTITY. Every row carries an ``event_key``
  ``date|norm_home|norm_away|family|market`` built with the operational
  accent-safe team key. Re-running the pipeline NEVER duplicates rows;
  parent (``ml-meta``) and fade (``ml-fade``) rows are distinct ledger
  entries for the same fixture, mirroring the operational ledger doctrine.
- DETERMINISTIC DERIVATION. The fade selection is the binary 1X2 inverse
  (home<->away, see edgefactory/fade.py); draw parents are excluded
  explicitly and counted. No inverse is invented, ever.
- FAIL-CLOSED SETTLEMENT. Rows settle only against the tracked
  ``settled_results.json`` facts with exact (or alias-confirmed) identity
  and a bounded date window. Conflicting or ambiguous outcomes move the row
  to a loud ``conflict`` status — never a guessed win/loss. Fixtures whose
  result never arrives age into ``unmatched`` (visible staleness), which is
  also never scored as a loss (or a win). Missing opposing-side prices stay
  missing (they are excluded from priced statistics, not scored).
- MODEL PROVENANCE. Each row records ``model_key`` (a hash of the serving
  model payload: coef/intercept/feature_cols) and every model key it was
  observed under. The frozen feature-serving method is checked against the
  pipeline's checkpoint-⑫ contract: any drift is surfaced loudly and the
  checkpoint report flags affected rows.

Persistence: the ledger is written to ``localdata/ml_fade_research_ledger.json``,
which is git-tracked (see .gitignore negation) so the bot's "persist pipeline
state" step commits it after every run — the single source of truth survives
cache eviction and runner replacement.
"""

from __future__ import annotations

import hashlib
import json
import math
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

_LOCAL_TZ = ZoneInfo("Africa/Johannesburg")

from edgefactory.fade import (
    DERIVATION,
    FADE_FAMILY,
    PARENT_FAMILY,
    fade_avg_p,
    fade_odds_column,
    inverse_selection,
)
from edgefactory.util import fold_ascii, ledger_team_key

SCHEMA = 1

LEDGER_NAME = "ml_fade_research_ledger.json"
STATE_NAME = "ml_fade_research_state.json"

MARKET = "1x2"

# ---------------------------------------------------------------------------
# Row status lifecycle. pending rows are pre-kickoff captures awaiting a
# result fact; settled rows are frozen forever; conflict rows carry two or
# more contradictory result claims and require human attention (never
# silently resolved); unmatched rows exhausted the staleness horizon with no
# result fact (postponed/void/vanished) and are excluded from win/loss stats.
STATUS_PENDING = "pending"
STATUS_SETTLED = "settled"
STATUS_CONFLICT = "conflict"
STATUS_UNMATCHED = "unmatched"

# Settlement tolerances (fixed, predeclared): a settled fact may sit up to
# N days from the captured fixture date (minor date-shift across sources);
# rows with no fact after M days are unmatched.
DEFAULT_DATE_WINDOW_DAYS = 3
DEFAULT_UNMATCHED_AFTER_DAYS = 21

# The pipeline's frozen ml-meta serve-time method (checkpoint ⑫ contract):
# the model is served with ht_diff/ht_total pinned to 0 pre-match. The
# capture path builds its feature vector the same way; a registry model whose
# feature set no longer matches this contract invalidates comparability of
# historical rows — surfaced as drift, never silently adopted.
FROZEN_FEATURE_COLS = (
    "fb_p",
    "zb_p",
    "sa_p",
    "avg_p",
    "min_p",
    "std_p",
    "pick_odds",
    "is_home",
    "is_away",
    "cat_friendly",
    "cat_youth",
    "cat_women",
    "cat_cup",
    "cat_league",
    "rolling_hit_rate",
    "ht_p",
    "ht_diff",
    "ht_total",
    "kelly",
    "pred_total",
    "pred_diff",
    "goalsavg",
    "p_ng",
    "p_under",
    "sa_ht_p",
    "p_gg",
)

# Immutable (bet-time) fields: merge may never overwrite these once set.
IMMUTABLE_FIELDS = (
    "event_key",
    "family",
    "date",
    "market",
    "sport",
    "league",
    "home",
    "away",
    "kickoff",
    "first_seen_at",
    "captured_at",
    "parent_family",
    "edge_family",
    "derivation",
    "parent_pick",
    "parent_ml_p",
    "parent_avg_p",
    "pick",
    "ml_p",
    "avg_p",
    "w_score",
    "first_odds_forebet",
    "first_odds_zulubet",
    "odds_source",
    "ml_ht_diff",
    "ml_ht_total",
    "sources_used",
    "sources_present",
)


# ---------------------------------------------------------------------------
# Model identity
# ---------------------------------------------------------------------------


def canonical_model_payload(model: dict | None) -> str:
    """Canonical serialization of a registry ml_model payload for hashing."""
    return json.dumps(model or {}, sort_keys=True, separators=(",", ":"), default=str)


def model_key(model: dict | None) -> str | None:
    """Short stable identity of the serving model (coef/intercept/features)."""
    if not model:
        return None
    return hashlib.sha256(canonical_model_payload(model).encode()).hexdigest()[:12]


def detect_model_drift(model: dict | None) -> dict:
    """Drift of the serving model against the frozen research method.

    Returns {drifted: bool, reasons: [...]}. Drift does NOT stop capture (the
    whole point of the ledger is to record what the model actually did), but
    it is surfaced loudly and recorded on the ledger state.
    """
    reasons: list[str] = []
    if not model:
        reasons.append("registry ml_model missing — no serve-able model")
        return {"drifted": True, "reasons": reasons, "model_key": None}
    cols = tuple(model.get("feature_cols") or ())
    missing = [c for c in FROZEN_FEATURE_COLS if c not in cols]
    extra = [c for c in cols if c not in FROZEN_FEATURE_COLS]
    reordered = (
        not missing
        and not extra
        and [c for c in FROZEN_FEATURE_COLS if c in cols]
        != [c for c in cols if c in FROZEN_FEATURE_COLS]
    )
    if missing:
        reasons.append(f"feature_cols missing frozen features: {missing}")
    if extra:
        reasons.append(f"feature_cols adds features beyond frozen method: {extra}")
    if reordered:
        reasons.append("feature_cols order changed vs frozen serving method")
    return {"drifted": bool(reasons), "reasons": reasons, "model_key": model_key(model)}


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def event_key(family: str, date_str: str, home: str, away: str, market: str = MARKET) -> str | None:
    """Stable event/selection identity, or None when identity is unusable.

    Fail-closed: a fixture without both team keys can never be ledgered.
    """
    hk = ledger_team_key(home or "")
    ak = ledger_team_key(away or "")
    if not hk or not ak or hk == ak:
        return None
    return f"{date_str}|{hk}|{ak}|{family}|{market}"


def _row_event_key(row: dict) -> str | None:
    return event_key(
        row.get("family") or "",
        row.get("date") or "",
        row.get("home") or "",
        row.get("away") or "",
        row.get("market") or MARKET,
    )


# ---------------------------------------------------------------------------
# Capture collector (serve-time)
# ---------------------------------------------------------------------------


class FadeResearchCollector:
    """Collects research candidates while the model scores fixtures.

    The collector is fed from the operational serve-time inference block with
    the exact same inputs (anchor/fb/zb rows, majority pick, ml_p, logit).
    It NEVER produces operational picks: its rows go only to the research
    ledger through ``finalize()``. Certification state plays no role — the
    collector has no access to the edge registry at all.
    """

    def __init__(self) -> None:
        self.rows: list[dict] = []
        self.scored = 0
        self.draw_excluded = 0
        self.identity_skipped = 0

    def record(
        self,
        *,
        day: str,
        anchor: dict,
        fb: dict | None,
        zb: dict | None,
        used: list[str],
        majority_pick: str,
        ml_p: float,
        z_score: float,
        model: dict | None,
        ml_ht_diff: float = 0.0,
        ml_ht_total: float = 0.0,
    ) -> None:
        """Record one model-scored fixture as parent (+fade) candidates."""
        self.scored += 1
        fb = fb or {}
        zb = zb or {}
        mkey = model_key(model)

        home = str(anchor.get("home") or "").strip()
        away = str(anchor.get("away") or "").strip()
        if not home or not away:
            self.identity_skipped += 1
            return

        base = {
            "schema": SCHEMA,
            "date": str(day),
            "market": MARKET,
            "sport": anchor.get("sport", "soccer"),
            "league": anchor.get("league"),
            "home": home,
            "away": away,
            "kickoff": anchor.get("kickoff") or anchor.get("time"),
            "sources_used": list(used or []),
            "sources_present": [s for s, r in (("forebet", fb), ("zulubet", zb)) if r],
            "model_key": mkey,
            "model_keys_seen": [mkey] if mkey else [],
            "w_score": round(float(z_score), 4),
            "ml_ht_diff": ml_ht_diff,
            "ml_ht_total": ml_ht_total,
        }

        # --- ml-meta parent candidate (the model's own selection) ---
        parent_sel = str(majority_pick or "").strip().lower()
        parent_odds_col = {"home": "odd1", "draw": "oddx", "away": "odd2"}.get(parent_sel)
        parent = dict(base)
        parent.update(
            {
                "family": PARENT_FAMILY,
                "parent_family": PARENT_FAMILY,
                "edge_family": PARENT_FAMILY,
                "derivation": None,
                "pick": parent_sel,
                "ml_p": round(float(ml_p), 4),
                "avg_p": round(float(ml_p) * 100.0, 1),
                "odds_forebet": _num(fb.get(parent_odds_col)) if parent_odds_col else None,
                "odds_zulubet": _num(zb.get(parent_odds_col)) if parent_odds_col else None,
            }
        )
        self._append(parent)

        # --- ml-fade candidate (deterministic inverse; draws excluded) ---
        fade_sel = inverse_selection(parent_sel)
        if fade_sel is None:
            self.draw_excluded += 1
            return  # explicit exclusion — never invent a 1X2 inverse
        fade_col = fade_odds_column(parent_sel)
        fade = dict(base)
        fade.update(
            {
                "family": FADE_FAMILY,
                "parent_family": PARENT_FAMILY,
                "edge_family": FADE_FAMILY,
                "derivation": DERIVATION,
                "parent_pick": parent_sel,
                "parent_ml_p": round(float(ml_p), 4),
                "parent_avg_p": round(float(ml_p) * 100.0, 1),
                "pick": fade_sel,
                "ml_p": round(1.0 - float(ml_p), 4),
                "avg_p": fade_avg_p(ml_p),
                "odds_forebet": _num(fb.get(fade_col)) if fade_col else None,
                "odds_zulubet": _num(zb.get(fade_col)) if fade_col else None,
            }
        )
        self._append(fade)

    def _append(self, row: dict) -> None:
        key = _row_event_key(row)
        if key is None:
            self.identity_skipped += 1
            return
        row["event_key"] = key
        self.rows.append(row)

    def finalize(self) -> list[dict]:
        """Dedup within the run (same fixture re-scanned intraday): FIRST wins."""
        seen: dict[str, dict] = {}
        out: list[dict] = []
        for row in self.rows:
            key = row["event_key"]
            if key in seen:
                continue
            seen[key] = row
            out.append(row)
        return out


def _num(value: object) -> float | None:
    """Parse a source odds cell; unparseable stays a visible None, never 0."""
    if value is None or value == "":
        return None
    try:
        v = float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None
    if v <= 1.0 or math.isnan(v):  # <=1.0 or NaN is not a real bookmaker quote
        return None
    return v


def _odds_source(row: dict) -> str | None:
    if row.get("odds_forebet") is not None:
        return "forebet_best"
    if row.get("odds_zulubet") is not None:
        return "zulubet"
    return None


# ---------------------------------------------------------------------------
# Ledger I/O + idempotent merge
# ---------------------------------------------------------------------------


def default_ledger_path(root: Path) -> Path:
    return root / "localdata" / LEDGER_NAME


def load_ledger(path: Path | str) -> dict:
    """Load the research ledger; a missing file is an empty v1 ledger."""
    p = Path(path)
    if not p.exists():
        return {"schema": SCHEMA, "updated_at": None, "rows": []}
    data = json.loads(p.read_text())
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError(
            f"research ledger at {p} has unexpected schema — failing closed "
            "(no silent migration of research evidence)"
        )
    if not isinstance(data.get("rows"), list):
        raise TypeError(f"research ledger at {p} is malformed (rows missing)")
    return data


def save_ledger(path: Path | str, ledger: dict, *, now: str) -> None:
    """Atomic-ish persist: temp file then replace. Deterministic ordering."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ledger = dict(ledger)
    ledger["schema"] = SCHEMA
    ledger["updated_at"] = now
    ledger["rows"] = sorted(ledger.get("rows", []), key=lambda r: r.get("event_key", ""))
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(ledger, indent=1, sort_keys=True) + "\n")
    tmp.replace(p)


class MergeStats:
    def __init__(self) -> None:
        self.added_parent = 0
        self.added_fade = 0
        self.repriced = 0
        self.observed_only = 0
        self.skipped_malformed = 0
        self.model_keys_new: list[str] = []

    def as_dict(self) -> dict:
        return {
            "added_parent": self.added_parent,
            "added_fade": self.added_fade,
            "repriced": self.repriced,
            "observed_only": self.observed_only,
            "skipped_malformed": self.skipped_malformed,
            "model_keys_new": list(self.model_keys_new),
        }


def merge_candidates(
    ledger: dict, candidates: list[dict], *, now: str, expected_model_key: str | None = None
) -> MergeStats:
    """Merge serve-time candidates into the ledger. Idempotent by event_key.

    - FIRST capture freezes bet-time fields (never overwritten).
    - Re-observation updates only last_seen_at / latest quotes / repriced_count.
    - A different serving model on an existing row is RECORDED
      (model_keys_seen), never adopted — the row belongs to the moment it was
      first bet-able.
    - Candidates with unusable identity were already rejected by the collector;
      here a missing event_key is counted as malformed (double fail-closed).
    """
    stats = MergeStats()
    rows = ledger.setdefault("rows", [])
    by_key = {r.get("event_key"): r for r in rows}

    for cand in candidates:
        key = cand.get("event_key")
        if not isinstance(key, str) or not key:
            stats.skipped_malformed += 1
            continue
        existing = by_key.get(key)
        if existing is None:
            row = dict(cand)
            row["status"] = STATUS_PENDING
            row["first_seen_at"] = now
            row["captured_at"] = now
            row["last_seen_at"] = now
            row["first_odds_forebet"] = cand.get("odds_forebet")
            row["first_odds_zulubet"] = cand.get("odds_zulubet")
            row["latest_odds_forebet"] = cand.get("odds_forebet")
            row["latest_odds_zulubet"] = cand.get("odds_zulubet")
            row["odds_source"] = _odds_source(cand)
            row["repriced_count"] = 0
            row["outcome"] = None
            row["settled_at"] = None
            row["result_source"] = None
            row["score"] = None
            row["graduation"] = None
            row["settle_notes"] = []
            rows.append(row)
            by_key[key] = row
            if cand.get("family") == FADE_FAMILY:
                stats.added_fade += 1
            else:
                stats.added_parent += 1
            if (
                expected_model_key
                and cand.get("model_key")
                and cand.get("model_key") != expected_model_key
            ):
                stats.model_keys_new.append(str(cand.get("model_key")))
            continue

        # Re-observation of an existing row: only frozen rows (settled /
        # conflict) stop updating; pending/unmatched rows stay observable
        # (unmatched may still be matched by a late-arriving fact with a
        # shifted date at the settlement stage — never re-priced).
        if existing.get("status") in (STATUS_SETTLED, STATUS_CONFLICT):
            continue
        existing["last_seen_at"] = now
        for book, col in (("forebet", "odds_forebet"), ("zulubet", "odds_zulubet")):
            new_q = cand.get(col)
            old_q = existing.get("latest_" + col)
            if new_q is not None and new_q != old_q:
                existing["latest_" + col] = new_q
                stats.repriced += 1
        stats.observed_only += 1
        seen = [k for k in (existing.get("model_keys_seen") or []) if k]
        mk = cand.get("model_key")
        if mk and mk not in seen:
            seen.append(mk)
        existing["model_keys_seen"] = seen
        if (
            expected_model_key
            and mk
            and mk != expected_model_key
            and mk not in stats.model_keys_new
        ):
            stats.model_keys_new.append(str(mk))
    return stats


# ---------------------------------------------------------------------------
# Settlement (fail-closed, alias-aware)
# ---------------------------------------------------------------------------


def load_alias_groups(path: Path | str | None) -> list[list[str]]:
    p = Path(path) if path else None
    if p is None or not p.exists():
        return []
    data = json.loads(p.read_text())
    return [g for g in data if isinstance(g, list)] if isinstance(data, list) else []


class TeamMatcher:
    """Keyset matcher over ledger keys + curated alias groups."""

    def __init__(self, alias_groups: list[list[str]]) -> None:
        self._groups_by_member: dict[str, set[str]] = {}
        for group in alias_groups:
            keys = {ledger_team_key(m) for m in group}
            keys.discard("")
            for member in group:
                mk = ledger_team_key(member)
                if not mk:
                    continue
                self._groups_by_member.setdefault(mk, set()).update(keys)

    def keyset(self, name: object) -> set[str]:
        """All ledger keys this name may legitimately be known by."""
        text = str(name or "").strip()
        keys = {ledger_team_key(text)}
        folded = ledger_team_key(fold_ascii(text))
        keys.add(folded)
        keys.discard("")
        expanded = set(keys)
        for k in keys:
            expanded |= self._groups_by_member.get(k, set())
        return expanded


def _result_signature(row: dict) -> tuple:
    return (row.get("outcome"), row.get("hs"), row.get("gs"))


class SettleStats:
    def __init__(self) -> None:
        self.settled = 0
        self.conflicts = 0
        self.unmatched = 0
        self.already_frozen = 0
        self.still_pending = 0
        self.conflict_keys: list[str] = []

    def as_dict(self) -> dict:
        return {
            "settled": self.settled,
            "conflicts": self.conflicts,
            "unmatched": self.unmatched,
            "already_frozen": self.already_frozen,
            "still_pending": self.still_pending,
            "conflict_keys": list(self.conflict_keys),
        }


def settle_ledger(
    ledger: dict,
    settled_rows: list[dict],
    *,
    matcher: TeamMatcher | None = None,
    now: str,
    today: date | None = None,
    date_window: int = DEFAULT_DATE_WINDOW_DAYS,
    unmatched_after_days: int = DEFAULT_UNMATCHED_AFTER_DAYS,
) -> SettleStats:
    """Apply settled-results facts to pending/unmatched ledger rows.

    Fail-closed rules:
      - a row settles only when every matching result fact AGREES
        (same outcome+score signature); disagreement -> conflict, loudly;
      - identity must match BOTH teams (ledger keys or curated aliases);
      - result date may shift at most ``date_window`` days (postponement);
      - a row with no fact after ``unmatched_after_days`` is unmatched —
        visible staleness, never a silent win/loss;
      - settled/conflict rows are FROZEN: later facts never reopen them.
    """
    stats = SettleStats()
    matcher = matcher or TeamMatcher([])
    ref_day = today or datetime.now(_LOCAL_TZ).date()

    # Index result facts by date -> list.
    facts: dict[str, list[dict]] = {}
    for fr in settled_rows or []:
        d = str(fr.get("date") or "")
        if not d:
            continue
        facts.setdefault(d, []).append(fr)

    for row in ledger.get("rows", []):
        status = row.get("status")
        if status in (STATUS_SETTLED, STATUS_CONFLICT):
            stats.already_frozen += 1
            continue
        try:
            row_day = date.fromisoformat(str(row.get("date")))
        except (TypeError, ValueError):
            # Malformed capture date: cannot settle, cannot age — fail closed.
            row["status"] = STATUS_CONFLICT
            row.setdefault("settle_notes", []).append(
                "malformed capture date; identity unverifiable"
            )
            stats.conflicts += 1
            stats.conflict_keys.append(str(row.get("event_key")))
            continue

        home_keys = matcher.keyset(row.get("home"))
        away_keys = matcher.keyset(row.get("away"))
        if not home_keys or not away_keys:
            row["status"] = STATUS_CONFLICT
            row.setdefault("settle_notes", []).append("identity keys unusable at settlement")
            stats.conflicts += 1
            stats.conflict_keys.append(str(row.get("event_key")))
            continue

        window = [
            (row_day - timedelta(days=date_window) + timedelta(days=i)).isoformat()
            for i in range(2 * date_window + 1)
        ]
        signatures: dict[tuple, list[dict]] = {}
        for d in window:
            for fr in facts.get(d, []):
                fh = matcher.keyset(fr.get("home"))
                fa = matcher.keyset(fr.get("away"))
                if not fh or not fa:
                    continue
                if not (home_keys & fh) or not (away_keys & fa):
                    continue
                sig = _result_signature(fr)
                signatures.setdefault(sig, []).append(fr)

        if len(signatures) > 1:
            row["status"] = STATUS_CONFLICT
            row.setdefault("settle_notes", []).append(
                f"conflicting result claims: {sorted(str(s) for s in signatures)}"
            )
            stats.conflicts += 1
            stats.conflict_keys.append(str(row.get("event_key")))
            continue
        if len(signatures) == 1:
            sig, frs = next(iter(signatures.items()))
            outcome, hs, gs = sig
            pick = str(row.get("pick") or "").strip().lower()
            if outcome not in ("home", "draw", "away"):
                # Unparseable outcome: not a result, visible but not scored.
                row["status"] = STATUS_CONFLICT
                row.setdefault("settle_notes", []).append(
                    f"unparseable outcome in result facts: {outcome!r}"
                )
                stats.conflicts += 1
                stats.conflict_keys.append(str(row.get("event_key")))
                continue
            row["status"] = STATUS_SETTLED
            row["outcome"] = outcome
            row["settled_at"] = now
            row["result_source"] = "|".join(sorted({str(fr.get("src") or "?") for fr in frs}))
            row["result_date"] = str(frs[0].get("date") or "")
            row["score"] = {"hs": hs, "gs": gs}
            row["graduation"] = "win" if pick == outcome else "loss"
            stats.settled += 1
            continue

        # No matching fact: age out or remain pending.
        if (ref_day - row_day).days > unmatched_after_days:
            if row.get("status") != STATUS_UNMATCHED:
                row["status"] = STATUS_UNMATCHED
                stats.unmatched += 1
            continue
        stats.still_pending += 1
    return stats


# ---------------------------------------------------------------------------
# Ledger views + statistics for the checkpoint report
# ---------------------------------------------------------------------------


def rows_by_family(ledger: dict, family: str) -> list[dict]:
    return [r for r in ledger.get("rows", []) if r.get("family") == family]


def wilson_lb(wins: int, n: int, z: float = 1.96) -> float | None:
    if n <= 0:
        return None
    p = wins / n
    z2 = z * z
    denom = 1 + z2 / n
    center = p + z2 / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    return (center - margin) / denom


def price_stats(rows: list[dict], price_field: str) -> dict:
    """Graded statistics for one FIXED price variant of a settled row set.

    Rows with a missing price are EXCLUDED from priced-stat denominators
    (reported as n_priced < n); they are never scored as wins or losses.
    """
    settled = [r for r in rows if r.get("status") == STATUS_SETTLED]
    n = len(settled)
    wins = sum(1 for r in settled if r.get("graduation") == "win")
    priced = []
    for r in settled:
        price = r.get(price_field)
        if price is None:
            continue
        try:
            p = float(price)
        except (TypeError, ValueError):
            continue
        if p <= 1.0:
            continue
        graded_win = r.get("graduation") == "win"
        priced.append((p, graded_win))
    n_priced = len(priced)
    p_wins = sum(1 for _, w in priced if w)
    pnl = sum((p - 1.0) if w else -1.0 for p, w in priced)
    return {
        "n": n,
        "wins": wins,
        "hit": (wins / n) if n else None,
        "wilson_lb": wilson_lb(wins, n),
        "n_priced": n_priced,
        "p_wins": p_wins,
        "p_hit": (p_wins / n_priced) if n_priced else None,
        "roi": (pnl / n_priced) if n_priced else None,
        "pnl": pnl,
        "priced_coverage": (n_priced / n) if n else None,
    }


def family_summary(ledger: dict) -> dict:
    """Per-family accrual counters for reports and warnings."""
    out: dict[str, dict] = {}
    for family in (PARENT_FAMILY, FADE_FAMILY):
        rows = rows_by_family(ledger, family)
        statuses: dict[str, int] = {}
        for r in rows:
            statuses[r.get("status") or "?"] = statuses.get(r.get("status") or "?", 0) + 1
        out[family] = {
            "rows": len(rows),
            "statuses": statuses,
            "settled": statuses.get(STATUS_SETTLED, 0),
            "pending": statuses.get(STATUS_PENDING, 0),
            "conflict": statuses.get(STATUS_CONFLICT, 0),
            "unmatched": statuses.get(STATUS_UNMATCHED, 0),
            "conflict_keys": [
                r.get("event_key") for r in rows if r.get("status") == STATUS_CONFLICT
            ],
        }
    return out


def accrual_between(ledger: dict, family: str, start: str | None, end: str | None) -> int:
    """Rows first captured strictly inside the [start, end] window."""
    n = 0
    for r in rows_by_family(ledger, family):
        t = str(r.get("first_seen_at") or "")[:10]
        if start and t < start:
            continue
        if end and t > end:
            continue
        n += 1
    return n


def active_days(ledger: dict, since: str | None = None) -> set[str]:
    """Distinct fixture dates with at least one ledger capture (>=since)."""
    days: set[str] = set()
    for r in ledger.get("rows", []):
        t = str(r.get("first_seen_at") or "")[:10]
        if since and t < since[:10]:
            continue
        if t:
            days.add(t)
    return days
