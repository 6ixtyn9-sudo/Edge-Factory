"""
ingest.py — source adapter -> Supabase (events, predictions, odds, results).
Idempotent: re-running any day is safe. Raw payloads archived for replay.

    python -m edgefactory.pipelines.ingest forebet 2026-06-11
    python -m edgefactory.pipelines.ingest forebet 2026-06-01 2026-06-11
"""
import json
import sys
from datetime import date, timedelta

from .. import db
from ..models import NormalizedEvent
from ..sources import get_source


def _source_id(key: str) -> int:
    rows = db.client().table("sources").select("id").eq("key", key).execute().data
    if not rows:
        raise RuntimeError(f"source '{key}' not registered in sources table")
    return rows[0]["id"]


def _sport_id(key: str) -> int:
    return db.client().table("sports").select("id").eq("key", key).execute().data[0]["id"]


def ingest_day(source_key: str, day: date) -> dict:
    src = get_source(source_key)
    sid = _source_id(source_key)
    sport_id = _sport_id(src.sport)

    raw = src.fetch_day(day)
    db.insert_ignore("raw_payloads", [{
        "source_id": sid, "fetch_key": f"day:{day.isoformat()}",
        "payload": json.loads(json.dumps(raw, default=str)),
    }], on_conflict="source_id,fetch_key,captured_at")

    events = src.normalize(raw, day)
    if not events:
        return {"events": 0}

    # -- competitions & participants (upsert on natural key) --
    comps, parts = {}, {}
    for e in events:
        comps[e.competition_ref] = {
            "sport_id": sport_id, "country": e.country, "name": e.competition_name,
            "source_key": source_key, "source_ref": e.competition_ref}
        for ref, name in ((e.home_ref, e.home_name), (e.away_ref, e.away_name)):
            parts[ref] = {"sport_id": sport_id, "name": name,
                          "source_key": source_key, "source_ref": ref}
    db.upsert("competitions", list(comps.values()), "source_key,source_ref")
    db.upsert("participants", list(parts.values()), "source_key,source_ref")

    comp_ids = {r["source_ref"]: r["id"] for r in db.fetch_all(
        "competitions", "id,source_ref", source_key=source_key)}
    part_ids = {r["source_ref"]: r["id"] for r in db.fetch_all(
        "participants", "id,source_ref", source_key=source_key)}

    # -- events --
    ev_rows = []
    for e in events:
        ev_rows.append({
            "sport_id": sport_id, "competition_id": comp_ids.get(e.competition_ref),
            "home_id": part_ids.get(e.home_ref), "away_id": part_ids.get(e.away_ref),
            "start_time": e.start_time.isoformat(),
            "source_key": source_key, "source_ref": e.source_ref,
            "status": ("void" if e.result and e.result.status == "void"
                       else "finished" if e.result else "scheduled")})
    db.upsert("events", ev_rows, "source_key,source_ref")
    ev_ids = {r["source_ref"]: r["id"] for r in db.fetch_all(
        "events", "id,source_ref", source_key=source_key)}

    # -- predictions & odds (append-only snapshots) --
    pred_rows, odds_rows, res_rows = [], [], []
    for e in events:
        eid = ev_ids[e.source_ref]
        for p in e.predictions:
            pred_rows.append({
                "event_id": eid, "source_id": sid, "market": p.market,
                "selection": p.selection, "probability": p.probability,
                "extra": p.extra,
                "content_hash": db.content_hash(p.market, p.selection,
                                                p.probability, p.extra)})
        for o in e.odds:
            odds_rows.append({
                "event_id": eid, "source_id": sid, "bookmaker": o.bookmaker,
                "market": o.market, "selection": o.selection, "odds": o.odds,
                "content_hash": db.content_hash(o.market, o.selection, o.odds)})
        if e.result and e.result.status == "finished":
            res_rows.append({
                "event_id": eid, "outcome_home": e.result.outcome_home,
                "outcome_away": e.result.outcome_away,
                "score_data": e.result.score_data})

    db.insert_ignore("predictions", pred_rows,
                     "event_id,source_id,market,selection,content_hash")
    db.insert_ignore("odds_snapshots", odds_rows,
                     "event_id,source_id,bookmaker,market,selection,content_hash")
    db.upsert("results", res_rows, "event_id")

    src.close()
    return {"events": len(events), "predictions": len(pred_rows),
            "odds": len(odds_rows), "results": len(res_rows)}


def main():
    source_key = sys.argv[1]
    start = date.fromisoformat(sys.argv[2])
    end = date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else start
    d = start
    while d <= end:
        stats = ingest_day(source_key, d)
        print(f"{d}: {stats}")
        d += timedelta(days=1)


if __name__ == "__main__":
    main()
