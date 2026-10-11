"""Env invariants for card_enrich lane — after operator paste landed.

B1-B4 final pre-merge:
- B1: persistence mechanism verified — .gitignore now negates shadow snapshots AND fixes false comment "(raw shadow snapshots stay ignored)"
- B2: base — lane built on main@1496515, main moved (bot persist + operator paste '90'/'20' on arena branch ef94edf, origin/main fetch blocked by TLS egress, so cannot confirm live HEAD, but branch now includes paste so won't revert on merge)
- B3: presence invariant no longer gated — paste landed, so test belongs in this PR, hardened regex against YAML style drift (: 90 unquoted valid, : '90' quoted valid)
- B4: paste body not title — surviving tests assert what they check, names match bodies, no green no-op

Two invariants:
1. STALENESS_DAYS must NOT be in daily.yml — module constant boggio.py:408, default kwarg 1093, no _env_int binding, inert config that reads like control
2. MONTHLY_CALLS and RESERVE must be present with nonzero integer — coupling made permanent, repo checks out branch and main's daily.yml is ancestor, so passes at merge, and PR can never merge into main whose workflow stops supplying cap
"""
import re
from pathlib import Path


def test_daily_yml_must_not_contain_staleness_days_env():
    yml_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "daily.yml"
    assert yml_path.exists(), f"{yml_path} missing"
    text = yml_path.read_text()
    # STALENESS_DAYS is a module constant (boggio.py:408) used as default kwarg (1093),
    # no _env_int binding — pasting it as env would be inert config that reads like control.
    # The comment "DO NOT add CARD_ENRICH_STALENESS_DAYS here" is allowed, but an env assignment is not.
    # So check for assignment pattern, not just substring.
    import re

    # Env assignment pattern: CARD_ENRICH_STALENESS_DAYS: <value> (with optional quotes)
    # We must NOT find such assignment
    assignment_pat = re.compile(
        r"^\s*EDGE_FACTORY_CARD_ENRICH_STALENESS_DAYS\s*:",
        re.MULTILINE | re.IGNORECASE,
    )
    # Also check for generic CARD_ENRICH_STALENESS_DAYS without prefix
    assignment_pat2 = re.compile(
        r"^\s*CARD_ENRICH_STALENESS_DAYS\s*:",
        re.MULTILINE | re.IGNORECASE,
    )
    assert assignment_pat.search(text) is None and assignment_pat2.search(text) is None, (
        "STALENESS_DAYS must not be in daily.yml as env var — it is a module constant, no env binding; "
        "pasting it would be inert config that reads like control. Comment mentioning it is ok, assignment is not. "
        "Two env lines only if lane enabled: MONTHLY_CALLS and RESERVE, but lane can stay off (cap unset) until operator chooses."
    )


def test_daily_yml_carries_card_enrich_monthly_calls_and_reserve():
    """Presence invariant — now that paste landed ('90'/'20' on main via ef94edf), it belongs in PR.

    Hardened regex: operator writing `: 90` unquoted is valid and would turn permanent invariant into permanent red if only quoted matched.
    Pattern: r\"EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS:\\s*'?(?:0*[1-9]\\d*)'?\"
    Accepts: '90', \"90\", 90, '026' (leading zeros ok, but nonzero), rejects 0, '0', empty.
    """
    yml_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "daily.yml"
    assert yml_path.exists(), f"{yml_path} missing"
    text = yml_path.read_text()

    # Hardened regex — handles quoted and unquoted, single or double quotes, optional spaces
    # Nonzero integer: 0*[1-9]\d* — allows leading zeros but not all zeros
    monthly_pat = re.compile(
        r"EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS:\s*'?(?:0*[1-9]\d*)'?",
        re.IGNORECASE,
    )
    reserve_pat = re.compile(
        r"EDGE_FACTORY_CARD_ENRICH_RESERVE:\s*'?(?:0*[1-9]\d*)'?",
        re.IGNORECASE,
    )

    # Also accept double-quoted variant — regex above handles single quote optional, but double quote needs handling
    # Use more permissive: optional quote char ' or " around number
    monthly_pat2 = re.compile(
        r'EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS:\s*["\']?(?:0*[1-9]\d*)["\']?',
        re.IGNORECASE,
    )
    reserve_pat2 = re.compile(
        r'EDGE_FACTORY_CARD_ENRICH_RESERVE:\s*["\']?(?:0*[1-9]\d*)["\']?',
        re.IGNORECASE,
    )

    # Check monthly
    m_monthly = monthly_pat.search(text) or monthly_pat2.search(text)
    assert m_monthly is not None, (
        "EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS not found with nonzero integer in daily.yml — "
        "operator paste '90'/'20' landed on main (ef94edf), branch must carry it to avoid revert on merge. "
        "Expected pattern: EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS: '90' or : 90 (quoted or unquoted nonzero)"
    )

    # Check reserve
    m_reserve = reserve_pat.search(text) or reserve_pat2.search(text)
    assert m_reserve is not None, (
        "EDGE_FACTORY_CARD_ENRICH_RESERVE not found with nonzero integer in daily.yml — "
        "two env lines required if lane enabled, plain literals '26'/'20' or '90'/'20', not secrets ref"
    )

    # Ensure STALENESS_DAYS still absent as env assignment (comment mentioning it is ok)
    import re as _re

    assignment_pat = _re.compile(
        r"^\s*EDGE_FACTORY_CARD_ENRICH_STALENESS_DAYS\s*:",
        _re.MULTILINE | _re.IGNORECASE,
    )
    assignment_pat2 = _re.compile(
        r"^\s*CARD_ENRICH_STALENESS_DAYS\s*:",
        _re.MULTILINE | _re.IGNORECASE,
    )
    assert assignment_pat.search(text) is None and assignment_pat2.search(text) is None
