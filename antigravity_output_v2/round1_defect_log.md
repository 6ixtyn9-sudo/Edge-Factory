# Round-1 Defect Log

The following defects were identified in Round-1 execution and are addressed in V2.1:

- **D1**: Edges full CSV missing / wrong keys (`hit_rate` instead of `train.hit`).
- **D2**: Picks OOS CSV missing / not fully joined.
- **D3**: Veto autopsy incorrectly used `p['result']` instead of settled audit view (`picks_audit_rolling.json` by bucket), resulting in n=0 for veto ROI.
- **D4**: Purity registry inverted proposal was empty `{ "contexts":{"niche":{}} }`.
- **D5**: `norm_team` joining key mutated from 9 to 15 chars in roadmap Day 1 proposal, risking warehouse collapse.
- **D6**: Power analysis contained "(≈600)" text contradiction instead of the formal O'Brien-Fleming table and exact n ≈ 11,724.
- **D7**: SWOT missing confidence tags `[A/B/C/D]` and evidence citations per bullet.
- **D8**: Roadmap wrongly paused operations and mutated `norm_team`.
- **D9**: Code audit missed `whatsapp.php` DOCS_DRIFT and `run_soft()` exception swallowing in `scripts/daily.py`.
- **D10**: Missing deliverables (shipped 11 files, 2 missing, 3 broken).
- **D11**: CLV forensic claimed "unmeasurable" instead of computing continuous point-biserial correlation and handling the 0 beat rate.
- **D12**: Red team stress lacked quantified Scenario 5 (book limit) and Scenario 6 (norm_team 5% corruption).

### New Preventative Controls Added (V2.1)
- **VC-16**: `NORM_TEAM_FREEZE` — strict pre/post flight Git diffs and SHA pinning on `src/edgefactory/util.py` to prevent any join key mutations.
- **VC-17**: `JOIN_KEY_REGRESSION_SENTINEL` — warehouse record count assertions for consensus 2/3/4 and certified edges to detect silent data drops.
- **VC-18**: `ARTIFACT CROSS-CONSISTENCY` — ensuring specific anchor metrics (e.g., hit rate, ROIs, CLV beat) exactly match across all distinct files, preventing isolated calculation failures like the n=0 veto bug.
