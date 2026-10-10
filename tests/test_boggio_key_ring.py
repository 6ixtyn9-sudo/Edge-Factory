"""No live calls; fake responses exercise key attribution and budget."""
import io
import urllib.error

import pytest
from edgefactory.sources import boggio


class Response:
    status = 200
    headers = {'X-RateLimit-Match-Stats-and-Prediction-endpoints-Remaining': '99'}
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, n): return b'{"data":[]}'


def test_ordered_ring_and_singular_fallback(monkeypatch):
    monkeypatch.setenv('RAPIDAPI_KEY', 'old')
    monkeypatch.delenv('RAPIDAPI_KEYS', raising=False)
    assert boggio.configured_keys() == ('old',)
    monkeypatch.setenv('RAPIDAPI_KEYS', ' one, two,one, ')
    assert boggio.configured_keys() == ('one', 'two')


def test_rejected_key_falls_over_once_without_leaking(monkeypatch):
    monkeypatch.setenv('RAPIDAPI_KEYS', 'secret-a,secret-b')
    monkeypatch.setattr(boggio, 'MIN_INTERVAL_S', 0)
    boggio.reset_state()
    boggio._DIAG.clear()
    seen = []
    def fake(req, timeout):
        key = req.get_header('X-rapidapi-key')
        seen.append(key)
        if key == 'secret-a':
            raise urllib.error.HTTPError(req.full_url, 429, 'quota', {}, io.BytesIO(b''))
        return Response()
    monkeypatch.setattr(boggio.urllib.request, 'urlopen', fake)
    code, data, headers = boggio.get_json(boggio.predictions_url('2026-10-10'))
    assert (code, data, len(seen)) == (200, {'data': []}, 2)
    assert [x['key_index'] for x in boggio.diagnostics()['key_attempts']] == [1, 2]
    assert 'secret-' not in repr(boggio.diagnostics())
    with pytest.raises(boggio.UpstreamBlocked, match='logical call budget'):
        boggio.get_json(boggio.predictions_url('2026-10-10'))
    assert len(seen) == 2
