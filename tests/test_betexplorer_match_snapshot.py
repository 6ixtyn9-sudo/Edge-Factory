from datetime import datetime, timezone
import json

import pytest

from edgefactory.sources import betexplorer_match_snapshot as source
import scripts.capture_betexplorer_match as capture


def test_url_guard_and_identity():
    good = 'https://www.betexplorer.com/football/usa/nwsl-women/boston-legacy-angel-city/nT46QDpf/'
    assert source.validated_url(good) == good
    for bad in [good + '?page=2', 'https://evil.example/football/usa/nwsl-women/a/b/',
                'https://www.betexplorer.com/bookmaker/123/']:
        with pytest.raises(ValueError):
            source.validated_url(bad)
    card = dict(date='2026-10-10', league='NWSL Women', home='Boston Legacy', away='Angel City')
    assert source.identity_match(card, dict(card))
    assert not source.identity_match(card, {**card, 'away': 'Other'})


def test_capture_only_once_even_after_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, 'LOCALDATA', tmp_path)
    day = '2026-10-10'
    url = 'https://www.betexplorer.com/football/usa/nwsl-women/boston-legacy-angel-city/nT46QDpf/'
    (tmp_path / 'picks_today.json').write_text(json.dumps([
        dict(date=day, league='NWSL Women', home='Boston Legacy', away='Angel City', match_url=url),
        dict(date=day, league='NWSL Women', home='Boston Legacy', away='Angel City', match_url=url),
    ]))
    calls = []
    def fail(url):
        calls.append(url)
        raise RuntimeError('offline failure')
    monkeypatch.setattr(source, 'fetch_page', fail)
    clock = lambda: datetime(2026, 10, 9, 23, tzinfo=timezone.utc)  # 01:00 Johannesburg
    assert capture.capture(day, clock=clock) == capture.capture(day, clock=clock)
    assert len(calls) == 1
    assert len(json.loads((tmp_path / f'betexplorer_match_shadow_{day}.json').read_text())) == 1


def test_day_and_offpeak_guard(tmp_path, monkeypatch):
    monkeypatch.setattr(capture, 'LOCALDATA', tmp_path)
    with pytest.raises(ValueError, match='off-peak'):
        capture.capture('2026-10-10', clock=lambda: datetime(2026, 10, 10, 12, tzinfo=timezone.utc))
    with pytest.raises(ValueError, match='today'):
        capture.capture('2026-10-09', clock=lambda: datetime(2026, 10, 9, 23, tzinfo=timezone.utc))
