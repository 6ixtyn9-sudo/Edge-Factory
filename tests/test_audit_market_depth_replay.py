"""Tests for tools/audit_market_depth_replay.py."""
from pathlib import Path
from tools.audit_market_depth_replay import audit_detail_files


def test_audit_market_depth_reconciles_116_fixtures():
    rep = audit_detail_files()
    assert rep["files_count"] == 10
    assert rep["total_fixtures"] == 116
    assert rep["unique_fixture_keys"] == 116
    assert rep["market_counts"]["1x2"] == 116
    assert rep["market_counts"]["ah"] == 111
    assert rep["market_counts"]["dc"] == 113
    assert rep["market_counts"]["ou"] == 113
    assert rep["timing_audit"]["captured_before_kickoff"] == 116
    assert rep["timing_audit"]["captured_post_kickoff"] == 0
