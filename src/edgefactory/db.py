"""
db.py — thin Supabase wrapper with bulk upserts and chunking.
All writes go through here so batching/retry policy lives in ONE place.
"""
import hashlib
import json
from functools import lru_cache

from supabase import Client, create_client

from .config import settings

CHUNK = 500  # PostgREST sweet spot for bulk upserts


@lru_cache(maxsize=1)
def client() -> Client:
    if not settings.supabase_url or not settings.supabase_key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env")
    return create_client(settings.supabase_url, settings.supabase_key)


def content_hash(*parts) -> str:
    return hashlib.md5(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()


def upsert(table: str, rows: list[dict], on_conflict: str) -> int:
    """Chunked idempotent upsert. Returns row count sent."""
    if not rows:
        return 0
    c = client()
    for i in range(0, len(rows), CHUNK):
        c.table(table).upsert(rows[i:i + CHUNK], on_conflict=on_conflict).execute()
    return len(rows)


def insert_ignore(table: str, rows: list[dict], on_conflict: str) -> int:
    """Insert, ignoring duplicates (append-only tables: predictions, odds)."""
    if not rows:
        return 0
    c = client()
    for i in range(0, len(rows), CHUNK):
        c.table(table).upsert(
            rows[i:i + CHUNK], on_conflict=on_conflict, ignore_duplicates=True
        ).execute()
    return len(rows)


def fetch_all(table: str, select: str = "*", page: int = 1000, **filters) -> list[dict]:
    """Paginated full-table read (PostgREST caps responses)."""
    c = client()
    out, start = [], 0
    while True:
        q = c.table(table).select(select).range(start, start + page - 1)
        for k, v in filters.items():
            q = q.eq(k, v)
        batch = q.execute().data
        out.extend(batch)
        if len(batch) < page:
            return out
        start += page
