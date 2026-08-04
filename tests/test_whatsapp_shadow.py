"""Addendum 24/25: shadow slate formatter + chunker tests."""
from edgefactory.whatsapp import (
    BUCKET_VETO,
    SHADOW_MAX_LINES,
    SHADOW_ENCODED_TEXT_BUDGET,
    chunk_whatsapp_shadow_summary,
    encoded_len,
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


def _bullet_lines(text):
    return [ln for ln in text.splitlines() if ln.startswith("• ")]


# --- Addendum 24 formatter behavior (updated for Addendum 25 slim lines) -----


def test_renders_all_shadow_sections_with_stream_labels():
    picks = [_p("A vs B", BUCKET_VETO), _p("C vs D", "WATCHLIST_NO_ODDS"),
             _p("E vs F", "WATCHLIST_UNKNOWN_CTX")]
    msg = format_whatsapp_shadow_summary("2026-08-05", picks, stats=_STATS)
    assert "Shadow Slate" in msg
    assert "SKIPPED_VETO" in msg and "WATCHLIST_NO_ODDS" in msg and "WATCHLIST_UNKNOWN_CTX" in msg
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


# --- Addendum 25: slim one-line picks + enhancement token --------------------


def test_slim_pick_is_one_logical_line_with_full_context():
    msg = format_whatsapp_shadow_summary("2026-08-05", [_p("Alpha FC vs Beta United", BUCKET_VETO, avg_p=82.0)], stats=_STATS)
    bullets = _bullet_lines(msg)
    assert len(bullets) == 1
    line = bullets[0]
    assert "Alpha FC vs Beta United" in line and "82%" in line and "· KO " in line
    assert "└" not in msg  # the two-line layout is gone
    assert "| Stream:" not in msg  # section headers carry stream context now


def test_enhancement_token_rendered_only_when_present():
    enh = _p("Gamma vs Delta", BUCKET_VETO)
    enh["enhancement_label"] = "Home Win + Over 2.5"
    enh["enhancement_probability"] = 0.5021
    msg_with = format_whatsapp_shadow_summary("2026-08-05", [enh], stats=_STATS)
    # Addendum 25.1: unresolved state renders as research (🔬), never 🔥
    assert "🔬 Home Win + Over 2.5 (50%)" in msg_with
    msg_without = format_whatsapp_shadow_summary("2026-08-05", [_p("Gamma vs Delta", BUCKET_VETO)], stats=_STATS)
    assert "🔥" not in msg_without and "🔬" not in msg_without


def test_enhancement_marker_is_state_and_price_honest():
    base = _p("Gamma vs Delta", BUCKET_VETO)
    base["enhancement_label"] = "Home Win + Over 2.5"
    base["enhancement_probability"] = 0.5021
    base["recommended_enhancement"] = "match_over_25"
    certified = dict(base, _enh_status="ELIGIBLE", _enh_priced=True)
    msg = format_whatsapp_shadow_summary("2026-08-05", [certified], stats=_STATS)
    assert "🔥 Home Win + Over 2.5 (50%)" in msg
    elig_unpriced = dict(base, _enh_status="ELIGIBLE", _enh_priced=False)
    msg = format_whatsapp_shadow_summary("2026-08-05", [elig_unpriced], stats=_STATS)
    assert "🔬" in msg and "🔥" not in msg  # ELIGIBLE but unpriced NOW is research
    paper_priced = dict(base, _enh_status="PAPER", _enh_priced=True)
    msg = format_whatsapp_shadow_summary("2026-08-05", [paper_priced], stats=_STATS)
    assert "🔬" in msg and "🔥" not in msg  # priced but uncertified type is research


# --- Addendum 25: chunker invariants ------------------------------------------


def test_small_slate_single_chunk_matches_flat_formatter():
    picks = [_p("A vs B", BUCKET_VETO), _p("C vs D", "WATCHLIST_UNKNOWN_CTX")]
    chunks = chunk_whatsapp_shadow_summary("2026-08-05", picks, stats=_STATS)
    assert len(chunks) == 1
    assert chunks[0] == format_whatsapp_shadow_summary("2026-08-05", picks, stats=_STATS)
    assert "(1/1)" not in chunks[0]


def test_monster_slate_chunks_respect_budget_and_structure():
    picks = [_p(f"Long Athletic Club {i} vs Rovers United {i}", BUCKET_VETO, avg_p=90.0 - i) for i in range(8)]
    picks += [_p(f"Watch Wanderers {i} vs City Rovers {i}", "WATCHLIST_UNKNOWN_CTX", avg_p=70.0 - i) for i in range(6)]
    budget = 700
    chunks = chunk_whatsapp_shadow_summary("2026-08-05", picks, stats=_STATS, budget=budget)
    assert len(chunks) >= 2
    n = len(chunks)
    for k, c in enumerate(chunks, 1):
        assert encoded_len(c) <= budget, f"chunk {k} over budget"
        assert f"({k}/{n})" in c.splitlines()[0]
    # every shown pick appears exactly once across chunks
    bullets = [ln for c in chunks for ln in c.splitlines() if ln.startswith("• ")]
    assert len(bullets) == len(set(bullets)) == 12  # SHADOW_MAX_LINES cap
    # no chunk ends orphaned on a section header
    for c in chunks:
        tail = [ln for ln in c.splitlines() if ln.strip()][-1]
        assert "— _30d:" not in tail
    # a split section restates its header
    assert any("(cont.)" in c for c in chunks)


def test_freak_overlong_line_is_truncated_and_marked():
    freak = _p("A" * 400 + " vs " + "B" * 200, BUCKET_VETO)
    budget = 500
    chunks = chunk_whatsapp_shadow_summary("2099-01-01", [freak], stats=_STATS, budget=budget)
    assert any("(cut)" in c for c in chunks)
    for c in chunks:
        assert encoded_len(c) <= budget  # strict: battery v9 caught the loose-bound regression
    assert len(chunks) >= 1


def test_chunk_output_is_deterministic():
    picks = [_p(f"Side {i} vs Other {i}", BUCKET_VETO, avg_p=80.0 - i) for i in range(6)]
    a = chunk_whatsapp_shadow_summary("2026-08-05", picks, stats=_STATS)
    b = chunk_whatsapp_shadow_summary("2026-08-05", picks, stats=_STATS)
    assert a == b


def test_default_budget_sits_below_measured_cut_zone():
    # Addendum 25.1: production cut MEASURED at ~1,415 encoded text chars
    # (received-prefix reconstruction of the 2026-08-04 phone paste; the
    # earlier "~2k" estimate was wrong). Budget pinned at 1100 = ~0.78x cut.
    assert SHADOW_ENCODED_TEXT_BUDGET == 1100
