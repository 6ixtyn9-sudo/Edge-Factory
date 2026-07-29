"""Shared normalization utilities.

Important split:
- norm_team()/norm_team_sql() are the legacy 9-char miner join keys. Do not
  change them without re-validating every certified edge.
- norm_entity_team()/norm_league() are richer context/entity keys for purity,
  reporting, and the learned entity registry.
"""
from __future__ import annotations

import re
import unicodedata

# Historical miner/source join noise tokens. Keep byte-compatible in spirit with
# the certified backtests.
_NOISE = re.compile(
    r"\b(fc|cf|sc|ac|cd|ca|club|deportivo|atletico|athletic|real|sporting|"
    r"u17|u18|u19|u20|u21|u23|ii|b|w|women|reserves?|res)\b",
    re.IGNORECASE,
)

_DASHES = str.maketrans({"–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-"})

_ENTITY_NOISE = re.compile(
    r"\b(fc|cf|sc|ac|cd|ca|club|deportivo|atletico|athletic|real|sporting)\b",
    re.IGNORECASE,
)

_ACCENT_FROM = (
    "ÀÁÂÃÄÅĀĂĄÇĆČĎĐÈÉÊËĒĖĘĚÌÍÎÏĪĮİŁÑŃŇÒÓÔÕÖØŌŐŔŘŚŠŞȘŤȚÙÚÛÜŪŮŰŲÝŸŽŹŻ"
    "àáâãäåāăąçćčďđèéêëēėęěìíîïīįıłñńňòóôõöøōőŕřśšşșťțùúûüūůűųýÿžźż"
)
_ACCENT_TO = (
    "AAAAAAAAACCCDDEEEEEEEEIIIIIIILNNNOOOOOOOORRSSSSTTUUUUUUUUYYZZZ"
    "aaaaaaaaacccddeeeeeeeeiiiiiiilnnnoooooooorrssssttuuuuuuuuyyzzz"
)

# Single-char → single-char translation table for fold_ascii.
# NFKD decomposition + combining-mark removal handles most accented Latin
# characters, but several Nordic/extended letters (ø Ø ð Ð Ł ł Đ đ etc.)
# do NOT decompose under NFKD.  Without this table they get silently
# stripped by [^a-z] filters, producing broken keys like "strmsgods"
# for "Strømsgodset" instead of the correct "stromsgod".
_ACCENT_TABLE = str.maketrans(_ACCENT_FROM, _ACCENT_TO)


def fold_ascii(text: object) -> str:
    """Unicode-fold to lowercase ASCII-ish text before punctuation stripping.

    Handles three categories of characters:
    1. Multi-char ligatures (ß Æ Œ) — replaced before NFKD
    2. Single-char accents that NFKD won't decompose (ø Ø Ł ł Đ đ etc.)
       — replaced via _ACCENT_TABLE before NFKD
    3. Standard combining-mark accents (é å ü etc.) — handled by NFKD
       decomposition + combining-char removal
    """
    s = str(text or "").translate(_DASHES)
    s = s.replace("ß", "ss").replace("ẞ", "SS")
    s = s.replace("Æ", "AE").replace("æ", "ae")
    s = s.replace("Œ", "OE").replace("œ", "oe")
    # Apply accent table for characters that NFKD does not decompose.
    # This must happen BEFORE NFKD so that, e.g., "Strømsgodset" →
    # "Stromsgodset" before NFKD processes the rest.
    s = s.translate(_ACCENT_TABLE)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower()


def compact_key(text: object) -> str:
    """ASCII-fold, lowercase, keep alphanumeric only."""
    return re.sub(r"[^a-z0-9]", "", fold_ascii(text))


def norm_team(name: str, width: int = 9) -> str:
    """Legacy team join key used by certified miners and warehouse joins.

    Do not upgrade this to accent-folding in-place: changing it alters historical
    consensus joins and can invalidate certified edge counts.
    """
    s = str(name or "").lower()
    s = _NOISE.sub(" ", s)
    s = re.sub(r"[^a-z]", "", s)
    return s[:width]


def norm_entity_team(name: object, width: int = 24) -> str:
    """Canonical team context key for purity/reporting/entity registry.

    Unlike norm_team(), this folds accents first so context keys do not lose
    letters: América -> america, Nõmme -> nomme.
    """
    s = fold_ascii(name)
    s = _ENTITY_NOISE.sub(" ", s)
    return re.sub(r"[^a-z0-9]", "", s)[:width]


def norm_league(name: object) -> str:
    """Deterministic league text key used as entity fallback."""
    spaced = re.sub(r"[^a-z0-9]+", " ", fold_ascii(name)).strip()
    spaced = re.sub(r"\s+", " ", spaced)
    return spaced or "unknown"


# Same legacy team normalization expressed as a DuckDB SQL expression.
def norm_team_sql(col: str, width: int = 9) -> str:
    noise = (
        r"\b(fc|cf|sc|ac|cd|ca|club|deportivo|atletico|athletic|real|sporting|"
        r"u17|u18|u19|u20|u21|u23|ii|b|w|women|reserves?|res)\b"
    )
    return (
        f"substr(regexp_replace(regexp_replace(lower({col}), '{noise}', ' ', 'g'),"
        f" '[^a-z]', '', 'g'), 1, {width})"
    )


def _sql_ascii_fold(expr: str) -> str:
    out = expr
    for old, new in (("ß", "ss"), ("ẞ", "SS"), ("Æ", "AE"), ("æ", "ae"), ("Œ", "OE"), ("œ", "oe")):
        out = f"replace({out}, '{old}', '{new}')"
    for old, new in zip(_ACCENT_FROM, _ACCENT_TO):
        out = f"replace({out}, '{old}', '{new}')"
    return f"lower({out})"


def norm_entity_team_sql(col: str, width: int = 24) -> str:
    noise = (
        r"\b(fc|cf|sc|ac|cd|ca|club|deportivo|atletico|athletic|real|sporting)\b"
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


def char_ngram_similarity(s1: str, s2: str, n: int = 2) -> float:
    """Jaccard character n-gram similarity between two strings."""
    def _ngrams(s: str) -> set[str]:
        clean = re.sub(r"[^a-z0-9]", "", s.lower())
        return {clean[i:i+n] for i in range(len(clean) - n + 1)} if len(clean) >= n else set()
    g1 = _ngrams(s1)
    g2 = _ngrams(s2)
    if not g1 or not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)
