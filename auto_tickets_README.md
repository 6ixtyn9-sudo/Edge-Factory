# Edge Factory — Auto-Tickets v4 (acca-only)

Discipline by construction: the tool chooses your accas for you, based ONLY on
combos with dynamically computed positive edge. NO singles — ever.
All output is percentages of capital (you do the rand math).

## Structure (operator plan)

- 28% of CAPITAL -> MULTIPLE 2-odd accas (split across 3 tickets, ~9.3% each)
- 10% of CAPITAL -> ONE 10-odd acca
- Total at risk per day = 38% of capital
- No singles. All tickets are accas.

## Install

Place both files in Edge-Factory/scripts/, then:

    cd ~/Edge-Factory
    PYTHONPATH=src python3 scripts/auto_tickets.py --history
    PYTHONPATH=src python3 scripts/auto_tickets.py
    PYTHONPATH=src python3 scripts/auto_tickets_grade.py

Run in that order after each daily.py run. The grader re-runs every day.

## Selection (dynamic, positive-ROI buckets only)

1. Every archived pick is joined with settled_results.json -> win/loss.
2. Edge is aggregated per (edge rule x odds source): n, hit, ROI, Wilson LB,
   plus a RECENT-window ROI (last 20 settled).
3. A combo PASSES when: n>=15, ROI>=+3%, Wilson LB>=0.68, recent ROI>=0.
   Combos enter and leave automatically as history matures or decays.
4. Today's slate is filtered: passing combo, bucket in
   CERTIFIED_CLEAN + SKIPPED_VETO (handover: SKIPPED_VETO 86.5% hit / +11.8% ROI;
   CAUTION negative -> excluded), trusted price only (BZZOIRO_PRIMARY /
   BETEXPLORER_RESCUE; scoutingstats -33% -> excluded), kickoff still ahead.
   There is NO per-pick model-edge floor: the combo pass is the edge test
   (short-odds legs like Porto @1.21 carry the edge even though their per-pick
   model edge is near zero).

## Ticket construction

- 2-ODD ACCAS: pair qualifying picks (smallest odds x largest odds) so each pair
  lands as close to 2.00 as possible. Up to 3 pairs.
- 10-ODD ACCA: ALL qualifying picks (reuse across ticket types is allowed - each
  ticket is an independent bet). Fewest legs to reach ~10.0, capped at 9 legs.
- No pick appears twice within a single ticket.

## Safety rails

- 09:00 GATE: tickets are NEVER generated before 09:00 local. Runs before that
  print "NOT YET - TICKETS GENERATE AT 09:00" and place nothing.
- FROZEN once generated: the 09:00 run writes the slip; all later runs (12:00,
  15:00, 18:00, ... 8x/day) re-print it unchanged. Use --force to regenerate.

- Drawdown guard: last 20 graded tickets ROI < -10% -> RED ALERT, --force overrides.
- Recency gate on combos (recent-20 ROI >= 0).
- The grader only grades tickets the tool generated. Manual slips are outside
  the loop - bet only what auto_tickets.py prints.
- Round each ticket UP to your bookmaker's minimum stake.

## Example output

    AT RISK: 38% of capital  (2-odds accas 28% + 10-odds acca 10%)

    [2-ODD ACCA #1] total 1.96, stake 9.3% of capital
       Porto vs Alverca      HOME @ 1.21
       Lech Poznan vs Piast  HOME @ 1.62

    [2-ODD ACCA #2] total 2.05, stake 9.3% of capital
    [2-ODD ACCA #3] total 2.04, stake 9.3% of capital

    [10-ODD ACCA] 7 leg(s), total 10.78, stake 10.0% of capital

If nothing qualifies: NO EDGE TODAY - DO NOT BET.

## Options

    --history   show the dynamic edge table and exit
    --force     override the drawdown pause
    --date YYYY-MM-DD   run for a specific date (default today)

## Disclaimer

A documented edge is not a guarantee. This is gambling. Bet only what you can
afford to lose. National Responsible Gambling line (ZA): 0800 006 008.
