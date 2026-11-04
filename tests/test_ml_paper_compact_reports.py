"""Concise human views retain the complete opt-in audit and frozen evidence."""

from copy import deepcopy
from datetime import timedelta

from test_ml_paper import DAY, NOW
from test_ml_paper_daily_presentation import numbers, publication
from test_ml_paper_rolling import run, slate

import scripts.auto_tickets_grade as grade
from edgefactory import ml_paper as mp


def test_three_tickets_and_many_empty_scans_are_not_an_audit_dump():
    rows = [publication(i) for i in range(3)] + [publication(i, count=0) for i in range(3, 103)]
    for row in rows:
        row['sha256'] = 'a' * 64
    original = deepcopy(rows)
    text = mp.render_daily_card(rows)
    assert numbers(text) == [1, 2, 3]
    assert '3 ticket publications · 100 scans without tickets' in text
    assert 'No additional tickets: 100 scan(s)' in text
    assert 'PUBLICATION REFERENCES' in text and 'PUBLICATION & LEG DETAILS' not in text
    for row in rows[:3]:
        assert row['decision_id'] in text
    for label in ('SHA256', 'Frozen at', 'Bank at decision', 'Rejections:', 'Learning:', 'quote age'):
        assert label not in text
    assert len(text.splitlines()) < 65
    audit = mp.render_daily_card(rows, audit=True)
    assert all(row['decision_id'] in audit for row in rows)
    assert audit.count('SHA256') == len(rows)
    assert 'Rejection counts are checks, not unique fixtures' in audit
    assert rows == original


def test_empty_scan_before_new_ticket_does_not_look_like_the_latest_scan():
    rows = [publication(count=0), publication(1)]
    text = mp.render_daily_card(rows)
    assert 'Scans without tickets: 1 scan(s)' in text
    assert 'No additional tickets:' not in text
    assert 'NO PAPER BET' not in text
    assert numbers(text) == [1] and 'reference P2/1' in text


def test_entirely_empty_day_has_one_notice_and_audit_pointer():
    rows = [publication(i, count=0) for i in range(12)]
    text = mp.render_daily_card(rows)
    assert text.count('NO PAPER BET') == 1
    assert '0 ticket publications · 12 scans without tickets' in text
    assert f'{mp.RECEIPT_DIR.as_posix()}/reports/{mp.PREFIX}_{DAY}_audit.txt' in text
    assert numbers(text) == []


def test_adjacent_grader_displays_held_daily_tickets_not_latest_empty_card(tmp_path, monkeypatch, capsys):
    first = run(tmp_path)
    empty = run(tmp_path, NOW + timedelta(minutes=1), slate(NOW, ids=(3,)))
    assert first['accas'] and not empty['accas']
    originals = {p: p.read_bytes() for p in mp.receipt_files(tmp_path)}
    monkeypatch.setattr(grade, 'LOCALDATA', tmp_path)
    monkeypatch.setattr(grade.at, 'load_settled_scores', dict)
    monkeypatch.setattr(grade.at, 'ml_paper_score_lookup', lambda _: lambda leg: None)
    report = grade.publish_ml_paper()
    text = capsys.readouterr().out
    assert numbers(text) == [1]
    assert 'NO PAPER BET' not in text
    assert 'No additional tickets: 1 scan(s)' in text
    assert f"CURRENT PAPER BANK (all dates): {report['paper_bank_units']:.3f}" in text
    assert text.count('autobets_ML TICKETS') == 1
    assert all(p.read_bytes() == blob for p, blob in originals.items())
    audit = tmp_path / mp.RECEIPT_DIR / 'reports' / f'{mp.PREFIX}_{DAY}_audit.txt'
    assert empty['decision_id'] in audit.read_text()


def test_latest_renderer_remains_read_only_and_keeps_draft_contract(tmp_path, monkeypatch):
    draft = publication()
    draft.pop('freeze_basis')
    before = set(tmp_path.iterdir())
    monkeypatch.setattr(mp, 'latest_card', lambda _: draft)
    assert mp.render_latest_card(tmp_path) == mp.render_card(draft)
    assert set(tmp_path.iterdir()) == before
    monkeypatch.setattr(mp, 'latest_card', lambda _: None)
    assert mp.render_latest_card(tmp_path) == ''
    assert set(tmp_path.iterdir()) == before
