# R2 pack — dynamic floors (relayed 2026-10-12)

**Provenance:** the round-4 instruction pack was relayed to this workspace in chat by
the reviewer; the reviewer's own sandbox is not available to this workspace, so this
file is the workspace's own copy, written from that relay. It is R2's source of truth.
Where a relayed line is quoted, it is quoted as relayed; where this file records a
*decision* about the pack (the round-6 supersessions), it says so and says why.

**Round-6 supersessions (the only changes to the pack):**

| pack says | round-6 ruling |
|---|---|
| §0/§7: "PR #2", "one PR per task", "push after #61" | **overridden** — everything lands on the session branch as its own distinguishable commit set, pushed as *checkpoints*; PR #61 is the single vehicle and the chain is the unit of review. The merge ends push access, so nothing waits for a second PR. |
| §6 B-7: "push after #61" | **overridden** the same way. |
| §5: "suite ≥ 2817 (the pack's count at packing time)" | superseded by this branch's current count: **2907** (CI-exact, fixed order). The requirement stands: *at least* this branch's count at the tip, i.e. no test lost. |
| §1 reviewer numbers | **re-measured first** on the moved base (`origin/main` = `dda42ee`) before any design work: `handoff/r2_sec1_remeasure.txt` — every number reproduces; nothing adjusted. |

Everything else stands as written below.

---

## §0 — What this round is

Add **dynamic price floors** to the enhancement lane, pre-merge, on the evidence the
committed registry already holds — without touching today's card (the lane's records
are additive), without loosening anything (tighten-only), and without lookahead.
The floors are the lane's own minimum acceptable price per (market, slice), derived
from the registry's realised hit-rate evidence with the same statistic the registry
already uses to certify a market.

## §1 — The numbers this round is designed against (re-measure before use)

From the pack, on the registry as committed (base has since moved to `dda42ee`; the
round-6 re-measurement is in `handoff/r2_sec1_remeasure.txt`):

* priced records: **409**; distinct team tokens: **578**
* teams with ≥10 records: **0**; ≥5 records: **8** (Celtic 6, Man City 6, Feyenoord 6,
  Arsenal 5, The New Saints 5, Benfica 5, Barcelona 5, Kristiansund BK 5)
* `league` field: **0/409** records carry one (the plumbing §3 exists because of this)
* per-market priced n: `match_over_25@v1` **350**, `match_over_15@v1` **33**,
  `match_over_35@v1` **16**, `btts_yes@v1` **7**, and three markets with n = 1
  (`away_under_25@v1`, `away_under_35@v1`, `match_over_45@v1`)
* the trap: `match_over_15@v1` is **72.7 % hits (24/33) and −5.78 u** — a high hit rate
  that still loses money at the prices actually paid. **This slice must never be used
  to lower a floor**, and no floor may be derived from hit rate alone.

## §2 — The rules (unchanged)

1. **Three levels, inheritance.** `market` (root) → `league` → `team`. A slice
   **inherits** its parent's floor unless its own evidence unlocks a deviation. A
   **team** slice never deviates (report-only; too thin to certify).
2. **Evidence gate.** A slice may deviate only with `n ≥ MIN_PRICED_N` (30) **and** a
   Wilson lower bound, using the repo's own `wilson_lb(hits, n)` and
   `WILSON_Z = 1.959963984540054` — the same statistic as the PAPER→ELIGIBLE gate.
   Thin slices self-disable (they keep the inherited floor).
3. **Tighten-only.** `floor(slice) = max(floor(parent), 1 / wilson_lb(hits_slice, n_slice) + margin)`.
   A slice may only ever *raise* the floor it inherits. **Loosening requires an
   explicit operator ruling** (n ≥ 30, LB above realised breakeven + margin, and the
   harness A/B on the table — B-2: stop and bring the A/B, never loosen quietly).
4. **No lookahead.** Day D's floors use only records with `date < D`. Derive daily
   from the committed registry; render the derivation into the day's slip and state;
   it must be re-derivable from the registry commit alone (no new literals, no second
   source of truth).
5. **Variant choice by harness, not by feel.** Pick variants with
   `replay_harness --enhancements` on the acceptance metric below; extend the harness
   to slice-aware arms — do not write a second harness. Honour the n < 30 noise flag.
6. **Acceptance metric: mean log growth per bet-day**, A/B against the current
   (single floor) behaviour, with the `MIN_ACCAS` no-bet frequency printed for both
   arms.
7. **Flag-off must stay byte-identical** (round-3 proof re-run): `EDGE_FACTORY_ENH_BOARD`
   off → the board and slip are unchanged, byte for byte.
8. Everything the lane already guarantees still holds: price alone sets value, no EV
   veto, no floor from form/H2H, nothing that changes today's card, and the named
   constants (`MIN_PRICED_N`, `MIN_MULTI_SOURCE_FRAC`, `BENCH_WINDOW_DAYS`,
   `BENCH_MIN_N`) are **not** touched.

## §3 — Plumbing (additive)

* At settle time record `league` and the `home`/`away` keys on each registry record
  (additive fields; the dedup key is unchanged).
* **Backfill** the existing 409 records by matching `date + match` against
  `git show origin/main:localdata/picks_<date>.json`, and **report the coverage %**.
  Unmatched records keep `league: null` and simply **inherit** their parent's floor.
* `ELIGIBLE`/`BENCHED` transitions and the four named constants: untouched.

## §4 — One entry point

`derive_floors(registry, as_of, *, parent_floors, margin, min_n=MIN_PRICED_N)` in
`src/edgefactory/enh_registry.py`:

* pure and deterministic (same registry + as_of ⇒ same floors, no clock, no I/O);
* per-slice inputs and outputs, each with `basis ∈ {inherited, market, league, team}`;
* the lane **consumes** it and never re-implements it;
* the slip leg renders `[registry … · floor … · basis … · book]`;
* the day's derivation table goes into the lane artifact and the lane state.

## §5 — The nine proofs

1. per-level refusal table (which slices are refused and why);
2. thin slice self-disables (n = 6 with a lucky 5/6 stays on the inherited floor);
3. no-lookahead diff (day D's table is unchanged by day D's own records);
4. `match_over_15` is **not** lowered on 72.7 % evidence;
5. tighten-only clamp visible (a slice cannot land below its parent's floor);
6. a hand re-derivation equals the slip's rendered derivation, row for row;
7. harness A/B on mean log growth per bet-day **plus** `MIN_ACCAS` no-bet frequency,
   both arms;
8. flag-off byte-identical board/slip (the round-3 proof, re-run);
9. suite ≥ this branch's count (2907), no test lost.

## §6 — Reporting (as relayed)

* every derived number printed, raw;
* the incident asks (below);
* artifacts under `handoff/`, committed early;
* raw output is the evidence — no claim without a command's output.

**B-7 (superseded as noted above):** "push after #61" → push checkpoints now.

## §7 — Named commits and the report

At least these commit subjects (named, never squashed):

* `floors: derive per-slice floors from Wilson evidence`
* `registry: record league and team keys`

Report in the PR body: the PR URL, the commit SHAs, per-file sha256 at that SHA, and
raw URLs where relevant.

## The three incident asks (round 6, land with the incident memo)

* **(a)** the 2026-10-12 demo run's **outbound request count** — from the receipt, or
  the word **"unknown"**, never an estimate;
* **(b)** the **pre-run status** of the two tracked files it touched, with sha256
  before and after, so "restored from HEAD" is only claimed if HEAD was their pre-run
  content;
* **(c)** the scratch redirect made **reusable**: one tiny shared helper under
  `handoff/`, used by every driver in the chain, named in the PR body's incident note.

Answered in `handoff/incident_2026-10-12.md` (+ `handoff/incident_2026-10-12_outbound_count.txt`,
helper `handoff/scratch_localdata.py`).
