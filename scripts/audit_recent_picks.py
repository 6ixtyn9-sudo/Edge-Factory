#!/usr/bin/env python3
"""Audit recent archived daily picks against settled warehouse results."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
WAREHOUSE = LOCALDATA / "warehouse.duckdb"
DEFAULT_LOCAL_TZ = "Africa/Johannesburg"

import sys
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.entities import canonical_team  # noqa: E402
from edgefactory.settlement import is_void_disposition, terminal_event_disposition  # noqa: E402
from edgefactory.util import ledger_team_key, norm_team  # noqa: E402


@dataclass
class SettledPick:
    date: str
    rule_name: str
    bucket: str
    odds_source: str
    odds_match_method: str
    price_evidence: str
    price_quarantine_reason: str
    market: str
    pick: str
    outcome: str
    won: bool
    odds: float | None
    pnl: float | None
    suspect_price: float | None


def local_today() -> str:
    try:
        return datetime.now(ZoneInfo(DEFAULT_LOCAL_TZ)).date().isoformat()
    except Exception:
        return date.today().isoformat()


def daterange(start: str, end: str):
    d = datetime.strptime(start, "%Y-%m-%d").date()
    e = datetime.strptime(end, "%Y-%m-%d").date()
    while d <= e:
        yield d.isoformat()
        d += timedelta(days=1)


def archived_picks_path(day: str) -> Path:
    """Legacy single-path helper for external callers.

    The audit itself uses ``load_archived_picks_with_receipt`` below, which
    safely combines an immutable morning baseline with verified official late
    additions. This helper retains the historic morning-first fallback only.
    """
    morning = LOCALDATA / f"picks_morning_{day}.json"
    if morning.exists():
        return morning
    return LOCALDATA / f"picks_{day}.json"


def _archive_pick_key(row: dict[str, Any], fallback_day: str) -> tuple[str, str, str, str, str]:
    """Stable identity for a frozen 1X2 ledger row."""
    return (
        str(row.get("date") or fallback_day)[:10],
        ledger_team_key(row.get("home") or ""),
        ledger_team_key(row.get("away") or ""),
        str(row.get("market") or "").lower(),
        str(row.get("pick") or "").lower(),
    )


def _load_archive_rows(path: Path, day: str) -> list[dict[str, Any]]:
    try:
        raw = json.loads(path.read_text())
    except Exception:
        return []
    if not isinstance(raw, list):
        return []
    out: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        row = dict(item)
        row.setdefault("date", day)
        if str(row.get("date") or "")[:10] != day:
            continue
        out.append(row)
    return out


def _same_frozen_payload(left: dict[str, Any], right: dict[str, Any]) -> bool:
    """Accept additions only when the regular ledger preserved each morning
    row exactly. A forecast-overwritten regular ledger must fail closed."""
    return json.dumps(left, sort_keys=True, ensure_ascii=False, default=str) == json.dumps(
        right, sort_keys=True, ensure_ascii=False, default=str
    )


def load_archived_picks_with_receipt(start: str, end: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Load immutable morning picks plus verified official late-slate additions.

    The regular daily ledger may contain valid intraday discoveries, but it can
    be replaced by a forecast refresh. Its new rows are accepted only when it is
    a payload-identical superset of every morning baseline row.
    """
    out: list[dict[str, Any]] = []
    receipt: dict[str, Any] = {
        "morning_baseline_rows": 0,
        "verified_late_additions": 0,
        "regular_only_rows": 0,
        "unsafe_regular_ledger_dates": [],
        "empty_regular_ledger_dates": [],
    }
    for day in daterange(start, end):
        morning_path = LOCALDATA / f"picks_morning_{day}.json"
        regular_path = LOCALDATA / f"picks_{day}.json"
        morning = _load_archive_rows(morning_path, day) if morning_path.exists() else []
        regular = _load_archive_rows(regular_path, day) if regular_path.exists() else []

        if not morning:
            # Legacy date: regular date archive is the sole available record.
            out.extend(regular)
            receipt["regular_only_rows"] += len(regular)
            continue

        out.extend(morning)
        receipt["morning_baseline_rows"] += len(morning)
        if not regular:
            if regular_path.exists():
                # A regular ledger file exists but holds zero rows. Either the
                # day legitimately recorded no late additions, or a post-kickoff
                # rerun emptied the ledger before 27.18 made writes append-only.
                # Either way the audit is morning-baseline-only for this date —
                # surface it instead of letting the gap stay silent.
                receipt["empty_regular_ledger_dates"].append(day)
            continue

        morning_by_key = {_archive_pick_key(row, day): row for row in morning}
        regular_by_key = {_archive_pick_key(row, day): row for row in regular}
        baseline_preserved = all(
            key in regular_by_key and _same_frozen_payload(row, regular_by_key[key])
            for key, row in morning_by_key.items()
        )
        if not baseline_preserved:
            receipt["unsafe_regular_ledger_dates"].append(day)
            continue

        for row in regular:
            if _archive_pick_key(row, day) not in morning_by_key:
                out.append(row)
                receipt["verified_late_additions"] += 1

    return out, receipt


def load_archived_picks(start: str, end: str) -> list[dict[str, Any]]:
    """Compatibility wrapper for callers/tests that need rows only."""
    return load_archived_picks_with_receipt(start, end)[0]


def dedupe_archived_picks(picks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate frozen pick rows without replacing them with later state.

    The first row from the selected frozen snapshot is authoritative. Do not
    choose by statistical sample size, because that can replace pick-time
    stats with a later regenerated state.
    """
    best: dict[tuple, dict[str, Any]] = {}
    for p in picks:
        home = ledger_team_key(p.get("home") or "")
        away = ledger_team_key(p.get("away") or "")
        day = str(p.get("date") or "")[:10]
        market = str(p.get("market") or "").lower()
        sel = str(p.get("pick") or "").lower()
        if not (home and away):
            continue
        key = (day, home, away, market, sel)

        comment = p.get("statistical_comment") or ""
        mu = re.search(r"n=(\d+)", comment)
        n_current = int(mu.group(1)) if mu else 0

        existing = best.get(key)
        if existing:
            # Preserve the first archived pick-time row. Never replace it with
            # a later row merely because it has a larger stats sample.
            continue

        if existing:
            e_comment = existing.get("statistical_comment") or ""
            e_mu = re.search(r"n=(\d+)", e_comment)
            n_existing = int(e_mu.group(1)) if e_mu else 0
            if n_current <= n_existing:
                continue

        best[key] = p

    return list(best.values())


def _dedupe_keys(keys: list[str]) -> list[str]:
    out: list[str] = []
    for key in keys:
        key = str(key or "")
        if key and key not in out:
            out.append(key)
    return out


def char_ngram_similarity(s1: str, s2: str, n: int = 2) -> float:
    def get_ngrams(s: str) -> set[str]:
        clean = re.sub(r"[^a-z0-9]", "", s.lower())
        return {clean[i : i + n] for i in range(len(clean) - n + 1)} if len(clean) >= n else set()

    g1 = get_ngrams(s1)
    g2 = get_ngrams(s2)
    if not g1 or not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)


def audit_team_key_candidates(raw: object) -> list[str]:
    text = str(raw or "")
    keys = [norm_team(text)]
    try:
        canon = canonical_team(text)
        keys.append(norm_team(canon))
        _DISAMBIG = {
            "launcesto": 14,
        }
        base9 = norm_team(text)
        if base9 in _DISAMBIG:
            keys.append(norm_team(canon, width=_DISAMBIG[base9]))
    except Exception:
        pass

    manual: dict[str, list[str]] = {
        "kpvj": ["kpvkokkol"],
        "kpvjk": ["kpvkokkol"],
        "guangzhou": ["guangdong"],
        "hebeikung": ["shijiazhu", "poweshiji"],
        "meizhouke": ["meizhouwu", "meizhouha"],
        "fcdunavru": ["dunavruse"],
        "csvolunta": ["voluntari"],
        "rfs": ["rigasfs"],
        "rigasfutb": ["rigasfs"],
        "rgasfs": ["rigasfs"],
        "fktukums": ["tukums"],
        "tukumsii": ["tukums"],
        "rigaii": ["rigafcii"],
        "valmierab": ["valmiera"],
        "neftchi": ["neftchife"],
        "dila": ["dilagori"],
        # Kyrgyzaltyn Kara-Balta is listed as Kara-Balta on picks and as
        # Kyrgyzaltyn / FC Kyrgyzaltyn on some result donors.
        "karabalta": ["kyrgyzalt", "kyrgyzaltyn"],
    }
    base = norm_team(text)
    if base in manual:
        keys.extend(manual[base])

    return _dedupe_keys(keys)


def _pick_diag(pick: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "date": str(pick.get("date") or "")[:10],
        "match": pick.get("match") or f"{pick.get('home')} vs {pick.get('away')}",
        "home": pick.get("home"),
        "away": pick.get("away"),
        "league": pick.get("league"),
        "rule": pick.get("edge_rule") or pick.get("rule") or pick.get("display_rule"),
        "bucket": pick.get("bucket"),
        "pick": pick.get("pick"),
        "odds": pick.get("odds"),
        "reason": reason,
        "home_key_candidates": audit_team_key_candidates(pick.get("home")),
        "away_key_candidates": audit_team_key_candidates(pick.get("away")),
    }


def _settled_overlay_path() -> Path:
    env = os.environ.get("EDGE_FACTORY_LOCALDATA")
    base = Path(env) if env else LOCALDATA
    return base / "settled_results.json"



def load_overlay_event_dispositions(path: Path | None = None) -> list[dict[str, Any]]:
    """Addendum 21 companion: bot-persisted terminal no-score facts.

    Same overlay file as scores. Only POSTPONED/CANCELLED/ABANDONED rows are
    accepted. Scheduled/live/blank never become a void. A later same-date
    score still wins in ``build_report``.
    """
    p = path or _settled_overlay_path()
    try:
        payload = json.loads(p.read_text())
        rows = payload.get("dispositions") or []
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        day = str(row.get("date") or "")[:10]
        home = str(row.get("home") or "")
        away = str(row.get("away") or "")
        disposition = str(row.get("disposition") or "")
        if not day or not home or not away or not is_void_disposition(disposition):
            continue
        out.append(
            {
                "date": day,
                "home": home,
                "away": away,
                "disposition": disposition,
                "origin": str(row.get("src") or row.get("origin") or "overlay"),
            }
        )
    return out


def load_settled_overlay(path: Path | None = None) -> list[dict[str, Any]]:
    """Addendum 21: bot-persisted settled-score facts shared across machines.

    Regenerated deterministically by export_settled_results.py (rolling window,
    bot-owned in git). A missing/stale file means warehouse-only behaviour —
    exactly the pre-overlay semantics.
    """
    p = path or _settled_overlay_path()
    try:
        payload = json.loads(p.read_text())
        rows = payload.get("rows") or []
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for r in rows:
        try:
            out.append(
                {
                    "date": str(r["date"])[:10],
                    "home": str(r["home"]),
                    "away": str(r["away"]),
                    "hs": int(r["hs"]),
                    "gs": int(r["gs"]),
                    "outcome": str(r["outcome"]),
                }
            )
        except (KeyError, TypeError, ValueError):
            continue
    return out


def _verified_event_dispositions_path() -> Path:
    preferred = ROOT / "Config" / "verified_event_dispositions.json"
    if preferred.exists() or (ROOT / "Config").exists():
        return preferred
    return ROOT / "config" / "verified_event_dispositions.json"


def load_verified_event_dispositions(path: Path | None = None) -> list[dict[str, Any]]:
    """Load exact, reviewed postponed/cancelled/abandoned facts.

    These are audit-only event dispositions, never result scores and never
    source/pick inputs. Invalid or non-terminal statuses fail closed.
    """
    p = path or _verified_event_dispositions_path()
    try:
        payload = json.loads(p.read_text())
        rows = payload.get("rows") or []
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        day = str(row.get("date") or "")[:10]
        home = str(row.get("home") or "")
        away = str(row.get("away") or "")
        disposition = str(row.get("disposition") or "")
        if not day or not home or not away or not is_void_disposition(disposition):
            continue
        out.append({
            "date": day,
            "home": home,
            "away": away,
            "disposition": disposition,
            "source": str(row.get("source") or "verified_disposition"),
            "verified_at": str(row.get("verified_at") or ""),
        })
    return out


def _add_disposition(
    index: dict[tuple[str, str, str], dict[str, Any]],
    *,
    day: str,
    home: str,
    away: str,
    disposition: str,
    origin: str,
    replace: bool = False,
) -> None:
    if not is_void_disposition(disposition):
        return
    entry = {
        "disposition": disposition,
        "home": home,
        "away": away,
        "origin": origin,
    }
    h9, a9 = norm_team(home), norm_team(away)
    h14, a14 = norm_team(home, 14), norm_team(away, 14)
    keys = [(day, h9, a9)]
    if (h14, a14) != (h9, a9):
        keys.append((day, h14, a14))
    for key in keys:
        if replace:
            index[key] = entry
        else:
            index.setdefault(key, entry)


def load_event_disposition_index(
    warehouse_path: Path,
    *,
    start: str | None = None,
    end: str | None = None,
) -> dict[tuple[str, str, str], dict[str, Any]]:
    """Collect positive terminal no-score evidence from existing raw sources.

    Only explicit postponed/cancelled/abandoned labels become a disposition.
    Missing, scheduled, live, and generic suspended statuses remain unknown.
    Warehouse source-status wins over the shared overlay; reviewed config
    facts override both. A final score still wins later in ``build_report``.
    """
    index: dict[tuple[str, str, str], dict[str, Any]] = {}
    try:
        import duckdb
        if not warehouse_path.exists():
            raise FileNotFoundError
        con = duckdb.connect(str(warehouse_path), read_only=True)
        tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
        source_tables = ("forebet", "vitibet", "scoutingstats")
        for source in source_tables:
            if source not in tables:
                continue
            filters = ["status IS NOT NULL"]
            if start:
                filters.append(f"CAST(date AS VARCHAR) >= '{start}'")
            if end:
                filters.append(f"CAST(date AS VARCHAR) <= '{end}'")
            query = f"SELECT date, home, away, status FROM {source} WHERE " + " AND ".join(filters)
            for day, home, away, status in con.execute(query).fetchall():
                disposition = terminal_event_disposition(status)
                if disposition:
                    _add_disposition(
                        index,
                        day=str(day)[:10],
                        home=str(home),
                        away=str(away),
                        disposition=disposition,
                        origin=f"source_status:{source}",
                    )
        con.close()
    except Exception:
        # Status evidence enriches audits but must never break score auditing.
        pass

    for row in load_overlay_event_dispositions():
        _add_disposition(
            index,
            day=row["date"],
            home=row["home"],
            away=row["away"],
            disposition=row["disposition"],
            origin=str(row.get("origin") or "overlay"),
            replace=False,
        )

    for row in load_verified_event_dispositions():
        _add_disposition(
            index,
            day=row["date"],
            home=row["home"],
            away=row["away"],
            disposition=row["disposition"],
            origin="verified_disposition",
            replace=True,
        )
    return index


def load_results_index(warehouse_path: Path) -> tuple[dict[tuple[str, str, str], dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    import duckdb

    from edgefactory.util import norm_team, norm_team_sql

    if not warehouse_path.exists():
        raise FileNotFoundError(f"warehouse not found: {warehouse_path}")

    con = duckdb.connect(str(warehouse_path), read_only=True)
    tables = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
    candidates = [
        (1, "forebet_settled"),
        (2, "bettingclosed_settled"),
        (3, "zulubet_settled"),
        (4, "statarea_settled"),
        (5, "scoutingstats_settled"),
        (6, "vitibet_settled"),
        (7, "betexplorer_settled"),
    ]
    active = [(prio, name) for prio, name in candidates if name in tables]
    if not active:
        return {}, {}

    nh9, na9 = norm_team_sql("home", 9), norm_team_sql("away", 9)
    nh14, na14 = norm_team_sql("home", 14), norm_team_sql("away", 14)

    union_sql = " UNION ALL ".join(
        f"SELECT {prio} AS prio, date, home, away, "
        f"{nh9} AS hkey, {na9} AS akey, "
        f"{nh14} AS hkey14, {na14} AS akey14, "
        f"hs, gs, outcome FROM {name} "
        f"WHERE hs IS NOT NULL AND gs IS NOT NULL"
        for prio, name in active
    )
    sql = f"""
    WITH all_results AS (
      {union_sql}
    ), ranked AS (
      SELECT *,
             ROW_NUMBER() OVER (PARTITION BY date, hkey, akey, hkey14, akey14 ORDER BY prio) AS rn
      FROM all_results
    )
    SELECT date, hkey, akey, hkey14, akey14, hs, gs, outcome, home, away
    FROM ranked
    WHERE rn = 1
    """
    rows = con.execute(sql).fetchall()
    index: dict[tuple[str, str, str], dict[str, Any]] = {}
    results_by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    known_pairs: dict[str, set[tuple[str, str]]] = defaultdict(set)

    for day, hkey, akey, hkey14, akey14, hs, gs, outcome, home, away in rows:
        entry = {
            "hs": int(hs), "gs": int(gs), "outcome": str(outcome),
            "home": str(home), "away": str(away), "origin": "warehouse",
        }
        d = str(day)[:10]
        # 9-char key (legacy)
        index[(d, str(hkey), str(akey))] = entry
        # 14-char key (disambiguation)
        if str(hkey14) != str(hkey) or str(akey14) != str(akey):
            index[(d, str(hkey14), str(akey14))] = entry

        results_by_date[d].append(entry)
        known_pairs[d].add((entry["home"].lower(), entry["away"].lower()))

    # Addendum 21: shared settled-results overlay (bot-persisted facts). The
    # warehouse wins on conflict; the overlay only fills rows this machine
    # never captured itself, so cloud and laptop settle the same fixtures.
    for o in load_settled_overlay():
        entry = {
            "hs": o["hs"], "gs": o["gs"], "outcome": o["outcome"],
            "home": o["home"], "away": o["away"], "origin": "overlay",
        }
        d = o["date"]
        h9, a9 = norm_team(o["home"]), norm_team(o["away"])
        if (d, h9, a9) not in index:
            index[(d, h9, a9)] = entry
        h14, a14 = norm_team(o["home"], 14), norm_team(o["away"], 14)
        if (h14, a14) != (h9, a9):
            index.setdefault((d, h14, a14), entry)
        pair = (entry["home"].lower(), entry["away"].lower())
        if pair not in known_pairs[d]:
            known_pairs[d].add(pair)
            results_by_date[d].append(entry)

    return index, results_by_date


# Red-team F4 (fixed 2026-08-05): the old fuzzy match compared COMBINED
# "home away" strings at 0.40, so swapped fixtures (Arsenal Chelsea vs
# Chelsea Arsenal, sim ~0.73) could settle a pick against the REVERSED
# outcome. Now ORIENTATION-CHECKED: the pick's home must match the result's
# home side at least as well as the result's away side (and vice versa).
# Swaps fail (each pick side matches the OPPOSITE result side better);
# legitimate name bridges (Clarence Zebras -> Hobart Zebras) still pass.
# Failing to match is honest (pending/unmatched) — a wrong settlement is not.
_FUZZY_MIN_SIM = 0.40
# Per-side floor for alias-conflict candidates. Below this, a "shared" team is
# a key collision, not a spelling variant: norm_team() strips the W suffix, so
# "Universitatea Craiova" (men) and "Universitatea Craiova W" (women) share a
# key, and the combined bigram score is dominated by the long home name. The
# away side ("FC Voluntari" vs "Ol. Cluj W", ~0.14) must also clear this floor
# or the women's fixture would false-flag a conflict.
_ALIAS_SIDE_MIN_SIM = 0.30


def _orientation_ok(pick_home: str, pick_away: str, res_h: str, res_a: str) -> bool:
    """Orientation guard: each pick side must match ITS result side better than
    the opposite side. Rejects swapped-fixture wrong settlements."""
    sim_hh = char_ngram_similarity(pick_home, res_h, n=2)
    sim_ha = char_ngram_similarity(pick_home, res_a, n=2)
    sim_ah = char_ngram_similarity(pick_away, res_h, n=2)
    sim_aa = char_ngram_similarity(pick_away, res_a, n=2)
    return sim_hh > sim_ha and sim_aa > sim_ah


def find_fuzzy_result_matches(
    pick_home: str,
    pick_away: str,
    results_on_date: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Every orientation-checked bigram match on the date (alias-aware).

    ``find_fuzzy_result_match`` returns only the best match; this returns all
    of them so callers can detect cross-spelling outcome conflicts instead of
    silently taking one spelling's result.
    """
    out: list[dict[str, Any]] = []
    for res in results_on_date:
        res_h = str(res.get("home", ""))
        res_a = str(res.get("away", ""))
        if not _orientation_ok(pick_home, pick_away, res_h, res_a):
            continue
        combined = char_ngram_similarity(f"{pick_home} {pick_away}", f"{res_h} {res_a}", n=2)
        if combined >= _FUZZY_MIN_SIM:
            out.append(res)
    return out


def find_fuzzy_result_match(pick_home: str, pick_away: str, results_on_date: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Orientation-checked bigram fallback when key mapping fails."""
    best_match = None
    best_sim = 0.0
    for res in find_fuzzy_result_matches(pick_home, pick_away, results_on_date):
        combined = char_ngram_similarity(
            f"{pick_home} {pick_away}",
            f"{res.get('home', '')} {res.get('away', '')}",
            n=2,
        )
        if combined > best_sim:
            best_sim = combined
            best_match = res
    return best_match


def _alias_candidate_results(
    pick_home: str,
    pick_away: str,
    pick_date: str,
    results_by_date: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Results on the pick's date sharing a normalized team key with the pick.

    Cheap pre-filter for alias-conflict detection: a fixture filed under
    several spellings (``Pafos vs Dinamo Tirana`` 2-2 vs ``Pafos vs KS Dinamo
    Tirana`` 4-2) shares the home key while the away spelling differs, so the
    exact key lookup hits only one spelling. We pull every result sharing
    either team key and keep those that bigram-match both sides with correct
    orientation — genuinely different fixtures sharing a key fragment are
    dropped by the combined-similarity threshold.
    """
    home_keys = set(audit_team_key_candidates(pick_home))
    away_keys = set(audit_team_key_candidates(pick_away))
    out: list[dict[str, Any]] = []
    for r in results_by_date.get(pick_date, []):
        rh = str(r.get("home", ""))
        ra = str(r.get("away", ""))
        hk = norm_team(rh)
        ak = norm_team(ra)
        if not (hk in home_keys or ak in away_keys or hk in away_keys or ak in home_keys):
            continue
        sim_hh = char_ngram_similarity(pick_home, rh, n=2)
        sim_aa = char_ngram_similarity(pick_away, ra, n=2)
        if min(sim_hh, sim_aa) < _ALIAS_SIDE_MIN_SIM:
            continue
        if not _orientation_ok(pick_home, pick_away, rh, ra):
            continue
        combined = char_ngram_similarity(f"{pick_home} {pick_away}", f"{rh} {ra}", n=2)
        if combined >= _FUZZY_MIN_SIM:
            out.append(r)
    return out


def _find_rescheduled_result(
    pick: dict[str, Any],
    pick_date: str,
    results: dict[tuple[str, str, str], dict[str, Any]],
    days: int = 3,
) -> dict[str, Any] | None:
    """Scan nearby calendar days for the same team pair.

    A pick that is pending on its own date but whose exact team pair settled
    within ±``days`` is a rescheduled fixture, not a missing result — the pick
    fired against a schedule that later moved (Viking 08-29 -> 08-30, Hønefoss
    W 08-29 -> 08-31). Report it as such instead of burying it under
    "pending/unmatched". Diagnostic-only: the pick is neither settled nor
    voided here, so there is no false-settlement risk.
    """
    try:
        d0 = datetime.strptime(pick_date, "%Y-%m-%d").date()
    except ValueError:
        return None
    hc = audit_team_key_candidates(pick.get("home"))
    ac = audit_team_key_candidates(pick.get("away"))
    nearest: tuple[int, str, dict[str, Any]] | None = None  # (dist, date, hit)
    for offset in range(-days, days + 1):
        if offset == 0:
            continue
        nd = (d0 + timedelta(days=offset)).isoformat()
        for hk in hc:
            for ak in ac:
                hit = results.get((nd, hk, ak))
                if hit is not None:
                    dist = abs(offset)
                    if nearest is None or dist < nearest[0]:
                        nearest = (dist, nd, hit)
    if nearest is None:
        return None
    _, nd, hit = nearest
    diag = _pick_diag(pick, "rescheduled")
    diag.update({
        "rescheduled_to": nd,
        "rescheduled_home": hit.get("home"),
        "rescheduled_away": hit.get("away"),
        "rescheduled_hs": hit.get("hs"),
        "rescheduled_gs": hit.get("gs"),
        "rescheduled_outcome": hit.get("outcome"),
        "rescheduled_origin": hit.get("origin"),
    })
    return diag


def _price_evidence_from_pick(pick: dict[str, Any]) -> tuple[str, str]:
    """Return archived price-evidence fields, deriving an honest legacy label.

    Addendum 26 writes explicit fields at pick time. Older frozen archives keep
    their original odds but are still classifiable for the new native audit
    tables, never silently promoted to trusted evidence.
    """
    explicit = str(pick.get("price_evidence") or "").strip()
    reason = str(pick.get("price_quarantine_reason") or "").strip()
    if explicit:
        return explicit, reason or "NONE"

    method = str(pick.get("odds_match_method") or "").strip()
    source = str(pick.get("odds_source") or "").strip()
    if method == "alias_fuzzy":
        return "SUSPECT_ALIAS_FUZZY", "alias_fuzzy"
    if source == "scoutingstats_odds":
        return "SCOUTINGSTATS_SOLE", "scoutingstats_sole_source"
    if source == "bzzoiro_odds":
        return "BZZOIRO_PRIMARY", "NONE"
    if source == "betexplorer_odds":
        return "BETEXPLORER_RESCUE", "NONE"
    if pick.get("odds") in (None, ""):
        return "UNMATCHED", "NONE"
    return "SOURCE_FALLBACK", "NONE"


def settle_pick(pick: dict[str, Any], result: dict[str, Any] | None) -> SettledPick | None:
    if not result:
        return None
    market = str(pick.get("market") or "")
    selection = str(pick.get("pick") or "")
    if market == "1x2":
        if selection not in {"home", "draw", "away"}:
            return None
        outcome = str(result.get("outcome") or "")
        won = selection == outcome
    elif market == "ou_2.5":
        # Over/Under 2.5 is settled from the final scoreline, not the 1X2
        # outcome. The consensus miner expresses the selection as over/under.
        if selection not in {"over", "under"}:
            return None
        hs, gs = result.get("hs"), result.get("gs")
        if hs is None or gs is None:
            return None
        outcome = "over" if (hs + gs) >= 3 else "under"
        won = selection == outcome
    elif market == "btts":
        # Both Teams to Score is settled from the final scoreline as well.
        if selection not in {"yes", "no"}:
            return None
        hs, gs = result.get("hs"), result.get("gs")
        if hs is None or gs is None:
            return None
        outcome = "yes" if (hs > 0 and gs > 0) else "no"
        won = selection == outcome
    else:
        return None
    odds_value = pick.get("odds")
    try:
        odds = float(odds_value) if odds_value not in (None, "") else None
    except (TypeError, ValueError):
        odds = None
    pnl = None if odds is None else (odds - 1.0 if won else -1.0)
    price_evidence, price_quarantine_reason = _price_evidence_from_pick(pick)
    suspect_payload = pick.get("suspect_price") if isinstance(pick.get("suspect_price"), dict) else {}
    try:
        suspect_price = float(suspect_payload.get("odds"))
        if not math.isfinite(suspect_price) or suspect_price <= 1.0:
            suspect_price = None
    except (TypeError, ValueError):
        suspect_price = None
    return SettledPick(
        date=str(pick.get("date") or "")[:10],
        rule_name=str(pick.get("edge_rule") or pick.get("rule") or pick.get("display_rule") or "UNKNOWN"),
        bucket=str(pick.get("bucket") or "UNKNOWN"),
        odds_source=str(pick.get("odds_source") or "UNKNOWN"),
        odds_match_method=str(pick.get("odds_match_method") or "UNKNOWN"),
        price_evidence=price_evidence,
        price_quarantine_reason=price_quarantine_reason,
        market=market,
        pick=selection,
        outcome=outcome,
        won=won,
        odds=odds,
        pnl=pnl,
        suspect_price=suspect_price,
    )


def summarize_scored(rows: list[SettledPick]) -> dict[str, Any]:
    settled = len(rows)
    wins = sum(1 for row in rows if row.won)
    with_odds = [row for row in rows if row.pnl is not None]
    pnl_sum = sum(float(row.pnl or 0.0) for row in with_odds)
    return {
        "settled_picks": settled,
        "wins": wins,
        "hit_rate": round(wins / settled, 6) if settled else None,
        "priced_picks": len(with_odds),
        "roi": round(pnl_sum / len(with_odds), 6) if with_odds else None,
    }


def summarize_by(rows: list[SettledPick], attr: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[SettledPick]] = defaultdict(list)
    for row in rows:
        grouped[str(getattr(row, attr) or "UNKNOWN")].append(row)
    return {name: summarize_scored(group_rows) for name, group_rows in sorted(grouped.items())}


def summarize_quarantine_by(rows: list[SettledPick], attr: str) -> dict[str, dict[str, Any]]:
    """Quarantine group scores plus the count/mean of excluded fuzzy prices."""
    grouped: dict[str, list[SettledPick]] = defaultdict(list)
    for row in rows:
        grouped[str(getattr(row, attr) or "UNKNOWN")].append(row)
    out: dict[str, dict[str, Any]] = {}
    for name, group_rows in sorted(grouped.items()):
        summary = summarize_scored(group_rows)
        suspect_prices = [r.suspect_price for r in group_rows if r.suspect_price is not None]
        summary["suspect_price_captures"] = len(suspect_prices)
        summary["avg_suspect_price"] = (
            round(sum(suspect_prices) / len(suspect_prices), 6) if suspect_prices else None
        )
        out[name] = summary
    return out


# --------------------------------------------------------------- veto deep dive
#
# Addendum 27.14: the flagship audit number must survive interrogation before it
# can steer staking policy. SKIPPED_VETO led the ROI table, but one blended
# figure hides the composition that decides whether the veto is mispriced or the
# audit is. These cuts are computed from the SAME settled rows as by_bucket —
# never a parallel settlement path.

VETO_DEEP_DIVE_SOFT_EVIDENCE = (
    "SUSPECT_ALIAS_FUZZY",
    "SCOUTINGSTATS_SOLE",
    "UNMATCHED",
    "SOURCE_FALLBACK",
)

_VETO_ODDS_BANDS = (
    (1.0, 1.5, "<1.50"),
    (1.5, 2.0, "1.50-2.00"),
    (2.0, 3.0, "2.00-3.00"),
    (3.0, None, ">=3.00"),
)


def _veto_odds_band(odds: float | None) -> str:
    if odds is None:
        return "unpriced"
    for lo, hi, name in _VETO_ODDS_BANDS:
        if odds >= lo and (hi is None or odds < hi):
            return name
    return "other"


def _veto_reason_label(pick: dict[str, Any]) -> str:
    raw = pick.get("veto_reason")
    if isinstance(raw, list):
        raw = "+".join(str(r) for r in raw if r)
    return str(raw or "").strip() or "UNRECORDED"


def _summarize_pairs(rows: list[tuple[SettledPick, dict[str, Any]]]) -> dict[str, Any]:
    return summarize_scored([s for s, _p in rows])


def build_veto_deep_dive(
    pairs: list[tuple[SettledPick, dict[str, Any]]],
    *,
    focus_bucket: str = "SKIPPED_VETO",
    contrast_bucket: str = "CAUTION",
) -> dict[str, Any]:
    """Cross-cut one bucket's settled rows by evidence, odds band and veto reason."""
    focus = [(s, p) for s, p in pairs if s.bucket == focus_bucket]
    contrast = [(s, p) for s, p in pairs if s.bucket == contrast_bucket]

    def cut(rows, key):
        grouped: dict[str, list] = defaultdict(list)
        for s, p in rows:
            grouped[key(s, p)].append((s, p))
        return grouped

    by_band = cut(focus, lambda s, _p: _veto_odds_band(s.odds))
    band_order = [name for _lo, _hi, name in _VETO_ODDS_BANDS] + ["unpriced", "other"]
    soft = set(VETO_DEEP_DIVE_SOFT_EVIDENCE)
    return {
        "focus_bucket": focus_bucket,
        "overall": _summarize_pairs(focus),
        "by_price_evidence": {
            k: _summarize_pairs(v)
            for k, v in sorted(cut(focus, lambda s, _p: s.price_evidence).items())
        },
        "by_odds_band": {
            name: _summarize_pairs(by_band[name])
            for name in band_order if name in by_band
        },
        "by_veto_reason": {
            k: _summarize_pairs(v)
            for k, v in sorted(cut(focus, lambda _s, p: _veto_reason_label(p)).items())
        },
        "trusted_evidence_only": _summarize_pairs(
            [(s, p) for s, p in focus if s.price_evidence not in soft]
        ),
        "soft_evidence_only": _summarize_pairs(
            [(s, p) for s, p in focus if s.price_evidence in soft]
        ),
        "soft_evidence_labels": sorted(soft),
        "contrast_bucket": contrast_bucket,
        "contrast_by_price_evidence": {
            k: _summarize_pairs(v)
            for k, v in sorted(cut(contrast, lambda s, _p: s.price_evidence).items())
        },
    }


def parse_statistical_comment(comment: str) -> dict[str, Any]:
    out = {
        "over25": None,
        "btts": None,
        "home_o15": None,
        "away_o15": None,
        "avg_goals": None,
        "top_scores": []
    }
    if not comment:
        return out

    m_avg = re.search(r"Avg Goals:\s*([\d.]+)", comment)
    if m_avg:
        try:
            avg = float(m_avg.group(1))
            if math.isfinite(avg):
                out["avg_goals"] = avg
        except ValueError:
            pass

    m_o25 = re.search(r"Over 2.5:\s*([\d.]+)%", comment)
    if m_o25:
        out["over25"] = float(m_o25.group(1)) / 100.0
        
    m_btts = re.search(r"BTTS:\s*([\d.]+)%", comment)
    if m_btts:
        out["btts"] = float(m_btts.group(1)) / 100.0
        
    m_h_o15 = re.search(r"Home Over 1.5 Goals:\s*([\d.]+)%", comment)
    if m_h_o15:
        out["home_o15"] = float(m_h_o15.group(1)) / 100.0
        
    m_a_o15 = re.search(r"Away Over 1.5 Goals:\s*([\d.]+)%", comment)
    if m_a_o15:
        out["away_o15"] = float(m_a_o15.group(1)) / 100.0
        
    m_scores = re.search(r"Top Scores:\s*(.*)", comment)
    if m_scores:
        scores_str = m_scores.group(1)
        parts = scores_str.split(",")
        for part in parts:
            part = part.strip()
            m = re.match(r"(\d+-\d+)\s*\(([\d.]+)%\)", part)
            if m:
                out["top_scores"].append({
                    "score": m.group(1),
                    "pct": float(m.group(2)) / 100.0
                })
    return out


def check_enhancement_hit(enh_type: str, selection: str, hs: int, gs: int) -> bool | None:
    if hs is None or gs is None:
        return None
    sel = selection.lower()
    if enh_type == "match_over_15":
        # FIX-2 (2026-08-03, Addendum 12): plain-market scoring. The promised %
        # rendered for this market and the price captured for it are both the
        # PLAIN total, so the hit must be selection-independent. The removed
        # Win+Over combo branches measured a different market than the one
        # priced, deflating every hit-rate (and any future registry
        # certification) built on them.
        return (hs + gs) >= 2
    elif enh_type == "match_over_25":
        # FIX-2: plain-market scoring (see match_over_15).
        return (hs + gs) >= 3
    elif enh_type == "match_under_15":
        return (hs + gs) <= 1
    elif enh_type == "match_under_25":
        return (hs + gs) <= 2
    elif enh_type == "match_under_35":
        return (hs + gs) <= 3
    elif enh_type == "btts_yes":
        # FIX-2: plain-market scoring (see match_over_15).
        return hs > 0 and gs > 0
    elif enh_type == "btts_no":
        return hs == 0 or gs == 0
    elif enh_type in ("team_over_05", "home_over_05"):
        return hs >= 1 if (enh_type == "home_over_05" or sel == "home") else gs >= 1
    elif enh_type in ("team_over_15", "home_over_15"):
        return hs >= 2 if (enh_type == "home_over_15" or sel == "home") else gs >= 2
    elif enh_type == "home_over_25":
        return hs >= 3
    elif enh_type == "home_over_35":
        return hs >= 4
    elif enh_type == "home_over_45":
        return hs >= 5
    elif enh_type == "home_under_05":
        return hs == 0
    elif enh_type == "home_under_15":
        return hs <= 1
    elif enh_type == "home_under_25":
        return hs <= 2
    elif enh_type == "home_under_35":
        return hs <= 3
    elif enh_type == "home_under_45":
        return hs <= 4
    elif enh_type == "away_over_05":
        return gs >= 1
    elif enh_type == "away_over_15":
        return gs >= 2
    elif enh_type == "away_over_25":
        return gs >= 3
    elif enh_type == "away_over_35":
        return gs >= 4
    elif enh_type == "away_over_45":
        return gs >= 5
    elif enh_type == "away_under_05":
        return gs == 0
    elif enh_type == "away_under_15":
        return gs <= 1
    elif enh_type == "away_under_25":
        return gs <= 2
    elif enh_type == "away_under_35":
        return gs <= 3
    elif enh_type == "away_under_45":
        return gs <= 4
    elif enh_type == "goal_range_0_1":
        return (hs + gs) in [0, 1]
    elif enh_type == "goal_range_2_3":
        return (hs + gs) in [2, 3]
    elif enh_type == "goal_range_4_5":
        return (hs + gs) in [4, 5]
    elif enh_type == "goal_range_4_6":
        return (hs + gs) in [4, 5, 6]
    elif enh_type == "goal_range_6_plus":
        return (hs + gs) >= 6
    elif enh_type == "goal_range_7_plus":
        return (hs + gs) >= 7
    elif enh_type == "exact_0":
        return (hs + gs) == 0
    elif enh_type == "exact_1":
        return (hs + gs) == 1
    elif enh_type == "exact_2":
        return (hs + gs) == 2
    elif enh_type == "exact_3":
        return (hs + gs) == 3
    elif enh_type == "exact_4":
        return (hs + gs) == 4
    elif enh_type == "exact_5":
        return (hs + gs) == 5
    elif enh_type == "match_over_05":
        return (hs + gs) >= 1
    elif enh_type == "match_over_35":
        return (hs + gs) >= 4
    elif enh_type == "match_over_45":
        return (hs + gs) >= 5
    elif enh_type == "match_over_55":
        return (hs + gs) >= 6
    elif enh_type == "match_under_05":
        return (hs + gs) == 0
    elif enh_type == "match_under_45":
        return (hs + gs) <= 4
    elif enh_type == "match_under_55":
        return (hs + gs) <= 5
    elif enh_type == "double_chance":
        if sel == "home": # 1X
            return hs >= gs
        elif sel == "away": # X2
            return gs >= hs
        elif sel == "draw": # 12
            return hs != gs
    return None


# ---------------------------------------------------------------------------
# Full-surface audit (2026-08-03, Addendum 12)
#
# Archived picks carry two machine-readable surfaces the operator reads, but
# the legacy report only scored the single recommended enhancement:
#   - event_notes:         the full 🔥 "Possible Events" list
#                          ({market, probability, raw_probability, label, reason,
#                            engine?, cohort_n?} — engine/cohort_n from Addendum 17)
#   - statistical_comment: the active 📊 line (Avg Goals / Over 2.5 / BTTS /
#                          Home|Away Over 1.5). Legacy archives can also carry
#                          retired Top Scores; those remain machine-audited but
#                          are no longer generated, rendered, or pooled.
# Every entry on both surfaces promises a probability. The helpers below score
# EVERY promise against the settled score and aggregate per-market hit tables,
# promised-vs-realized calibration buckets, Brier scores and an Avg-Goals MAE.
#
# Doctrine: none of these numbers carries a price, so they say NOTHING about
# value. Calibration ≠ edge. They must never feed staking decisions; market
# certification remains the enhancement registry's job. The JSON shapes are
# stable (by_market / promised_buckets / avg_goals) so a later payload can
# extend load_rolling_audit_hit_rates() in picks_today.py to consume them.
# ---------------------------------------------------------------------------

# Markets whose archived label may read "{Team} Win + …" while promised %,
# captured price and scoring are all plain-market (FIX-2). Addendum 16
# (label honesty): the graded render normalizes them to PLAIN_LABELS via
# _display_label() so a settled pick never shows a HIT on "Home Win + …"
# the home side did not land.
COMBO_LABEL_MARKETS = ("match_over_15", "match_over_25", "btts_yes")

# Canonical plain-market display labels for COMBO_LABEL_MARKETS — this is
# exactly what is promised, priced and scored for these markets. Picks
# archived after 2026-08-03 carry these labels from the source
# (picks_today); _display_label() normalizes older archives at render time.
PLAIN_LABELS = {
    "match_over_15": "Match Over 1.5 Goals",
    "match_over_25": "Match Over 2.5 Goals",
    "btts_yes": "Both Teams to Score - Yes (BTTS-Yes)",
}


def _display_label(market: str | None, archive_label: str | None) -> str:
    """Render label for a scored 🔥 note.

    COMBO_LABEL_MARKETS are plain-market end-to-end (FIX-2) but were
    archived with "{Team} Win + …" wording, which renders contradictions on
    settled picks (live specimen: Kongsvinger vs Strommen 1-3, the HOME pick
    LOST, yet "Home Win + Over 1.5" graded [🟢 HIT]). Render the canonical
    plain label for those markets; every other market keeps the archived
    wording verbatim. Stored observations stay faithful to the archive —
    only display is normalized.
    """
    if market in PLAIN_LABELS:
        return PLAIN_LABELS[market]
    if archive_label:
        return str(archive_label)
    return str(market or "?")

NOTE_SCORING_DEFINITION = (
    "plain-market: a note hits iff its market lands in the final score "
    "(selection-independent for match totals and BTTS; the 1X2 selection only "
    "picks the team for team totals and the double-chance leg)"
)

STATLINE_SCORING_DEFINITION = (
    "each active metric is scored as a probabilistic forecast of its event "
    "(Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; "
    "the retired exact-score field remains in machine history only"
)


def _finite_prob(value: Any) -> float | None:
    """Coerce to a finite float in [0, 1]; NaN/Inf/junk -> None (never raises)."""
    if isinstance(value, bool):
        return None
    try:
        p = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(p) or p < 0.0 or p > 1.0:
        return None
    return p


def _bucket_label(p: float) -> str:
    """Decile bucket for a probability in [0,1] -> e.g. '0.7-0.8'."""
    lo = min(int(p * 10.0), 9) / 10.0
    return f"{lo:.1f}-{lo + 0.1:.1f}"


def _new_calibration_slot() -> dict[str, Any]:
    return {"n": 0, "hits": 0, "promised_sum": 0.0, "brier_sum": 0.0}


def _accumulate(slot: dict[str, Any], promised: float, hit: bool) -> None:
    slot["n"] += 1
    if hit:
        slot["hits"] += 1
    slot["promised_sum"] += promised
    slot["brier_sum"] += (promised - (1.0 if hit else 0.0)) ** 2


def _finalize_slot(slot: dict[str, Any]) -> dict[str, Any]:
    n = slot["n"]
    if not n:
        return {"n": 0, "hits": 0, "mean_promised": None, "realized": None,
                "delta": None, "brier": None}
    mean_promised = slot["promised_sum"] / n
    realized = slot["hits"] / n
    return {
        "n": n,
        "hits": slot["hits"],
        "mean_promised": round(mean_promised, 6),
        "realized": round(realized, 6),
        "delta": round(realized - mean_promised, 6),
        "brier": round(slot["brier_sum"] / n, 6),
    }


def score_event_notes(pick: dict[str, Any], selection: str, hs: int, gs: int) -> list[dict[str, Any]]:
    """Score every 🔥 event note on one settled pick.

    One observation per distinct note market (first note wins if a market is
    duplicated; corrupt/non-dict entries are skipped). hit=None means the
    market has no scoring definition in check_enhancement_hit().
    """
    out: list[dict[str, Any]] = []
    notes = pick.get("event_notes")
    if not isinstance(notes, list):
        return out
    seen_markets: set[str] = set()
    for note in notes:
        if not isinstance(note, dict):
            continue
        market = str(note.get("market") or "")
        if not market or market in seen_markets:
            continue
        seen_markets.add(market)
        hit = check_enhancement_hit(market, selection, hs, gs)
        out.append({
            "market": market,
            "label": str(note.get("label") or market),
            "promised": _finite_prob(note.get("probability")),
            "raw_promised": _finite_prob(note.get("raw_probability")),
            "hit": bool(hit) if hit is not None else None,
            # Addendum 17: probability provenance — notes archived before the
            # hybrid engine carry no tag and bucket as "legacy".
            "engine": str(note.get("engine") or "legacy"),
        })
    return out


def aggregate_event_notes(observations: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate note observations into per-market + pooled-bucket calibration."""
    by_market: dict[str, dict[str, Any]] = defaultdict(_new_calibration_slot)
    by_engine: dict[str, dict[str, Any]] = defaultdict(_new_calibration_slot)
    by_engine_by_market: dict[tuple[str, str], dict[str, Any]] = defaultdict(_new_calibration_slot)
    pooled: dict[str, dict[str, Any]] = defaultdict(_new_calibration_slot)
    notes_per_market: dict[str, int] = defaultdict(int)
    unscorable: dict[str, int] = defaultdict(int)
    promised_missing = 0
    for ob in observations:
        market = str(ob.get("market") or "UNKNOWN")
        notes_per_market[market] += 1
        hit = ob.get("hit")
        if hit is None:
            unscorable[market] += 1
            continue
        promised = ob.get("promised")
        if promised is None:
            promised_missing += 1
            continue
        _accumulate(by_market[market], promised, bool(hit))
        engine = str(ob.get("engine") or "legacy")
        _accumulate(by_engine[engine], promised, bool(hit))
        _accumulate(by_engine_by_market[(engine, market)], promised, bool(hit))
        _accumulate(pooled[_bucket_label(promised)], promised, bool(hit))
    return {
        "definition": NOTE_SCORING_DEFINITION,
        "total_notes": len(observations),
        "scored": sum(slot["n"] for slot in by_market.values()) + promised_missing,
        "promised_missing": promised_missing,
        "unscorable": dict(sorted(unscorable.items())),
        "by_market": {
            m: {**_finalize_slot(by_market[m]), "notes": notes_per_market[m]}
            for m in sorted(by_market)
        },
        # Addendum 17: grade the probability engines against each other
        # (model | hybrid_cohort | legacy) on their own promises.
        "by_engine": {
            eng: _finalize_slot(slot) for eng, slot in sorted(by_engine.items())
        },
        # Engine x market cells (Addendum 17 + 19): the per-engine, per-market
        # promised-vs-realized read the debias rule requires. Pooled-by-engine
        # deltas alone cannot decide whether hybrid notes should be gated at
        # hr=1.0; the market-level split can. Audit-only; no policy effect.
        "by_engine_by_market": {
            eng: {
                m: _finalize_slot(by_engine_by_market[(eng, m)])
                for (e, m) in sorted(by_engine_by_market)
                if e == eng
            }
            for eng in sorted({e for e, _ in by_engine_by_market})
        },
        "promised_buckets": [
            {"bucket": label, **_finalize_slot(slot)}
            for label, slot in sorted(pooled.items())
        ],
    }


def score_statline(parsed_stats: dict[str, Any], hs: int, gs: int) -> list[dict[str, Any]]:
    """Score every promised metric of the 📊 line as a probabilistic forecast."""
    out: list[dict[str, Any]] = []
    metrics = (
        ("over25", (hs + gs) >= 3),
        ("btts", hs > 0 and gs > 0),
        ("home_o15", hs >= 2),
        ("away_o15", gs >= 2),
    )
    for name, hit in metrics:
        promised = _finite_prob(parsed_stats.get(name))
        if promised is None:
            continue
        out.append({"metric": name, "promised": promised, "hit": bool(hit)})
    actual_score = f"{hs}-{gs}"
    for item in parsed_stats.get("top_scores") or []:
        if not isinstance(item, dict):
            continue
        promised = _finite_prob(item.get("pct"))
        if promised is None:
            continue
        out.append({"metric": "top_score", "promised": promised,
                    "hit": str(item.get("score") or "") == actual_score})
    return out


def aggregate_statline(observations: list[dict[str, Any]],
                       goal_forecasts: list[tuple[float, float]] | None = None) -> dict[str, Any]:
    """Aggregate 📊 observations into per-metric + pooled-bucket calibration
    plus the Avg-Goals point-forecast error (MAE / bias)."""
    by_metric: dict[str, dict[str, Any]] = defaultdict(_new_calibration_slot)
    pooled: dict[str, dict[str, Any]] = defaultdict(_new_calibration_slot)
    for ob in observations:
        promised, hit = ob.get("promised"), ob.get("hit")
        if promised is None or hit is None:
            continue
        metric = str(ob.get("metric") or "UNKNOWN")
        _accumulate(by_metric[metric], promised, bool(hit))
        # Preserve retired Top Scores in machine-readable by_metric history,
        # but do not let them distort active pooled calibration.
        if metric != "top_score":
            _accumulate(pooled[_bucket_label(promised)], promised, bool(hit))
    avg_goals = None
    if goal_forecasts:
        n = len(goal_forecasts)
        mae = sum(abs(actual - promised) for promised, actual in goal_forecasts) / n
        bias = sum(actual - promised for promised, actual in goal_forecasts) / n
        mean_p = sum(p for p, _ in goal_forecasts) / n
        mean_a = sum(a for _, a in goal_forecasts) / n
        avg_goals = {"n": n, "mae": round(mae, 6), "bias": round(bias, 6),
                     "mean_promised": round(mean_p, 6), "mean_actual": round(mean_a, 6)}
    return {
        "definition": STATLINE_SCORING_DEFINITION,
        "by_metric": {m: _finalize_slot(by_metric[m]) for m in sorted(by_metric)},
        "promised_buckets": [
            {"bucket": label, **_finalize_slot(slot)}
            for label, slot in sorted(pooled.items())
        ],
        "avg_goals": avg_goals,
    }


def _pct(value: Any) -> str:
    if isinstance(value, bool):
        return "n/a"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not math.isfinite(v):
        return "n/a"
    return f"{v:.1%}"


def _signed_pct(value: Any) -> str:
    if isinstance(value, bool):
        return "n/a"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "n/a"
    if not math.isfinite(v):
        return "n/a"
    return f"{v:+.1%}"


def _event_actual_context(market: Any, selection: str, hs: int, gs: int) -> str:
    """Short realized context for a graded 🔥 line, mirroring the 📊 style."""
    m = str(market or "")
    sel = str(selection or "")
    if m.startswith("team_"):
        side_home = sel == "home"
        return f"{hs if side_home else gs} {'home' if side_home else 'away'} goals"
    if m.startswith("home_"):
        return f"{hs} home goals"
    if m.startswith("away_"):
        return f"{gs} away goals"
    if m.startswith("btts_"):
        return "BTTS-Yes" if (hs > 0 and gs > 0) else "BTTS-No"
    if m == "double_chance":
        outcome = "home" if hs > gs else "draw" if hs == gs else "away"
        return f"{outcome} ({hs}-{gs})"
    return f"{hs + gs} goals"


def _render_event_notes_section(aud: dict[str, Any]) -> list[str]:
    lines = [
        "## Possible Events (🔥) Full-Surface Audit",
        "",
        "> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. "
        "Certification and staking remain gated by the enhancement registry.",
        "",
        "> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only "
        "high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails "
        "promised on display-filtered markets — part of any promised−realized gap here is "
        "the selection effect of the display filter, not engine error.",
        "",
        "Every machine-readable 🔥 note on every settled pick in the window, scored against the "
        f"final score ({NOTE_SCORING_DEFINITION}).",
        "",
    ]
    if not aud or not aud.get("total_notes"):
        lines.append("- (no settled picks carried machine-readable 🔥 event notes in this window)")
        lines.append("")
        return lines
    unsc = aud.get("unscorable") or {}
    unsc_total = sum(unsc.values())
    summary = (f"- notes on settled picks: **{aud.get('total_notes', 0)}** | "
               f"scored: {aud.get('scored', 0)}")
    if unsc_total:
        summary += f" | unscorable (no outcome definition): {unsc_total} {unsc}"
    if aud.get("promised_missing"):
        summary += f" | without promised % (legacy rows): {aud['promised_missing']}"
    lines.append(summary)
    lines.append("")
    by_market = aud.get("by_market") or {}
    if by_market:
        lines.extend([
            "### Per-market hit table",
            "",
            "| market | notes | n | hits | realized | promised avg | Δ | Brier |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ])
        for market, slot in sorted(by_market.items(), key=lambda kv: (-kv[1].get("n", 0), kv[0])):
            low_n = " ⚠️low-n" if slot.get("n", 0) < 5 else ""
            brier = slot.get("brier")
            lines.append(
                f"| `{market}` | {slot.get('notes', slot.get('n', 0))} | {slot.get('n', 0)} | "
                f"{slot.get('hits', 0)} | {_pct(slot.get('realized'))} | {_pct(slot.get('mean_promised'))} | "
                f"{_signed_pct(slot.get('delta'))} | {brier if brier is not None else 'n/a'}{low_n} |"
            )
        lines.append("")
        labels_mapping = "; ".join(f"`{m}` → \"{PLAIN_LABELS[m]}\"" for m in COMBO_LABEL_MARKETS)
        lines.append(
            "Labels render plain-market exactly as promised, priced and scored: "
            "" + labels_mapping + ". Raw archive labels written before 2026-08-03 may still "
            "carry the old \"Win + …\" wording in their stored label field; the render normalizes them."
        )
        lines.append("")
    engines = aud.get("by_engine") or {}
    if engines:
        lines.extend([
            "### By probability engine (🔥)",
            "",
            "> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned "
            "empirical cohort anchor · `legacy` = archived before engine tagging.",
            "",
            "| engine | n | hits | realized | promised avg | Δ | Brier |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ])
        for eng, slot in sorted(engines.items(), key=lambda kv: (-kv[1].get("n", 0), kv[0])):
            brier = slot.get("brier")
            lines.append(
                f"| {eng} | {slot.get('n', 0)} | {slot.get('hits', 0)} | {_pct(slot.get('realized'))} | "
                f"{_pct(slot.get('mean_promised'))} | {_signed_pct(slot.get('delta'))} | "
                f"{brier if brier is not None else 'n/a'} |"
            )
        lines.append("")
        lines.append("")
    buckets = aud.get("promised_buckets") or []
    if buckets:
        lines.extend([
            "### Promised-vs-realized calibration (all 🔥 notes pooled)",
            "",
            "| promised bucket | n | promised avg | realized | Δ |",
            "| --- | --- | --- | --- | --- |",
        ])
        for slot in buckets:
            lines.append(
                f"| {slot.get('bucket')} | {slot.get('n', 0)} | {_pct(slot.get('mean_promised'))} | "
                f"{_pct(slot.get('realized'))} | {_signed_pct(slot.get('delta'))} |"
            )
        lines.append("")
    return lines


def _render_statline_section(cal: dict[str, Any]) -> list[str]:
    lines = [
        "## Statistical Line (📊) Calibration",
        "",
        "> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — "
        "this section scores promise vs realization only and must not drive staking.",
        "",
        f"Scored as probabilistic forecasts per settled pick ({STATLINE_SCORING_DEFINITION}).",
        "",
    ]
    by_metric = cal.get("by_metric") or {}
    active_by_metric = {key: value for key, value in by_metric.items() if key != "top_score"}
    avg_goals = cal.get("avg_goals")
    buckets = cal.get("promised_buckets") or []
    if not active_by_metric and not avg_goals and not buckets:
        lines.append("- (no settled picks carried a parseable 📊 statistical comment in this window)")
        lines.append("")
        return lines
    if avg_goals:
        lines.append(
            f"- **Avg Goals forecast**: n={avg_goals.get('n', 0)}, "
            f"MAE={avg_goals.get('mae')} goals, bias={avg_goals.get('bias')} (realized − promised), "
            f"promised avg {avg_goals.get('mean_promised')} vs realized {avg_goals.get('mean_actual')}"
        )
        lines.append("")
    if active_by_metric:
        label_map = {"over25": "Over 2.5", "btts": "BTTS-Yes", "home_o15": "Home Over 1.5",
                     "away_o15": "Away Over 1.5"}
        lines.extend([
            "### Per-metric calibration",
            "",
            "| metric | n | promised avg | realized | Δ | Brier |",
            "| --- | --- | --- | --- | --- | --- |",
        ])
        for metric, slot in sorted(active_by_metric.items(), key=lambda kv: (-kv[1].get("n", 0), kv[0])):
            low_n = " ⚠️low-n" if slot.get("n", 0) < 5 else ""
            brier = slot.get("brier")
            lines.append(
                f"| {label_map.get(metric, metric)} | {slot.get('n', 0)} | {_pct(slot.get('mean_promised'))} | "
                f"{_pct(slot.get('realized'))} | {_signed_pct(slot.get('delta'))} | "
                f"{brier if brier is not None else 'n/a'}{low_n} |"
            )
        lines.append("")
    if buckets:
        lines.extend([
            "### Promised-vs-realized calibration (all 📊 metrics pooled)",
            "",
            "| promised bucket | n | promised avg | realized | Δ |",
            "| --- | --- | --- | --- | --- |",
        ])
        for slot in buckets:
            lines.append(
                f"| {slot.get('bucket')} | {slot.get('n', 0)} | {_pct(slot.get('mean_promised'))} | "
                f"{_pct(slot.get('realized'))} | {_signed_pct(slot.get('delta'))} |"
            )
        lines.append("")
    return lines


def build_report(start: str, end: str, warehouse_path: Path, *, include_same_day: bool = False) -> dict[str, Any]:
    picks, archive_receipt = load_archived_picks_with_receipt(start, end)
    picks = dedupe_archived_picks(picks)
    results, results_by_date = load_results_index(warehouse_path)
    dispositions = load_event_disposition_index(warehouse_path, start=start, end=end)
    settled_rows: list[SettledPick] = []
    settled_pairs: list[tuple[SettledPick, dict[str, Any]]] = []  # (row, archived pick) for veto_deep_dive
    archived_dates = sorted({str(p.get("date") or "")[:10] for p in picks if p.get("date")})
    today_local = local_today()
    same_day_excluded = 0
    eligible_prior_picks = 0
    unmatched_result_examples: list[dict[str, Any]] = []
    rescheduled_result_examples: list[dict[str, Any]] = []
    voided_event_examples: list[dict[str, Any]] = []
    ambiguous_disposition_examples: list[dict[str, Any]] = []
    voided_by_disposition: Counter[str] = Counter()
    overlay_rescued = 0
    ambiguous_result_examples: list[dict[str, Any]] = []

    # Dynamic Secondary Market realized stats counters
    sec_stats = {
        "over25_wins": 0, "over25_total": 0,
        "btts_wins": 0, "btts_total": 0,
        "team_o15_wins": 0, "team_o15_total": 0,
    }

    # Dynamic Enhancement Auditing counters
    enh_stats = {
        "total_recommended": 0,
        "total_hits": 0,
        "by_enhancement": defaultdict(lambda: {"recommended": 0, "hits": 0,
                                               "priced_n": 0, "priced_hits": 0,
                                               "priced_profit": 0.0})
    }
    priced_outcomes: list[dict] = []  # settled outcomes with REAL captured prices (registry feed)

    # Full-surface audit collectors (Addendum 12): every 🔥 note and every 📊
    # promised metric on every settled pick — not just the one recommendation.
    note_observations: list[dict] = []
    statline_observations: list[dict] = []
    goal_forecasts: list[tuple[float, float]] = []

    # RT-1 (red-team 2026-08-03): enhancement scoring must read prices from the
    # IMMUTABLE capture store (localdata/theoddsapi_odds_YYYY-MM.csv.gz), never
    # from archived pick fields. Morning snapshots are frozen before the close
    # capture exists, and the intraday ledger merge retains locked picks verbatim
    # (anti-drift), so archived enhancement_price fields can never carry the close
    # price — scoring off them would starve the registry. Probing raw capture rows
    # per pick-date yields one consistent definition for every metric below and
    # for the registry: best captured theoddsapi price for (date, pair, market).
    try:
        from edgefactory import enh_pricing as _enh_pricing
    except Exception:
        _enh_pricing = None
    _prices_by_day: dict[str, dict] = {}

    # Detailed ledger of settled picks and their granular expectations audits
    settled_ledger = []

    for pick in picks:
        pick_date = str(pick.get("date") or "")[:10]
        if not include_same_day and pick_date >= today_local:
            same_day_excluded += 1
            continue
        market = str(pick.get("market") or "")
        selection = str(pick.get("pick") or "")
        valid_selections = {
            "1x2": {"home", "draw", "away"},
            "ou_2.5": {"over", "under"},
            "btts": {"yes", "no"},
        }.get(market)
        if valid_selections is None or selection not in valid_selections:
            continue
        eligible_prior_picks += 1

        result = None
        pick_home = str(pick.get("home") or "")
        pick_away = str(pick.get("away") or "")

        # Exact/candidate-key hits (priority-deduped warehouse + overlay).
        exact_matches: list[dict[str, Any]] = []
        for hk in audit_team_key_candidates(pick.get("home")):
            for ak in audit_team_key_candidates(pick.get("away")):
                candidate = results.get((pick_date, hk, ak))
                if candidate is not None and candidate not in exact_matches:
                    exact_matches.append(candidate)

        # Alias-conflict scan (cross-spelling, orientation-checked): a fixture
        # filed under several spellings with differing outcomes (Pafos vs
        # Dinamo Tirana 2-2 draw vs Pafos vs KS Dinamo Tirana 4-2 home) must
        # surface as ambiguous, not silently first-win the exact-key spelling.
        alias_matches = _alias_candidate_results(pick_home, pick_away, pick_date, results_by_date)

        candidates: list[dict[str, Any]] = []
        for r in exact_matches + alias_matches:
            if r not in candidates:
                candidates.append(r)

        distinct_scores = {(r.get("hs"), r.get("gs"), r.get("outcome")) for r in candidates}
        if len(distinct_scores) > 1:
            ambiguous_result_examples.append(_pick_diag(pick, "ambiguous_alias_result"))
            continue

        if candidates:
            # Prefer the exact-key hit for provenance; all outcomes agree here.
            result = exact_matches[0] if exact_matches else candidates[0]

        if result is None:
            # Event dispositions are deliberately exact-only. A false void is
            # worse than a pending row, so no fuzzy postponed/cancelled match.
            disposition_hits: list[dict[str, Any]] = []
            for hk in audit_team_key_candidates(pick.get("home")):
                for ak in audit_team_key_candidates(pick.get("away")):
                    candidate = dispositions.get((pick_date, hk, ak))
                    if candidate is not None:
                        disposition_hits.append(candidate)
            unique_dispositions = {
                (str(item.get("disposition")), str(item.get("origin")))
                for item in disposition_hits
            }
            if len({item[0] for item in unique_dispositions}) == 1 and unique_dispositions:
                disposition, origin = sorted(unique_dispositions)[0]
                diag = _pick_diag(pick, "void_event")
                diag.update({"disposition": disposition, "origin": origin})
                voided_event_examples.append(diag)
                voided_by_disposition[disposition] += 1
                continue
            if len({item[0] for item in unique_dispositions}) > 1:
                diag = _pick_diag(pick, "ambiguous_event_disposition")
                diag["dispositions"] = sorted(unique_dispositions)
                ambiguous_disposition_examples.append(diag)

            results_on_date = results_by_date.get(pick_date, [])
            fuzzy_matches = find_fuzzy_result_matches(pick_home, pick_away, results_on_date)
            fuzzy_scores = {(r.get("hs"), r.get("gs"), r.get("outcome")) for r in fuzzy_matches}
            if len(fuzzy_scores) > 1:
                ambiguous_result_examples.append(_pick_diag(pick, "ambiguous_alias_result"))
                continue
            if fuzzy_matches:
                result = max(
                    fuzzy_matches,
                    key=lambda r: char_ngram_similarity(
                        f"{pick_home} {pick_away}",
                        f"{r.get('home', '')} {r.get('away', '')}",
                        n=2,
                    ),
                )
            else:
                rescheduled = _find_rescheduled_result(pick, pick_date, results)
                if rescheduled is not None:
                    rescheduled_result_examples.append(rescheduled)
                    continue
                unmatched_result_examples.append(_pick_diag(pick, "pending_or_unmatched_result"))
                continue

        settled = settle_pick(pick, result)
        if settled is not None:
            if result.get("origin") == "overlay":
                overlay_rescued += 1
            settled_rows.append(settled)
            settled_pairs.append((settled, pick))

            # Score secondary markets on this settled match. This realized-rates
            # table is measured on the 1X2 consensus slate only: an OU/BTTS row
            # is a *separate pick on the same fixture*, so counting it here would
            # double-count fixtures that carry both a 1X2 and an OU/BTTS pick.
            hs = result.get("hs")
            gs = result.get("gs")
            if hs is not None and gs is not None:
                if market == "1x2":
                    # 1. Over 2.5 goals
                    sec_stats["over25_total"] += 1
                    if hs + gs >= 3:
                        sec_stats["over25_wins"] += 1

                    # 2. Both teams to score
                    sec_stats["btts_total"] += 1
                    if hs > 0 and gs > 0:
                        sec_stats["btts_wins"] += 1

                    # 3. Selected team over 1.5 goals
                    if selection in ("home", "away"):
                        sec_stats["team_o15_total"] += 1
                        selected_goals = hs if selection == "home" else gs
                        if selected_goals >= 2:
                            sec_stats["team_o15_wins"] += 1

                # 4. Recommended enhancement hit check
                enh_type = pick.get("recommended_enhancement")
                if enh_type:
                    hit = check_enhancement_hit(enh_type, selection, hs, gs)
                    if hit is not None:
                        enh_stats["total_recommended"] += 1
                        if hit:
                            enh_stats["total_hits"] += 1
                        
                        slot = enh_stats["by_enhancement"][enh_type]
                        slot["recommended"] += 1
                        if hit:
                            slot["hits"] += 1
                        # Price from the immutable capture store (RT-1 above), not
                        # from the archived presentation-time field.
                        price = None
                        price_source = ""
                        if _enh_pricing is not None and pick_date:
                            if pick_date not in _prices_by_day:
                                _prices_by_day[pick_date] = _enh_pricing.load_prices_index(ROOT, pick_date)
                            probe = {"home": pick.get("home"), "away": pick.get("away"),
                                     "recommended_enhancement": enh_type}
                            _enh_pricing.attach_enhancement_price(probe, _prices_by_day[pick_date])
                            price = probe.get("enhancement_price")
                            price_source = probe.get("enhancement_price_source") or ""
                        if (isinstance(price, (int, float)) and not isinstance(price, bool)
                                and math.isfinite(price) and price > 1.0):
                            slot["priced_n"] += 1
                            if hit:
                                slot["priced_hits"] += 1
                            slot["priced_profit"] += (price - 1.0) if hit else -1.0
                            priced_outcomes.append({
                                "date": str(pick_date), "match": pick.get("match") or "",
                                "market": enh_type, "price": float(price), "hit": bool(hit),
                                "source": price_source,
                                # governance N5 (Addendum 27.11): whether >=2
                                # distinct sources priced this exact selection.
                                "multi_source": bool(probe.get("enhancement_multi_source")),
                            })

                # 5. Granular expectations audit ledger populator
                # (full-surface: score the pick's 🔥 notes ONCE here so the
                # per-pick graded render and the aggregate tables share the
                # exact same observations — one definition, no divergence).
                notes_for_pick = score_event_notes(pick, selection, hs, gs)
                comment = pick.get("statistical_comment")
                parsed_stats = parse_statistical_comment(comment)
                
                o25_hit = None
                if parsed_stats["over25"] is not None:
                    o25_hit = (hs + gs) >= 3
                    
                btts_hit = None
                if parsed_stats["btts"] is not None:
                    # FIX-1 (2026-08-03): parsed fractions are 0..1 (parser
                    # divides by 100.0); the legacy 50.0 cut was never True, so
                    # every BTTS expectation was scored as BTTS-No and the
                    # HIT/MISS icons were inverted for BTTS-Yes expectations.
                    expected_btts_yes = parsed_stats["btts"] >= 0.50
                    actual_btts_yes = hs > 0 and gs > 0
                    btts_hit = actual_btts_yes if expected_btts_yes else not actual_btts_yes
                    
                home_o15_hit = None
                if parsed_stats["home_o15"] is not None:
                    expected_over = parsed_stats["home_o15"] >= 0.50
                    actual_over = hs >= 2
                    home_o15_hit = actual_over if expected_over else not actual_over
                    
                away_o15_hit = None
                if parsed_stats["away_o15"] is not None:
                    expected_over = parsed_stats["away_o15"] >= 0.50
                    actual_over = gs >= 2
                    away_o15_hit = actual_over if expected_over else not actual_over
                    
                top_scores_audited = []
                for item in parsed_stats["top_scores"]:
                    actual_score = f"{hs}-{gs}"
                    hit = item["score"] == actual_score
                    top_scores_audited.append({
                        "score": item["score"],
                        "pct": item["pct"],
                        "hit": hit
                    })
                    
                settled_ledger.append({
                    "date": pick_date,
                    "match": pick.get("match") or f"{pick.get('home')} vs {pick.get('away')}",
                    "market": market,
                    "selection": selection,
                    "avg_p": pick.get("avg_p") or 0.0,
                    "hs": hs,
                    "gs": gs,
                    "outcome": settled.outcome,
                    "won": settled.won,
                    "odds": pick.get("odds"),
                    "odds_source": settled.odds_source,
                    "odds_match_method": settled.odds_match_method,
                    "price_evidence": settled.price_evidence,
                    "price_quarantine_reason": settled.price_quarantine_reason,
                    "suspect_price": settled.suspect_price,
                    "parsed_stats": {
                        "over25_expected": parsed_stats["over25"],
                        "over25_hit": o25_hit,
                        "btts_expected": parsed_stats["btts"],
                        "btts_hit": btts_hit,
                        "home_o15_expected": parsed_stats["home_o15"],
                        "home_o15_hit": home_o15_hit,
                        "away_o15_expected": parsed_stats["away_o15"],
                        "away_o15_hit": away_o15_hit,
                        "top_scores": top_scores_audited
                    },
                    "notes_audit": notes_for_pick,
                })

                # 6. Full-surface audit (Addendum 12): score EVERY 🔥 note and
                # every 📊 promised metric on this settled pick — the legacy
                # sections above only score the single recommended enhancement.
                note_observations.extend(notes_for_pick)
                statline_observations.extend(score_statline(parsed_stats, hs, gs))
                avg_goals_promised = parsed_stats.get("avg_goals")
                if (isinstance(avg_goals_promised, (int, float))
                        and not isinstance(avg_goals_promised, bool)
                        and math.isfinite(avg_goals_promised)):
                    goal_forecasts.append((float(avg_goals_promised), float(hs + gs)))

    serialized_by_enhancement = {}
    for enh, stats in enh_stats["by_enhancement"].items():
        rec = stats["recommended"]
        hits = stats["hits"]
        p_n = stats.get("priced_n", 0)
        p_profit = stats.get("priced_profit", 0.0)
        serialized_by_enhancement[enh] = {
            "recommended": rec,
            "hits": hits,
            "hit_rate": round(hits / rec, 6) if rec else 0.0,
            "priced_n": p_n,
            "priced_hits": stats.get("priced_hits", 0),
            "priced_roi": round(p_profit / p_n, 6) if p_n else None,
        }

    serialized_enh_audit = {
        "total_recommended": enh_stats["total_recommended"],
        "total_hits": enh_stats["total_hits"],
        "hit_rate": round(enh_stats["total_hits"] / enh_stats["total_recommended"], 6) if enh_stats["total_recommended"] else None,
        "by_enhancement": serialized_by_enhancement
    }

    # Enhancement certification registry: feed priced settled outcomes (idempotent,
    # fail-soft) and snapshot states for the report. Unpriced outcomes never advance
    # certification — probability without price is not evidence of value.
    registry_states: dict[str, str] = {}
    try:
        from edgefactory.enh_registry import all_statuses, record_outcome
        for oc in priced_outcomes:
            record_outcome(ROOT, date_=oc["date"], match=oc["match"], market=oc["market"],
                           price=oc["price"], hit=oc["hit"], source=oc["source"],
                           multi_source=oc.get("multi_source", False))
        registry_states = all_statuses(ROOT)
    except Exception:
        registry_states = {}

    return {
        "start": start,
        "end": end,
        "archived_pick_rows": len(picks),
        "archived_pick_dates": archived_dates,
        "morning_baseline_rows": archive_receipt["morning_baseline_rows"],
        "verified_late_additions": archive_receipt["verified_late_additions"],
        "regular_only_rows": archive_receipt["regular_only_rows"],
        "unsafe_regular_ledger_dates": archive_receipt["unsafe_regular_ledger_dates"],
        "empty_regular_ledger_dates": archive_receipt.get("empty_regular_ledger_dates", []),
        "same_day_excluded": same_day_excluded,
        "same_day_cutoff": today_local,
        "include_same_day": include_same_day,
        "eligible_prior_picks": eligible_prior_picks,
        "unmatched_result_picks": len(unmatched_result_examples),
        "pending_result_picks": len(unmatched_result_examples),
        "rescheduled_result_picks": len(rescheduled_result_examples),
        "voided_event_picks": len(voided_event_examples),
        "by_event_disposition": dict(sorted(voided_by_disposition.items())),
        "voided_event_examples": voided_event_examples[:50],
        "ambiguous_disposition_picks": len(ambiguous_disposition_examples),
        "ambiguous_disposition_examples": ambiguous_disposition_examples[:50],
        "settled_via_overlay_picks": overlay_rescued,
        "ambiguous_result_picks": len(ambiguous_result_examples),
        "unmatched_examples": unmatched_result_examples[:50],
        "rescheduled_examples": rescheduled_result_examples[:50],
        "ambiguous_examples": ambiguous_result_examples[:50],
        "overall": summarize_scored(settled_rows),
        "by_rule": summarize_by(settled_rows, "rule_name"),
        "by_bucket": summarize_by(settled_rows, "bucket"),
        # Addendum 27.14: the flagship number under interrogation — evidence,
        # odds-band and veto-reason composition of the best-ROI bucket.
        "veto_deep_dive": build_veto_deep_dive(settled_pairs),
        "by_odds_source": summarize_by(settled_rows, "odds_source"),
        "by_odds_match_method": summarize_by(settled_rows, "odds_match_method"),
        # Addendum 26: first-class tables for the two pricing interrogations.
        "by_price_evidence": summarize_by(settled_rows, "price_evidence"),
        "by_price_quarantine_reason": summarize_quarantine_by(
            settled_rows, "price_quarantine_reason"
        ),
        "secondary_stats": sec_stats,
        "enhancements_audit": serialized_enh_audit,
        "enhancement_registry": registry_states,
        "settled_ledger": settled_ledger,
        "event_notes_audit": aggregate_event_notes(note_observations),
        "statline_calibration": aggregate_statline(statline_observations, goal_forecasts),
    }


def _summary_pct(v, nd=1):
    """Format headline hit rate / ROI with an explicit sign.

    Keep this separate from the earlier unsigned ``_pct`` probability helper.
    Reusing the same name silently changed every calibration and per-pick
    probability to a signed ``+81.5%`` string at function-call time.
    """
    if v is None:
        return "-"
    try:
        return f"{float(v)*100:+.{nd}f}%"
    except (TypeError, ValueError):
        return str(v)


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    overall = report.get("overall", {})
    lines = [
        f"# Edge Factory — Recent picks audit ({report['start']} to {report['end']})",
        "",
        "## Overall",
        "",
        f"- archived pick rows: {report.get('archived_pick_rows', 0)}",
        f"- archived pick dates: {len(report.get('archived_pick_dates', []))}",
        f"- immutable morning-baseline rows: {report.get('morning_baseline_rows', 0)}",
        f"- verified official late-slate additions: {report.get('verified_late_additions', 0)}",
        f"- regular-ledger-only legacy rows: {report.get('regular_only_rows', 0)}",
        f"- unsafe regular ledgers ignored: {len(report.get('unsafe_regular_ledger_dates', []))}",
        "- empty regular ledgers (morning-baseline coverage only): "
        f"{len(report.get('empty_regular_ledger_dates', []))}"
        + (
            f" ({', '.join(report['empty_regular_ledger_dates'])})"
            if report.get("empty_regular_ledger_dates")
            else ""
        ),
        f"- settled picks: {overall.get('settled_picks', 0)}",
        f"- eligible prior picks: {report.get('eligible_prior_picks', 0)}",
        f"- pending/unmatched result picks: {report.get('pending_result_picks', report.get('unmatched_result_picks', 0))}",
        f"- rescheduled result picks (settled ±3d): {report.get('rescheduled_result_picks', 0)}",
        f"- voided postponed/cancelled/abandoned events: {report.get('voided_event_picks', 0)}",
        f"- ambiguous event-disposition rows: {report.get('ambiguous_disposition_picks', 0)}",
        f"- settled via shared overlay facts: {report.get('settled_via_overlay_picks', 0)}",
        f"- ambiguous result picks: {report.get('ambiguous_result_picks', 0)}",
        f"- wins: {overall.get('wins', 0)}",
        f"- hit rate: {_summary_pct(overall.get('hit_rate'))}",
        f"- priced picks: {overall.get('priced_picks', 0)}",
        f"- ROI: {_summary_pct(overall.get('roi'))}",
        "",
        "## Settlement policy",
        "",
        f"- include same-day picks: {report.get('include_same_day')}",
        f"- same-day cutoff date: {report.get('same_day_cutoff')}",
        f"- same-day rows excluded: {report.get('same_day_excluded', 0)}",
        "",
    ]
    
    # Render Secondary Market realized stats
    sec = report.get("secondary_stats", {})
    if sec and sec.get("over25_total", 0) > 0:
        over25_wins = sec.get("over25_wins", 0)
        over25_total = sec.get("over25_total", 0)
        over25_pct = over25_wins / over25_total
        
        btts_wins = sec.get("btts_wins", 0)
        btts_total = sec.get("btts_total", 0)
        btts_pct = btts_wins / btts_total
        
        team_o15_wins = sec.get("team_o15_wins", 0)
        team_o15_total = sec.get("team_o15_total", 0)
        team_o15_pct = team_o15_wins / team_o15_total
        
        lines.extend([
            "## Secondary Market Realized Rates",
            "",
            "Metrics scored against actual outcomes of the settled consensus picks in this window:",
            f"- **Over 2.5 Goals**: occurred in {over25_wins} / {over25_total} matches ({over25_pct:.1%})",
            f"- **Both Teams to Score (BTTS)**: occurred in {btts_wins} / {btts_total} matches ({btts_pct:.1%})",
            f"- **Selected Team Over 1.5 Goals**: occurred in {team_o15_wins} / {team_o15_total} matches ({team_o15_pct:.1%})",
            "",
        ])

    # Render Recommended Enhancements Audit
    enh_aud = report.get("enhancements_audit", {})
    if enh_aud and enh_aud.get("total_recommended", 0) > 0:
        total_rec = enh_aud.get("total_recommended", 0)
        total_hits = enh_aud.get("total_hits", 0)
        overall_rate = enh_aud.get("hit_rate", 0.0)
        
        lines.extend([
            "## Recommended Enhancements Audit",
            "",
            "Performance of deep context-derived recommended enhancements overlay:",
            f"- **Total Recommended Enhancements**: {total_rec}",
            f"- **Total Hits**: {total_hits}",
            f"- **Overall Hit Rate**: {overall_rate:.1%}",
            "",
            "### Breakdown by Enhancement Type:",
        ])
        by_enh = enh_aud.get("by_enhancement", {})
        if not by_enh:
            lines.append("- (none)")
        else:
            for key, summary in sorted(by_enh.items()):
                rec = summary.get("recommended", 0)
                hits = summary.get("hits", 0)
                hr = summary.get("hit_rate", 0.0)
                lines.append(f"- `{key}`: recommended={rec}, hits={hits}, hit_rate={hr:.1%}")
        lines.append("")

    # Full-surface audit sections (Addendum 12)
    lines.extend(_render_event_notes_section(report.get("event_notes_audit") or {}))
    lines.extend(_render_statline_section(report.get("statline_calibration") or {}))

    lines.extend(["## By rule", ""])
    by_rule = report.get("by_rule", {})
    if not by_rule:
        lines.append("- none")
    else:
        for key, summary in by_rule.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    lines.extend(["", "## By bucket", ""])
    by_bucket = report.get("by_bucket", {})
    if not by_bucket:
        lines.append("- none")
    else:
        for key, summary in by_bucket.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    lines.extend(["", "## By odds source", ""])
    by_source = report.get("by_odds_source", {})
    if not by_source:
        lines.append("- none")
    else:
        for key, summary in by_source.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )
    lines.extend(["", "## By odds match method", ""])
    by_method = report.get("by_odds_match_method", {})
    if not by_method:
        lines.append("- none")
    else:
        for key, summary in by_method.items():
            lines.append(
                f"- `{key}`: settled={summary.get('settled_picks', 0)}, wins={summary.get('wins', 0)}, hit_rate={summary.get('hit_rate')}, ROI={summary.get('roi')}"
            )

    # Addendum 26: these are deliberately separate from raw source/method
    # breakdowns. They answer the two pre-registered interrogation questions:
    # which price evidence was allowed to speak, and which rows were quarantined
    # because their displayed price was not safe to push.
    evidence_labels = {
        "BZZOIRO_PRIMARY": "Bzzoiro primary match",
        "SCOUTINGSTATS_SOLE": "ScoutingStats sole fallback",
        "SUSPECT_ALIAS_FUZZY": "Suspect alias_fuzzy candidate",
        "BETEXPLORER_RESCUE": "BetExplorer rescue",
        "SOURCE_FALLBACK": "Source fallback",
        "UNMATCHED": "No usable price",
    }
    lines.extend([
        "",
        "## Price Evidence / Corroboration Audit",
        "",
        "> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit "
        "but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed "
        "to replace operational best odds.",
        "",
        "| price evidence | settled | wins | hit rate | priced | ROI |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    by_evidence = report.get("by_price_evidence", {})
    if not by_evidence:
        lines.append("| none | 0 | 0 | n/a | 0 | n/a |")
    else:
        for key, summary in by_evidence.items():
            lines.append(
                f"| {evidence_labels.get(key, key)} (`{key}`) | "
                f"{summary.get('settled_picks', 0)} | {summary.get('wins', 0)} | "
                f"{summary.get('hit_rate')} | {summary.get('priced_picks', 0)} | {summary.get('roi')} |"
            )

    # Addendum 27.14: the flagship number under interrogation. A blended ROI
    # cannot steer staking policy until its composition is known.
    veto_dd = report.get("veto_deep_dive", {}) or {}

    def _dd_row(name: str, summary: dict[str, Any] | None) -> None:
        summary = summary or {}
        lines.append(
            f"| {name} | {summary.get('settled_picks', 0)} | {summary.get('wins', 0)} | "
            f"{summary.get('hit_rate')} | {summary.get('priced_picks', 0)} | {summary.get('roi')} |"
        )

    lines.extend([
        "",
        "## Veto Deep Dive",
        "",
        "> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, "
        "> computed from the SAME settled rows as the bucket table. "
        "> `trusted evidence only` excludes the soft labels: "
        f"> {', '.join(veto_dd.get('soft_evidence_labels', []))}.",
        "",
        "| cut | settled | wins | hit rate | priced | ROI |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    if not veto_dd:
        _dd_row("n/a", None)
    else:
        _dd_row(f"**overall ({veto_dd.get('focus_bucket', 'SKIPPED_VETO')})**", veto_dd.get("overall"))
        _dd_row("**trusted evidence only**", veto_dd.get("trusted_evidence_only"))
        _dd_row("**soft evidence only**", veto_dd.get("soft_evidence_only"))
        for key, summary in (veto_dd.get("by_price_evidence") or {}).items():
            _dd_row(f"evidence: {key}", summary)
        for key, summary in (veto_dd.get("by_odds_band") or {}).items():
            _dd_row(f"odds band: {key}", summary)
        for key, summary in (veto_dd.get("by_veto_reason") or {}).items():
            _dd_row(f"veto reason: {key}", summary)
        for key, summary in (veto_dd.get("contrast_by_price_evidence") or {}).items():
            _dd_row(f"contrast {veto_dd.get('contrast_bucket', 'CAUTION')}: {key}", summary)

    quarantine_labels = {
        "NONE": "No price quarantine",
        "alias_fuzzy": "alias_fuzzy match",
        "scoutingstats_sole_source": "ScoutingStats sole source",
    }
    lines.extend([
        "",
        "## Suspect-price Quarantine Audit",
        "",
        "> Rows remain in the frozen ledger and are scored here. Quarantine removes push "
        "eligibility; it does not erase adverse evidence from the audit window.",
        "",
        "| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ])
    by_quarantine = report.get("by_price_quarantine_reason", {})
    if not by_quarantine:
        lines.append("| none | 0 | 0 | n/a | 0 | n/a | 0 | n/a |")
    else:
        for key, summary in by_quarantine.items():
            lines.append(
                f"| {quarantine_labels.get(key, key)} (`{key}`) | "
                f"{summary.get('settled_picks', 0)} | {summary.get('wins', 0)} | "
                f"{summary.get('hit_rate')} | {summary.get('priced_picks', 0)} | {summary.get('roi')} | "
                f"{summary.get('suspect_price_captures', 0)} | {summary.get('avg_suspect_price')} |"
            )
    # Render Settled Picks Granular Expectations Audit Ledger
    ledger = report.get("settled_ledger", [])
    if ledger:
        lines.extend([
            "## Settled Picks Granular Expectations Audit",
            "",
            "Visual audit of expected historical stats (from the `📊` line) against actual realized scores:",
            ""
        ])
        granular_cutoff = (
            date.fromisoformat(report["end"]) - timedelta(days=1)
        ).isoformat()

        for item in sorted(ledger, key=lambda x: x["date"], reverse=True):
            if str(item.get("date") or "")[:10] < granular_cutoff:
                continue

            status = "🟢 WON" if item["won"] else "🔴 LOST"
            lines.append(f"### {item['date']}: {item['match']} (Actual Score: **{item['hs']}-{item['gs']}**)")
            market_label = {
                "1x2": "1X2 Pick",
                "ou_2.5": "Over/Under 2.5 Pick",
                "btts": "BTTS Pick",
            }.get(item.get("market"), "Pick")
            lines.append(f"- **{market_label}**: Selected `{item['selection'].upper()}` @ {item['odds'] or 'n/a'} -> {status} (Expected prob: {item['avg_p']:.1f}%)")
            
            stats = item["parsed_stats"]
            if stats["over25_expected"] is not None:
                o25_icon = "🟢 HIT" if stats["over25_hit"] else "🔴 MISS"
                lines.append(f"  - [{o25_icon}] **Over 2.5 Goals**: expected {stats['over25_expected']:.1%} (Actual: {item['hs'] + item['gs']} goals)")
                
            if stats["btts_expected"] is not None:
                btts_icon = "🟢 HIT" if stats["btts_hit"] else "🔴 MISS"
                btts_dir = "BTTS-Yes" if stats["btts_expected"] >= 0.50 else "BTTS-No"
                actual_dir = "BTTS-Yes" if item["hs"] > 0 and item["gs"] > 0 else "BTTS-No"
                lines.append(f"  - [{btts_icon}] **{btts_dir}**: expected {stats['btts_expected']:.1%} (Actual: {actual_dir})")
                
            if stats["home_o15_expected"] is not None:
                h_o15_icon = "🟢 HIT" if stats["home_o15_hit"] else "🔴 MISS"
                if stats["home_o15_expected"] >= 0.50:
                    lines.append(f"  - [{h_o15_icon}] **Home Team Over 1.5 Goals**: expected {stats['home_o15_expected']:.1%} (Actual: {item['hs']} goals)")
                else:
                    lines.append(f"  - [{h_o15_icon}] **Home Team Under 1.5 Goals**: expected {1.0 - stats['home_o15_expected']:.1%} (Actual: {item['hs']} goals)")
                
            if stats["away_o15_expected"] is not None:
                a_o15_icon = "🟢 HIT" if stats["away_o15_hit"] else "🔴 MISS"
                if stats["away_o15_expected"] >= 0.50:
                    lines.append(f"  - [{a_o15_icon}] **Away Team Over 1.5 Goals**: expected {stats['away_o15_expected']:.1%} (Actual: {item['gs']} goals)")
                else:
                    lines.append(f"  - [{a_o15_icon}] **Away Team Under 1.5 Goals**: expected {1.0 - stats['away_o15_expected']:.1%} (Actual: {item['gs']} goals)")
                
            # Per-pick graded 🔥 Possible Events (Addendum 13/14): the same
            # observations that feed the aggregate table, rendered ONE EVENT
            # PER LINE in the 📊 layout (expected % + realized context) so the
            # operator can scan pick by pick. Addendum 16: combo-worded
            # markets render their canonical plain label via _display_label.
            notes_audit = item.get("notes_audit") or []
            if notes_audit:
                lines.append("  - **🔥 Possible Events (graded)**:")
                for note in notes_audit:
                    ev_label = _display_label(note.get("market"), note.get("label"))
                    if note.get("hit") is None:
                        lines.append(f"    - [⚪ n/a] **{ev_label}**: promised "
                                     f"{_pct(note.get('promised'))} (no scoring definition)")
                    else:
                        ev_icon = "🟢 HIT" if note["hit"] else "🔴 MISS"
                        actual_ctx = _event_actual_context(note.get("market"),
                                                           item.get("selection"),
                                                           item["hs"], item["gs"])
                        lines.append(f"    - [{ev_icon}] **{ev_label}**: expected "
                                     f"{_pct(note.get('promised'))} (Actual: {actual_ctx})")
            else:
                lines.append("  - **🔥 Possible Events (graded)**: none recorded on the archived pick")
            lines.append("")

    lines.extend(["", "## Event Disposition / Void Audit", ""])
    dispositions = report.get("by_event_disposition", {}) or {}
    if not dispositions:
        lines.append("- none")
    else:
        lines.extend([
            "| disposition | voided picks |",
            "| --- | --- |",
        ])
        for disposition, count in sorted(dispositions.items()):
            lines.append(f"| {disposition} | {count} |")
    for item in report.get("voided_event_examples", [])[:25]:
        lines.append(
            f"- {item.get('date')} `{item.get('disposition')}` `{item.get('bucket')}` — "
            f"{item.get('match')} ({item.get('origin')}); excluded from win/loss/ROI"
        )

    lines.extend(["", "## Rescheduled Fixture Examples", ""])
    rescheduled = report.get("rescheduled_examples", [])
    if not rescheduled:
        lines.append("- none")
    else:
        for ex in rescheduled[:25]:
            lines.append(
                f"- {ex.get('date')} `{ex.get('bucket')}` `{ex.get('rule')}` — {ex.get('match')} "
                f"-> {str(ex.get('pick')).upper()} @ {ex.get('odds')} (rescheduled → "
                f"{ex.get('rescheduled_to')}; actual {ex.get('rescheduled_home')} "
                f"{ex.get('rescheduled_hs')}-{ex.get('rescheduled_gs')} "
                f"{ex.get('rescheduled_away')} [{ex.get('rescheduled_outcome')}])"
            )

    lines.extend(["", "## Pending / Unmatched Result Examples", ""])
    examples = report.get("unmatched_examples", [])
    if not examples:
        lines.append("- none")
    else:
        for ex in examples[:25]:
            lines.append(
                f"- {ex.get('date')} `{ex.get('bucket')}` `{ex.get('rule')}` — {ex.get('match')} -> {str(ex.get('pick')).upper()} @ {ex.get('odds')} ({ex.get('reason')}); keys={ex.get('home_key_candidates')}/{ex.get('away_key_candidates')}"
            )

    lines.extend(["", "## Ambiguous result examples", ""])
    amb = report.get("ambiguous_examples", [])
    if not amb:
        lines.append("- none")
    else:
        for ex in amb[:25]:
            lines.append(f"- {ex.get('date')} `{ex.get('bucket')}` `{ex.get('rule')}` — {ex.get('match')} ({ex.get('reason')})")
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit recent archived daily picks against settled warehouse results.")
    ap.add_argument("--end", default=date.today().isoformat(), help="End date inclusive (YYYY-MM-DD).")
    ap.add_argument("--start", default=None, help="Start date inclusive (YYYY-MM-DD). Overrides --days if provided.")
    ap.add_argument("--days", type=int, default=30, help="Rolling window length in days (default: 30). Ignored if --start is provided.")
    ap.add_argument("--warehouse", default=str(WAREHOUSE), help="Path to warehouse.duckdb")
    ap.add_argument(
        "--include-same-day",
        action="store_true",
        help="Allow same-day archived picks to count as settled. Default is OFF to avoid live/in-progress false settlements.",
    )
    args = ap.parse_args()

    end = datetime.strptime(args.end, "%Y-%m-%d").date()
    if args.start:
        start_date = datetime.strptime(args.start, "%Y-%m-%d").date()
        if start_date > end:
            print(f"error: --start {args.start} is after --end {args.end}", file=sys.stderr)
            return 1
        start = start_date.isoformat()
    else:
        start = (end - timedelta(days=max(0, args.days - 1))).isoformat()
    report = build_report(start, end.isoformat(), Path(args.warehouse), include_same_day=args.include_same_day)

    json_path = LOCALDATA / "picks_audit_rolling.json"
    md_path = LOCALDATA / f"picks_audit_{end.isoformat()}.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True))
    write_markdown(md_path, report)

    overall = report.get("overall", {})
    print(f"Recent picks audit — {start} to {end.isoformat()}")
    print(f" archived pick rows: {report.get('archived_pick_rows', 0)}")
    print(f" archived pick dates: {len(report.get('archived_pick_dates', []))}")
    print(f" same-day rows excluded: {report.get('same_day_excluded', 0)}")
    print(f" eligible prior picks: {report.get('eligible_prior_picks', 0)}")
    print(f" settled picks: {overall.get('settled_picks', 0)}")
    print(f" pending/unmatched result picks: {report.get('pending_result_picks', report.get('unmatched_result_picks', 0))}")
    print(f" rescheduled result picks (settled ±3d): {report.get('rescheduled_result_picks', 0)}")
    print(f" voided event picks: {report.get('voided_event_picks', 0)}")
    print(f" settled via shared overlay facts: {report.get('settled_via_overlay_picks', 0)}")
    print(f" ambiguous result picks: {report.get('ambiguous_result_picks', 0)}")
    print(f" hit rate: {overall.get('hit_rate')}")
    print(f" ROI: {overall.get('roi')}")
    _vd = report.get("veto_deep_dive", {}) or {}
    if _vd.get("overall"):
        _ov = _vd["overall"]
        _tr = _vd.get("trusted_evidence_only", {}) or {}
        _so = _vd.get("soft_evidence_only", {}) or {}
        print(f" veto deep-dive ({_vd.get('focus_bucket', 'SKIPPED_VETO')}): "
              f"settled={_ov.get('settled_picks', 0)} roi={_ov.get('roi')} | "
              f"trusted n={_tr.get('priced_picks', 0)} roi={_tr.get('roi')} | "
              f"soft n={_so.get('priced_picks', 0)} roi={_so.get('roi')}")
        for _band, _sum in (_vd.get("by_odds_band") or {}).items():
            print(f"   odds {_band}: settled={_sum.get('settled_picks', 0)} "
                  f"wins={_sum.get('wins', 0)} roi={_sum.get('roi')}")
    _ena = report.get("event_notes_audit", {}) or {}
    print(f" possible-events notes scored: {_ena.get('scored', 0)}/{_ena.get('total_notes', 0)}")
    _avg_goals = (report.get("statline_calibration", {}) or {}).get("avg_goals") or {}
    if _avg_goals:
        print(f" stat-line avg-goals MAE: {_avg_goals.get('mae')} (n={_avg_goals.get('n')})")
    print(f" json: {json_path}")
    print(f" markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
