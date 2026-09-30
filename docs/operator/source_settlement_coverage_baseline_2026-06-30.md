# Source settlement coverage — 2026-04-01..2026-06-30

Prediction->final-score matching quality per source. Row counts alone are NOT validation.
Donor rows indexed: 85121 across 4 donor labels.
Guarded alias tier: enabled (edgefactory.identity fold).

| source | fixtures | own_score | exact | alias | matched | agree | conflict | donor_conf | unmatched | ambig | rev | cov% | confl% | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| forebet | 31429 | 31063 | 6874 | 5140 | 12014 | 11941 | 27 | 5 | 19005 | 405 | 3 | 38.23 | 0.23 | unproven |
| zulubet | 4790 | 4728 | 2698 | 533 | 3231 | 3207 | 7 | 4 | 1410 | 145 | 1 | 67.45 | 0.22 | partial |
| statarea | 12199 | 10941 | 6117 | 1818 | 7935 | 7087 | 34 | 0 | 3909 | 355 | 2 | 65.05 | 0.48 | partial |
| vitibet | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| scoutingstats | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| predictz | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| windrawwin | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| prosoccer | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| soccervista | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| bettingclosed | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| betclan | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| freesupertips | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| afootballreport | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| bzzoiro | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| bzzoiro_odds | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | excluded_pricing_only |
| theoddsapi_odds | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | excluded_pricing_only |
| oddspapi_odds | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | excluded_pricing_only |

## Notes
- **forebet** (prediction): orientation risk on 3 fixtures; 5 donor-conflicted fixtures; 405 ambiguous rejected; insufficient matched settlement evidence
- **zulubet** (prediction): orientation risk on 1 fixtures; 4 donor-conflicted fixtures; 145 ambiguous rejected; below validated thresholds (volume/coverage/conflict)
- **statarea** (prediction): orientation risk on 2 fixtures; 355 ambiguous rejected; below validated thresholds (volume/coverage/conflict)
- **vitibet** (prediction): no completed-window prediction rows in localdata
- **scoutingstats** (prediction): no completed-window prediction rows in localdata
- **predictz** (prediction): no completed-window prediction rows in localdata
- **windrawwin** (prediction): no completed-window prediction rows in localdata
- **prosoccer** (prediction): no completed-window prediction rows in localdata
- **soccervista** (prediction): no completed-window prediction rows in localdata
- **bettingclosed** (prediction): no completed-window prediction rows in localdata
- **betclan** (prediction): no completed-window prediction rows in localdata
- **freesupertips** (prediction): no completed-window prediction rows in localdata
- **afootballreport** (prediction): no completed-window prediction rows in localdata
- **bzzoiro** (prediction): no completed-window prediction rows in localdata
- **bzzoiro_odds** (pricing-only): pricing-only source; excluded from prediction->score coverage
- **theoddsapi_odds** (pricing-only): pricing-only source; excluded from prediction->score coverage
- **oddspapi_odds** (pricing-only): pricing-only source; excluded from prediction->score coverage

## Examples (max 5 per class per source)
### forebet
- ambiguous:
  - 2026-04-01 Burgos CF vs AD Ceuta — reason=multiple alias donor candidates, candidates=2
  - 2026-04-01 CD Águila vs Fuerte San Francisco — reason=multiple alias donor candidates, candidates=2
  - 2026-04-01 Club Rubio Ñu vs Club Guaraní — reason=multiple alias donor candidates, candidates=2
  - 2026-04-01 FC Andorra vs Málaga CF — reason=multiple alias donor candidates, candidates=2
  - 2026-04-01 Torrent CF vs CD Castellón B — reason=multiple alias donor candidates, candidates=2
- conflict:
  - 2026-04-09 FK Taraz vs Ulytau — reason=source score != donor score, source_score=0-0, donor_score=0-1, donors=statarea_csv
  - 2026-04-19 Celtic vs St Mirren — reason=source score != donor score, source_score=2-2, donor_score=6-2, donors=statarea_csv
  - 2026-04-22 Bodo/Glimt vs KFUM Oslo — reason=source score != donor score, source_score=1-1, donor_score=2-1, donors=statarea_csv
  - 2026-04-24 CA Batna vs USM Alger — reason=source score != donor score, source_score=1-1, donor_score=1-3, donors=statarea_csv
  - 2026-04-24 NEC vs Mbarara City — reason=source score != donor score, source_score=1-0, donor_score=0-0, donors=betexplorer_results_csv
- donor_conflict:
  - 2026-04-21 Budapest Honved vs Zalaegerszegi TE — reason=independent donors disagree, donor_scores=statarea_csv=2-2; zulubet_csv=1-1
  - 2026-05-05 Queen of the South vs Stenhousemuir FC — reason=independent donors disagree, donor_scores=statarea_csv=0-1; zulubet_csv=1-1
  - 2026-05-09 Bodo/Glimt vs Brann — reason=independent donors disagree, donor_scores=statarea_csv=3-3; zulubet_csv=2-2
  - 2026-05-23 Barcelona W vs Lyon W — reason=independent donors disagree, donor_scores=betexplorer_results_csv=4-0; statarea_csv=8-0
  - 2026-06-06 Machida Zelvia vs Nagoya Grampus — reason=independent donors disagree, donor_scores=statarea_csv=2-1; zulubet_csv=0-0
- reversed_candidate:
  - 2026-05-09 Marsaxlokk vs Hamrun Spartans — reason=donor has reversed home/away, donor_score=1-1, donors=statarea_csv
  - 2026-05-09 Valletta FC vs Floriana FC — reason=donor has reversed home/away, donor_score=0-0, donors=statarea_csv
  - 2026-05-10 Chiba vs Shao Jiang — reason=donor has reversed home/away, donor_score=3-3, donors=betexplorer_results_csv
- unmatched:
  - 2026-04-01 AC Rangers vs FC Mk de Kinshasa — reason=no independent donor row, source_score=0-1
  - 2026-04-01 AE Mykonos vs Ionikos — reason=no independent donor row, source_score=1-2
  - 2026-04-01 Aetos Orfani vs SKODA Xanthi — reason=no independent donor row, source_score=0-7
  - 2026-04-01 Aias Salamina vs Ilisiakos — reason=no independent donor row, source_score=0-3
  - 2026-04-01 Alexandreia vs Apollon Kalamaria — reason=no independent donor row, source_score=0-3
### zulubet
- ambiguous:
  - 2026-04-01 Burgos vs AD Ceuta FC — reason=multiple alias donor candidates, candidates=2
  - 2026-04-01 Águila vs Fuerte San Francisco — reason=multiple alias donor candidates, candidates=2
  - 2026-04-02 Brisbane Roar vs Sydney — reason=multiple alias donor candidates, candidates=2
  - 2026-04-02 FAS vs Municipal Limeño — reason=multiple alias donor candidates, candidates=2
  - 2026-04-02 Macarthur vs Newcastle Jets — reason=multiple alias donor candidates, candidates=2
- conflict:
  - 2026-04-01 Fjolnir vs Vídir — reason=source score != donor score, source_score=1-1, donor_score=2-1, donors=statarea_csv
  - 2026-04-02 Lyon W vs VfL Wolfsburg W — reason=source score != donor score, source_score=1-0, donor_score=4-0, donors=statarea_csv
  - 2026-04-23 VfB Stuttgart vs SC Freiburg — reason=source score != donor score, source_score=1-1, donor_score=2-1, donors=statarea_csv
  - 2026-05-05 Queen of the South vs Stenhousemuir — reason=source score != donor score, source_score=1-1, donor_score=0-1, donors=statarea_csv
  - 2026-05-24 Sporting CP vs Torreense — reason=source score != donor score, source_score=1-1, donor_score=1-2, donors=statarea_csv
- donor_conflict:
  - 2026-04-01 Chelsea W vs Arsenal W — reason=independent donors disagree, donor_scores=betexplorer_results_csv=1-0; statarea_csv=2-0
  - 2026-04-21 Budapest Honved vs Zalaegerszegi TE — reason=independent donors disagree, donor_scores=forebet_csv=1-1; statarea_csv=2-2
  - 2026-05-09 Bodo/Glimt vs Brann — reason=independent donors disagree, donor_scores=forebet_csv=2-2; statarea_csv=3-3
  - 2026-06-06 Machida Zelvia vs Nagoya Grampus — reason=independent donors disagree, donor_scores=forebet_csv=0-0; statarea_csv=2-1
- reversed_candidate:
  - 2026-04-27 Al Quwa Al Jawiya vs Newroz — reason=donor has reversed home/away, donor_score=1-1, donors=betexplorer_results_csv
- unmatched:
  - 2026-04-01 Alaniya Vladikavkaz vs Dinamo Stavropol — reason=no independent donor row, source_score=3-1
  - 2026-04-01 Alianza Valledupar vs Deportivo Pasto — reason=no independent donor row, source_score=0-0
  - 2026-04-01 Bayern Munich W vs Manchester United W — reason=no independent donor row, source_score=2-1
  - 2026-04-01 Birmingham City W vs Sunderland W — reason=no independent donor row, source_score=1-0
  - 2026-04-01 Bogota FC vs Real Soacha — reason=no independent donor row, source_score=2-2
### statarea
- ambiguous:
  - 2026-04-01 Burgos vs AD Ceuta — reason=multiple alias donor candidates, candidates=2
  - 2026-04-01 Puebla (w) vs Club Queretaro (w) — reason=multiple alias donor candidates, candidates=2
  - 2026-04-01 Torrent CF vs Castellon B — reason=multiple alias donor candidates, candidates=2
  - 2026-04-02 Brisbane Roar FC vs Sydney FC — reason=multiple alias donor candidates, candidates=2
  - 2026-04-02 Dempo SC vs Namdhari FC — reason=multiple alias donor candidates, candidates=2
- conflict:
  - 2026-04-01 Chelsea (w) vs Arsenal (w) — reason=source score != donor score, source_score=2-0, donor_score=1-0, donors=betexplorer_results_csv,zulubet_csv
  - 2026-04-01 Fjolnir vs Vidir — reason=source score != donor score, source_score=2-1, donor_score=1-1, donors=zulubet_csv
  - 2026-04-02 Lyon (w) vs VfL Wolfsburg (w) — reason=source score != donor score, source_score=4-0, donor_score=1-0, donors=zulubet_csv
  - 2026-04-09 Taraz vs Ulytau — reason=source score != donor score, source_score=0-1, donor_score=0-0, donors=forebet_csv
  - 2026-04-19 Celtic vs St Mirren — reason=source score != donor score, source_score=6-2, donor_score=2-2, donors=forebet_csv
- reversed_candidate:
  - 2026-04-23 FH Hafnarfjordur vs Valur Reykjavik — reason=donor has reversed home/away, donor_score=3-0, donors=forebet_csv
  - 2026-05-09 Hamrun Spartans vs Marsaxlokk — reason=donor has reversed home/away, donor_score=1-1, donors=forebet_csv
- unmatched:
  - 2026-04-01 Ansbach vs VfB Eichstatt — reason=no independent donor row, source_score=1-1
  - 2026-04-01 Atletico Goianiense vs Nautico Recife — reason=no independent donor row, source_score=1-2
  - 2026-04-01 Bahia vs Atletico Paranaense — reason=no independent donor row, source_score=3-0
  - 2026-04-01 Botafogo vs Mirassol — reason=no independent donor row, source_score=3-2
  - 2026-04-01 Deportes Tolima vs Rionegro FC — reason=no independent donor row, source_score=4-1

Verdicts are EVIDENCE, not certification. No source graduates from shadow/candidate on this report alone; operator sign-off is required.
