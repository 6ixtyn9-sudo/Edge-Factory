"""
backfill.py — replay a source across a date range (resumable).
Tracks progress in the DB itself (raw_payloads fetch_key) so it can be
interrupted and re-run safely.

    python scripts/backfill.py forebet 2024-01-01 2026-06-11
"""
import sys
import time
from datetime import date, timedelta

from edgefactory import db
from edgefactory.pipelines.ingest import ingest_day


def main():
    source_key, start_s, end_s = sys.argv[1], sys.argv[2], sys.argv[3]
    start, end = date.fromisoformat(start_s), date.fromisoformat(end_s)

    sid = db.client().table("sources").select("id").eq(
        "key", source_key).execute().data[0]["id"]
    done = {r["fetch_key"] for r in db.fetch_all(
        "raw_payloads", "fetch_key", source_id=sid)}

    d, n = start, 0
    while d <= end:
        key = f"day:{d.isoformat()}"
        if key not in done:
            try:
                stats = ingest_day(source_key, d)
                n += 1
                print(f"{d}: {stats}")
            except Exception as e:
                print(f"{d}: FAILED ({e}) — continuing")
            time.sleep(0.5)
        d += timedelta(days=1)
    print(f"\nBackfill complete: {n} new days ingested.")


if __name__ == "__main__":
    main()
