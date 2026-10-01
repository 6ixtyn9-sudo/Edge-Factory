# Same-day source funnel — 2026-10-01

as_of `2026-10-01T07:37:20+02:00`, min_lead 30m. Read-only, no network; gates reused from scripts/picks_today.py.

## A. Per-source same-day availability

| source | raw | fixtures | kickoff | ko_ok | prematch | 1x2 | ou | btts | in_1x2 | used | wh |
|---|---|---|---|---|---|---|---|---|---|---|---|
| forebet | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | True | True | True |
| zulubet | 36 | 20 | 20 | 20 | 20 | 20 | 0 | 0 | True | True | True |
| statarea | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | True | True | True |
| vitibet | 133 | 118 | 117 | 117 | 103 | 31 | 0 | 0 | True | True | True |
| betclan | 70 | 66 | 0 | 0 | 0 | 66 | 0 | 0 | True | True | True |
| scoutingstats | 37 | 33 | 33 | 33 | 25 | 23 | 23 | 21 | False | True | True |
| bzzoiro | 44 | 22 | 22 | 22 | 18 | 22 | 22 | 22 | True | True | True |
| predictz | 32 | 32 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | True |
| windrawwin | 25 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | True |
| freesupertips | 5 | 5 | 5 | 5 | 5 | 0 | 0 | 0 | False | False | True |
| afootballreport | 399 | 301 | 301 | 301 | 214 | 0 | 0 | 0 | False | False | True |
| prosoccer | 25 | 25 | 25 | 25 | 19 | 25 | 0 | 0 | False | False | True |
| soccervista | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | False |
| bettingclosed | 70 | 62 | 0 | 0 | 0 | 0 | 0 | 0 | False | False | True |

Notes:
- **forebet**: no same-day rows captured
- **zulubet**: 1 rows dropped by <4-char identity key
- **statarea**: no same-day rows captured
- **vitibet**: 2 rows dropped by <4-char identity key
- **betclan**: no trusted kickoff -> same-day guard drops anything anchored here; 2 rows dropped by <4-char identity key
- **scoutingstats**: consumed for OU/BTTS only, not in SOURCES_1X2
- **bzzoiro**: -
- **predictz**: NOT consumed by picks engine (captured but cannot vote); no trusted kickoff -> same-day guard drops anything anchored here; no 1X2 probability signal
- **windrawwin**: NOT consumed by picks engine (captured but cannot vote); no trusted kickoff -> same-day guard drops anything anchored here; no 1X2 probability signal; 1 rows dropped by <4-char identity key
- **freesupertips**: NOT consumed by picks engine (captured but cannot vote); no 1X2 probability signal
- **afootballreport**: NOT consumed by picks engine (captured but cannot vote); no 1X2 probability signal; 11 rows dropped by <4-char identity key
- **prosoccer**: NOT consumed by picks engine (captured but cannot vote)
- **soccervista**: no same-day rows captured
- **bettingclosed**: NOT consumed by picks engine (captured but cannot vote); no trusted kickoff -> same-day guard drops anything anchored here; no 1X2 probability signal; 1 rows dropped by <4-char identity key

## B. Cross-source identity overlap

- fixture groups: 506
- single-source groups: 423
- two-source groups: 43
- three-plus-source groups: 40
- reversed home/away risk groups: 5

Examples — singletons:
  - fixture=6deenero vs atleticoparanaense, source=afootballreport
  - fixture=aarau vs youngboys, source=afootballreport
  - fixture=acskidstampabrasov vs coronabrasov, source=afootballreport
  - fixture=adalcorcon vs toledo, source=afootballreport
  - fixture=adamsstategrizzlies vs westerncoloradomountaine, source=afootballreport
  - fixture=affguatemala vs deportivofraijanes, source=afootballreport
  - fixture=aguiadesaopaulo vs gabusinho, source=afootballreport
  - fixture=alahli vs alnassr, source=afootballreport
  - fixture=alain vs ajman, source=afootballreport
  - fixture=albertusmagnusfalcons vs mitchellmariners, source=afootballreport
Examples — multi_source:
  - fixture=anguilla vs antiguabarbuda, sources=bzzoiro,scoutingstats
  - fixture=argentina vs bolivia, sources=betclan,bzzoiro,predictz,prosoccer,windrawwin
  - fixture=armeniau21 vs italyu21, sources=bettingclosed,vitibet
  - fixture=asantekotoko vs karela, sources=predictz,vitibet,windrawwin
  - fixture=ashdod vs maccabiherzliya, sources=betclan,bettingclosed,vitibet,zulubet
  - fixture=athletic vs sportrecife, sources=afootballreport,bzzoiro,scoutingstats
  - fixture=atleticonacional vs junior, sources=betclan,windrawwin
  - fixture=atleticoottawa vs cavalry, sources=predictz,windrawwin
  - fixture=austriawienw vs intermilanow, sources=scoutingstats,vitibet
  - fixture=azerbaijan vs liechtenstein, sources=betclan,bettingclosed,bzzoiro,predictz,prosoccer,scoutingstats,vitibet,windrawwin,zulubet
Examples — reversed_risk:
  - fixture=bakuelectronics vs nathan, sources=afootballreport, reversed_sources=afootballreport
  - fixture=faust21stcentury vs pfmkcontentcreators, sources=afootballreport, reversed_sources=afootballreport
  - fixture=heroesdezaci vs universidadautonomadetam, sources=afootballreport, reversed_sources=afootballreport
  - fixture=lynnfightingknights vs rollinstars, sources=afootballreport, reversed_sources=afootballreport
  - fixture=millikinbigblue vs wheatonthunder, sources=afootballreport, reversed_sources=afootballreport

## C. Consensus funnel

- match surface (union of forebet,zulubet,statarea,vitibet,betclan,bzzoiro): **156**
- fixtures with >=2 voters carrying 1X2 probs: **25**
- fixtures ML-meta can score (needs one of forebet,zulubet,statarea): **11**
- of those, pre-match eligible: **11**

Drops:
  - fewer_than_2_voters_with_1x2: 131
  - no_ml_anchor_source_present: 14
Examples — fewer_than_2_voters_with_1x2:
  - fixture=Al-Gharafa vs Al Mesaimeer, sources_with_1x2=-
  - fixture=Alianza vs Club Atletico Platense, sources_with_1x2=vitibet
  - fixture=Al Musannah vs Ibri, sources_with_1x2=-
  - fixture=Al Nasr vs Smail, sources_with_1x2=-
  - fixture=Al Shamal vs Muaither SC, sources_with_1x2=-
  - fixture=Al-Ula W vs Al Hilal W, sources_with_1x2=-
  - fixture=Anguilla vs Antigua and Barbuda, sources_with_1x2=bzzoiro
  - fixture=Armenia U21 vs Italy U21, sources_with_1x2=-
  - fixture=Asante Kotoko SC vs Karela, sources_with_1x2=vitibet
  - fixture=Athletic Club vs Sport Recife, sources_with_1x2=bzzoiro
Examples — no_ml_anchor_source_present:
  - fixture=Argentina vs Bolivia, sources_with_1x2=betclan,bzzoiro
  - fixture=Bnei Yehuda vs Maccabi Kiryat Gat, sources_with_1x2=vitibet,betclan
  - fixture=Dominica vs Guyana, sources_with_1x2=betclan,bzzoiro
  - fixture=Envigado vs Orsomarso, sources_with_1x2=vitibet,betclan
  - fixture=Hapoel Afula vs Hapoel Rishon LeZion, sources_with_1x2=vitibet,betclan
  - fixture=Hapoel Ra'anana vs Kafr Qasim, sources_with_1x2=vitibet,betclan
  - fixture=Japan vs Ecuador, sources_with_1x2=betclan,bzzoiro
  - fixture=Maccabi Ahi Nazareth vs Ironi Modi'in, sources_with_1x2=vitibet,betclan
  - fixture=Maccabi Kabilio Jaffa vs Hapoel Acre, sources_with_1x2=vitibet,betclan
  - fixture=Maldives vs Lebanon, sources_with_1x2=betclan,bzzoiro

## D. Kickoff / timing funnel

| source | fixtures | has_kickoff | trusted | missing | untrusted | pre_match |
|---|---:|---:|---:|---:|---:|---:|
| zulubet | 20 | 20 | 20 | 0 | 0 | 20 |
| vitibet | 118 | 117 | 117 | 1 | 0 | 103 |
| betclan | 66 | 0 | 0 | 66 | 0 | 0 |
| scoutingstats | 33 | 33 | 33 | 0 | 0 | 25 |
| bzzoiro | 22 | 22 | 22 | 0 | 0 | 18 |
| predictz | 32 | 0 | 0 | 32 | 0 | 0 |
| windrawwin | 24 | 0 | 0 | 24 | 0 | 0 |
| freesupertips | 5 | 5 | 5 | 0 | 0 | 5 |
| afootballreport | 301 | 301 | 301 | 0 | 0 | 214 |
| prosoccer | 25 | 25 | 25 | 0 | 0 | 19 |
| bettingclosed | 62 | 0 | 0 | 62 | 0 | 0 |

## A2. Voter classification

| source | tier | role | raw | fixtures | 1x2 rows | blocker |
|---|---|---|---:|---:|---:|---|
| forebet | live | blocked | 0 | 0 | 0 | no same-day rows captured |
| zulubet | live | live_voter | 36 | 20 | 20 | - |
| statarea | live | blocked | 0 | 0 | 0 | no same-day rows captured |
| vitibet | live | live_voter | 133 | 118 | 31 | - |
| betclan | live | live_voter | 70 | 66 | 66 | - |
| scoutingstats | live | not_a_voter | 37 | 33 | 23 | adapter exposes no 1X2 probability fields |
| bzzoiro | live | live_voter | 44 | 22 | 22 | - |
| predictz | shadow | blocked | 32 | 32 | 0 | rows captured but no 1X2 probability fields parsed |
| windrawwin | shadow | blocked | 25 | 24 | 0 | rows captured but no 1X2 probability fields parsed |
| freesupertips | shadow | blocked | 5 | 5 | 0 | rows captured but no 1X2 probability fields parsed |
| afootballreport | shadow | blocked | 399 | 301 | 0 | rows captured but no 1X2 probability fields parsed |
| prosoccer | shadow | shadow_voter | 25 | 25 | 25 | source tier is shadow: not settlement-validated for dispatch |
| soccervista | shadow | blocked | 0 | 0 | 0 | no same-day rows captured |
| bettingclosed | donor | not_a_voter | 70 | 62 | 0 | settlement/result donor only |

## A3. Shadow candidates (NON-DISPATCH)

- shadow candidate fixtures: **15** (dispatchable: False)
- shadow voter sources today: predictz, windrawwin, freesupertips, afootballreport, prosoccer, soccervista

Shadow evaluation only. These rows are NEVER dispatched, never become CLEAN/CAUTION picks, and are not read by the pick engine. Promotion requires settlement-coverage evidence plus operator sign-off.

Blockers:
  - fewer_than_2_live_voters: 3
  - inside_30m_lead_or_started: 1
  - no_ml_feature_provider_on_fixture: 7
  - shadow_sources_not_settlement_validated: 15

## A1. Source health warnings

- SOURCE_HEALTH: 'scoutingstats' has 1X2 rows today but its tier ('live') excludes it from both live and shadow consensus
- SOURCE_HEALTH: 11 candidate(s) existed but odds enrichment matched 0 — price identity may be broken (not merely an empty slate)

## E0. Shadow voter expansion (diagnostic, NON-DISPATCH)

- certified voter sources: forebet,zulubet,statarea,vitibet,betclan,bzzoiro
- shadow sources carrying 1X2 today: scoutingstats,prosoccer
- fixtures with >=2 certified voters: **25**
- fixtures with >=2 voters if shadow admitted: **32** (+7)

Diagnostic only. Admitting a shadow source is a certification decision requiring settlement-coverage evidence and operator sign-off; this audit never promotes anything.
Examples of fixtures that would gain a quorum:
  - athletic vs sportrecife (bzzoiro,scoutingstats)
  - austriawienw vs intermilanow (vitibet,scoutingstats)
  - bastia vs orleans (vitibet,scoutingstats)
  - curacao vs trinidadtobago (bzzoiro,scoutingstats)
  - guinea vs kenya (vitibet,scoutingstats,prosoccer)
  - indonesia vs bangladesh (zulubet,prosoccer)
  - ireland vs austria (bzzoiro,prosoccer)

## E. Odds / pricing funnel

| odds source | cached rows | fixtures | overlap with 1X2 surface | cov% |
|---|---:|---:|---:|---:|
| bzzoiro_odds | 0 | 0 | 0 | 0.0 |
| theoddsapi_odds | 0 | 0 | 0 | 0.0 |
| oddspapi_odds | 0 | 0 | 0 | 0.0 |
| betexplorer_odds | 0 | 0 | 0 | 0.0 |

Diagnosis: **no_price_rows_captured_today** (candidates before odds: 11)
- bzzoiro_odds: empty_no_rows_today
- theoddsapi_odds: empty_no_rows_today
- oddspapi_odds: empty_no_rows_today
- betexplorer_odds: empty_no_rows_today

## F. Backfill depth / retryable gaps

| source | first | latest | dates | capture window | fwd-only | missing in D30 | retryable | deeper possible |
|---|---|---|---:|---|---|---:|---:|---|
| forebet | 2024-01-01 | 2026-09-29 | 957 | 2026-09-01..2026-10-02 | no | 2 | 0 | yes |
| zulubet | 2024-01-01 | 2026-10-01 | 959 | 2026-09-01..2026-10-01 | no | 0 | 0 | no |
| statarea | 2017-01-01 | 2026-09-30 | 3511 | 2026-09-01..2026-10-01 | no | 1 | 2 | yes |
| vitibet | 2026-07-29 | 2026-10-02 | 66 | 2026-09-01..2026-10-02 | no | 0 | 0 | no |
| betclan | 2026-08-28 | 2026-10-01 | 35 | 2026-10-01..2026-10-01 | yes | 0 | 0 | no |
| scoutingstats | 2026-07-29 | 2026-10-01 | 65 | 2026-09-01..2026-10-01 | no | 0 | 0 | no |
| bzzoiro | 2026-08-27 | 2026-10-23 | 44 | 2026-10-01..2026-10-01 | yes | 0 | 0 | no |
| predictz | 2026-08-08 | 2026-10-01 | 36 | 2026-09-01..2026-10-01 | no | 1 | 2 | yes |
| windrawwin | 2026-08-29 | 2026-10-02 | 31 | 2026-10-01..2026-10-02 | yes | 4 | 1 | no |
| freesupertips | 2026-09-24 | 2026-10-01 | 4 | 2026-10-01..2026-10-02 | yes | 27 | 0 | no |
| afootballreport | 2026-08-28 | 2026-10-01 | 32 | 2026-10-01..2026-10-01 | yes | 3 | 0 | no |
| prosoccer | 2026-09-29 | 2026-10-02 | 4 | 2026-09-30..2026-10-02 | no | 28 | 0 | yes |
| soccervista | - | - | 0 | 2026-10-01..2026-10-01 | yes | 31 | 1 | no |
| bettingclosed | 2026-07-29 | 2026-10-01 | 65 | 2026-09-01..2026-10-01 | no | 0 | 0 | no |

Gap expectations:
  - forebet: historical — GAP WITHOUT RECORDED FAILURE — investigate the job/adapter
  - zulubet: d30 — complete for D30
  - statarea: d30 — gap with retryable failures — retry, then re-audit
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
