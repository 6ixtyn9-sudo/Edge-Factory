# Review proposal: separate ML and consensus provenance before changing selection

**Date:** 2026-10-09 (SAST)  
**Revision:** 4 — updates current reviewer verdicts and pins source-version attribution (see §12)<br>
**Status:** AUDIT DESIGN: APPROVE WITH CHANGES; LIVE ROUTING: NOT APPROVED FOR ACTIVATION  
**Review baseline:** commit `01f580c1f41b78883d7c807e354ba76903bbd026`  
**Session branch:** `arena/11e63d6d-edge-factory`  
**Implementation in this proposal:** documentation only. No production code, model, threshold, ticket, archive, or workflow changes.

## 1. Decision requested

Review a staged correction to a confirmed collision between the ML rule selector and the ordinary unanimous-consensus selector.

**Recommendation:** approve **sidecar-only** provenance instrumentation, distinct signal identities, and an offline/shadow comparison first. Do **not** yet approve a live consensus-floor change, a new electorate, a replacement model, or a new deduplication policy. Approve live routing only after those semantics and their downstream effects are reviewed.

The intended end state is:

1. An ML rule can qualify a selection only through matching model inference.
2. A consensus rule can qualify a selection only through an explicitly supported consensus predicate and electorate.
3. When both support the same selection, one operational pick can retain both independent evidence records without double-counting a bet.
4. Reports distinguish model probability, source average, qualifying threshold, and legacy/unknown provenance.

**Implementation approval:** none yet. The design disposition is conditional, not evidence that audit parity tests passed. See the [acceptance checklist](CHECKLIST-ML-CONSENSUS-PROVENANCE-2026-10-09.md).

**Expected benefit:** better correctness, explainability, and evaluation. **Unproven benefit:** higher hit rate, ROI, or bankroll growth. This proposal must not be justified as a guaranteed profitability improvement.

## 2. Why review is needed

The supplied GitHub Actions log for run `37896531094` shows apparent contradictions such as:

- PSV Eindhoven–Heerenveen: `ML-META≥55`, displayed probability approximately 80%.
- Zlin–Slavia Praha: `ML-META≥55`, displayed probability approximately 78%.
- FC Nordsjaelland–Odense: `ML-META≥60`, displayed probability approximately 61%.
- Cork City–Finn Harps: `ML-META≥80`, displayed probability approximately 85%.

A threshold label is not itself a prediction: a 63.5% model score legitimately clears the 60 tier. However, in this codebase the same ML label can also come from a **non-ML emission path**, and `avg_p` then means something different.

The current genuine ML path already selects the highest qualifying certified tier. The problem is not solved by changing that loop again or blindly relabelling all 78% rows as ML≥65.

## 3. Evidence and limits

### 3.1 Direct code observations

| Location | Observed behaviour | Consequence |
|---|---|---|
| [`scripts/picks_today.py`](../../scripts/picks_today.py), `_edge_entry()` | An `ml-meta` entry without an N-way token receives `n_way=3`. | Model rules enter the key space used by source-count consensus selection. |
| Same file, `load_thresholds()` and `_prefer_entry()` | Certified 1X2 entries share slots by N-way; unqualified rules take precedence over qualified variants; the lower threshold wins within that preference. | The current three-source slot is owned by `ml-meta avg_p>=55`. |
| Same file, `eval_1x2()` ML emission | Computes `ml_p`, selects the highest qualifying certified ML threshold, writes `ml_p`, and sets `avg_p = ml_p * 100`. | Genuine model output currently uses tiers 55, 60, 65, and 80. |
| Same file, `eval_1x2()` consensus emission | Requires agreeing available voters, uses `thr_for(len(used), t1x2)`, gates on `mean(ps) * 100`, and copies the selected entry's rule. It does not write `ml_p`. | A source-average-qualified pick can be called ML-META≥55. |
| Same file, `_representative_score()` / `_with_duplicate_metadata()` | Picks one representative by a tuple including context, price, `w_score`, and `avg_p`; retains alternate rule labels, but not full per-path inference evidence. | A consensus representative can obscure a separately emitted ML signal. ML logit and consensus vote weight are not comparable scales. |
| [`src/edgefactory/util.py`](../../src/edgefactory/util.py), `honest_display_label()` / `heal_ledger_labels()` | Rebuilds the display label from `edge_rule`/`rule`. | A cosmetic edit of `display_rule` alone will be undone; the stored rule/provenance needs attention. |

The current local dated archive corroborates the mechanism: Nordsjaelland has `ml_p=0.6071` and an ML≥60 rule, while Galatasaray and Corvinul carry ML≥55 rules but no `ml_p` field. This archive is a snapshot, **not** asserted to be byte-identical to the supplied run's final artifact.

**Important distinction:** missing archived `ml_p` does not prove inference never ran. A model candidate can have been emitted separately and then lost as the representative during collapse. Record emission-path provenance directly rather than infer it from missing fields.

**Explicit finding:** archived `avg_p` is semantically overloaded: model output uses model probability ×100; consensus output uses a source average ×100. They share percentage units but not calibration or meaning. Untyped pooled archive cuts on `avg_p` can mix these estimands; higher source average does not imply higher model confidence. This does **not** mean every historical ROI figure is mixed: verified model-prediction exports and explicitly provenance-stratified cohorts require separate treatment.

### 3.2 Existing repository review — not newly reproduced here

[`DECISIONS-2026-10-09.md`, §3](DECISIONS-2026-10-09.md) already reports:

- Current selector keys `[2, 3]`, with slot 3 selecting ML≥55.
- Excluding ML/fade entries **in memory** makes slot 3 select `3way-unanimous avg_p>=65`.
- A no-model 70% control emits an ML-labelled candidate under the current path, a unanimous candidate under separated routing, and **no candidate** under the reviewed blanket-suppression alternative.
- 1,013 ML-tagged regular archive rows: 336 with `ml_p`, 677 without it; 169 missing-field rows have duplicate-collapse metadata.

Its native-overlay historical performance receipt includes:

| Archived cohort | Settled | Priced | ROI | Date-cluster bootstrap 95% interval |
|---|---:|---:|---:|---:|
| Missing `ml_p`, below 65 | 306 | 302 | -3.38% | [-11.94%, +6.20%] |
| Missing `ml_p`, at least 65 | 132 | 128 | +6.67% | [-5.06%, +17.07%] |
| Has `ml_p` | 240 | 219 | -1.53% | [-11.03%, +8.19%] |

These are **observational archive cohorts**, not a replay of the proposed policy. They do not isolate electorate, price quality, context, source outages, or deduplication. The review's clean high-minus-low ROI comparison is also inconclusive. Raw below-65 inventory is not an estimate of how many live picks or ticket legs would disappear.

The same review documents archive-integrity and unresolved settlement limitations. Do not restore discarded additions, settle ambiguities by convenience, or reinterpret unavailable historical prices as execution-safe evidence.

### 3.3 Verification and review boundary

Two user-supplied reviews report additional synthetic controls. Their full evaluator, ordering, qualifier, fallback, and sync experiments were **not rerun here**. Their results are attributed in [the review synthesis](REVIEW-SYNTHESIS-ML-CONSENSUS-2026-10-09.md).

Two isolated controls **were reproduced here** using the current checkout, in-memory records and a temporary directory only:

- Canonical loader: an unchanged morning row plus a regular late addition admits one addition. Adding only provenance fields to the regular copy of the morning row admits zero additions and marks the date unsafe.
- Existing shadow `candidate_id()`: two records with identical fixture/selection/rule but distinct model/consensus emission paths get the same ID.

Code inspection also confirms whole-payload frozen equality, full-pick copying into Supabase `source_payload`, label-based ML emission counts, and date-qualified Forebet fetch exclusion. These controls are not a full replay or performance study.

Review 1 now withdraws its claim that the separated-routing control was untested. Attribute the synthetic result directly to **Review 2's reported control**; no new evaluator experiment was run here. Review 1 disputes the wording in its decision-record copy; our baseline contains the relevant observation at [lines 57–59 of the pinned source](https://github.com/6ixtyn9-sudo/Edge-Factory/blob/01f580c1f41b78883d7c807e354ba76903bbd026/docs/operator/DECISIONS-2026-10-09.md#L57-L59). This is a source-version discrepancy, not grounds to claim the reviewer's own copy or authorship is verified. The synthesis no longer uses a flattened block quote to resolve it.

## 4. A second issue reviewers must not overlook: electorate semantics

Simply excluding ML rules from `load_thresholds()` is a small patch, but **not a complete certification repair**.

The served consensus registry's `where` predicates reference specific historical sources, for example:

```text
3way-unanimous avg_p>=65:
    fb_pick = zb_pick AND zb_pick = sa_pick
    AND mean(fb_p, zb_p, sa_p) >= 65
```

The live consensus evaluator instead considers available entries in `SOURCES_1X2`. Forebet is parked for production dates after 2026-06-12. A three-source agreement involving Statarea, Vitibet, and Bzzoiro is not automatically the same population as historical Forebet/Zulubet/Statarea agreement.

This mismatch also affects the historical **two-way Forebet/Zulubet** rules, not only the trio. Extra dissenting voters matter too: the live evaluator tests agreement across available voters, whereas an exact historical predicate tests named electors. These are separate population changes.

**Parked-source availability:** Forebet remains in the static `SOURCES_1X2` roster for historical processing, but `fetch_all()` explicitly skips it after the retirement date and `run_day()` sets its effective weight to zero. Retaining the name is not, by itself, a stale-membership defect. Weight zero alone is not a generic eligibility filter inside a directly called evaluator; normal live exclusion is enforced by the fetch boundary. Static membership or historical cached rows are not proof of live availability. Audit receipts must distinguish roster membership, date eligibility, observed input availability, and certification-elector membership. Directly supplied replay inputs must apply the date policy explicitly; do not remove historical rows or redefine source eligibility as part of instrumentation.

Therefore:

- Removing the collision corrects family routing.
- It does **not** establish that a generic three-available-source signal deserves a historically certified trio label.
- The apparently obvious 55→65 floor change remains an operational change requiring review.

Reviewers must choose between exact historical-elector semantics (potentially dormant while Forebet is parked) and an explicitly defined available-voter rule that needs its own evidence/promotion. Neither should silently masquerade as the other.

Qualified rules also need real predicate enforcement: `min_p`, home/away restrictions, odds bands, and confirmation sources are not merely label suffixes. A selector must not let a qualified rule inherit the generic evaluator unless that evaluator actually enforces every condition.

## 5. Proposed changes and why

### P1 — Add sidecar-only provenance and separate signal identity (first priority)

**Storage boundary:** emit copied evidence into a separate, versioned audit stream at scoring/emission, before duplicate collapse. Do not add fields to operational picks, regular/morning archives, notifications, Supabase payloads, ticket state, or existing candidate IDs in stage 1. Do not weaken whole-payload frozen equality to accommodate metadata. Extend neither the existing shadow stream nor its consolidation key blindly.

Identity requirements:

- Keep existing operational/candidate IDs unchanged and reference them where available.
- Distinguish fixture occurrence, market/selection identity, logical signal identity, and per-build observation identity.
- Signal identity includes emission path plus verified model/consensus-contract identity and qualifying rule. Observation identity additionally links the build and input snapshot. Preserve repeated observations without counting them as multiple bets.
- Use the existing occurrence-identity boundaries where supported; ambiguous occurrence precision stays explicit and never justifies an unsafe merge.
- Link both signals to the selected operational representative without mutating it. Missing receipts remain missing, not invented identities.

Illustrative sidecar fields, subject to consumer review:

```json
{
  "prediction_provenance_version": 1,
  "emission_path": "ml_model",
  "target_selection": "home",
  "probability_kind": "model_probability",
  "model_probability": 0.623,
  "source_average_probability": null,
  "qualifying_rule": "ml-meta avg_p>=60",
  "nominal_threshold_pct": 60,
  "effective_threshold_pct": 60,
  "rule_origin": "registry",
  "model_key": "<verified model identity>",
  "imputed_features": ["fb_p"],
  "elector_sources": ["statarea"],
  "feature_sources_available": ["statarea", "vitibet"],
  "electorate_matched_certification": null
}
```

This is an **illustrative schema**, not an actual fixture, model receipt, or suggested literal placeholder to write. Store a model key obtained from the verified registry/guard; never invent one. Use null/explicit unavailable status where evidence cannot be established. Probabilities are 0–1; thresholds have explicitly named percentage units.

For consensus signals, set `emission_path=unanimous_consensus`, `probability_kind=source_average`, the actual agreeing-source average, and the actual electorate. Record separately any model inference available for that fixture rather than attaching its probability to the consensus qualifying rule.

**Why:** source coverage, model feature availability, and the sources electing the model's target are distinct concepts. The existing `sources_used` list alone does not express them.

Record the electorate-match status **before** policy comparison, with a reason and explicit unknown state when the contract is unavailable. It is diagnostic, not permission to claim certification or make a generic-elector signal executable.

Also capture guard verdict, feature-contract version, input-snapshot reference, actual target electors, observed feature suppliers, competition adjustment, and fallback origin at their computation points. Do not reconstruct these from the representative or today's warehouse.

**Fade-specific receipt:** thresholds qualify on parent `ml_p`; the legacy displayed complement `(1 - ml_p)` is not a verified opposite-side 1X2 win probability. A draw defeats both home and away bets. Record parent selection/probability, inverse selection, qualification basis, and `legacy_parent_complement`; do not change the legacy output or model in this audit patch.

Initially preserve all operational payloads and display behaviour byte-for-byte. Explanatory output lives in the new audit report only. Later operational-schema migration requires separate approval.

### P2 — Separate rule-family routing in an offline/shadow selector

- Model/fade rules must never be inserted into a consensus N-way slot.
- Keep the guarded ML inference and highest-qualifying-certified-tier logic unchanged.
- Consensus routing must classify supported families explicitly and reject unsupported predicates in the proposed policy, with a recorded reason.
- Keep qualified variants separate from plain rules; do not implement arbitrary registry SQL execution inside the live picker as a shortcut.
- Separate real source quorum from the legacy model `n_way=3` identifier.
- Specify fallback behaviour when a registry is missing, unreadable, guarded, or has no supported consensus rule. Do not accidentally activate a default fallback merely because ML was filtered out.

Compare at least three versions: existing behaviour; family-only separation with existing available-voter semantics; and exact-predicate/electorate enforcement. This isolates the small routing fix from the larger population change.

**Why:** reviewers need to know which removals are caused by the floor, which by source identity, and which by predicate enforcement. No model candidate should be withheld just because a consensus path also exists, and no valid consensus candidate should be suppressed merely because the ML model is absent or guarded.

### P3 — Preserve evidence through duplicate collapse

Keep one operational fixture/market/selection row, with a deterministic collection of supporting signal records. Preserve each signal's family, score basis, exact rule, model identity where relevant, and eligibility/context evidence.

Do not combine opposite selections, invent a blended probability, or rank ML logits against consensus vote weights. Preserve identity/squad/kickoff boundaries.

For the initial audit stage, leave the operational representative and bucket logic unchanged; capture the full competing records in the separate signal sidecar, not under the existing candidate consolidation key. A later production representative policy needs separate review:

- Which signal controls the operational probability and exact edge reference?
- Do current worst-bucket protections remain across supporting signals?
- How does a changed rule affect purity/context lookup, odds floors, ranking, and ticket selection?

**Why:** choosing an honest label can change context and selection. It is not safe to “prefer ML” indiscriminately or choose whichever path happens to obtain a better bucket.

### P4 — Update reports and consumers after schema review

Report examples should look like:

```text
ML-META≥60 — model 62.3%; 1 model input imputed
Consensus — source average 78.0%; electorate Statarea/Vitibet/Bzzoiro
Historical certified-trio equivalence: not established
```

Keep the legacy qualifying rule visible during migration; do not rewrite it solely to produce a prettier display. For legacy records, use evidence states such as `legacy_model_score_present`, `legacy_provenance_unresolved`, or verified reconstruction. An old score without a verifiable model receipt is not newly verified model provenance.

Audit notification rendering/dedupe and opposing selections, Supabase edge references/probability fields/full `source_payload` and sync manifests, canonical archive admission/retention, shadow candidate IDs/report consolidation, recent-pick reporting, firing tripwires, purity lookup, and ticket ranking before making new fields authoritative.

Also inspect the label-based `-> N pick(s)` log and `ml_meta_state.json`: both count ML-labelled rows, potentially including consensus emissions. Preserve their existing operational state in stage 1; report actual inference and per-path emission counts separately in the sidecar.

[`scripts/decay_monitor.py`](../../scripts/decay_monitor.py) uses warehouse views and guarded model-keyed prediction exports for ML decay, not archived pick labels. Label changes alone should not change that population; do not extend this observation to every decay dependency. Include the ML-fade research collector/ledger and its checkpoint counts as parity-sensitive consumers. Missing-field historical cohorts remain descriptive, not reconstructed truth.

**Why:** [`scripts/sync_supabase.py`](../../scripts/sync_supabase.py) uses exact rule aliases and `avg_p`; [`scripts/audit_recent_picks.py`](../../scripts/audit_recent_picks.py) groups by stored rule; [`scripts/auto_tickets.py`](../../scripts/auto_tickets.py) consumes probability, bucket, and price eligibility. A local display fix can leave downstream semantics wrong.

## 6. Alternatives and recommendation

| Alternative | Benefit | Problem | Recommendation |
|---|---|---|---|
| Keep current behaviour indefinitely | No immediate output change | Leaves misleading attribution and mixed rule populations | Not a satisfactory end state |
| Cosmetic relabelling by displayed percentage | Easy, attractive board | Mistakes source average for model probability; label self-heal reverses display-only edits | Reject |
| Raise all ML cuts to 65 | Fewer low-score picks | Changes the actual model policy without fixing provenance; no demonstrated ROI benefit | Reject as this fix |
| Blanket suppression of one path when another exists | Fewer duplicates | Can remove otherwise valid candidates, including no-model controls | Reject |
| Exclude ML from consensus slots immediately | Removes confirmed collision | Floor, context, electorate, fallback, and ticket effects not yet evaluated | Shadow first |
| Provenance → controlled comparison → reviewed routing | Isolates mechanisms; preserves rollback | More engineering and evidence collection | **Recommended** |
| New generic-elector consensus rule or replacement model | Could address structural source changes | Separate evidence, certification, and promotion decision | Separate proposal |

## 7. Evaluation plan

### 7.1 Deterministic controls

Use synthetic fixtures and temporary registries to test:

1. No model + genuine consensus: never emit an ML-labelled result in proposed routing; do not accidentally suppress a valid consensus signal.
2. Model probability 62.3%, source average 78%: ML tier 60 remains distinct from source average; preserve both when both paths qualify.
3. Certified model cuts 55/60/65/80, benched 70/75: score 78% qualifies at 65, not 75 or 80; benching a nested cut does not automatically ban the entire upper probability band.
4. Source averages around 55 and 65 with identical model scores: attribute changes to the correct gate, including competition adjustments.
5. Missing/guarded model, absent historical electors, extra voters, contradictory voters, qualified variants, and unsupported rules: explicit, deterministic outcomes.
6. Duplicate permutations: deterministic signal evidence, but match the baseline operational output **for each input ordering**. Review 2 reports a reachable equal-score tie whose representative changes with order. Making that representative permutation-invariant is a separately approved behavioural change.
7. Kickoff lead-time, identity/squad separation, price quarantine, eligibility, and frozen-ticket tests remain intact.
8. Audit hook failures, including serialization, receipt lookup and disk writes: operational results remain unchanged; no shared-object mutation or selection-affecting exception.
9. Archive metadata counterexample: protect whole-payload equality and late-addition admission with sidecar on/off/failure. Sync `source_payload`, manifests and notification bodies/IDs must be unchanged.
10. Same fixture/selection/rule from two paths: distinct signal IDs and observations survive report consolidation, linked to one unchanged operational representative.
11. Electorate mismatch: Statarea/Vitibet/Bzzoiro agreement is flagged as not the historical trio; proposed certified routing must not present it as that trio. Test historical two-way mismatch and named-trio agreement with extra dissenting voters too.
12. Qualifier counterexamples: `min_p>=60` with 56/72/72 must not qualify in the proposed predicate evaluator; home-only must not qualify away. Baseline remains unchanged in audit mode.
13. OU-only certified registry and empty supported-consensus roster: record real fallback origin even if the legacy `is_fallback` flag says false. No new silently activated 1X2 defaults.
14. Fade: parent threshold and complementary legacy display remain distinct; a draw is not a fade win.

Existing slot-selection tests in [`tests/test_picks_today.py`](../../tests/test_picks_today.py) currently pin the collision. Preserve them as baseline controls or deliberately update them **only when the behavioural change is approved**; do not merely change expected strings until tests pass.

### 7.2 Same-input replay and forward shadow

Run baseline and proposed selectors against the **same captured source rows**, verified model, registry, purity snapshot, `as_of`, and cached prices. Also pin guard/activation state, feature-contract version, derived-feature inputs (including rolling-hit-rate warehouse facts), entity registry/overrides, date-based source eligibility, context/debias/veto-resolution state, and historical ticket/bank/ladder/freeze state. Missing decision-time dependencies make a replay partial or non-replayable, not permission to use today's state. No live provider calls, production mining, or operational-state writes for this comparison.

Do not replay through a live-fetching entry point. Feed saved/synthetic inputs directly to isolated evaluators. Where point-in-time source/purity/price snapshots are missing, mark a date non-replayable rather than substitute today's data. Future outcomes may grade decisions but may never create decision-time eligibility or price evidence.

For each variant record:

- Fixtures scored, per-path emissions, overlapping/opposing signals, and final selections.
- Added/removed selections with reasons: family routing, floor, electorate, qualifier, context, price, or collapse.
- Rule, probability basis, bucket, odds evidence, and price eligibility changes.
- Ticket legs/ACCA pairings/stakes/no-bet days under the unchanged ticket engine in a temporary state copy.
- Provenance failures, unresolved legacy rows, and non-replayable dates.

Reuse the observability principles in [`SCORED-CANDIDATE-SHADOW.md`](SCORED-CANDIDATE-SHADOW.md); verify its schema and persistence coverage before extending it. Keep large audit datasets out of tracked Git and do not introduce a second production lane.

### 7.3 Outcome analysis

Separate model-only, consensus-only, and overlap cohorts. Report source/electorate and price-quality strata, number of dates, settled count, priced denominator, pending/conflicting outcomes, hit rate, and ROI with date-cluster uncertainty. Do not count multiple signals supporting one bet as multiple operational successes.

Compare identical populations where possible; give additions/removals their own analysis. Distinguish flat-stake signal ROI from printed-ticket results and from captured-price research ROI. No guaranteed bankroll improvement and no cherry-picked threshold winner.

## 8. Acceptance, activation, and rollback

**Audit-stage acceptance:** sidecar enabled, disabled, and failing at the hook leave operational rows/archives, canonical admission, selections, buckets, ranking inputs, prices, stakes, notification payloads/identities, full sync payloads/manifests, and frozen locks unchanged on controls; report every baseline mismatch. Model/consensus provenance has distinct signal identities before collapse; evidence is deterministic while baseline tie behaviour is preserved. Hook failures cannot gate production.

**Live-routing prerequisites:** review resolves supported electorate/predicates, fallback behaviour, representative policy, downstream probability semantics, and legacy treatment. Same-input differences are explained; source outages and model guards are tested; an operator explicitly approves activation. No unsupported historical certification is claimed.

A correctness correction does not require a statistically proven profitability increase. It does require an explicit semantic contract, explained selection differences, preserved safety invariants, and operator acceptance. Neither higher retrospective ROI nor a mismatch flag supplies missing certification.

Activation must be versioned at a prospective boundary. Preserve frozen cards and original bet-time evidence; do not backfill live qualification into historical records. Keep the old routing implementation available for code/config rollback. Rollback must not mutate the served model, relax price safety, or regenerate locked tickets.

## 9. Explicitly outside this proposal

- Retraining/promoting the research or Phase 5 model; changing its feature contract or certification clauses.
- Lowering gates to clear source-health/firing alarms; restoring Forebet through alternative capture methods.
- Changing stake fraction, ladder, bucket eligibility, ACCA count, market, kickoff guard, or freeze time.
- Fixing provider 403/404/429 responses, league aliases, or missing execution prices.
- Rewriting historical settlement, canonical archive admission, or discarded additions.

The supplied run's missing Forebet/model-input warnings are a separate model-domain issue. This proposal makes them visible in provenance; it does not establish that imputed scores are calibrated or solve the outage.

## 10. Questions for independent LLM reviewers

Please inspect the cited code and decision receipt rather than treating this proposal as authority. Return **approve / approve with changes / reject** separately for the audit stage and live-routing stage.

1. Does the code mechanism above reproduce? Which claims are observations, inferences, or unsupported?
2. Is family separation sufficient, or must exact historical-elector/predicate enforcement block activation? Define the smallest honest policy.
3. Should generic available-source consensus be shadow-only pending separate certification? What evidence would justify promotion?
4. How should one operational pick choose its rule/probability when model and consensus both qualify, without mixing score scales or weakening context safeguards?
5. What hidden consumers use `rule`, `edge_rule`, `avg_p`, `n_way`, `w_score`, or `display_rule`? Identify any missed sync, notification, audit, or ticket migration risk.
6. Is the proposed first stage genuinely behaviour-preserving? What would falsify that claim?
7. Which adversarial tests or replay controls are missing? How should missing point-in-time data limit conclusions?
8. What evidence would justify changing selection even if profitability remains statistically uncertain? Separate correctness approval from profit claims.
9. Should legacy ML-tagged records remain unresolved, or can some be reconstructed from preserved pre-collapse evidence? State proof requirements.
10. Recommend a minimal patch order, activation criteria, and rollback test. Do not propose relaxed safety gates or automatic model promotion.

### Suggested review response format

```text
Audit-stage verdict:
Live-routing verdict:
Confirmed mechanism (code references):
Disagreements / missing evidence:
Electorate and qualifier policy:
Duplicate / probability policy:
Downstream consumers to inspect:
Required tests and replay controls:
Expected correctness benefits:
Profitability claims that remain unproven:
Minimal patch sequence and rollback:
```

## 11. Work performed for this document

Read-only inspection of selector, emission, collapse, label healing, context lookup, downstream consumers, tests, registry predicates, and existing reviews. No new performance experiment or full replay was run. The historical measurements above are explicitly attributed to the existing decision document. Revision 1 changed this proposal and its handbook link. Revision 2 additionally records the review synthesis and performs the two isolated temporary/in-memory controls in §3.3. No production pipeline, provider calls, full replay, or performance experiment was run.


## 12. Review disposition (revision 4)

See [the review synthesis](REVIEW-SYNTHESIS-ML-CONSENSUS-2026-10-09.md) for attributed verdicts, verification scope and unresolved disagreements.

Accepted amendments: sidecar-only storage; separate signal/observation identity; mixed-probability finding; electorate flag before comparisons; date-qualified source availability; two-way electorate coverage; qualifier/fallback adversarial tests; baseline order-sensitive parity; fuller inference/fade receipts; expanded consumers and replay manifest.

**Not approved:** immediate live routing, generic available-voter production under a historical certified name, weakened archive equality, operational provenance-field migration, or deterministic representative changes. A diagnostic flag preserves visibility but is not deployment authorization. Exact-elector enforcement is a comparison policy, not an approved fix; parked electors can make that consensus family dormant without necessarily suppressing independent model or other valid paths.


The supplied reconciliation response requests documentation and an acceptance checklist, not live implementation. Revision 3 clarifies: both probability kinds use percentage units; not every ROI population is mixed; Forebet roster retention is legitimate historical support; zero output from missing required electors can be valid abstention rather than blanket suppression. The acceptance checklist records every implementation/replay test as **not yet run**, except the two isolated counterexample probes already described.

Before activation, explicitly choose **supported historical-contract enforcement**, or **a separately identified available-voter contract with required evidence and promotion**. A legacy label plus a false electorate flag is acceptable only as audit annotation while baseline behaviour is deliberately unchanged; it is not a completed live certification repair.


Revision 4 records the latest consensus: **both reviewers conditionally approve the audit design with changes; neither approves live activation or audit implementation automatically**. Review 2 reports checking all three revision-3 documents pinned to `0dac025`; Review 1 reports reading the synthesis only. Its earlier verdict is superseded. The next requested deliverable is Gate A's concrete schema/storage specification for explicit review, not audit-hook code. This update makes no changes to the unchecked acceptance requirements.
