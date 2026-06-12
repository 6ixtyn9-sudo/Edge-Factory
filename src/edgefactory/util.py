"""Shared utilities: team-name normalization for cross-source matching."""
from __future__ import annotations

import re

# tokens that differ between sources but mean nothing for identity
_NOISE = re.compile(
    r"\b(fc|cf|sc|ac|cd|ca|club|deportivo|atletico|athletic|real|sporting|"
    r"u17|u18|u19|u20|u21|u23|ii|b|w|women|reserves?|res)\b",
    re.IGNORECASE,
)


def norm_team(name: str, width: int = 9) -> str:
    """Normalize a team name to a cross-source join key.

    Strategy (matches the certified consensus backtests):
    lowercase -> strip noise tokens -> keep alpha only -> first `width` chars.
    """
    s = name.lower()
    s = _NOISE.sub(" ", s)
    s = re.sub(r"[^a-z]", "", s)
    return s[:width]


# Same normalization expressed as a DuckDB SQL expression on a column name.
def norm_team_sql(col: str, width: int = 9) -> str:
    noise = (
        r"\b(fc|cf|sc|ac|cd|ca|club|deportivo|atletico|athletic|real|sporting|"
        r"u17|u18|u19|u20|u21|u23|ii|b|w|women|reserves?|res)\b"
    )
    return (
        f"substr(regexp_replace(regexp_replace(lower({col}), '{noise}', ' ', 'g'),"
        f" '[^a-z]', '', 'g'), 1, {width})"
    )
