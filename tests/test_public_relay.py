from __future__ import annotations

import json

from edgefactory.sources import public_relay


def test_configured_relays_fail_over_and_validate_exact_source(monkeypatch):
    source = "https://scoutingstats.ai/api/fixtures/2026-09-30"
    monkeypatch.setenv(public_relay.URLS_ENV, "https://relay-one,https://relay-two")
    monkeypatch.setenv(public_relay.TOKEN_ENV, "secret")
    calls = []

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self, _limit):
            return json.dumps(self.payload).encode()

    def open_(request, timeout):
        calls.append((request.full_url, json.loads(request.data), timeout))
        if request.full_url.endswith("one"):
            raise OSError("down")
        return Response({"source_url": source, "status": 200, "body": '{"upcoming":{}}'})

    monkeypatch.setattr(public_relay.urllib.request, "urlopen", open_)
    rows = list(public_relay.fetches(source))
    assert rows == [("https://relay-two", b'{"upcoming":{}}')]
    assert calls[1][1] == {"token": "secret", "url": source}


def test_relay_rejects_wrong_provenance(monkeypatch):
    source = "https://scoutingstats.ai/api/fixtures/2026-09-30"
    monkeypatch.setenv(public_relay.URLS_ENV, "https://relay")
    monkeypatch.setenv(public_relay.TOKEN_ENV, "secret")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self, _limit):
            return json.dumps({"source_url": source + "-wrong", "status": 200, "body": "{}"}).encode()

    monkeypatch.setattr(public_relay.urllib.request, "urlopen", lambda *_a, **_k: Response())
    assert list(public_relay.fetches(source)) == []
