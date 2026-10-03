# Price-source roles and selection policy

**Decision date:** 2026-10-03 · **Status:** active

This document is the single place that says *what each price source is*. The
code that enforces it is `src/edgefactory/price_sources.py`; everything else
(the pick path, the price board, the ticket builder, source health) reads its
labels from there.

## Why this exists

`bzzoiro_odds` used to be "the primary odds source". It was not primary
because it was the best or the healthiest board — it was primary because
`scripts/picks_today.py` built its bundle first and passed it as the first
argument. When Bzzoiro returned nothing, the price lane degraded even while
other approved sources were healthy.

Source priority is now **data, not call order**.

## Roles

Not everything that returns a number returns a bookmaker price. Three kinds
of number are kept strictly apart, and a fourth source class supplies no
price at all.

| Role | Sources | `odds_kind` | Named book? | May print a ticket price? |
|---|---|---|---|---|
| Named bookmaker / bookmaker-backed | `bzzoiro_odds`, `betexplorer`, `theoddsapi`, `oddspapi_odds`, `pinnapi_odds`, `sharpapi_odds` | `bookmaker` | yes | yes |
| Average-bookmaker price donor | `boggio` | `provider_average` | **no** | yes, while the donor switch is on |
| Model / fair-price donor | `betbetter` | `fair` | **no** | yes, while the donor switch *and* the stakeable switch are on |
| Conditional provider-price donor | `betminer` | `provider_average` / `bookmaker` when provenance is given | no | **no** — evidence only |
| Audit-only price | `scoutingstats_odds` | `provider_average` | no | **no** — quarantined |
| Historical source fallback | `forebet_best` | `provider_average` | no | **no by default** — explicit opt-in only |
| Vote donors | `bzzoiro`, `forebet`, `futbolpronosticos`, tips feeds, … | — | — | **no** |

`predictiq` remains a convergent echo-candidate: zero voice credit, never a
corroborator.

## Role changes made on 2026-10-03 (operator decision)

- **Boggio**: `voice-shadow; average odds provenance only` →
  **approved average-bookmaker price donor**. Its `odds` object is an average
  across books, so it is labelled `average_bookie_aggregate`, it is *never* a
  named bookmaker, and its independence family is `boggio_average`. The
  12-hour free-tier lookahead safeguards are unchanged: `published_at` and
  `captured_at` are both retained and a row published after it was captured is
  marked `timestamp_suspect` and loses price eligibility.
- **Bet Better**: `benchmark-only / never a price donor` → **approved
  fair-price donor**. Its numbers are model fair odds: `odds_kind="fair"`,
  `provider_role="model_fair_price_donor"`, `bookmaker=None`,
  `named_bookmaker=False`, family `betbetter_fair`. They are not executable
  bookmaker quotes and the ticket must say so.

## Selection order

`select_price_source` ranks every approved source *per pick*:

1. source health for the requested date;
2. exact fixture and market match;
3. freshness of the matched quote;
4. execution eligibility;
5. named-book provenance;
6. configured source priority.

A healthy source with a valid exact fixture match beats an unavailable source
whatever its historic priority. Every quote from every source stays in
`price_board`; selection only decides which one is *printed*.

## Independence families

Corroboration is counted over independent **families**, not over API vendors —
two vendors republishing one model number are one piece of evidence:

```
bzzoiro_book
betexplorer_book
sharpapi_book
pinnacle_book
theoddsapi_bookmaker:<book>
oddspapi_bookmaker:<book>
boggio_average
betbetter_fair
betminer_provider
```

## Active policy

> A configured donor may supply a price. Named-book corroboration remains
> preferred but is not required, because the operator has explicitly enabled
> non-bookmaker donors. Every printed leg must disclose the donor type.

| Switch | Default | Effect |
|---|---|---|
| `EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR` | `1` | Boggio (and BetMiner aggregates) may donate prices |
| `EDGE_FACTORY_ENABLE_FAIR_PRICE_DONOR` | `1` | Bet Better may donate fair prices |
| `EDGE_FACTORY_FAIR_PRICE_STAKEABLE` | `1` | Separate switch permitting a fair price to be the *printed* price; evidence remains visible while off |
| `EDGE_FACTORY_REQUIRE_PRICE_CORROBORATION` | `0` | Restores the strict 2026-10-02 Option C gate |
| `EDGE_FACTORY_REQUIRE_NAMED_BOOK_CORROBORATION` | `0` | Only named-book families may corroborate |
| `EDGE_FACTORY_ALLOW_SOURCE_FALLBACK` | `0` | Explicitly opts the registered historical `forebet_best` fallback into execution; default is abstain |

The active policy is printed by `psrc.policy_line()` on every run and with
every abstention. Nothing here is a silent default.

## The gate's three distinct concepts

- **price availability** — does any approved donor quote this leg at all?
- **execution eligibility** (`price_push_eligible`) — may the configured donor
  supply the printed price?
- **corroboration** (`price_corroborated`, `price_corroboration_sufficient`) —
  is a second *independent family* quoting the same market and selection?

The builder still abstains on: fewer than two qualifying legs, no valid donor
price, a stale quote, a future-dated quote, an inexact market/selection match,
a malformed payload, a settled or kicked-off fixture, a suspect/fuzzy price, a
price under the odds floor, or a disabled/unhealthy source. When it abstains it
prints a `PRICE SUPPLY:` breakdown so "no odds" is never confused with "odds
available but rejected by policy".

## Endpoint contracts

| Adapter | Before | After |
|---|---|---|
| BetMiner | `GET /matches/{date}` and an unverified single-date value-bets probe | `GET /value-bets/{dateFrom}/{dateTo}` with same-day range (legacy shape still parsed for cached receipts; 404 ⇒ `reason=http_404_endpoint_contract`) |
| SharpAPI | `GET /odds?date=…` | `GET /api/v1/odds` with required `SHARPAPI_SPORT` plus configurable `limit` / `book` / `market`; `date` only when `SHARPAPI_DATE_PARAM` is set |

Diagnostics carry status-derived reason codes only — never a key, a header or
a request URL.

## Shared donor join vocabulary

Every donor adapter and the final bundle boundary use
`edgefactory.odds_normalization`. Explicit provider aliases become `1x2`,
`btts`, or `ou[_line]`, and 1/X/2 or an exact home/away team token becomes
`home`, `draw`, or `away`. Unmappable market or selection tokens are withheld
from the join and counted as `canonicalization_drop_reasons`; they are never
silently guessed. Source-health receipts also report captured/scored versus
matched rows, so a large ledger with zero overlap is visible.

BetMiner contract discovery is cache/receipt-first: a failed endpoint probe
writes `localdata/betminer_probe_<date>.json` with the endpoint, status,
scrubbed schema sample, and timestamp. A later run on that date reads the
receipt and consumes no further provider calls.
