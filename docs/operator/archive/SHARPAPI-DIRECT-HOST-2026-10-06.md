# SharpAPI — repointed from the marketplace relay to the vendor's own host

> **Status: code change complete, live behaviour UNVERIFIED.** The sandbox has
> no network, so every claim below is either (a) read off a response the
> operator captured in the vendor playground and pasted in, or (b) proved
> against a mocked payload. Nothing here was observed from a pipeline run.
> One required step is **not** done and cannot be done from here: the
> workflow still pins the wrong endpoint. See "What still has to happen".

## What was wrong — three bugs, stacked

The adapter had never returned a usable row. Each fix alone would have
changed nothing, which is why the earlier single-cause repairs appeared to
fail and kept pointing at the credential.

1. **Wrong host and wrong auth model.** Requests went to the RapidAPI
   marketplace relay `sharpapi1.p.rapidapi.com` carrying two credentials, on
   the theory that the gateway checks one and SharpAPI's origin checks the
   other. That theory was built on real evidence — the 401 carried SharpAPI's
   own `{"error":{"code":"disabled_api_key"}}` envelope rather than the
   gateway's `Endpoint ... does not exist`. The inference drawn from it was
   wrong. The operator's account is a **direct** account that was never a
   marketplace account, so the relay was always going to refuse it.

2. **Wrong endpoint, injected by the deployment.** The adapter's default was
   corrected to `/api/v1/odds` on 2026-10-03, but the workflow sets
   `SHARPAPI_ENDPOINT` to `/odds` — a gateway-relative path — which silently
   overrode the correction. The repair never reached production and nothing
   in the diagnostics said so.

3. **Wrong parser.** The parser only accepted a nested
   `event → bookmakers → markets` structure. The vendor sends a **flat board:
   one record per selection**. Even a perfectly authenticated request to the
   right path would have produced zero rows and reported
   `schema_unrecognized`.

## The contract, as captured

    GET https://api.sharpapi.io/api/v1/odds?sport=soccer
    X-API-Key: <SHARPAPI_KEY>

Captured soccer response, 2026-10-06 ~15:20Z, free tier: 200 OK, 50 rows,
`has_more: true`, cursor pagination, 12 requests/minute.

| | before | after |
|---|---|---|
| host | `sharpapi1.p.rapidapi.com` | `api.sharpapi.io` |
| headers | `X-RapidAPI-Key`, `X-RapidAPI-Host`, `X-API-Key` | `X-API-Key` only |
| credential | `RAPIDAPI_KEY` + `SHARPAPI_KEY` | `SHARPAPI_KEY` alone |
| endpoint (effective) | `/odds` | `/api/v1/odds` |
| accepted payload | nested books | flat rows (nested still accepted) |
| live prices | would have been kept | refused and counted |

## Why this source is worth the trouble — observed

The previous shadow vendor failed because it spoke a US two-way vocabulary
with no draw. SharpAPI does not have that problem:

- `moneyline` carries a real `draw` row (`selection_type: "draw"`). Genuine
  1X2.
- `total_goals` carries a numeric `line` with main/alternate flags.
- The board includes `uefa_-_nations_league` — which was the **largest single
  league on the 2026-10-06 card, 5 of 14 picks**, re-derived from the picks
  file rather than recalled.

Both markets map cleanly through the shared normalizer with no new
vocabulary: `moneyline` → `1x2`, `total_goals` → `ou_<line>`. Everything else
the vendor sends (`double_chance`, `draw_no_bet`, `correct_score`,
`team_total_*`, `anytime_goal_scorer`) drops as unsupported, which is correct
behaviour and not a defect.

## Three traps, all observed in the captured page

1. **The event identifier does not encode home and away.** One row has
   `..._kazakhstan_moldova_...` with `home_team: "Moldova U21"`; another has
   `..._faroeislands_kazakhstan_...` with `home_team: "Kazakhstan"`. Two
   contradicting examples in a single 50-row page. Keying a fixture off the
   slug would invert sides for an unknowable subset — and **an inverted side
   prices perfectly**, so nothing downstream would flag it. Sides are taken
   only from the declared fields.

2. **Every row in the sample was in-play.** The capture ran after kickoff. An
   in-play price is not a worse prematch price, it is a different quantity,
   and it would corrupt any closing-line measurement. Live, stale-pregame and
   player-prop rows are now refused and counted by reason.

3. **The same competition appears under two different league ids across
   books** (`euro_quals_-_u21_championship` vs `uefa_u21_euro_qualifiers`).
   League cannot be matched as a raw string. **Not fixed here** — see tickets.

## Zero rows now has three distinguishable causes

A bare zero is useless, and these prescribe opposite actions:

| recorded reason | meaning | what to do |
|---|---|---|
| `provider_empty_slate` | board recognised, nothing on it | come back later |
| `all_rows_live_or_stale` | board full, capture ran too late | move the capture earlier |
| `all_rows_unmappable` | market vocabulary moved | fix the mapping |
| `schema_unrecognized` | payload shape not recognised | fix the parser |

`prematch_dropped` and `prematch_drop_reasons` carry the counts. The
effective endpoint is recorded too, so bug 2 would now show as data.

## What still has to happen

1. **Apply the workflow change — this is blocking.** Agent sessions cannot
   push `.github/workflows/`. The corrected file is committed at
   `docs/operator/proposed-daily.yml` (valid YAML, verified). Copy it over
   `.github/workflows/daily.yml`. Until then production still calls `/odds`
   on the new host and will 404. The only functional change is
   `SHARPAPI_ENDPOINT` → `/api/v1/odds`, plus an optional `SHARPAPI_LEAGUE`
   passthrough; the rest is comment correction.
2. **Rotate the SharpAPI key.** It was exposed in plaintext chat earlier.
   This is not a repository-history incident — no rewrite, no force-push —
   but the credential is burned.
3. **Read the recorded reason first on the first real run**, before anything
   else. It is a four-way discriminator and it tells you which of the three
   bugs, if any, is still live.

## Scope of this verification

Forty-two tests cover this adapter, all passing, including negative controls:
each new guard was deliberately broken, watched to fail, and restored
(slug-derived sides → 2 failures; live filter removed → 3; gateway headers
reintroduced → 1; zero-row reasons collapsed → 1).

This is **clean for the shapes we know**. The captured page is 50 rows from
one sport at one moment, entirely in-play, from two books. It is strong
evidence about the response shape and no evidence at all about prematch
coverage, which is the number that actually decides whether this vendor is
worth keeping. Nobody has yet seen a single prematch row from this source.
