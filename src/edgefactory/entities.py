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

from .util import compact_key, norm_entity_team, norm_league, norm_team

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


def _override_lookup(kind: str, raw: object) -> str | None:
    overrides = load_overrides().get(kind, {})
    if not isinstance(overrides, dict):
        return None
    candidates = [str(raw or ""), norm_league(raw), compact_key(raw), norm_team(str(raw or ""))]
    for key in candidates:
        if key in overrides:
            return str(overrides[key])
    return None


def _registry_lookup(kind: str, raw: object) -> str | None:
    registry = load_registry()
    alias_index = registry.get("alias_index", {}).get(kind, {})
    if not isinstance(alias_index, dict):
        return None
    candidates = [str(raw or ""), norm_league(raw), compact_key(raw), norm_team(str(raw or ""))]
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
    return norm_league(raw)


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
    return norm_entity_team(str(raw or ""), width=width)


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
