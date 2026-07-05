# ANTIGRAVITY v2.1 — Tactical Roadmap

## Next 30 Days (Immediate Horizon)

### 1. Active Integration of CLV Checks
Currently, the CLV tracking is purely passive/forensic.
- **Action:** Transition `audit_clv.py` from an audit-only module to an active gating mechanism.
- **Rule:** Automatically bench any edge that consistently shows a negative IP Delta > -0.02 pre-match over a trailing 7-day window.

### 2. Niche Purity Evolution
The purity registry correctly blocks weak evidence, but heavily limits output.
- **Action:** Wait for the `CAUTION` bucket sample size to mature (currently n=25 with negative ROI). Continue logging caution outcomes. 
- **Rule:** If the `CAUTION` bucket sample exceeds n=100 and retains a negative ROI, automatically transition the ruleset to instantly `VETO` all caution picks, formally solidifying the toxicity of those niche contexts.

### 3. Join-Key Defense
The `norm_team` crisis from early June highlighted the sensitivity of the entire pipeline to a single key mapping length.
- **Action:** Implement a hard git hook or continuous integration check that computes the SHA256 of `src/edgefactory/util.py` and instantly fails any build that modifies the `team_name[:9]` truncation rule unless explicitly overridden by a human.

## Long-Term Objectives

### Expansion of Evaluated Live Sources
- Introduce BetExplorer into a standalone shadowing phase (Phase A) purely to validate predictive hit rates in parallel to `bzzoiro_odds`. Do not merge it into `warehouse.duckdb` core consensus until it proves a baseline standalone hit rate > 65% on home favorites.

### Automated Account Rotation Strategy
- Acknowledging the extreme bookmaker restrictions on short-odds strategies (as proven by the Red-Team limit shock analysis), begin exploring API-driven bet placement rotation mechanisms across multiple soft books to distribute the footprint.
