"""Forebet adapter — JSON endpoint, richest source (probs + best odds + FT/HT scores).

Endpoint: /scripts/getrs.php?ln=en&tp={1x2,uo,bts,ht}&in=DATE&ord=0&tz=0&tzs=&tze=
Needs UA + Referer + X-Requested-With. Serves nothing before 2024-01-01.
Response: [rows, meta]. The 1x2 payload already carries FT and HT scores,
so one merged wide row per match covers all markets.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

BASE = "https://www.forebet.com/scripts/getrs.php"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Referer": "https://www.forebet.com/en/football-tips-and-predictions-for-today",
    "X-Requested-With": "XMLHttpRequest",
}
MIN_DATE = "2024-01-01"
DEFAULT_MARKETS = ("1x2", "uo", "bts")  # ht is certified charcoal; opt-in only


CFFI_IMPERSONATIONS = ("safari17_0", "firefox133")
CLOUD_RETRY_ENV = "EDGE_FACTORY_FOREBET_CLOUD"


def _cloud_fetch_disabled() -> bool:
    """Fail fast on GitHub-hosted runners after a confirmed provider block.

    Run #503 spent almost 19 minutes in intraday execution while every
    urllib/curl_cffi Forebet transport still produced zero usable votes. The
    provider is reachable locally, so local operation remains enabled. An
    explicit opt-in keeps cloud re-probing possible without another code edit.
    """
    in_actions = os.environ.get("GITHUB_ACTIONS", "").strip().lower() == "true"
    opt_in = os.environ.get(CLOUD_RETRY_ENV, "").strip().lower() in {
        "1", "true", "yes", "on"
    }
    return in_actions and not opt_in


def _decode_payload(raw: bytes | str) -> list[dict]:
    """Decode and validate Forebet's ``[rows, meta]`` response.

    A Cloudflare/challenge HTML page can return HTTP 200. Treating it as an
    empty slate hid the cloud-capture failure for weeks, so invalid shape is a
    transport failure, not ``[]``.
    """
    text = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
    data = json.loads(text)
    if not (isinstance(data, list) and data and isinstance(data[0], list)):
        raise ValueError("unexpected payload shape")
    return data[0]


def _urllib_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read()


def _cffi_get(url: str, impersonate: str) -> bytes:
    """Browser-TLS fallback for datacenter/Actions anti-bot responses."""
    from curl_cffi import requests as curl_requests

    # Let curl_cffi provide a User-Agent matching its TLS fingerprint; retain
    # the endpoint-specific AJAX headers Forebet requires.
    headers = {key: value for key, value in HEADERS.items() if key.lower() != "user-agent"}
    headers["Accept-Language"] = "en-US,en;q=0.9"
    response = curl_requests.get(
        url,
        impersonate=impersonate,
        headers=headers,
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}")
    return bytes(response.content)


def _get(tp: str, date: str, retries: int = 3) -> list[dict]:
    """Fetch one market, falling back from urllib to browser impersonation."""
    url = f"{BASE}?ln=en&tp={tp}&in={date}&ord=0&tz=0&tzs=&tze="
    transports = [("urllib", lambda: _urllib_get(url))]
    transports.extend(
        (f"curl_cffi:{identity}", lambda identity=identity: _cffi_get(url, identity))
        for identity in CFFI_IMPERSONATIONS
    )
    errors = []
    attempt_limit = max(1, min(int(retries), len(transports)))
    for attempt, (name, request) in enumerate(transports[:attempt_limit]):
        try:
            return _decode_payload(request())
        except Exception as exc:  # noqa: BLE001 - retry with a distinct transport
            errors.append(f"{name}={type(exc).__name__}")
            if attempt + 1 < attempt_limit:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(
        f"Forebet {tp} {date} failed across transports: {', '.join(errors)}"
    )


def _f(v):
    try:
        x = float(v)
        return x if x == x else None
    except (TypeError, ValueError):
        return None


def _i(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def fetch_day(date: str, markets=DEFAULT_MARKETS, sleep: float = 0.15) -> list[dict]:
    """Fetch one calendar day, merge all market endpoints by match id."""
    if date < MIN_DATE:
        return []
    if _cloud_fetch_disabled():
        raise RuntimeError(
            "Forebet cloud fetch disabled after confirmed GitHub Actions provider block; "
            f"set {CLOUD_RETRY_ENV}=1 for a deliberate retry"
        )
    rows: dict[str, dict] = {}
    failures: list[str] = []
    for tp in markets:
        try:
            payload = _get(tp, date)
        except Exception as exc:  # noqa: BLE001 - preserve partial markets, report failure
            failures.append(f"{tp}:{type(exc).__name__}")
            payload = []
        for m in payload:
            mid = str(m.get("id"))
            row = rows.setdefault(
                mid,
                {
                    "date": date,
                    "kickoff": m.get("DATE_BAH"),
                    "league_id": m.get("league_id"),
                    "league": m.get("short_tag"),
                    "home": m.get("HOST_NAME"),
                    "away": m.get("GUEST_NAME"),
                    "hs": _i(m.get("Host_SC")),
                    "gs": _i(m.get("Guest_SC")),
                    "ht_hs": _i(m.get("Host_SC_HT")),
                    "ht_gs": _i(m.get("Guest_SC_HT")),
                    "status": m.get("comment"),
                },
            )
            if tp == "1x2":
                row.update(
                    p1=_f(m.get("Pred_1")), px=_f(m.get("Pred_X")), p2=_f(m.get("Pred_2")),
                    odd1=_f(m.get("best_odd_1")), oddx=_f(m.get("best_odd_X")),
                    odd2=_f(m.get("best_odd_2")), kelly=_f(m.get("kelly")),
                    pred_hs=_i(m.get("host_sc_pr")), pred_gs=_i(m.get("guest_sc_pr")),
                )
            elif tp == "uo":
                row.update(
                    p_under=_f(m.get("pr_under")), p_over=_f(m.get("pr_over")),
                    odd_under=_f(m.get("best_under")), odd_over=_f(m.get("best_over")),
                    goalsavg=_f(m.get("goalsavg")),
                )
            elif tp == "bts":
                row.update(
                    p_gg=_f(m.get("Pred_gg")), p_ng=_f(m.get("Pred_no_gg")),
                    odd_gg=_f(m.get("odds_gg_y")), odd_ng=_f(m.get("odds_gg_n")),
                )
            elif tp == "ht":
                row.update(
                    p1_ht=_f(m.get("Pred_1_HT")), px_ht=_f(m.get("Pred_X_HT")),
                    p2_ht=_f(m.get("Pred_2_HT")),
                )
        time.sleep(sleep)
    if failures and not rows:
        # local_backfill must not mark an anti-bot/error response as a completed
        # zero-fixture day. Raising keeps the day retryable and makes the cause
        # visible in Actions logs.
        raise RuntimeError(
            f"Forebet {date}: no usable rows; failed markets={','.join(failures)}"
        )
    if failures:
        print(
            f"Forebet {date}: partial capture; failed markets={','.join(failures)}",
            file=sys.stderr,
        )
    return list(rows.values())


COLUMNS = [
    "date", "kickoff", "league_id", "league", "home", "away",
    "hs", "gs", "ht_hs", "ht_gs", "status",
    "p1", "px", "p2", "odd1", "oddx", "odd2", "kelly", "pred_hs", "pred_gs",
    "p_under", "p_over", "odd_under", "odd_over", "goalsavg",
    "p_gg", "p_ng", "odd_gg", "odd_ng",
    "p1_ht", "px_ht", "p2_ht",
]
