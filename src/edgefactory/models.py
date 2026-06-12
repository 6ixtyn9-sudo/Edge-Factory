"""
Normalized data contracts between adapters and pipelines.
An adapter's ONLY job: turn its site's mess into these shapes.
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class NormalizedPrediction:
    market: str          # '1x2', 'ou_2.5', 'btts', 'ml', ...
    selection: str       # 'home', 'away', 'draw', 'over', 'under', 'yes', 'no'
    probability: float   # 0..1
    extra: dict = field(default_factory=dict)


@dataclass
class NormalizedOdds:
    market: str
    selection: str
    odds: float          # decimal
    bookmaker: str = "best"


@dataclass
class NormalizedResult:
    outcome_home: float | None
    outcome_away: float | None
    score_data: dict = field(default_factory=dict)
    status: str = "finished"          # finished | void


@dataclass
class NormalizedEvent:
    """One event from one source, fully self-contained."""
    source_ref: str                   # adapter's own event id
    sport: str                        # 'soccer', 'tennis', ...
    competition_name: str
    competition_ref: str
    country: str
    home_name: str
    home_ref: str
    away_name: str
    away_ref: str
    start_time: datetime
    predictions: list[NormalizedPrediction] = field(default_factory=list)
    odds: list[NormalizedOdds] = field(default_factory=list)
    result: NormalizedResult | None = None
