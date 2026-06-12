"""
assay.py — the pure math. No I/O, no DB, fully unit-tested.
If these functions are wrong, everything downstream lies. Keep them boring.
"""
import math
from dataclasses import dataclass

WILSON_Z = 1.645  # 95% one-sided

GRADES = [
    ("PLATINUM", 0.85),
    ("GOLD", 0.72),
    ("SILVER", 0.62),
    ("BRONZE", 0.55),
    ("CHARCOAL", 0.0),
]


def wilson_lower_bound(wins: int, n: int, z: float = WILSON_Z) -> float:
    """Worst plausible true win rate given the sample. Small n -> punished."""
    if n == 0:
        return 0.0
    p = wins / n
    denom = 1 + z * z / n
    center = p + z * z / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, (center - spread) / denom)


def grade(rate: float) -> str:
    for name, threshold in GRADES:
        if rate >= threshold:
            return name
    return "CHARCOAL"


@dataclass
class BetStats:
    n: int = 0
    wins: int = 0
    pl_units: float = 0.0   # flat 1u staking
    priced_n: int = 0

    def add(self, won: bool, odds: float | None) -> None:
        self.n += 1
        self.wins += int(won)
        if odds is not None and odds > 1.0:
            self.priced_n += 1
            self.pl_units += (odds - 1.0) if won else -1.0

    @property
    def hit_rate(self) -> float:
        return self.wins / self.n if self.n else 0.0

    @property
    def lb(self) -> float:
        return wilson_lower_bound(self.wins, self.n)

    @property
    def roi_pct(self) -> float | None:
        return self.pl_units / self.priced_n * 100 if self.priced_n else None

    def as_dict(self) -> dict:
        return {
            "n": self.n, "wins": self.wins,
            "hit": round(self.hit_rate, 4), "lb": round(self.lb, 4),
            "roi": round(self.roi_pct, 2) if self.roi_pct is not None else None,
            "grade": grade(self.lb),
        }


def decay_verdict(monthly_roi: list[float]) -> str:
    """Compare first half vs second half of a monthly ROI curve."""
    if len(monthly_roi) < 4:
        return "unknown"
    half = len(monthly_roi) // 2
    first = sum(monthly_roi[:half]) / half
    second = sum(monthly_roi[half:]) / (len(monthly_roi) - half)
    if second > first + 3:
        return "growing"
    if second < first - 8:
        return "dead" if second < 0 else "decaying"
    return "stable"


def wilson_upper_bound(wins: int, n: int, z: float = WILSON_Z) -> float:
    """Best plausible true win rate given the sample."""
    if n == 0:
        return 1.0
    p = wins / n
    denom = 1 + z * z / n
    center = p + z * z / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return min(1.0, (center + spread) / denom)


def should_bench(live_wins: int, live_n: int, certified_hit: float,
                 tolerance: float = 0.05, min_n: int = 40) -> bool:
    """Bench when live performance is SIGNIFICANTLY worse than certificate:
    even the best plausible live rate (Wilson upper bound) sits below
    certified_hit - tolerance. Noise alone can't bench an on-track edge."""
    if live_n < min_n:
        return False
    return wilson_upper_bound(live_wins, live_n) < (certified_hit - tolerance)
