# Shadow candidates — 2026-09-30 (NON-DISPATCH)

dispatchable: **False**. Shadow evaluation only. These rows are NEVER dispatched, never become CLEAN/CAUTION picks, and are not read by the pick engine. Promotion requires settlement-coverage evidence plus operator sign-off.

- live voter sources: forebet, zulubet, statarea, vitibet, betclan, bzzoiro
- shadow voter sources today: predictz, windrawwin, freesupertips, afootballreport, prosoccer, soccervista
- shadow candidate fixtures: **5**

Blockers:

- inside_30m_lead_or_started: 4
- no_ml_feature_provider_on_fixture: 2
- shadow_sources_not_settlement_validated: 5

| fixture | live voters | shadow voters | kickoff | blockers |
|---|---|---|---|---|
| Bahrain vs Yemen | zulubet,betclan | prosoccer | 2026-09-30T19:30:00+02:00 | inside_30m_lead_or_started; shadow_sources_not_settlement_validated:prosoccer |
| Eastleigh vs Southend | zulubet,vitibet,betclan | prosoccer | 2026-09-30T20:45:00+02:00 | shadow_sources_not_settlement_validated:prosoccer |
| Lithuania vs Andorra | zulubet,statarea,betclan,bzzoiro | prosoccer | 09:00 | inside_30m_lead_or_started; shadow_sources_not_settlement_validated:prosoccer |
| Mexico vs Peru | betclan,bzzoiro | prosoccer | 2026-09-30T01:00:00Z | no_ml_feature_provider_on_fixture; inside_30m_lead_or_started; shadow_sources_not_settlement_validated:prosoccer |
| Seychelles vs Sri Lanka | betclan,bzzoiro | prosoccer | 2026-09-30T13:00:00Z | no_ml_feature_provider_on_fixture; inside_30m_lead_or_started; shadow_sources_not_settlement_validated:prosoccer |

These rows are evidence only. They are never dispatched and the pick engine does not read this file.
