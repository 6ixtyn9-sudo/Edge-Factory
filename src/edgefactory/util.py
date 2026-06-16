"""Shared normalization utilities for cross-source matching and context keys.

The miner joins, odds enrichment, and purity assay all depend on stable text
keys. Keep this module dependency-free: only Python stdlib is allowed here.
"""
from __future__ import annotations

import re
import unicodedata

# Tokens that differ between sources but usually do not identify the team.
# Keep this conservative: over-stripping is worse than leaving a harmless token.
_NOISE = re.compile(
    r"\b(fc|cf|sc|afc|ac|cd|ca|club|deportivo|atletico|athletic|real|sporting|"
    r"fk|sk|if|bk|nk|kk|sv|vfl|vfb|ssc|asd|us|ud|sd|cs|as|ac|"
    r"u17|u18|u19|u20|u21|u23|ii|iii|b|w|women|ladies|reserves?|res)\b",
    re.IGNORECASE,
)

_DASHES = str.maketrans({"–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-"})

# Single-character Latin folds for DuckDB SQL translate(). Python uses
# unicodedata, but warehouse SQL needs an explicit equivalent.
_ACCENT_FROM = (
    "ÀÁÂÃÄÅĀĂĄÆÇĆČĎĐÈÉÊËĒĖĘĚÌÍÎÏĪĮİŁÑŃŇÒÓÔÕÖØŌŐŒŔŘŚŠŞȘŤȚÙÚÛÜŪŮŰŲÝŸŽŹŻ"
    "àáâãäåāăąæçćčďđèéêëēėęěìíîïīįıłñńňòóôõöøōőœŕřśšşșťțùúûüūůűųýÿžźż"
)
_ACCENT_TO = (
    "AAAAAAAAAACCCDDEEEEEEEEIIIIIIILNNNOOOOOOOOORRSSSSTTUUUUUUUUYYZZZ"
    "aaaaaaaaaacccddeeeeeeeeiiiiiiilnnnooooooooorrrssssttuuuuuuuuyyzzz"
)



def fold_ascii(text: object) -> str:
    """Lowercase-ish ASCII fold preserving letters before punctuation stripping.

    This fixes keys like:
      América Mineiro -> america mineiro, not amrica mineiro
      Nõmme United    -> nomme united, not nmme united
    """
    s = str(text or "").translate(_DASHES)
    s = s.replace("ß", "ss").replace("ẞ", "SS")
    s = s.replace("Æ", "AE").replace("æ", "ae")
    s = s.replace("Œ", "OE").replace("œ", "oe")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower()


def compact_key(text: object) -> str:
    """ASCII-fold, lowercase, keep alphanumeric only."""
    return re.sub(r"[^a-z0-9]", "", fold_ascii(text))


def norm_team(name: str, width: int = 9) -> str:
    """Normalize a team name to a cross-source join/context key.

    The previous 9-char key stripped accents before folding, so names like
    América/Nõmme lost meaningful letters. This version transliterates first,
    strips source-noise tokens, keeps alphanumerics, applies common aliases, and
    keeps the historical 9-character width so certified miner joins do not drift.
    """
    s = fold_ascii(name)
    s = _NOISE.sub(" ", s)
    key = re.sub(r"[^a-z0-9]", "", s)
    return key[:width]


def norm_league(name: object) -> str:
    """Deterministic league text key used as fallback by entities.py.

    Alias/canonical merging belongs in edgefactory.entities via manual overrides
    and localdata/entity_registry.json. This function only folds text safely.
    """
    spaced = re.sub(r"[^a-z0-9]+", " ", fold_ascii(name)).strip()
    spaced = re.sub(r"\s+", " ", spaced)
    return spaced or "unknown"


def _sql_ascii_fold(expr: str) -> str:
    # DuckDB has no Python unicodedata equivalent. Build a deterministic
    # replace-chain that handles multi-character folds and common Latin accents.
    out = expr
    for old, new in (("ß", "ss"), ("ẞ", "SS"), ("Æ", "AE"), ("æ", "ae"), ("Œ", "OE"), ("œ", "oe")):
        out = f"replace({out}, '{old}', '{new}')"
    for old, new in zip(_ACCENT_FROM, _ACCENT_TO):
        out = f"replace({out}, '{old}', '{new}')"
    return f"lower({out})"


# Same team normalization expressed as a DuckDB SQL expression on a column name.
def norm_team_sql(col: str, width: int = 9) -> str:
    noise = (
        r"\b(fc|cf|sc|afc|ac|cd|ca|club|deportivo|atletico|athletic|real|sporting|"
        r"fk|sk|if|bk|nk|kk|sv|vfl|vfb|ssc|asd|us|ud|sd|cs|as|ac|"
        r"u17|u18|u19|u20|u21|u23|ii|iii|b|w|women|ladies|reserves?|res)\b"
    )
    folded = _sql_ascii_fold(col)
    return (
        f"substr(regexp_replace(regexp_replace({folded}, '{noise}', ' ', 'g'),"
        f" '[^a-z0-9]', '', 'g'), 1, {width})"
    )


def norm_league_sql(col: str) -> str:
    folded = _sql_ascii_fold(f"COALESCE({col}, '')")
    compact = f"regexp_replace({folded}, '[^a-z0-9]+', ' ', 'g')"
    compact = f"trim(regexp_replace({compact}, '\\s+', ' ', 'g'))"
    return f"CASE WHEN {compact} = '' THEN 'unknown' ELSE {compact} END"
