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


def ledger_team_key(name: object, width: int = 9) -> str:
    """Accent-safe team key for operational pick-ledger identity.

    This deliberately wraps, rather than changes, ``norm_team``. Certified
    miner joins must retain their historical byte-compatible normalization,
    while operational ledgers must treat spelling variants such as
    ``Nordsjælland`` and ``Nordsjaelland`` as the same team.
    """
    return norm_team(fold_ascii(name), width=width)


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


# ---------------------------------------------------------------------------
# Honest rule labels (single source for every render path).
#
# Archived ledger rows may carry a display_rule computed by older code (e.g.
# pre-qualifier labels like "2WAY-UNANIMOUS>=60" for the bc-confirms variant).
# The merge layer retains rows exactly, so a stored display can stay stale
# forever. The exact miner rule string is the ground truth — always derive the
# label from it at render time instead of trusting a stored display.
# ---------------------------------------------------------------------------

_RULE_NWAY_RE = re.compile(r"(\d+)\s*way")
_RULE_THR_RE = re.compile(r"avg_p\s*>=?\s*([\d.]+)")


def display_rule_label(market: str, n_way: int, threshold: float, rule: str = "") -> str:
    """Short honest label derived from the exact miner rule.

    Qualifiers (bc-confirms / home-only / away-only / min_p / odds-) are
    shown so a variant can never hide behind the plain unanimous name:
    e.g. rule "2way+bc-confirms avg_p>=60" renders as
    "2WAY-UNANIMOUS+BC-CONFIRMS≥60". Mirrors picks_today.display_rule;
    keep in sync with that wrapper (which delegates here).
    """
    qual = ""
    if rule:
        rl = rule.lower()
        toks = []
        if "bc-confirms" in rl:
            toks.append("BC-CONFIRMS")
        if "home-only" in rl:
            toks.append("HOME-ONLY")
        if "away-only" in rl:
            toks.append("AWAY-ONLY")
        if "min_p" in rl:
            toks.append("MIN-P")
        if "odds-" in rl:
            toks.append("ODDS")
        if toks:
            qual = "+" + "+".join(toks)
    if "ml-meta" in market.lower() or "ml-meta" in rule.lower() or n_way == 0:
        return f"ML-META≥{threshold:.0f}"
    if market == "1x2":
        return f"{n_way}WAY-UNANIMOUS{qual}≥{threshold:.0f}"
    if market == "ou_2.5":
        return f"OU25-UNANIMOUS-{n_way}WAY{qual}≥{threshold:.0f}"
    if market == "btts":
        return f"BTTS-UNANIMOUS-{n_way}WAY{qual}≥{threshold:.0f}"
    return f"{market.upper()}-{n_way}WAY{qual}≥{threshold:.0f}"


def honest_display_label(pick: dict) -> str:
    """Render a pick's rule label from the EXACT rule string.

    Falls back to the stored display/rule for unparseable rules (ml-meta,
    legacy display-string rows) — never worse than the stored label.
    """
    rule = str(pick.get("edge_rule") or pick.get("rule") or "").strip()
    market = pick.get("market") or "1x2"
    if rule:
        mn, mt = _RULE_NWAY_RE.search(rule), _RULE_THR_RE.search(rule)
        if mn and mt:
            try:
                return display_rule_label(market, int(mn.group(1)), float(mt.group(1)), rule)
            except (TypeError, ValueError):
                pass
    return pick.get("display_rule") or rule or "?"


def heal_ledger_labels(ledger: list) -> int:
    """Rewrite stored display_rule from the exact rule string (self-heal).

    The merge layer retains archived rows exactly, so rows archived by older
    code can carry a stale display_rule forever (e.g. pre-qualifier labels
    like "2WAY-UNANIMOUS>=60" for the bc-confirms variant). This derives the
    honest label from rule/edge_rule and writes it back, making the STORED
    data truthful too — not just the render. It only touches the display
    field; never rule, odds, result, or any performance field. Idempotent:
    rows that already match are left untouched. Returns count healed.
    """
    healed = 0
    for p in ledger:
        if not isinstance(p, dict):
            continue
        stored = p.get("display_rule")
        derived = honest_display_label(p)
        if derived != "?" and derived != stored:
            p["display_rule"] = derived
            healed += 1
    return healed
