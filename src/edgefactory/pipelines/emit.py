"""
emit.py — certified edges x upcoming events -> edge_picks (+ optional Telegram).
The ONLY consumer-facing pipeline. It refuses to read anything except
certified, non-decayed edges. That's the contract.

    python -m edgefactory.pipelines.emit            # today + tomorrow
"""
import sys
from datetime import datetime, timedelta, timezone

import httpx
import pandas as pd

from .. import db
from ..config import settings


def upcoming_picks(days_ahead: int = 2) -> pd.DataFrame:
    edges = [e for e in db.fetch_all("edges", "*", status="certified")
             if e["decay_verdict"] in ("growing", "stable", "unknown")]
    if not edges:
        return pd.DataFrame()

    now = datetime.now(timezone.utc)
    horizon = now + timedelta(days=days_ahead)
    events = pd.DataFrame(db.fetch_all("events", "id,start_time,status"))
    events["start_time"] = pd.to_datetime(events["start_time"], utc=True)
    events = events[(events["status"] == "scheduled") &
                    (events["start_time"] > now) &
                    (events["start_time"] <= horizon)]
    if events.empty:
        return pd.DataFrame()

    preds = pd.DataFrame(db.fetch_all(
        "latest_predictions", "event_id,market,selection,probability"))
    odds = pd.DataFrame(db.fetch_all(
        "latest_odds", "event_id,market,selection,odds"))
    preds = preds[preds["event_id"].isin(set(events["id"]))]
    df = preds.merge(odds, on=["event_id", "market", "selection"], how="left")
    top = (df.sort_values("probability", ascending=False)
             .groupby(["event_id", "market"], as_index=False).first())

    picks = []
    for e in edges:
        rule = e["rule"]
        bt = rule["btype"]
        if "&" in bt:  # combo
            (ma_sa, mb_sb) = bt.split("&")
            ma, sa = ma_sa.split(":")
            mb, sb = mb_sb.split(":")
            a = top[(top["market"] == ma) & (top["selection"] == sa) &
                    (top["probability"] >= rule["p1_min"])]
            b = top[(top["market"] == mb) & (top["selection"] == sb)]
            if rule["p2_min"]:
                b = b[b["probability"] >= rule["p2_min"]]
            m = a.merge(b, on="event_id", suffixes=("_a", "_b"))
            m["odds_c"] = m["odds_a"] * m["odds_b"]
            if rule["odd_min"]:
                m = m[m["odds_c"] >= rule["odd_min"]]
            for _, r in m.iterrows():
                picks.append({"edge_id": e["id"], "event_id": r["event_id"],
                              "market": f"{ma}&{mb}", "selection": f"{sa}&{sb}",
                              "probability": float(r["probability_a"]),
                              "odds": float(r["odds_c"]) if pd.notna(r["odds_c"]) else None})
        else:
            mk, sel = bt.split(":")
            m = top[(top["market"] == mk) & (top["selection"] == sel) &
                    (top["probability"] >= rule["p1_min"])]
            if rule["odd_min"]:
                m = m[m["odds"] >= rule["odd_min"]]
            for _, r in m.iterrows():
                picks.append({"edge_id": e["id"], "event_id": r["event_id"],
                              "market": mk, "selection": sel,
                              "probability": float(r["probability"]),
                              "odds": float(r["odds"]) if pd.notna(r["odds"]) else None})
    return pd.DataFrame(picks)


def notify_telegram(text: str):
    if not settings.telegram_token or not settings.telegram_chat:
        return
    httpx.post(f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage",
               json={"chat_id": settings.telegram_chat, "text": text,
                     "parse_mode": "Markdown"}, timeout=15)


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    picks = upcoming_picks(days)
    if picks.empty:
        print("No qualifying picks in window.")
        return
    n = db.upsert("edge_picks", picks.to_dict("records"),
                  "edge_id,event_id,market,selection")
    print(f"{n} picks written to ledger")
    notify_telegram(f"🏭 Edge Factory: *{n}* new picks for the next {days} days. "
                    f"Check the ledger.")


if __name__ == "__main__":
    main()
