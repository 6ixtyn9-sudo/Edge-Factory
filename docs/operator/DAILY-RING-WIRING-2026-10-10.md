# Operator paste — production Boggio key ring in `daily.yml` (priority #1, 2026-10-10)

**Why this is urgent (verified state, do not re-derive):** the boggio family pot is
100 calls/**key**/month and is SHARED by production capture, probes and stats.
Production spends ~2.5 calls/day and today `daily.yml` injects only the singular
`RAPIDAPI_KEY`, so all of it drains **pool A alone** (31 remaining at 2026-10-10
16:32Z, provider reset ~2026-11-02) → projected exhaustion ~2026-10-22/23. Pool B
(99 remaining, reset ~2026-11-10) is unreachable to the daily job until this line
exists. The adapter code already rotates the ring (`sources/boggio.py:
configured_keys()` prefers `RAPIDAPI_KEYS`, falls back to `RAPIDAPI_KEY`) —
only the workflow env mapping is missing. That is gap #1.

## What to paste

`docs/operator/daily-ring.proposed` is a byte-exact copy of `.github/workflows/daily.yml`
as it exists on `main` (`3594d21`) plus ONE inserted env line (and its comment block).
Diff to apply (the only difference between the two files):

```
@@ after current line 42 (      RAPIDAPI_KEY: ${{ secrets.RAPIDAPI_KEY }}) @@
+      # BOGGIO KEY RING (production, 2026-10-10). boggio.configured_keys()
+      # already prefers the ordered comma-separated RAPIDAPI_KEYS ring and
+      # falls back to the singular RAPIDAPI_KEY, so this ONE line is the whole
+      # wiring change: it lets the daily boggio shadow capture (~2.5 family
+      # calls/day) rotate across both free pools instead of exhausting pool A
+      # around 2026-10-22/23. Absent/empty secret = exactly today's behaviour
+      # (singular key only), exactly as an unset ODDSPAPI_API_KEYS no-ops its
+      # capture today. Same secret-name idiom as the verified shim line on main
+      # (source-probe-dispatch.yml:32). Value never printed.
+      RAPIDAPI_KEYS: ${{ secrets.RAPIDAPI_KEYS || '' }}
```

## Exact web-editor steps (agent cannot push workflow files — GitHub refuses the
## `workflows` scope for this credential; that is why this doc exists)

1. GitHub → repo `6ixtyn9-sudo/Edge-Factory` → **Actions** → **Workflows** (or the
   file directly): open `.github/workflows/daily.yml` **on branch `main`**.
2. Click the pencil (Edit). Do NOT edit any other file; do NOT use "Create a new
   branch" — commit directly to `main` is the only way this reaches the dispatcher
   (GitHub registers/parses workflows from the default branch).
3. Find the line `      RAPIDAPI_KEY: ${{ secrets.RAPIDAPI_KEY }}` (currently line 42).
   Paste the ten lines above immediately AFTER it, keeping the same 6-space indent.
4. **Safest alternative:** select-all and replace the whole file with the contents of
   `docs/operator/daily-ring.proposed` (it is the current main file + this insertion
   only). If you do, verify the diff view shows ONLY those ten added lines.
5. Commit message suggestion: `Wire RAPIDAPI_KEYS ring into daily boggio capture`.
6. Verify (zero cost, no dispatch needed):
   - `main`'s `.github/workflows/daily.yml` contains `RAPIDAPI_KEYS: ${{ secrets.RAPIDAPI_KEYS || '' }}`;
   - the secret `RAPIDAPI_KEYS` exists in Settings → Secrets and variables → Actions,
     comma-separated, pool A first (rotation order), pool B second.
7. Do NOT dispatch `daily.yml` to test this. It runs on its own external cadence, and
   the first ordinary run after the paste is the test: its boggio stats line should
   show the ring in effect. On any routine boggio call, READ
   `X-RateLimit-Match-Stats-and-Prediction-endpoints-Remaining` rather than running
   `--verify-keys` (the latter spends 2 family calls and is already done).

## Failure modes this prevents / risks it carries

- Unwired: pool A dies ~Oct 22/23, boggio shadow goes `quota`-blocked for ~10 days,
  price-donor lane loses its average-book donor mid-month.
- Pasted line alone, secret absent: no behaviour change (fail-soft) — that is by design.
- Pooling two free accounts for additive quota is **ToS-permittedness UNVERIFIED**;
  the operator accepted that risk on 2026-10-10, and the machinery stays
  account-agnostic so the fallback is a single account (delete the secret, keep the line).
- Rotation order matters: pool A resets first (Nov 2), so putting it first spends the
  soon-to-reset pool and leaves pool B (Nov 10 reset) as the late-month reserve.
