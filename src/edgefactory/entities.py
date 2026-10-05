"""Canonical entity registry for leagues and teams.

This module is deliberately lightweight and safe on fresh clones:

1. manual overrides from config/entity_overrides.json
2. learned aliases from localdata/entity_registry.json
3. deterministic normalization fallback from util.py

Use this for purity contexts, reporting, and read-model keys. Do not use it to
silently change certified miner joins without re-validating the miner.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .identity import canonical_league_key, fold_league_identity, team_identity_words
from .util import (
    clear_team_alias_cache,
    compact_key,
    norm_entity_team,
    norm_league,
    norm_team,
    norm_team_legacy,
)

ROOT = Path(__file__).resolve().parents[2]
CONFIG_OVERRIDES_PATH = ROOT / "Config" / "entity_overrides.json"
if not CONFIG_OVERRIDES_PATH.exists():
    CONFIG_OVERRIDES_PATH = ROOT / "config" / "entity_overrides.json"
ENTITY_REGISTRY_PATH = ROOT / "localdata" / "entity_registry.json"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


@lru_cache(maxsize=1)
def load_overrides() -> dict[str, Any]:
    data = _read_json(CONFIG_OVERRIDES_PATH)
    return data if isinstance(data, dict) else {}


@lru_cache(maxsize=1)
def load_registry() -> dict[str, Any]:
    data = _read_json(ENTITY_REGISTRY_PATH)
    return data if isinstance(data, dict) else {}


def clear_entity_caches() -> None:
    """Clear cached registry/override data, useful in tests or long processes."""
    load_overrides.cache_clear()
    load_registry.cache_clear()
    clear_team_alias_cache()


def _override_lookup(kind: str, raw: object) -> str | None:
    overrides = load_overrides().get(kind, {})
    if not isinstance(overrides, dict):
        return None
    candidates = [
        str(raw or ""), norm_league(raw), compact_key(raw),
        norm_team(str(raw or "")),
        # Dual key: entries/callers created before the 2026-10-05
        # transliteration fix still resolve through the frozen key.
        norm_team_legacy(str(raw or "")),
    ]
    for key in candidates:
        if key in overrides:
            return str(overrides[key])
    return None


def _registry_lookup(kind: str, raw: object) -> str | None:
    registry = load_registry()
    alias_index = registry.get("alias_index", {}).get(kind, {})
    if not isinstance(alias_index, dict):
        return None
    # Legacy candidates first, byte-unchanged; folded identity candidates
    # appended (additive-only coverage, see edgefactory/identity.py).
    # Registry candidates use the PLAIN fold, not canonical_league_key, so
    # the curated alias table can never be applied twice through a learned
    # alias_index.
    candidates = [
        str(raw or ""), norm_league(raw), compact_key(raw),
        norm_team(str(raw or "")),
        norm_team_legacy(str(raw or "")),  # legacy-keyed learned aliases
    ]
    if kind == "leagues":
        candidates.append(fold_league_identity(raw))
    else:
        folded_team = team_identity_words(str(raw or ""))
        candidates.append(norm_team(folded_team))
        candidates.append(norm_entity_team(folded_team, width=24))
    for key in candidates:
        if key in alias_index:
            return str(alias_index[key])
    return None


def canonical_league(raw: object) -> str:
    """Return canonical league key for purity/reporting contexts."""
    override = _override_lookup("leagues", raw)
    if override:
        return norm_league(override)
    learned = _registry_lookup("leagues", raw)
    if learned:
        return norm_league(learned)
    # Folded identity fallback: identical to norm_league(raw) for clean
    # names; unifies '&' -> 'and' spellings and applies evidence aliases
    # (e.g. "England,Fa Cup" -> "fa"). See edgefactory/identity.py.
    return canonical_league_key(raw) or "unknown"


def classify_competition(league_name: object) -> str:
    """Classify a competition/league into structural categories:
    friendly, youth, women, cup, or league.
    """
    s = str(league_name or "").lower()
    if any(tok in s for tok in ("friendly", "amichevole", "freundschaftsspiele", "club amic")):
        return "friendly"
    if any(tok in s for tok in ("u17", "u18", "u19", "u20", "u21", "u23", "youth", "reserves", "reserve", "young", "primavera", "junior")):
        return "youth"
    if any(tok in s for tok in ("women", "fem", "donna", "ladies", "w-cup", "frau")):
        return "women"
    if any(tok in s for tok in ("cup", "copa", "coppa", "coupe", "pokal", "trophy", "shield", "fa cup", "dff pokal", "ko-runde", "play-offs", "playoffs", "tournament")):
        return "cup"
    return "league"


def canonical_team(raw: object, *, width: int = 24) -> str:
    """Return canonical team key for purity/reporting contexts."""
    override = _override_lookup("teams", raw)
    if override:
        return norm_entity_team(override, width=width)
    learned = _registry_lookup("teams", raw)
    if learned:
        return norm_entity_team(learned, width=width)
    # Folded identity fallback: identical to the legacy form for clean
    # names; unifies '&' <-> 'and' spellings (Dagenham incident).
    return norm_entity_team(team_identity_words(str(raw or "")), width=width)


def canonical_team_variants(raw: object, *, width: int = 24) -> list[str]:
    """Every entity-key spelling that denotes the SAME team.

    Returned in priority order: the canonical key first, then the
    pre-alias fallback key (what this name resolved to before the
    2026-10-05 canonicalization), then the keys of every curated sibling
    spelling that maps to the same canonical name.

    Context/purity tables learned their keys under whichever spelling the
    feeds used at the time (the live registry, for example, carries
    ``turkiye`` entries and no ``turkey`` ones). Canonicalizing the lookup
    key alone would therefore ORPHAN that evidence — including VETO
    verdicts. Callers look up every variant and keep the most severe
    verdict, so canonicalization can never lose a veto.

    Deterministic: curated table + folding only, no fuzzy matching.
    """
    variants: list[str] = []

    def _add(key: str) -> None:
        if key and key not in variants:
            variants.append(key)

    _add(canonical_team(raw, width=width))
    # pre-alias fallback: the historical key for this exact spelling
    _add(norm_entity_team(team_identity_words(str(raw or "")), width=width))
    override = _override_lookup("teams", raw)
    if override:
        teams = load_overrides().get("teams", {})
        if isinstance(teams, dict):
            for spelling, canonical in teams.items():
                if str(canonical) != str(override):
                    continue
                _add(norm_entity_team(team_identity_words(str(spelling)),
                                      width=width))
    return variants


def explain_entity(kind: str, raw: object) -> dict[str, Any]:
    """Return canonical key plus evidence metadata if available."""
    canonical = canonical_league(raw) if kind == "leagues" else canonical_team(raw)
    registry = load_registry()
    entities = registry.get(kind, {}) if isinstance(registry, dict) else {}
    meta = entities.get(canonical, {}) if isinstance(entities, dict) else {}
    return {
        "raw": raw,
        "canonical": canonical,
        "meta": meta,
    }
