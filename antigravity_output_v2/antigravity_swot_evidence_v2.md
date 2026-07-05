# ANTIGRAVITY v2.1 — SWOT Evidence Matrix

## Strengths (S)
- **Edge Mining Robustness:** The walk-forward methodology and consensus filtering effectively surface profitable opportunities (e.g., ROI ~6% out of sample) without lookahead bias.
- **Defensive Posture:** Strict checks against away favorites and non-1x2 markets (OU 2.5, draws) keep the system immune to known areas of high negative edge decay.
- **Rigid Data Integration:** Utilizing DuckDB as a fast cache for querying historical odds and lines provides an immutable ground truth for edge mining that isn't dependent on heavy external data warehouses.

## Weaknesses (W)
- **Limited Volume:** Extreme vetting rules yield very few bets per week. The system is heavily bottlenecked by finding the perfect set of conditions (home favorites, odds <1.25, unanimous consensus).
- **Time-Decay Vulnerability:** Short odds inherently depend heavily on the timing of when the odds are fetched, leaving the strategy sensitive to late line movements.
- **Niche Bias:** A lot of leagues end up dropping into the `UNKNOWN` purity category because of low historical data depth.

## Opportunities (O)
- **Granular Purity Registry:** Refining the `niche` purity rules and utilizing deeper tracking of the "CAUTION" bucket can reveal new pockets of edge outside the classic major leagues.
- **CLV Integration:** Integrating the `clv_forensic` results as an active gate during picking—rather than just passively auditing—can further sharpen the ROI by dropping edges that consistently suffer negative CLV pre-match.

## Threats (T)
- **Bookmaker Restrictions:** Winning consistently on short odds often leads to quick account limitations or outright bans from soft books.
- **Join Key Drift Risk:** The system is exquisitely sensitive to data mapping keys (e.g., `norm_team` truncating at 9 chars). Any accidental data drift in naming structures could collapse consensus and invalidate all trained edges overnight.
- **Odds Squeezing:** Market efficiency continues to improve. Finding 1.20-1.75 edges might dry up if prediction consensus APIs are priced in by sharps before execution.
