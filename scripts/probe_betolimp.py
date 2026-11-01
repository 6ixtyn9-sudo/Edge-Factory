#!/usr/bin/env python3
"""Bounded manual bookmaker diagnostic. Prints JSON; writes nothing.

--input decodes labelled saved reader excerpts; --card compares them read-only.
--native-url makes ONE ordinary GET per public URL (maximum three; fail-fast).
--context-input audits every own-card row against labelled saved StatsHub reader pages.
--native-source defaults to BetOlimp; bookmaker pages are pinned; StatsHub accepts
ordinary public match URLs on the fixed, observed SportPesa tenant route only.
SportPesa StatsHub is explicitly third-party supplied, not an independent bookmaker feed.
No redirects, retries, proxies, cookies, credentials or production admission.
Native responses are transport evidence, NOT executable or decoded quotes.
--native-loader decodes one StatsHub page: fixture/source-score candidates and supported semantic tables.
History is limited to the supported match/sibling schema; source ft scores are NOT verified regulation.
No form aggregates, slate binding or production admission are enabled, and no APIs are called.
--native-discovery follows at most two referenced same-origin JS assets, within three GETs.
--native-context opts into semantic standings/shape inspection for StatsHub only.
This does not enable native H2H/results, whole-slate coverage or production admission.
No raw native body, scripts, cookies, arbitrary headers or exception details are printed.
Opt-in context output is limited to bound public team IDs/names and numeric standings.
Not used by daily/picks/ENH. Native checks require an allowed network environment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.odds_normalization import parse_zoned_timestamp
from edgefactory.sources.betolimp_snapshot import (
    MAX_BYTES,
    compare_card_identity,
    parse_saved_excerpt,
    validate_event_url,
)
from edgefactory.sources.bookmaker_context_snapshot import (
    context_slate_coverage,
    inspect_native_data_loading,
    inspect_native_loader_state,
    parse_context_batch,
    parse_native_context_html,
    validate_context_url,
    validate_discovery_asset_url,
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
        payload = _read_json(card_path, 16 * 1024 * 1024)
        card = payload if isinstance(payload, list) else (
            payload.get("picks") if isinstance(payload, dict) else None)
        if not isinstance(card, list) or len(card) > 5000 or any(
                not isinstance(row, dict) for row in card):
            raise ValueError("invalid or oversized own card")
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


def context_dry_run(input_path: Path, card_path: Path, as_of: datetime) -> dict:
    pages = parse_context_batch(_read_json(input_path, 8 * 1024 * 1024))
    payload = _read_json(card_path, 16 * 1024 * 1024)
    card = payload if isinstance(payload, list) else (
        payload.get("picks") if isinstance(payload, dict) else None)
    return context_slate_coverage(card, pages, as_of)


MAX_NATIVE_BYTES = 2 * 1024 * 1024
NATIVE_HOLDS = (
    "collection_permission_unresolved", "native_market_decoding_unimplemented",
    "odds_view_profile_unverified", "absolute_kickoff_unverified",
    "quote_update_time_unverified", "fixture_not_independently_corroborated",
    "production_admission_not_implemented", "native_context_decoding_unimplemented",
)


# Diagnostic-only exact pages actually observed in public navigation. Not a
# production registry, host-wide crawler, endpoint discovery or API integration.
# No dynamic tenant/client identifiers, credentials or arbitrary query strings.
NATIVE_SOURCE_PAGES = {
    "hollywoodbets": (
        ("https://www.hollywoodbets.net/betting/1/soccer/all/248/england/3092452/"
         "premier-league?filter=match-betting"),
        "https://www.hollywoodbets.net/betting/1/soccer/results?filter=latest",
    ),
    "betway": (
        ("https://www.betway.co.za/event/soccer/italy/serie-a/"
         "lazio-cagliari?eventId=71945376&fixtureType=highlights"),
        ("https://www.betway.co.za/event/soccer/scotland/premiership/"
         "falkirk-celtic?eventId=72201696&fixtureType=highlights"),
    ),
    "betxchange": ("https://betxchange.com/sports", "https://betxchange.com/page/fixtures"),
    "sportpesa": (
        "https://www.sportpesa.co.za/en/sports-betting/soccer-1/",
        "https://www.sportpesa.co.za/results",
    ),
    "sportpesa-statshub": (
        "https://statshub.sportradar.com/sportpesa/en/match/72341350",
        "https://statshub.sportradar.com/sportpesa/en/match/74319006",
    ),
}


def _validate_native_url(url: str, source: str) -> None:
    if source == "betolimp":
        validate_event_url(url)
    elif source == "sportpesa-statshub":
        validate_context_url(url)
    elif source not in NATIVE_SOURCE_PAGES or url not in NATIVE_SOURCE_PAGES[source]:
        raise ValueError("expected an exact observed public page for the selected source")


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


def _native_receipt(response, body: bytes, complete: bool, *, context_url: str | None = None,
                    discovery_url: str | None = None, is_script: bool = False,
                    loader_url: str | None = None, observed_at_utc: str | None = None) -> dict:
    # Default receipts contain fixed metadata/hashes only. Opt-in semantic
    # context adds a strict public-field allowlist, never raw markup. No
    # Location/Set-Cookie, body/title, arbitrary markup URLs, exception strings,
    # request headers or timestamps promoted to quote time.
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
        "context_label_presence": None,
        "decoded_context_row_count": 0,
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
    elif is_script and media in {"application/javascript", "text/javascript", "application/x-javascript"}:
        classification = "native_script_received_unverified"
    elif media not in {"text/html", "application/xhtml+xml"} or is_script:
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
            # Labels can be menus, tutorials or promotional copy. Never count
            # them as statistics, fixture status, form probabilities or results.
            result["context_label_presence"] = {
                label: label.casefold() in visible for label in (
                    "Head to Head", "H2H", "Last meetings", "Last matches",
                    "Season Statistics", "League Position", "Overall Form", "Stats Hub")}
    if context_url is not None and classification == "native_html_received_unverified":
        context = parse_native_context_html(body, context_url)
        result["native_context"] = context
        result["decoded_context_row_count"] = context["decoded_context_row_count"]
    if discovery_url is not None and classification in {
            "native_html_received_unverified", "native_script_received_unverified"}:
        result["data_loading_discovery"] = inspect_native_data_loading(
            body, discovery_url, is_script=is_script)
    if loader_url is not None and classification == "native_html_received_unverified":
        result["loader_state"] = inspect_native_loader_state(
            body, loader_url, observed_at_utc=observed_at_utc)
    return {**result, "classification": classification,
            "transport_ok": classification in {
                "native_html_received_unverified", "native_script_received_unverified"}}


def native_probe(urls: list[str], source: str = "betolimp", *, native_context: bool = False,
                 native_discovery: bool = False, native_loader: bool = False) -> dict:
    """Read-only ordinary public GETs, one attempt each, without an ingest path."""
    if native_loader and (source != "sportpesa-statshub" or len(urls) != 1
                          or native_context or native_discovery):
        raise ValueError("loader inspection requires one StatsHub page and excludes other native modes")
    if native_discovery and (source != "sportpesa-statshub" or len(urls) != 1 or native_context):
        raise ValueError("discovery requires one StatsHub document and excludes context decoding")
    if native_context and source != "sportpesa-statshub":
        raise ValueError("native context inspection is fixed to the observed StatsHub tenant")
    if not 1 <= len(urls) <= 3 or len(set(urls)) != len(urls):
        raise ValueError("expected one to three distinct exact event URLs")
    # Validate the ENTIRE batch before the first request (no partial SSRF).
    for url in urls:
        _validate_native_url(url, source)
    receipts = []
    queue = list(urls)
    for url in queue:
        is_script = native_discovery and url != urls[0]
        if is_script:
            validate_discovery_asset_url(url)
        started = time.monotonic()
        receipt = {"source_url": url, "source_profile": source,
                   "content_origin": "third_party_bookmaker_branded_portal"
                   if source == "sportpesa-statshub" else "bookmaker_public_page",
                   "bookmaker_brand": "sportpesa" if source == "sportpesa-statshub" else source,
                   "identified_context_supplier": "sportradar"
                   if source == "sportpesa-statshub" else None,
                   "decoded_context_row_count": 0,
                   "evidence_kind": "native_http_attempt",
                   "request_started_at_utc": datetime.now(UTC).isoformat(),
                   "admitted_rows": 0, "kickoff_utc": None, "quoted_at": None,
                   "hold_reasons": ([h for h in NATIVE_HOLDS
                                     if h != "native_context_decoding_unimplemented"] + [
                                         "native_results_and_h2h_decoding_unimplemented",
                                         "native_context_field_validation_pending"]
                                    if native_context else list(NATIVE_HOLDS))}
        try:
            # Fresh client per URL prevents Set-Cookie reuse. Ignore proxy,
            # .netrc/auth and SSL override environment; never follow redirects.
            with httpx.Client(trust_env=False, follow_redirects=False,
                              timeout=httpx.Timeout(15.0, connect=5.0),
                              headers={"User-Agent": "EdgeFactory-BetOlimpProbe/1.0"
                                       if source == "betolimp" else "EdgeFactory-PublicBookmakerProbe/1.0",
                                       "Accept": "text/javascript" if is_script else "text/html",
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
                receipt.update(_native_receipt(response, bytes(body), complete,
                                               context_url=url if native_context else None,
                                               discovery_url=url if native_discovery else None,
                                               is_script=is_script,
                                               loader_url=url if native_loader else None,
                                               observed_at_utc=receipt["request_started_at_utc"]))
        except httpx.HTTPError as error:
            receipt.update({"transport_ok": False,
                            "classification": "transport_timeout" if isinstance(
                                error, httpx.TimeoutException) else "transport_error"})
        receipt["request_finished_at_utc"] = datetime.now(UTC).isoformat()
        receipts.append(receipt)
        if native_discovery and not is_script and receipt["transport_ok"]:
            assets = receipt.get("data_loading_discovery", {}).get("script_asset_urls", [])
            queue.extend(assets[:2])  # Never more than three total GETs; no recursive imports.
        if not receipt["transport_ok"]:
            break  # Do not try other event paths after denial/challenge/failure.
    result = {"mode": "native_embedded_loader_diagnostic_only" if native_loader
            else "native_static_discovery_diagnostic_only" if native_discovery
            else "native_access_diagnostic_only", "source_profile": source,
            "network_requests": len(receipts),
            "writes": 0, "admitted_rows": 0, "receipts": receipts,
            "requested_url_count": len(queue), "unattempted_urls": queue[len(receipts):],
            "transport_ok": all(r["transport_ok"] for r in receipts),
            "coverage_status": "unmeasured_native_quote_decoding_not_implemented",
            "context_status": "embedded_loader_decoding_not_stats_or_api_validation" if native_loader
            else "static_data_loading_discovery_not_api_verification" if native_discovery
            else "opt_in_native_semantic_inspection_not_slate_coverage" if native_context
            else "unmeasured_native_context_decoding_not_implemented"}
    if native_loader:
        result["loader_decoding_ok"] = all(
            r.get("loader_state", {}).get("decoded_loader_state_count") == 1 for r in receipts)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input", type=Path, help="saved labelled JSON transcriptions")
    mode.add_argument("--context-input", type=Path, help="labelled StatsHub reader pages; requires --card")
    mode.add_argument("--native-url", action="append", help="exact public URL for selected source; repeat up to 3")
    parser.add_argument("--card", type=Path, help="optional existing card JSON (offline input only)")
    parser.add_argument("--native-source", default="betolimp",
                        choices=("betolimp", *NATIVE_SOURCE_PAGES),
                        help="native only; pinned bookmaker pages or fixed-tenant public StatsHub match URLs")
    parser.add_argument("--native-context", action="store_true",
                        help="StatsHub only: opt into bounded semantic standings/shape inspection")
    parser.add_argument("--native-discovery", action="store_true",
                        help="StatsHub only: inspect one page and at most two referenced static JS assets")
    parser.add_argument("--native-loader", action="store_true",
                        help="StatsHub only: decode supported embedded loader JSON from exactly one page")
    parser.add_argument("--as-of", help="zone-bearing cutoff for offline context coverage only")
    args = parser.parse_args(argv)
    if args.native_loader and (not args.native_url or len(args.native_url) != 1
            or args.native_source != "sportpesa-statshub" or args.native_discovery or args.native_context):
        parser.error("--native-loader requires one StatsHub --native-url and excludes other native modes")
    if args.native_discovery and (not args.native_url or len(args.native_url) != 1
            or args.native_source != "sportpesa-statshub" or args.native_context):
        parser.error("--native-discovery requires one StatsHub --native-url and excludes --native-context")
    if args.native_context and (not args.native_url or args.native_source != "sportpesa-statshub"):
        parser.error("--native-context requires --native-url and --native-source sportpesa-statshub")
    if args.context_input and not args.card:
        parser.error("--context-input requires --card so missing slate rows stay visible")
    if args.as_of and not args.context_input:
        parser.error("--as-of requires --context-input")
    if not args.native_url and args.native_source != "betolimp":
        parser.error("--native-source requires --native-url; --input snapshots remain BetOlimp-only")
    if args.native_url and args.card:
        parser.error("--card is offline-only: use --input or --context-input, not --native-url")
    try:
        if args.context_input:
            as_of = parse_zoned_timestamp(args.as_of) if args.as_of else datetime.now(UTC)
            result = context_dry_run(args.context_input, args.card, as_of)
        else:
            result = (native_probe(args.native_url, args.native_source, native_context=args.native_context,
                                   native_discovery=args.native_discovery,
                                   native_loader=args.native_loader) if args.native_url
                      else dry_run(args.input, args.card))
    except (ValueError, OSError, TypeError, KeyError, IndexError):
        # Do not echo untrusted input, file contents, URLs or exception strings.
        status = "invalid_native_input" if args.native_url else "invalid_offline_input"
        print(json.dumps({"status": status, "admitted_rows": 0}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    if args.native_url and (not result["transport_ok"] or (
            args.native_loader and not result["loader_decoding_ok"])):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
