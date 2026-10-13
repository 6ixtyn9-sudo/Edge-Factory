"""Match-under price floors (base-rate derived, 2026-10-13).

The floors are the 1/Wilson-LB + margin of the realised 2026 base rate, not
registry evidence: the registry has no under records because unders never
fired. These tests pin the table and the clear/no-clear behaviour, so a future
edit cannot quietly drop the floor and let unders fire again.
"""
import edgefactory.enh_registry as reg


def test_match_under_floors_are_the_base_rate_numbers():
    assert reg.floor_for("match_under_15") == 4.45
    assert reg.floor_for("match_under_25") == 2.38
    assert reg.floor_for("match_under_35") == 1.64


def test_match_under_25_clears_only_at_or_above_its_floor():
    assert reg.clears_floor("match_under_25", 2.30) is False
    assert reg.clears_floor("match_under_25", 2.38) is True
    assert reg.clears_floor("match_under_25", 2.50) is True


def test_match_under_35_clears_at_its_floor():
    assert reg.clears_floor("match_under_35", 1.60) is False
    assert reg.clears_floor("match_under_35", 1.64) is True


def test_team_unders_have_no_static_floor_their_floors_are_evidence_derived():
    # The operator's static table has no team entries: team-under floors come
    # from the side-keyed pick evidence (enh_team_floors), never from here.
    assert reg.floor_for("home_under_35") is None
    assert reg.floor_for("away_under_35") is None
    assert reg.clears_floor("away_under_35", 1.90) is False


def test_under_floor_is_inherited_by_the_slice_lookup_when_no_evidence():
    floors = reg.derive_floors({}, "2026-10-14", parent_floors=reg.ENHANCEMENT_PRICE_FLOORS,
                               margin=reg.ENHANCEMENT_FLOOR_MARGIN)
    floor, basis = reg.floor_for_slice(floors, "match_under_25", "England: Championship")
    assert floor == 2.38
    assert basis == "inherited"


def test_under_floor_binds_when_the_derived_table_has_no_row(tmp_path):
    # Production path: derive_floors_for_day returns a table without a row for
    # the under markets, so the lookup must fall back to the operator's floor.
    table = reg.derive_floors_for_day(tmp_path, "2026-10-13")
    assert "match_under_25" not in table["floors"]
    assert reg.floor_for_slice(table, "match_under_25", None) == (2.38, "inherited")
    assert reg.floor_for_slice(table, "match_under_25", "England: Championship") == (2.38, "inherited")
