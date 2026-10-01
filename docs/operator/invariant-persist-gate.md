# Apply: refuse to commit generated state when invariants fail

**Status: NOT YET APPLIED.** This is the one change in the invariant gate
that the agent cannot push — GitHub rejects it with *"refusing to allow a
GitHub App to create or update workflow `.github/workflows/daily.yml`
without `workflows` permission"*. Everything else is already on the branch.

## Why this matters

Withholding the official-run completion marker is **not** a gate. The
persist step runs with `if: always()`, so a run that printed invariant
ERRORs still staged, committed and pushed its generated state. That is
exactly how contradictory state shipped previously: the checker shouted
and the pipeline persisted the run anyway.

`scripts/daily.py` already writes a `.invariant_failure` sentinel at the
repository root when the strict check reports an ERROR, and clears it at
the start of every run. The workflow has to read it.

## The change

In `.github/workflows/daily.yml`, in the step
**"Persist pipeline state to git (single source of truth)"**, insert this
block at the very top of the `run:` script, *before* the `git config`
lines and before `git add -A localdata/`:

```yaml
          # An invariant ERROR means two artifacts contradict each other.
          # Committing that state publishes a run we already know is not
          # trustworthy, which is how the previous contradictory state was
          # shipped. Artifacts are still uploaded for inspection below.
          if [ -f .invariant_failure ]; then
            echo "INVARIANT ERRORS: refusing to commit generated state."
            cat .invariant_failure
            echo "State is available in the uploaded artifact for inspection."
            exit 1
          fi
```

Leave the rest of the step unchanged.

## What stays working

- The **Upload Pick Ledgers & Reports as Artifacts** step keeps
  `if: always()`, so a blocked run still uploads everything for
  inspection. The gate refuses the *commit*, not the evidence.
- A clean run is unaffected: no sentinel, no early exit.
- A stale sentinel cannot block a later clean run, because `daily.py`
  deletes it at the start of each run.

## Verifying it took effect

`tests/test_invariant_persist_gate.py::test_the_persist_step_refuses_to_commit_bad_state`
skips while the guard is absent and passes once it is applied. Run:

```
PYTHONPATH=src python3 -m pytest tests/test_invariant_persist_gate.py -q
```

A fully applied gate reports no skips.
