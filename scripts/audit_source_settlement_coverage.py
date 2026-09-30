#!/usr/bin/env python3
"""Per-source prediction -> final-score settlement/matching audit.

Why this exists (2026-09-30, run #874 was YELLOW not green): the existing
``scripts/audit_source_availability.py`` answers "did files/rows/tables
appear?". That is a *capture* question. It cannot tell the operator whether a
replacement source's prediction rows can actually be joined to trustworthy
final scores, which is the only property that lets a source feed certified
picks. Row counts are not validation.

This audit answers, per source, over COMPLETED fixtures only:

  * how many unique prediction fixtures exist
  * how many carry a source-supplied final score (hs/gs)
  * how many match an INDEPENDENT donor exactly on the normalized key
  * how many match only through the guarded entity/alias identity fold
  * how many are unmatched
  * how many are ambiguous (key collision) and therefore REJECTED
  * how many have a reversed home/away candidate (orientation risk), split
    into operator-reviewed (explained) and unexplained
  * how many have conflicting donor scores (donors disagree)
  * how many have source score agreeing / conflicting with donor score
  * settlement coverage % and conflict %
  * up to N representative examples of each failure class

Design rules:
  * conservative — ambiguity is never resolved, it is rejected and reported;
  * a source is NEVER its own independent donor;
  * alias matching only uses the already-verified guarded identity fold in
    ``edgefactory.identity`` (folds + explicit evidence aliases, no fuzz);
  * read-only: nothing here mutates localdata source files or the warehouse;
  * a source with ANY unexplained reversed home/away candidate can never be
    ``settlement_validated`` — it caps at ``review_required``;
  * pricing-only sources are listed but excluded from coverage scoring;
  * no network, no Forebet Browser Run, no probes.

Usage (also wired into ``scripts/daily.py`` official mode as a soft step):

    PYTHONPATH=src python3 scripts/audit_source_settlement_coverage.py \\
        --end-date 2026-09-30 --days 90 \\
        --output-json localdata/source_settlement_coverage_2026-09-30.json \\
        --output-md   localdata/source_settlement_coverage_2026-09-30.md
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, Iterator

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
if str(ROOT / "src") not in sys.path:  # allow bare `python3 scripts/...`
    sys.path.insert(0, str(ROOT / "src"))

# Prediction sources audited for prediction -> score settlement quality.
PREDICTION_SOURCES: tuple[str, ...] = (
    "forebet",
    "zulubet",
    "statarea",
    "vitibet",
    "scoutingstats",
    "predictz",
    "windrawwin",
    "prosoccer",
    "soccervista",
    "bettingclosed",
    "betclan",
    "freesupertips",
    "afootballreport",
    "bzzoiro",
)

# Identified, but excluded from prediction -> score coverage scoring.
PRICING_ONLY_SOURCES: tuple[str, ...] = (
    "bzzoiro_odds",
    "theoddsapi_odds",
    "oddspapi_odds",
)

# Operator-reviewed reversed home/away explanations. Each entry is a single
# fixture a human looked at and signed off (e.g. a donor's orientation is known
# wrong, or the fixture is a two-legged tie whose legs share a date). ONLY
# fixtures listed here stop counting as unexplained orientation risk. There is
# no wildcard and no per-source blanket waiver by design.
REVERSAL_REVIEW_PATH = ROOT / "Config" / "reversal_reviews.json"

# Independent score donors available without a warehouse (raw cache files).
CSV_DONOR_SOURCES: tuple[str, ...] = (
    "betexplorer_results",
    "forebet",
    "statarea",
    "zulubet",
    "bettingclosed",
    "vitibet",
    "scoutingstats",
)

# Warehouse relations used as donors when a materialized warehouse exists.
WAREHOUSE_DONOR_TABLES: tuple[str, ...] = (
    "results_donor",
    "forebet_settled",
    "statarea_settled",
    "zulubet_settled",
    "bettingclosed_settled",
    "vitibet_settled",
    "scoutingstats_settled",
    "betexplorer_settled",
    "predictz_settled",
    "prosoccer_settled",
)

# Donor label -> owning prediction source, so a source can never validate
# itself. ``results_donor`` is a priority-merged view whose provenance is not
# recoverable per row, so it is treated as owned by nobody but is EXCLUDED
# from a source's donor set when that source is one of its known feeders.
DONOR_OWNER_OVERRIDES = {"betexplorer_results": "betexplorer"}
RESULTS_DONOR_FEEDERS = frozenset(
    {"forebet", "bettingclosed", "zulubet", "statarea", "scoutingstats", "vitibet"}
)

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def load_reversal_reviews(path: Path | None = None) -> dict[tuple[str, str, str, str], str]:
    """Load signed-off reversal explanations keyed by (source, date, hkey, akey)."""
    target = path or REVERSAL_REVIEW_PATH
    try:
        payload = json.loads(target.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    reviews: dict[tuple[str, str, str, str], str] = {}
    for entry in payload.get("reviewed") or []:
        if not isinstance(entry, dict):
            continue
        day = _day(entry.get("date"))
        source = str(entry.get("source") or "").strip().lower()
        explanation = str(entry.get("explanation") or "").strip()
        home, away = norm_key(entry.get("home")), norm_key(entry.get("away"))
        # A review without a written explanation is not a review.
        if not (day and source and home and away and explanation):
            continue
        reviews[(source, day, home, away)] = explanation
    return reviews

# Verdict thresholds. Deliberately strict: a source only becomes
# "settlement-validated" with real completed-fixture volume, high independent
# coverage, and low donor conflict. Graduation from shadow/candidate still
# requires operator sign-off; this audit only supplies evidence.
# ``settlement_validated`` additionally requires ZERO unexplained reversed
# home/away candidates (operator review, 2026-09-30: Zulubet hit 93.2% coverage
# with rev=1 and was wrongly called validated).
MIN_FIXTURES_VALIDATED = 200
MIN_COVERAGE_VALIDATED = 90.0
MAX_CONFLICT_VALIDATED = 2.0
MIN_FIXTURES_PARTIAL = 30
MIN_COVERAGE_PARTIAL = 60.0
MAX_CONFLICT_PARTIAL = 10.0


def norm_key(value: object) -> str:
    """Basic normalized join key (matches backfill_results semantics)."""
    return _NON_ALNUM.sub("", str(value or "").strip().lower())


def alias_key(value: object) -> str:
    """Guarded identity-fold key with explicit evidence aliases.

    Uses ``edgefactory.identity.source_team_key`` — folds plus an explicit,
    evidence-seeded alias table. No fuzzy similarity. Falls back to the basic
    key if the package is unavailable (keeps the script runnable standalone).
    """
    try:
        from edgefactory.identity import source_team_key
    except Exception:  # pragma: no cover - import guard
        return norm_key(value)
    return source_team_key(value)


def alias_available() -> bool:
    try:
        from edgefactory.identity import source_team_key  # noqa: F401
    except Exception:  # pragma: no cover - import guard
        return False
    return True


def _day(value: object) -> str | None:
    raw = str(value or "").strip()[:10]
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError:
        return None


def _score(value: object) -> int | None:
    raw = str(value if value is not None else "").strip()
    if raw in {"", "None", "nan", "NaN", "-"}:
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


def source_files(localdata: Path, source: str) -> list[Path]:
    """Exact legacy + monthly files for one source (never prefix-bleeds)."""
    monthly = sorted(localdata.glob(f"{source}_[0-9][0-9][0-9][0-9]-[0-9][0-9].csv.gz"))
    legacy = localdata / f"{source}.csv.gz"
    return ([legacy] if legacy.exists() else []) + monthly


def iter_rows(path: Path) -> Iterator[dict[str, str]]:
    opener = gzip.open if path.suffix == ".gz" else open
    try:
        with opener(path, "rt", newline="", encoding="utf-8", errors="replace") as handle:
            yield from csv.DictReader(handle)
    except (OSError, csv.Error, UnicodeError):
        return


# --------------------------------------------------------------------------
# Donor index
# --------------------------------------------------------------------------


@dataclass
class DonorIndex:
    """(date, hkey, akey) -> {donor_label: (hs, gs)} plus an alias view."""

    exact: dict[tuple[str, str, str], dict[str, tuple[int, int]]] = field(default_factory=dict)
    alias: dict[tuple[str, str, str], set[tuple[str, str, str]]] = field(default_factory=dict)
    donors_seen: set[str] = field(default_factory=set)
    rows_loaded: int = 0

    def add(self, day: str, home: object, away: object, hs: int, gs: int, donor: str) -> None:
        key = (day, norm_key(home), norm_key(away))
        if not key[1] or not key[2]:
            return
        self.exact.setdefault(key, {})[donor] = (hs, gs)
        akey = (day, alias_key(home), alias_key(away))
        if akey[1] and akey[2]:
            self.alias.setdefault(akey, set()).add(key)
        self.donors_seen.add(donor)
        self.rows_loaded += 1


def load_settled_overlay(localdata: Path, index: DonorIndex, start: str, end: str) -> None:
    path = localdata / "settled_results.json"
    if not path.exists():
        return
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return
    for row in payload.get("rows") or []:
        if not isinstance(row, dict):
            continue
        day = _day(row.get("date"))
        if day is None or not (start <= day <= end):
            continue
        hs, gs = _score(row.get("hs")), _score(row.get("gs"))
        if hs is None or gs is None:
            continue
        donor = str(row.get("src") or "settled_overlay")
        index.add(day, row.get("home"), row.get("away"), hs, gs, donor)


def load_csv_donors(localdata: Path, index: DonorIndex, start: str, end: str,
                    donors: Iterable[str] = CSV_DONOR_SOURCES) -> None:
    for donor in donors:
        for path in source_files(localdata, donor):
            for row in iter_rows(path):
                day = _day(row.get("date"))
                if day is None or not (start <= day <= end):
                    continue
                hs, gs = _score(row.get("hs")), _score(row.get("gs"))
                if hs is None or gs is None:
                    continue
                index.add(day, row.get("home"), row.get("away"), hs, gs, f"{donor}_csv")


def load_warehouse_donors(localdata: Path, index: DonorIndex, start: str, end: str) -> None:
    path = localdata / "warehouse.duckdb"
    if not path.exists():
        return
    try:
        import duckdb
    except Exception:
        return
    try:
        con = duckdb.connect(str(path), read_only=True)
    except Exception:
        return
    try:
        tables = {
            str(row[0])
            for row in con.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
            ).fetchall()
        }
        for table in WAREHOUSE_DONOR_TABLES:
            if table not in tables:
                continue
            try:
                rows = con.execute(
                    f"SELECT substr(CAST(date AS VARCHAR),1,10) AS d, home, away, hs, gs "  # noqa: S608 - fixed allowlist
                    f"FROM {table} WHERE hs IS NOT NULL AND gs IS NOT NULL "
                    f"AND substr(CAST(date AS VARCHAR),1,10) BETWEEN ? AND ?",
                    [start, end],
                ).fetchall()
            except Exception:
                continue
            for day, home, away, hs, gs in rows:
                hs_i, gs_i = _score(hs), _score(gs)
                if day is None or hs_i is None or gs_i is None:
                    continue
                index.add(str(day), home, away, hs_i, gs_i, f"wh:{table}")
    finally:
        try:
            con.close()
        except Exception:
            pass


def build_donor_index(localdata: Path, start: str, end: str, *, use_warehouse: bool = True) -> DonorIndex:
    index = DonorIndex()
    load_settled_overlay(localdata, index, start, end)
    load_csv_donors(localdata, index, start, end)
    if use_warehouse:
        load_warehouse_donors(localdata, index, start, end)
    return index


def donor_owner(label: str) -> str:
    """Owning prediction source of a donor label ('' when not source-owned)."""
    base = label.split(":", 1)[-1]
    for suffix in ("_settled", "_csv"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
    return DONOR_OWNER_OVERRIDES.get(base, base)


def independent_scores(
    donor_scores: dict[str, tuple[int, int]], source: str
) -> dict[str, tuple[int, int]]:
    """Drop donors owned by ``source`` — no source validates itself."""
    out: dict[str, tuple[int, int]] = {}
    for label, score in donor_scores.items():
        owner = donor_owner(label)
        if owner == source:
            continue
        if owner == "results_donor" and source in RESULTS_DONOR_FEEDERS:
            # Priority-merged view: provenance per row is unrecoverable, so it
            # may contain this source's own rows. Exclude conservatively.
            continue
        out[label] = score
    return out


# --------------------------------------------------------------------------
# Per-source audit
# --------------------------------------------------------------------------


@dataclass
class SourceCoverage:
    source: str
    role: str = "prediction"
    files: int = 0
    prediction_rows: int = 0
    prediction_fixtures: int = 0
    source_score_present: int = 0
    independent_donor_exact_matches: int = 0
    alias_matches: int = 0
    matched_total: int = 0
    source_score_matches_donor: int = 0
    source_score_conflicts_donor: int = 0
    donor_score_conflicts: int = 0
    unmatched: int = 0
    ambiguous: int = 0
    reversed_candidates: int = 0
    reversed_reviewed: int = 0
    reversed_unexplained: int = 0
    coverage_pct: float = 0.0
    self_score_pct: float = 0.0
    conflict_pct: float = 0.0
    verdict: str = "no_data"
    notes: str = ""
    examples: dict[str, list[dict[str, str]]] = field(default_factory=dict)


def _add_example(bucket: list[dict[str, str]], payload: dict[str, str], limit: int) -> None:
    if len(bucket) < limit:
        bucket.append(payload)


def audit_source(
    source: str,
    *,
    localdata: Path,
    donors: DonorIndex,
    start: str,
    end: str,
    examples_limit: int = 10,
    reversal_reviews: dict[tuple[str, str, str, str], str] | None = None,
) -> SourceCoverage:
    """Audit one prediction source's prediction->score matching quality."""
    result = SourceCoverage(source=source)
    reviews = reversal_reviews if reversal_reviews is not None else load_reversal_reviews()
    files = source_files(localdata, source)
    result.files = len(files)

    if source in PRICING_ONLY_SOURCES:
        result.role = "pricing-only"
        result.verdict = "excluded_pricing_only"
        result.notes = "pricing-only source; excluded from prediction->score coverage"
        return result

    # fixture key -> {"raw": (home, away), "score": (hs, gs)|None, "variants": set}
    fixtures: dict[tuple[str, str, str], dict] = {}
    for path in files:
        for row in iter_rows(path):
            day = _day(row.get("date"))
            if day is None or not (start <= day <= end):
                continue  # future fixtures and out-of-window rows excluded
            home, away = row.get("home"), row.get("away")
            key = (day, norm_key(home), norm_key(away))
            if not key[1] or not key[2]:
                continue
            result.prediction_rows += 1
            hs, gs = _score(row.get("hs")), _score(row.get("gs"))
            entry = fixtures.setdefault(key, {"raw": (str(home), str(away)), "scores": set(), "variants": set()})
            entry["variants"].add((str(home), str(away)))
            if hs is not None and gs is not None:
                entry["scores"].add((hs, gs))

    result.prediction_fixtures = len(fixtures)
    if not fixtures:
        result.verdict = "no_data"
        result.notes = "no completed-window prediction rows in localdata"
        return result

    ex: dict[str, list[dict[str, str]]] = defaultdict(list)

    for key, entry in sorted(fixtures.items()):
        day, hkey, akey = key
        home, away = entry["raw"]
        base = {"date": day, "home": home, "away": away}

        # Ambiguity #1: several distinct raw fixtures collapse onto one key.
        if len(entry["variants"]) > 1:
            result.ambiguous += 1
            _add_example(ex["ambiguous"], {**base, "reason": "source key collision",
                                           "variants": " | ".join(sorted(f"{h} vs {a}" for h, a in entry["variants"]))[:200]},
                         examples_limit)
            continue

        own_score: tuple[int, int] | None = None
        if entry["scores"]:
            result.source_score_present += 1
            if len(entry["scores"]) == 1:
                own_score = next(iter(entry["scores"]))
            else:
                # Source disagrees with itself across rows for one fixture.
                result.ambiguous += 1
                _add_example(ex["ambiguous"], {**base, "reason": "source self-inconsistent scores",
                                               "scores": ",".join(f"{h}-{g}" for h, g in sorted(entry["scores"]))},
                             examples_limit)
                continue

        donor_scores = independent_scores(donors.exact.get(key, {}), source)
        match_kind = "exact" if donor_scores else ""

        if not donor_scores and alias_available():
            # Guarded alias tier: only accept when exactly ONE donor fixture
            # resolves through the identity fold. Multiple => ambiguous.
            cand = donors.alias.get((day, alias_key(home), alias_key(away)), set())
            cand = {c for c in cand if independent_scores(donors.exact.get(c, {}), source)}
            if len(cand) == 1:
                donor_scores = independent_scores(donors.exact.get(next(iter(cand)), {}), source)
                match_kind = "alias"
            elif len(cand) > 1:
                result.ambiguous += 1
                _add_example(ex["ambiguous"], {**base, "reason": "multiple alias donor candidates",
                                               "candidates": str(len(cand))}, examples_limit)
                continue

        if not donor_scores:
            # Orientation risk: donor has the reversed pairing.
            rev = independent_scores(donors.exact.get((day, akey, hkey), {}), source)
            if rev:
                result.reversed_candidates += 1
                rhs, rgs = next(iter(rev.values()))
                explanation = reviews.get((source, day, hkey, akey))
                if explanation:
                    result.reversed_reviewed += 1
                    bucket = "reversed_candidate_reviewed"
                else:
                    result.reversed_unexplained += 1
                    bucket = "reversed_candidate_unexplained"
                _add_example(ex[bucket],
                             {**base, "reason": "donor has reversed home/away",
                              "donor_score": f"{rhs}-{rgs}", "donors": ",".join(sorted(rev)),
                              "review": explanation or "UNEXPLAINED - blocks validation"},
                             examples_limit)
            result.unmatched += 1
            _add_example(ex["unmatched"],
                         {**base, "reason": "no independent donor row",
                          "source_score": f"{own_score[0]}-{own_score[1]}" if own_score else ""},
                         examples_limit)
            continue

        distinct = set(donor_scores.values())
        if len(distinct) > 1:
            result.donor_score_conflicts += 1
            _add_example(ex["donor_conflict"],
                         {**base, "reason": "independent donors disagree",
                          "donor_scores": "; ".join(f"{d}={s[0]}-{s[1]}" for d, s in sorted(donor_scores.items()))},
                         examples_limit)
            # A contested score is not settlement evidence; do not count it as
            # a clean match, and do not judge the source score against it.
            continue

        if match_kind == "alias":
            result.alias_matches += 1
        else:
            result.independent_donor_exact_matches += 1
        result.matched_total += 1

        donor_score = next(iter(distinct))
        if own_score is not None:
            if own_score == donor_score:
                result.source_score_matches_donor += 1
            else:
                result.source_score_conflicts_donor += 1
                _add_example(ex["conflict"],
                             {**base, "reason": "source score != donor score",
                              "source_score": f"{own_score[0]}-{own_score[1]}",
                              "donor_score": f"{donor_score[0]}-{donor_score[1]}",
                              "donors": ",".join(sorted(donor_scores))},
                             examples_limit)

    total = result.prediction_fixtures or 1
    result.coverage_pct = round(100.0 * result.matched_total / total, 2)
    result.self_score_pct = round(100.0 * result.source_score_present / total, 2)
    judged = result.source_score_matches_donor + result.source_score_conflicts_donor
    result.conflict_pct = round(100.0 * result.source_score_conflicts_donor / judged, 2) if judged else 0.0
    result.examples = {k: v for k, v in ex.items() if v}
    result.verdict, result.notes = classify(result)
    return result


def classify(row: SourceCoverage) -> tuple[str, str]:
    """Evidence verdict. Never a certification — gates stay operator-owned."""
    if row.prediction_fixtures == 0:
        return "no_data", "no completed-window prediction rows"
    notes: list[str] = []
    if row.reversed_candidates:
        notes.append(
            f"orientation risk on {row.reversed_candidates} fixtures "
            f"({row.reversed_unexplained} unexplained, {row.reversed_reviewed} reviewed)"
        )
    if row.donor_score_conflicts:
        notes.append(f"{row.donor_score_conflicts} donor-conflicted fixtures")
    if row.ambiguous:
        notes.append(f"{row.ambiguous} ambiguous rejected")
    if (
        row.prediction_fixtures >= MIN_FIXTURES_VALIDATED
        and row.coverage_pct >= MIN_COVERAGE_VALIDATED
        and row.conflict_pct <= MAX_CONFLICT_VALIDATED
    ):
        if row.reversed_unexplained:
            # Coverage/conflict are at the validated bar, but an unexplained
            # home/away reversal means identity orientation is not proven.
            # Conservative cap: a human must sign the fixture off in
            # Config/reversal_reviews.json before this can go green.
            verdict = "review_required"
            notes.append(
                f"validated on coverage/conflict but {row.reversed_unexplained} unexplained "
                "reversed home/away candidate(s) - sign off in Config/reversal_reviews.json"
            )
        else:
            verdict = "settlement_validated"
    elif (
        row.prediction_fixtures >= MIN_FIXTURES_PARTIAL
        and row.coverage_pct >= MIN_COVERAGE_PARTIAL
        and row.conflict_pct <= MAX_CONFLICT_PARTIAL
    ):
        verdict = "partial"
        notes.append("below validated thresholds (volume/coverage/conflict)")
    else:
        verdict = "unproven"
        notes.append("insufficient matched settlement evidence")
    return verdict, "; ".join(notes) or "-"


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

_COLUMNS = (
    ("source", "source"),
    ("fixtures", "prediction_fixtures"),
    ("own_score", "source_score_present"),
    ("exact", "independent_donor_exact_matches"),
    ("alias", "alias_matches"),
    ("matched", "matched_total"),
    ("agree", "source_score_matches_donor"),
    ("conflict", "source_score_conflicts_donor"),
    ("donor_conf", "donor_score_conflicts"),
    ("unmatched", "unmatched"),
    ("ambig", "ambiguous"),
    ("rev", "reversed_candidates"),
    ("rev_unexp", "reversed_unexplained"),
    ("cov%", "coverage_pct"),
    ("confl%", "conflict_pct"),
    ("verdict", "verdict"),
)


def render_markdown(rows: list[SourceCoverage], *, start: str, end: str, donors: DonorIndex,
                    examples_limit: int = 10) -> str:
    out: list[str] = [
        f"# Source settlement coverage — {start}..{end}",
        "",
        "Prediction->final-score matching quality per source. Row counts alone are NOT validation.",
        f"Donor rows indexed: {donors.rows_loaded} across {len(donors.donors_seen)} donor labels.",
        f"Guarded alias tier: {'enabled (edgefactory.identity fold)' if alias_available() else 'unavailable'}.",
        "",
        "| " + " | ".join(h for h, _ in _COLUMNS) + " |",
        "|" + "|".join("---" for _ in _COLUMNS) + "|",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(getattr(row, attr)) for _, attr in _COLUMNS) + " |")
    out.append("")
    out.append("## Notes")
    for row in rows:
        out.append(f"- **{row.source}** ({row.role}): {row.notes}")
    out.append("")
    out.append(f"## Examples (max {examples_limit} per class per source)")
    for row in rows:
        if not row.examples:
            continue
        out.append(f"### {row.source}")
        for kind, items in sorted(row.examples.items()):
            out.append(f"- {kind}:")
            for item in items:
                detail = ", ".join(f"{k}={v}" for k, v in item.items() if k not in {"date", "home", "away"})
                out.append(f"  - {item['date']} {item['home']} vs {item['away']} — {detail}")
    out.append("")
    out.append(
        "Verdicts are EVIDENCE, not certification. No source graduates from "
        "shadow/candidate on this report alone; operator sign-off is required. "
        "A source with ANY unexplained reversed home/away candidate caps at "
        "`review_required` - explain the fixture in Config/reversal_reviews.json "
        "or treat the orientation as unproven."
    )
    return "\n".join(out) + "\n"


def summarise(rows: list[SourceCoverage]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        buckets[row.verdict].append(row.source)
    return dict(buckets)


def run_audit(
    *,
    localdata: Path,
    end_date: date,
    days: int,
    sources: Iterable[str],
    examples_limit: int = 10,
    use_warehouse: bool = True,
) -> dict:
    start = (end_date - timedelta(days=days)).isoformat()
    end = end_date.isoformat()
    donors = build_donor_index(localdata, start, end, use_warehouse=use_warehouse)
    reviews = load_reversal_reviews()
    rows = [
        audit_source(
            source,
            localdata=localdata,
            donors=donors,
            start=start,
            end=end,
            examples_limit=examples_limit,
            reversal_reviews=reviews,
        )
        for source in sources
    ]
    return {
        "schema": 1,
        "generated_for": end,
        "window_start": start,
        "window_end": end,
        "window_days": days,
        "alias_tier": alias_available(),
        "reversal_reviews_loaded": len(reviews),
        "donor_rows": donors.rows_loaded,
        "donor_labels": sorted(donors.donors_seen),
        "thresholds": {
            "validated": {
                "min_fixtures": MIN_FIXTURES_VALIDATED,
                "min_coverage_pct": MIN_COVERAGE_VALIDATED,
                "max_conflict_pct": MAX_CONFLICT_VALIDATED,
                "max_unexplained_reversals": 0,
            },
            "partial": {
                "min_fixtures": MIN_FIXTURES_PARTIAL,
                "min_coverage_pct": MIN_COVERAGE_PARTIAL,
                "max_conflict_pct": MAX_CONFLICT_PARTIAL,
            },
        },
        "sources": [asdict(row) for row in rows],
        "summary": summarise(rows),
        "_rows": rows,
        "_donors": donors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--end-date", default=date.today().isoformat(), help="last completed date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, default=90, help="lookback window in days (inclusive)")
    parser.add_argument("--sources", help="comma-separated source list override")
    parser.add_argument("--examples", type=int, default=10, help="max examples per class per source")
    parser.add_argument("--output-json", type=Path, help="write JSON report here")
    parser.add_argument("--output-md", type=Path, help="write Markdown report here")
    parser.add_argument("--localdata", type=Path, default=LOCALDATA, help=argparse.SUPPRESS)
    parser.add_argument("--no-warehouse", action="store_true", help="skip duckdb donors")
    args = parser.parse_args(argv)

    try:
        end_date = date.fromisoformat(args.end_date)
    except ValueError as exc:
        parser.error(str(exc))
    if args.days < 1:
        parser.error("--days must be >= 1")

    sources = tuple(
        part.strip()
        for part in (args.sources or ",".join(PREDICTION_SOURCES + PRICING_ONLY_SOURCES)).split(",")
        if part.strip()
    )

    report = run_audit(
        localdata=args.localdata,
        end_date=end_date,
        days=args.days,
        sources=sources,
        examples_limit=args.examples,
        use_warehouse=not args.no_warehouse,
    )
    rows: list[SourceCoverage] = report.pop("_rows")
    donors: DonorIndex = report.pop("_donors")
    markdown = render_markdown(
        rows, start=report["window_start"], end=report["window_end"],
        donors=donors, examples_limit=args.examples,
    )
    print(markdown)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.output_json.with_suffix(args.output_json.suffix + ".tmp")
        tmp.write_text(json.dumps(report, indent=2, sort_keys=True))
        tmp.replace(args.output_json)
        print(f"wrote {args.output_json}")
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.output_md.with_suffix(args.output_md.suffix + ".tmp")
        tmp.write_text(markdown)
        tmp.replace(args.output_md)
        print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
