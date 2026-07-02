from scripts.audit_recent_picks import audit_team_key_candidates, settle_pick


def test_kpv_j_alias_candidate_reaches_warehouse_key():
    assert "kpvkokkol" in audit_team_key_candidates("KPV-j")


def test_settle_pick_counts_home_loss():
    pick = {
        "date": "2026-07-02",
        "edge_rule": "2way-unanimous avg_p>=65",
        "bucket": "SKIPPED_VETO",
        "market": "1x2",
        "pick": "home",
        "odds": 1.46,
    }
    result = {"hs": 0, "gs": 1, "outcome": "away"}
    settled = settle_pick(pick, result)
    assert settled is not None
    assert settled.won is False
    assert settled.pnl == -1.0
