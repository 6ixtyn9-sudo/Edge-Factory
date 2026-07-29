# Edge Factory — Recent picks audit (2026-06-30 to 2026-07-29)

## Overall

- archived pick rows: 59
- archived pick dates: 19
- settled picks: 56
- eligible prior 1x2 picks: 56
- unmatched result picks: 0
- ambiguous result picks: 0
- wins: 45
- hit rate: 0.803571
- priced picks: 56
- ROI: 0.07875

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-07-29
- same-day rows excluded: 3

## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 36 / 56 matches (64.3%)
- **Both Teams to Score (BTTS)**: occurred in 26 / 56 matches (46.4%)
- **Selected Team Over 1.5 Goals**: occurred in 42 / 56 matches (75.0%)

## By rule

- `2way-unanimous avg_p>=70`: settled=22, wins=18, hit_rate=0.818182, ROI=0.134091
- `3way-unanimous avg_p>=65`: settled=8, wins=5, hit_rate=0.625, ROI=-0.1525
- `3way-unanimous home-only avg_p>=60`: settled=10, wins=9, hit_rate=0.9, ROI=0.277
- `3way-unanimous home-only avg_p>=65`: settled=16, wins=13, hit_rate=0.8125, ROI=-0.005625

## By bucket

- `CAUTION`: settled=12, wins=7, hit_rate=0.583333, ROI=0.013333
- `SKIPPED_VETO`: settled=38, wins=33, hit_rate=0.868421, ROI=0.123158
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333, ROI=-0.071667

## By odds source

- `betexplorer_odds`: settled=35, wins=30, hit_rate=0.857143, ROI=0.092
- `bzzoiro_odds`: settled=12, wins=11, hit_rate=0.916667, ROI=0.433333
- `forebet_best`: settled=1, wins=1, hit_rate=1.0, ROI=0.22
- `scoutingstats_odds`: settled=7, wins=3, hit_rate=0.428571, ROI=-0.461429
- `zulubet`: settled=1, wins=0, hit_rate=0.0, ROI=-1.0

## By odds match method

- `alias_fuzzy`: settled=1, wins=1, hit_rate=1.0, ROI=0.39
- `betexplorer`: settled=35, wins=30, hit_rate=0.857143, ROI=0.092
- `exact`: settled=18, wins=13, hit_rate=0.722222, ROI=0.087778
- `fallback`: settled=2, wins=1, hit_rate=0.5, ROI=-0.39
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-07-28: Neftchi vs Navbahor (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.76 -> 🔴 LOST (Expected prob: 73.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 74.6% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 40.7% (Actual: BTTS-Yes)
  - **Top Scores**: [🔴 MISS] 1-0 (12.8%), [🔴 MISS] 2-0 (12.6%)

### 2026-07-28: Apollon Limassol vs Dila (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.39 -> 🟢 WON (Expected prob: 73.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 75.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 42.1% (Actual: BTTS-No)
  - **Top Scores**: [🟢 HIT] 3-0 (12.5%), [🔴 MISS] 1-0 (12.3%)

### 2026-07-28: Apollon Limassol vs Dila Gori (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.39 -> 🟢 WON (Expected prob: 65.7%)

### 2026-07-27: Valmiera / BSS vs Riga FC II (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 79.0%)

### 2026-07-27: CFR 1907 Cluj vs FC Voluntari (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.87 -> 🟢 WON (Expected prob: 65.3%)

### 2026-07-27: Metta / LU vs Tukums II (Actual Score: **9-0**)
- **1X2 Pick**: Selected `HOME` @ 1.07 -> 🟢 WON (Expected prob: 85.5%)

### 2026-07-27: Tukums vs Rīgas FS (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.23 -> 🟢 WON (Expected prob: 73.0%)

### 2026-07-27: FK Tukums 2000 vs Rigas Futbola skola (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.22 -> 🟢 WON (Expected prob: 71.0%)

### 2026-07-27: Dunav Ruse vs Ludogorets (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.33 -> 🟢 WON (Expected prob: 69.2%)

### 2026-07-24: Vasteras SK FK vs Orgryte IS (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 2.06 -> 🟢 WON (Expected prob: 71.5%)

### 2026-07-24: FC Dornbirn vs SV Ried (Actual Score: **1-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.13 -> 🟢 WON (Expected prob: 75.5%)

### 2026-07-24: Vikingur Reykjavik vs Keflavik (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 73.0%)

### 2026-07-23: Rakow Czestochowa vs Valletta FC (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.13 -> 🟢 WON (Expected prob: 71.7%)

### 2026-07-23: BATE Borisov vs FC Sion (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.26 -> 🔴 LOST (Expected prob: 67.3%)

### 2026-07-22: Sassuolo vs Padova (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 70.0%)

### 2026-07-22: Independiente del Valle vs Tecnico Universitario (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🟢 WON (Expected prob: 82.0%)

### 2026-07-21: Livingston vs Forfar Athletic (Actual Score: **8-0**)
- **1X2 Pick**: Selected `HOME` @ 1.07 -> 🟢 WON (Expected prob: 67.0%)

### 2026-07-21: Cumberland Utd vs Heidelberg United (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.23 -> 🟢 WON (Expected prob: 65.7%)

### 2026-07-21: Walsall vs Aston Villa (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 2.18 -> 🟢 WON (Expected prob: 64.0%)

### 2026-07-21: Clyde FC vs Annan Athletic (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.61 -> 🟢 WON (Expected prob: 62.7%)

### 2026-07-21: Dunfermline vs Cove Rangers (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.29 -> 🟢 WON (Expected prob: 62.7%)

### 2026-07-21: Kelty Hearts vs Brora Rangers (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.39 -> 🟢 WON (Expected prob: 62.7%)

### 2026-07-21: Alloa Athletic vs Falkirk FC (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.24 -> 🔴 LOST (Expected prob: 62.3%)

### 2026-07-21: Bayswater City vs Sydney FC (Actual Score: **1-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.21 -> 🟢 WON (Expected prob: 62.0%)

### 2026-07-20: HK Kopavogur vs Vestri (Actual Score: **6-2**)
- **1X2 Pick**: Selected `HOME` @ 1.47 -> 🟢 WON (Expected prob: 60.0%)

### 2026-07-18: Thor Akureyri vs Vikingur Reykjavik (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.13 -> 🔴 LOST (Expected prob: 78.3%)

### 2026-07-18: Monaco vs Saint-Priest (Actual Score: **5-2**)
- **1X2 Pick**: Selected `HOME` @ 1.01 -> 🟢 WON (Expected prob: 76.5%)

### 2026-07-18: Cavalry FC vs HFX Wanderers (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🔴 LOST (Expected prob: 65.2%)

### 2026-07-18: Always Ready vs Universitario de Vinto (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.06 -> 🟢 WON (Expected prob: 80.3%)

### 2026-07-15: Universitatea Craiova vs ML Vitebsk (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.74 -> 🟢 WON (Expected prob: 77.4%)

### 2026-07-15: Cuniburo vs El Nacional Quito (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.32 -> 🟢 WON (Expected prob: 71.7%)

### 2026-07-14: Brechin vs Livingston (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.05 -> 🟢 WON (Expected prob: 76.3%)

### 2026-07-14: Dunfermline vs Dumbarton FC (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🟢 WON (Expected prob: 75.0%)

### 2026-07-14: Levski Sofia vs Borac Banja Luka (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.35 -> 🟢 WON (Expected prob: 71.5%)

### 2026-07-14: Brora Rangers vs Aberdeen (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.07 -> 🟢 WON (Expected prob: 70.0%)

### 2026-07-14: Linlithgow Rose vs St Johnstone (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.16 -> 🟢 WON (Expected prob: 66.0%)

### 2026-07-14: Annan Athletic vs Dundee (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.15 -> 🟢 WON (Expected prob: 65.7%)

### 2026-07-13: Honka vs HJS Akatemia (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.21 -> 🔴 LOST (Expected prob: 73.0%)

### 2026-07-12: Gimnasia Jujuy vs Chacarita Juniors (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🔴 LOST (Expected prob: 66.0%)

### 2026-07-12: Fram Reykjavik vs Thor Akureyri (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.31 -> 🟢 WON (Expected prob: 71.3%)

### 2026-07-11: Gnistan vs Mariehamn (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 80.0%)

### 2026-07-11: Guangzhou E-Power vs Hebei Kungfu (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 2.29 -> 🟢 WON (Expected prob: 73.5%)

### 2026-07-11: South Hobart vs Ulverstone (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.02 -> 🟢 WON (Expected prob: 84.5%)

### 2026-07-11: Moreton City Excelsior vs Magic United (Actual Score: **4-3**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🟢 WON (Expected prob: 70.7%)

### 2026-07-11: Shaanxi Union vs Meizhou Kejia (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.49 -> 🟢 WON (Expected prob: 70.0%)

### 2026-07-11: Ansan Greeners vs Suwon Bluewings (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.38 -> 🔴 LOST (Expected prob: 69.0%)

### 2026-07-11: IF Gnistan vs IFK Mariehamn (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.36 -> 🟢 WON (Expected prob: 65.8%)

### 2026-07-11: Canberra FC vs Brindabella Blues (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.02 -> 🟢 WON (Expected prob: 77.7%)

### 2026-07-09: Sheriff Tiraspol vs Aluminij (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.31 -> 🔴 LOST (Expected prob: 74.0%)

### 2026-07-09: Qarabag vs Vestri (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.05 -> 🟢 WON (Expected prob: 74.3%)

### 2026-07-08: Spain U19 vs Croatia U19 (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.34 -> 🟢 WON (Expected prob: 66.0%)

### 2026-07-07: Monaro Panthers vs Queanbeyan City (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.54 -> 🟢 WON (Expected prob: 65.7%)

### 2026-07-07: Tre Fiori vs Larne (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.43 -> 🟢 WON (Expected prob: 74.5%)

### 2026-07-07: Argentina vs Egypt (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 70.8%)

### 2026-07-06: Universidad Catolica vs Mushuc Runa SC (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🔴 LOST (Expected prob: 67.0%)

### 2026-07-05: FAR Rabat vs CR Khemis Zemamra (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🔴 LOST (Expected prob: 70.0%)


## Unmatched result examples

- none

## Ambiguous result examples

- none
