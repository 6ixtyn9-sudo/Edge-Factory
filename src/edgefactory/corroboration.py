"""Documentation-grade bookmaker independence mapping.

This helper is intentionally not called by live corroboration. Promotion
code must opt in explicitly after settled evidence; donor APIs are not
independent merely because their transport differs.
"""
from __future__ import annotations

def bookmaker_family(source: object, row: dict | None = None) -> str | None:
    name=str(source or '').strip().lower(); row=row or {}
    if name in {'pinnapi_odds','kdobrev_pinnacle','pinnacle'}: return 'pinnacle'
    if name in {'scoutingstats','scoutingstats_odds'}: return 'scoutingstats'
    if name in {'theoddsapi','theoddsapi_odds'}: return str(row.get('book') or row.get('bookmaker') or '').strip().lower() or None
    if name in {'sharpapi_odds','sportsgameodds'}: return str(row.get('book') or row.get('bookmaker') or '').strip().lower() or None
    return str(row.get('book') or row.get('bookmaker') or '').strip().lower() or None
