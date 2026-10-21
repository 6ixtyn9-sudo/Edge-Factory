"""Round 6D — the measurement ledger and the certification ledger (2026-10-12).

The operator's question was why the registry showed ~409 enhancement measurements
while the daily performance view showed thousands. Answer: two ledgers. The
performance view counts every recommendation; the registry counts priced settled
outcomes only (its caller literally iterated ``priced_outcomes``). Round 6D feeds
the registry the unpriced settled outcomes too, through the processed-only path
they were always supposed to take, and pins the two invariants that makes safe:

* an unpriced outcome never moves certification (any of it, including status);
* ``processed`` can always dedupe a whole rescan window (trim-safety).
"""
import json
from pathlib import Path

from edgefactory.enh_registry import (MAX_PROCESSED_KEYS, _read, _write_atomic,
                                      processed_window_is_safe, record_outcome,
                                      registry_path, versioned)

REPO = Path(__file__).resolve().parents[1]
CERT_FIELDS = ("n", "hits", "records", "profit", "inv_price_sum", "multi_n",
               "status", "status_since", "status_reason")


def _cert(entry: dict) -> dict:
    return {k: entry.get(k) for k in CERT_FIELDS}


def test_an_unpriced_outcome_is_processed_and_never_moves_certification(tmp_path):
    # First touch of a market key: the registry's own lifecycle assigns the
    # opening status (SHADOW). That is _evaluate's rule, not the outcome's, so
    # the invariant is measured from there: from now on, nothing an unpriced
    # outcome does may move a counter, a record, or a status.
    record_outcome(tmp_path, date_="2026-10-12", match="A vs B",
                   market="match_over_25", price=None, hit=True, today="2026-10-12")
    reg = json.loads(registry_path(tmp_path).read_text())
    entry = reg["markets"][versioned("match_over_25")]
    assert entry["processed"] == ["2026-10-12|A vs B|match_over_25@v1"]
    opened = _cert(entry)
    assert (entry["n"], entry["hits"], entry["records"],
            entry["profit"], entry["inv_price_sum"], entry["multi_n"]) == (0, 0, [], 0.0, 0.0, 0)

    for i in range(24):
        record_outcome(tmp_path, date_="2026-10-12", match=f"U{i} vs V{i}",
                       market="match_over_25", price=None, hit=bool(i % 2),
                       today="2026-10-12")
    entry = json.loads(registry_path(tmp_path).read_text())["markets"][versioned("match_over_25")]
    # 25 unpriced outcomes later: every certification field AND the status are
    # exactly what they were after the first one
    assert _cert(entry) == opened
    assert len(entry["processed"]) == 25

    # idempotent: the same outcome twice is one key, not two
    again = record_outcome(tmp_path, date_="2026-10-12", match="A vs B",
                           market="match_over_25", price=None, hit=True, today="2026-10-12")
    assert again["recorded"] is False
    entry = json.loads(registry_path(tmp_path).read_text())["markets"][versioned("match_over_25")]
    assert len(entry["processed"]) == 25 and _cert(entry) == opened

    # and a PRICED outcome for a key that was already processed unpriced still
    # cannot double-record — the dedup that keeps certification honest
    record_outcome(tmp_path, date_="2026-10-12", match="A vs B",
                   market="match_over_25", price=1.9, hit=True, today="2026-10-12")
    entry = json.loads(registry_path(tmp_path).read_text())["markets"][versioned("match_over_25")]
    assert len(entry["processed"]) == 25 and entry["n"] == 0 and entry["records"] == []


def test_many_unpriced_outcomes_leave_certification_byte_identical(tmp_path):
    """The 6D acceptance shape: feed N unpriced outcomes; certification fields
    must be identical to what they were before the feed."""
    record_outcome(tmp_path, date_="2026-10-01", match="C vs D",
                   market="btts_yes", price=2.0, hit=True, today="2026-10-12")
    before = _cert(json.loads(registry_path(tmp_path).read_text())["markets"][versioned("btts_yes")])
    for i in range(25):
        record_outcome(tmp_path, date_="2026-10-02", match=f"U{i} vs V{i}",
                       market="btts_yes", price=None, hit=bool(i % 2),
                       today="2026-10-12")
    entry = json.loads(registry_path(tmp_path).read_text())["markets"][versioned("btts_yes")]
    assert _cert(entry) == before
    assert len(entry["processed"]) == 26  # 1 priced + 25 unpriced


def test_a_trimmed_window_cannot_hide_a_key_the_archives_will_present():
    """Trim-safety over the committed archives, measured — not assumed.

    ``processed`` is retained in full since 2026-10-21 (no trimming), so this
    bound is currently vacuous — it is kept as the guard trimming would need.
    Historically it kept the newest MAX_PROCESSED_KEYS keys. A key still inside
    an audit rescan window must never have been trimmed, or a priced outcome
    would be recorded twice. So: per market, the keys any window the audits
    actually use can present must be fewer than the cap. The whole-archive
    window is checked too — it is the widest rescan anyone has run (the registry
    was built from it). When this test fails, 6D's guardrail applies: unpriced
    keys move to their own capped list; do not raise the cap.
    """
    by_market: dict[str, set[str]] = {}
    for path in sorted((REPO / "localdata").glob("picks_2026-*.json")):
        try:
            raw = json.loads(path.read_text())
        except Exception:
            continue
        day = path.stem.split("_")[-1]
        picks = raw if isinstance(raw, list) else raw.get("picks") or []
        for p in picks:
            market = p.get("recommended_enhancement")
            if not market:
                continue
            match = p.get("match") or f"{p.get('home')} vs {p.get('away')}"
            by_market.setdefault(market, set()).add(f"{day}|{match}|{market}")

    assert by_market, "the picks archive is empty; trim-safety would be vacuous"
    days = sorted({k.split("|")[0] for keys in by_market.values() for k in keys})
    worst: dict[str, int] = {}
    for market, keys in by_market.items():
        dated = {}
        for k in keys:
            dated.setdefault(k.split("|")[0], 0)
            dated[k.split("|")[0]] += 1
        best = 0
        for i, day in enumerate(days):
            window = days[max(0, i - 29): i + 1]          # the default 30-day rescan
            n = sum(dated.get(d, 0) for d in window)
            best = max(best, n)
        worst[market] = best
        assert processed_window_is_safe(best), (
            f"{market}: {best} keys in a 30-day window >= cap {MAX_PROCESSED_KEYS} — "
            f"move unpriced keys to their own capped list (round 6D guardrail)")
        # the widest rescan anyone has run: the whole archive
        assert processed_window_is_safe(len(keys)), (
            f"{market}: {len(keys)} keys in the whole-archive window >= cap "
            f"{MAX_PROCESSED_KEYS}")
    assert max(worst.values()) < MAX_PROCESSED_KEYS
