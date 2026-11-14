# Price-source operator checklist

Updated 2026-10-03. Nothing in this checklist is enabled by code defaults.
Do not paste secret values into logs, issues, fixtures, or commits.

## SharpAPI (RapidAPI)

The provider's `GET /api/v1/sports` contract identifies soccer as exactly
`id="soccer"`. Verify on the subscribed plan with:

```bash
PYTHONPATH=src python3 scripts/probe_sharpapi.py --discover-sport
```

The probe prints `observed_soccer_id=soccer` and
`soccer_id_confirmed=True`; it never prints the key. With no key it is inert.

Operator actions:

1. Add/confirm the repository secret **`RAPIDAPI_KEY`** (shared RapidAPI
   credential already referenced by `daily.yml`).
2. Add repository secret **`SHARPAPI_SPORT`** with value `soccer`.
3. Manually expose it in the workflow job environment as
   `SHARPAPI_SPORT: ${{ secrets.SHARPAPI_SPORT }}`. The agent deliberately did
   not edit `.github/workflows/*`; adding a repository secret alone does not
   inject it into a job.
4. Leave `SHARPAPI_DATE_PARAM` unset until the vendor documents a date filter.

Expected health change: the token
`sharpapi=sa_raw0/sa_matched0[reason=missing_sport_filter]/sa_scored0`
loses `missing_sport_filter`. A covered slate reports honest non-zero
`sa_raw`/`sa_scored` and possibly `sa_matched`; a valid uncovered slate may
remain zero but must report `provider_empty_slate`, not a fabricated match.

## OddsPAPI

Operator actions:

1. Add repository secret **`ODDSPAPI_API_KEYS`** as the comma-separated key
   ring.
2. Add repository secret **`EDGE_FACTORY_ODDSPAPI_PRICES`** with value `1` to
   opt in. The workflow default is deliberately `off`.
3. Leave **`ODDSPAPI_MAX_FIXTURES`** at `20` for now. The 2026-10-04 log showed
   `slate_priority_fixtures=6` out of roughly 24 priceable slate fixtures, so
   the next lever is exact slate/provider fixture-overlap repair, not spending
   20 extra requests on provider-order leftovers. The existing workflow already
   maps all three names.

Expected health change: `oddspapi=raw0/usable0/matched0` becomes
`oddspapi=rawN/usableU/matchedM` when the provider covers the bounded slate.
`U` can be lower than `N` after timestamp/schema validation and `M` can
honestly be zero when no canonical fixture joins. Do not loosen matching to
inflate it.

## BetMiner quota note

No repository-secret change is needed beyond `RAPIDAPI_KEY`. The documented
V3 board is one `GET /matches/{date}` call. `scripts/probe_betminer.py` makes
at most one call per day, writes `localdata/betminer_probe_YYYY-MM-DD.json`,
and reuses that receipt on later invocations. The 2026-10-03 repair consumed
**0 live provider calls** in this checkout; contract verification used vendor
documentation and the existing captured Match Object fixture.
