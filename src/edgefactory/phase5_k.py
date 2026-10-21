"""Phase 5 K-contract features — ONE builder for fit and serve.

The forward era model is a fixed 32-column contract (``K_FEATURES``): 22 base
columns plus ``{source}_p`` / ``{source}_available`` for each declared source.
This module is the single place that turns "what we know about a fixture" into
those 32 columns, so the trainer and the live scorer cannot drift apart — the
exact failure class the 2026-10-06 diagnosis is about (trained on one feature
meaning, served on another).

Two rules the contract depends on:

* A declared source that is dark is NOT column-dropped. Its ``_p`` falls back
  to the model's recorded era-train-slice mean and its ``_available`` is 0.0.
  When the feed returns, nothing about the schema changes — the flag flips to
  1.0 and the same fitted coefficient starts seeing real values.
* A missing column must never be substituted with a bare ``0.0`` at serve.
  The legacy scoring loop did ``feat_dict.get(col, 0.0)``, which for the five
  probability columns silently injects a logit shift instead of the training
  mean. ``feature_vector`` below is the replacement and is deliberately loud:
  it reports the columns it had to impute.
"""
from __future__ import annotations

import math

from edgefactory.util import finite_probability

from edgefactory.phase5_activation import (
    DECLARED_SOURCE_ORDER,
    K_FEATURES,
)

__all__ = [
    "DECLARED_SOURCE_ORDER",
    "K_FEATURES",
    "AVAILABLE_SUFFIX",
    "PROB_SUFFIX",
    "default_fallbacks",
    "majority_pick",
    "source_columns",
    "build_k_features",
    "feature_vector",
    "payload_problems",
]

AVAILABLE_SUFFIX = "_available"
PROB_SUFFIX = "_p"

def default_fallbacks() -> dict[str, None]:
    """Schema only: no invented neutral probabilities, rates, odds or goals."""
    return dict.fromkeys(K_FEATURES)


def _finite(value):
    return (float(value) if isinstance(value, (int, float))
            and not isinstance(value, bool) and math.isfinite(value) else None)


def majority_pick(picks: list[str | None]) -> str | None:
    """Consensus pick from per-source picks.

    Byte-for-byte the rule the live 1x2 evaluator applies (picks_today.py
    eval_1x2): the caller passes each source's own top pick in the order the
    engine uses — ``(forebet, zulubet, statarea)`` — and the election is:

    * 3-way agreement (first == last, with all three present), else
    * the first two agreeing, else
    * the last two agreeing, else
    * **the first available pick** (the engine's documented fallback).

    Only the first three sources take part in the live election; the other
    declared voters are evidence, not electors. Returns None only when no
    source offered a pick at all.
    """
    non_none = [p for p in picks if p in ("home", "draw", "away")]
    if not non_none:
        return None
    if len(non_none) >= 3 and non_none[0] == non_none[2]:
        return non_none[0]
    if len(non_none) >= 2 and non_none[0] == non_none[1]:
        return non_none[0]
    if len(non_none) >= 3 and non_none[1] == non_none[2]:
        return non_none[1]
    return non_none[0]


def source_columns(sources: dict[str, tuple[float | None, bool]]) -> dict[str, float | None]:
    """``{source}_p`` / ``{source}_available`` pairs for the declared sources.

    ``sources`` maps source name -> (probability for the elected pick, present).
    A source with no usable probability gets ``None`` (the vector builder then
    imputes the model's recorded mean) and ``available = 0.0`` — so a dark
    feed is represented, never dropped. Invalid probabilities stay unavailable;
    a malformed or percent-scaled value is not silently clamped to certainty.
    """
    out: dict[str, float | None] = {}
    for source in DECLARED_SOURCE_ORDER:
        prob, present = sources.get(source, (None, False))
        value = finite_probability(prob)
        if value is None or not present:
            out[f"{source}{PROB_SUFFIX}"] = None
            out[f"{source}{AVAILABLE_SUFFIX}"] = 0.0
            continue
        out[f"{source}{PROB_SUFFIX}"] = value
        out[f"{source}{AVAILABLE_SUFFIX}"] = 1.0
    return out


def build_k_features(
    *,
    base: dict[str, float | None],
    sources: dict[str, tuple[float | None, bool]],
    fallbacks: dict[str, float] | None = None,
) -> dict[str, float | None]:
    """Assemble the full K vector, in ``K_FEATURES`` order, imputing the rest.

    ``base`` carries the 22 non-source columns (fb_p, zb_p, sa_p, avg_p, ...);
    ``sources`` the declared-source probabilities. Anything absent falls back
    to the recorded mean for that column (``fallbacks``), never to a silent
    zero. Without a recorded mean it stays None. The returned dict has exactly
    ``K_FEATURES`` keys; a fit must refuse unresolved columns.
    """
    means = dict(default_fallbacks())
    if fallbacks:
        means.update({k: _finite(v) for k, v in fallbacks.items() if k in means})
    merged: dict[str, float | None] = {}
    merged.update(source_columns(sources))
    for col, value in base.items():
        if col in merged and merged[col] is not None:
            continue
        merged[col] = _finite(value)

    row: dict[str, float | None] = {}
    for col in K_FEATURES:
        value = merged.get(col)
        row[col] = means[col] if value is None else value
    return row


def feature_vector(
    feat_dict: dict,
    model: dict,
    *,
    fallbacks: dict[str, float] | None = None,
) -> tuple[list[float], list[str]]:
    """Build a model's input vector in ITS recorded column order.

    Returns ``(vector, imputed_columns)``. Columns the live path did not
    produce are imputed from the payload's own recorded means; the caller is
    expected to surface ``imputed_columns`` (a K model scoring with whole
    sources imputed is a different animal from one scoring on live feeds).
    """
    cols = model.get("feature_cols") or []
    means = dict(default_fallbacks())
    payload_means = model.get("fallback_means")
    if isinstance(payload_means, dict):
        means.update({k: _finite(v) for k, v in payload_means.items()})
    if fallbacks:
        means.update({k: _finite(v) for k, v in fallbacks.items() if k in means})

    vector: list[float] = []
    imputed: list[str] = []
    for col in cols:
        value = _finite(feat_dict.get(col))
        if value is None:
            imputed.append(str(col))
            value = means.get(col)
        if value is None:
            raise ValueError(f"unavailable feature without recorded training mean: {col}")
        vector.append(float(value))
    return vector, imputed


def payload_problems(payload: dict, *, fallback_means: dict | None = None,
                     require_fallbacks: bool = False) -> list[str]:
    """Shape problems in a candidate model payload, activation-gate style.

    Mirrors the checks ``phase5_activation._load_passing_certificate`` applies,
    so a fit can be self-validated before it is ever offered as a candidate.

    The gate reads ``fallback_means`` as a SIBLING of the model payload on the
    certificate, so callers pass it explicitly (or leave it embedded in the
    payload for convenience); ``require_fallbacks`` makes its absence an error.
    """
    import math

    problems: list[str] = []
    if not isinstance(payload, dict):
        return ["payload is not a dict"]
    cols = payload.get("feature_cols")
    if cols != list(K_FEATURES):
        problems.append(
            "feature_cols must equal the frozen K contract in order "
            f"(got {len(cols) if isinstance(cols, list) else 'non-list'}, "
            f"expected {len(K_FEATURES)})"
        )
    coef = payload.get("coef")
    if not isinstance(coef, list) or len(coef) != len(K_FEATURES):
        problems.append("coef must be a list of exactly len(K_FEATURES) values")
    elif not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                 and math.isfinite(float(v)) for v in coef):
        problems.append("coef contains a non-finite value")
    intercept = payload.get("intercept")
    if not isinstance(intercept, (int, float)) or isinstance(intercept, bool) \
            or not math.isfinite(float(intercept)):
        problems.append("intercept must be a finite number")
    means = fallback_means if fallback_means is not None else payload.get("fallback_means")
    if means is None:
        if require_fallbacks:
            problems.append("fallback_means are required but missing")
    elif not isinstance(means, dict) or set(means) != set(K_FEATURES):
        problems.append("fallback_means must cover exactly every K column")
    elif not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                 and math.isfinite(float(v)) for v in means.values()):
        problems.append("fallback_means contains a non-finite value")
    return problems
