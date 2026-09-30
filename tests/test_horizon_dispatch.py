"""Future-dated horizon dispatch, kickoff parsing, and event-date sync.

Every fixture, team, price and kickoff here is synthetic on purpose:
synthetic data is permitted inside unit tests and nowhere else.

Two things are under test. First, the kickoff parser: the feeds publish
``DD-MM, HH:MM`` and the parser was reading it as ``MM-DD``, which made every
kickoff after the 12th of a month unparseable and silently moved the rest by
months. Second, horizon dispatch: a pick that passes every gate but happens
to be played tomorrow must reach production under *its own event date*,
without letting an empty same-day slate delete it.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fp = _load("fresh_production_horizon_under_test", "fresh_production.py")
pt = _load("picks_today_horizon_under_test", "picks_today.py")

from edgefactory import production_lane as pl  # noqa: E402

TZ = timezone(timedelta(hours=2))
RUN_DATE = "2026-09-30"
EVENT_DATE = "2026-10-01"
AS_OF = datetime(2026, 9, 30, 8, 0, tzinfo=TZ)
FRESH = {"EDGE_FACTORY_PRODUCTION_LANE": "fresh_production"}


# --------------------------------------------------------------------------
# Kickoff parsing — the reason kickoffs went missing on the 30th
# --------------------------------------------------------------------------


@pytest.mark.parametrize("raw,reference,expected", [
    # zulubet publishes 2024-07-24 as "24-07, 14:00": day first, then month.
    ("24-07, 14:00", "2024-07-24", datetime(2024, 7, 24, 14, 0, tzinfo=TZ)),
    ("23-04, 16:30", "2024-04-23", datetime(2024, 4, 23, 16, 30, tzinfo=TZ)),
    # The case that broke production: day 30 is not a valid month.
    ("30-09, 08:10", "2026-09-30", datetime(2026, 9, 30, 8, 10, tzinfo=TZ)),
    # Ambiguous digits must still resolve day-first, not month-first.
    ("01-10, 06:10", "2026-10-01", datetime(2026, 10, 1, 6, 10, tzinfo=TZ)),
    ("12-06, 19:45", "2026-06-12", datetime(2026, 6, 12, 19, 45, tzinfo=TZ)),
])
def test_kickoff_is_parsed_day_first_not_month_first(raw, reference, expected):
    assert pt.parse_kickoff_dt(raw, reference) == expected


def test_kickoff_after_the_twelfth_is_no_longer_unparseable():
    """Reading DD-MM as MM-DD made every day above 12 an invalid month."""
    for day in range(13, 31):   # September has 30 days
        raw = f"{day:02d}-09, 18:00"
        parsed = pt.parse_kickoff_dt(raw, f"2026-09-{day:02d}")
        assert parsed is not None, f"{raw} must parse"
        assert parsed.day == day and parsed.month == 9


def test_bare_time_uses_the_fixture_date_not_the_wall_clock():
    """A bare 'HH:MM' on a future fixture must not be stamped with today."""
    parsed = pt.parse_kickoff_dt("18:00", EVENT_DATE)
    assert parsed == datetime(2026, 10, 1, 18, 0, tzinfo=TZ)


def test_kickoff_year_rolls_over_instead_of_backwards():
    """A December run reading a January fixture must go forward a year."""
    assert pt.parse_kickoff_dt("01-01, 12:00", "2026-12-31").year == 2027
    assert pt.parse_kickoff_dt("31-12, 23:00", "2027-01-01").year == 2026


def test_started_fixture_is_rejected_now_that_its_kickoff_parses():
    """The mis-parse used to push a started match months into the future.

    A kickoff of "12-06, 07:00" read as 6 December looked like a fixture
    half a year away, so the pre-match guard passed it. Reading it correctly
    as 12 June shows it had already started.
    """
    pick = {"date": "2026-06-12", "kickoff": "12-06, 07:00"}
    as_of = datetime(2026, 6, 12, 8, 0, tzinfo=TZ)
    ok, reason = pt.operational_pick_eligibility(pick, as_of=as_of, min_lead=30)
    assert ok is False
    assert reason == "inside_30m_lead_or_started"


def test_unparseable_kickoff_still_fails_closed():
    assert pt.parse_kickoff_dt("kick-off TBC", RUN_DATE) is None
    assert pt.parse_kickoff_dt("", RUN_DATE) is None
    assert pt.parse_kickoff_dt("99-99, 10:00", RUN_DATE) is None


# --------------------------------------------------------------------------
# Timing blocker classification
# --------------------------------------------------------------------------


def _timing_group(observations, kickoff=""):
    group = fp.FixtureGroup(date=RUN_DATE, key=("alpha", "beta"),
                            home="Alpha Town", away="Beta City",
                            league="Test League")
    group.kickoff = kickoff
    group.kickoff_observations = list(observations)
    return group


def test_non_timing_source_kickoff_is_not_reported_as_parser_missed():
    """A kickoff only a non-timing source published is a policy block.

    Calling it 'parser missed' would send an engineer hunting a parsing
    defect that does not exist.
    """
    diagnosis = fp.diagnose_timing(
        _timing_group([{"source": "betclan", "raw": f"{RUN_DATE} 18:00",
                        "timing_capable": False, "parsed": True}]),
        guard_reason=None)
    assert diagnosis["classification"] == fp.TIMING_NON_TIMING_SOURCE
    assert diagnosis["classification"] != fp.TIMING_PARSE_FAILED


def test_parser_missed_is_reserved_for_a_trusted_source_that_failed_to_parse():
    diagnosis = fp.diagnose_timing(
        _timing_group([{"source": "zulubet", "raw": "kick-off TBC",
                        "timing_capable": True, "parsed": False}]),
        guard_reason=None)
    assert diagnosis["classification"] == fp.TIMING_PARSE_FAILED


def test_non_timing_source_kickoff_never_dispatches():
    """Correct labelling must not turn into permission to bet."""
    group = _timing_group([{"source": "betclan", "raw": f"{RUN_DATE} 18:00",
                            "timing_capable": False, "parsed": True}])
    assert not group.kickoff
    diagnosis = fp.diagnose_timing(group, guard_reason=None)
    assert diagnosis["kickoff"] is None
    assert diagnosis["kickoff_source"] is None


def test_a_valid_timing_provider_kickoff_is_accepted():
    group = _timing_group([{"source": "zulubet", "raw": f"{RUN_DATE} 18:00",
                            "timing_capable": True, "parsed": True}],
                          kickoff=f"{RUN_DATE} 18:00")
    diagnosis = fp.diagnose_timing(group, guard_reason=None)
    assert diagnosis["classification"] == fp.TIMING_OK
    assert diagnosis["kickoff"] == f"{RUN_DATE} 18:00"


# --------------------------------------------------------------------------
# Dispatch plan
# --------------------------------------------------------------------------


def _horizon_payload(picks, *, horizon_end="2026-10-02"):
    return {"generated_for": RUN_DATE, "horizon_end": horizon_end,
            "min_lead_minutes": 30, "max_lead_hours": 48,
            "eligible_pick_count": len(picks), "picks": picks}


def _eligible_pick(event_date=EVENT_DATE, **overrides):
    pick = {
        "date": event_date, "kickoff": f"{event_date} 08:10",
        "league": "World Cup Qualification", "home": "Panama",
        "away": "New Zealand", "selection": "home",
        "rule_id": "1x2_two_source_p60_majority", "probability": 0.72,
        "odds": 1.75, "implied_probability": 0.5714, "edge": 0.1403,
        "dispatchable": True, "internal_stake_units": 1.0,
        "dispatch_method": "certified_rule", "pricing_source": "bzzoiro",
        "timing_source": "zulubet", "source_voters": ["zulubet", "vitibet"],
        "price_match_method": "exact", "price_tier": "dedicated_pricing_feed",
        "bookmaker": "bet365", "model_version": "v2",
        "feature_schema_version": "s1", "walkforward_evidence": {},
    }
    pick.update(overrides)
    return pick


def test_eligible_horizon_pick_becomes_a_future_dated_production_pick():
    horizon = _horizon_payload([_eligible_pick()])
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)
    assert plan["same_day_pick_count"] == 0
    assert plan["horizon_pick_count"] == 1

    row = plan["horizon_picks"][0]
    for field in ("run_date", "event_date", "kickoff", "home", "away",
                  "selection", "rule_id", "probability", "odds",
                  "implied_probability", "edge", "pricing_source",
                  "timing_source", "source_voters", "dispatch_method",
                  "staking_policy", "staking_owner"):
        assert field in row, f"dispatched pick is missing {field}"
    # Staking is delegated, never sized here.
    assert row["staking_policy"] == "handled_by_auto_tickets"
    assert row["staking_owner"] == "auto_tickets"
    assert "stake" not in row and "stake_units" not in row
    assert row["run_date"] == RUN_DATE
    assert row["event_date"] == EVENT_DATE
    assert row["lane"] == "fresh_production"
    assert row["horizon_pick"] is True


def test_horizon_pick_is_dated_by_event_date_not_run_date():
    horizon = _horizon_payload([_eligible_pick()])
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)
    row = plan["horizon_picks"][0]
    assert row["date"] == EVENT_DATE != RUN_DATE
    assert plan["event_dates"] == [EVENT_DATE]
    assert RUN_DATE in plan["sync_dates"] and EVENT_DATE in plan["sync_dates"]


def test_an_undispatchable_horizon_candidate_is_not_published():
    horizon = _horizon_payload([_eligible_pick(dispatchable=False)])
    assert fp.horizon_pick_rows(horizon) == []


def test_a_horizon_pick_on_the_run_date_is_treated_as_same_day():
    """It must be published once, as a same-day pick, not duplicated."""
    horizon = _horizon_payload([_eligible_pick(event_date=RUN_DATE)])
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)
    assert plan["horizon_pick_count"] == 0
    assert plan["same_day_pick_count"] == 1
    assert plan["notification_action"] == "same_day_pick"


def test_notification_action_reflects_what_was_actually_found():
    empty = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                   horizon_rows=[], horizon=_horizon_payload([]))
    assert empty["notification_action"] == "empty_slate"

    horizon = _horizon_payload([_eligible_pick()])
    future = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                    horizon_rows=fp.horizon_pick_rows(horizon),
                                    horizon=horizon)
    assert future["notification_action"] == "future_pick"


# --------------------------------------------------------------------------
# Safe replace semantics
# --------------------------------------------------------------------------


def test_empty_same_day_slate_does_not_delete_an_existing_future_pick():
    """The core safety property of future-dated dispatch.

    Tomorrow's pick was dispatched yesterday. Today's run produces nothing,
    so it must replace only today and leave tomorrow's staked bet alone.
    """
    sync = _load("sync_supabase_horizon_under_test", "sync_supabase.py")
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=[], horizon=_horizon_payload([]))
    replace = sync.dates_safe_to_replace(plan, already_dispatched={EVENT_DATE})
    assert replace == [RUN_DATE]
    assert EVENT_DATE not in replace


def test_a_future_date_is_replaced_when_this_run_produced_picks_for_it():
    sync = sys.modules["sync_supabase_horizon_under_test"]
    horizon = _horizon_payload([_eligible_pick()])
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)
    replace = sync.dates_safe_to_replace(plan, already_dispatched={EVENT_DATE})
    assert replace == [RUN_DATE, EVENT_DATE]


def test_dispatch_plan_rows_are_keyed_on_the_event_date():
    sync = sys.modules["sync_supabase_horizon_under_test"]
    horizon = _horizon_payload([_eligible_pick()])
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)
    rows = sync.dispatch_plan_rows(plan)
    assert [r["date"] for r in rows] == [EVENT_DATE]


# --------------------------------------------------------------------------
# Notification
# --------------------------------------------------------------------------


def test_future_pick_notification_is_distinct_from_the_empty_heartbeat(tmp_path):
    notify = _load("notify_horizon_under_test", "notify.py")
    horizon = _horizon_payload([_eligible_pick()])
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan))

    message = notify.format_future_pick_message(path, RUN_DATE)
    assert message is not None
    assert f"FRESH PRODUCTION PICK — event date {EVENT_DATE}" in message
    assert "Panama vs New Zealand" in message
    assert f"No same-day picks for {RUN_DATE}." in message
    # It must not present a future fixture as today's bet.
    assert f"event date {RUN_DATE}" not in message


def test_no_future_picks_means_no_future_notification(tmp_path):
    notify = sys.modules["notify_horizon_under_test"]
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=[], horizon=_horizon_payload([]))
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan))
    # None means "fall back to the ordinary empty-slate heartbeat".
    assert notify.format_future_pick_message(path, RUN_DATE) is None


# --------------------------------------------------------------------------
# Gates still apply to horizon picks
# --------------------------------------------------------------------------


class _StubEngine:
    @staticmethod
    def parse_kickoff_dt(raw, reference=None):
        try:
            return datetime.strptime(raw, "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        except (TypeError, ValueError):
            return None

    def operational_pick_eligibility(self, pick, *, as_of, min_lead):
        kickoff = self.parse_kickoff_dt(pick.get("kickoff") or "")
        if kickoff is None:
            return False, "unparseable_kickoff"
        if kickoff - as_of < timedelta(minutes=min_lead):
            return False, "inside_lead_or_started"
        return True, ""


def _candidate(event_date, kickoff, **overrides):
    fields = dict(
        date=event_date, kickoff=kickoff, league="Test League", home="Panama",
        away="New Zealand", selection="home",
        rule_id="1x2_two_source_p60_majority", probability=0.72, odds=1.75,
        edge=0.1403, dispatchable=True, internal_stake_units=fp.FLAT_STAKE_UNITS)
    fields.update(overrides)
    return fp.Candidate(**fields)


def _plan_horizon(by_day, *, max_lead_hours=fp.HORIZON_MAX_LEAD_HOURS,
                  as_of=AS_OF):
    def fake_build(groups, *, day, **kwargs):
        return list(by_day.get(day, [])), {}

    with patch.object(fp, "build_candidates", fake_build), \
         patch.object(fp, "build_price_board",
                      lambda *a, **k: {"bundles": [], "stats": {}}):
        return fp.plan_horizon(
            groups={}, evidence={}, envelope={}, engine=_StubEngine(),
            localdata=Path("/nonexistent"), day=RUN_DATE, as_of=as_of,
            horizon_days=2, voters=(), max_lead_hours=max_lead_hours)


def test_horizon_pick_requires_a_certified_dispatchable_rule():
    cand = _candidate(EVENT_DATE, f"{EVENT_DATE} 18:00", rule_id=None,
                      dispatchable=False,
                      blockers=[f"{fp.BLOCKER_NO_RULE}: none matched"])
    assert _plan_horizon({EVENT_DATE: [cand]})["eligible_pick_count"] == 0


def test_horizon_pick_requires_odds():
    cand = _candidate(EVENT_DATE, f"{EVENT_DATE} 18:00", odds=None, edge=None,
                      dispatchable=False,
                      blockers=[f"{fp.BLOCKER_MISSING_ODDS}: no price"])
    assert _plan_horizon({EVENT_DATE: [cand]})["eligible_pick_count"] == 0


def test_horizon_pick_rejects_a_suspect_price():
    cand = _candidate(EVENT_DATE, f"{EVENT_DATE} 18:00", dispatchable=False,
                      blockers=[f"{fp.BLOCKER_SUSPECT_PRICE}: fuzzy join"])
    assert _plan_horizon({EVENT_DATE: [cand]})["eligible_pick_count"] == 0


def test_horizon_pick_rejects_started_or_inside_lead_events():
    """The planner enforces the minimum lead itself, not just upstream.

    These candidates arrive already flagged dispatchable, as they would if
    an upstream gate were bypassed or regressed. The money-placing path must
    still refuse a match that has started or is inside the lead window.
    """
    started = _candidate(RUN_DATE, f"{RUN_DATE} 07:00")
    inside = _candidate(RUN_DATE, f"{RUN_DATE} 08:15")
    payload = _plan_horizon({RUN_DATE: [started, inside]})
    assert payload["eligible_pick_count"] == 0
    for cand in (started, inside):
        assert any(b.startswith(fp.BLOCKER_KICKOFF_GUARD) for b in cand.blockers)
        assert cand.internal_stake_units == 0.0


def test_horizon_pick_respects_the_maximum_horizon():
    far = "2026-10-02"
    payload = _plan_horizon({far: [_candidate(far, f"{far} 18:00")]},
                            max_lead_hours=24)
    assert payload["eligible_pick_count"] == 0

    within = _plan_horizon({far: [_candidate(far, f"{far} 18:00")]},
                           max_lead_hours=72)
    assert within["eligible_pick_count"] == 1


def test_an_eligible_future_candidate_survives_every_gate():
    payload = _plan_horizon({EVENT_DATE: [_candidate(EVENT_DATE,
                                                     f"{EVENT_DATE} 08:10")]})
    assert payload["eligible_pick_count"] == 1
    assert payload["picks"][0]["date"] == EVENT_DATE


# --------------------------------------------------------------------------
# Routing, reports and the operator summary
# --------------------------------------------------------------------------


@patch.dict(os.environ, FRESH)
def test_downstream_consumers_route_through_the_dispatch_plan(tmp_path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    horizon = _horizon_payload([_eligible_pick()])
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)
    pl.dispatch_plan_path(RUN_DATE, localdata).write_text(json.dumps(plan))

    payload = pl.production_payload(RUN_DATE, localdata)
    assert payload["horizon_pick_count"] == 1
    assert payload["event_dates"] == [EVENT_DATE]
    assert payload["notification_action"] == "future_pick"
    assert payload["replaceable_dates"] == [RUN_DATE, EVENT_DATE]
    assert Path(payload["dispatch_plan_file"]).name == \
        f"fresh_production_dispatch_plan_{RUN_DATE}.json"


@patch.dict(os.environ, FRESH)
def test_a_missing_plan_yields_an_explicit_empty_plan_not_a_fallback(tmp_path):
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    (localdata / f"picks_{RUN_DATE}.json").write_text(json.dumps(
        [{"home": "Legacy", "away": "Row", "pick": "home"}]))
    plan = pl.load_dispatch_plan(RUN_DATE, localdata)
    assert plan["same_day_picks"] == []
    assert plan["horizon_picks"] == []
    assert plan["notification_action"] == "empty_slate"


def test_dispatch_plan_artifacts_contain_no_legacy_or_parked_labels():
    horizon = _horizon_payload([_eligible_pick()])
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)
    blob = json.dumps(plan) + fp.render_dispatch_plan_md(plan)
    for parked in fp.PARKED_PREDICTORS:
        assert parked not in blob, f"{parked} leaked into the dispatch plan"
    assert "legacy_baseline" not in blob


def test_operator_summary_makes_a_future_pick_obvious():
    horizon = _horizon_payload([_eligible_pick()])
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=fp.horizon_pick_rows(horizon),
                                  horizon=horizon)
    text = "\n".join(fp.render_dispatch_plan_summary(plan, {"blocker_counts": {}}))
    assert "PRODUCTION DISPATCH PLAN" in text
    assert "same-day picks:                0" in text
    assert "future-dated picks:            1" in text
    assert "auto-ticket action:" in text
    assert "staking:                       handled_by_auto_tickets" in text
    assert f"FUTURE {EVENT_DATE}" in text
    assert "Panama vs New Zealand" in text
    assert "notification action:           future_pick" in text


def test_operator_summary_lists_blockers_when_there_is_nothing_to_dispatch():
    plan = fp.build_dispatch_plan(run_date=RUN_DATE, same_day_rows=[],
                                  horizon_rows=[], horizon=_horizon_payload([]))
    text = "\n".join(fp.render_dispatch_plan_summary(
        plan, {"blocker_counts": {"kickoff_guard": 3}}))
    assert "top blockers if none:" in text
    assert "kickoff_guard: 3" in text


def test_dispatch_plan_is_a_known_retention_prefix():
    cl = _load("clean_localdata_horizon_under_test", "clean_localdata.py")
    prefixes = [prefix for prefix, _exts in cl._ALL_PREFIXES]
    assert "fresh_production_dispatch_plan" in prefixes
