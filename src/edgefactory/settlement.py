"""Pure settlement-disposition helpers.

A missing final score is not itself a loss, a draw, or proof that an event was
postponed. These helpers map only positive terminal event-status evidence into
an audit disposition. Unknown/scheduled/live statuses remain non-terminal.

``load_verified_results`` reads operator-confirmed final scores (the
``verified_event_dispositions.json`` analogue for score facts). Verified rows
outrank every donor in both the audit and the auto-ticket grader, so a single
bad donor row can no longer hold a pick as an alias-outcome conflict.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

POSTPONED = "POSTPONED"
CANCELLED = "CANCELLED"
ABANDONED = "ABANDONED"

_TERMINAL_STATUS_PATTERNS = (
    (POSTPONED, re.compile(r"\b(postp(?:oned)?|postponed)\b", re.IGNORECASE)),
    (CANCELLED, re.compile(r"\b(cancel(?:led|ed)?|canc\.)\b", re.IGNORECASE)),
    (ABANDONED, re.compile(r"\b(abandon(?:ed)?|abnd\.)\b", re.IGNORECASE)),
)


def terminal_event_disposition(status: object) -> str | None:
    """Return a positive terminal no-score disposition, else ``None``.

    Deliberately does not map ``scheduled``, blank, live, suspended, or a
    missing score to a disposition. Those states are not proof that an original
    fixture was voided.
    """
    text = str(status or "").strip()
    if not text:
        return None
    for disposition, pattern in _TERMINAL_STATUS_PATTERNS:
        if pattern.search(text):
            return disposition
    return None


def is_void_disposition(value: object) -> bool:
    return str(value or "") in {POSTPONED, CANCELLED, ABANDONED}


def _verified_results_path() -> Path:
    root = Path(__file__).resolve().parent.parent.parent
    preferred = root / "Config" / "verified_results.json"
    if preferred.exists() or (root / "Config").exists():
        return preferred
    return root / "config" / "verified_results.json"


def load_verified_results(path: Path | None = None) -> list[dict]:
    """Load operator-verified final scores.

    These are authoritative score facts that outrank every donor. Invalid rows
    (missing date/teams/score, non-home-away-draw outcome) fail closed.
    """
    p = path or _verified_results_path()
    try:
        payload = json.loads(p.read_text())
        rows = payload.get("rows") or []
    except Exception:
        return []
    out: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        day = str(row.get("date") or "")[:10]
        home = str(row.get("home") or "")
        away = str(row.get("away") or "")
        outcome = str(row.get("outcome") or "")
        if not day or not home or not away or outcome not in ("home", "away", "draw"):
            continue
        date.fromisoformat(day)
        if row.get("hs") is None or row.get("gs") is None:
            continue
        pair = regulation_score(row)
        if pair is None:
            raise ValueError("verified result has no valid regulation-time score")
        hs, gs = pair
        if outcome != ("home" if hs > gs else "away" if hs < gs else "draw"):
            raise ValueError("verified result outcome contradicts its regulation score")
        out.append({
            **({"verified_at": str(row["verified_at"])} if row.get("verified_at") else {}),
            "date": day,
            "home": home,
            "away": away,
            "hs": hs,
            "gs": gs,
            "outcome": outcome,
            "src": str(row.get("src") or "operator_verified"),
        })
    return out


# Soccer 1x2, totals, BTTS and team totals settle on 90 minutes PLUS stoppage
# time, never extra time/shootouts. Missing period metadata on legacy donors
# is not positive extra-time evidence, but an observed AET/PEN flag must survive
# source priority, exports and cache reuse. Never infer a 90-minute score.
_PERIOD_PATTERN = r"\b(?:AET|ET|PEN|PENS|PENALTIES|AP|SHOOT[ -]*OUT|EXTRA[ -]+TIME|AFTER[ -]+PENALTIES)\b"
_PERIOD_RE = re.compile(_PERIOD_PATTERN, re.I)
REGULATION_FIELDS = ("status", "score_period", "regulation_hs", "regulation_gs")
RESULT_SOURCES = ("forebet", "bettingclosed", "zulubet", "statarea",
                  "scoutingstats", "vitibet", "betexplorer")


def non_regulation_status(value: object) -> bool:
    text = str(value or "").replace("_", " ").replace(".", "")
    return bool(_PERIOD_RE.search(text))


def result_period_status(text: object) -> str:
    """Preserve positive period evidence from a result cell, not team names."""
    return "AET" if non_regulation_status(text) else ""


def _goal(value):
    import math
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
        if not math.isfinite(number) or number < 0 or number > 2147483647 or not number.is_integer():
            return None
        return int(number)
    except (ValueError, TypeError, OverflowError):
        return None


def explicit_regulation_score(row):
    """Only observed regulation columns or an explicit 90-minute period tag."""
    if any(row.get(f) not in (None, "") for f in ("regulation_hs", "regulation_gs")):
        pair = (_goal(row.get("regulation_hs")), _goal(row.get("regulation_gs")))
    elif str(row.get("score_period") or "").strip().lower() in {"regulation", "90", "90_minutes"}:
        pair = (_goal(row.get("hs")), _goal(row.get("gs")))
    else:
        return None
    return pair if None not in pair else None


def regulation_score(row):
    if terminal_event_disposition(row.get("status")):
        return None
    # A partial/invalid explicit score is not permission to use the aggregate.
    if any(row.get(f) not in (None, "") for f in ("regulation_hs", "regulation_gs")):
        return explicit_regulation_score(row)
    explicit = explicit_regulation_score(row)
    if explicit is not None:
        return explicit
    if non_regulation_status(row.get("status")) or non_regulation_status(row.get("score_period")):
        return None
    if str(row.get("status") or "").replace("_", " ").strip().upper() in {"LIVE", "HT", "1H", "2H", "IN PLAY", "INPLAY"}:
        return None
    pair = (_goal(row.get("hs")), _goal(row.get("gs")))
    return pair if None not in pair else None


def regulation_fixture_key(row):
    from .identity import source_team_key, squad_markers
    return (str(row.get("date") or "")[:10], source_team_key(row.get("home")),
            source_team_key(row.get("away")), tuple(sorted(squad_markers(row.get("home")))),
            tuple(sorted(squad_markers(row.get("away")))))


def warehouse_regulation_rows(con, sources=RESULT_SOURCES, *, start=None):
    """Read existing views, preserving cross-donor non-regulation vetoes.

    Works with old warehouses too. A plain FT/blank-status score from another
    donor cannot override observed AET/PEN evidence. Explicit regulation scores
    may resolve it; reviewed verified results are applied by callers afterwards.
    Returns priority-ordered scores and period evidence, including holds
    resolved by explicit regulation scores (needed to vet older overlay rows).
    """
    tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
    candidates, risk = [], {}
    for source in sources:
        for table in (source + "_settled", source, source + "_raw"):
            if table not in tables:
                continue
            cols = {r[0] for r in con.execute(f'DESCRIBE "{table}"').fetchall()}
            if not {"date", "home", "away"} <= cols:
                continue
            fields = [f for f in ("date", "home", "away", "hs", "gs", *REGULATION_FIELDS) if f in cols]
            where = " WHERE substr(CAST(date AS VARCHAR),1,10) >= ?" if start else ""
            rows = con.execute(f'SELECT {", ".join(fields)} FROM "{table}"' + where,
                               [start] if start else []).fetchall()
            for values in rows:
                row = dict(zip(fields, values))
                key = regulation_fixture_key(row)
                if non_regulation_status(row.get("status")) or non_regulation_status(row.get("score_period")):
                    risk.setdefault(key, row)
                if table == source + "_settled":
                    row["src"] = table
                    candidates.append(row)
    return filter_regulation_rows(candidates, list(risk.values()))


def _result_identity_valid(row):
    if not isinstance(row, dict) or not row.get("home") or not row.get("away"):
        return False
    try:
        date.fromisoformat(str(row.get("date") or "")[:10])
        return True
    except ValueError:
        return False


def filter_regulation_rows(rows, period_holds=()):
    rows = [r for r in rows if _result_identity_valid(r)]
    risk = {regulation_fixture_key(r): r for r in period_holds if _result_identity_valid(r)}
    for row in rows:
        if non_regulation_status(row.get("status")) or non_regulation_status(row.get("score_period")):
            risk.setdefault(regulation_fixture_key(row), row)
    accepted = []
    for row in rows:
        pair = regulation_score(row)
        if pair is None or (regulation_fixture_key(row) in risk and explicit_regulation_score(row) is None):
            continue
        hs, gs = pair
        accepted.append(dict(row, date=str(row["date"])[:10], hs=hs, gs=gs,
                             outcome="home" if hs > gs else "away" if hs < gs else "draw"))
    holds = [dict({k: str(row.get(k) or "") for k in ("home", "away", "status", "score_period")},
                  date=str(row.get("date") or "")[:10]) for row in risk.values()]
    return accepted, holds


def load_period_holds(path):
    try:
        payload = json.loads(Path(path).read_text())
        rows = list(payload.get("period_holds", [])) + list(payload.get("rows", []))
        return [r for r in rows if _result_identity_valid(r)
                and (non_regulation_status(r.get("status")) or non_regulation_status(r.get("score_period")))]
    except (OSError, ValueError, TypeError, AttributeError):
        return []


def regulation_sql_goals(columns):
    """Warehouse raw views use the same period rule, before miners see scores."""
    def valid(col):
        return (f"(isfinite(TRY_CAST({col} AS DOUBLE)) AND TRY_CAST({col} AS DOUBLE)>=0 "
                f"AND TRY_CAST({col} AS DOUBLE)=TRY_CAST({col} AS BIGINT) "
                f"AND TRY_CAST({col} AS INT) IS NOT NULL)")
    guards = []
    for field in ("status", "score_period"):
        if field in columns:
            guards.append(f"NOT regexp_matches(upper(replace(replace(coalesce({field},''),'_',' '),'.','')), '{_PERIOD_PATTERN}')")
    if "status" in columns:
        guards.append("NOT regexp_matches(upper(trim(replace(coalesce(status,''),'_',' '))), '(POSTP|CANCEL|ABANDON|^LIVE$|^HT$|^1H$|^2H$|^IN PLAY$|^INPLAY$)')")
    raw_ok = " AND ".join([valid("hs"), valid("gs"), *guards])
    explicit = {"regulation_hs", "regulation_gs"} <= columns
    tagged = "score_period" in columns
    out = []
    for side in ("hs", "gs"):
        cases = []
        if "status" in columns:
            cases.append("WHEN regexp_matches(upper(coalesce(status,'')), '(POSTP|CANCEL|ABANDON)') THEN NULL")
        if explicit:
            cases.append(f"WHEN nullif(trim(regulation_hs),'') IS NOT NULL OR nullif(trim(regulation_gs),'') IS NOT NULL THEN CASE WHEN {valid('regulation_hs')} AND {valid('regulation_gs')} THEN TRY_CAST(regulation_{side} AS INT) END")
        if tagged:
            cases.append(f"WHEN lower(trim(score_period)) IN ('regulation','90','90_minutes') AND {valid('hs')} AND {valid('gs')} THEN TRY_CAST({side} AS INT)")
        out.append(f"CASE {' '.join(cases)} WHEN {raw_ok} THEN TRY_CAST({side} AS INT) END AS {side}")
    return out
