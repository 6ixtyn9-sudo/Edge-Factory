"""Authenticated transport for operator-owned, public-source fetch relays.

The relay is transport only: callers still validate provider JSON/schema.  A
POST body keeps the shared token out of URLs, proxy logs, and referrers.
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Iterator

URLS_ENV = "EDGE_FACTORY_RELAY_URLS"
TOKEN_ENV = "EDGE_FACTORY_RELAY_TOKEN"
MAX_RESPONSE_BYTES = 12 * 1024 * 1024


def configured() -> bool:
    return bool(os.environ.get(URLS_ENV, "").strip() and os.environ.get(TOKEN_ENV, "").strip())


def _urls() -> list[str]:
    return [url.strip() for url in os.environ.get(URLS_ENV, "").split(",") if url.strip()]


def fetches(source_url: str, *, timeout: int = 40) -> Iterator[tuple[str, bytes]]:
    """Yield validated relay responses in configured order.

    Individual relay failures are skipped so Cloudflare and Apps Script form
    independent egress paths.  The exact source URL must be echoed by the
    relay; an HTTP success with the wrong provenance is rejected.
    """
    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        return
    payload = json.dumps({"token": token, "url": source_url}).encode()
    for relay_url in _urls():
        try:
            request = urllib.request.Request(
                relay_url,
                data=payload,
                method="POST",
                headers={"Content-Type": "application/json", "User-Agent": "EdgeFactory/1.0"},
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ValueError("relay response exceeds size limit")
            envelope = json.loads(raw.decode("utf-8", "replace"))
            if not isinstance(envelope, dict) or envelope.get("source_url") != source_url:
                raise ValueError("relay source URL mismatch")
            if int(envelope.get("status", 0)) != 200 or not isinstance(envelope.get("body"), str):
                raise ValueError("relay upstream failure")
            yield relay_url, envelope["body"].encode()
        except Exception:
            continue
