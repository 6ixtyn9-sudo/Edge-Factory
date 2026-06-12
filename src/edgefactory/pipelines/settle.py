"""
settle.py — market settlement + pick ledger settlement.
1. For finished events without market_results: derive winners per market.
2. For open edge_picks on settled markets: mark won/lost, compute P/L.
3. Auto-bench edges whose live performance falls below certificate.

Market settlement rules are pluggable per market string.
"""
from datetime import datetime, timezone

from .. import db
from ..assay import should_bench
from ..config import settings

# market -> fn(result_row) -> list of winning selections
SETTLERS = {
    "1x2": lambda r: ["home"] if r["outcome_home"] > r["outcome_away"]
           else (["away"] if r["outcome_away"] > r["outcome_home"] else ["draw"]),
    "ou_2.5": lambda r: ["over"] if (r["outcome_home"] + r["outcome_away"]) > 2.5
              else ["under"],
    "btts": lambda r: ["yes"] if r["outcome_home"] > 0 and r["outcome_away"] > 0
            else ["no"],
}


def settle_markets() -> int:
    """Write market_results for finished events that lack them."""
    c = db.client()
    rows = c.rpc("exec_sql", {}).execute() if False else None  # placeholder no-op
    # Portable approach: fetch finished events w/ results, left-anti-join in python
    finished = db.fetch_all("results", "event_id,outcome_home,outcome_away")
    have = {(r["event_id"], r["market"]) for r in db.fetch_all(
        "market_results", "event_id,market")}
    out = []
    for r in finished:
        if r["outcome_home"] is None:
            continue
        for market, fn in SETTLERS.items():
            if (r["event_id"], market) in have:
                continue
            out.append({"event_id": r["event_id"], "market": market,
                        "winning_selections": fn(r)})
    return db.upsert("market_results", out, "event_id,market")


def settle_picks() -> int:
    """Settle open edge_picks against market_results. Combo selections use '&'."""
    open_picks = db.fetch_all("edge_picks", "*", status="open")
    if not open_picks:
        return 0
    mr = {(r["event_id"], r["market"]): set(r["winning_selections"])
          for r in db.fetch_all("market_results", "event_id,market,winning_selections")}

    updates = []
    for p in open_picks:
        legs = p["selection"].split("&")
        markets = p["market"].split("&")
        if len(markets) == 1 and len(legs) > 1:
            markets = markets * len(legs)
        verdicts = []
        for market, sel in zip(markets, legs):
            winners = mr.get((p["event_id"], market))
            if winners is None:
                verdicts = None
                break
            verdicts.append(sel in winners)
        if verdicts is None:
            continue
        won = all(verdicts)
        odds = float(p["odds"] or 0)
        updates.append({
            "id": p["id"], "edge_id": p["edge_id"], "event_id": p["event_id"],
            "market": p["market"], "selection": p["selection"],
            "status": "won" if won else "lost",
            "pl_units": round((odds - 1.0), 4) if won and odds > 1 else
                        (-1.0 if odds > 1 else 0.0),
            "settled_at": datetime.now(timezone.utc).isoformat()})
    return db.upsert("edge_picks", updates, "id")


def auto_bench() -> list[str]:
    """Bench certified edges whose live LB collapsed below certificate."""
    benched = []
    for row in db.fetch_all("edge_bench_check", "*"):
        if should_bench(row["live_wins"], row["live_n"],
                        float(row["certified_hit"]), settings.bench_tolerance):
            db.client().table("edges").update({
                "status": "benched",
                "benched_at": datetime.now(timezone.utc).isoformat(),
                "decay_verdict": "decaying",
            }).eq("id", row["id"]).execute()
            benched.append(row["name"])
    return benched


def main():
    print(f"market_results written: {settle_markets()}")
    print(f"picks settled: {settle_picks()}")
    b = auto_bench()
    print(f"edges auto-benched: {b or 'none'}")


if __name__ == "__main__":
    main()
