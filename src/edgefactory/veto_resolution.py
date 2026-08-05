"""Veto re-mine resolution overlay (Phase 1/2). Read-only. OFF by default.

Resolves ``UNKNOWN`` league purity verdicts at pick time via the locked O1/O2
rules (see HANDOVER.md Addendum 27 — veto re-mine locked decisions):

- O1: rule-pooled league verdicts — pool key ``(sport, league_key, market,
  side_role)``, n-weighted unconditional w_roi (Q2), Scenario B gates
  (ALLOW>=40, CAUTION>=20, VETO>=12) (Q3).
- O2: hierarchical fallback league -> niche -> competition_type (Q1).

Guarantees (pinned by tests):
- Only ``UNKNOWN`` is resolvable; a native non-UNKNOWN verdict is never
  overridden (monotone VETO).
- ``purity_registry.json`` is never written; this module is pure + read-only.
- ``apply_resolution_to_ctx`` shadow-logs ``resolution_*`` fields ALWAYS
  (even with the flag OFF) so the >=30-settled gate accrues from day one;
  the verdict is applied to ``ctx["league"]`` only when enabled.
"""
from __future__ import annotations

import json
from pathlib import Path

ENV_FLAG = "EDGE_FACTORY_VETO_RESOLUTION"  # == "1" activates the overlay

ALLOW_MIN_N = 40
CAUTION_MIN_N = 20
VETO_MIN_N = 12

PLAYABLE = {"ALLOW", "BOOST"}
RESOLVED = {"ALLOW", "BOOST", "CAUTION", "VETO"}

RESOLUTION_FIELDS = (
    "resolution_original_verdict",
    "resolution_verdict",
    "resolution_path",
    "resolution_pool_n",
    "resolution_pool_roi",
    "resolution_reason",
)


def pooled_verdict(n: int, w_roi: float | None) -> str:
    """Scenario B pooled verdict: ALLOW>=40, CAUTION>=20, VETO>=12.

    Mirrors ``context_verdict_league`` with the stricter pooled minimums;
    ``recent_roi`` is None for pooled evidence (conservative VETO branch at
    n>=40). Returns "UNKNOWN" when evidence is insufficient or absent.
    """
    if w_roi is None:
        return "UNKNOWN"
    if n < VETO_MIN_N:
        return "UNKNOWN"
    if n < 40:
        if w_roi <= -0.10:
            return "VETO"
        if n >= CAUTION_MIN_N and w_roi <= -0.04:
            return "CAUTION"
        return "UNKNOWN"
    # n >= 40 (standard gates; recent None -> conservative VETO branch)
    if w_roi <= -0.05:
        return "VETO"
    if w_roi < 0.0:
        return "CAUTION"
    if n >= 100 and w_roi >= 0.03:
        return "BOOST"
    return "ALLOW"


def build_pool_table(contexts: dict) -> dict[tuple[str, str, str, str], dict]:
    """Canonical pool table from the league dimension.

    Pool key ``(sport, league, market, side_role)``; n = sum of cell n;
    w_roi = n-weighted mean over priced cells; verdict per Scenario B.
    This is the deterministic pool table Phase 0 defines (the second-agent's
    pool-bucket numbers were not reproducible — this is).
    """
    pools: dict[tuple[str, str, str, str], dict] = {}
    league_ctx = contexts.get("league", {}) if isinstance(contexts, dict) else {}
    for key, cell in league_ctx.items():
        if not isinstance(key, str) or not isinstance(cell, dict):
            continue
        parts = key.split("|")
        if len(parts) != 5:
            continue
        sport, league, market, _rule, side = parts
        pk = (sport, league, market, side)
        p = pools.setdefault(pk, {"n": 0, "w_roi_num": 0.0, "w_roi_den": 0, "cells": 0})
        n = int(cell.get("n") or 0)
        p["n"] += n
        p["cells"] += 1
        roi = cell.get("roi")
        if roi is not None:
            p["w_roi_num"] += n * float(roi)
            p["w_roi_den"] += n
    out: dict[tuple[str, str, str, str], dict] = {}
    for pk, p in pools.items():
        w_roi = (p["w_roi_num"] / p["w_roi_den"]) if p["w_roi_den"] else None
        out[pk] = {
            "n": p["n"],
            "w_roi": w_roi,
            "verdict": pooled_verdict(p["n"], w_roi),
            "cells": p["cells"],
        }
    return out


def o2_verdict(contexts: dict, ctx: dict, market: str, rule: str,
               sport: str) -> tuple[str, str]:
    """O2 hierarchical fallback: niche -> competition_type.

    Returns ``(verdict, path)``; "UNKNOWN" when neither level resolves.
    Key shapes (verified against the live registry):
      niche:      sport|league|market|rule|odds_band|side_role
      comp_type:  sport|market|rule|comp_type_name
    Only non-UNKNOWN verdicts resolve; VETO is never downgraded (we only
    ever return a stored non-UNKNOWN verdict unchanged).
    """
    league = str(ctx.get("league_key") or "")
    side = str(ctx.get("side_role") or "")
    band = str(ctx.get("odds_band_name") or "")
    if league and rule and band and side:
        cell = (contexts.get("niche", {}) if isinstance(contexts, dict) else {}).get(
            f"{sport}|{league}|{market}|{rule}|{band}|{side}")
        if cell and isinstance(cell, dict) and cell.get("verdict") not in (None, "UNKNOWN"):
            return str(cell["verdict"]), "O2-niche"
    comp = str(ctx.get("comp_type_name") or "")
    if rule and comp:
        cell = (contexts.get("competition_type", {}) if isinstance(contexts, dict) else {}).get(
            f"{sport}|{market}|{rule}|{comp}")
        if cell and isinstance(cell, dict) and cell.get("verdict") not in (None, "UNKNOWN"):
            return str(cell["verdict"]), "O2-competition_type"
    return "UNKNOWN", "unresolved"


def resolve_pick_verdict(contexts: dict, ctx: dict, pools: dict | None = None,
                         *, sport: str = "soccer", market: str = "1x2",
                         rule: str = "") -> dict:
    """Resolve the league verdict for one pick context.

    Returns ``{verdict, path, applied, pool_n, pool_w_roi, reason}``.
    ``applied`` is True only when the native verdict was UNKNOWN and O1/O2
    produced a resolved verdict (the caller decides whether to apply it).
    Never raises; any missing/empty input resolves to UNKNOWN/unresolved.
    """
    league_v = str(ctx.get("league") or "") if isinstance(ctx, dict) else ""
    if league_v != "UNKNOWN":
        return {"verdict": league_v, "path": "native", "applied": False,
                "pool_n": None, "pool_w_roi": None,
                "reason": f"native verdict {league_v} unchanged (only UNKNOWN is resolvable)"}
    if not isinstance(contexts, dict):
        return {"verdict": "UNKNOWN", "path": "unresolved", "applied": False,
                "pool_n": None, "pool_w_roi": None, "reason": "no registry"}
    if pools is None:
        pools = build_pool_table(contexts)
    league_key = str(ctx.get("league_key") or "")
    side = str(ctx.get("side_role") or "")
    if league_key and side:
        p = pools.get((sport, league_key, market, side))
        if p and p["verdict"] in RESOLVED:
            w = p["w_roi"]
            reason = (f"O1 pool n={p['n']} w_roi={w:+.4f} -> {p['verdict']}"
                      if w is not None else f"O1 pool n={p['n']} -> {p['verdict']}")
            return {"verdict": p["verdict"], "path": "O1-pool", "applied": True,
                    "pool_n": p["n"], "pool_w_roi": w, "reason": reason}
    v, path = o2_verdict(contexts, ctx, market, rule, sport)
    if v != "UNKNOWN":
        return {"verdict": v, "path": path, "applied": True,
                "pool_n": None, "pool_w_roi": None, "reason": f"{path} resolved to {v}"}
    return {"verdict": "UNKNOWN", "path": "unresolved", "applied": False,
            "pool_n": None, "pool_w_roi": None, "reason": "unresolved by O1/O2"}


def apply_resolution_to_ctx(ctx: dict, contexts: dict, pools: dict | None = None,
                            enable: bool = False, *, sport: str = "soccer",
                            market: str = "1x2", rule: str = "") -> dict:
    """Shadow-log resolution fields; apply the resolved league verdict when enabled.

    Always adds ``resolution_*`` fields (accrual log from day one). When
    ``enable`` is True and the resolution ``applied``, ``ctx["league"]`` is
    replaced with the resolved verdict (ALLOW/BOOST/CAUTION/VETO) so
    ``bucket_pick`` buckets accordingly. Returns a NEW dict; never raises.
    """
    if not isinstance(ctx, dict):
        return {}
    out = dict(ctx)
    try:
        res = resolve_pick_verdict(contexts, out, pools,
                                   sport=sport, market=market, rule=rule)
    except Exception as exc:  # pragma: no cover - defensive
        out["resolution_error"] = f"{type(exc).__name__}: {exc}"
        return out
    out["resolution_original_verdict"] = str(out.get("league") or "")
    out["resolution_verdict"] = res["verdict"]
    out["resolution_path"] = res["path"]
    out["resolution_pool_n"] = res["pool_n"]
    out["resolution_pool_roi"] = res["pool_w_roi"]
    out["resolution_reason"] = res["reason"]
    if enable and res["applied"]:
        out["league"] = res["verdict"]
    return out


def load_registry(root: Path) -> dict:
    """Read ``localdata/purity_registry.json`` -> contexts dict.

    Read-only: never writes. Returns {} on missing/corrupt file.
    """
    try:
        data = json.loads((Path(root) / "localdata" / "purity_registry.json").read_text())
        return data.get("contexts", {}) if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}
