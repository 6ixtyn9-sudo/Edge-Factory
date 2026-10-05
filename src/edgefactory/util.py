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
from datetime import date, datetime

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


def norm_team_legacy(name: str, width: int = 9) -> str:
    """Pre-2026-10-05 team join key: diacritics DELETED, not transliterated.

    Frozen byte-for-byte. Historical artefacts (settled-result exports,
    warehouse caches, archived ledgers) were written under this key, so
    readers keep it available as a SECOND lookup key alongside the fixed
    ``norm_team``. Never use it to write new keys.
    """
    s = str(name or "").lower()
    s = _NOISE.sub(" ", s)
    s = re.sub(r"[^a-z]", "", s)
    return s[:width]


def norm_team(name: str, width: int = 9) -> str:
    """Team join key used by miners, warehouse joins and settlement.

    2026-10-05 fix: the input is ASCII-FOLDED (transliterated) first, so
    accented names keep their letters: "Türkiye" -> ``turkiye`` (was
    ``trkiye``), "Beşiktaş" -> ``besiktas`` (was ``beikta``), "Atlético"
    -> ``atletico``. Deleting diacritics produced keys that joined to
    nothing and disagreed with :func:`ledger_team_key`, splitting one real
    fixture into two identities.

    This is a transliteration-only change: no fuzzy matching, no aliasing.
    The frozen pre-fix behaviour remains available as
    :func:`norm_team_legacy` for reader-side dual-key lookups against data
    persisted before the fix.
    """
    s = fold_ascii(name)
    s = _NOISE.sub(" ", s)
    s = re.sub(r"[^a-z]", "", s)
    return s[:width]


# ---------------------------------------------------------------------------
# Curated exonym / spelling alias layer (explicit, reviewed, NEVER fuzzy).
#
# Source of truth: Config/entity_overrides.json -> "teams". Entries map a
# raw spelling to ONE canonical display name; both spellings therefore
# collapse onto a single canonical key. Transliteration alone cannot join
# exonyms such as Türkiye/Turkey (the 2022 rename) or Czechia/Czech
# Republic, so they are curated here rather than guessed.
# ---------------------------------------------------------------------------

_OVERRIDES_CANDIDATE_PATHS = ("Config/entity_overrides.json", "config/entity_overrides.json")


def _overrides_path():
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    for rel in _OVERRIDES_CANDIDATE_PATHS:
        p = root / rel
        if p.exists():
            return p
    return None


_TEAM_ALIAS_CACHE: dict[str, str] | None = None

# Set when the curated alias config could not be loaded, so callers and
# tests can assert the degradation was announced rather than silent.
ALIAS_CONFIG_WARNINGS: list[str] = []


def _warn_alias_config(detail: str) -> None:
    """Announce loudly that the curated alias layer is NOT in effect.

    Degrading to pre-alias behaviour is safe (keys simply stop merging
    exonyms); degrading SILENTLY is not, because every Turkiye/Turkey-class
    fixture then splits again with no operator signal. Never half-applied:
    the table is all-or-nothing.
    """
    import sys as _sys

    msg = ("!! TEAM ALIAS CONFIG UNAVAILABLE - running with ZERO curated "
           f"aliases (exonym fixtures WILL split): {detail}")
    ALIAS_CONFIG_WARNINGS.append(msg)
    print(msg, file=_sys.stderr)


def team_alias_table() -> dict[str, str]:
    """Curated raw-spelling -> canonical-name team aliases (cached).

    Keys are indexed in several deterministic key spaces (raw text,
    ASCII-folded text, compact key, fixed and legacy norm_team keys) so a
    curated entry resolves whichever spelling a source emits.
    """
    global _TEAM_ALIAS_CACHE
    if _TEAM_ALIAS_CACHE is not None:
        return _TEAM_ALIAS_CACHE
    import json

    table: dict[str, str] = {}
    path = _overrides_path()
    if path is None:
        _warn_alias_config("Config/entity_overrides.json not found")
    if path is not None:
        try:
            data = json.loads(path.read_text())
            teams = data.get("teams") if isinstance(data, dict) else None
            if not isinstance(teams, dict):
                _warn_alias_config(f"{path}: no usable 'teams' object")
        except Exception as exc:
            _warn_alias_config(f"{path}: unreadable/malformed JSON ({exc})")
            teams = None
        if isinstance(teams, dict):
            for raw, canonical in teams.items():
                canon = str(canonical or "").strip()
                if not canon:
                    continue
                for key in (
                    str(raw),
                    fold_ascii(raw),
                    compact_key(raw),
                    norm_team(str(raw), width=64),
                    norm_team_legacy(str(raw), width=64),
                ):
                    if key:
                        table.setdefault(key, canon)
    _TEAM_ALIAS_CACHE = table
    return table


def clear_team_alias_cache() -> None:
    global _TEAM_ALIAS_CACHE
    _TEAM_ALIAS_CACHE = None
    ALIAS_CONFIG_WARNINGS.clear()


def resolve_team_alias(name: object) -> tuple[str, str | None]:
    """Return ``(canonical_name, matched_alias_key)`` for a raw team name.

    ``matched_alias_key`` is ``None`` when no curated alias applied — the
    raw name is then returned unchanged. Deterministic dictionary lookup
    only; nothing here guesses similarity.
    """
    raw = str(name or "")
    table = team_alias_table()
    for key in (raw, fold_ascii(raw), compact_key(raw),
                norm_team(raw, width=64), norm_team_legacy(raw, width=64)):
        if key and key in table:
            return table[key], key
    return raw, None


# ---------------------------------------------------------------------------
# Distinct-entity (squad) markers.
#
# "Turkey" and "Turkey U21" are DIFFERENT teams that play on the same day,
# in the same market, often with the same selection. The legacy noise
# regex deletes these tokens, so both sides key as "turkey" — identity
# collapse in the dangerous direction. These tokens are therefore carried
# into the canonical key as an explicit suffix and act as a hard veto on
# any merge between names whose markers differ.
# ---------------------------------------------------------------------------

_SQUAD_MARKERS: dict[str, str] = {}
for _age in range(14, 24):
    _SQUAD_MARKERS[f"u{_age}"] = f"u{_age}"
    _SQUAD_MARKERS[f"u{_age}s"] = f"u{_age}"
for _tok in ("b", "ii"):
    _SQUAD_MARKERS[_tok] = "b"
for _tok in ("iii", "c"):
    _SQUAD_MARKERS[_tok] = "c"
for _tok in ("w", "women", "womens", "ladies", "feminine", "femenino", "fem"):
    _SQUAD_MARKERS[_tok] = "w"
for _tok in ("res", "reserve", "reserves"):
    _SQUAD_MARKERS[_tok] = "res"
# NB: "junior(s)" is deliberately NOT a marker — it is part of real senior
# club names (Boca Juniors, Argentinos Juniors, Barnsley?); only
# unambiguous squad words are listed.
for _tok in ("youth", "academy"):
    _SQUAD_MARKERS[_tok] = "youth"


# Curated real clubs whose name BEGINS with what looks like a squad
# marker. Explicit list, never a heuristic: "W Connection" (Trinidad) is a
# senior men's club, not a women's side; "B 1903" and "B36 Torshavn" are
# Danish/Faroese club names. Compared on the folded name.
MARKER_EXEMPT_NAMES: frozenset[str] = frozenset({
    "w connection", "w connection fc",
    "b 1903", "b 1903 copenhagen", "b 1908", "b 68", "b 71", "b 36",
    "b36", "b36 torshavn", "b68 toftir", "b71 sandoy",
})


def squad_markers(name: object) -> frozenset[str]:
    """Distinct-entity markers carried by a raw team name.

    Word-level only: ``Wanderers`` is not ``W``, ``Boca`` is not ``B``.
    Returns a (possibly empty) frozenset of canonical marker tokens.
    """
    folded = re.sub(r"[^a-z0-9 ]", " ", fold_ascii(name))
    folded = re.sub(r"\s+", " ", folded).strip()
    if folded in MARKER_EXEMPT_NAMES:
        return frozenset()
    words = re.findall(r"[a-z0-9]+", folded)
    return frozenset(_SQUAD_MARKERS[w] for w in words if w in _SQUAD_MARKERS)


def squad_marker_suffix(name: object) -> str:
    markers = squad_markers(name)
    return ("_" + "_".join(sorted(markers))) if markers else ""


def markers_conflict(a: object, b: object) -> bool:
    """True when two names denote different squads of (possibly) one club."""
    return squad_markers(a) != squad_markers(b)


# Curated, explicit abbreviation expansions used ONLY when comparing two
# names for same-club linkage (never when building a key). Deterministic
# dictionary, no similarity: "Drogheda Utd" and "Drogheda United" are one
# club; "Launceston City" and "Launceston United" still are not.
TEAM_TOKEN_EXPANSIONS: dict[str, str] = {
    "utd": "united", "unt": "united",
    "cty": "city",
    "ath": "athletic", "athl": "athletic",
    "dep": "deportivo", "depor": "deportivo",
    "spt": "sporting", "sptg": "sporting",
    "rov": "rovers", "rovs": "rovers",
    "wdrs": "wanderers", "wand": "wanderers",
    "cf": "", "fc": "",
    "mgladbach": "monchengladbach", "gladbach": "monchengladbach",
    "utdd": "united",
}


def expand_team_token(token: str) -> str:
    return TEAM_TOKEN_EXPANSIONS.get(token, token)


_SCRIPT_RANGES = (
    ("cyrillic", 0x0400, 0x04FF),
    ("greek", 0x0370, 0x03FF),
)


def script_anomaly(name: object) -> str | None:
    """Flag a predominantly-Latin name carrying homoglyph codepoints.

    ``Sp\u0430rt\u0430k`` (Cyrillic a) is visually identical to ``Spartak``
    but folds to ``sprtk``: one feed emitting it silently reproduces the
    duplicate-fixture incident. Transliteration is deliberately NOT
    attempted here (it would need a dependency and would be a guess) —
    this is a visibility tripwire: the row is flagged, never auto-merged.
    """
    text = str(name or "")
    latin = sum(1 for ch in text if "a" <= ch.lower() <= "z")
    for label, lo, hi in _SCRIPT_RANGES:
        foreign = sum(1 for ch in text if lo <= ord(ch) <= hi)
        if foreign and latin:
            return f"mixed_script_{label}"
    return None


MIN_IDENTITY_KEY_LEN = 3


# Out-of-alphabet sentinel. Keys are built from ``[a-z0-9]`` only, so a
# marker character that can NEVER appear in a normalized name is the only
# safe way to distinguish a sentinel from a real club. A plain "deg"
# string prefix was wrong: the real Swedish club ``Degerfors`` keys to
# ``degerfors`` and was classified as degenerate, which made
# ``Degerfors IF`` refuse to merge with ``Degerfors`` — the original
# duplicate-leg incident, reintroduced by the sentinel itself.
DEGENERATE_KEY_PREFIX = "deg~"

# Sentinels written by earlier builds of this branch used the ambiguous
# bare "deg" + 8 hex digits form. Recognized on read, never written.
_LEGACY_DEGENERATE_RE = re.compile(r"^deg[0-9a-f]{8}$")


def _degenerate_key(name: object) -> str:
    """Stable, unique, NON-EMPTY placeholder for an unusable team key.

    An empty key matches every other empty key, so ``Athletic Club``,
    ``Sporting Club`` and every Cyrillic/Greek name would share one
    identity. Instead each raw spelling gets its own marked key: distinct
    teams stay distinct (fail-closed), and the ``deg`` prefix tells every
    consumer the identity is not trustworthy.
    """
    import hashlib

    seed = re.sub(r"\s+", " ", fold_ascii(name)).strip() or str(name or "")
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8]
    return f"{DEGENERATE_KEY_PREFIX}{digest}"


def is_degenerate_team_key(key: object) -> bool:
    """True when a normalized key is too short to identify a team.

    ``Athletic Club`` and ``Sporting Club`` normalize to ``""`` (every word
    is a structure token); non-Latin scripts (Cyrillic, Greek) are deleted
    rather than transliterated and also collapse to ``""`` or a single
    stray character. Such keys match EVERYTHING, so callers must refuse to
    use them for identity. Mirrors the fail-closed guard that
    ``ml_fade_research.event_key`` already applies.
    """
    base = str(key or "").split("_")[0]
    if base.startswith(DEGENERATE_KEY_PREFIX) and len(base) > len(DEGENERATE_KEY_PREFIX):
        return True
    if _LEGACY_DEGENERATE_RE.match(base):  # pre-"deg~" sentinel, read-side only
        return True
    return len(base) < MIN_IDENTITY_KEY_LEN


def canonical_team_key(name: object, width: int = 9) -> str:
    """Canonical operational team key.

    Transliteration + curated explicit aliases, with any distinct-entity
    marker (U21/B/W/Reserves/...) preserved as a suffix so a senior side
    and its youth/reserve/women's squad can never share an identity.
    """
    canonical, _matched = resolve_team_alias(name)
    base = norm_team(canonical, width=width)
    if len(base) < MIN_IDENTITY_KEY_LEN:
        # Numeric club names ("B 1903", "FC 08 Homburg") lose their only
        # distinctive token to the [^a-z] filter. Fall back to the
        # alphanumeric compact key BEFORE the sentinel: it is a real,
        # stable identity, so "B 1903" and "B 1903 Copenhagen" can still
        # be linked instead of both being refused as untrustworthy.
        alnum = compact_key(canonical)
        if len(alnum) >= MIN_IDENTITY_KEY_LEN and any(c.isdigit() for c in alnum):
            return alnum[:width] + squad_marker_suffix(name)
        # never emit an empty/1-char ledger key component
        return _degenerate_key(name) + squad_marker_suffix(name)
    # markers come from the RAW name: the curated alias canonicalizes the
    # club, never the squad.
    return base + squad_marker_suffix(name)


def explain_team_key(name: object, width: int = 9) -> dict[str, object]:
    """Debug view of the key derivation (alias application is never silent)."""
    canonical, matched = resolve_team_alias(name)
    return {
        "raw": str(name or ""),
        "folded": fold_ascii(name),
        "norm_team": norm_team(str(name or ""), width=width),
        "norm_team_legacy": norm_team_legacy(str(name or ""), width=width),
        "alias_matched_key": matched,
        "alias_canonical_name": canonical if matched else None,
        "canonical_team_key": norm_team(canonical, width=width),
        "alias_source": "Config/entity_overrides.json:teams" if matched else None,
    }


def ledger_team_key(name: object, width: int = 9) -> str:
    """Canonical team key for operational pick-ledger / fixture identity.

    Transliterates (so ``Nordsjælland`` == ``Nordsjaelland``) and applies
    the curated alias layer (so ``Türkiye`` == ``Turkey``). Identical to
    :func:`canonical_team_key`; kept as the historical call name used by
    the ledgers and the shadow fixture identity.
    """
    return canonical_team_key(name, width=width)


def research_ledger_team_key(name: object, width: int = 9) -> str:
    """FROZEN pre-2026-10-05 operational key: transliteration, NO aliases.

    Byte-identical to what ``ledger_team_key`` returned before the curated
    alias layer existed. The ml-fade RESEARCH ledger persists ``event_key``
    strings built from this key and reconciles against them across runs,
    so its identity must never drift (see edgefactory/identity.py rule 4).
    Operational identity seams use ``canonical_team_key`` instead.
    """
    return norm_team_legacy(fold_ascii(name), width=width)


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


def strip_retired_top_scores(comment: object) -> str:
    """Remove the retired ``Top Scores`` tail from a statistical comment.

    Historical archives remain byte-unchanged for audit provenance. Human
    renderers call this helper so legacy rows stop displaying the retired
    exact-score surface immediately.
    """
    text = str(comment or "")
    return re.sub(r"\s*\|\s*Top Scores:\s*.*$", "", text, flags=re.IGNORECASE).strip()


_NORM_TEAM_SQL_NOISE = (
    r"\b(fc|cf|sc|ac|cd|ca|club|deportivo|atletico|athletic|real|sporting|"
    r"u17|u18|u19|u20|u21|u23|ii|b|w|women|reserves?|res)\b"
)


def norm_team_sql_legacy(col: str, width: int = 9) -> str:
    """SQL mirror of :func:`norm_team_legacy` (diacritics deleted). Frozen."""
    return (
        f"substr(regexp_replace(regexp_replace(lower({col}), '{_NORM_TEAM_SQL_NOISE}', ' ', 'g'),"
        f" '[^a-z]', '', 'g'), 1, {width})"
    )


# Same team normalization expressed as a DuckDB SQL expression. Must stay in
# lockstep with the Python norm_team() — including the 2026-10-05 ASCII fold,
# otherwise warehouse-side and Python-side keys disagree on accented names.
def norm_team_sql(col: str, width: int = 9) -> str:
    folded = _sql_ascii_fold(col)
    return (
        f"substr(regexp_replace(regexp_replace({folded}, '{_NORM_TEAM_SQL_NOISE}', ' ', 'g'),"
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


_KO_ISO_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
_KO_DMY_RE = re.compile(
    r"^(\d{1,2})[./\-](\d{1,2})(?:[./\-](\d{2,4}))?(?:[ ,T]+\d{1,2}:\d{2}(?::\d{2})?)?\s*$"
)


def _kickoff_year(fallback_date: str | None) -> int:
    if fallback_date:
        try:
            return int(str(fallback_date)[:4])
        except (TypeError, ValueError):
            pass
    return datetime.now().year


def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def kickoff_date(value: object, fallback_date: str | None = None) -> str | None:
    """Resolve the calendar date of a raw source kickoff string, or None.

    Source kickoffs arrive in a format zoo. This resolves ONLY the calendar
    date (the archive/audit layers file rows by date, and must never invent a
    date for a bare time):

      - ISO ``YYYY-MM-DD[ T]HH:MM[:SS][±HH:MM|Z]``  → its date part (searched
        anywhere, matching the legacy archive behaviour)
      - ``DD-MM[, HH:MM]`` / ``DD.MM[.YYYY]`` / ``DD/MM[/YYYY]`` → day+month,
        with the year taken from an explicit 4-digit token or inferred from
        ``fallback_date`` (rollover-aware across Dec/Jan)
      - bare ``HH:MM`` or anything else              → ``None``

    ``fallback_date`` (``YYYY-MM-DD``) anchors year inference for the day-month
    forms. Callers that still need a date after ``None`` fall back to the pick's
    own ``date`` field — a bare time cannot name a calendar day.
    """
    text = str(value or "").strip()
    if not text:
        return None

    iso = _KO_ISO_DATE_RE.search(text)
    if iso:
        return f"{iso.group(1)}-{iso.group(2)}-{iso.group(3)}"

    m = _KO_DMY_RE.match(text)
    if not m:
        return None
    dd, mm = int(m.group(1)), int(m.group(2))
    if not (1 <= dd <= 31 and 1 <= mm <= 12):
        return None

    year_token = m.group(3)
    if year_token:
        year = int(year_token) + (2000 if len(year_token) == 2 else 0)
        return _safe_date(year, mm, dd).isoformat() if _safe_date(year, mm, dd) else None

    year = _kickoff_year(fallback_date)
    cand = _safe_date(year, mm, dd)
    if cand is None:
        return None
    if fallback_date:
        try:
            fb = date.fromisoformat(str(fallback_date)[:10])
            delta = (cand - fb).days
            if delta < -180:
                cand = _safe_date(year + 1, mm, dd) or cand
            elif delta > 180:
                cand = _safe_date(year - 1, mm, dd) or cand
        except (ValueError, TypeError):
            pass
    return cand.isoformat()


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
    if "ml-fade" in market.lower() or "ml-fade" in rule.lower():
        return f"ML-FADE≥{threshold:.0f}"
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

    Falls back to the stored display/rule for unparseable rules (legacy
    display-string rows) — never worse than the stored label. Model families
    without an N-way token (ml-meta and its derived ml-fade slice) derive
    from their exact threshold the same way: a stored display that disagrees
    with the family's rule string is rewritten by heal_ledger_labels.
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
        rl = rule.lower()
        if rl.startswith(("ml-fade", "ml-meta")):
            mt = _RULE_THR_RE.search(rule)
            if mt:
                try:
                    return display_rule_label(market, 0, float(mt.group(1)), rule)
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
