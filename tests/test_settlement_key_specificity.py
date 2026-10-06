"""WO-7: settlement keys must name one fixture, not a nine-character prefix.

The settled-result map was keyed on nine characters of each club name.
Nine characters is shorter than most club names, so one key routinely
covered several clubs: "Adelaide City", "Adelaide Cobras" and "Adelaide
Comets" all collapsed to "adelaidec". 35.9% of the names in the current
archive shared a key with a genuinely different club.

The guard that was supposed to catch this only refused a key when the
colliding rows DISAGREED about the outcome, which made roughly half of
all collisions invisible by construction.

These tests pin the three repairs: a full-width key tried first, the
truncated key demoted to a guarded fallback, and names that normalise
away never written as a key at all.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load():
    spec = importlib.util.spec_from_file_location(
        "auto_tickets_wo7", ROOT / "scripts" / "auto_tickets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _settle(at, rows, day="2026-10-05"):
    """Build the settled map the way the loader does, guard included."""
    entries = {day: rows}
    key_to = {}
    for d, rs in entries.items():
        for e in rs:
            for hk, ak in at._result_write_keys(e["home"], e["away"]):
                key_to[(d, hk, ak)] = e["result"]
    at._drop_ambiguous_result_keys(key_to, entries)
    at.SETTLED_KEY_NAMES.clear()
    for d, rs in entries.items():
        for e in rs:
            for hk, ak in at._result_write_keys(e["home"], e["away"]):
                at.SETTLED_KEY_NAMES.setdefault((d, hk, ak), set()).add(
                    (e["home"], e["away"]))
    return key_to


def _grade(at, settled, home, away, day="2026-10-05"):
    """The outcome settlement actually resolves this fixture to.

    pick_result reports win/loss against a selection, so the outcome is
    recovered by asking which selection wins.
    """
    def ask(sel):
        return at.pick_result(
            {"date": day, "home": home, "away": away, "pick": sel}, settled)

    first = ask("home")
    if first is None or first == "void":
        return first
    if first == "win":
        return "home"
    return "away" if ask("away") == "win" else "draw"


# --- A: the key must be specific enough to name one club ----------------

def test_most_specific_key_separates_distinct_clubs():
    at = _load()
    city = at._result_write_keys("Adelaide City", "Sydney FC")
    cobras = at._result_write_keys("Adelaide Cobras", "Sydney FC")
    assert city[0] != cobras[0], (
        "the first key tried must tell Adelaide City from Adelaide Cobras")


def test_most_specific_key_separates_ferroviario():
    at = _load()
    a = at._result_write_keys("Ferroviario Nacala", "Costa do Sol")
    b = at._result_write_keys("Ferroviario Nampula", "Costa do Sol")
    assert a[0] != b[0]


def test_narrow_key_retained_as_fallback():
    """A feed that truncates the name must still settle.

    "Oliveira Hospita" is how one donor writes "Oliveira Hospital". The
    full-width keys differ, so the nine-character tier is the only thing
    that can link them, and it must still be there.
    """
    at = _load()
    keys = at._result_write_keys("Oliveira Hospital", "Benfica")
    truncated = at._result_write_keys("Oliveira Hospita", "Benfica")
    assert set(keys) & set(truncated), "the fallback tier was removed"
    settled = _settle(at, [{"home": "Oliveira Hospital", "away": "Benfica",
                            "result": "home"}])
    assert _grade(at, settled, "Oliveira Hospita", "Benfica") == "home"


def test_colliding_fixtures_both_settle():
    """Two clubs behind one truncated key: both grade, neither guesses."""
    at = _load()
    rows = [
        {"home": "Adelaide City", "away": "Sydney FC", "result": "home"},
        {"home": "Adelaide Cobras", "away": "Sydney FC", "result": "away"},
    ]
    settled = _settle(at, rows)
    assert _grade(at, settled, "Adelaide City", "Sydney FC") == "home"
    assert _grade(at, settled, "Adelaide Cobras", "Sydney FC") == "away"


def test_agreeing_outcomes_do_not_license_a_truncated_key():
    """The invisible half of the defect.

    Only one of the two colliding fixtures has been filed. The old guard
    saw a single outcome behind the key, concluded nothing could be
    mis-settled, and answered "home" for the match that is missing.
    """
    at = _load()
    settled = _settle(at, [{"home": "Manchester City", "away": "Arsenal",
                            "result": "home"}])
    assert _grade(at, settled, "Manchester City", "Arsenal") == "home"
    assert _grade(at, settled, "Manchester United", "Arsenal") is None, (
        "an unfiled fixture must not inherit its neighbour's result")


# --- B: an abbreviated word is the same club ----------------------------

def test_abbreviated_token_links_same_club():
    at = _load()
    assert at._same_club_names("Accrington St", "Accrington Stanley")
    assert at._same_club_names("Nottingham For", "Nottingham Forest")


def test_abbreviation_rule_does_not_overlink():
    at = _load()
    for a, b in [
        ("Manchester City", "Manchester Utd"),
        ("Juventud Unida SL", "Juventud Unida Univ."),
        ("Adelaide City", "Adelaide Cobras"),
        ("Ferroviario Nacala", "Ferroviario Nampula"),
    ]:
        assert not at._same_club_names(a, b), f"{a} must not link to {b}"


def test_squad_boundary_intact():
    """An abbreviation never crosses a youth/reserve/women's boundary."""
    at = _load()
    assert not at._same_club_names("Accrington St U21", "Accrington Stanley")
    assert not at._same_club_names("Turkey U21", "Turkey")


# --- C: a name that normalises away is not a key ------------------------

def test_empty_component_never_written():
    at = _load()
    for hk, ak in at._result_write_keys("Athletic Club", "Atletico FC"):
        assert hk.strip() and ak.strip(), "an empty key half was written"
    for hk, ak, _blind in at._exact_result_lookup_specs("B.93", "FC 1"):
        assert hk.strip() and ak.strip(), "an empty key half was looked up"


def test_structure_only_names_do_not_share_one_key():
    """Eleven clubs shared ('','') in the archive; the last row won."""
    at = _load()
    rows = [
        {"home": "Athletic Club", "away": "Sevilla", "result": "home"},
        {"home": "Atletico FC", "away": "Sevilla", "result": "away"},
    ]
    settled = _settle(at, rows)
    assert _grade(at, settled, "Athletic Club", "Sevilla") == "home"
    assert _grade(at, settled, "Atletico FC", "Sevilla") == "away"


# --- regression: WO-6 must keep settling --------------------------------

def test_wo6_turkiye_regression():
    at = _load()
    settled = _settle(at, [{"home": "Turkey", "away": "Spain",
                            "result": "home"}])
    assert _grade(at, settled, "Türkiye", "Spain") == "home"
