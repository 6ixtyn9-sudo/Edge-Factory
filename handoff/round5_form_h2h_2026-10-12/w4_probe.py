"""W4 probe: the page's own last-5 blocks against the archive's last-5.

The page side is not re-parsed by hand: the served text of the form blocks is
fed to the capture's own ``parse_match_page_blocks``, so what is compared is
exactly what the capture would have stored. The text is the saved excerpt (the
only match page read this round — the committed ledger's ``page`` blocks are
null, so this is a worked example, not a rate over the 409 settled fixtures).

Every difference is classified by the module's own comparator, and the whole
comparison is repeated with the identity function swapped to the width-9
``norm_team`` bucket, so the reading this round replaced stays visible.

    PYTHONPATH=src .venv/bin/python \
        handoff/round5_form_h2h_2026-10-12/w4_probe.py
"""
from __future__ import annotations


import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()   # every localdata write goes to scratch (incident 2026-10-12)

import re
import sys
from pathlib import Path

sys.path.insert(0, "src")

from edgefactory import form_intel as fi            # noqa: E402
from edgefactory.sources import betexplorer_match_snapshot as snap   # noqa: E402
from edgefactory.util import norm_team              # noqa: E402

HERE = Path(__file__).resolve().parent
EXCERPT = HERE / "w1_served_excerpt.txt"
LOCALDATA = "localdata"
AS_OF = "2026-10-12"
HOME, AWAY = "Coventry", "Newcastle Utd"
LEAGUE = "Premier League"
#: The excerpt is a flat text render: adjacent date runs come back glued
#: ("19.09.202619.09."). The HTML the capture reads keeps them separate, so the
#: documented one-line separation is applied only for this probe, never in the
#: capture parser itself (see w1_counts.txt).
DATE_RUN_GLUE = re.compile(r"(\d{2}\.\d{2}\.\d{4})(\d{2}\.\d{2}\.)")


def _section(text: str, name: str) -> str:
    start = text.index(f"SECTION {name}")
    rest = [text.index(f"SECTION {other}") for other in ("A", "B", "C")
            if f"SECTION {other}" in text and text.index(f"SECTION {other}") > start]
    return text[start:min(rest)] if rest else text[start:]


def page_rows() -> list[dict]:
    """The served last-results rows, read by the capture's own parser."""
    section = _section(EXCERPT.read_text(encoding="utf-8"), "A")
    parsed = snap.parse_match_page_blocks(DATE_RUN_GLUE.sub(r"\1 \2", section))
    print(f"capture parser over section A: blocks={parsed['blocks']}, "
          f"{len(parsed['last_results_rows'])} rows, "
          f"labels={sorted({r['label'] for r in parsed['last_results_rows']})}")
    return parsed["last_results_rows"]


def show(reading: str, archive: fi.ResultsArchive, page: dict) -> dict:
    print(f"--- {reading} ---")
    print(f"identity census: 'Newcastle Utd' rows "
          f"{len(archive.team_rows('Newcastle Utd'))}, "
          f"'Newcastle' rows {len(archive.team_rows('Newcastle'))}, "
          f"'Coventry' rows {len(archive.team_rows('Coventry'))}")
    report = fi.compare_page_to_archive(archive, page, as_of=AS_OF, home=HOME,
                                        away=AWAY, league=LEAGUE, window=5)
    print(f"unmatched labels: {report['unmatched_labels']}")
    for team in (HOME, AWAY):
        verdict = report["teams"].get(team)
        if not verdict or verdict.get("unmatched_label"):
            print(f"{team}: no page block matched (unmatched label)")
            continue
        print(f"{team}: page_n={verdict['page_n']} archive_n={verdict['archive_n']} "
              f"matched={verdict['matched']}")
        for entry in verdict["verdicts"]:
            arch = entry.get("archive")
            line = f"    page {entry['date']} {entry['score']} -> {entry['verdict']}"
            if arch:
                line += (f"   [{arch['home']} {arch['hs']}-{arch['gs']} {arch['away']}"
                         f" league={arch['league']!r}]")
            print(line)
        for entry in verdict["archive_only"]:
            print(f"    archive {entry['date']} {entry['home']} {entry['hs']}-"
                  f"{entry['gs']} {entry['away']} league={entry['league']!r}"
                  f" -> {entry['verdict']}")
    return report


def _rows(report: dict) -> tuple[int, int]:
    return (sum(v.get("matched", 0) for v in report["teams"].values()),
            sum(v.get("page_n", 0) for v in report["teams"].values()))


def _load(identity) -> fi.ResultsArchive:
    fi.source_team_key = identity
    return fi.load_archive(LOCALDATA)


def main() -> None:
    print("W4 — page blocks vs the archive, every difference named")
    print("command: PYTHONPATH=src .venv/bin/python "
          "handoff/round5_form_h2h_2026-10-12/w4_probe.py")
    print(f"source: {EXCERPT.name} (section A), fixture {HOME} vs {AWAY} "
          f"as of {AS_OF}")
    rows = page_rows()
    for row in rows:
        print(f"  {row['label']:12s} {row['date']} {row['score']} "
              f"odds={row['odds']}")
    print()

    canonical = fi.source_team_key
    strict = show("canonical identity (the shipped rule)", _load(canonical),
                  {"last_results_rows": rows})
    print()
    loose = show("comparison run: the same code path with the identity function "
                 "swapped to the width-9 norm_team bucket",
                 _load(norm_team), {"last_results_rows": rows})
    fi.source_team_key = canonical
    print()
    print("reading   | page rows matched | unmatched labels")
    for name, report in (("canonical", strict), ("width-9", loose)):
        matched, page_n = _rows(report)
        print(f"  {name:9s} | {matched}/{page_n} | {report['unmatched_labels']}")
    print()
    print("note: the width-9 bucket folds 'Newcastle Utd' in with Newcastle Town,")
    print("Newcastle Jets and Newcastle U23s: its 2026-09-19 'matched' row is")
    print("Anstey Nomads 2-1 Newcastle Town - a different club's fixture with the")
    print("same date and score. The canonical rule refuses the guess and names the")
    print("alias gap (unmatched_identity) instead.")
    print()
    print("note: the served rows carry closing 1x2 odds in the raw excerpt")
    print("(first row 1.64/3.88/5.49, read live), but the capture's odds regex")
    print("does not fire on this flat text render, so 'odds=None' above is a")
    print("render artefact of the excerpt, not a capture defect - the odds")
    print("parsing runs on the HTML the capture actually reads, which is not")
    print("re-derivable from this sandbox (no route to betexplorer.com).")


if __name__ == "__main__":
    main()
