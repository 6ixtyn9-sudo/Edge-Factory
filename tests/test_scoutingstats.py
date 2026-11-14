from __future__ import annotations

import json

import pytest

from edgefactory.sources import scoutingstats


def _wrapped(url: str, payload: dict) -> bytes:
    return (
        f"Title: \n\nURL Source: {url}\n\n{scoutingstats.RELAY_MARKER}"
        + json.dumps(payload)
    ).encode()


def test_relay_json_validates_provenance_and_decodes(monkeypatch):
    url = f"{scoutingstats.BASE}/fixtures/2026-09-30"

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return _wrapped(url, {"upcoming": {}})

    monkeypatch.setattr(scoutingstats.urllib.request, "urlopen", lambda *_a, **_k: Response())
    assert scoutingstats._relay_json(url) == {"upcoming": {}}


def test_relay_json_rejects_wrong_source(monkeypatch):
    url = f"{scoutingstats.BASE}/fixtures/2026-09-30"

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return _wrapped(url + "-wrong", {"upcoming": {}})

    monkeypatch.setattr(scoutingstats.urllib.request, "urlopen", lambda *_a, **_k: Response())
    with pytest.raises(ValueError, match="source URL mismatch"):
        scoutingstats._relay_json(url)


def test_actions_skips_broken_direct_tls_and_uses_relay(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    calls = []
    monkeypatch.setattr(
        scoutingstats,
        "_direct_json",
        lambda _url: (_ for _ in ()).throw(AssertionError("direct called")),
    )
    monkeypatch.setattr(
        scoutingstats,
        "_relay_json",
        lambda url: calls.append(url) or {"upcoming": {}},
    )
    assert scoutingstats._get_json(f"{scoutingstats.BASE}/fixtures/2026-09-30") == {"upcoming": {}}
    assert len(calls) == 1


def test_local_falls_back_to_relay_after_direct_failure(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(
        scoutingstats,
        "_direct_json",
        lambda _url: (_ for _ in ()).throw(OSError("TLS closed")),
    )
    monkeypatch.setattr(scoutingstats.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(scoutingstats, "_relay_json", lambda _url: {"upcoming": {}})
    assert scoutingstats._get_json(f"{scoutingstats.BASE}/fixtures/2026-09-30") == {"upcoming": {}}
