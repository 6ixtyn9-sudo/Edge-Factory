import json

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

    # home_over_25 / home_under_25
    assert check_enhancement_hit("home_over_25", "home", 3, 0) is True
    assert check_enhancement_hit("home_over_25", "home", 2, 0) is False
    assert check_enhancement_hit("home_under_25", "home", 2, 0) is True
    assert check_enhancement_hit("home_under_25", "home", 3, 0) is False

    # away_over_25 / away_under_25
    assert check_enhancement_hit("away_over_25", "away", 0, 3) is True
    assert check_enhancement_hit("away_over_25", "away", 0, 2) is False
    assert check_enhancement_hit("away_under_25", "away", 0, 2) is True
    assert check_enhancement_hit("away_under_25", "away", 0, 3) is False

    # home_over_35 / home_under_35 / home_over_45 / home_under_45
    assert check_enhancement_hit("home_over_35", "home", 4, 0) is True
    assert check_enhancement_hit("home_over_35", "home", 3, 0) is False
    assert check_enhancement_hit("home_under_35", "home", 3, 0) is True
    assert check_enhancement_hit("home_under_35", "home", 4, 0) is False
    assert check_enhancement_hit("home_over_45", "home", 5, 0) is True
    assert check_enhancement_hit("home_over_45", "home", 4, 0) is False
    assert check_enhancement_hit("home_under_45", "home", 4, 0) is True
    assert check_enhancement_hit("home_under_45", "home", 5, 0) is False

    # away_over_35 / away_under_35 / away_over_45 / away_under_45
    assert check_enhancement_hit("away_over_35", "away", 0, 4) is True
    assert check_enhancement_hit("away_over_35", "away", 0, 3) is False
    assert check_enhancement_hit("away_under_35", "away", 0, 3) is True
    assert check_enhancement_hit("away_under_35", "away", 0, 4) is False
    assert check_enhancement_hit("away_over_45", "away", 0, 5) is True
    assert check_enhancement_hit("away_over_45", "away", 0, 4) is False
    assert check_enhancement_hit("away_under_45", "away", 0, 4) is True
    assert check_enhancement_hit("away_under_45", "away", 0, 5) is False
    
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



# ---------------------------------------------------------------------------
# Full-surface audit (Addendum 12, 2026-08-03)
# ---------------------------------------------------------------------------


def test_check_enhancement_hit_plain_market_semantics():
    """FIX-2 regression: match totals and BTTS score selection-independently.

    The promised % and the captured price for these markets are the PLAIN
    market; scoring them as Win+… combos measured a different (harder) market
    and would have deflated registry certification with plain-market prices.
    """
    from scripts.audit_recent_picks import check_enhancement_hit

    # btts_yes ignores the 1X2 selection (combo branch removed)
    assert check_enhancement_hit("btts_yes", "home", 1, 1) is True
    assert check_enhancement_hit("btts_yes", "away", 1, 1) is True
    assert check_enhancement_hit("btts_yes", "draw", 2, 2) is True
    assert check_enhancement_hit("btts_yes", "home", 2, 0) is False

    # match totals ignore the selection as well
    assert check_enhancement_hit("match_over_25", "home", 2, 1) is True
    assert check_enhancement_hit("match_over_25", "away", 1, 2) is True
    assert check_enhancement_hit("match_over_25", "home", 2, 0) is False
    assert check_enhancement_hit("match_over_15", "home", 1, 1) is True
    assert check_enhancement_hit("match_over_15", "away", 1, 1) is True
    assert check_enhancement_hit("match_over_15", "home", 1, 0) is False

    # selection still matters where it must: team totals + double chance
    assert check_enhancement_hit("team_over_05", "home", 1, 0) is True
    assert check_enhancement_hit("team_over_05", "away", 1, 0) is False
    assert check_enhancement_hit("double_chance", "home", 0, 0) is True
    assert check_enhancement_hit("double_chance", "away", 0, 0) is True
    assert check_enhancement_hit("double_chance", "draw", 0, 0) is False


def test_parse_statistical_comment_avg_goals_and_fractions():
    from scripts.audit_recent_picks import parse_statistical_comment

    comment = ("📊 Realized Stats on Home Win (n=863): Avg Goals: 3.51 | Over 2.5: 68.8% | "
               "BTTS: 81.5% | Home Over 1.5 Goals: 85.7% | Away Over 1.5 Goals: 9.6% | "
               "Top Scores: 2-0 (16.9%), 1-1 (12.0%)")
    parsed = parse_statistical_comment(comment)
    assert parsed["avg_goals"] == 3.51
    # fractions are 0..1 (the FIX-1 domain the legacy 50.0 threshold violated);
    # compare rounded: 16.9/100.0 is not exactly representable as a float.
    assert round(parsed["btts"], 6) == 0.815
    assert round(parsed["over25"], 6) == 0.688
    assert round(parsed["home_o15"], 6) == 0.857
    assert round(parsed["away_o15"], 6) == 0.096
    assert [(t["score"], round(t["pct"], 6)) for t in parsed["top_scores"]] == [
        ("2-0", 0.169),
        ("1-1", 0.12),
    ]
    # missing comment -> all None / empty
    empty = parse_statistical_comment("")
    assert empty["avg_goals"] is None
    assert empty["btts"] is None
    assert empty["top_scores"] == []


def test_finite_prob_guard():
    from scripts.audit_recent_picks import _finite_prob

    assert _finite_prob(0.55) == 0.55
    assert _finite_prob(0.0) == 0.0
    assert _finite_prob(1.0) == 1.0
    assert _finite_prob("0.42") == 0.42
    assert _finite_prob(None) is None
    assert _finite_prob("junk") is None
    assert _finite_prob(float("nan")) is None
    assert _finite_prob(float("inf")) is None
    assert _finite_prob(-float("inf")) is None
    assert _finite_prob(-0.1) is None
    assert _finite_prob(1.2) is None
    assert _finite_prob(True) is None  # bool is not a probability


def test_score_event_notes_dedupe_and_guards():
    from scripts.audit_recent_picks import score_event_notes

    pick = {
        "event_notes": [
            {"market": "match_over_25", "probability": 0.55, "raw_probability": 0.6},
            {"market": "btts_yes", "probability": 0.815, "raw_probability": 0.815},
            "corrupt-note",
            {"market": "match_over_25", "probability": 0.99, "raw_probability": 0.99},  # dupe: first wins
            {"market": "corners_over_95", "probability": 0.5},  # no scoring definition
            {"market": "goal_range_2_3", "probability": float("nan")},  # promised unparseable
            {"market": ""},  # empty market skipped entirely
        ]
    }
    obs = score_event_notes(pick, "home", 1, 1)
    markets = [o["market"] for o in obs]
    assert markets == ["match_over_25", "btts_yes", "corners_over_95", "goal_range_2_3"]
    by = {o["market"]: o for o in obs}
    assert by["match_over_25"]["promised"] == 0.55  # first duplicate kept
    assert by["match_over_25"]["hit"] is False  # 1-1 -> 2 goals (plain scoring, FIX-2)
    assert by["btts_yes"]["hit"] is True  # plain BTTS even though home did not win
    assert by["corners_over_95"]["hit"] is None
    assert by["goal_range_2_3"]["hit"] is True
    assert by["goal_range_2_3"]["promised"] is None  # NaN filtered, hit still scored

    # notes absent / wrong shape -> no observations, no crash
    assert score_event_notes({}, "home", 1, 1) == []
    assert score_event_notes({"event_notes": None}, "home", 1, 1) == []
    assert score_event_notes({"event_notes": {"market": "btts_yes"}}, "home", 1, 1) == []


def test_score_statline_mapping():
    from scripts.audit_recent_picks import parse_statistical_comment, score_statline

    comment = ("📊 Realized Stats on Home Win (n=863): Avg Goals: 3.51 | Over 2.5: 68.8% | "
               "BTTS: 81.5% | Home Over 1.5 Goals: 85.7% | Away Over 1.5 Goals: 9.6% | "
               "Top Scores: 2-0 (16.9%), 1-1 (12.0%)")
    obs = score_statline(parse_statistical_comment(comment), 1, 1)
    by = {(o["metric"], round(o["promised"], 6)): o["hit"] for o in obs}
    assert by[("over25", 0.688)] is False  # 2 goals
    assert by[("btts", 0.815)] is True     # 1-1
    assert by[("home_o15", 0.857)] is False  # home scored 1
    assert by[("away_o15", 0.096)] is False  # away scored 1
    assert by[("top_score", 0.169)] is False  # 2-0 did not land
    assert by[("top_score", 0.12)] is True    # 1-1 landed
    # promised-None metrics are skipped
    assert score_statline({"over25": None, "btts": None, "top_scores": []}, 2, 1) == []
    # corrupt top-score rows are skipped without crashing
    obs2 = score_statline({"top_scores": ["junk", {"score": "2-1", "pct": "junk"},
                                           {"score": "2-1", "pct": 0.2}]}, 2, 1)
    assert obs2 == [{"metric": "top_score", "promised": 0.2, "hit": True}]


def test_aggregate_event_notes_math():
    from scripts.audit_recent_picks import aggregate_event_notes

    obs = [
        {"market": "match_over_25", "promised": 0.55, "raw_promised": 0.6, "hit": False},
        {"market": "match_over_25", "promised": 0.62, "raw_promised": 0.62, "hit": True},
        {"market": "btts_yes", "promised": 0.815, "raw_promised": 0.815, "hit": True},
        {"market": "corners_over_95", "promised": 0.5, "raw_promised": 0.5, "hit": None},
        {"market": "goal_range_2_3", "promised": None, "raw_promised": None, "hit": True},
    ]
    aud = aggregate_event_notes(obs)
    assert aud["total_notes"] == 5
    assert aud["scored"] == 4  # 3 with promised % + 1 scorable legacy row
    assert aud["promised_missing"] == 1
    assert aud["unscorable"] == {"corners_over_95": 1}
    mo = aud["by_market"]["match_over_25"]
    assert mo["n"] == 2 and mo["hits"] == 1
    assert mo["notes"] == 2
    assert mo["mean_promised"] == round((0.55 + 0.62) / 2, 6)
    assert mo["realized"] == 0.5
    assert mo["delta"] == round(0.5 - 0.585, 6)
    assert mo["brier"] == round((0.55**2 + (1 - 0.62) ** 2) / 2, 6)
    buckets = {b["bucket"]: b for b in aud["promised_buckets"]}
    assert set(buckets) == {"0.5-0.6", "0.6-0.7", "0.8-0.9"}
    assert buckets["0.8-0.9"]["n"] == 1
    assert buckets["0.8-0.9"]["realized"] == 1.0
    assert buckets["0.6-0.7"]["realized"] == 1.0
    assert buckets["0.5-0.6"]["realized"] == 0.0
    # by_engine_by_market: per-engine x per-market cells for the debias read
    assert aud["by_engine_by_market"]["legacy"]["match_over_25"]["n"] == 2
    assert aud["by_engine_by_market"]["legacy"]["btts_yes"]["n"] == 1
    assert set(aud["by_engine_by_market"]) == {"legacy"}


def test_aggregate_event_notes_engine_market_cells():
    from scripts.audit_recent_picks import aggregate_event_notes

    obs = [
        {"market": "match_over_25", "promised": 0.55, "raw_promised": 0.6, "hit": False,
         "engine": "hybrid_cohort"},
        {"market": "match_over_25", "promised": 0.62, "raw_promised": 0.62, "hit": True,
         "engine": "hybrid_cohort"},
        {"market": "match_over_25", "promised": 0.5, "raw_promised": 0.5, "hit": True},
        {"market": "btts_yes", "promised": 0.7, "raw_promised": 0.7, "hit": True,
         "engine": "model"},
        {"market": "btts_yes", "promised": 0.6, "raw_promised": 0.6, "hit": None,
         "engine": "hybrid_cohort"},
    ]
    aud = aggregate_event_notes(obs)
    ebm = aud["by_engine_by_market"]
    assert set(ebm) == {"hybrid_cohort", "legacy", "model"}
    assert ebm["hybrid_cohort"]["match_over_25"]["n"] == 2
    assert ebm["hybrid_cohort"]["match_over_25"]["realized"] == 0.5
    assert ebm["hybrid_cohort"]["match_over_25"]["mean_promised"] == round((0.55 + 0.62) / 2, 6)
    assert ebm["legacy"]["match_over_25"]["n"] == 1
    assert ebm["model"]["btts_yes"]["n"] == 1
    # unscorable rows (hit None) do not leak into cells
    assert "btts_yes" not in ebm["hybrid_cohort"]
    # pooled by_engine stays consistent with the existing surface
    assert aud["by_engine"]["hybrid_cohort"]["n"] == 2


def test_aggregate_statline_math():
    from scripts.audit_recent_picks import aggregate_statline

    obs = [
        {"metric": "over25", "promised": 0.688, "hit": False},
        {"metric": "over25", "promised": 0.40, "hit": True},
        {"metric": "btts", "promised": 0.815, "hit": True},
        {"metric": "btts", "promised": 0.22, "hit": True},
        {"metric": "top_score", "promised": 0.169, "hit": False},
        {"metric": "over25", "promised": None, "hit": True},  # skipped
    ]
    cal = aggregate_statline(obs, goal_forecasts=[(3.51, 2.0), (2.10, 3.0)])
    o25 = cal["by_metric"]["over25"]
    assert o25["n"] == 2 and o25["hits"] == 1
    assert o25["brier"] == round((0.688**2 + (1 - 0.40) ** 2) / 2, 6)
    assert cal["by_metric"]["btts"]["realized"] == 1.0
    assert cal["by_metric"]["top_score"]["n"] == 1  # legacy machine history retained
    assert sum(slot["n"] for slot in cal["promised_buckets"]) == 4  # retired score excluded
    ag = cal["avg_goals"]
    assert ag["n"] == 2
    assert ag["mae"] == round((abs(3.51 - 2) + abs(2.10 - 3)) / 2, 6)  # 1.205
    assert ag["bias"] == round(((2 - 3.51) + (3 - 2.10)) / 2, 6)      # -0.305
    assert ag["mean_promised"] == round((3.51 + 2.10) / 2, 6)
    assert ag["mean_actual"] == 2.5
    # no goal forecasts -> None, sections still render from metrics
    assert aggregate_statline(obs)["avg_goals"] is None


PICK_A = {
    "date": "2026-07-20", "home": "Alpha", "away": "Beta", "match": "Alpha vs Beta",
    "league": "Test League", "market": "1x2", "pick": "home", "odds": 2.10,
    "edge_rule": "test-rule", "bucket": "TEST", "avg_p": 62.0,
    "statistical_comment": (
        "📊 Realized Stats on Home Win (n=863): Avg Goals: 3.51 | Over 2.5: 68.8% | "
        "BTTS: 81.5% | Home Over 1.5 Goals: 85.7% | Away Over 1.5 Goals: 9.6% | "
        "Top Scores: 2-0 (16.9%), 1-1 (12.0%)"
    ),
    "event_notes": [
        {"market": "match_over_25", "probability": 0.55, "raw_probability": 0.60,
         "label": "Home Win + Over 2.5"},   # legacy combo wording — render must normalize (Addendum 16)
        {"market": "btts_yes", "probability": 0.815, "raw_probability": 0.815,
         "label": "Home Win + BTTS (Yes)",  # legacy combo wording — render must normalize (Addendum 16)
         "engine": "hybrid_cohort", "cohort_n": 220},  # Addendum 17 provenance
        {"market": "goal_range_2_3", "probability": 0.47, "raw_probability": 0.47, "label": "c",
         "engine": "hybrid_cohort", "cohort_n": 220},  # Addendum 17 provenance
        {"market": "corners_over_95", "probability": 0.5, "raw_probability": 0.5, "label": "d"},
    ],
}

PICK_B = {
    "date": "2026-07-20", "home": "Gamma", "away": "Delta", "match": "Gamma vs Delta",
    "league": "Test League", "market": "1x2", "pick": "away", "odds": 2.50,
    "edge_rule": "test-rule", "bucket": "TEST", "avg_p": 58.0,
    "statistical_comment": (
        "📊 Realized Stats on Away Win (n=120): Avg Goals: 2.10 | Over 2.5: 40.0% | "
        "BTTS: 22.0% | Home Over 1.5 Goals: 33.3% | Away Over 1.5 Goals: 44.0% | "
        "Top Scores: 0-1 (11.0%)"
    ),
    "event_notes": [
        {"market": "match_over_25", "probability": 0.62, "raw_probability": 0.62,
         "label": "Away Win + Over 2.5"},   # legacy combo wording — render must normalize (Addendum 16)
        {"market": "btts_no", "probability": 0.35, "raw_probability": 0.35, "label": "f"},
        {"market": "home_over_15", "probability": 0.71, "raw_probability": 0.71, "label": "g"},
    ],
}

# Pick C has notes but no settled result in the warehouse -> must be excluded.
PICK_C = {
    "date": "2026-07-20", "home": "Omega", "away": "Sigma", "match": "Omega vs Sigma",
    "league": "Test League", "market": "1x2", "pick": "home", "odds": 1.90,
    "edge_rule": "test-rule", "bucket": "TEST", "avg_p": 61.0,
    "statistical_comment": (
        "📊 Realized Stats on Home Win (n=5): Avg Goals: 1.00 | Over 2.5: 10.0% | "
        "BTTS: 10.0% | Home Over 1.5 Goals: 10.0% | Away Over 1.5 Goals: 10.0% | "
        "Top Scores: 0-0 (20.0%)"
    ),
    "event_notes": [{"market": "match_over_25", "probability": 0.99, "raw_probability": 0.99}],
}


# Pick D settles but carries neither event_notes nor a 📊 comment — exercises
# the explicit "none recorded" per-pick render and zero-contribution paths.
PICK_D = {
    "date": "2026-07-20", "home": "Kappa", "away": "Lambda", "match": "Kappa vs Lambda",
    "league": "Test League", "market": "1x2", "pick": "home", "odds": 1.60,
    "edge_rule": "test-rule", "bucket": "TEST", "avg_p": 59.0,
}


def _fixture_report(tmp_path, monkeypatch):
    import duckdb

    import scripts.audit_recent_picks as audit_mod

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    # Addendum 26 fixtures cover both pre-registered price interrogations.
    # These fields are pick-time evidence, independent of settlement outcome.
    pick_a = dict(
        PICK_A,
        odds_source="scoutingstats_odds",
        odds_match_method="exact",
        price_evidence="SCOUTINGSTATS_SOLE",
        price_quarantine_reason="scoutingstats_sole_source",
    )
    pick_b = dict(
        PICK_B,
        odds_source="bzzoiro_odds",
        odds_match_method="alias_fuzzy",
        price_evidence="SUSPECT_ALIAS_FUZZY",
        price_quarantine_reason="alias_fuzzy",
        suspect_price={"odds": 2.88, "source": "bzzoiro_odds", "match_method": "alias_fuzzy"},
    )
    pick_d = dict(
        PICK_D,
        odds_source="bzzoiro_odds",
        odds_match_method="exact",
        price_evidence="BZZOIRO_PRIMARY",
    )
    (localdata / "picks_2026-07-20.json").write_text(
        json.dumps([pick_a, pick_b, PICK_C, pick_d])
    )
    wh = tmp_path / "warehouse.duckdb"
    con = duckdb.connect(str(wh))
    con.execute(
        "CREATE TABLE forebet_settled (date VARCHAR, home VARCHAR, away VARCHAR, "
        "hs INTEGER, gs INTEGER, outcome VARCHAR)"
    )
    con.execute("INSERT INTO forebet_settled VALUES ('2026-07-20','Alpha','Beta',1,1,'draw')")
    con.execute("INSERT INTO forebet_settled VALUES ('2026-07-20','Gamma','Delta',2,1,'home')")
    con.execute("INSERT INTO forebet_settled VALUES ('2026-07-20','Kappa','Lambda',0,1,'away')")
    con.close()
    # Hermetic: archived picks + price probes + registry read all resolve under tmp.
    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)
    monkeypatch.setattr(audit_mod, "LOCALDATA", localdata)
    return audit_mod.build_report("2026-07-20", "2026-07-20", wh), tmp_path


def test_build_report_full_surface_integration(tmp_path, monkeypatch):
    report, tmp_path = _fixture_report(tmp_path, monkeypatch)

    # settlement baseline: A (1-1 draw, picked home), B (2-1 home, picked away),
    # D (0-1 away, picked home) settle; C unmatched
    assert report["overall"]["settled_picks"] == 3
    assert report["unmatched_result_picks"] == 1

    # FIX-1 regression: parsed fractions are 0..1 — BTTS direction honored.
    ledger = {item["match"]: item for item in report["settled_ledger"]}
    a_stats = ledger["Alpha vs Beta"]["parsed_stats"]
    assert a_stats["btts_expected"] == 0.815
    assert a_stats["btts_hit"] is True       # expected Yes (81.5%), actual 1-1 Yes
    b_stats = ledger["Gamma vs Delta"]["parsed_stats"]
    assert b_stats["btts_expected"] == 0.22
    assert b_stats["btts_hit"] is False      # expected No (22%), actual 2-1 Yes -> miss

    # Addendum 13: per-pick graded 🔥 events ride the settled ledger, sharing
    # the exact observations of the aggregate table.
    a_notes = {n["market"]: n for n in ledger["Alpha vs Beta"]["notes_audit"]}
    assert set(a_notes) == {"match_over_25", "btts_yes", "goal_range_2_3", "corners_over_95"}
    assert a_notes["match_over_25"]["hit"] is False       # 1-1 -> 2 goals (plain scoring)
    assert a_notes["btts_yes"]["hit"] is True             # 1-1 (plain BTTS, FIX-2)
    assert a_notes["goal_range_2_3"]["hit"] is True       # 2 goals
    assert a_notes["corners_over_95"]["hit"] is None      # no outcome definition
    assert a_notes["btts_yes"]["label"] == "Home Win + BTTS (Yes)"  # storage preserves archived wording
    d_stats = ledger["Kappa vs Lambda"]
    assert d_stats["notes_audit"] == []                   # nothing recorded -> explicit empty
    assert d_stats["parsed_stats"]["over25_expected"] is None  # no 📊 comment either

    # Event notes audit: only settled picks contribute (C excluded), plain scoring (FIX-2).
    aud = report["event_notes_audit"]
    assert aud["total_notes"] == 7           # 4 on A + 3 on B (C excluded)
    assert aud["scored"] == 6
    assert aud["unscorable"] == {"corners_over_95": 1}
    mo = aud["by_market"]["match_over_25"]
    assert mo["n"] == 2 and mo["hits"] == 1  # 1-1 under, 2-1 over — selection-independent
    assert aud["by_market"]["btts_yes"]["realized"] == 1.0
    assert aud["by_market"]["btts_no"]["hits"] == 0

    # Addendum 17: provenance rides the observations; the by-engine aggregation
    # grades each probability engine on its own promises.
    assert a_notes["btts_yes"]["engine"] == "hybrid_cohort"
    assert a_notes["match_over_25"]["engine"] == "legacy"   # untagged archive -> legacy
    engines = aud["by_engine"]
    assert engines["hybrid_cohort"]["n"] == 2 and engines["hybrid_cohort"]["hits"] == 2
    assert engines["hybrid_cohort"]["realized"] == 1.0
    assert engines["legacy"]["n"] == 4 and engines["legacy"]["hits"] == 2
    assert engines["legacy"]["realized"] == 0.5

    # Statistical line calibration.
    cal = report["statline_calibration"]
    assert cal["by_metric"]["over25"]["n"] == 2
    assert cal["by_metric"]["over25"]["hits"] == 1
    assert cal["by_metric"]["btts"]["realized"] == 1.0
    assert cal["by_metric"]["away_o15"]["hits"] == 0
    assert cal["by_metric"]["top_score"]["n"] == 3
    assert cal["by_metric"]["top_score"]["hits"] == 1  # 1-1 landed on pick A only
    ag = cal["avg_goals"]
    assert ag["n"] == 2
    assert ag["mae"] == 1.205
    assert ag["bias"] == -0.305

    # Addendum 26: native price evidence and quarantine tables make both
    # interrogation cohorts machine-readable without /tmp forensics.
    assert report["by_price_evidence"]["SCOUTINGSTATS_SOLE"]["settled_picks"] == 1
    assert report["by_price_evidence"]["SUSPECT_ALIAS_FUZZY"]["settled_picks"] == 1
    assert report["by_price_evidence"]["BZZOIRO_PRIMARY"]["settled_picks"] == 1
    assert report["by_price_quarantine_reason"]["scoutingstats_sole_source"]["settled_picks"] == 1
    suspect = report["by_price_quarantine_reason"]["alias_fuzzy"]
    assert suspect["settled_picks"] == 1
    assert suspect["suspect_price_captures"] == 1
    assert suspect["avg_suspect_price"] == 2.88

    # Report stays JSON-serializable for picks_audit_rolling.json consumers.
    json.dumps(report, sort_keys=True)

    # No prices under the hermetic root -> no registry file may be created.
    assert not (tmp_path / "localdata" / "enhancement_registry.json").exists()


def test_write_markdown_full_surface_sections(tmp_path, monkeypatch):
    import scripts.audit_recent_picks as audit_mod

    report, _ = _fixture_report(tmp_path, monkeypatch)
    md = tmp_path / "audit.md"
    audit_mod.write_markdown(md, report)
    text = md.read_text()

    assert "## Possible Events (🔥) Full-Surface Audit" in text
    assert "## Statistical Line (📊) Calibration" in text
    assert text.count("Calibration ≠ edge") >= 2  # doctrine guardrail on both sections
    assert "`match_over_25`" in text
    assert "0.8-0.9" in text  # pooled promised bucket row
    assert "Avg Goals forecast" in text
    assert "MAE=1.205" in text
    assert "Win + …" in text  # label-honesty disclaimer documents the legacy wording (Addendum 16)
    assert "## Price Evidence / Corroboration Audit" in text
    assert "## Suspect-price Quarantine Audit" in text
    assert "immutable morning-baseline rows" in text
    assert "verified official late-slate additions" in text
    assert "## Event Disposition / Void Audit" in text
    assert "pending/unmatched result picks" in text
    assert "SCOUTINGSTATS_SOLE" in text
    assert "SUSPECT_ALIAS_FUZZY" in text
    assert "alias_fuzzy" in text
    # Retired exact-score surface remains machine-auditable but is no longer
    # rendered in either aggregate or per-pick operator reports.
    assert "Top Scores" not in text
    assert "2-0 (16.9%)" not in text

    # Per-pick graded 🔥 render (Addendum 13/14): one event per line in the 📊
    # layout — expected % + realized context; note-less picks render
    # explicitly. Addendum 16: combo-worded archive labels render as the
    # canonical plain-market label they were promised/priced/scored as.
    assert "🔥 Possible Events (graded)" in text
    assert "    - [🟢 HIT] **Both Teams to Score - Yes (BTTS-Yes)**: expected 81.5% (Actual: BTTS-Yes)" in text
    assert "    - [🔴 MISS] **Match Over 2.5 Goals**: expected 55.0% (Actual: 2 goals)" in text
    # Kongsvinger regression pin: no "Home Win + "/"Away Win + " wording may
    # survive into the report (a 1-3 home loss must never read as a HIT on
    # "Home Win + Over 1.5").
    assert "Home Win + " not in text
    assert "Away Win + " not in text
    assert "    - [🟢 HIT] **c**: expected 47.0% (Actual: 2 goals)" in text   # non-combo: verbatim
    assert "    - [⚪ n/a] **d**: promised 50.0% (no scoring definition)" in text

    # Addendum 17: by-engine grading table renders with the provenance rows.
    assert "### By probability engine (🔥)" in text
    assert "| hybrid_cohort | 2 | 2 | 100.0% |" in text
    assert "| legacy | 4 | 2 | 50.0% |" in text
    assert "none recorded on the archived pick" in text  # pick D had no notes

    # Empty-state rendering must be explicit (never silent) and crash-proof.
    empty_report = {
        "start": "2026-07-05", "end": "2026-08-03", "overall": {},
        "event_notes_audit": {}, "statline_calibration": {},
    }
    md2 = tmp_path / "audit_empty.md"
    audit_mod.write_markdown(md2, empty_report)
    text2 = md2.read_text()
    assert "no settled picks carried machine-readable 🔥 event notes" in text2
    assert "no settled picks carried a parseable 📊 statistical comment" in text2


def test_event_actual_context():
    from scripts.audit_recent_picks import _event_actual_context

    # match totals / ranges / exacts -> total goals
    assert _event_actual_context("match_over_25", "home", 2, 1) == "3 goals"
    assert _event_actual_context("goal_range_2_3", "away", 1, 1) == "2 goals"
    assert _event_actual_context("exact_0", "home", 0, 0) == "0 goals"
    # team totals name the side and its goals
    assert _event_actual_context("home_over_15", "home", 3, 0) == "3 home goals"
    assert _event_actual_context("away_under_25", "home", 1, 2) == "2 away goals"
    assert _event_actual_context("team_over_05", "away", 0, 4) == "4 away goals"
    # btts spells the realized side
    assert _event_actual_context("btts_yes", "home", 1, 1) == "BTTS-Yes"
    assert _event_actual_context("btts_no", "away", 2, 0) == "BTTS-No"
    # double chance names the realized outcome
    assert _event_actual_context("double_chance", "home", 2, 1) == "home (2-1)"
    assert _event_actual_context("double_chance", "away", 1, 1) == "draw (1-1)"
    # unknown/garbage markets degrade to total goals, never crash
    assert _event_actual_context(None, "home", 2, 2) == "4 goals"


def test_display_label_combo_normalization():
    """Addendum 16 (label honesty): combo-worded archive labels for
    plain-scored markets render as the canonical plain label — the live
    Kongsvinger 1-3 specimen graded [🟢 HIT] on "Home Win + Over 1.5" for a
    home LOSS. Every other market keeps the archived wording verbatim, and
    storage stays faithful (normalization is display-only)."""
    from scripts.audit_recent_picks import _display_label

    # The three plain-scored combo markets normalize (home AND away wording).
    assert _display_label("match_over_15", "Home Win + Over 1.5") == "Match Over 1.5 Goals"
    assert _display_label("match_over_25", "Away Win + Over 2.5") == "Match Over 2.5 Goals"
    assert _display_label("btts_yes", "Home Win + BTTS (Yes)") == "Both Teams to Score - Yes (BTTS-Yes)"
    # Already-plain labels on those markets pass through unchanged.
    assert _display_label("match_over_15", "Match Over 1.5 Goals") == "Match Over 1.5 Goals"
    # Non-combo markets: archived wording is verbatim, however short.
    assert _display_label("goal_range_2_3", "c") == "c"
    assert _display_label("home_under_35", "Home Team Under 3.5 Goals") == "Home Team Under 3.5 Goals"
    # Missing label falls back to the market id; missing both never raises.
    assert _display_label("mystery_market", None) == "mystery_market"
    assert _display_label(None, None) == "?"


# --- Addendum 21: shared settled-results overlay -----------------------------


def _overlay_setup(tmp_path, monkeypatch):
    import duckdb

    import scripts.audit_recent_picks as audit_mod

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    wh = tmp_path / "warehouse.duckdb"
    con = duckdb.connect(str(wh))
    con.execute(
        "CREATE TABLE forebet_settled (date VARCHAR, home VARCHAR, away VARCHAR, "
        "hs INTEGER, gs INTEGER, outcome VARCHAR)"
    )
    con.execute("INSERT INTO forebet_settled VALUES ('2026-08-03','Celtic','Dundee',1,0,'home')")
    con.close()
    monkeypatch.setattr(audit_mod, "LOCALDATA", localdata)
    return audit_mod, localdata, wh


def _write_overlay(localdata, rows):
    (localdata / "settled_results.json").write_text(
        json.dumps({"schema": 1, "window_days": 90, "rows": rows})
    )


def test_overlay_fills_row_absent_from_warehouse(tmp_path, monkeypatch):
    audit_mod, localdata, wh = _overlay_setup(tmp_path, monkeypatch)
    _write_overlay(localdata, [
        {"date": "2026-07-11", "home": "South Hobart", "away": "Ulverstone",
         "hs": 2, "gs": 0, "outcome": "home", "src": "forebet_settled"}
    ])
    from edgefactory.util import norm_team

    index, by_date = audit_mod.load_results_index(wh)
    entry = index.get(("2026-07-11", norm_team("South Hobart"), norm_team("Ulverstone")))
    assert entry is not None
    assert entry["hs"] == 2 and entry["origin"] == "overlay"
    assert any(e["home"] == "South Hobart" for e in by_date["2026-07-11"])


def test_warehouse_wins_over_overlay_on_conflict(tmp_path, monkeypatch):
    audit_mod, localdata, wh = _overlay_setup(tmp_path, monkeypatch)
    _write_overlay(localdata, [
        {"date": "2026-08-03", "home": "Celtic", "away": "Dundee",
         "hs": 9, "gs": 9, "outcome": "away", "src": "zulubet_settled"}
    ])
    from edgefactory.util import norm_team

    index, by_date = audit_mod.load_results_index(wh)
    entry = index[("2026-08-03", norm_team("Celtic"), norm_team("Dundee"))]
    assert entry["hs"] == 1 and entry["origin"] == "warehouse"
    assert len([e for e in by_date["2026-08-03"] if e["home"] == "Celtic"]) == 1


def test_missing_overlay_file_is_noop(tmp_path, monkeypatch):
    audit_mod, _, wh = _overlay_setup(tmp_path, monkeypatch)
    index, by_date = audit_mod.load_results_index(wh)
    assert len(by_date["2026-08-03"]) == 1
    assert all(e["origin"] == "warehouse" for e in index.values())


def test_build_report_rescues_pick_via_overlay_fuzzy(tmp_path, monkeypatch):
    # The real 2026-08-02 case: pick source said "Clarence Zebras"; forebet
    # served the same club as "Hobart Zebras". Overlay supplies the row the
    # local warehouse never captured; fuzzy matcher (>=0.40) bridges the name.
    import duckdb

    import scripts.audit_recent_picks as audit_mod

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / "picks_2026-08-02.json").write_text(json.dumps([
        {"date": "2026-08-02", "home": "Clarence Zebras", "away": "Ulverstone",
         "match": "Clarence Zebras vs Ulverstone", "league": "NPL Tasmania",
         "market": "1x2", "pick": "home", "odds": 1.23,
         "edge_rule": "2way-unanimous avg_p>=70", "bucket": "WATCHLIST_UNKNOWN_CTX"},
    ]))
    _write_overlay(localdata, [
        {"date": "2026-08-02", "home": "Hobart Zebras", "away": "Ulverstone",
         "hs": 1, "gs": 0, "outcome": "home", "src": "forebet_settled"}
    ])
    wh = tmp_path / "warehouse.duckdb"
    con = duckdb.connect(str(wh))
    con.execute(
        "CREATE TABLE forebet_settled (date VARCHAR, home VARCHAR, away VARCHAR, "
        "hs INTEGER, gs INTEGER, outcome VARCHAR)"
    )
    con.execute("INSERT INTO forebet_settled VALUES ('2026-08-03','Celtic','Dundee',1,0,'home')")
    con.close()
    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)
    monkeypatch.setattr(audit_mod, "LOCALDATA", localdata)
    report = audit_mod.build_report("2026-08-02", "2026-08-02", wh)
    assert report["settled_via_overlay_picks"] == 1
    assert report["unmatched_result_picks"] == 0
    assert report["overall"]["wins"] == 1


def test_settle_pick_derives_legacy_price_evidence_conservatively():
    base = {
        "date": "2026-07-20",
        "edge_rule": "test-rule",
        "bucket": "WATCHLIST_UNKNOWN_CTX",
        "market": "1x2",
        "pick": "home",
        "odds": 1.90,
    }
    result = {"hs": 1, "gs": 0, "outcome": "home"}

    scouting = settle_pick(
        dict(base, odds_source="scoutingstats_odds", odds_match_method="exact"), result
    )
    assert scouting is not None
    assert scouting.price_evidence == "SCOUTINGSTATS_SOLE"
    assert scouting.price_quarantine_reason == "scoutingstats_sole_source"

    fuzzy = settle_pick(
        dict(base, odds_source="bzzoiro_odds", odds_match_method="alias_fuzzy"), result
    )
    assert fuzzy is not None
    assert fuzzy.price_evidence == "SUSPECT_ALIAS_FUZZY"
    assert fuzzy.price_quarantine_reason == "alias_fuzzy"

# --- Integrity hotfix: complete official late-slate settlement ledger --------


def _late_ledger_pick(day, home, away, *, pick="home", bucket="SKIPPED_VETO", odds=1.50):
    return {
        "date": day,
        "home": home,
        "away": away,
        "match": f"{home} vs {away}",
        "league": "Test League",
        "market": "1x2",
        "pick": pick,
        "odds": odds,
        "edge_rule": "test-rule",
        "bucket": bucket,
        "as_of": f"{day}T08:00:00+02:00",
    }


def test_audit_dedupe_collapses_accent_and_ascii_team_aliases():
    import scripts.audit_recent_picks as audit_mod

    day = "2026-08-13"
    accented = _late_ledger_pick(day, "FC Nordsjælland", "Valur Reykjavik")
    ascii_alias = _late_ledger_pick(day, "FC Nordsjaelland", "Valur Reykjavik")

    rows = audit_mod.dedupe_archived_picks([accented, ascii_alias])

    assert rows == [accented]


def test_archived_pick_loader_merges_verified_late_official_additions(tmp_path, monkeypatch):
    import scripts.audit_recent_picks as audit_mod

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    day = "2026-08-04"
    baseline = _late_ledger_pick(day, "Alpha", "Beta")
    late = _late_ledger_pick(day, "Gamma", "Delta", pick="away")
    (localdata / f"picks_morning_{day}.json").write_text(json.dumps([baseline]))
    (localdata / f"picks_{day}.json").write_text(json.dumps([baseline, late]))
    monkeypatch.setattr(audit_mod, "LOCALDATA", localdata)

    rows, receipt = audit_mod.load_archived_picks_with_receipt(day, day)

    assert [row["match"] for row in rows] == ["Alpha vs Beta", "Gamma vs Delta"]
    assert receipt["morning_baseline_rows"] == 1
    assert receipt["verified_late_additions"] == 1
    assert receipt["unsafe_regular_ledger_dates"] == []


def test_archived_pick_loader_rejects_forecast_mutated_regular_ledger(tmp_path, monkeypatch):
    import scripts.audit_recent_picks as audit_mod

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    day = "2026-08-04"
    baseline = _late_ledger_pick(day, "Alpha", "Beta")
    mutated = dict(baseline, odds=9.99)
    late = _late_ledger_pick(day, "Gamma", "Delta", pick="away")
    (localdata / f"picks_morning_{day}.json").write_text(json.dumps([baseline]))
    (localdata / f"picks_{day}.json").write_text(json.dumps([mutated, late]))
    monkeypatch.setattr(audit_mod, "LOCALDATA", localdata)

    rows, receipt = audit_mod.load_archived_picks_with_receipt(day, day)

    assert [row["match"] for row in rows] == ["Alpha vs Beta"]
    assert receipt["verified_late_additions"] == 0
    assert receipt["unsafe_regular_ledger_dates"] == [day]


def test_build_report_scores_verified_late_row(tmp_path, monkeypatch):
    from collections import defaultdict

    import scripts.audit_recent_picks as audit_mod
    from edgefactory.util import norm_team

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    day = "2026-08-04"
    baseline = _late_ledger_pick(day, "Alpha", "Beta")
    late = _late_ledger_pick(day, "Carabobo FC", "Trujillanos FC")
    (localdata / f"picks_morning_{day}.json").write_text(json.dumps([baseline]))
    (localdata / f"picks_{day}.json").write_text(json.dumps([baseline, late]))

    alpha = {"hs": 1, "gs": 0, "outcome": "home", "home": "Alpha", "away": "Beta", "origin": "warehouse"}
    carabobo = {"hs": 2, "gs": 0, "outcome": "home", "home": "Carabobo FC", "away": "Trujillanos FC", "origin": "warehouse"}
    index = {
        (day, norm_team("Alpha"), norm_team("Beta")): alpha,
        (day, norm_team("Carabobo FC"), norm_team("Trujillanos FC")): carabobo,
    }
    by_date = defaultdict(list, {day: [alpha, carabobo]})

    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)
    monkeypatch.setattr(audit_mod, "LOCALDATA", localdata)
    monkeypatch.setattr(audit_mod, "load_results_index", lambda _warehouse: (index, by_date))

    report = audit_mod.build_report(day, day, tmp_path / "unused.duckdb")

    assert report["archived_pick_rows"] == 2
    assert report["verified_late_additions"] == 1
    assert report["overall"]["settled_picks"] == 2
    assert {row["match"] for row in report["settled_ledger"]} == {
        "Alpha vs Beta", "Carabobo FC vs Trujillanos FC",
    }

# --- Event disposition / postponed fixture audit ----------------------------


def test_verified_event_disposition_schema_rejects_nonterminal_status(tmp_path, monkeypatch):
    import scripts.audit_recent_picks as audit_mod

    config = tmp_path / "Config"
    config.mkdir()
    (config / "verified_event_dispositions.json").write_text(json.dumps({
        "schema": 1,
        "rows": [
            {"date": "2026-07-19", "home": "FC Levadia Tallinn", "away": "Tammeka", "disposition": "POSTPONED"},
            {"date": "2026-07-19", "home": "Bad", "away": "Status", "disposition": "SCHEDULED"},
        ],
    }))
    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)

    rows = audit_mod.load_verified_event_dispositions()

    assert rows == [{
        "date": "2026-07-19", "home": "FC Levadia Tallinn", "away": "Tammeka",
        "disposition": "POSTPONED", "source": "verified_disposition", "verified_at": "",
    }]


def test_build_report_voids_exact_postponed_event_without_scoring(tmp_path, monkeypatch):
    from collections import defaultdict

    import scripts.audit_recent_picks as audit_mod
    from edgefactory.util import norm_team

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    day = "2026-07-19"
    pick = _late_ledger_pick(day, "FC Levadia Tallinn", "Tammeka")
    (localdata / f"picks_{day}.json").write_text(json.dumps([pick]))

    disposition = {
        "disposition": "POSTPONED", "home": "FC Levadia Tallinn", "away": "Tammeka", "origin": "verified_disposition",
    }
    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)
    monkeypatch.setattr(audit_mod, "LOCALDATA", localdata)
    monkeypatch.setattr(audit_mod, "load_results_index", lambda _warehouse: ({}, defaultdict(list)))
    monkeypatch.setattr(
        audit_mod,
        "load_event_disposition_index",
        lambda *_args, **_kwargs: {(day, norm_team("FC Levadia Tallinn"), norm_team("Tammeka")): disposition},
    )

    report = audit_mod.build_report(day, day, tmp_path / "unused.duckdb")

    assert report["voided_event_picks"] == 1
    assert report["by_event_disposition"] == {"POSTPONED": 1}
    assert report["unmatched_result_picks"] == 0
    assert report["overall"]["settled_picks"] == 0


def test_score_wins_over_same_fixture_postponement_status(tmp_path, monkeypatch):
    from collections import defaultdict

    import scripts.audit_recent_picks as audit_mod
    from edgefactory.util import norm_team

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    day = "2026-07-26"
    pick = _late_ledger_pick(day, "Super Nova", "Riga", pick="away")
    (localdata / f"picks_{day}.json").write_text(json.dumps([pick]))
    result = {"hs": 0, "gs": 2, "outcome": "away", "home": "Super Nova", "away": "Riga", "origin": "warehouse"}
    disposition = {"disposition": "POSTPONED", "home": "Super Nova", "away": "Riga", "origin": "source_status:forebet"}

    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)
    monkeypatch.setattr(audit_mod, "LOCALDATA", localdata)
    monkeypatch.setattr(
        audit_mod,
        "load_results_index",
        lambda _warehouse: ({(day, norm_team("Super Nova"), norm_team("Riga")): result}, defaultdict(list, {day: [result]})),
    )
    monkeypatch.setattr(
        audit_mod,
        "load_event_disposition_index",
        lambda *_args, **_kwargs: {(day, norm_team("Super Nova"), norm_team("Riga")): disposition},
    )

    report = audit_mod.build_report(day, day, tmp_path / "unused.duckdb")

    assert report["overall"]["settled_picks"] == 1
    assert report["voided_event_picks"] == 0
    assert report["overall"]["wins"] == 1


def test_source_status_postponement_is_detected_from_raw_warehouse(tmp_path, monkeypatch):
    import duckdb

    import scripts.audit_recent_picks as audit_mod
    from edgefactory.util import norm_team

    wh = tmp_path / "warehouse.duckdb"
    con = duckdb.connect(str(wh))
    con.execute("CREATE TABLE forebet (date VARCHAR, home VARCHAR, away VARCHAR, status VARCHAR)")
    con.execute("INSERT INTO forebet VALUES ('2026-07-26','Supernova Riga','Riga FC','Postp.')")
    con.execute("INSERT INTO forebet VALUES ('2026-07-25','Coquimbo Unido','Universidad de Concepcion','scheduled')")
    con.close()
    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)

    index = audit_mod.load_event_disposition_index(wh, start="2026-07-01", end="2026-07-31")

    postp = index[("2026-07-26", norm_team("Supernova Riga"), norm_team("Riga FC"))]
    assert postp["disposition"] == "POSTPONED"
    assert postp["origin"] == "source_status:forebet"
    assert ("2026-07-25", norm_team("Coquimbo Unido"), norm_team("Universidad de Concepcion")) not in index


def test_disposition_is_never_fuzzy_matched(tmp_path, monkeypatch):
    from collections import defaultdict

    import scripts.audit_recent_picks as audit_mod
    from edgefactory.util import norm_team

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    day = "2026-07-19"
    pick = _late_ledger_pick(day, "FC Levadia Tallinn", "Tammeka")
    (localdata / f"picks_{day}.json").write_text(json.dumps([pick]))
    wrong = {"disposition": "POSTPONED", "home": "FCI Levadia Town", "away": "Tammeka", "origin": "source_status:forebet"}

    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)
    monkeypatch.setattr(audit_mod, "LOCALDATA", localdata)
    monkeypatch.setattr(audit_mod, "load_results_index", lambda _warehouse: ({}, defaultdict(list)))
    monkeypatch.setattr(
        audit_mod,
        "load_event_disposition_index",
        lambda *_args, **_kwargs: {(day, norm_team("FCI Levadia Town"), norm_team("Tammeka")): wrong},
    )

    report = audit_mod.build_report(day, day, tmp_path / "unused.duckdb")

    assert report["voided_event_picks"] == 0
    assert report["unmatched_result_picks"] == 1


def test_fuzzy_match_pair_constrained_rejects_swapped():
    # Red-team F4: swapped home/away must NOT fuzzy-match (reversed settle)
    from scripts.audit_recent_picks import find_fuzzy_result_match
    results = [{"home": "Chelsea", "away": "Arsenal", "hs": 2, "gs": 1}]
    assert find_fuzzy_result_match("Arsenal", "Chelsea", results) is None


def test_fuzzy_match_pair_constrained_accepts_legit_pair():
    from scripts.audit_recent_picks import find_fuzzy_result_match
    results = [{"home": "Manchester United", "away": "Liverpool", "hs": 2, "gs": 1}]
    got = find_fuzzy_result_match("Man United", "Liverpool", results)
    assert got is not None and got["home"] == "Manchester United"


def test_veto_deep_dive_cuts(tmp_path, monkeypatch):
    """Addendum 27.14: the flagship veto ROI must decompose by evidence tier,
    odds band and veto reason — from the same settled rows as by_bucket."""
    import duckdb

    import scripts.audit_recent_picks as audit_mod

    localdata = tmp_path / "localdata"
    localdata.mkdir()
    # trusted evidence, small odds, recorded reason; result 1-1 draw -> home pick LOSES
    veto_hard = dict(PICK_A, bucket="SKIPPED_VETO", odds=1.42,
                     price_evidence="BZZOIRO_PRIMARY", veto_reason=["niche_league"])
    # soft evidence, mid odds, NO veto_reason field -> UNRECORDED; result 0-1 -> away pick WINS
    veto_soft = dict(PICK_D, bucket="SKIPPED_VETO", pick="away", odds=2.30,
                     price_evidence="SCOUTINGSTATS_SOLE")
    # contrast bucket row on a DISTINCT fixture (dedupe keeps one row per match)
    caution_row = dict(PICK_B, bucket="CAUTION", price_evidence="SCOUTINGSTATS_SOLE")
    (localdata / "picks_2026-07-20.json").write_text(
        json.dumps([veto_hard, veto_soft, caution_row])
    )
    wh = tmp_path / "warehouse.duckdb"
    con = duckdb.connect(str(wh))
    con.execute(
        "CREATE TABLE forebet_settled (date VARCHAR, home VARCHAR, away VARCHAR, "
        "hs INTEGER, gs INTEGER, outcome VARCHAR)"
    )
    con.execute("INSERT INTO forebet_settled VALUES ('2026-07-20','Alpha','Beta',1,1,'draw')")
    con.execute("INSERT INTO forebet_settled VALUES ('2026-07-20','Gamma','Delta',2,1,'home')")
    con.execute("INSERT INTO forebet_settled VALUES ('2026-07-20','Kappa','Lambda',0,1,'away')")
    con.close()
    monkeypatch.setattr(audit_mod, "ROOT", tmp_path)
    monkeypatch.setattr(audit_mod, "LOCALDATA", localdata)
    report = audit_mod.build_report("2026-07-20", "2026-07-20", wh)

    dd = report["veto_deep_dive"]
    assert dd["focus_bucket"] == "SKIPPED_VETO"
    assert dd["overall"]["settled_picks"] == 2
    assert dd["overall"]["wins"] == 1
    # pnl: hard lost -1.0 at 1.42-home(draw); soft won +1.30 at 2.30-away -> +0.15 blended
    assert dd["overall"]["roi"] == 0.15

    ev = dd["by_price_evidence"]
    assert set(ev) == {"BZZOIRO_PRIMARY", "SCOUTINGSTATS_SOLE"}
    assert ev["BZZOIRO_PRIMARY"]["roi"] == -1.0            # the trusted row lost
    assert ev["SCOUTINGSTATS_SOLE"]["roi"] == 1.3          # the soft row won
    assert dd["trusted_evidence_only"]["settled_picks"] == 1
    assert dd["trusted_evidence_only"]["roi"] == -1.0
    assert dd["soft_evidence_only"]["settled_picks"] == 1
    assert dd["soft_evidence_only"]["roi"] == 1.3

    bands = dd["by_odds_band"]
    assert bands["<1.50"]["settled_picks"] == 1
    assert bands["2.00-3.00"]["settled_picks"] == 1
    assert list(bands) == ["<1.50", "2.00-3.00"]           # band order, not lexical

    reasons = dd["by_veto_reason"]
    assert reasons["niche_league"]["settled_picks"] == 1
    assert reasons["UNRECORDED"]["settled_picks"] == 1     # missing field, never dropped

    contrast = dd["contrast_by_price_evidence"]
    assert contrast["SCOUTINGSTATS_SOLE"]["settled_picks"] == 1
    assert dd["contrast_bucket"] == "CAUTION"


def _ledger_row(home, away, day="2026-08-05", odds=1.50, pick="home"):
    return {
        "date": day,
        "home": home,
        "away": away,
        "market": "1x2",
        "pick": pick,
        "odds": odds,
        "bucket": "SKIPPED_VETO",
    }


def test_empty_regular_ledger_flagged_and_baseline_kept(tmp_path, monkeypatch):
    """Addendum 27.18 regression: a regular ledger that EXISTS but holds []
    must (a) still yield the morning baseline rows and (b) be enumerated in
    the receipt — an emptied ledger must never again be a silent coverage gap
    (2026-08-05: 4 of 6 slate rows vanished from the audit)."""
    import scripts.audit_recent_picks as arp

    monkeypatch.setattr(arp, "LOCALDATA", tmp_path)
    day = "2026-08-05"
    morning = [_ledger_row("Panathinaikos", "CSKA 1948"), _ledger_row("Fenerbahçe", "Sturm Graz")]
    (tmp_path / f"picks_morning_{day}.json").write_text(__import__("json").dumps(morning))
    (tmp_path / f"picks_{day}.json").write_text("[]")

    rows, receipt = arp.load_archived_picks_with_receipt(day, day)
    assert len(rows) == 2
    assert receipt["morning_baseline_rows"] == 2
    assert receipt["verified_late_additions"] == 0
    assert receipt["empty_regular_ledger_dates"] == [day]


def test_missing_regular_ledger_is_not_flagged(tmp_path, monkeypatch):
    """No regular file at all is the ordinary early-day state — not a gap."""
    import scripts.audit_recent_picks as arp

    monkeypatch.setattr(arp, "LOCALDATA", tmp_path)
    day = "2026-08-05"
    morning = [_ledger_row("Panathinaikos", "CSKA 1948")]
    (tmp_path / f"picks_morning_{day}.json").write_text(__import__("json").dumps(morning))

    rows, receipt = arp.load_archived_picks_with_receipt(day, day)
    assert len(rows) == 1
    assert receipt["empty_regular_ledger_dates"] == []


def test_nonempty_superset_ledger_not_flagged(tmp_path, monkeypatch):
    """A payload-identical superset yields verified late additions and no flag."""
    import scripts.audit_recent_picks as arp

    monkeypatch.setattr(arp, "LOCALDATA", tmp_path)
    day = "2026-08-05"
    morning = [_ledger_row("Panathinaikos", "CSKA 1948")]
    regular = morning + [_ledger_row("Napoli", "Osasuna", odds=1.72)]
    (tmp_path / f"picks_morning_{day}.json").write_text(__import__("json").dumps(morning))
    (tmp_path / f"picks_{day}.json").write_text(__import__("json").dumps(regular))

    rows, receipt = arp.load_archived_picks_with_receipt(day, day)
    assert len(rows) == 2
    assert receipt["verified_late_additions"] == 1
    assert receipt["empty_regular_ledger_dates"] == []
