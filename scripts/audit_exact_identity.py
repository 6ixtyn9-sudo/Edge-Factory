#!/usr/bin/env python3
"""Exact-identity card / pool / history report (READ-ONLY).

For every bet-day with a ticket card in localdata/, joins three populations on
exact identity (date + canonical home key + canonical away key + side), never
on list position:

  pool     all same-day 1X2 candidates in picks_YYYY-MM-DD.json (incl. SKIPPED_VETO)
  card     legs printed on auto_tickets_YYYY-MM-DD.txt
  history  settled accumulators in auto_tickets_state.json["history"]

Outcomes come from the production results archive (form_intel.load_archive).
Nothing is written unless --out / --json is given. No provider calls, no
grading pipeline, no state or history changes.

Usage (from the repo root):
  PYTHONPATH=src python3 scripts/audit_exact_identity.py [--localdata DIR]
      [--out report.md] [--json report.json] [--reps 5000] [--seed 20261019]

Interval method: 95% percentile day-block bootstrap. Paired gaps resample the
same date blocks for both populations.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from edgefactory import form_intel as fi  # noqa: E402

CARD_RE = re.compile(r"^auto_tickets_(\d{4}-\d{2}-\d{2})\.txt$")
ACCA_RE = re.compile(r"^\[ACCA #(\d+)\] @([0-9.]+) — stake ([0-9.]+)% of capital")
LEG_RE = re.compile(
    r"^\s+(.+?) vs (.+?)\s{2,}(HOME|AWAY|DRAW|OVER|UNDER)\s+@ ?([0-9.]+)\s+\(stated (\d+)%\)"
)
BANDS = [(0.0, 1.20, "<1.20"), (1.20, 1.30, "1.20-1.30"), (1.30, 1.50, "1.30-1.50"),
         (1.50, 1.80, "1.50-1.80"), (1.80, 2.20, "1.80-2.20"), (2.20, 99.0, ">=2.20")]


def band_of(price: float) -> str | None:
    for lo, hi, name in BANDS:
        if lo <= price < hi:
            return name
    return None


def flat_pnl(won: bool | None, odds: float) -> float | None:
    if won is None:
        return None
    return (odds - 1.0) if won else -1.0


def boot_ci(values, dates, reps, rng):
    values = np.asarray(values, float)
    if len(values) < 2:
        return [None, None]
    ud, inv = np.unique(np.asarray(dates), return_inverse=True)
    S = np.bincount(inv, weights=values, minlength=len(ud))
    C = np.bincount(inv, minlength=len(ud)).astype(float)
    idx = rng.integers(0, len(ud), size=(reps, len(ud)))
    with np.errstate(divide="ignore", invalid="ignore"):
        means = S[idx].sum(axis=1) / C[idx].sum(axis=1)
    means = means[np.isfinite(means)]
    if len(means) == 0:
        return [None, None]
    return [round(float(np.percentile(means, 2.5)), 4), round(float(np.percentile(means, 97.5)), 4)]


def parse_card(path: Path):
    accas, cur = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ACCA_RE.match(line)
        if m:
            cur = {"n": int(m.group(1)), "odds": float(m.group(2)),
                   "stake_pct": float(m.group(3)), "legs": []}
            accas.append(cur)
            continue
        if cur is not None:
            lm = LEG_RE.match(line)
            if lm:
                cur["legs"].append({"home": lm.group(1).strip(), "away": lm.group(2).strip(),
                                    "side": lm.group(3), "price": float(lm.group(4))})
            elif not line.strip():
                cur = None
    locked = any(line.startswith("FROZEN AT") for line in path.read_text(encoding="utf-8").splitlines())
    return accas, locked


class Identity:
    """Canonical identity: production source_team_key via the archive's _key."""

    def __init__(self, archive):
        self.archive = archive
        self.key = archive._key
        self.results = defaultdict(list)
        for r in archive.rows:
            self.results[(r["date"], frozenset((self.key(r["home"]), self.key(r["away"]))))].append(r)

    def leg_key(self, day, home, away, side):
        return (day, self.key(home), self.key(away), str(side).upper())

    def outcome(self, day, home, away):
        """'HOME' | 'AWAY' | 'DRAW' | None (no result) | 'AMBIGUOUS'."""
        cands = self.results.get((day, frozenset((self.key(home), self.key(away)))))
        if not cands:
            return None
        outs = set()
        for c in cands:
            hs, gs = int(c["hs"]), int(c["gs"])
            if self.key(c["home"]) == self.key(home):
                h, a = hs, gs
            else:
                h, a = gs, hs
            outs.add("HOME" if h > a else "AWAY" if h < a else "DRAW")
        return outs.pop() if len(outs) == 1 else "AMBIGUOUS"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--localdata", default=str(Path(__file__).resolve().parents[1] / "localdata"))
    ap.add_argument("--out", default=None, help="write the markdown report here")
    ap.add_argument("--json", default=None, help="write machine-readable results here")
    ap.add_argument("--reps", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=20261019)
    args = ap.parse_args()
    LD = Path(args.localdata)
    rng = np.random.default_rng(args.seed)

    archive = fi.load_archive(LD)
    ident = Identity(archive)
    state = json.loads((LD / "auto_tickets_state.json").read_text(encoding="utf-8"))
    hist = {h["date"]: h for h in state.get("history", [])}
    frozen = set((state.get("frozen_by_date") or {}).keys())

    card_days = sorted(
        m.group(1) for p in LD.glob("auto_tickets_*.txt") if (m := CARD_RE.match(p.name))
    )
    notes = defaultdict(list)
    out = {"card_days": len(card_days), "populations": {}, "bands": {}, "identity": {}, "notes": {}}

    pool_rows, card_legs, card_accas, hist_days = [], [], [], []
    price_deltas, matched_n, unmatched = [], 0, []
    locked_counts = Counter()
    out_of_day_total = 0

    for day in card_days:
        accas, locked = parse_card(LD / f"auto_tickets_{day}.txt")
        locked_counts["locked" if locked else "unlocked"] += 1
        # Pool: same-day file, rows whose embedded date equals the file date.
        pool_path = LD / f"picks_{day}.json"
        day_pool = {}
        if pool_path.exists():
            for r in json.loads(pool_path.read_text(encoding="utf-8")):
                if r.get("market") != "1x2" or r.get("odds") is None or r.get("pick") not in ("home", "away"):
                    continue
                if str(r.get("date") or "")[:10] != day:
                    out_of_day_total += 1
                    notes[day].append("out-of-day pool rows excluded")
                    continue
                k = ident.leg_key(day, r["home"], r["away"], r["pick"])
                if k in day_pool:
                    continue  # first vintage kept; later duplicates ignored
                day_pool[k] = r
        else:
            notes[day].append("no picks file")
        for k, r in day_pool.items():
            res = ident.outcome(day, r["home"], r["away"])
            if res is None or res == "AMBIGUOUS":
                notes[day].append("pool fixture without a clean result")
                continue
            won = (res == str(r["pick"]).upper())
            price = float(r["odds"])
            pool_rows.append({"date": day, "pnl": flat_pnl(won, price), "band": band_of(price), "price": price})

        # Card legs and accumulators.
        for a_i, a in enumerate(accas, 1):
            leg_res, leg_pnls = [], []
            for lg in a["legs"]:
                k = ident.leg_key(day, lg["home"], lg["away"], lg["side"])
                row = day_pool.get(k)
                if row is None:
                    unmatched.append((day, lg["home"], lg["away"], lg["side"], lg["price"]))
                else:
                    matched_n += 1
                    d = abs(float(row["odds"]) - lg["price"])
                    price_deltas.append(d)
                res = ident.outcome(day, lg["home"], lg["away"])
                won = None if res in (None, "AMBIGUOUS") else (res == lg["side"].upper())
                pnl = flat_pnl(won, lg["price"])
                leg_res.append(won)
                card_legs.append({"date": day, "pnl": pnl, "band": band_of(lg["price"]), "price": lg["price"],
                                  "stake_pct": a["stake_pct"], "acca": a_i})
            resolved = len(leg_res) > 0 and all(w is not None for w in leg_res)
            won_acca = all(leg_res) if resolved else None
            card_accas.append({"date": day, "odds": a["odds"], "stake_pct": a["stake_pct"], "won": won_acca,
                               "pnl": flat_pnl(won_acca, a["odds"]) if resolved else None,
                               "legs": len(a["legs"])})

        if day in hist:
            hist_days.append({"date": day, "locked": day in frozen, "staked": hist[day]["staked_pct"],
                              "returned": hist[day]["returned_pct"],
                              "accas": hist[day]["accas"], "card_accas": len(accas)})
            if len(accas) != len(hist[day]["accas"]):
                notes[day].append(f"card has {len(accas)} acca(s); history has {len(hist[day]['accas'])}")
        else:
            notes[day].append("no settled history row (card only)")
        n_un = sum(1 for u in unmatched if u[0] == day)
        if n_un:
            notes[day].append(f"{n_un} card leg(s) without exact pool identity")

    # ---- populations -------------------------------------------------------
    pool_dates = [r["date"] for r in pool_rows if r["pnl"] is not None]
    pool_pnl = [r["pnl"] for r in pool_rows if r["pnl"] is not None]
    out["populations"]["pool_all_buckets"] = {
        "priced_rows": len(pool_rows), "resolved": len(pool_pnl),
        "flat_roi": round(float(np.mean(pool_pnl)), 4) if pool_pnl else None,
        "flat_roi_ci": boot_ci(pool_pnl, pool_dates, args.reps, rng),
    }
    cl = [l for l in card_legs if l["pnl"] is not None]
    out["populations"]["card_legs"] = {
        "legs": len(card_legs), "resolved": len(cl),
        "wins": int(sum(1 for l in cl if l["pnl"] > 0)),
        "flat_roi": round(float(np.mean([l["pnl"] for l in cl])), 4) if cl else None,
        "flat_roi_ci": boot_ci([l["pnl"] for l in cl], [l["date"] for l in cl], args.reps, rng),
    }
    ca = [a for a in card_accas if a["pnl"] is not None]
    w = np.array([a["stake_pct"] for a in ca], float)
    p = np.array([a["pnl"] for a in ca], float)
    out["populations"]["card_accas"] = {
        "accas": len(card_accas), "resolved": len(ca),
        "flat_roi": round(float(p.mean()), 4) if ca else None,
        "flat_roi_ci": boot_ci(p, [a["date"] for a in ca], args.reps, rng),
        "stake_weighted_roi": round(float((w * p).sum() / w.sum()), 4) if ca else None,
        "stake_weighted_roi_ci": boot_ci(w * p / w.mean(), [a["date"] for a in ca], args.reps, rng) if ca else [None, None],
        "stake_basis": "printed stake % of capital on the card",
    }
    hs = [h for h in hist_days]
    hs_flat = [(acc["odds"] - 1) if acc["won"] else -1.0 for h in hs for acc in h["accas"]]
    hs_flat_dates = [h["date"] for h in hs for _ in h["accas"]]
    st_s = np.array([h["staked"] for h in hs], float)
    st_r = np.array([h["returned"] for h in hs], float)
    dayroi = (st_r - st_s) / st_s
    out["populations"]["settled_history"] = {
        "days": len(hs), "accas": len(hs_flat),
        "flat_roi": round(float(np.mean(hs_flat)), 4) if hs_flat else None,
        "flat_roi_ci": boot_ci(hs_flat, hs_flat_dates, args.reps, rng),
        "stake_weighted_roi_pooled": round(float(st_r.sum() / st_s.sum() - 1), 4) if len(hs) else None,
        "stake_weighted_roi_ci": boot_ci(dayroi, [h["date"] for h in hs], args.reps, rng),
        "stake_basis": "recorded day stake and return in state history",
    }
    out["populations"]["receipt_verified_placements"] = {"n": 0, "note": "no bookmaker receipts in workspace"}

    # ---- paired card minus pool, by day and band --------------------------
    def paired(filter_fn):
        days = sorted({l["date"] for l in cl})
        diffs, dd = [], []
        for d in days:
            c = [l["pnl"] for l in cl if l["date"] == d and filter_fn(l)]
            q = [r["pnl"] for r in pool_rows if r["date"] == d and r["pnl"] is not None and filter_fn(r)]
            if c and q:
                diffs.append(np.mean(c) - np.mean(q))
                dd.append(d)
        if not diffs:
            return {"days": 0}
        return {"days": len(diffs), "gap_pp": round(100 * float(np.mean(diffs)), 2),
                "gap_ci_pp": [None if x is None else round(100 * x, 2)
                              for x in boot_ci(diffs, dd, args.reps, rng)]}

    out["paired_overall"] = paired(lambda x: True)
    out["paired_by_band"] = {}
    for _, _, name in BANDS:
        out["paired_by_band"][name] = paired(lambda x, nm=name: x.get("band") == nm)

    # ---- identity / price counts ------------------------------------------
    out["identity"] = {
        "card_legs": len(card_legs), "matched": matched_n, "unmatched": len(unmatched),
        "price_delta_gt_0.01": int(sum(1 for d in price_deltas if d > 0.01)),
        "price_delta_gt_0.05": int(sum(1 for d in price_deltas if d > 0.05)),
        "mean_abs_price_delta": round(float(np.mean(price_deltas)), 4) if price_deltas else None,
        "out_of_day_pool_rows_excluded": out_of_day_total,
    }
    out["cards"] = dict(locked_counts)
    out["notes"] = {k: sorted(set(v)) for k, v in notes.items() if v}
    out["unmatched_legs"] = unmatched[:50]

    # ---- markdown ----------------------------------------------------------
    def fmt(v):
        return "n/a" if v is None else (f"{v:+.2%}" if isinstance(v, float) else str(v))
    lines = [f"# Exact-identity report ({len(card_days)} card days)", "",
             "| Population | Size | Flat ROI | 95% CI | Stake-weighted |", "|---|---|---|---|---|"]
    pa = out["populations"]
    lines.append(f"| Pool, all buckets | {pa['pool_all_buckets']['resolved']} resolved | "
                 f"{fmt(pa['pool_all_buckets']['flat_roi'])} | {pa['pool_all_buckets']['flat_roi_ci']} | n/a |")
    lines.append(f"| Card legs | {pa['card_legs']['resolved']} resolved | {fmt(pa['card_legs']['flat_roi'])} | "
                 f"{pa['card_legs']['flat_roi_ci']} | n/a |")
    lines.append(f"| Card accas | {pa['card_accas']['resolved']} resolved | {fmt(pa['card_accas']['flat_roi'])} | "
                 f"{pa['card_accas']['flat_roi_ci']} | {fmt(pa['card_accas']['stake_weighted_roi'])} |")
    lines.append(f"| Settled history | {pa['settled_history']['accas']} accas / {pa['settled_history']['days']} days | "
                 f"{fmt(pa['settled_history']['flat_roi'])} | {pa['settled_history']['flat_roi_ci']} | "
                 f"{fmt(pa['settled_history']['stake_weighted_roi_pooled'])} |")
    lines += ["", f"Identity: {out['identity']}", f"Cards: {out['cards']}",
              f"Paired card-minus-pool overall: {out['paired_overall']}", "", "Paired by band:"]
    for name, v in out["paired_by_band"].items():
        lines.append(f"- {name}: {v}")
    lines += ["", "Non-clean days:"]
    for d in sorted(out["notes"]):
        lines.append(f"- {d}: " + "; ".join(out["notes"][d]))
    md = "\n".join(lines) + "\n"
    print(md)
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
    if args.json:
        Path(args.json).write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
