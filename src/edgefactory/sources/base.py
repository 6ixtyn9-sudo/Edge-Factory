"""
base.py — SourceAdapter contract + shared politeness infrastructure.
Every scraper inherits this. Rate limiting and retries are NOT optional
and NOT reimplemented per adapter.
"""
import abc
import random
import time
from datetime import date

import httpx
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_exponential)

from ..config import settings
from ..models import NormalizedEvent

DEFAULT_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


class SourceAdapter(abc.ABC):
    """Implement fetch_day() + normalize() and the rest of the factory is yours."""

    source_key: str = ""      # must match a row in `sources` table
    sport: str = ""           # must match a row in `sports` table
    min_delay: float = 0.0    # extra per-request delay on top of global

    def __init__(self):
        self._client = httpx.Client(
            headers={"User-Agent": DEFAULT_UA},
            timeout=30,
            follow_redirects=True,
        )
        self._last_request = 0.0

    # ---------- contract ----------

    @abc.abstractmethod
    def fetch_day(self, day: date) -> dict:
        """Return raw payload(s) for one day. Will be archived to raw_payloads."""

    @abc.abstractmethod
    def normalize(self, raw: dict, day: date) -> list[NormalizedEvent]:
        """Raw payload -> normalized events. Pure function, no I/O."""

    # ---------- shared plumbing ----------

    def _throttle(self):
        wait = settings.min_delay + self.min_delay + random.random() * 0.5
        elapsed = time.time() - self._last_request
        if elapsed < wait:
            time.sleep(wait - elapsed)
        self._last_request = time.time()

    class _Retryable(Exception):
        pass

    @retry(stop=stop_after_attempt(3),
           wait=wait_exponential(multiplier=1.5, min=2, max=30),
           retry=retry_if_exception_type(_Retryable))
    def get(self, url: str, **kwargs) -> httpx.Response:
        self._throttle()
        resp = self._client.get(url, **kwargs)
        if resp.status_code in (404, 410):
            # permanently gone — surface immediately, never retry
            resp.raise_for_status()
        if resp.status_code >= 400:
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError as e:
                raise self._Retryable(str(e)) from e
        return resp

    def close(self):
        self._client.close()
