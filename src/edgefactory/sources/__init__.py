from . import forebet
from . import zulubet
from . import statarea
from . import predictz
from . import windrawwin
from . import scoutingstats
from . import vitibet
from . import afootballreport
from . import betclan
from . import freesupertips
from . import bettingclosed
from . import bzzoiro
from . import bzzoiro_odds
from . import theoddsapi


# Re-export registry: bare submodule imports above are the package surface;
# __all__ marks them as intentional exports (pyflakes-clean).
__all__ = [
    "forebet",
    "zulubet",
    "statarea",
    "predictz",
    "windrawwin",
    "scoutingstats",
    "vitibet",
    "afootballreport",
    "betclan",
    "freesupertips",
    "bettingclosed",
    "bzzoiro",
    "bzzoiro_odds",
    "theoddsapi",
]
