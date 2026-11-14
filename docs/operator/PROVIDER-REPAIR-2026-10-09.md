# Provider repair: 9 October run

Scope: provider transport/parser/matching investigation. No model, qualifier,
electorate, price-safety, workflow, notification, ticket or archive-policy edits.
No live requests to providers or credential changes were performed.

## Evidence pinned

- Supplied Actions run: `37933770254`, checkout
  `16f587df3e518168baa0efaf06603efd5ab2560a`.
- Its persisted state commit (resolved through the repository API):
  `89d97b96e0b78241b2bce720e71393f2e3ea97ac`.
- Read that commit's `localdata/source_health_2026-10-09.json`, not a later
  overwritten copy. It confirms the observations below.
- Reports artifact ID `11620621454` exists and was reported unexpired. Download
  failed at the redirected blob-storage host in this environment. Artifact
  contents have **not** been inspected or claimed recovered. Do not store the
  signed download URL in a report.

## Repairs delivered

### Bzzoiro: repeated identical rejected requests

Both prediction and odds transports retried all HTTP errors three times,
including the observed 403. They now return non-transient HTTP 4xx (except 408)
and quota 509 immediately. 408, transient 5xx and network failures retain their
existing bounded retries. This does **not** turn a 403 into success or infer
whether it represents an invalid credential, plan restriction or endpoint
permission. There is no new persistent blacklist or cross-endpoint suppression;
independent permitted endpoints remain usable. Separate requests/processes can
still contact the provider; this is not a global cooldown claim.

### SharpAPI: fabricated empty-board measurements on cache hits

The pinned receipt reports 18 cached rows but a board of zero fixtures/rows and
card overlap 0/24. The cache-hit branch rebuilt default-zero stats rather than
reading the capture's retained board receipt.

Cache hits now preserve recorded board fields where available and report
missing board context as unknown. Prior card-specific measurements are not
reused for a different current card. Source health renders unknown overlap as
`cardunknownofN`, not a measured zero. Cached rows, order, odds and join logic
are unchanged, and reading the cache does not rewrite its bytes. This repairs
the misleading coverage diagnosis, not a demonstrated underlying fixture join.

### PinnAPI: misleading zero diagnosis and sample-induced capture failure

The pinned receipt contains 3,262 events, 3,262 with teams, **zero** with recognized
market containers, and no canonicalization drops. The diagnosis nevertheless
said every price was discarded. A distinct `events_without_market_payload`
reason now identifies that condition without claiming prices cannot exist
elsewhere in an unseen schema. No invented endpoint or mapping was introduced.

Separately, sample trimming attempted `json.loads(text[:20000])` for large
serialized events. A truncated JSON prefix can throw, making otherwise valid
price parsing fail in the diagnostics step. Oversized samples now produce a
small explicit truncation receipt; valid prices remain available. Regression
control exercises a recognized event with a 25,000-character extra field.

## Unresolved provider access/schema evidence

| Source | Confirmed observation | Next evidence needed, not a speculative code patch |
|---|---|---|
| BetBetter | 1,370 cached rows; 634 selection-unmapped, 589 unsupported-market, 80 unmapped-market, 65 out-of-window, 2 fixture-key misses | `betbetter_shadow_2026-10-09.json` from the Reports artifact. If it lacks the upstream selection field, obtain a sanitized original pick object. Do not infer sides from probabilities, team order or prose. |
| PinnAPI | Teams present but no recognized market containers | `pinnapi_odds_shadow_2026-10-09.json`, especially `stats.sample_event` and response shape. Confirm the provider's actual market endpoint/schema before extending parsing. |
| SharpAPI | Cached board receipt was lost; 18 unmatched rows | `sharpapi_odds_shadow_2026-10-09.json` and card rows from the same artifact. Check fixture/date/market overlap before adding aliases; no fuzzy relaxation. |
| BetMiner | Retained probe explicitly says `/matches/2026-10-09` endpoint does not exist | Current endpoint documentation for the subscribed API product or a sanitized successful response. Preserve the one-probe/day cap; no endpoint guessing. |
| Bzzoiro | HTTP 403/auth-or-plan classification | Account-side entitlement/credential verification, kept private. No credential requested in chat. Retry repair does not restore access. |
| OddsPapi | HTTP 429 | Provider quota/Retry-After/reset details. Existing transport already avoids same-key immediate retry for 429 and uses configured sequential key failover. No additional polling or quota bypass. |

Unsupported spread, draw-no-bet, corners, shots and double-chance rows are not
silently relabelled as supported markets. Empty selections remain refused.
Existing fixtures prove some parser contracts, not the unknown current payloads.

## Executed verification

Targeted provider/source-health suite: **297 passed**.

```
.venv/bin/python -m pytest -q tests
6 failed, 2605 passed in 68.34s

git diff --check
(no output)
```

The six failures are exactly the intentional qualifier/electorate contract
assertions in `tests/test_consensus_contract_gaps.py`. No tests were skipped,
xfail-marked or weakened. New controls cover HTTP request counts/no sleeps,
retained transient retries, independent endpoint access, diagnostic secrecy,
cache-byte/row equality, unknown versus zero overlap, missing market containers,
and successful price parsing despite oversized diagnostic samples.

Changes are on the Arena working branch, not deployed to the production branch.
