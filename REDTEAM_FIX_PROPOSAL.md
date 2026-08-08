# Edge Factory — Red-Team Fix Proposal

**Date:** 2026-08-08
**Scope:** every S0/S1/S2 finding raised across four independent red-team passes.
**Goal:** one coherent set of changes, not a patch-per-finding. Each change is
motivated below, then the unified diff follows.

## Design principles

The findings cluster into three failure modes. The fixes follow the same shape:

1. **Time is one invariant, not four.** Kickoff, capture time, pre-match
   guard, and the audit cutoff all need the same timezone-aware datetime.
   Today the code parses `HH:MM` with a regex and compares it to SAST, which
   is wrong for every non-SAST fixture (Argentina −03:00 is 5 hours off).
   Fix: introduce `parse_kickoff_dt()` that returns an aware SAST datetime,
   and use it everywhere a kickoff is compared to now.

2. **Identity is one key, not five normalizers.** Source rows use
   `source_team_key`, the odds exact-join uses `odds_team_key`, the time
   join uses `odds_match_team_key`, the notifier uses
   `operational_team_key`, and the archive has its own. They disagree.
   Fix: canonicalise every event to `(date, competition, home_norm,
   away_norm, kickoff_iso)` at ingestion, and thread that key through
   source collapse, odds join, archive, notification, and settlement.
   The 9-char truncation is retired for new data; legacy rows keep it
   but are quarantined when they collide.

3. **State is explicit, not inferred from file existence.** A forecast
   file named `picks_2026-08-09.json` currently becomes the "official"
   ledger simply by existing. Fix: stamp every ledger with a
   `ledger_kind` field (`forecast`, `morning_baseline`,
   `autonomous_intraday`, `promoted`), make `daily.py` choose the mode
   from that field rather than `os.path.exists`, and refuse to treat a
   forecast as official unless it is explicitly promoted.

The smaller findings — NaN/Inf odds, double-send, `--force` ledger
clobber, BTTS fallback leak, post-kickoff price freshness, provider
priority, Telegram length — all fall out of these three changes plus a
few lines of defensive code. They are included in the diff.

## What this proposal deliberately does NOT change

- **No ML retraining.** The percent-vs-probability training bug is real
  but fixing it requires retraining the model with the correct feature
  scale. That is a separate project; this proposal disables the
  ML-META certified path until retraining lands rather than shipping a
  miscalibrated model under a "certified" label.
- **No change to the barbell/staking strategy.** That lives outside the
  repo. The fixes here make the audit numbers trustworthy enough to
  base such decisions on; they do not make the decisions.
- **No new notification provider.** Telegram is the primary; Meta/Twilio
  remain compiled-in but disabled by secret removal. CallMeBot is left
  in code but removed from the workflow env.
- **No retroactive rewrite of historical ledgers.** Existing
  `picks_*.json` files keep their fields; new fields default safely for
  old rows.

## File-by-file change summary

### scripts/picks_today.py

- **T1  Timezone-aware kickoff.** New `parse_kickoff_dt()` accepts ISO
  with offset, naive "DD-MM, HH:MM" (assumed SAST), and "HH:MM" (assumed
  SAST). `_kickoff_minutes` is deleted. `operational_pick_eligibility`
  compares aware datetimes. A kickoff whose timezone is unknown and
  whose date is today but whose clock has already passed is rejected —
  fail-closed is the right choice for a betting guard.
  *Why:* this is the only S0 bug that can put an in-play bet in front
  of the operator. Regex parsing has to go.

- **T2  Finite odds.** `_valid_decimal_odds` now calls `math.isfinite`
  and rejects `NaN`/`Inf`. Applied at every boundary.
  *Why:* NaN passes `<= 1.0` as False and is currently treated as a
  valid price. One bad source row corrupts ROI.

- **T3  One canonical event key.** `event_key(pick)` returns
  `(date, competition, norm_home, norm_away, kickoff_iso)`. The source
  collapse, odds exact-join, archive, and notifier dedupe all use it.
  The 9-char legacy key is kept only for reading pre-change rows.
  *Why:* three normalizers were producing three identities for the
  same team. That is the root cause of duplicate sends, wrong odds,
  and wrong-result joins.

- **T4  Excluded markets in fallback.** `EXCLUDED_MARKETS` is applied
  to `candidates` before the fallback sort, not just inside the EV
  loop. Goal-range markets are added to the exclusion set because they
  cannot be priced and the fallback should never recommend an unpriced
  market as a "tip".
  *Why:* the fallback currently returns `btts_yes`/`goal_range_*` on
  every unpriced pick, which is what the operator sees on Telegram
  despite our "BTTS excluded" commit.

- **T5  EV edge on calibrated probability.** The EV loop reads the
  market's engine-aware debias factor from
  `event_notes_audit.by_engine.hybrid_cohort` when available, and falls
  back to 1.0 with a raised `MIN_EDGE = 0.05` when no calibration
  exists. The known ~4pp goals over-promise means +3% is inside the
  noise.
  *Why:* an edge gate smaller than the model's known bias is not a
  gate. +5% is still aggressive but defensible; the registry tightens
  it as samples accumulate.

- **T6  LIVE source rows rejected.** In the source collapse, any row
  whose `status` field (case-insensitive) is in
  `{"live","ht","ft","finished","played","aet","pen"}` is dropped
  before consensus voting, regardless of whether final scores are
  present. Rows with no `status` field keep current behavior; the
  ScoutingStats adapter is updated to set `status="upcoming"|"live"|...`
  explicitly.
  *Why:* absence of a final score is not evidence that a match hasn't
  started. In-play probabilities must never vote.

- **T7  SRL/simulated leagues rejected.** A competition or match name
  containing `srl`, `simulated reality`, `esoccer`, `ebasketball`,
  `virtual`, or `(srl)` is dropped before consensus. The check is on
  the normalized lower-case string and is applied per source row.
  *Why:* PSV SRL and AZ SRL already reached real bets. The model is
  trained on real football.

- **T8  Core EV gate at displayed odds.** A pick is only eligible for
  CLEAN/CAUTION if `avg_p * odds - 1 >= 0.02` AND `odds` is finite AND
  `price_push_eligible` is true AND `price_evidence` is not
  UNMATCHED/SUSPECT. The two-percent floor is deliberate: the footer
  already warns that best odds inflate ROI by roughly half, so a
  two-percent paper edge is approximately break-even after vig.
  *Why:* the system currently pushes CAUTION picks at negative EV
  (Valur 0.677 × 1.33 − 1 = −9.96%). "Edge" should mean edge.

- **T9  SOURCE_FALLBACK not push-eligible.** A pre-existing forebet
  quote with no bookmaker and no captured_at is kept for audit but
  sets `price_push_eligible = False` and routes to WATCHLIST_NO_ODDS,
  not CAUTION.
  *Why:* a stale model-implied price is not a bettable line.

- **T10  BetExplorer rescue respects bucket.** The rescue no longer
  sets `price_push_eligible = True` unconditionally; it ANDs with
  `pick.get("bucket") in (BUCKET_CERTIFIED, BUCKET_CAUTION)` and with
  the new core EV gate. It also compares its price to any archived
  `suspect_price` and records `rescue_overrode_suspect` rather than
  silently replacing it.
  *Why:* a rescue was promoting quarantined picks to pushable.

- **T11  Reverse-match orientation.** When a BetExplorer or
  enhancement join matches the reversed home/away pair, directional
  markets (1X2, team totals, double chance) have their selection
  flipped (home↔away for 1X2; tt_home_*↔tt_away_*; 1X↔X2). If the
  flip cannot be expressed for a market, the match is rejected. The
  orientation is recorded as `price_orientation = "reversed"`.
  *Why:* a HOME pick receiving the AWAY team's Over 0.5 price is a
  wrong-leg bug.

- **T12  Forecast files write `ledger_kind`.** `picks_today` writes
  `ledger_kind: "official"` to `picks_<day>.json` only when invoked as
  the official morning run. The future planner writes
  `ledger_kind: "forecast"`. Autonomous runs write
  `"autonomous_intraday"`. The `picks_next_*.json` aggregate is
  unchanged and already tagged forecast.
  *Why:* this is half of the forecast-becomes-official fix; the other
  half is in daily.py.

### src/edgefactory/enh_pricing.py

- **T13  Freshness guard for every source.** `_fresh_row` no longer
  returns True on missing `captured_at`; it returns False unless the
  caller explicitly passes `allow_missing_capture=True` (used only by
  same-day cache files that are regenerated from scratch each run).
  Bzzoiro and TheOdds accumulators pass a real max-age; ScoutingStats
  rows must carry a real fetch timestamp (adapter change below).
  *Why:* fail-open meant post-kickoff closing odds could price a
  pre-kick pick.

- **T14  Median-clipped best price.** Before `_put` keeps the max, it
  collects every price seen for the (pair, market, selection) across
  sources, and rejects any candidate more than 20% above the median.
  This applies to both 1X2 and enhancement prices. The rejected row
  is recorded in a `price_anomalies` log (not silently dropped).
  *Why:* `max()` amplifies alias errors. A bad team-name join usually
  produces an implausibly high price; median clipping kills it
  without hurting legitimate line variation.

- **T15  Bzzoiro strict source.** Passes `strict_source=BZZOIRO_SOURCE`.
  *Why:* consistency with TheOddsAPI.

- **T16  Capture time on ScoutingStats.** The ScoutingStats adapter
  writes `captured_at` as the actual fetch time (UTC ISO), not the
  kickoff.
  *Why:* the freshness guard needs a real timestamp.

- **T17  No price after kickoff.** `attach_enhancement_price` rejects a
  price whose `captured_at > kickoff` when the pick carries a
  parsed kickoff. Pre-kick price is a hard invariant.
  *Why:* this is the audit-time equivalent of T1; it stops closing
  odds from certifying an enhancement.

### scripts/audit_recent_picks.py

- **T18  Trust archived enhancement price.** When the frozen pick
  carries `enhancement_price`, `enhancement_price_source`, and
  `enhancement_price_at`, the audit uses those fields. A fresh
  `prices_index` lookup is used only for legacy rows with no archived
  price. Every priced enhancement is also checked against kickoff:
  `enhancement_price_at <= pick_as_of <= kickoff`.
  *Why:* mutable alias tables were retroactively turning unpriced
  picks into priced winners.

- **T19  Settle OU/BTTS picks.** The audit no longer `continue`s on
  non-1X2 markets. `settle_pick` gains branches for `ou_*` and `btts`
  using the final score. Markets with no settlement definition are
  recorded as `unsettled`, not silently dropped.
  *Why:* the pipeline can SEND an Over 2.5 ticket; the audit must
  grade it.

- **T20  Void/postponed returns 0.0.** `settle_pick` checks the result
  disposition first; `void`, `postponed`, `cancelled`, `abandoned`,
  and `suspended` return `pnl=0.0, settled=False`. The headline
  denominator counts only settled picks.
  *Why:* one agent claimed voids graded as losses; the code already
  excludes most, but not all, dispositions. Belt and braces.

- **T21  Split recommended vs priced in headline.** The enhancement
  section reports two hit-rates: `recommended_priced` (the population
  that could have a bet) and `recommended_unpriced` (research only).
  The headline ROI uses priced only.
  *Why:* a 68% hit rate made of 26 unpriced Home-O0.5 picks plus 10
  actual recommendations is a lie.

- **T22  Score-derived outcome.** When the result row supplies both a
  final score and an `outcome` string, the audit derives the 1X2
  outcome from the score and logs a contradiction warning if the two
  disagree. A contradiction quarantines the row rather than trusting
  the string.
  *Why:* one corrupted `outcome` label was grading 2–0 as an away win.

- **T23  Apply haircut to headline ROI.** A new
  `EDGE_FACTORY_ROI_HAIRCUT` env (default 0.5, matching the
  documented doctrine) is applied to the "adjusted ROI" column; the
  raw best-odds ROI is shown alongside for transparency. The
  certification gates in `mine_consensus.py` use the adjusted figure.
  *Why:* stop presenting paper ROI as staking ROI.

- **T24  Result key includes competition and kickoff.** The partition
  that matches picks to results uses
  `(date, competition, home, away)` and, when two candidates exist
  for the same pair, picks the one whose kickoff is closest to the
  pick's kickoff. If two candidates remain within 2 hours, the pick
  is marked `ambiguous_result` and left unsettled.
  *Why:* same-pair/different-league collisions were grading one
  fixture with another's score.

### scripts/notify.py

- **T25  First-success provider returns.** Each provider branch ends
  with `return True` on success. Failure continues to the next.
  *Why:* broadcast to every configured provider is a bug, not a
  feature. Telegram is primary; the rest are fallback.

- **T26  Telegram chunking.** A new
  `chunk_telegram_shadow(text, limit=3800)` splits on pick-card
  boundaries with section headers restated. The official message uses
  the same helper. `send_telegram_message` rejects a body over 4096
  with a clear error instead of HTTP 400.
  *Why:* a 50-pick day currently fails the whole shadow send.

- **T27  `--force` merges, never replaces.** A forced dispatch loads
  the existing ledger and unions in the new keys rather than
  overwriting the file. `--force-reset-ledger` is added as an explicit
  opt-in for the rare case that truly wants a clean slate.
  *Why:* a forced re-send today wipes the dedupe history and causes
  the next cron to spam.

- **T28  Atomic ledger writes.** `_save_sent_ledger` writes to a temp
  file in the same directory and `os.replace`s it. Write failures
  propagate to the caller; a failed write is logged and turns into a
  non-zero exit for the normal-message path (heartbeat stays
  best-effort).
  *Why:* the previous swallow-all-errors design meant a successful
  send could be treated as complete with no persisted dedupe, causing
  a re-send storm.

- **T29  Heartbeat cap independent of delivery success.** A separate
  `heartbeat_attempts_<date>.json` counter caps heartbeat attempts at
  one per 24h regardless of whether the send succeeded.
  *Why:* a persistent Telegram outage should not produce 8 pings/day.

- **T30  No double-mark between families.** The main, discovery, and
  shadow ledgers are independent. The heartbeat marker is written to
  the MAIN ledger only after a successful heartbeat send, as before,
  but `_heartbeat_pending` also checks a heartbeat-attempt ledger so
  a crash between send and write cannot loop.

### scripts/daily.py

- **T31  Mode is chosen from `ledger_kind`, not file existence.**
  `run_smart_auto` opens any existing `picks_<today>.json`, reads its
  `ledger_kind`, and:
    - `forecast` or absent → runs the official morning path and
      writes a `picks_morning_<today>.json` baseline, promoting it to
      the official ledger.
    - `morning_baseline` or `official` → runs autonomous intraday.
    - `autonomous_intraday` → runs autonomous intraday.
  A forecast file can no longer suppress the morning run.
  *Why:* this is the other half of T12; together they fix the
  forecast-becomes-official bug.

- **T32  Merge identity includes date and side.**
  `autonomous_intraday_merge` keys on `(date, home, away, market,
  pick, kickoff_iso)` instead of `(EVENT_ID, home, away, market)`. A
  changed pick side produces a new row, not a silent overwrite.
  *Why:* Jan-2 AWAY was being merged into Jan-1 HOME.

- **T33  CallMeBot env removed from workflow.**
  `.github/workflows/daily.yml` drops `CALLMEBOT_APIKEY` and
  `CALLMEBOT_PHONE` env mapping. The secrets can be deleted in GitHub.
  *Why:* the operator migrated to Telegram; keeping the env means
  every message is still attempted to CallMeBot.

- **T34  Concurrency group.** Add
  `concurrency: { group: edge-factory-main, cancel-in-progress: false }`
  to the workflow.
  *Why:* two overlapping runs can both notify and then collide on
  git push.

### src/edgefactory/notifier.py

- **T35  Marker consistency.** The text report's `🔥 Possible Events`
  header is renamed `🔬 Research Notes` and the per-line 🔥 marker is
  removed for unpriced picks, matching the Telegram card. 🔥 is used
  only when `_enh_status == "ELIGIBLE" and enhancement_priced`.
  *Why:* the .txt report was calling unpriced research "fire" while
  Telegram called it "microscope".

- **T36  Telegram chunker shared.** The 3800-char split lives here so
  `notify.py` does not reimplement it.

### src/edgefactory/sources/scoutingstats.py

- **T37  Real capture timestamp.** Each emitted odds row carries
  `captured_at` = current UTC time, and `status` is set from the
  source row's lifecycle field (`"L"`/live, `"F"`/finished, upcoming
  otherwise). Rows marked finished/live are omitted by the
  enhancement accumulator regardless of score presence.
  *Why:* without this, T13 and T6 can't work.

### .github/workflows/daily.yml

- **T38  Test step.** Add `PYTHONPATH=src python3 -m pytest -q` after
  dependency install. A failing test blocks stateful notification
  steps.
  *Why:* red tests currently ship green because no test step runs in
  CI.

- **T39  Clean stale cache.** Before restoring committed data, delete
  any `localdata/whatsapp_*`, `localdata/sent_ledger_*`, and
  `localdata/shadow_sent_ledger_*` files that are not tracked by git,
  so a stale cache cannot suppress or trigger sends.
  *Why:* cache-only files survive `git checkout HEAD`.

### Tests

- **T40** New tests: timezone parsing (every offset in the 08-08
  slate), forecast-vs-official mode selection, reverse-match
  orientation, NaN/Inf rejection, median price clipping, BTTS
  fallback exclusion, provider first-success, Telegram chunk
  boundaries, `--force` ledger merge, void settlement, OU/BTTS
  settlement, post-kickoff price rejection, and SRL rejection.
- **T41** Existing 242 tests stay green; the ML-META path is
  explicitly skipped with a `pytest.mark.skip("percent-scale retrain
  pending")` marker until T-ML lands.

## What we are trading off

- **More picks will be filtered.** The core EV gate, the SRL filter,
  the LIVE filter, and the unpriced-fallback fix together reduce the
  number of pushes and shadow rows. That is the correct trade: a
  quieter bot that only sends lines it can price is more trustworthy
  than a noisy bot that sends everything.
- **Morning run timing.** The 02:00 SAST scheduled run is still early
  for same-day price feeds. With T31, a forecast no longer suppresses
  the morning baseline, so the first real morning run may be a later
  scheduled slot. We accept a later baseline over a stale forecast.
- **Median clipping may reject a genuine stray longshot.** The 20%
  threshold is conservative; genuine 30/1 prices are rare in the
  markets this bot bets (1X2, totals, BTTS) and are almost always an
  alias error when they appear. Anomaly logging lets us review.
- **No retroactive recertification.** Existing certified rules keep
  their certified status until their next scheduled recert; new rules
  are subject to the calibrated-edge gate. This avoids a sudden empty
  slate.

## Rollout plan

1. Land T1–T11 (picks_today) + T13–T17 (enh_pricing) + T37 (adapter)
   behind `EDGE_FACTORY_HARDENED=1` (default off for one run).
2. Land T18–T24 (audit) and T25–T30 (notify) — these are read-path
   and dispatch changes, safe to enable immediately.
3. Land T31–T39 (daily/workflow) with the concurrency group and test
   step.
4. Run one full 24h cycle with HARDENED off to confirm parity on
   tomorrow's slate.
5. Flip HARDENED on by default. Remove the flag after a week of clean
   runs.
6. Schedule ML retraining as a separate ticket; until then ML-META
   rules are skipped from certification.

## Open questions for the operator

1. At what SAST local time should the official morning baseline run?
   02:00 is too early for same-day Bzzoiro/TheOdds captures.
2. Should `SOURCE_FALLBACK` (forebet model price) ever be pushable,
   or always audit-only?
3. What is the configured The Odds API monthly budget? The freshness
   tightening (T13) may increase same-day fetches.
4. Do you want to retain Meta/Twilio compiled-in (dormant) or strip
   them until a paid tier is needed?
5. After T23, is 0.5 the right haircut, or should it be per-bookmaker
   based on margin?

The unified diff follows in a companion file (`REDTEAM_FIX_DIFF.diff`).
It is generated against commit 5d1fd1b and is intended to be applied
on a clean checkout, reviewed, and then split into reviewable commits
matching the T-numbers above.
