"""Source registry. Add a new adapter = import + register here."""
from .afootballreport import AFootballReportSource
from .forebet import ForebetSource
from .scoutingstats import ScoutingStatsSource
from .statarea import StatareaSource
from .vitibet import VitibetSource
from .zulubet import ZulubetSource

SOURCES = {
    ForebetSource.source_key: ForebetSource,
    ZulubetSource.source_key: ZulubetSource,
    StatareaSource.source_key: StatareaSource,
    ScoutingStatsSource.source_key: ScoutingStatsSource,
    VitibetSource.source_key: VitibetSource,
    AFootballReportSource.source_key: AFootballReportSource,
}

# sources with date-addressable history (backfillable)
BACKFILLABLE = {"forebet", "zulubet", "statarea"}


def get_source(key: str):
    if key not in SOURCES:
        raise KeyError(f"Unknown source '{key}'. Registered: {list(SOURCES)}")
    return SOURCES[key]()
