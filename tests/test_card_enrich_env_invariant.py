"""Env invariants for card_enrich lane — persistence + presence coupling.

Two invariants that repo controls:
1. STALENESS_DAYS must NOT be in daily.yml as env assignment — module constant boggio.py:408, default kwarg 1093, no _env_int binding, inert config that reads like control. Comment mentioning it is ok, assignment is not.
2. MONTHLY_CALLS and RESERVE must be present with nonzero integer — coupling made permanent so PR can never merge into main whose workflow stops supplying cap. Hardened regex handles quoted and unquoted YAML style drift.

Operator ruling: cap=90, reserve=20, plain literals '90'/'20', not secrets ref. Branch must NOT carry workflow file (diff .github 0) to avoid clobbering main's future edits — test reads checked-out branch copy, which after rebase onto main with paste is legitimate (reads main's content through branch). If paste absent on main, test fails honestly and operator re-pastes.
"""
import re
from pathlib import Path


def test_daily_yml_must_not_contain_staleness_days_env():
    yml_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "daily.yml"
    assert yml_path.exists(), f"{yml_path} missing"
    text = yml_path.read_text()
    # Assignment pattern, not substring — comment "DO NOT add CARD_ENRICH_STALENESS_DAYS here" is allowed
    assignment_pat = re.compile(
        r"^\s*EDGE_FACTORY_CARD_ENRICH_STALENESS_DAYS\s*:",
        re.MULTILINE | re.IGNORECASE,
    )
    assignment_pat2 = re.compile(
        r"^\s*CARD_ENRICH_STALENESS_DAYS\s*:",
        re.MULTILINE | re.IGNORECASE,
    )
    assert assignment_pat.search(text) is None and assignment_pat2.search(text) is None, (
        "STALENESS_DAYS must not be in daily.yml as env var — it is a module constant, no env binding; "
        "pasting it would be inert config that reads like control. Comment mentioning it is ok, assignment is not."
    )


def test_daily_yml_carries_card_enrich_monthly_calls_and_reserve():
    """Presence invariant — hardened regex handles quoted and unquoted.

    Pattern: r"EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS:\s*'?(?:0*[1-9]\d*)'?"
    Accepts: '90', "90", 90, '026' (leading zeros ok, nonzero), rejects 0, '0', empty.
    Operator ruling is 90/20 plain literals, not 26, not secrets ref.
    """
    yml_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "daily.yml"
    assert yml_path.exists(), f"{yml_path} missing"
    text = yml_path.read_text()

    # Hardened regex — handles single or double quotes optional, unquoted valid
    # Nonzero integer: 0*[1-9]\d* — allows leading zeros but not all zeros
    # Char class ["']? already covers both quote styles, so no duplicate regex needed
    monthly_pat = re.compile(
        r'EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS:\s*["\']?(?:0*[1-9]\d*)["\']?',
        re.IGNORECASE,
    )
    reserve_pat = re.compile(
        r'EDGE_FACTORY_CARD_ENRICH_RESERVE:\s*["\']?(?:0*[1-9]\d*)["\']?',
        re.IGNORECASE,
    )

    m_monthly = monthly_pat.search(text)
    assert m_monthly is not None, (
        "EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS not found with nonzero integer in daily.yml — "
        "operator paste '90'/'20' expected on main, branch must not carry workflow file (diff .github 0) "
        "to avoid clobbering, but test reads branch copy which after rebase onto main with paste is main's content. "
        "If absent, paste landed on wrong branch or didn't push, and PR must not be vehicle."
    )

    m_reserve = reserve_pat.search(text)
    assert m_reserve is not None, (
        "EDGE_FACTORY_CARD_ENRICH_RESERVE not found with nonzero integer in daily.yml — "
        "two env lines required if lane enabled, plain literals '90'/'20' per operator ruling, not secrets ref"
    )

    # Ensure STALENESS_DAYS still absent as env assignment
    assignment_pat = re.compile(
        r"^\s*EDGE_FACTORY_CARD_ENRICH_STALENESS_DAYS\s*:",
        re.MULTILINE | re.IGNORECASE,
    )
    assignment_pat2 = re.compile(
        r"^\s*CARD_ENRICH_STALENESS_DAYS\s*:",
        re.MULTILINE | re.IGNORECASE,
    )
    assert assignment_pat.search(text) is None and assignment_pat2.search(text) is None
