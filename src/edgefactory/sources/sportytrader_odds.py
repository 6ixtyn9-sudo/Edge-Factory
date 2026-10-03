"""SportyTrader shadow odds adapter.

The adapter is deliberately separate from the pick path. It captures named
bookmaker rows into a shadow board; ``SPORTYTRADER_CORROBORATOR=on`` is the
only path that lets those rows reach the existing price-corroboration stamp.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from edgefactory.odds_normalization import canonical_market_selection

SOURCE = "sportytrader_odds"
BASE = "https://www.sportytrader.es"
UA = "EdgeFactory-cooperative-shadow/1.0 (+operator review)"
MIN_INTERVAL_S = float(os.environ.get("EDGE_FACTORY_ST_MIN_INTERVAL_S", "2.0"))
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA", Path(__file__).resolve().parents[3] / "localdata"))
DISALLOWED_PREFIXES = (
    "/en-gb/", "/en-za/", "/en-ng/", "/en-in/", "/fr-be/", "/fr-ca/",
    "/es-co/", "/es-pe/", "/cdn-cgi/",
)
ALLOWED_LOCALES = {"es", "fr", "de", "it", "pt-br"}

_LOCK = threading.Lock()
_LAST_REQUEST = 0.0
_ROBOTS: dict[str, str] = {}
_COOLING = False
_429S = 0
_TRAINING_ONLY = False


class RateLimited(RuntimeError):
    pass


class ChallengeWalled(RuntimeError):
    pass


def reset_state() -> None:
    global _LAST_REQUEST, _COOLING, _429S, _TRAINING_ONLY
    _LAST_REQUEST = 0.0
    _COOLING = False
    _429S = 0
    _TRAINING_ONLY = False


def _host(url: str) -> str:
    return urllib.parse.urlsplit(url).netloc.lower()


def locale_for_url(url: str) -> str | None:
    parsed = urllib.parse.urlsplit(url)
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path or "/"
    if any(path.lower().startswith(prefix) for prefix in DISALLOWED_PREFIXES):
        return None
    host_locales = {
        "sportytrader.es": "es", "sportytrader.fr": "fr",
        "sportytrader.de": "de", "sportytrader.it": "it",
    }
    for domain, locale in host_locales.items():
        if host == domain or host.endswith("." + domain):
            return locale
    parts = [p for p in path.split("/") if p]
    if parts and parts[0].lower() in ALLOWED_LOCALES:
        return parts[0].lower()
    return None


def allowed_url(url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"https"}:
        return False
    host = parsed.netloc.lower().removeprefix("www.")
    supported_domains = (
        "sportytrader.es", "sportytrader.fr", "sportytrader.de",
        "sportytrader.it", "sportytrader.com",
    )
    if not any(host == domain or host.endswith("." + domain) for domain in supported_domains):
        return False
    if any(parsed.path.lower().startswith(prefix) for prefix in DISALLOWED_PREFIXES):
        return False
    return locale_for_url(url) in ALLOWED_LOCALES


def robots_allows(url: str, robots_text: str, user_agent: str = UA) -> bool:
    path = urllib.parse.urlsplit(url).path or "/"
    groups: list[tuple[list[str], list[str]]] = []
    agents: list[str] = []
    disallows: list[str] = []
    active = False
    for raw in robots_text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = [x.strip() for x in line.split(":", 1)]
        if key.lower() == "user-agent":
            if active:
                groups.append((agents, disallows))
            agents, disallows, active = [value.lower()], [], True
        elif key.lower() == "disallow" and active:
            disallows.append(value)
    if active:
        groups.append((agents, disallows))
    applicable: list[str] = []
    for names, rules in groups:
        if "*" in names or any(name in user_agent.lower() for name in names):
            applicable.extend(rules)
    return not any(rule and path.startswith(rule) for rule in applicable)


def _retry_after(value: str | None) -> float:
    if not value:
        return 30.0
    try:
        return max(30.0, min(60.0, float(value)))
    except ValueError:
        try:
            stamp = parsedate_to_datetime(value)
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            return max(30.0, min(60.0, stamp.timestamp() - datetime.now(timezone.utc).timestamp()))
        except Exception:
            return 30.0


def _challenge(text: str, status: int | None = None) -> bool:
    sample = text.lower()[:100000]
    return bool(
        status in {403, 503}
        and any(marker in sample for marker in ("cloudflare", "cf-chl-", "cdn-cgi", "just a moment", "verify you are human"))
    ) or any(marker in sample for marker in ("/cdn-cgi/", "cf-chl-", "verify you are human"))


def _raw_get(url: str) -> tuple[int, str, dict[str, str]]:
    global _LAST_REQUEST, _COOLING, _429S, _TRAINING_ONLY
    if not allowed_url(url):
        raise ChallengeWalled(f"sportytrader: disallowed or unsupported locale URL {url}")
    with _LOCK:
        if _COOLING:
            raise RateLimited("sportytrader: cooling down after HTTP 429")
        wait = MIN_INTERVAL_S - (time.monotonic() - _LAST_REQUEST)
        if wait > 0:
            time.sleep(wait)
        _LAST_REQUEST = time.monotonic()
        request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es,en;q=0.8"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = int(getattr(response, "status", 200))
                text = response.read().decode("utf-8", "replace")
                if _challenge(text, status):
                    _TRAINING_ONLY = True
                    raise ChallengeWalled("sportytrader: Cloudflare/challenge markers detected")
                return status, text, {str(k): str(v) for k, v in response.headers.items()}
        except urllib.error.HTTPError as exc:
            text = exc.read().decode("utf-8", "replace") if exc.fp else ""
            if _challenge(text, exc.code):
                _TRAINING_ONLY = True
                raise ChallengeWalled("sportytrader: Cloudflare/challenge response") from exc
            if exc.code == 429:
                _429S += 1
                _COOLING = True
                wait_seconds = _retry_after(exc.headers.get("Retry-After") if exc.headers else None)
                time.sleep(wait_seconds)
                raise RateLimited(f"sportytrader: HTTP 429; waited {wait_seconds:.0f}s") from exc
            raise


def _get(url: str) -> str:
    host = _host(url)
    if host not in _ROBOTS:
        scheme_host = f"{urllib.parse.urlsplit(url).scheme}://{host}"
        status, robots, _ = _raw_get(f"{scheme_host}/robots.txt")
        if status >= 400:
            raise ChallengeWalled(f"sportytrader: robots unavailable HTTP {status}")
        _ROBOTS[host] = robots
    if not robots_allows(url, _ROBOTS[host]):
        raise ChallengeWalled(f"sportytrader: robots disallows {urllib.parse.urlsplit(url).path}")
    return _raw_get(url)[1]


class _Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self.href: str | None = None
        self.bits: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() == "a":
            self.href = dict(attrs).get("href")
            self.bits = []

    def handle_data(self, data: str):
        if self.href is not None:
            self.bits.append(data)

    def handle_endtag(self, tag: str):
        if tag.lower() == "a" and self.href:
            self.links.append((self.href, " ".join("".join(self.bits).split())))
            self.href = None
            self.bits = []


class _Preds(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[dict[str, str]] = []
        self.attrs: dict[str, str] | None = None
        self.bits: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        values = {str(k): str(v) for k, v in attrs if v is not None}
        if "data-market" in values or "data-selection" in values:
            self.attrs = values
            self.bits = []

    def handle_data(self, data: str):
        if self.attrs is not None:
            self.bits.append(data)

    def handle_endtag(self, tag: str):
        if self.attrs is not None and tag.lower() in {"div", "tr", "li", "article"}:
            row = dict(self.attrs)
            row["text"] = " ".join(" ".join(self.bits).split())
            self.rows.append(row)
            self.attrs = None
            self.bits = []


def _text(page: str) -> str:
    parser = HTMLParser(convert_charrefs=True)
    bits: list[str] = []
    parser.handle_data = bits.append  # type: ignore[method-assign]
    parser.feed(page)
    return " ".join(" ".join(bits).split())


def _num(value: object) -> float | None:
    try:
        return float(str(value).replace(",", ".").rstrip("%"))
    except (TypeError, ValueError):
        return None


def parse_listing(page: str, base: str = BASE) -> list[str]:
    parser = _Links()
    parser.feed(page)
    out: list[str] = []
    seen: set[str] = set()
    for href, _label in parser.links:
        url = urllib.parse.urljoin(base, href)
        path = urllib.parse.urlsplit(url).path
        if "/pronosticos/" not in path or path.rstrip("/") == "/pronosticos/futbol":
            continue
        if not allowed_url(url) or url in seen:
            continue
        seen.add(url)
        out.append(url)
    return out


def _teams(text: str) -> tuple[str | None, str | None]:
    title = re.sub(r"\s+", " ", text).strip()
    for pattern in (
        r"Pronóstico\s+(.+?)\s+-\s+(.+?)(?:\s+-\s+|\s+\||$)",
        r"Pronóstico\s+(.+?)\s+vs\.?\s+(.+?)(?:\s+-\s+|\s+\||$)",
    ):
        match = re.search(pattern, title, re.I)
        if match:
            return match.group(1).strip(), match.group(2).strip()
    return None, None


def parse_match_page(page: str, *, day: str, url: str | None = None) -> list[dict[str, Any]]:
    title = re.search(r"<title[^>]*>(.*?)</title>", page, re.I | re.S)
    text = _text(page)
    home, away = _teams(title.group(1) if title else text[:500])
    if not home or not away:
        home, away = _teams(text[:900])
    if not home or not away:
        return []
    parser = _Preds()
    parser.feed(page)
    rows: list[dict[str, Any]] = []
    for raw in parser.rows:
        raw_market = raw.get("data-market") or raw.get("market") or ""
        raw_selection = raw.get("data-selection") or raw.get("selection") or ""
        if not raw_market or not raw_selection:
            continue
        canonical, _failure = canonical_market_selection(
            raw_market, raw_selection, home=home, away=away,
            line=raw.get("data-line") or raw.get("line"),
        )
        if canonical is None:
            continue
        odds = _num(raw.get("data-odds") or raw.get("odds"))
        probability = _num(raw.get("data-probability") or raw.get("probability"))
        bookmaker = raw.get("data-bookmaker") or raw.get("bookmaker")
        if not bookmaker:
            match = re.search(r"([0-9]+(?:[.,][0-9]+)?)\s+(?:en|at)\s+([A-Z][A-Za-z0-9 .-]{2,})", raw.get("text", ""))
            if match:
                odds = odds or _num(match.group(1))
                bookmaker = match.group(2).strip()
        rows.append({
            "source": SOURCE, "date": day, "home": home, "away": away,
            "fixture_url": url, "market": canonical.market, "selection": canonical.selection,
            "raw_market": raw_market, "raw_selection": raw_selection,
            "line": canonical.line,
            "probability": probability, "odds": odds, "book": bookmaker, "bookmaker": bookmaker,
            "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
    return rows


_HTML_CACHE: dict[str, dict[str, str]] = {}


def _cache_path(day: str) -> Path:
    return LOCALDATA / f"{SOURCE}_html_cache_{day}.json"


def _load_cache(day: str) -> dict[str, str]:
    if day in _HTML_CACHE:
        return _HTML_CACHE[day]
    path = _cache_path(day)
    try:
        value = json.loads(path.read_text())
        _HTML_CACHE[day] = value if isinstance(value, dict) else {}
    except (OSError, ValueError, TypeError):
        _HTML_CACHE[day] = {}
    return _HTML_CACHE[day]


def _save_cache(day: str, cache: dict[str, str]) -> None:
    LOCALDATA.mkdir(parents=True, exist_ok=True)
    path = _cache_path(day)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(cache, sort_keys=True))
    tmp.replace(path)


def capture_day(day: str, *, max_fixtures: int = 60) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stats: dict[str, Any] = {
        "status": "not_run", "st_raw": 0, "st_matched": 0, "requests": 0,
        "cache_hits": 0, "http_429": 0, "training_only": False, "errors": [], "blocker": None,
    }
    reset_state()
    cache = _load_cache(day)
    try:
        listing_url = f"{BASE}/pronosticos/futbol/"
        if listing_url in cache:
            listing = cache[listing_url]
            stats["cache_hits"] += 1
        else:
            listing = _get(listing_url)
            cache[listing_url] = listing
            stats["requests"] += 1
        links = parse_listing(listing)
        stats["st_raw"] = len(links)
        rows: list[dict[str, Any]] = []
        for url in links[:max(0, int(max_fixtures))]:
            try:
                page = cache.get(url)
                if page is not None:
                    stats["cache_hits"] += 1
                else:
                    page = _get(url)
                    cache[url] = page
                    stats["requests"] += 1
                rows.extend(parse_match_page(page, day=day, url=url))
            except (RateLimited, ChallengeWalled):
                raise
            except Exception as exc:
                stats["errors"].append(str(exc)[:180])
        _save_cache(day, cache)
        stats["st_matched"] = len(rows)
        stats["status"] = "ok" if rows else "empty"
        return rows, stats
    except ChallengeWalled as exc:
        stats["status"] = "training_only"
        stats["training_only"] = True
        stats["blocker"] = str(exc)
    except RateLimited as exc:
        stats["status"] = "cooling_down"
        stats["blocker"] = str(exc)
        stats["http_429"] = _429S
    except Exception as exc:
        stats["status"] = "unavailable"
        stats["blocker"] = str(exc)[:180]
    return [], stats


def persist_shadow(day: str, rows: list[dict[str, Any]], stats: dict[str, Any], *, localdata: Path = LOCALDATA) -> Path:
    localdata.mkdir(parents=True, exist_ok=True)
    path = localdata / f"{SOURCE}_shadow_{day}.json"
    payload = {"schema": 1, "source": SOURCE, "date": day, "stats": stats, "rows": rows}
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(path)
    return path


def fetch_day(date: str) -> list[dict]:
    return capture_day(date)[0]
