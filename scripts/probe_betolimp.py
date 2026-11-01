#!/usr/bin/env python3
"""Bounded manual source diagnostic (legacy BetOlimp entry point). Prints JSON; writes nothing.

--input decodes labelled saved reader excerpts; --card compares them read-only.
--native-url makes ONE ordinary GET per exact public event URL (maximum three; fail-fast).
No redirects, retries, proxies, cookies, credentials or production admission.
Native responses are transport evidence, NOT executable or decoded quotes.
No native body, cookies, arbitrary headers or exception details are printed.
Not used by daily/picks/ENH. Native checks require an allowed network environment. --native-source selects
a narrowly validated source; the default remains betolimp. Public JSON sources
report fixture/result shape only, never executable quotes or automatic features.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import UTC, date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.sources.betolimp_snapshot import (
    MAX_BYTES,
    compare_card_identity,
    parse_saved_excerpt,
    validate_event_url,
)


def _read_json(path: Path, limit: int):
    # Bound bytes actually read, not only stat (file can change between calls).
    with path.open("rb") as handle:
        body = handle.read(limit + 1)
    if len(body) > limit:
        raise ValueError("input file exceeds diagnostic size limit")
    return json.loads(body)


def dry_run(input_path: Path, card_path: Path | None = None) -> dict:
    raw = _read_json(input_path, 10 * MAX_BYTES)
    if not isinstance(raw, list) or not 1 <= len(raw) <= 10:
        raise ValueError("expected 1–10 labelled offline snapshots")
    # All-or-nothing: a malformed excerpt cannot yield a partial success report.
    snapshots = [parse_saved_excerpt(item) for item in raw]
    card = None
    if card_path is not None:
        card = _card_rows(card_path)
        for snapshot in snapshots:
            comparisons = [compare_card_identity(row, snapshot) for row in card]
            snapshot["card_comparison"] = {
                "ordered_team_candidate_rows": sum(c["ordered_teams_match"] for c in comparisons),
                "complete_identity_matches": sum(
                    c["ordered_teams_match"] and c["league_match"]
                    and c["absolute_kickoff_match"] for c in comparisons),
            }
    return {"mode": "offline_only", "network_requests": 0, "writes": 0,
            "snapshot_count": len(snapshots),
            "displayed_observation_count": sum(len(s["observations"]) for s in snapshots),
            "admitted_rows": 0, "card_rows_examined": len(card) if card is not None else None,
            "coverage_status": "unmeasured_not_a_live_actual_card_coverage_test",
            "snapshots": snapshots}


MAX_NATIVE_BYTES = 2 * 1024 * 1024
NATIVE_HOLDS = (
    "collection_permission_unresolved", "native_market_decoding_unimplemented",
    "odds_view_profile_unverified", "absolute_kickoff_unverified",
    "quote_update_time_unverified", "fixture_not_independently_corroborated",
    "production_admission_not_implemented",
)


class _PageShape(HTMLParser):
    """Coarse label presence only; never reconstruct prices or fixture identity."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "template", "noscript"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "template", "noscript"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def _validate_native_url(url: str, source: str) -> None:
    if source == "betolimp":
        validate_event_url(url)
        return
    if not isinstance(url, str) or any(c.isspace() for c in url):
        raise ValueError("invalid source URL")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.netloc != "api.github.com"
            or parsed.query or parsed.fragment or "%" in parsed.path):
        raise ValueError("not an exact public dataset URL")
    if source == "openfootball":
        pattern = r"/repos/openfootball/football\.json/contents/20\d{2}(?:-\d{2})?/[a-z]{2}\.\d+(?:-full)?\.json"
    elif source == "statsbomb":
        pattern = r"/repos/statsbomb/open-data/contents/data/matches/\d+/\d+\.json"
    else:
        raise ValueError("unsupported source")
    if not re.fullmatch(pattern, parsed.path):
        raise ValueError("not an approved dataset path")


def _card_rows(path: Path) -> list[dict]:
    payload = _read_json(path, 16 * 1024 * 1024)
    rows = payload if isinstance(payload, list) else (
        payload.get("picks") if isinstance(payload, dict) else None)
    if not isinstance(rows, list) or len(rows) > 5000 or any(not isinstance(r, dict) for r in rows):
        raise ValueError("invalid or oversized own card")
    return rows


def _fixture_summary(body: bytes, source: str, card: list[dict] | None) -> dict:
    data = json.loads(body)
    matches = data.get("matches") if source == "openfootball" and isinstance(data, dict) else data
    if not isinstance(matches, list) or not matches or len(matches) > 5000:
        raise ValueError("invalid or empty fixture payload")
    fixtures = []
    for row in matches:
        if not isinstance(row, dict):
            raise TypeError("invalid fixture row")
        if source == "openfootball":
            home, away, day = row.get("team1"), row.get("team2"), row.get("date")
            clock = row.get("time")
            league = data.get("name")
            score = row.get("score")
            pair = score.get("ft") if isinstance(score, dict) else None
            event_id = None
        else:
            home = (row.get("home_team") or {}).get("home_team_name")
            away = (row.get("away_team") or {}).get("away_team_name")
            day, clock = row.get("match_date"), row.get("kick_off")
            league = (row.get("competition") or {}).get("competition_name")
            pair = [row.get("home_score"), row.get("away_score")]
            event_id = row.get("match_id")
        if (not isinstance(home, str) or not isinstance(away, str)
                or not home.strip() or not away.strip() or len(home) > 160 or len(away) > 160
                or not isinstance(day, str) or date.fromisoformat(day).isoformat() != day):
            raise ValueError("unverified fixture identity/date")
        valid_score = (isinstance(pair, list) and len(pair) == 2
                       and all(type(n) is int and n >= 0 for n in pair))
        fixtures.append({"home": home, "away": away, "date": day,
                         "league": league if isinstance(league, str) else None,
                         "kickoff_display": clock if isinstance(clock, str) else None,
                         "event_id_present": type(event_id) is int and event_id > 0,
                         "score_pair_present": valid_score})
    candidates = None
    if card is not None:
        candidates = sum(any(
            str(row.get("date") or "") == f["date"]
            and compare_card_identity(row, f)["ordered_teams_match"] for f in fixtures) for row in card)
    today = datetime.now(UTC).date().isoformat()
    return {"fixture_rows": len(fixtures),
            "rows_with_score_pair": sum(f["score_pair_present"] for f in fixtures),
            "rows_with_event_id": sum(f["event_id_present"] for f in fixtures),
            "first_match_date": min(f["date"] for f in fixtures),
            "last_match_date": max(f["date"] for f in fixtures),
            "rows_dated_on_or_after_probe_utc_day": sum(f["date"] >= today for f in fixtures),
            "card_rows_examined": len(card) if card is not None else None,
            "same_date_ordered_team_candidate_rows": candidates,
            "complete_identity_matches": 0,
            "examples": fixtures[:3],
            "scope": "fixture_results_sample_only",
            "not_probed": ["named_book_odds", "standings", "injuries", "lineups", "xg",
                           "competition_wide_depth", "authoritative_timezone", "update_sla"],
            "score_period_semantics": "unverified_not_admitted_to_settlement",
            "prematch_context": "derivable_only_from_complete_predecision_verified_history"}


def _native_receipt(response, body: bytes, complete: bool, source="betolimp", card=None) -> dict:
    # Only fixed enum-like metadata and hashes leave the native response.
    # In particular: no Location/Set-Cookie, body/title, URLs from markup,
    # exception strings, request headers or timestamps promoted to quote time.
    media = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if not re.fullmatch(r"[a-z0-9.+-]+/[a-z0-9.+-]+", media) or len(media) > 80:
        media = "unknown"
    encoding = response.headers.get("content-encoding", "identity").strip().lower()
    identity = encoding in {"", "identity"}
    result = {
        "evidence_kind": "native_http_response",
        "http_status": response.status_code, "media_type": media,
        "sampled_body_bytes": len(body), "body_complete": complete,
        "body_sha256": hashlib.sha256(body).hexdigest() if complete else None,
        "sample_sha256": hashlib.sha256(body).hexdigest(),
        "content_encoding": "identity" if identity else "unsupported",
        "main_market_label_presence": None,
        "decoded_observation_count": 0,
    }
    status = response.status_code
    if 300 <= status < 400:
        classification = "redirect_not_followed"
    elif status in {401, 403}:
        classification = "access_denied"
    elif status == 429:
        classification = "rate_limited"
    elif status != 200:
        classification = "http_error"
    elif not complete:
        classification = "response_size_limit"
    elif not identity:
        classification = "unsupported_content_encoding"
    elif source != "betolimp":
        if media not in {"application/json", "application/vnd.github.raw+json"}:
            classification = "unexpected_content_type"
        else:
            try:
                result["fixture_summary"] = _fixture_summary(body, source, card)
                classification = "native_json_received_unverified"
            except (ValueError, TypeError, KeyError, AttributeError, RecursionError):
                classification = "invalid_fixture_json"
    elif media not in {"text/html", "application/xhtml+xml"}:
        classification = "unexpected_content_type"
    else:
        page = _PageShape()
        try:
            page.feed(body.decode("utf-8", errors="replace"))
            page.close()
        except (ValueError, AssertionError):
            return {**result, "classification": "unparseable_html", "transport_ok": False}
        visible = " ".join(" ".join(page.parts).split()).casefold()
        # Normal /cdn-cgi/ assets alone are NOT evidence of a challenge.
        challenge = any(marker in visible for marker in (
            "just a moment...", "verify you are human", "checking your browser",
            "enable javascript and cookies to continue"))
        if challenge:
            classification = "challenge_not_bypassed"
        else:
            classification = "native_html_received_unverified"
            result["main_market_label_presence"] = {
                label: label.casefold() in visible for label in (
                    "Full Time Result", "Total Goals", "Both teams to score")}
    return {**result, "classification": classification,
            "transport_ok": classification in {"native_html_received_unverified",
                                               "native_json_received_unverified"}}


def native_probe(urls: list[str], *, source="betolimp", card_path: Path | None = None) -> dict:
    """Read-only ordinary public GETs, one attempt each, without an ingest path."""
    if not 1 <= len(urls) <= 3 or len(set(urls)) != len(urls):
        raise ValueError("expected one to three distinct exact event URLs")
    # Validate the ENTIRE batch before the first request (no partial SSRF).
    for url in urls:
        _validate_native_url(url, source)
    if card_path is not None and source == "betolimp":
        raise ValueError("native bookmaker HTML cannot be compared as decoded fixtures")
    card = _card_rows(card_path) if card_path is not None else None
    holds = list(NATIVE_HOLDS) if source == "betolimp" else [
        "dataset_reuse_terms_unverified", "fixture_not_independently_corroborated",
        "absolute_kickoff_unverified", "source_recency_and_completeness_unverified",
        "prematch_admission_not_implemented"]
    receipts = []
    for url in urls:
        started = time.monotonic()
        receipt = {"source_url": url, "evidence_kind": "native_http_attempt",
                   "request_started_at_utc": datetime.now(UTC).isoformat(),
                   "admitted_rows": 0, "kickoff_utc": None, "quoted_at": None,
                   "hold_reasons": holds, "source_profile": source}
        try:
            # Fresh client per URL prevents Set-Cookie reuse. Ignore proxy,
            # .netrc/auth and SSL override environment; never follow redirects.
            with httpx.Client(trust_env=False, follow_redirects=False,
                              timeout=httpx.Timeout(15.0, connect=5.0),
                              headers={"User-Agent": "EdgeFactory-BetOlimpProbe/1.0" if source == "betolimp"
                                       else "EdgeFactory-PrematchProbe/1.0",
                                       "Accept": "text/html" if source == "betolimp"
                                       else "application/vnd.github.raw+json",
                                       "Accept-Encoding": "identity"}) as client, \
                    client.stream("GET", url) as response:
                body = bytearray()
                complete = True
                for chunk in response.iter_raw(chunk_size=65536):
                    if time.monotonic() - started > 30:
                        raise httpx.TimeoutException("bounded response deadline")
                    body.extend(chunk[:MAX_NATIVE_BYTES + 1 - len(body)])
                    if len(body) > MAX_NATIVE_BYTES:
                        complete = False
                        break
                receipt.update(_native_receipt(response, bytes(body), complete, source, card))
        except httpx.HTTPError as error:
            receipt.update({"transport_ok": False, "transport_error_type": type(error).__name__,
                            "classification": "transport_timeout" if isinstance(
                                error, httpx.TimeoutException) else "transport_error"})
        receipt["request_finished_at_utc"] = datetime.now(UTC).isoformat()
        receipts.append(receipt)
        if not receipt["transport_ok"]:
            break  # Do not try other event paths after denial/challenge/failure.
    return {"mode": "native_access_diagnostic_only", "network_requests": len(receipts),
            "writes": 0, "admitted_rows": 0, "receipts": receipts,
            "requested_url_count": len(urls), "unattempted_urls": urls[len(receipts):],
            "transport_ok": all(r["transport_ok"] for r in receipts),
            "coverage_status": "unmeasured_native_quote_decoding_not_implemented"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input", type=Path, help="saved labelled JSON transcriptions")
    mode.add_argument("--native-url", action="append", help="exact public event URL; repeat up to 3")
    parser.add_argument("--native-source", choices=("betolimp", "openfootball", "statsbomb"),
                        default="betolimp", help="explicit URL profile; not an arbitrary URL fetcher")
    parser.add_argument("--card", type=Path,
                        help="read-only card comparison for saved input or public fixture JSON")
    args = parser.parse_args(argv)
    if args.native_url and args.card and args.native_source == "betolimp":
        parser.error("--card requires --input; native responses are not decoded quotes")
    try:
        if args.input and args.native_source != "betolimp":
            parser.error("--native-source applies only to --native-url")
        result = native_probe(args.native_url, source=args.native_source, card_path=args.card) \
            if args.native_url else dry_run(args.input, args.card)
    except (ValueError, OSError, TypeError, KeyError, IndexError):
        # Do not echo untrusted input, file contents, URLs or exception strings.
        status = "invalid_native_input" if args.native_url else "invalid_offline_input"
        print(json.dumps({"status": status, "admitted_rows": 0}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 1 if args.native_url and not result["transport_ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
