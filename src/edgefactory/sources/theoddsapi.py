"""theoddsapi adapter — The Odds API (the-odds-api.com) prices for the certified shortlist.

Bootstrap-friendly use of the free tier (~500 credits/month per key):
  * /sports and /events are usage-free; only odds payloads cost credits
    (markets x regions per event request).
  * fetch_day() is shortlist-driven: it targets matches from
    localdata/picks_<date>.json / picks_morning_<date>.json (the frozen
    daily slate) instead of scanning whole leagues.
  * Multi-key rotation: ODDS_API_KEYS=k1,k2,k3. Every request walks a
    daily-rotated ring; a key that auth-fails or runs out of credits
    (401/403/429 or server usage counters) is marked exhausted and the
    next key takes over automatically. Per-key monthly ledger
    (localdata/theoddsapi_usage.json) enforces a hard budget stop below
    each key's free allotment (raw keys are never written to disk —
    only sha256 fingerprints).

Standard adapter contract:
    fetch_day(date: str) -> list[dict]
    COLUMNS = [...]

Rows mirror the bzzoiro_odds schema so enrichment/CLV tooling treats all
odds feeds uniformly:
    source, source_type="odds", sport, date, kickoff, league, home, away,
    market, selection, odds, bookmaker, captured_at

Env (see .env.example):
    ODDS_API_KEYS             comma list of API keys (rotation ring)
    ODDS_API_KEY              single key (fallback if ODDS_API_KEYS unset)
    ODDS_API_REGIONS          default "eu"          (1 region keeps cost at 1x)
    ODDS_API_MARKETS          default "h2h,totals,totals_alt,btts,team_totals,double_chance"
                            (prices the enhancement overlay: ou 1.5/2.5/3.5/4.5, btts,
                             team totals, double chance; each market = +1 credit/event)
    ODDS_API_TOTAL_POINTS     default "1.5,2.5,3.5,4.5"  totals lines to keep
    ODDS_API_MONTHLY_BUDGET   default "480"         hard stop per key, below free 500
    ODDS_API_BOOKMAKERS       optional comma list   (default: all books in region)
    ODDS_API_VERBOSE          "1" for diagnostics
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import contextlib
import urllib.error
import urllib.parse
import urllib.request
from datetime import date as _date
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

try:  # POSIX advisory locking (macOS/Linux/CI); absent on Windows
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

load_dotenv()

try:  # reuse pipeline join keys when importable; fall back to a local copy
    from edgefactory.util import norm_team as _ef_norm_team
except Exception:  # pragma: no cover - standalone use
    _ef_norm_team = None


def _parse_keys() -> tuple[str, ...]:
    raw = os.environ.get("ODDS_API_KEYS") or os.environ.get("ODDS_API_KEY") or ""
    seen, out = set(), []
    for part in raw.split(","):
        key = part.strip()
        if key and key not in seen:
            seen.add(key)
            out.append(key)
    return tuple(out)


API_KEYS = _parse_keys()
TOKEN = API_KEYS[0] if API_KEYS else None  # back-compat single-key view
BASE = os.environ.get("ODDS_API_BASE", "https://api.the-odds-api.com/v4").rstrip("/")

REGIONS = tuple(x.strip() for x in os.environ.get("ODDS_API_REGIONS", "eu").split(",") if x.strip()) or ("eu",)
MARKETS = tuple(x.strip() for x in os.environ.get("ODDS_API_MARKETS", "h2h,totals,totals_alt,btts,team_totals,double_chance").split(",") if x.strip()) or ("h2h",)
TOTAL_POINTS = tuple(x.strip() for x in os.environ.get("ODDS_API_TOTAL_POINTS", "1.5,2.5,3.5,4.5").split(",") if x.strip())
MONTHLY_BUDGET = int(os.environ.get("ODDS_API_MONTHLY_BUDGET", "480") or 480)
BOOKMAKERS = tuple(x.strip() for x in os.environ.get("ODDS_API_BOOKMAKERS", "").split(",") if x.strip())

LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA") or (Path(__file__).resolve().parents[3] / "localdata"))
SPORTS_CACHE_FILE = Path(os.environ.get("THEODDSAPI_SPORTS_CACHE") or (LOCALDATA / "theoddsapi_sports.json"))
USAGE_FILE = Path(os.environ.get("THEODDSAPI_USAGE_FILE") or (LOCALDATA / "theoddsapi_usage.json"))
USAGE_LOCK_FILE = Path(os.environ.get("THEODDSAPI_USAGE_LOCK") or (LOCALDATA / "theoddsapi_usage.lock"))
SPORTS_CACHE_TTL_DAYS = 7

COLUMNS = [
    "source", "source_type", "sport", "date", "kickoff", "league", "home", "away",
    "market", "selection", "odds", "bookmaker", "captured_at",
]

# Manual league-title hints for containment misses (normalized league_raw
# fragment -> The Odds API sport key). Extend as coverage reports accumulate.
# League label -> The Odds API sport key candidates, in preference order.
#
# Values are CHAINS: the first key the provider actually lists wins. Off-season
# swaps matter — UCL qualifiers sit on soccer_uefa_champs_league_qualification
# while the main key is unlisted. The first matching FRAGMENT wins-or-returns
# -None: no fallthrough to other fragments, so a second-tier label can never
# inherit its top tier's sport key (wrong competition is worse than unpriced).
# Fragments are matched against the digit-preserving _league_code form and
# checked longest-first (_ALIAS_FRAGS).
LEAGUE_KEY_ALIASES: dict[str, tuple[str, ...]] = {
    # UEFA — qualifying window: main keys go unlisted, the quals key stays live
    "uefachampionsleague": ("soccer_uefa_champs_league",
                            "soccer_uefa_champs_league_qualification"),
    "uefaeuropaconferenceleague": ("soccer_uefa_europa_conference_league",),
    "uefaeuropaleague": ("soccer_uefa_europa_league",),
    # England
    "englandpremierleague": ("soccer_epl",),
    "englisnpremierleague": ("soccer_epl",),  # historical provider typo, kept
    "englandchampionship": ("soccer_efl_champ",),
    "englandleagueone": ("soccer_england_league1",),
    "englandleague1": ("soccer_england_league1",),
    "englandleaguetwo": ("soccer_england_league2",),
    "englandleague2": ("soccer_england_league2",),
    # Spain / Germany / Italy / France (tier-guard fragments before their prefix)
    "spainlaliga2": ("soccer_spain_segunda_division",),
    "spainlaliga": ("soccer_spain_la_liga",),
    "germanybundesliga2": ("soccer_germany_bundesliga2",),
    "germanybundesliga": ("soccer_germany_bundesliga",),
    "italyseriea": ("soccer_italy_serie_a",),
    "franceligue2": ("soccer_france_ligue_two",),
    "franceligue1": ("soccer_france_ligue_one",),
    # Rest of the covered domestic leagues
    "netherlandseredivisie": ("soccer_netherlands_eredivisie",),
    "swedenallsvenskan": ("soccer_sweden_allsvenskan",),
    "norwayeliteserien": ("soccer_norway_eliteserien",),
    "australiaaleague": ("soccer_australia_aleague",),
    "usamls": ("soccer_usa_mls",),
    "brazilserieb": ("soccer_brazil_serie_b",),
    "brazilseriea": ("soccer_brazil_campeonato",),
    "brazilcampeonato": ("soccer_brazil_campeonato",),
    # tightened: bare "argentinaprimera" mislabelled Primera B Metropolitana
    "argentinaprimeradivisin": ("soccer_argentina_primera_division",),
    "denmarksuperliga": ("soccer_denmark_superliga",),
    "belgiumfirstdiv": ("soccer_belgium_first_div",),
    "austriabundesliga": ("soccer_austria_bundesliga",),
    "greecesuperleague": ("soccer_greece_super_league",),
    "polandekstraklasa": ("soccer_poland_ekstraklasa",),
    "turkeysuperlig": ("soccer_turkey_super_league",),
    "mexicoligamx": ("soccer_mexico_ligamx",),
    # Evidence-backed additions (labels observed in the picks archives)
    "scotlandpremiership": ("soccer_spl",),
    "chileprimeradivisin": ("soccer_chile_campeonato",),
    "czechliga": ("soccer_czech_liga",),
}

# Exact-match provider short codes, matched before any fragment logic on the
# digit-preserving _league_code form (the code carries the tier: "Se2" is
# Superettan, "Se4" is Division 2 — stripping digits would collapse them).
SHORT_LEAGUE_KEYS: dict[str, tuple[str, ...]] = {
    "ucl": ("soccer_uefa_champs_league", "soccer_uefa_champs_league_qualification"),
    "uel": ("soccer_uefa_europa_league",),
    "ecl": ("soccer_uefa_europa_conference_league",),
    "fi1": ("soccer_finland_veikkausliiga",),
    "se2": ("soccer_sweden_superettan",),
    "ie1": ("soccer_league_of_ireland",),
}


def _league_code(raw: object) -> str:
    """Digit-preserving normalization — the competition tier lives in the digit
    ("Se2"=Superettan / "Se4"=Division 2; "La Liga 2" != "La Liga"). Fragment
    and containment matching both run on this form, so a second-tier label can
    never collapse onto its top tier's sport key."""
    return re.sub(r"[^a-z0-9]", "", str(raw or "").lower())


def _first_listed(keys: tuple[str, ...], sports: list[dict]) -> str | None:
    """First chain link the provider currently lists.

    With an empty sports list (no cache to verify against) the chain head is
    trusted — same contract the aliases had before. An empty chain is a
    deliberate dead-end and returns None.
    """
    for key in keys:
        if any(s.get("key") == key for s in sports):
            return key
    return keys[0] if keys and not sports else None


# Fragments checked longest-first: tier-guards ("germanybundesliga2") must win
# over their prefixes ("germanybundesliga"). Deterministic within equal length.
_ALIAS_FRAGS = sorted(LEAGUE_KEY_ALIASES.items(), key=lambda kv: (-len(kv[0]), kv[0]))


class KeysExhausted(Exception):
    """Raised when every key in the rotation ring fails or is out of budget."""


def _verbose() -> bool:
    return os.environ.get("ODDS_API_VERBOSE", "").strip().lower() in {"1", "true", "yes", "on"}


def _log(message: str, *, always: bool = False) -> None:
    if always or _verbose():
        print(f"theoddsapi: {message}", file=sys.stderr)


def _norm_team(name: object) -> str:
    if _ef_norm_team is not None:
        try:
            return _ef_norm_team(str(name or ""))
        except Exception:
            pass
    return re.sub(r"[^a-z]", "", str(name or "").lower())[:9]


def _norm_full(name: object) -> str:
    return re.sub(r"[^a-z]", "", str(name or "").lower())


def enabled() -> bool:
    return bool(API_KEYS)


def cost_per_event() -> int:
    """Credit estimate per event odds fetch: markets x regions."""
    return max(1, len(MARKETS)) * max(1, len(REGIONS))


def total_monthly_budget() -> int:
    return MONTHLY_BUDGET * max(1, len(API_KEYS))


# ---------------------------------------------------------------- key ledger
# v2: usage is tracked per key fingerprint (sha256(key)[:12]); raw keys are
# never persisted. v1 flat ledgers are folded into the first key on write.


def _key_fp(key: str) -> str:
    return "k_" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def _key_slot(ledger: dict, fp: str) -> dict:
    keys = ledger.setdefault("keys", {})
    slot = keys.setdefault(fp, {})
    slot.setdefault("months", {})
    slot.setdefault("last_server_used", None)
    slot.setdefault("last_server_remaining", None)
    slot.setdefault("exhausted", False)
    slot.setdefault("exhausted_reason", None)
    slot.setdefault("exhausted_at", None)
    return slot


def load_usage() -> dict:
    try:
        if USAGE_FILE.exists():
            data = json.loads(USAGE_FILE.read_text())
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {"version": 2, "keys": {}}


@contextlib.contextmanager
def _usage_lock():
    """Serialize ledger read-modify-write across overlapping runs.

    3h cron jitter can overlap two pipeline iterations; a torn or clobbered
    ledger used to silently lose credit accounting (red-team 2026-08-03:
    quota-leak race). flock is advisory — only processes using this helper
    cooperate, which is exactly the pipeline's own writers. Lock failure is
    never fatal: the atomic replace below still prevents corrupted JSON."""
    if fcntl is None:
        yield
        return
    fh = None
    try:
        USAGE_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        fh = open(USAGE_LOCK_FILE, "a")
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
    except OSError:
        pass
    try:
        yield
    finally:
        if fh is not None:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            fh.close()


def _atomic_write_json(path: Path, data: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True))
    os.replace(tmp, path)  # atomic on POSIX: readers never see torn files


def save_usage(ledger: dict, *, _locked: bool = False) -> None:
    """Persist the usage ledger. Callers that already hold _usage_lock() pass
    _locked=True (flock is not re-entrant across fds)."""
    def _write() -> None:
        with _usage_lock() if not _locked else contextlib.nullcontext():
            ledger["version"] = 2
            # v1 migration: fold top-level flat stats into the first key's slot
            flat_months = ledger.pop("months", None)
            flat_used = ledger.pop("last_server_used", None)
            flat_remaining = ledger.pop("last_server_remaining", None)
            if (flat_months or flat_used is not None) and API_KEYS:
                slot = _key_slot(ledger, _key_fp(API_KEYS[0]))
                for ym, stats in (flat_months or {}).items():
                    m = slot["months"].setdefault(ym, {"credits": 0, "requests": 0})
                    m["credits"] = int(m.get("credits", 0)) + int(stats.get("credits", 0))
                    m["requests"] = int(m.get("requests", 0)) + int(stats.get("requests", 0))
                if flat_used is not None and slot["last_server_used"] is None:
                    slot["last_server_used"] = flat_used
                    slot["last_server_remaining"] = flat_remaining
            USAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write_json(USAGE_FILE, ledger)

    try:
        _write()
    except Exception as exc:  # ledger failure must never break capture
        _log(f"usage ledger write failed: {exc}", always=True)


def _month_key(day: str | None = None) -> str:
    return (day or _date.today().isoformat())[:7]


def _budget_ok(need: int, fp: str, *, day: str | None = None) -> bool:
    ledger = load_usage()
    slot = ledger.get("keys", {}).get(fp, {})
    if slot.get("exhausted"):
        return False
    remaining = slot.get("last_server_remaining")
    if remaining is not None:
        try:
            if int(remaining) - need < 0:
                return False
        except (TypeError, ValueError):
            pass
    month = slot.get("months", {}).get(_month_key(day), {})
    return int(month.get("credits", 0)) + need <= MONTHLY_BUDGET


def _record_charge(need: int, fp: str, headers: dict, *, day: str | None = None) -> None:
    with _usage_lock():  # hold across the whole read-modify-write
        ledger = load_usage()
        slot = _key_slot(ledger, fp)
        month = slot["months"].setdefault(_month_key(day), {"credits": 0, "requests": 0})
        month["credits"] = int(month.get("credits", 0)) + need
        month["requests"] = int(month.get("requests", 0)) + 1
        used, remaining = headers.get("x-requests-used"), headers.get("x-requests-remaining")
        try:
            if used is not None:
                slot["last_server_used"] = int(used)
            if remaining is not None:
                slot["last_server_remaining"] = int(remaining)
                if int(remaining) <= 0:
                    _mark_exhausted(fp, "server usage depleted", ledger=ledger, slot=slot)
        except (TypeError, ValueError):
            pass
        save_usage(ledger, _locked=True)


def _mark_exhausted(fp: str, reason: str, *, ledger: dict | None = None, slot: dict | None = None) -> None:
    own = ledger is None
    if own:
        with _usage_lock():
            ledger = load_usage()
            slot = _key_slot(ledger, fp)
            slot["exhausted"] = True
            slot["exhausted_reason"] = reason
            slot["exhausted_at"] = datetime.now(timezone.utc).isoformat()
            save_usage(ledger, _locked=True)
    else:
        slot["exhausted"] = True
        slot["exhausted_reason"] = reason
        slot["exhausted_at"] = datetime.now(timezone.utc).isoformat()
    _log(f"key {fp} exhausted: {reason}", always=True)


def unmark_exhausted() -> None:
    """Manual reset (new billing month / replaced key)."""
    with _usage_lock():
        ledger = load_usage()
        for slot in ledger.get("keys", {}).values():
            slot["exhausted"] = False
            slot["exhausted_reason"] = None
            slot["exhausted_at"] = None
        save_usage(ledger, _locked=True)


def _key_ring() -> list[str]:
    """Daily-rotated ring: start offset follows the date so wear spreads."""
    if not API_KEYS:
        return []
    offset = _date.today().toordinal() % len(API_KEYS)
    return list(API_KEYS[offset:]) + list(API_KEYS[:offset])


def _active_key(day: str | None = None) -> str | None:
    """First ring key that is not exhausted and still has local budget."""
    ledger = load_usage()
    for key in _key_ring():
        fp = _key_fp(key)
        slot = ledger.get("keys", {}).get(fp, {})
        if slot.get("exhausted"):
            continue
        if not _budget_ok(1, fp, day=day):
            continue
        return key
    return None


def ledger_status() -> dict:
    ledger = load_usage()
    ym = _month_key()
    keys = []
    for key in _key_ring():
        fp = _key_fp(key)
        slot = ledger.get("keys", {}).get(fp, {})
        month = slot.get("months", {}).get(ym, {})
        keys.append({
            "fp": fp,
            "credits_local": int(month.get("credits", 0)),
            "budget": MONTHLY_BUDGET,
            "server_used": slot.get("last_server_used"),
            "server_remaining": slot.get("last_server_remaining"),
            "exhausted": bool(slot.get("exhausted")),
        })
    return {
        "month": ym,
        "keys": keys,
        "n_keys": len(API_KEYS),
        "credits_local": sum(k["credits_local"] for k in keys),
        "budget": total_monthly_budget(),
        "cost_per_event": cost_per_event(),
        "server_remaining": next(
            (k["server_remaining"] for k in keys if not k["exhausted"] and k["server_remaining"] is not None),
            None,
        ),
    }


# ---------------------------------------------------------------- http


def _get_key(key: str, path: str, params: dict):
    """Single-key request. Raises urllib errors upward for rotation handling."""
    qs = urllib.parse.urlencode({**params, "apiKey": key})
    url = f"{BASE}{path}?{qs}"
    last: Exception | None = None
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                return json.loads(resp.read().decode("utf-8", "replace")), headers
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403, 429, 422):
                raise
            last = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
        except Exception as exc:  # noqa: BLE001 - dependency-free helper
            last = exc
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    if last is not None:
        raise last
    raise KeysExhausted("unreachable")


def _get_json(path: str, params: dict, *, cost: int = 0, day: str | None = None):
    """Rotation-aware request. Free endpoints (cost=0) use the first live key;
    costed endpoints pre-check budget per key and charge after success.

    Returns (data, key_fingerprint). Raises KeysExhausted when the whole ring
    is spent/dead; re-raises network errors after all keys fail.
    """
    last: Exception | None = None
    for key in _key_ring():
        fp = _key_fp(key)
        ledger = load_usage()
        slot = ledger.get("keys", {}).get(fp, {})
        if slot.get("exhausted"):
            continue
        if cost and not _budget_ok(cost, fp, day=day):
            _log(f"budget stop for {fp}: need={cost}", always=True)
            continue
        try:
            data, headers = _get_key(key, path, params)
        except urllib.error.HTTPError as exc:
            if exc.code == 401:
                body = ""
                try:
                    body = exc.read().decode("utf-8", "replace").lower()
                except Exception:
                    pass
                reason = "usage credits depleted" if "usage" in body or "credit" in body else "http 401 (auth)"
                _mark_exhausted(fp, reason)
                last = exc
                continue
            if exc.code in (403, 429):
                _mark_exhausted(fp, f"http {exc.code}")
                last = exc
                continue
            if exc.code == 422:
                # Plan-level rejection (premium market or sport not on this
                # key's plan) — NOT key exhaustion, and failed calls are
                # never charged. Record the failure and move on without
                # permanently killing the ring.
                _log(f"{fp}: http 422 (market/sport not on plan) — skipping request", always=True)
                last = exc
                break
            last = exc
            break
        except Exception as exc:  # network/parse: not a key problem
            last = exc
            break
        if cost:
            _record_charge(cost, fp, headers, day=day)
        else:  # still learn server counters from free calls when provided
            used, remaining = headers.get("x-requests-used"), headers.get("x-requests-remaining")
            if used is not None or remaining is not None:
                _record_charge(0, fp, headers, day=day)
        return data, fp
    if last is not None and not any(
        not load_usage().get("keys", {}).get(_key_fp(k), {}).get("exhausted") for k in _key_ring()
    ):
        raise KeysExhausted(str(last))
    if last is not None:
        raise last
    raise KeysExhausted("no usable API keys")


# ---------------------------------------------------------------- sports map


def load_sports(*, refresh: bool = False) -> list[dict]:
    """Soccer sport keys, cached locally (free endpoint, but no need to re-pull)."""
    if not refresh and SPORTS_CACHE_FILE.exists():
        try:
            data = json.loads(SPORTS_CACHE_FILE.read_text())
            fetched = datetime.fromisoformat(str(data.get("fetched_at", "")).replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - fetched
            if age.days < SPORTS_CACHE_TTL_DAYS and isinstance(data.get("sports"), list):
                return data["sports"]
        except Exception:
            pass
    data, _fp = _get_json("/sports/", {})
    sports = [s for s in (data or []) if isinstance(s, dict)]
    soccer = [s for s in sports if str(s.get("group", "")).lower() == "soccer"]
    try:
        SPORTS_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SPORTS_CACHE_FILE.write_text(json.dumps({
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "sports": soccer,
        }, indent=2))
    except Exception as exc:
        _log(f"sports cache write failed: {exc}", always=True)
    return soccer


def sport_key_for_league(league_raw: object, sports: list[dict]) -> str | None:
    """Resolve a pick's league name to a The Odds API sport key.

    Returns None when the league is not covered — caller reports the miss.
    Resolution contract, strictest stage first — and None is always preferred
    over a wrong-competition key:

      1. exact provider short code ("ECL", "Fi1"; digits preserved: the code
         carries the tier, so "Se2" -> Superettan can never become Allsvenskan);
      2. first matching alias fragment wins-or-returns-None (no fallthrough,
         so a second-tier label never inherits its top tier's sport key);
      3. containment fallback only on REAL overlap — >= 8 chars and at least
         half the longer string, otherwise a bare "league" token (digits
         stripped from "League 2") junk-matches every "...League" label and
         fabricates wrong-competition prices (2026-08-06 incident: 13 archived
         labels, incl. all UEFA comps, resolved to soccer_england_league2).

    Stages 2 and 3 match on _league_code (digits preserved), so "K League 2"
    can never inherit soccer_korea_kleague1 and "Japan J2 League" can never
    inherit soccer_japan_j_league.
    """
    if not str(league_raw or "").strip():
        return None
    code = _league_code(league_raw)
    if code in SHORT_LEAGUE_KEYS:
        return _first_listed(SHORT_LEAGUE_KEYS[code], sports)
    if len(code) < 4:
        # too short to match safely ("ie2" -> "ie" would false-hit "premiership")
        return None
    for frag, keys in _ALIAS_FRAGS:
        if frag in code:
            return _first_listed(keys, sports)  # wins-or-None; never falls through
    candidates = []
    for s in sports:
        if not s.get("active", True):
            continue
        title_code = _league_code(s.get("title"))
        key_code = _league_code(str(s.get("key", "")).replace("soccer_", "").replace("_", ""))
        for cand in (title_code, key_code):
            overlap = min(len(cand), len(code))
            if (overlap >= 8 and overlap * 2 >= max(len(cand), len(code))
                    and (cand in code or code in cand)):
                candidates.append((overlap, str(s.get("key"))))
                break
    if candidates:
        candidates.sort(key=lambda t: (-t[0], t[1]))  # longest overlap, then name
        return candidates[0][1]
    return None


# ---------------------------------------------------------------- shortlist


def _shortlist_file(date: str) -> Path | None:
    for name in (f"picks_{date}.json", f"picks_morning_{date}.json"):
        path = LOCALDATA / name
        if path.exists():
            return path
    return None


def shortlist(date: str) -> list[dict]:
    """Unique fixtures from the frozen daily picks archive (quota shield).

    Empty when no frozen slate exists for `date` — fetch_day then returns []
    without spending a single credit.
    """
    path = _shortlist_file(date)
    if path is None:
        _log(f"no picks archive for {date}; shortlist empty")
        return []
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        _log(f"cannot parse {path.name}: {exc}", always=True)
        return []
    picks = data if isinstance(data, list) else data.get("picks", []) if isinstance(data, dict) else []
    fixtures: dict[tuple, dict] = {}
    for p in picks:
        if not isinstance(p, dict):
            continue
        home, away = p.get("home"), p.get("away")
        if not home or not away:
            continue
        ctx = p.get("ctx") if isinstance(p.get("ctx"), dict) else {}
        key = (str(home), str(away))
        fixtures.setdefault(key, {
            "date": p.get("date") or date,
            "kickoff": p.get("kickoff"),
            "league": ctx.get("league_raw") or p.get("league") or "",
            "home": home,
            "away": away,
        })
    return list(fixtures.values())


# ---------------------------------------------------------------- matching


# Club-affix tokens dropped before subset comparison (prefix/suffix junk like
# IK Sirius vs Sirius, Halmstads BK vs Halmstad). Scoped to token sets only.
_TEAM_NOISE = {
    "fc", "cf", "sc", "ac", "cd", "ca", "as", "rc", "ud", "sv", "bk", "ik",
    "sk", "fk", "if", "ifk", "aik", "gif", "bif", "afc", "ssc", "vfl", "vfb",
    "tsg", "club", "deportivo", "atletico", "athletic", "sporting",
    "u17", "u18", "u19", "u20", "u21", "u23", "ii", "w", "women",
    "reserve", "reserves", "res",
}


def _team_tokens(name: object) -> set[str]:
    words = re.sub(r"[^a-z ]", "", str(name or "").lower()).split()
    return {w for w in words if w not in _TEAM_NOISE and len(w) > 1}


def _pick_kickoff_utc(pick: dict) -> datetime | None:
    raw = str(pick.get("kickoff") or "").strip()
    m = re.match(r"(\d{1,2})-(\d{1,2}),\s*(\d{1,2}):(\d{2})", raw)
    if not m:
        return None
    dd, mm, hh, mi = (int(x) for x in m.groups())
    # Year comes from the fixture's own pipeline date, NEVER from wall-clock:
    # a Dec-31 run on a Jan-01 slate must not regress the fixture a full year
    # (red-team 2026-08-03: year-boundary bug -> wrong-year month/day matches).
    date_str = str(pick.get("date") or "")[:10]
    try:
        year = int(date_str[:4])
    except (TypeError, ValueError):
        year = datetime.now(timezone.utc).year
    try:
        # pick kickoffs are pipeline-local (Africa/Johannesburg, UTC+2, no DST)
        return datetime(year, mm, dd, hh, mi, tzinfo=timezone.utc) - timedelta(hours=2)
    except ValueError:
        return None


def _team_names_match(a: object, b: object) -> bool:
    """Cross-feed team-name equivalence: exact/9-char keys, prefix containment,
    or significant-token subset (affix drops like IK Sirius vs Sirius)."""
    a_full, b_full = _norm_full(a), _norm_full(b)
    if not a_full or not b_full:
        return False
    if a_full == b_full:
        return True
    a9, b9 = _norm_team(a), _norm_team(b)
    if a9 and b9 and a9 == b9:
        return True
    shorter, longer = sorted((a_full, b_full), key=len)
    if len(shorter) >= 5 and longer.startswith(shorter):
        return True
    a_tok = _team_tokens(a)
    b_tok = _team_tokens(b)
    if a_tok and b_tok:
        shared = a_tok & b_tok
        if shared and (shared == a_tok or shared == b_tok):
            return sum(len(w) for w in shared) >= 5
    return False


def match_event(pick: dict, events: list[dict]) -> dict | None:
    """Find the API event for a pick fixture. Pair-constrained matching:
    home must match home AND away match away; kickoff breaks ties."""
    kickoff = _pick_kickoff_utc(pick)

    def event_dt(ev: dict) -> datetime | None:
        try:
            return datetime.fromisoformat(str(ev.get("commence_time", "")).replace("Z", "+00:00"))
        except ValueError:
            return None

    scored = []
    for ev in events:
        if not _team_names_match(pick.get("home"), ev.get("home_team")):
            continue
        if not _team_names_match(pick.get("away"), ev.get("away_team")):
            continue
        dt = event_dt(ev)
        delta = abs((dt - kickoff).total_seconds()) if (dt and kickoff) else 86_400
        if kickoff and dt and delta > 14 * 3600:  # wrong day entirely
            continue
        scored.append((delta, ev))
    if not scored:
        return None
    scored.sort(key=lambda x: x[0])
    return scored[0][1]


# ---------------------------------------------------------------- odds parse


def fetch_event_odds(sport_key: str, event_id: str, *, day: str | None = None) -> dict:
    """Per-event odds. Costs markets x regions credits (charged after success,
    with per-key budget pre-check and automatic key rotation)."""
    params = {
        "regions": ",".join(REGIONS),
        "markets": ",".join(MARKETS),
        "oddsFormat": "decimal",
        "dateFormat": "iso",
    }
    if BOOKMAKERS:
        params["bookmakers"] = ",".join(BOOKMAKERS)
    data, _fp = _get_json(f"/sports/{sport_key}/events/{event_id}/odds/", params,
                          cost=cost_per_event(), day=day)
    return data if isinstance(data, dict) else {}


def _h2h_selection(outcome_name: object, home: object, away: object) -> str | None:
    n = _norm_full(outcome_name)
    if n in {"draw", "tie", "x"}:
        return "draw"
    if n and n == _norm_full(home):
        return "home"
    if n and n == _norm_full(away):
        return "away"
    return None


def _market_row(base: dict, market: str, selection: str, odds: object, bookmaker: str) -> dict | None:
    try:
        price = float(odds)
    except (TypeError, ValueError):
        return None
    if not (1.0 < price < 1000.0):
        return None
    return {**base, "market": market, "selection": selection, "odds": price,
            "bookmaker": bookmaker}


def rows_from_event_odds(pick: dict, event: dict, payload: dict) -> list[dict]:
    """Flatten bookmakers -> markets -> outcomes into COLUMNS-shaped rows."""
    home = event.get("home_team") or pick.get("home")
    away = event.get("away_team") or pick.get("away")
    base = {
        "source": "theoddsapi",
        "source_type": "odds",
        "sport": "soccer",
        "date": pick.get("date"),
        "kickoff": event.get("commence_time") or pick.get("kickoff"),
        "league": pick.get("league") or payload.get("sport_title") or "",
        "home": home,
        "away": away,
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    rows: list[dict] = []
    for book in payload.get("bookmakers", []) or []:
        if not isinstance(book, dict):
            continue
        bname = book.get("title") or book.get("key") or "unknown"
        for market in book.get("markets", []) or []:
            if not isinstance(market, dict):
                continue
            mkey = str(market.get("key") or "")
            for oc in market.get("outcomes", []) or []:
                if not isinstance(oc, dict):
                    continue
                if mkey == "h2h":
                    sel = _h2h_selection(oc.get("name"), home, away)
                    if sel:
                        row = _market_row(base, "1x2", sel, oc.get("price"), bname)
                        if row:
                            rows.append(row)
                elif mkey in ("totals", "totals_alt"):
                    point = oc.get("point")
                    try:
                        pstr = f"{float(point):g}"
                    except (TypeError, ValueError):
                        continue
                    if TOTAL_POINTS and pstr not in TOTAL_POINTS:
                        continue
                    sel = str(oc.get("name") or "").strip().lower()
                    if sel in {"over", "under"}:
                        row = _market_row(base, f"ou_{pstr}", sel, oc.get("price"), bname)
                        if row:
                            rows.append(row)
                elif mkey == "team_totals":
                    # outcome name like "Halmstads BK Over 1.5" (or point field set)
                    name = str(oc.get("name") or "")
                    point = oc.get("point")
                    if point is None:
                        m = re.search(r"(?i)\b(over|under)\s+([0-9]+(?:\.[0-9]+)?)\s*$", name)
                        if not m:
                            continue
                        sel = m.group(1).lower()
                        try:
                            pstr = f"{float(m.group(2)):g}"
                        except ValueError:
                            continue
                        team_part = name[:m.start()].strip()
                    else:
                        try:
                            pstr = f"{float(point):g}"
                        except (TypeError, ValueError):
                            continue
                        m2 = re.search(r"(?i)\b(over|under)\b", name)
                        sel = m2.group(1).lower() if m2 else None
                        if sel not in ("over", "under"):
                            continue
                        team_part = name[:m2.start()].strip()
                    if TOTAL_POINTS and pstr not in TOTAL_POINTS:
                        continue
                    n = _norm_full(team_part)
                    if not n:
                        continue
                    if n == _norm_full(home):
                        tside = "home"
                    elif n == _norm_full(away):
                        tside = "away"
                    else:
                        continue
                    row = _market_row(base, f"tt_{tside}_{pstr}", sel, oc.get("price"), bname)
                    if row:
                        rows.append(row)
                elif mkey == "double_chance":
                    dc = {"homeordraw": "1x", "awayordraw": "x2", "homeoraway": "12"}
                    sel = dc.get(str(oc.get("name") or "").strip().lower().replace(" ", ""))
                    if sel:
                        row = _market_row(base, "dc", sel, oc.get("price"), bname)
                        if row:
                            rows.append(row)
                elif mkey == "btts":
                    sel = str(oc.get("name") or "").strip().lower()
                    if sel in {"yes", "no"}:
                        row = _market_row(base, "btts", sel, oc.get("price"), bname)
                        if row:
                            rows.append(row)
    return rows


# ---------------------------------------------------------------- fetch core


def fetch_events(sport_key: str) -> list[dict]:
    """Upcoming events for a sport key. Usage cost: 0 credits."""
    data, _fp = _get_json(f"/sports/{sport_key}/events/", {"dateFormat": "iso"})
    return [e for e in (data or []) if isinstance(e, dict)]


def fetch_fixtures(fixtures: list[dict], *, day: str | None = None) -> tuple[list[dict], list[str], int]:
    """Fetch prices for an explicit fixture list. Never raises.

    Shortlist contract still protects quota: callers pass the frozen-slate
    fixtures only (see shortlist()). Returns (rows, unmatched_lines, matched)."""
    if not API_KEYS:
        _log("no ODDS_API_KEYS configured; 0 rows", always=True)
        return [], [], 0
    if not fixtures:
        return [], [], 0
    sports = load_sports()  # free; raises if the whole ring is dead
    if any(sport_key_for_league(f.get("league"), sports) is None for f in fixtures):
        # comp availability swaps at season boundaries (UCL quals key appears,
        # UECL returns in-season) faster than the 7-day sports cache rolls;
        # one free refresh re-resolves stale misses. Never fatal, never priced.
        try:
            fresh = load_sports(refresh=True)
            if fresh:
                sports = fresh
        except Exception as exc:
            _log(f"sports refresh skipped (using cache): {exc}")

    groups: dict[str, list[dict]] = {}
    unmatched: list[str] = []
    for f in fixtures:
        key = sport_key_for_league(f.get("league"), sports)
        if key:
            groups.setdefault(key, []).append(f)
        else:
            unmatched.append(f"{f.get('home')} vs {f.get('away')} (league not covered: {f.get('league')})")

    rows: list[dict] = []
    matched = 0
    for key, picks in groups.items():
        try:
            events = fetch_events(key)
        except KeysExhausted as exc:
            _log(f"all keys exhausted during events fetch: {exc}", always=True)
            unmatched.extend(f"{p.get('home')} vs {p.get('away')} (keys exhausted)" for p in picks)
            break
        except Exception as exc:
            _log(f"events fetch failed for {key}: {exc}", always=True)
            unmatched.extend(f"{p.get('home')} vs {p.get('away')} (events error)" for p in picks)
            continue
        for p in picks:
            ev = match_event(p, events)
            if not ev:
                unmatched.append(f"{p.get('home')} vs {p.get('away')} (no event in {key})")
                continue
            try:
                payload = fetch_event_odds(key, str(ev.get("id")), day=day or p.get("date"))
            except KeysExhausted as exc:
                _log(f"ring exhausted mid-run: {exc}", always=True)
                unmatched.append(f"{p.get('home')} vs {p.get('away')} (budget/keys exhausted)")
                break
            except Exception as exc:
                _log(f"odds fetch failed for event {ev.get('id')}: {exc}", always=True)
                unmatched.append(f"{p.get('home')} vs {p.get('away')} (odds error)")
                continue
            new_rows = rows_from_event_odds(p, ev, payload)
            if not new_rows:
                unmatched.append(f"{p.get('home')} vs {p.get('away')} (0 markets returned)")
            else:
                matched += 1
            rows.extend(new_rows)

    out: dict[tuple, dict] = {}
    for r in rows:
        k = (r.get("date"), r.get("home"), r.get("away"), r.get("market"),
             r.get("selection"), r.get("bookmaker"))
        out[k] = r  # within one snapshot, last update wins
    status = ledger_status()
    _log(
        f"fetch_fixtures {day or ''}: fixtures={len(fixtures)} matched={matched} "
        f"rows={len(out)} credits_used_month={status['credits_local']}/{status['budget']} "
        f"keys_live={sum(1 for k in status['keys'] if not k['exhausted'])}/{status['n_keys']}",
        always=True,
    )
    if unmatched:
        _log(f"unmatched: {'; '.join(unmatched)}", always=True)
    return list(out.values()), unmatched, matched


def fetch_day(date: str) -> list[dict]:
    """Fetch prices for the frozen shortlist of `date`. Never raises.

    Credit discipline:
      - no picks archive for the date -> 0 rows, 0 credits
      - league not covered by the API -> reported unmatched, 0 credits
      - monthly budget exhausted on every key -> stops, keeps rows captured
    """
    fixtures = shortlist(date)
    if not fixtures:
        return []
    try:
        rows, _unmatched, _matched = fetch_fixtures(fixtures, day=date)
    except Exception as exc:
        _log(f"fetch_day {date} failed: {exc}", always=True)
        return []
    return rows


def fetch_today_tomorrow() -> list[dict]:
    today = _date.today().isoformat()
    tomorrow = (_date.today() + timedelta(days=1)).isoformat()
    return fetch_day(today) + fetch_day(tomorrow)
