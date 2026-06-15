"""Lightweight market registry for Edge Factory.

Defines which markets the system is allowed to discover and bet on.
Populated from odds adapters (bzzoiro_odds and future sources).

This is the single source of truth for bettable markets.
"""

MARKETS = {
    "1x2": {
        "selections": ["home", "draw", "away"],
        "odds_tier": "low",
        "description": "Full-time match winner",
    },
    "ht_1x2": {
        "selections": ["home", "draw", "away"],
        "odds_tier": "mid",
        "description": "Half-time match winner",
    },
    "ou_2.5": {
        "selections": ["over", "under"],
        "odds_tier": "mid",
        "description": "Full-time over/under 2.5 goals",
    },
    "ht_ou_1.5": {
        "selections": ["over", "under"],
        "odds_tier": "mid",
        "description": "Half-time over/under 1.5 goals",
    },
    "ht_ou_2.5": {
        "selections": ["over", "under"],
        "odds_tier": "high",
        "description": "Half-time over/under 2.5 goals",
    },
    "btts": {
        "selections": ["yes", "no"],
        "odds_tier": "mid",
        "description": "Both teams to score",
    },
}


def get_bettable_markets() -> list[str]:
    """Return list of markets the miner is allowed to test."""
    return list(MARKETS.keys())


def get_market_info(market: str) -> dict:
    """Return metadata for a specific market."""
    return MARKETS.get(market, {})


def get_odds_tier(market: str) -> str:
    """Return the odds tier for a market (low/mid/high)."""
    return MARKETS.get(market, {}).get("odds_tier", "mid")
