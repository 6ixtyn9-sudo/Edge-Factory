"""Shared identity folding for team and league names.

Provenance: 2026-09-22 Dagenham incident. Two voter spellings of one
fixture ("Dagenham & Redbridge" vs "Dagenham and Redbridge", league
"FA" vs "England,Fa Cup") produced two distinct pick rows that rode
together into one acca card. The 782f3f5 emergency guard dedups at
slip-planning time; this module applies the same fold at the identity
seam so the duplicates die at capture and so every downstream consumer
(slips, purity contexts, diagnostics) shares ONE definition of
"same fixture" / "same league".

Hard rules:

1. FOLDS ONLY, NO FUZZ. Deterministic text folding plus an explicit,
   evidence-seeded alias table. Nothing here guesses similarity; two
   different real entities must never collapse into one key.
2. ADDITIVE WIRING. Callers keep their legacy lookup order intact;
   folded forms/aliases only add coverage that previously returned
   UNKNOWN.
3. SCOPE. Used for *identity* seams: voter-row indexing, purity/entity
   canonicalisation, slip dedup. Odds/price-matching keys
   (alias_fuzzy quarantine surface) are deliberately out of scope.
4. The research ml-fade ledger identity fold lives in
   edgefactory/ml_fade_research.py and stays frozen there for ledger
   reconciliation stability; this module mirrors its fold semantics
   (``&`` -> ``and``, punctuation collapse) plus accent folding.
"""

from __future__ import annotations

import re

from .util import fold_ascii

_WS_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9 ]+")


def fold_identity_words(name: object) -> str:
    """ASCII-fold, lowercase, ``&`` -> ``and``, punctuation -> space.

    Total and deterministic; idempotent; invariant under ``&`` vs ``and``
    spellings and under punctuation/case choice. Output is a
    space-separated word string (empty string for empty input).
    """
    s = fold_ascii(name).replace("&", " and ")
    s = _NON_ALNUM_RE.sub(" ", s)
    return _WS_RE.sub(" ", s).strip()


def team_identity_words(name: object) -> str:
    """Team identity words with the glue token ``and`` removed.

    ``Dagenham & Redbridge`` and ``Dagenham and Redbridge`` both become
    ``dagenham redbridge``. ``and`` is only ever produced by the ``&``
    fold in real club names here; dropping it as a standalone token is
    the exact unification the incident required. Compound words that
    merely contain ``and`` (e.g. ``Wanderers``) are untouched because
    removal is word-level.
    """
    words = [w for w in fold_identity_words(name).split() if w != "and"]
    return " ".join(words)


def fold_league_identity(name: object) -> str:
    """League fold: identity words, no token dropping."""
    return fold_identity_words(name)


# Explicit alias pairs, each PROVEN same-league by archive evidence:
# the same (date, folded home, folded away) fixture appearing under both
# spellings in the same slate. Targets are the purity-registry keys so
# pool/verdict lookups resolve.
LEAGUE_ALIASES: dict[str, str] = {
    "england fa cup": "fa",  # 2026-09-22 Dagenham vs Waltham Abbey under both
    "england national league south": "enterprise national league south",
}


def canonical_league_key(name: object) -> str:
    """Fold a raw league label, then apply explicit evidence aliases."""
    folded = fold_league_identity(name)
    return LEAGUE_ALIASES.get(folded, folded)
