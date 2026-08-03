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
    assert cal["by_metric"]["top_score"]["n"] == 1
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
         "label": "Home Win + BTTS (Yes)"},  # legacy combo wording — render must normalize (Addendum 16)
        {"market": "goal_range_2_3", "probability": 0.47, "raw_probability": 0.47, "label": "c"},
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
    (localdata / "picks_2026-07-20.json").write_text(
        json.dumps([PICK_A, PICK_B, PICK_C, PICK_D])
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
