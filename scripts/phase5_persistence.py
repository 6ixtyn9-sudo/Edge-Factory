#!/usr/bin/env python3
"""Preserve append-only Phase 5 evidence across cache restore and Git races.

The daily workflow's cache is an optimization, not the source of truth. Before
restoring the remaining tracked localdata, this helper unions the cached and
committed Phase 5 JSONL ledgers. At persistence time it resolves only
append-only Phase 5 JSONL rebase conflicts; any other conflict is left intact
for an explicit warning and the workflow artifact fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# The workflow invokes this script directly without PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from edgefactory.util import (ticket_receipt_files, ticket_receipt_path, ticket_receipt_bytes,
                              compact_ticket_receipts, write_ticket_receipt, encode_ticket_receipt,
                              read_ticket_receipt, freeze_timestamp_matches)

APPEND_ONLY_JSONL_IDS = {
    "localdata/phase5_shadow/rows.jsonl": "row_id",
    "localdata/phase5_shadow/attempts.jsonl": "attempt_id",
    "localdata/phase5_activation/mutation_receipts.jsonl": "receipt_sha256",
}
PHASE5_CLEAN_EXCLUDES = (
    "/localdata/phase5_shadow/",
    "/localdata/phase5_activation/",
    "/localdata/phase5_reconciliation/",
    "/localdata/card_enrich_call_ledger.jsonl",
    "/localdata/card_enrich_shadow_*.json",
    "/localdata/scored_candidate_shadow_*.jsonl",
    "/localdata/*_decision*.json",
)


class EvidenceMergeError(RuntimeError):
    """An append-only evidence file cannot be merged without ambiguity."""


def _run(
    repo: Path,
    *args: str,
    check: bool = False,
    env: dict[str, str] | None = None,
    input_data: bytes | None = None,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
        env=env,
    )


def _decode_output(value: bytes) -> str:
    return value.decode("utf-8", errors="replace").strip()


def _parse_jsonl(payload: bytes, *, path: str) -> list[tuple[str, dict[str, Any], bytes]]:
    records: list[tuple[str, dict[str, Any], bytes]] = []
    for line_number, raw_line in enumerate(payload.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            value = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise EvidenceMergeError(
                f"{path} line {line_number} is not valid JSON; refusing evidence merge"
            ) from exc
        if not isinstance(value, dict):
            raise EvidenceMergeError(
                f"{path} line {line_number} is not a JSON object; refusing evidence merge"
            )
        records.append((raw_line.decode("utf-8"), value, raw_line))
    return records


def merge_jsonl_payloads(
    first: bytes,
    second: bytes,
    *,
    path: str,
) -> tuple[bytes, int]:
    """Return a stable, duplicate-free union; reject identity collisions.

    ``first`` remains the prefix (committed/upstream in current callers), then
    unseen rows from ``second`` are appended in their original order. Durable
    record IDs deduplicate byte-different encodings of the same event. If a
    record ID maps to different JSON objects, neither version is discarded.
    """
    identity_field = APPEND_ONLY_JSONL_IDS.get(path)
    if identity_field is None:
        raise EvidenceMergeError(f"{path} is not an approved append-only Phase 5 ledger")

    output: list[bytes] = []
    seen: dict[str, dict[str, Any]] = {}
    added = 0
    for payload in (first, second):
        for original_line, record, raw_line in _parse_jsonl(payload, path=path):
            identifier = record.get(identity_field)
            identity = (
                f"{identity_field}:{identifier}"
                if identifier not in (None, "")
                else "line-sha256:" + hashlib.sha256(raw_line).hexdigest()
            )
            previous = seen.get(identity)
            if previous is not None:
                if previous != record:
                    raise EvidenceMergeError(
                        f"{path} has conflicting records for {identity}; preserving both inputs"
                    )
                continue
            seen[identity] = record
            output.append(original_line.encode("utf-8"))
            added += 1

    merged = b"" if not output else b"\n".join(output) + b"\n"
    return merged, added


def _head_blob(repo: Path, path: str) -> bytes:
    result = _run(repo, "show", f"HEAD:{path}")
    return result.stdout if result.returncode == 0 else b""


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.phase5-merge.tmp")
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def merge_cached_phase5_evidence(repo: Path | str) -> dict[str, int]:
    """Union cache-restored ledgers with HEAD before the workflow restores files."""
    repo = Path(repo)
    merged_counts: dict[str, int] = {}
    for relative, _identity_field in APPEND_ONLY_JSONL_IDS.items():
        path = repo / relative
        cached = path.read_bytes() if path.exists() else b""
        committed = _head_blob(repo, relative)
        if not cached and not committed:
            continue
        merged, count = merge_jsonl_payloads(committed, cached, path=relative)
        if merged != cached:
            _atomic_write(path, merged)
        merged_counts[relative] = count
    return merged_counts


def _tracked_localdata_paths(repo: Path) -> list[str]:
    result = _run(repo, "ls-files", "-z", "--", "localdata/")
    if result.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {_decode_output(result.stderr)}")
    return [os.fsdecode(path) for path in result.stdout.split(b"\0") if path]


ENH_STATE = "localdata/enhancement_tickets_state.json"
MAIN_STATE = "localdata/auto_tickets_state.json"


def _financial_rows(state):
    rows = {}
    for row in state.get("history", []):
        day = row["date"]
        if day in rows:
            raise EvidenceMergeError("duplicate financial bet-day")
        rows[day] = {k: row.get(k) for k in ("staked_pct", "returned_pct", "accas")}
    return rows


def _financial_fingerprint(state):
    """Bind a supersession to the full ledger, bank, positions and freeze locks.

    Descriptive floor tables and recovery receipts are not financial state.
    Do not reduce tickets to totals: different legs at equal stakes still differ.
    """
    fields = ("base_pct", "bank", "cycle_base", "history", "events",
              "open_slips", "frozen_by_date")
    payload = json.dumps({k: state.get(k) for k in fields}, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(payload).hexdigest()


def _acca_identity(acca: dict) -> tuple:
    """The money identity of one acca: stake, price and every priced leg.

    Numeric parts are rounded at the precision the ledger itself stores, so a
    re-rounded settling price (book-style ``round(prod, 2)``) is still the same
    bet, while different legs at equal stakes are still different bets.
    """
    return (
        round(float(acca.get("stake_pct") or 0.0), 4),
        round(float(acca.get("odds") or 0.0), 2),
        tuple(
            (str(leg.get("match") or ""), str(leg.get("pick") or ""),
             round(float(leg.get("odds") or 0.0), 3), str(leg.get("label") or ""))
            for leg in (acca.get("legs") or [])
        ),
    )


def _ledger_extends(new_rows: dict, old_rows: dict) -> bool:
    """True when every bet-day of `old_rows` survives unchanged or extended.

    Only the older days are inspected, so a committed ledger that carries days
    the cache never had is still a valid superset. This is the read-only
    direction used to decide that HEAD already contains the cache.
    """
    for day, original in old_rows.items():
        current = new_rows.get(day)
        if current is None:
            return False
        before = original.get("accas") or []
        after = current.get("accas") or []
        if after[:len(before)] != before or len(after) < len(before):
            return False
        extra = after[len(before):]
        for field, key in (("staked_pct", "stake_pct"),
                           ("returned_pct", "returned_pct")):
            expected = float(original.get(field) or 0.0) + sum(
                float(acca.get(key) or 0.0) for acca in extra)
            if abs(float(current.get(field) or 0.0) - expected) > 1e-3:
                return False
    return True


def _settlement_step(newer, older):
    """(settled_accas, draft_accas) when `newer` is one settlement step ahead.

    A settlement step is: the committed ledger, plus newly booked accas on days
    it already carries, plus (optionally) one brand-new bet-day; then every
    committed open position has to be accounted for exactly once -- either it
    was settled by one of those booked accas, or it is still open unchanged.
    Anything else that appears in the open book must be a fresh draft: a day
    that has already been bet cannot gain an unbooked position, and a frozen
    day cannot gain one at all.

    Returns None for anything that is not exactly that, so every refusal stays
    a refusal. The caller never trusts ``newer`` on a truthy result alone: it
    also requires the bank to move by exactly the booked delta.
    """
    unchanged = ("base_pct", "cycle_base", "events", "frozen_by_date",
                 "superseded_by_date")
    if any(newer.get(k) != older.get(k) for k in unchanged):
        return None
    old_rows, new_rows = _financial_rows(older), _financial_rows(newer)
    added: list[tuple[str, dict, bool]] = []      # (day, acca, brand_new_day)
    for day, old in old_rows.items():
        new = new_rows.get(day)
        if new is None:
            return None
        before = old.get("accas") or []
        after = new.get("accas") or []
        if after[:len(before)] != before:
            return None                      # an already-booked acca changed
        extra = after[len(before):]
        for field, key in (("staked_pct", "stake_pct"),
                           ("returned_pct", "returned_pct")):
            expected = float(old.get(field) or 0.0) + sum(
                float(acca.get(key) or 0.0) for acca in extra)
            if abs(float(new.get(field) or 0.0) - expected) > 1e-3:
                return None
        added.extend((day, acca, False) for acca in extra)
    for day, new in new_rows.items():
        if day in old_rows:
            continue
        accas = new.get("accas") or []
        if not accas:
            return None                      # a new bet-day is a settled card
        for field, key in (("staked_pct", "stake_pct"),
                           ("returned_pct", "returned_pct")):
            if abs(float(new.get(field) or 0.0)
                   - sum(float(acca.get(key) or 0.0) for acca in accas)) > 1e-3:
                return None
        added.extend((day, acca, True) for acca in accas)
    if not added or any(type(acca.get("won")) is not bool for _, acca, _ in added):
        return None

    committed: list[tuple[str, dict]] = []
    for slip in older.get("open_slips") or []:
        day = str(slip.get("date") or "")
        if not day:
            return None
        for acca in slip.get("accas") or []:
            committed.append((day, acca))

    settled: set[int] = set()
    for day, acca, new_day in added:
        identity = _acca_identity(acca)
        hits = [i for i, (cday, cacca) in enumerate(committed)
                if cday == day and i not in settled
                and _acca_identity(cacca) == identity]
        if new_day and len(hits) != 1:
            # A whole new bet-day may only book bets that were actually placed.
            # (A day the committed ledger already carries may be topped up by
            # settlements whose slip the ledger no longer lists.)
            return None
        if len(hits) > 1:
            return None                      # ambiguous position
        if hits:
            settled.add(hits[0])

    kept: set[int] = set()
    drafted = 0
    newest_day = max(old_rows) if old_rows else ""
    frozen = older.get("frozen_by_date") or {}
    for slip in newer.get("open_slips") or []:
        day = str(slip.get("date") or "")
        for acca in slip.get("accas") or []:
            same = [i for i, (cday, cacca) in enumerate(committed)
                    if cday == day and i not in kept and cacca == acca]
            if same:
                kept.add(same[0])
                continue
            if not day or day in frozen or (newest_day and day <= newest_day):
                return None                  # an unbooked position on a bet day
            drafted += 1
    if kept & settled or (kept | settled) != set(range(len(committed))):
        return None                          # a position vanished unbooked

    delta = sum(float(acca.get("returned_pct") or 0.0)
                - float(acca.get("stake_pct") or 0.0) for _, acca, _ in added)
    if not math.isfinite(delta):
        return None
    if abs(float(newer["bank"]) - float(older["bank"]) - delta) > 1e-3:
        return None                          # the bank did not move with the bets
    return len(settled), drafted


def _reviewed_financial_projection(repo, state):
    reviewed = _head_blob(repo, "Config/verified_results.json")
    if not reviewed:
        return state
    try:
        facts = json.loads(reviewed).get("rows", [])
        if not isinstance(facts, list) or any(not isinstance(r, dict) for r in facts):
            return state
    except (ValueError, AttributeError):
        return state
    import copy
    # Works for the workflow's plain `python scripts/phase5_persistence.py`
    # invocation as well as package imports; no PYTHONPATH/root assumption.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from auto_tickets import regrade_verified_settlements
    projected = copy.deepcopy(state)
    lines = regrade_verified_settlements(projected, verified=facts)
    if lines:
        print("PHASE5_PERSISTENCE applied_HEAD_verified_regulation_correction")
        for line in lines:
            print(line)
    return projected


def _approved_cached_freeze(repo, relative, head, cache):
    """Recover ONLY a HEAD-authorized unpublished freeze, not arbitrary cache.

    This explicit one-shot approval is financial authority. Receipt hashes and
    run provenance corroborate its exact card; they never authorize a bank or
    history change. All ordinary unapproved cache conflicts still fail closed.
    """
    approval = (head.get("integrity_recovery") or {}).get("pending_cached_freeze")
    if not approval or approval.get("status") != "approved":
        return None
    day = approval["date"]
    head_locks, cache_locks = head.get("frozen_by_date") or {}, cache.get("frozen_by_date") or {}
    if day in head_locks:
        return None
    if day not in cache_locks:
        raise EvidenceMergeError(f"approved recovery requires the saved freeze for {day}; "
                                 "cache is missing/stale, refusing to rebuild")
    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        import copy
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from auto_tickets import effective_bank, ticket_card_identity
        lane = "main" if relative == MAIN_STATE else "enh"
        prefix = "auto_tickets" if lane == "main" else "autobets_enh_tickets"
        lock = cache_locks[day]
        stamp = datetime.fromisoformat(lock["frozen_at"])
        if (lock.get("final") is not True or stamp.utcoffset() is None
                or stamp.astimezone(ZoneInfo("Africa/Johannesburg")).strftime("%Y-%m-%dT%H:%M")
                != approval["frozen_minute"]
                or day in (head.get("superseded_by_date") or {})
                or (repo / "localdata" / f"{prefix}_{day}.frozen").exists()
                or b"FROZEN AT " in (_head_blob(repo, f"localdata/{prefix}_{day}.txt") or b"")):
            raise ValueError("freeze lock is outside the approved recovery")
        if {d: v for d, v in cache_locks.items() if d != day} != head_locks:
            raise ValueError("other freeze locks changed")
        for field in ("base_pct", "bank", "cycle_base", "history", "events", "superseded_by_date",
                      "unplaced_enhancement_resets", "settled_enhancement_reconciliations"):
            if cache.get(field) != head.get(field):
                raise ValueError(f"unapproved financial change: {field}")
        outside = lambda state: [s for s in state.get("open_slips", []) if s.get("date") != day]
        if outside(cache) != outside(head):
            raise ValueError("other open positions changed")
        slips = [s for s in cache.get("open_slips", []) if s.get("date") == day]
        if len(slips) != 1 or not slips[0].get("accas"):
            raise ValueError("missing or duplicate approved frozen slip")
        plan = slips[0]["accas"]
        inventory = [[[l["match"], l["pick"], l["market"], l["odds"]]
                      for l in a["legs"]] for a in plan]
        if inventory != approval["card"]:
            raise ValueError("card differs from the explicitly approved run output")
        free = effective_bank(head, exclude_date=day)
        expected = round(free * .25 / len(plan), 4)
        if (not math.isfinite(free) or free <= 0
                or any(not math.isfinite(float(a["stake_pct"])) or a["stake_pct"] <= 0
                       or abs(a["stake_pct"] - expected) > .0002
                       or abs(a["odds"] - round(math.prod(l["odds"] for l in a["legs"]), 2)) > .0001
                       for a in plan)
                or not math.isfinite(slips[0]["staked_pct"])
                or abs(slips[0]["staked_pct"] - sum(a["stake_pct"] for a in plan)) > .0002):
            raise ValueError("frozen stakes do not reconcile to the unchanged bank/day cap")
        receipts = []
        for path in ticket_receipt_files(repo / "localdata", prefix):
            if path.name.removesuffix(".gz") != f"{prefix}_{day}_decision.json":
                continue
            payload = read_ticket_receipt(path)
            digest = payload.pop("sha256")
            if hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                         allow_nan=False).encode()).hexdigest() != digest:
                raise ValueError("recovery receipt hash mismatch")
            if payload.get("status") != "frozen":
                continue  # An older draft alias is not the recovered freeze.
            context, provenance = payload["context"], payload["execution_provenance"]
            identity = ticket_card_identity(plan)
            equivalent = lambda a, b: json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
            if (payload.get("schema") != 1 or context["lane"] != lane or context["date"] != day
                    or str(provenance.get("run_id")) != str(approval["source_run_id"])
                    or provenance.get("checkout_head_at_capture") != approval["source_head"]
                    or not freeze_timestamp_matches(lock["frozen_at"], context["build_at"])
                    or context["bank_total"] != head["bank"] or abs(context["bank_eff"] - free) > .0002
                    or not equivalent(identity, ticket_card_identity(payload["plan"]))
                    or not equivalent(identity, payload["card_identity"])):
                raise ValueError("frozen receipt does not corroborate the approved state/run")
            receipts.append(digest)
        if not receipts or len(set(receipts)) != 1:
            raise ValueError("missing or divergent frozen recovery receipts")
        text = (repo / "localdata" / f"{prefix}_{day}.txt").read_text()
        footer = f"FROZEN AT {stamp.astimezone(ZoneInfo('Africa/Johannesburg')):%H:%M} - FINAL"
        if footer not in text or any(not any(l["match"] in line and f"@ {l['odds']:.2f}" in line
                                            for line in text.splitlines()) for a in plan for l in a["legs"]):
            raise ValueError("saved frozen text does not match the recovered positions")
        retained = copy.deepcopy(head)
        retained.update(open_slips=copy.deepcopy(cache["open_slips"]), frozen_by_date=copy.deepcopy(cache_locks))
        retained["integrity_recovery"]["pending_cached_freeze"].update(
            status="recovered", receipt_sha256=receipts[0], recovered_financial_sha256=_financial_fingerprint(retained))
        print(f"PHASE5_PERSISTENCE validated_approved_cached_freeze lane={lane} date={day} "
              f"source_run={approval['source_run_id']}; bank/history unchanged")
        return json.dumps(retained, indent=2).encode()
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        raise EvidenceMergeError(f"approved cached freeze recovery refused: {exc}") from exc


def _retain_financial_state(repo, relative=ENH_STATE):
    """Cache is never allowed to reset/truncate durable ticket finance.

    A verified extension can survive checkout. Conflicts/new unmergeable stakes
    stop restoration for investigation instead of silently choosing a bank.
    """
    blob = _head_blob(repo, relative)
    if not blob:
        return None
    head = json.loads(blob)
    path = repo / relative
    if not path.exists():
        _approved_cached_freeze(repo, relative, head, {})  # Pending recovery must not silently rebuild.
        return json.dumps(_reviewed_financial_projection(repo, head), indent=2).encode()
    cache = json.loads(path.read_bytes())
    head = _reviewed_financial_projection(repo, head)
    cache = _reviewed_financial_projection(repo, cache)
    blob = json.dumps(head, indent=2).encode()
    hrows, crows = _financial_rows(head), _financial_rows(cache)
    for state in (head, cache):
        bank = state.get("bank")
        if isinstance(bank, bool) or not isinstance(bank, (int, float)) or not math.isfinite(bank):
            raise EvidenceMergeError("non-finite enhancement bank")
    approved = _approved_cached_freeze(repo, relative, head, cache)
    if approved is not None:
        return approved
    # A committed correction is not append-only (e.g. replacing a mistakenly
    # settled draft with the actually placed ticket). Only an explicit HEAD
    # receipt binding BOTH exact financial snapshots can supersede that cache.
    # Cached receipts are never trusted, and unknown positions cannot match.
    receipt = head.get("integrity_recovery", {}).get("cache_supersession", {})
    head_sha, cache_sha = _financial_fingerprint(head), _financial_fingerprint(cache)
    if (receipt.get("schema") == 1
            and receipt.get("superseded_financial_sha256") == cache_sha
            and receipt.get("retained_financial_sha256") == head_sha):
        return blob
    # A reversed unplaced settlement is not "new history" just because an old
    # cache has more rows. The committed reconciliation book is a durable
    # tombstone even if its original receipt file was later removed. Permit a
    # new settlement on that date ONLY for actual committed frozen positions.
    # Already-committed history is left untouched: this guard never retroactively
    # repairs money, and a legitimate later card on the same day may settle.
    for day, approval in (head.get("settled_enhancement_reconciliations") or {}).items():
        if not isinstance(approval, dict) or approval.get("confirmed_none_placed") is not True:
            continue
        before = (hrows.get(day) or {}).get("accas") or []
        after = (crows.get(day) or {}).get("accas") or []
        if after[:len(before)] != before:
            continue  # Not an extension; existing conflict/rollback checks decide.
        added = after[len(before):]
        if not added:
            continue
        committed = [_acca_identity(a) for slip in head.get("open_slips") or []
                     if slip.get("date") == day for a in slip.get("accas") or []]
        for acca in added:
            identity = _acca_identity(acca)
            if day not in (head.get("frozen_by_date") or {}) or identity not in committed:
                raise EvidenceMergeError(
                    f"cached settlement on reconciled date {day} does not match "
                    "a committed frozen position; refusing to resurrect an unplaced bet")
            committed.remove(identity)  # One open position cannot settle twice.

    # Equal settled totals do not prove equal bets. Check full position metadata,
    # market/selection, freeze locks and cycle state BEFORE either extension path.
    # Unknown differences must fail closed; only the exact committed receipt
    # above can authorize replacing them. Cached receipts are never authoritative.
    # Pre-freeze plans are replaceable recommendations, not settled money.
    # Only discard cache draft differences when ALL other durable state is
    # identical. Locks from either input protect that date, including legacy
    # per-day markers; a missing lock must never unlock a committed ticket.
    def locked_positions(state):
        locks = set(head.get("frozen_by_date") or {}) | set(cache.get("frozen_by_date") or {})
        locks |= {p.name.removeprefix("autobets_enh_tickets_").removesuffix(".frozen")
                  for p in (repo / "localdata").glob("autobets_enh_tickets_*.frozen")}
        positions = state.get("open_slips") or []
        if any(not isinstance(p.get("date"), str) or not p["date"] for p in positions):
            raise EvidenceMergeError("divergent enhancement financial histories: undated position")
        return [p for p in positions if p["date"] in locks]

    other_fields = ("base_pct", "bank", "cycle_base", "history", "events",
                    "frozen_by_date", "superseded_by_date", "unplaced_enhancement_resets")
    if (cache.get("open_slips") != head.get("open_slips")
            and all(cache.get(k) == head.get(k) for k in other_fields)
            and locked_positions(cache) == locked_positions(head)):
        print("PHASE5_PERSISTENCE retained_committed_unfrozen_draft; bank/history/locks unchanged")
        return blob

    # Both lanes, one rule. A run settles the slips it just closed and then
    # drafts the next card; when the push that would have carried that step is
    # rejected, the cache ends up exactly one legitimate step ahead of HEAD.
    # Refusing that step is what wedged the 2026-10-26 run: restore raised on a
    # settlement plus a fresh draft, the workflow died at step one, and every
    # later run restored the same cache and hit the same wall. Accept the step,
    # but only after proving it is one: an exact ledger extension, every
    # committed position either settled by it or still open, and anything new
    # an unfrozen draft for a day that has not been bet yet.
    if cache_sha != head_sha:
        step = _settlement_step(cache, head)
        if step is not None:
            settled, drafted = step
            print("PHASE5_PERSISTENCE retained_cached_settlement_step; "
                  f"settled_accas={settled} draft_accas={drafted}")
            # Keep durable correction/approval metadata from HEAD even when the
            # cache carries the newer settled ledger and the next draft.
            retained = dict(head)
            retained.update(bank=cache["bank"], history=cache.get("history", []),
                            open_slips=cache.get("open_slips") or [])
            return json.dumps(retained, indent=2).encode()
    if cache_sha == head_sha:
        return blob
    # No position changed: the ledger alone decides, as it always has.
    position_fields = ("base_pct", "cycle_base", "events", "open_slips",
                       "frozen_by_date", "superseded_by_date")
    if all(cache.get(k) == head.get(k) for k in position_fields):
        if _ledger_extends(crows, hrows):
            delta = (sum(r["returned_pct"] - r["staked_pct"] for r in crows.values())
                     - sum(r["returned_pct"] - r["staked_pct"] for r in hrows.values()))
            if not math.isfinite(delta) or abs(cache["bank"] - head["bank"] - delta) > .001:
                raise EvidenceMergeError(
                    "cached enhancement bank does not reconcile to committed history")
            retained = dict(head)
            retained.update(bank=cache["bank"], history=cache.get("history", []))
            return json.dumps(retained, indent=2).encode()
        if _ledger_extends(hrows, crows):
            # Committed history is newer: the cache is a rollback, keep HEAD.
            return blob
    elif _settlement_step(head, cache) is not None:
        # HEAD is itself one settlement step ahead of the cache: the cache is
        # stale, and the committed ledger already books everything in it.
        return blob
    raise EvidenceMergeError(
        "divergent enhancement financial histories: different open positions, "
        "freeze locks or cycle state; no matching committed supersession receipt "
        f"(committed={head_sha}, cached={cache_sha})"
    )


def _retain_ticket_decisions(repo: Path, financial_blobs: dict) -> dict[str, bytes]:
    """Keep cached frozen audit receipts when finance restore retains that freeze.

    Receipt bytes NEVER influence the financial restore. Divergent frozen
    receipts are retained as an artifact-visible conflict, never auto-merged.
    """
    retained = {}
    for prefix in ("auto_tickets", "autobets_enh_tickets"):
        for path in ticket_receipt_files(repo / "localdata", prefix):
            relative = path.relative_to(repo).as_posix()
            cached = path.read_bytes()
            # Resolve both layouts by logical receipt name, not storage suffix.
            name = path.name.removesuffix(".gz")
            canonical = ticket_receipt_path(repo / "localdata", name).relative_to(repo).as_posix()
            legacy = "localdata/" + name
            head_blob, head_relative = None, relative
            for alternative in dict.fromkeys((canonical, legacy)):
                result = _run(repo, "show", f"HEAD:{alternative}")
                if result.returncode == 0:
                    head_blob, head_relative = result.stdout, alternative
                    break
            try:
                # Seed the canonical destination with HEAD, even when HEAD is
                # legacy JSON and an untracked gzip alias survives git clean.
                # An authorized cached freeze below may upgrade only a draft.
                if head_blob is not None:
                    head_raw = ticket_receipt_bytes(repo / head_relative, raw=head_blob)
                    retained.setdefault(canonical, encode_ticket_receipt(repo / canonical, head_raw))
                candidate = json.loads(ticket_receipt_bytes(path))
                digest = candidate.pop("sha256")
                encoded = json.dumps(candidate, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
                if hashlib.sha256(encoded).hexdigest() != digest:
                    raise ValueError("cached decision receipt hash mismatch")
                expected_lane = "main" if prefix == "auto_tickets" else "enh"
                if (candidate["context"]["lane"] != expected_lane
                        or name != f"{prefix}_{candidate['context']['date']}_decision.json"):
                    raise ValueError("cached receipt filename/context mismatch")
                if head_blob is not None:
                    head = json.loads(head_raw)
                    if candidate["status"] != "frozen" or head.get("sha256") == digest:
                        continue
                    if head.get("status") == "frozen":
                        raise ValueError("divergent frozen decision receipts")
                    lane = candidate["context"]["lane"]
                    day = candidate["context"]["date"]
                    state_path = MAIN_STATE if lane == "main" else ENH_STATE
                    state_blob = financial_blobs.get(state_path)
                    if state_blob is None:
                        state_blob = _run(repo, "show", f"HEAD:{state_path}").stdout
                    state = json.loads(state_blob)
                    freeze = (state.get("frozen_by_date") or {}).get(day) or {}
                    if not freeze_timestamp_matches(freeze.get("frozen_at"), candidate["context"]["build_at"]):
                        raise ValueError("cached receipt is not the independently retained financial freeze")
                if canonical in retained:
                    previous = json.loads(ticket_receipt_bytes(repo / canonical, raw=retained[canonical]))
                    if previous.get("status") == "frozen":
                        if candidate.get("status") != "frozen":
                            continue
                        if previous.get("sha256") != digest:
                            raise ValueError("divergent cached frozen decision receipts")
                retained[canonical] = encode_ticket_receipt(repo / canonical, ticket_receipt_bytes(path))
            except (OSError, EOFError, ValueError, KeyError, TypeError, AttributeError) as exc:
                # Keep HEAD authoritative and the differing cache bytes visible
                # to the report/artifact, without modifying bank or history.
                try:
                    evidence = ticket_receipt_bytes(path)
                except (OSError, EOFError, ValueError):
                    evidence = cached  # retain even malformed gzip bytes
                conflict = ticket_receipt_path(repo / "localdata", name.removesuffix(".json")
                    + f"_cache_conflict_{hashlib.sha256(evidence).hexdigest()}.json")
                write_ticket_receipt(conflict, evidence)
                print(f"::warning::Ticket decision receipt conflict: {relative}: {exc}")
    return retained


def restore_committed_localdata(repo: Path | str) -> dict[str, Any]:
    """Restore ordinary tracked state without overwriting cached append-only evidence."""
    repo = Path(repo)
    # Validate BOTH lanes before checkout/clean mutates any restored evidence.
    financial_blobs = {relative: _retain_financial_state(repo, relative)
                       for relative in (ENH_STATE, MAIN_STATE)}
    # Save original human cards before checkout, only after BOTH lanes passed
    # the explicit recovery checks. Never replace a committed frozen card.
    recovered_cards = {}
    for relative, blob in financial_blobs.items():
        if blob is None:
            continue
        state = json.loads(blob)
        record = (state.get("integrity_recovery") or {}).get("pending_cached_freeze") or {}
        committed = json.loads(_head_blob(repo, relative) or b"{}")
        if record.get("status") == "recovered" and record["date"] not in (committed.get("frozen_by_date") or {}):
            prefix = "auto_tickets" if relative == MAIN_STATE else "autobets_enh_tickets"
            card = f"localdata/{prefix}_{record['date']}.txt"
            recovered_cards[card] = (repo / card).read_bytes()
    decision_blobs = _retain_ticket_decisions(repo, financial_blobs)
    try:
        merge_counts = merge_cached_phase5_evidence(repo)
    except (OSError, EvidenceMergeError) as exc:
        # Fail closed: do not check out or clean the Phase 5 directories below.
        # The untouched cache copy is still uploaded by the workflow artifact step.
        merge_counts = {"merge_warning": 1}
        print(f"::warning::Phase 5 cache/HEAD union was not applied: {exc}")

    restored: list[str] = []
    protected = set(APPEND_ONLY_JSONL_IDS)
    for relative in _tracked_localdata_paths(repo):
        if relative in protected:
            continue
        result = _run(repo, "checkout", "HEAD", "--", relative)
        if result.returncode != 0:
            raise RuntimeError(
                f"could not restore committed localdata file {relative}: "
                f"{_decode_output(result.stderr)}"
            )
        restored.append(relative)

    for relative, blob in recovered_cards.items():
        _atomic_write(repo / relative, blob)
    for relative, blob in decision_blobs.items():
        _atomic_write(repo / relative, blob)

    for relative, financial_blob in financial_blobs.items():
        if financial_blob is not None:
            _atomic_write(repo / relative, financial_blob)
    clean = _run(
        repo,
        "clean", "-fd", "localdata/",
        *sum((("-e", pattern) for pattern in PHASE5_CLEAN_EXCLUDES), ()),
    )
    if clean.returncode != 0:
        raise RuntimeError(f"git clean failed: {_decode_output(clean.stderr)}")
    compacted = compact_ticket_receipts(repo / "localdata")
    return {
        "compacted_ticket_receipts": compacted,
        "phase5_ledgers": merge_counts,
        "restored_tracked_files": len(restored),
        "clean_output": _decode_output(clean.stdout),
    }


def _unmerged_paths(repo: Path) -> list[str]:
    result = _run(repo, "diff", "--name-only", "--diff-filter=U", "-z")
    if result.returncode != 0:
        return []
    return [os.fsdecode(path) for path in result.stdout.split(b"\0") if path]


def _stage_blob(repo: Path, stage: int, path: str) -> bytes | None:
    result = _run(repo, "show", f":{stage}:{path}")
    return result.stdout if result.returncode == 0 else None


def resolve_phase5_jsonl_conflicts(repo: Path | str) -> tuple[bool, list[str], str | None]:
    """Resolve only allowlisted Phase 5 JSONL conflicts using index stages."""
    repo = Path(repo)
    paths = _unmerged_paths(repo)
    if not paths:
        return True, [], None
    unsupported = sorted(path for path in paths if path not in APPEND_ONLY_JSONL_IDS)
    if unsupported:
        return False, [], "unsupported conflicts: " + ", ".join(unsupported)

    merged_payloads: dict[str, bytes] = {}
    try:
        for path in paths:
            upstream = _stage_blob(repo, 2, path) or b""
            replayed = _stage_blob(repo, 3, path) or b""
            merged, _count = merge_jsonl_payloads(upstream, replayed, path=path)
            merged_payloads[path] = merged
    except EvidenceMergeError as exc:
        return False, [], str(exc)

    for relative, payload in merged_payloads.items():
        _atomic_write(repo / relative, payload)
    for relative in paths:
        staged = _run(repo, "add", "--", relative)
        if staged.returncode != 0:
            detail = _decode_output(staged.stderr)
            return False, [], f"could not stage merged evidence {relative}: {detail}"
    return True, paths, None


def _rebase_in_progress(repo: Path) -> bool:
    result = _run(repo, "rev-parse", "--git-path", "rebase-merge")
    if result.returncode == 0 and (repo / _decode_output(result.stdout)).exists():
        return True
    result = _run(repo, "rev-parse", "--git-path", "rebase-apply")
    return result.returncode == 0 and (repo / _decode_output(result.stdout)).exists()


def _index_and_worktree_clean(repo: Path) -> bool:
    return (
        _run(repo, "diff", "--quiet").returncode == 0
        and _run(repo, "diff", "--cached", "--quiet").returncode == 0
    )


def finish_rebase(repo: Path | str, *, max_steps: int = 32) -> tuple[bool, str | None]:
    """Continue a rebase, auto-merging only append-only Phase 5 evidence."""
    repo = Path(repo)
    for _ in range(max_steps):
        if not _rebase_in_progress(repo):
            return True, None
        conflicts = _unmerged_paths(repo)
        if conflicts:
            resolved, paths, reason = resolve_phase5_jsonl_conflicts(repo)
            if not resolved:
                return False, reason
            print("PHASE5_PERSISTENCE merged_rebase_conflicts=" + ",".join(paths))

        env = os.environ.copy()
        env["GIT_EDITOR"] = "true"
        continued = _run(repo, "rebase", "--continue", env=env)
        if continued.returncode == 0:
            continue
        if _unmerged_paths(repo):
            continue
        if _index_and_worktree_clean(repo) and _rebase_in_progress(repo):
            # The local patch was a byte/record duplicate of upstream. Skipping
            # its now-empty commit loses no evidence and avoids a false failure.
            skipped = _run(repo, "rebase", "--skip", env=env)
            if skipped.returncode == 0:
                continue
        detail = _decode_output(continued.stderr) or _decode_output(continued.stdout)
        return False, f"git rebase --continue failed: {detail}"
    return False, "rebase exceeded the bounded conflict-resolution step count"


# Upstream 5xx and transport blips are not review findings. On 2026-10-25 a
# state push was rejected with "remote: Internal Server Error" and the whole
# settlement step was left cache-only; the next run then had to reconcile it.
# Those failures are retried in place instead of being reported as terminal.
_TRANSIENT_PUSH_MARKERS = (
    "internal server error", "bad gateway", "service unavailable",
    "gateway timeout", "timed out", "timeout", "connection reset",
    "connection refused", "rpc failed", "early eof", "unexpected eof",
    "remote end hung up", "unexpected disconnect", "http 500", "http 502",
    "http 503", "http 504", "sideband",
)


def _is_transient_push_failure(detail: str) -> bool:
    lower = detail.lower()
    return any(marker in lower for marker in _TRANSIENT_PUSH_MARKERS)


def _warn_not_persisted(reason: str) -> None:
    print(
        "::warning::Pipeline state commit was not pushed. "
        "Phase 5 evidence is included in the always-uploaded artifact. "
        + reason
    )


def persist_localdata(
    repo: Path | str,
    *,
    run_id: str | None = None,
    max_push_attempts: int = 3,
    push_backoff: tuple[int, ...] = (5, 15, 30),
) -> dict[str, Any]:
    """Commit, rebase with safe JSONL unions, and push without force."""
    repo = Path(repo)
    # Capture BEFORE commit/pull/rebase. This identifies this persistence
    # invocation, not the revision used by every earlier pipeline subprocess.
    revision = _run(repo, "rev-parse", "HEAD")
    pre_persist_head = _decode_output(revision.stdout) if revision.returncode == 0 else "unavailable"
    verified_path = repo / "Config" / "verified_results.json"
    try:
        verified_sha = hashlib.sha256(verified_path.read_bytes()).hexdigest()
    except OSError:
        verified_sha = "unavailable"
    # Raw candidate ledgers can exceed GitHub's per-blob limit in one day.
    # Keep working copies for the cache + dedicated 30-day artifact, including
    # files tracked by older revisions. Do not delete or truncate evidence.
    staged = _run(repo, "add", "-A", "--", "localdata/",
                  ":(exclude)localdata/scored_candidate_shadow_*.jsonl")
    if staged.returncode != 0:
        reason = _decode_output(staged.stderr)
        _warn_not_persisted(f"git add failed: {reason}")
        return {"status": "not_persisted", "reason": reason}
    if _run(repo, "diff", "--cached", "--quiet").returncode == 0:
        print("PHASE5_PERSISTENCE no_localdata_changes")
        return {"status": "no_changes"}

    run_id = run_id or os.environ.get("GITHUB_RUN_ID", "local")
    commit = _run(repo, "commit", "-m", f"chore: persist pipeline state (run {run_id})",
                  "-m", f"pre_persist_head={pre_persist_head}\nverified_results_sha256={verified_sha}\n"
                        f"event_sha={os.environ.get('GITHUB_SHA', 'unavailable')}\n"
                        "scope=persistence invocation; earlier subprocess revisions not inferred")
    if commit.returncode != 0:
        reason = _decode_output(commit.stderr) or _decode_output(commit.stdout)
        _warn_not_persisted(f"git commit failed: {reason}")
        return {"status": "not_persisted", "reason": reason}

    push_error = "no push attempted"
    for attempt in range(1, max_push_attempts + 1):
        transient = False
        pull = _run(repo, "pull", "--rebase", "--autostash")
        if pull.returncode != 0:
            if not _rebase_in_progress(repo):
                reason = _decode_output(pull.stderr) or _decode_output(pull.stdout)
                _warn_not_persisted(f"git pull --rebase failed: {reason}")
                return {"status": "not_persisted", "reason": reason}
            resolved, reason = finish_rebase(repo)
            if not resolved:
                _run(repo, "rebase", "--abort")
                _warn_not_persisted(reason or "Phase 5 rebase conflict was not safely mergeable")
                return {"status": "not_persisted", "reason": reason}

        pushed = _run(repo, "push")
        if pushed.returncode == 0:
            print(f"PHASE5_PERSISTENCE pushed attempt={attempt}")
            return {"status": "pushed", "attempt": attempt}
        push_error = _decode_output(pushed.stderr) or _decode_output(pushed.stdout)
        lower = push_error.lower()
        transient = _is_transient_push_failure(push_error)
        if transient:
            print(f"PHASE5_PERSISTENCE push_transient_failure attempt={attempt} "
                  f"of {max_push_attempts}: "
                  + push_error.splitlines()[0][:200], flush=True)
        if not transient and not any(marker in lower for marker in
                                     ("non-fast-forward", "fetch first")):
            _warn_not_persisted(f"git push failed: {push_error}")
            return {"status": "not_persisted", "reason": push_error}
        if transient and attempt < max_push_attempts:
            walk = push_backoff[min(attempt - 1, len(push_backoff) - 1)] if push_backoff else 0
            if walk:
                time.sleep(walk)

    kind = "push race" if not transient else "transient push failure"
    reason = (f"{kind} persisted after {max_push_attempts} bounded synchronization attempts: "
              f"{push_error}")
    _warn_not_persisted(reason)
    return {"status": "not_persisted", "reason": reason}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("restore", "persist", "history-prepare", "history-recover", "history-check"))
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--reference-hit", choices=("true", "false"), default="false")
    args = parser.parse_args(argv)

    if args.action.startswith("history-"):
        sys.path.insert(0, str(args.repo / "src"))
        from edgefactory import prediction_history as history
        if args.action == "history-prepare":
            result = history.prepare(args.repo)
        elif args.action == "history-recover":
            result = history.recover(args.repo, reference_hit=args.reference_hit == "true")
        else:
            result = history.check(args.repo)
        print("PREDICTION_HISTORY " + json.dumps(result, sort_keys=True))
        return 0
    if args.action == "restore":
        result = restore_committed_localdata(args.repo)
        print(
            "PHASE5_PERSISTENCE restored "
            f"tracked_files={result['restored_tracked_files']} "
            f"phase5_ledgers={json.dumps(result['phase5_ledgers'], sort_keys=True)}"
        )
        return 0
    result = persist_localdata(args.repo, run_id=args.run_id)
    # The CLI is the workflow publication gate. A warning/artifact fallback
    # preserves evidence, but is NOT successful publication of the registry.
    return 0 if result["status"] in {"pushed", "no_changes"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
