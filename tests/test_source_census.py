"""The source/day fixture census: which matches does each source see?

The funnel counts rows. This answers the operator's actual question when
the slate is thin, and it is strictly diagnostic: it may not dispatch,
promote, certify or re-tier anything, and it must never invent a
probability, kickoff, price or fixture identity.

Synthetic rows are used throughout, which is permitted inside unit tests
and nowhere else.
"""

from __future__ import annotations

import csv
import gzip
import importlib.util
import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

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


engine = _load("picks_today_census_under_test", "picks_today.py")
census_cli = _load("source_census_cli_under_test", "source_census.py")

from edgefactory import source_census as sc          # noqa: E402
from edgefactory import source_registry              # noqa: E402

DAY = "2026-09-30"
NEXT = "2026-10-01"
TZ = timezone(timedelta(hours=2))
AS_OF = datetime(2026, 9, 30, 8, 0, tzinfo=TZ)


def _write_source(localdata: Path, source: str, rows: list[dict]) -> Path:
    """Write a capture cache exactly as the real loader expects it."""
    path = localdata / f"{source}_2026-09.csv.gz"
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with gzip.open(path, "wt", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields or ["date"])
        writer.writeheader()
        writer.writerows(rows)
    return path


def _row(home, away, date=DAY, kickoff="30-09, 18:00", p1=0.55, px=0.25,
         p2=0.20, **extra):
    row = {"date": date, "home": home, "away": away, "kickoff": kickoff}
    if p1 is not None:
        row.update({"p1": p1, "px": px, "p2": p2})
    row.update(extra)
    return row


def _build(localdata, *, horizon_days=1, as_of=AS_OF, sources=None):
    return sc.build_census(
        run_date=DAY, localdata=localdata, engine=engine, as_of=as_of,
        horizon_days=horizon_days, sources=sources)


# ===========================================================================
# 1. Summary covers every source/date pair, including the empty ones
# ===========================================================================


def test_every_registered_source_appears_for_every_date(tmp_path):
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    census = _build(tmp_path, horizon_days=1)

    assert census["dates"] == [DAY, NEXT]
    registered = set(sc.census_sources())
    assert registered >= {"forebet", "zulubet", "statarea", "vitibet",
                          "betclan", "scoutingstats", "bzzoiro", "predictz",
                          "windrawwin", "freesupertips", "afootballreport",
                          "prosoccer", "soccervista", "bettingclosed",
                          "bzzoiro_odds", "theoddsapi_odds",
                          "betexplorer_odds"}
    for day in census["dates"]:
        seen = {s["source"] for s in census["per_date"][day]["sources"]}
        assert seen == registered, f"{day} is missing sources"


def test_a_source_with_no_rows_is_reported_explicitly_with_a_reason(tmp_path):
    """Silence about an absent source is how coverage gaps stay invisible."""
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    census = _build(tmp_path, horizon_days=0)
    by_source = {s["source"]: s
                 for s in census["per_date"][DAY]["sources"]}

    vitibet = by_source["vitibet"]
    assert vitibet["raw_rows"] == 0
    assert vitibet["fixture_count"] == 0
    assert sc.B_NO_ROWS in vitibet["blockers"]
    assert vitibet["production_role"] == sc.ROLE_UNAVAILABLE


def test_markdown_lists_every_source_and_date(tmp_path):
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    md = sc.render_markdown(_build(tmp_path, horizon_days=1))
    for day in (DAY, NEXT):
        assert day in md
    for source in sc.census_sources():
        assert source in md
    assert "Diagnostic only" in md


def test_the_report_states_that_it_cannot_dispatch_or_certify(tmp_path):
    census = _build(tmp_path, horizon_days=0)
    md = sc.render_markdown(census)
    assert "cannot dispatch, promote, certify or enable any source" in census["note"]
    assert "capture, not validation" in census["note"]
    assert "it does not license dispatch" in md


# ===========================================================================
# 2. Fixtures land under the right source and the right date
# ===========================================================================


def test_fixtures_are_listed_under_their_source_and_event_date(tmp_path):
    _write_source(tmp_path, "zulubet", [
        _row("Panama", "New Zealand", date=DAY, kickoff="30-09, 18:00"),
        _row("Guatemala", "Suriname", date=NEXT, kickoff="01-10, 06:10"),
    ])
    census = _build(tmp_path, horizon_days=1)

    today = [s for s in census["per_date"][DAY]["sources"]
             if s["source"] == "zulubet"][0]
    tomorrow = [s for s in census["per_date"][NEXT]["sources"]
                if s["source"] == "zulubet"][0]

    assert [f"{f['raw_home']} vs {f['raw_away']}" for f in today["fixtures"]] \
        == ["Panama vs New Zealand"]
    assert [f"{f['raw_home']} vs {f['raw_away']}" for f in tomorrow["fixtures"]] \
        == ["Guatemala vs Suriname"]


def test_markdown_shows_the_actual_matches_per_source(tmp_path):
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    md = sc.render_markdown(_build(tmp_path, horizon_days=0))
    assert "Panama vs New Zealand" in md
    assert "**zulubet**" in md


def test_settled_rows_are_not_a_betting_surface(tmp_path):
    _write_source(tmp_path, "zulubet", [
        _row("Panama", "New Zealand", hs="2"),
        _row("Guatemala", "Suriname"),
    ])
    summary = [s for s in _build(tmp_path, horizon_days=0)["per_date"][DAY]["sources"]
               if s["source"] == "zulubet"][0]
    assert summary["raw_rows"] == 2
    assert summary["fixture_count"] == 1
    assert summary["already_settled_rows"] == 1


# ===========================================================================
# 3. Roles and blockers
# ===========================================================================


def test_roles_are_derived_from_the_capability_registry(tmp_path):
    for source in ("zulubet", "predictz", "bettingclosed", "bzzoiro_odds"):
        _write_source(tmp_path, source, [_row("Panama", "New Zealand")])
    by_source = {s["source"]: s for s in
                 _build(tmp_path, horizon_days=0)["per_date"][DAY]["sources"]}

    assert by_source["zulubet"]["production_role"] == sc.ROLE_LIVE_VOTER
    assert by_source["predictz"]["production_role"] == sc.ROLE_SHADOW_VOTER
    assert by_source["bettingclosed"]["production_role"] == sc.ROLE_DONOR_ONLY
    assert by_source["bzzoiro_odds"]["production_role"] == sc.ROLE_ODDS_ONLY


def test_a_shadow_source_is_never_production_consumable(tmp_path):
    """Capture volume is not promotion. Evidence decides."""
    _write_source(tmp_path, "afootballreport",
                  [_row(f"Home{i}", f"Away{i}") for i in range(50)])
    summary = [s for s in _build(tmp_path, horizon_days=0)["per_date"][DAY]["sources"]
               if s["source"] == "afootballreport"][0]

    assert summary["fixture_count"] == 50
    assert summary["production_role"] == sc.ROLE_SHADOW_VOTER
    assert sc.B_TIER_NOT_DISPATCHABLE in summary["blockers"]
    assert all(not f["production_consumable"] for f in summary["fixtures"])
    assert all(sc.B_TIER_NOT_DISPATCHABLE in f["non_consumable_reasons"]
               for f in summary["fixtures"])


def test_rows_without_probability_fields_are_not_consumable(tmp_path):
    _write_source(tmp_path, "zulubet",
                  [_row("Panama", "New Zealand", p1=None)])
    summary = [s for s in _build(tmp_path, horizon_days=0)["per_date"][DAY]["sources"]
               if s["source"] == "zulubet"][0]

    assert summary["fixture_count"] == 1
    assert summary["rows_with_1x2"] == 0
    assert sc.B_NO_1X2 in summary["blockers"]
    fixture = summary["fixtures"][0]
    assert fixture["has_1x2"] is False
    assert fixture["production_consumable"] is False
    assert sc.B_NO_1X2 in fixture["non_consumable_reasons"]
    # Absent probabilities must stay absent, never be inferred.
    assert fixture["home_probability"] is None
    assert fixture["draw_probability"] is None
    assert fixture["away_probability"] is None


def test_a_pricing_source_without_team_columns_is_reported_not_silent(tmp_path):
    """betexplorer_odds is keyed by event_id: a finding, not an empty day."""
    _write_source(tmp_path, "betexplorer_odds",
                  [{"date": DAY, "event_id": "abc", "odd1": "2.1",
                    "oddx": "3.2", "odd2": "3.4"}])
    summary = [s for s in _build(tmp_path, horizon_days=0)["per_date"][DAY]["sources"]
               if s["source"] == "betexplorer_odds"][0]

    assert summary["raw_rows"] == 1
    assert summary["fixture_count"] == 0
    assert summary["rows_without_fixture_identity"] == 1
    assert sc.B_NO_IDENTITY_COLUMNS in summary["blockers"]


def test_routine_attrition_is_counted_not_called_a_blocker(tmp_path):
    """A healthy source must not look broken because one row was settled."""
    _write_source(tmp_path, "zulubet", [
        _row("Panama", "New Zealand", hs="1"),
        _row("Guatemala", "Suriname"),
    ])
    summary = [s for s in _build(tmp_path, horizon_days=0)["per_date"][DAY]["sources"]
               if s["source"] == "zulubet"][0]
    assert summary["already_settled_rows"] == 1
    assert sc.B_SETTLED not in summary["blockers"]


# ===========================================================================
# 4. Overlap and quorum — the number that explains a thin slate
# ===========================================================================


def test_voter_count_and_quorum_are_computed_per_fixture(tmp_path):
    _write_source(tmp_path, "zulubet", [
        _row("Panama", "New Zealand"), _row("Lonely", "Fixture")])
    _write_source(tmp_path, "statarea", [_row("Panama", "New Zealand")])
    groups = {g["fixture"]: g
              for g in _build(tmp_path, horizon_days=0)["per_date"][DAY]["fixture_groups"]}

    shared = groups["Panama vs New Zealand"]
    assert shared["voter_count_1x2"] == 2
    assert shared["quorum_met"] is True
    assert shared["live_1x2_voters"] == ["statarea", "zulubet"]

    lonely = groups["Lonely vs Fixture"]
    assert lonely["voter_count_1x2"] == 1
    assert lonely["quorum_met"] is False
    assert sc.D_FEWER_THAN_2_VOTERS in lonely["blockers"]
    assert sc.D_SINGLE_SOURCE in lonely["blockers"]


def test_shadow_rows_do_not_count_toward_the_live_quorum(tmp_path):
    """Two sources is not two voters if one of them cannot vote."""
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    _write_source(tmp_path, "predictz", [_row("Panama", "New Zealand")])
    group = _build(tmp_path, horizon_days=0)["per_date"][DAY]["fixture_groups"][0]

    assert group["sources"] == ["predictz", "zulubet"]
    assert group["voter_count_1x2"] == 1
    assert group["quorum_met"] is False
    assert group["shadow_sources"] == ["predictz"]


def test_ml_anchor_presence_comes_from_the_registry(tmp_path):
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    _write_source(tmp_path, "statarea", [_row("Panama", "New Zealand")])
    _write_source(tmp_path, "betclan", [_row("Other", "Fixture")])
    _write_source(tmp_path, "vitibet", [_row("Other", "Fixture")])
    groups = {g["fixture"]: g
              for g in _build(tmp_path, horizon_days=0)["per_date"][DAY]["fixture_groups"]}

    assert groups["Panama vs New Zealand"]["ml_anchor_present"] is True
    anchorless = groups["Other vs Fixture"]
    assert anchorless["quorum_met"] is True
    assert anchorless["ml_anchor_present"] is False
    assert sc.D_NO_ML_ANCHOR in anchorless["blockers"]
    assert "betclan" not in source_registry.ml_feature_providers()


def test_date_totals_match_the_operator_funnel_shape(tmp_path):
    _write_source(tmp_path, "zulubet", [
        _row("Panama", "New Zealand"), _row("Lonely", "Fixture")])
    _write_source(tmp_path, "statarea", [_row("Panama", "New Zealand")])
    totals = _build(tmp_path, horizon_days=0)["per_date"][DAY]["totals"]

    assert totals["unique_fixture_groups"] == 2
    assert totals["groups_with_quorum"] == 1
    assert totals["ml_scoreable_groups"] == 1
    assert totals["prematch_eligible_ml_scoreable"] == 1


# ===========================================================================
# 5. Kickoff parsing regression — day-first, against the fixture's own date
# ===========================================================================


def test_dd_mm_kickoffs_land_on_the_correct_event_date(tmp_path):
    _write_source(tmp_path, "zulubet", [
        _row("Panama", "New Zealand", date=DAY, kickoff="30-09, 18:00"),
        _row("Guatemala", "Suriname", date=NEXT, kickoff="01-10, 06:10"),
    ])
    census = _build(tmp_path, horizon_days=1)

    today = [s for s in census["per_date"][DAY]["sources"]
             if s["source"] == "zulubet"][0]["fixtures"][0]
    assert today["kickoff_trusted"] is True
    assert today["kickoff_parsed"].startswith("2026-09-30T18:00")

    tomorrow = [s for s in census["per_date"][NEXT]["sources"]
                if s["source"] == "zulubet"][0]["fixtures"][0]
    assert tomorrow["kickoff_parsed"].startswith("2026-10-01T06:10")
    # The classic defect: 01-10 read as 10 January.
    assert not tomorrow["kickoff_parsed"].startswith("2026-01-10")


def test_a_bare_time_uses_the_fixture_date_not_the_run_date(tmp_path):
    _write_source(tmp_path, "zulubet",
                  [_row("Guatemala", "Suriname", date=NEXT, kickoff="06:10")])
    fixture = [s for s in _build(tmp_path, horizon_days=1)["per_date"][NEXT]["sources"]
               if s["source"] == "zulubet"][0]["fixtures"][0]
    assert fixture["kickoff_parsed"].startswith("2026-10-01T06:10")


def test_an_unparseable_kickoff_is_reported_never_guessed(tmp_path):
    _write_source(tmp_path, "zulubet", [
        _row("Panama", "New Zealand", kickoff="not a time"),
        _row("Guatemala", "Suriname", kickoff=""),
    ])
    summary = [s for s in _build(tmp_path, horizon_days=0)["per_date"][DAY]["sources"]
               if s["source"] == "zulubet"][0]

    assert summary["rows_with_trusted_kickoff"] == 0
    assert sc.B_NO_TRUSTED_KICKOFF in summary["blockers"]
    for fixture in summary["fixtures"]:
        assert fixture["kickoff_trusted"] is False
        assert fixture["kickoff_parsed"] is None      # not invented
        assert sc.B_NO_TRUSTED_KICKOFF in fixture["non_consumable_reasons"]


def test_a_started_fixture_is_reported_inside_lead(tmp_path):
    _write_source(tmp_path, "zulubet",
                  [_row("Panama", "New Zealand", kickoff="30-09, 07:00")])
    as_of = datetime(2026, 9, 30, 8, 0, tzinfo=TZ)
    summary = [s for s in _build(tmp_path, horizon_days=0, as_of=as_of)
               ["per_date"][DAY]["sources"] if s["source"] == "zulubet"][0]

    fixture = summary["fixtures"][0]
    assert fixture["kickoff_trusted"] is True
    assert fixture["prematch_eligible"] is False
    assert sc.B_INSIDE_LEAD in fixture["non_consumable_reasons"]
    assert summary["prematch_eligible_count"] == 0


# ===========================================================================
# 6. Non-interference — the census must change nothing
# ===========================================================================


def test_the_census_writes_only_its_own_artifacts(tmp_path):
    """A diagnostic that mutates production state is not a diagnostic."""
    localdata = tmp_path
    _write_source(localdata, "zulubet", [_row("Panama", "New Zealand")])

    protected = {
        f"fresh_production_dispatch_plan_{DAY}.json": '{"run_date": "x"}',
        f"fresh_production_production_picks_{DAY}.json": "[]",
        f"auto_ticket_outcomes_{DAY}.json": '{"outcomes": {}}',
        f"supabase_sync_manifest_{DAY}.json": '{"row_count": 1}',
        f"sent_ledger_{DAY}.json": "[]",
        f"picks_{DAY}.json": "[]",
    }
    for name, body in protected.items():
        (localdata / name).write_text(body)
    before = {name: (localdata / name).read_text() for name in protected}
    listing_before = sorted(p.name for p in localdata.iterdir())

    census = _build(localdata, horizon_days=1)
    census_cli.write_census(census, localdata=localdata, run_date=DAY)

    for name, body in before.items():
        assert (localdata / name).read_text() == body, f"{name} was modified"

    new_files = set(sorted(p.name for p in localdata.iterdir())) - set(listing_before)
    assert new_files == {
        f"source_fixture_census_{DAY}.json",
        f"source_fixture_census_{DAY}.md",
        f"source_fixture_census_{DAY}.csv.gz",
    }


def test_the_census_never_creates_backup_copies(tmp_path):
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    census_cli.write_census(_build(tmp_path, horizon_days=0),
                            localdata=tmp_path, run_date=DAY)
    bad = [p.name for p in tmp_path.iterdir()
           if p.suffix in (".bak", ".old", ".legacy", ".orig")]
    assert not bad


def test_the_census_module_performs_no_network_access():
    src = (SRC / "edgefactory" / "source_census.py").read_text()
    for forbidden in ("requests", "urllib", "httpx", "socket", "selenium",
                      "playwright", "webdriver", "probe="):
        assert forbidden not in src, f"census must not reference {forbidden}"


def test_the_census_cannot_promote_or_certify():
    """Prose may discuss promotion; executable code may not perform it.

    The module's own disclaimer contains the words "promote" and
    "certify", so this inspects what the code *does* — the names it
    calls, imports and assigns — rather than the characters it contains.
    """
    import ast

    tree = ast.parse((SRC / "edgefactory" / "source_census.py").read_text())
    banned = ("certif", "promote", "graduate", "force_enable", "dispatch",
              "write", "save", "sync", "notify", "stake", "ticket")

    called, assigned, imported = set(), set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = (func.attr if isinstance(func, ast.Attribute)
                    else getattr(func, "id", ""))
            called.add(name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            assigned.add(node.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imported.add(getattr(node, "module", "") or "")
            imported.update(a.name for a in node.names)

    for name in called | imported:
        low = name.lower()
        assert not any(b in low for b in banned), \
            f"census must not reference {name}"
    for name in assigned:
        low = name.lower()
        assert not any(b in low for b in ("certif", "promote", "graduate")), \
            f"census must not assign {name}"


# ===========================================================================
# 7. Thin-slate diagnosis
# ===========================================================================


def test_diagnosis_names_the_objective_bottleneck(tmp_path):
    """Many raw rows, little overlap: the census must say exactly that."""
    _write_source(tmp_path, "afootballreport",
                  [_row(f"Shadow{i}", f"Team{i}") for i in range(40)])
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    payload = _build(tmp_path, horizon_days=0)["per_date"][DAY]
    codes = {f["code"] for f in payload["diagnosis"]}

    assert sc.D_FEWER_THAN_2_VOTERS in codes
    assert sc.D_SINGLE_SOURCE in codes
    assert sc.D_TIER_NOT_DISPATCHABLE in codes
    finding = [f for f in payload["diagnosis"]
               if f["code"] == sc.D_FEWER_THAN_2_VOTERS][0]
    assert finding["fixtures_affected"] == 41


def test_diagnosis_reports_missing_kickoff_and_inside_lead(tmp_path):
    _write_source(tmp_path, "zulubet", [
        _row("Panama", "New Zealand", kickoff="junk"),
        _row("Started", "Fixture", kickoff="30-09, 07:00"),
    ])
    _write_source(tmp_path, "statarea", [
        _row("Panama", "New Zealand", kickoff="junk"),
        _row("Started", "Fixture", kickoff="30-09, 07:00"),
    ])
    codes = {f["code"] for f in
             _build(tmp_path, horizon_days=0)["per_date"][DAY]["diagnosis"]}
    assert sc.D_MISSING_KICKOFF in codes
    assert sc.D_INSIDE_LEAD in codes


def test_diagnosis_reports_an_unavailable_source_without_calling_it_empty(tmp_path):
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    finding = [f for f in _build(tmp_path, horizon_days=0)["per_date"][DAY]["diagnosis"]
               if f["code"] == "source_unavailable"][0]
    assert "not evidence of an empty fixture list" in finding["detail"]
    assert "forebet" in finding["detail"]


def test_diagnosis_never_suggests_weakening_a_gate(tmp_path):
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    md = sc.render_markdown(_build(tmp_path, horizon_days=0)).lower()
    for phrase in ("lower the", "relax the gate", "reduce the threshold",
                   "disable the guard", "loosen", "bypass the gate",
                   "force-certify"):
        assert phrase not in md
    assert "gates are not to be relaxed" in md


# ===========================================================================
# 8. Artifacts
# ===========================================================================


def test_json_and_markdown_and_csv_are_written(tmp_path):
    _write_source(tmp_path, "zulubet", [_row("Panama", "New Zealand")])
    written = census_cli.write_census(_build(tmp_path, horizon_days=0),
                                      localdata=tmp_path, run_date=DAY)
    names = [p.name for p in written]
    assert names == [f"source_fixture_census_{DAY}.json",
                     f"source_fixture_census_{DAY}.md",
                     f"source_fixture_census_{DAY}.csv.gz"]

    payload = json.loads((tmp_path / names[0]).read_text())
    assert payload["schema"] == "source_fixture_census/1"
    assert payload["run_date"] == DAY

    with gzip.open(tmp_path / names[2], "rt") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and rows[0]["source"] == "zulubet"
    assert rows[0]["raw_home"] == "Panama"
    assert rows[0]["production_role"] == sc.ROLE_LIVE_VOTER


def test_the_census_is_wired_into_the_daily_pipeline_read_only():
    src = (ROOT / "scripts" / "daily.py").read_text()
    assert "scripts/source_census.py" in src
    assert "diagnostic, read-only" in src
    # It runs after the funnel and after fresh_production, so it can
    # annotate itself with the dispatch plan.
    order = [src.index("audit_source_funnel.py"),
             src.index("run_fresh_production_lane(target_date)"),
             src.index("scripts/source_census.py")]
    assert order == sorted(order)


def test_census_annotates_itself_with_the_dispatch_plan(tmp_path):
    _write_source(tmp_path, "zulubet", [_row("Guatemala", "Suriname", date=NEXT)])
    plan = {"run_date": DAY, "same_day_picks": [],
            "horizon_picks": [{"event_date": NEXT, "home": "Guatemala",
                               "away": "Suriname"}]}
    census = sc.build_census(
        run_date=DAY, localdata=tmp_path, engine=engine, as_of=AS_OF,
        horizon_days=1, dispatch_plan=plan,
        ticket_outcomes={NEXT: {"status": "declined_insufficient_legs"}})

    assert census["per_date"][NEXT]["production_selections"] == 1
    assert census["per_date"][NEXT]["ticket_status"] == "declined_insufficient_legs"
    assert census["per_date"][DAY]["production_selections"] == 0
