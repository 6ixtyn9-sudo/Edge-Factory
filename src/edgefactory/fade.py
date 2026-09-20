"""ml-fade — the inverse-selection sibling of the ml-meta rule family.

An ``ml-fade`` edge is DERIVED from eligible ``ml-meta`` selections and then
graded as a first-class rule family with its own identity, its own odds, and
its own walk-forward certification:

- binary 1X2 inversion: the ml-meta selection ``home`` becomes ``away`` and
  ``away`` becomes ``home``. That is the ONLY honest binary inverse on the
  1X2 market.
- draw selections have no honest binary inverse (the complement of "draw" is
  "home or away" — a double-chance market, not a 1X2 side). They are EXCLUDED
  explicitly; nothing is invented.
- the fade is priced at the FADE selection's own odds (the opposing side of
  the book — forebet ``odd2`` when the parent is ``home``, ``odd1`` when the
  parent is ``away``). The parent pick's price is never used to score a fade.
- certification is the standard machinery (mine_consensus.evaluate on the
  ``ml_fade_settled`` view): same train/validation split, minimum sample
  gates, Wilson lower bound, train/validation ROI and odds checks, with
  candidate/certified status and decay-monitor benching.

Derivation inputs are pick-time only: the parent selection, the model
probability ``ml_p`` and the pre-match 1X2 odds. No settlement, closing or
post-kickoff information participates in deriving or pricing a fade.
"""
from __future__ import annotations

# The fade family and its parent, as named in rules, ledgers and registry
# metadata. edge_family is load-bearing: it is the fade row's distinct ledger
# identity (scripts/daily.py match_market_key) and its report grouping.
FADE_FAMILY = "ml-fade"
PARENT_FAMILY = "ml-meta"
DERIVATION = "inverse-selection"

# The DuckDB view every robust pipeline stage (mine, decay, purity assay)
# reads the fade slice from. Defined once here so the three TEMP-view
# recreation sites cannot drift apart (Handover Rule L1 view graph).
FADE_VIEW = "ml_fade_settled"

# Binary 1X2 inverse map. "draw" is deliberately ABSENT: no honest binary
# inverse exists for a draw selection.
INVERSE_SELECTION = {"home": "away", "away": "home"}

# Odds column of the fade selection (the opposing side of the same book).
# Parent home -> fade away is priced at odd2; parent away -> fade home at odd1.
FADE_ODDS_COLUMN = {"home": "odd2", "away": "odd1"}


def inverse_selection(selection: object) -> str | None:
    """Binary 1X2 inverse of an ml-meta selection, or None when there isn't one.

    home -> away, away -> home. Draws return None — the caller must exclude
    them explicitly rather than invent an inverse.
    """
    return INVERSE_SELECTION.get(str(selection or "").strip().lower())


def fade_odds_column(selection: object) -> str | None:
    """Warehouse odds column pricing the fade of ``selection``, None for draws."""
    return FADE_ODDS_COLUMN.get(str(selection or "").strip().lower())


def fade_avg_p(ml_p: float) -> float:
    """Stated confidence of the fade, on the pipeline's 0-100 avg_p scale.

    The fade wins exactly when the parent selection loses, so its stated
    probability is the complement of the model's ``ml_p``. (Draws are already
    excluded from the slice, so the parent selection is binary home/away.)
    """
    return round((1.0 - float(ml_p)) * 100.0, 1)


def fade_edge_metadata(threshold) -> dict:
    """Registry provenance stamped on every mined ml-fade edge.

    Independent identity (own family), explicit parentage (rule and family)
    and the derivation kind, so audit/replay/reporting can attribute every
    fade edge to the ml-meta operating band it was derived from.
    """
    return {
        "edge_family": FADE_FAMILY,
        "parent_family": PARENT_FAMILY,
        "parent_rule": f"ml-meta avg_p>={float(threshold):g}",
        "derivation": DERIVATION,
        "derivation_note": (
            "binary 1X2 inverse of the ml-meta selection "
            "(home<->away) at the opposing side's own odds; "
            "parent draw selections are excluded — no honest "
            "binary inverse exists."),
    }


def ml_fade_settled_sql(ml_raw_view: str = "ml_meta_raw") -> str:
    """CREATE VIEW statement for the graded ml-fade slice.

    ``ml_raw_view`` is the raw ml-meta predictions relation (the miner's
    registered frame ``ml_meta_raw_df`` or the CSV-backed ``ml_meta_raw`` view
    the monitors recreate from localdata/ml_meta_predictions.csv.gz).

    Semantics, in one place for every stage that recreates this view:

    - ``pick`` is the INVERSE of the parent ml-meta selection
      (home <-> away; draw rows are excluded by the WHERE clause);
    - ``pick_odds`` is the FADE selection's own price — forebet ``odd2`` for
      an away fade of a home parent, ``odd1`` for a home fade of an away
      parent — never the parent pick's odds;
    - ``parent_pick``/``ml_p`` are carried for provenance and threshold scans
      (``ml_p*100 >= thr`` selects the same eligible parent confidence band
      the ml-meta rules scan);
    - ``outcome`` comes from consensus3 exactly like ml_meta_settled — it
      grades the fade selection against the result, nothing else. The
      derivation columns (pick, pick_odds) never touch results columns.
    """
    return f"""
        CREATE OR REPLACE TEMP VIEW {FADE_VIEW} AS
        WITH ml AS (SELECT DISTINCT ON (date, home, away) * FROM {ml_raw_view}),
             c3 AS (SELECT DISTINCT ON (date, home, away) * FROM consensus3),
             fb AS (SELECT DISTINCT ON (date, home, away)
                           date, home, away, odd1, odd2
                    FROM forebet_settled)
        SELECT c3.sport, c3.date, c3.home, c3.away, c3.outcome,
               ml.pick AS parent_pick,
               CASE ml.pick WHEN 'home' THEN 'away' ELSE 'home' END AS pick,
               ml.ml_p,
               CASE ml.pick WHEN 'home' THEN fb.odd2
                            ELSE fb.odd1 END AS pick_odds,
               c3.pick_odds AS parent_pick_odds,
               c3.league
        FROM c3 JOIN ml USING (date, home, away)
                LEFT JOIN fb USING (date, home, away)
        WHERE ml.pick IN ('home', 'away')
    """
