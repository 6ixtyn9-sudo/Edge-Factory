# Operator handbook — single entry point

Everything an operator needs for the production lane starts here. Nothing in
this tree was deleted during consolidation (OP-01 T3): deep-evidence documents
moved to [`archive/`](archive/) and are linked below.

Standing constraints (unchanged by any document here): no proxies / stealth /
CAPTCHA bypass; `EDGE_FACTORY_FOREBET_BROWSER=off`; `scripts/auto_tickets.py`
is the sole owner of tickets and staking; abstention is valid; **single
production lane** (no dual production); no `edge >= 0` hard gate; no
production re-mine without explicit operator promotion; gap-only mining
(never refetch what we hold, existing rows win collisions, independent
settlement, raw + checksum + provenance per crawl). The GitHub App cannot push
`.github/workflows/` — workflow changes ship as paste-ready docs only.

Latest reviewed decisions:
[`DECISIONS-2026-10-09.md`](DECISIONS-2026-10-09.md) transfers D1–D5 with
snapshot-bound evidence, corrected archive/price/provenance claims, the
test-first Authorization repair, and explicit unresolved/deployment boundaries.

**Decision-record identity:** this repository's record is the **Edge-Factory
transferred/re-reviewed D1–D5 record**, not the other workspace's independently
written document with the same filename. Its existing §1 states that distinction.
Use [the pinned repository record](https://github.com/6ixtyn9-sudo/Edge-Factory/blob/01f580c1f41b78883d7c807e354ba76903bbd026/docs/operator/DECISIONS-2026-10-09.md)
as the local D1–D5 reference for this proposal, within its explicit scope and
operator-approval limits. Filename equality is not document identity.

The latest supplied follow-up identifies a separate, local-only record at
`e489654` and reports a D1–D7 scheme. That record has not been retrieved or
verified here; it is **not an interchangeable repository authority**. No D6/D7
numbering or dispositions are adopted by this handbook: this repository records
the Authorization work under D4 and Kladno under D5. References across workspaces
must include repository/workspace, full revision when available, path, section
and preferably content hash. Importing or reconciling the external record needs
the actual document and an explicit decision; no source text is silently replaced.

Open review proposal (documentation only; not approved for production):
[`PROPOSAL-ML-CONSENSUS-PROVENANCE-2026-10-09.md`](PROPOSAL-ML-CONSENSUS-PROVENANCE-2026-10-09.md)
revision 4 incorporates [two independent reviews](REVIEW-SYNTHESIS-ML-CONSENSUS-2026-10-09.md)
and requires sidecar-only provenance, distinct signal identities, and parity
verification before any live routing, electorate, or representative change.
The [acceptance checklist](CHECKLIST-ML-CONSENSUS-PROVENANCE-2026-10-09.md)
separates conditional design approval from implementation and activation evidence.

---

## 1. Daily card ops

| phase | what happens | artifact |
|---|---|---|
| build window opens | `auto_tickets.py --today` starts building at `GENERATE_HOUR_START`; earlier runs print `NOT YET` | stdout |
| draft | every run before the freeze hour regenerates the card | `localdata/auto_tickets_<date>.txt`, status line `⏳ DRAFT` |
| freeze | the first run at/after `FREEZE_HOUR` on the card's own date locks the date **write-once** | slip footer + `frozen_by_date` entry |
| frozen rerun | later runs re-print the saved slip byte-for-byte and re-upsert evidence only | same slip, unchanged |
| settle | open slips settle independently against warehouse score facts | `auto_tickets_state.json`, `auto_tickets_performance.txt` |

### The FROZEN footer

A frozen slip ends with exactly one line:

```
FROZEN AT HH:MM - FINAL
```

That footer is the human-readable half of the lock. The machine half is a
**write-once** entry inside the committed ticket state:

```jsonc
// localdata/auto_tickets_state.json
"frozen_by_date": {
  "2026-10-02": { "frozen_at": "2026-10-02T12:03:41+02:00",
                  "final": true, "lock_source": "state" }
}
```

Rules, enforced by `tests/test_ticket_freeze_lock.py`:

- **Write-once.** Once a date is in `frozen_by_date` it can never be rewritten
  — not by a later run, not by `--force`. `--force` may rebuild the card, but
  the lock and its timestamp are immutable.
- **Co-located with the state persist.** The lock is written in the *same*
  `save_state` call that persists the slip, so a card can never be staked for
  a date whose lock lands later (or not at all).
- **Legacy compat.** Pre-2026-10-02 per-day sidecars
  (`localdata/auto_tickets_<date>.frozen`) still lock their date on read and
  their timestamp is adopted, not re-minted. **They are never deleted, and no
  new ones are created.**
- If the footer is missing, the card is a draft. Do not place a draft.

**Operator reading of the lock:** the slip you hold is the bet. If a later run
ever prints a different card for a frozen date, that is an incident — the
write-once lock exists because a rotating "frozen" card put placed bets at
risk in the experiment lane (see §3).

### Abstention validity

**A no-bet day is a valid, successful outcome.** `NO BET TODAY — n qualifying
leg(s), need k` and `insufficient_voter_quorum` are results, not failures.
Nothing may be relaxed — not price corroboration, not the kickoff guard, not
the quorum — to manufacture a card. Bank stays unbet; the day is recorded.

---

## 2. Source-health legend

The same vocabulary is used across
[`HISTORY-SOURCES.md`](HISTORY-SOURCES.md),
[`CANDIDATE-SOURCES.md`](CANDIDATE-SOURCES.md) and the audit scripts.

**Availability (`scripts/audit_source_availability.py`, coverage inventory):**

| term | meaning |
|---|---|
| `committed` | rows exist in committed capture files; auditable and gradeable in-repo |
| `cache-only` | rows exist only in the runner cache; one cold cache from gone |
| `absent` | no rows in-repo for this source |
| `alias/cache` | a view over another source, not an independent voice |
| `internal gap` | a missing day *inside* an otherwise covered range — the only legal crawl candidate |
| `stale since <date>` | fetch layer may be healthy, but persistence stopped at that date |

**Verification class (source triage / candidates):**

| term | meaning |
|---|---|
| `VERIFIED-from-relay` | robots + fetch receipt obtained through the sandbox relay |
| `UNVERIFIED` | no current receipt; prior sample only. Never production-eligible |
| `forward-only` | no proven dated archive; capture from today onward only |
| `mineable-backfill candidate` | dated archive proven; still needs explicit operator promotion |
| `shadow` / `zero weight` | runs and is logged, contributes **no** consensus vote weight |
| `reject` | robots opt-out, non-cooperative, or unprovable settlement |

**Live health signals:**

| signal | meaning | operator action |
|---|---|---|
| `http=403 auth/plan-denied` | the account/plan cannot see this endpoint | do not retry harder; see the bzzoiro ticket in §5 |
| `429` / `Retry-After` | politeness backoff engaged; single-flight + throttle in force | none; the runner cools off and exits zero |
| `challenge` / source-freeze receipt | a crawl wrote a freeze receipt and stopped | none automatic; no alternate transport is permitted |
| `zero-row done` | a day terminated with zero rows | only legitimate when the day was genuinely empty — not when it was a 403 |
| tripwire fired | an expected signal stopped firing | read the diagnostics artifact before changing anything |

**Health-line role verdicts (T0):** the compact
`Source health <date>: …` line judges each source against **its own role**, not
an all-three check. `bzzoiro` is healthy at `fetch/vote` (it never prices);
`bzzoiro_odds` and `betexplorer` are healthy at `fetch/price` (they never
vote); full sources like `scoutingstats` still need `fetch/price/vote`. A
source whose fetch or role capability fails prints `BLOCKED`. Shadow zero-row
counters append a deterministic reason suffix, e.g.
`betminer=bm_raw0/bm_scored0(auth403)` or
`pinnapi=pa_raw0/pa_matched0(http400)` and
`boggio=bg_raw0/bg_scored0(auth403)`; success and `not_run` are unsuffixed.
The verdict is display-only: the per-day health contract in
`source_health_YYYY-MM-DD.json` remains the authoritative record.

**Price evidence / quarantine buckets seen on legs:** `CERTIFIED_CLEAN`,
`CAUTION`, `WATCHLIST_UNCORROBORATED_PRICE`, `WATCHLIST_UNKNOWN_CTX`,
`SKIPPED_VETO`, `BETEXPLORER_RESCUE`, `SOURCE_FALLBACK`,
`SCOUTINGSTATS_SOLE`. The 7% price-corroboration gate (PR #20) is what keeps
the last three off production cards; the evidence for not adding an
`edge >= 0` gate is in
[`archive/EDGE-GATE-EVIDENCE.md`](archive/EDGE-GATE-EVIDENCE.md).

---

## 3. Experiments archive

| experiment | lane | verdict | record |
|---|---|---|---|
| 01 — ungated lane vs protected main | `arena/01a0f2b3-edge-factory` (PR #18, CLOSED) | **NOT PROVEN** on bet quality, **NEGATIVE** on operational safety | [`EXPERIMENT-01-LANE-CLOSEOUT.md`](EXPERIMENT-01-LANE-CLOSEOUT.md) |

Experiment 01 in one line: +77.8 bank points on +2.8 points of hit rate, with
51% of in-season ridden legs priced off a single unconfirmed source, a frozen
card that could rotate under placed bets, a ghost leg in a frozen ACCA, and
21.1% of capital staked a day early on a card that could never freeze. Its one
transferable finding — freeze durability — is banked as the write-once lock in
§1. Branch sha for operator deletion is in the closeout.

Deep evidence retained in [`archive/`](archive/):

- [`archive/EDGE-GATE-EVIDENCE.md`](archive/EDGE-GATE-EVIDENCE.md) — edge-gate
  accounting and options; **no gate applied**.
- [`archive/SOURCE-TRIAGE.md`](archive/SOURCE-TRIAGE.md) — committed-capture
  audit TR-1…TR-4, independence matrix, new-source yardstick.
- [`archive/SPORTYTRADER-SHADOW-BUILD.md`](archive/SPORTYTRADER-SHADOW-BUILD.md)
  and [`archive/SPORTYTRADER-7PCT-REPORT.json`](archive/SPORTYTRADER-7PCT-REPORT.json)
  — shadow corroborator build and its offline 7% evidence report.
- [`archive/PR15-RED-TEAM.md`](archive/PR15-RED-TEAM.md) — PR #15 red-team pass.
- [`archive/WO-8-PINNAPI-2026-10-06.md`](archive/WO-8-PINNAPI-2026-10-06.md) —
  WO-8 Pinnacle relay request contract (CLOSED): outcome, the brief as issued,
  and what stays unverified until a live run.
- [`DATED-CLAIMS.md`](DATED-CLAIMS.md) — live ledger: every dated claim in a
  code comment names what backs it, enforced by `tests/test_dated_claims_ledger.py`.
- `../../HANDOVER.md` — the append-only repo-wide anti-drift log. It stays at
  the repository root on purpose: ~10 source files, `README.md` and the daily
  pipeline reference it by that path, so moving it would rot live references.
  Treat it as the long-form archive behind every document here.

---

## 4. Source program

- [`HISTORY-SOURCES.md`](HISTORY-SOURCES.md) — history-source hunt, decision
  rules (vote archive vs price archive), per-source archive-crawl plans.
- [`CANDIDATE-SOURCES.md`](CANDIDATE-SOURCES.md) — candidate ladder, locale /
  one-publisher rules, shadow-first policy.
- [`REMINE-PLAN.md`](REMINE-PLAN.md) — coverage inventory (B0) and the bounded
  backfill state machine (B1): ≤10 BetExplorer gap requests per run,
  `gap_fill_complete` → Football-Data proof → Legalbet sample. Ledger:
  `localdata/backfill_ledger.jsonl`. Hist namespaces only; zero vote-weight
  change. Regenerate the inventory with
  `python3 scripts/coverage_inventory.py --append-plan docs/operator/REMINE-PLAN.md`.
- [`PRICE-SOURCE-ROLES.md`](PRICE-SOURCE-ROLES.md) — the authoritative source
  role table (named book / average-bookmaker donor / fair-price donor / vote
  donor), the health-aware selection order that replaced the hard-coded
  Bzzoiro-first path, independence families, the active donor policy and its
  switches, and the repaired BetMiner and SharpAPI endpoint contracts.
- [`JOIN-REPAIR-2026-10-03.md`](JOIN-REPAIR-2026-10-03.md) — why every donor
  lane scored 0 matched on 2026-10-03 and what was repaired: the shared
  canonicaliser's `mapped`/`unsupported`/`unknown` outcomes, Boggio's silent
  drop, OddsPAPI's teamless `/odds` rows (all 414 mislabelled `1x2/home`),
  `date_mismatch` vs `out_of_window`, the per-source (NOT systematic) kickoff
  display offset census, and the deterministic zero-row reason tokens.
- [`JOIN-REPAIR-ROUND-2.md`](JOIN-REPAIR-ROUND-2.md) — round 2: the OddsPAPI
  `schema_version` generation marker that invalidates the 414 rows written by
  the superseded parser (counted as `stale_schema`, never deleted); proof the
  Bet Better vocabulary census works and why the 687 tokens still need a live
  run; the statarea (UTC−5/−7) and zulubet (UTC+1) renderers behind the
  kickoff offset families; and the two already-played fixtures the pre-match
  lead guard admitted on 2026-10-03, now clamped one-directionally.
- [`SOURCE-HUNT-2026-10.md`](SOURCE-HUNT-2026-10.md) — HUNT-01 exhaustive
  hunt for free prediction/odds APIs ("like bzzoiro"): search log, 25-candidate
  inventory, A–H scorecards, shortlist of 3 (**Betminer** voice winner /
  PredictIQ echo-test / pinnapi Pinnacle prices) and operator probe plans.
  Seed finding resolved against API-Football: free-plan seasons lag current
  (2022–2024), so it is backfill-only. Shortlist draft tickets (c)–(e) are in
  [`TICKETS-OPEN.md`](TICKETS-OPEN.md).
- Runner: `scripts/remine_backfill.py`, invoked by `scripts/daily.py`. Sandbox
  crawling is closed; the Actions runner is the only place bounded requests
  may be made.

Proposed workflow artifacts (paste-ready, never pushed by the App):
[`daily.yml.proposed`](daily.yml.proposed),
[`forebet-browser-diagnostic.yml.proposed`](forebet-browser-diagnostic.yml.proposed),
[`daily-freeze-marker.patch`](daily-freeze-marker.patch),
[`enable-manual-dispatch.patch`](enable-manual-dispatch.patch).

---

## 5. OPERATOR ACTIONS checklist

| # | action | status | detail |
|---|---|---|---|
| 1 | Apply [`daily-freeze-marker.patch`](daily-freeze-marker.patch) to the deployed `.github/workflows/daily.yml` | **PENDING** | Exempts the freeze-marker family from `git clean -fd localdata/`. Still pending as directed. Note: with the OP-01 T2 write-once lock, the authoritative lock now lives in the already-committed `auto_tickets_state.json`, so this patch protects legacy sidecars only — its urgency is reduced, not its status. Apply with `git apply --unidiff-zero`. |
| 2 | Enable manual dispatch ([`enable-manual-dispatch.patch`](enable-manual-dispatch.patch)) | **NOT NEEDED** | The checked-in `daily.yml` already declares `workflow_dispatch` with its mode inputs. Applying it to a file that already has the key creates a duplicate YAML key. Retained only for an older deployed copy; validate first with `git apply --check`. |
| 3 | Glance at the bzzoiro diagnostics dashboard after the next run | **PENDING** | PR #21 shipped bzzoiro diagnostics + tripwire. The tripwire currently reports `http=403` auth/plan-denied on 2026-10-02 and 2026-10-03 while the tips feed works — confirm whether the odds plan is actually entitled. Ticket: §5a below. |
| 4 | Decide on deleting the closed experiment lane branch | **OPERATOR** | Branch + sha in [`EXPERIMENT-01-LANE-CLOSEOUT.md`](EXPERIMENT-01-LANE-CLOSEOUT.md). This repo never modifies or dispatches that branch. |
| 5 | Promote (or decline) any production re-mine | **OPERATOR** | Required before any crawl beyond the bounded backfill already approved. |

### 5a. Open small tickets

- **bzzoiro_odds zero-row-done redo** — days whose terminal state was a
  403/auth-zero must be retried on later runs instead of being treated as
  done. See [`TICKETS-OPEN.md`](TICKETS-OPEN.md).
- **soccervista restore-or-drop** — all transports including the relay fail;
  recommendation and evidence in [`TICKETS-OPEN.md`](TICKETS-OPEN.md).
  No code change shipped.
- **HUNT-01 shortlist drafts (c)–(e)** — Betminer shadow voice, PredictIQ
  echo-test voice, pinnapi Pinnacle price corroborator: operator registers
  free key → probe → shadow (zero credit) → echo test → promotion only on
  settled evidence. See [`TICKETS-OPEN.md`](TICKETS-OPEN.md) and
  [`SOURCE-HUNT-2026-10.md`](SOURCE-HUNT-2026-10.md).
- **SHADOW-01 shipped (c), (e) + tagged (d)** — Betminer (voice shadow,
  never a price donor: its odds carry no bookmaker identity), pinnapi_odds
  (Pinnacle price shadow, corroboration default-off, same-day-only gate)
  and keyless Bet Better (CC BY 4.0 benchmark board) now capture zero-credit
  per-date ledgers in the nightly shadow lane; PredictIQ is
  convergent-tagged at the registry level (`predictiq=echo/only`, zero
  voice credit permanently). Keys are env-only
  (`RAPIDAPI_KEY`/`PINNAPI_KEY` — see
  `docs/operator/patches/daily-rapidapi-env.patch`); promotion requires the
  echo/7%-gate evidence in tickets (f)/(g). See
  [`SOURCE-HUNT-2026-10.md`](SOURCE-HUNT-2026-10.md) §10 for receipts and
  the operator runbook.

---

## 6. Guardrails on this handbook

`tests/test_docs_links.py` walks every relative Markdown link in `README.md`,
`docs/**` and this file and fails if a target does not exist. Links here
cannot rot silently; move a document and the suite tells you.

### Gate A specification — pending approval

The [Gate A schema/storage draft](GATE-A-ML-CONSENSUS-SCHEMA-STORAGE-2026-10-09.md)
is now draft 3. A1–A3 have renewed technical design approval; A4 separates
always-ignored detailed manifests from atomically admitted compact-index publication
and adopts refusal-only unexported retention. Steward/export resources remain
unassigned/unprovisioned; close must mark such builds non-replayable. The
[attributed review reconciliation](GATE-A-REVIEW-DISPOSITION-2026-10-09.md) keeps
S1/S2 verdicts and verification scopes separate; A4 review and explicit operator
authorization are required before coding. A durable
index is not durable bulk evidence. No hooks, ignore/workflow edits, implementation
tests, replay or activation were performed.
