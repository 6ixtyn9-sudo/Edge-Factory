#!/usr/bin/env python3
"""card_enrich — silent, weekly, budget-ledgered Boggio H2H capture (Phase 2).

Operator-approved shape (2026-10-10), all of it binding and none of it widened
here: the TOP-6 card fixtures by proximity to consensus certification, the
``/api/v2/head-to-head/:id`` endpoint ONLY, ONE call per fixture, a staleness
skip (a snapshot younger than 7 days is never refetched), a hard monthly budget
that spans both key pools via a per-key counter, as-of stamps on every dated
row, a per-call ledger, and a fail-closed budget: no
``EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS`` means no calls at all.

Two modes, and the distinction is the whole safety story:

* default (PLAN) — spends ZERO vendor calls. It prints the mandatory pre-flight
  budget math and the per-fixture decisions, then stops. Safe to dispatch on
  any ref, and the only safe dispatch;
* ``--execute`` — pays quota. It still cannot exceed the pre-flight allowance,
  and every call it makes is written to ``localdata/card_enrich_call_ledger.jsonl``
  before anything else is believed.

Capture only: this script never registers a rule, never evaluates a predicate,
never touches the pick path, gates, notifications, or any display column. The
context snapshot it writes is shaped for ``edgefactory.context_rules`` so a
later certification can consume it, and it stays inert until the pre-registered
bars clear on their own.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from edgefactory.identity import source_team_key, squad_marker_mismatch  # noqa: E402
from edgefactory.sources import boggio  # noqa: E402

CARD_LIMIT_DEFAULT = 6
_MATCH_RULE = re.compile(r"^(?P<family>.*?)\s*avg_p>=(?P<threshold>\d+(?:\.\d+)?)$")


def load_card(localdata: Path, day: str) -> list[dict]:
    raw = json.loads((localdata / "picks_today.json").read_text(encoding="utf-8"))
    rows = raw if isinstance(raw, list) else raw.get("rows", raw.get("picks", []))
    return [r for r in rows if isinstance(r, dict) and str(r.get("date", ""))[:10] == day] \
        if isinstance(rows, list) else []


def margin(row: dict) -> float | None:
    """How far this row clears its own consensus threshold - the proximity rank.

    A fixture already 25 points past its bar does not need another evidence
    source; one sitting on the line does. Rows that are below their threshold,
    malformed, or unrankable return ``None`` and are never enriched: proximity
    to certification means *on the line*, not "anywhere on the card".
    """
    rule = str(row.get("rule") or row.get("edge_rule") or "")
    match = _MATCH_RULE.match(rule.strip())
    if not match:
        return None
    avg_p = row.get("avg_p")
    if isinstance(avg_p, bool) or not isinstance(avg_p, (int, float)):
        return None
    return round(float(avg_p) - float(match["threshold"]), 3)


def select_candidates(card: list[dict], *, limit: int) -> tuple[list[dict], list[dict]]:
    """Pick the ``limit`` fixtures closest to certification. Returns (chosen, census).

    One entry per fixture (the tightest margin on that fixture wins), so a
    fixture with two markets can never eat two of the six budgeted calls.
    """
    best: dict[tuple[str, str], dict] = {}
    skipped: dict[str, int] = {}
    for row in card:
        home, away = row.get("home"), row.get("away")
        home_key, away_key = source_team_key(home), source_team_key(away)
        if not home_key or not away_key:
            skipped["unkeyable_team"] = skipped.get("unkeyable_team", 0) + 1
            continue
        if squad_marker_mismatch(home, away):
            # A reserve/B-vs-first-team pairing is an identity hazard, not a
            # fixture. It gets no call and no snapshot.
            skipped["squad_marker_pair"] = skipped.get("squad_marker_pair", 0) + 1
            continue
        value = margin(row)
        if value is None:
            skipped["unrankable_rule"] = skipped.get("unrankable_rule", 0) + 1
            continue
        if value < 0:
            skipped["below_threshold"] = skipped.get("below_threshold", 0) + 1
            continue
        fixture_key = f"{home_key}|{away_key}"
        entry = best.get(fixture_key)
        if entry is None or value < entry["margin"]:
            best[fixture_key] = {
                "fixture_key": fixture_key, "home": home, "away": away,
                "home_key": home_key, "away_key": away_key,
                "kickoff_utc": row.get("kickoff_utc"), "league": row.get("league"),
                "date": str(row.get("date", ""))[:10], "margin": value,
                "rule": str(row.get("rule") or row.get("edge_rule")),
                "avg_p": row.get("avg_p"), "bucket": row.get("bucket"),
            }
    chosen = sorted(best.values(), key=lambda item: (item["margin"], item["fixture_key"]))[:limit]
    census = [
        {"fixture_key": item["fixture_key"], "margin": item["margin"],
         "rule": item["rule"], "selected": item in chosen}
        for item in sorted(best.values(), key=lambda item: (item["margin"], item["fixture_key"]))
    ] or [{"skipped_census": skipped}]
    if skipped:
        census.append({"skipped_census": skipped})
    return chosen, census


def event_map(localdata: Path, days: list[str]) -> dict[tuple[str, str], dict]:
    """Provider fixture ids from the shadow ledgers we ALREADY paid for.

    Keyed by the same folded team pair the card uses. No vendor call here: the
    listing's ``id`` is retained by ``sources/boggio.py`` precisely so this
    resolution is free.
    """
    out: dict[tuple[str, str], dict] = {}
    for day in days:
        path = localdata / f"boggio_shadow_{day}.json"
        try:
            rows = json.loads(path.read_text(encoding="utf-8")).get("rows", [])
        except (OSError, ValueError, TypeError, AttributeError):
            continue
        for row in rows if isinstance(rows, list) else []:
            if not isinstance(row, dict):
                continue
            event_id = row.get("event_id")
            home_key, away_key = source_team_key(row.get("home")), source_team_key(row.get("away"))
            if not event_id or not home_key or not away_key:
                continue
            out.setdefault((home_key, away_key), {
                "event_id": event_id, "kickoff": row.get("kickoff"),
                "status": "pending_assumed_from_listing",
            })
    return out


def resolve_from_listing(payload, *, day: str) -> dict[tuple[str, str], dict]:
    """Pending, unexpired, future listing rows only - expired sample rows are NOT
    valid stats keys (live-verified lesson) and stats endpoints reject past
    fixtures outright."""
    now_london = datetime.now(ZoneInfo("Europe/London"))
    out: dict[tuple[str, str], dict] = {}
    items = payload.get("data") if isinstance(payload, dict) else None
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict) or str(item.get("status", "")).lower() != "pending":
            continue
        if item.get("is_expired") is True:
            continue
        event_id = item.get("id")
        if not isinstance(event_id, int) or isinstance(event_id, bool) or event_id <= 0:
            continue
        try:
            start = datetime.fromisoformat(str(item.get("start_date") or "").replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        start = start.replace(tzinfo=ZoneInfo("Europe/London")) if start.tzinfo is None \
            else start.astimezone(ZoneInfo("Europe/London"))
        if start <= now_london:
            continue
        home_key, away_key = source_team_key(item.get("home_team")), source_team_key(item.get("away_team"))
        if not home_key or not away_key:
            continue
        out[(home_key, away_key)] = {"event_id": event_id, "kickoff": item.get("start_date"),
                                     "listing_day": day, "start_london": start.isoformat()}
    return out


def last_observed_remaining(localdata: Path) -> dict[str, int]:
    """Most recent provider-reported family remaining per key fingerprint."""
    seen: dict[str, int] = {}
    for entry in boggio.read_call_ledger(localdata):
        remaining = entry.get("family_remaining")
        fingerprint = entry.get("key")
        if isinstance(remaining, int) and isinstance(fingerprint, str):
            seen[fingerprint] = remaining
    return seen


def plan_run(day: str, *, localdata: Path, limit: int, allow_listing: bool,
             bootstrap: dict[str, int]) -> dict:
    """Every decision that can cost money, taken offline. Never touches the network."""
    card = load_card(localdata, day)
    chosen, census = select_candidates(card, limit=limit)
    snapshots = boggio.load_snapshots(localdata)
    known = last_observed_remaining(localdata)
    known.update({str(k): int(v) for k, v in (bootstrap or {}).items()})
    ids = event_map(localdata, [day])
    for item in chosen:
        pair = (item["home_key"], item["away_key"])
        item["event_id"] = (ids.get(pair) or {}).get("event_id")
        item["stale_skip"] = not boggio.needs_capture(item["fixture_key"], snapshots, day=day)
        item["needs_call"] = bool(not item["stale_skip"])
        item["resolvable"] = item["event_id"] is not None
    need_h2h = sum(1 for i in chosen if i["needs_call"] and i["resolvable"])
    unresolved = [i for i in chosen if i["needs_call"] and not i["resolvable"]]
    need_listing = 1 if (allow_listing and unresolved) else 0
    preflight = boggio.preflight(need_h2h=need_h2h, need_listing=need_listing,
                                localdata=localdata, day=day, observed_remaining=known)
    return {"day": day, "card_rows": len(card), "candidates": chosen, "census": census,
            "unresolved": [i["fixture_key"] for i in unresolved],
            "allow_listing": bool(allow_listing), "preflight": preflight,
            "need_h2h": need_h2h, "need_listing": need_listing}


def execute(day: str, plan: dict, *, localdata: Path, log=print) -> dict:
    """Pay for the plan, in pre-flight order, one ledger line per call."""
    results = {"calls": 0, "usable": 0, "statuses": [], "unattributed": []}
    budget = dict(allowed=plan["preflight"]["allowed_calls"])
    entries = boggio.read_call_ledger(localdata)
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    listing_ids: dict[tuple[str, str], dict] = {}

    if plan["need_listing"] and budget["allowed"] > 0:
        try:
            key, index, code, payload, headers = boggio.listing_call(day)
            remaining = boggio.quota_remaining(headers)
            listing_ids = resolve_from_listing(payload, day=day)
            budget["allowed"] -= 1
            results["calls"] += 1
            boggio.record_call(entries, day=day, fixture_key="listing",
                               endpoint=boggio.H2H_ENDPOINT + ":listing", pool_index=index, key=key,
                               status=code, remaining=remaining, spent=True,
                               what_bought=f"fixture-id resolution: {len(listing_ids)} pending unexpired rows")
            results["statuses"].append(f"listing http={code} resolved={len(listing_ids)}")
        except boggio.UpstreamBlocked as exc:
            boggio.record_call(entries, day=day, fixture_key="listing",
                               endpoint=boggio.H2H_ENDPOINT + ":listing",
                               pool_index=getattr(exc, "ring_pool_index", None),
                               key=getattr(exc, "ring_key", None),
                               status=None, remaining=None, spent=True,
                               what_bought="listing rejected; ids unresolved for this run", error=exc)
            results["statuses"].append(f"listing blocked: {str(exc)[:80]}")

    for item in plan["candidates"]:
        if not item["needs_call"]:
            log(f"ledger=card_enrich fixture={item['fixture_key']} decision=staleness_skip "
                f"window_days={boggio.CARD_ENRICH_STALENESS_DAYS}")
            continue
        event_id = item["event_id"] or (listing_ids.get((item["home_key"], item["away_key"])) or {}).get("event_id")
        if not event_id:
            log(f"ledger=card_enrich fixture={item['fixture_key']} decision=unresolved_id "
                f"calls_spent=0 (no pending listing row; --allow-listing not credited)")
            continue
        if budget["allowed"] <= 0:
            log(f"ledger=card_enrich fixture={item['fixture_key']} decision=budget_stop "
                f"allowed_exhausted=1 calls_spent=0")
            results["unattributed"].append(item["fixture_key"])
            continue
        try:
            key, index, code, payload, headers = boggio.h2h_call(event_id)
        except boggio.UpstreamBlocked as exc:
            # Charged: a refused or half-delivered call is still a call the vendor
            # may have billed. Attributed to the LAST pool the ring touched, which
            # the transport reports on the exception rather than left to chance.
            budget["allowed"] -= 1
            results["calls"] += 1
            touched = getattr(exc, "ring_attempts", 1) or 1
            boggio.record_call(entries, day=day, fixture_key=item["fixture_key"],
                               endpoint=boggio.H2H_ENDPOINT,
                               pool_index=getattr(exc, "ring_pool_index", None),
                               key=getattr(exc, "ring_key", None),
                               status=None, remaining=None, spent=True,
                               what_bought=f"ring rejected the fixture ({touched} pool(s) touched); no payload",
                               error=exc)
            log(f"ledger=card_enrich fixture={item['fixture_key']} event_id={event_id} status=blocked")
            continue
        remaining = boggio.quota_remaining(headers)
        snapshot = boggio.parse_head_to_head(payload, fixture={
            "home": item["home"], "away": item["away"], "kickoff_utc": item["kickoff_utc"]},
            captured_at=captured_at)
        snapshot.update({"fixture_key": item["fixture_key"], "event_id": event_id,
                         "selection": {"margin": item["margin"], "rule": item["rule"],
                                       "avg_p": item["avg_p"], "bucket": item["bucket"]}})
        budget["allowed"] -= 1
        results["calls"] += 1
        results["usable"] += 1 if snapshot.get("usable") else 0
        results["statuses"].append(f"{item['fixture_key']} http={code}")
        plan["snapshots"].append(snapshot)
        boggio.record_call(entries, day=day, fixture_key=item["fixture_key"],
                           endpoint=boggio.H2H_ENDPOINT, pool_index=index, key=key, status=code,
                           remaining=remaining, spent=True,
                           what_bought=(f"identity_verified={snapshot['identity_verified']} "
                                        f"usable={snapshot['usable']} encounters={len(snapshot['encounters'])} "
                                        f"features={sorted(snapshot['features'])} reason={snapshot['reason']}"))
        log(f"ledger=card_enrich fixture={item['fixture_key']} event_id={event_id} pool={index + 1} "
            f"http={code} family_remaining={remaining} encounters={len(snapshot['encounters'])} "
            f"usable={snapshot['usable']} features={sorted(snapshot['features'])}")
    kept = boggio.write_call_ledger(entries, localdata)
    results["ledger_entries"] = kept
    return results


def _harvest_pool_readings(argv: list[str]) -> tuple[list[str], list[str]]:
    """Pull --pool-remaining pairs out of argv BEFORE argparse sees them.

    A pool label is the last four characters of a secret, and four characters can
    legally start with '-'. Handing argparse a value that looks like a switch is
    how a receipt becomes a usage error, and a receipt that dies on a usage error
    buys nothing and explains nothing. So the pairs are read here, in both
    ``--pool-remaining TAIL=N`` and ``--pool-remaining=TAIL=N`` forms.
    """
    kept, readings = [], []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg.startswith("--pool-remaining="):
            readings.append(arg.split("=", 1)[1])
            i += 1
            continue
        if arg == "--pool-remaining":
            if i + 1 < len(argv):
                readings.append(argv[i + 1])
                i += 2
            else:
                readings.append("")     # let the validator report the missing value
                i += 1
            continue
        kept.append(arg)
        i += 1
    return kept, readings


def main(argv=None) -> int:
    argv, pool_readings = _harvest_pool_readings(list(sys.argv[1:] if argv is None else argv))
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", default=None, help="Card date (YYYY-MM-DD); default today, SAST")
    parser.add_argument("--limit", type=int, default=CARD_LIMIT_DEFAULT)
    parser.add_argument("--allow-listing", action="store_true",
                        help="Permit EXACTLY ONE default-listing call for fixture-id resolution (it "
                             "draws the same family pot; counted in pre-flight or it does not happen)")
    # (accepted via --pool-remaining, harvested above so a '-'-leading pool label
    # cannot be mistaken for a switch)
    parser.add_argument("--pool-remaining", action="append", default=None, metavar="FINGERPRINT=N",
                        help="Operator-supplied provider header reading (family-remaining counter) used "
                             "ONLY to plan, keyed by pool fingerprint or key tail from the receipt. "
                             "Never a key value.")
    parser.add_argument("--execute", action="store_true", help="Spend quota. Without it: plan only.")
    parser.add_argument("--localdata", default=os.environ.get("EDGE_FACTORY_LOCALDATA")
                        or str(ROOT / "localdata"))
    parser.add_argument("--max-requests", type=int, default=7,
                        help="Hard ceiling on physical calls per run, regardless of budget")
    args = parser.parse_args(argv)

    localdata = Path(args.localdata)
    day = args.date or datetime.now(ZoneInfo("Africa/Johannesburg")).date().isoformat()
    bootstrap: dict[str, int] = {}
    for item in pool_readings + list(args.pool_remaining or []):
        if "=" not in item:
            parser.error("--pool-remaining expects FINGERPRINT=N")
        fingerprint, _, value = item.partition("=")
        try:
            bootstrap[fingerprint.strip()] = max(0, int(value))
        except ValueError:
            parser.error(f"--pool-remaining value must be an integer, got {value!r}")

    plan = plan_run(day, localdata=localdata, limit=max(1, args.limit),
                    allow_listing=args.allow_listing, bootstrap=bootstrap)
    plan["snapshots"] = []
    boggio.print_preflight(plan["preflight"], log=print)
    print(f"ledger=card_enrich_plan date={day} card_rows={plan['card_rows']} "
          f"candidates={len(plan['candidates'])} need_h2h={plan['need_h2h']} "
          f"need_listing={plan['need_listing']} unresolved={len(plan['unresolved'])} "
          f"allow_listing={int(plan['allow_listing'])} verdict={plan['preflight']['verdict']}")
    pools = plan["preflight"]["pool_labels"]
    for fingerprint, tail in sorted(pools.items()):
        print(f"ledger=card_enrich_pool fingerprint={fingerprint} key_tail=***{tail} "
              f"allowance={plan['preflight']['allowance_by_key'].get(fingerprint, 0)} "
              f"(to plan from a header reading you hold: --pool-remaining {fingerprint}=N "
              f"or --pool-remaining {tail}=N; never pass a key)")
    for item in plan["candidates"]:
        print(f"ledger=card_enrich_candidate fixture={item['fixture_key']} margin={item['margin']} "
              f"event_id={item['event_id']} staleness_skip={int(item['stale_skip'])} "
              f"needs_call={int(item['needs_call'])}")
    for line in plan["census"]:
        print(f"ledger=card_enrich_rank {json.dumps(line, sort_keys=True)}")

    if not args.execute:
        print("ledger=card_enrich mode=plan_only calls_spent=0 "
              "note=pass --execute to pay quota (budget- and ledger-gated)")
        return 0
    if plan["preflight"]["allowed_calls"] <= 0:
        print(f"ledger=card_enrich mode=execute calls_spent=0 "
              f"verdict={plan['preflight']['verdict']} note=fails closed; nothing was purchased")
        return 0
    if plan["preflight"]["allowed_calls"] > args.max_requests:
        print(f"ledger=card_enrich mode=execute calls_spent=0 verdict=run_ceiling "
              f"allowed={plan['preflight']['allowed_calls']} max_requests={args.max_requests} "
              f"note=refusing an unplanned burst; lower the budget or raise the cap deliberately")
        return 0
    results = execute(day, plan, localdata=localdata)
    path = boggio.persist_snapshots(day, plan["snapshots"], plan["preflight"], localdata=localdata,
                                    notes=[f"need_h2h={plan['need_h2h']}",
                                           f"unresolved={len(plan['unresolved'])}"])
    print(f"ledger=card_enrich mode=execute calls_spent={results['calls']} "
          f"usable_snapshots={results['usable']} ledger_entries={results['ledger_entries']} "
          f"shadow={path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
