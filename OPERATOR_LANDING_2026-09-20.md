# Operator landing authorization — 2026-09-20

**Operator rule change 2026-09-20** — for this one bounded landing sequence,
the operator explicitly authorized, on record: pushing to `main`
(`git push origin HEAD:main`, no `--force`), checking out `main`, and deleting
the session branch `arena/01a0bed7-edge-factory` afterwards. The session's
standing constraints (session-branch-only pushes, no checkout, no branch
deletion) resume afterwards unless the operator says otherwise.

- Session branch being landed: `arena/01a0bed7-edge-factory`
- **Pre-rebase branch tip: `b6916f955a58d8457babd0cd25fd75865bf2d452`**
  (*Correct home-fade signal classification to INSUFFICIENT EVIDENCE*)
- Stack being landed (4 commits): `8e7635d` ml-fade slice → `bee72e6`
  conditional scan → `efeddb3` price-robustness study → `b6916f9`
  classification correction.
- Divergence being resolved by rebase: `origin/main` moved to `53a5f1e`
  (bot "persist pipeline state", `localdata/*`-only) after the branch
  point `d369b15`; the session stack touches only `src/`, `scripts/`,
  `tests/` — zero file overlap, clean replay expected.
- Bot-owned pipeline content (`localdata/*`, incl. `edges_consensus.json`)
  is NOT part of this stack and is untouched by hand. If a bot-commit race
  made the rebase conflict in generated files, the `origin/main` side wins
  (it regenerates); it did not, per pre-flight diff.
- Honesty note: after the rebase the four commits land with NEW SHAs; the
  pre-rebase SHAs above become unreachable when the session-branch ref is
  deleted. A mapping commit is added post-rebase so prior receipts
  referencing `b6916f9…` remain interpretable.
