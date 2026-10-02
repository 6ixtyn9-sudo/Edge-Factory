#!/usr/bin/env python3
"""Probe Betminer (RapidAPI) capability without printing secrets or payloads.

Diagnostic tool, NOT an ingest path (SHADOW-01 T2, mirrors
scripts/probe_bzzoiro_odds.py). Prints compact metadata only: endpoint
status, JSON shape, counts, one trimmed sample match, and rate-limit
headers. It never prints RAPIDAPI_KEY or full response bodies.

BUDGET WARNING: the free tier is 5 requests/day and this probe costs up to
3 of them (leagues + countries + one /matches/{date}). Run it once, in the
morning, and let the shadow adapter's cache-first capture handle the rest.

Acceptance checks (HUNT-01 SOURCE-HUNT-2026-10 section 7.1):
  1. LEAGUE-COUNT  - reconcile the listing-vs-site-vs-docs conflict
                     (RapidAPI listing says 368+, site 1,216, docs 500+).
  2. SCHEMA-SAMPLE - confirm the documented Match Object in the wild
                     (probabilities/predictions/odds subkeys).
  3. RATE-LIMIT    - record X-RateLimit-* response headers so the adapter's
                     quota diagnostics are grounded, not assumed.

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
    parser = argparse.ArgumentParser(description="Probe Betminer (RapidAPI) capability")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (default: today UTC)")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds")
    parser.add_argument("--skip-leagues", action="store_true",
                        help="skip the /leagues + /countries probes (saves 2 of the 5 free daily calls)")
    args = parser.parse_args()

    from datetime import date as _date
    from datetime import datetime, timezone
    day = args.date or datetime.now(timezone.utc).date().isoformat()
    _ = _date  # silence unused import

    key = os.environ.get(KEY_ENV, "").strip()
    print(f"{KEY_ENV} present: {'yes' if key else 'no'}")
    print(f"Probe date={day}  (free tier: 5 requests/day; this probe costs {'1' if args.skip_leagues else '3'})")
    if not key:
        print("No key: nothing to probe. The shadow adapter stays inert (status=not_run) without a key.")
        return 0

    results: list[tuple[str, str, dict[str, Any]]] = []
    if not args.skip_leagues:
        for name, url in (
            ("leagues (league-count reconciliation)", f"{BASE}/leagues"),
            ("countries", f"{BASE}/countries"),
        ):
            result = request_json(url, key, args.timeout)
            result["summary"] = summarize(result.get("data"))
            results.append((name, url, result))
    result = request_json(f"{BASE}/matches/{day}", key, args.timeout)
    result["summary"] = summarize(result.get("data"))
    results.append((f"matches {day} (schema sample)", f"{BASE}/matches/{day}", result))

    for name, url, result in results:
        print(format_result(name, url, result))
        print("-" * 72)

    # Acceptance-check digest (operator fills the blanks from the output above).
    leagues_result = next((r for n, _u, r in results if n.startswith("leagues")), None)
    if leagues_result and leagues_result.get("summary", {}).get("list_len") is not None:
        observed = leagues_result["summary"]["list_len"]
        print("ACCEPTANCE 1 - LEAGUE-COUNT: observed", observed,
              "vs claims", LEAGUE_COUNT_CLAIMS,
              "-> record the observed figure in the ticket before any promotion talk.")
    matches_result = results[-1]
    if matches_result.get("summary", {}).get("sample_probabilities_keys"):
        print("ACCEPTANCE 2 - SCHEMA-SAMPLE: Match Object subkeys observed; confirm they match",
              "the documented probabilities/predictions/odds shape before wiring expectations.")
    if any(r.get("rate_limit_headers") for _n, _u, r in results):
        print("ACCEPTANCE 3 - RATE-LIMIT: headers observed above; feed the real figures into the adapter quota hints.")
    else:
        print("ACCEPTANCE 3 - RATE-LIMIT: no rate-limit headers observed; quota hints stay header-independent.")
    print("Done. No key or full payload was printed.")

    # Diagnostic-only: failures are reported but do not fail CI/nightly.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
