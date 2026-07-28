from scripts.audit_recent_picks import audit_team_key_candidates, settle_pick


def test_kpv_j_alias_candidate_reaches_warehouse_key():
    assert "kpvkokkol" in audit_team_key_candidates("KPV-j")


def test_new_alias_mappings():
    assert "guangdong" in audit_team_key_candidates("Guangzhou E-Power")
    assert "shijiazhu" in audit_team_key_candidates("Hebei Kungfu")
    assert "poweshiji" in audit_team_key_candidates("Hebei Kungfu")
    assert "meizhouwu" in audit_team_key_candidates("Meizhou Kejia")
    assert "meizhouha" in audit_team_key_candidates("Meizhou Kejia")


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


def test_check_enhancement_hit():
    from scripts.audit_recent_picks import check_enhancement_hit
    
    # match_over_15
    assert check_enhancement_hit("match_over_15", "home", 2, 0) is True
    assert check_enhancement_hit("match_over_15", "home", 1, 0) is False
    
    # match_over_25
    assert check_enhancement_hit("match_over_25", "home", 2, 1) is True
    assert check_enhancement_hit("match_over_25", "home", 2, 0) is False

    # match_under_15
    assert check_enhancement_hit("match_under_15", "home", 1, 0) is True
    assert check_enhancement_hit("match_under_15", "home", 1, 1) is False

    # match_under_25
    assert check_enhancement_hit("match_under_25", "home", 2, 0) is True
    assert check_enhancement_hit("match_under_25", "home", 2, 1) is False

    # match_under_35
    assert check_enhancement_hit("match_under_35", "home", 3, 0) is True
    assert check_enhancement_hit("match_under_35", "home", 2, 2) is False
    
    # btts_yes
    assert check_enhancement_hit("btts_yes", "home", 1, 1) is True
    assert check_enhancement_hit("btts_yes", "home", 2, 0) is False
    
    # btts_no
    assert check_enhancement_hit("btts_no", "home", 2, 0) is True
    assert check_enhancement_hit("btts_no", "home", 1, 1) is False
    
    # team_over_05
    assert check_enhancement_hit("team_over_05", "home", 1, 0) is True
    assert check_enhancement_hit("team_over_05", "home", 0, 2) is False
    assert check_enhancement_hit("team_over_05", "away", 0, 1) is True
    assert check_enhancement_hit("team_over_05", "away", 2, 0) is False
    
    # team_over_15
    assert check_enhancement_hit("team_over_15", "home", 2, 0) is True
    assert check_enhancement_hit("team_over_15", "home", 1, 2) is False
    assert check_enhancement_hit("team_over_15", "away", 0, 2) is True
    assert check_enhancement_hit("team_over_15", "away", 1, 1) is False
    
    # double_chance
    assert check_enhancement_hit("double_chance", "home", 1, 0) is True
    assert check_enhancement_hit("double_chance", "home", 1, 1) is True
    assert check_enhancement_hit("double_chance", "home", 0, 1) is False
    
    assert check_enhancement_hit("double_chance", "away", 0, 1) is True
    assert check_enhancement_hit("double_chance", "away", 1, 1) is True
    assert check_enhancement_hit("double_chance", "away", 1, 0) is False

