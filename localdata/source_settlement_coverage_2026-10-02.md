# Source settlement coverage — 2026-07-04..2026-10-02

Prediction->final-score matching quality per source. Row counts alone are NOT validation.
Donor rows indexed: 130115 across 20 donor labels.
Guarded alias tier: enabled (edgefactory.identity fold).

| source | fixtures | own_score | exact | alias | matched | agree | conflict | donor_conf | unmatched | ambig | rev | rev_unexp | cov% | confl% | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| forebet | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| zulubet | 2109 | 2062 | 1952 | 14 | 1966 | 1961 | 0 | 3 | 133 | 7 | 0 | 0 | 93.22 | 0.0 | settlement_validated |
| statarea | 4076 | 3924 | 2373 | 430 | 2803 | 2786 | 0 | 1 | 1174 | 98 | 0 | 0 | 68.77 | 0.0 | partial |
| vitibet | 15734 | 3743 | 6009 | 1753 | 7762 | 3735 | 0 | 15 | 7673 | 284 | 7 | 7 | 49.33 | 0.0 | unproven |
| scoutingstats | 4125 | 3966 | 1927 | 579 | 2506 | 2502 | 4 | 1 | 1442 | 176 | 0 | 0 | 60.75 | 0.16 | partial |
| predictz | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| windrawwin | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| prosoccer | 108 | 0 | 23 | 0 | 23 | 0 | 0 | 1 | 84 | 0 | 0 | 0 | 21.3 | 0.0 | unproven |
| soccervista | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | no_data |
| bettingclosed | 6881 | 6737 | 2536 | 407 | 2943 | 2940 | 3 | 6 | 3787 | 145 | 0 | 0 | 42.77 | 0.1 | unproven |
| betclan | 36 | 0 | 4 | 0 | 4 | 0 | 0 | 0 | 32 | 0 | 0 | 0 | 11.11 | 0.0 | unproven |
| freesupertips | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0.0 | 0.0 | unproven |
| afootballreport | 231 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 231 | 0 | 0 | 0 | 0.0 | 0.0 | unproven |
| bzzoiro | 27 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 27 | 0 | 0 | 0 | 0.0 | 0.0 | unproven |
| bzzoiro_odds | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | excluded_pricing_only |
| theoddsapi_odds | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | excluded_pricing_only |
| oddspapi_odds | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0.0 | 0.0 | excluded_pricing_only |

## Notes
- **forebet** (prediction): no completed-window prediction rows in localdata
- **zulubet** (prediction): 3 donor-conflicted fixtures; 7 ambiguous rejected
- **statarea** (prediction): 1 donor-conflicted fixtures; 98 ambiguous rejected; below validated thresholds (volume/coverage/conflict)
- **vitibet** (prediction): orientation risk on 7 fixtures (7 unexplained, 0 reviewed); 15 donor-conflicted fixtures; 284 ambiguous rejected; insufficient matched settlement evidence
- **scoutingstats** (prediction): 1 donor-conflicted fixtures; 176 ambiguous rejected; below validated thresholds (volume/coverage/conflict)
- **predictz** (prediction): no completed-window prediction rows in localdata
- **windrawwin** (prediction): no completed-window prediction rows in localdata
- **prosoccer** (prediction): 1 donor-conflicted fixtures; insufficient matched settlement evidence
- **soccervista** (prediction): no completed-window prediction rows in localdata
- **bettingclosed** (prediction): 6 donor-conflicted fixtures; 145 ambiguous rejected; insufficient matched settlement evidence
- **betclan** (prediction): insufficient matched settlement evidence
- **freesupertips** (prediction): insufficient matched settlement evidence
- **afootballreport** (prediction): insufficient matched settlement evidence
- **bzzoiro** (prediction): insufficient matched settlement evidence
- **bzzoiro_odds** (pricing-only): pricing-only source; excluded from prediction->score coverage
- **theoddsapi_odds** (pricing-only): pricing-only source; excluded from prediction->score coverage
- **oddspapi_odds** (pricing-only): pricing-only source; excluded from prediction->score coverage

## Examples (max 10 per class per source)
### zulubet
- ambiguous:
  - 2026-09-03 Mjallby AIF vs Djurgardens IF — reason=multiple alias donor candidates, candidates=2
  - 2026-09-06 FK Crvena Zvezda vs FK Partizan — reason=multiple alias donor candidates, candidates=2
  - 2026-09-07 Kalmar FF vs Djurgardens IF — reason=multiple alias donor candidates, candidates=2
  - 2026-09-10 Haninge vs Djurgardens IF — reason=multiple alias donor candidates, candidates=2
  - 2026-09-17 Železničar Pančevo vs FK Crvena Zvezda — reason=multiple alias donor candidates, candidates=2
  - 2026-09-20 FK Crvena Zvezda vs Radnicki NIS — reason=multiple alias donor candidates, candidates=2
  - 2026-09-24 Rivers United vs Kun Khalifat FC — reason=multiple alias donor candidates, candidates=2
- donor_conflict:
  - 2026-09-02 TOGB vs Katwijk — reason=independent donors disagree, donor_scores=bettingclosed_csv=3-2; bettingclosed_settled=3-2; scoutingstats_csv=3-2; vitibet_csv=2-2; wh:bettingclosed_settled=3-2; wh:scoutingstats_settled=3-2
  - 2026-09-10 FC Tallinn vs Maardu — reason=independent donors disagree, donor_scores=bettingclosed_csv=4-2; bettingclosed_settled=0-0; wh:bettingclosed_settled=4-2
  - 2026-10-01 Indonesia vs Bangladesh — reason=independent donors disagree, donor_scores=bettingclosed_csv=9-2; vitibet_csv=7-2; wh:bettingclosed_settled=9-2
- unmatched:
  - 2026-09-02 Atletico vs MG - Cruzeiro — reason=no independent donor row, source_score=2-1
  - 2026-09-02 Gintra vs Universitetas W - Sturm Graz W — reason=no independent donor row, source_score=3-5
  - 2026-09-02 H&H Export vs Walter Ferretti — reason=no independent donor row, source_score=1-1
  - 2026-09-02 HNK Cibalia vs Orijent 1919 — reason=no independent donor row, source_score=0-0
  - 2026-09-02 Inter Milano W vs VfL Wolfsburg W — reason=no independent donor row, source_score=2-0
  - 2026-09-02 Luton vs Stockport County — reason=no independent donor row, source_score=2-0
  - 2026-09-02 Paris Saint Germain W vs Eintracht Frankfurt W — reason=no independent donor row, source_score=1-1
  - 2026-09-02 St. Truiden vs Union St. Gilloise — reason=no independent donor row, source_score=0-3
  - 2026-09-03 Al vs Fayha - Al Kholood — reason=no independent donor row, source_score=2-2
  - 2026-09-03 Cariari Pococi vs Pitbulls Santa Barbara FC — reason=no independent donor row, source_score=
### statarea
- ambiguous:
  - 2026-09-02 Gornik Zabrze II vs Olimpia Grudziadz — reason=multiple alias donor candidates, candidates=2
  - 2026-09-02 Grasshopper-Club vs FC St. Gallen — reason=multiple alias donor candidates, candidates=2
  - 2026-09-02 VfL Osnabruck vs Bayern Munich — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 Deportivo Capiata vs Club 3 De Noviembre — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 Igdir FK vs Manisa FK — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 Metropolitanos FC vs Trujillanos FC — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Cheongju FC vs Seoul E-Land FC — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Novi Pazar vs Zeleznicar Pancevo — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Richards Bay FC vs AmaZulu — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Sportivo Carapegua vs Paraguari Ac — reason=multiple alias donor candidates, candidates=2
- donor_conflict:
  - 2026-09-18 Spartakos Kitiou vs MEAP Nisou — reason=independent donors disagree, donor_scores=forebet_settled=4-1; vitibet_csv=4-0
- unmatched:
  - 2026-09-02 Aluminij vs NK Celje — reason=no independent donor row, source_score=0-2
  - 2026-09-02 Al-Wehda Club vs Dhamk — reason=no independent donor row, source_score=2-2
  - 2026-09-02 Baltika vs Krylya Sovetov — reason=no independent donor row, source_score=
  - 2026-09-02 Charlotte Independence vs Portland Hearts Of Pine — reason=no independent donor row, source_score=3-2
  - 2026-09-02 Club Nacional vs Libertad — reason=no independent donor row, source_score=3-0
  - 2026-09-02 C-Osaka vs Kashiwa Reysol — reason=no independent donor row, source_score=2-0
  - 2026-09-02 El Gouna FC vs Al Mokawloon — reason=no independent donor row, source_score=0-1
  - 2026-09-02 Fatih Karagumruk AS vs Kayserispor — reason=no independent donor row, source_score=1-1
  - 2026-09-02 FC Arges Pitesti vs FCSB — reason=no independent donor row, source_score=0-5
  - 2026-09-02 Flora Tallinn vs Tammeka Tartu — reason=no independent donor row, source_score=3-2
### vitibet
- ambiguous:
  - 2026-09-02 Boleráz vs Šoporňa — reason=multiple alias donor candidates, candidates=2
  - 2026-09-02 Mamelodi Sundowns FC vs Milford FC — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 CD Limache vs Nublense — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 Diyala SC vs Al-Karma — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 Mjallby AIF vs Djurgårdens IF — reason=multiple alias donor candidates, candidates=3
  - 2026-09-03 Vélez Sarsfield vs CA Boca Juniors — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Emmen vs FC Volendam — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Frem vs Ringsted — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 HB Koge vs Hillerød — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Marumo Gallants FC vs Polokwane City FC — reason=multiple alias donor candidates, candidates=2
- donor_conflict:
  - 2026-09-02 Sloven Ruma vs Kabel Novi Sad — reason=independent donors disagree, donor_scores=bettingclosed_csv=1-1; bettingclosed_settled=2-1; wh:bettingclosed_settled=1-1
  - 2026-09-02 TOGB vs Katwijk — reason=independent donors disagree, donor_scores=bettingclosed_csv=3-2; bettingclosed_settled=3-2; scoutingstats_csv=3-2; wh:bettingclosed_settled=3-2; wh:scoutingstats_settled=3-2; wh:zulubet_settled=2-2; zulubet_csv=2-2
  - 2026-09-06 Parndorf vs Wolfsberger AC — reason=independent donors disagree, donor_scores=bettingclosed_csv=2-2; forebet_settled=1-1; wh:bettingclosed_settled=2-2
  - 2026-09-09 Bishop Auckland vs AFC Emley — reason=independent donors disagree, donor_scores=forebet_settled=0-0; scoutingstats_csv=0-2; wh:scoutingstats_settled=0-2
  - 2026-09-09 CF Talavera vs Navalcarnero — reason=independent donors disagree, donor_scores=bettingclosed_csv=0-2; forebet_settled=0-0; wh:bettingclosed_settled=0-2
  - 2026-09-09 Uskok Klis vs HNK Gorica — reason=independent donors disagree, donor_scores=bettingclosed_csv=1-3; forebet_settled=1-1; wh:bettingclosed_settled=1-3
  - 2026-09-10 FC Tallinn vs Maardu — reason=independent donors disagree, donor_scores=bettingclosed_csv=4-2; bettingclosed_settled=0-0; wh:bettingclosed_settled=4-2
  - 2026-09-12 Merw vs Köpetdag Aşgabat — reason=independent donors disagree, donor_scores=bettingclosed_csv=2-2; bettingclosed_settled=0-0; wh:bettingclosed_settled=2-2
  - 2026-09-12 Oleksandria II vs Rebel — reason=independent donors disagree, donor_scores=bettingclosed_csv=0-1; forebet_settled=1-1; wh:bettingclosed_settled=0-1
  - 2026-09-18 Spartakos Kitiou vs MEAP Nisou — reason=independent donors disagree, donor_scores=forebet_settled=4-1; statarea_csv=4-0; wh:statarea_settled=4-0
- reversed_candidate_unexplained:
  - 2026-09-06 Jaraíz vs Atlético Pueblonuevo — reason=donor has reversed home/away, donor_score=2-2, donors=forebet_settled, review=UNEXPLAINED - blocks validation
  - 2026-09-06 Werder Bremen II vs Phönix Lübeck — reason=donor has reversed home/away, donor_score=0-2, donors=forebet_settled, review=UNEXPLAINED - blocks validation
  - 2026-09-12 Melaka vs Kuching FA — reason=donor has reversed home/away, donor_score=1-2, donors=bettingclosed_csv,forebet_settled,wh:bettingclosed_settled, review=UNEXPLAINED - blocks validation
  - 2026-09-20 Cherno more II vs Olympic Varna — reason=donor has reversed home/away, donor_score=2-0, donors=forebet_settled, review=UNEXPLAINED - blocks validation
  - 2026-09-20 Santa Amalia vs Atlético Pueblonuevo — reason=donor has reversed home/away, donor_score=1-1, donors=forebet_settled, review=UNEXPLAINED - blocks validation
  - 2026-09-25 Gualaceo SC vs Independiente del Valle — reason=donor has reversed home/away, donor_score=0-2, donors=wh:zulubet_settled,zulubet_csv,zulubet_settled, review=UNEXPLAINED - blocks validation
  - 2026-09-26 Borac Banja Luka vs Radnik Bijeljina — reason=donor has reversed home/away, donor_score=3-4, donors=scoutingstats_csv, review=UNEXPLAINED - blocks validation
- unmatched:
  - 2026-09-02 Agram W vs Minsk W — reason=no independent donor row, source_score=
  - 2026-09-02 Aston Villa U21 vs Brondby U21 — reason=no independent donor row, source_score=
  - 2026-09-02 ATC 65 vs DVS 33 Ermelo — reason=no independent donor row, source_score=
  - 2026-09-02 Athletico PR U17 vs Corinthians U17 — reason=no independent donor row, source_score=
  - 2026-09-02 Atletico GO U17 vs Vasco U17 — reason=no independent donor row, source_score=
  - 2026-09-02 Atletico-MG vs Cruzeiro — reason=no independent donor row, source_score=
  - 2026-09-02 Atletico Torres U20 vs CA Porto U20 — reason=no independent donor row, source_score=
  - 2026-09-02 Bahia U17 vs Atlético Mineiro U17 — reason=no independent donor row, source_score=
  - 2026-09-02 Baltika vs Krylia Sovetov — reason=no independent donor row, source_score=
  - 2026-09-02 Benešov vs Sparta Praha II — reason=no independent donor row, source_score=
### scoutingstats
- ambiguous:
  - 2026-09-03 Basel vs Sion — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 Raków Częstochowa vs Górnik Zabrze — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Novi Pazar vs Železničar Pančevo — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Paju Citizen vs Daegu — reason=multiple alias donor candidates, candidates=2
  - 2026-09-05 Bastia vs Amiens SC — reason=multiple alias donor candidates, candidates=2
  - 2026-09-05 Brann vs Lillestrøm — reason=multiple alias donor candidates, candidates=2
  - 2026-09-05 Danubio vs Peñarol — reason=multiple alias donor candidates, candidates=3
  - 2026-09-05 Grasshopper vs Zürich — reason=multiple alias donor candidates, candidates=3
  - 2026-09-05 Juárez vs Pachuca — reason=multiple alias donor candidates, candidates=3
  - 2026-09-05 Kagoshima United vs Ryūkyū — reason=multiple alias donor candidates, candidates=2
- conflict:
  - 2026-09-09 Bishop Auckland vs AFC Emley — reason=source score != donor score, source_score=0-2, donor_score=0-0, donors=forebet_settled
  - 2026-09-20 FC Serpa vs Louletano — reason=source score != donor score, source_score=1-2, donor_score=1-1, donors=forebet_settled
  - 2026-09-22 Dorking Wanderers vs Southall — reason=source score != donor score, source_score=5-4, donor_score=3-3, donors=forebet_settled
  - 2026-09-22 Koninklijke HFC vs DOVO — reason=source score != donor score, source_score=3-1, donor_score=1-1, donors=forebet_settled
- donor_conflict:
  - 2026-09-02 TOGB vs Katwijk — reason=independent donors disagree, donor_scores=bettingclosed_csv=3-2; bettingclosed_settled=3-2; vitibet_csv=2-2; wh:bettingclosed_settled=3-2; wh:zulubet_settled=2-2; zulubet_csv=2-2
- unmatched:
  - 2026-09-02 ACV vs Westlandia — reason=no independent donor row, source_score=6-1
  - 2026-09-02 AGF vs FC Midtjylland — reason=no independent donor row, source_score=0-2
  - 2026-09-02 Austria Wien vs WSG Tirol — reason=no independent donor row, source_score=0-1
  - 2026-09-02 Avispa Fukuoka vs Urawa Reds — reason=no independent donor row, source_score=2-3
  - 2026-09-02 Baltika Kaliningrad vs Krylya Sovetov — reason=no independent donor row, source_score=0-0
  - 2026-09-02 Ceramica Cleopatra vs Modern Sport FC — reason=no independent donor row, source_score=2-0
  - 2026-09-02 Colegiales vs Midland — reason=no independent donor row, source_score=3-0
  - 2026-09-02 Coquimbo Unido vs Univ. Concepción — reason=no independent donor row, source_score=1-0
  - 2026-09-02 El Gounah vs Al Mokawloon — reason=no independent donor row, source_score=0-1
  - 2026-09-02 Fatih Karagümrük vs Kayserispor — reason=no independent donor row, source_score=1-1
### prosoccer
- donor_conflict:
  - 2026-10-01 INDONESIA vs BANGLADESH — reason=independent donors disagree, donor_scores=bettingclosed_csv=9-2; vitibet_csv=7-2; wh:bettingclosed_settled=9-2; wh:results_donor=9-2; wh:zulubet_settled=7-2; zulubet_csv=7-2
- unmatched:
  - 2026-09-30 BELIZE vs ST. VINCENT & G — reason=no independent donor row, source_score=
  - 2026-09-30 EAST TIMOR vs CAMBODIA — reason=no independent donor row, source_score=
  - 2026-09-30 ENYIMBA INTERNATIO vs SHOOTING STARS — reason=no independent donor row, source_score=
  - 2026-09-30 HONEFOSS vs KFUM KAMERATENE — reason=no independent donor row, source_score=
  - 2026-09-30 INDEP. MEDELLIN vs LOS MILLONARIOS — reason=no independent donor row, source_score=
  - 2026-09-30 KATSINA vs RIVERS UNITED — reason=no independent donor row, source_score=
  - 2026-09-30 SPORTING LAGOS vs IKORODU UNITED — reason=no independent donor row, source_score=
  - 2026-09-30 TAMWORTH vs SUTTON UNT — reason=no independent donor row, source_score=
  - 2026-09-30 U. ARAB EMIRATE vs QATAR — reason=no independent donor row, source_score=
  - 2026-09-30 WARRI WOLVES vs ENUGU RANGERS INTE — reason=no independent donor row, source_score=
### bettingclosed
- ambiguous:
  - 2026-09-02 VfL Osnabruck vs Bayern Munchen — reason=multiple alias donor candidates, candidates=2
  - 2026-09-02 Yaracuyanos vs Urena SC — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 Basel vs FC Sion — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 Cittadella vs Renate AC — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 FC Rouen vs Valenciennes — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 Igdir vs Manisa — reason=multiple alias donor candidates, candidates=2
  - 2026-09-03 Mjallby AIF vs Djurgardens — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Aalesund FK vs Start IK — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Hobro vs Hvidovre IF — reason=multiple alias donor candidates, candidates=2
  - 2026-09-04 Noah vs FC Gandzasar — reason=multiple alias donor candidates, candidates=2
- conflict:
  - 2026-09-09 Talavera CF vs Navalcarnero — reason=source score != donor score, source_score=0-2, donor_score=0-0, donors=forebet_settled
  - 2026-09-16 Terrassa vs Binefar — reason=source score != donor score, source_score=4-0, donor_score=0-0, donors=forebet_settled
  - 2026-10-01 Indonesia vs Bangladesh — reason=source score != donor score, source_score=9-2, donor_score=7-2, donors=vitibet_csv,wh:zulubet_settled,zulubet_csv
- donor_conflict:
  - 2026-09-02 TOGB vs Katwijk — reason=independent donors disagree, donor_scores=scoutingstats_csv=3-2; vitibet_csv=2-2; wh:scoutingstats_settled=3-2; wh:zulubet_settled=2-2; zulubet_csv=2-2
  - 2026-09-06 Parndorf vs Wolfsberger AC — reason=independent donors disagree, donor_scores=forebet_settled=1-1; vitibet_csv=2-2
  - 2026-09-09 Uskok Klis vs HNK Gorica — reason=independent donors disagree, donor_scores=forebet_settled=1-1; vitibet_csv=1-3
  - 2026-09-12 Oleksandria II vs Rebel — reason=independent donors disagree, donor_scores=forebet_settled=1-1; vitibet_csv=0-1
  - 2026-09-20 Serpa vs Louletano — reason=independent donors disagree, donor_scores=forebet_settled=1-1; scoutingstats_csv=1-2; wh:scoutingstats_settled=1-2
  - 2026-09-26 Diegem Sport vs Francs Borains — reason=independent donors disagree, donor_scores=forebet_settled=0-0; vitibet_csv=0-1
- unmatched:
  - 2026-09-02 ACV Assen vs Westlandia — reason=no independent donor row, source_score=6-1
  - 2026-09-02 AEL Larissa vs Olympiakos — reason=no independent donor row, source_score=0-4
  - 2026-09-02 AGF Aarhus vs Midtjylland — reason=no independent donor row, source_score=0-2
  - 2026-09-02 Altamura vs Sambenedettese — reason=no independent donor row, source_score=2-2
  - 2026-09-02 Al Wehda(KSA) vs Damac — reason=no independent donor row, source_score=2-2
  - 2026-09-02 Ameliano vs Sportivo Trinide — reason=no independent donor row, source_score=0-3
  - 2026-09-02 ArzignanoChiampo vs Dolomiti Bellune — reason=no independent donor row, source_score=2-2
  - 2026-09-02 AS Sorrento Calc vs Cosenza Calcio 1 — reason=no independent donor row, source_score=1-0
  - 2026-09-02 Ath. Carpi vs Pro Vercelli — reason=no independent donor row, source_score=1-1
  - 2026-09-02 Atletico El Vigi vs Club Atletico Ba — reason=no independent donor row, source_score=2-1
### betclan
- unmatched:
  - 2026-10-02 Athletic Club Mg vs Sport Recife — reason=no independent donor row, source_score=
  - 2026-10-02 Baladiyyat Al Mehalla vs Team — reason=no independent donor row, source_score=
  - 2026-10-02 Ca Batna vs Msp Batna — reason=no independent donor row, source_score=
  - 2026-10-02 China Pr vs Palestine — reason=no independent donor row, source_score=
  - 2026-10-02 Dukla Praha vs Fk Jablonec — reason=no independent donor row, source_score=
  - 2026-10-02 El Dakhleya vs Maleyet Kafr El Zayiat — reason=no independent donor row, source_score=
  - 2026-10-02 Ferro Carril Oeste vs Deportivo Madryn — reason=no independent donor row, source_score=
  - 2026-10-02 Fremad Amager vs B 93 — reason=no independent donor row, source_score=
  - 2026-10-02 Garliava vs Dainava — reason=no independent donor row, source_score=
  - 2026-10-02 Helmond Sport vs Heracles — reason=no independent donor row, source_score=
### freesupertips
- unmatched:
  - 2026-10-02 Belgium vs Turkiye — reason=no independent donor row, source_score=
  - 2026-10-02 Bosnia And Herzegovina vs Sweden — reason=no independent donor row, source_score=
  - 2026-10-02 France vs Italy — reason=no independent donor row, source_score=
  - 2026-10-02 Poland vs Romania — reason=no independent donor row, source_score=
  - 2026-10-02 Ukraine vs Northern Ireland — reason=no independent donor row, source_score=
### afootballreport
- unmatched:
  - 2026-10-02 Aarau vs Young Boys — reason=no independent donor row, source_score=
  - 2026-10-02 ACS Kids Tampa Brasov vs Corona Brașov — reason=no independent donor row, source_score=
  - 2026-10-02 AD Alcorcon vs CD Toledo — reason=no independent donor row, source_score=
  - 2026-10-02 Adams State Grizzlies vs Colorado Mesa Mavericks — reason=no independent donor row, source_score=
  - 2026-10-02 AE Medea vs IBKEK — reason=no independent donor row, source_score=
  - 2026-10-02 AGF vs Vendsyssel FF — reason=no independent donor row, source_score=
  - 2026-10-02 Al-Ahli vs Al-Nassr — reason=no independent donor row, source_score=
  - 2026-10-02 Al-Ain vs Ajman — reason=no independent donor row, source_score=
  - 2026-10-02 Al Rams vs Baynounah — reason=no independent donor row, source_score=
  - 2026-10-02 Al-Sahra vs Al Ethihad — reason=no independent donor row, source_score=
### bzzoiro
- unmatched:
  - 2026-10-02 Belgium vs Türkiye — reason=no independent donor row, source_score=
  - 2026-10-02 Bosnia & Herzegovina vs Sweden — reason=no independent donor row, source_score=
  - 2026-10-02 CA Independiente vs Instituto De Córdoba — reason=no independent donor row, source_score=
  - 2026-10-02 CD Eldense vs Real Oviedo — reason=no independent donor row, source_score=
  - 2026-10-02 China vs Palestine — reason=no independent donor row, source_score=
  - 2026-10-02 China vs Turkmenistan — reason=no independent donor row, source_score=
  - 2026-10-02 Cyprus vs Armenia — reason=no independent donor row, source_score=
  - 2026-10-02 DR Congo vs Uganda — reason=no independent donor row, source_score=
  - 2026-10-02 Faroe Islands vs Slovakia — reason=no independent donor row, source_score=
  - 2026-10-02 Fath Union Sport vs Union Sportive Amal Tiznit — reason=no independent donor row, source_score=

Verdicts are EVIDENCE, not certification. No source graduates from shadow/candidate on this report alone; operator sign-off is required. A source with ANY unexplained reversed home/away candidate caps at `review_required` - explain the fixture in Config/reversal_reviews.json or treat the orientation as unproven.
