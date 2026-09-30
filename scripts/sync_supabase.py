#!/usr/bin/env python3
"""Sync certified edges + daily picks to Supabase.

CSV/DuckDB remains the live ingest path. This script promotes the current edge
registry and an explicit picks ledger into Supabase for dashboards / app read
models. It supports authoritative replace-for-date syncing so stale same-day
rows cannot survive downstream.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.db import delete_picks_for_date, get_client, upsert_edges, upsert_picks  # noqa: E402
from edgefactory.util import ledger_team_key  # noqa: E402

LOCALDATA = ROOT / "localdata"
EDGES = LOCALDATA / "edges_consensus.json"
DEFAULT_PICKS = ROOT / "localdata" / "picks_today.json"

SPORT_ID = 1  # sports.key='soccer'
SOURCE_ID = 1  # sources.key='forebet' / consensus base source
EVENT_SOURCE_KEY = "edgefactory_picks"


def _response_data(resp) -> list[dict]:
    return list(getattr(resp, "data", None) or [])


def _display_rule_from_name(name: str, market: str = "1x2") -> str | None:
    """Map miner rule names to the short picks_today display label."""
    import re

    mn = re.search(r"(\d+)\s*way", name or "", re.I)
    mt = re.search(r"avg_p\s*>=?\s*([\d.]+)", name or "", re.I)
    if not mn or not mt:
        return None
    n_way = int(mn.group(1))
    thr = float(mt.group(1))
    if market == "ou_2.5":
        return f"OU25-UNANIMOUS-{n_way}WAY≥{thr:.0f}"
    if market == "btts":
        return f"BTTS-UNANIMOUS-{n_way}WAY≥{thr:.0f}"
    return f"{n_way}WAY-UNANIMOUS≥{thr:.0f}"


def _lane_marks(rule_source: str, *, dispatchable: bool, comparison_only: bool) -> dict:
    """Lane provenance carried on every synced rule.

    The warehouse schema has no lane column, so the marks live inside the
    ``rule`` payload. A dashboard reading ``comparison_only`` therefore cannot
    mistake a retired legacy rule for a live production rule.
    """
    from edgefactory import production_lane

    return {
        "lane": production_lane.active_lane(),
        "rule_source": rule_source,
        "dispatchable": dispatchable,
        "comparison_only": comparison_only,
    }


def load_legacy_edges(*, comparison_only: bool) -> list[dict]:
    """Legacy certified edges. Marked comparison-only outside legacy mode."""
    try:
        data = json.loads(EDGES.read_text())
    except Exception:
        return []

    out = []
    for e in data.get("edges", []):
        if e.get("status") != "certified":
            continue
        decay = e.get("decay", {}) if isinstance(e.get("decay"), dict) else {}
        marks = _lane_marks("legacy_baseline", dispatchable=not comparison_only,
                            comparison_only=comparison_only)
        out.append({
            "name": e["rule"],
            "sport_id": SPORT_ID,
            "source_id": SOURCE_ID,
            "rule": {**e, **marks},
            "status": "comparison_only" if comparison_only else "certified",
            "train_stats": e.get("train", {}),
            "valid_stats": e.get("valid", {}),
            "decay_verdict": decay.get("verdict", "unknown"),
        })
    return out


def load_fresh_production_edges(path: Path) -> list[dict]:
    """Fresh-production rules. Only dispatchable ones are production-active.

    Research rules are published so the dashboard can see them, but they are
    explicitly ``dispatchable: false`` — they are being tracked, not traded.
    """
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []

    out = []
    for bucket, dispatchable in (("certified_dispatchable_rules", True),
                                 ("research_rules", False)):
        for rule in data.get(bucket, []) or []:
            name = rule.get("rule_id")
            if not name:
                continue
            marks = _lane_marks("fresh_production", dispatchable=dispatchable,
                                comparison_only=False)
            out.append({
                "name": name,
                "sport_id": SPORT_ID,
                "source_id": SOURCE_ID,
                "rule": {**rule, **marks,
                         "model_version": data.get("model_version"),
                         "feature_schema_version": data.get("feature_schema_version")},
                "status": "certified" if dispatchable else "research",
                "train_stats": {"walkforward_sample": rule.get("sample"),
                                "hit_rate": rule.get("hit_rate"),
                                "hit_rate_lower_bound": rule.get("hit_rate_lb")},
                "valid_stats": {"recent_sample": rule.get("recent_sample"),
                                "brier": rule.get("brier"),
                                "base_rate": rule.get("base_rate")},
                "decay_verdict": rule.get("status", "unknown"),
            })
    return out


def load_edges(target_date: str | None = None) -> list[dict]:
    """Certified rules for the ACTIVE production lane.

    In ``fresh_production`` mode the fresh registry supplies the production
    rules and the legacy registry is published as comparison-only, so no
    retired rule is ever shown as production-active.
    """
    from edgefactory import production_lane

    if not production_lane.fresh_production_is_active():
        return load_legacy_edges(comparison_only=False)

    day = target_date or date.today().isoformat()
    fresh = load_fresh_production_edges(
        production_lane.production_edges_path(day, LOCALDATA))
    return fresh + load_legacy_edges(comparison_only=True)


def load_picks_raw(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []
    return data if isinstance(data, list) else []


def infer_target_date(picks: list[dict], fallback: str | None = None) -> str | None:
    if fallback:
        return fallback
    for p in picks:
        value = str(p.get("picked_for") or p.get("date") or "")[:10]
        if value:
            return value
    return None


def build_rule_aliases(edges: list[dict]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    # Retired rule IDs resolve to their current name so historical rows and
    # artifacts written before the rename still join. Nothing writes them.
    aliases.update(deprecated_production_rule_aliases())
    for e in edges:
        name = e.get("name")
        if not name:
            continue
        aliases[name] = name
        rule = e.get("rule", {}) if isinstance(e.get("rule"), dict) else {}
        display = _display_rule_from_name(name, rule.get("market", "1x2"))
        if display:
            aliases[display] = name
    return aliases


def deprecated_production_rule_aliases() -> dict[str, str]:
    """Retired production rule ID -> current ID (internal compatibility)."""
    aliases: dict[str, str] = {}
    words = {2: "two", 3: "three", 4: "four"}
    for voters, word in words.items():
        for threshold in (55, 60, 65, 70):
            for kind in ("majority", "unanimous"):
                aliases[f"fresh_1x2_v{voters}_p{threshold}_{kind}"] = \
                    f"1x2_{word}_source_p{threshold}_{kind}"
    return aliases


def pick_edge_name(pick: dict, aliases: dict[str, str]) -> str | None:
    for key in ("edge_rule", "rule", "display_rule"):
        val = pick.get(key)
        if val and val in aliases:
            return aliases[val]
    return pick.get("edge_rule") or pick.get("rule")


def event_source_ref(pick: dict) -> str:
    sport = pick.get("sport") or "soccer"
    day = pick.get("date") or date.today().isoformat()
    home = ledger_team_key(pick.get("home") or "")
    away = ledger_team_key(pick.get("away") or "")
    if not home or not away:
        digest = hashlib.sha1(json.dumps(pick, sort_keys=True).encode()).hexdigest()[:16]
        home, away = "unknown", digest
    return f"{sport}|{day}|{home}|{away}"


def event_row_from_pick(pick: dict) -> dict:
    day = pick.get("date") or date.today().isoformat()
    return {
        "sport_id": SPORT_ID,
        "start_time": f"{day}T12:00:00+00:00",
        "source_key": EVENT_SOURCE_KEY,
        "source_ref": event_source_ref(pick),
        "status": "scheduled",
    }


def fetch_edge_ids(client, edge_names: list[str]) -> dict[str, str]:
    if not edge_names:
        return {}
    resp = (
        client.table("edges")
        .select("id,name")
        .eq("sport_id", SPORT_ID)
        .eq("source_id", SOURCE_ID)
        .in_("name", sorted(set(edge_names)))
        .execute()
    )
    return {r["name"]: r["id"] for r in _response_data(resp) if r.get("name") and r.get("id")}


def upsert_events(client, picks: list[dict]) -> dict[str, str]:
    if not picks:
        return {}
    by_ref = {event_source_ref(p): event_row_from_pick(p) for p in picks}
    rows = list(by_ref.values())
    client.table("events").upsert(rows, on_conflict="source_key,source_ref").execute()
    resp = (
        client.table("events")
        .select("id,source_ref")
        .eq("source_key", EVENT_SOURCE_KEY)
        .in_("source_ref", sorted(by_ref))
        .execute()
    )
    return {
        r["source_ref"]: r["id"]
        for r in _response_data(resp)
        if r.get("source_ref") and r.get("id")
    }


def _sync_meta(target_date: str, picks_path: Path) -> dict[str, Any]:
    return {
        "producer": "edgefactory",
        "target_date": target_date,
        "sync_mode": "authoritative_replace",
        "synced_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_file": str(picks_path),
    }


def build_pick_rows(
    picks: list[dict],
    edge_ids: dict[str, str],
    event_ids: dict[str, str],
    aliases: dict[str, str],
    *,
    target_date: str,
    picks_path: Path,
) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    skipped: list[dict] = []
    seen_conflicts: set[tuple[Any, Any, Any, Any]] = set()
    sync_meta = _sync_meta(target_date, picks_path)
    for p in picks:
        edge_name = pick_edge_name(p, aliases)
        event_ref = event_source_ref(p)
        edge_id = edge_ids.get(edge_name or "")
        event_id = event_ids.get(event_ref)
        if not edge_id or not event_id:
            skipped.append({
                "pick": p,
                "edge_name": edge_name,
                "event_ref": event_ref,
                "reason": "missing_edge_or_event_id",
            })
            continue
        bucket = p.get("bucket") or "UNKNOWN"
        try:
            probability = round(float(p.get("avg_p")) / 100.0, 4)
        except Exception:
            probability = None
        market = p.get("market", "1x2")
        selection = p.get("pick")
        conflict_key = (edge_id, event_id, market, selection)
        if conflict_key in seen_conflicts:
            # Postgres rejects an UPSERT batch that proposes the same unique
            # key twice (SQLSTATE 21000). Keep the first frozen payload and
            # quarantine the duplicate instead of deleting the date then
            # failing to repopulate it.
            skipped.append({
                "pick": p,
                "edge_name": edge_name,
                "event_ref": event_ref,
                "reason": "duplicate_conflict_key",
            })
            continue
        seen_conflicts.add(conflict_key)

        payload = dict(p)
        payload["_sync_meta"] = sync_meta
        rows.append({
            "edge_id": edge_id,
            "event_id": event_id,
            "market": market,
            "selection": selection,
            "probability": probability,
            "odds": p.get("odds"),
            "status": "skipped" if str(bucket).startswith("SKIPPED") else "open",
            "bucket": bucket,
            "context": {**(p.get("ctx", {}) or {}), "_sync_meta": sync_meta},
            "rule": edge_name,
            "match_name": p.get("match"),
            "picked_for": (p.get("date") or target_date)[:10],
            "market_type": p.get("market_type") or p.get("market"),
            "odds_tier": p.get("odds_tier"),
            "source_payload": payload,
        })
    return rows, skipped


def write_sync_manifest(*, target_date: str, picks_path: Path, raw_text: str,
                        pick_rows: list[dict], replace_date: bool,
                        rows_by_event_date: dict[str, int] | None = None) -> Path:
    """Record the publish, including its per-event-date breakdown.

    A run publishes future-dated selections alongside same-day ones, but
    the manifest is named for the run date. Without the breakdown the
    whole total is attributed to the run date, so a summary reads
    "4 (2026-10-01=4)" for a run that published 2 and 2 across two
    event dates.
    """
    if rows_by_event_date is None:
        rows_by_event_date = {}
        for row in pick_rows:
            day = str(row.get("picked_for") or target_date)[:10]
            rows_by_event_date[day] = rows_by_event_date.get(day, 0) + 1
    manifest = {
        "target_date": target_date,
        "picks_path": str(picks_path),
        "row_count": len(pick_rows),
        "row_counts_by_event_date": dict(sorted(rows_by_event_date.items())),
        "sha1": hashlib.sha1(raw_text.encode()).hexdigest(),
        "sync_mode": "authoritative_replace" if replace_date else "upsert_only",
        "written_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    out = ROOT / "localdata" / f"supabase_sync_manifest_{target_date}.json"
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return out


def dispatch_plan_rows(plan: dict, ticket_outcomes: dict | None = None
                       ) -> list[dict]:
    """Every selection the plan publishes, each under its own event date.

    Rows are production *selections*. ``ticket_status`` records whether
    auto-tickets turned each one into a bet; a schema lacking the column
    simply drops it, which is why the record stays self-describing via
    ``record_type`` and ``staking_owner`` too.
    """
    rows: list[dict] = []
    for row in list(plan.get("same_day_picks") or []) + \
               list(plan.get("horizon_picks") or []):
        row = dict(row)
        # The event date is authoritative. A future-dated pick published
        # under the run date would appear on the dashboard as a bet on a
        # match that is not played that day.
        row["date"] = row.get("event_date") or row.get("date")
        row.setdefault("run_date", plan.get("run_date"))
        # The warehouse must be able to tell a production SELECTION from a
        # production TICKET. Auto-tickets owns the latter, so the selection
        # row records the delegation and the ticket verdict separately
        # rather than implying a bet that may never have been placed.
        row["record_type"] = "production_selection"
        row.setdefault("staking_owner", "auto_tickets")
        row.setdefault("ticket_status",
                       (ticket_outcomes or {}).get(str(row["date"]), {})
                       .get("status") or "not_evaluated")
        rows.append(row)
    return rows


def dates_safe_to_replace(plan: dict, *, already_dispatched: set[str]) -> list[str]:
    """Which event dates this run may delete before re-publishing.

    The run date is always authoritative for itself. A future date may only
    be replaced when this run actually produced picks for it — otherwise an
    empty same-day slate would silently delete a future pick that was
    already dispatched and possibly already staked.
    """
    run_date = plan.get("run_date")
    produced = set(plan.get("future_event_dates") or [])
    safe = {run_date} if run_date else set()
    safe |= produced
    # Never delete a future date we previously dispatched but did not
    # reproduce in this run.
    protected = already_dispatched - produced - ({run_date} if run_date else set())
    return sorted(d for d in safe if d and d not in protected)


def main() -> None:
    p = argparse.ArgumentParser(description="Sync certified edges and an explicit picks ledger to Supabase")
    p.add_argument("--picks", default=str(DEFAULT_PICKS), help="Path to source picks JSON.")
    p.add_argument("--target-date", default=None, help="Authoritative target date (YYYY-MM-DD).")
    p.add_argument("--replace-date", action="store_true", help="Delete existing rows for target date before upserting.")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--dispatch-plan", default=None,
                   help="Path to a fresh_production dispatch plan. Publishes "
                        "same-day and future-dated picks under their event "
                        "dates, replacing only the dates this run produced.")
    args = p.parse_args()

    if args.dispatch_plan:
        return sync_dispatch_plan(Path(args.dispatch_plan), dry_run=args.dry_run)

    picks_path = Path(args.picks)
    raw_text = picks_path.read_text() if picks_path.exists() else "[]"
    raw_picks = load_picks_raw(picks_path)
    target_date = infer_target_date(raw_picks, args.target_date)
    edges = load_edges(target_date)
    aliases = build_rule_aliases(edges)

    from edgefactory import production_lane

    production = sum(1 for e in edges
                     if e["rule"].get("dispatchable") and not e["rule"].get("comparison_only"))
    comparison = len(edges) - production
    print(f"Production lane: {production_lane.active_lane()}")
    print(f"Certified edges to sync: {len(edges)} "
          f"({production} production-active, {comparison} comparison-only/research)")
    print(f"Daily picks to sync: {len(raw_picks)}")
    print(f"Sync source file: {picks_path}")
    print(f"Target date: {target_date}")
    print(f"Replace date mode: {args.replace_date}")

    if args.dry_run:
        print("DRY RUN")
        return

    if args.replace_date and not target_date:
        print("Sync failed: --replace-date requires --target-date or picks with a date field")
        sys.exit(1)

    try:
        client = get_client()
        if edges:
            upsert_edges(client, edges)
        edge_ids = fetch_edge_ids(client, [e["name"] for e in edges])
        event_ids = upsert_events(client, raw_picks)
        pick_rows, skipped = build_pick_rows(
            raw_picks,
            edge_ids,
            event_ids,
            aliases,
            target_date=target_date or date.today().isoformat(),
            picks_path=picks_path,
        )
        if skipped:
            reasons: dict[str, int] = {}
            for item in skipped:
                reason = str(item.get("reason") or "missing_edge_or_event_id")
                reasons[reason] = reasons.get(reason, 0) + 1
            detail = ", ".join(f"{reason}={count}" for reason, count in sorted(reasons.items()))
            print(f"Skipped picks: {len(skipped)} ({detail})")

        # Prepare and validate the complete replacement batch before deleting
        # the currently published date. The old order deleted first, so a
        # duplicate-batch SQLSTATE 21000 left the date empty.
        if args.replace_date and raw_picks and not pick_rows:
            raise RuntimeError(
                "refusing to delete existing date: non-empty source produced zero syncable picks"
            )
        if args.replace_date and target_date:
            delete_picks_for_date(client, target_date)
        if pick_rows:
            upsert_picks(client, pick_rows)
        manifest = write_sync_manifest(
            target_date=target_date or date.today().isoformat(),
            picks_path=picks_path,
            raw_text=raw_text,
            pick_rows=pick_rows,
            replace_date=args.replace_date,
        )
        print(f"Sync manifest written: {manifest}")
        print("Supabase sync done.")
    except Exception as e:
        print("Sync failed:", e)
        sys.exit(1)


def sync_dispatch_plan(plan_path: Path, *, dry_run: bool) -> None:
    """Publish a fresh_production dispatch plan across its event dates."""
    from edgefactory import production_lane

    try:
        plan = json.loads(plan_path.read_text())
    except Exception as exc:
        print(f"Sync failed: cannot read dispatch plan {plan_path}: {exc}")
        sys.exit(1)

    run_date = plan.get("run_date") or date.today().isoformat()
    rows = dispatch_plan_rows(plan)
    replace_dates = dates_safe_to_replace(
        plan, already_dispatched=previously_dispatched_dates(run_date))
    edges = load_edges(run_date)
    aliases = build_rule_aliases(edges)

    print(f"Production lane: {production_lane.active_lane()}")
    print(f"Dispatch plan: {plan_path}")
    print(f"Run date: {run_date}")
    print(f"Same-day picks: {plan.get('same_day_pick_count', 0)}")
    print(f"Future-dated horizon picks: {plan.get('horizon_pick_count', 0)}")
    print(f"Event dates to publish: {', '.join(plan.get('event_dates') or []) or 'none'}")
    print(f"Dates to replace: {', '.join(replace_dates) or 'none'}")

    if dry_run:
        print("DRY RUN")
        return

    try:
        client = get_client()
        if edges:
            upsert_edges(client, edges)
        edge_ids = fetch_edge_ids(client, [e["name"] for e in edges])
        event_ids = upsert_events(client, rows)

        by_date: dict[str, list[dict]] = {}
        for row in rows:
            by_date.setdefault(str(row.get("date")), []).append(row)

        prepared: dict[str, list[dict]] = {}
        for event_date, date_rows in by_date.items():
            pick_rows, skipped = build_pick_rows(
                date_rows, edge_ids, event_ids, aliases,
                target_date=event_date, picks_path=plan_path)
            if date_rows and not pick_rows:
                raise RuntimeError(
                    f"refusing to publish {event_date}: {len(date_rows)} plan "
                    f"row(s) produced zero syncable picks ({len(skipped)} skipped)")
            prepared[event_date] = pick_rows

        # Delete only the dates this run is authoritative for, then publish.
        for event_date in replace_dates:
            delete_picks_for_date(client, event_date)
            print(f"  replaced date: {event_date}")
        for event_date, pick_rows in sorted(prepared.items()):
            if pick_rows:
                upsert_picks(client, pick_rows)
                print(f"  published {len(pick_rows)} pick(s) for {event_date}")

        record_dispatched_dates(run_date, plan)
        manifest = write_sync_manifest(
            target_date=run_date, picks_path=plan_path,
            raw_text=plan_path.read_text(),
            pick_rows=[r for rows_ in prepared.values() for r in rows_],
            replace_date=True,
            rows_by_event_date={d: len(r) for d, r in prepared.items() if r})
        print(f"Sync manifest written: {manifest}")
        print("Supabase sync done.")
    except Exception as e:
        print("Sync failed:", e)
        sys.exit(1)


def _dispatch_ledger_path() -> Path:
    return LOCALDATA / "fresh_production_dispatched_dates.json"


def previously_dispatched_dates(run_date: str) -> set[str]:
    """Event dates this lane has already published picks for.

    Used to protect an already-dispatched future pick from being deleted by
    a later run that produced nothing for that date.
    """
    try:
        data = json.loads(_dispatch_ledger_path().read_text())
    except Exception:
        return set()
    if not isinstance(data, dict):
        return set()
    return {d for d, count in data.items()
            if isinstance(count, int) and count > 0 and d >= run_date}


def record_dispatched_dates(run_date: str, plan: dict) -> None:
    """Append this run's published event dates to the dispatch ledger."""
    try:
        data = json.loads(_dispatch_ledger_path().read_text())
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}
    counts: dict[str, int] = {}
    for row in dispatch_plan_rows(plan):
        key = str(row.get("date"))
        counts[key] = counts.get(key, 0) + 1
    for event_date in plan.get("event_dates") or []:
        data[event_date] = counts.get(event_date, 0)
    try:
        _dispatch_ledger_path().write_text(json.dumps(data, indent=2, sort_keys=True))
    except OSError:
        pass


if __name__ == "__main__":
    main()
