"""Exact post-Forebet predicates shared by the existing miner and consumers.

This module does not mine, fetch, certify or persist a registry. Source/result
provenance and observation quarantine are identical offline and in selection.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import date

from edgefactory.identity import source_team_key
from edgefactory.market_registry import get_bettable_markets

SCHEMA = "post_forebet_v1"
POST_FOREBET_START = "2026-06-13"
REMINE_SOURCES = (
    "zulubet", "statarea", "vitibet", "scoutingstats", "prosoccer",
    "betclan", "bzzoiro", "predictz", "windrawwin", "soccervista",
    "bettingclosed", "freesupertips", "afootballreport",
)
REMINE_MARKETS = tuple(dict.fromkeys(
    get_bettable_markets() + ["ou_1.5", "ou_3.5", "ou_4.5"]))
REMINE_THRESHOLDS = (0, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90)


def _table_exists(con, name: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {name} LIMIT 0")
        return True
    except Exception:
        return False


def _table_columns(con, name: str) -> set[str]:
    try:
        return {str(row[1]) for row in con.execute(f"PRAGMA table_info('{name}')").fetchall()}
    except Exception:
        return set()


def _number(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def _score_pair(row, prefix=""):
    pair = [_number(row.get(prefix + field)) for field in ("hs", "gs")]
    return tuple(int(v) for v in pair) if all(
        v is not None and v >= 0 and v.is_integer() for v in pair) else None


def _remine_key(row):
    home, away = source_team_key(row.get("home")), source_team_key(row.get("away"))
    if min(len(home), len(away)) < 4 or home == away:
        return None
    return str(row["date"])[:10], home, away


def _remine_signal(row, market):
    """Observed probabilities or categorical tips; never turn streaks into p.

    Warehouse sources have different units, so infer one scale from the full
    1X2 vector (when available), otherwise from the probability field itself.
    A full vector must be finite, bounded and sum approximately to one.
    """
    triple = [_number(row.get(c)) for c in ("p1", "px", "p2")]
    scale = 100.0 if any(v is not None and v > 1.5 for v in triple) else 1.0
    if market in ("1x2", "ht_1x2"):
        fields = ("p1", "px", "p2") if market == "1x2" else ("p1_ht", "px_ht", "p2_ht")
        values = [_number(row.get(c)) for c in fields]
        if market == "ht_1x2":
            scale = 100.0 if any(v is not None and v > 1.5 for v in values) else 1.0
        if all(v is not None and 0 <= v <= scale for v in values):
            probs = dict(zip(("home", "draw", "away"), (v / scale for v in values)))
            if abs(sum(probs.values()) - 1) > 0.05:
                return None
            best = max(probs.values())
            leaders = [side for side, prob in probs.items() if prob == best]
            return (leaders[0], probs) if len(leaders) == 1 else None
        if market != "1x2":
            return None
        # A categorical tip is eligible for the no-probability-floor test only.
        raw = str(row.get("pick") or row.get("pick_1x2") or row.get("tip") or "").lower()
        side = {"1": "home", "x": "draw", "2": "away"}.get(raw, raw)
        return (side, None) if side in ("home", "draw", "away") else None
    field = {"ou_1.5": "p_o15", "ou_2.5": "p_o25", "ou_3.5": "p_o35",
             "ou_4.5": "p_o45", "btts": "p_gg", "ht_ou_1.5": "p_o15_ht",
             "ht_ou_2.5": "p_o25_ht"}[market]
    value = _number(row.get(field))
    yes, no = ("yes", "no") if market == "btts" else ("over", "under")
    if value is not None:
        if all(v is None for v in triple):
            scale = 100.0 if value > 1.5 else 1.0
        value /= scale
        if not 0 <= value <= 1 or value == 0.5:
            return None
        return (yes if value > 0.5 else no, {yes: value, no: 1 - value})
    raw = str(row.get("pick_btts") if market == "btts" else
              row.get("pick_ou") if market == "ou_2.5" else "").lower()
    raw = {"gol": "yes", "nogol": "no", "over 2.5": "over", "under 2.5": "under"}.get(raw, raw)
    return (raw, None) if raw in (yes, no) else None


def _remine_outcome(scores, market):
    pair = scores.get("ht" if market.startswith("ht_") else "ft")
    if pair is None:
        return None
    hs, gs = pair
    if market.endswith("1x2"):
        return "home" if hs > gs else "away" if hs < gs else "draw"
    if market == "btts":
        return "yes" if hs > 0 and gs > 0 else "no"
    line = float(market.rsplit("_", 1)[1])
    return "over" if hs + gs > line else "under"


def _remine_odds(rows, market, side):
    fields = {"1x2": {"home": ("odd1",), "draw": ("oddx",), "away": ("odd2",)},
              "ou_2.5": {"over": ("odd_over", "odd_o25"), "under": ("odd_under", "odd_u25")},
              "btts": {"yes": ("odd_gg",), "no": ("odd_ng",)},
              "ht_1x2": {"home": ("odd1_ht",), "draw": ("oddx_ht",), "away": ("odd2_ht",)}}.get(market, {})
    if market.startswith("ou_") or market.startswith("ht_ou_"):
        line = market.rsplit("_", 1)[1].replace(".", "")
        suffix = "_ht" if market.startswith("ht_") else ""
        explicit = {"over": (f"odd_o{line}{suffix}",), "under": (f"odd_u{line}{suffix}",)}
        fields = {s: tuple(dict.fromkeys((*fields.get(s, ()), *cols))) for s, cols in explicit.items()}
    # Conservative minimum for the SAME side/market only. Never use an
    # opposing vote's odds, fair odds or an invented complement price.
    prices = [_number(row.get(field)) for row in rows for field in fields.get(side, ())]
    prices = [v for v in prices if v is not None and v > 1]
    return min(prices) if prices else None


def collect_observations(con, *, start, as_of, include_snapshot=False):
    coverage, source_rows = {}, {}
    for source in (*REMINE_SOURCES, "betexplorer"):
        # Raw predictions must win over a pre-settled convenience view:
        # another independent donor may settle rows absent from that view.
        table = next((t for t in (source, source + "_raw", source + "_settled")
                      if _table_exists(con, t)), None)
        if table is None:
            coverage[source] = {"status": "missing_table", "rows": 0}
            continue
        columns = _table_columns(con, table)
        if not {"date", "home", "away"}.issubset(columns):
            coverage[source] = {"status": "missing_identity_columns", "rows": 0}
            continue
        cursor = con.execute(f"SELECT * FROM {table} WHERE TRY_CAST(date AS DATE) >= ? "
                             "AND TRY_CAST(date AS DATE) < ?", [start, as_of])
        names = [col[0] for col in cursor.description]
        rows = [dict(zip(names, values)) for values in cursor.fetchall()]
        source_rows[source] = rows
        coverage[source] = {"status": "present" if rows else "no_rows_in_era", "table": table,
                            "rows": len(rows), "market_votes": {m: 0 for m in REMINE_MARKETS}}
        if include_snapshot:
            coverage[source].update(
                first_date=min((str(r["date"])[:10] for r in rows), default=None),
                last_date=max((str(r["date"])[:10] for r in rows), default=None),
                observation_sha256=hashlib.sha256("\n".join(sorted(
                    json.dumps(r, sort_keys=True, default=str) for r in rows
                )).encode()).hexdigest(),
                hash_basis="sorted_query_rows_in_exclusive_mining_window")


    scores = defaultdict(lambda: defaultdict(set))
    # Only self-scoring donors. In particular do NOT use results_donor or
    # categorical *_settled scores which may have been inherited from Forebet.
    donors = {"zulubet", "statarea", "vitibet", "scoutingstats", "prosoccer",
              "bettingclosed", "betexplorer"}
    for source in donors:
        for row in source_rows.get(source, []):
            key = _remine_key(row)
            if key is None or str(row.get("result_source") or source) == "forebet":
                continue
            for period, prefix in (("ft", ""), ("ht", "ht_")):
                pair = _score_pair(row, prefix)
                if pair is not None:
                    scores[key][period].add(pair)
    resolved = {key: {period: next(iter(values)) for period, values in periods.items()
                      if len(values) == 1} for key, periods in scores.items()}
    observations = defaultdict(dict)
    ambiguous = set()
    for source in REMINE_SOURCES:
        for row in source_rows.get(source, []):
            key = _remine_key(row)
            if key is None:
                continue
            for market in REMINE_MARKETS:
                signal = _remine_signal(row, market)
                if signal is None:
                    continue
                identity = (key, market, source)
                bucket = observations[(key, market)]
                vote = {"side": signal[0], "probs": signal[1], "row": row}
                previous = bucket.get(source)
                if previous:
                    before = (previous["side"], previous["probs"],
                              previous["row"].get("kickoff") or previous["row"].get("time"))
                    after = (vote["side"], vote["probs"], row.get("kickoff") or row.get("time"))
                    if before != after:
                        ambiguous.add(identity)
                    else:
                        # Identical predictions still count once. Quote updates
                        # may not make historical ROI depend on input row order:
                        # retain the conservative explicit price for each field.
                        vote["row"] = dict(row)
                        for field, old in previous["row"].items():
                            if not field.startswith("odd"):
                                continue
                            prices = [_number(old), _number(row.get(field))]
                            prices = [p for p in prices if p is not None and p > 1]
                            if prices:
                                vote["row"][field] = min(prices)
                bucket[source] = vote
    return coverage, observations, ambiguous, resolved, scores


def project_votes(votes, sources, strategy, follow=None):
    """Return (selected side, actual selected-side mean percent), or no signal.

    Extra sources cannot veto a validated subset. Missing/ambiguous members
    cannot be replaced. Strict majorities require disagreement; dissent-follow
    requires disagreement, but need not follow a numerically minority voter.
    """
    if not sources or any(s not in votes for s in sources):
        return None
    electorate = [votes[s] for s in sources]
    counts = Counter(v["side"] for v in electorate)
    if strategy == "single":
        if len(sources) != 1 or follow is not None:
            return None
        side = electorate[0]["side"]
    elif strategy == "unanimous":
        if len(sources) < 2 or len(counts) != 1 or follow is not None:
            return None
        side = electorate[0]["side"]
    elif strategy == "majority":
        side, n = counts.most_common(1)[0]
        if len(counts) == 1 or n <= len(sources) / 2 or follow is not None:
            return None
    elif strategy == "disagree_follow":
        if len(counts) == 1 or follow not in sources:
            return None
        side = votes[follow]["side"]
    else:
        return None
    contributing = [votes[follow]] if follow else electorate
    probability = (100 * sum(v["probs"][side] for v in contributing) / len(contributing)
                   if all(v["probs"] is not None for v in contributing) else None)
    return side, probability


def contract_spec(edge):
    """Validate an explicit recipe; never infer certification from a label."""
    sources = edge.get("sources")
    threshold = edge.get("threshold")
    strategy, follow = edge.get("strategy"), edge.get("follow_source")
    if (not isinstance(sources, list) or not sources
            or any(s not in REMINE_SOURCES for s in sources)
            or sources != sorted(set(sources))
            or edge.get("market") not in REMINE_MARKETS
            or type(threshold) is not int or threshold not in REMINE_THRESHOLDS
            or strategy not in ("single", "unanimous", "majority", "disagree_follow")
            or (strategy == "single" and len(sources) != 1)
            or (strategy != "single" and len(sources) < 2)
            or (strategy == "disagree_follow" and follow not in sources)
            or (strategy != "disagree_follow" and follow is not None)):
        raise ValueError("invalid post-Forebet recipe")
    return {"schema": SCHEMA, "market": edge["market"], "sources": sources,
            "strategy": strategy, "follow_source": follow, "threshold": threshold}


def contract_identity(edge):
    spec = contract_spec(edge)
    encoded = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
    return "pfc_" + hashlib.sha256(encoded).hexdigest()[:24]


def validate_contract(edge):
    identity = contract_identity(edge)
    if (edge.get("contract_schema") != SCHEMA or edge.get("contract_id") != identity
            or edge.get("rule") != identity or edge.get("view") != identity
            or edge.get("where") != "1=1"):
        raise ValueError("post-Forebet contract identity mismatch")
    window = edge.get("mining_window", {})
    start, split, end = (window.get(k, "") for k in ("start", "split", "as_of_exclusive"))
    for value in (start, split, end):
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError("invalid contract chronology")
    if not POST_FOREBET_START <= start < split < end:
        raise ValueError("invalid contract chronology")
    activated = edge.get("activated_as_of", "")
    if date.fromisoformat(activated).isoformat() != activated or activated < end:
        raise ValueError("activation must follow the exclusive validation boundary")
    return identity


def contract_rows(observations, ambiguous, resolved, edge, *, settled=True):
    """Project an exact recipe; never substitute votes, sides, lines or prices."""
    sources, market = edge["sources"], edge["market"]
    for (key, observed_market), all_votes in observations.items():
        if key[0] < edge.get("mining_window", {}).get("start", POST_FOREBET_START):
            continue
        if observed_market != market:
            continue
        votes = {s: v for s, v in all_votes.items() if (key, market, s) not in ambiguous}
        projected = project_votes(votes, sources, edge["strategy"], edge.get("follow_source"))
        if projected is None:
            continue
        side, probability = projected
        if edge["threshold"] and (probability is None or probability < edge["threshold"]):
            continue
        outcome = _remine_outcome(resolved.get(key, {}), market)
        if settled and outcome is None:
            continue
        rows = [votes[s]["row"] for s in sources]
        # Live emission may not resurface completed fixtures, even if the
        # market outcome is missing (e.g. no separate half-time scores).
        if not settled and any(_score_pair(r) is not None or
                               str(r.get("status", "")).upper() in ("FT", "FINISHED", "AET", "PEN")
                               for r in rows):
            continue
        anchor = rows[0]
        yield {"date": key[0], "home": anchor["home"], "away": anchor["away"],
               "league": anchor.get("league"), "kickoff": anchor.get("kickoff") or anchor.get("time"),
               "pick": side, "outcome": outcome, "avg_p": probability,
               "pick_odds": _remine_odds(rows, market, side), "source_rows": rows}


def recreate_contract_views(con, edges, *, as_of=None):
    """Recreate only well-formed operational contracts in this connection.

    Consumers use current completed history, exclusive of today; their stored
    validation baseline remains immutable. One scan, no subset/threshold search.
    Missing inputs produce empty relations, never legacy substitutes.
    """
    import pandas as pd
    as_of = as_of or date.today().isoformat()
    valid = []
    for edge in edges:
        if edge.get("contract_schema") != SCHEMA:
            continue
        try:
            validate_contract(edge)
            valid.append(edge)
        except (TypeError, ValueError):
            continue
    if not valid:
        return set()
    _, observations, ambiguous, resolved, _ = collect_observations(
        con, start=min(e["mining_window"]["start"] for e in valid), as_of=as_of)
    columns = ["date", "home", "away", "league", "kickoff", "pick", "outcome", "avg_p", "pick_odds"]
    available = set()
    for edge in valid:
        rows = [{k: r[k] for k in columns}
                for r in contract_rows(observations, ambiguous, resolved, edge)]
        frame = pd.DataFrame(rows, columns=columns)
        # Empty frames need typed numeric columns for SUM/CASE consumers.
        for col in ("avg_p", "pick_odds"):
            frame[col] = pd.to_numeric(frame[col], errors="coerce").astype(float)
        for col in columns:
            if col not in ("avg_p", "pick_odds"):
                frame[col] = frame[col].astype("string")
        con.register(edge["view"], frame)
        available.add(edge["view"])
    return available


def enhancement_cohort(con, edge, *, as_of, selection, min_n=100, cache=None):
    """All outcomes of the exact parent recipe; never condition on its winning.

    No Forebet voter/result inheritance, substitute electorate, future fixtures
    or probability-band proxy. This is descriptive evidence, NOT certification
    of an enhancement market or an estimate of betting returns.
    """
    identity = validate_contract(edge)
    if date.fromisoformat(as_of).isoformat() != as_of or edge['activated_as_of'] > as_of:
        raise ValueError('cohort precedes activation or has an invalid boundary')
    # Caller-owned, read-phase-only cache. Never shared across warehouse builds
    # or invocations; validation above still runs on every request.
    start = edge['mining_window']['start']
    snapshot_key = ('observations', con, start, as_of)
    cohort_key = ('cohort', con, identity, start, as_of, selection, min_n)
    if cache is not None and cohort_key in cache:
        cached = cache[cohort_key]
        return dict(cached) if cached is not None else None
    if cache is not None and snapshot_key in cache:
        snapshot = cache[snapshot_key]
    else:
        snapshot = collect_observations(con, start=start, as_of=as_of)
        if cache is not None:
            cache[snapshot_key] = snapshot
    _, observations, ambiguous, resolved, _ = snapshot
    pairs = []
    parent_hits = 0
    for row in contract_rows(observations, ambiguous, resolved, edge):
        if row['pick'] != selection:
            continue
        pair = resolved.get(_remine_key(row), {}).get('ft')
        if pair is not None:
            pairs.append(pair)
            parent_hits += row['pick'] == row['outcome']
    n = len(pairs)
    if not n or n < min_n:
        if cache is not None:
            cache[cohort_key] = None
        return None
    def rate(predicate):
        return sum(predicate(h, a) for h, a in pairs) / n
    result = {'n': n, 'avg_goals': sum(h + a for h, a in pairs) / n,
              'contract_id': identity, 'as_of_exclusive': as_of,
              'window_start': start, 'selection': selection,
              'parent_hits': parent_hits, 'parent_hit_rate': parent_hits / n}
    for goals in (2, 3, 4, 5):
        result[f'over{goals - 1}5'] = rate(lambda h, a: h + a >= goals)
    result['btts'] = rate(lambda h, a: h > 0 and a > 0)
    for side in ('h', 'a'):
        for goals in (1, 2, 3, 4):
            result[f'{side}_o{goals - 1}5'] = rate(
                lambda h, a: (h if side == 'h' else a) >= goals)
    if cache is not None:
        cache[cohort_key] = dict(result)
    return result
