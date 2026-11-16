"""A committed review may retire exact stale cache blocks, never new conflicts."""

import hashlib
import json
from copy import deepcopy

import pytest
from test_ml_paper_redteam import sign
from test_ml_paper_rolling import run
from test_phase5_persistence_audit import _git, _persistence_module, _seed_repo

from edgefactory import ml_paper as mp


@pytest.mark.parametrize("case,cleared", [
    ("reviewed", True),
    ("cache_overwrote_review", True),
    ("cache_only_approval", False),
    ("different_block", False),
    ("new_receipt_conflict", False),
    ("invalid_committed_review", False),
    ("active_committed_block", False),
])
def test_cache_restore_requires_committed_review_of_exact_block(tmp_path, capsys, case, cleared):
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed_repo(repo)
    root = repo / "localdata"
    first = run(root)
    receipt = mp.rolling_receipt_path(root, first)
    receipt_bytes = receipt.read_bytes()
    ordinary = root / "edges_consensus.json"
    ordinary_bytes = ordinary.read_bytes()
    marker = root / "autobets_ML_integrity_block.json"
    original = json.dumps({
        "lane": "autobets_ML", "paper_only": True,
        "status": "blocked_pending_evidence_review", "conflicts": [],
    }, indent=2).encode()
    sha = hashlib.sha256(original).hexdigest()
    marker.write_bytes(original)
    _git(repo, "add", "-f", str(receipt.relative_to(repo)), str(marker.relative_to(repo)))
    _git(repo, "commit", "-qm", "paper receipt and old integrity block")

    review = {
        "lane": "autobets_ML", "paper_only": True,
        "status": "resolved_copies_byte_identical", "block_sha256": sha,
    }
    approval = root / f"autobets_ML_conflicts/integrity_block.resolved_test.{sha}.json"
    approval.parent.mkdir(parents=True, exist_ok=True)
    approval.write_text(json.dumps(review))
    if case == "invalid_committed_review":
        approval.write_text("not JSON")
    if case != "cache_only_approval":
        _git(repo, "add", "-f", str(approval.relative_to(repo)))
    if case != "active_committed_block":
        marker.unlink()
        _git(repo, "add", "-u", str(marker.relative_to(repo)))
    _git(repo, "commit", "-qm", "operator resolution")

    # actions/cache overlays an obsolete block after the resolution checkout.
    marker.write_bytes(original)
    if case == "cache_overwrote_review":
        approval.write_text("stale cache, not the committed authorization")
    if case == "different_block":
        marker.write_bytes(original + b"\n")  # even changed whitespace is unapproved
    if case == "new_receipt_conflict":
        changed = deepcopy(first)
        changed["rejections"]["new_conflict"] = 1
        receipt.write_text(json.dumps(sign(changed)))

    _persistence_module().restore_committed_localdata(repo)
    assert ordinary.read_bytes() == ordinary_bytes
    assert receipt.read_bytes() == receipt_bytes  # immutable evidence never rewritten
    archive = root / f"autobets_ML_conflicts/integrity_block.reviewed_{sha}.json"
    if cleared:
        assert not marker.exists()
        assert archive.read_bytes() == original
        report = mp.publish(root, lambda c: (2, 0) if c["selection"] == "home" else (0, 2))
        assert report["decision_receipts"] == 1
        assert report["settled_accas"] == len(first["accas"])
        assert receipt.read_bytes() == receipt_bytes
        assert "evidence conflict" not in capsys.readouterr().out
        # No repeat clearing or accounting on the next restore.
        _persistence_module().restore_committed_localdata(repo)
        assert not marker.exists() and archive.read_bytes() == original
    else:
        assert marker.exists()
        assert not archive.exists()
        with pytest.raises(ValueError, match="evidence conflict"):
            mp.receipts(root)
