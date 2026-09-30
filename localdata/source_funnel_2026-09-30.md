# Same-day source funnel — 2026-09-30

as_of `2026-09-30T18:34:21+02:00`, min_lead 30m. Read-only, no network; gates reused from scripts/picks_today.py.

## A. Per-source same-day availability

| source | raw | fixtures | kickoff | ko_ok | prematch | 1x2 | ou | btts | in_1x2 | used | wh |
|---|---|---|---|---|---|---|---|---|---|---|---|
| forebet | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | True | True | True |
| zulubet | 58 | 45 | 31 | 0 | 0 | 45 | 0 | 0 | True | True | True |
| statarea | 22 | 18 | 18 | 18 | 0 | 18 | 18 | 0 | True | True | True |
| vitibet | 199 | 172 | 151 | 151 | 85 | 18 | 0 | 0 | True | True | True |
| betclan | 64 | 60 | 0 | 0 | 0 | 60 | 0 | 0 | True | True | True |
| scoutingstats | 28 | 20 | 20 | 20 | 12 | 17 | 17 | 16 | False | True | True |
| bzzoiro | 18 | 17 | 17 | 17 | 6 | 17 | 17 | 17 | True | True | True |
| predictz | 19 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | True |
| windrawwin | 32 | 31 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | True |
| freesupertips | 2 | 2 | 2 | 2 | 2 | 0 | 0 | 0 | False | False | True |
| afootballreport | 332 | 243 | 243 | 243 | 86 | 0 | 0 | 0 | False | False | True |
| prosoccer | 16 | 15 | 15 | 15 | 2 | 15 | 0 | 0 | False | False | True |
| soccervista | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | False |
| bettingclosed | 73 | 45 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | True |

Notes:
- **forebet**: no same-day rows captured
- **zulubet**: no trusted kickoff -> same-day guard drops anything anchored here; 1 rows dropped by <4-char identity key
- **statarea**: 1 rows dropped by <4-char identity key
- **vitibet**: 4 rows dropped by <4-char identity key
- **betclan**: no trusted kickoff -> same-day guard drops anything anchored here; 2 rows dropped by <4-char identity key
- **scoutingstats**: consumed for OU/BTTS only, not in SOURCES_1X2
- **bzzoiro**: 1 rows dropped by <4-char identity key
- **predictz**: NOT consumed by picks engine (captured but cannot vote); no trusted kickoff -> same-day guard drops anything anchored here; no 1X2 probability signal; 2 rows dropped by <4-char identity key
- **windrawwin**: NOT consumed by picks engine (captured but cannot vote); no trusted kickoff -> same-day guard drops anything anchored here; no 1X2 probability signal; 1 rows dropped by <4-char identity key
- **freesupertips**: NOT consumed by picks engine (captured but cannot vote); no 1X2 probability signal
- **afootballreport**: NOT consumed by picks engine (captured but cannot vote); no 1X2 probability signal; 2 rows dropped by <4-char identity key
- **prosoccer**: NOT consumed by picks engine (captured but cannot vote); 1 rows dropped by <4-char identity key
- **soccervista**: no same-day rows captured
- **bettingclosed**: NOT consumed by picks engine (captured but cannot vote); no trusted kickoff -> same-day guard drops anything anchored here; no 1X2 probability signal

## B. Cross-source identity overlap

- fixture groups: 528
- single-source groups: 442
- two-source groups: 47
- three-plus-source groups: 39
- reversed home/away risk groups: 0

Examples — singletons:
  - fixture=1demarzo vs sportivoiteno, source=afootballreport
  - fixture=abumuslim vs omarzawak, source=afootballreport
  - fixture=adelphipanthers vs franklinpierceravens, source=afootballreport
  - fixture=aguila vs interformandounatletau20, source=afootballreport
  - fixture=albertusmagnusfalcons vs deanbulldogs, source=afootballreport
  - fixture=albertusmagnusfalcons vs mitchellmariners, source=afootballreport
  - fixture=alettihad vs alistiqlal, source=afootballreport
  - fixture=alianza vs atleticoplatense, source=vitibet
  - fixture=alianza vs cdplatense, source=afootballreport
  - fixture=alula vs alhilal, source=afootballreport
Examples — multi_source:
  - fixture=afcfylde vs carlisle, sources=betclan,windrawwin
  - fixture=aguila vs inter, sources=bettingclosed,vitibet
  - fixture=aktobew vs ajaxw, sources=vitibet,zulubet
  - fixture=australia vs brazil, sources=betclan,windrawwin
  - fixture=bahrain vs yemen, sources=betclan,bettingclosed,prosoccer,vitibet,zulubet
  - fixture=barrow vs scunthorpe, sources=betclan,windrawwin
  - fixture=belize vs saintvincentthegrenadine, sources=bzzoiro,predictz
  - fixture=birminghamcityw vs liverpoolw, sources=vitibet,zulubet
  - fixture=botafogosp vs pontepreta, sources=afootballreport,betclan,windrawwin
  - fixture=brannw vs hjkw, sources=vitibet,zulubet

## C. Consensus funnel

- match surface (union of forebet,zulubet,statarea,vitibet,betclan,bzzoiro): **238**
- fixtures with >=2 voters carrying 1X2 probs: **23**
- fixtures ML-meta can score (needs one of forebet,zulubet,statarea): **18**
- of those, pre-match eligible: **4**

Drops:
  - fewer_than_2_voters_with_1x2: 215
  - no_ml_anchor_source_present: 5
Examples — fewer_than_2_voters_with_1x2:
  - fixture=Afc Fylde vs Carlisle, sources_with_1x2=betclan
  - fixture=Águila vs Inter, sources_with_1x2=vitibet
  - fixture=Aktobe W vs Ajax W, sources_with_1x2=zulubet
  - fixture=Alianza vs Club Atletico Platense, sources_with_1x2=vitibet
  - fixture=Älvsjö AIK W vs Djurgården W, sources_with_1x2=-
  - fixture=America PE U20 vs Serrano PE U20, sources_with_1x2=-
  - fixture=Angola U23 vs Namibia U23, sources_with_1x2=-
  - fixture=Anguilla vs Aruba, sources_with_1x2=-
  - fixture=FC Argeș Pitești vs Cetate Deva, sources_with_1x2=-
  - fixture=Arna-Bjørnar W vs Frigg Oslo FK W, sources_with_1x2=-
Examples — no_ml_anchor_source_present:
  - fixture=Independiente Medellin vs Millonarios, sources_with_1x2=betclan,bzzoiro
  - fixture=Katsina United FC vs Rivers United FC, sources_with_1x2=vitibet,bzzoiro
  - fixture=Mexico vs Peru, sources_with_1x2=betclan,bzzoiro
  - fixture=Seychelles vs Sri Lanka, sources_with_1x2=betclan,bzzoiro
  - fixture=Union San Felipe vs San Luis, sources_with_1x2=vitibet,betclan

## D. Kickoff / timing funnel

| source | fixtures | has_kickoff | trusted | missing | untrusted | pre_match |
|---|---:|---:|---:|---:|---:|---:|
| zulubet | 45 | 31 | 0 | 14 | 31 | 0 |
| statarea | 18 | 18 | 18 | 0 | 0 | 0 |
| vitibet | 172 | 151 | 151 | 21 | 0 | 85 |
| betclan | 60 | 0 | 0 | 60 | 0 | 0 |
| scoutingstats | 20 | 20 | 20 | 0 | 0 | 12 |
| bzzoiro | 17 | 17 | 17 | 0 | 0 | 6 |
| predictz | 17 | 0 | 0 | 17 | 0 | 0 |
| windrawwin | 31 | 0 | 0 | 31 | 0 | 0 |
| freesupertips | 2 | 2 | 2 | 0 | 0 | 2 |
| afootballreport | 243 | 243 | 243 | 0 | 0 | 86 |
| prosoccer | 15 | 15 | 15 | 0 | 0 | 2 |
| bettingclosed | 45 | 0 | 0 | 45 | 0 | 0 |

Same-day guard drops on the ML-scoreable surface:
  - inside_30m_lead_or_started: 14
Examples — inside_30m_lead_or_started:
  - fixture=Brooklyn vs Detroit City FC, kickoff_raw=16:00, kickoff_donors=statarea,scoutingstats,bzzoiro, sources=statarea,bzzoiro
  - fixture=Cerro Largo vs Rentistas, kickoff_raw=12:00, kickoff_donors=statarea,vitibet, sources=zulubet,statarea,vitibet,betclan
  - fixture=Cerro Porteno vs Rubio Nu, kickoff_raw=15:30, kickoff_donors=statarea, sources=statarea,betclan
  - fixture=Defensor Sporting vs Plaza Colonia, kickoff_raw=12:00, kickoff_donors=statarea,vitibet, sources=statarea,vitibet,betclan
  - fixture=Enyimba vs Shooting Stars, kickoff_raw=08:00, kickoff_donors=statarea,bzzoiro, sources=zulubet,statarea,vitibet,betclan,bzzoiro
  - fixture=Eritrea vs South Africa, kickoff_raw=2026-09-30T16:00:00Z, kickoff_donors=scoutingstats, sources=zulubet,vitibet,betclan
  - fixture=Häcken W vs Juventus W, kickoff_raw=2026-09-30T18:45:00+02:00, kickoff_donors=vitibet,scoutingstats, sources=zulubet,vitibet
  - fixture=Lithuania vs Andorra, kickoff_raw=09:00, kickoff_donors=statarea,scoutingstats,bzzoiro,prosoccer, sources=zulubet,statarea,vitibet,betclan,bzzoiro
  - fixture=New York Red Bulls vs St. Louis City, kickoff_raw=16:30, kickoff_donors=statarea,bzzoiro, sources=statarea,bzzoiro
  - fixture=Paris FC W vs Arsenal W, kickoff_raw=2026-09-30T18:45:00+02:00, kickoff_donors=vitibet,scoutingstats, sources=zulubet,vitibet

## A2. Voter classification

| source | tier | role | raw | fixtures | 1x2 rows | blocker |
|---|---|---|---:|---:|---:|---|
| forebet | live | blocked | 0 | 0 | 0 | no same-day rows captured |
| zulubet | live | live_voter | 58 | 45 | 45 | - |
| statarea | live | live_voter | 22 | 18 | 18 | - |
| vitibet | live | live_voter | 199 | 172 | 18 | - |
| betclan | live | live_voter | 64 | 60 | 60 | - |
| scoutingstats | live | not_a_voter | 28 | 20 | 17 | adapter exposes no 1X2 probability fields |
| bzzoiro | live | live_voter | 18 | 17 | 17 | - |
| predictz | shadow | blocked | 19 | 17 | 0 | rows captured but no 1X2 probability fields parsed |
| windrawwin | shadow | blocked | 32 | 31 | 0 | rows captured but no 1X2 probability fields parsed |
| freesupertips | shadow | blocked | 2 | 2 | 0 | rows captured but no 1X2 probability fields parsed |
| afootballreport | shadow | blocked | 332 | 243 | 0 | rows captured but no 1X2 probability fields parsed |
| prosoccer | shadow | shadow_voter | 16 | 15 | 15 | source tier is shadow: not settlement-validated for dispatch |
| soccervista | shadow | blocked | 0 | 0 | 0 | no same-day rows captured |
| bettingclosed | donor | not_a_voter | 73 | 45 | 0 | settlement/result donor only |

## A3. Shadow candidates (NON-DISPATCH)

- shadow candidate fixtures: **5** (dispatchable: False)
- shadow voter sources today: predictz, windrawwin, freesupertips, afootballreport, prosoccer, soccervista

Shadow evaluation only. These rows are NEVER dispatched, never become CLEAN/CAUTION picks, and are not read by the pick engine. Promotion requires settlement-coverage evidence plus operator sign-off.

Blockers:
  - inside_30m_lead_or_started: 3
  - no_ml_feature_provider_on_fixture: 2
  - shadow_sources_not_settlement_validated: 5

## A1. Source health warnings

- SOURCE_HEALTH: 'scoutingstats' has 1X2 rows today but its tier ('live') excludes it from both live and shadow consensus

## E0. Shadow voter expansion (diagnostic, NON-DISPATCH)

- certified voter sources: forebet,zulubet,statarea,vitibet,betclan,bzzoiro
- shadow sources carrying 1X2 today: scoutingstats,prosoccer
- fixtures with >=2 certified voters: **23**
- fixtures with >=2 voters if shadow admitted: **29** (+6)

Diagnostic only. Admitting a shadow source is a certification decision requiring settlement-coverage evidence and operator sign-off; this audit never promotes anything.
Examples of fixtures that would gain a quorum:
  - cienciano vs loschankas (betclan,scoutingstats)
  - eastleigh vs southendunited (bzzoiro,scoutingstats)
  - kalsdorf vs grazerak (zulubet,scoutingstats)
  - montevideocitytorque vs penarol (statarea,scoutingstats)
  - slbenficaw vs bayernmunichw (vitibet,scoutingstats)
  - tamworth vs suttonunited (bzzoiro,scoutingstats)

## E. Odds / pricing funnel

| odds source | cached rows | fixtures | overlap with 1X2 surface | cov% |
|---|---:|---:|---:|---:|
| bzzoiro_odds | 89 | 1 | 1 | 0.42 |
| theoddsapi_odds | 0 | 0 | 0 | 0.0 |
| oddspapi_odds | 0 | 0 | 0 | 0.0 |
| betexplorer_odds | 0 | 0 | 0 | 0.0 |

Diagnosis: **price_fixtures_overlap_the_surface** (candidates before odds: 4)
- theoddsapi_odds: empty_no_rows_today
- oddspapi_odds: empty_no_rows_today
- betexplorer_odds: empty_no_rows_today

## F. Backfill depth / retryable gaps

| source | first | latest | dates | capture window | fwd-only | missing in D30 | retryable | deeper possible |
|---|---|---|---:|---|---|---:|---:|---|
| forebet | 2024-01-01 | 2026-09-29 | 957 | 2026-08-31..2026-10-01 | no | 1 | 0 | yes |
| zulubet | 2024-01-01 | 2026-09-30 | 958 | 2026-08-31..2026-09-30 | no | 0 | 0 | no |
| statarea | 2017-01-01 | 2026-09-30 | 3511 | 2026-08-31..2026-09-30 | no | 0 | 0 | no |
| vitibet | 2026-07-29 | 2026-10-01 | 65 | 2026-08-31..2026-10-01 | no | 0 | 0 | no |
| betclan | 2026-08-28 | 2026-09-30 | 34 | 2026-09-30..2026-09-30 | yes | 0 | 0 | no |
| scoutingstats | 2026-07-29 | 2026-09-30 | 64 | 2026-08-31..2026-09-30 | no | 0 | 0 | no |
| bzzoiro | 2026-08-27 | 2026-10-23 | 43 | 2026-09-30..2026-09-30 | yes | 0 | 0 | no |
| predictz | 2026-08-08 | 2026-09-30 | 35 | 2026-08-31..2026-09-30 | no | 1 | 2 | yes |
| windrawwin | 2026-08-29 | 2026-10-01 | 30 | 2026-09-30..2026-10-01 | yes | 4 | 1 | no |
| freesupertips | 2026-09-24 | 2026-09-30 | 3 | 2026-09-30..2026-10-01 | yes | 28 | 0 | no |
| afootballreport | 2026-08-28 | 2026-09-30 | 31 | 2026-09-30..2026-09-30 | yes | 3 | 0 | no |
| prosoccer | 2026-09-29 | 2026-10-01 | 3 | 2026-09-29..2026-10-01 | no | 29 | 0 | yes |
| soccervista | - | - | 0 | 2026-09-30..2026-09-30 | yes | 31 | 1 | no |
| bettingclosed | 2026-07-29 | 2026-09-30 | 64 | 2026-08-31..2026-09-30 | no | 0 | 0 | no |

Gap expectations:
  - forebet: historical — GAP WITHOUT RECORDED FAILURE — investigate the job/adapter
  - zulubet: d30 — complete for D30
  - statarea: d30 — complete for D30
  - vitibet: d30 — complete for D30
  - betclan: capture_forward_only — thin history EXPECTED (capture-forward only adapter)
  - scoutingstats: d30 — complete for D30
  - bzzoiro: capture_forward_only — thin history EXPECTED (capture-forward only adapter)
  - predictz: d30 — gap with retryable failures — retry, then re-audit
  - windrawwin: capture_forward_only — thin history EXPECTED (capture-forward only adapter)
  - freesupertips: capture_forward_only — thin history EXPECTED (capture-forward only adapter)
  - afootballreport: capture_forward_only — thin history EXPECTED (capture-forward only adapter)
  - prosoccer: d30 — GAP WITHOUT RECORDED FAILURE — investigate the job/adapter
  - soccervista: capture_forward_only — thin history EXPECTED (capture-forward only adapter)
  - bettingclosed: d30 — complete for D30

This audit is diagnostic only. It cannot create, promote or certify a pick, and a source appearing here with good numbers is NOT validated — see scripts/audit_source_settlement_coverage.py for settlement evidence.
