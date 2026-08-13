"""Mocked Supabase tests."""
from unittest.mock import patch, MagicMock
from edgefactory.db import get_client, upsert_edges, upsert_picks

@patch("os.getenv")
@patch("edgefactory.db.create_client")
def test_get_client(mock_create, mock_getenv):
    mock_getenv.side_effect = lambda k, d=None: "dummy" if "SUPABASE" in k else None
    mock_create.return_value = MagicMock()
    # Ensure it doesn't crash on missing environment
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


def test_upsert_picks_dedupes_postgres_conflict_key():
    client = MagicMock()
    duplicate = {
        "edge_id": "edge-1",
        "event_id": "event-1",
        "market": "1x2",
        "selection": "home",
        "odds": 1.12,
    }

    upsert_picks(client, [duplicate, dict(duplicate)])

    table = client.table.return_value
    submitted = table.upsert.call_args.args[0]
    assert submitted == [duplicate]
    assert table.upsert.call_args.kwargs["on_conflict"] == (
        "edge_id,event_id,market,selection"
    )
