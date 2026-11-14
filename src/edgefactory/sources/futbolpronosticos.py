"""Cooperative, shadow-only FutbolPronosticos donor adapter.

This adapter deliberately does not join ``ALL_SOURCES``: it captures a
separate shadow ledger and has no consensus or ticket effect. The site exposes
structured per-fixture ``/pronostico-...`` pages, while settlement is owned by
Edge Factory's existing warehouse/backfill path.
"""
from __future__ import annotations

import html as _html
import json
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

SOURCE = "futbolpronosticos"
BASE = "https://www.futbolpronosticos.com"
UA = "EdgeFactory-cooperative-shadow/1.0 (+operator review)"
MIN_INTERVAL_S = float(os.environ.get("EDGE_FACTORY_FP_MIN_INTERVAL_S", "1.5"))
MAX_FIXTURES = int(os.environ.get("EDGE_FACTORY_FP_MAX_FIXTURES", "80"))
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA", Path(__file__).resolve().parents[3] / "localdata"))

_LOCK = threading.Lock()
_LAST_REQUEST = 0.0
_ROBOTS: dict[str, str] = {}


class UpstreamBlocked(RuntimeError):
    """A cooperative request was blocked or rate-limited."""


def _host(url: str) -> str:
    return urllib.parse.urlsplit(url).netloc.lower()


def robots_allows(url: str, robots_text: str, user_agent: str = UA) -> bool:
    """Conservative robots check for the ``*`` group.

    The page was relay-verified with no Disallow lines. This local parser keeps
    the adapter honest if the site changes policy; it does not attempt to
    interpret a blocked page as an empty slate.
    """
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
        lower = key.lower()
        if lower == "user-agent":
            if active:
                groups.append((agents, disallows))
            agents, disallows, active = [value.lower()], [], True
        elif lower == "disallow" and active:
            disallows.append(value)
    if active:
        groups.append((agents, disallows))
    applicable: list[str] = []
    for agent_names, rules in groups:
        if "*" in agent_names or any(a in user_agent.lower() for a in agent_names):
            applicable.extend(rules)
    for rule in applicable:
        if rule and path.startswith(rule):
            return False
    return True


def _raw_get(url: str) -> str:
    global _LAST_REQUEST
    with _LOCK:
        wait = MIN_INTERVAL_S - (time.monotonic() - _LAST_REQUEST)
        if wait > 0:
            time.sleep(wait)
        _LAST_REQUEST = time.monotonic()
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es,en;q=0.8"})
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                raise UpstreamBlocked("futbolpronosticos: HTTP 429; aborting shadow capture") from exc
            raise UpstreamBlocked(f"futbolpronosticos: HTTP {exc.code}") from exc


def _get(url: str) -> str:
    host = _host(url)
    if host not in _ROBOTS:
        robots_url = f"{urllib.parse.urlsplit(url).scheme}://{host}/robots.txt"
        try:
            _ROBOTS[host] = _raw_get(robots_url)
        except Exception as exc:
            raise UpstreamBlocked(f"futbolpronosticos: robots unavailable: {exc}") from exc
    if not robots_allows(url, _ROBOTS[host]):
        raise UpstreamBlocked(f"futbolpronosticos: robots disallows {urllib.parse.urlsplit(url).path}")
    return _raw_get(url)


class _Links(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag.lower() == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str):
        if tag.lower() == "a" and self._href:
            self.links.append((self._href, " ".join("".join(self._text).split())))
            self._href = None
            self._text = []


class _DataPredictions(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[dict[str, str]] = []
        self._attrs: dict[str, str] | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        attrs_d = {str(k): str(v) for k, v in attrs if v is not None}
        if "data-market" in attrs_d or "data-selection" in attrs_d:
            self._attrs = attrs_d
            self._text = []

    def handle_data(self, data: str):
        if self._attrs is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str):
        if self._attrs is not None and tag.lower() in {"div", "tr", "li", "article"}:
            row = dict(self._attrs)
            if self._text:
                row["text"] = " ".join(" ".join(self._text).split())
            self.rows.append(row)
            self._attrs = None
            self._text = []


def _visible_text(page: str) -> str:
    parser = HTMLParser(convert_charrefs=True)
    bits: list[str] = []
    parser.handle_data = bits.append  # type: ignore[method-assign]
    try:
        parser.feed(page)
    except Exception:
        pass
    return " ".join(" ".join(bits).split())


def _num(value: object) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).replace(",", ".").rstrip("%"))
    except (TypeError, ValueError):
        return None


def parse_slate(page: str, base: str = BASE) -> list[dict[str, str]]:
    parser = _Links()
    parser.feed(page)
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for href, label in parser.links:
        absolute = urllib.parse.urljoin(base, href)
        if "/pronostico-" not in urllib.parse.urlsplit(absolute).path:
            continue
        if _host(absolute) != urllib.parse.urlsplit(base).netloc:
            continue
        if absolute in seen:
            continue
        seen.add(absolute)
        out.append({"url": absolute, "label": label})
    return out


def _fixture_teams(text: str) -> tuple[str | None, str | None]:
    cleaned = _html.unescape(text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    patterns = (
        r"Pronóstico\s+(.+?)\s+-\s+(.+?)(?:\s+-\s+|\s+\||$)",
        r"Pronostico\s+(.+?)\s+vs\.?\s+(.+?)(?:\s+-\s+|\s+\||$)",
        r"^(.+?)\s+vs\.?\s+(.+?)$",
    )
    for pattern in patterns:
        match = re.search(pattern, cleaned, re.I)
        if match:
            return match.group(1).strip(), match.group(2).strip()
    return None, None


def parse_fixture(page: str, *, day: str, url: str | None = None) -> dict[str, Any] | None:
    text = _visible_text(page)
    title_match = re.search(r"<title[^>]*>(.*?)</title>", page, re.I | re.S)
    heading = _html.unescape(title_match.group(1)) if title_match else text[:300]
    home, away = _fixture_teams(heading)
    if not home or not away:
        home, away = _fixture_teams(text[:900])
    if not home or not away:
        return None

    parser = _DataPredictions()
    parser.feed(page)
    markets: list[dict[str, Any]] = []
    for raw in parser.rows:
        market = raw.get("data-market") or raw.get("market")
        selection = raw.get("data-selection") or raw.get("selection")
        if not market or not selection:
            continue
        markets.append({
            "market": market.lower(),
            "selection": selection.lower(),
            "probability": _num(raw.get("data-probability") or raw.get("probability")),
            "odds": _num(raw.get("data-odds") or raw.get("odds")),
            "bookmaker": raw.get("data-bookmaker") or raw.get("bookmaker"),
        })

    # Visible fallback for the site's Spanish labels. This intentionally
    # records the text, rather than inventing a probability or bookmaker.
    prediction = None
    match = re.search(r"(?:El pronóstico|Pronóstico|Predicción)\s*:\s*([^|<]{2,100})", text, re.I)
    if match:
        prediction = " ".join(match.group(1).split())
    score = re.search(r"(?:resultado exacto|marcador exacto)\s*([0-9]{1,2}\s*[:\-]\s*[0-9]{1,2})", text, re.I)
    row: dict[str, Any] = {
        "source": SOURCE,
        "date": day,
        "home": home,
        "away": away,
        "fixture_url": url,
        "prediction_text": prediction,
        "predicted_score": score.group(1).replace(" ", "") if score else None,
        "markets": markets,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    # Only structured fields enter the shadow columns.
    for market_name in ("1x2", "ou", "ou_1.5", "ou_2.5", "ou_3.5", "btts", "cs", "correct_score"):
        found = next((m for m in markets if m["market"] == market_name), None)
        if found:
            row[f"{market_name}_selection"] = found["selection"]
            row[f"{market_name}_probability"] = found["probability"]
    return row


def capture_day(day: str, *, max_fixtures: int = MAX_FIXTURES) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Capture a bounded shadow slate and return rows plus honest diagnostics."""
    stats: dict[str, Any] = {
        "status": "not_run", "raw": 0, "scored": 0, "requests": 0,
        "errors": [], "blocker": None,
    }
    try:
        slate = _get(f"{BASE}/predicciones-de-futbol")
        stats["requests"] += 1
        links = parse_slate(slate)
        stats["raw"] = len(links)
        rows: list[dict[str, Any]] = []
        for link in links[:max(0, int(max_fixtures))]:
            try:
                page = _get(link["url"])
                stats["requests"] += 1
                parsed = parse_fixture(page, day=day, url=link["url"])
                if parsed:
                    rows.append(parsed)
            except Exception as exc:
                stats["errors"].append(str(exc)[:180])
        stats["scored"] = len(rows)
        stats["status"] = "ok" if rows else "empty"
        return rows, stats
    except UpstreamBlocked as exc:
        stats["status"] = "blocked"
        stats["blocker"] = str(exc)
    except Exception as exc:
        stats["status"] = "unavailable"
        stats["blocker"] = str(exc)[:180]
    return [], stats


def _fixture_key(row: dict[str, Any]) -> tuple[str, str, str]:
    def clean(value: object) -> str:
        return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())
    return str(row.get("date") or row.get("match_date") or ""), clean(row.get("home")), clean(row.get("away"))


def settlement_coverage(rows: list[dict[str, Any]], settled_scores: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare donor rows with existing warehouse/backfill score facts.

    No source-owned results are fetched here. A mismatch is an operator
    warning: the existing score backfill did not cover every captured fixture.
    """
    settled_keys = {_fixture_key(row) for row in settled_scores if row.get("hs") is not None or row.get("home_score") is not None}
    captured_keys = {_fixture_key(row) for row in rows}
    matched = len(captured_keys & settled_keys)
    return {
        "captured": len(captured_keys),
        "settled": matched,
        "unmatched": max(0, len(captured_keys) - matched),
        "mismatch": bool(captured_keys and matched != len(captured_keys)),
        "settlement_source": "existing warehouse-score backfill",
    }


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
