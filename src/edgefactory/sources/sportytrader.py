"""Compatibility import for the verified SportyTrader shadow adapter.

The odds-specific implementation lives in ``sportytrader_odds`` so its source
name stays distinct in price boards. Both import paths resolve to the same
module object and state.
"""
from __future__ import annotations

import sys

from . import sportytrader_odds as _implementation

sys.modules[__name__] = _implementation
