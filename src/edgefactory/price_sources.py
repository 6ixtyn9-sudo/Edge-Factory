"""Explicit price-source registry and health-aware source selection.

Why this module exists
----------------------
Before this module, ``scripts/picks_today.py`` hard-coded ``bzzoiro_odds`` as
the first (and therefore preferred) live odds bundle. That made Bzzoiro the
"primary" source for an accident of build order, not because it was the best
or the healthiest source on the day. When Bzzoiro returned nothing, the whole
price lane degraded even though other approved donors were healthy.

The registry below makes two things explicit that used to be implicit:

1. **Role.** Not every source that returns a number returns a *bookmaker
   price*. A named-book execution quote, an average-of-bookmakers aggregate,
   and a model fair price are three different kinds of evidence and must never
   be printed or counted as if they were the same thing.
2. **Independence family.** Price corroboration is only meaningful between
   *independent* families. Two API vendors republishing the same model number
   are one piece of evidence, not two.

Nothing here fetches anything, and nothing here relaxes a safety gate: the
registry only describes what each source *is* and lets the caller rank the
sources that are actually healthy for the requested date.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

#: A named bookmaker quote (or a feed that carries the book's identity).
#: Only this role may be described in operator output as a book execution price.
ROLE_NAMED_BOOKMAKER = "named_bookmaker"
#: An aggregate of several bookmakers with no single book identity.
ROLE_AVERAGE_PRICE_DONOR = "average_bookmaker_price_donor"
#: A model's fair/no-vig price. Never an executable market quote.
ROLE_FAIR_PRICE_DONOR = "model_fair_price_donor"
#: A prediction/tip source. Votes only, never a price.
ROLE_VOTE_DONOR = "prediction_vote_donor"

#: ``odds_kind`` values that travel with every price-board entry.
ODDS_KIND_BOOKMAKER = "bookmaker"
ODDS_KIND_PROVIDER_AVERAGE = "provider_average"
ODDS_KIND_FAIR = "fair"

_ROLE_ODDS_KIND = {
    ROLE_NAMED_BOOKMAKER: ODDS_KIND_BOOKMAKER,
    ROLE_AVERAGE_PRICE_DONOR: ODDS_KIND_PROVIDER_AVERAGE,
    ROLE_FAIR_PRICE_DONOR: ODDS_KIND_FAIR,
    ROLE_VOTE_DONOR: None,
}

_TRUTHY = {"1", "true", "yes", "on"}
_FALSEY = {"0", "false", "no", "off"}


def _flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    value = raw.strip().lower()
    if value in _TRUTHY:
        return True
    if value in _FALSEY:
        return False
    return default


# ---------------------------------------------------------------------------
# Operator configuration switches
# ---------------------------------------------------------------------------

def fair_price_donor_enabled() -> bool:
    """Bet Better (and any other fair-price donor) may supply a price."""
    return _flag("EDGE_FACTORY_ENABLE_FAIR_PRICE_DONOR", True)


def average_price_donor_enabled() -> bool:
    """Boggio (and any other average-book donor) may supply a price."""
    return _flag("EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR", True)


def require_named_book_corroboration() -> bool:
    """When on, only named-book families may corroborate a printed price.

    Default OFF: the operator has explicitly promoted non-bookmaker donors, so
    named-book corroboration stays *preferred* but is not *required*. Every
    printed leg still has to disclose its donor type - see ``donor_disclosure``.
    """
    return _flag("EDGE_FACTORY_REQUIRE_NAMED_BOOK_CORROBORATION", False)


def require_corroboration() -> bool:
    """When on, a printed leg needs a second independent family."""
    return _flag("EDGE_FACTORY_REQUIRE_PRICE_CORROBORATION", False)


def source_fallback_enabled() -> bool:
    """Whether the legacy source fallback is allowed into execution.

    The fallback is disabled by default. It is a separately registered audit
    source because the historical Forebet/miner path is not a named-book
    quote. Turning it on is an explicit operator decision and is printed in
    the active policy; it is never an implicit rescue when donor joins fail.
    """
    return _flag("EDGE_FACTORY_ALLOW_SOURCE_FALLBACK", False)


def fair_price_directly_stakeable() -> bool:
    """Separate, explicit switch: may a fair price be the *printed* price?

    This is deliberately its own setting. Enabling the fair-price donor makes
    its numbers visible and usable as evidence; making them stakeable is a
    second, conscious decision and must never happen as a side effect. The
    setting remains separate from donor enablement so policy can turn it off
    without changing capture or evidence. The production-safe default is OFF;
    an operator must explicitly set EDGE_FACTORY_FAIR_PRICE_STAKEABLE=1.
    """
    return _flag("EDGE_FACTORY_FAIR_PRICE_STAKEABLE", False)


def corroboration_policy() -> dict[str, Any]:
    """The active, printable price policy. No hidden defaults."""
    return {
        "average_price_donor_enabled": average_price_donor_enabled(),
        "fair_price_donor_enabled": fair_price_donor_enabled(),
        "fair_price_directly_stakeable": fair_price_directly_stakeable(),
        "require_corroboration": require_corroboration(),
        "require_named_book_corroboration": require_named_book_corroboration(),
        "source_fallback_enabled": source_fallback_enabled(),
        "min_independent_families": 2 if require_corroboration() else 1,
    }


def policy_line() -> str:
    """One deterministic line describing the active donor policy."""
    policy = corroboration_policy()
    bits = [
        "avg_donor=" + ("on" if policy["average_price_donor_enabled"] else "off"),
        "fair_donor=" + ("on" if policy["fair_price_donor_enabled"] else "off"),
        "fair_stakeable=" + ("on" if policy["fair_price_directly_stakeable"] else "off"),
        "corroboration=" + ("required" if policy["require_corroboration"] else "preferred"),
        "named_book_corroboration="
        + ("required" if policy["require_named_book_corroboration"] else "preferred"),
        "source_fallback=" + ("execution" if policy["source_fallback_enabled"] else "abstain"),
    ]
    return "PRICE POLICY: " + " ".join(bits)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PriceSourceSpec:
    """What one price source *is* - never what it happened to return."""

    name: str
    role: str
    priority: int
    enabled_by_default: bool = True
    execution_eligible: bool = True
    corroboration_eligible: bool = True
    independence_family: str = ""
    #: ``True`` only when the row identifies the actual bookmaker.
    named_bookmaker: bool = False
    #: Human label used in printed tickets and diagnostics.
    label: str = ""
    notes: str = ""
    #: Env switch that must be truthy for this source to donate a price.
    enable_flag: str | None = None

    @property
    def odds_kind(self) -> str | None:
        return _ROLE_ODDS_KIND.get(self.role)

    @property
    def family(self) -> str:
        return self.independence_family or self.name

    def enabled(self) -> bool:
        if self.enable_flag == "EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR":
            return average_price_donor_enabled()
        if self.enable_flag == "EDGE_FACTORY_ENABLE_FAIR_PRICE_DONOR":
            return fair_price_donor_enabled()
        if self.enable_flag:
            return _flag(self.enable_flag, self.enabled_by_default)
        return self.enabled_by_default

    def can_execute(self) -> bool:
        """May this source supply the price actually printed on a ticket?"""
        if not self.enabled() or not self.execution_eligible:
            return False
        if self.role == ROLE_FAIR_PRICE_DONOR and not fair_price_directly_stakeable():
            return False
        return True

    def can_corroborate(self) -> bool:
        if not self.enabled() or not self.corroboration_eligible:
            return False
        if require_named_book_corroboration() and not self.named_bookmaker:
            return False
        return True


_SPECS: tuple[PriceSourceSpec, ...] = (
    # --- named-book / bookmaker-backed price sources -----------------------
    PriceSourceSpec(
        name="bzzoiro_odds",
        role=ROLE_NAMED_BOOKMAKER,
        priority=10,
        independence_family="bzzoiro_book",
        named_bookmaker=True,
        label="Bzzoiro named-book price",
        notes="Historic default primary. Kept as one approved source among several.",
    ),
    PriceSourceSpec(
        name="betexplorer",
        role=ROLE_NAMED_BOOKMAKER,
        priority=20,
        independence_family="betexplorer_book",
        named_bookmaker=True,
        label="BetExplorer named-book price",
    ),
    PriceSourceSpec(
        name="betexplorer_odds",
        role=ROLE_NAMED_BOOKMAKER,
        priority=20,
        independence_family="betexplorer_book",
        named_bookmaker=True,
        label="BetExplorer named-book price",
        notes="Compatibility name used by the rescue adapter; same family as betexplorer.",
    ),
    PriceSourceSpec(
        name="theoddsapi",
        role=ROLE_NAMED_BOOKMAKER,
        priority=20,
        independence_family="theoddsapi_bookmaker",
        named_bookmaker=True,
        label="TheOddsAPI named-book price",
        notes="Family is per-book: theoddsapi_bookmaker:<book>.",
    ),
    PriceSourceSpec(
        name="oddspapi_odds",
        role=ROLE_NAMED_BOOKMAKER,
        priority=25,
        independence_family="oddspapi_bookmaker",
        named_bookmaker=True,
        label="OddsPAPI named-book price",
    ),
    PriceSourceSpec(
        name="pinnapi_odds",
        role=ROLE_NAMED_BOOKMAKER,
        priority=15,
        independence_family="pinnacle_book",
        named_bookmaker=True,
        label="Pinnacle named-book price",
    ),
    PriceSourceSpec(
        name="sharpapi_odds",
        role=ROLE_NAMED_BOOKMAKER,
        priority=18,
        independence_family="sharpapi_book",
        named_bookmaker=True,
        label="SharpAPI named-book price",
    ),
    PriceSourceSpec(
        name="sportytrader_odds",
        role=ROLE_NAMED_BOOKMAKER,
        priority=60,
        enabled_by_default=False,
        execution_eligible=False,
        independence_family="sportytrader_book",
        named_bookmaker=True,
        label="SportyTrader named-book price (corroborator only)",
        enable_flag="SPORTYTRADER_CORROBORATOR",
    ),
    # --- average-bookmaker donor ------------------------------------------
    PriceSourceSpec(
        name="boggio",
        role=ROLE_AVERAGE_PRICE_DONOR,
        priority=40,
        independence_family="boggio_average",
        named_bookmaker=False,
        label="Boggio average-bookmaker price donor",
        notes=(
            "Operator-promoted 2026-10-03 from voice-shadow to approved average "
            "price donor. The odds object is an average across books: it is NOT "
            "a named bookmaker and never counts as a named-book family."
        ),
        enable_flag="EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR",
    ),
    # --- model / fair price donor -----------------------------------------
    PriceSourceSpec(
        name="betbetter",
        role=ROLE_FAIR_PRICE_DONOR,
        priority=50,
        independence_family="betbetter_fair",
        named_bookmaker=False,
        label="Bet Better fair-price donor",
        notes=(
            "Operator-promoted 2026-10-03 from benchmark-only to approved "
            "fair-price donor. These are model fair odds, not executable "
            "bookmaker quotes."
        ),
        enable_flag="EDGE_FACTORY_ENABLE_FAIR_PRICE_DONOR",
    ),
    # --- conditional / provider-price donor -------------------------------
    PriceSourceSpec(
        name="betminer",
        role=ROLE_AVERAGE_PRICE_DONOR,
        priority=55,
        execution_eligible=False,
        independence_family="betminer_provider",
        named_bookmaker=False,
        label="BetMiner provider-price donor",
        notes=(
            "Price donor ONLY when the response supplies a normalized quote "
            "whose provenance is identified; otherwise votes only."
        ),
        enable_flag="EDGE_FACTORY_ENABLE_AVERAGE_PRICE_DONOR",
    ),
    # --- audit-only price feeds -------------------------------------------
    PriceSourceSpec(
        name="scoutingstats_odds",
        role=ROLE_AVERAGE_PRICE_DONOR,
        priority=80,
        execution_eligible=False,
        corroboration_eligible=False,
        independence_family="scoutingstats_average",
        named_bookmaker=False,
        label="ScoutingStats audit-only price",
        notes="Retained for audit; quarantined from push eligibility (sole-source incident 2026-09-25).",
    ),
    # Historical Forebet/miner fallback. It is registered so its provenance
    # cannot silently become an execution quote, but disabled unless the
    # operator explicitly opts in. The default production decision is abstain:
    # Forebet is historical-only and carries no named-book provenance.
    PriceSourceSpec(
        name="forebet_best",
        role=ROLE_AVERAGE_PRICE_DONOR,
        priority=90,
        enabled_by_default=False,
        execution_eligible=True,
        corroboration_eligible=False,
        independence_family="forebet_fallback",
        named_bookmaker=False,
        label="Forebet/miner fallback price",
        notes="Historical-only fallback; not a named bookmaker and off by default.",
        enable_flag="EDGE_FACTORY_ALLOW_SOURCE_FALLBACK",
    ),
)

REGISTRY: dict[str, PriceSourceSpec] = {spec.name: spec for spec in _SPECS}

#: Sources that only ever donate votes, never prices.
VOTE_ONLY_SOURCES: frozenset[str] = frozenset({
    "bzzoiro", "zulubet", "statarea", "vitibet", "betclan", "bettingclosed",
    "prosoccer", "predictz", "windrawwin", "freesupertips", "afootballreport",
    "soccervista", "forebet", "futbolpronosticos", "predictiq",
})

_UNKNOWN = PriceSourceSpec(
    name="unknown",
    role=ROLE_VOTE_DONOR,
    priority=999,
    enabled_by_default=False,
    execution_eligible=False,
    corroboration_eligible=False,
    independence_family="unknown",
    named_bookmaker=False,
    label="unregistered source",
    notes="Fail-closed: an unregistered source is never a price donor.",
)


def spec(name: str | None) -> PriceSourceSpec:
    """Registry lookup. Unknown names fail closed as non-donors."""
    key = str(name or "").strip()
    found = REGISTRY.get(key)
    if found is not None:
        return found
    if key in VOTE_ONLY_SOURCES:
        return PriceSourceSpec(
            name=key, role=ROLE_VOTE_DONOR, priority=900,
            enabled_by_default=True, execution_eligible=False,
            corroboration_eligible=False, independence_family=f"{key}_vote",
            named_bookmaker=False, label=f"{key} vote donor",
        )
    return _UNKNOWN


def known(name: str | None) -> bool:
    return str(name or "").strip() in REGISTRY


def price_donor_names() -> tuple[str, ...]:
    """Every registered source that may contribute a price, by priority."""
    return tuple(
        s.name for s in sorted(_SPECS, key=lambda s: (s.priority, s.name))
        if s.role != ROLE_VOTE_DONOR
    )


def execution_donor_names() -> tuple[str, ...]:
    return tuple(
        s.name for s in sorted(_SPECS, key=lambda s: (s.priority, s.name))
        if s.can_execute()
    )


# ---------------------------------------------------------------------------
# Row / board-entry annotation
# ---------------------------------------------------------------------------

def independence_family(source: str | None, bookmaker: object = None) -> str:
    """The independence family a quote belongs to.

    TheOddsAPI and OddsPAPI aggregate many books: each distinct book is its own
    family, otherwise one aggregator could "corroborate" itself.
    """
    source_spec = spec(source)
    book = str(bookmaker or "").strip().lower()
    if source_spec.named_bookmaker and source_spec.name in {"theoddsapi", "oddspapi_odds"} and book:
        return f"{source_spec.independence_family}:{book}"
    return source_spec.family


def annotate_row(row: dict[str, Any], *, source: str | None = None) -> dict[str, Any]:
    """Stamp role/provenance fields onto a price row (returns a new dict).

    This never invents a price and never changes one. It only labels the price
    that is already there, so that downstream code cannot mistake a model fair
    price for a bookmaker quote.
    """
    out = dict(row)
    name = str(source or out.get("source") or out.get("provider") or "")
    source_spec = spec(name)
    out.setdefault("source", name)
    out["provider_role"] = source_spec.role
    if source_spec.odds_kind:
        out.setdefault("odds_kind", source_spec.odds_kind)
    out["named_bookmaker"] = bool(source_spec.named_bookmaker and out.get("bookmaker"))
    out["price_independence_family"] = independence_family(name, out.get("bookmaker"))
    # An adapter may already have withheld this row (future publication
    # stamp, missing quote, operator switch). Annotation must never upgrade
    # a withheld row back to eligible - it can only ever narrow.
    out["price_push_eligible"] = bool(
        source_spec.can_execute() and row.get("price_push_eligible", True) is not False)
    return out


def donor_disclosure(source: str | None, bookmaker: object = None) -> str:
    """The mandatory per-leg disclosure of what kind of price this is."""
    source_spec = spec(source)
    if source_spec.role == ROLE_NAMED_BOOKMAKER:
        book = str(bookmaker or "").strip()
        return f"{source_spec.label}" + (f" ({book})" if book else "")
    if source_spec.role == ROLE_AVERAGE_PRICE_DONOR:
        return f"{source_spec.label} — average across books, not a named-book execution quote"
    if source_spec.role == ROLE_FAIR_PRICE_DONOR:
        return f"{source_spec.label} — model fair price, not a named-book execution quote"
    return f"{source_spec.label} — not a price donor"


def role_summary() -> list[str]:
    """Deterministic ``name: role`` lines for diagnostics output."""
    return [
        f"{s.name}: {s.role}" + ("" if s.enabled() else " [disabled]")
        for s in sorted(_SPECS, key=lambda s: (s.priority, s.name))
    ]


# ---------------------------------------------------------------------------
# Health-aware selection
# ---------------------------------------------------------------------------

@dataclass
class SourceCandidate:
    """One source's observed state for the requested date."""

    name: str
    healthy: bool = False
    exact_match: bool = False
    rows: int = 0
    freshness_h: float | None = None
    bundle: Any = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def spec(self) -> PriceSourceSpec:
        return spec(self.name)


_HEALTHY_STATUSES = {"ok", "cache_only"}


def status_is_healthy(status: object, rows: int = 0) -> bool:
    """A source is healthy for the day when it actually produced usable rows."""
    text = str(status or "").strip().lower()
    if text in {"auth", "quota", "unavailable", "blocked", "error", "cooldown",
                "not_run", "disabled"}:
        return False
    if text in _HEALTHY_STATUSES:
        return rows > 0
    return rows > 0


def rank_candidates(
    candidates: Iterable[SourceCandidate],
    *,
    execution_only: bool = False,
) -> list[SourceCandidate]:
    """Rank price sources for the requested date.

    Order, most significant first:

    1. source health for the requested date;
    2. exact fixture and market match;
    3. freshness (smaller age wins; unknown age sorts last);
    4. execution eligibility;
    5. named-book provenance;
    6. configured source priority.

    Bzzoiro no longer wins by construction: a healthy source with a valid exact
    fixture match beats an unavailable source whatever its historic priority.
    """
    pool = [c for c in candidates if c.spec.enabled()]
    if execution_only:
        pool = [c for c in pool if c.spec.can_execute()]

    def key(candidate: SourceCandidate) -> tuple:
        source_spec = candidate.spec
        age = candidate.freshness_h
        return (
            0 if candidate.healthy else 1,
            0 if candidate.exact_match else 1,
            float(age) if isinstance(age, (int, float)) else float("inf"),
            0 if source_spec.can_execute() else 1,
            0 if source_spec.named_bookmaker else 1,
            source_spec.priority,
            source_spec.name,
        )

    return sorted(pool, key=key)


def select_execution_source(
    candidates: Iterable[SourceCandidate],
) -> SourceCandidate | None:
    """The healthiest execution-eligible source, or ``None`` to abstain."""
    ranked = rank_candidates(candidates, execution_only=True)
    for candidate in ranked:
        if candidate.healthy and candidate.exact_match:
            return candidate
    for candidate in ranked:
        if candidate.healthy:
            return candidate
    return None


def independent_families(entries: Sequence[dict[str, Any]]) -> set[str]:
    """Distinct independence families present in a set of board entries."""
    families: set[str] = set()
    for entry in entries:
        family = entry.get("price_independence_family")
        if not family:
            family = independence_family(entry.get("source"), entry.get("bookmaker"))
        if family and family != _UNKNOWN.independence_family:
            families.add(str(family))
    return families


def corroborators_are_sufficient(
    chosen_source: str | None,
    corroborator_entries: Sequence[dict[str, Any]],
) -> bool:
    """Does this set of corroborators satisfy the active policy?

    Two API vendors republishing the same model number share a family and
    therefore do not corroborate each other.
    """
    chosen_family = independence_family(chosen_source)
    families = {f for f in independent_families(corroborator_entries) if f != chosen_family}
    if require_named_book_corroboration():
        families = {
            f for f in families
            if any(
                s.named_bookmaker and (f == s.family or f.startswith(s.family + ":"))
                for s in _SPECS
            )
        }
    if not require_corroboration():
        return True
    return bool(families)
