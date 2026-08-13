"""Supabase client for edges and edge_picks.
Uses service_role key only. Credentials loaded via load_dotenv().
"""

from supabase import create_client
from dotenv import load_dotenv
import os


def get_client():
    """Return authenticated Supabase client (service role)."""
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise ValueError("Supabase credentials not found in environment")
    return create_client(url, key)


def upsert_edges(client, edges_list):
    """Upsert list of edge dicts into the edges table."""
    if not edges_list:
        return
    resp = client.table("edges").upsert(edges_list, on_conflict="sport_id,source_id,name").execute()
    print(f"Upserted 'edges': {len(edges_list)} rows")
    return resp


def delete_picks_for_date(client, picked_for: str):
    """Delete existing edge_picks rows for a target date before authoritative re-sync."""
    resp = (
        client.table("edge_picks")
        .delete()
        .eq("picked_for", picked_for)
        .execute()
    )
    print(f"Deleted existing 'edge_picks' for {picked_for}")
    return resp


def upsert_picks(client, picks_list):
    """Upsert unique pick rows into ``edge_picks``.

    Postgres cannot update the same constrained row twice in one UPSERT command
    (SQLSTATE 21000). Deduplicate at this final boundary as a fail-safe even
    though the sync builder also filters duplicate conflict keys.
    """
    if not picks_list:
        return

    unique_picks = []
    seen = set()
    conflict_columns = ("edge_id", "event_id", "market", "selection")
    for pick in picks_list:
        key = tuple(pick.get(column) for column in conflict_columns)
        if key in seen:
            continue
        seen.add(key)
        unique_picks.append(pick)

    duplicates = len(picks_list) - len(unique_picks)
    if duplicates:
        print(f"Skipped duplicate 'edge_picks' conflict rows: {duplicates}")
    resp = (
        client.table("edge_picks")
        .upsert(unique_picks, on_conflict=",".join(conflict_columns))
        .execute()
    )
    print(f"Upserted 'edge_picks': {len(unique_picks)} rows")
    return resp
