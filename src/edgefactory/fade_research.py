"""Conditional ml-fade slice research (read-only, no certification authority).

Investigates whether profitable ``ml-fade`` slices hide inside well-defined
contexts (league, competition type, odds band, model-probability band, fade
side, season segment) WITHOUT touching the production certification path.

Design guarantees:

- LEAKAGE — candidate *definition* may only reference pre-kickoff fields of
  the ``ml_fade_settled`` view (``ml_p``, ``parent_pick``, ``pick``,
  ``pick_odds`` (the fade's own price), ``league``, ``date``). Results
  (``outcome``), score columns and any closing price are structurally
  unavailable to the condition predicates (see :data:`ALLOWED_CONDITION_FIELDS`
  and the leak tests). ``outcome`` is used ONLY to grade rows, exactly like
  ``mine_consensus`` does.
- WALK-FORWARD — grading mirrors ``mine_consensus.stats`` accounting:
  train ``date < split``, validation ``split <= date < confirm_start``, and an
  untouched confirmation window ``date >= confirm_start``. Candidates are
  never selected on validation or confirmation performance.
- MULTIPLE TESTING — the grid is finite, predeclared here, and every
  candidate's result is reported (nothing hidden). Overlapping candidates
  with identical realized evidence are collapsed by
  :func:`dedupe_by_evidence`, mirroring the spirit of the miner's
  ``dedupe_equivalent_certified_edges``.
- PROMOTION — :func:`decide_promotion` is a STRICT SUPERSET of the production
  gates (``edgefactory.config.GATES`` are never altered): production
  train/valid gates + validation-day count + untouched-confirmation
  persistence. Nothing below that bar is more than "candidate".
- PRICE — ROI is computed on the fade's own opposing-side odds. Raw and
  realistic (:data:`edgefactory.config.BEST_ODDS_HAIRCUT`, the repo's
  "halve it" convention) figures are reported side by side.

This module promotes NOTHING operationally. Research-certified findings are
exploratory until independently re-mined through the production path.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .assay import wilson_lb
from .config import BEST_ODDS_HAIRCUT, GATES
from .entities import canonical_league, classify_competition

# --------------------------------------------------------------------------
# Predeclared search space. Any change here changes the candidate count that
# must be reported — edit only with a recorded reason.
# --------------------------------------------------------------------------
THRESHOLDS: tuple[int, ...] = (55, 60, 65, 70, 75, 80, 85)
"""Parent-confidence thresholds — identical to the production fade scan."""

FADE_SIDES: tuple[str, ...] = ("home", "away")

# Fade odds bands (pre-kickoff, fade's own price). Longshot tails separated:
# short fade prices mean fading an underdog parent; extreme tails are where
# book skew lives and where small samples lie loudest.
ODDS_BANDS: tuple[tuple[float, float], ...] = (
    (1.01, 2.00),
    (2.00, 3.00),
    (3.00, 4.50),
    (4.50, 6.50),
    (6.50, 10.00),
    (10.00, 1e9),
)

# Model probability bands (ml_p is knowable pre-kickoff; the production
# certified band starts at 0.55).
ML_P_BANDS: tuple[tuple[float, float], ...] = (
    (0.00, 0.55),
    (0.55, 0.60),
    (0.60, 0.65),
    (0.65, 0.70),
    (0.70, 0.75),
    (0.75, 1.01),
)

COMP_TYPES: tuple[str, ...] = ("league", "cup", "friendly", "youth", "women")

TOP_LEAGUES: int = 20
"""How many leagues enter the league dimension, ranked by TRAIN row count."""

DEFAULT_CONFIRM_START = "2026-01-01"
"""Untouched confirmation window start (predeclared)."""

# Research-only promotion tightening (production GATES are never changed).
MIN_VALID_DAYS: int = 30
"""Minimum distinct validation days, mirroring the audit window style."""

CONFIRM_MIN_N: int = 30
"""Minimum confirmation-window rows for a promotion to be considered."""

TRAIN_HALF_MIN_N: int = 60
"""Per-half train rows required before persistence is even evaluable."""

ALLOWED_CONDITION_FIELDS = frozenset(
    {
        "date",
        "home",
        "away",
        "league",
        "parent_pick",
        "pick",
        "ml_p",
        "pick_odds",
        "parent_pick_odds",
        "sport",
    }
)
"""Fields a candidate condition may read. outcome/hs/gs/closing are absent."""

# Dimensions actually searched, in scan order (recorded in the report).
GRID_DIMENSIONS: tuple[str, ...] = (
    "overall",  # no condition — the aggregate baseline
    "fade_side",  # fade lands on home vs away
    "odds_band",  # fade price band
    "ml_p_band",  # parent model confidence band
    "comp_type",  # classify_competition(league)
    "league",  # top-N canonical leagues by train rows
    "fade_side_odds",  # side x odds band
    "fade_side_comp",  # side x competition type
)


@dataclass(frozen=True)
class Condition:
    """One predeclared slice condition. ``field`` names the dimension; the
    value is a label for sides/comp/league or a (lo, hi) numeric band."""

    dim: str
    field: str  # resolver key (see _RESOLVERS)
    value: object

    def matches(self, row: dict) -> bool:
        resolved = _resolve(self.field, row)
        if self.dim in ("fade_side", "league", "comp_type"):
            return resolved == self.value
        return _in_band(resolved, self.value)

    def label(self) -> str:
        if self.dim in ("fade_side",):
            return f"{self.value}-fade"
        if self.dim == "ml_p_band":
            lo, hi = self.value
            return f"ml_p-{lo:.2f}-{hi:.2f}"
        if self.dim == "odds_band":
            lo, hi = self.value
            hi_s = "50+" if hi >= 1e9 else f"{hi:g}"
            return f"odds-{lo:g}-{hi_s}"
        return str(self.value)


def _resolve(field_name: str, row: dict) -> object:
    if field_name == "fade_side":
        return str(row.get("pick") or "").lower()
    if field_name == "league":
        # Callers may precompute `league_canonical` once per row (the scanner
        # does); plain rows still work via canonical_league().
        return row.get("league_canonical") or canonical_league(row.get("league"))
    if field_name == "comp_type":
        return row.get("comp_type_pre") or classify_competition(row.get("league"))
    if field_name == "ml_p":
        return row.get("ml_p")
    if field_name == "pick_odds":
        return row.get("pick_odds")
    raise KeyError(f"no resolver for {field_name}")


def _in_band(v: object, band: tuple[float, float]) -> bool:
    try:
        x = float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    lo, hi = band
    return lo <= x < hi


@dataclass(frozen=True)
class Candidate:
    """A condition (possibly composite) at one parent threshold."""

    threshold: float
    conditions: tuple[Condition, ...] = ()

    def matches(self, row: dict) -> bool:
        ml_p = row.get("ml_p")
        try:
            x = float(ml_p)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return False
        if math.isnan(x) or x * 100.0 < self.threshold:  # NaN never matches (SQL WHERE drops NULL)
            return False
        return all(c.matches(row) for c in self.conditions)

    def name(self) -> str:
        if self.conditions:
            cond = "+".join(c.label() for c in self.conditions)
            return f"ml-fade {cond} avg_p>={self.threshold:g}"
        return f"ml-fade avg_p>={self.threshold:g}"

    def dim(self) -> str:
        if not self.conditions:
            return "overall"
        if len(self.conditions) == 2:
            pair = (self.conditions[0].field, self.conditions[1].field)
            return {
                ("fade_side", "pick_odds"): "fade_side_odds",
                ("fade_side", "comp_type"): "fade_side_comp",
            }[pair]
        return self.conditions[0].dim

    def provenance(self) -> dict:
        return {
            "edge_family": "ml-fade",
            "parent_family": "ml-meta",
            "derivation": "inverse-selection",
            "scan": "research",
            "conditions": {
                c.field: (list(c.value) if isinstance(c.value, tuple) else c.value)
                for c in self.conditions
            }
            or {},
            "parent_threshold": self.threshold,
        }


# --------------------------------------------------------------------------
# Grid construction — train-ONLY information decides which leagues enter.
# --------------------------------------------------------------------------
def select_top_leagues(train_rows: list[dict], top_n: int = TOP_LEAGUES) -> list[str]:
    """Top-N canonical leagues by TRAIN row count. Validation/confirmation
    rows must never influence this (leakage) — callers pass train rows only."""
    counts: dict[str, int] = {}
    for row in train_rows:
        key = row.get("league_canonical") or canonical_league(row.get("league")) or "UNKNOWN"
        counts[key] = counts.get(key, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [k for k, _ in ranked[:top_n]]


def build_grid(top_leagues: list[str], thresholds=THRESHOLDS) -> list[Candidate]:
    """The full, finite, predeclared candidate grid (documented count)."""
    grid: list[Candidate] = []
    for thr in thresholds:
        grid.append(Candidate(thr))
        for side in FADE_SIDES:
            grid.append(Candidate(thr, (Condition("fade_side", "fade_side", side),)))
        for band in ODDS_BANDS:
            grid.append(Candidate(thr, (Condition("odds_band", "pick_odds", band),)))
        for band in ML_P_BANDS:
            grid.append(Candidate(thr, (Condition("ml_p_band", "ml_p", band),)))
        for comp in COMP_TYPES:
            grid.append(Candidate(thr, (Condition("comp_type", "comp_type", comp),)))
        for league in top_leagues:
            grid.append(Candidate(thr, (Condition("league", "league", league),)))
        for side in FADE_SIDES:
            for band in ODDS_BANDS:
                grid.append(
                    Candidate(
                        thr,
                        (
                            Condition("fade_side", "fade_side", side),
                            Condition("odds_band", "pick_odds", band),
                        ),
                    )
                )
            for comp in COMP_TYPES:
                grid.append(
                    Candidate(
                        thr,
                        (
                            Condition("fade_side", "fade_side", side),
                            Condition("comp_type", "comp_type", comp),
                        ),
                    )
                )
    return grid


# --------------------------------------------------------------------------
# Grading — mirrors mine_consensus.stats() accounting exactly.
# --------------------------------------------------------------------------
def _window(date_iso: str, split: str, confirm_start: str) -> str:
    if date_iso >= confirm_start:
        return "confirm"
    return "train" if date_iso < split else "valid"


def _price(v: object) -> float | None:
    """A usable price, or None for NULL/NaN/unparseable (matches SQL IS NOT NULL)."""
    if v is None:
        return None
    try:
        x = float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) else x


def _new_window() -> dict:
    return {
        "n": 0,
        "wins": 0,
        "pnl": 0.0,
        "n_priced": 0,
        "odds_sum": 0.0,
        "days": set(),
        "roi": None,
        "hit": 0.0,
        "wilson_lb": 0.0,
        "avg_odds": None,
    }


def _finish_window(w: dict) -> dict:
    n, wins, n_priced = w["n"], w["wins"], w["n_priced"]
    roi = (w["pnl"] / n_priced) if n_priced else None
    return {
        "n": n,
        "wins": wins,
        "hit": round(wins / n, 4) if n else 0.0,
        "wilson_lb": round(wilson_lb(wins, n), 4),
        "avg_odds": round(w["odds_sum"] / n_priced, 3) if n_priced else None,
        "roi": round(roi, 4) if roi is not None else None,
        "roi_realistic": round(roi * BEST_ODDS_HAIRCUT, 4) if roi is not None else None,
        "n_priced": n_priced,
        "n_days": len(w["days"]),
    }


def grade_rows(
    rows: list[dict], candidate: Candidate, split: str, confirm_start: str = DEFAULT_CONFIRM_START
) -> dict:
    """Walk-forward grading of one candidate over pre-kickoff rows.

    Mirrors mine_consensus.stats accounting: n counts every qualifying row,
    ROI only over priced rows (flat 1 unit at the fade's own odds).
    Train is additionally split chronologically into two halves for the
    persistence check; valid days are counted for the day-count gate.
    """
    win = {
        "train_early": _new_window(),
        "train_late": _new_window(),
        "train": _new_window(),
        "valid": _new_window(),
        "confirm": _new_window(),
    }
    train_dates = sorted({str(r.get("date"))[:10] for r in rows if str(r.get("date"))[:10] < split})
    mid = train_dates[len(train_dates) // 2] if train_dates else split

    for row in rows:
        if not candidate.matches(row):
            continue
        d = str(row.get("date"))[:10]
        wname = _window(d, split, confirm_start)
        w = win[wname]
        win_flag = row.get("pick") == row.get("outcome")
        w["n"] += 1
        w["days"].add(d)
        if win_flag:
            w["wins"] += 1
        odds_f = _price(row.get("pick_odds"))
        if odds_f is not None:
            w["n_priced"] += 1
            w["odds_sum"] += odds_f
            w["pnl"] += (odds_f - 1.0) if win_flag else -1.0
        if wname == "train":
            half = win["train_early" if d < mid else "train_late"]
            half["n"] += 1
            half["days"].add(d)
            if win_flag:
                half["wins"] += 1
            if odds_f is not None:
                half["n_priced"] += 1
                half["pnl"] += (odds_f - 1.0) if win_flag else -1.0

    out = {name: _finish_window(w) for name, w in win.items()}
    out["train_mid_date"] = mid
    return out


# --------------------------------------------------------------------------
# Promotion decision — strict superset of production gates; never weaker.
# --------------------------------------------------------------------------
def production_gates_pass(graded: dict) -> tuple[bool, list[str]]:
    """The production certification gates, verbatim (mine_consensus.evaluate)."""
    tr, va = graded["train"], graded["valid"]
    reasons: list[str] = []
    if tr["n"] < GATES.min_n_train:
        reasons.append(f"train n {tr['n']} < {GATES.min_n_train}")
    if va["n"] < GATES.min_n_valid:
        reasons.append(f"valid n {va['n']} < {GATES.min_n_valid}")
    if tr["roi"] is not None and tr["roi"] < GATES.min_roi_train:
        reasons.append(f"train roi {tr['roi']:+.2%} < {GATES.min_roi_train:+.0%}")
    if va["roi"] is not None and va["roi"] < GATES.min_roi_valid:
        reasons.append(f"valid roi {va['roi']:+.2%} < {GATES.min_roi_valid:+.0%}")
    if va["wilson_lb"] < 0.5:
        reasons.append(f"valid wilson_lb {va['wilson_lb']:.3f} < 0.500")
    return (not reasons), reasons


def decide_promotion(graded: dict) -> tuple[str, list[str]]:
    """Classify a graded candidate.

    Returns one of:
    - ``research-certified``: production gates + valid-day count + untouched
      confirmation ROI >= 0 + non-negative ROI in BOTH train halves and the
      confirmation window (persistence). Still exploratory — promotion to a
      live rule requires re-mining through the production path.
    - ``exploratory-positive``: production gates pass but confirmation or
      persistence is missing/failing — explicitly NOT promotable; exactly
      the class multiple testing manufactures.
    - ``candidate``: decently sampled but fails a gate.
    - ``sparse``: too little data to judge.
    - ``rejected``: decently sampled with decisively negative ROI.
    """
    tr, va, cf = graded["train"], graded["valid"], graded["confirm"]
    prod_ok, reasons = production_gates_pass(graded)

    if tr["n"] < 2 * TRAIN_HALF_MIN_N and va["n"] < GATES.min_n_valid:
        return "sparse", reasons

    if not prod_ok:
        decisive_negative = (va["roi"] is not None and va["roi"] < GATES.min_roi_valid) or (
            tr["roi"] is not None and tr["roi"] < GATES.min_roi_train
        )
        if decisive_negative and tr["n"] >= 2 * TRAIN_HALF_MIN_N and va["n"] >= CONFIRM_MIN_N:
            return "rejected", reasons
        return "candidate", reasons

    extras: list[str] = []
    if va["n_days"] < MIN_VALID_DAYS:
        extras.append(f"valid days {va['n_days']} < {MIN_VALID_DAYS}")
    halves = [graded["train_early"], graded["train_late"]]
    persistence_fail = (
        extras
        or any(h["n"] < TRAIN_HALF_MIN_N or (h["roi"] or -1.0) < 0 for h in halves)
        or cf["n"] < CONFIRM_MIN_N
        or (cf["roi"] or -1.0) < GATES.min_roi_valid
    )
    if not persistence_fail:
        return "research-certified", ["all gates + persistence cleared"]
    cf_roi = f"{cf['roi']:+.2%}" if cf["roi"] is not None else "n/a"
    extras.append(
        f"exploratory only: confirmation/persistence not met "
        f"(confirm n {cf['n']}, confirm roi {cf_roi}, "
        f"train-halves roi "
        f"{[('%+.2f%%' % (100 * h['roi'])) if h['roi'] is not None else 'n/a' for h in halves]})"
    )
    return "exploratory-positive", reasons + extras


# --------------------------------------------------------------------------
# Evidence dedup — same spirit as the miner's equivalence collapse.
# --------------------------------------------------------------------------
def _evidence_signature(result: dict) -> tuple:
    v = result["graded"]["valid"]
    t = result["graded"]["train"]
    return (t["n"], t["wins"], t["n_priced"], v["n"], v["wins"], v["n_priced"])


def _canonicality_key(r: dict) -> tuple:
    """Lower is more canonical: fewest conditions, then lowest threshold,
    then name. Result entries carry the candidate NAME (JSON-friendly), so
    conditions come from the recorded provenance."""
    return (
        len(r.get("provenance", {}).get("conditions", {})),
        r.get("threshold", 0.0),
        r.get("candidate", ""),
    )


def dedupe_by_evidence(results: list[dict]) -> tuple[list[dict], list[dict]]:
    """Collapse candidates with identical realized train+valid evidence.

    Only applied to candidates that pass the production gates (same scope as
    the miner's `dedupe_equivalent_certified_edges`): among identical
    evidence keep the most canonical (fewest conditions, then lowest
    threshold, then name). Non-passers are NEVER hidden. Returns (kept,
    removed)."""
    kept: dict[tuple, dict] = {}
    removed: list[dict] = []
    orderable = [r for r in results if r.get("production_gates_pass")]
    others = [r for r in results if not r.get("production_gates_pass")]
    for r in orderable:
        sig = _evidence_signature(r)
        inc = kept.get(sig)
        if inc is None:
            kept[sig] = r
            continue
        best, worst = (r, inc) if _canonicality_key(r) < _canonicality_key(inc) else (inc, r)
        kept[sig] = best
        # if the incumbent the loser pointed at was itself displaced, retarget
        # transitively so every removed variant names a SURVIVING variant.
        for rem in removed:
            if rem.get("deduped_into") == worst["candidate"]:
                rem["deduped_into"] = best["candidate"]
        removed.append(worst | {"deduped_into": best["candidate"]})
    return others + list(kept.values()), removed
