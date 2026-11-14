"""Veto re-mine resolution overlay tests (Phase 1/2).

Pins: Scenario B gates, n-weighted w_roi pooling, O1-before-O2, only-UNKNOWN
resolvable, monotone VETO, shadow-log-always (resolution_* fields even when
disabled), and the registry read-only guarantee.
"""
import json

from edgefactory.veto_resolution import (
    RESOLUTION_FIELDS,
    apply_resolution_to_ctx,
    build_pool_table,
    load_registry,
    o2_verdict,
    pooled_verdict,
    resolve_pick_verdict,
)


def _cell(n, roi, verdict=None):
    e = {"n": n, "roi": roi, "recent_roi": None}
    if verdict is not None:
        e["verdict"] = verdict
    return e


# ----------------------------------------------------------------------
# Scenario B gates
# ----------------------------------------------------------------------
def test_pooled_verdict_scenario_b_gates():
    # ALLOW needs n>=40
    assert pooled_verdict(39, 0.05) == "UNKNOWN"
    assert pooled_verdict(40, 0.05) == "ALLOW"
    assert pooled_verdict(40, 0.02) == "ALLOW"
    # n>=40 negative roi -> CAUTION, <=-0.05 -> VETO
    assert pooled_verdict(40, -0.02) == "CAUTION"
    assert pooled_verdict(40, -0.06) == "VETO"
    # BOOST at n>=100, roi>=0.03
    assert pooled_verdict(100, 0.04) == "BOOST"
    # CAUTION needs n>=20
    assert pooled_verdict(19, -0.06) == "UNKNOWN"
    assert pooled_verdict(20, -0.06) == "CAUTION"
    # VETO at n>=12; below the floor stays UNKNOWN
    assert pooled_verdict(12, -0.15) == "VETO"
    assert pooled_verdict(11, -0.15) == "UNKNOWN"
    # no priced evidence -> UNKNOWN regardless of n
    assert pooled_verdict(100, None) == "UNKNOWN"


# ----------------------------------------------------------------------
# Pool table: n-weighted w_roi, unpriced cells count in n only
# ----------------------------------------------------------------------
def test_build_pool_table_n_weighted_w_roi():
    contexts = {
        "league": {
            "soccer|epl|1x2|ml-meta avg_p>=70|home": _cell(100, 0.05),
            "soccer|epl|1x2|2way-unanimous avg_p>=70|home": _cell(50, -0.02),
            "soccer|epl|1x2|3way-unanimous avg_p>=65|home": _cell(30, None),  # unpriced
            "soccer|epl|1x2|ml-meta avg_p>=70|away": _cell(40, -0.10),
        }
    }
    pools = build_pool_table(contexts)
    p = pools[("soccer", "epl", "1x2", "home")]
    assert p["n"] == 180                      # unpriced cell counts in n
    assert abs(p["w_roi"] - (4.0 / 150.0)) < 1e-9   # 100*.05 + 50*(-.02) = 4 over priced n 150
    assert p["verdict"] == "ALLOW"            # n>=100, roi>=0.03? 0.0267<0.03 -> ALLOW
    assert pools[("soccer", "epl", "1x2", "away")]["verdict"] == "VETO"  # n=40 roi=-0.10
    assert p["cells"] == 3


# ----------------------------------------------------------------------
# O1 before O2; resolution semantics
# ----------------------------------------------------------------------
def test_o1_precedes_o2_and_applies():
    contexts = {
        "league": {"soccer|epl|1x2|ml-meta avg_p>=70|home": _cell(80, 0.05, "ALLOW")},
        "niche": {"soccer|epl|1x2|ml-meta avg_p>=70|1.20-1.35|home": _cell(5, 0.5, "BOOST")},
        "competition_type": {"soccer|1x2|ml-meta avg_p>=70|league": _cell(1000, -0.3, "VETO")},
    }
    pools = build_pool_table(contexts)
    ctx = {"league": "UNKNOWN", "league_key": "epl", "side_role": "home",
           "odds_band_name": "1.20-1.35", "comp_type_name": "league"}
    res = resolve_pick_verdict(contexts, ctx, pools, market="1x2", rule="ml-meta avg_p>=70")
    assert res["verdict"] == "ALLOW" and res["path"] == "O1-pool" and res["applied"] is True
    assert res["pool_n"] == 80 and abs(res["pool_w_roi"] - 0.05) < 1e-9
    assert "O1 pool" in res["reason"]


def test_o2_niche_then_competition_type():
    contexts = {
        "league": {},
        "niche": {"soccer|bol|1x2|ml-meta avg_p>=70|1.10-1.20|home": _cell(9, 0.2, "ALLOW")},
        "competition_type": {"soccer|1x2|ml-meta avg_p>=70|league": _cell(1000, -0.3, "VETO")},
    }
    ctx = {"league": "UNKNOWN", "league_key": "bol", "side_role": "home",
           "odds_band_name": "1.10-1.20", "comp_type_name": "league"}
    assert o2_verdict(contexts, ctx, "1x2", "ml-meta avg_p>=70", "soccer") == ("ALLOW", "O2-niche")
    # niche misses -> competition_type ladder
    ctx2 = dict(ctx, odds_band_name="9.99+")
    assert o2_verdict(contexts, ctx2, "1x2", "ml-meta avg_p>=70", "soccer") == ("VETO", "O2-competition_type")
    # neither resolves
    assert o2_verdict({"niche": {}, "competition_type": {}}, ctx, "1x2", "x", "soccer") == ("UNKNOWN", "unresolved")


# ----------------------------------------------------------------------
# Monotone VETO / only UNKNOWN is resolvable
# ----------------------------------------------------------------------
def test_native_verdicts_never_overridden():
    contexts = {"league": {"soccer|epl|1x2|ml-meta avg_p>=70|home": _cell(500, 0.2, "BOOST")}}
    pools = build_pool_table(contexts)
    for native in ("CAUTION", "VETO", "ALLOW", "BOOST"):
        ctx = {"league": native, "league_key": "epl", "side_role": "home"}
        res = resolve_pick_verdict(contexts, ctx, pools, market="1x2", rule="ml-meta avg_p>=70")
        assert res["verdict"] == native and res["path"] == "native" and res["applied"] is False


# ----------------------------------------------------------------------
# apply_resolution_to_ctx: shadow-log always; application gated
# ----------------------------------------------------------------------
def test_apply_shadow_logs_when_disabled():
    contexts = {"league": {"soccer|epl|1x2|ml-meta avg_p>=70|home": _cell(80, 0.05, "ALLOW")}}
    pools = build_pool_table(contexts)
    ctx = {"league": "UNKNOWN", "league_key": "epl", "side_role": "home"}
    out = apply_resolution_to_ctx(ctx, contexts, pools, enable=False,
                                  market="1x2", rule="ml-meta avg_p>=70")
    assert out["league"] == "UNKNOWN"            # not applied
    assert out["resolution_original_verdict"] == "UNKNOWN"
    assert out["resolution_verdict"] == "ALLOW"
    assert out["resolution_path"] == "O1-pool"
    assert out["resolution_pool_n"] == 80
    assert out["resolution_pool_roi"] == 0.05
    assert "O1 pool" in out["resolution_reason"]
    assert all(f in out for f in RESOLUTION_FIELDS)
    # original dict untouched (pure)
    assert ctx["league"] == "UNKNOWN" and "resolution_verdict" not in ctx


def test_apply_resolves_when_enabled():
    cases = [
        ({"soccer|epl|1x2|ml-meta avg_p>=70|home": _cell(80, 0.05)}, "ALLOW"),
        ({"soccer|epl|1x2|ml-meta avg_p>=70|home": _cell(60, -0.03)}, "CAUTION"),
        ({"soccer|epl|1x2|ml-meta avg_p>=70|home": _cell(40, -0.10)}, "VETO"),
        ({"soccer|epl|1x2|ml-meta avg_p>=70|home": _cell(100, 0.04)}, "BOOST"),
    ]
    for league_cells, expected in cases:
        contexts = {"league": league_cells}
        pools = build_pool_table(contexts)
        ctx = {"league": "UNKNOWN", "league_key": "epl", "side_role": "home"}
        out = apply_resolution_to_ctx(ctx, contexts, pools, enable=True,
                                      market="1x2", rule="ml-meta avg_p>=70")
        assert out["league"] == expected, (expected, out)


def test_apply_never_raises_on_garbage():
    out = apply_resolution_to_ctx(None, None, None, True)
    assert out == {}
    out = apply_resolution_to_ctx({"league": "UNKNOWN"}, {}, {}, False)
    assert out["league"] == "UNKNOWN" and out["resolution_verdict"] == "UNKNOWN"
    out = apply_resolution_to_ctx({"league": "UNKNOWN"}, {"league": {}}, None, True,
                                  market="1x2", rule="")
    assert out["league"] == "UNKNOWN" and out["resolution_path"] == "unresolved"


# ----------------------------------------------------------------------
# Registry read-only
# ----------------------------------------------------------------------
def test_load_registry_reads_and_never_writes(tmp_path):
    (tmp_path / "localdata").mkdir()
    reg = {"contexts": {"league": {"soccer|epl|1x2|ml-meta avg_p>=70|home": _cell(10, 0.1, "ALLOW")}}}
    p = tmp_path / "localdata" / "purity_registry.json"
    p.write_text(json.dumps(reg))
    before = p.read_bytes()
    ctx_reg = load_registry(tmp_path)
    assert ctx_reg["league"]["soccer|epl|1x2|ml-meta avg_p>=70|home"]["verdict"] == "ALLOW"
    assert p.read_bytes() == before
    # missing file -> {}
    assert load_registry(tmp_path / "nope") == {}
    # corrupt file -> {}
    bad = tmp_path / "localdata" / "purity_registry.json"
    bad.write_text("{ not json")
    assert load_registry(tmp_path) == {}
