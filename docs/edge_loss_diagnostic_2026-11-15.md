# Edge-lane losing streak — diagnostic run 2026-11-15

**Question:** why is edge losing lately; is the bleed odds>1.5 + confidence<60%;
would double-chance @odds>1.7 do better?

**Data:** committed `localdata` on `origin/main` (persist run 43716676848, 15:48 SAST):
daily rolling tickets (30d), `auto_tickets_performance.json` settled history,
`settled_results.json` (53,402 scores), `auto_tickets_slice_ledger.jsonl`,
theoddsapi/oddspapi monthly 1x2 odds archives, oddspapi market census.
Harness: throwaway scripts joining printed slips → settled leg results → odds triples.

---

## 1. The slump, quantified (rolling main lane, 2026-10-17 → 2026-11-15)

- 48 settled accas: **26W/22L, +89.4% net on 1708% staked (+5.2% ROI)** — the window
  is positive overall; the *lately* part is concentrated.
- Bank trajectory: 454.8% peak after 11-08 → **257.8% today** (−197% of capital in 4 bet-days).
- **Two days are the whole slump:**

| Date | Result | Day net | Deployed | Legs |
|---|---|---|---|---|
| 11-09 | 0W/2L | **−113.8%** | 113.8% (max of window) | 1.69@52%, 2.35@42%, 2.05@48%, 1.94@47% |
| 11-12 | 0W/2L | **−85.3%** | 85.3% | 1.61@62%, 1.85@48%, 2.00@49%, 2.06@49% |

Every other window day netted roughly breakeven-or-better except 11-13 (−9.9%).

## 2. Hypothesis 1 — "odds >1.5 + confidence <60% is bleeding us": CONFIRMED (at slip level)

Leg-level, flat-stake (n=94 settled legs):

| odds band | n | hit | ROI |
|---|---|---|---|
| <1.50 | 63 | 82.5% | **+12.5%** |
| **1.50–1.70** | 18 | 55.6% | **−12.6%** ← the only losing band |
| 1.70–2.00 | 7 | 71.4% | +32.7% (tiny n) |
| ≥2.00 | 6 | 50.0% | +3.5% |

Suspect legs (odd>1.5 & conf<60) as *singles*: n=15, +8.7% ROI — mildly +EV. The damage is
**structural**: inside 2-leg accas at bank-scaled stakes.

Acca-level split (the money table):

| acca type | n | W/L | net (% capital) | ROI |
|---|---|---|---|---|
| contains ≥1 suspect leg | 12 | 4W/8L | **−83.1%** | **−15.0%** |
| clean | 36 | 22W/14L | **+172.5%** | **+15.0%** |

Combined-odds bands: <2.0 → +16.2% (16W/8L) · 2.0–2.6 → **−18.9%** · 2.6–3.5 → +60.7% (n=5) · ≥3.5 → **−21.7%**.

Counterfactual: skipping every acca with a suspect leg changes the window from
+89.4% to **+172.5% of capital** — roughly +83% better, and bank would sit ≈341%, not 258%.

**The amplifier:** staking is 12.5% of *free bank* per acca — after the green run to 455%,
each acca staked 56.9% of capital on 11-09, the worst card of the month. Maximum size
landed on minimum-quality legs.

**Why the gate didn't save us:** the assay labels these legs `SKIPPED_VETO`, but
`BUCKETS` in `scripts/auto_tickets.py` explicitly includes `SKIPPED_VETO`
(operator ruling 2026-09-08, "taken against the evidence", in-code comment). The veto
is an assay label, not an admission gate: on 11-12, legs the ledger itself marked
SKIPPED_VETO (Türkiye @1.85/48%, Italy @2.00/49%, Albania @2.06/49%) printed anyway.
As flat singles the veto cohort is genuinely +EV (+8–10%, both the assay and my settle
join agree) — so the fix is **exclude the combination from accas**, not from the universe.

**Culprit mechanism — draws.** ≥6 of ~10 losing legs across red days died by draw:
Antalyaspor 1-1, Port FC 1-1, Deportivo Garcilaso 0-0, Plymouth 1-1,
Slovakia 2-2 (a *clean* leg: HOME @1.40, stated 63%), Salford 1-1.

## 2b. Hypothesis 3 (operator) — "the international break is where it started": CONFIRMED as the trigger

Split at break start (11-09, the Monday after the last full club weekend):

| regime | days | legs | day-net total | day-net avg | suspect-leg share | avg conf |
|---|---|---|---|---|---|---|
| club season (10-17 → 11-08) | 22 | 80 | **+286.9%** | +13.0%/day | 9% | 68.9% |
| break (11-09 → 11-15) | 5 | 20 | **−197.4%** | −49.3%/day | **40%** | 61.3% |

- The two catastrophic days (11-09 avg conf **47.2%**, avg odd 2.01; 11-12: 52.0%, avg odd 1.88)
  are the two worst-confidence cards of the whole window, both 100%/75% suspect.
- Fixture mix flips: 7 international + 3 thin-club + 10 uncovered legs during break.
  Settled legs by class (flat stake): club-major **90% hit / +30.2%**; international 50% / −22.3%;
  club-minor 50% / −26.5%.
- 11-09's card was literally Plymouth Parkway vs Berkhamsted (**English 7th tier**), Pineto
  (Serie C), Hvidovre (Danish 2nd tier), Kristiansund (Norwegian relegation-playoff fringe).
- November odds-archive coverage: every Nations League break fixture HAS books';
  **13 of the 21 break-day legs sit in fixtures with ZERO coverage** from theoddsapi/oddspapi
  (all basement clubs + the Sweden–Bosnia friendly) — i.e. single-source or watchlist-grade
  pricing exactly when conf was lowest.
- Mechanism chain: break drains top-league volume → miner reaches into internationals +
  uncovered micro-leagues → stated conf collapses (47–52%) and odds lengthen (1.9–2.1) →
  admission policy (SKIPPED_VETO ticket-eligible) lets them print anyway → bank-scaled staker
  (12.5% of free bank per acca, peaked at the break's eve) puts RECORD stakes on the
  weakest card of the month.
- Caveats for honesty: midweek 11-03/11-04/11-06 also ran 50% suspect shares and won
  (Champions League slates at proper prices) — suspect legs on *covered, top-tier* cards are
  survivable; suspect legs on *thin-break* cards were not. And big red days existed pre-break
  too (10-25 −71.7% at 0% suspects) — variance is not new; the regime made it systematic.
- **Outlook → outcome:** break runs to ~Nov 17/18 (club football back 11-21/22). 11-15's two
  accas (@4.62: Godoy Cruz @2.10/76% + Portimonense @2.20/72%; @2.64: Sochi @1.65/75% +
  Croatia @1.60/75%) **both lost** (operator report 11-15; settled store catch-up pending at
  the 18:47 persist) → day-net ≈ −64.4%, bank ≈ **193.4%**.
  **Break-week tally: 11-09 −113.8 · 11-12 −85.3 · 11-13 −9.9 · 11-14 +11.7 · 11-15 −64.4
  = −261.7% of capital, accas 2W/8L.** Bank has round-tripped 455→193 in five bet-days —
  all of it inside the international break.

## 3. Hypothesis 2 — "double chance @ odds >1.7 would do better": UNTESTABLE as stated, structurally mismatched

- Only 33/204 mined legs (slip ctx, since 09-15) joinable to full book 1X2 triples
  (archives capture what sources served; thin). Derived, margin-modelled DC prices
  (overround-stripped, ~5.5% re-margined): **average 1.11** — the miner picks strong
  favourites (1x2@1.2–1.6 ⇒ DC 1X/X2 ≈ 1.05–1.25).
- **n = 0 legs pass DC>1.7.** At a book, DC>1.7 corresponds to 1x2 sides priced ≳2.6–2.8
  — a fixture universe our miner simply never surfaces. The rule doesn't rescue these
  slips; it changes the entire slate.
- Sample DC flat ROI on convertible legs: −10.6% (n=33, avg price 1.11) — draw insurance
  at near-1.0 prices does not pay for itself.
- Draw-death pattern *is* real (§2), but DC on favourites is the most expensive insurance
  on the market; draw-no-bet is cheaper but equally not capturable today.

**Blocker to real evidence:** oddspapi publishes **market 101902 "Double Chance Full
Time"** — seen **116×** in the November census — but `_classify_catalog_entry` routes
"double chance" to `unsupported_double_chance` before the priced-type step; parse
receipts show **448 DC rows skipped**. Parser support for `double_chance` already exists
(market `dc` emission via `_DC_SELECTION`), `ml_paper` already understands
`double_chance`, and `odds_normalization` keeps `dc` OUT of 1x2 boards (the 2026-10-11
Vidar/Brattvag incident class stays contained). So a small classifier change starts
capturing real DC prices from tomorrow → re-run this harness on real prices in 2–4 weeks.

## 4. autobets_ML held accas — corrected answer

Previous "one-tick lag, self-heals" was **wrong**. The paper lane is hard-blocked by
`localdata/autobets_ML_integrity_block.json` (5 receipts listed invalid, from 11-13/11-14),
written by the 11-15 10:07 deferred-restore run. `receipts()` refuses to read anything
while the marker exists; the design **never auto-clears** ("Never clear an integrity block").

**Evidence review performed now:** all 5 quarantined receipts pass
`ml_paper.validate_record()` under current main code (schema/checksum/date/freeze chain,
bets, concentration, admission). The block is *stale*: it was written under the
mid-migration code state and nothing re-evaluates it. While it stands, the 6 HELD ML
accas from 11-14 cannot settle and no new ML paper accas print. Live lanes are untouched
by design. Unblock = operator deletes the one marker file (conflict copies in
`localdata/autobets_ML_conflicts/` remain as evidence).

## 6. Problem tally (each with evidence)

- **P1 — Admission hole.** SKIPPED_VETO legs are ticket-eligible (2026-09-08 ruling, made on
  singles evidence). Suspect cell (odd>1.5 AND conf<60%) inside accas: 12 slips 4W/8L,
  **−15.0% ROI, −83.1% capital** vs clean accas +15.0% / +172.5%. 100% of the four
  catastrophic accas contained suspect legs.
- **P2 — No slate/regime awareness.** Break slates collapse input quality (avg conf 47–52%
  on the two disaster days vs 69% club-season; 13/21 break legs in fixtures with ZERO
  theoddsapi/oddspapi November book coverage) and the lane fires full size regardless.
- **P3 — Stake amplifier.** 12.5% of *free bank* per acca is anti-martingale across regime
  boundaries: record deployment (113.8% of capital on 11-09) landed on the weakest card.
- **P4 — No combined-price containment.** Two-leg slips routinely reach 3.97–4.62 combined;
  bands ≥2.0 ran −18.9% / −21.7% ROI vs +16.2% for <2.0.
- **P5 — Draw deaths, no insurance priced.** ≥6 of ~10 red-day culprit legs died to draws.
  DC/DNB never captured: oddspapi DC market 101902 catalogued 116× in Nov but classified
  unsupported (448 rows skipped). Derived DC on our favourites ≈1.11 → a DC>1.7 rule
  selects nothing on the current slate.
- **P6 — Evidence exists but is not enforced.** The assay already tags these legs
  (SKIPPED_VETO) and tracks them as *singles* (+8–10%) — nothing measures
  bucket-in-acca performance or feeds it back into admission.
- **P7 — ML lane ops debt.** Stale integrity block since 11-13 (5/5 quarantined receipts
  validate under current code; never auto-clears by design) → 6 held accas unsettle-able;
  comparison lane dark during the exact week we needed it.
- **P8 — (context) ENH lane.** Bank 23.5%, 21W/33L over 28 bet-days — likely the same
  slate-regime cause; not examined in this run.

## 7. Solution brainstorm

| # | Fix | Addresses | Evidence | Effort | Tradeoff / note |
|---|---|---|---|---|---|
| S1 | Reject accas containing a leg odd>1.5 & conf<60 (or halve-stake) | P1 | +89.4%→+172.5% window counterfactual | tiny (code + pins) | partly reverses 2026-09-08 ruling — for the acca *product* only, singles universe unchanged |
| S2 | Break regime gate: dynamic morning coverage scan (corroborated-price share < threshold ⇒ tighten to conf≥60 & odd<1.5, else notify-only) | P2 | §2b; generalizes to any thin slate, no calendar to maintain | small-mid | standing down thin days forfeits their (negative-EV) learning; paper-trade mode keeps evidence w/o stakes |
| S3 | Stake cap at fixed % of capital and/or quality-scaled stakes | P3 | 11-09: cap@25%/acca would have cut the damage ~56% | tiny | throttles the compounding that built +455%; best *after* S1/S2 so caps bind only on degraded cards |
| S4 | Combined-odds cap <2.6 | P4 | band ROIs +16.2 vs −18.9/−21.7 | one constant | cuts some big-win days (2.6–3.5 band +60.7% on n=5) |
| S9 | League-conditioned admission: veto (or ¼-stake) acca legs from INTL / ENG-lower / Asia-Afr groups; extend to minor/unknown during flagged break days | P2 | pure-major accas +60.4% vs negative-group −15.9% ROI (60d) | small | group taxonomy must come from NEUTRAL features (coverage/tier), not these in-window ROIs — see §10 |
| S5 | Wire oddspapi market 101902 (fulltime DC) into capture | P5 | 116 catalog sightings/mo; 448 rows dropped | small (classifier + tests) | enables real DC-price evaluation in 2–4 wks; derived data says DC on OUR slate averages ~1.11 → insurance price, not a profit line; zero-coverage break fixtures still uncovered |
| S6 | Self-guard loop: daily "in-acca ROI by odds×conf cell" block on the ticket assay; auto-tighten when a cell's 30d acca ROI goes negative with LB significance | P6 | ladder already computes LB bands per bucket | mid | the lasting version of S1; prevents "gate rots silently" |
| S7 | Delete stale `autobets_ML_integrity_block.json` + daily "conflicts revalidated: 0 remain" line in persist so staleness is visible without auto-clearing | P7 | 5/5 receipts pass validate_record today | trivial | preserves fail-closed design; restores the comparison lane |
| S8 | Same treatment for ENH lane after main lane stabilizes | P8 | 21W/33L | — | later |

**Recommended sequence:** S7 (free), **S1+S4 in one PR** (the money), S2 dynamic gate (next),
S5 (enabler for your DC hypothesis). S3 after a week of S1/S2 data. S6 when S1 shows teeth.
None of it touches workflows — all code + tests.

## 5. Recommendations (operator decisions) — superseded by §7 table

1. **Acca admission guard:** reject (or halve-stake) any acca containing a leg with
   priced-odd >1.50 AND stated conf <60%; optionally cap combined odds <2.6.
   Window counterfactual: +89.4% → +172.5%. This reverses part of the 2026-09-08 ruling —
   that ruling compared buckets as singles; the harm is in the acca product.
1b. **Break-regime overlay:** during FIFA international windows (or when the scheduled
   slate's archive-odds coverage collapses — measurable per-day, e.g. share of candidate
   fixtures with corroborated prices), additionally require conf ≥60% AND odd <1.50
   (i.e. only the historically-safe cell), or stand the lane down to notification-only.
   Break days were 40% suspects at avg conf 61% vs 9%/69% in club season.
2. **Wire oddspapi market 101902** (fulltime double chance) so real DC prices land in
   `oddspapi_odds` archives; re-evaluate DC>1.7 on real prices in 2–4 weeks. Zero DC
   coverage among current slips means hypothesis 2 cannot be validated until this lands.
   **✅ LANDED this session (capture vocabulary rewire):** full-time DC + DNB now
   classify (`double_chance` / `draw_no_bet`), parse to (`dc`, 1x/x2/12) /
   (`dnb`, home/away) with order-insensitive names + ambiguity/unresolved fails, and
   canonicalize in `odds_normalization` (so boards stop recounting them as unsupported
   misses). Half-time/second-half variants still refuse at the period gate.
   7115-pass suite verified incl. admission pins for both veto classes.
   The one remaining blocked piece (unrelated to betting): the DC>1.7 retrospective
   needs the provider's full catalog outcome-name strings for ids 101902/10214
   (e.g. exact "Home or Draw" spelling) — not persisted in the repo, and outbound
   network from the analysis sandbox was restricted. One codespace call to
   `python3 scripts/probe_oddspapi_markets.py` closes that gap for a future-run ledger
   test; capture does NOT wait on it.
3. **Clear the stale ML integrity block** after the recorded review above; the 6 held
   11-14 accas then settle on the next paper tick.
4. Today (11-15) ACCA#1 @4.62 (2.10@76% + 2.20@72%) sits in the historically losing
   ≥3.5 combined band — flagged, pending tonight.

## 8. Counterfactual re-simulation — "where would we be with the fixes active?"

Day-by-day bank re-simulation over the whole 30-day window (10-17 → 11-15), real printed
odds/results/stakes, stakes re-derived per world (`printed stake × sim-bank / real-bank`;
win = stake×(odds−1), loss = −stake). **Validation: simulated as-run reproduces every
recorded close exactly.** 11-15 uses the operator-reported double loss.

| world | end bank 11-15 | vs actual | break-week P/L (11-09→15) | max drawdown |
|---|---|---|---|---|
| actual (as-run) | **193.4%** | — | **−261.9%** | 455→193 = −57.5% |
| S1 only (kill suspect-leg accas) | 249.8% | +56.4 | −11.7% | shallow |
| S1+S4 (+combined cap 2.6) | 249.8% | +56.4 | −11.7% | shallow |
| **bundle S1+S4+S2 (break overlay)** | **285.6%** | **+92.2** | **−11.2%** | ~−15% max |
| bundle + stake cap 25%/acca | 294.1% | +100.7 | −17.0% | ~−15% max |

What the bundle actually does during the collapse (fire/veto log):

| date | acca@ | legs (odd,conf) | gate | real outcome |
|---|---|---|---|---|
| 11-09 | 3.97 | (1.69,52)(2.35,42) | veto S1+S4+S2 | LOST ✓ avoided |
| 11-09 | 3.98 | (2.05,48)(1.94,47) | veto S1+S4+S2 | LOST ✓ avoided |
| 11-12 | 2.98 | (1.61,62)(1.85,48) | veto S1+S4+S2 | LOST ✓ avoided |
| 11-12 | 4.12 | (2.00,49)(2.06,49) | veto S1+S4+S2 | LOST ✓ avoided |
| 11-13 | 1.86 | (1.33,71)(1.40,63) | FIRE | LOST ✗ taken |
| 11-13 | 1.69 | (1.30,71)(1.30,67) | FIRE | WON ✓ taken |
| 11-14 | 2.38 | (1.55,60)(1.54,59) | veto S1(S2) | WON ✗ forgone (+42.5%) |
| 11-14 | 2.45 | (1.58,60)(1.55,60) | veto S2 | LOST ✓ avoided |
| 11-15 | 4.62 | (2.10,76)(2.20,72) | veto S4+S2 | LOST ✓ avoided |
| 11-15 | 2.64 | (1.65,75)(1.60,75) | veto S4+S2 | LOST ✓ avoided |

Honest caveats:
- The gates also skip the **winning** suspect cells before the break: 11-03/11-04/11-06
  UCL-midweek cards (three of four suspect accas WON, +155% of capital forgone). The bundle
  enters the break at 297 rather than 455. Net-net it still ends +46–52% ahead — the rule
  trades jackpot upside for survival — but S1's cell is crude (4 of its 12 kills were
  winners). S6 (data-driven cell admission) is the refined version.
- The bundle is **not** variance-proof: 10-25 (−71.7%, two clean accas, 0% suspects) lands
  in every world. What it kills is *systematic* bad-cell exposure, not ordinary losing days.
- Stake-cap ends slightly ahead (+100.7pp) mostly by softening pre-break losers, at the cost
  of throttling compounding in green streaks.

## 9. 60-day panel (2026-09-17 → 11-15, recovered via localdata/archive + git)

Ticket slips recovered from `localdata/archive/auto_tickets/` (54 bet-days, 196 legs).
Legs settled against the warehouse via the repo's own alias/orientation-proof matcher
(188/196 matched; 8 unsettled, excluded). Acca outcomes: perf ledger first (money truth),
leg-derived fallback for recut slips (e.g. 10-15). Sim validation: day nets track history
within rounding; end-anchor 196.2% vs true 193.4% (+1.4% drift over 60d).

### signals replicate on 60d

- **only negative odds band: 1.50–1.70 → −4.9%** (n=35; <1.50 +9.0% on n=130).
  Worst cell overall: **1.50–1.70 × conf 60–66: −24% (n=21)**.
- user cell (odd>1.5 & conf<60) as *singles*: +9.7% (n=18) — not the poison as singles.
  **As accas: suspect-containing 6W/9L, −5.9% ROI (net −35.3%) vs clean accas +7.4% ROI —
  but new on 60d: suspect *accas*' −35.3% net vs clean +148.1% net (additively staked).**
- **international legs −4.4% (n=18) vs club +9.8% (n=170)** — the regime signal replicates.

### counterfactual bank (60d, end = 11-15)

| world | end bank | break-day P&L (7 flagged days) | club-day P&L (47 days) |
|---|---|---|---|
| actual | 196.2% (true 193.4) | **−110.4%** | +203.2% |
| S1 only | 185.6% | — | — |
| S1+S4 | 202.0% | — | — |
| **bundle S1+S4+S2 (empirical intl-share break flag)** | **291.2%** | **+13.1%** | +174.8% |
| bundle + cap 25% | 329.9% | +22.7% | +203.8% |

- Break days (empirically flagged: ≥50% national-team legs at freeze): 09-24, 09-29,
  10-01, 10-04, 10-06, 11-12, 11-13. Actual lost −110.4% across them; the bundle went +13.1%
  (it still fires clean break cards: 09-29 2/2 fired).
- November nuance: 11-09's basement-club card is NOT intl-flagged — **S1 alone catches it**
  (4/4 suspect legs). S1+S4 lets 11-14's losing acca through (+its winner skipped) — the
  flags are complementary, not redundant.
- **S1-only notably ends below actual** on the 60d path: early skipped winners shrink the
  bank that compounds later. The value is in the *combination*: S1 removes the toxic cell,
  S4 the tail, S2 the regime days.
- Recut reconciliation: 10-15's printed @5.36 acca was later settled as a @1.78 acca
  (post-freeze recut) — handled via ledger-first join.

## 10. League attribution (60d) — how leagues drive performance

All 196 legs resolved to leagues (100%, via the lane's own CLV snapshots). Group taxonomy:
UEFA club comps / INTL (national teams) / TOP5 / EU-MAJOR2 / NORDIC / EAST-BALK / SOUTH-AM /
ASIA-AFR / ENG-LOWER / OTHER-MIN.

### leg ROI by league group

| group | n | hit | ROI | avgOdd | avgConf |
|---|---|---|---|---|---|
| UEFA-CLUB (UCL/UEL/UECL) | 25 | 80.0% | **+28.1%** | 1.56 | 67% |
| EU-MAJOR2 | 13 | 84.6% | +17.3% | 1.37 | 72% |
| NORDIC | 11 | 72.7% | +11.2% | 1.64 | 67% |
| OTHER-MIN | 72 | 79.2% | +10.1% | 1.43 | 67% |
| SOUTH-AM | 6 | 66.7% | +3.7% | 1.53 | 67% |
| EAST-BALK | 9 | 66.7% | +1.9% | 1.49 | 67% |
| INTL | 25 | 68.0% | −1.1% | 1.51 | 64% |
| TOP5 | 16 | 68.8% | −5.3% | 1.39 | 72% |
| ASIA-AFR | 6 | 66.7% | −8.0% | 1.48 | 69% |
| ENG-LOWER | 5 | 60.0% | −14.8% | 1.41 | 69% |

### acca containment by group (the decisive table)

| acca composition | n | W/L | net | ROI |
|---|---|---|---|---|
| **pure major** (UEFA/TOP5/EU-MAJOR2/NORDIC/EAST-BALK) | 22 | 15W/7L | **+382.3%** | **+60.4%** |
| contains minor/unclassified | 44 | 28W/16L | +35.9% | +2.9% |
| **contains INTL/ENG-lower/Asia-Afr leg** | 26 | 12W/14L | **−88.5%** | **−15.9%** |

- All-UEFA accas: n=9, 6W/3L, **+52.5% ROI (+169% net)**. But "any one UEFA leg" mixed accas: **−21.5%** — one golden leg does not redeem a toxic partner. Purity, not presence.
- **Month-robustness (the subtle finding):** minor/unclassified accas were GOOD in Sep (+53%, n=14) and Oct (+18%, n=21) and collapsed only in Nov (**−37%**) — minor leagues are fine when they are *covered* mid-tiers, toxic when they're break-week basement cards. NEG-group accas were ≤0 in **every** month (−3%/−1%/−40%) — the one consistently harmless-to-hostile set. Pure-major: +50% Oct, +78% Nov (n=2 in Sep).
- Every catastrophic break slip mixes exactly these groups (league labels from the CLV record):
  11-09 #1 Serie C + Eliteserien playoff; #2 **FA Cup (7th tier) + Danish First Division**;
  11-12 #1 **El Salvador + Nations League U21s of pricing**; #2 two Nations League legs @49% conf.
- TOP5's −5.3% (n=16) is small-n variance on deep-favourite pricing (avgOdd 1.39) — flagged, not a claim.

**Caveat:** the group→ROI estimates use the same 60d window they'd gate on. Safe operational use:
anchor the taxonomy on *neutral* features (league's price-corroboration coverage + documented tier),
then let S6 accumulate per-group in-acca ROI going forward. The honest actionable form today:
veto INTL/ENG-lower/Asia-Afr legs from accas (≤0 in all three months, −88.5% net) and, during
flagged break days, extend to minor+unknown.

## 11. Team-level attribution (60d) — "toxic teams" answered in the negative

All 196 legs attributed to picked teams; 141 of 162 picked teams appear exactly once,
repeat max n=3 (Inter, Barcelona, Germany, Portugal, Benfica). Worst repeat offenders:

| team | n | hit | ROI | draw-kills |
|---|---|---|---|---|
| Slavia Praha | 2 | 50% | −36% | 1 |
| PAOK | 2 | 50% | −35% | 0 |
| Molde | 2 | 50% | −34% | 0 |
| Slovakia | 2 | 50% | −30% | 1 |
| Bursaspor | 2 | 50% | −29% | 1 |

**No team survives an n≥2 & cumulative-loss bar.** Team identity is not the carrier.
The draw-death catalogue is: **26/46 losing legs (~57%) drew**, spread across 27 different
teams — Bayern (2-2), Dortmund (2-2 twice incl. Bayern match), Sparta, Vasco, Gibraltar (0-0),
Russia 3-3 (!). Accas containing a leg that later drew: 4W/23L, −62.9% ROI — tautological
(a drawn backed leg is a lost leg), but it isolates the leak class: **draws**, not teams.

Draw risk is priced by the market per-fixture (derbies, cup rotation, break friendlies like
Russia 3-3 carry rotation risk), not by team DNA at this sample size. This is the argument
for **priced draw insurance (DC/DNB capture — landed §3-ref)** and against a static team
blocklist. Harness support for team probes exists (`teams=` include/`!exclude` filter)
so any future "gate team X" idea can be tested against data before pinning.

## 12. Venue (home/away) attribution (60d) — the strongest clean signal in the whole panel

### leg level
| backed | n | hit | implied | gap vs market | ROI | draw-kills |
|---|---|---|---|---|---|---|
| at home | 129 | 77.5% | 70.4% | **+7.2pp** | **+12.2%** | 18/29 losses |
| away | 59 | 69.5% | 68.3% | +1.2pp | +0.2% | 9/18 losses |

### calibration by favourite depth (market-implied vs actual)
| venue × depth | n | hit | implied | gap | ROI |
|---|---|---|---|---|---|
| HOME <1.40 | 65 | 81.5% | 77.0% | +4.5pp | +5.6% |
| **HOME 1.40–1.60** | 42 | 73.8% | 68.0% | +5.8pp | +9.4% |
| **HOME ≥1.60** | 22 | 72.7% | 55.2% | **+17.5pp** | **+75.8%** |
| AWAY <1.40 | 29 | 86.2% | 76.1% | +10.1pp | +13.6% |
| **AWAY 1.40–1.60** | 15 | 60.0% | 67.7% | **−7.7pp** | **−15.0%** |
| **AWAY ≥1.60** | 15 | 46.7% | 54.0% | **−7.3pp** | **−21.8%** |

Pattern: **home sides are under-priced at every depth (worse for longer prices)** — the market
slate under-rates home; away faves are only safe when deep (<1.40). Medium/long away prices
systematically underperform their own implied probability.

### venue × conf (user cell becomes venue-asymmetric)
- HOME conf<60: n=11, +41.6% ROI (home discount compensates low stated conf)
- **AWAY conf<60: n=9, −24.8% ROI — the toxic cell**; AWAY conf 60–69 −11.5%; AWAY conf≥70 +20.9%

### acca containment
- accas with an away leg odd≥1.40 & conf<70: n=20, 7W/13L, **−26.2% ROI, −153.3% net**
- without: n=72, 48W/24L, **+26.0% ROI, +483.0% net**

### team×venue (repeat teams)
Every repeat-team loser row is a HOME-backed failure (Molde/PAOK/Villarreal/Dortmund home);
the dual-side repeats show the split clearly (Slovakia: home −100%, away +40%; Slavia Praha:
home −100%, away +28%; Barcelona: home −100%, away +27%; Inter likewise). n=1–3 per cell —
flavour, not gate material by itself.

**Caveat:** away-cell n=15 per depth band — small; but the sign flip is coherent across
bands, conf strata and containment levels (three independent cuts), and the home-side
under-pricing has a known market-microstructure rationale (retail books shade away prices).
Probe before pinning: harness `teams=` exists now; venue probes need a `side=` filter —
added alongside in the same PR if this cut survives codespace replay.

## 13. Three-way calibration (60d): actual hit vs market-implied vs model-stated

| venue×depth | n | hit | mkt | model | hit−mkt | hit−mdl | ROI |
|---|---|---|---|---|---|---|---|
| H <1.40 | 65 | 81.5% | 77.0% | 72.3% | +4.5pp | +9.2pp | +5.6% |
| H 1.40–1.60 | 42 | 73.8% | 68.0% | 66.1% | +5.8pp | +7.7pp | +7.7% |
| H ≥1.60 | 22 | 72.7% | 55.2% | 60.5% | **+17.5pp** | +12.3pp | **+40.0%** |
| A <1.40 | 29 | 86.2% | 76.1% | 71.5% | +10.1pp | +14.7pp | +13.6% |
| A 1.40–1.60 | 15 | 60.0% | 67.7% | 64.5% | −7.7pp | −4.5pp | **−11.3%** |
| A ≥1.60 | 15 | 46.7% | 54.0% | 58.2% | −7.3pp | **−11.5pp** | **−14.2%** |

- **The model is systematically under-confident on this slate**: conf<60 legs actually hit
  65% (+13pp over stated); conf≥70 legs hit 84% (+10pp). Printed legs are price-selected
  favourites — the market knows more than the shrunk model on them.
- **Away mid/long prices: the model is WORSE than the market, in the staking direction.**
  A ≥1.60: model 58%, market-implied 54%, reality 47%. Trusting model confidence there is
  strictly worse than trusting price.
- **Model-vs-market disagreement is the real edge signature** (small n, sign-coherent):
  model−market ≥+5pp → n=24, +32% ROI (home +41.9%); model−market ≤−5pp → +0.9% overall,
  split: home +8.6% (market right) / away −11.4% (both wrong, −EV under either belief).
- **Venue×conf:** H conf<60 +41.6% (home discount swallows low stated conf); A conf<60 −24.8%,
  A conf 60–69 −11.5%, A conf≥70 +20.9%.

**Consolidated gate rule consistent with every independent cut in this document:**
an away leg must be DEEP (odd<1.40) OR CONFIDENT (≥70 stated). Away legs failing both are
−11%…−25% ROI whether cut by conf band, depth band, disagreement band, or acca
containment (−26.2% ROI inside accas vs +26.0% without). This subsumes and sharpens S1's
blunt odd>1.5&conf<60 cell — which only fires because it accidentally correlates with
away mid/long prices.

*Repro note: throwaway harness in /tmp (not committed); all inputs are committed
localdata snapshots, so any future run reproduces these numbers until the next 30d window shifts.*

## 14. Codespace paired A/B verdicts (main @ de922226, live-faithful pool, 25 candidate-days / 21 bet-days, --since 2026-09-17)

ENGINE ACTUAL extended: bank 257.8% · 74 bet-days · 85W/64L · 1 open.
New rows: 11-13 @1.86L @1.69W → 246.1%; 11-14 @2.38W @2.45L → 257.8%. Still far below the 455% peak — slump regime intact within the window.

Replay baseline (window): log/day +0.0311, final 192%, 35 accas, hit 49%, maxDD 58%.

| probe | Δ log/day | P(B>A) | verdict |
|---|---|---|---|
| acca_veto=2.6:1.5:0.60 (S1+S4 combined) | +0.0043 | 45% | **NO SHIP** — luck-shaped; acts 100% as DAY-SKIP (cards differ 0/25 days: vetoes turn 7 bet-days into no-bet days); 2026-10-15 carries 316% of the diff; sign flips on 5 of 21 leave-one-day-outs. maxDD 58→25% is real but the growth is not separable from luck at this n. |
| side=HOME (home-only pool) | −0.0501 | 16% | **DEAD** — venue-as-pool-restriction HURTS (final 70%, hit 41%). The §12 leg-level home edge does NOT survive acca selection/pairing: restricting the pool changes which legs/pairs rank on top. Venue story remains descriptive, not admission-actionable as a blunt restriction. |
| acca_veto=0:1.4:0.70,side=AWAY (venue-aware away gate) | — | — | **INVALID RUN** — parser artifact, see below; rerun required. |
| battery: S1 veto / S1+min_prob rows showing 0 days 0 accas | — | — | **Same artifact**, not evidence of universal toxic-leg exposure. |

**Parser artifact found & fixed (harness commit on this branch):** `_combined_veto` parsed
`acca_veto=0:odd:prob` as combined-cap = 0.0, and every acca is priced ≥ 0.0 → veto-all.
Semantics now: cap ≤ 0 ⇒ cap disabled; odd_floor 0 ⇒ pure prob floor. Pinned by
`test_acca_veto_zero_cap_means_no_combined_cap_not_kill_everything`.

**Battery rows that DID read true:** S4 cap ≥2.6 alone −0.0394 (hurts — price cap alone kills
winners). Strongest in-window levers, all awaiting paired bootstrap judgement:
5 accas on saturated days +0.0320 (final 376%, maxDD 44%), floor 1.25 +0.0204,
legacy strict pool gate +0.0191, always-on prob ≥65 +0.0907 (8 days only, still the
4x-rejected tripwire — §13 shows stated-conf under-reads reality).

**Universe caveat:** main replays 25 candidate-days vs the stale codespace branch's 49 —
merged live-faithful pool + rebuilt settlement facts (94,980 keys, 93 dates, pending
candidates 26→1) are stricter. All n here is small; treat every number as exploratory and
prefer wider windows (--since 2026-08-27 now that archive tickets are tracked on main).

**Rerun list (post-fix):**
```
PYTHONPATH=src python3 scripts/replay_harness.py --since 2026-09-17 --ab live "acca_veto=0:1.4:0.70,side=AWAY"   # real away gate, no cap
PYTHONPATH=src python3 scripts/replay_harness.py --since 2026-09-17 --ab live "acca_veto=0:1.5:0.60"            # clean S1-solo (suspect leg at any price)
PYTHONPATH=src python3 scripts/replay_harness.py --since 2026-09-17 --battery-fixes                              # S1 rows now read true
PYTHONPATH=src python3 scripts/replay_harness.py --since 2026-08-27 --ab live "acca_veto=2.6:1.5:0.60"          # widen n on the only positive gate
```

## 15. Wide-window verdict on the day-skip gate (43 candidate-days, --since 2026-08-27) + blowup-day anatomy

Codespace ran the rerun list on the PRE-merge tree (git pull refused: no upstream) —
so zero-cap specs there re-show the kill-all artifact. One spec was unaffected:
`acca_veto=2.6:1.5:0.60` (cap 2.6 never hit the parse bug), giving the first
wide-window reading:

| window | A live | B veto | Δ log/day | P(B>A) |
|---|---|---|---|---|
| 25 candidate-days / 21 bet-days | +0.0311 (192%) | +0.0353 (164%) | +0.0043 | 45% |
| 43 candidate-days / 38 bet-days | +0.0222 (232%) | −0.0113 (74%) | **−0.0335** | **12%** |

`cards differ on 0/43 days` — the gate is 100% day-skip (vetoes convert bet-days to
no-bet days; selection untouched). The short-window gain was one-day luck, as the
leave-one-day-out concentrations warned. **S1+S4 dead at n=38.**

**Why day-targeting fails (the "days that brought us here" question):** worst-day is
0.75 = both 12.5% accas lose. Legs are disjoint across accas (barbell pairing consumes
distinct legs; fixture-dedup since 2026-09-22) — two-loss days are four independent
legs failing in the same SLATE REGIME (thin slates, away mid-prices), not one shared
leg. And the blowup days are inseparable from the building days ex ante: skipping
price-tagged days also skips the @2–@4 wins that drove 74→455%. The viable attack is
dilution, not avoidance: `saturated_accas` is a live spec key, so the volume lever
gets a paired bootstrap directly (`--ab live "saturated_accas=5"`). The only
risk-shaped lever that touches blowup days is stake/day (worst-day scales linearly);
the stake battery row shows growth flat 25→33% then decaying ≥50%.

## 16. Post-fix codespace reads (main @ c0d912e) — the first real signal

| probe | window | Δ log/day | P(B>A) | verdict |
|---|---|---|---|---|
| acca_veto=0:1.5:0.60 (clean S1: suspect leg at ANY price) | 25 cd / 21 bd | **+0.0580** (final 454% vs 192%, hit 49→62%, maxDD 58→25%) | **98%** | **CANDIDATE** — paired bootstrap one-sided, p10 +0.0129 p90 +0.0713; LODO +0.0287..+0.0523 = broad-based (no day >30%); cards differ 0/25 → still acts as drop (9 accas / 4 full days removed of 35/21), i.e. day-skip + partial-day skip of suspect accas. REQUIRES wide-window confirm (next run). |
| acca_veto=0:1.4:0.70,side=AWAY (venue-aware away gate) | 25 cd | +0.0665 | 30% | **DEAD by coverage**: 1 bet-day / 1 acca in the whole window — away legs passing (odd<1.40 OR conf≥70) almost never pair up. Venue chapter CLOSED: §12's away toxicity loads entirely through the odd&conf cell that S1 already targets; blunt home restriction hurt (§14), away-gated pool can't field a card. |
| saturated_accas=5 (volume dilution) | 43 cd / 38 bd | +0.0177 | 87% | NOT SHIP-GRADE YET — fires on only 2/43 days (pool rarely reaches 12 legs after faithful-pool pruning); 09-19 carries 67%; "2 coin flips". Probe softer trigger: volume_pool=8,saturated_accas=4. |
| battery cross-checks | 25 cd | — | — | S1 row now reads +0.0580 (matches A/B); S1+min_prob60 ≡ always-on prob≥60 (+0.0168) strictly dominated by S1; S4 cap solo −0.0394 dead; UEFA-only S9 2 days, noise. |

Pending confirmations before any engine admission change: (a) S1 on 43 cd window;
(b) note semantic: veto = drop suspect accas, day goes no-bet if all dropped —
live engine change would match (skip card), coverage cost 21→17 days.

## 17. Wide-window confirmations — program conclusion (43 candidate-days / 38 bet-days)

| lever | Δ log/day | P(B>A) | verdict |
|---|---|---|---|
| acca_veto=0:1.5:0.60 (S1 solo) | +0.0163 (318% vs 232%, hit 49→53%, maxDD 58→47%) | **67%** | LUCK-SHAPED — short-window P=98% was 2026-09-20-shaped (that day carries 92% of the wide-window diff; LODO low end +0.0007). Directionally positive on growth AND risk, uncertifiable at n=38. DO NOT SHIP. |
| volume_pool=8,saturated_accas=4 | −0.0009 | 43% | DEAD — softer trigger adds 14 accas, hit FALLS 49→45%; 2026-10-11 carries 571%; sign flips on 4 LODO. Volume dilution needs a saturated-pool prerequisite the data rarely offers (2/43 days at 12, 7/43 at 8), and when it fires it doesn't pay. |

**Program conclusion:** at the live-faithful replay ceiling (43 cd) NO admission, price-cap,
venue, team, or volume lever separates from luck. Shipped from the diagnostic: only the
DC-DNB settlement fix (a semantics bug, not a knob). Open items: (a) S1 consistency probe
on --unfaithful-pool superset; (b) S1 SHADOW telemetry in live engine (log would-be-vetoed
accas, settle separately) for out-of-sample evidence — the only evidence class that can
certify a drop-rule, since replay is quote-history-capped. No admission change on
retrospective luck-shaped deltas.

## 18. S1 closed — three-sample ledger + final program statement

S1 (`acca_veto=0:1.5:0.60`) across all three universes, largest last:

| universe | cd / bd | Δ log/day | P(B>A) | carrier |
|---|---|---|---|---|
| faithful, 09-17→ | 25 / 21 | +0.0580 | 98% | 09-20 30% |
| faithful, 08-27→ | 43 / 38 | +0.0163 | 67% | 09-20 92% |
| superset (--unfaithful-pool), 08-27→ | 50 / 50 | **−0.0060** (median −0.0056, p90 +0.0015) | **16%** | 09-28 58% |

Verdict: the 98% was 09-20 luck; both larger samples deflate it, and the superset
is outright negative at the median. **S1 drop-rule is dead. Do not install it live or
in engine code.** (Superset caveats noted: unbettable quotes dilute the A arm to
+0.0035/day; relative diff remains the doctrine metric.)

**Final program statement (2026-11-15 slump diagnostic, complete):**
- SHIPPED: DC-DNB settlement fix (semantics bug); harness instrumentation
  (--battery-fixes, acca_veto with corrected cap<=0 semantics, teams=, side=).
- NULL RESULTS (tested, luck-shaped or coverage-dead at all attainable n): suspect-leg
  veto S1/S1+S4/S2, price cap S4, team filters, venue restriction/gate, volume dilution
  (12 & 8 saturation), prob floors remain 4x-rejected tripwire.
- MECHANISM: slump = variance concentrating in the odd>1.5 × conf<60 cell within the
  same slate regime as the winning days; no ex-ante separator exists in 50 days of data.
- STANDING RULE: no admission change without out-of-sample evidence (shadow ledger
  remains optional but deprioritised — prior for S1 success now low across three
  samples). Engine admission/selection unchanged going forward from main c0d912e.

## 19. Regime boundary: post-Forebet (user correction 2026-11-15)

The replay windows so far pooled TWO model regimes. Registry facts
(localdata/edges_consensus.json): current `post_forebet_v1` contracts mined from
**2026-06-13 → 2026-11-15**, split 2026-10-18; committed probability CSVs end
2026-06-12; production recovery ran 2026-10-20 (run 39350936425). Therefore:

- post-Forebet DATA era starts **2026-06-13** (live-capture era);
- post-Forebet PRODUCTION era (current ensemble driving tickets) starts **2026-10-21**.
- ALL prior A/B windows (08-27, 09-17) pool pre-recovery captures with post-recovery
  ones. Both carrier days sit pre-recovery: 09-20 (92% of S1-wide) and 10-15
  (41–316% of the other probes). §16–§18 verdicts are regime-pooled; re-judge on
  --since 2026-10-21 (in-regime, carriers out by construction) and the full-era
  ladder --since 2026-06-13 (maximal n, quote-coverage permitting).

## 20. The replay is blind over the post-Forebet production era — and the era ladder needed a flag

Codespace reads, main @ c0d912e:

- **--since 2026-10-21 → 0 candidate-days.** The replay universe is built from
  pick-pool captures (`picks_morning_*.json` / archived `picks_*.json`); committed
  archives end mid-October (last ~2026-10-16; `localdata/archive/picks/2026/` holds
  months 06–10 only). Post-recovery days keep `picks_*.txt` only, which the pool
  reader deliberately ignores. **The slump regime (11-09→11-14) has ENGINE ACTUAL
  coverage only — no counterfactual replay is possible for it from current data.**
  All A/B verdicts in §14–§18 are pre-recovery-regime statements (strengthens the
  nulls: no lever survived even the regime that built 455%).
- **--since 2026-06-13 → 64 candidate-days** (June–Aug pools DO exist), but growth
  nan'd: ~10 selected cards pending settlement in thin early-era coverage poisoned
  the whole comparison ("A/B SKIPPED").
- Harness fix (this branch): `--drop-pending-days` — opt-in; excludes pending-SELECTED
  days from both arms' realized growth (the bootstrap already excluded them
  pair-wise; default strict refusal unchanged; excluded days printed). Pinned by test.
- Rerun list:
  ```
  PYTHONPATH=src python3 scripts/replay_harness.py --since 2026-06-13 --drop-pending-days --ab live "acca_veto=0:1.5:0.60"
  PYTHONPATH=src python3 scripts/replay_harness.py --since 2026-06-13 --drop-pending-days --battery-fixes
  ```
- Structural gap for the forward regime: resume committing replayable pick-pool JSON
  (morning capture) for post-10-21 days, or the only post-Forebet evidence will ever
  be the descriptive ledger. If any gate is ever proposed again, shadow telemetry +
  forward collection is the evidence path; retro replay cannot reach this regime.

## 21. Full-era ladder reads (64 candidate-days / 43 graded bet-days, pending-excluded) — retrospective ceiling

Main @ caf5794, --since 2026-06-13 --drop-pending-days. Baseline: +0.0342 log/day,
final 435%, 69 accas, hit 52%, maxDD 58%. (This echo of the pre-slump build is the
435% the real ledger spent; the regime was genuinely strong pre-recovery.)

**S1 — final ledger, monotonic deflation with n:**
| universe | bd | Δ | P(B>A) |
|---|---|---|---|
| faithful 09-17 | 21 | +0.0580 | 98% |
| faithful 08-27 | 38 | +0.0163 | 67% |
| faithful 06-13 era | 43 | **−0.0017** | **31%** (08-20 carries 89%) |
| superset 08-27 | 50 | −0.0060 | 16% |
**S1 CLOSED.** The 98% was small-n + carrier-day luck; every larger sample deflates it.

**Battery at max n (un-bootstrapped rows, Δ vs baseline):**
- floor 1.25: **+0.0150** → 829% final, hit 58%, maxDD 58→33%, SAME 43 days. Positive at
  n=21 (+0.0204) AND n=43 — the only lever with the same sign in every window tried.
- saturated_accas=5 (pool≥12): **+0.0157** → 852%, hit 49→55%, maxDD→44%.
- legacy strict pool gate: +0.0093 → 649%, maxDD→44%.
- DEAD at max n: rank-by-EV −0.0465 (prob-ranking superiority is now a max-n fact),
  S4 cap −0.0379, S1+S4 −0.0457, flat max-accas 4/5/6 all negative (volume without
  saturation-conditioning hurts), stake 75% −0.0436.
- always-on prob≥65 +0.0365 but 18/43 days (4x-rejected tripwire stands).

**Next:** paired bootstraps on the two survivors and their combo:
```
--since 2026-06-13 --drop-pending-days --ab live "floor=1.25"
--since 2026-06-13 --drop-pending-days --ab live "saturated_accas=5"
--since 2026-06-13 --drop-pending-days --ab live "floor=1.25,saturated_accas=5"
```
Caveat repeated: these certify only the PRE-recovery regime; the live regime (slump)
is replay-blind, so even a positive P here ships, if ever, only after forward evidence.

## 22. The certification trio (era window, 64 cd / 43 graded bd, pending-excluded)

| arm | Δ log/day | P(B>A) | concentration | verdict |
|---|---|---|---|---|
| floor=1.25 | +0.0150 (829%, hit 58%, maxDD 33%) | 90% | 09-20 70%, p10 −0.0002 | positive but carrier-heavy alone |
| saturated_accas=5 | +0.0157 (852%, hit 55%, maxDD 44%) | 87% | 09-19 67%, **3 differ-days** ("3 coin flips") | positive but ultra-thin trigger |
| **floor=1.25 + saturated_accas=5** | **+0.0307 → final 1625%, hit 59%, maxDD 58→25%** | **98%**, p10 **+0.0098** | 09-20 33%; LODO **+0.0205..+0.0351 = broad-based**; 18/64 differ | **SHIP-GRADE retrospectively** |

Notable: Δ_combo = Δ_floor + Δ_sat EXACTLY (+0.0150 + 0.0157 = +0.0307) — the two
channels are independent and interfere zero: (i) 1.25–1.30 legs are win-positive in
this model (§13: stated conf under-reads reality at the low-price end); (ii) deeper
pools → deeper cards on saturated days. maxDD halves AND growth doubles.

**STANDING CAVEAT (doctrine-complete):** certified on the PRE-recovery regime only;
the live post-Forebet regime is replay-blind (§20). Any ship decision must pair the
engine change with (a) resumed pick-pool JSON capture so forward evidence can
accumulate, and (b) an explicit revert tripwire (re-judge after ~15 live bet-days).

## 23. SHIP — combo armed 2026-11-15 (operator decision)

**Decision:** certified combo from §22 armed as the live recipe.
**Change:** `scripts/auto_tickets.py` — `MIN_LEG_ODDS 1.30 → 1.25` and new
`SATURATED_ACCAS = 5` (resolved in `select_accas` defaults so bare `plan_day`
calls — live tickets and the parity snapshot — see the armed constants).
**Lane scope guard discovered in test repair:** the certification ran the main
acca lane; the enhancement lane keeps `ENH_MAX_ACCAS = 3` on every day.
`select_accas(..., enhancements=True)` excludes saturation (resolution is
lane-aware) — ship does NOT silently widen the enh lane to 5.
**Receipt:** combo +0.0307 log/day, P(B>A)=98%, p10 +0.0098, LODO
+0.0205..+0.0351, exactly additive channels (§22). Conditions: pre-recovery
regime only; tripwire below governs the live regime.

**Test surface of the ship (full suite 7120 passed / 2 skipped):** pins moved
with receipts attached: recipe lock & parity baseline regenerated
(`tests/data/engine_parity_baseline.json`: 30/80 archive days moved BY DESIGN —
floor widens cards; max stake delta 12.5pp; base_commit e419930) — the file now
pins the post-ship production recipe, generated_note carries the chain.
Boundary probes probed 1.29 now probe 1.24 (sub-floor semantics preserved in 5
files); the acca-gate probe universe was rebuilt so the sub-threshold block
pairs with itself through the barbell joint on a saturated x5 card (monotone
descend spreads weakness across every acca → completeness fallback → gate
becomes invisible to the probe: a NO-OP class the pin explicitly names);
routing pin (cap arithmetic) now shows saturation production math
(per-acca 0.07×5 requested → clamps to STAKE_FRAC 25% ⇒ 5.0% per acca).
Parity synthetic corpus review: no fixture in the [1.25,1.30) band;
06-22 has 6 legs < VOLUME_POOL=12 (never saturated): committed corpus unchanged.

**Tripwire (revert rule):** re-judge after ~15 live bet-days forward from
11-15. Revert (MIN_LEG_ODDS back to 1.30 AND SATURATED_ACCAS back to None) if
live forward bank growth over the first ~15 graded bet-days is materially below
the baseline trajectory of the pre-ship live path (peak 455.1% 11-08 → 257.8%
11-14: slide persistent). Re-judge means: paired-day live comparison of the
armed recipe trajectory vs the baseline observed slide window (no replay —
the slump regime is replay-blind §20): ENGINE ACTUAL bank trajectory over the
15-day window decides, with §22 numbers as regime-certification only.
Saved bookmarks: revert values MIN_LEG_ODDS = 1.30; SATURATED_ACCAS = None.

**Capture resume (standing scope note, not shipped here):** the slump regime is
replay-invisible simply because `localdata/archive/picks/2026/**/*.json` commits
ended ~10-16. The writers still run live (`scripts/picks_today.py` ~7588 writes
the day archive `picks_<day>.json` via `dated_artifact_path`; `scripts/daily.py`
writes morning/candidate ledgers). The break is in PERSISTENCE: post-recovery
production commits route through `scripts/phase5_persistence.py` (whitelist at
~:31-43 spans phase5 shadows/receipts and autobets ledgers — the plain pick-pool
JSONs are outside it; the artifact upload at `.github/workflows/daily.yml` is
`localdata/*.json` root-only, not the dated archive). Resuming the pool commits
(isolated, evidence-only, no money-path effect) is a follow-on; the tripwire
window can be judged from ENGINE ACTUAL alone if capture follows afterward.

---

## 24. autobets_ML lane unblock (resolution landed 2026-11-16)

Production CI run 43801399651 (2026-11-16, main c4088c0) showed the paper lane
still blocked: `autobets_ML evidence conflict; paper lane blocked, live lanes
unchanged` at persistence restore, both PAPER capture steps, and the ENH grade
(`autobets_ML report unavailable`). The 2026-11-15 local resolution of the same
chain never reached the remote (workspace loss before commit); this section
records the re-applied resolution now shipped.

**Link 1 — integrity block of 2026-11-13/14, cleared.** All five conflicted
receipts are byte-identical between cache and committed copies (sha256 of each
`.cached.` side equals the `.committed.` side), so no evidence ever diverged;
the block came from row-level sha ties during those restores under the schema
then current. Resolution marker
`localdata/autobets_ML_conflicts/integrity_block.resolved_2026-11-16.510997949f38d746af358cbea8d61d396b68b620801a2e337bc911f190fb8f5d.json`
documents the review; `localdata/autobets_ML_integrity_block.json` is removed.
The cache can resurrect a deleted block, so persistence restore retires only
its exact reviewed bytes when HEAD contains the matching approval, no active
block remains committed, and the current restore found no new receipt conflicts.
The original bytes are archived before removal. Cache-only approvals, changed
blocks and new conflicts never clear PAPER. Receipt validation post-clear:
all 118 receipts pass (137 s in the initial in-process check).

**Link 2 — operator supersession deed, honored in code.** Receipt 1a902a22
(2026-11-13T09:13:03Z) carries `supersession.policy =
operator_pre_kickoff_paper_replacement_v1` targeting acca 1 of fdbe9fde
(2026-11-12T22:36:42Z, a still-open double-draw; both legs kicked off 19:45 UTC,
~10.5 h after the replacement froze). Without the deed in the committed-ledger
fixture accounting, the replacement's declared `prior_open_stake_micro_units: 0`
failed validation; without it in performance accounting, the replaced acca
booked P&L it never risked. `SUPERSESSION_POLICY` + `_superseded_accas`
(src/edgefactory/ml_paper.py) now validate deeds fail-closed (unknown policy,
self/unknown/out-of-range targets, non-earlier receipts, kicked-off legs all
raise), receipts() releases superseded stakes at the replacement decision,
not retroactively across intervening receipts. The pre-kickoff check uses the
replacement's actual freeze, not its earlier capture. Performance voids
superseded accas — neither settled nor pending — surfacing
`superseded_tickets` and both receipt hashes in the release audit, not the HELD
list. Cancelled forecasts remain candidate-pool evidence but are no longer
selected-ticket observations unless actively re-selected. Ledger after the
fix: 53 settled (7W/46L),
3 pending, 1 superseded, profit −43.6093 u, paper bank 56.3907 u.

**Link 3 — orphaned history legs healed, evidence-only.** Three settled-acca
legs permanently stuck at `result=None` (settlement only reads open slips):
ENH 2026-10-19 Mes Shahr-e Babak vs Persepolis FC over-1.5 → **win** (0-3; the
store spells the club "Mes Shahr Babak" — a curated identity pair was added in
BOTH `TEAM_KEY_RAW_ALIASES` and `Config/entity_overrides.json`, either table
alone being insufficient); ENH 2026-11-05 AC Milan vs Ferencvarosi TC over-2.5
→ **loss** (0-2); Main 2026-11-08 Deportivo Garcilaso vs Comerciantes Unidos
HOME → **loss** (0-0 draw; per-day archive row never landed).
`heal_history_leg_results` (scripts/auto_tickets.py, wired into
settle_open_slips before save_state) fills only None results on confirmed
settled accas: same-day 1X2 outcomes must agree, market legs require one exact
score, and every available outcome/score must be consistent. Frozen identities,
squad markers and narrow-key neighbour guards still apply; adjacent dates are
not borrowed. It never rebooks won/stakes/banks and is idempotent.
Restore carries HEAD's confirmed None-to-result audit fills into a stale
cache only for identical frozen leg metadata on settled accas, then applies
all existing bank, placement, history and freeze checks. It never trusts a
cache-only fill or overwrites a known conflicting result. This prevents an
unchanged-money cache from rejecting the committed audit heal. The historical
October recovery snapshot remains untouched; its preservation test explicitly
pins the one Mes Shahr None-to-win difference and every other original field.
The fourth orphan — Main 2026-10-21 Sporting JAX vs Louisville City AWAY —
has no settled-facts evidence on or near its date and correctly stays None.

Out of scope, deliberately: no booked bank/stake rewriting anywhere; the
supersession deed surfaces and voids — frozen ML receipts remain byte-identical; ENH
ticket-decision receipt shard gaps and the >50 MiB conflict-cache files
flagged in the same CI run are adjacent infra follow-ons, untouched here.
Proof: tests/test_ml_paper_supersession.py (24),
tests/test_ml_paper_integrity_resolution.py (7, including restore + publish),
tests/test_auto_tickets_rolling.py (12 heal cases, 50 total), and 18 paired-lane
financial cache backfill/guard cases in tests/test_phase5_persistence_audit.py —
plus the in-process receipts()/performance() check over the restored store above.
Full regression: **7,189 passed, 2 skipped** (`PYTHONPATH=src:scripts:tests
.venv/bin/python -m pytest tests/ -q`); all 118 frozen ML receipts remain
byte-identical after report regeneration.
