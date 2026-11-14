# EXPERIMENT 01 — lane closeout (ungated experiment lane vs protected main)

Status: **CLOSED. Single production lane stands.**
Compiled 2026-10-02 from read-only inspection of the experiment branch.

Source of record (READ ONLY — never modified, never dispatched, never deleted
by this bundle):

| item | value |
|---|---|
| branch | `arena/01a0f2b3-edge-factory` (PR #18, CLOSED, not merged) |
| head sha | `e42e5681309eb5a70560ba67bf9a1ea28d9335ca` (`e42e568`, 2026-10-02T06:13:36Z) |
| fetched as | `refs/pull/18/head` (local read-only ref `exp/pr18`) |
| ledger files read | `localdata/auto_tickets_state.json`, `localdata/auto_tickets_performance.txt`, `localdata/auto_tickets_slice_ledger.jsonl`, `HANDOVER.md` |

No file on that branch was written, no workflow on it was dispatched, and
nothing from it was merged into this branch. Numbers below are transcribed.

---

## 1. Thesis

The experiment lane existed to test one claim: **that running the card engine
with the integrity gates relaxed — riding uncorroborated/sole-source prices,
accepting horizon (future-dated) selections, and tolerating a non-durable
freeze marker — would produce a better bank than protected main, and that the
engine's state-integrity work could be judged by the bank curve it produced.**

Secondary claim, from the branch's own standing verdict: *"Engine/state
integrity: PR #18 is safer than main."* That half was tested too.

Protected main is the control: price corroboration gate, kickoff guard,
same-day-only policy, independent settlement, `auto_tickets.py` as sole owner
of tickets/staking, abstention valid.

---

## 2. Outcome

### 2.1 Bank curve (experiment lane, `auto_tickets_state.json` @ `e42e568`)

35 bet-days, 2026-08-27 → 2026-10-01, base 100% of capital.

| date | accas (odds / result) | bank % of capital |
|---|---|---:|
| 2026-08-27 | @1.60L @1.74W @1.30W | 106.2 |
| 2026-08-28 | @1.75W @1.89W @1.82L | 105.3 |
| 2026-08-29 | @1.69W @1.70W @1.52L | 101.2 |
| 2026-08-30 | @1.26L @1.84W @2.13W | 112.3 |
| 2026-08-31 | @1.48W @1.58L @2.36L | 103.9 |
| 2026-09-01 | @1.42W @1.68W @2.25W | 133.2 |
| 2026-09-02 | @1.64W @2.77L @1.52W | 134.9 |
| 2026-09-03 | @1.56L @2.32W @1.41W | 143.1 |
| 2026-09-04 | @2.01L | 125.3 |
| 2026-09-05 | @1.62L @1.57L @1.96L | 97.4 |
| 2026-09-06 | @1.61W @2.29L @1.85W | 102.4 |
| 2026-09-07 | @1.76L @2.85L | **68.3** (lane trough) |
| 2026-09-08 | @1.82W @2.41W @2.49W | 96.5 |
| 2026-09-09 | @1.69W @1.68W @2.28W | 124.9 |
| 2026-09-10 | @1.76L @1.83L | 93.5 |
| 2026-09-11 | @2.10L @1.76W | 106.5 |
| 2026-09-12 | @3.15L @2.16L | 83.8 |
| 2026-09-13 | @2.03L @1.70W | 81.2 |
| 2026-09-14 | @1.83L @1.77W | 79.3 |
| 2026-09-15 | @1.56W @1.59W | 88.5 |
| 2026-09-16 | @1.84W @1.80W | 103.4 |
| 2026-09-17 | @1.97W @1.72W | 122.0 |
| 2026-09-18 | @1.62W @1.95W | 142.8 |
| 2026-09-19 | @1.56W @1.81L | 135.8 |
| 2026-09-20 | @1.77W @1.71W | 158.1 |
| 2026-09-21 | @1.70L | 140.3 |
| 2026-09-22 | @1.49L @2.04L | 109.1 |
| 2026-09-23 | @2.04L @2.01W | 93.6 |
| 2026-09-24 | @1.61W @1.92W | 111.5 |
| 2026-09-25 | @2.18L @1.92W | 110.4 |
| 2026-09-26 | @1.77W @1.56W | 124.3 |
| 2026-09-27 | @1.76W | 136.1 |
| 2026-09-28 | @2.55W | 159.5 |
| 2026-09-29 | @1.66W @1.73W | 184.5 |
| 2026-10-01 | @1.95W | **204.5** (lane close) |

Take-profit notification: one, 2026-10-01, +104.5% that cycle, next target
409.1%. Open slips at close: 2.

### 2.2 Settled record, side by side

| metric | experiment lane (`e42e568`) | protected main (`13f8f80`) |
|---|---:|---:|
| bet-days | 35 | 35 |
| accas settled | 77 | 79 |
| won / lost | 49W / 28L | 48W / 31L |
| acca hit rate | 63.6% | 60.8% |
| closing bank | **204.5%** of capital (x2.05) | **126.7%** of capital (x1.27) |
| peak bank | 204.5% | 184.5% |
| trough bank | 68.3% | 68.3% |
| max drawdown | 52.3% | 52.3% |
| take-profit notifications | 1 | 0 |
| legs in slice ledger | 338 rows (0 shadow; 160 `slip`-sourced, 178 `replay`-sourced) across 88 dates | — |

Read the gap honestly: **+77.8 points of bank on +2.8 points of hit rate over
77 vs 79 accas.** Two extra acca wins and a different stake path explain the
whole divergence; the two lanes share an identical trough (68.3%) and an
identical 52.3% max drawdown. This is one 35-day sample at acca odds ~1.5–3.0.
Nothing in it is a statistically distinguishable edge.

### 2.3 Failure classes observed in the lane

**(a) Uncorroborated / rescue prices ridden into live cards.**
Quarantine census on ridden legs (branch `HANDOVER.md`, Task B, measure-only):
whole archive 242 ridden legs, **98 flagged (40%)** on 35 of 54 days;
in-season ≥08-01, 182 ridden legs, **93 flagged (51%)** on 32 of 35 days.
Flag breakdown: `SCOUTINGSTATS_SOLE` 74 (all in-season), `BETEXPLORER_RESCUE`
12, `SOURCE_FALLBACK` 2, `BZZOIRO_PRIMARY` 1; quarantine reason
`scoutingstats_sole_source` 74; buckets `WATCHLIST_UNCORROBORATED_PRICE` 27,
`WATCHLIST_UNKNOWN_CTX` 24, `SKIPPED_VETO` 47. Day-block bootstrap
(4000 draws, paired days, seed 20260906): ΔROI(flagged − unflagged) whole
archive p10 −5.2%, 90% CI [−8.0%, +18.5%] (32 paired days); in-season p10
−6.3%, CI [−9.3%, +19.0%] (29 days). **Over half the in-season lane card was
priced off a single unconfirmed source, and the CI spans zero by ~27 points.**
The lane's bank was therefore not attributable to selection skill — it was
drawn from a price population main's 7% corroboration gate rejects.

**(b) Rotation — a frozen card that was not actually frozen.**
`.gitignore` allowlisted `auto_tickets_20*.txt`/`.json` but **not**
`auto_tickets_20*.frozen`. The slip was committed, the marker was not, so on
any cache miss or fresh checkout `frozen.exists()` was false and the engine
rebuilt a card for a date already frozen **and already staked** — the
operator's placed bets rotated under them. Fixed late on the branch
(`9b5b428`), i.e. the lane ran most of its life with a freeze that survived
only in the Actions cache. Related: *"Frozen-card status was date-level"* —
when the slate changed after a freeze, selections never carded inherited
frozen status.

**(c) Ghost legs / horizon staking.**
2026-09-06: the slip was already frozen at 09:13 **with a ghost leg in ACCA
#3** before any code change could stop it; operator instruction on the branch
was "bet ACCA #1 and ACCA #2 only". The ghost row was a `scoutingstats_odds`
row with a clock-only kickoff (`22:30`, no date/zone) that *also* carried
`WATCHLIST_UNCORROBORATED_PRICE` / `scoutingstats_sole_source` — failure
classes (a) and (c) on the same leg. Separately, the 2026-10-01 run wrote a
future-dated card (`auto_tickets_2026-10-02.txt`) and **no same-day slip**;
both timing gates were written `target == today`, so the horizon card skipped
the build-hour gate, could never freeze, and still entered state as an open
slip staking **21.116% of capital a day before the event**
(`HORIZON_TICKET_POLICY` → `same_day_only` fixed it on-branch).

**(d) State divergence as a merge blocker.**
~40 diverged generated state files (bank ledger, binary CLV and odds
snapshots). The branch's own correction notes the merge base is `da5b4f1` and
that the blocker is *"which lane's state is authoritative"* — exactly the
dual-production hazard the single-lane directive exists to prevent.

---

## 3. Conclusion, with numbers

1. **The ungated lane did not demonstrate an edge.** +77.8 bank points on
   +2.8 points of hit rate (63.6% vs 60.8%) over 77 vs 79 accas, with an
   identical 68.3% trough and identical 52.3% max drawdown. Two acca outcomes
   and stake path, not method.
2. **Its bank is contaminated by the very prices the production gate blocks.**
   51% of in-season ridden legs flagged; 74 legs `SCOUTINGSTATS_SOLE`; ΔROI CI
   [−9.3%, +19.0%] — not separable from zero. A bank built on 51% unconfirmed
   prices is not a result that transfers to a corroborated lane.
3. **It shipped at least three live-money defects main did not:** a frozen
   card that could rotate under placed bets, a ghost leg in a frozen ACCA, and
   21.116% of capital staked on a future-dated card that could never freeze.
4. **The one genuine transferable finding is the freeze-durability gap.** The
   branch's claim that *main has the same gap* is correct in kind: main's
   freeze marker is a per-day `localdata/auto_tickets_*.frozen` file whose
   durability depends on it being present. That finding is being banked —
   **T2 of this bundle replaces per-day `.frozen` files with write-once
   `frozen_by_date` entries inside the committed tickets state**, with legacy
   read-side compatibility. The lane's one useful output is absorbed without
   the lane.
5. **Dual production was the real cost.** Two banks, two state trees, ~40
   diverged generated files, and an unanswerable "which state is
   authoritative" question. No bank number justifies that.

**Verdict: the experiment is closed as NOT PROVEN on bet quality, and NEGATIVE
on operational safety.**

---

## 4. Directive restated

- **Single production lane.** `main` is the only lane that builds, stakes,
  settles, or persists bank state. No second lane may run the card engine.
- **`auto_tickets.py` remains the sole owner of tickets and staking.**
- **Abstention is a valid outcome.** A no-bet day is a result, not a failure
  to be rescued by relaxing a gate.
- **No production re-mine without explicit operator promotion.** Gap-only
  mining; existing rows win on collision; independent settlement; raw +
  checksum + provenance per crawl; hist namespaces only.
- **No `edge >= 0` hard gate, no proxies/stealth/CAPTCHA bypass,
  `EDGE_FACTORY_FOREBET_BROWSER=off`.**

### Operator action — branch deletion

The experiment lane is finished. For deletion at the operator's discretion:

```
branch: arena/01a0f2b3-edge-factory
head:   e42e5681309eb5a70560ba67bf9a1ea28d9335ca
PR:     #18 (CLOSED, not merged)
```

This document is the retained record; the branch carries no unique un-banked
finding beyond the freeze-durability gap now addressed in T2. Deletion is an
**operator** action — this bundle did not and will not delete, modify, or
dispatch that branch.
