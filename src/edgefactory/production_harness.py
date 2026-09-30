"""Production-reality checks shared by tests and by the official run.

These encode the invariants of the current production lane so that a
regression fails loudly rather than being noticed months later in a report.
Each check raises ``AssertionError`` with a message naming the offending
value, and each is safe to run against JSON payloads, Markdown text and
plain strings.

The invariants, and why each exists:

* Rule identifiers describe a rule, not a release. ``v2`` was never a
  version — it was the required voter count — and reading it as a version
  invites the wrong question.
* The lane is *the* production lane, so a ``fresh_`` prefix distinguishes it
  from nothing and dates every artifact that carries it.
* The pick engine does not size bets. ``auto_tickets`` owns bankroll, open
  exposure and slip structure, so a pick states its evidence and delegates
  staking.
* The dispatch plan is authoritative: an empty same-day file must never hide
  a future-dated pick that was already dispatched.
* Legacy baseline output is comparison-only and may never drive production.
* Parked/degraded browser-dependent sources are never probed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# ``v1``/``V2``/``v3`` etc. as a standalone token inside an identifier.
FORBIDDEN_VERSION_LABEL = re.compile(r"(?:^|[_\-\s])[vV]\d+(?:$|[_\-\s])")

# Bare stake-unit shorthand such as "1.0u", "stake: 1", "stake=2u".
STAKE_SIZE_NOTATION = re.compile(
    r"(?:\bstake\s*[:=]\s*\d|\b\d+(?:\.\d+)?\s*u\b)", re.IGNORECASE)

STAKING_POLICY = "handled_by_auto_tickets"
STAKING_OWNER = "auto_tickets"

# Browser-dependent probe entry points that must never run.
BROWSER_PROBE_MARKERS = ("probe=forebet_getrs", "probe=page_access",
                         "forebet_browser_run")


def _as_text(payload: Any) -> str:
    if isinstance(payload, (dict, list)):
        return json.dumps(payload, default=str)
    if isinstance(payload, Path):
        return payload.read_text()
    return str(payload)


def _iter_rule_ids(payload: Any):
    """Every value that looks like a rule identifier, at any depth."""
    keys = {"rule_id", "edge_rule", "rule", "name", "display_rule",
            "rule_name", "edge_rule_name"}
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in keys and isinstance(value, str) and value:
                yield value
            else:
                yield from _iter_rule_ids(value)
    elif isinstance(payload, list):
        for item in payload:
            yield from _iter_rule_ids(item)


def assert_no_forbidden_version_labels(payload: Any, *, context: str = "") -> None:
    """No production rule ID may carry a ``v1``/``v2``/``v3`` style label."""
    for rule_id in _iter_rule_ids(payload):
        assert not FORBIDDEN_VERSION_LABEL.search(rule_id), (
            f"{context or 'payload'} exposes a version-like rule ID: "
            f"{rule_id!r}. Use the voter count in words, e.g. "
            f"'1x2_two_source_p55_unanimous'.")


def assert_no_fresh_prefix_in_rule_ids(payload: Any, *, context: str = "") -> None:
    """The production lane needs no lane prefix on its own rule IDs."""
    for rule_id in _iter_rule_ids(payload):
        assert not rule_id.startswith("fresh_"), (
            f"{context or 'payload'} exposes a prefixed rule ID: {rule_id!r}. "
            f"This lane is the production lane; drop the 'fresh_' prefix.")


def assert_pick_engine_does_not_emit_stake_size(payload: Any, *,
                                                context: str = "") -> None:
    """A pick may not carry a stake amount, only a delegation marker."""
    rows = payload if isinstance(payload, list) else [payload]
    for row in rows:
        if not isinstance(row, dict):
            continue
        for banned in ("stake", "stake_units", "stake_size", "risk_label"):
            assert banned not in row, (
                f"{context or 'pick'} carries {banned!r}: staking belongs to "
                f"{STAKING_OWNER}, not the pick engine.")


def assert_no_stake_notation_in_text(text: Any, *, context: str = "") -> None:
    """User-facing text must not show unexplained stake shorthand."""
    body = _as_text(text)
    match = STAKE_SIZE_NOTATION.search(body)
    assert match is None, (
        f"{context or 'text'} shows stake notation {match.group(0)!r}. "
        f"Staking is {STAKING_POLICY}; the pick engine displays none.")


def assert_staking_delegated_to_auto_tickets(payload: Any, *,
                                             context: str = "") -> None:
    """Every dispatched pick must name who owns staking."""
    rows = payload if isinstance(payload, list) else [payload]
    for row in rows:
        if not isinstance(row, dict):
            continue
        assert row.get("staking_policy") == STAKING_POLICY, (
            f"{context or 'pick'} is missing staking_policy="
            f"{STAKING_POLICY!r}")
        assert row.get("staking_owner") == STAKING_OWNER, (
            f"{context or 'pick'} is missing staking_owner={STAKING_OWNER!r}")


def assert_dispatch_plan_authoritative(plan: dict, *, context: str = "") -> None:
    """The plan must fully describe what production will publish."""
    for key in ("run_date", "same_day_picks", "horizon_picks", "event_dates",
                "sync_dates", "replaceable_dates", "notification_action"):
        assert key in plan, f"{context or 'dispatch plan'} is missing {key!r}"
    expected = "empty_slate"
    if plan["same_day_picks"]:
        expected = "same_day_pick"
    elif plan["horizon_picks"]:
        expected = "future_pick"
    assert plan["notification_action"] == expected, (
        f"{context or 'dispatch plan'} says notification_action="
        f"{plan['notification_action']!r} but holds "
        f"{len(plan['same_day_picks'])} same-day and "
        f"{len(plan['horizon_picks'])} future pick(s)")


def assert_future_picks_event_dated(plan: dict, *, context: str = "") -> None:
    """A future pick is keyed on the day it is played, not the run day."""
    run_date = plan.get("run_date")
    for row in plan.get("horizon_picks") or []:
        event_date = row.get("event_date")
        assert event_date, f"{context or 'horizon pick'} has no event_date"
        assert event_date != run_date, (
            f"{context or 'horizon pick'} is dated on the run date "
            f"{run_date!r}; a same-day pick belongs in same_day_picks")
        assert row.get("date") == event_date, (
            f"{context or 'horizon pick'} publishes date={row.get('date')!r} "
            f"but its event date is {event_date!r}")
        assert row.get("run_date") == run_date, (
            f"{context or 'horizon pick'} lost its run_date provenance")


def assert_legacy_baseline_comparison_only(payload: Any, *,
                                           context: str = "") -> None:
    """Legacy rows may be published, but never as production."""
    rows = payload if isinstance(payload, list) else [payload]
    for row in rows:
        if not isinstance(row, dict):
            continue
        rule = row.get("rule") if isinstance(row.get("rule"), dict) else row
        if rule.get("rule_source") != "legacy_baseline":
            continue
        assert rule.get("comparison_only") is True, (
            f"{context or 'row'} publishes a legacy_baseline rule that is not "
            f"marked comparison_only")
        assert rule.get("dispatchable") is False, (
            f"{context or 'row'} marks a legacy_baseline rule dispatchable")


def assert_kickoff_parser_dd_mm_reference_date(parse_kickoff_dt) -> None:
    """The parser reads day-first and takes its calendar from the fixture.

    Reading ``DD-MM`` as ``MM-DD`` made every kickoff after the 12th of a
    month unparseable and moved the rest by months, which both hid fixtures
    and let already-started matches pass the pre-match guard.
    """
    checks = [
        ("30-09, 08:10", "2026-09-30", (2026, 9, 30, 8, 10)),
        ("01-10, 06:10", "2026-10-01", (2026, 10, 1, 6, 10)),
        ("24-07, 14:00", "2024-07-24", (2024, 7, 24, 14, 0)),
        ("31-12, 23:00", "2026-12-31", (2026, 12, 31, 23, 0)),
        ("01-01, 01:00", "2027-01-01", (2027, 1, 1, 1, 0)),
        ("06:10", "2026-10-01", (2026, 10, 1, 6, 10)),
    ]
    for raw, reference, expected in checks:
        parsed = parse_kickoff_dt(raw, reference)
        assert parsed is not None, f"{raw!r} with {reference} must parse"
        actual = (parsed.year, parsed.month, parsed.day, parsed.hour,
                  parsed.minute)
        assert actual == expected, (
            f"{raw!r} with reference {reference} parsed as {actual}, "
            f"expected {expected}")
    for bad in ("kick-off TBC", "", "99-99, 10:00"):
        assert parse_kickoff_dt(bad, "2026-09-30") is None, (
            f"{bad!r} must fail closed rather than guess")


def assert_no_browser_probe_paths(text: Any, *, context: str = "") -> None:
    """Parked/degraded browser-dependent probes must never be invoked."""
    body = _as_text(text).lower()
    for marker in BROWSER_PROBE_MARKERS:
        assert marker not in body, (
            f"{context or 'payload'} references browser probe {marker!r}, "
            f"which is disabled for this lane")


def check_production_artifact(payload: Any, *, context: str = "") -> None:
    """Every naming/staking invariant, for one production artifact."""
    assert_no_forbidden_version_labels(payload, context=context)
    assert_no_fresh_prefix_in_rule_ids(payload, context=context)
    assert_no_browser_probe_paths(payload, context=context)
