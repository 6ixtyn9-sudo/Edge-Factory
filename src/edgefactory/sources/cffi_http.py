"""Shared curl_cffi fetcher for Cloudflare-protected sources.

KEY INTEL (2026-06-11): predictz/windrawwin block chrome124/chrome131/edge101
impersonation (403) but ACCEPT safari17_0 and firefox133. Don't change without
re-testing.
"""
from __future__ import annotations

import time

from curl_cffi import requests as cr

IMPERSONATE = "safari17_0"
FALLBACK = "firefox133"


def get(url: str, retries: int = 3, timeout: int = 25) -> str | None:
    """GET with browser impersonation. Returns text or None for 404-ish."""
    last = None
    for attempt in range(retries):
        imp = IMPERSONATE if attempt < 2 else FALLBACK
        try:
            r = cr.get(url, impersonate=imp, timeout=timeout,
                       headers={"Accept-Language": "en-US,en;q=0.9"})
            if r.status_code in (404, 410):
                return None
            if r.status_code == 200:
                return r.text
            last = f"HTTP {r.status_code}"
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}"
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET {url} failed after {retries} tries: {last}")
