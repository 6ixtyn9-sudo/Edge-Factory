# Card Enrich H2H — deterministic `captured_at` — FINAL RECEIPT (2026-10-11)

**Base:** `origin/main` @ `b033de9`, verified live this session (git), with the workflow/env facts re-read from that commit.
**Change set under review: 2 files** — `scripts/capture_card_enrich.py` (the fix, 3 hunks) and this receipt.
**`.github/` diff vs `origin/main`: 0 files.** No workflow file is added, edited, or pasted by this change; both env literals (`'90'`, `'20'`) already live on `origin/main`.
**Vendor calls: 0.** Every command below is offline (fixtures, faked transports, temp dirs); the only network reads are read-only `git` verifications against the already-fetched base.
**Ledger delta: 0** for the cited runs — byte-identical hashes in §3.6, which also reports one pre-existing, out-of-scope observation found while proving it.

> Superseded history: the previous revision of this file (pre-merge gates B1-B4, branch-paste narrative, its own SHA corrections) is preserved in git history at the base commit above. It is **not** current verification and nothing in it is relied on here. Every claim in this file was executed against the live base on 2026-10-11; where a claim has a limit, the limit is written next to it.

---

## 1. Defect, reproduction, fix

The lane stamps every snapshot with `captured_at`, and its own parser turns that stamp
into eligibility: `src/edgefactory/sources/boggio.py:1042` sets

```
usable = bool(identity_hits and kickoff is not None and capture is not None and capture < kickoff)
```

with `captured_at_or_after_kickoff` as the refusal reason (`boggio.py:1050-1051`).
Before this fix, `execute()` read that stamp from the wall clock while the plan that
authorised the spend already used an **injected** clock. Consequence: the same script,
same fixtures, same budget — different result depending only on the hour the runner
woke up. A run after the first kickoff pays for rows its own pre-kickoff rule discards.

**Reproduction (live, this session).** Wall clock was `2026-10-11T14:22Z`; the fixture
card's first kickoff is `14:00Z`, so the stamp is 22 minutes past the boundary:

```
$ PYTHONPATH=src .venv/bin/python -m pytest \
    tests/test_card_enrich_h2h.py tests/test_bootstrap_and_inertness.py \
    tests/test_card_enrich_env_invariant.py -q
1 failed, 48 passed

>   assert "mode=execute calls_spent=2 usable_snapshots=1" in out
E   AssertionError: ... 'mode=execute calls_spent=2 usable_snapshots=0 ledger_entries=2 ...'
tests/test_card_enrich_h2h.py:435: AssertionError
```

**After the fix, same command, same wall clock:** `49 passed in 0.24s`.

**The fix (only production-code change; the receipt is the only other file):**

```
diff --git a/scripts/capture_card_enrich.py b/scripts/capture_card_enrich.py
index 9f9619f..01d1717 100644
--- a/scripts/capture_card_enrich.py
+++ b/scripts/capture_card_enrich.py
@@ -264,12 +264,19 @@ def plan_run(day: str, *, localdata: Path, limit: int,
             "need_h2h": need_h2h, "need_listing": need_listing}
 
 
-def execute(day: str, plan: dict, *, localdata: Path, log=print) -> dict:
-    """Pay for the plan, in pre-flight order, one ledger line per call."""
+def execute(day: str, plan: dict, *, localdata: Path, log=print,
+            now: datetime | None = None) -> dict:
+    """Pay for the plan, in pre-flight order, one ledger line per call.
+
+    ``now`` is the observation clock, injectable for the same reason as in
+    ``main``: the stamp written here is what ``parse_head_to_head`` compares
+    against the kickoff to decide ``usable``, so a run whose clock is read from
+    the wall would pay for rows its own pre-kickoff rule then discards.
+    """
     results = {"calls": 0, "usable": 0, "statuses": [], "unattributed": [], "local_blocks": 0}
     budget = dict(allowed=plan["preflight"]["allowed_calls"])
     entries = boggio.read_call_ledger(localdata)
-    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
+    captured_at = (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")
     listing_ids: dict[tuple[str, str], dict] = {}
 
     # A listing call is only worth paying if a call it unlocks also fits in the
@@ -500,7 +507,7 @@ def main(argv=None, *, now=None) -> int:
               f"allowed={plan['preflight']['allowed_calls']} max_requests={args.max_requests} "
               f"note=refusing an unplanned burst; lower the budget or raise the cap deliberately")
         return 0
-    results = execute(day, plan, localdata=localdata)
+    results = execute(day, plan, localdata=localdata, now=now)
     path = boggio.persist_snapshots(day, plan["snapshots"], plan["preflight"], localdata=localdata,
                                     notes=[f"need_h2h={plan['need_h2h']}",
                                            f"unresolved={len(plan['unresolved'])}"])
```

### Why this is deterministic and why production is unchanged

* `main(now=...)` already existed for the freshness guard (`pre_kickoff`). The fix is to
  hand the *same* clock to the spend path, so planning and stamping cannot disagree.
* Hard proof — wall clock faked six hours **past** kickoff, injected clock pinned
  pre-kickoff, real execute path with the fake transport:

```
rc=0 wall_clock_faked=2026-10-11T20:00:00+00:00 injected_now=2026-10-11T04:00:00+00:00
usable_line_present: True
ineligible_line_present: False
snapshot_captured_at: 2026-10-11T04:00:00+00:00
snapshot_usable: True | identity_verified: True
PROOF OK: captured_at follows the injected clock, not the faked wall clock
```

* Negative control — `now=None` (the production call shape), wall clock faked to
  `12:00Z`:

```
rc=0 wall_clock_faked=2026-10-11T12:00:00+00:00 injected_now=2026-10-11T04:00:00+00:00
snapshot_captured_at: 2026-10-11T12:00:00+00:00
CONTROL OK: with now=None the stamp IS the faked wall clock (12:00Z), diverging from the injected 04:00Z
```

So production behaviour is unchanged (wall clock when nothing is injected) and test
behaviour is fully controlled (injected clock wins). The failure mode this closes is
time-rot: the suite would have gone red on its own the moment its card day started,
with no code change to blame.

---

## 2. Diffstat and per-file justification

```
 docs/operator/card-enrich-wiring-receipt.md | 675 +++++++++++++++++++++-------
 scripts/capture_card_enrich.py              |  15 +-
 2 files changed, 525 insertions(+), 165 deletions(-)
```

### `scripts/capture_card_enrich.py` — why each line moved (justification begins here)

* **`def execute(day, plan, *, localdata, log=print, now: datetime | None = None)`** —
  `now` is keyword-only and defaulted, so the one existing caller (`main`) stays
  source-compatible and the production default is still "read the wall clock". No
  positional-argument contract is broken for any embedder or future script that
  imports `execute` directly.
* **The docstring added under it** — records *why* the parameter exists, in the file
  with the bug: the stamp written here is what `parse_head_to_head` compares against
  the kickoff, so a wall-clock read pays for rows the lane's own pre-kickoff rule then
  discards. The defect was an undocumented clock dependency; the fix documents the
  dependency next to the code that owns it. No SHA, branch name, or environment
  detail is embedded in it.
* **`captured_at = (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")`** —
  the format is unchanged (`isoformat`, `timespec="seconds"`, UTC offset), so every
  persisted snapshot keeps its schema and every downstream parser sees the same shape.
  The single difference is *which* clock supplies the instant. `now` is an aware
  `datetime` (the same type `main` and `plan_run` already take), so no string-vs-object
  ambiguity is introduced and no timezone guessing happens downstream.
* **`results = execute(day, plan, localdata=localdata, now=now)` in `main`** — one
  clock now drives both halves of the run: the plan's `pre_kickoff` freshness decision
  and the snapshot stamp. Those two disagreed before, and the disagreement was the bug.
  In production `now` is `None`, so the fallback branch runs and behaviour is
  byte-identical to before for every scheduled run.
* **What was deliberately *not* changed** — no endpoint, URL whitelist, budget,
  reserve, monthly cap, ledger write, listing logic, staleness window, or preflight
  arithmetic moved; no new environment variable was introduced; no vendor call was
  added or removed; the `--execute` gate, `run_ceiling` guard, fail-closed
  `budget_disabled` path and `lane_blocked_local` accounting are untouched. The diff
  is a clock hand-off and its justification, nothing else.
* **Why not "fix" the parser instead** — `parse_head_to_head` is correct: comparing an
  observation stamp against the kickoff is exactly the point-in-time discipline the
  lane exists to enforce (`test_capture_at_or_after_kickoff_is_ineligible_not_repaired`,
  `test_missing_kickoff_stamp_fails_closed`). The defect was the caller's clock read,
  so the caller is the fix.
* **Why not widen the tests instead** — the tests already inject `now` everywhere; two
  of them pin a *post-kickoff* run on purpose
  (`test_a_card_whose_fixtures_have_kicked_off_is_refused_not_billed`). Moving fixture
  dates forward would hide the product defect, rot again on the next date, and leave
  the production lane stamping spend with a clock that disagrees with its own plan.
* **Why an explicit parameter rather than reading `now` out of `plan`** — the plan dict
  is data; threading the clock through it would create implicit coupling and tempt
  future readers to trust a data field as a clock. `now=` matches the idiom already
  used by `main` and `plan_run`, so there is one convention in the file, not two.
* **Determinism evidence for these exact lines** — §1's faked-wall-clock proof (stamp
  follows the injected clock with the wall clock six hours past kickoff) and its
  negative control (`now=None` stamps the wall clock, as production must).

### `docs/operator/card-enrich-wiring-receipt.md` — why the receipt is rewritten

* **Replacement, not an append.** The base revision of this file carried a pre-merge
  gate narrative (B1-B4), a fabricated-SHA correction, and pasted test bodies that no
  longer match the tree — including a duplicated twin regex for the same key and a
  branch SHA inside a docstring. Appending a new section above that would leave one
  file containing two mutually exclusive accounts of the same lane, with no way for a
  reader to tell which lines are current. A receipt's only value is knowing which
  claims are live.
* **Nothing is lost.** The superseded content is preserved in git at the base commit
  (this is a tracked file; `git show <base>:docs/operator/card-enrich-wiring-receipt.md`
  still resolves it). The header of the new receipt says so explicitly.
* **Every number re-executed.** All commands, hashes, outputs and test names pasted
  here were run against this tree today; the test-name list is the collector's output,
  not a retyped table. Where a limit exists (PyYAML absent from `requirements.txt`,
  the key-ring ledger leak, the ignored e2e file, lane dormancy) the limit is written
  next to the claim instead of being sanded off.
* **Required content, each verifiable in place:** the diffstat with per-file
  justification; ledger delta 0 with before/after hashes; facet parity (provider AND
  recomputed, WARN on divergence, fail-closed); the 49 named tests; priced decisions
  (900 vs 24/month vs cap 90 vs pot 200); the matrix row; the `.github` diff-0 proof;
  the `yaml.safe_load` proof; the prune proof; and the cap stated as 90, not 26.
* **Hygiene properties kept:** no branch SHA and no fabricated SHA anywhere (the only
  commit named is the real base, in the header prose); a single hardened regex per env
  key with no duplicate twin; the `yaml.safe_load` check retained; branch names and
  session identifiers kept out of quoted code and docstrings.

---

## 3. Verification (commands and real output)

### 3.1 The 49 named tests

Command:

```
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/test_card_enrich_h2h.py tests/test_bootstrap_and_inertness.py \
  tests/test_card_enrich_env_invariant.py -q
49 passed in 0.24s
```

The 49 named tests (names as collected, not titles):

tests/test_card_enrich_h2h.py (37):
  test_documented_contract_yields_the_dormant_feature_and_drops_offside_rows
  test_encounter_dates_must_precede_the_target_kickoff
  test_dated_rows_carry_an_as_of_that_is_an_observation_time_not_a_match_date
  test_capture_at_or_after_kickoff_is_ineligible_not_repaired
  test_missing_kickoff_stamp_fails_closed
  test_payload_about_other_clubs_is_unverified_identity
  test_garbage_payloads_never_become_features
  test_snapshot_satisfies_the_dormant_predicate_schema_but_activates_nothing
  test_ranking_is_by_margin_and_skips_below_threshold_and_squad_pairs
  test_one_call_budget_per_fixture_not_per_market_row
  test_limit_bounds_the_slate_selection
  test_quota_header_parsing_and_opaque_pool_labels
  test_h2h_endpoint_whitelist_rejects_any_other_id_shape
  test_budget_unset_fails_closed_even_with_a_full_pool
  test_unmeasured_pool_gets_no_allowance
  test_monthly_cap_spans_both_pools_and_reserve_is_held_for_production
  test_month_spend_depletes_the_allowance_across_runs
  test_ledger_prunes_to_its_retention_window
  test_staleness_skip_suppresses_a_second_call_inside_the_window
  test_plan_mode_never_calls_the_transport
  test_nothing_to_capture_still_prunes_twenty_day_shadow_file
  test_listing_is_auto_credited_only_when_preflight_can_pay_for_h2h_too
  test_paid_listing_is_not_repeated_on_the_same_date
  test_execute_pays_at_most_the_pre_flight_allowance_and_ledgers_every_call
  test_execute_stops_when_the_budget_says_zero_and_spends_nothing
  test_a_refusal_still_costs_a_ledger_line
  test_a_transport_failure_is_still_attributed_to_a_named_pool
  test_run_ceiling_refuses_an_unplanned_burst
  test_pre_flight_count_equals_what_the_run_actually_pays
  test_a_tight_budget_degrades_the_plan_and_never_overspends_it
  test_failed_listing_consumes_its_preflight_unit_before_h2h_calls
  test_a_refusal_we_caused_ourselves_must_not_be_paid_for_twice
  test_contacted_listing_failure_spends_one_planned_unit
  test_local_h2h_block_does_not_spend_or_write_a_receipt
  test_first_run_auto_pays_for_one_listing_before_attempting_h2h
  test_a_card_whose_fixtures_have_kicked_off_is_refused_not_billed
  test_no_context_rule_is_registered_and_no_lane_is_wired_into_the_pick_path
tests/test_bootstrap_and_inertness.py (10):
  test_production_listing_seeds_ledger_with_charged_false_and_real_header
  test_charged_false_does_not_move_allowance
  test_bootstrap_run1_may_refuse_run2_must_capture
  test_falsifications_budget_disabled_and_unattributed_quota
  test_capability_fixture_6encounters_2competitions_mixed_first_half
  test_differential_inertness_production_builder_byte_identical
  test_bootstrap_default_path_seed_file_then_preflight_without_handfed_observed
  test_previous_month_header_does_not_authorize_a_new_month
  test_d2_fail_closed_dominance_withheld_on_rate_divergence
  test_dead_snapshot_must_not_block_capture
tests/test_card_enrich_env_invariant.py (2):
  test_daily_yml_must_not_contain_staleness_days_env
  test_daily_yml_carries_card_enrich_monthly_calls_and_reserve

### 3.2 Full suite

```
$ PYTHONPATH=src .venv/bin/python -m pytest --ignore=tests/test_e2e_backtest.py -q
2698 passed in 77.43s
```

`tests/test_e2e_backtest.py` is ignored exactly as in prior receipts: it is the live
end-to-end file the repo already excludes from this measurement.

### 3.3 `.github/` diff is 0 — proof

```
$ git diff origin/main -- .github/ --stat
            (empty — no files)
$ git status --porcelain
 M scripts/capture_card_enrich.py
 M docs/operator/card-enrich-wiring-receipt.md
```

No workflow file appears in either command. The cap/reserve come from the base commit,
not from this change, so there is nothing to clobber and no paste in this PR.

### 3.4 Cap is 90, not 26 — and the YAML parse proof

`origin/main`'s `.github/workflows/daily.yml` lines 51-52, verbatim:

```
      EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS: '90'
      EDGE_FACTORY_CARD_ENRICH_RESERVE: '20'
```

Plain literals, quoted strings, under `jobs.run-autonomous-agent.env` — not a secrets
reference, not `26`. Parsed, not grepped:

```
$ .venv/bin/python -c "import yaml; d=yaml.safe_load(open('.github/workflows/daily.yml')); ..."
MONTHLY_CALLS = '90'
RESERVE       = '20'
keys found    = ['EDGE_FACTORY_CARD_ENRICH_MONTHLY_CALLS', 'EDGE_FACTORY_CARD_ENRICH_RESERVE']
```

**Honest caveat (found while proving the above).** The env-invariant test wraps its YAML
block in `try: import yaml ... except ImportError: pass`, and PyYAML is **not** in
`requirements.txt` — a clean `pip install -r requirements.txt` (exactly what the CI
regression job runs) does not provide it:

```
$ python3 -m venv /tmp/probe_venv && /tmp/probe_venv/bin/pip install -q -r requirements.txt
$ /tmp/probe_venv/bin/python -c "import yaml"
PyYAML ABSENT from requirements-only install
$ PYTHONPATH=src /tmp/probe_venv/bin/python -m pytest tests/test_card_enrich_env_invariant.py -q
2 passed          # regex path only; the YAML block silently no-ops
$ PYTHONPATH=src .venv/bin/python -m pytest tests/test_card_enrich_env_invariant.py -q
2 passed          # PyYAML 6.0.3 present; the YAML block really executed
```

So the regex invariant is always enforced; the YAML-parse invariant is enforced in any
environment with PyYAML (including the one used for the proof above) and is inert in
CI's regression job. This receipt keeps the check (it is real and passing) and reports
the gap rather than implying the stronger thing. Fixing it means one line in
`requirements.txt` — out of this change's 2-file scope, listed in §7.

### 3.5 Prune proof (14 days, and it runs even when the lane buys nothing)

Code, `src/edgefactory/sources/boggio.py:1206-1223`:

```
def prune_snapshots(day, *, localdata=None, retention_days=14):
    """Prune old day-scoped H2H snapshots, even when today's run buys nothing."""
    ...
            if file_date < cutoff:
                old_file.unlink()
```

Call sites: `boggio.py:1250` (inside `persist_snapshots`) and
`scripts/capture_card_enrich.py:440` (before planning, so a no-capture or refusal day
still prunes). Live demonstration, this session:

```
removed = 1
left    = ['card_enrich_shadow_2026-10-05.json', 'card_enrich_shadow_2026-10-11.json']
PRUNE PROOF OK: 20-day-old pruned, 6-day-old and today kept, retention=14
```

Regression test: `test_nothing_to_capture_still_prunes_twenty_day_shadow_file`, part of
the 49. The ledger and the surviving snapshots are preserved through cleanup by
`PHASE5_CLEAN_EXCLUDES` (`scripts/phase5_persistence.py:26-33`, wired into
`git clean -fd localdata/ ... -e <pattern>` at line 190), and the whitelist negations
`.gitignore:101`/`:113` keep them tracked.

### 3.6 Ledger delta 0

Method: hash the tracked ledger before and after the cited 49-test run.

```
before=e7095bb6b0cdfb4347a5905ddf14ace649ed6c1683e18df50df1ff9e3b8ff6f4
after =e7095bb6b0cdfb4347a5905ddf14ace649ed6c1683e18df50df1ff9e3b8ff6f4
$ git status --porcelain localdata/
            (empty)
```

**Out-of-scope observation, reported not fixed.** A *full-suite* run mutates the tracked
ledger once, via an untouched, pre-existing test: `tests/test_boggio_key_ring.py:38`
calls `boggio.get_json(boggio.predictions_url(...))` with no `localdata=`, so it uses the
repo default and appends one `charged:false` bootstrap line
(`boggio.py:119-131`, `what_it_bought=production_boggio_listing`). Reproduced by running
that single file against a restored ledger. It is unrelated to this change, invisible to
the 49-test run, and fixing it (pass a tmp dir) is a third file — left for the operator
in §7. The ledger in the delivered tree is byte-identical to `origin/main`'s.

### 3.7 Paste body — the surviving env-invariant tests, not the title

Names and bodies match; nothing here is a green no-op. Quoted from
`tests/test_card_enrich_env_invariant.py` in the delivered tree:

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

Note the property the earlier revision was missing: **one** regex per key. The quote
class `["\']?` handles `'90'`, `"90"` and bare `90` in a single pattern, so there is no
second twin pattern to drift out of sync. There is no branch SHA anywhere
in these docstrings — the only commit this receipt names is the real base in the header.

---

## 4. Facet parity — provider AND recomputed, WARN on divergence, fail-closed

The snapshot keeps the provider's published facets verbatim and *also* recomputes them
from the kept encounters, comparing the two (`boggio.py:806-829`):

* shares (`over_05/15/25/35`, `both_teams_scored`): compared against
  `h2h_*_share_recomputed`; `diff > 0.35` with ≥3 usable encounters appends a
  `divergence <field>: provider_share=... recomputed=... diff=...` warning. The
  recomputed value is kept and flagged — the provider's series is not silently trusted,
  and the disagreement is recorded rather than rounded away.
* W-D-L rates: `boggio.py:1015-1023` — `diff > 0.35` on either side appends a
  `W-D-L divergence (rate)` warning **and withholds `h2h_dominance`** (fail-closed:
  `features.pop("h2h_dominance", None)`).
* Fail-closed path is itself tested: `test_d2_fail_closed_dominance_withheld_on_rate_divergence`.

The provider's `overall` block is retained verbatim for audit; the lane's usable feature
set is the recomputed one, which is what a later certification would consume.

---

## 5. Priced decisions (the four numbers, stated with their meaning)

| Number | What it is | Arithmetic |
|---|---|---|
| 900/month | Unbounded worst case the spec forbids | 6 calls/run × 5 runs/day × 30 days |
| 24/month | What the lane is *shaped* to need | 4 weekly runs × 6 = 24 (+buffer ≈ 24-30), i.e. spread, not burst |
| cap **90** | The deployed ceiling, operator ruling (`daily.yml:51`) | 90/6 = 15 runs ≈ 3 days at daily cadence, then `budget_exhausted` |
| pot ~200 | The shared family's monthly headroom | 100/key/month × 2 pools − RESERVE 20/key ≈ 160 spendable |

Reading: the cap is a **ceiling, not a target** — the lane still spends only its
per-run need (≤6 H2H, plus at most one listing, and staleness skips suppress repeat
calls), so a 90 cap authorises at most the 24-ish calls the weekly shape wants and
bounds any accidental daily cadence. 26 was the tight weekly-fit number; the operator
ruled 90/20 as plain literals, and on a 200-pot the cap can never bind harder than the
header allowance already does. Deployed values are `'90'`/`'20'` (verified in §3.4);
`boggio.py:396` records the same sizing in code ("100/key/month family, ~24-30 does at
weekly cadence with staleness skips") and the persisted snapshot carries the matching
cadence note (`boggio.py:1236`).

---

## 6. Matrix row

`docs/operator/SOURCE-INTERROGATION-MATRIX-2026-10-10.md:188`:

> | card_enrich, weekly top-6, H2H-only, staleness-skip | 6 H2H + 0-1 listing = **~7 per run, 4 runs = 24-30** | fits inside B's 99 alongside production | combined ~105 -> exceeds ONE pool (100), fits the DOUBLED pool (200) |

That row is why the lane is specified weekly, why the cap exists, and why the
fail-closed default is 0 with no env (`boggio.py` `month_budget()`), which the suite
pins with `test_budget_unset_fails_closed_even_with_a_full_pool` and
`test_falsifications_budget_disabled_and_unattributed_quota`.

---

## 7. Open items for the operator (facts, not asks)

1. **Merge decision:** this change is 2 files, no workflow file, operator merges.
2. **PyYAML gap (§3.4):** the YAML-parse invariant is inert in the CI regression job
   because `requirements.txt` has no PyYAML. One line fixes it; it is deliberately not
   in this 2-file diff.
3. **Ledger leak (§3.6):** `tests/test_boggio_key_ring.py` writes one `charged:false`
   bootstrap line into the tracked `localdata/` ledger during a full-suite run. Also
   deliberately out of scope; the delivered ledger is byte-identical to the base.
4. **Dormancy unchanged:** with the cap unset the lane still captures nothing
   (`verdict=budget_disabled`); with `'90'`/`'20'` on `main` it is live on the next
   scheduled run. This change touches none of that.
