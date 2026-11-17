"""Check relative links in the maintained documentation."""
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
