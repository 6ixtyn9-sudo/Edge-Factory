#!/usr/bin/env python3
"""6D — the measurement ledger and the certification ledger, proven.

The operator's question: the performance view shows thousands of enhancement
measurements, the registry showed 409. Answer: the registry only ever received
PRICED settled outcomes — its caller iterated ``priced_outcomes`` — even though
the module has always accepted unpriced ones (processed-only; they dedupe and are
measurable, but never advance certification: probability without price is not
evidence of value). Round 6D feeds both.

This driver proves the change on the shipped path, in a scratch worktree:

* runs the real audit (``scripts/audit_recent_picks.py``) over the registry's own
  coverage window (2026-08-01 → today) with the 6D wiring in place;
* runs it a second time and shows the feed is idempotent;
* compares the resulting registry with the committed one, per market:
  certification fields byte-identical, no processed key lost, and every ADDED key
  traceable to a recommendation in this window (dedup explains the rest);
* prints the trim-safety table — per-market keys inside the audit's 30-day rescan
  window and over the whole archive, against ``MAX_PROCESSED_KEYS``;
* prints the per-label reconciliation (recommended / settled / priced_n /
  registry_processed / class), which the audit report now carries;
* with ``--apply``, copies the registry into this repository (the one state file
  this round changes) and re-verifies.

The worktree is a scratch checkout: the audit's report artifacts and its
warehouse land there, never in this repository. Needs duckdb (the audit's results
index); the driver builds the warehouse from the tracked ``*.csv.gz`` when the
worktree does not have one yet.

Writes ``handoff/r6d_ledger_proof.txt``.
"""
from __future__ import annotations

import io
import json
import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "bin" / "python")
WORKTREE = pathlib.Path(os.environ.get("R6D_WORKTREE", "/tmp/r6d_wt"))
START = "2026-08-01"
CERT_FIELDS = ("n", "hits", "records", "profit", "inv_price_sum", "multi_n",
               "status", "status_since", "status_reason")


def _run(args, cwd, env=None, timeout=1800):
    return subprocess.run(args, cwd=str(cwd), capture_output=True, text=True,
                          timeout=timeout, env={**os.environ, "PYTHONPATH": "src",
                                                 **(env or {})})


def main() -> int:
    apply_now = "--apply" in sys.argv
    out = io.StringIO()

    def say(line: str = "") -> None:
        out.write(line + "\n")

    failures: list[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        say(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    def finish() -> int:
        text = out.getvalue()
        (ROOT / "handoff" / "r6d_ledger_proof.txt").write_text(text)
        print(text, end="")
        return 1 if failures else 0

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    day = subprocess.run(["date", "-u", "+%F"], capture_output=True, text=True).stdout.strip()

    say(f"== 6D: the measurement ledger and the certification ledger (tip {head[:7]}) ==")
    say("")
    say(f"window: {START} → {day} (the registry's own coverage starts {START})")
    say("")

    # ---------------------------------------------------------------- worktree
    say("-- the scratch checkout --")
    subprocess.run(["git", "worktree", "remove", "--force", str(WORKTREE)],
                   cwd=ROOT, capture_output=True)
    p = subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(WORKTREE), head],
                       cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        say(f"worktree add failed: {p.stderr}")
        return finish()
    say(f"  git worktree add --detach {WORKTREE} {head[:7]}  → a checkout at this tip")
    wh = WORKTREE / "localdata" / "warehouse.duckdb"
    if not wh.exists():
        say("  warehouse absent in the worktree (not a tracked file): building it from the")
        say("  tracked captures — the audit's results index needs it.")
        b = _run([PY, "scripts/build_warehouse.py"], WORKTREE)
        say(f"  build_warehouse.py exit={b.returncode}; "
            f"{[ln for ln in b.stdout.splitlines() if ln.startswith('warehouse built')] or b.stderr.splitlines()[-1:]}")
        check("the warehouse builds offline in the scratch checkout", wh.exists())
    else:
        say("  warehouse already present in the worktree")
    say("")

    # ------------------------------------------------------------------- runs
    def audit(tag: str) -> tuple[int, pathlib.Path]:
        log = _run([PY, "scripts/audit_recent_picks.py", "--start", START, "--end", day], WORKTREE)
        (ROOT / "handoff" / f"r6d_audit_{tag}.out.txt").write_text(log.stdout + log.stderr)
        return log.returncode, WORKTREE / "localdata" / "enhancement_registry.json"

    say("-- run 1: the real audit, both ledgers fed --")
    rc, reg_path = audit("run1")
    say(f"  scripts/audit_recent_picks.py --start {START} --end {day}  (in the scratch checkout)")
    say(f"  exit={rc}; full output: handoff/r6d_audit_run1.out.txt")
    check("the audit run completes", rc == 0)
    reg_a = json.loads(reg_path.read_text())
    after_a = reg_path.read_bytes()
    say("")

    say("-- run 2: idempotence --")
    rc2, _ = audit("run2")
    after_b = reg_path.read_bytes()
    say(f"  exit={rc2}")
    check("a second identical run changes the registry not at all (byte-identical)",
          after_a == after_b and rc2 == 0, f"{len(after_b)} bytes")
    say("")

    # ------------------------------------------------------------- comparison
    committed = json.loads(subprocess.run(
        ["git", "show", f"{head}:localdata/enhancement_registry.json"], cwd=ROOT,
        capture_output=True, text=True).stdout)
    before_markets = committed.get("markets") or {}
    after_markets = reg_a.get("markets") or {}

    say("-- certification is untouched; processed grows by the unpriced keys --")
    say(f"  {'market':22s} {'cert fields':12s} {'processed before':>16s} "
        f"{'after':>7s} {'added':>6s} {'lost':>5s}")
    cert_same = True
    no_loss = True
    for mkey in sorted(set(before_markets) | set(after_markets)):
        b = before_markets.get(mkey) or {}
        a = after_markets.get(mkey) or {}
        if mkey in before_markets:
            same = all(b.get(f) == a.get(f) for f in CERT_FIELDS)
        else:
            # Newly opened market initialized by _blank(): unpriced outcomes cannot advance it,
            # so certification fields must remain at 0/empty/SHADOW
            same = (a.get("n") == 0 and a.get("hits") == 0 and a.get("records") == [] and
                    a.get("profit") == 0.0 and a.get("inv_price_sum") == 0.0 and
                    a.get("multi_n") == 0 and a.get("status") == "SHADOW")
        cert_same &= same
        bp = set(b.get("processed") or [])
        ap = set(a.get("processed") or [])
        lost = bp - ap
        no_loss &= not lost
        label = "identical" if same and mkey in before_markets else ("new(SHADOW/0)" if same else "MOVED")
        say(f"  {mkey:22s} {label:14s} "
            f"{len(bp):14d} {len(ap):7d} {len(ap - bp):6d} {len(lost):5d}")
    check("every certification field is byte-identical per market "
          "(n/hits/records/profit/inv_price_sum/multi_n/status*)", cert_same)
    check("no processed key was lost (the trim never reached inside the window)", no_loss)

    # every ADDED key must be a recommendation the archives carry inside the window
    archive_keys: set[str] = set()
    for pattern in ("picks_2026-*.json", "picks_morning_2026-*.json"):
        for path in sorted((WORKTREE / "localdata").glob(pattern)):
            try:
                raw = json.loads(path.read_text())
            except Exception:
                continue
            picks = raw if isinstance(raw, list) else raw.get("picks") or []
            for pick in picks:
                d = str(pick.get("date") or "")[:10]
                if not (START <= d <= day):
                    continue
                m = pick.get("recommended_enhancement")
                if not m or m not in {k.split("@")[0] for k in after_markets}:
                    continue
                match = pick.get("match") or f"{pick.get('home')} vs {pick.get('away')}"
                archive_keys.add(f"{d}|{match}|{m}")
    added = {f"{k}" for mkey in after_markets
             for k in (set((after_markets[mkey].get("processed") or []))
                       - set((before_markets.get(mkey) or {}).get("processed") or []))}
    unmatchable = {k for k in added
                   if "|".join(k.split("|")[:2]) not in
                   {"|".join(a.split("|")[:2]) for a in archive_keys}}
    say(f"  added keys: {len(added)}; of those, keys with no matching recommendation "
        f"row in the window: {len(unmatchable)}")
    if unmatchable:
        for k in sorted(unmatchable)[:5]:
            say(f"    (sample) {k}")
    check("every added key corresponds to a recommendation row in this window",
          not unmatchable)
    say("")

    # ------------------------------------------------------------ trim safety
    say("-- trim safety: keys a rescan window can present vs the cap --")
    sys.path.insert(0, str(ROOT / "src"))
    from edgefactory.enh_registry import MAX_PROCESSED_KEYS, processed_window_is_safe
    by_market: dict[str, dict[str, int]] = {}
    for path in sorted((WORKTREE / "localdata").glob("picks_2026-*.json")):
        try:
            raw = json.loads(path.read_text())
        except Exception:
            continue
        d = path.stem.split("_")[-1]
        picks = raw if isinstance(raw, list) else raw.get("picks") or []
        for pick in picks:
            m = pick.get("recommended_enhancement")
            if not m:
                continue
            by_market.setdefault(m, {})
            by_market[m][d] = by_market[m].get(d, 0) + 1
    days = sorted({d for dated in by_market.values() for d in dated})
    say(f"  MAX_PROCESSED_KEYS = {MAX_PROCESSED_KEYS}")
    say(f"  {'market':18s} {'worst 30d window':>17s} {'whole archive':>14s}   safe?")
    worst_any = 0
    for m in sorted(by_market):
        dated = by_market[m]
        best = 0
        for i, d in enumerate(days):
            window = days[max(0, i - 29): i + 1]
            best = max(best, sum(dated.get(x, 0) for x in window))
        worst_any = max(worst_any, best)
        total = sum(dated.values())
        say(f"  {m:18s} {best:17d} {total:14d}   "
            f"{'yes' if processed_window_is_safe(best) and processed_window_is_safe(total) else 'NO'}")
    check("every market's rescan window stays under the cap "
          "(so the trim can never force a re-record)", worst_any < MAX_PROCESSED_KEYS,
          f"worst = {worst_any}")
    say("")

    # -------------------------------------------------------- reconciliation
    say("-- the per-label reconciliation the audit report now carries --")
    report = json.loads((WORKTREE / "localdata" / "picks_audit_rolling.json").read_text())
    ea = report.get("enhancements_audit") or {}
    say(f"  {'label':18s} {'recommended':>11s} {'settled':>8s} {'priced_n':>8s} "
        f"{'processed':>9s}  class")
    for k in sorted(ea.get("by_enhancement") or {}):
        v = ea["by_enhancement"][k]
        say(f"  {k:18s} {v.get('recommended', 0):11d} {v.get('settled', 0):8d} "
            f"{v.get('priced_n', 0):8d} {v.get('registry_processed', 0):9d}  "
            f"{v.get('price_source_class', '')}")
    classes = {v.get("price_source_class") for v in (ea.get("by_enhancement") or {}).values()}
    check("every label carries a price-source class", classes <= {"priced", "no_price_source",
                                                                 "no_price_observed", "unknown"}
          and "unknown" not in classes)
    check("the never-priceable class is labelled, not silent",
          "no_price_source" in classes, "goal_range_* = no captured feed quotes it")
    say("")

    # ------------------------------------------------------------------ apply
    if apply_now:
        say("-- apply: the one state file this round changes --")
        target = ROOT / "localdata" / "enhancement_registry.json"
        target.write_bytes(after_b)
        applied = json.loads(target.read_text())
        ap_markets = applied.get("markets") or {}
        say(f"  wrote {target.relative_to(ROOT)} ({len(after_b)} bytes)")
        same_cert = all(all((before_markets.get(m) or {}).get(f) == (ap_markets.get(m) or {}).get(f)
                            for f in CERT_FIELDS) for m in before_markets)
        n_before = sum(len(e.get("processed") or []) for e in before_markets.values())
        n_after = sum(len(e.get("processed") or []) for e in ap_markets.values())
        recs = sum(len(e.get("records") or []) for e in ap_markets.values())
        say(f"  processed: {n_before} → {n_after} (+{n_after - n_before}); "
            f"priced records: {recs} (was {sum(len(e.get('records') or []) for e in before_markets.values())})")
        check("applied file: certification still byte-identical", same_cert)
        check("applied file: priced records unchanged",
              recs == sum(len(e.get("records") or []) for e in before_markets.values()))
        check("applied file: the working tree's registry equals the audit's output",
              target.read_bytes() == after_b)
        say("")

    subprocess.run(["git", "worktree", "remove", "--force", str(WORKTREE)],
                   cwd=ROOT, capture_output=True)
    say("-- scratch checkout removed; the repository's localdata holds only the applied file --")
    st = subprocess.run(["git", "status", "--porcelain", "--", "localdata/"], cwd=ROOT,
                        capture_output=True, text=True).stdout.strip()
    say("  git status --porcelain -- localdata/ →")
    for line in (st.splitlines() or ["(clean)"]):
        say(f"    {line}")
    say("")
    say(f"== verdict: {'ALL CHECKS PASS' if not failures else 'FAILURE — ' + '; '.join(failures)} ==")
    return finish()


if __name__ == "__main__":
    raise SystemExit(main())
