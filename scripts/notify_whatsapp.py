#!/usr/bin/env python3
"""WhatsApp Business standalone dispatch agent for Edge Factory.

Reads the localdata/picks_today.json ledger, intelligently dedupes against
previously sent picks for the same date, and transmits mobile-optimized
Markdown summaries via official Meta Cloud, Twilio, or CallMeBot APIs.

Usage
-----
  python3 scripts/notify_whatsapp.py
  python3 scripts/notify_whatsapp.py --force
  python3 scripts/notify_whatsapp.py --date 2026-06-18
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.whatsapp import (  # noqa: E402
    BUCKET_CAUTION,
    BUCKET_CLEAN,
    format_whatsapp_summary,
    send_callmebot_whatsapp,
    send_meta_whatsapp_cloud,
    send_twilio_whatsapp,
)

# Attempt to autoload .env if present
try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

LOCALDATA = ROOT / "localdata"
DEFAULT_PICKS_FILE = LOCALDATA / "picks_today.json"


def _build_match_dedupe_key(pick: dict[str, Any], fallback_date: str) -> str:
    """Return an exact, deterministic key to guard against duplicate alerts."""
    match_date = str(pick.get("date") or pick.get("picked_for") or fallback_date)[:10]
    match_str = str(pick.get("match") or "").lower().strip()
    market = str(pick.get("market") or "1x2").lower()
    return f"{match_date}|{match_str}|{market}"


def _load_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        logging.warning(f"⚠️ Source picks file does not exist: {path}")
        return []
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, list):
            logging.warning(f"⚠️ Expected JSON list but found {type(data)} in {path}")
            return []
        return data
    except Exception as exc:
        logging.warning(f"⚠️ Exception reading JSON picks from {path}: {exc}")
        return []


def _load_sent_ledger(path: Path) -> set[str]:
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text())
        return set(data) if isinstance(data, list) else set()
    except Exception as exc:
        logging.warning(f"⚠️ Could not load sent ledger from {path}: {exc}")
        return set()


def _save_sent_ledger(path: Path, keys: set[str]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(sorted(keys), indent=2))
    except Exception as exc:
        logging.warning(f"⚠️ Could not save sent ledger to {path}: {exc}")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    ap = argparse.ArgumentParser(description="WhatsApp Business Dispatch Engine for Edge Factory.")
    ap.add_argument("--picks", default=str(DEFAULT_PICKS_FILE), help="Path to source picks JSON.")
    ap.add_argument("--date", default=None, help="Target date (YYYY-MM-DD). Defaults to today.")
    ap.add_argument("--force", action="store_true", help="Bypass sent ledger and transmit all items.")
    ap.add_argument("--late-slate-only", action="store_true", help="Strict intraday scan mode.")
    args = ap.parse_args()

    picks_file = Path(args.picks)
    target_date = args.date or date.today().isoformat()
    sent_ledger_file = LOCALDATA / f"whatsapp_sent_ledger_{target_date}.json"

    # 1. Verify active credentials
    meta_token = os.environ.get("WHATSAPP_TOKEN")
    meta_phone_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
    meta_recipient = os.environ.get("WHATSAPP_RECIPIENT")
    meta_template = os.environ.get("WHATSAPP_TEMPLATE_NAME") or "edgefactory_picks_alert"

    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_number = os.environ.get("TWILIO_WHATSAPP_NUMBER")

    callmebot_key = os.environ.get("CALLMEBOT_APIKEY")
    callmebot_phone = os.environ.get("CALLMEBOT_PHONE") or meta_recipient

    has_meta = bool(meta_token and meta_phone_id and meta_recipient)
    has_twilio = bool(twilio_sid and twilio_token and twilio_number and meta_recipient)
    has_callmebot = bool(callmebot_key and callmebot_phone)

    if not any((has_meta, has_twilio, has_callmebot)):
        logging.warning("⚠️ No active WhatsApp Business credentials detected. Skipping operational notification.")
        return 0

    # 2. Load picks and evaluate sent ledger
    raw_picks = _load_json_list(picks_file)
    logging.info(f"Loaded {len(raw_picks)} total operational picks from {picks_file}")

    # We only notify CERTIFIED_CLEAN and CAUTION
    notifiable_picks = [p for p in raw_picks if p.get("bucket") in (BUCKET_CLEAN, BUCKET_CAUTION)]

    sent_keys = set() if args.force else _load_sent_ledger(sent_ledger_file)
    is_first_run_of_day = not sent_ledger_file.exists()

    unsent_picks = []
    for pick in notifiable_picks:
        dkey = _build_match_dedupe_key(pick, target_date)
        if dkey not in sent_keys:
            unsent_picks.append(pick)

    # 3. Smart decision on notification transmission
    is_late_slate = args.late_slate_only or not is_first_run_of_day

    if not unsent_picks and not is_first_run_of_day and not args.force:
        logging.info("  [WhatsApp] All active strong/caution picks were already notified earlier today. Remaining silent.")
        return 0

    message_text = format_whatsapp_summary(
        target_date=target_date,
        picks=unsent_picks if is_late_slate else notifiable_picks,
        is_late_slate_alert=is_late_slate and bool(unsent_picks),
    )

    logging.info("\n>>> Dispatching operational WhatsApp Business notification...\n")
    print(message_text)
    print("\n" + "=" * 60)

    # 4. Transmit via active adapters
    dispatched = False

    if has_meta and meta_token and meta_phone_id and meta_recipient:
        logging.info(f"  └ Sending via Meta WhatsApp Cloud API to recipient ending in ...{meta_recipient[-4:]}")
        try:
            resp = send_meta_whatsapp_cloud(
                token=meta_token,
                phone_number_id=meta_phone_id,
                recipient=meta_recipient,
                message_text=message_text,
                template_name=meta_template,
            )
            logging.info(f"    └ Meta Success ID: {resp.get('messages', [{}])[0].get('id', 'OK')}")
            dispatched = True
        except Exception as exc:
            logging.error(f"    └ Meta Cloud API Dispatch Exception: {exc}")

    if has_twilio and twilio_sid and twilio_token and twilio_number and meta_recipient:
        logging.info(f"  └ Sending via Twilio WhatsApp API to recipient ending in ...{meta_recipient[-4:]}")
        try:
            resp = send_twilio_whatsapp(
                account_sid=twilio_sid,
                auth_token=twilio_token,
                from_number=twilio_number,
                recipient=meta_recipient,
                message_text=message_text,
            )
            logging.info(f"    └ Twilio Success SID: {resp.get('sid', 'OK')}")
            dispatched = True
        except Exception as exc:
            logging.error(f"    └ Twilio Dispatch Exception: {exc}")

    if has_callmebot and callmebot_key and callmebot_phone:
        logging.info(f"  └ Sending via CallMeBot API to phone ending in ...{callmebot_phone[-4:]}")
        try:
            resp_str = send_callmebot_whatsapp(
                apikey=callmebot_key,
                phone=callmebot_phone,
                message_text=message_text,
            )
            logging.info("    └ CallMeBot Dispatch Success")
            dispatched = True
        except Exception as exc:
            logging.error(f"    └ CallMeBot Dispatch Exception: {exc}")

    # 5. Persist sent ledger on success
    if dispatched or args.force:
        for p in (unsent_picks if is_late_slate else notifiable_picks):
            sent_keys.add(_build_match_dedupe_key(p, target_date))
        _save_sent_ledger(sent_ledger_file, sent_keys)
        logging.info(f"✅ Deduplication ledger updated: {len(sent_keys)} distinct items logged in {sent_ledger_file}")

    return 0 if dispatched else 1


if __name__ == "__main__":
    sys.exit(main())
