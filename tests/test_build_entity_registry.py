from __future__ import annotations

import gzip
import json
import sys

from scripts import build_entity_registry as builder


def test_repeated_headers_cannot_become_registry_entities(tmp_path, monkeypatch, capsys):
    path = tmp_path / "forebet.csv.gz"
    with gzip.open(path, "wt") as handle:
        handle.write("date,home,away,league\n2026-06-12,Alpha,Beta,L\n"
                     "date,home,away,league\n2026-02-30,Ghost,Ghost Away,Ghost League\n")
    monkeypatch.setattr(builder, "LOCALDATA", tmp_path)
    output = tmp_path / "registry.json"
    monkeypatch.setattr(builder, "ENTITY_REGISTRY_PATH", output)
    monkeypatch.setattr(sys, "argv", ["build_entity_registry"])
    builder.main()
    registry = json.loads(output.read_text())
    assert registry["inputs"]["rows_seen"] == 1
    aliases = registry["alias_index"]
    assert "home" not in aliases["teams"] and "away" not in aliases["teams"]
    assert "league" not in aliases["leagues"]
    assert "ghost" not in aliases["teams"]
    print("P4 after: rows_seen=1; header and invalid-date entities absent")
