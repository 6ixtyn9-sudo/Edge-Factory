#!/usr/bin/env python3
"""Probe Betminer (RapidAPI) capability without printing secrets or payloads.

Diagnostic tool, NOT an ingest path (SHADOW-01 T2, mirrors
scripts/probe_bzzoiro_odds.py). Prints compact metadata only: endpoint
status, JSON shape, counts, one trimmed sample match, and rate-limit
headers. It never prints RAPIDAPI_KEY or full response bodies.

BUDGET WARNING: the free tier is 5 requests/day. This probe makes at most ONE
``/matches/{date}`` request and writes a scrubbed daily receipt under
``localdata/``. A later run reads that receipt and consumes zero calls. It never
tries an endpoint ladder.

Acceptance checks:
  1. CONTRACT      - confirm the documented V3 Match Object endpoint.
  2. SCHEMA-SAMPLE - retain scrubbed keys/counts, never the full payload.
  3. RATE-LIMIT    - record only X-RateLimit/Retry-After response headers.

Usage:
    RAPIDAPI_KEY=... PYTHONPATH=src python scripts/probe_betminer.py
    RAPIDAPI_KEY=... PYTHONPATH=src python scripts/probe_betminer.py --date 2026-10-03
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - requirements includes python-dotenv
    load_dotenv = None

if load_dotenv:
    load_dotenv()

from edgefactory.sources import betminer as adapter  # noqa: E402

BASE = "https://betminer.p.rapidapi.com"
API_HOST = "betminer.p.rapidapi.com"
KEY_ENV = "RAPIDAPI_KEY"

# The three coverage claims to reconcile (see SOURCE-HUNT-2026-10 section 5.1.H).
LEAGUE_COUNT_CLAIMS = {"rapidapi_listing": "368+", "site_homepage": "1216", "docs_subtitle": "500+"}


def _headers(key: str) -> dict[str, str]:
    return {
        "Accept": "application/json",
        "User-Agent": "EdgeFactory-cooperative-probe/1.0 (+operator review)",
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": API_HOST,
    }


def request_json(url: str, key: str, timeout: int) -> dict[str, Any]:
    """Return compact request result with parsed JSON or sanitized error."""
    req = urllib.request.Request(url, headers=_headers(key))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(2_000_000).decode("utf-8", "replace")
            rate_headers = {
                str(k): str(v) for k, v in resp.headers.items()
                if "ratelimit" in str(k).lower() or str(k).lower() == "retry-after"
            }
            try:
                data = json.loads(body) if body else None
                parse_error = None
            except json.JSONDecodeError as exc:
                data, parse_error = None, f"JSONDecodeError: {exc}"
            return {
                "ok": 200 <= resp.status < 400,
                "status": resp.status,
                "rate_limit_headers": rate_headers,
                "data": data,
                "parse_error": parse_error,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        snippet = ""
        try:
            snippet = exc.read(200).decode("utf-8", "replace")
        except Exception:
            pass
        rate_headers = {
            str(k): str(v) for k, v in (exc.headers or {}).items()
            if "ratelimit" in str(k).lower() or str(k).lower() == "retry-after"
        }
        return {
            "ok": False, "status": exc.code, "rate_limit_headers": rate_headers,
            "data": None, "parse_error": None,
            "error": f"HTTPError: {exc.code} {exc.reason}", "body_snippet": snippet[:200],
        }
    except Exception as exc:
        return {
            "ok": False, "status": None, "rate_limit_headers": {},
            "data": None, "parse_error": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def summarize(data: Any) -> dict[str, Any]:
    """Compact shape summary: counts, keys, and one trimmed sample match."""
    out: dict[str, Any] = {"json_type": type(data).__name__ if data is not None else "none"}
    if isinstance(data, dict):
        out["top_keys"] = [str(k) for k in list(data.keys())[:12]]
        out["list_counts"] = {str(k): len(v) for k, v in data.items() if isinstance(v, list)}
        inner = data.get("data")
        if isinstance(inner, list) and inner:
            out["data_len"] = len(inner)
            first = inner[0] if isinstance(inner[0], dict) else {}
            out["sample_keys"] = [str(k) for k in list(first.keys())[:20]]
            for sub in ("probabilities", "predictions", "odds", "competition", "home_team"):
                if isinstance(first.get(sub), dict):
                    out[f"sample_{sub}_keys"] = [str(k) for k in list(first[sub].keys())[:14]]
            out["sample_trimmed"] = {
                k: first.get(k) for k in (
                    "kickoff", "status", "league", "home_team", "away_team",
                    "probabilities", "predictions",
                ) if k in first
            }
    elif isinstance(data, list):
        out["list_len"] = len(data)
        if data and isinstance(data[0], dict):
            out["sample_keys"] = [str(k) for k in list(data[0].keys())[:16]]
    return out


def format_result(name: str, url: str, result: dict[str, Any]) -> str:
    mark = "OK" if result.get("ok") else "ERR"
    lines = [f"[{mark}] {name}  status={result.get('status')}", f"  url={url}"]
    if result.get("error"):
        lines.append(f"  error={result['error']}")
    if result.get("body_snippet"):
        lines.append(f"  body_snippet={result['body_snippet']}")
    if result.get("parse_error"):
        lines.append(f"  parse_error={result['parse_error']}")
    if result.get("rate_limit_headers"):
        lines.append(f"  rate_limit_headers={result['rate_limit_headers']}")
    summary = result.get("summary", {})
    for key in ("json_type", "top_keys", "list_counts", "list_len", "data_len", "sample_keys"):
        if summary.get(key) is not None:
            lines.append(f"  {key}={summary[key]}")
    for key in ("sample_probabilities_keys", "sample_predictions_keys", "sample_odds_keys"):
        if summary.get(key):
            lines.append(f"  {key}={summary[key]}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe one documented Betminer endpoint")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (default: today UTC)")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds")
    args = parser.parse_args()

    from datetime import datetime, timezone
    day = args.date or datetime.now(timezone.utc).date().isoformat()
    endpoint = adapter.matches_url(day)
    existing = adapter._load_probe_receipt(day)  # daily quota guard shared with capture
    if existing is not None:
        print(f"Probe date={day} calls_consumed=0/5 (persisted receipt reused)")
        print(json.dumps(existing, indent=2, sort_keys=True))
        return 0

    key = os.environ.get(KEY_ENV, "").strip()
    print(f"{KEY_ENV} present: {'yes' if key else 'no'}")
    print(f"Probe date={day} calls_budgeted=1/5 endpoint=/matches/{{date}}")
    if not key:
        print("No key: calls_consumed=0/5; adapter remains inert (status=not_run).")
        return 0

    result = request_json(endpoint, key, args.timeout)
    result["summary"] = summarize(result.get("data"))
    print(format_result(f"matches {day} (schema sample)", endpoint, result))
    reason = None if result.get("ok") else (
        "http_404_endpoint_contract" if result.get("status") == 404 else "probe_http_failure"
    )
    receipt_path = adapter._persist_probe_receipt(
        day,
        endpoint=endpoint,
        http_status=result.get("status"),
        reason=reason,
        schema_sample=result.get("summary"),
    )
    print(f"receipt={receipt_path}")
    print("calls_consumed=1/5; later probes/captures read this receipt (zero calls).")
    print("No key or full payload was printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
