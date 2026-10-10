"""SharpAPI named-book price source.

Endpoint contract (repaired 2026-10-06 against the vendor playground)
---------------------------------------------------------------------
This adapter used to go through the RapidAPI marketplace relay at
``sharpapi1.p.rapidapi.com``, which returned HTTP 401 with SharpAPI's own
``disabled_api_key`` envelope. The operator's account is a DIRECT one, and
the vendor playground shows the real contract::

    GET https://api.sharpapi.io/api/v1/odds?sport=soccer
    X-API-Key: <SHARPAPI_KEY>

One host, one credential, no gateway. A captured soccer response confirms
the board carries UEFA Nations League with a three-way ``moneyline`` (the
draw included) and ``total_goals`` lines - the two markets this system
bets. The query is built from
explicit configuration rather than assumption - in particular ``date`` is NOT
sent unless ``SHARPAPI_DATE_PARAM`` names a parameter the provider actually
documents. Sending an unsupported filter is how a healthy source starts
looking empty.

Configuration (all explicit; ``SHARPAPI_SPORT`` is required for capture)::

    SHARPAPI_ENDPOINT=/api/v1/odds
    SHARPAPI_SPORT=soccer
    SHARPAPI_LIMIT=...
    SHARPAPI_BOOK=...
    SHARPAPI_MARKET=...
    SHARPAPI_DATE_PARAM=...   # only when the provider confirms a date filter

Failure classification is deliberately granular: 401 is auth, 403 is
auth/plan, 429 is quota, and a VALID EMPTY result is never confused with an
unrecognized schema. Prices are PREMATCH only: the captured sample was entirely ``is_live``
in-play pricing, which must never reach a prematch card or a closing-line
measurement. No credential is ever logged.
"""
from __future__ import annotations
import json, os, re, threading, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from edgefactory import rapidapi_diagnostics as _rapidapi
from edgefactory.odds_normalization import canonical_market_selection
from edgefactory.source_health import SHARPAPI_BOARD_FIELDS

SOURCE = "sharpapi_odds"
BASE = "https://api.sharpapi.io"
API_HOST = "api.sharpapi.io"
DEFAULT_ENDPOINT = "/api/v1/odds"


def endpoint() -> str:
    """Current endpoint path, normalized to a leading slash."""
    value = (os.environ.get("SHARPAPI_ENDPOINT") or DEFAULT_ENDPOINT).strip() or DEFAULT_ENDPOINT
    return value if value.startswith("/") else "/" + value


def query_params(day: str | None = None) -> dict[str, str]:
    """The documented, configurable request contract.

    ``date`` is intentionally absent by default: the published example filters
    by ``sport`` and ``limit`` only. An operator who has confirmed a date
    filter in the playground sets ``SHARPAPI_DATE_PARAM`` to its real name.
    """
    params: dict[str, str] = {}
    for env_name, param in (
        ("SHARPAPI_SPORT", "sport"),
        ("SHARPAPI_LIMIT", "limit"),
        ("SHARPAPI_BOOK", "book"),
        ("SHARPAPI_MARKET", "market"),
        # Constrains the board at the server. An earlier note here said the
        # soccer feed pages at 50 rows behind a cursor, which would have made
        # the configured limit a no-op. The live board on 2026-10-06 says
        # otherwise: one request, a configured limit of 100, and exactly 100
        # rows came back truncated at the limit. The limit is honoured and the
        # real board is larger than the page we see. Whether values ABOVE 100
        # are honoured has never been tried.
        #
        # What actually binds is that rows are metered per market per book,
        # not per match: those 100 rows carried five fixtures and a single
        # under-21 qualifier took 67 of them. So this filter is what puts a
        # chosen competition in front of the prematch filter. A larger page
        # reaches deeper for free but is not a substitute for it.
        ("SHARPAPI_LEAGUE", "league"),
    ):
        value = (os.environ.get(env_name) or "").strip()
        if value:
            params[param] = value
    date_param = (os.environ.get("SHARPAPI_DATE_PARAM") or "").strip()
    if date_param and day:
        params[date_param] = str(day)
    return params
KEY_ENV = "SHARPAPI_KEY"
# One credential, one host. The earlier two-key theory was wrong in an
# instructive way: the 401 carried SharpAPI's OWN envelope
# {"error":{"code":"disabled_api_key"}} rather than the gateway's
# {"message":"Endpoint ... does not exist"}, which was read as "the gateway
# passed us through and the origin rejected the key". The likelier reading,
# confirmed by the vendor playground, is that the marketplace listing is not
# the operator's account at all. The direct host accepts SHARPAPI_KEY alone.
#
# Unset, the header is sent blank rather than omitted so the provider's own
# 401 wording is what gets recorded; a silently dropped header produces a
# different error and teaches us nothing about the credential.
ORIGIN_KEY_ENV = KEY_ENV   # retained: one credential now serves both roles
LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA", Path(__file__).resolve().parents[3] / "localdata"))
MIN_INTERVAL_S = float(os.environ.get("EDGE_FACTORY_SHARPAPI_MIN_INTERVAL_S", "5"))
MAX_CALLS_PER_RUN = int(os.environ.get("EDGE_FACTORY_SHARPAPI_MAX_CALLS", "1"))
RETRYABLE_ZERO_ROW_STATUSES = {"auth", "quota", "unavailable", "blocked", "error", "cooldown"}
_lock = threading.Lock(); _last = 0.0; _calls = 0; _429 = 0; _cooling = False; _DIAG: dict[str, Any] = {}
_CANONICALIZATION_DROP_REASONS: dict[str, int] = {}

class UpstreamBlocked(RuntimeError): pass

def reset_state() -> None:
    global _last, _calls, _429, _cooling
    _last = 0.0; _calls = 0; _429 = 0; _cooling = False

def diagnostics() -> dict[str, Any]: return dict(_DIAG)
def _set_diag(value: dict[str, Any]) -> dict[str, Any]: _DIAG.update(value); return value
def _key() -> str | None:
    value = os.environ.get(KEY_ENV, "").strip(); return value or None

def _origin_key() -> str | None:
    """SharpAPI's own origin credential, sent as X-API-Key. None when unset."""
    value = os.environ.get(ORIGIN_KEY_ENV, "").strip(); return value or None

def auth_headers() -> dict[str, str]:
    """The single credential the direct vendor API accepts.

    The gateway headers are gone. Sending them to the vendor's own host was
    the defect: the marketplace relay answered 401 with SharpAPI's own
    disabled-key envelope, which reads like a dead credential and is in fact
    a dead middleman. One key, one header, named by the vendor's docs.
    """
    return {"X-API-Key": _key() or ""}

def odds_url(day: str | None = None) -> str:
    params = query_params(day)
    query = urllib.parse.urlencode(sorted(params.items()))
    return BASE + endpoint() + (f"?{query}" if query else "")

def _headers(headers: Any) -> dict[str, str]:
    return {str(k): str(v) for k, v in (headers.items() if hasattr(headers, "items") else [])
            if "ratelimit" in str(k).lower() or str(k).lower() == "retry-after"}

def _wait(value: str | None) -> float:
    try: return max(1.0, min(60.0, float(value or 5)))
    except ValueError: return 5.0

def get_json(url: str, *, timeout: int = 30) -> tuple[int, Any, dict[str, str]]:
    global _last, _calls, _429, _cooling
    if _cooling: raise UpstreamBlocked("sharpapi: run cooling down after repeated HTTP 429 responses")
    if not _key(): raise UpstreamBlocked(f"{KEY_ENV} not set; shadow capture skipped")
    for attempt in range(2):
        if _calls >= MAX_CALLS_PER_RUN: raise UpstreamBlocked("sharpapi: per-run call budget reached")
        with _lock:
            delay = MIN_INTERVAL_S - (time.monotonic() - _last)
            if delay > 0: time.sleep(delay)
            _last = time.monotonic(); _calls += 1
        req = urllib.request.Request(url, headers={"Accept":"application/json", "User-Agent":"EdgeFactory-cooperative-shadow/1.0 (+operator review)", **auth_headers()})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read(8_000_000).decode("utf-8", "replace")
                try: payload = json.loads(body) if body else None
                except json.JSONDecodeError: payload = None
                return int(getattr(response, "status", 200)), payload, _headers(response.headers)
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                _429 += 1
                if _429 >= 2 or attempt: _cooling = True; raise UpstreamBlocked("sharpapi: repeated HTTP 429; cooling down") from exc
                time.sleep(_wait(exc.headers.get("Retry-After") if exc.headers else None)); continue
            # Capture the provider's own explanation. Without it a 404 is
            # unactionable: "path not routed" and "key not subscribed to this
            # API" are the same status code and opposite fixes.
            snippet = ""
            try: snippet = exc.read(400).decode("utf-8", "replace")
            except Exception: pass
            raise UpstreamBlocked(f"sharpapi: HTTP {exc.code} {exc.reason}; {snippet[:240]}") from exc
        except Exception as exc: raise UpstreamBlocked(f"sharpapi: {type(exc).__name__}: {exc}") from exc
    raise UpstreamBlocked("sharpapi: exhausted retries")

def _scrub(value: str) -> str:
    """Never echo credential material into diagnostics or ledgers.

    BOTH credentials are redacted. The origin key is the one most likely to be
    echoed back, because providers quote the offending credential in auth
    errors and that error body is retained verbatim in the ledger.
    """
    for secret in (_key(), _origin_key()):
        if secret:
            value = value.replace(secret, "[REDACTED]")
    return value


def _num(x: object) -> float | None:
    try: return float(x)
    except (TypeError, ValueError): return None

_PREMATCH_DROP_REASONS: dict[str, int] = {}
# Refusals that mean the capture window was wrong, as opposed to refusals
# that mean the board carried markets we do not bet. The distinction decides
# which remedy the health line asks for, so the two groups are named here
# rather than inferred at the branch.
_LIVE_LIKE_DROP_REASONS = ("live_price", "stale_pregame_price")

# What the board itself looked like, independent of how many rows survived.
# A zero with no board context is unreadable: an empty slate, a page that
# filled up with live games before reaching our fixtures, and a competition
# filter the server did not recognise all print the same bare zero. These
# counts are what separate them. Vendor-supplied values only - never a
# configured filter value, which arrives from a deployment secret.
_BOARD_CONTEXT: dict[str, Any] = {}
# Bounds on what travels into a committed artefact: enough competitions to
# recognise a global board, short enough that no payload gets archived.
_MAX_LEAGUES_RECORDED = 12
_MAX_LEAGUE_NAME_CHARS = 48
# Team names are two per row, so the cap is larger than the competition
# one but still a census: enough to recognise our own card written the
# vendor's way, never enough to archive a board.
_MAX_TEAM_NAMES_RECORDED = 40
_MAX_TEAM_NAME_CHARS = 40


def board_context() -> dict[str, Any]:
    """Board shape observed by the most recent parse."""
    return dict(_BOARD_CONTEXT)


def _league_token(value: object) -> str:
    """Comparison form for a competition id: case and punctuation removed.

    Deliberately tolerant. The vendor spells one competition at least two
    ways inside a single response (``euro_quals_-_u21_championship`` and
    ``uefa_u21_euro_qualifiers`` were both observed on 2026-10-06), so an
    exact string comparison would report a working filter as a broken one.
    """
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())


def _bounded_census(counts: dict[str, int], *, limit: int, width: int) -> dict[str, int]:
    """Rank on the full name, cap, and only then shorten.

    Shortening first merges names that share a long prefix and throws one
    of the counts away with them. Adding on collision keeps the total
    honest when two names are still identical once shortened.
    """
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:limit]
    out: dict[str, int] = {}
    for name, count in ranked:
        short = name[:width]
        out[short] = out.get(short, 0) + count
    return out


def _record_board(fixtures: set[tuple[str, str]], leagues: dict[str, int],
                  teams: dict[str, int], *, priced_rows: int) -> None:
    """Store what the board carried, bounded for a committed artefact."""
    _BOARD_CONTEXT.update({
        "board_fixtures": len(fixtures),
        "board_league_count": len(leagues),
        "board_leagues": _bounded_census(leagues, limit=_MAX_LEAGUES_RECORDED,
                                         width=_MAX_LEAGUE_NAME_CHARS),
        # The vendor's own spelling of the sides. This is what makes a zero
        # overlap answerable after the fact: the join key is an exact match
        # on a compacted string plus a small hand-curated alias table built
        # against the sources we already run, and this vendor's naming has
        # never been exercised against it. So "none of our fixtures matched"
        # has two causes with opposite remedies - the board genuinely does
        # not carry our card, or it carries it under names the table does
        # not fold. Recording the names lets the artefact settle which,
        # without committing to a looser matcher before a real board has
        # ever been seen.
        "board_team_count": len(teams),
        "board_team_names": _bounded_census(teams, limit=_MAX_TEAM_NAMES_RECORDED,
                                            width=_MAX_TEAM_NAME_CHARS),
        "board_non_prematch_rows": sum(_PREMATCH_DROP_REASONS.values()),
        "board_priced_rows": priced_rows,
    })


def _text(value: object) -> str:
    """Flatten either a bare string or a {"name": ...} reference object."""
    if isinstance(value, dict):
        value = value.get("name") or value.get("title") or value.get("display_name")
    return str(value or "").strip()


def _sides(row: dict[str, Any]) -> tuple[str, str]:
    """Home and away from the DECLARED fields only.

    Deliberately never parsed out of ``event_id``. The captured sample proves
    the slug does not encode orientation: ``..._kazakhstan_moldova_...`` is a
    Moldova home fixture while ``..._faroeislands_kazakhstan_...`` is a
    Kazakhstan home fixture. Deriving sides from the slug would silently
    invert the card for an unknowable subset of events, and an inverted side
    prices perfectly - it just prices the wrong team.
    """
    home = _text(row.get("home_team")) or _text(row.get("home"))
    away = _text(row.get("away_team")) or _text(row.get("away"))
    return home, away


def _selection_for(row: dict[str, Any], home: str, away: str) -> str:
    """Prefer the vendor's explicit side token over the display label.

    ``selection_type`` is a closed vocabulary (home/away/draw/over/under);
    ``selection`` is free text carrying club names that drift between books.
    Resolving home/away back to the fixture's own team names lets the shared
    normalizer confirm the side instead of string-matching a brand.
    """
    kind = str(row.get("selection_type") or "").strip().lower()
    if kind == "home" and home: return home
    if kind == "away" and away: return away
    if kind in {"draw", "tie"}: return "draw"
    if kind in {"over", "under"}: return kind
    return _text(row.get("selection"))


def _is_flat(records: list[Any]) -> bool:
    """True when rows are one-selection-per-record rather than nested books."""
    for record in records:
        if not isinstance(record, dict): continue
        if any(isinstance(record.get(k), list) for k in ("bookmakers", "bookies", "books")):
            return False
        if "market_type" in record or "selection_type" in record or "odds_decimal" in record:
            return True
    return False


def parse_flat_rows(price_rows: list[Any], *, day: str,
                    card_keys: set[tuple[str, str]] | None = None,
                    team_key: Any = None) -> tuple[list[dict[str, Any]], bool]:
    """Parse the vendor's flat one-row-per-selection board.

    Each record is a single price: fixture, book, market, selection, odds.
    The parameter used to be called ``events``, which was a lie: a hundred
    of these is not a hundred matches. On 2026-10-06 a hundred of them was
    five fixtures, one of which carried sixty-seven. The name misled a
    reader into annotating the board as a hundred events, which reverses
    the verdict on the vendor - a hundred matches none of which are ours
    is damning coverage evidence, five in-play strangers is a filtering
    problem. ``board_rows`` counts these records; ``board_fixtures``
    counts the distinct matches behind them, and both are recorded.
    Live and stale prices are refused here rather than downstream - this lane
    feeds a prematch card, and an in-play price is not a worse prematch price,
    it is a different quantity.

    When our own card is supplied, every refusal is counted twice: once for
    the board and once restricted to OUR fixtures. On an unfiltered global
    board those are different measurements and only the second one is about
    us. Soccer runs continuously somewhere, so in-play rows in the top of a
    world board are background, not a statement about our capture window.
    """
    global _PREMATCH_DROP_REASONS
    rows: list[dict[str, Any]] = []; shaped = False
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    fixtures: set[tuple[str, str]] = set()
    leagues: dict[str, int] = {}
    teams: dict[str, int] = {}
    card_keys = set(card_keys or ())
    seen_card: set[tuple[str, str]] = set()
    seen_reversed: set[tuple[str, str]] = set()
    card_drops: dict[str, int] = {}
    card_vocabulary: dict[str, int] = {}
    card_priced = 0

    def _refuse(reason: str, ours: bool, bucket: dict[str, int]) -> None:
        bucket[reason] = bucket.get(reason, 0) + 1
        if ours:
            target = card_vocabulary if bucket is _CANONICALIZATION_DROP_REASONS else card_drops
            target[reason] = target.get(reason, 0) + 1

    for row in price_rows:
        if not isinstance(row, dict): continue
        home, away = _sides(row)
        # Overlap is answered BEFORE the well-formedness guard below. The
        # question is "did our fixture appear on this board at all", and a
        # row of ours that is missing a book still answers it yes.
        ours = False
        if card_keys and home and away and team_key is not None:
            pair = (team_key(home), team_key(away))
            if pair in card_keys:
                seen_card.add(pair); ours = True
            elif (pair[1], pair[0]) in card_keys:
                # Our fixture, listed the other way round. Recorded apart so
                # an inverted board cannot be reported as an absent one.
                seen_reversed.add((pair[1], pair[0]))
        book = _text(row.get("sportsbook")) or _text(row.get("sportsbook_ref"))
        raw_market = _text(row.get("market_type")) or _text(row.get("market_ref"))
        if not home or not away or not book or not raw_market: continue
        shaped = True
        # Recorded BEFORE the prematch refusal. A board that was entirely
        # in-play still has to be able to say which competitions were on it:
        # that is the difference between "the filter matched nothing" and
        # "the filter was ignored and we got the whole world".
        fixtures.add((home, away))
        for side in (home, away):
            teams[side] = teams.get(side, 0) + 1
        league_name = _text(row.get("league")) or _text(row.get("league_ref"))
        if league_name:
            leagues[league_name] = leagues.get(league_name, 0) + 1
        if row.get("is_live"):
            _refuse("live_price", ours, _PREMATCH_DROP_REASONS)
            continue
        if row.get("is_stale_pregame_price"):
            _refuse("stale_pregame_price", ours, _PREMATCH_DROP_REASONS)
            continue
        if row.get("is_player_prop"):
            _refuse("player_prop", ours, _PREMATCH_DROP_REASONS)
            continue
        price = _num(row.get("odds_decimal") or row.get("decimal_odds") or row.get("price"))
        if price is None or price <= 1:
            _refuse("no_decimal_price", ours, _PREMATCH_DROP_REASONS)
            continue
        raw_selection = _selection_for(row, home, away)
        canonical, _failure = canonical_market_selection(
            raw_market, raw_selection, home=home, away=away, line=row.get("line"),
        )
        if canonical is None:
            reason = _failure.reason if _failure is not None else "unmappable"
            _refuse(reason, ours, _CANONICALIZATION_DROP_REASONS)
            continue
        if ours:
            card_priced += 1
        rows.append({"source": SOURCE, "date": day, "home": home, "away": away,
                     "kickoff": row.get("event_start_time") or row.get("kickoff"),
                     "market": canonical.market, "selection": canonical.selection,
                     "line": canonical.line, "raw_market": raw_market,
                     "raw_selection": raw_selection, "odds": price, "book": book,
                     "bookmaker": book, "odds_kind": "bookmaker",
                     "league": _text(row.get("league")) or _text(row.get("league_ref")),
                     "event_uuid": _text(row.get("event_uuid")),
                     "named_bookmaker": True, "captured_at": stamp})
    _record_board(fixtures, leagues, teams, priced_rows=len(rows))
    _BOARD_CONTEXT.update({
        "card_fixture_count": len(card_keys),
        "card_fixtures_on_board": len(seen_card),
        "card_fixtures_reversed": len(seen_reversed - seen_card),
        "card_priced_rows": card_priced,
        "card_prematch_drop_reasons": dict(card_drops),
        "card_canonicalization_drop_reasons": dict(card_vocabulary),
    })
    return rows, shaped


def parse_snapshot(payload: Any, *, day: str,
                   card_keys: set[tuple[str, str]] | None = None,
                   team_key: Any = None) -> tuple[list[dict[str, Any]], bool]:
    """Accept only explicit event/bookmaker/market rows; unknown shapes yield no rows."""
    # Reset BEFORE any exit path. An unrecognized payload leaves this
    # function early, and a board count left over from an earlier parse
    # would be worse than no count at all, because it reads as a
    # measurement of this response rather than of the previous one.
    global _CANONICALIZATION_DROP_REASONS, _PREMATCH_DROP_REASONS, _BOARD_CONTEXT
    _CANONICALIZATION_DROP_REASONS = {}
    _PREMATCH_DROP_REASONS = {}
    _BOARD_CONTEXT = {"board_rows": 0, "board_fixtures": 0,
                      "board_league_count": 0, "board_leagues": {},
                      "board_non_prematch_rows": 0, "board_priced_rows": 0,
                      "board_team_count": 0, "board_team_names": {},
                      "card_fixture_count": 0, "card_fixtures_on_board": 0,
                      "card_fixtures_reversed": 0, "card_priced_rows": 0,
                      "card_prematch_drop_reasons": {},
                      "card_canonicalization_drop_reasons": {}}
    records = payload if isinstance(payload, list) else next((payload.get(k) for k in ("events", "data", "matches", "odds") if isinstance(payload, dict) and isinstance(payload.get(k), list)), None)
    if not isinstance(records, list): return [], False
    # A recognized but EMPTY event list is a valid empty result, not a schema
    # failure: conflating the two turns a quiet slate into a false outage (and
    # a real contract break into a false "no games today").
    # Price records, not matches: see parse_flat_rows. board_fixtures
    # carries the distinct-match count for the same board.
    _BOARD_CONTEXT["board_rows"] = len(records)
    if not records:
        return [], True   # recognized board, nothing on it
    if _is_flat(records):
        return parse_flat_rows(records, day=day, card_keys=card_keys,
                               team_key=team_key)
    rows: list[dict[str, Any]] = []; shaped = not records; stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    fixtures: set[tuple[str, str]] = set()
    leagues: dict[str, int] = {}
    teams: dict[str, int] = {}
    for event in records:
        if not isinstance(event, dict): continue
        home = event.get("home") or event.get("home_team"); away = event.get("away") or event.get("away_team")
        if isinstance(home, dict): home = home.get("name")
        if isinstance(away, dict): away = away.get("name")
        books = event.get("bookmakers") or event.get("bookies") or event.get("books")
        if not home or not away or not isinstance(books, list): continue
        shaped = True
        fixtures.add((str(home).strip(), str(away).strip()))
        for side in (str(home).strip(), str(away).strip()):
            teams[side] = teams.get(side, 0) + 1
        league_name = _text(event.get("league")) or _text(event.get("league_ref"))
        if league_name:
            leagues[league_name] = leagues.get(league_name, 0) + 1
        for book in books:
            if not isinstance(book, dict): continue
            bookmaker = str(book.get("name") or book.get("bookmaker") or book.get("title") or "").strip()
            markets = book.get("markets") or book.get("odds") or []
            if not bookmaker or not isinstance(markets, list): continue
            for market in markets:
                if not isinstance(market, dict): continue
                price = _num(market.get("price") or market.get("odds") or market.get("value"))
                if price is None or price <= 1: continue
                raw_market = str(market.get("market") or market.get("name") or "").strip()
                raw_selection = str(market.get("selection") or market.get("label") or "").strip()
                canonical, _failure = canonical_market_selection(
                    raw_market, raw_selection, home=home, away=away,
                    line=market.get("line"),
                )
                if canonical is None:
                    reason = _failure.reason if _failure is not None else "unmappable"
                    _CANONICALIZATION_DROP_REASONS[reason] = (
                        _CANONICALIZATION_DROP_REASONS.get(reason, 0) + 1
                    )
                    continue
                rows.append({"source": SOURCE, "date": day, "home": str(home).strip(), "away": str(away).strip(), "kickoff": event.get("kickoff") or event.get("start_at"), "market": canonical.market, "selection": canonical.selection, "line": canonical.line, "raw_market": raw_market, "raw_selection": raw_selection, "odds": price, "book": bookmaker, "bookmaker": bookmaker, "odds_kind": "bookmaker", "named_bookmaker": True, "captured_at": stamp})
    _record_board(fixtures, leagues, teams, priced_rows=len(rows))
    return rows, shaped

def _status(code: int | None) -> str:
    if code in (401, 403): return "auth"
    if code in (402, 429, 509): return "quota"
    return "unavailable"


def _reason(code: int | None) -> str:
    """Deterministic zero-row reason suffix for the health line."""
    if code == 401: return "http_401_auth"
    if code == 403: return "http_403_auth_plan"
    if code == 429: return "http_429_quota"
    if code in (402, 509): return f"http_{code}_quota"
    if code == 404: return _rapidapi.REASON_UNCONFIRMED
    if code is None: return "transport_error"
    return f"http_{code}_unavailable"

def _requested_limit() -> int | None:
    """Row limit actually present on the request, or None.

    Read back out of the built query rather than from the environment a
    second time. Two readers of one setting is how a deployment value and a
    code default drift apart, and it describes what was SENT rather than
    what was configured - which is the thing the board count is compared
    against.
    """
    try:
        value = int(query_params().get("limit", ""))
    except ValueError:
        return None
    return value if value > 0 else None


def _requested_league() -> str:
    """Competition filter actually present on the request, or empty."""
    return query_params().get("league", "")


def _league_filter_effective(board: dict[str, Any]) -> bool | None:
    """Did the server actually apply the competition filter we asked for?

    Returns True when the board agrees with the request, False when it
    plainly does not, and None when the question cannot be answered from
    what came back. The None cases matter as much as the False one: with no
    competition on the board, or with exactly one that does not match, a
    "not applied" verdict would be a guess. The vendor is known to spell one
    competition two ways in a single response, so a single unmatched name is
    at least as likely to be the other spelling as a rejected filter.

    The configured value is read here and never stored: it arrives from a
    deployment secret and this verdict ends up in a committed artefact.
    """
    requested = _league_token(_requested_league())
    if not requested:
        return None
    observed = [_league_token(name) for name in (board.get("board_leagues") or {})]
    observed = [token for token in observed if token]
    if not observed:
        return None
    if any(token == requested or requested in token or token in requested
           for token in observed):
        return True
    return False if len(observed) >= 2 else None


def _drop_maps_in_scope(stats: dict[str, Any]) -> tuple[dict[str, int], dict[str, int]]:
    """Refusal counts for OUR fixtures when we have a card, else the board's.

    With a card supplied and at least one of our fixtures on the board, the
    diagnosis is about those rows and not about the rest of the world's.
    Falling back to the board-wide counts keeps behaviour unchanged for
    callers that pass no card.
    """
    if int(stats.get("card_fixture_count") or 0) and int(
            stats.get("card_fixtures_on_board") or 0):
        return (dict(stats.get("card_prematch_drop_reasons") or {}),
                dict(stats.get("card_canonicalization_drop_reasons") or {}))
    return dict(_PREMATCH_DROP_REASONS), dict(_CANONICALIZATION_DROP_REASONS)


def _zero_row_reason(stats: dict[str, Any]) -> str:
    """Name which of seven things produced a zero, because they differ.

    An empty slate means come back later. A page that filled with in-play
    games before reaching our fixtures means narrow the request - the
    opposite of waiting. A board of player props means the markets we bet
    were not on it. A competition filter the server ignored means the
    identifier is not one it knows. A filter it honoured onto an empty
    board means that competition had nothing on. An unmappable board means
    the market vocabulary moved. Collapsing these into one zero is what
    kept the 2026-10-06 result unreadable.
    """
    if stats.get("league_filter_requested") and not int(stats.get("board_rows") or 0):
        return "league_filter_returned_empty"
    if stats.get("league_filter_effective") is False:
        return "league_filter_not_applied"
    # Did our fixtures appear AT ALL? On an unfiltered global board this
    # outranks every refusal token, because those tokens describe other
    # people's games. Soccer runs continuously somewhere in the world, so
    # a top-of-board full of in-play rows is background noise rather than
    # a statement about our capture window, and a board of props from
    # another continent is exactly as uninformative. Until the overlap is
    # non-zero, no refusal reason on this board is about us.
    # Only meaningful against a board that returned something. On an empty
    # board our fixtures are trivially absent, and saying so would dress a
    # quiet slate up as a coverage finding and send the operator to narrow
    # a request that returned nothing to narrow.
    # The token names the OBSERVATION - nothing of ours matched - and not a
    # cause. Two causes produce it and they have opposite remedies: the
    # board does not carry our card, or it carries it under names our join
    # key does not fold. That key is an exact match on a compacted string
    # plus a small curated alias table, and this vendor has never been
    # exercised against it, so the naming case is the likelier one on first
    # contact. The recorded team names are what settle it after the run.
    if int(stats.get("card_fixture_count") or 0) and int(stats.get("board_rows") or 0):
        if not int(stats.get("card_fixtures_on_board") or 0):
            return ("card_fixtures_matched_sides_reversed"
                    if int(stats.get("card_fixtures_reversed") or 0)
                    else "card_fixtures_unmatched_on_board")
    prematch, vocabulary = _drop_maps_in_scope(stats)
    if prematch and not vocabulary:
        # READ THIS BEFORE CONCLUDING ANYTHING ABOUT MARKET VOCABULARY.
        # Reaching this branch means the vocabulary map is EMPTY, and that
        # is not evidence our market names match the vendor's. The prematch
        # refusal above runs BEFORE the vocabulary step, so when every row
        # is refused as in-play or as a prop, nothing ever reaches the
        # mapper and it reports no failures for a purely trivial reason.
        # An empty failure map here means "untested", never "agrees".
        truncated = bool(stats.get("board_truncated"))
        live = sum(prematch.get(reason, 0)
                   for reason in _LIVE_LIKE_DROP_REASONS)
        props = prematch.get("player_prop", 0)
        # Timing outranks market selection when both are present. An in-play
        # row is a different quantity that would corrupt a closing-line
        # measurement, so it invalidates the capture window itself; a prop
        # row is merely a market we never bet. Reporting props while live
        # rows are also present would hide the more serious fault.
        if live:
            return ("board_truncated_live_first" if truncated
                    else "all_rows_live_or_stale")
        if props:
            return ("board_truncated_player_props" if truncated
                    else "all_rows_player_props")
        return "all_rows_unpriced"
    if vocabulary:
        return "all_rows_unmappable"
    return "provider_empty_slate"


def _path(day: str, localdata: Path | None = None) -> Path: return (localdata or LOCALDATA) / f"{SOURCE}_shadow_{day}.json"
def capture_day(day: str, *, localdata: Path | None = None,
                card: Any = None, team_key: Any = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stats = {"status":"not_run","sa_raw":0,"sa_matched":0,"requests":0,"http_statuses":[],"http_429":0,"errors":[],"blocker":None,"schema_match":None,"sample_event":None,"budget":MAX_CALLS_PER_RUN,"reason":None,"endpoint":endpoint(),"query_params":sorted(query_params(day)),"canonicalization_dropped":0,"canonicalization_drop_reasons":{},"prematch_dropped":0,"prematch_drop_reasons":{},"board_rows":0,"board_fixtures":0,"board_league_count":0,"board_leagues":{},"board_non_prematch_rows":0,"board_priced_rows":0,"board_team_count":0,"board_team_names":{},"board_truncated":None,"requested_limit":_requested_limit(),"league_filter_requested":bool(_requested_league()),"league_filter_effective":None,"card_fixture_count":0,"card_fixtures_on_board":0,"card_fixtures_reversed":0,"card_priced_rows":0,"card_prematch_drop_reasons":{},"card_canonicalization_drop_reasons":{}}
    reset_state()
    sport = (os.environ.get("SHARPAPI_SPORT") or "").strip()
    if not sport:
        stats.update(
            status="not_run",
            reason="missing_sport_filter",
            blocker="SHARPAPI_SPORT not set; soccer sport filter is required; capture skipped",
        )
        return [], _set_diag(stats)
    # Our own card for the day, folded with the PIPELINE's team key so the
    # overlap number means the same thing as the pipeline's own join. A
    # second, private matcher here would produce a number that looked like
    # coverage and answered a different question.
    card_keys: set[tuple[str, str]] = set()
    if card and team_key is not None:
        for fixture in card:
            try:
                home, away = fixture
            except (TypeError, ValueError):
                continue
            key = (team_key(home), team_key(away))
            if all(key):
                card_keys.add(key)
    stats["card_fixture_count"] = len(card_keys)
    if not _key(): stats["blocker"] = f"{KEY_ENV} not set; shadow capture skipped"; return [], _set_diag(stats)
    try:
        ledger = json.loads(_path(day, localdata).read_text())
        held = ledger.get("rows", [])
        if held:
            # The normalized cache is not the upstream board. Preserve its
            # recorded board receipt; absent receipts are unknown, not zero.
            # Never reuse an earlier card's overlap for today's caller/card.
            captured_stats = ledger.get("stats")
            captured_stats = captured_stats if isinstance(captured_stats, dict) else {}
            for field in SHARPAPI_BOARD_FIELDS:
                stats[field] = None if field.startswith("card_") else captured_stats.get(field)
            stats["card_fixture_count"] = len(card_keys)
            stats.update(status="cache_only", cache_hits=1, sa_raw=len(held),
                         sa_matched=len(held), schema_match=True)
            return held, _set_diag(stats)
    except (OSError, ValueError, TypeError): pass
    try:
        code, payload, headers = get_json(odds_url(day)); stats["requests"] = 1; stats["http_statuses"] = [code]; stats["rate_limit_headers"] = headers
        if code != 200 or payload is None: stats.update(status=_status(code), reason=_reason(code), blocker=f"sharpapi: HTTP {code} or non-JSON payload"); return [], _set_diag(stats)
        rows, shaped = parse_snapshot(payload, day=day, card_keys=card_keys,
                                      team_key=team_key); stats["schema_match"] = shaped
        stats["canonicalization_drop_reasons"] = dict(_CANONICALIZATION_DROP_REASONS)
        stats["canonicalization_dropped"] = sum(_CANONICALIZATION_DROP_REASONS.values())
        stats["prematch_drop_reasons"] = dict(_PREMATCH_DROP_REASONS)
        stats["prematch_dropped"] = sum(_PREMATCH_DROP_REASONS.values())
        # Board context travels with every capture, not only with a zero. A
        # non-zero capture that saw 100 rows of a global board is also worth
        # knowing about, because it says the narrowing has not taken effect.
        stats.update(board_context())
        # board_context() carries this key with a parse-time default, and the
        # legacy nested branch never fills it. The card size is known here
        # regardless of which branch parsed, so it is restated rather than
        # inherited - a zero here would read as "we asked about no fixtures".
        stats["card_fixture_count"] = len(card_keys)
        limit = stats.get("requested_limit")
        stats["board_truncated"] = (
            bool(limit) and int(stats.get("board_rows") or 0) >= int(limit))
        stats["league_filter_effective"] = _league_filter_effective(stats)
        # A recognizable but empty event list is a VALID empty result; only an
        # unrecognizable payload is a contract failure.
        if not shaped: stats.update(status="unavailable", reason="schema_unrecognized", blocker="sharpapi: snapshot schema not recognized; raw sample retained"); stats["sample_event"] = _scrub(str(payload)[:200]); return [], _set_diag(stats)
        stats["sa_raw"] = len({(r["home"], r["away"]) for r in rows}); stats["sa_matched"] = len(rows); stats["status"] = "ok" if rows else "empty"
        if not rows:
            stats["reason"] = _zero_row_reason(stats)
        return rows, _set_diag(stats)
    except UpstreamBlocked as exc:
        msg = _scrub(str(exc)); stats["http_429"] = _429
        import re as _re
        found = _re.search(r"HTTP (\d{3})", msg)
        code = int(found.group(1)) if found else None
        stats["status"] = "cooldown" if _cooling else ("quota" if "budget" in msg or "429" in msg else _status(code))
        stats["reason"] = "run_cooldown" if _cooling else ("budget_reached" if "budget" in msg else _reason(code))
        if code == 404 and not _cooling:
            # Sub-classify from the body so the health line names the fix.
            provider_message = _rapidapi.provider_snippet(msg)
            stats["reason"] = _rapidapi.classify_404(provider_message)
            stats["provider_message"] = provider_message
            stats["operator_action"] = _rapidapi.explain(stats["reason"])
        stats["blocker"] = msg[:180]; stats["errors"] = [msg[:180]]; return [], _set_diag(stats)

def persist_shadow(day: str, rows: list[dict[str, Any]], stats: dict[str, Any], *, localdata: Path | None = None) -> Path:
    root = localdata or LOCALDATA; root.mkdir(parents=True, exist_ok=True); path = _path(day, root)
    payload = {"schema":1,"source":SOURCE,"date":day,"role":"named-book price source (never a vote; same-day freshness required)","provenance":{"api":BASE + endpoint(),"host":API_HOST,"hunt":"docs/operator/SOURCE-HUNT-2026-10.md#sharpapi"},"stats":stats,"rows":rows}
    tmp = path.with_suffix(path.suffix + ".tmp"); tmp.write_text(json.dumps(payload, indent=2, sort_keys=True)); tmp.replace(path); return path
