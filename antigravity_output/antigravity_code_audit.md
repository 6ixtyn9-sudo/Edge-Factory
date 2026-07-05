# Edge Factory — Code & Security Audit

## Severity: CRITICAL
- **`norm_team` 9-Character Collision:** `src/edgefactory/util.py` truncates to 9 characters. This causes collisions like `Launceston City` vs `Launceston United` both becoming `launcesto`. This systematically merges distinct teams in the miner, polluting train/valid ROI.
- **Silent Failures in CI:** `scripts/daily.py` extensively uses `run_soft()` to wrap `notify_whatsapp.py` and `sync_supabase.py`. If Supabase goes down or WhatsApp tokens expire, the script catches the exception, prints to stderr, and exits 0. The GitHub Action will report a green build, completely hiding the SPOF delivery failure.

## Severity: HIGH
- **WhatsApp Endpoint Bug:** `src/edgefactory/whatsapp.py:237` currently attempts to call `whatsapp.php`. However, documentation indicates there was an endpoint bug. If this was partially fixed, the `run_soft` swallowing makes it impossible to verify delivery deterministically without checking the sent ledger manually.
- **Unpinned Dependencies:** `requirements.txt` and `pyproject.toml` use loose version bounds (e.g., `supabase>=2.4`, `pandas>=2.2`). This exposes the pipeline to upstream breaking changes. A locked `requirements.txt` (or poetry/uv lockfile) is strongly recommended. Run `pip-audit`.

## Severity: MEDIUM
- **Pre-match Guard Strictness:** `scripts/picks_today.py` enforces a `min_lead_minutes = 30` cutoff. If kickoff time is missing (`kickoff is None`), the pick is entirely dropped. This correctly protects against after-the-fact cheating, but drops edge data if the provider's timestamp is null.
- **Duplicate Collapse Logic:** `picks_today.py` strips `AC/FC/IFK` safely, but custom aliasing logic (`SOURCE_TEAM_KEY_ALIASES`) is hardcoded. Requires ongoing maintenance to avoid drift.

## Severity: LOW / INFO
- **Wilson LB Usage:** Verified in `src/edgefactory/assay.py`. `wilson_lb` is exclusively used for edge grading and certification. Raw hit rate is correctly ignored for certification logic.
- **ROI Calculation:** Verified in `src/edgefactory/assay.py:206`. Formula `(wins * avg_odds - n) / n` correctly uses total `n` as denominator.
- **Decay Auto-bench:** `src/edgefactory/assay.py:91` `should_bench()` correctly fires on `DECAYING` and `DEAD` verdicts. The circuit breaker in `mine_consensus.py` correctly refuses to overwrite the registry if 0 edges are certified, preventing an empty cache wipe.
- **Secrets Management:** Verified. `os.environ.get()` is used safely. `SUPABASE_KEY` is not leaked. `.env` is properly ignored. No hardcoded API keys exist in the codebase.
- **Tests:** `pytest` passes cleanly (30/30 tests).
