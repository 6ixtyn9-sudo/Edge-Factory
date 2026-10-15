"""Band x evidence cut covers every bucket (audit veto deep dive)."""

from scripts.audit_recent_picks import (
    SettledPick,
    _bucket_band_evidence_cut,
    build_veto_deep_dive,
)


def _pick(bucket, evidence, odds, won):
    row = SettledPick(
        date="2026-09-01", rule_name="r", bucket=bucket, odds_source="x",
        odds_match_method="exact", price_evidence=evidence, price_quarantine_reason="NONE",
        market="1x2", pick="home", outcome="win" if won else "loss", won=won,
        odds=odds, pnl=(None if odds is None else ((odds - 1.0) if won else -1.0)), suspect_price=None,
    )
    return (row, {})


def test_cut_includes_every_bucket_not_only_focus_and_contrast():
    pairs = [
        _pick("SKIPPED_VETO", "SCOUTINGSTATS_SOLE", 1.7, True),
        _pick("CAUTION", "SCOUTINGSTATS_SOLE", 1.7, False),
        _pick("CERTIFIED_CLEAN", "NAMED_BOOKMAKER_PRICE", 1.8, True),
        _pick("WATCHLIST_NO_ODDS", "UNMATCHED", None, True),
    ]
    cut = _bucket_band_evidence_cut(pairs)
    assert set(k.split("|")[0] for k in cut) == {
        "SKIPPED_VETO", "CAUTION", "CERTIFIED_CLEAN", "WATCHLIST_NO_ODDS"
    }
    dd = build_veto_deep_dive(pairs)
    assert "all_buckets_band_evidence" in dd
    assert dd["all_buckets_band_evidence"].keys() == cut.keys()


def test_implied_and_z_are_computed_from_odds():
    pairs = [
        _pick("SKIPPED_VETO", "SCOUTINGSTATS_SOLE", 1.7, True),
        _pick("SKIPPED_VETO", "SCOUTINGSTATS_SOLE", 1.7, False),
    ]
    cell = _bucket_band_evidence_cut(pairs)["SKIPPED_VETO|1.50-2.00|SCOUTINGSTATS_SOLE"]
    assert cell["settled_picks"] == 2 and cell["wins"] == 1
    assert abs(cell["implied_hit_rate"] - 1 / 1.7) < 1e-6
    assert cell["z_vs_implied"] == round((1 - 2 / 1.7) / (((1 / 1.7) * (1 - 1 / 1.7)) * 2) ** 0.5, 3)
