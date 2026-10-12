"""W3 identity census: the canonical rule and the width-9 bucket, side by side.

Measured on the committed archives over the fixture sides the registry settled.
No classification heuristic is applied to names here: the width-9-only rows are
printed verbatim as (query, row side span) pairs so the reader judges them, and
the dedup-key comparison counts merges, not guesses.

    PYTHONPATH=src .venv/bin/python \
        handoff/round5_form_h2h_2026-10-12/w3_identity_census.py
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "src")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from edgefactory import form_intel as fi                        # noqa: E402
from edgefactory.util import norm_team                          # noqa: E402
from intel_report import load_records                           # noqa: E402

LOCALDATA = "localdata"
WINDOW = 5


def main() -> None:
    print("W3 identity census — command: PYTHONPATH=src .venv/bin/python "
          "handoff/round5_form_h2h_2026-10-12/w3_identity_census.py")
    records = load_records(LOCALDATA)
    fixtures = sorted({(r["date"], r["home"], r["away"]) for r in records})
    sides = [(team, day) for day, home, away in fixtures for team in (home, away)]
    print(f"registry records {len(records)}, distinct fixtures {len(fixtures)}, "
          f"fixture sides {len(sides)}")

    canonical = fi.source_team_key
    canon = fi.load_archive(LOCALDATA)
    print(f"archive rows: canonical {len(canon.rows)}", end="")

    def ident(rows):
        return {(r["date"], r["home"], r["away"], r["hs"], r["gs"], r["source"])
                for r in rows}

    # The archive indexes are built under whichever key is active, and the
    # lookups read the same module-global key AT CALL TIME - so each reading
    # must be queried with its own key in force. Interleaving the two (the
    # first version of this script did) queries a width-9 index with canonical
    # keys and reports nonsense; found and fixed 2026-10-12.
    def pass_over(archive):
        out = {}
        for team, day in sides:
            out[(team, day)] = ident(archive.prior_rows(team, day))
        return out

    seen_canon = pass_over(canon)
    fi.source_team_key = norm_team
    wide = fi.load_archive(LOCALDATA)
    seen_wide = pass_over(wide)
    fi.source_team_key = canonical
    print(f", width-9 {len(wide.rows)}")

    stats = Counter()
    width9_only: Counter = Counter()
    for team, day in sides:
        a, b = seen_canon[(team, day)], seen_wide[(team, day)]
        stats["canonical"] += len(a)
        stats["width9"] += len(b)
        stats["both"] += len(a & b)
        stats["width9_only"] += len(b - a)
        stats["canonical_only"] += len(a - b)
        stats["sides_canon_sufficient"] += len(a) >= WINDOW
        stats["sides_wide_sufficient"] += len(b) >= WINDOW
        for row in b - a:
            _date, home, away, _hs, _gs, _src = row
            width9_only[(team, f"{home} v {away}")] += 1

    print()
    print(f"prior rows over the {len(sides)} sides: canonical {stats['canonical']}"
          f"   width-9 {stats['width9']}")
    print(f"  in both readings: {stats['both']}")
    print(f"  width-9 only: {stats['width9_only']}")
    print(f"  canonical only: {stats['canonical_only']}")
    print("  NOTE: the width-9 reading reads MORE rows here, not fewer: its")
    print("  wider bucket attaches other clubs' and other squads' rows to the")
    print("  query (the width-9-only rows are listed verbatim below), so sides")
    print("  look covered while much of the history behind them is not theirs.")
    print("  The first version of this script interleaved the two readings and")
    print("  queried a width-9 index with canonical keys, reporting the")
    print("  opposite; fixed 2026-10-12 - see the note in pass_over().")
    print()
    print("coverage: fixture sides with >=5 prior matches:")
    print(f"  canonical: {stats['sides_canon_sufficient']}/{len(sides)} sides "
          f"(driver: 376/409 records)")
    print(f"  width-9  : {stats['sides_wide_sufficient']}/{len(sides)} sides "
          f"(driver: 376/409 records)")
    print()
    print(f"width-9-only rows, verbatim pairs ({stats['width9_only']} rows):")
    for (team, span), count in width9_only.most_common():
        print(f"  {team:38s} <- {span!r} x{count}")
    print()
    groups = defaultdict(list)
    for row in canon.rows:
        groups[(row["date"], norm_team(row["home"]), norm_team(row["away"]),
                row["hs"], row["gs"])].append(row)
    conflicts = {k: v for k, v in groups.items() if len(v) > 1 and
                 len({(canonical(r["home"]), canonical(r["away"])) for r in v}) > 1}
    dropped = sum(len(v) - 1 for v in conflicts.values())
    print(f"the width-9 dedup key would merge {len(conflicts)} same-date/"
          f"same-score groups whose canonical identities differ, dropping "
          f"{dropped} rows")
    for key, members in list(conflicts.items())[:10]:
        names = " / ".join(sorted(f"{r['home']} v {r['away']}" for r in members))
        print(f"  {key[0]}  {names}")


if __name__ == "__main__":
    main()
