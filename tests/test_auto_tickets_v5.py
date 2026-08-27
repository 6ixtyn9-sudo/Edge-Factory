"""Auto-tickets v5 contract tests.

Pins the three v5 changes:
  1. two-level gate — a pick rides if its (rule x source) COMBO passes OR its
     SOURCE passes pooled across all rules (forebet-style fragmentation case);
  2. ACCA10 suspension (ACCA10_ENABLED=False) — slip records acca10=[] and
     stakes_frac.acca10 == 0.0;
  3. PROBATION — stakes halved while < PROBATION_MIN_TICKETS graded tickets
     have settled, full after.

The grader contract (stakes_frac-driven) is exercised via the recorded slip.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402


# norm_team strips digits and punctuation, so team names must be distinct
# ALPHABETICALLY across all picks on the same day.
_WORDS = [a + b + c for a in "abcdefgh" for b in "abcdefg" for c in "abcdef"]


def _mk_pick(day, rule, src, odds, outcome, bucket="SKIPPED_VETO", tag=None):
    # unique teams per pick: settled-results are keyed (date, home, away)
    idx = int(tag) if tag is not None else 0
    return {
        "date": day, "home": _WORDS[2 * idx].title(), "away": _WORDS[2 * idx + 1].title(), "league": "Test League",
        "pick": "home", "bucket": bucket, "edge_rule": rule, "odds_source": src,
        "odds": odds, "avg_p": 80.0, "quarantine": "none",
        "_archive_day": day,
    }


def _settled_for(picks, outcomes):
    """Build a settled_results mapping keyed like load_settled() produces."""
    from edgefactory.util import norm_team
    out = {}
    for p, oc in zip(picks, outcomes):
        key = (str(p["date"])[:10], norm_team(p["home"]), norm_team(p["away"]))
        out[key] = oc
    return out


@pytest.fixture
def frag_case(tmp_path, monkeypatch):
    """Fragmentation case: source is +EV pooled (n=16, all wins) but split
    across two rules of n=8 each — no combo can pass, the source must."""
    monkeypatch.setattr(at, "LOCALDATA", tmp_path)
    picks, outcomes = [], []
    c = 0
    # 16 winning picks across 2 rules (8+8) at odds 1.5 -> source ROI +50%
    for i in range(8):
        for rule in ("ruleA avg_p>=55", "ruleB avg_p>=65"):
            picks.append(_mk_pick(f"2026-08-{i+1:02d}", rule, "frag_src", 1.5, "home", tag=str(c)))
            outcomes.append("home"); c += 1
    # 15 losing picks for a bad source at odds 1.5 -> ROI -100%
    for i in range(15):
        picks.append(_mk_pick(f"2026-08-{i+1:02d}", "ruleA avg_p>=55", "bad_src", 1.5, "away", tag=str(c)))
        outcomes.append("away"); c += 1
    return picks, _settled_for(picks, outcomes)


def test_source_table_passes_fragmented_source(frag_case):
    picks, settled = frag_case
    combo_t = at.build_edge_table(picks, settled, target_date="2026-08-20")
    src_t = at.build_source_table(picks, settled, target_date="2026-08-20")
    # no combo cell reaches PASS_N=15 for frag_src
    assert all(not v["pass"] for (r, s), v in combo_t.items() if s == "frag_src")
    # pooled source passes: n=16, ROI +50%, fresh
    assert src_t["frag_src"]["n"] == 16
    assert src_t["frag_src"]["pass"] is True
    # bad source fails on its own numbers
    assert src_t["bad_src"]["pass"] is False


def test_selection_admits_via_source_gate(frag_case, tmp_path, monkeypatch):
    picks, settled = frag_case
    monkeypatch.setattr(at, "load_archived_picks", lambda: picks)
    monkeypatch.setattr(at, "load_settled", lambda: settled)
    monkeypatch.setattr(at, "adaptive_ideal_pool", lambda target: 4)
    monkeypatch.setattr(at, "graded_settled_tickets", lambda: at.PROBATION_MIN_TICKETS)
    monkeypatch.setattr(at, "load_pause_state", lambda: False)
    # today's slate: one frag_src pick whose COMBO cannot pass (n=8 < 15)
    slate = [_mk_pick("2026-08-20", "ruleA avg_p>=55", "frag_src", 1.9, "home"),
             _mk_pick("2026-08-20", "ruleA avg_p>=55", "frag_src", 1.2, "home"),
             # a bad_src pick must NOT ride even on a rich day
             _mk_pick("2026-08-20", "ruleA avg_p>=55", "bad_src", 1.5, "home")]
    # distinct teams so pairing works
    slate[0]["home"], slate[0]["away"] = "Alpha", "Beta"
    slate[1]["home"], slate[1]["away"] = "Gamma", "Delta"
    slate[2]["home"], slate[2]["away"] = "Eps", "Zeta"
    (tmp_path / "picks_today.json").write_text(json.dumps(slate))
    rc = at.main_args(["--date", "2026-08-20", "--force"]) if hasattr(at, "main_args") \
        else _run_main(["--date", "2026-08-20", "--force"])
    assert rc == 0
    slip = json.loads((tmp_path / "auto_tickets_2026-08-20.json").read_text())
    legs = [l for pair in slip["acca2"] for l in pair[0]]
    srcs = {l["source"] for l in legs}
    assert srcs == {"frag_src"}, "bad_src must never ride; frag_src rides via source gate"
    assert all(l.get("via") == "source" for l in legs)
    assert "frag_src" in slip["pass_sources"]


def _run_main(argv):
    sys.argv = ["auto_tickets.py"] + argv
    return at.main()


def test_acca10_suspended(frag_case, tmp_path, monkeypatch):
    picks, settled = frag_case
    monkeypatch.setattr(at, "load_archived_picks", lambda: picks)
    monkeypatch.setattr(at, "load_settled", lambda: settled)
    monkeypatch.setattr(at, "adaptive_ideal_pool", lambda target: 4)
    monkeypatch.setattr(at, "graded_settled_tickets", lambda: at.PROBATION_MIN_TICKETS)
    monkeypatch.setattr(at, "load_pause_state", lambda: False)
    slate = [_mk_pick("2026-08-20", "ruleA avg_p>=55", "frag_src", 1.9, "home"),
             _mk_pick("2026-08-20", "ruleA avg_p>=55", "frag_src", 1.2, "home")]
    slate[0]["home"], slate[0]["away"] = "Alpha", "Beta"
    slate[1]["home"], slate[1]["away"] = "Gamma", "Delta"
    (tmp_path / "picks_today.json").write_text(json.dumps(slate))
    assert _run_main(["--date", "2026-08-20", "--force"]) == 0
    slip = json.loads((tmp_path / "auto_tickets_2026-08-20.json").read_text())
    assert at.ACCA10_ENABLED is False
    assert slip["acca10"] == []
    assert slip["stakes_frac"]["acca10"] == 0.0


def test_probation_halves_stakes(frag_case, tmp_path, monkeypatch):
    picks, settled = frag_case
    monkeypatch.setattr(at, "load_archived_picks", lambda: picks)
    monkeypatch.setattr(at, "load_settled", lambda: settled)
    monkeypatch.setattr(at, "adaptive_ideal_pool", lambda target: 2)
    monkeypatch.setattr(at, "load_pause_state", lambda: False)
    slate = [_mk_pick("2026-08-20", "ruleA avg_p>=55", "frag_src", 1.9, "home"),
             _mk_pick("2026-08-20", "ruleA avg_p>=55", "frag_src", 1.2, "home")]
    slate[0]["home"], slate[0]["away"] = "Alpha", "Beta"
    slate[1]["home"], slate[1]["away"] = "Gamma", "Delta"
    (tmp_path / "picks_today.json").write_text(json.dumps(slate))

    # < 30 settled tickets -> probation, stakes halved
    (tmp_path / "auto_tickets_performance.json").write_text(json.dumps(
        {"detail": [{"result": "WIN"}] * 3 + [{"result": "PENDING"}]}))
    assert at.graded_settled_tickets() == 3
    assert _run_main(["--date", "2026-08-20", "--force"]) == 0
    slip = json.loads((tmp_path / "auto_tickets_2026-08-20.json").read_text())
    full = (at.CAP_ACCA2 * 1.0) / at.N_ACCA2_TICKETS
    assert slip["stakes_frac"]["probation"] is True
    assert slip["stakes_frac"]["stake_scale"] == at.PROBATION_STAKE_SCALE
    assert slip["stakes_frac"]["acca2_per_ticket"] == pytest.approx(full * at.PROBATION_STAKE_SCALE)

    # >= 30 settled tickets -> full stakes
    (tmp_path / "auto_tickets_performance.json").write_text(json.dumps(
        {"detail": [{"result": "LOSS"}] * at.PROBATION_MIN_TICKETS}))
    assert _run_main(["--date", "2026-08-20", "--force"]) == 0
    slip = json.loads((tmp_path / "auto_tickets_2026-08-20.json").read_text())
    assert slip["stakes_frac"]["probation"] is False
    assert slip["stakes_frac"]["acca2_per_ticket"] == pytest.approx(full)


def test_gate_stats_shared_logic():
    rows = [("2026-08-01", "win", 1.5)] * 16
    st = at._gate_stats(rows, at.datetime.strptime("2026-08-20", "%Y-%m-%d").date())
    assert st["n"] == 16 and st["roi"] == pytest.approx(0.5)
    assert st["pass"] is True
    # stale newest settle fails freshness
    rows_stale = [("2026-05-01", "win", 1.5)] * 16
    st2 = at._gate_stats(rows_stale, at.datetime.strptime("2026-08-20", "%Y-%m-%d").date())
    assert st2["fresh"] is False and st2["pass"] is False
