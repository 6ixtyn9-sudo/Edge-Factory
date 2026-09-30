# FRESH PRODUCTION DISPATCH PLAN — run date 2026-10-01

- same-day dispatchable picks: 2
- horizon dispatchable picks: 2
- event dates: 2026-10-01, 2026-10-02
- sync dates: 2026-10-01, 2026-10-02
- notification action: same_day_pick

## Same-day picks

| event date | kickoff | fixture | selection | prob | odds | implied | edge | rule | staking |
|---|---|---|---|---:|---:|---:|---:|---|---|
| 2026-10-01 | 2026-10-01T18:00:00+02:00 | Guinea vs Kenya | home | 0.635 | 1.65 | 0.6061 | +0.0289 | 1x2_two_source_p60_unanimous | handled_by_auto_tickets |
| 2026-10-01 | 2026-10-01T06:10:00Z | Panama vs New Zealand | home | 0.585 | 2.25 | 0.4444 | +0.1403 | 1x2_two_source_p55_unanimous | handled_by_auto_tickets |

## Future-dated horizon picks

| event date | kickoff | fixture | selection | prob | odds | implied | edge | rule | staking |
|---|---|---|---|---:|---:|---:|---:|---|---|
| 2026-10-02 | 2026-10-02T20:45:00+02:00 | Hungary vs Georgia | home | 0.580 | 1.85 | 0.5405 | +0.0392 | 1x2_two_source_p55_unanimous | handled_by_auto_tickets |
| 2026-10-02 | 2026-10-02T20:45:00+02:00 | Belgium vs Turkey | home | 0.720 | 1.45 | 0.6897 | +0.0303 | 1x2_two_source_p70_majority | handled_by_auto_tickets |

Future-dated picks are dispatched under their EVENT date. A run replaces its own run date unconditionally and a future date only when that date appears in this plan, so an empty same-day slate can never delete an already-dispatched future pick.
