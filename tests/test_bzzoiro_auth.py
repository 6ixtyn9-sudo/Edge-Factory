from __future__ import annotations

from datetime import date

import pytest

from edgefactory.sources import bzzoiro, bzzoiro_odds


def test_bzzoiro_missing_token_is_retryable_failure(monkeypatch):
    monkeypatch.setattr(bzzoiro, "TOKEN", None)

    with pytest.raises(RuntimeError, match="BZZOIRO_TOKEN missing"):
        bzzoiro.fetch_day(date.today().isoformat())


def test_bzzoiro_odds_missing_token_is_retryable_failure(monkeypatch):
    monkeypatch.setattr(bzzoiro_odds, "TOKEN", None)

    with pytest.raises(RuntimeError, match="BZZOIRO_TOKEN missing"):
        bzzoiro_odds.fetch_day(date.today().isoformat())
