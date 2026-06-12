"""Mocked Supabase tests."""
import pytest
from unittest.mock import patch, MagicMock
from edgefactory.db import get_client, upsert_edges, upsert_picks

@patch("edgefactory.db.create_client")
def test_get_client(mock_create):
    mock_create.return_value = MagicMock()
    assert get_client() is not None

@patch("edgefactory.db.get_client")
def test_upsert_edges(mock_get):
    m = MagicMock()
    mock_get.return_value = m
    upsert_edges(m, [{"id":1}])
    m.table.assert_called()

@patch("edgefactory.db.get_client")
def test_upsert_picks(mock_get):
    m = MagicMock()
    mock_get.return_value = m
    upsert_picks(m, [{"id":1}])
    m.table.assert_called()
