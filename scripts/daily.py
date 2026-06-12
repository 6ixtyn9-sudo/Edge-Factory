"""
daily.py — THE cron entrypoint. One command, full cycle:
  1. ingest yesterday (results land) + today + tomorrow (new fixtures)
  2. settle markets & picks, auto-bench decayed edges
  3. emit new picks from certified edges

Run it from GitHub Actions, a Pi, a VPS — anywhere with the .env.
"""
from datetime import date, timedelta

from edgefactory.pipelines import emit, ingest, settle
from edgefactory.sources import SOURCES


def main():
    today = date.today()
    for key in SOURCES:
        for d in (today - timedelta(days=1), today, today + timedelta(days=1)):
            try:
                stats = ingest.ingest_day(key, d)
                print(f"[ingest] {key} {d}: {stats}")
            except Exception as e:  # one bad day must not kill the run
                print(f"[ingest] {key} {d} FAILED: {e}")

    print(f"[settle] market_results: {settle.settle_markets()}")
    print(f"[settle] picks: {settle.settle_picks()}")
    benched = settle.auto_bench()
    if benched:
        print(f"[settle] AUTO-BENCHED: {benched}")

    emit.main()


if __name__ == "__main__":
    main()
