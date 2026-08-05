# Phase 1/2 — Veto re-mine resolution layer (design + implementation spec)

Date: 2026-08-05 · Status: **implementation-ready spec, pending operator
sign-off**. Phase 0 (counterfactual harness) validated on both machines with
identical output. **Correction (same day, found while building the module):**
3 of the 20 WATCHLIST_UNKNOWN_CTX picks were short-sniper niche-UNKNOWN
blocks (league already resolved — OUT of the league overlay's scope). The
honest league-overlay counterfactual is: **17 in-scope picks, 17/17 resolved
(2 O1-pool, 15 O2), green-light 1 pick (unsettled, n/a), caution-grade 16
would-play / 15 settled / 13 wins / 86.7% / +0.042** (30-day slice: 15/15
settled / 13 wins / +0.042). The 3 out-of-scope picks all won (+0.167) — a
separate short-sniper niche policy question, NOT the league overlay. This
spec turns the locked parameters into a flag-gated-off overlay — no live
behavior change until the ≥30-settled gate passes.

## 1. Objective

Resolve `UNKNOWN` purity verdicts at pick time via the locked O1/O2 rules, as
a **read-only overlay** that never mutates `purity_registry.json` (Q5), is
OFF by default, and is trivially reversible.

## 2. Locked parameters (from design doc sections 8 + 10)

- **Pool key:** `(sport, league_key, market, side_role)` — rules pooled within
  the league dimension; n-weighted unconditional w_roi (Q2).
- **Gates (Scenario B):** ALLOW n≥40, CAUTION n≥20, VETO n≥12 (Q3).
- **O2 ladder:** league (pooled) → niche → competition_type (Q1).
- **Verdict semantics:** ALLOW/BOOST = green-light (played); CAUTION =
  caution-grade (played by the live pipeline); VETO = blocked; UNKNOWN =
  unchanged (watchlist/skip).
- **Overlay-only:** registry never rewritten; `assay_purity.py` untouched.
- **Measurement window:** all available settled results (2026-05-07 → now);
  operator slice 30 days (Q4).

## 3. New module: `src/edgefactory/veto_resolution.py`

Pure, stdlib-only, no side effects — mirroring `debias.py`'s testability.

```python
"""Veto re-mine resolution overlay (Phase 1/2). Read-only. OFF by default."""

# --- constants ---
ALLOW_MIN_N = 40
CAUTION_MIN_N = 20
VETO_MIN_N = 12
PLAYABLE = {"ALLOW", "BOOST"}
RESOLVED = {"ALLOW", "BOOST", "CAUTION", "VETO"}
ENV_FLAG = "EDGE_FACTORY_VETO_RESOLUTION"   # == "1" activates

# --- pool table (canonical, deterministic) ---
def build_pool_table(contexts: dict) -> dict[tuple[str, str, str, str], dict]:
    """(sport, league, market, side_role) -> {n, w_roi, verdict} from the
    league dimension. w_roi = n-weighted mean over priced cells; verdict per
    Scenario B gates."""

def pooled_verdict(n: int, w_roi: float | None) -> str:
    """Scenario B: ALLOW>=40, CAUTION>=20, VETO>=12 (mirrors
    context_verdict_league; recent_roi=None -> conservative VETO branch)."""

# --- O2 fallback ---
def o2_verdict(contexts: dict, ctx: dict, market: str, rule: str, sport: str
               ) -> tuple[str, str]:
    """niche -> competition_type. Returns (verdict, path). Key shapes:
    niche:      sport|league|market|rule|odds_band|side_role
    comp_type:  sport|market|rule|comp_type_name
    Only non-UNKNOWN verdicts resolve; VETO never downgraded."""

# --- resolution entry ---
def resolve_pick_verdict(contexts: dict, pick: dict) -> dict:
    """Returns {verdict, path, pool_n, pool_w_roi, reason} for one pick.
    O1 first (pooled league), then O2 ladder if still UNKNOWN. Uses the
    pick's ctx: league_key, side_role, odds_band_name, comp_type_name."""

def load_registry(root: Path) -> dict:
    """Read localdata/purity_registry.json -> contexts dict (never modified)."""
```

Key design decisions:
- **Key shapes verified** (registry keys embed canonical league names +
  `odds_band_name` / `comp_type_name` — the harness proved the mapping).
- **Overlay is a pure function** of (contexts, pick) → same inputs, same
  verdict; deterministic and auditable per-pick (reason string logged).
- **Registry read once per run** at pick-time, cached; no writes ever.

## 4. `scripts/picks_today.py` integration (flag-gated, OFF by default)

At the pick loop where `ctx` verdicts gate selection (after purity ctx is
built, before the bucket assignment):

```python
veto_on = os.environ.get("EDGE_FACTORY_VETO_RESOLUTION") == "1"
_veto_map = None
if veto_on:
    from edgefactory.veto_resolution import load_registry, build_pool_table
    _contexts = load_registry(ROOT / "localdata" / "purity_registry.json")
    _pools = build_pool_table(_contexts)

# inside the per-pick context evaluation:
if ctx.get("league") == "UNKNOWN" and veto_on:
    res = resolve_pick_verdict(_contexts, pick, _pools)
    if res["verdict"] != "UNKNOWN":
        # log the resolution + reason into the pick's ctx/audit fields
        pick["ctx"]["resolution_verdict"] = res["verdict"]
        pick["ctx"]["resolution_path"] = res["path"]
        pick["ctx"]["resolution_pool_n"] = res["pool_n"]
        pick["ctx"]["resolution_pool_w_roi"] = res["pool_w_roi"]
        # apply only when the resolution layer would CHANGE the bucket:
        #   ALLOW/BOOST -> treat as ALLOW (if it was UNKNOWN)
        #   CAUTION     -> treat as CAUTION (if it was UNKNOWN)
        #   VETO        -> stays blocked (already not played)
        #   UNKNOWN     -> unchanged
        if res["verdict"] in PLAYABLE:
            bucket = "CERTIFIED" if ... else "ALLOW"
        elif res["verdict"] == "CAUTION":
            bucket = "CAUTION"
        # VETO/UNKNOWN: bucket unchanged
```

Requirements for the implementation:
- **OFF default:** with the flag unset, `picks_today.py` behavior and output
  must be byte-identical to today (assert in tests).
- **Log every resolution** into the pick record (`resolution_*` fields) so the
  audit and the next counterfactual run can score them — auditability (Q5).
- **VETO never downgraded:** if the native verdict is VETO, the overlay never
  overrides it (monotone rule).
- **Only UNKNOWN is resolvable:** a specific non-UNKNOWN native verdict is
  never changed by the overlay.
- **CAUTION handling:** CAUTION picks are played by the live pipeline; the
  overlay may surface UNKNOWN→CAUTION, which the pipeline then plays with the
  usual caution semantics.

## 5. Tests (unit + integration, mirroring the debias test pattern)

`tests/test_veto_resolution.py`:
- `test_pooled_verdict_gates` — Scenario B thresholds (n=39 ALLOW blocked,
  n=40 ALLOW allowed; n=19 CAUTION blocked, n=20 allowed; VETO at n≥12).
- `test_pool_table_n_weighted_w_roi` — fixture contexts, verify w_roi =
  n-weighted mean; cells with roi None excluded from the mean.
- `test_o2_niche_resolves_unknown` / `test_o2_competition_type_resolves` —
  fixture registry, verify ladder + path labels.
- `test_o1_precedes_o2` — when the league pool resolves, O2 is not consulted.
- `test_never_overrides_veto` — native VETO + overlay ALLOW → VETO stays.
- `test_only_unknown_resolvable` — native CAUTION stays CAUTION.
- `test_resolve_pick_verdict_reason` — reason string contains path + n.
- `test_registry_never_modified` — load + resolve leaves the file bytes
  unchanged (read-only guarantee).

`tests/test_picks_today_integration.py` (or extend existing):
- `test_flag_off_byte_identical` — run `picks_today.py` with flag unset vs
  today's output; identical (the standing rule).
- `test_flag_on_resolves_unknown_ctx` — fixture registry + fixture picks;
  UNKNOWN → ALLOW/CAUTION resolution applied, `resolution_*` fields present.

## 6. Ship protocol (standing, unchanged)

1. Payload = full-file placement + SHA256SUMS BASE/TARGET + Phase-0 red-team
   + battery + fresh-tree rehearsal + independent upstream sha-verify before
   "deployed" is declared.
2. Explicit FILES commit (`git add <files>` — never `git add -A`).
3. Gates without pasted output did not happen.
4. **OFF by default; shadow receipts first:** the integration shadow-logs
   `resolution_*` fields on every pick's ctx ALWAYS (flag OFF = log only, no
   verdict/bucket change — per the second-agent refinement, the ≥30-settled
   gate accrues from day one). Compare the shadow counterfactual against the
   corrected Phase-0 report after 2–3 cycles. Only after ≥30 settled outcomes
   at the Phase-0-measured performance (hit ≥ Wilson LB, ROI ≥ 0) may the
   flag be turned ON (cloud: workflow env or secret).

## 7. Definition of done (for Phase 1/2)

- [ ] `src/edgefactory/veto_resolution.py` + `tests/test_veto_resolution.py`
      committed; full suite green (192 + new).
- [ ] `picks_today.py` integration flag-gated OFF; flag-off byte-identical
      (asserted in tests).
- [ ] `resolution_*` audit fields present in pick records when flag ON.
- [ ] Counterfactual harness re-run with the overlay ON (shadow) reproduces
      the Phase-0 report within tolerance.
- [ ] No `purity_registry.json` write path exists in the new code.

## 8. Pre-committed gate & decision rule (anti-mood — write-down-now)

Thresholds are FIXED from 2026-08-05 and must not be changed while the gate
accrues. The checkpoint is mechanical: `scripts/counterfactual_veto_resolution.py`
prints this checklist on every run (report section 6 + stdout).

Baseline for comparison: the audit's WATCHLIST_UNKNOWN_CTX bucket (the
watchlist the overlay would replace) — 19 settled / 17 wins / **+0.061**
would-be ROI / 89.5% hit on the current 30-day audit.

| gate | condition | current (2026-08-05) | status |
| --- | --- | --- | --- |
| G1 | settled in-scope caution-grade picks ≥ 30 | 15 | WIP |
| G2 | overlay ROI > 0 AND ≥ bucket ROI − 1pp | +0.042 vs +0.061 | **FAIL/WIP** |
| G3 | overlay 90% Wilson LB ≥ bucket hit − 5pp | 66.6% vs 89.5% | **FAIL/WIP** |

- **FLAG-ON requires ALL of G1–G3.** Until then the flag stays OFF; the
  overlay keeps shadow-logging `resolution_*` on every pick.
- **FLAG-OFF (keep shadow, keep waiting):** any of G1–G3 fails at a
  checkpoint. Note: G2 and G3 fail TODAY on the current window — the evidence
  mildly favors the status quo bucket over the overlay (the overlay selects
  the weaker half of the watchlist; the 3 out-of-scope winners stay
  unplayed). This is a negative signal to respect, not a neutral one.
- **DEPRECATE:** at ≥60 settled, if overlay ROI < bucket ROI − 2pp at two
  consecutive checkpoints (≥2 weeks apart), retire the overlay — flag stays
  OFF, code stays, decision recorded in HANDOVER. Prevents shadow limbo.

**Green-light retirement:** ALLOW/BOOST is N/A as an evidence category — no
in-scope green-light picks with settled outcomes; the overlay is
caution-grade-only in practice. The harness prints this note automatically;
do not read green-light rows as evidence.

**Threshold rationale + small-n honesty (27.1):** G2 epsilon 1pp is small vs
typical ROI scale (±0.05–0.2) and compares overlay vs bucket over the SAME
window (both noisy). G3 epsilon 5pp is deliberately generous so small n is
not punished; the 90% Wilson LB tightens with n, so G3 is meaningful only
near n=30. Today's G2/G3 FAIL at n=15 is an **insufficient-data state, not a
verdict** — the harness prints this note on every run. Deprecation: at n≥60
with G2 AND G3 still failing and ROI gap ≥2pp, confirm at a second checkpoint
≥2 weeks apart, then retire (flag OFF, code stays, HANDOVER records it).

**Timeline (be honest):** first shadow-data read in 2–3 bot cycles (days —
confirm `resolution_*` appears in archived picks); the 30-settled gate is
~6–9 weeks at the observed accrual rate (~0.5 in-scope settled/day). These
are different milestones; do not conflate them.

**Two flag-gated overlays — interaction stated:** engine-aware debias
(`6ccb18f`) applies at 🔥 note construction (engine/market-level); veto
resolution (`31f47ab`) applies at the ctx → bucket stage (context-level).
Different stages → no conflict by construction; both OFF; both log per-pick.
**Explicit: debias going live does not affect the veto gate's settled-outcome
counter** — the veto counter counts picks that were WATCHLIST_UNKNOWN_CTX at
the time they were made, which debias (a probability damp at the note stage)
cannot change. If a third overlay is proposed, document interaction semantics
before shipping.

## 9. Open risks (tracked)

- **UNKNOWN→CAUTION flooding:** with 15/20 O2-competition_type resolutions
  being CAUTION, turning the flag on could surface many CAUTION picks at once.
  Mitigation: shadow receipts measure the count delta before enabling.
- **Key-shape drift:** registry key formats may change upstream; tests pin the
  current shapes and will fail loudly if they do.
- **Pooled w_roi is a point estimate** — no CI. Mitigation: keep ALLOW at
  n≥40 (Scenario B) and require walk-forward ROI ≥ 0 before enabling.
- **Performance:** registry is ~36k cells; build_pool_table is O(cells) and
  cached per run — negligible.

## 10. Sequence

1. Implement `veto_resolution.py` + unit tests (pure functions first).
2. Integrate `picks_today.py` flag-gated OFF + integration tests.
3. Full suite + battery + fresh-tree rehearsal (standing protocol).
4. Payload + verified apply + explicit commit (exactly the new files).
5. Shadow receipts (flag OFF, `resolution_*` logged) for 2–3 cycles.
6. Re-run the Phase-0 harness against shadow logs; compare.
7. **Only then:** operator decides to enable via env/secret; ≥30-settled gate
   enforced by re-running the harness before enablement.
