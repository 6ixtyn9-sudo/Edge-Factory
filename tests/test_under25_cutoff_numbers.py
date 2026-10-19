"""Arithmetic stress is not a policy change or a profitability backtest."""
import pytest
from scripts import audit_under25_cutoff as audit


def test_eighty_percent_at_one_point_four_is_twelve_percent_not_eighty_five_required():
    assert 1/1.4 == pytest.approx(.7142857142857143)
    # Independently sum payouts from 80 wins / 20 losses on 100 one-unit bets.
    assert (80 * .4 - 20)/100 == pytest.approx(.12)
    assert audit.expected_return(.8, 1.4) == pytest.approx(.12)
    assert audit.expected_return(.85, 1.4) == pytest.approx(.19)
    assert audit.legacy_thresholds()['match_under_25'] == .85


@pytest.mark.parametrize('p, haircut, expected', [
    (.80, 0, .12), (.80, .02, .0976), (.80, .05, .064),
    (.80, .10, .008), (.75, 0, .05), (.70, 0, -.02),
    (.75, .05, -.0025), (.70, .05, -.069), (.65, 0, -.09),
])
def test_joint_calibration_and_price_stress(p, haircut, expected):
    assert audit.expected_return(p, 1.4*(1-haircut)) == pytest.approx(expected)


def test_sample_size_changes_uncertainty_not_the_observed_rate():
    small = audit.sampling_case(80, 100, 1.4)
    large = audit.sampling_case(160, 200, 1.4)
    bigger = audit.sampling_case(320, 400, 1.4)
    assert small['observed_rate'] == large['observed_rate'] == bigger['observed_rate'] == .8
    assert small['wilson_two_sided_95pct'][0] == pytest.approx(.7111708344068411)
    assert small['roi_at_lower_endpoint'] < 0 < large['roi_at_lower_endpoint']
    assert large['roi_at_lower_endpoint_after_5pct_price_haircut'] < 0
    assert bigger['roi_at_lower_endpoint_after_5pct_price_haircut'] > 0


def test_eighty_five_is_not_a_universal_statistical_guarantee_at_the_minimum_odds():
    assert audit.expected_return(audit.wilson_lb(85, 100), 1.3) < 0
    assert audit.min_hits_for_lower_bound(100, 1.3) == 86
    assert audit.min_hits_for_lower_bound(100, 1.4) == 81


@pytest.mark.parametrize('p, price', [(float('nan'), 1.4), (.8, float('inf')),
                                     (True, 1.4), (.8, True), (1.1, 1.4), (-.1, 1.4), (.8, 1)])
def test_invalid_numbers_rejected(p, price):
    with pytest.raises(ValueError):
        audit.expected_return(p, price)


def test_snapshot_distribution_is_not_a_profitable_eighty_percent_fixture(tmp_path):
    import json
    data = tmp_path / 'localdata'
    data.mkdir()
    row = {'date': '2026-10-18', 'home': 'Alpha', 'away': 'Beta',
           'as_of': '2026-10-18T12:00:00Z', 'kickoff_utc': '2026-10-18T16:00:00Z',
           'event_notes': [{'market': 'match_over_25', 'cohort_rate': .70}]}
    (data / 'picks_2026-10-18.json').write_text(json.dumps([row]))
    got = audit.archived_under25(tmp_path)
    assert got['available_under25_rates'] == 1
    assert got['minimum_rate'] == pytest.approx(.30)
    assert got['at_least_80pct'] == got['at_least_85pct'] == 0
    assert got['newly_eligible_at_80_vs_85'] == 0
