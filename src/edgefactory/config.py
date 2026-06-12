"""Certification gates. These numbers are the law — no edge gets certified
without clearing every one of them on a proper walk-forward split.
"""
from __future__ import annotations

from dataclasses import dataclass
from dotenv import load_dotenv

# Load env once at import time
load_dotenv()


@dataclass(frozen=True)
class Gates:
    min_n_train: int = 400
    min_n_valid: int = 120
    min_roi_train: float = 0.03   # +3% on train
    min_roi_valid: float = 0.00   # at least break-even out-of-sample
    walkforward_split: str = "2025-06-01"
    # consensus-specific
    min_overlap_n: int = 200      # min joined matches before a consensus rule is even scored
    # decay monitoring
    recent_window_days: int = 60
    min_recent_n: int = 30


GATES = Gates()

# "Best odds" inflate ROI vs what a real book pays. Apply this haircut when
# sanity-checking whether an edge survives real-world pricing (~halves ROI).
BEST_ODDS_HAIRCUT = 0.5
