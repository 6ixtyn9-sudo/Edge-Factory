#!/usr/bin/env python3
"""Bounded manual bookmaker diagnostic. Prints JSON; writes nothing.

--input decodes labelled saved reader excerpts; --card compares them read-only.
--browser-response-input inspects labelled operator-supplied JSON offline; no token replay.
Source FT score candidates remain unadmitted; null status is not completion proof.
--native-url makes ONE ordinary GET per public URL (maximum three; fail-fast).
--context-input audits every own-card row against labelled saved StatsHub reader pages.
--native-source defaults to BetOlimp; bookmaker pages are pinned; StatsHub accepts
ordinary public match URLs on the fixed, observed SportPesa tenant route only.
SportPesa StatsHub is explicitly third-party supplied, not an independent bookmaker feed.
Default HTTP modes: no redirects, retries, proxies, cookies, credentials or production admission.
Native responses are transport evidence, NOT executable or decoded quotes.
--native-loader decodes one StatsHub page: fixture/source-score candidates and supported semantic tables.
History is limited to the supported match/sibling schema; source ft scores are NOT verified regulation.
No form aggregates, slate binding or production admission are enabled, and no APIs are called.
--native-discovery follows at most two referenced same-origin JS assets, within three GETs.
--native-context opts into semantic standings/shape inspection for StatsHub only.
This does not enable native H2H/results, whole-slate coverage or production admission.
No raw native body, scripts, cookies, arbitrary headers or exception details are printed.
Opt-in context output is limited to bound public team IDs/names and numeric standings.
--browser-context explicitly loads one public page in a fresh optional Playwright browser.
Only that page may initiate bounded GET dependencies; no feed replay, clicks or raw output.
It returns unverified numeric field samples, not admitted history or standings.
Requires Playwright/Chromium; --browser-install-runtime explicitly installs them
on a GitHub-hosted Linux runner only, without workflow YAML changes.
Not used by daily/picks/ENH. Native checks require an allowed network environment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from contextlib import contextmanager
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
    MAX_CONTEXT_BYTES,
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


# This is an optional, isolated Playwright path in the EXISTING manual probe.
# It is deliberately not imported by production or by the one-GET modes.
_BROWSER_MAX_REQUESTS = 192
_BROWSER_MAX_FEEDS = 32
_BROWSER_MAX_BODY = 2 * 1024 * 1024
_BROWSER_OPERATIONS = frozenset({
    "match_info_statshub", "stats_match_get", "stats_match_head2head",
    "stats_team_lastx", "stats_team_nextx", "stats_team_versus", "stats_season_tables",
    "config_tree_mini", "event_get", "stats_match_form", "stats_match_tableslice",
    "stats_team_versusrecent", "stats_team_lastxextended", "stats_uniquetournament_fixtures",
    "stats_season_teamfixtures", "stats_season_fixtures2", "stats_season_meta",
    "livescore_season_fixtures",
})


def _browser_request_kind(url, resource_type, source_url, fixture):
    """Classify browser-initiated reads; never construct/replay a supplier URL."""
    from urllib.parse import urlsplit

    try:
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.username or parsed.password or parsed.fragment
                or parsed.port not in (None, 443)):
            return None
        if resource_type == "document":
            return "document" if url == source_url else None
        if (parsed.hostname == "statshub.sportradar.com" and resource_type in {"script", "stylesheet"}
                and re.fullmatch(r"/assets/[A-Za-z0-9_@.,-]+\.(js|css)", parsed.path)):
            return "asset"
        if (parsed.hostname not in {"sh.fn.sportradar.com", "widgets.fn.sportradar.com"}
                or resource_type not in {"fetch", "xhr"} or fixture is None):
            return None
        # Tenant/language/timezone prefix is selected by the page, not this probe.
        match = re.fullmatch(r"/(?:[A-Za-z0-9_:/.-]+/)?gismo/([a-z_0-9]+)/([0-9/]+)", parsed.path)
        if not match or match[1] not in _BROWSER_OPERATIONS:
            return None
        operation, arguments = match[1], match[2].split("/")
        if any(not a or len(a) > 12 for a in arguments):
            return None
        # Constrain inspected history/tables to the loader's actual identity domains.
        if operation == "stats_team_lastx":
            if (arguments[0] not in {fixture[s]["team_uid"] for s in ("home", "away")}
                    or len(arguments) != 2 or arguments[1] != "20"):
                return None
            return "history:" + arguments[0]
        if operation == "stats_match_tableslice":
            return "table_slice:" + arguments[0] if arguments == [fixture["event_id"]] else None
        if operation == "stats_season_tables":
            if arguments != [fixture["_seasonid"]]:
                return None
            return "standings:" + arguments[0]
        # These are dependency reads triggered by this page, not crawl targets.
        return "support"
    except (ValueError, TypeError, KeyError):
        return None


def _browser_numeric_sample(record):
    """Exact numeric field projection, NOT an extractor or identity/status binding.

    No strings, URLs, keys outside this literal allowlist, inferred dates/scores,
    defaults for missing values, or source credentials can reach output.
    """
    if not isinstance(record, dict):
        return {}
    scalar = ("_id", "_sid", "_seasonid", "_utid", "uid", "pos", "rank", "played", "won",
              "drawn", "lost", "points", "goalsfor", "goalsagainst", "goalsdiff",
              "playedTotal", "winTotal", "drawTotal", "lossTotal", "pointsTotal",
              "goalsForTotal", "goalsAgainstTotal", "goalsDiffTotal", "home", "away", "uts",
              "ended_uts", "updated_uts")
    selected = {k: record[k] for k in scalar
                if type(record.get(k)) is int and abs(record[k]) <= 10**12}
    if "status" in record and record["status"] is None:
        selected["status"] = None
    for flag in ("inlivescore", "tobeannounced", "postponed", "walkover", "retired", "disqualified", "canceled"):
        if type(record.get(flag)) is bool:
            selected[flag] = record[flag]
    # A bounded, explicitly named two-level projection; never a generic recursive dump.
    for key in ("time", "_dt", "team", "result", "status"):
        if isinstance(record.get(key), dict):
            selected[key] = {k: v for k, v in record[key].items()
                             if k in scalar and type(v) is int and abs(v) <= 10**12}
    teams = record.get("teams")
    if isinstance(teams, dict):
        selected["teams"] = {s: {k: teams[s][k] for k in ("_id", "uid")
                                if type(teams[s].get(k)) is int and 0 < teams[s][k] <= 10**12}
                             for s in ("home", "away") if isinstance(teams.get(s), dict)}
    periods = record.get("periods")
    if isinstance(periods, dict):
        selected["periods"] = {p: {s: periods[p][s] for s in ("home", "away")
                                  if type(periods[p].get(s)) is int and 0 <= periods[p][s] <= 999}
                               for p in ("ft", "ot", "ap") if isinstance(periods.get(p), dict)}
    return selected


def _browser_history_score_candidates(data, owner_uid, generated):
    """Observed lastx contract only. Source FT fields are not regulation admission.

    Null status, missing completion times, mixed competitions and season-local
    team IDs are retained as such. Never interpret inlivescore as lifecycle, use
    result.winner for regulation, or convert opaque supplier form coefficients.
    """
    def positive(value):
        return type(value) is int and 0 < value < 10**12

    def score(value):
        return isinstance(value, dict) and all(
            type(value.get(s)) is int and 0 <= value[s] <= 999 for s in ("home", "away"))

    candidates, conflicts, invalid_events, held = {}, set(), set(), {}
    for match in data["matches"]:
        try:
            if (data["team"].get("_doc") != "uniqueteam" or type(data["team"].get("_sid")) is not int
                    or data["team"]["_sid"] != 1 or match.get("_doc") != "match" or match.get("_sid") != 1
                    or type(match.get("_sid")) is not int
                    or not all(positive(match.get(k)) for k in ("_id", "_rcid", "_tid", "_utid", "_seasonid"))):
                raise ValueError("identity_unresolved")
            teams = match["teams"]
            if (not isinstance(teams, dict) or any(not isinstance(teams.get(s), dict)
                    or not positive(teams[s].get("_id")) or not positive(teams[s].get("uid"))
                    or type(teams[s].get("_sid")) is not int or teams[s]["_sid"] != 1
                    or teams[s].get("virtual") is not False for s in ("home", "away"))
                    or teams["home"]["uid"] == teams["away"]["uid"]
                    or teams["home"]["_id"] == teams["away"]["_id"]
                    or sum(teams[s]["uid"] == owner_uid for s in ("home", "away")) != 1):
                raise ValueError("team_uid_binding_unresolved")
            for flag in ("tobeannounced", "postponed", "walkover", "retired", "disqualified", "canceled"):
                if match.get(flag) is not False:
                    raise ValueError("exception_flags_unresolved")
            tournament = data.get("tournaments", {}).get(str(match["_tid"]))
            unique = data.get("uniquetournaments", {}).get(str(match["_utid"]))
            if (not isinstance(tournament, dict) or not isinstance(unique, dict)
                    or any(type(tournament.get(k)) is not int or tournament[k] != match[m]
                           for k, m in (("_id", "_tid"), ("_tid", "_tid"), ("_utid", "_utid"),
                                        ("_sid", "_sid"), ("_rcid", "_rcid"), ("seasonid", "_seasonid")))
                    or any(type(unique.get(k)) is not int or unique[k] != match[m]
                           for k, m in (("_id", "_utid"), ("_utid", "_utid"), ("_sid", "_sid"),
                                        ("_rcid", "_rcid"), ("currentseason", "_seasonid")))):
                raise ValueError("competition_metadata_unresolved")
            clock = match["time"]
            if (not isinstance(clock, dict) or type(clock.get("uts")) is not int
                    or not 0 < clock["uts"] < 4102444800 or clock.get("tz") != "UTC"
                    or type(clock.get("tzoffset")) is not int or clock["tzoffset"] != 0):
                raise ValueError("source_clock_unresolved")
            kickoff = datetime.fromtimestamp(clock["uts"], UTC)
            if kickoff.strftime("%d/%m/%y") != clock.get("date") or kickoff.strftime("%H:%M") != clock.get("time"):
                raise ValueError("source_clock_conflict")
            periods, displayed = match.get("periods"), match.get("result")
            ft = periods.get("ft") if isinstance(periods, dict) else None
            if not score(ft) or not score(displayed):
                raise ValueError("source_score_unresolved")
            period = displayed.get("period")
            if period not in ("nt", "ap"):
                raise ValueError("source_period_unsupported")
            if period == "nt" and (any(k in periods for k in ("ot", "ap"))
                                   or any(ft[s] != displayed[s] for s in ("home", "away"))):
                raise ValueError("source_normal_time_score_conflict")
            if period == "ap" and (not score(periods.get("ap")) or any(
                    periods["ap"][s] != displayed[s] for s in ("home", "away"))):
                raise ValueError("source_penalty_score_conflict")
            record = {"event_id": str(match["_id"]), "owner_team_uid": str(owner_uid),
                      "owner_side": next(s for s in ("home", "away") if teams[s]["uid"] == owner_uid),
                      "kickoff_utc": kickoff.isoformat(),
                      "teams": {s: {"team_id": str(teams[s]["_id"]), "team_uid": str(teams[s]["uid"])}
                                for s in ("home", "away")},
                      "season_id": str(match["_seasonid"]), "tournament_id": str(match["_tid"]),
                      "unique_tournament_id": str(match["_utid"]),
                      "source_ft_score": {s: ft[s] for s in ("home", "away")},
                      "source_display_score": {s: displayed[s] for s in ("home", "away")},
                      "source_display_period": period, "source_status_is_null": match.get("status", {}) is None,
                      "source_has_extra_time": "ot" in periods, "source_has_penalties": "ap" in periods,
                      "kickoff_before_source_generation": kickoff.timestamp() < generated if generated else None,
                      "completion_verified": False, "regulation_verified": False, "admitted": False}
            event = record["event_id"]
            if event in candidates and candidates[event] != record:
                conflicts.add(event)
            candidates[event] = record
        except (KeyError, TypeError, AttributeError, ValueError) as error:
            # Only fixed reason enums may leave this parser; never source strings.
            allowed = {"identity_unresolved", "team_uid_binding_unresolved", "exception_flags_unresolved",
                       "competition_metadata_unresolved", "source_clock_unresolved", "source_clock_conflict",
                       "source_score_unresolved", "source_period_unsupported", "source_normal_time_score_conflict",
                       "source_penalty_score_conflict"}
            reason = str(error) if type(error) is ValueError and str(error) in allowed else "unsupported_record_shape"
            held[reason] = held.get(reason, 0) + 1
            if positive(match.get("_id")):
                invalid_events.add(str(match["_id"]))
    bindings = {}
    for record in candidates.values():
        for team in record["teams"].values():
            for a, b in (("team_id", "team_uid"), ("team_uid", "team_id")):
                bindings.setdefault((record["season_id"], a, team[a]), set()).add(team[b])
    for event, record in candidates.items():
        if any(len(bindings[(record["season_id"], a, team[a])]) != 1
               for team in record["teams"].values()
               for a in ("team_id", "team_uid")):
            conflicts.add(event)
    records = sorted((r for event, r in candidates.items() if event not in conflicts | invalid_events),
                     key=lambda r: (r["kickoff_utc"], r["event_id"]), reverse=True)
    if conflicts:
        held["duplicate_event_conflict"] = len(conflicts)
    return {"source_ft_score_candidates": records, "source_ft_candidate_count": len(records),
            "held_record_reasons": held, "usable_form_rows": 0, "admitted_rows": 0,
            "fixture_binding_verified": False, "capture_time_verified": False,
            "collection_permission_verified": False, "freshness_verified": False,
            "hold_reasons": ["operator_response_not_independent_capture", "completion_time_unverified",
                             "freshness_unverified",
                             "regulation_results_unverified", "target_fixture_binding_unverified",
                             "historical_sample_completeness_unverified", "production_admission_disabled"]}


def _browser_stat_sample(body, kind):
    """Expose actual field samples only; no guessed parser, form or admission."""
    if len(body) > _BROWSER_MAX_BODY:
        raise ValueError("browser body limit")
    payload = json.loads(body)
    docs = payload.get("doc") if isinstance(payload, dict) else None
    if not isinstance(docs, list) or len(docs) != 1 or not isinstance(docs[0], dict):
        return {"status": "unsupported_document_envelope"}
    data = docs[0].get("data")
    if kind.startswith("table_slice:"):
        return {"status": "empty_match_table_slice" if data == [] else "unsupported_match_table_slice_shape",
                "empty_table_slice": data == [], "standings_availability_verified": False}
    if not isinstance(data, dict):
        return {"status": "unsupported_data_envelope"}
    if kind.startswith("history:"):
        team = data.get("team")
        matches = data.get("matches")
        if (not isinstance(team, dict) or type(team.get("_id")) is not int
                or str(team["_id"]) != kind.split(":")[1]
                or not isinstance(matches, list) or len(matches) > 100
                or any(not isinstance(m, dict) for m in matches)):
            return {"status": "unsupported_or_unbound_history_envelope"}
        return {"status": "public_numeric_field_samples_only", "owner_team_uid": team["_id"],
                "response_match_count": len(matches), "sample_truncated": len(matches) > 20,
                "matches": [_browser_numeric_sample(m) for m in matches[:20]],
                **_browser_history_score_candidates(data, team["_id"], docs[0].get("_dob")
                    if type(docs[0].get("_dob")) is int and 0 < docs[0]["_dob"] < 4102444800 else None)}
    tables = data.get("tables")
    if not isinstance(tables, list) or len(tables) > 8:
        return {"status": "unsupported_table_envelope"}
    selected = []
    for table in tables:
        rows = table.get("tablerows") if isinstance(table, dict) else None
        if (not isinstance(rows, list) or len(rows) > 40
                or any(not isinstance(r, dict) for r in rows)):
            return {"status": "unsupported_table_rows"}
        selected.append({"table": _browser_numeric_sample(table),
                         "rows": [_browser_numeric_sample(r) for r in rows]})
    return {"status": "public_numeric_field_samples_only", "tables": selected}


def _browser_setup_runtime():
    """Explicit disposable Actions-runner setup, never production/app-state writes."""
    import os
    import subprocess

    if (os.environ.get("GITHUB_ACTIONS") != "true"
            or os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted"
            or os.environ.get("RUNNER_OS") != "Linux"):
        return False
    # Fixed commands only. No source URL, input interpolation, shell, relay,
    # credentials, package registry override or proxy environment is passed.
    env = {k: os.environ[k] for k in ("PATH", "HOME", "TMPDIR", "LANG") if k in os.environ}
    env["DEBIAN_FRONTEND"] = "noninteractive"
    commands = [([sys.executable, "-m", "pip", "install", "--quiet", "--retries", "0",
                  "--timeout", "20", "playwright==1.56.0"], 60),
                ([sys.executable, "-m", "playwright", "install", "--with-deps",
                  "--only-shell", "chromium"], 120)]
    try:
        for command, timeout in commands:
            subprocess.run(command, check=True, timeout=timeout, env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.SubprocessError, OSError):
        return False
    return True


@contextmanager
def _browser_runtime():
    # Same optional runtime as sources.forebet._playwright_get. No relay/secrets.
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as runtime:
            yield runtime
    except PlaywrightError:
        # Playwright errors can embed token-bearing request URLs.
        raise RuntimeError("browser operation failed") from None


def browser_context_probe(url, *, install_runtime=False):
    """One fresh public page; bounded automatic reads, no clicks/replay/persistence.

    This explicitly authorized mode is NOT the native one-GET contract. It blocks
    POST, redirects, other documents, popups, service workers and unrelated hosts.
    Only sanitized field samples are retained. An unsupported shape stays unknown.
    """
    import os
    from types import SimpleNamespace

    validate_context_url(url)
    started = datetime.now(UTC).isoformat()
    result = {"mode": "public_browser_context_inspection_only", "source_profile": "sportpesa-statshub",
              "source_url": url, "request_started_at_utc": started,
              "transport_ok": False, "status": "browser_runtime_unavailable", "javascript_enabled": False,
              "network_requests": 0, "page_initiated_feed_requests": 0, "blocked_requests": 0,
              "request_limit_reached": False, "application_data_writes": 0,
              "admitted_rows": 0, "usable_form_rows": 0, "regulation_verified": False,
              "whole_slate_coverage_verified": False, "statistic_samples": [],
              "sample_policy": "first_completed_response_per_kind_not_cross_copy_validation",
              "hold_reasons": ["samples_are_not_bound_statistics", "completion_and_regulation_unverified",
                               "freshness_unverified", "production_admission_disabled"]}
    result["runtime_preparation_requested"] = install_runtime
    if install_runtime and not _browser_setup_runtime():
        result["status"] = "browser_runtime_setup_failed_or_not_hosted_runner"
        result["request_finished_at_utc"] = datetime.now(UTC).isoformat()
        return result
    # Dependency setup does not spend the public-page observation window.
    started = datetime.now(UTC).isoformat()
    result["request_started_at_utc"] = started
    fixture = None
    document_seen = False
    document_ok = False
    fatal = False
    samples_seen = set()
    deadline = time.monotonic() + 30

    def route_request(route):
        nonlocal document_seen, fatal
        request = route.request
        kind = _browser_request_kind(request.url, request.resource_type, url, fixture)
        if (time.monotonic() >= deadline or result["network_requests"] >= _BROWSER_MAX_REQUESTS
                or (kind not in {None, "asset", "document"}
                    and result["page_initiated_feed_requests"] >= _BROWSER_MAX_FEEDS)):
            result["request_limit_reached"] = True
            fatal = True
            kind = None
        if (fatal or request.method != "GET" or request.redirected_from is not None
                or kind is None or (kind == "document" and document_seen)):
            result["blocked_requests"] += 1
            route.abort()
            return
        if kind == "document":
            document_seen = True
        elif kind != "asset":
            result["page_initiated_feed_requests"] += 1
        result["network_requests"] += 1
        route.continue_()

    def observe_response(response):
        nonlocal fixture, document_ok, fatal
        request = response.request
        kind = _browser_request_kind(response.url, request.resource_type, url, fixture)
        if kind is None:
            return
        # Never print response headers, addresses, exception messages or raw data.
        if response.status in {401, 403, 429}:
            result["status"] = "access_denied_not_bypassed"
            fatal = True
            return
        if response.status != 200 or kind in {"asset", "support"} or fatal or kind in samples_seen:
            return
        try:
            length = response.headers.get("content-length")
            if length is not None and (not length.isdigit() or int(length) > _BROWSER_MAX_BODY):
                raise ValueError("browser body limit")
            body = response.body()
            if len(body) > _BROWSER_MAX_BODY:
                raise ValueError("browser body limit")
            if kind == "document":
                # Playwright has already decompressed this document. Reuse the
                # existing challenge/loader inspector, NOT its wire-byte claims.
                document = SimpleNamespace(status_code=response.status,
                                           headers={"content-type": response.headers.get("content-type", "")})
                receipt = _native_receipt(document, body, True, loader_url=url, observed_at_utc=started)
                if not receipt["transport_ok"]:
                    result["status"] = "page_rejected_not_bypassed"
                    fatal = True
                    return
                loader = receipt.get("loader_state", {})
                candidate = loader.get("fixture_candidate", {})
                fixture = candidate.get("fixture")
                result["fixture_candidate"] = candidate
                document_ok = True
            elif kind not in samples_seen:
                samples_seen.add(kind)
                result["statistic_samples"].append({"kind": kind.split(":")[0],
                                                    **_browser_stat_sample(body, kind)})
        except (ValueError, TypeError, KeyError, IndexError, RecursionError, OSError):
            # A network/JSON error may contain credentials. Fail closed.
            result["status"] = "response_inspection_failed"
            fatal = True

    try:
        with _browser_runtime() as runtime:
            # Do not pass application secrets or proxy env to the child browser.
            env = {k: os.environ[k] for k in ("PATH", "HOME", "TMPDIR", "LANG", "LD_LIBRARY_PATH")
                   if k in os.environ}
            browser = runtime.chromium.launch(headless=True, env=env)
            try:
                context = browser.new_context(service_workers="block", accept_downloads=False)
                context.route("**/*", route_request)
                context.route_web_socket("**/*", lambda connection: connection.close())
                result["javascript_enabled"] = True
                page = context.new_page()
                context.on("page", lambda other: other.close() if other != page else None)
                page.on("response", observe_response)
                result["status"] = "browser_page_incomplete"
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                # No clicks, scrolling, extra routes, feed calls or arbitrary sleeps.
                # Give only this page's normal initial dependency requests time to finish.
                if not fatal:
                    page.wait_for_timeout(max(0, min(8000, int((deadline - time.monotonic()) * 1000))))
                if document_ok and not fatal:
                    result.update(status="browser_page_observed_not_statistics_validation", transport_ok=True)
            finally:
                browser.close()
    except (ImportError, RuntimeError, OSError, ValueError, TypeError, KeyError, AttributeError):
        # Missing package/browser, navigation denial, timeout and tool errors
        # are sanitized. Never retry/fallback to relay, requests or other matches.
        result["transport_ok"] = False
        if result["status"] in {"browser_page_incomplete", "browser_page_observed_not_statistics_validation"}:
            result["status"] = "browser_navigation_failed"
    result["request_finished_at_utc"] = datetime.now(UTC).isoformat()
    return result


def saved_browser_response_dry_run(path):
    raw = _read_json(path, 4 * MAX_CONTEXT_BYTES)
    if not isinstance(raw, list) or not 1 <= len(raw) <= 4:
        raise ValueError("expected one to four labelled saved browser responses")
    receipts = []
    for item in raw:
        if (not isinstance(item, dict) or set(item) != {
                "evidence_kind", "payload_scope", "source_url", "observed_at_utc", "response"}
                or item["evidence_kind"] != "operator_supplied_browser_response"
                or item["payload_scope"] not in {"selected_fields_projection", "full_response"}):
            raise ValueError("invalid saved browser response label")
        source_url = validate_context_url(item["source_url"])
        observed = item["observed_at_utc"]
        if observed is not None and (not isinstance(observed, str) or len(observed) > 128
                                     or parse_zoned_timestamp(observed) is None):
            raise ValueError("invalid response observation timestamp")
        response = item["response"]
        query = response.get("queryUrl") if isinstance(response, dict) else None
        match = re.fullmatch(r"(stats_team_lastx)/([1-9]\d{0,11})/20|(stats_match_tableslice)/([1-9]\d{0,11})", query or "")
        if match is None:
            raise ValueError("unsupported saved response query")
        if match[1]:
            kind, event = "history:" + match[2], "stats_team_lastx"
        else:
            if match[4] != source_url.removesuffix("/statistics").rsplit("/", 1)[-1]:
                raise ValueError("table slice page event mismatch")
            kind, event = "table_slice:" + match[4], "stats_match_tableslice"
        docs = response.get("doc")
        if (not isinstance(docs, list) or len(docs) != 1 or not isinstance(docs[0], dict)
                or docs[0].get("event") != event):
            raise ValueError("saved response event mismatch")
        sample = _browser_stat_sample(json.dumps(response, allow_nan=False).encode(), kind)
        generated = docs[0].get("_dob")
        generated = generated if type(generated) is int and 0 < generated < 4102444800 else None
        receipts.append({"evidence_kind": item["evidence_kind"], "payload_scope": item["payload_scope"],
                         "source_url": source_url, "observed_at_utc": observed,
                         "source_generated_at_utc": datetime.fromtimestamp(generated, UTC).isoformat()
                         if generated else None, "source_timestamp_is_not_capture_or_completion": True,
                         "kind": kind.split(":")[0], **sample})
    return {"mode": "saved_browser_response_diagnostic_only", "source_profile": "sportpesa-statshub",
            "network_requests": 0, "application_data_writes": 0, "admitted_rows": 0,
            "usable_form_rows": 0, "whole_slate_coverage_verified": False, "receipts": receipts}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input", type=Path, help="saved labelled JSON transcriptions")
    mode.add_argument("--browser-response-input", type=Path,
                      help="offline labelled browser response JSON; no request replay, card binding or admission")
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
    parser.add_argument("--browser-context", action="store_true",
                        help="StatsHub only: opt-in read-only public-page Playwright inspection; one URL")
    parser.add_argument("--browser-install-runtime", action="store_true",
                        help="explicitly install pinned Playwright/Chromium on a GitHub-hosted Linux runner only")
    parser.add_argument("--as-of", help="zone-bearing cutoff for offline context coverage only")
    args = parser.parse_args(argv)
    if args.browser_response_input and args.card:
        parser.error("--browser-response-input does not implement card binding")
    if args.browser_install_runtime and not args.browser_context:
        parser.error("--browser-install-runtime requires --browser-context")
    if args.browser_context and (not args.native_url or len(args.native_url) != 1
            or args.native_source != "sportpesa-statshub" or args.native_context
            or args.native_discovery or args.native_loader):
        parser.error("--browser-context requires one StatsHub --native-url and excludes other native modes")
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
        if args.browser_context:
            result = browser_context_probe(args.native_url[0], install_runtime=args.browser_install_runtime)
        elif args.browser_response_input:
            result = saved_browser_response_dry_run(args.browser_response_input)
        elif args.context_input:
            as_of = parse_zoned_timestamp(args.as_of) if args.as_of else datetime.now(UTC)
            result = context_dry_run(args.context_input, args.card, as_of)
        else:
            result = (native_probe(args.native_url, args.native_source, native_context=args.native_context,
                                   native_discovery=args.native_discovery,
                                   native_loader=args.native_loader) if args.native_url
                      else dry_run(args.input, args.card))
    except (ValueError, OSError, TypeError, KeyError, IndexError, RecursionError, OverflowError):
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
