# Corrected ML ENH card — 26 October 2026

**Status: reconstructed from preserved predecision evidence; NOT a live freeze or placement record.**

The corrected production selector returns **two two-leg accas on four distinct fixtures**, rather than NO BET. Both use the captured **bet365.us** quotes. These are existing captured prices, not fresh bookmaker availability checks. Confirm the selections and available prices before placing; this document does not record a personal bet.

## The card

| Acca | Fixture | Selection | Captured odds | ML ranking score | Kickoff SAST |
|---|---|---|---:|---:|---|
| 1 | Mladost Ždralovi–Jadran LP | Match Over 1.5 goals | 1.30 | 79.24% | 15:00 |
| 1 | Galatasaray–Fenerbahçe | Match Over 2.5 goals | 1.48 | 62.25% | 20:30 |
| 2 | Beşiktaş–İstanbul Başakşehir | Match Over 2.5 goals | 1.40 | 65.91% | 18:00 |
| 2 | Santa Clara–Benfica | Match Over 2.5 goals | 1.85 | 65.27% | 20:45 |

- **Acca 1: 1.924 unrounded; selector displays 1.92.**
- **Acca 2: 2.59.**
- Saved free bank: **39.0372% of base capital**.
- Existing staking: **4.8796% of base capital per acca**, equal to **12.5% of free bank each**.
- Total: **9.7592% of base capital = 25% of free bank**. No staking configuration changed.
- ML scores are experimental ordering scores, not calibrated fixture probabilities or a joint acca probability.

The existing live `PAIRING=barbell` configuration chooses this pairing within the executable bookmaker/source group: highest-ranked Mladost with lowest-ranked Galatasaray, then the two middle-ranked fixtures, Beşiktaş and Santa Clara. No pair was hand-selected or force-admitted.

## What was repaired

1. **Schedule-source dependency:** BetExplorer admission could read independent OddsPapi/TheOddsAPI schedules, but not timestamped ScoutingStats/Vitibet source responses. Its coverage therefore failed when the odds providers lacked these fixtures, even though other existing sources had explicit zoned kickoffs.
2. **Missing source capture receipts:** the normal source CSV writer did not retain genuine response capture time/origin for these two source schedules. The existing writer now stamps the response just fetched and retains independent observations, including conflicting changes. Legacy rows are not retroactively timestamped.
3. **Alias lookup masking:** an earlier schedule-only display-name entry could stop lookup before a later priced equivalent fixture. ENH now skips empty price buckets and recognizes the repository's existing curated same-club aliases, including Basaksehir / İstanbul Başakşehir. No new global alias or fuzzy-name threshold was added.

The live reader uses the existing top-level source monthly CSVs only. It does **not** consume Phase 5 research/shadow ledgers, generated picks, inferred warehouse clocks, or file mtimes as independent schedule evidence.

## Evidence and reconstruction boundaries

Original run: [40283113075](https://github.com/6ixtyn9-sudo/Edge-Factory/actions/runs/40283113075).

Persisted inputs: [`c8e77c3946b5ceeaf7b44f385916142925deb39f`](https://github.com/6ixtyn9-sudo/Edge-Factory/commit/c8e77c3946b5ceeaf7b44f385916142925deb39f).

The original source captures were preserved in the append-only response-backed archive. For this **offline reconstruction only**, their source fixture names, explicit-offset kickoff strings and original observation times were recovered into isolated source-format CSVs. The companion JSON preserves the original capture records/row IDs and the selected quote receipts. No runtime reader was connected to that research archive.

- Source observations used for the missing fixtures were recorded before the original 09:00 SAST cutoff; the latest relevant ScoutingStats observation was **06:02:52 SAST**, and Vitibet **06:02:01 SAST**.
- The existing BetExplorer market cells and their original capture times were reused. Parent 1X2 prices were not substituted for totals prices.
- The run's saved exact-parent cohort profiles and compact ML models were reused unchanged. The reconstruction did not refit a model or query a later warehouse population.
- The same `compute_dynamic_enhancement`, `enhancement_legs(execution_safe=True)`, `apply_enhancement_timing`, `enhancement_pool`, `plan_day(... enhancements=True)` and `_carry_lane_evidence` functions produced the card.
- Result: **23 passing quotes over four fixtures; one exchange quote rejected**. No timing drops at the execution check recorded in the companion JSON.
- Matchbook 1.91 remains excluded. The selected Santa Clara quote is **bet365.us 1.85**.
- All existing cohort/sample-size, minimum-price, payout-bound, source, identity, same-fixture, book/source grouping and timing checks remain in place.

**No live ticket, bank, open-slip, freeze, settlement, placed flag or historical result was changed. No workflow was dispatched.** The original NO BET remains an authentic run output; this document is its explicitly labelled corrected reconstruction, not a backdated production artifact.

For future runs, the fixed normal capture path must run before cutoff so its schedule receipts exist. Merely rerunning selection after cutoff against legacy unstamped CSVs does not manufacture earlier evidence. Today's reconstruction is supplied separately rather than laundering such a rerun into an original freeze.

## Regression checks

Targeted checks cover both schedule sources; supported match totals, BTTS and double chance; complete-ticket construction; absent/naive/late timestamps; identity and squad mismatches; circular source labels; conflicting schedules; live receipt tampering; source CSV persistence; the Basaksehir alias/empty-bucket regression; and Phase 5 operational isolation.

**676 targeted tests passed** on the final code, covering capture, corroboration, ENH pricing/selection, live evidence admission, freeze/unplaced protection, daily orchestration and research isolation. `git diff --check` passed. This is not a claim of a completed full-suite run.

Machine-readable evidence: [enh_schedule_repair_2026-10-26.json](enh_schedule_repair_2026-10-26.json).

## Follow-up: make the recovered schedules available to a normal workflow

The missing operational recovery is now implemented as two tiny, committed,
schedule-only source archives:

- `localdata/schedule_scoutingstats_2026-10.csv.gz` — six original observations.
- `localdata/schedule_vitibet_2026-10.csv.gz` — sixteen original observations.

Their 22 rows are exact projections of the original source capture records in
the companion JSON: original fixture names, kickoff strings, capture times,
source and capture-row IDs are preserved. The extraction verified each original
record's SHA-256 row ID. No observation time was assigned from the current
clock or from kickoff. No probabilities, scores, odds, or selected tickets were
inserted into these schedule files.

The normal schedule reader and live receipt checker now accept this separate
archive prefix. The warehouse's existing source globs do not match it, so it
cannot add predictions or change mining/consensus units. The existing workflow
restore step restores these tracked inputs over a missing or stale cache. A
normal run therefore has the recovered pre-cutoff schedules available without
reading any Phase 5 shadow file.

The four relevant BetExplorer detail-cache entries were already visited and
remain within their existing 24-hour freshness window. Their normal cache path
does not refetch and replace those quote captures merely because a workflow is
dispatched. No collection policy was changed.

### Verified freeze, not just a selector result

Using the saved exact-parent profiles and quotes, the restored source archives,
and the original run's ENH financial state, the **actual `cmd_enhancement` entry
point** was executed with `force=False` in an isolated scratch lane at 10:40 SAST.
It produced the two accas above and wrote all three real freeze outputs:

1. `frozen_by_date['2026-10-26']` with `final=True`;
2. an open slip with two accas and total stake **9.7592 capital points**;
3. `FROZEN AT 10:40 - FINAL` on its ticket text.

The scratch state's paths were isolated from production. This proves the
normal freeze path can consume the recovered inputs; it does **not** claim
that production has already frozen or that fresh prices/cohorts cannot change.

### Dispatch after the follow-up is merged

Use the existing **Autonomous Edge Factory 3-Hour Service** workflow,
branch **main**, execution mode **auto**. Equivalent command, for the operator
to run (not dispatched by the agent):

```bash
gh workflow run daily.yml --repo 6ixtyn9-sudo/Edge-Factory --ref main -f mode=auto
```

`auto` performs the existing current-day intraday rebuild because today's
official marker exists, then reaches the separate **Enhancement tickets
(generate/freeze)** step. There is no need for `recover_and_rebuild`, a reset,
remine-only mode, an ENH force flag or a manually fabricated ticket. A qualifying
card after 09:00 SAST freezes at that run's actual time. Existing frozen cards
remain write-once. If a real new conflict, started fixture, unavailable price or
other execution check prevents a card, the workflow must report that rejection
rather than force this reconstructed card.

Follow-up validation: **696 targeted tests passed**, including both archived
schedule sources, restored/missing runner-cache handling, preservation of original
capture values, exclusion from prediction warehouse inputs and existing freeze,
selection, orchestration and isolation protections. No workflow was dispatched.
