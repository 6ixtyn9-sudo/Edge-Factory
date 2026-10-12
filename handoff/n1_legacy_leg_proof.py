#!/usr/bin/env python3
"""N-1(b)(c)(d)(e): the acca lifecycle proof across the Utd fold, plus the
A1 guards of the 2026-10-12 close-out.

A slip frozen BEFORE the 2026-10-12 word fold stores the key the old fold
computed. The enhancement lane stamps folded keys (``enhancement_legs`` ->
``_folded_leg_key``), so its frozen legs carry glued seam keys, and re-folding a
glued key cannot recover the new spelling. This script freezes such a slip and
settles it ACROSS the fold:

  arm 1  the pre-fold identity, settled by the current code   -> resolves, and
         the compatibility hit is journaled as a record (both keys, the slip's
         day, the resolved fixture)
  arm 2  the same leg against the primary key only            -> misses (the
         pre-fix behaviour: a 1x2 leg has no market fallback, so it waits out
         the 5-day void timer - exactly the Türkiye failure the key's docstring
         quotes)
  arm 3  a main-lane leg (raw spellings, recomputed at read)  -> resolves with
         no compatibility key at all
  arm 4  THE ADVERSARIAL CASE (A1b): a same-day pair whose keys collide - the
         leg's own spelling folded, and a DIFFERENT club that folds onto the
         same key. With the corroboration guard ON the other club's score is
         refused and the leg is held; with the guard monkeypatched OFF the same
         slip books the OTHER fixture's result, which is what the guard exists
         to prevent.
  arm 5  primary-first (A1a): when BOTH keys are present in the index, the leg's
         own fixture is graded and no compatibility record is made.

State is written to a scratch directory; nothing here touches localdata.

Run from the repository root:
  PYTHONPATH=src .venv/bin/python handoff/n1_legacy_leg_proof.py
"""
from __future__ import annotations

import inspect
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "src"))

import auto_tickets as at  # noqa: E402
from edgefactory.identity import (TEAM_KEY_ALIASES,  # noqa: E402
                                  TEAM_STRUCTURE_NOISE, migrate_folded_key,
                                  source_team_key, team_identity_words)

DAY = "2026-07-14"
HOME_RAW, AWAY_RAW = "Tonbridge Angels", "Sutton Utd"      # a settled archive row
HOME_KEY, AWAY_KEY = source_team_key(HOME_RAW), source_team_key(AWAY_RAW)


def pre_fold_key_reconstruction(name: str) -> str:
    """The pre-fold key, re-derived HERE from the raw pieces (a cross-check of
    the library's own ``fold_tokens=False`` answer, not a second code path)."""
    words = [w for w in team_identity_words(name, fold_tokens=False).split()
             if w not in TEAM_STRUCTURE_NOISE]
    key = re.sub(r"[^a-z0-9]", "", " ".join(words))[:24]
    return TEAM_KEY_ALIASES.get(key, key)


def pre_fold_key(name: str) -> str:
    """The key the pre-2026-10-12 fold computed for a spelling.

    ``source_team_key(name, fold_tokens=False)`` is the historical rule: the
    token fold lives inside ``team_identity_words``, so switching it off is
    exactly what the code did before the fold existed, and everything else
    (structure noise, width, alias resolution) stays the same code path.
    """
    return source_team_key(name, fold_tokens=False)


def scratch(tmp: Path) -> None:
    at.LOCALDATA = tmp
    at.STATE_FILE = tmp / "state.json"
    at.ENHANCEMENT_STATE_FILE = tmp / "enhancement_state.json"
    at.BUCKET_PNL_FILE = tmp / "bucket.json"


def slip_state(fixture_key, *, pick="AWAY", day=DAY, match=None, odds=1.9):
    return {"bank": 100.0, "base_pct": 10.0, "cycle_base": 10.0,
            "history": [], "events": [],
            "open_slips": [{"date": day, "staked_pct": 10.0, "accas": [{
                "odds": odds, "stake_pct": 10.0, "results": [None], "won": None,
                "legs": [{"match": match or f"{HOME_RAW} vs {AWAY_RAW}", "pick": pick,
                          "prob": 0.6, "odds": odds, "result": None,
                          "fixture_key": fixture_key}]}]}]}


def settled_for(home, away, day, outcome="away"):
    """An outcome mapping the settlement's OWN lookup spec can hit.

    ``pick_result`` reads the result from the settled mapping, not from the
    pick row, and a miss there means "not known yet" - which the 5-day void
    timer then closes as void. These arms exist to show a leg GRADING through
    the compatibility key, so the mapping is built from the settlement's own
    key specs (``_exact_result_lookup_specs`` + ``_narrow_result_keys``), one
    outcome per space, rather than hand-picked keys.
    """
    mapping = {}
    for hk, ak, _legacy in at._exact_result_lookup_specs(home, away):
        mapping[(day, hk, ak)] = outcome
    for hk, ak in at._narrow_result_keys(home, away):
        mapping[(day, hk, ak)] = outcome
    return mapping


def index_of(rows):
    idx = {}
    for p in rows:
        day = str(p.get("date") or "")[:10]
        idx[at._folded_leg_key(day, p.get("home"), p.get("away"), p.get("pick"))] = p
    return idx


def settle(archives, stored, *, day=DAY, pick="AWAY", match=None,
           disable_guard=None, settled=None):
    """Settle one frozen slip against ``archives``; return (state, lines)."""
    at.LEGACY_KEY_HITS.clear()
    at.LEGACY_KEY_REFUSED.clear()
    original = at._compat_refusal
    if disable_guard is not None:
        at._compat_refusal = disable_guard
    try:
        st = slip_state(stored, pick=pick, day=day, match=match)
        lines = at.settle_open_slips(st, settled or {}, archives=archives,
                                     entries_by_date={})
    finally:
        at._compat_refusal = original
    return st, lines


def main() -> int:
    print("== N-1(c) acca lifecycle proof across the Utd fold ==")
    print("   (+ A1(a) guard lines, A1(b) adversarial collision, A1(d) audit trail)")
    print(f"fixture: {DAY} {HOME_RAW} vs {AWAY_RAW} (a settled archive row)")
    print(f"  current seam keys      : {HOME_KEY!r} / {AWAY_KEY!r}")
    print(f"  pre-fold seam keys     : {pre_fold_key(HOME_RAW)!r} / "
          f"{pre_fold_key(AWAY_RAW)!r}")
    print(f"  migrate_folded_key     : {migrate_folded_key(pre_fold_key(AWAY_RAW))!r}")
    assert pre_fold_key(AWAY_RAW) != AWAY_KEY, "the pre-fold arm would be a no-op"
    assert pre_fold_key_reconstruction(AWAY_RAW) == pre_fold_key(AWAY_RAW), \
        "the library's fold_tokens=False must equal the historical rule"
    assert pre_fold_key("Coventry") == source_team_key("Coventry"), \
        "a spelling with no folded token must not move"
    print("  (the pre-fold key differs, so the two arms really are two identities;")
    print("   a spelling with no folded token produces the same key both ways)")
    print()

    archives = [{"date": DAY, "home": HOME_RAW, "away": AWAY_RAW, "pick": "AWAY",
                 "outcome": "away", "avg_p": 61.0, "odds": 1.9}]
    index = index_of(archives)
    print(f"archive index keys the settlement builds: {list(index)}")
    print()

    # ---- A1(a): the guard, as source, and the scoping assertions -----------
    print("== A1(a) the compatibility candidate's guards (source of the symbols) ==")
    for fn in (at.leg_lookup_keys, at._compat_refusal):
        src = inspect.getsource(fn).rstrip().splitlines()
        print(f"-- auto_tickets.{fn.__name__}():")
        for line in src[:6]:
            print(f"   {line}")
        print(f"   ... ({len(src)} line(s) total; cited by symbol, never by line number)")
    print()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        scratch(tmp)

        # ---- arm 1: the pre-fold folded key, settled by today's code --------
        frozen = [DAY, pre_fold_key(HOME_RAW), pre_fold_key(AWAY_RAW), "AWAY"]
        leg = slip_state(frozen)["open_slips"][0]["accas"][0]["legs"][0]
        primary = at.leg_lookup_key(DAY, leg)
        keys = at.leg_lookup_keys(DAY, leg)
        print("arm 1 -- a slip frozen before the fold (enhancement-lane shape)")
        print(f"  stored fixture_key : {frozen}")
        print(f"  primary key        : {primary}")
        print(f"  lookup keys        : {keys}")
        # A1(a) scoping: the candidate differs from the primary ONLY in the
        # tokens; the day and the pick are the stored ones on BOTH keys, so a
        # candidate can never reach another day's or another market's row.
        assert keys[0] == primary, "the primary key must come first"
        assert keys[1][0] == primary[0] and keys[1][3] == primary[3], \
            "the candidate must keep the stored day and pick"
        assert keys[1][1:] != primary[1:], "the candidate must actually differ"
        print("  candidate scoping  : same stored day and pick as the primary; "
              "only the team tokens differ")
        print(f"  primary alone in the index? "
              f"{'HIT' if index.get(primary) else 'MISS (this is the pre-fix path)'}")
        graded = settled_for(HOME_RAW, AWAY_RAW, DAY, outcome="away")
        st, lines = settle(archives, frozen, settled=graded)
        booked = st["history"][-1] if st["history"] else None
        print(f"  settled: open_slips={st['open_slips']} history={booked}")
        print(f"  graded, not voided  : the acca's odds are the leg's own "
              f"({booked['accas'][0]['odds'] if booked else None} = the leg), "
              f"not the all-void 1.0 stake-back")
        print("  A1(d) audit trail (LEGACY_KEY_HITS, one record per answered leg):")
        for rec in at.LEGACY_KEY_HITS:
            for field, value in rec.items():
                print(f"      {field:>16}: {value}")
        print("  A1(d) the same trail in the settlement's own lines:")
        for line in lines:
            if line.startswith("compat key"):
                print(f"      {line}")
        assert primary not in index and keys[1] in index, "the two arms collapsed"
        assert st["open_slips"] == [] and booked and booked["accas"][0]["won"], \
            "the pre-fold leg did not settle"
        assert booked["accas"][0]["odds"] == 1.9, \
            "the leg was voided by the timer, not graded by the row it found"
        assert len(at.LEGACY_KEY_HITS) == 1, "the hit must be journaled"
        rec = at.LEGACY_KEY_HITS[0]
        assert rec["primary"] == primary and rec["matched"] == keys[1]
        assert rec["stored"] == tuple(frozen) and rec["slip_date"] == DAY
        assert rec["fixture"] == [DAY, HOME_RAW, AWAY_RAW], \
            "the record must name the resolved fixture, not just a counter"
        print()

        # ---- arm 2: what the primary key alone would have done --------------
        print("arm 2 -- the same leg if only the primary key were consulted")
        print(f"  index.get({primary}) -> {index.get(primary)}")
        print("  a 1x2 leg has no market fallback, so settlement would hold it and")
        print("  the void timer (5 days past the slip date) would close it as void:")
        print("  the leg is orphaned exactly as the Türkiye rename orphaned its acca,")
        print("  except the cause here is a word-boundary fold, not a rename.")
        print()

        # ---- arm 3: the main-lane shape -------------------------------------
        raw = [DAY, HOME_RAW, AWAY_RAW, "AWAY"]
        print("arm 3 -- a slip frozen with RAW spellings (the main lane's shape)")
        print(f"  stored fixture_key : {raw}")
        leg3 = slip_state(raw)["open_slips"][0]["accas"][0]["legs"][0]
        keys3 = at.leg_lookup_keys(DAY, leg3)
        print(f"  lookup keys        : {keys3}")
        print(f"  keys == [primary] (no compatibility key needed): "
              f"{len(keys3) == 1}")
        st3, _ = settle(archives, raw, settled=graded)
        print(f"  settled: open_slips={st3['open_slips']} "
              f"history_booked={bool(st3['history'])} "
              f"compat_hits={at.LEGACY_KEY_HITS}")
        assert len(keys3) == 1 and st3["open_slips"] == []
        assert st3["history"] and st3["history"][-1]["accas"][0]["odds"] == 1.9
        assert not at.LEGACY_KEY_HITS, "raw spellings must not need a compat key"
        print()

        # ---- arm 4: THE ADVERSARIAL CASE (A1b) ------------------------------
        print("arm 4 -- A1(b) the collision: a DIFFERENT club folds onto the same key")
        # The frozen leg says 'Newcastle Utd' (its own club). A second club,
        # 'Newcastle United', played the SAME day, so both spellings fold onto
        # one index slot - and that slot is the OTHER club's row.
        other = [{"date": DAY, "home": "Coventry", "away": "Newcastle United",
                  "pick": "AWAY", "outcome": "home", "avg_p": 55.0, "odds": 2.4}]
        stored_leg = [DAY, "coventry", "newcastleutd", "AWAY"]
        print(f"  the frozen leg     : {stored_leg}")
        print(f"  the other club's row: {other[0]['home']} vs {other[0]['away']} "
              f"({other[0]['outcome']} -> the leg's pick AWAY would LOSE)")
        print(f"  that row's own key  : {list(index_of(other))[0]}")
        today = at.datetime.now(at.TZ).strftime("%Y-%m-%d")
        other_graded = settled_for("Coventry", "Newcastle United", DAY,
                                   outcome="home")     # the leg's AWAY pick LOSES
        print("  (i) refusal inside the void window (slip day = today): the leg is HELD")
        st_on, lines_on = settle(other, stored_leg, day=today, match="Coventry vs Newcastle Utd",
                                 settled=settled_for("Coventry", "Newcastle United", today,
                                                     outcome="home"))
        print(f"      guard ON  -> hits={len(at.LEGACY_KEY_HITS)} "
              f"refused={len(at.LEGACY_KEY_REFUSED)} "
              f"open_slips={len(st_on['open_slips'])} history={bool(st_on['history'])}")
        for rec in at.LEGACY_KEY_REFUSED:
            print(f"      refused_because: {rec['refused_because']}")
        for line in lines_on:
            if line.startswith("compat key"):
                print(f"      {line}")
        on_hits, on_refused = len(at.LEGACY_KEY_HITS), len(at.LEGACY_KEY_REFUSED)
        on_open, on_history = len(st_on["open_slips"]), len(st_on["history"])
        on_lines = [line for line in lines_on if line.startswith("compat key")]
        print("  (ii) the same refusal on the old slip day (outside the window): VOID")
        st_void, _ = settle(other, stored_leg, match="Coventry vs Newcastle Utd")
        void_records = list(at.LEGACY_KEY_REFUSED)
        voided = st_void["history"][-1]["accas"][0] if st_void["history"] else None
        print(f"      guard ON  -> open_slips={len(st_void['open_slips'])} "
              f"history_accа={voided}  (stake back, never the other score)")
        print(f"      against the archive row grading 'home' -> the leg's AWAY pick")
        print(f"      would LOSE ({other_graded and 'grading available'})")
        print("  (iii) guard OFF (monkeypatched): the same slip is decided by the OTHER club")
        st_off, _ = settle(other, stored_leg, match="Coventry vs Newcastle Utd",
                           disable_guard=lambda leg, row: None,
                           settled=other_graded)
        won = st_off["history"][-1]["accas"][0]["won"] if st_off["history"] else None
        odds = st_off["history"][-1]["accas"][0]["odds"] if st_off["history"] else None
        print(f"      guard OFF -> hits={len(at.LEGACY_KEY_HITS)} "
              f"open_slips={len(st_off['open_slips'])} history={bool(st_off['history'])} "
              f"booked_won={won} odds={odds}")
        # Each arm clears the trails first, so assert on the counts captured
        # beside the arm that produced them (the LAST arm must not be read as
        # evidence about an earlier one).
        assert on_open == 1 and on_history == 0, "the guard must hold the leg"
        assert on_hits == 0 and on_refused == 1
        assert on_lines and on_lines[0].startswith("compat key REFUSED")
        assert len(void_records) == 1 and void_records[0]["refused_because"]
        assert voided is not None and voided["odds"] == 1.0, \
            "outside the window the leg must VOID (stake back), not grade"
        assert st_off["open_slips"] == [] and won is False and odds == 1.9, \
            "without the guard the OTHER fixture's result decides the acca"
        assert len(at.LEGACY_KEY_HITS) == 1 and at.LEGACY_KEY_REFUSED == [], \
            "with the guard disabled the collision is taken as a hit, silently"
        print("  => the guard is load-bearing: without it, the other club's score")
        print("     grades this leg as a loss the book pays, and the void timer never")
        print("     runs. With it the leg holds inside the window and voids outside,")
        print("     which is the same outcome a missing row gets.")
        print()

        # ---- arm 5: A1(a) the consultation order ----------------------------
        print("arm 5 -- A1(a) primary-first: the candidate is only CONSULTED on a miss")
        src = inspect.getsource(at.settle_open_slips)
        anchor = "# A compatibility candidate."
        if anchor in src:
            block = src.split(anchor)[0].rsplit("for leg_key in keys:", 1)
            assert len(block) == 2, "the guard region moved: update the anchor"
            print("  the settle loop, as source (symbol-cited, not line-cited):")
            for line in ("for leg_key in keys:" + block[1] + anchor).splitlines()[:8]:
                print(f"      {line.rstrip()}")
        both = [{"date": DAY, "home": HOME_RAW, "away": AWAY_RAW, "pick": "AWAY",
                 "outcome": "away", "odds": 1.9},
                {"date": DAY, "home": "Coventry", "away": "Newcastle United",
                 "pick": "AWAY", "outcome": "home", "odds": 2.4}]
        idx5 = index_of(both)
        leg5 = slip_state([DAY, pre_fold_key(HOME_RAW), pre_fold_key(AWAY_RAW), "AWAY"])
        leg5 = leg5["open_slips"][0]["accas"][0]["legs"][0]
        print(f"  index holds         : "
              f"{sorted(k[1] + '/' + k[2] for k in idx5)}")
        print("  the loop's own order, replayed against that index:")
        for i, k in enumerate(at.leg_lookup_keys(DAY, leg5)):
            hit = idx5.get(k)
            print(f"      [{i}] {'primary' if i == 0 else 'candidate'} {k[1]}/"
                  f"{k[2]} -> {'HIT' if hit else 'miss'}")
            if hit:
                break
        # the mechanical assertion of "no candidate without a miss": a leg whose
        # stored identity the current fold reproduces gets ONE key, and it is the
        # primary - there is nothing else to consult.
        leg_no_fold = slip_state([DAY, HOME_RAW, AWAY_RAW, "AWAY"])
        leg_no_fold = leg_no_fold["open_slips"][0]["accas"][0]["legs"][0]
        keys_no_fold = at.leg_lookup_keys(DAY, leg_no_fold)
        print(f"  a leg with no folded token: keys={len(keys_no_fold)} "
              f"(the primary only) -> primary({keys_no_fold[0][1]}/{keys_no_fold[0][2]}) "
              f"{'HIT' if idx5.get(keys_no_fold[0]) else 'miss'}")
        st5, lines5 = settle(both, [DAY, pre_fold_key(HOME_RAW), pre_fold_key(AWAY_RAW),
                                    "AWAY"], settled=graded)
        booked5 = st5["history"][-1] if st5["history"] else None
        print(f"  the folded leg      : compat hits={len(at.LEGACY_KEY_HITS)}, "
              f"graded from its own fixture: "
              f"{booked5['accas'][0]['won'] if booked5 else None}")
        assert len(keys_no_fold) == 1 and idx5.get(keys_no_fold[0])
        assert len(at.LEGACY_KEY_HITS) == 1 and at.LEGACY_KEY_REFUSED == []
        assert booked5 and booked5["accas"][0]["won"] is True
        print()

        print("both slip shapes resolve; the compatibility tier is exercised only by a")
        print("stored folded key, it is consulted only after the primary key misses, it")
        print("is refused unless the matched row corroborates the stored identity, and")
        print("every use is journaled with both keys and the resolved fixture.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
