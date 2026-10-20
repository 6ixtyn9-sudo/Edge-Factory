"""Shared identity folding for team and league names.

Provenance: 2026-09-22 Dagenham incident. Two voter spellings of one
fixture ("Dagenham & Redbridge" vs "Dagenham and Redbridge", league
"FA" vs "England,Fa Cup") produced two distinct pick rows that rode
together into one acca card. The 782f3f5 emergency guard dedups at
slip-planning time; this module applies the same fold at the identity
seam so the duplicates die at capture and so every downstream consumer
(slips, purity contexts, diagnostics) shares ONE definition of
"same fixture" / "same league".

Hard rules:

1. FOLDS ONLY, NO FUZZ. Deterministic text folding plus an explicit,
   evidence-seeded alias table. Nothing here guesses similarity; two
   different real entities must never collapse into one key.
2. ADDITIVE WIRING. Callers keep their legacy lookup order intact;
   folded forms/aliases only add coverage that previously returned
   UNKNOWN.
3. SCOPE. Used for *identity* seams: voter-row indexing, purity/entity
   canonicalisation, slip dedup. Odds/price-matching keys
   (alias_fuzzy quarantine surface) are deliberately out of scope.
4. The research ml-fade ledger identity fold lives in
   edgefactory/ml_fade_research.py and stays frozen there for ledger
   reconciliation stability; this module mirrors its fold semantics
   (``&`` -> ``and``, punctuation collapse) plus accent folding.
"""

from __future__ import annotations

import re

from .util import fold_ascii

_WS_RE = re.compile(r"\s+")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9 ]+")


def fold_identity_words(name: object) -> str:
    """ASCII-fold, lowercase, ``&`` -> ``and``, punctuation -> space.

    Total and deterministic; idempotent; invariant under ``&`` vs ``and``
    spellings and under punctuation/case choice. Output is a
    space-separated word string (empty string for empty input).
    """
    s = fold_ascii(name).replace("&", " and ")
    s = _NON_ALNUM_RE.sub(" ", s)
    return _WS_RE.sub(" ", s).strip()


# One-token abbreviation folds. Several feeds abbreviate systematically -
# BetExplorer serves "Newcastle Utd", "Man Utd", "Scunthorpe Utd" while the
# archive spells the club out - so a per-pair patch leaves the same join
# broken across the corpus. Measured 2026-10-12 over the committed archives:
# 137 of 23,239 distinct spellings carry the token; folding it merges 78 key
# groups, and every one of those groups is the same club once spacing and the
# United spelling are set aside (0 wrong merges: no two real clubs differ only
# by United/Utd). Full list:
# handoff/round5_form_h2h_2026-10-12/a_identity_checks.txt
TEAM_TOKEN_FOLDS: dict[str, str] = {"utd": "united"}


def team_identity_words(name: object, *, fold_tokens: bool = True) -> str:
    """Team identity words: ``and`` dropped, abbreviations folded.

    ``Dagenham & Redbridge`` and ``Dagenham and Redbridge`` both become
    ``dagenham redbridge``. ``and`` is only ever produced by the ``&``
    fold in real club names here; dropping it as a standalone token is
    the exact unification the incident required. Compound words that
    merely contain ``and`` (e.g. ``Wanderers``) are untouched because
    removal is word-level. ``TEAM_TOKEN_FOLDS`` applies the same
    word-level rule to abbreviations of one word (``Utd`` -> ``United``).

    ``fold_tokens=False`` gives the historical rule (``and`` dropped,
    abbreviations kept). The persisted operational key layers pass it -
    their keys are stored in ``localdata`` (the purity registry, learned
    aliases) and joined against data written before the fold existed, so
    a fold there would orphan stored evidence; the seam carries the fold.
    """
    words = fold_identity_words(name).split()
    if fold_tokens:
        words = [TEAM_TOKEN_FOLDS.get(w, w) for w in words]
    return " ".join(w for w in words if w != "and")


def fold_league_identity(name: object) -> str:
    """League fold: identity words, no token dropping."""
    return fold_identity_words(name)


# Explicit alias pairs, each PROVEN same-league by archive evidence:
# the same (date, folded home, folded away) fixture appearing under both
# spellings in the same slate. Targets are the purity-registry keys so
# pool/verdict lookups resolve.
LEAGUE_ALIASES: dict[str, str] = {
    "england fa cup": "fa",  # 2026-09-22 Dagenham vs Waltham Abbey under both
    # The 2026-10-20 persisted assay registry has 19 `nls` contexts, not
    # the former sponsored-name key. The committed capture has 538 matching
    # date/team fixtures under NLs and the exact Statarea regular-season label.
    # Preserve the CODE already used by those contexts; never invent evidence
    # under a missing sponsor key or fold North/youth/playoffs into this league.
    "england national league south": "nls",
    "enterprise national league south": "nls",
}


def canonical_league_key(name: object) -> str:
    """Fold a raw league label, then apply explicit evidence aliases."""
    folded = fold_league_identity(name)
    return LEAGUE_ALIASES.get(folded, folded)


# ---------------------------------------------------------------------------
# Source (voter-row) team key — the width-9-collision fix (2026-09-22
# red-team follow-up, operator-directed).
#
# Legacy norm_team (width 9 + honorific/w/ii/b/res noise stripping) makes
# unrelated teams collide on one voter key ('atletico madrid' ==
# 'realmadrid' vs.  'real madrid' == 'madrid' -> Atletico vs Real both
# "madrid"; "Arsenal" == "Arsenal W"; "FC Porto" == "FC Porto B").
# Colliding keys mis-attach wrong-match evidence for same-day same-source
# fixtures. This key keeps 24 chars and every squad distinguisher
# (w/ii/b/res/youth tokens), strips ONLY pure club-structure tokens, folds
# '&' <-> 'and' and accents, then applies explicit same-club aliases.

TEAM_STRUCTURE_NOISE = frozenset(
    {"fc", "cf", "sc", "ac", "cd", "ca", "club",
     "sk", "if", "fk", "bk", "ik", "ff"}  # Nordic club tokens (corpus-evidenced)
)


def source_team_key_base(name: object, *, width: int = 24,
                         fold_tokens: bool = True) -> str:
    """Structure-stripped key. ``fold_tokens=False`` is the historical rule.

    The token fold (``utd`` -> ``united``) is a WORD rule, so it is applied
    inside ``team_identity_words``; a caller that needs the PRE-fold key -
    the compatibility guard in ``auto_tickets``, which checks that a stored
    pre-fold key really is what this spelling used to produce - passes
    ``fold_tokens=False`` and otherwise runs the identical code path.
    """
    words = [
        w for w in team_identity_words(name, fold_tokens=fold_tokens).split()
        if w not in TEAM_STRUCTURE_NOISE
    ]
    return re.sub(r"[^a-z0-9]", "", " ".join(words))[:width]


# Explicit same-club pairs, each proven by corpus evidence or structural
# argument (abbreviation / transliteration / geographic or nickname suffix
# of ONE club — never two clubs). Keys/targets are DERIVED through
# source_team_key_base so the table can never drift from the key function.
TEAM_KEY_RAW_ALIASES: tuple[tuple[str, str], ...] = (
    # legacy alias map, re-expressed in raw-name space
    ("Thunder SC", "Dandenong Thunder"),
    ("Hobart Zebras", "Clarence Zebras"),
    ("Neftchi", "Neftchi Fergana"),
    ("Dila", "Dila Gori"),
    # corpus-audited same-club pairs (2026-09-22 red-team pass)
    ("Borussia M'gladbach", "Borussia Monchengladbach"),
    ("Rodina Moscow", "Rodina Moskva"),
    ("Tekstilshchik Iv.", "Tekstilshtik Ivanovo"),
    ("Grasshopper-Club", "Grasshoppers"),
    ("Ferencvaros", "Ferencvarosi TC"),
    ("Haverfordwest", "Haverfordwest County"),
    ("Ludogorets", "Ludogorets Razgrad"),
    ("Broadmeadow", "Broadmeadow Magic"),
    ("Leicester", "Leicester City"),
    ("West Torrens", "West Torrens Birkalla"),
    ("Bayern Munich", "Bayern Munchen"),
    # curated national-team exonyms / renames (2026-10-05 Türkiye split).
    # Transliteration alone cannot join these: "turkiye" != "turkey".
    # Mirrors Config/entity_overrides.json -> teams (same curated pairs).
    ("Türkiye", "Turkey"),
    ("Czechia", "Czech Republic"),
    ("Ivory Coast", "Côte d'Ivoire"),
    ("Cabo Verde", "Cape Verde"),
    # pinnapi probe 2026-10-10 run#4: Manchester United–Tottenham, England Premier League
    ("Tottenham", "Tottenham Hotspur"),
    # 2026-10-13 picks card: the same UCL fixture (Inter v Club Brugge, 13-10,
    # 19:00Z) was listed twice, once as "Club Brugge KV" (the club's official
    # name) and once as "Club Brugge". Same date, opponent and competition.
    ("Club Brugge KV", "Club Brugge"),
    # pinnapi probe 2026-10-10 run#4: Rizespor–Fenerbahçe, Turkey Super League (not U19)
    ("Rizespor", "Caykur Rizespor"),
    # pinnapi probe 2026-10-10 run#4: SC Paderborn 07–VfB Stuttgart, Germany Bundesliga
    ("SC Paderborn 07", "Paderborn"),
    # pinnapi probe 2026-10-10 run#4: SC Paderborn 07–VfB Stuttgart, Germany Bundesliga
    ("VfB Stuttgart", "Stuttgart"),
    # pinnapi probe 2026-10-10 run#4: Arsenal–Leeds, England Premier League
    ("Leeds", "Leeds United"),
    # pinnapi probe 2026-10-10 run#4: 1899 Hoffenheim–Hamburger SV, Germany Bundesliga
    ("1899 Hoffenheim", "Hoffenheim"),
    # pinnapi probe 2026-10-10 run#4: AFC Fylde–Scunthorpe, England National League
    ("Scunthorpe", "Scunthorpe United"),
    # betexplorer archive 2026-10-12: the same 2026-08-05 Arsenal–Real Betis
    # Club Friendly fixture is spelled "Betis" in the monthly archive and
    # "Real Betis" on the pick surface (7 same-date, same-opponent fixtures
    # under both spellings: 2026-07-29 Lyon, 08-01 Almeria, 08-05 Arsenal,
    # 08-08 Bournemouth)
    ("Betis", "Real Betis"),
    # ------------------------------------------------------------------
    # 2026-10-12 adjudication (A-2): bare/abbreviated spellings the archive
    # serves for one club, each with its evidence. Two evidence classes:
    # "mutual" = the same date+opponent fixture under both spellings; "row"
    # = rows whose opponents and competition belong to that one club (listed).
    # The measurement script and every row are in
    # handoff/round5_form_h2h_2026-10-12/a_identity_checks.txt.
    ("Accrington", "Accrington Stanley"),        # evidence: row-case-only - 26 League Two rows vs the club's own league (a_identity_checks.txt, A-2 per-pair table)
    ("Accrington St", "Accrington Stanley"),     # mutual x4 (Crawley, Barnet, Newport, Salford)
    ("Borussia Monchen", "Borussia M'gladbach"), # mutual x2 (RB Leipzig, SV Elversberg)
    ("Carrarese", "Carrarese Calcio"),           # mutual x4 (Torino, Ascoli, Empoli, Padova)
    ("Charlton", "Charlton Athletic"),           # mutual x3 (Cheltenham, West Ham, Tottenham)
    ("Ferroviaria", "Ferroviária SP"),           # mutual x2 (Figueirense, Paysandu)
    # NB: "Ferroviario" (Serie D / Cearense, x31) is a DIFFERENT club - not aliased.
    ("JEF United", "JEF United Chiba"),          # mutual x8 (Machida, FC Tokyo, Kawasaki ...)
    ("JEF United Ichih", "JEF United Chiba"),    # mutual x6 (truncated spelling of the same club)
    ("Kidderminster", "Kidderminster Harriers"), # mutual x2 (AFC Hornchurch, Southend)
    ("Kidderminster Ha", "Kidderminster Harriers"),  # evidence: row-case-only - NL North, opponents Halesowen/Stourbridge (a_identity_checks.txt)
    ("Scunthorpe Unite", "Scunthorpe United"),   # evidence: row-case-only - truncation of the same club (mutual count is 0; the row case carries it)
    ("Zeljeznicar", "Zeljeznicar Sarajevo"),     # mutual x2 (BSK Banja Luka, Zrinjski)
    ("Mallorca", "Real Mallorca"),               # evidence: row-case-only - 21 LaLiga rows, only LaLiga club of the name
    ("Flint Town", "Flint Town Utd"),            # row: Cymru Premier opponents (TNS, Connahs Quay)
    ("Omonia Nicosia F", "Omonia Nicosia"),      # mutual x7 (Lincoln Red Imps twice, Aradippou ...)
    ("Aris Thessalonik", "Aris Thessalonikis"),  # evidence: row-case-only - Greek top-flight opponents (PAOK, OFI, Volos)
    ("Corvinul Hunedoa", "Corvinul Hunedoara"),  # evidence: row-case-only - Romanian opponents (CFR Cluj, Csikszereda)
    ("Newcastle", "Newcastle United"),           # mutual x11 (the EPL side; the archive's own
    #                                              spelling of the fixture this round was read for)
    # betexplorer archive 2026-10-12: 2026-08-01 Basel–Lausanne, Switzerland
    # Super League appears under both spellings ("Basel" x38 rows, "FC Basel
    # 1893" on the pick surface)
    ("Basel", "FC Basel 1893"),
    # pinnapi probe 2026-10-10 run#4: Kairat Almaty–Zhetysu, Kazakhstan Premier League
    ("Zhetysu", "Zhetysu Taldykorgan"),
    # pinnapi probe 2026-10-10 run#4: Genk–Kortrijk, Belgium Pro League
    ("Kortrijk", "KV Kortrijk"),
    # pinnapi probe 2026-10-10 run#4: Grazer AK–Red Bull Salzburg, Austria Bundesliga
    ("Red Bull Salzburg", "Salzburg"),
    # pinnapi probe 2026-10-10 run#4: Al-Tadhamon–Al-Qadsia, Kuwait Premier League
    ("Al-Tadhamon", "Al Tadamon"),
    # pinnapi probe 2026-10-10 run#4: Al-Tadhamon–Al-Qadsia, Kuwait Premier League
    ("Al-Qadsia", "Qadsia SC"),
    # pinnapi probe 2026-10-10 run#4: York–Northampton, England League 2
    ("York", "York City"),
    # pinnapi probe 2026-10-10 run#4: York–Northampton, England League 2
    ("Northampton", "Northampton Town"),
    # pinnapi probe 2026-10-10 run#4: RAAL La Louvière–Club Brugge KV, Belgium Pro League (senior only)
    ("Club Brugge KV", "Club Brugge"),
    # pinnapi probe 2026-10-10 run#4: Vilzing–Buchbach, Germany Regionalliga Bavaria
    ("Vilzing", "DJK Vilzing"),
    # pinnapi probe 2026-10-10 run#4: Leixoes–FC Porto B, Portugal Liga 2 (reserve only)
    ("FC Porto B", "Porto II"),
    # pinnapi probe 2026-10-10 run#4: Zemplin Michalovce–Dunajska Streda, Slovakia Super Liga
    ("Dunajska Streda", "DAC 1904"),
    # ------------------------------------------------------------------
    # 2026-10-21 name audit, fix 2: same-club pairs found by joining the Aug-Oct
    # pick and odds fixtures to the archive on the fixture date (one side or
    # both sides differ only by abbreviation, a cut, a suffix or a
    # transliteration; the other side of each fixture matches too). Pairs where
    # the two names could be different clubs or squads are NOT listed
    # (e.g. Wiener SC / Wiener SK, Club America / Tigres, Valencia W / Athletic
    # Club W, Kolos Kovalivka II, Gornik Zabrze II, Volos FC, Ararat / Ararat-Armenia).
    ("Sarpsborg 08", "Sarpsborg FK"),
    ("Grasshopper Zürich", "Grasshoppers"),
    ("NK Celje", "Celje"),
    ("Huddersfield Tow", "Huddersfield Town"),
    ("Wimbledon", "AFC Wimbledon"),
    ("OB Odense", "Odense"),
    ("FC Twente Ensche", "FC Twente Enschede"),
    ("Iraklis 1908", "Iraklis FC"),
    ("Aris Thessaloniki", "Aris Thessalonikis"),
    ("Atalanta BC", "Atalanta"),
    ("AS Monaco", "Monaco"),
    ("PFC CSKA Sofia", "CSKA Sofia"),
    ("PFC Levski Sofia", "Levski Sofia"),
    ("Stade Brestois 29", "Stade Brestois"),
    ("Shelbourne Dublin", "Shelbourne FC"),
    ("Portland Hearts", "Portland Hearts Of Pine"),
    ("Vancouver Whitec", "Vancouver Whitecaps"),
    ("Saint Louis City", "St. Louis City"),
    ("Philadelphia Uni", "Philadelphia Union"),
    ("Universidad de Chile", "Universidad Chile"),
    ("Club Universidad de Chile", "Universidad Chile"),
    ("Sporting Braga", "SC Braga"),
    ("GD Estoril", "Estoril"),
    ("Enugu Rangers In", "Enugu Rangers"),
    ("Omonia 29is Maiou", "Omonia 29th May"),
    ("AEK Larnaka", "AEK Larnaca"),
    ("Qabala", "Gabala"),
    ("AI Kahrabaa", "Al-Kahrabaa"),
    ("Atletico-MG", "Atletico Mineiro"),
    ("Sporting KC", "Sporting Kansas City"),
    ("1. FC Nürnberg", "Nurnberg"),
    ("1. FC Heidenheim", "FC Heidenheim"),
    ("Genclerbirligi", "Gençlerbirliği S.K."),
    ("Vukovar '91", "Vukovar 1991"),
    ("Viimsi JK", "Viimsi"),
    ("Viimsi MRJK", "Viimsi"),
    ("Maccabi Kabilio Jaffa", "Maccabi Kabilio"),
    ("Hapoel Acre", "Hapoel Ironi Acre"),
    ("Hapoel Kfar Shalem", "Hapoel Kfar Shal"),
    ("Bnei Yehuda Tel", "Bnei Yehuda"),
    ("Maccabi Kiryat Gat", "Maccabi Kiryat G"),
    ("AZ Alkmaar", "AZ"),
    ("Kheybar Khorramabad", "Kheybar Khorrama"),
    ("Vikingur Reykjavik", "Vikingur Reykjav"),
    ("Throttur Reykjavik", "Trottur Reykjavik"),
    ("Jeonbuk Hyundai Motors", "Jeonbuk Hyundai"),
    ("Besiktas JK", "Besiktas"),
    ("BK Hacken", "Hacken"),
    ("Orgryte IS", "Orgryte"),
    ("Sparta Prague", "Sparta Praha"),
    ("NEC Nijmegen", "NEC"),
    ("CS Maritimo", "Maritimo"),
    ("Central Cordoba de Santiago", "Central Córdoba SdE"),
    ("Povltava FA", "Povltavska FA"),
    ("Comerciantes Unidos", "CD Comerciantes"),
    ("Univ. Concepción", "Universidad de Concepción"),
    ("Universidad de C", "Universidad de Concepción"),
)

def _curated_override_pairs() -> tuple[tuple[str, str], ...]:
    """Curated team aliases from Config/entity_overrides.json.

    SINGLE SOURCE OF TRUTH: the voter-row seam derives its aliases from
    the same reviewed file the entity/context layer uses, so the two
    curated tables can no longer drift (2026-10-05 sweep found four that
    already had: Ulsan Hyundai, KPV-j, Zvyagel, Maxline were canonicalized
    for contexts but still split at the voter-row seam).
    """
    from .util import team_alias_table

    pairs: list[tuple[str, str]] = []
    for raw, canonical in sorted(team_alias_table().items()):
        if not raw or not canonical or raw == canonical:
            continue
        # keep only human-readable spellings, not the derived key forms
        if raw.islower() and " " not in raw and raw != canonical.lower():
            continue
        pairs.append((raw, str(canonical)))
    return tuple(pairs)


_ALIAS_STEPS: dict[str, str] = {
    source_team_key_base(alias): source_team_key_base(canonical)
    for alias, canonical in TEAM_KEY_RAW_ALIASES + _curated_override_pairs()
    if source_team_key_base(alias) and source_team_key_base(canonical)
}


def _alias_fixed_point(key: str) -> str:
    """Follow the alias map to its fixed point.

    Needed because a target spelling can itself be an alias in the curated
    file (``Borussia M'gladbach`` -> ``Borussia Monchengladbach``), and a
    single hop would then make a pair disagree with its own target. Measured
    2026-10-12: among 160 alias keys only the one pair added that day moves
    under this resolution, and over 13,517 archive/curated spellings exactly
    one spelling's key moves - so the table was already closed and this only
    removes the footgun. The guard stops on a revisit: a cycle is a table
    defect, and returning the key is safer than looping.
    """
    seen = {key}
    while key in _ALIAS_STEPS:
        nxt = _ALIAS_STEPS[key]
        if nxt in seen:
            break
        seen.add(nxt)
        key = nxt
    return key


TEAM_KEY_ALIASES: dict[str, str] = {
    key: _alias_fixed_point(key) for key in _ALIAS_STEPS
}
TEAM_KEY_ALIASES = {key: value for key, value in TEAM_KEY_ALIASES.items()
                    if value != key}


def source_team_key(name: object, *, fold_tokens: bool = True) -> str:
    """Identity-folded voter-row team key with alias resolution.

    ``fold_tokens=False`` answers the key the PRE-fold rule produced for a
    spelling: alias resolution included, token folding off. The alias map's
    keys are derived through the folding base, so a pre-fold lookup can miss
    an entry whose key only exists in folded space - that direction is
    deliberate, because a miss asks the caller to fail closed rather than to
    guess which club was meant.
    """
    key = source_team_key_base(name, fold_tokens=fold_tokens)
    return TEAM_KEY_ALIASES.get(key, key)


def migrate_folded_key(name: object) -> str:
    """Re-spell a STORED key whose tail is a folded token (``utd``).

    The token fold is word-level, and a persisted key is one glued word, so
    ``source_team_key`` cannot migrate it: ``source_team_key("newcastleutd")``
    is ``"newcastleutd"``, because there is no separate ``utd`` token left to
    fold. Any file written before the fold therefore carries keys the current
    seam never produces, and re-deriving them at read time cannot recover the
    new spelling - the same asymmetry the Türkiye rename had, except the
    rename was a different word and this one is a different WORD BOUNDARY.

    This returns the current-key spelling for a text that ends in the folded
    token (``newcastleutd`` -> ``newcastleunited``) and the text unchanged for
    everything else. Compatibility only: the value is a lookup candidate
    beside the recomputed key, never written back into any state file, and the
    corpus says the fold it undoes merges no two real clubs (68 groups over
    the committed archives, 0 wrong: handoff/round5_form_h2h_2026-10-12/
    a_identity_checks.txt).

    Measured 2026-10-12 over every committed localdata artifact: the only
    stored seam keys a pre-fold writer could have left are ``nasarawautd``
    (clv_unmatched_2026-09-17) and ``ayrutd`` (clv_unmatched_2026-10-03),
    plus 14 phase5_shadow identity keys - see the enumeration in
    handoff/n1_persisted_keys.txt (sites, classes and the churn count) for the
    per-artifact read/write classification.
    """
    text = str(name or "")
    if len(text) > 3 and text[-3:].lower() == "utd" and text[-4:-3].isalnum():
        return text[:-3] + "united"
    return text


# Squad distinguishers, as marker CLASSES. Two names whose marker classes
# disagree never denote the same team: "Club Brugge KV" and "Club Brugge KV
# U23" are different sides of the same club playing in different
# competitions. Classes (not raw tokens) so "Arsenal W" == "Arsenal Women".
#
# Evidence observed 2026-10-10 (localdata/betexplorer_odds_cache_2026-10-10.json):
# the RAAL La Louvière vs Club Brugge KV odds-cache key held three price rows
# for Dender vs Club Brugge KV U23 (Challenger Pro League) — the width-9
# fuzzy key ("clubbrugg") collapsed the senior and U23 sides and the
# partial-match branch accepted the reserve page. Wrong-squad pricing must
# lose to unpriced.
SQUAD_MARKER_CLASSES: dict[str, str] = {}
for _tokens, _cls in (
    (("u17", "u18", "u19", "u20", "u21", "u22", "u23", "u25"), None),  # age grade: exact token
    # 2026-10-15 red-team: side-market annotations a relay appends to a team
    # name ("AZ Alkmaar (Bookings)"). The name is not the match side.
    # Only the unambiguous side-market words: a bare "card" or "special" can be
    # part of a real club name, and a false marker costs a price for no gain.
    (("bookings", "booking", "corners", "cards"), "non_match"),
    (("ii", "b", "res", "reserve", "reserves", "yth", "youth", "amateur", "amateurs"), "reserve"),
    (("w", "women", "womens", "woman", "ladies", "feminino", "feminina",
      "femenino", "femenina", "damer"), "women"),
):
    for _tok in _tokens:
        SQUAD_MARKER_CLASSES[_tok] = _cls or _tok


def squad_markers(name: object) -> frozenset[str]:
    """The squad-marker classes a team name carries (empty for a senior side)."""
    out: set[str] = set()
    for word in team_identity_words(name).split():
        cls = SQUAD_MARKER_CLASSES.get(word)
        if cls:
            out.add(cls)
    return frozenset(out)


def squad_marker_mismatch(a: object, b: object) -> bool:
    """True when the two names cannot be the same squad of the same club.

    One side carries a squad/age/women marker the other lacks. Deliberately
    one-directional in the VETO sense only: it never asserts two names ARE
    the same team, it just refuses to let a truncated fuzzy key treat a
    reserve/youth/women side as the senior side. A false veto costs one
    price; a false match prices one fixture with another team's odds.
    """
    ma, mb = squad_markers(a), squad_markers(b)
    return ma != mb


# ---------------------------------------------------------------------------
# Truncated archive spellings (2026-10-21 name audit, fix 1).
#
# The ``bettingclosed`` settled view writes team names cut at exactly
# ``TRUNCATION_WIDTH`` characters: 6,763 of its 28,908 names sit at 16 and
# almost none run longer, so "Hapoel Beer Shev", "Vikingur Reykjav" and
# "Enugu Rangers In" are the archive's spelling of "Hapoel Beer Sheva",
# "Vikingur Reykjavik" and "Enugu Rangers Int". The key function does not
# undo a cut, so a join on ``source_team_key`` misses those fixtures.
#
# The rule below is deterministic and corpus-derived, not fuzzy: a name of
# exactly TRUNCATION_WIDTH characters maps to a longer spelling only when
# (a) the longer spelling starts with it after identity folding, (b) it is
# the ONLY distinct longer spelling in the corpus that does, and (c) the
# squad markers agree, so "Sporting Cristal" never folds onto a reserve
# "Sporting Cristal II". Two different clubs cannot be collapsed by it
# without a second longer spelling of the same prefix, which the uniqueness
# test refuses.
# ---------------------------------------------------------------------------

TRUNCATION_WIDTH = 16


def truncation_key_map(names) -> dict[str, str]:
    """Map a truncated spelling's ``source_team_key`` to its full key.

    ``names`` is any iterable of raw team-name strings (the whole archive is
    fine). Returns only unambiguous, squad-consistent mappings; a name whose
    key already equals its full key is omitted.
    """
    distinct = {str(n) for n in names if n}
    long_by_fold: dict[str, set[str]] = {}
    for full in distinct:
        if len(full.strip()) > TRUNCATION_WIDTH:
            long_by_fold.setdefault(fold_identity_words(full), set()).add(full)
    out: dict[str, str] = {}
    for short in distinct:
        if len(short.strip()) != TRUNCATION_WIDTH:
            continue
        short_fold = fold_identity_words(short)
        if not short_fold:
            continue
        candidates: set[str] = set()
        for long_fold, spellings in long_by_fold.items():
            if long_fold.startswith(short_fold) and long_fold != short_fold:
                candidates.update(spellings)
        candidates = {c for c in candidates
                      if not squad_marker_mismatch(c, short)}
        full_keys = {source_team_key(c) for c in candidates}
        if len(full_keys) != 1:
            continue
        (full_key,) = full_keys
        short_key = source_team_key(short)
        if short_key != full_key:
            out[short_key] = full_key
    return out
