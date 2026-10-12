"""Enhancement certification registry — SHADOW -> PAPER -> ELIGIBLE -> BENCHED.

Each enhancement market type (versioned "<type>@v1") lives in exactly one state:

    SHADOW    known but unpriced/untested — never presented as a recommendation
    PAPER     real-priced outcomes accumulating from settled picks (paper trades)
    ELIGIBLE  Wilson LB95 hit-rate >= mean breakeven of the prices actually paid
              (i.e. clears real prices with statistical margin) on n >= MIN_PRICED_N;
              only ELIGIBLE types may be presented as recommendations
    BENCHED   was ELIGIBLE, then rolling BENCH_WINDOW_DAYS evidence turned
              unprofitable (circuit breaker — mirrors the decay monitor). There is
              NO automatic re-entry (RT-5): a benched market returns to PAPER only
              by an explicit operator reset after a fresh re-validation review.

Unpriced outcomes NEVER advance certification: probability without price is not
evidence of value (the 2026-08-03 audit lesson).

State persists in localdata/enhancement_registry.json (git-tracked so it rides the
persist-to-git loop). Writes hold a POSIX advisory flock across the full
read-modify-write and land via tmp + os.replace (the quota-ledger race lesson).
The flock is placed on a STABLE sidecar file (enhancement_registry.lock), never on
the json itself: flock is per-inode, and os.replace swaps the json's inode on every
write — locking the data file silently loses mutual exclusion the instant a write
lands (measured: only 8-15/40 concurrent records survived before this fix).
All public functions are fail-soft: audit/picks paths must never crash on registry.
"""
from __future__ import annotations

import json
import math
import os
import tempfile
import time
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

REGISTRY_FILENAME = "enhancement_registry.json"
REGISTRY_VERSION = "v1"
MIN_PRICED_N = 30
# Governance N5 (Addendum 27.11, 2026-08-05): PAPER->ELIGIBLE additionally
# requires this fraction of the priced outcomes to have been priced by
# >=2 DISTINCT sources (multi-source verification). Single-source prices
# still accrue toward n and the Wilson math (per Addendum 27.7) but cannot
# certify a market to the staking level. ceil(n * frac) at n=30 -> 8.
MIN_MULTI_SOURCE_FRAC = 0.25
WILSON_Z = 1.959963984540054
BENCH_WINDOW_DAYS = 60
BENCH_MIN_N = 20
MAX_RECORDS_PER_MARKET = 400
MAX_PROCESSED_KEYS = 1600


# ---------------------------------------------------------------------------
# Minimum acceptable price per enhancement market — "the floor".
#
# Operator ruling 2026-10-12, verbatim: "betting on ev will lead us to not bet
# at all, we have the track record of enhanced, we know what wins more, we just
# need prices above a certain threshold, like how autobets does it."
#
# There is deliberately NO EV veto anywhere on this path. The row's
# ``enhancement_breakeven`` and ``enhancement_edge_sample`` stay attached as
# INFORMATION ONLY and gate nothing.
#
# Each floor is the market's break-even price (1 / settled hit-rate) plus a
# margin, read off the settled registry on 2026-10-12:
#
#   market            n   hits   rate   breakeven   floor   profit(u)
#   match_over_25   350    231  66.0%     1.515      1.60    +2.297
#   match_over_15    33     24  72.7%     1.375      1.45    -5.780
#   match_over_35    16      5  31.2%     3.200      3.30    -2.200
#   btts_yes          7      4  57.1%     1.750      1.85    +1.990
#
# These are plain numeric literals (repo convention: daily.yml keeps its caps as
# literal '90' / '20') and they are a STARTING POINT to be re-derived from the
# settled slices, not gospel — match_over_15 clears its break-even on hit rate
# alone while being NEGATIVE in profit, which is exactly why the floor is
# per-market rather than one constant.
#
# A market with no floor listed here does not fire: with no settled evidence
# there is no threshold to clear, and inventing one would be the unvalidated
# betting the registry exists to prevent. Adding a market is a one-line diff
# once its slice justifies a number.
ENHANCEMENT_PRICE_FLOORS: dict[str, float] = {
    "match_over_25": 1.60,
    "match_over_15": 1.45,
    "match_over_35": 3.30,
    "btts_yes": 1.85,
}


# ---------------------------------------------------------------------------
# Market scoring: what counts as a HIT for a settled enhancement market
#
# One definition, shared: the audit certifies the registry from it, and the
# ticket engine grades a frozen enhancement leg from it. Kept next to the
# floors because the floor and the hit definition answer the same question
# from opposite sides (what price is enough / what actually landed).
# ---------------------------------------------------------------------------
def check_enhancement_hit(enh_type: str, selection: str, hs: int, gs: int) -> bool | None:
    if hs is None or gs is None:
        return None
    sel = selection.lower()
    if enh_type == "match_over_15":
        # FIX-2 (2026-08-03, Addendum 12): plain-market scoring. The promised %
        # rendered for this market and the price captured for it are both the
        # PLAIN total, so the hit must be selection-independent. The removed
        # Win+Over combo branches measured a different market than the one
        # priced, deflating every hit-rate (and any future registry
        # certification) built on them.
        return (hs + gs) >= 2
    elif enh_type == "match_over_25":
        # FIX-2: plain-market scoring (see match_over_15).
        return (hs + gs) >= 3
    elif enh_type == "match_under_15":
        return (hs + gs) <= 1
    elif enh_type == "match_under_25":
        return (hs + gs) <= 2
    elif enh_type == "match_under_35":
        return (hs + gs) <= 3
    elif enh_type == "btts_yes":
        # FIX-2: plain-market scoring (see match_over_15).
        return hs > 0 and gs > 0
    elif enh_type == "btts_no":
        return hs == 0 or gs == 0
    elif enh_type in ("team_over_05", "home_over_05"):
        return hs >= 1 if (enh_type == "home_over_05" or sel == "home") else gs >= 1
    elif enh_type in ("team_over_15", "home_over_15"):
        return hs >= 2 if (enh_type == "home_over_15" or sel == "home") else gs >= 2
    elif enh_type == "home_over_25":
        return hs >= 3
    elif enh_type == "home_over_35":
        return hs >= 4
    elif enh_type == "home_over_45":
        return hs >= 5
    elif enh_type == "home_under_05":
        return hs == 0
    elif enh_type == "home_under_15":
        return hs <= 1
    elif enh_type == "home_under_25":
        return hs <= 2
    elif enh_type == "home_under_35":
        return hs <= 3
    elif enh_type == "home_under_45":
        return hs <= 4
    elif enh_type == "away_over_05":
        return gs >= 1
    elif enh_type == "away_over_15":
        return gs >= 2
    elif enh_type == "away_over_25":
        return gs >= 3
    elif enh_type == "away_over_35":
        return gs >= 4
    elif enh_type == "away_over_45":
        return gs >= 5
    elif enh_type == "away_under_05":
        return gs == 0
    elif enh_type == "away_under_15":
        return gs <= 1
    elif enh_type == "away_under_25":
        return gs <= 2
    elif enh_type == "away_under_35":
        return gs <= 3
    elif enh_type == "away_under_45":
        return gs <= 4
    elif enh_type == "goal_range_0_1":
        return (hs + gs) in [0, 1]
    elif enh_type == "goal_range_2_3":
        return (hs + gs) in [2, 3]
    elif enh_type == "goal_range_4_5":
        return (hs + gs) in [4, 5]
    elif enh_type == "goal_range_4_6":
        return (hs + gs) in [4, 5, 6]
    elif enh_type == "goal_range_6_plus":
        return (hs + gs) >= 6
    elif enh_type == "goal_range_7_plus":
        return (hs + gs) >= 7
    elif enh_type == "exact_0":
        return (hs + gs) == 0
    elif enh_type == "exact_1":
        return (hs + gs) == 1
    elif enh_type == "exact_2":
        return (hs + gs) == 2
    elif enh_type == "exact_3":
        return (hs + gs) == 3
    elif enh_type == "exact_4":
        return (hs + gs) == 4
    elif enh_type == "exact_5":
        return (hs + gs) == 5
    elif enh_type == "match_over_05":
        return (hs + gs) >= 1
    elif enh_type == "match_over_35":
        return (hs + gs) >= 4
    elif enh_type == "match_over_45":
        return (hs + gs) >= 5
    elif enh_type == "match_over_55":
        return (hs + gs) >= 6
    elif enh_type == "match_under_05":
        return (hs + gs) == 0
    elif enh_type == "match_under_45":
        return (hs + gs) <= 4
    elif enh_type == "match_under_55":
        return (hs + gs) <= 5
    elif enh_type == "double_chance":
        if sel == "home": # 1X
            return hs >= gs
        elif sel == "away": # X2
            return gs >= hs
        elif sel == "draw": # 12
            return hs != gs
    return None


def floor_for(market: str | None) -> float | None:
    """The minimum acceptable price for `market`, or None when it has none."""
    if not market:
        return None
    return ENHANCEMENT_PRICE_FLOORS.get(str(market).strip())


def clears_floor(market: str | None, price: object) -> bool:
    """True when `price` is at or above the market's floor.

    False for a market with no floor (no threshold exists), and False for
    anything that is not a real number > 1.0 — the same definition of "is a
    price" the render and the capture boundary use (RT-2), so a string or a
    bool can never stand in for a decimal price. A leg BELOW its floor is not a
    bet — not paper, not shadow.
    """
    floor = floor_for(market)
    if floor is None:
        return False
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        return False
    value = float(price)
    return math.isfinite(value) and value > 1.0 and value >= floor


def registry_path(root: Path) -> Path:
    return Path(root) / "localdata" / REGISTRY_FILENAME


def versioned(market: str | None) -> str | None:
    return f"{market}@{REGISTRY_VERSION}" if market else None


@contextmanager
def _locked(root: Path):
    """Serialize registry read-modify-write across processes and threads.

    Locks a DEDICATED sidecar file that is appended to but never replaced, keeping
    the locked inode constant (mirrors the quota-ledger's USAGE_LOCK_FILE pattern).
    Advisory: only processes using this helper respect it; non-fatal where flock is
    unavailable."""
    lock_path = registry_path(root).with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(lock_path, "a")  # noqa: PTH123
    try:
        try:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        except Exception:
            pass
        yield
    finally:
        try:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        fh.close()


def _read(path: Path) -> dict:
    """Parse the registry; on corruption QUARANTINE the bad file (recoverable,
    auditable) and return a fresh structure — never silently lose history (RT-4)."""
    try:
        if path.exists():
            try:
                with open(path, "rb") as fh:
                    data = json.loads(fh.read().decode("utf-8"))
                if isinstance(data, dict) and isinstance(data.get("markets"), dict):
                    return data
            except Exception:
                try:
                    quarantine = path.with_name(
                        f"{path.stem}.corrupt-{int(time.time())}{path.suffix}")
                    os.replace(path, quarantine)
                except Exception:
                    pass
    except Exception:
        pass
    return {"version": 2, "markets": {}}


def _write_atomic(path: Path, data: dict) -> None:
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(json.dumps(data, indent=1, sort_keys=True).encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def _blank() -> dict:
    return {"status": "SHADOW", "n": 0, "hits": 0, "profit": 0.0,
            "inv_price_sum": 0.0, "processed": [], "records": [],
            "multi_n": 0,  # governance N5: outcomes priced by >=2 distinct sources
            "status_since": None, "status_reason": None}


def wilson_lb(hits: int, n: int, z: float = WILSON_Z) -> float:
    if n <= 0:
        return 0.0
    p = hits / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = p + z2 / (2.0 * n)
    margin = z * ((p * (1.0 - p) + z2 / (4.0 * n)) / n) ** 0.5
    return (centre - margin) / denom


def _evaluate(entry: dict, today: str) -> None:
    if entry.get("status") not in {"SHADOW", "PAPER", "ELIGIBLE", "BENCHED"}:
        entry["status"] = "SHADOW"
    n, hits = entry.get("n", 0), entry.get("hits", 0)

    if entry["status"] == "SHADOW" and n >= 1:
        entry.update(status="PAPER", status_since=today,
                     status_reason="first priced outcome recorded")

    if entry["status"] == "PAPER" and n >= MIN_PRICED_N:
        mean_be = (entry.get("inv_price_sum", 0.0) / n) if n else None
        lb = wilson_lb(hits, n)
        if mean_be and lb >= mean_be:
            multi_n = entry.get("multi_n", 0)
            multi_req = max(1, math.ceil(n * MIN_MULTI_SOURCE_FRAC))
            if multi_n >= multi_req:
                entry.update(status="ELIGIBLE", status_since=today,
                             status_reason=f"n={n} wilsonLB95={lb:.4f} >= mean breakeven {mean_be:.4f}, multi-source {multi_n}/{multi_req}")
            else:
                # Governance N5: Wilson evidence clears but verification does not.
                # Stay PAPER with a transparent reason (never silently stall).
                entry.update(status_reason=f"n={n} wilsonLB95={lb:.4f} >= mean breakeven {mean_be:.4f} but multi-source verification {multi_n}/{multi_req} not met")

    if entry["status"] == "ELIGIBLE":
        try:
            cutoff = (date.fromisoformat(today) - timedelta(days=BENCH_WINDOW_DAYS)).isoformat()
        except Exception:
            cutoff = today
        recs = [r for r in entry.get("records", [])
                if (r.get("date") or "") >= cutoff and (r.get("price") or 0) > 1.0]
        if len(recs) >= BENCH_MIN_N:
            roi = sum((float(r["price"]) - 1.0) if r.get("hit") else -1.0 for r in recs) / len(recs)
            if roi < 0.0:
                entry.update(status="BENCHED", status_since=today,
                             status_reason=f"rolling {BENCH_WINDOW_DAYS}d roi={roi:+.4f} on n={len(recs)} (circuit breaker)")


def record_outcome(root: Path, *, date_: str, match: str, market: str | None,
                   price: float | None, hit: bool, source: str = "",
                   today: str | None = None, multi_source: bool = False,
                   bucket: str = "", rule: str = "", stated: float | None = None) -> dict:
    """Idempotently record one settled enhancement outcome.

    Dedupes on "date|match|<market>@v1" so repeated audit runs cannot double-count.
    Unpriced outcomes are recorded as processed but never advance certification.
    ``today`` injects the evaluation date (default: real system date) so the
    rolling BENCH window is deterministic in tests and batch replay.
    ``multi_source`` (governance N5): True when >=2 distinct sources priced this
    outcome; increments the market's multi_n used by the ELIGIBLE floor.

    Slice provenance (2026-10-12), recorded so the settled track record can
    answer "do enhancement bets pay better out of SKIPPED_VETO picks?":
    ``bucket`` is the parent pick's bucket, ``rule`` its rule id, ``stated`` the
    enhancement's own probability as stated at pick time. They are PROVENANCE,
    not gates — nothing here reads them. All three are optional, so every record
    written before this change renders as ``unattributed`` in a slice instead of
    being guessed at, and the dedup key is unchanged.

    Returns {"status": str|None, "recorded": bool}. Never raises."""
    try:
        mkey = versioned(market)
        if not mkey or not match:
            return {"status": None, "recorded": False}
        path = registry_path(root)
        today = today or date.today().isoformat()
        pkey = f"{date_}|{match}|{mkey}"
        with _locked(root):
            reg = _read(path)
            entry = reg["markets"].setdefault(mkey, _blank())
            if pkey in set(entry.get("processed", [])):
                return {"status": entry.get("status"), "recorded": False}
            entry.setdefault("processed", []).append(pkey)
            # RT-2: NaN/infinite prices must never advance certification.
            if price and math.isfinite(float(price)) and float(price) > 1.0:
                price_f = float(price)
                entry["n"] = entry.get("n", 0) + 1
                entry["hits"] = entry.get("hits", 0) + (1 if hit else 0)
                entry["profit"] = round(entry.get("profit", 0.0) + ((price_f - 1.0) if hit else -1.0), 6)
                entry["inv_price_sum"] = entry.get("inv_price_sum", 0.0) + 1.0 / price_f
                entry.setdefault("records", []).append(
                    {"date": date_, "match": match, "price": round(price_f, 3),
                     "hit": bool(hit), "source": source or "",
                     "multi_source": bool(multi_source),
                     # Slice provenance (2026-10-12). "" / None means
                     # unattributed, never a guess.
                     "bucket": str(bucket or ""),
                     "rule": str(rule or ""),
                     "stated": (float(stated) if isinstance(stated, (int, float))
                                and not isinstance(stated, bool)
                                and math.isfinite(float(stated)) else None)})
                entry["records"] = entry["records"][-MAX_RECORDS_PER_MARKET:]
                if multi_source:
                    entry["multi_n"] = entry.get("multi_n", 0) + 1
            entry["processed"] = entry["processed"][-MAX_PROCESSED_KEYS:]
            _evaluate(entry, today)
            _write_atomic(path, reg)
            return {"status": entry.get("status"), "recorded": True}
    except Exception:
        return {"status": None, "recorded": False}


UNATTRIBUTED = "unattributed"


def market_track_record(root: Path | None = None,
                        market: str | None = None) -> list[dict]:
    """Settled per-market rows for the settlement tables.

    ``[{market, status, n, hits, rate, breakeven, profit}]`` where ``breakeven``
    is 1/rate — the price at which the settled hit rate exactly pays for itself
    (the number the floors in ``ENHANCEMENT_PRICE_FLOORS`` are derived from).
    ``market`` selects one unversioned market; None returns every market, most
    settled first. Fail-soft: [] on any error.
    """
    try:
        root = root or Path(__file__).resolve().parents[2]
        reg = _read(registry_path(root))
        suffix = f"@{REGISTRY_VERSION}"
        rows = []
        for key, entry in (reg.get("markets") or {}).items():
            plain = key[: -len(suffix)] if key.endswith(suffix) else key
            if market is not None and plain != market:
                continue
            n = int(entry.get("n") or 0)
            hits = int(entry.get("hits") or 0)
            rate = (hits / n) if n else 0.0
            rows.append({
                "market": plain,
                "status": entry.get("status") or "SHADOW",
                "n": n,
                "hits": hits,
                "rate": rate,
                "breakeven": (1.0 / rate) if rate else None,
                "profit": float(entry.get("profit") or 0.0),
                "floor": floor_for(plain),
            })
        rows.sort(key=lambda r: (-r["n"], r["market"]))
        return rows
    except Exception:
        return []


def slice_records(records: list[dict], key: str) -> dict[str, dict]:
    """Group settled records by a provenance key ("bucket" or "rule").

    Returns ``{value: {n, hits, rate, profit}}`` sorted most-settled first.
    Records written before slice provenance existed have no such field and are
    reported as ``UNATTRIBUTED`` — never guessed at.
    """
    out: dict[str, dict] = {}
    for rec in records or []:
        try:
            value = str(rec.get(key) or "").strip() or UNATTRIBUTED
            slot = out.setdefault(value, {"n": 0, "hits": 0, "profit": 0.0})
            price = rec.get("price")
            if not isinstance(price, (int, float)) or isinstance(price, bool):
                continue
            if not math.isfinite(float(price)) or float(price) <= 1.0:
                continue
            slot["n"] += 1
            slot["hits"] += 1 if rec.get("hit") else 0
            slot["profit"] = round(
                slot["profit"] + ((float(price) - 1.0) if rec.get("hit") else -1.0), 6)
        except Exception:
            continue
    for slot in out.values():
        slot["rate"] = (slot["hits"] / slot["n"]) if slot["n"] else 0.0
    return dict(sorted(out.items(), key=lambda kv: (-kv[1]["n"], kv[0])))


def slice_for_market(root: Path | None = None, market: str | None = None,
                     key: str = "bucket") -> dict[str, dict]:
    """``slice_records`` over one market's settled history, newest markets first.

    Fail-soft: {} on any error.
    """
    try:
        root = root or Path(__file__).resolve().parents[2]
        entry = _read(registry_path(root))["markets"].get(versioned(market)) or {}
        return slice_records(entry.get("records") or [], key)
    except Exception:
        return {}


def status_for(market: str | None, root: Path | None = None) -> str:
    """Read-only status lookup for presentation. Fail-soft 'SHADOW'."""
    if not market:
        return "SHADOW"
    try:
        root = root or Path(__file__).resolve().parents[2]
        entry = _read(registry_path(root))["markets"].get(versioned(market))
        return (entry or {}).get("status") or "SHADOW"
    except Exception:
        return "SHADOW"


def all_statuses(root: Path | None = None) -> dict[str, str]:
    """{unversioned_market: status} for reporting. Fail-soft {}."""
    try:
        root = root or Path(__file__).resolve().parents[2]
        reg = _read(registry_path(root))
        suffix = f"@{REGISTRY_VERSION}"
        return {k[: -len(suffix)] if k.endswith(suffix) else k: (v or {}).get("status", "SHADOW")
                for k, v in reg.get("markets", {}).items()}
    except Exception:
        return {}
