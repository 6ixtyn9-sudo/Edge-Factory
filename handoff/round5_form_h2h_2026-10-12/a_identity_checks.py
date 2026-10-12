"""A-2 / A-3 checks for the round-5 adjudication (2026-10-12).

Answers the reviewer's questions with measurements over the committed archives:

  A-3  is a reserve side with a roman-numeral suffix joined to its senior club?
       (the Ludogorets III question) — and which layers keep them apart.
  A-2  which layer actually fails for each proposed join (`base -> key`), the
       blast radius of a deterministic `utd -> united` token fold, the W3
       join-count before/after, and the evidence for the per-pair additions.
       The Al Ittihad question is a refusal check: are those rows one club?

    PYTHONPATH=src .venv/bin/python \
        handoff/round5_form_h2h_2026-10-12/a_identity_checks.py
"""
from __future__ import annotations


import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()   # every localdata write goes to scratch (incident 2026-10-12)

import re
import csv
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "src")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from edgefactory import form_intel as fi                        # noqa: E402
from edgefactory import identity as ident                       # noqa: E402
from edgefactory.util import ledger_team_key                    # noqa: E402
from intel_report import load_records                           # noqa: E402

LOCALDATA = "localdata"
WINDOW = 5
NAMED = ["Ludogorets III", "Ludogorets II", "Ludogorets", "Ludogorets Razgrad",
         "Kongsvinger 2", "Kongsvinger II", "Kongsvinger", "Newcastle U23s",
         "FC Porto B", "Porto II", "Porto",
         "Scunthorpe Utd", "Scunthorpe United", "Scunthorpe",
         "Newcastle Utd", "Newcastle United", "Newcastle",
         "Real Betis", "Betis", "FC Basel 1893", "Basel",
         "Al-Ittihad Alexandria", "Al Ittihad", "Al-Ittihad"]


def folded(name: object) -> str:
    """The candidate fold: the token ``utd`` is ``united``."""
    return " ".join("united" if w == "utd" else w
                    for w in ident.team_identity_words(name).split())


def fold_tokens(name: object) -> tuple[str, ...]:
    """Structure-stripped words under the fold — the key's own token stream."""
    return tuple(w for w in folded(name).split() if w not in ident.TEAM_STRUCTURE_NOISE)


def club_string(name: object) -> str:
    """The name's club words: spacing, structure tokens, United spelling gone."""
    return "".join("united" if w in ("utd", "united") else w for w in fold_tokens(name))


def same_club_by_words(a: tuple[str, str], b: tuple[str, str]) -> bool:
    """One club when one club string is the other with its first word dropped.

    Takes ``(raw name, club_string)`` pairs. The archive's spellings of one
    club are character-count truncations of each other (a prefix relation)
    and/or drop a leading honourific the feed omits ("Real Mallorca" /
    "Mallorca"). Only ever applied *within* a seam key group.
    """
    a_name, a_str = a
    b_name, b_str = b
    if a_str == b_str:
        return True
    short, long_ = sorted((a_str, b_str), key=len)
    if len(short) >= 4 and long_.startswith(short):
        return True
    if len(short) < 4:
        return False
    for name in (a_name, b_name):
        tokens = [t for t in folded(name).split() if t not in ident.TEAM_STRUCTURE_NOISE]
        stripped = "".join("united" if t == "utd" else t for t in tokens[1:])
        if len(tokens) > 1 and stripped == short:
            return True
    return False


def key_with(words_out: str) -> str:
    words = [w for w in words_out.split() if w not in ident.TEAM_STRUCTURE_NOISE]
    return re.sub(r"[^a-z0-9]", "", " ".join(words))[:24]


def aliases_with(key_fn) -> dict[str, str]:
    out: dict[str, str] = {}
    for alias, canonical in ident.TEAM_KEY_RAW_ALIASES + ident._curated_override_pairs():
        a, c = key_fn(alias), key_fn(canonical)
        if a and c:
            out[a] = c
    return out


def section_layers() -> None:
    print("== A-3/A-2 layer table: which layer carries the join?")
    print(f"{'name':24s} | {'base':22s} | {'source key':22s} | ledger key | markers")
    for name in NAMED:
        print(f"{name:24s} | {ident.source_team_key_base(name):22s} | "
              f"{ident.source_team_key(name):22s} | {ledger_team_key(name):10s} | "
              f"{sorted(ident.squad_markers(name))}")
    print()
    print("  reading: the join happens when the SOURCE KEY matches. The ledger key")
    print("  (width-9 norm_team) is the operational layer and is coarser; the source")
    print("  key is the voter-row seam form_intel reads.")
    print()


def section_reserve() -> None:
    print("== A-3 reserve check (the Ludogorets III question)")
    arch = fi.load_archive(LOCALDATA)
    for senior in ("Ludogorets Razgrad", "Kongsvinger", "FC Porto", "Porto"):
        rows = arch.team_rows(senior)
        reserve = [r for r in rows
                   if any(tok in str(r["home"]).lower() + " " + str(r["away"]).lower()
                          for tok in ("iii", " ii", " 2", "u23", "u21", "b "))]
        print(f"  team_rows({senior!r}) = {len(rows)} rows; of those, rows whose "
              f"fixture names a reserve-looking side: {len(reserve)}")
        for r in reserve[:5]:
            print(f"      {r['date']} {r['home']} {r['hs']}-{r['gs']} {r['away']}")
    print()
    print("  directly:")
    for pair in (("Ludogorets III", "Ludogorets Razgrad"),
                 ("Ludogorets II", "Ludogorets Razgrad"),
                 ("Kongsvinger 2", "Kongsvinger"),
                 ("Newcastle U23s", "Newcastle")):
        a, b = pair
        print(f"    source_team_key({a!r}) = {ident.source_team_key(a)!r}  vs "
              f"{b!r} = {ident.source_team_key(b)!r}  -> "
              f"{'JOINED' if ident.source_team_key(a) == ident.source_team_key(b) else 'distinct'}"
              f"  (marker mismatch {ident.squad_marker_mismatch(a, b)})")
    print()


def words_pre(name: object) -> str:
    """The word string BEFORE this round's change: no token fold."""
    return " ".join(w for w in ident.fold_identity_words(name).split() if w != "and")


def words_shipped(name: object) -> str:
    """The word string as shipped now (``and`` dropped, ``Utd`` -> ``United``)."""
    return ident.team_identity_words(name)


# the spellings this round added to the seam tables and to
# Config/entity_overrides.json (A-2). Listed here so "before" is the pre-change
# pipeline and nothing else.
ROUND_SPELLINGS = {
    "Accrington", "Accrington St", "Borussia Monchen", "Carrarese", "Charlton",
    "Ferroviaria", "JEF United", "JEF United Ichih", "Kidderminster",
    "Kidderminster Ha", "Scunthorpe Unite", "Zeljeznicar", "Mallorca",
    "Flint Town", "Omonia Nicosia F", "Aris Thessalonik", "Corvinul Hunedoa",
    "Newcastle", "Betis", "Basel",
}


def key_fn(words_fn, pairs, *, drop_round_spellings: bool):
    """Rebuild the seam key from a word function and an alias-pair list."""
    def base(name: object) -> str:
        words = [w for w in words_fn(name).split() if w not in ident.TEAM_STRUCTURE_NOISE]
        return re.sub(r"[^a-z0-9]", "", " ".join(words))[:24]

    aliases: dict[str, str] = {}
    for alias, canonical in pairs:
        a, c = base(alias), base(canonical)
        if a and c and not (drop_round_spellings and str(alias) in ROUND_SPELLINGS):
            aliases[a] = c
    return lambda name: aliases.get(base(name), base(name))  # noqa: E731


def section_fold(arch: fi.ResultsArchive) -> None:
    print("== A-2 the utd -> united fold and the per-pair additions")
    counts: Counter = Counter()
    for row in arch.rows:
        counts[row["home"]] += 1
        counts[row["away"]] += 1
    names = set(counts)
    utd = [n for n in names if "utd" in n.lower()]
    print(f"  archive: {len(names)} distinct spellings; {len(utd)} carry a 'utd' token")
    print("  top by rows:")
    for name, count in sorted(((n, counts[n]) for n in utd), key=lambda t: -t[1])[:8]:
        print(f"    {name:34s} x{count}")

    pairs_all = ident.TEAM_KEY_RAW_ALIASES + ident._curated_override_pairs()
    pairs_pre = tuple((a, c) for a, c in pairs_all
                      if str(a) not in ROUND_SPELLINGS)

    before = key_fn(words_pre, pairs_pre, drop_round_spellings=True)
    after = key_fn(words_shipped, pairs_all, drop_round_spellings=False)

    before_groups: dict[str, set[str]] = defaultdict(set)
    after_groups: dict[str, set[str]] = defaultdict(set)
    for name in names:
        before_groups[before(name)].add(name)
        after_groups[after(name)].add(name)

    changed = [n for n in names if before(n) != after(n)]
    new_merges = [(key, sorted(members)) for key, members in after_groups.items()
                  if len(members) > 1 and len({before(m) for m in members}) > 1]
    bad = []
    for key, members in new_merges:
        pairs = [(m, club_string(m)) for m in members]
        if not all(same_club_by_words(x, y) for i, x in enumerate(pairs)
                   for y in pairs[i + 1:]):
            bad.append((key, members))
    utd_groups = [(k, sorted(m)) for k, m in after_groups.items()
                  if len(m) > 1 and any("utd" in n.lower().split() for n in m)]
    utd_bad = []
    for key, members in utd_groups:
        pairs = [(m, club_string(m)) for m in members]
        if not all(same_club_by_words(x, y) for i, x in enumerate(pairs)
                   for y in pairs[i + 1:]):
            utd_bad.append((key, members))
    print(f"  spellings whose seam key changes: {len(changed)}")
    print(f"  key groups that merge two or more previous keys: {len(new_merges)}")
    print(f"  of those, groups whose members are NOT one club "
          f"(a wrong merge): {len(bad)}")
    for key, members in bad[:10]:
        print(f"    WRONG MERGE {key}: {members}")
    print(f"  every key group holding a Utd spelling: {len(utd_groups)}; "
          f"of those, wrong: {len(utd_bad)}")
    if utd_bad:
        for key, members in utd_bad[:10]:
            print(f"    WRONG MERGE {key}: {members}")
    print("  the new merges, in full (a wrong one is visible, not asserted away):")
    for key, members in new_merges:
        print(f"    {key:24s} <- {members}")

    print()
    print("  W3 census (fixture sides from the settled registry):")
    print("    before = the same key builder with the token fold off and this")
    print("             round's spellings removed (a model of the old key)")
    print("    after  = the SHIPPED source_team_key")
    print("    authoritative before/after, running the real old code from a")
    print("    worktree at the parent commit: a_census_worktree.txt")
    records = load_records(LOCALDATA)
    fixtures = sorted({(r["date"], r["home"], r["away"]) for r in records})
    sides = [(team, day) for day, home, away in fixtures for team in (home, away)]
    for label, key in (("before", before), ("after", ident.source_team_key)):
        fi.source_team_key = key
        arch2 = fi.load_archive(LOCALDATA)
        priors = sufficient = 0
        for team, day in sides:
            rows = arch2.prior_rows(team, day)
            priors += len(rows)
            sufficient += len(rows) >= WINDOW
        print(f"    {label:6s}: prior rows {priors:6d}   sides with >=5 priors "
              f"{sufficient:4d}/{len(sides)}")
    fi.source_team_key = ident.source_team_key
    print()


def section_al_ittihad(arch: fi.ResultsArchive) -> None:
    print("== A-2 refusal check: is 'Al Ittihad' one club?")
    for spelling in ("Al Ittihad", "Al-Ittihad", "Al-Ittihad Alexandria"):
        rows = [r for r in arch.rows if spelling in (r["home"], r["away"])]
        by_league = Counter(r["league"] or "(no league label)" for r in rows)
        print(f"  {spelling!r}: {len(rows)} rows")
        for league, count in by_league.most_common():
            opp = Counter((r["away"] if r["home"] == spelling else r["home"])
                          for r in rows if (r["league"] or "(no league label)") == league)
            print(f"      {league:28s} x{count:3d}   opponents: "
                  f"{', '.join(f'{n} x{c}' for n, c in opp.most_common(4))}")
    print()


def raw_rows() -> list[dict]:
    """Every committed result row, BEFORE the archive's identity dedup.

    The pair evidence must be read here: once two spellings are joined, the
    shipped archive keeps one row per fixture, so "the same fixture under both
    spellings" is no longer visible in it (measured 2026-10-12: the probe's
    first version read the deduped archive and reported 0 mutual fixtures for
    every pair, including the pairs whose evidence was already on record).
    """
    rows: list[dict] = []
    for path in sorted(Path(LOCALDATA).glob("betexplorer_results_*.csv.gz")):
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
            for raw in csv.DictReader(fh):
                if raw.get("home") and raw.get("away") and raw.get("date"):
                    rows.append({"date": str(raw["date"]).strip(),
                                 "home": str(raw["home"]).strip(),
                                 "away": str(raw["away"]).strip(),
                                 "league": str(raw.get("league") or "").strip(),
                                 "source": path.name})
    settled = Path(LOCALDATA) / "settled_results.json"
    if settled.exists():
        doc = json.loads(settled.read_text(encoding="utf-8"))
        for raw in doc.get("rows") or []:
            home, away = str(raw.get("home") or "").strip(), str(raw.get("away") or "").strip()
            if home and away and raw.get("date"):
                rows.append({"date": str(raw["date"]).strip(), "home": home, "away": away,
                             "league": "", "source": settled.name})
    return rows


# every spelling this round added to the curated tables, with its canonical
# side; the evidence class is decided by what the raw files show.
ROUND_PAIRS = (
    ("Betis", "Real Betis"),
    ("Basel", "FC Basel 1893"),
    ("Accrington", "Accrington Stanley"),
    ("Accrington St", "Accrington Stanley"),
    ("Borussia Monchen", "Borussia M'gladbach"),
    ("Carrarese", "Carrarese Calcio"),
    ("Charlton", "Charlton Athletic"),
    ("Ferroviaria", "Ferroviária SP"),
    ("JEF United", "JEF United Chiba"),
    ("JEF United Ichih", "JEF United Chiba"),
    ("Kidderminster", "Kidderminster Harriers"),
    ("Kidderminster Ha", "Kidderminster Harriers"),
    ("Scunthorpe Unite", "Scunthorpe United"),
    ("Zeljeznicar", "Zeljeznicar Sarajevo"),
    ("Mallorca", "Real Mallorca"),
    ("Flint Town", "Flint Town Utd"),
    ("Omonia Nicosia F", "Omonia Nicosia"),
    ("Aris Thessalonik", "Aris Thessalonikis"),
    ("Corvinul Hunedoa", "Corvinul Hunedoara"),
    ("Newcastle", "Newcastle United"),
)


def section_pairs() -> None:
    """Per-pair evidence: mutual fixtures where they exist, else the row case.

    The memo's rule for a bare/truncated form is that the pair has to be shown
    to denote ONE club. Two evidence classes are printed here and named as such
    in the curated tables: "mutual" (the same date + opponent served under both
    spellings) and "row" (every row of the spelling belongs to the one club's
    own competition and opponents - the same test Al Ittihad fails).
    """
    print("== A-2 per-pair evidence (raw files, pre-dedup)")
    print(f"  {'spelling':20s} {'rows':>5s} {'mutual':>7s}  leagues / top opponents")
    rows = raw_rows()
    classes: Counter = Counter()
    for spelling, canonical in ROUND_PAIRS:
        mine = [r for r in rows if spelling in (r["home"], r["away"])]
        other = [r for r in rows if canonical in (r["home"], r["away"])]
        index: dict[tuple[str, str], set[str]] = defaultdict(set)
        for row in rows:
            for name, opp in ((row["home"], row["away"]), (row["away"], row["home"])):
                if name in (spelling, canonical):
                    index[(row["date"], opp)].add(name)
        mutual = sum(1 for names in index.values() if len(names) > 1)
        leagues = Counter(r["league"] or "no label" for r in mine)
        opps = Counter((r["away"] if r["home"] == spelling else r["home"]) for r in mine)
        top = ", ".join(f"{k} x{v}" for k, v in leagues.most_common(3))
        names = ", ".join(f"{k} x{v}" for k, v in opps.most_common(3))
        classes["mutual" if mutual else "row"] += 1
        print(f"  {spelling:20s} {len(mine):>5d} {mutual:>7d}  {top}")
        print(f"  {'':20s} {'':>5s} {'':>7s}  vs {names}")
    print(f"  classes: {classes['mutual']} pair(s) with mutual fixtures, "
          f"{classes['row']} on the row case alone (of {len(ROUND_PAIRS)})")
    print()
    print("  class per pair: mutual>0 -> 'mutual' evidence; mutual=0 -> the row")
    print("  case above must show one club's own competition (checked by eye in")
    print("  the curated file's comments, which name the fixtures). Pairs with")
    print("  neither are not added: 'Al Ittihad' (three countries' leagues) is")
    print("  refused, and the bare forms that only repeat the club's own league")
    print("  are the ones listed above.")
    print()


def section_evidence() -> None:
    print("== A-2 same-club evidence for the per-pair additions")
    print("  read from the RAW committed files (pre-dedup): a mutual fixture is")
    print("  the same date + opponent served under both spellings")
    rows = raw_rows()
    for a, b in (("Real Betis", "Betis"), ("FC Basel 1893", "Basel"),
                 ("Scunthorpe Utd", "Scunthorpe"), ("Scunthorpe Utd", "Scunthorpe United"),
                 ("Newcastle Utd", "Newcastle")):
        index: dict[tuple[str, str], set[str]] = defaultdict(set)
        leagues: dict[tuple[str, str], set[str]] = defaultdict(set)
        for row in rows:
            for spelling, other in ((row["home"], row["away"]), (row["away"], row["home"])):
                if spelling in (a, b):
                    index[(row["date"], other)].add(spelling)
                    leagues[(row["date"], other)].add(row["league"])
        both = [(day, other) for (day, other), sp in index.items() if len(sp) > 1]
        print(f"  {a} / {b}: {len(both)} same-date same-opponent fixture(s) under both")
        for day, other in sorted(both)[:6]:
            labels = ", ".join(sorted(x for x in leagues[(day, other)] if x)) or "no label"
            print(f"      {day}  vs {other:28s} league={labels}")
    print()


def main() -> None:
    print("identity checks — command: PYTHONPATH=src .venv/bin/python "
          "handoff/round5_form_h2h_2026-10-12/a_identity_checks.py")
    arch = fi.load_archive(LOCALDATA)
    section_layers()
    section_reserve()
    section_fold(arch)
    section_al_ittihad(arch)
    section_pairs()
    section_evidence()


if __name__ == "__main__":
    main()
