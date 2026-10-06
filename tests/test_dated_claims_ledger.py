"""Cited receipts must resolve, or be labelled as recollection.

A comment that cites a dated observation - "panel receipt 2026-10-02",
"verified 2026-08-05", "observed on 2026-10-03" - is a claim about the
outside world. One such comment in the Pinnacle relay adapter named a
receipt that never existed, and because it read like evidence the adapter
asked for the wrong sport for four days.

This pins the cheap, mechanical half of the problem: every dated claim in
a comment has a row in docs/operator/DATED-CLAIMS.md, and a row whose
backing names a file must name a file that is on disk. It cannot judge
whether a claim is true; it only forces the diff to say what backs it.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "docs" / "operator" / "DATED-CLAIMS.md"
SCANNED = ("src", "scripts", "tests")

DATE = r"20\d{2}-\d{2}-\d{2}"
WORD = r"receipt|verified|confirmed|observed"
# A dated claim: a comment carrying both an evidence word and a date.
CLAIM = re.compile(rf"#.*(?:(?:{WORD}).*{DATE}|{DATE}.*(?:{WORD}))", re.I)

LABELS = {"OPERATOR-RELAYED", "RUNTIME-OBSERVED"}


def _claim_sites() -> set[str]:
    """Files whose comments cite a dated observation."""
    found: set[str] = set()
    for folder in SCANNED:
        for path in sorted((ROOT / folder).rglob("*.py")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if CLAIM.search(line):
                    found.add(str(path.relative_to(ROOT)))
                    break
    return found


def _rows() -> list[tuple[str, str, str]]:
    rows = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `") and not line.startswith("| src"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3:
            rows.append(tuple(c.strip("`") for c in cells))  # type: ignore[arg-type]
    return rows


def test_the_ledger_parses_and_is_not_empty():
    assert _rows(), "the ledger table could not be read; check its formatting"


def test_every_dated_claim_in_code_has_a_ledger_row():
    listed = {row[0] for row in _rows()}
    missing = sorted(_claim_sites() - listed)
    assert not missing, (
        f"{missing} cite a dated observation with no row in {LEDGER.name}. "
        "Add one saying what backs it - an artifact path, OPERATOR-RELAYED, "
        "or RUNTIME-OBSERVED. A claim that reads like evidence and is not "
        "evidence is the failure this guards against.")


def test_no_stale_ledger_rows():
    sites = _claim_sites()
    stale = sorted({row[0] for row in _rows()} - sites)
    assert not stale, (
        f"{stale} have ledger rows but no dated claim in their comments. "
        "Remove the row, so the ledger stays a description of the code.")


@pytest.mark.parametrize("row", _rows(), ids=lambda r: f"{r[0]}::{r[2][:40]}")
def test_a_backing_that_names_a_file_resolves(row):
    _file, _claim, backing = row
    if backing in LABELS:
        return  # explicitly labelled as unbacked; that is a valid answer
    assert "/" in backing and not backing.endswith("."), (
        f"backing {backing!r} is neither a path nor one of {sorted(LABELS)}")
    assert (ROOT / backing).exists(), (
        f"the ledger cites {backing} but it is not on disk. A cited receipt "
        "that does not resolve is exactly the defect this file exists for.")


def test_the_ledger_states_its_own_blind_spot():
    """It cannot catch a confident claim about our own behaviour."""
    text = LEDGER.read_text(encoding="utf-8")
    assert "does not catch" in text
    assert "our own" in text
