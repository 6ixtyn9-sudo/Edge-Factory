#!/usr/bin/env python3
"""WO-7 acceptance gate: ambiguous settlement keys.

Runs on a bare `python3` (no venv, no third-party installs). Every check
is BEHAVIOURAL and uses only names that already exist in
scripts/auto_tickets.py today, so it cannot be satisfied by renaming
things. `None` = pass, a string = fail, an exception = fail.

    python3 scripts/verify_wo7.py
"""
from __future__ import annotations

import importlib.abc
import importlib.util
import sys
import types

sys.path.insert(0, "src")

_OPTIONAL = {
    "curl_cffi", "dotenv", "bs4", "lxml", "requests", "supabase",
    "httpx", "duckdb", "pandas", "sklearn", "scipy", "joblib", "numpy",
}


class _Any:
    def __call__(self, *a, **k):
        return _Any()

    def __getattr__(self, n):
        return _Any()

    def __iter__(self):
        return iter(())


class _StubLoader(importlib.abc.Loader):
    def create_module(self, spec):
        m = types.ModuleType(spec.name)
        m.__getattr__ = lambda n: _Any()
        return m

    def exec_module(self, m):
        pass


class _StubFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in _OPTIONAL:
            return importlib.util.spec_from_loader(name, _StubLoader())
        return None


sys.meta_path.append(_StubFinder())

_spec = importlib.util.spec_from_file_location("at", "scripts/auto_tickets.py")
at = importlib.util.module_from_spec(_spec)
sys.modules["at"] = at
_spec.loader.exec_module(at)

RESULTS: list[tuple[str, str, object]] = []


def check(task, name):
    def deco(fn):
        try:
            RESULTS.append((task, name, fn()))
        except Exception as exc:  # noqa: BLE001
            RESULTS.append((task, name, f"EXCEPTION {type(exc).__name__}: {exc}"))
        return fn
    return deco


# --------------------------------------------------------------- FAULT A
# One 9-character key covers several real clubs. Adelaide City,
# Adelaide Cobras, Adelaide Comets and Adelaide Croatia Raiders all
# reduce to 'adelaidec'. A more specific key must be tried FIRST.

@check("A", "most_specific_key_separates_distinct_clubs")
def _a1():
    a = at._result_write_keys("Adelaide City", "Adelaide Comets")
    b = at._result_write_keys("Adelaide Cobras", "Adelaide Croatia Raiders")
    if not a or not b:
        return f"no write keys produced: {a!r} {b!r}"
    if a[0] == b[0]:
        return (f"most specific key is identical for two different fixtures: "
                f"{a[0]!r}")
    return None


@check("A", "most_specific_key_separates_ferroviario")
def _a2():
    a = at._result_write_keys("Ferrovi\u00e1rio Nacala", "Ferrovi\u00e1rio de Lichinga")
    b = at._result_write_keys("Ferrovi\u00e1rio Nampula", "Ferrovi\u00e1rio Maputo")
    if a[0] == b[0]:
        return f"Ferroviario cluster still collides on {a[0]!r}"
    return None


@check("A", "narrow_key_retained_as_fallback")
def _a3():
    a = at._result_write_keys("Adelaide City", "Adelaide Comets")
    if ("adelaidec", "adelaidec") not in a:
        return ("the 9-char key was REMOVED rather than demoted; it must "
                "remain as a last-resort fallback so loosely-spelled "
                f"result feeds still join. got {a!r}")
    return None


# --------------------------------------------------------------- FAULT B
# _same_club_names calls a truncated spelling a different club, so a
# settleable leg is refused forever.

@check("B", "abbreviated_token_links_same_club")
def _b1():
    bad = [p for p in [("Accrington St", "Accrington Stanley"),
                       ("Sheffield Wed", "Sheffield Wednesday"),
                       ("Nottingham For", "Nottingham Forest")]
           if not at._same_club_names(*p)]
    return f"should link but do not: {bad}" if bad else None


@check("B", "abbreviation_rule_does_not_overlink")
def _b2():
    bad = [p for p in [("Manchester City", "Manchester Utd"),
                       ("Manchester City", "Manchester United"),
                       ("Juventud Unida SL", "Juventud Unida Univ."),
                       ("Adelaide City", "Adelaide Cobras"),
                       ("Ferrovi\u00e1rio Nacala", "Ferrovi\u00e1rio Nampula")]
           if at._same_club_names(*p)]
    return f"must stay distinct but were linked: {bad}" if bad else None


@check("B", "squad_boundary_intact")
def _b3():
    bad = [p for p in [("Manchester City", "Manchester City U21"),
                       ("Malm\u00f6 FF", "Malm\u00f6 FF W"),
                       ("USA", "USA U17")]
           if at._same_club_names(*p)]
    return f"senior/youth/women boundary crossed: {bad}" if bad else None


# --------------------------------------------------------------- FAULT C
# Names made entirely of structure tokens normalise to the empty string
# and are written into the settled map as ('', ''). Every such club
# collides with every other such club on the same date.

@check("C", "empty_component_never_written")
def _c1():
    bad = []
    for h, a in [("Athletic Club", "Atletico FC"), ("B.93", "FC 1"),
                 ("Athletic Club", "B.93")]:
        for hk, ak in at._result_write_keys(h, a):
            if not str(hk).strip() or not str(ak).strip():
                bad.append((h, a, (hk, ak)))
    return f"empty settlement key written: {bad}" if bad else None


# --------------------------------------------------------------- END TO END

@check("D", "colliding_fixtures_both_settle")
def _d1():
    day = "2026-03-28"
    rows = [
        {"home": "Adelaide City", "away": "Adelaide Comets", "outcome": "home"},
        {"home": "Adelaide Cobras", "away": "Adelaide Croatia Raiders",
         "outcome": "away"},
    ]
    entries = {day: [dict(r) for r in rows]}
    key_to = {}
    for r in rows:
        for hk, ak in at._result_write_keys(r["home"], r["away"]):
            key_to[(day, hk, ak)] = r["outcome"]

    dropped, detail = at._drop_ambiguous_result_keys(key_to, entries)
    if dropped:
        return (f"two genuinely different fixtures still collapse to one "
                f"key and were dropped ({dropped}): {detail}")

    for r in rows:
        got = {key_to.get((day, hk, ak))
               for hk, ak in at._result_write_keys(r["home"], r["away"])
               if (day, hk, ak) in key_to}
        if got != {r["outcome"]}:
            return (f"{r['home']} vs {r['away']} resolves to {got!r}, "
                    f"expected {{'{r['outcome']}'}}")
    return None


@check("D", "wo6_turkiye_regression")
def _d2():
    if not at._same_club_names("T\u00fcrkiye", "Turkey"):
        return "WO-6 regression: Turkiye no longer links to Turkey"
    a = set(at._result_write_keys("Italy", "T\u00fcrkiye"))
    b = set(at._result_write_keys("Italy", "Turkey"))
    if not (a & b):
        return (f"WO-6 regression: Italy vs Turkiye and Italy vs Turkey "
                f"share no settlement key. {a!r} vs {b!r}")
    return None


def main() -> int:
    width = max(len(n) for _, n, _ in RESULTS)
    failed = 0
    for task, name, res in RESULTS:
        ok = res is None
        failed += 0 if ok else 1
        print(f"[{task}] {name.ljust(width)}  "
              f"{'PASS' if ok else 'FAIL'}" + ("" if ok else f"  -> {res}"))
    total = len(RESULTS)
    print(f"\n{total - failed}/{total} checks pass")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
