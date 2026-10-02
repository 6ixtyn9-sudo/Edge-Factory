# Same-day source funnel — 2026-10-02

as_of `2026-10-02T06:08:50+02:00`, min_lead 30m. Read-only, no network; gates reused from scripts/picks_today.py.

## A. Per-source same-day availability

| source | raw | fixtures | kickoff | ko_ok | prematch | 1x2 | ou | btts | in_1x2 | used | wh |
|---|---|---|---|---|---|---|---|---|---|---|---|
| forebet | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | True | True | True |
| zulubet | 22 | 19 | 19 | 19 | 12 | 19 | 0 | 0 | True | True | True |
| statarea | 78 | 72 | 72 | 72 | 58 | 72 | 72 | 0 | True | True | True |
| vitibet | 302 | 294 | 294 | 294 | 279 | 49 | 0 | 0 | True | True | True |
| betclan | 37 | 34 | 0 | 0 | 0 | 34 | 0 | 0 | True | True | True |
| scoutingstats | 114 | 107 | 107 | 107 | 105 | 74 | 74 | 31 | False | True | True |
| bzzoiro | 27 | 26 | 26 | 26 | 26 | 26 | 26 | 26 | True | True | True |
| predictz | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | False |
| windrawwin | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | True |
| freesupertips | 5 | 5 | 5 | 5 | 5 | 0 | 0 | 0 | False | False | True |
| afootballreport | 308 | 221 | 221 | 221 | 215 | 0 | 0 | 0 | False | False | True |
| prosoccer | 67 | 67 | 67 | 67 | 59 | 67 | 0 | 0 | False | False | True |
| soccervista | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | False |
| bettingclosed | 128 | 121 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | True |

Notes:
- **forebet**: no same-day rows captured
- **zulubet**: -
- **statarea**: 4 rows dropped by <4-char identity key
- **vitibet**: 5 rows dropped by <4-char identity key
- **betclan**: no trusted kickoff -> same-day guard drops anything anchored here; 2 rows dropped by <4-char identity key
- **scoutingstats**: consumed for OU/BTTS only, not in SOURCES_1X2; 2 rows dropped by <4-char identity key
- **bzzoiro**: 1 rows dropped by <4-char identity key
- **predictz**: no same-day rows captured
- **windrawwin**: no same-day rows captured
- **freesupertips**: NOT consumed by picks engine (captured but cannot vote); no 1X2 probability signal
- **afootballreport**: NOT consumed by picks engine (captured but cannot vote); no 1X2 probability signal; 13 rows dropped by <4-char identity key
- **prosoccer**: NOT consumed by picks engine (captured but cannot vote)
- **soccervista**: no same-day rows captured
- **bettingclosed**: NOT consumed by picks engine (captured but cannot vote); no trusted kickoff -> same-day guard drops anything anchored here; no 1X2 probability signal

## B. Cross-source identity overlap

- fixture groups: 656
- single-source groups: 496
- two-source groups: 84
- three-plus-source groups: 76
- reversed home/away risk groups: 0

Examples — singletons:
  - fixture=1860munchenii vs 1860rosenheim, source=vitibet
  - fixture=1heidenheim vs wurzburgerkickers, source=vitibet
  - fixture=1kaiserslautern vs sgsonnenhofgrossaspach, source=vitibet
  - fixture=1muhlhausen vs cfrpforzheim, source=vitibet
  - fixture=1nuremberg vs ingolstadt04, source=vitibet
  - fixture=7deabril vs friburguense, source=vitibet
  - fixture=aarau vs bscyoungboys, source=vitibet
  - fixture=aarhus vs vendsyssel, source=vitibet
  - fixture=academicabals vs vulturiifarcasesti, source=vitibet
  - fixture=academicarecea vs sighetumarmatiei, source=vitibet
Examples — multi_source:
  - fixture=aarau vs youngboys, sources=afootballreport,bettingclosed,prosoccer,scoutingstats
  - fixture=alain vs ajman, sources=afootballreport,vitibet
  - fixture=albaniau19 vs lithuaniau19, sources=bettingclosed,vitibet
  - fixture=anderlecht vs reims, sources=prosoccer,scoutingstats
  - fixture=andorrau21 vs moldovau21, sources=bettingclosed,statarea,vitibet
  - fixture=athletic vs sportrecife, sources=prosoccer,zulubet
  - fixture=athleticmg vs sportrecife, sources=betclan,vitibet
  - fixture=athlonetown vs corkcity, sources=afootballreport,bettingclosed,statarea,vitibet
  - fixture=augsburg vs herthaberlin, sources=bettingclosed,prosoccer,statarea
  - fixture=augsburg vs herthabsc, sources=scoutingstats,vitibet

## C. Consensus funnel

- match surface (union of forebet,zulubet,statarea,vitibet,betclan,bzzoiro): **339**
- fixtures with >=2 voters carrying 1X2 probs: **42**
- fixtures ML-meta can score (needs one of forebet,zulubet,statarea): **35**
- of those, pre-match eligible: **30**

Drops:
  - fewer_than_2_voters_with_1x2: 297
  - no_ml_anchor_source_present: 7
Examples — fewer_than_2_voters_with_1x2:
  - fixture=1860 München II vs 1860 Rosenheim, sources_with_1x2=-
  - fixture=1. FC Heidenheim vs Wurzburger Kickers, sources_with_1x2=-
  - fixture=1. FC Kaiserslautern vs SG Sonnenhof Grossaspach, sources_with_1x2=-
  - fixture=1. FC Muhlhausen vs CFR Pforzheim, sources_with_1x2=-
  - fixture=1. FC Nuremberg vs FC Ingolstadt 04, sources_with_1x2=-
  - fixture=7 de Abril vs Friburguense, sources_with_1x2=-
  - fixture=FC Aarau vs BSC Young Boys, sources_with_1x2=-
  - fixture=Aarhus vs Vendsyssel FF, sources_with_1x2=-
  - fixture=Academica Balș vs Vulturii Fărcăşeşti, sources_with_1x2=-
  - fixture=Academica Recea vs Sighetu Marmaţiei, sources_with_1x2=-
Examples — no_ml_anchor_source_present:
  - fixture=Athletic Club MG vs Sport Recife, sources_with_1x2=vitibet,betclan
  - fixture=Helmond Sport vs Heracles, sources_with_1x2=vitibet,betclan
  - fixture=Krems / Rehberg vs Wiener SC, sources_with_1x2=vitibet,betclan
  - fixture=Oberwart vs SV Horn, sources_with_1x2=vitibet,betclan
  - fixture=PWD Sports Club vs Brothers Union, sources_with_1x2=vitibet,betclan
  - fixture=Suriname vs Guatemala, sources_with_1x2=betclan,bzzoiro
  - fixture=Widad Témara vs UTS Rabat, sources_with_1x2=vitibet,betclan

## D. Kickoff / timing funnel

| source | fixtures | has_kickoff | trusted | missing | untrusted | pre_match |
|---|---:|---:|---:|---:|---:|---:|
| zulubet | 19 | 19 | 19 | 0 | 0 | 12 |
| statarea | 72 | 72 | 72 | 0 | 0 | 58 |
| vitibet | 294 | 294 | 294 | 0 | 0 | 279 |
| betclan | 34 | 0 | 0 | 34 | 0 | 0 |
| scoutingstats | 107 | 107 | 107 | 0 | 0 | 105 |
| bzzoiro | 26 | 26 | 26 | 0 | 0 | 26 |
| freesupertips | 5 | 5 | 5 | 0 | 0 | 5 |
| afootballreport | 221 | 221 | 221 | 0 | 0 | 215 |
| prosoccer | 67 | 67 | 67 | 0 | 0 | 59 |
| bettingclosed | 121 | 0 | 0 | 121 | 0 | 0 |

Same-day guard drops on the ML-scoreable surface:
  - inside_30m_lead_or_started: 5
Examples — inside_30m_lead_or_started:
  - fixture=China vs Palestine, kickoff_raw=06:35, kickoff_donors=statarea,vitibet,bzzoiro,prosoccer, sources=statarea,vitibet,bzzoiro
  - fixture=Dominican Republic vs Haiti, kickoff_raw=02-10, 01:00, kickoff_donors=zulubet,vitibet, sources=zulubet,vitibet,betclan
  - fixture=Internacional de Bogota vs Once Caldas, kickoff_raw=02-10, 02:00, kickoff_donors=zulubet,vitibet,scoutingstats, sources=zulubet,vitibet
  - fixture=Seattle Sounders vs Sporting Kansas City, kickoff_raw=02-10, 02:30, kickoff_donors=zulubet,statarea,vitibet, sources=zulubet,statarea,vitibet
  - fixture=South Korea vs Venezuela, kickoff_raw=06:00, kickoff_donors=statarea,vitibet,bzzoiro,prosoccer, sources=statarea,vitibet,betclan,bzzoiro

## A2. Voter classification

| source | tier | role | raw | fixtures | 1x2 rows | blocker |
|---|---|---|---:|---:|---:|---|
| forebet | live | blocked | 0 | 0 | 0 | no same-day rows captured |
| zulubet | live | live_voter | 22 | 19 | 19 | - |
| statarea | live | live_voter | 78 | 72 | 72 | - |
| vitibet | live | live_voter | 302 | 294 | 49 | - |
| betclan | live | live_voter | 37 | 34 | 34 | - |
| scoutingstats | live | not_a_voter | 114 | 107 | 74 | adapter exposes no 1X2 probability fields |
| bzzoiro | live | live_voter | 27 | 26 | 26 | - |
| predictz | shadow | blocked | 0 | 0 | 0 | no same-day rows captured |
| windrawwin | shadow | blocked | 0 | 0 | 0 | no same-day rows captured |
| freesupertips | shadow | blocked | 5 | 5 | 0 | rows captured but no 1X2 probability fields parsed |
| afootballreport | shadow | blocked | 308 | 221 | 0 | rows captured but no 1X2 probability fields parsed |
| prosoccer | shadow | shadow_voter | 67 | 67 | 67 | source tier is shadow: not settlement-validated for dispatch |
| soccervista | shadow | blocked | 0 | 0 | 0 | no same-day rows captured |
| bettingclosed | donor | not_a_voter | 128 | 121 | 0 | settlement/result donor only |

## A3. Shadow candidates (NON-DISPATCH)

- shadow candidate fixtures: **23** (dispatchable: False)
- shadow voter sources today: predictz, windrawwin, freesupertips, afootballreport, prosoccer, soccervista

Shadow evaluation only. These rows are NEVER dispatched, never become CLEAN/CAUTION picks, and are not read by the pick engine. Promotion requires settlement-coverage evidence plus operator sign-off.

Blockers:
  - fewer_than_2_live_voters: 8
  - inside_30m_lead_or_started: 6
  - no_ml_feature_provider_on_fixture: 4
  - shadow_sources_not_settlement_validated: 23

## A1. Source health warnings

- SOURCE_HEALTH: 'scoutingstats' has 1X2 rows today but its tier ('live') excludes it from both live and shadow consensus
- SOURCE_HEALTH: 30 candidate(s) existed but odds enrichment matched 0 — price identity may be broken (not merely an empty slate)

## E0. Shadow voter expansion (diagnostic, NON-DISPATCH)

- certified voter sources: forebet,zulubet,statarea,vitibet,betclan,bzzoiro
- shadow sources carrying 1X2 today: scoutingstats,prosoccer
- fixtures with >=2 certified voters: **42**
- fixtures with >=2 voters if shadow admitted: **70** (+28)

Diagnostic only. Admitting a shadow source is a certification decision requiring settlement-coverage evidence and operator sign-off; this audit never promotes anything.
Examples of fixtures that would gain a quorum:
  - aarau vs youngboys (scoutingstats,prosoccer)
  - athletic vs sportrecife (zulubet,prosoccer)
  - augsburg vs herthaberlin (statarea,prosoccer)
  - belgium vs turkiye (bzzoiro,scoutingstats)
  - caymanislands vs puertorico (betclan,prosoccer)
  - chinapr vs palestine (betclan,scoutingstats)
  - eldense vs realoviedo (bzzoiro,scoutingstats)
  - gornikzabrze vs odraopole (statarea,scoutingstats)
  - heidenheim vs wurzburgerkickers (statarea,scoutingstats)
  - laval vs rennes (statarea,scoutingstats,prosoccer)

## E. Odds / pricing funnel

| odds source | cached rows | fixtures | overlap with 1X2 surface | cov% |
|---|---:|---:|---:|---:|
| bzzoiro_odds | 0 | 0 | 0 | 0.0 |
| theoddsapi_odds | 0 | 0 | 0 | 0.0 |
| oddspapi_odds | 0 | 0 | 0 | 0.0 |
| betexplorer_odds | 0 | 0 | 0 | 0.0 |

Diagnosis: **no_price_rows_captured_today** (candidates before odds: 30)
- bzzoiro_odds: empty_no_rows_today
- theoddsapi_odds: empty_no_rows_today
- oddspapi_odds: empty_no_rows_today
- betexplorer_odds: empty_no_rows_today

## F. Backfill depth / retryable gaps

| source | first | latest | dates | capture window | fwd-only | missing in D30 | retryable | deeper possible |
|---|---|---|---:|---|---|---:|---:|---|
| forebet | 2024-01-01 | 2026-06-12 | 894 | 2026-09-02..2026-10-03 | no | 31 | 0 | yes |
| zulubet | 2024-01-01 | 2026-10-02 | 925 | 2026-09-02..2026-10-02 | no | 0 | 0 | no |
| statarea | 2017-01-01 | 2026-10-02 | 3478 | 2026-09-02..2026-10-02 | no | 0 | 0 | no |
| vitibet | 2026-09-02 | 2026-10-03 | 32 | 2026-09-02..2026-10-03 | no | 0 | 0 | no |
| betclan | 2026-10-02 | 2026-10-02 | 1 | 2026-10-02..2026-10-02 | yes | 30 | 0 | no |
| scoutingstats | 2026-09-02 | 2026-10-02 | 31 | 2026-09-02..2026-10-02 | no | 0 | 0 | no |
| bzzoiro | 2026-10-02 | 2026-10-09 | 8 | 2026-10-02..2026-10-02 | yes | 30 | 0 | no |
| predictz | - | - | 0 | 2026-09-02..2026-10-02 | no | 31 | 14 | yes |
| windrawwin | 2026-10-03 | 2026-10-03 | 1 | 2026-10-02..2026-10-03 | yes | 31 | 1 | no |
| freesupertips | 2026-10-02 | 2026-10-02 | 1 | 2026-10-02..2026-10-03 | yes | 30 | 0 | no |
| afootballreport | 2026-10-02 | 2026-10-02 | 1 | 2026-10-02..2026-10-02 | yes | 30 | 0 | no |
| prosoccer | 2026-09-30 | 2026-10-03 | 4 | 2026-10-01..2026-10-03 | no | 28 | 0 | yes |
| soccervista | - | - | 0 | 2026-10-02..2026-10-02 | yes | 31 | 1 | no |
| bettingclosed | 2026-09-02 | 2026-10-02 | 31 | 2026-09-02..2026-10-02 | no | 0 | 0 | no |

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
