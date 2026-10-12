"""The A-2 census, run once per tree (see a_census_before_after.sh).

Reads the settled registry's fixtures, walks each side's prior archive rows
through ``form_intel`` - the same reader the features use - and prints the
totals. Whatever tree is on PYTHONPATH decides the identity layer, so running
this with the parent commit's src and with the working tree's src measures the
identity change itself, not a reconstruction of it.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# The driver module comes from this bundle; ``edgefactory`` comes from
# PYTHONPATH (never from a hard-coded path) so the same script can be run
# against another tree's src - that is what makes the before/after real.
sys.path.insert(0, HERE)

from edgefactory import form_intel as fi  # noqa: E402

from intel_report import LOCALDATA, load_records  # noqa: E402

WINDOW = 5


def main() -> None:
    records = load_records(LOCALDATA)
    fixtures = sorted({(r["date"], r["home"], r["away"]) for r in records})
    sides = [(team, day) for day, home, away in fixtures for team in (home, away)]
    archive = fi.load_archive(LOCALDATA)
    priors = sum(len(archive.prior_rows(t, d)) for t, d in sides)
    sufficient = sum(1 for t, d in sides if len(archive.prior_rows(t, d)) >= WINDOW)
    print(json.dumps({"edgefactory_from": fi.__file__,
                      "tree": os.environ.get("PYTHONPATH", "").split(":")[0],
                      "fixture_sides": len(sides), "prior_rows": priors,
                      "sides_with_window": sufficient, "window": WINDOW}, indent=2))


if __name__ == "__main__":
    main()
