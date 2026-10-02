"""Dead-link guard for the operator docs (OP-01 T3).

Documents were restructured (archive/ subtree, REMINE-PLAN.nd -> .md). This
test walks every *relative* Markdown link in README.md and docs/** and fails
if the target does not exist, so a future move cannot silently rot the
operator handbook's links.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOCS = sorted(list((ROOT / "docs").rglob("*.md")) + [ROOT / "README.md"])

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SKIP_PREFIX = ("http://", "https://", "mailto:", "#", "<")


def _targets(path: Path):
    text = path.read_text(encoding="utf-8")
    # ignore fenced code blocks: examples there are not navigation
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    for raw in LINK.findall(text):
        if raw.startswith(SKIP_PREFIX):
            continue
        target = raw.split("#", 1)[0]
        if target:
            yield raw, target


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_markdown_links_resolve(doc):
    missing = [raw for raw, target in _targets(doc)
               if not (doc.parent / target).resolve().exists()]
    assert not missing, f"{doc.relative_to(ROOT)} has dead link(s): {missing}"


def test_operator_readme_is_the_entry_point_and_covers_its_sections():
    readme = (ROOT / "docs" / "operator" / "README.md").read_text(encoding="utf-8")
    for needed in ("Daily card ops", "FROZEN AT HH:MM - FINAL", "Abstention",
                   "Source-health legend", "Experiments archive",
                   "Source program", "OPERATOR ACTIONS"):
        assert needed in readme, f"operator README lost section marker: {needed}"


def test_moved_documents_are_present_at_their_new_paths():
    op = ROOT / "docs" / "operator"
    for rel in ("REMINE-PLAN.md", "README.md", "HISTORY-SOURCES.md",
                "CANDIDATE-SOURCES.md", "EXPERIMENT-01-LANE-CLOSEOUT.md",
                "TICKETS-OPEN.md",
                "archive/EDGE-GATE-EVIDENCE.md", "archive/SOURCE-TRIAGE.md",
                "archive/SPORTYTRADER-SHADOW-BUILD.md",
                "archive/SPORTYTRADER-7PCT-REPORT.json",
                "archive/PR15-RED-TEAM.md"):
        assert (op / rel).exists(), f"missing after consolidation: {rel}"
    assert not (op / "REMINE-PLAN.nd").exists()


def test_no_source_file_points_at_a_moved_doc_path():
    """Code references to relocated docs must have been fixed, not left stale."""
    stale = []
    for path in list((ROOT / "scripts").glob("*.py")) + \
            list((ROOT / "src").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if "REMINE-PLAN.nd" in text:
            stale.append(f"{path.name}:REMINE-PLAN.nd")
        if '"operator" / "SPORTYTRADER-7PCT-REPORT.json"' in text:
            stale.append(f"{path.name}:SPORTYTRADER-7PCT-REPORT.json")
    assert not stale, stale
