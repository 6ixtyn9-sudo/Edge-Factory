#!/usr/bin/env python3
"""Diagnostic-only SharpAPI probe; never prints the RapidAPI key or query URL."""
from __future__ import annotations
import json, os, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
BASE = "https://sharpapi1.p.rapidapi.com"
HOST = "sharpapi1.p.rapidapi.com"
ENDPOINT = os.environ.get("SHARPAPI_ENDPOINT", "/odds")

def main() -> int:
    key = os.environ.get("RAPIDAPI_KEY", "").strip()
    print(f"RAPIDAPI_KEY present: {'yes' if key else 'no'}")
    if not key: return 0
    url = BASE + ENDPOINT + "?" + urllib.parse.urlencode({"date": datetime.now(timezone.utc).date().isoformat()})
    req = urllib.request.Request(url, headers={"Accept":"application/json", "X-RapidAPI-Key":key, "X-RapidAPI-Host":HOST})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read(2_000_000).decode("utf-8", "replace")
            print(f"status={response.status}")
            print("rate_limit_headers=" + repr({str(k):str(v) for k,v in response.headers.items() if 'ratelimit' in str(k).lower() or str(k).lower() == 'retry-after'}))
            print("body_sample=" + body[:200].replace(key, "[REDACTED]"))
            try: data = json.loads(body)
            except json.JSONDecodeError: data = None
            if isinstance(data, dict): print("top_keys=" + repr(list(data)[:20]))
            if isinstance(data, list) and data and isinstance(data[0], dict): print("first_object_keys_types=" + repr({k:type(v).__name__ for k,v in list(data[0].items())[:20]}))
    except urllib.error.HTTPError as exc:
        sample = exc.read(200).decode("utf-8", "replace") if exc.fp else ""
        print(f"status={exc.code} error_class=HTTPError body_sample={sample.replace(key, '[REDACTED]')[:200]}")
    except Exception as exc: print(f"status=error error_class={type(exc).__name__}")
    return 0
if __name__ == "__main__": raise SystemExit(main())
