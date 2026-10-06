#!/usr/bin/env python3
"""Probe pinnapi (Pinnacle relay) capability without printing secrets.

Diagnostic tool, NOT an ingest path (SHADOW-01 T3, mirrors
scripts/probe_bzzoiro_odds.py). Prints compact metadata only: endpoint
status, JSON shape, event counts, market-name histogram, one trimmed sample
event, and rate-limit headers. It never prints PINNAPI_KEY - URLs are
sanitized before printing.

Acceptance checks (HUNT-01 SOURCE-HUNT-2026-10 section 7.3):
  1. AUTH      - exercise the same contract the adapter uses: the key as an
                 ``x-portal-apikey`` request header, with the legacy ``key=``
                 query form retried only on HTTP 401 (``--auth`` pins one
                 mechanism and skips the fallback). A 401/403 on both is a
                 fail-closed "do not wire" answer.
  2. SCHEMA    - confirm the snapshot shape (event list with home/away and a
                 markets list with market/selection/price). If the shape is
                 different, capture the printed sample event and adjust
                 pinnapi_odds.parse_snapshot - no new crawl needed.
  3. COVERAGE  - event count + league spread vs our 432-league net.

Budget: 2 requests of the 100/day free tier (3 if the 401 fallback fires).

Usage:
    PINNAPI_KEY=... python3 scripts/probe_pinnapi.py
    PINNAPI_KEY=... python3 scripts/probe_pinnapi.py --auth query
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any



def coverage_report(data: Any, slate: list[dict[str, Any]]) -> dict[str, Any]:
    """Join probe events to a supplied slate without persisting anything."""
    events = _events(data)
    priced = {(source_team_key(e.get("home")), source_team_key(e.get("away")))
              for e in events if isinstance(e, dict) and (e.get("markets") or e.get("odds"))}
    matched = []; unmatched = []
    for row in slate:
        key = (source_team_key(row.get("home")), source_team_key(row.get("away")))
        (matched if key in priced else unmatched).append(f"{row.get('home')} v {row.get('away')}")
    total = len(slate)
    return {"slate": total, "matched": len(matched), "coverage_pct": round(100*len(matched)/total, 1) if total else 0.0, "unmatched_examples": unmatched[:5]}

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from edgefactory.identity import source_team_key

# Load the shipped adapter by path: importing edgefactory.sources as a
# package would drag in every other adapter's third-party dependencies, and
# this diagnostic must not fail for a reason unrelated to pinnapi. Reading
# the real module is what keeps the probe on the same contract.
_SPEC = importlib.util.spec_from_file_location(
    "pinnapi_odds_probe", ROOT / "src" / "edgefactory" / "sources" / "pinnapi_odds.py")
adapter = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(adapter)

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - requirements includes python-dotenv
    load_dotenv = None

if load_dotenv:
    load_dotenv()

BASE = os.environ.get("PINNAPI_BASE_URL", "https://pinnapi.com").rstrip("/")
KEY_ENV = "PINNAPI_KEY"


def _sanitize(url: str) -> str:
    """Return an endpoint without any query string (keys never reach stdout)."""
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def _scrub(text: object, key: str = "") -> str:
    value = str(text)
    if key:
        value = value.replace(key, "[REDACTED]")
    return re.sub(r"([?&]key=)[^&\s]+", r"\1[REDACTED]", value)


def _request(url: str, key: str, timeout: int, extra_headers: dict[str, str] | None = None) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "EdgeFactory-cooperative-probe/1.0 (+operator review)",
    }
    headers.update(extra_headers or {})
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(4_000_000).decode("utf-8", "replace")
            rate_headers = {
                str(k): str(v) for k, v in resp.headers.items()
                if "ratelimit" in str(k).lower() or str(k).lower() == "retry-after"
            }
            try:
                data = json.loads(body) if body else None
                parse_error = None
            except json.JSONDecodeError as exc:
                data, parse_error = None, f"JSONDecodeError: {exc}"
            return {"ok": 200 <= resp.status < 400, "status": resp.status,
                    "rate_limit_headers": rate_headers, "data": data,
                    "body_snippet": body[:200], "parse_error": parse_error, "error": None}
    except urllib.error.HTTPError as exc:
        snippet = ""
        try:
            snippet = exc.read(200).decode("utf-8", "replace")
        except Exception:
            pass
        return {"ok": False, "status": exc.code, "rate_limit_headers": {},
                "data": None, "parse_error": None,
                "error": f"HTTPError: {exc.code} {exc.reason}", "body_snippet": snippet[:200]}
    except Exception as exc:
        return {"ok": False, "status": None, "rate_limit_headers": {}, "data": None,
                "parse_error": None, "error": f"{type(exc).__name__}: {exc}"}


def _events(data: Any) -> list[Any]:
    if isinstance(data, dict):
        for key in ("events", "data", "matches"):
            if isinstance(data.get(key), list):
                return data[key]
        return []
    if isinstance(data, list):
        return data
    return []


def _summarize(data: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"json_type": type(data).__name__ if data is not None else "none"}
    events = _events(data)
    if isinstance(data, dict):
        out["top_keys"] = [str(k) for k in list(data.keys())[:12]]
    out["event_count"] = len(events)
    if events and isinstance(events[0], dict):
        first = events[0]
        out["sample_event_keys"] = [str(k) for k in list(first.keys())[:18]]
        markets = first.get("markets") or first.get("odds") or []
        if isinstance(markets, list) and markets and isinstance(markets[0], dict):
            out["first_market_keys"] = [str(k) for k in list(markets[0].keys())[:20]]
            out["first_market_types"] = {str(k): type(v).__name__ for k, v in list(markets[0].items())[:20]}
        histogram: Counter[str] = Counter()
        leagues: Counter[str] = Counter()
        for event in events:
            if not isinstance(event, dict):
                continue
            league = event.get("league") or event.get("tournament") or event.get("competition")
            if isinstance(league, dict):
                league = league.get("name")
            if league:
                leagues[str(league)] += 1
            for entry in (event.get("markets") or event.get("odds") or []):
                if isinstance(entry, dict):
                    histogram[str(entry.get("market") or entry.get("name"))] += 1
        out["market_histogram_top"] = dict(histogram.most_common(10))
        out["leagues_top"] = dict(leagues.most_common(15))
    return out


def _format(name: str, url: str, result: dict[str, Any], secret: str = "") -> str:
    mark = "OK" if result.get("ok") else "ERR"
    lines = [f"[{mark}] {name}  status={result.get('status')}", f"  endpoint={_sanitize(url)}"]
    if result.get("error"):
        lines.append(f"  error={_scrub(result['error'], secret)}")
    if result.get("body_snippet"):
        lines.append(f"  body_sample={_scrub(result['body_snippet'], secret)[:200]}")
    if result.get("parse_error"):
        lines.append(f"  parse_error={_scrub(result['parse_error'], secret)}")
    if result.get("rate_limit_headers"):
        lines.append(f"  rate_limit_headers={result['rate_limit_headers']}")
    for key, value in (result.get("summary") or {}).items():
        if value not in (None, {}, []):
            lines.append(f"  {key}={_scrub(value, secret)}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe pinnapi (Pinnacle relay) capability")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds")
    parser.add_argument("--auth", choices=("query", "header", "auto"), default="auto",
                        help=("auth mechanism: auto (default) sends the "
                              f"{adapter.AUTH_HEADER} header and retries the legacy key= "
                              "query form on HTTP 401; query/header pin one mechanism"))
    args = parser.parse_args()

    key = os.environ.get(KEY_ENV, "").strip()
    print(f"{KEY_ENV} present: {'yes' if key else 'no'}")
    print(f"Base={BASE}  auth={args.auth}  (free tier: 100 REST requests/day; this probe costs 2, 3 if the 401 fallback fires)")
    if not key:
        print("No key: nothing to probe. The shadow adapter stays inert (status=not_run) without a key.")
        return 0

    results: list[tuple[str, str, dict[str, Any]]] = []

    health_url = f"{BASE}/kit/v1/health"
    result = _request(health_url, key, args.timeout)
    result["summary"] = _summarize(result.get("data"))
    results.append(("health (connectivity/auth check)", health_url, result))

    # Same request the adapter builds - URL and auth both come from it, so
    # the probe cannot drift away from the shipped contract.
    order = {"auto": ("header", "query"), "header": ("header",), "query": ("query",)}[args.auth]
    mechanism_used = None
    for mechanism in order:
        markets_url = adapter.markets_url(auth=mechanism)
        headers = {adapter.AUTH_HEADER: key} if mechanism == "header" else None
        result = _request(markets_url, key, args.timeout, extra_headers=headers)
        result["summary"] = _summarize(result.get("data"))
        results.append((f"markets snapshot (soccer sport_id={adapter.sport_id()}, "
                        f"{adapter.EVENT_TYPE}, auth={mechanism})", markets_url, result))
        mechanism_used = mechanism
        if result.get("ok"):
            break
        if result.get("status") != 401:
            break  # only a 401 is a question about the auth mechanism

    for name, url, res in results:
        print(_format(name, url, res, key))
        print("-" * 72)

    markets_result = results[-1][2]
    slate_path = Path(os.environ.get("EDGE_FACTORY_SLATE", str(ROOT / "localdata" / "picks_today.json")))
    try:
        slate_payload = json.loads(slate_path.read_text())
        slate = slate_payload if isinstance(slate_payload, list) else slate_payload.get("rows", [])
    except (OSError, ValueError, TypeError):
        slate = []
    cov = coverage_report(markets_result.get("data"), slate)
    print(f"coverage_pct={cov['coverage_pct']} slate={cov['slate']} matched={cov['matched']}")
    print(f"unmatched_examples={cov['unmatched_examples']}")
    print("projection: shared-fixture target >=30; coverage is diagnostic only and is not persisted.")
    print("ACCEPTANCE 1 - AUTH:",
          f"{mechanism_used} auth works (adapter records this as auth_mechanism)"
          if markets_result.get("ok") else
          "FAILED on every mechanism tried; do not wire (fail-closed)")
    if not markets_result.get("summary", {}).get("event_count"):
        print("ACCEPTANCE 2 - SCHEMA: zero events returned. Record this shape; do NOT")
        print("  write a parser for a payload that has not been observed.")
    if markets_result.get("summary", {}).get("sample_event_keys"):
        print("ACCEPTANCE 2 - SCHEMA: event keys observed above; confirm home/away + markets/market/selection/price")
        print("ACCEPTANCE 3 - COVERAGE: leagues_top above - diff against our 432-league net before promotion talk")
    else:
        print("ACCEPTANCE 2 - SCHEMA: no recognizable event shape; capture output and adjust parse_snapshot")
    print("Done. No key was printed.")

    # Diagnostic-only: failures are reported but do not fail CI/nightly.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
