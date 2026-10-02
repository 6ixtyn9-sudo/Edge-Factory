"""Stale-price containment for the scoutingstats odds board (2026-10-02).

The scoutingstats adapter fabricates captured_at = the fixture's starting_at
kickoff (no true capture stamp exists in the feed), so when the board stopped
refreshing on 2026-09-04 every downstream freshness check still passed and
weeks-old price quotes kept reaching the ledger (10-01 archive: Malta vs
Gibraltar @1.28 priced SCOUTINGSTATS_SOLE off a >=27-day-old file).

Containment: the cache file's mtime is the only honest freshness witness —
past SCOUTINGSTATS_ODDS_MAX_AGE_H the board is retired from BOTH pricing
paths (pick pricing bundle + enhancement pricing index) until the feed is
refreshed. Explicitly injected rows (audits/backtests) bypass the gate.
Self-healing: a refreshed file carries a current mtime and pricing resumes.
"""
from __future__ import annotations

import csv
import gzip
import io
import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import scripts.picks_today as pt  # noqa: E402
from edgefactory import enh_pricing  # noqa: E402

DAY = "2026-10-07"
BOARD_ROW = {
    "date": DAY, "kickoff": "2026-10-07T19:00:00Z", "league": "Test League",
    "home": "Alpha FC", "away": "Beta United", "hs": "", "gs": "",
    "odd1": "1.50", "oddx": "3.90", "odd2": "6.50",
    "odd_o15": "1.15", "odd_u15": "5.00", "odd_o25": "2.10", "odd_u25": "1.72",
    "odd_o35": "3.40", "odd_u35": "1.30", "odd_gg": "1.95", "odd_ng": "1.80",
}
COLUMNS = list(BOARD_ROW.keys())


def _write_month_csv(path: Path, rows, *, mtime: float | None = None) -> None:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    with gzip.open(path, "wt", newline="", encoding="utf-8") as fh:
        fh.write(buf.getvalue())
    if mtime is not None:
        os.utime(path, (mtime, mtime))


@pytest.fixture
def localdata(tmp_path, monkeypatch):
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    return tmp_path


def test_stale_cache_retired_from_pick_pricing(localdata, capsys):
    path = localdata / f"scoutingstats_{DAY[:7]}.csv.gz"
    old = time.time() - 40 * 24 * 3600   # 40 days old — the 2026-09-04 class
    _write_month_csv(path, [BOARD_ROW], mtime=old)

    stats: dict = {}
    bundle = pt.scoutingstats_odds_bundle(DAY, stats=stats)

    assert bundle["exact"] == {}
    assert bundle["provider"] == pt.SCOUTINGSTATS_ODDS_SOURCE  # shape intact
    assert stats["retired_stale_cache"] is True
    assert stats["cached_rows"] == 0
    assert stats["cache_age_h"] > 40 * 24 - 1
    assert "RETIRED" in capsys.readouterr().err


def test_fresh_cache_prices_normally(localdata, capsys):
    path = localdata / f"scoutingstats_{DAY[:7]}.csv.gz"
    _write_month_csv(path, [BOARD_ROW])   # mtime = now

    stats: dict = {}
    bundle = pt.scoutingstats_odds_bundle(DAY, stats=stats)

    assert bundle["exact"] != {}
    assert "retired_stale_cache" not in stats
    assert stats["cached_rows"] == 1
    assert 0 <= stats["cache_age_h"] < 1
    assert "RETIRED" not in capsys.readouterr().err


def test_injected_rows_bypass_gate_for_audits(localdata):
    """Audits/backtests construct rows explicitly and own their provenance."""
    path = localdata / f"scoutingstats_{DAY[:7]}.csv.gz"
    old = time.time() - 40 * 24 * 3600
    _write_month_csv(path, [BOARD_ROW], mtime=old)   # stale file on disk too

    bundle = pt.scoutingstats_odds_bundle(DAY, cached_rows=[dict(BOARD_ROW)])
    assert bundle["exact"] != {}


def test_missing_cache_is_silent_no_pricing(localdata):
    stats: dict = {}
    bundle = pt.scoutingstats_odds_bundle(DAY, stats=stats)
    assert bundle["exact"] == {}
    assert "retired_stale_cache" not in stats
    assert "cache_age_h" not in stats


# ---- enhancement pricing overlay ----

def _enh_root(tmp_path: Path) -> Path:
    """load_prices_index takes a repo ROOT and appends localdata/."""
    root = tmp_path / "repo"
    (root / "localdata").mkdir(parents=True)
    return root


def test_stale_cache_retired_from_enhancement_pricing(tmp_path):
    root = _enh_root(tmp_path)
    path = root / "localdata" / f"scoutingstats_{DAY[:7]}.csv.gz"
    old = time.time() - 40 * 24 * 3600
    _write_month_csv(path, [BOARD_ROW], mtime=old)

    index = enh_pricing.load_prices_index(root, DAY)
    assert index["pairs"] == {}


def test_fresh_cache_prices_enhancement(tmp_path):
    root = _enh_root(tmp_path)
    path = root / "localdata" / f"scoutingstats_{DAY[:7]}.csv.gz"
    _write_month_csv(path, [BOARD_ROW])   # mtime = now

    index = enh_pricing.load_prices_index(root, DAY)
    assert index["pairs"] != {}
    from edgefactory.util import norm_team
    key = (norm_team(BOARD_ROW["home"]), norm_team(BOARD_ROW["away"]))
    assert key in index["pairs"]
    assert ("ou_2.5", "over") in index["pairs"][key]
