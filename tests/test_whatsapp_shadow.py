"""Addendum 24: shadow slate formatter tests."""
from edgefactory.whatsapp import (
    BUCKET_VETO,
    SHADOW_MAX_LINES,
    format_stream_record,
    format_whatsapp_shadow_summary,
)

_STATS = {
    "SKIPPED_VETO": {"hit_rate": 0.865, "roi": 0.118, "settled_picks": 52, "wins": 45, "priced_picks": 49},
    "WATCHLIST_NO_ODDS": {"hit_rate": 0.667, "roi": None, "settled_picks": 3, "wins": 2, "priced_picks": 0},
}


def _p(match, bucket, avg_p=70.0, odds=1.9):
    return {"date": "2026-08-05", "match": match, "pick": "home", "bucket": bucket,
            "avg_p": avg_p, "odds": odds, "display_rule": "2way-unanimous avg_p>=70"}


def test_renders_all_shadow_sections_with_stream_labels():
    picks = [_p("A vs B", BUCKET_VETO), _p("C vs D", "WATCHLIST_NO_ODDS"),
             _p("E vs F", "WATCHLIST_UNKNOWN_CTX")]
    msg = format_whatsapp_shadow_summary("2026-08-05", picks, stats=_STATS)
    assert "Shadow Slate" in msg
    assert "SKIPPED_VETO" in msg and "WATCHLIST_NO_ODDS" in msg and "WATCHLIST_UNKNOWN_CTX" in msg
    assert "| Stream: SKIPPED_VETO" in msg
    assert "30d: 86% hit · +11.8% ROI (52 settled)" in msg
    assert "30d: 67% hit · ROI n/a (3 settled)" in msg  # roi None renders honestly


def test_excludes_main_slate_buckets_and_counts_overflow_correctly():
    picks = [_p("A vs B", BUCKET_VETO), _p("MAIN vs X", "CAUTION"), _p("CLEAN vs Y", "CERTIFIED_CLEAN")]
    msg = format_whatsapp_shadow_summary("2026-08-05", picks, stats=_STATS)
    assert "MAIN vs X" not in msg and "CLEAN vs Y" not in msg
    assert "more on the slate file" not in msg  # CAUTION/CLEAN must not count as overflow


def test_no_stats_degrades_gracefully():
    msg = format_whatsapp_shadow_summary("2026-08-05", [_p("A vs B", BUCKET_VETO)], stats=None)
    assert "30d: no settled record yet" in msg


def test_overflow_cap_marks_hidden_count():
    picks = [_p(f"Team{i} vs Team{i+1}", BUCKET_VETO) for i in range(SHADOW_MAX_LINES + 4)]
    msg = format_whatsapp_shadow_summary("2026-08-05", picks, stats=_STATS)
    assert "+4 more on the slate file" in msg


def test_empty_shadow_slate():
    msg = format_whatsapp_shadow_summary("2026-08-05", [], stats=_STATS)
    assert "Shadow slate empty" in msg


def test_stream_record_without_settled_history():
    assert format_stream_record("SKIPPED_VETO", {}) == "30d: no settled record yet"
    assert format_stream_record("SKIPPED_VETO", None) == "30d: no settled record yet"
