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
from edgefactory.settlement import terminal_event_disposition

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


def collect_observations(con, *, start, as_of, include_snapshot=False,
                         regulation_only=False):
    """Collect once; ENH can exclude disputed event status/score periods.

    Default contract mining/main semantics are unchanged. Missing status on a
    legacy score is not a verified period, but is not invented as a disposition.
    """
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
    blocked = set()
    for source in donors:
        for row in source_rows.get(source, []):
            key = _remine_key(row)
            if key is None or str(row.get("result_source") or source) == "forebet":
                continue
            if regulation_only:
                status = str(row.get("status") or "").strip().upper()
                # A score-shaped value is not proof of a played regulation
                # result. Keep contradictory status/period evidence out of
                # live ENH rates, regardless of donor or row order. No cash
                # void, guessed 90-minute score or alias override is inferred.
                if (terminal_event_disposition(status) or status in {
                        "AET", "PEN", "PENS", "PENALTIES", "AFTER EXTRA TIME",
                        "AFTER EXTRA-TIME", "AFTER PENALTIES"}):
                    blocked.add(key)
            for period, prefix in (("ft", ""), ("ht", "ht_")):
                if regulation_only and any(isinstance(row.get(prefix + f), bool)
                                           for f in ("hs", "gs")):
                    continue
                pair = _score_pair(row, prefix)
                if pair is not None:
                    scores[key][period].add(pair)
    resolved = {key: {period: next(iter(values)) for period, values in periods.items()
                      if len(values) == 1} for key, periods in scores.items()
                if key not in blocked}
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
                        conflicts = set(previous["row"].get("_enh_conflicts", []))
                        conflicts.update(f for f in ENH_FORECAST_FIELDS
                                         if _number(previous["row"].get(f)) != _number(row.get(f)))
                        vote["row"]["_enh_conflicts"] = sorted(conflicts)
                        vote["row"]["_enh_timing_blocked"] = (
                            not _enhancement_forecast_eligible(previous["row"])
                            or not _enhancement_forecast_eligible(row))
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


def contract_rows(observations, ambiguous, resolved, edge, *, settled=True, enhancement_features=False):
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
        emitted = {"date": key[0], "home": anchor["home"], "away": anchor["away"],
               "league": anchor.get("league"), "kickoff": anchor.get("kickoff") or anchor.get("time"),
               "pick": side, "outcome": outcome, "avg_p": probability,
               "pick_odds": _remine_odds(rows, market, side), "source_rows": rows}
        if enhancement_features:
            # Extra observed sources are context, never replacement voters.
            emitted['enhancement_source_features'] = enhancement_source_features(
                [v['row'] for v in votes.values()])
            emitted['enhancement_feature_sources'] = sorted(votes)
        yield emitted


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



# Feature allowlist: predictions, not realized scores, HT results, prices or
# inherited Main/Forebet model inputs. Same units and builder in fit and serve.
ENH_FORECAST_FIELDS = ("p1", "px", "p2", "p_o15", "p_o25", "p_o35", "p_o45", "p_gg", "xg_home", "xg_away")
ENH_FORECAST_MARKETS = {"1x2": ("home", "draw", "away"),
                        "ou_1.5": ("over",), "ou_2.5": ("over",),
                        "ou_3.5": ("over",), "ou_4.5": ("over",), "btts": ("yes",)}
ENH_FORM_FIELDS = ("gf", "ga", "over15", "over25", "over35", "btts")
ENH_OPTIONAL_FEATURES = tuple(
    f"forecast_{market}_{side}_{stat}"
    for market, sides in ENH_FORECAST_MARKETS.items() for side in sides
    for stat in ("mean", "spread")) + tuple(
    f"forecast_xg_{side}_{stat}" for side in ('home', 'away')
    for stat in ('mean', 'spread')) + tuple(
    f"{side}_{field}" for side in ("home_form", "away_form", "h2h")
    for field in ENH_FORM_FIELDS)


def _enhancement_forecast_eligible(row):
    from datetime import datetime
    if row.get('_enh_timing_blocked'):
        return False
    # Inspect every retained receipt, not whichever one happened to be first.
    for captured in (row.get('captured_at'), row.get('observed_at_utc')):
        if not captured:
            continue
        try:
            at = datetime.fromisoformat(str(captured).replace('Z', '+00:00'))
            ko = datetime.fromisoformat(str(row.get('kickoff')).replace('Z', '+00:00'))
            if at.tzinfo is None or ko.tzinfo is None or at >= ko:
                return False
        except (TypeError, ValueError):
            return False
    return True


def enhancement_source_features(rows):
    """Observed same-fixture forecasts; extras never replace contract voters.

    Legacy archives lack authenticated capture times. We cannot certify their
    point-in-time provenance; explicitly late/timing-malformed observations
    are excluded. Missing values remain None, never a neutral prediction.
    """
    buckets = defaultdict(list)
    for original in rows:
        row = dict(original)
        if not _enhancement_forecast_eligible(row):
            continue
        for field in ENH_FORECAST_FIELDS:
            if isinstance(row.get(field), bool) or field in row.get('_enh_conflicts', []):
                row[field] = None
        if any(f in row.get('_enh_conflicts', []) for f in ('p1', 'px', 'p2')):
            for field in ('p1', 'px', 'p2'):
                row[field] = None
        for side in ('home', 'away'):
            value = _number(row.get('xg_' + side))
            if value is not None and value >= 0:
                buckets['forecast_xg_' + side].append(value)
        for market, sides in ENH_FORECAST_MARKETS.items():
            signal = _remine_signal(row, market)
            if signal is None or signal[1] is None:
                continue
            for side in sides:
                buckets[f"forecast_{market}_{side}"].append(signal[1][side])
    result = {}
    for market, sides in ENH_FORECAST_MARKETS.items():
        for side in sides:
            name = f"forecast_{market}_{side}"
            values = buckets.get(name, [])
            result[name + '_mean'] = sum(values) / len(values) if values else None
            result[name + '_spread'] = max(values) - min(values) if values else None
    for side in ('home', 'away'):
        name = 'forecast_xg_' + side
        values = buckets.get(name, [])
        result[name + '_mean'] = sum(values) / len(values) if values else None
        result[name + '_spread'] = max(values) - min(values) if values else None
    return result


def _enhancement_feature_valid(name, value):
    return (type(value) in (int, float) and math.isfinite(value) and value >= 0
            and (name.endswith(('_gf', '_ga')) or name.startswith('forecast_xg_') or value <= 1))


def _enhancement_snapshot(con, start, as_of, cache):
    key = ('observations', con, start, as_of, 'enh_regulation')
    if cache is not None and key in cache:
        return cache[key]
    snapshot = collect_observations(con, start=start, as_of=as_of, regulation_only=True)
    if cache is not None:
        cache[key] = snapshot
    return snapshot


def _enhancement_archive(con, start, as_of, resolved, cache):
    from edgefactory.form_intel import ResultsArchive
    key = ('enh_form_archive', con, start, as_of)
    if cache is not None and key in cache:
        return cache[key]
    # Reuse the cohort's adjudication, NOT load_archive's unfiltered donors.
    # Canonical fixture keys preserve squad distinctions; no fuzzy/trunc joins.
    archive = ResultsArchive([dict(date=k[0], home=k[1], away=k[2],
        hs=v['ft'][0], gs=v['ft'][1], league='')
        for k, v in sorted(resolved.items()) if 'ft' in v])
    if cache is not None:
        cache[key] = archive
    return archive


def enhancement_model_features(row, archive, cache=None):
    """One feature meaning in historical fitting and current fixture scoring.

    form_intel's last-10 windows/min-history/squad guards are reused. Same-day
    results are never features. Counts are coverage, not invented zero rates.
    """
    from edgefactory.form_intel import team_form, pair_history, MIN_HISTORY, H2H_MIN_MEETINGS
    features = dict.fromkeys(ENH_OPTIONAL_FEATURES)
    supplied = row.get('enhancement_source_features') or {}
    for name in features:
        value = supplied.get(name)
        if name.startswith('forecast_') and _enhancement_feature_valid(name, value):
            features[name] = float(value)
    for prefix, team in (('home_form', row['home']), ('away_form', row['away']), ('h2h', None)):
        key = ('enh_form', id(archive), row['date'], prefix,
               source_team_key(team) if team else (source_team_key(row['home']), source_team_key(row['away'])))
        form = cache.get(key) if cache is not None else None
        if form is None:
            form = (team_form(archive, team, row['date']) if team else
                    pair_history(archive, row['home'], row['away'], row['date']))
            if cache is not None:
                cache[key] = form
        n = form['n']
        if n < (MIN_HISTORY if team else H2H_MIN_MEETINGS):
            continue
        features[prefix + '_gf'] = form['goals_for' if team else 'goals_for_home'] / n
        features[prefix + '_ga'] = form['goals_against' if team else 'goals_for_away'] / n
        for field, hits in (('over15', 'over_15_hits'), ('over25', 'over_25_hits'),
                            ('over35', 'over_35_hits'), ('btts', 'btts_hits')):
            features[prefix + '_' + field] = form[hits] / n
    probability = row.get('avg_p')
    features['confidence'] = (probability / 100 if type(probability) in (int, float)
                              and math.isfinite(probability) and 0 <= probability <= 100 else None)
    return features


def enhancement_ml_inputs(con, edge, pick, cache=None):
    """Fixture-bound feature receipt, separate from the shared cached fit."""
    start, day = edge['mining_window']['start'], pick['date']
    resolved = _enhancement_snapshot(con, start, day, cache)[3]
    archive = _enhancement_archive(con, start, day, resolved, cache)
    return dict(fixture=[day, source_team_key(pick['home']), source_team_key(pick['away'])],
                contract_id=edge['contract_id'],
                sources=pick.get('enhancement_feature_sources', []),
                values=enhancement_model_features(pick, archive, cache))


def enhancement_feature_vector(features, model):
    """Recorded train-mean imputation + explicit missing flags, never defaults.

    Unobserved columns cannot enter the fit. Missing observations stay absent
    in the receipt; zero below is *standardized mean*, not a fabricated rate.
    """
    from edgefactory.enh_registry import MIN_COHORT_N
    cols = model['feature_cols']
    if (not cols or cols[0] != 'confidence' or len(cols) != len(set(cols))
            or any(c not in ('confidence', *ENH_OPTIONAL_FEATURES) for c in cols)):
        raise ValueError('invalid enhancement feature contract')
    vector, missing = [], []
    for col in cols:
        mean, scale = model['feature_means'][col], model['feature_scales'][col]
        if (type(mean) not in (int, float) or not math.isfinite(mean)
                or type(scale) not in (int, float) or not math.isfinite(scale) or scale <= 0
                or type(model['feature_observed_n'][col]) is not int
                or not MIN_COHORT_N <= model['feature_observed_n'][col] <= model['n']):
            raise ValueError('invalid observed training statistics')
        value = features.get(col)
        if value is not None and not _enhancement_feature_valid(col, value):
            raise ValueError('invalid feature value')
        if col == 'confidence' and value is None:
            raise ValueError('missing parent confidence')
        vector.append((value - mean) / scale if value is not None else 0.)
        if col != 'confidence':
            missing.append(float(value is None))
    return vector + missing

def enhancement_cohort(con, edge, *, as_of, selection, min_n=100, cache=None, fit_ml=False):
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
    cohort_key = ('cohort', con, identity, start, as_of, selection, min_n, 'enh_regulation', fit_ml)
    if cache is not None and cohort_key in cache:
        from copy import deepcopy
        return deepcopy(cache[cohort_key])
    snapshot = _enhancement_snapshot(con, start, as_of, cache)
    _, observations, ambiguous, resolved, _ = snapshot
    pairs, training = [], []
    archive = _enhancement_archive(con, start, as_of, resolved, cache) if fit_ml else None
    feature_cache = cache if cache is not None else {}
    parent_hits = 0
    for row in contract_rows(observations, ambiguous, resolved, edge, enhancement_features=fit_ml):
        if row['pick'] != selection:
            continue
        pair = resolved.get(_remine_key(row), {}).get('ft')
        if pair is not None:
            pairs.append(pair)
            probability = _number(row.get('avg_p'))
            if probability is not None and 0 <= probability <= 100:
                training.append((_remine_key(row), probability / 100, f'{pair[0]}:{pair[1]}',
                                 enhancement_model_features(row, archive, feature_cache) if fit_ml else {}))
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
    if fit_ml:
        # The existing sklearn learner, but with an ENH score-pair target, not
        # the unrelated main 1X2-correctness target. One fit per cached contract.
        from edgefactory.enh_registry import MIN_COHORT_N
        result['ml_status'] = 'insufficient_or_constant_training_data'
        training.sort(key=lambda r: r[0])
        observed = {c: [r[3][c] for r in training if r[3].get(c) is not None]
                    for c in ('confidence', *ENH_OPTIONAL_FEATURES)}
        result['ml_feature_coverage'] = {c: len(v) for c, v in observed.items()}
        cols = ['confidence'] + [c for c in ENH_OPTIONAL_FEATURES
            if len(observed[c]) >= MIN_COHORT_N and len(set(observed[c])) > 1]
        if (len(training) >= MIN_COHORT_N and any(len(set(observed[c])) > 1 for c in cols)
                and len({r[2] for r in training}) > 1):
            try:
                import warnings
                from sklearn.exceptions import ConvergenceWarning
                from sklearn.linear_model import LogisticRegression
                with warnings.catch_warnings():
                    warnings.simplefilter('error', ConvergenceWarning)
                    means = {c: sum(observed[c]) / len(observed[c]) for c in cols}
                    scales = {c: math.sqrt(sum((v - means[c]) ** 2 for v in observed[c]) / len(observed[c])) or 1.
                              for c in cols}
                    feature_spec = dict(feature_cols=cols, feature_means=means, feature_scales=scales,
                        feature_observed_n={c: len(observed[c]) for c in cols}, n=len(training))
                    model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
                    model.fit([enhancement_feature_vector(r[3], feature_spec) for r in training],
                              [r[2] for r in training])
                payload = dict(schema='enh_score_logit_v2', contract_id=identity,
                    feature_basis='observed_forecasts_and_prior_regulation_form',
                    train_window_start=start, form_window=10,
                    as_of_exclusive=as_of, selection=selection, n=len(training),
                    train_last_date=max(r[0][0] for r in training),
                    feature_min=min(r[1] for r in training),
                    feature_max=max(r[1] for r in training),
                    training_sha256=hashlib.sha256(json.dumps(training).encode()).hexdigest(),
                    **{k: v for k, v in feature_spec.items() if k != 'n'},
                    classes=model.classes_.tolist(), coef=model.coef_.tolist(),
                    intercept=model.intercept_.tolist())
                payload['model_key'] = hashlib.sha256(json.dumps(
                    payload, sort_keys=True, allow_nan=False).encode()).hexdigest()
                result.update(ml_model=payload, ml_status='fitted')
            except (ImportError, ValueError, TypeError, AttributeError, ArithmeticError, Warning):
                # Optional learner/API failure must not erase measured evidence.
                result['ml_status'] = 'fit_unavailable'
    if cache is not None:
        from copy import deepcopy
        cache[cohort_key] = deepcopy(result)
    return result
