# First instrumented production run: 39307259942

Read-only diagnosis of the 19 October 2026 intraday run. No provider requests, workflow reruns, rule changes, operational file updates or frozen-slip regeneration. This supplements, rather than rewrites, the earlier pre-instrumentation diagnosis.

## Evidence and scope

- Workflow: https://github.com/6ixtyn9-sudo/Edge-Factory/actions/runs/39307259942
- Final picks-build run: `20261019T192636-3969ca2a-picks_build`.
- Persisted evidence read directly from Git commit `008f8cfc74f4cffea46b19a35426c2bc8d69f069`, fetched without switching or changing the session branch.
- Eight date-routed scored-candidate ledgers contain this run's fixture decisions. The adjacent [JSON receipt](game-attrition-run-39307259942.json) records their SHA-256 hashes and the registry hash. These are persisted repository records, not an artifact download.
- Timing and infrastructure observations below come from the user's complete workflow log. Registry status details come from the persisted registry; per-decision empty certified-rule lists independently confirm the runtime emission restriction.

## Correct denominator and measured funnel

The log's 849 source keys are not 849 October 19 games. Of those keys, **611 are Bzzoiro-only fixtures for October 20–26**, all rejected for insufficient probability sources. Their records are correctly routed to their own event-date ledgers.

| Event date | Source keys |
|---|---:|
| October 19 | 238 |
| October 20 | 55 |
| October 21 | 34 |
| October 22 | 44 |
| October 23 | 58 |
| October 24 | 234 |
| October 25 | 178 |
| October 26 | 8 |
| **Full scan** | **849** |

The **October 19** funnel is:

| Decision | Count |
|---|---:|
| Source fixture keys, not independently verified unique fixtures | 238 |
| Insufficient complete probability sources | 184 |
| At least two complete probability sources | 54 |
| Below effective consensus threshold | 27 |
| Voter disagreement | 23 |
| Candidate emitted | 4 |
| Emitted candidate rejected by pre-match guard | 4 |
| Fresh eligible picks from this build | 0 |

Reconciliation: `238 = 184 + 27 + 23 + 4`; `849 = 611 + 238`; scan-wide insufficient count `795 = 611 + 184`. Thus 93.6% is a mixed-date insufficient-source rate, not the target-day rate. The target-day rate is 77.3%.

### Source input limitation, not automatically a parser bug

On the target day, Vitibet is present on 203 keys, but only 93 have complete probability triples. The other 110 lack all of `p1`, `px`, `p2`. The adapter documents probability disappearance after settlement; retained diagnostics alone do not distinguish provider omission, stale rows or a parsing issue. Do not invent or backfill probabilities from later data. Other complete-probability coverage is Zulubet 36, Statarea 43, Betclan 40 and Bzzoiro 5. Forebet remains intentionally retired from this production electorate.

## The four candidates had already started

All four receive `inside_30m_lead_or_started`, with decision time `2026-10-19T21:25:13+02:00`:

| Fixture | Resolved kickoff, SAST |
|---|---|
| Omonia Nicosia – Olympiakos | 18:00 |
| Hapoel Kfar Shalem – Hapoel Acre | 18:00 |
| Mes Shahr-e Babak – Persepolis FC | 14:00 |
| Bursaspor – Pendikspor | 19:00 |

The 17:00 and 18:00 strings in some source rows are not SAST; these times use the guard's recorded UTC resolutions converted to UTC+02:00. All were already started at the run's approximately 21:01 SAST initial cutoff. Removing the roughly 23-minute pre-discovery delay would **not** have rescued these four. The time guard worked correctly; lowering it would not produce legitimate new pre-match picks.

The zero is fresh intraday discovery, not an empty daily portfolio. Two earlier official picks and the frozen two-leg main and enhancement slips were retained. A rediscovered started candidate being rejected does not invalidate its earlier pre-match inclusion.

## Why 40 ML scores produce no ML picks

Of the 54 target-day keys passing the shared probability-input gate, 40 reach ML scoring and 14 lack eligible legacy-source probability input. All 40 record `no_certified_ml_rules`; fade has the analogous absence.

The miner's “preserved 14” refers to registry entries, not 14 active emission rules. The persisted registry contains six `ml-meta` entries marked `benched`, one `ml-meta` entry marked `candidate`, and seven `ml-fade` entries marked `candidate`. None is `certified`. The pick loaders require certified status plus the operational registry guard. This is not evidence of a missing-loader defect, nor authorization to promote research rules into serving.

## Concrete integration issue and limits of this evidence

`bzzoiro.fetch_day(today)` deliberately snapshots **all upcoming dates**, whereas `scripts/picks_today.py:fetch_all(day)` accepts those rows without event-date scoping and indexes them by team pair only. The adapter module header incorrectly describes a date-filtered contract; the actual function documents snapshot semantics.

This explains the 611 out-of-day keys and misleading daily denominator. A correction should scope the picking consumer by event occurrence, while preserving full capture-forward ingestion. It must also test repeated team pairs on different dates, missing dates and timezone boundaries. Do not truncate capture coverage to make a daily log look smaller. No false emitted candidate from these 611 was observed: every one was single-source and rejected. This diagnosis does not claim an observed cross-date misjoin or that all single-source target-day keys are naming failures.

## Other markets remain relevant

This is the 1X2 source-key funnel, not a complete multi-market opportunity report. The persisted registry has no certified direct OU/BTTS generator rules. Enhancement-market competition can compare eligible totals/BTTS/other markets on surviving parent fixtures, but broader cohort selection does not independently introduce the 184 fixtures rejected before parent generation. A missing parent and an enhancement candidate losing market ranking are different failures. Nothing here establishes that a 75% rather than 85% cohort cutoff is profitable or should be changed.

## Independent reliability problems

The successful workflow conclusion does not mean every noncritical operation succeeded:

- ProSoccer result refresh and recapture took approximately 600.7 + 577.9 seconds, with timeout failures. Discovery should not wait behind duplicate slow maintenance work without a bounded design.
- Main ticket build and grade took approximately 923.5 + 619.4 seconds. Separate enhancement build and grade each took roughly 15 minutes, repeatedly scanning historical settlement. These are performance targets, not reasons to relax selection rules.
- Both Supabase rows lacked edge/event IDs. Sync refused to delete existing remote date rows when no new rows were syncable; that fail-safe should be preserved while identity mapping is repaired.
- Bzzoiro odds returned HTTP 403; Betminer retained its 404 failure receipt; OddsPapi had no daily budget remaining. No credential workaround, extra provider call or quota increase was attempted.
- Large quote rejection totals are quote rows, often outside the event window or unsupported markets, not discarded eligible games. Zero matched rows after zero eligible picks is not by itself evidence of wholesale fixture-join failure.

## Priorities

1. Correct the daily picking/date-scope integration and denominator, with occurrence-aware regression tests and full capture preserved.
2. Investigate target-day usable-source coverage from saved pre-match captures; separate missing provider probabilities from parser or identity failures before repair.
3. Bound/avoid duplicate blocking result refreshes and repeated historical settlement passes. Do not claim these changes would have rescued this run's already-started games.
4. Repair Supabase IDs without weakening its no-destructive-empty-sync protection.
5. Evaluate broader market/fixture entry and any threshold changes separately with forward-safe evidence. Do not automatically certify ML rules or admit single-source fixtures simply to increase volume.

No production code or betting policy changes were made for this diagnosis. The new logging has supplied the previously missing gate-level evidence.
