"""The purity registry must not be thinned by a starved rebuild.

Run 36872608772 had a cold localdata cache, so assay_purity rebuilt from
committed history alone. It wrote 433 contexts over an existing 426 --
MORE by total count -- while name-shaped league contexts collapsed from
90 to 3, orphaning every LEAGUE_ALIASES target. The existing
regression-to-zero guard passed because the total had risen.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "assay_purity", ROOT / "scripts" / "assay_purity.py")
ap = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ap)


def _registry(named, coded=400):
    league = {f"soccer|{n}|1x2|rule|home": {} for n in named}
    league.update({f"soccer|c{i:03d}|1x2|rule|home": {}
                   for i in range(coded)})
    return {"contexts": {"league": league}}


def _named(n):
    return [f"enterprise national league {i}" for i in range(n)]


def test_named_league_contexts_are_identified():
    reg = _registry(_named(3), coded=10)
    assert len(ap._named_league_contexts(reg)) == 3


def test_short_codes_are_not_counted_as_named():
    assert ap._named_league_contexts(_registry([], coded=50)) == set()


def test_a_collapse_is_refused_even_when_the_total_rises(tmp_path, monkeypatch):
    """The exact 90 -> 3 shape, with total contexts going 426 -> 433."""
    out = tmp_path / "purity_registry.json"
    out.write_text(json.dumps(_registry(_named(90), coded=336)))
    monkeypatch.setattr(ap, "OUT", out)

    starved = _registry(_named(3), coded=430)
    written = ap.write_purity_registry(starved)

    assert written is False, "a starved rebuild must not overwrite"
    kept = json.loads(out.read_text())
    assert len(ap._named_league_contexts(kept)) == 90


def test_a_healthy_rebuild_still_writes(tmp_path, monkeypatch):
    out = tmp_path / "purity_registry.json"
    out.write_text(json.dumps(_registry(_named(90), coded=336)))
    monkeypatch.setattr(ap, "OUT", out)

    assert ap.write_purity_registry(_registry(_named(92), coded=340)) is True
    assert len(ap._named_league_contexts(json.loads(out.read_text()))) == 92


def test_ordinary_churn_is_not_blocked(tmp_path, monkeypatch):
    """Leagues legitimately come and go; only a collapse is refused."""
    out = tmp_path / "purity_registry.json"
    out.write_text(json.dumps(_registry(_named(90), coded=336)))
    monkeypatch.setattr(ap, "OUT", out)

    assert ap.write_purity_registry(_registry(_named(70), coded=336)) is True


def test_a_first_run_with_no_existing_registry_writes(tmp_path, monkeypatch):
    out = tmp_path / "purity_registry.json"
    monkeypatch.setattr(ap, "OUT", out)

    assert ap.write_purity_registry(_registry(_named(5), coded=10)) is True
