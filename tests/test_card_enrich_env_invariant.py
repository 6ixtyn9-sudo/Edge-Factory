"""Regression guard: daily.yml must NOT contain inert STALENESS_DAYS env.

Follow-up Round 2 corrections:
- Previous version asserted MONTHLY_CALLS present nonzero + arithmetic 150 <= cap.
  That assertion was INVERTED: it required production's ~150 listing calls/month
  (charged:false BY DESIGN, spend_by_key() ignores them) to fit inside enrichment
  lane's budget — coupling wrong quantities, pushing cap to 200.
- Cap 200 is not a limiter: family pot =100/key/month minus RESERVE 20/key = ~160
  headroom, so cap 200 never binds, binding moves to header allowance, guard cannot fail.
- Previous invariant was permanently red (agents never touch workflow files, manual paste
  lives only one cycle because daily persist commits localdata not .github/workflows),
  training suite to ignore real signals.
- Correct fix: keep ONLY assertions repo controls — STALENESS_DAYS absent is pure
  regression guard, correct, in-repo, cannot rot. Drop presence/nonzero/env-coupling.
- If fail-closed-by-default (no cap => lane off) is unwanted, clean move is module-level
  default in month_budget() with one-line comment — but note it weakens deliberate
  "a capture that cannot prove its budget may not spend" rule, so propose as operator decision,
  not as fix.
- Cadence choice (operator): cap=26 + weekly-ish (4 runs x6 =24, best fit for n>=30
  capture-dates bar, ~26 with buffer) OR cap unset + lane stays off. No paste needed for merge.

This test now only asserts STALENESS_DAYS absent.
"""
from pathlib import Path


def test_daily_yml_must_not_contain_staleness_days_env():
    yml_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "daily.yml"
    assert yml_path.exists(), f"{yml_path} missing"
    text = yml_path.read_text()
    # STALENESS_DAYS is a module constant (boggio.py:408) used as default kwarg (1093),
    # no _env_int binding — pasting it would be inert config that reads like control.
    assert "CARD_ENRICH_STALENESS_DAYS" not in text, (
        "STALENESS_DAYS must not be in daily.yml — it is a module constant, no env binding; "
        "pasting it would be inert config that reads like control. Two env lines only if lane enabled: "
        "MONTHLY_CALLS and RESERVE, but lane can stay off (cap unset) until operator chooses."
    )
