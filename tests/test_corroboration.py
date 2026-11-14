from edgefactory.corroboration import bookmaker_family

def test_bookmaker_family_collapses_pinnacle_relays():
    assert bookmaker_family('pinnapi_odds', {'book':'Pinnacle'}) == 'pinnacle'
    assert bookmaker_family('kdobrev_pinnacle', {}) == 'pinnacle'

def test_bookmaker_family_uses_named_book_for_price_donors():
    assert bookmaker_family('sharpapi_odds', {'book':'DraftKings'}) == 'draftkings'
    assert bookmaker_family('theoddsapi_odds', {'bookmaker':'Bet365'}) == 'bet365'

def test_bookmaker_family_marks_scoutingstats_unnamed():
    assert bookmaker_family('scoutingstats', {'book':'Pinnacle'}) == 'scoutingstats'
