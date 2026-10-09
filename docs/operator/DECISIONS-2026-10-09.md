# Decision record — 2026-10-09

## 1. Authority, provenance and scope

The operator requested: **transfer the decision record, fix the three sanitizer
formats test-first, then merge**.

This transfers the D1–D5 positions from the user-supplied decision text together
with the independently reproduced review dispositions. It is **not a verbatim
copy** of the other workspace's document: neither the cited revision `2f83c3e`
nor `docs/operator/DECISIONS-2026-10-09.md` could be retrieved from this repository
on GitHub (both lookups returned HTTP 404). Do not attribute this document's
review corrections to that unavailable revision.

The review was artifact-driven, **not blinded**: the supplied comparison values
were visible. Reproduction wins over supplied numbers. Unresolved findings stay
unresolved rather than changing a matcher until a desired count appears.

The figures below describe the review checkout anchored at
`70ca2b36829e694cccc7993acd4ff4c307bcdcaa`, with the previously reviewed fixes and
the authorized Kladno Config decision. The review's 990-file integrity comparison
found zero changes to that starting snapshot. Subsequent upstream pipeline-state
commits are not the measurement population; these counts are **snapshot-bound**,
not live-system constants.

Standing constraints remain:

- No emission exclusion or selector rewrite is authorized by these findings.
- No refit/retrain of incumbent `model_key=a45beab0c878`, lowered threshold,
  quorum, gate, or operational Phase5-era floor.
- No manual rewrite of historical picks or research ledger rows; no donor
  conflict auto-resolution. Only an explicit operator-verified decision may
  resolve its exact dated, oriented fixture through the reviewed settlement
  path, retaining capture-time fields and original conflict notes.
- No workflow files are staged or changed. Source retirement, vocabulary changes,
  price-coverage policy changes and credential/plan repairs remain separate
  operator decisions.

## 2. Transferred positions and reviewed disposition

| Decision | Transferred position | Reviewed disposition |
|---|---|---|
| **D1** | Separate ML/unanimous provenance in reporting; defer emission exclusion; Option B is unsafe. | **Retain cautious deferral.** The selector collision and Option B counterexample reproduce. Absence of a clean-band advantage is not established. Reporting must distinguish archived output provenance from whether inference ever ran. |
| **D2** | Canonical loader is correct/closed; 48 unsafe dates, 336 discarded additions, allegedly contiguous. | **Retain the current fail-closed loader; reopen closure wording.** The receipt and original material-field calculation reproduce. Contiguity is refuted; materiality depends on the frozen-field contract, and two name variants remain uncleared. No candidate additions are restored. |
| **D3** | Single-source price quality is universally binding, with a claimed roughly ten-point ROI effect. | **Retain the cross-family risk concern, not universal causal certification.** Different outcome populations do not isolate price inaccuracy; clean and quarantined counts and priced denominators must be shown separately. No new operational price-policy change is made. |
| **D4** | Fix all seven Forebet exception-detail loss sites, including the four CI paths. | **Seven-site diagnostic coverage confirmed.** The additional Token/Digest/AWS Authorization leaks were reproduced test-first and repaired with an opaque whole-header redactor; do not generalize these tests to every possible sensitive field. |
| **D5** | Kladno is a regulation-time draw; production wiring was alleged to be inert. | **Kladno decision retained; inert local wiring refuted.** Exact official/intraday commands use the default Config path and resolve both copied conflicts. Deployment execution remains unverified; the real ledger was not edited during the review. |

## 3. D1: mechanism, provenance and uncertainty

Read-only/in-memory probes against
[`picks_today.py`](../../scripts/picks_today.py) produced:

- Selector keys `[2, 3]`; current slot 3 selects `ml-meta avg_p>=55`.
- Excluding ML/fade entries only in memory selects
  `3way-unanimous avg_p>=65` for slot 3.
- No-model 70% fixture: current path returns an ML-labelled candidate;
  Option A returns a unanimous candidate; Option B returns **zero** candidates.
  Research callbacks are zero in those controls.
- Regular archive inventory: **1,013** ML-tagged rows, **336** with `ml_p`,
  **677** missing it (66.83%). Missing-field source counts:
  `{3:487, 4:142, 5:44, 6:4}`; fewer than three sources: **zero**.
- Genuine-model and fade output literals carry `ml_p`; the unanimous-path
  literal does not. The 336 present values had zero invalid probabilities and
  zero `avg_p`/`ml_p * 100` inconsistencies in the field check.
- **169** missing-field rows have duplicate-collapse metadata. A model/consensus
  two-row control collapses to one consensus row with `ml_p=None`. Consequently,
  absence of that archived field does not prove inference never ran.

The parser claim is conditional, not literal for any arbitrary substring:
`2way ml-meta avg_p>=55` parses as two-way; a threshold-less ML string returns
None. The current-registry collision above nevertheless reproduces.

### 3.1 Performance receipt

Canonical loading/deduplication precedes cohort filtering for
**2026-08-11–2026-10-08**: **1,090** deduplicated rows, **703** ML-tagged.
The [`native audit`](../../scripts/audit_recent_picks.py) extraction was validated
against real `build_report` populations: **1,040 overlay / 1,039 hybrid**.
Enhancement persistence was disabled for measurement; historical data were not
written.

Below are native-overlay matches plus operator-verified decisions. Hit intervals
are Wilson 95%; ROI intervals use 20,000 date-cluster bootstrap draws, seed
`20261009`. ROI uses finite decimal odds greater than 1. The source scores and
prices remain audit inputs, not certified truth merely because they matched.

| Cohort | Settled | Hit % [95% CI] | Priced | ROI % [95% CI] |
|---|---:|---:|---:|---:|
| All ML-tagged | 678 | 67.40 [63.79, 70.83] | 649 | -0.77 [-6.75, +5.41] |
| Missing `ml_p` | 438 | 66.44 [61.89, 70.70] | 430 | -0.39 [-7.91, +7.31] |
| Missing `ml_p`, below 65 | 306 | 60.46 [54.88, 65.77] | 302 | -3.38 [-11.94, +6.20] |
| Missing `ml_p`, at least 65 | 132 | 80.30 [72.70, 86.19] | 128 | +6.67 [-5.06, +17.07] |
| Has `ml_p` | 240 | 69.17 [63.06, 74.67] | 219 | -1.53 [-11.03, +8.19] |
| Has `ml_p`, at least 3 sources | 35 | 74.29 [57.93, 85.84] | 35 | +2.43 [-17.54, +21.93] |
| Below 65, literal NONE | 130 | 64.62 [56.08, 72.31] | 127 | +3.29 [-10.13, +18.04] |
| At least 65, literal NONE | 53 | 75.47 [62.43, 85.07] | 49 | +4.18 [-12.82, +20.69] |
| Has `ml_p`, literal NONE | 142 | 71.13 [63.19, 77.95] | 123 | -0.74 [-12.46, +10.37] |

Use literal `price_quarantine_reason == "NONE"`, not truthiness. NONE is a status,
not proof of a usable quote: the clean high band contains 53 settled but only
49 priced observations.

Clean high-minus-low ROI is **+0.90 percentage points**, interval
**[-21.05, +22.24]** under native overlay matching. Under native hybrid matching
it is **+3.12 points**, interval **[-18.77, +23.86]**. Neither establishes
positive edge, equivalence, or absence of advantage. The 336 discarded additions
are not graded by this canonical measurement. Raw below-65 inventory is not a
forecast of post-fix emission changes: other gates, model candidates and final
collapse still matter.

### 3.2 Settlement reconciliation stays open

| Matching/source method | Settled ML-tagged | Settled missing `ml_p` |
|---|---:|---:|
| Strict overlay | 677 | 437 |
| Native overlay | 678 | 438 |
| Native overlay plus warehouse | 677 | 437 |

With the matcher/population held fixed, adding warehouse facts produced zero
newly settled matches, one settled-to-ambiguous transition and one common score
disagreement: **Arsenal–Como, 2026-08-12, overlay 1–1 versus warehouse 2–1**.
No operator resolution was made for that disagreement.

The supplied **398-to-437** gap was not reproduced. Separate, explicitly labelled
identity-method controls changed counts substantially (literal matching gave
396 missing-field settlements; normalized nine-character matching gave 437).
They do not recover the unavailable reviewer's exact matcher or fact snapshot.
Do not attribute +39 to warehouse coverage without that evidence.

## 4. D2: archive and identity limitations

Actual canonical receipt: morning **969**, verified additions **5**, regular-only
**118**, unsafe dates **48**, empty dates **0**. Unsafe August 14–October 6 spans
**54 days**, omitting August 15–19 and September 30: **not contiguous**.

Original field changes reproduce: `avg_p=454`, `odds=441`, `sources_used=255`,
`edge_rule=153`, `bucket=97`, `away=14`, `home=11` across 669 changed matched keys;
no morning key was missing. Discarded additions: **336**.

| Materiality set | Material dates | Cosmetic dates | Candidate additions under relaxation |
|---|---:|---:|---:|
| Narrow selection/market/rule/bucket | 44 | 4 | 16 |
| Original ten fields | 48 | 0 | 0 |
| Broader bet-time evidence | 48 | 0 | 0 |

The four narrow-only dates are August 27, September 1, September 24 and October 1.
That narrow contract may describe unpriced selection inventory; it does not
establish frozen price/probability integrity for ROI. The 16 candidates are
**not approved official additions**. No loader relaxation is applied.

The **25 name-field changes occur in 18 matched rows** (11 home, 14 away).
Twenty-two share marker-preserving 24-character identities; three do not.
Benevento has a matching independent fixture witness; Drogheda United/Utd and
Borussia M'gladbach/Mönchengladbach remain uncleared. Zero differing squad markers
and zero confirmed genuine collisions do not prove that all names are benign.
The existing merge safety guard vetoed 13 name-changing rows, so equal short keys
must not be treated as identity certification.

## 5. D3: broad price exposure, not isolated price error

Native-overlay below-65 observations: **130 NONE / 176 quarantined**; quarantine
reasons are scoutingstats **170**, fuzzy alias **5**, fallback **1**. Clean versus
quarantined ROI is **+3.29% / -8.22%**, a descriptive **11.50-point** spread.
Hit rates also differ (**64.62% / 57.39%**); the 7.23-point hit-rate difference's
date-bootstrap interval spans zero. These are different pick populations, not
paired tests of price accuracy.

The wider June 18–October 8 native-hybrid diagnostic has 1,389 canonical rows,
1,323 settled, and five broad families with at least 30 settled observations:

| Family | Settled | Quarantined share | Clean ROI % | Quarantined ROI % |
|---|---:|---:|---:|---:|
| 2way + bookmaker confirmation | 33 | 30.30% | -30.48 | -2.20 |
| 2way | 444 | 31.31% | +1.87 | -7.94 |
| 3way | 123 | 9.76% | +10.81 | -55.33 |
| ML-meta tag, mixed output paths | 677 | 52.14% | +2.62 | -2.95 |
| OU25 | 46 | 76.09% | -8.70 | -16.54 |

These contrasts are descriptive, not causal or promotion evidence. The 3way
quarantined subset has only 12 observations; OU25 only 10 clean priced
observations. The first family's direction reverses the claim that clean
necessarily means better observed ROI. Widening this diagnostic does **not**
change the operational Phase5-era floor. Universal price-error or decision-grade
claims require paired same-fixture, same-time independent quote evidence.

## 6. D4: test-first Authorization repair

The seven original loss sites in
[`forebet.py`](../../src/edgefactory/sources/forebet.py) retain bounded, sanitized
reasons. The four mocked CI cloud paths are exercised with
`GITHUB_ACTIONS=true`; direct transport remains skipped in relay mode.

The adversarial review exposed three unsupported unquoted Authorization
formats: **Token, Digest and AWS4-HMAC-SHA256**. Synthetic values survived in
three of six initial attacks; no actual credential exposure was observed.

New regressions were added **before** the fix. Red-phase command:

```bash
PYTHONPATH=src /home/user/_work/.venv/bin/python -m pytest tests/test_forebet.py -q \
  -k 'complete_authorization_header or folded_authorization_value or redaction_marker_in_header or authorization_redaction_is_idempotent or each_cloud_path'
```

Result: **11 failed, 5 passed, 35 deselected**. Failures include all three
unquoted formats, repr/JSON Digest values, folded headers, attacker-supplied
redaction markers and the three CI-path cases.

The repair treats Authorization as an opaque complete value, not a whitelist of
schemes. It handles escaped repr/JSON values and unquoted lines with indented
continuations, including Digest comma parameters and AWS SignedHeaders
semicolons. Unquoted lines are deliberately consumed to the line boundary rather
than guessing which fragments are safe. The emitted non-assignment marker keeps
repeat sanitization idempotent without trusting a raw `[redacted]` marker.
Transport/status prefixes, distinct causes and existing 160/720-character bounds
remain covered.

Green command:

```bash
PYTHONPATH=src /home/user/_work/.venv/bin/python -m pytest \
  tests/test_forebet.py tests/test_refresh_result_sources.py -q
```

Result: **57 passed**. Coverage is in
[`test_forebet.py`](../../tests/test_forebet.py). This closes the reproduced three
formats, not every conceivable credential representation in every adapter.

## 7. D5: operator authority and exact default wiring

The authorized record in
[`Config/verified_results.json`](../../Config/verified_results.json) is
**Kladno–Banik Ostrava, 2026-09-23, regulation 1–1, draw, source_verified**.
Five verified rows load; three explicitly state 90-minute settlement; zero have
inconsistent score/outcome. Existing convention is also documented in
[`FINDINGS-2026-10-07.md`](FINDINGS-2026-10-07.md). The separately cited `d60f729c`
revision could not be verified locally; textual convention is not a general
machine-enforced period validator.

The unchanged production command factory, maintenance wrapper and actual CLI
were exercised in disposable data copies:

```bash
PYTHONPATH=src python3 scripts/ml_fade_research_eval.py --today 2026-10-09
PYTHONPATH=src python3 scripts/ml_fade_research_eval.py --today 2026-10-09 --settle-monitor-only
```

Each command exited zero and settled **both** copied Kladno conflicts as
draw/source_verified through the default Config path. Removing only the Kladno
record left **both conflicted**. The copied real state naturally had no
checkpoint due; no policy or gate was suppressed. Capture-time fields and original
conflict notes were retained. The real ledger remained unchanged at SHA256
`3e8eb940382e3e7b714b40eec4bebe405a3b40fbc5058b52ce32214ac4064e4f`.

The existing command unit test has zero exact-equality assertions. Its coverage
gap does not make the default path inert. A controlled `run_soft` exit-7 probe
retained the child diagnostic, printed a warning and continued. Actual deployed
settlement execution remains unverified; do not retry the inaccessible historical
GitHub logs/artifacts or select a donor score automatically.

## 8. Earlier claim corrections and follow-up evidence

- **C8.1:** two loss sites refuted: seven original sites covered.
- **C8.2:** 1,012 is not an invariant: this review measured 1,013 regular ML-tagged
  rows; retain snapshot/loader definitions with every count.
- **C8.3:** A=B refuted: the 70% no-model candidate survives A, not B.
- **C8.4:** model decay is not the firing-label counter. The model-key export
  guard rejects the absent export; registry has zero `fired_last` fields.
- **C8.5:** the identified consensus path does not feed research: 2,416 ledger
  rows (1,301 parents, 1,115 fades), zero missing `ml_p`, zero consensus callbacks.
- **C8.6:** twelve reference files are not twelve demonstrated metric errors.
  The inventory includes a pure producer with two writes/zero reads, reporting,
  context routing, identity/export and formatting. Six reader controls propagate
  the recorded label; the firing window is 199 rows, 160 missing `ml_p`.
  OU25's goals criteria admit 268/677 missing-field rows; that alone is not proof
  of corrupt model-performance evaluation.

Evidence needed to change the open dispositions:

1. **D1:** source-reconciled prospective clean-price contrasts with enough
   precision to distinguish the bands; keep gates/model fixed.
2. **D2:** an explicit frozen-field contract and independent dated fixture IDs
   clearing the remaining identities and any proposed recovered additions.
3. **D3:** paired independent quotes separating price error from pick composition.
4. **D4:** extend regression coverage for newly reproduced sensitive formats
   before modifying redaction; green existing tests are not blanket safety proof.
5. **D5:** exact command-string assertions and an authorized observable deployed
   run using the verified Config decision; do not manually edit the ledger.

## 9. Release boundary

Merge includes the previously reviewed read-only coverage probe, bounded source
error reporting, entity-registry date/header validation, seven-site Forebet
reason preservation, explicit operator-only conflict settlement/default Config
plumbing and authorized Kladno Config record, their regressions, this decision
transfer and the test-first Authorization repair. It does not introduce the
proposed emission exclusion or reporting-cohort implementation, modify workflow
files, change model/threshold/gate policy, or rewrite historical data.

Full-suite and merged-tree validation results are recorded with the pull
request. Large probes, scratch databases and disposable copied ledgers remain
outside Git. Future pipeline-state updates on main are not authored or rewritten
by this patch.
