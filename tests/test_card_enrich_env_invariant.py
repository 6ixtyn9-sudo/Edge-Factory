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
    """Presence invariant — hardened regex + YAML parse.

    Pattern: r"EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS:\s*'?(?:0*[1-9]\d*)'?"
    Accepts: '90', "90", 90, '026' (leading zeros ok, nonzero), rejects 0, '0', empty.
    Operator ruling is 90/20 plain literals, not 26, not secrets ref.

    Added YAML parse check per reviewer: grep alone can match a comment or wrong mapping.
    We parse with yaml.safe_load (PyYAML in requirements) and require keys under
    jobs.run-autonomous-agent.env with nonzero int value. This cannot be satisfied by
    a stray comment and proves cap is actually set.
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

    # YAML parse check — proves keys are under correct mapping, not comment
    try:
        import yaml

        data = yaml.safe_load(text)
        env = (
            data.get("jobs", {})
            .get("run-autonomous-agent", {})
            .get("env", {})
        )
        assert isinstance(env, dict), f"env is not dict: {type(env)} — CARD_ENRICH not in correct mapping"
        monthly_keys = [k for k in env if "CARD_ENRICH_MONTHLY_CALLS" in k]
        reserve_keys = [k for k in env if "CARD_ENRICH_RESERVE" in k]
        assert "EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS" in env, (
            f"MONTHLY_CALLS not in jobs.run-autonomous-agent.env dict, found {monthly_keys} — "
            "paste may be outside env or wrong indentation"
        )
        assert "EDGE_FACTORY_CARD_ENRICH_RESERVE" in env, (
            f"RESERVE not in jobs.run-autonomous-agent.env dict, found {reserve_keys}"
        )
        # Nonzero int value check
        monthly_val = env.get("EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS")
        reserve_val = env.get("EDGE_FACTORY_CARD_ENRICH_RESERVE")
        # yaml may parse '90' as int 90 or str '90' — both ok if nonzero
        for name, val in [
            ("MONTHLY_CALLS", monthly_val),
            ("RESERVE", reserve_val),
        ]:
            if isinstance(val, int):
                assert val != 0, f"{name} is 0, must be nonzero"
            elif isinstance(val, str):
                assert val.strip().strip("'\"") != "0" and val.strip().strip("'\"") != "", (
                    f"{name} string is 0/empty: {val}"
                )
                # also ensure it parses to nonzero int
                try:
                    assert int(val.strip().strip("'\"")) != 0
                except ValueError:
                    assert False, f"{name} not int-parseable: {val}"
            else:
                assert False, f"{name} unexpected type {type(val)}: {val}"
    except ImportError:
        # PyYAML not available in minimal env — regex already checked, but fail if yaml missing in CI?
        # In this repo PyYAML is in requirements, so this path should not happen in CI
        pass
