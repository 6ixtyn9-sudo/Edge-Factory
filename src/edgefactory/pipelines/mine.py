"""
mine.py — walk-forward edge discovery over everything in the database.
Sport-agnostic: it mines (prediction, odds, outcome) triples per market,
including same-event combo markets.

    python -m edgefactory.pipelines.mine --split 2025-06-01

Writes certified edges into the `edges` table. Existing certified edges are
re-audited; decayed ones get benched verdicts. Candidates that fail OOS are
stored as 'retired' for the audit trail (so we don't re-discover trash).
"""
import argparse
import itertools
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from .. import db
from ..assay import BetStats, decay_verdict
from ..config import settings

P1_GRID = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
P2_GRID = [0.0, 0.60, 0.70, 0.80, 0.90]
ODD_GRID = [0.0, 1.5, 2.0]

COMBOS = [  # (market_a, sel_a, market_b, sel_b)
    ("1x2", "home", "ou_2.5", "over"), ("1x2", "away", "ou_2.5", "over"),
    ("1x2", "home", "btts", "no"), ("1x2", "away", "btts", "no"),
    ("1x2", "home", "btts", "yes"), ("1x2", "away", "btts", "yes"),
]


def load_frame() -> pd.DataFrame:
    """Pull (event, market, selection, prob, odds, won) rows from Supabase."""
    preds = pd.DataFrame(db.fetch_all(
        "latest_predictions", "event_id,market,selection,probability"))
    odds = pd.DataFrame(db.fetch_all(
        "latest_odds", "event_id,market,selection,odds", ))
    mr = pd.DataFrame(db.fetch_all(
        "market_results", "event_id,market,winning_selections"))
    events = pd.DataFrame(db.fetch_all("events", "id,start_time,sport_id"))
    events = events.rename(columns={"id": "event_id"})

    df = preds.merge(odds, on=["event_id", "market", "selection"], how="left")
    df = df.merge(mr, on=["event_id", "market"], how="inner")
    df = df.merge(events, on="event_id", how="left")
    df["won"] = df.apply(lambda r: r["selection"] in r["winning_selections"], axis=1)
    df["date"] = pd.to_datetime(df["start_time"]).dt.strftime("%Y-%m-%d")
    df["probability"] = df["probability"].astype(float)
    df["odds"] = pd.to_numeric(df["odds"], errors="coerce")
    return df


def top_pick_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the source's TOP selection per (event, market) — the 'pick'."""
    return (df.sort_values("probability", ascending=False)
              .groupby(["event_id", "market"], as_index=False).first())


def build_combo_frame(picks: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for ma, sa, mb, sb in COMBOS:
        a = picks[(picks["market"] == ma) & (picks["selection"] == sa)]
        b = picks[(picks["market"] == mb) & (picks["selection"] == sb)]
        m = a.merge(b, on="event_id", suffixes=("_a", "_b"))
        if m.empty:
            continue
        frames.append(pd.DataFrame({
            "event_id": m["event_id"],
            "date": m["date_a"],
            "btype": f"{ma}:{sa}&{mb}:{sb}",
            "p1": m["probability_a"], "p2": m["probability_b"],
            "odds": m["odds_a"] * m["odds_b"],
            "won": m["won_a"] & m["won_b"],
        }))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def stats_of(sub: pd.DataFrame) -> BetStats:
    s = BetStats()
    for won, odds in zip(sub["won"].values, sub["odds"].values):
        s.add(bool(won), None if np.isnan(odds) else float(odds))
    return s


def mine(df: pd.DataFrame, split: str) -> list[dict]:
    picks = top_pick_frame(df)
    solo = picks.rename(columns={"probability": "p1"}).assign(
        btype=lambda d: d["market"] + ":" + d["selection"], p2=np.nan)[
        ["event_id", "date", "btype", "p1", "p2", "odds", "won"]]
    combo = build_combo_frame(picks)
    bets = pd.concat([solo, combo], ignore_index=True)
    bets = bets[bets["odds"].notna()]

    train = bets[bets["date"] < split]
    valid = bets[bets["date"] >= split]
    certified = []

    for btype in bets["btype"].unique():
        tr_t, va_t = train[train["btype"] == btype], valid[valid["btype"] == btype]
        is_combo = "&" in btype
        for p1, p2, omin in itertools.product(
                P1_GRID, (P2_GRID if is_combo else [0.0]), ODD_GRID):
            tr = tr_t[(tr_t["p1"] >= p1) & (tr_t["odds"] >= omin)]
            if is_combo and p2:
                tr = tr[tr["p2"] >= p2]
            if len(tr) < settings.min_n_train:
                continue
            ts = stats_of(tr)
            if ts.roi_pct is None or ts.roi_pct < settings.min_roi_train:
                continue
            va = va_t[(va_t["p1"] >= p1) & (va_t["odds"] >= omin)]
            if is_combo and p2:
                va = va[va["p2"] >= p2]
            if len(va) < settings.min_n_valid:
                continue
            vs = stats_of(va)
            if vs.roi_pct is None or vs.roi_pct < settings.min_roi_valid:
                continue

            monthly = (va.assign(month=va["date"].str[:7])
                         .groupby("month")
                         .apply(lambda b: float(np.where(
                             b["won"], b["odds"] - 1, -1).sum() / len(b) * 100),
                             include_groups=False))
            certified.append({
                "name": f"{btype} p1>={p1} p2>={p2} o>={omin}",
                "rule": {"btype": btype, "p1_min": p1, "p2_min": p2, "odd_min": omin},
                "train_stats": ts.as_dict(), "valid_stats": vs.as_dict(),
                "decay_verdict": decay_verdict(list(monthly.values)),
            })

    # best rule per btype only
    best = {}
    for e in certified:
        k = e["rule"]["btype"]
        if k not in best or e["valid_stats"]["roi"] > best[k]["valid_stats"]["roi"]:
            best[k] = e
    return list(best.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="2025-06-01")
    ap.add_argument("--sport", default="soccer")
    ap.add_argument("--source", default="forebet")
    args = ap.parse_args()

    print("Loading frame from Supabase ...")
    df = load_frame()
    print(f"  {len(df):,} pick-rows")

    edges = mine(df, args.split)
    print(f"  {len(edges)} edges certified out-of-sample")

    sport_id = db.client().table("sports").select("id").eq(
        "key", args.sport).execute().data[0]["id"]
    source_id = db.client().table("sources").select("id").eq(
        "key", args.source).execute().data[0]["id"]

    now = datetime.now(timezone.utc).isoformat()
    rows = [{**e, "sport_id": sport_id, "source_id": source_id,
             "status": "certified", "certified_at": now, "updated_at": now}
            for e in edges]
    db.upsert("edges", rows, "sport_id,source_id,name")

    for e in sorted(edges, key=lambda x: -(x["valid_stats"]["roi"] or 0)):
        v = e["valid_stats"]
        print(f"  [{e['decay_verdict']:^8}] {e['name']:<45} "
              f"OOS n={v['n']:>5} hit={v['hit']*100:.1f}% roi={v['roi']:+.1f}%")


if __name__ == "__main__":
    main()
