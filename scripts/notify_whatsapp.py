#!/usr/bin/env python3
"""WhatsApp Business standalone dispatch agent for Edge Factory.

Reads an explicit picks ledger, dedupes against previously sent items, and
transmits mobile-optimized Markdown summaries via Meta Cloud, Twilio, or
CallMeBot APIs. Supports a separate same-day discovery-watchlist flow so late
watchlist discoveries do not block later real bet alerts.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.whatsapp import (  # noqa: E402
    BUCKET_CAUTION,
    BUCKET_CLEAN,
    BUCKET_WL_CTX,
    BUCKET_WL_ODDS,
    SHADOW_BUCKETS,
    format_whatsapp_discovery_summary,
    format_whatsapp_shadow_summary,
    format_whatsapp_summary,
    send_callmebot_whatsapp,
    send_meta_whatsapp_cloud,
    send_twilio_whatsapp,
)

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

LOCALDATA = ROOT / "localdata"
DEFAULT_PICKS_FILE = LOCALDATA / "picks_today.json"


def _default_target_date() -> str:
    tz_name = os.environ.get("EDGE_FACTORY_TZ") or os.environ.get("TZ") or "Africa/Johannesburg"
    try:
        return datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d")
    except Exception:
        return date.today().isoformat()


def _build_match_dedupe_key(pick: dict[str, Any], fallback_date: str) -> str:
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
        return [item for item in data if isinstance(item, dict)]
    except Exception as exc:
        logging.warning(f"⚠️ Exception reading JSON picks from {path}: {exc}")
        return []


HEARTBEAT_MARKER_PREFIX = "__heartbeat__|"
HEARTBEAT_TEXT = (
    "📭 Edge Factory — no certified picks today.\n"
    "System ran normally; the slate is simply empty. Tracking continues automatically."
)


def _filter_discoveries(candidates: list[dict[str, Any]], target_date: str,
                        discovery_sent_keys: set[str], sent_keys: set[str]) -> list[dict[str, Any]]:
    """Discovery-alert filter with main-ledger suppression (anti-spam backstop).

    A fixture already messaged via the normal pick path (main sent ledger) must
    never re-alert as a 'discovery', even if the separate discovery ledger was
    lost between runs (cache eviction / stale committed copy).
    """
    out = []
    for p in candidates:
        key = _build_match_dedupe_key(p, target_date)
        if key in discovery_sent_keys or key in sent_keys:
            continue
        out.append(p)
    return out


def _heartbeat_key(target_date: str) -> str:
    return f"{HEARTBEAT_MARKER_PREFIX}{target_date}"


def _heartbeat_pending(sent_keys: set[str], target_date: str) -> bool:
    return _heartbeat_key(target_date) not in sent_keys


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


def _load_rolling_bucket_stats() -> dict[str, Any] | None:
    """Rolling 30d per-stream records for shadow-slate labels (Addendum 24).
    Reads localdata/picks_audit_rolling.json (bot-persisted); absent/malformed
    degrades to None and labels render 'no settled record yet'."""
    try:
        payload = json.loads((LOCALDATA / "picks_audit_rolling.json").read_text())
        bb = payload.get("by_bucket")
        return bb if isinstance(bb, dict) else None
    except Exception:
        return None


def _morning_baseline_file(target_date: str) -> Path:
    return LOCALDATA / f"picks_morning_{target_date}.json"


def _dispatch_message(*, message_text: str, meta_token: str | None, meta_phone_id: str | None, meta_recipient: str | None, meta_template: str, twilio_sid: str | None, twilio_token: str | None, twilio_number: str | None, callmebot_key: str | None, callmebot_phone: str | None) -> bool:
    dispatched = False
    if meta_token and meta_phone_id and meta_recipient:
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
    if twilio_sid and twilio_token and twilio_number and meta_recipient:
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
    if callmebot_key and callmebot_phone:
        logging.info(f"  └ Sending via CallMeBot API to phone ending in ...{callmebot_phone[-4:]}")
        try:
            send_callmebot_whatsapp(apikey=callmebot_key, phone=callmebot_phone, message_text=message_text)
            logging.info("    └ CallMeBot Dispatch Success")
            dispatched = True
        except Exception as exc:
            logging.error(f"    └ CallMeBot Dispatch Exception: {exc}")
    return dispatched


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    ap = argparse.ArgumentParser(description="WhatsApp Business Dispatch Engine for Edge Factory.")
    ap.add_argument("--picks", default=str(DEFAULT_PICKS_FILE), help="Path to source picks JSON.")
    ap.add_argument("--date", default=None, help="Target date (YYYY-MM-DD). Defaults to today.")
    ap.add_argument("--force", action="store_true", help="Bypass sent ledgers and transmit all items.")
    ap.add_argument("--late-slate-only", action="store_true", help="Strict intraday scan mode.")
    ap.add_argument("--heartbeat", action="store_true",
                    help="Send one 'no certified picks today' ping when the slate is empty "
                         "(morning official pass only; deduped via the sent ledger).")
    args = ap.parse_args()

    picks_file = Path(args.picks)
    target_date = args.date or _default_target_date()
    sent_ledger_file = LOCALDATA / f"whatsapp_sent_ledger_{target_date}.json"
    discovery_sent_ledger_file = LOCALDATA / f"whatsapp_discovery_sent_ledger_{target_date}.json"

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

    raw_picks = _load_json_list(picks_file)
    logging.info(f"Loaded {len(raw_picks)} total operational picks from {picks_file}")

    notifiable_picks = [p for p in raw_picks if p.get("bucket") in (BUCKET_CLEAN, BUCKET_CAUTION)]
    sent_keys = set() if args.force else _load_sent_ledger(sent_ledger_file)
    is_first_run_of_day = not sent_ledger_file.exists()
    unsent_picks = [p for p in notifiable_picks if _build_match_dedupe_key(p, target_date) not in sent_keys]
    is_late_slate = args.late_slate_only or not is_first_run_of_day

    normal_message = None
    normal_message_picks: list[dict[str, Any]] = []
    normal_silent_logged = False
    if notifiable_picks:
        if unsent_picks or is_first_run_of_day or args.force:
            normal_message_picks = unsent_picks if is_late_slate else notifiable_picks
            if normal_message_picks:
                normal_message = format_whatsapp_summary(
                    target_date=target_date,
                    picks=normal_message_picks,
                    is_late_slate_alert=is_late_slate and bool(unsent_picks),
                )
        else:
            logging.info("  [WhatsApp] All active strong/caution picks were already notified earlier today. Remaining silent.")
            normal_silent_logged = True

    discovery_enabled = os.environ.get("EDGE_FACTORY_NOTIFY_DISCOVERY_WATCHLIST", "").strip().lower() in {"1", "true", "yes", "on"}
    discovery_message = None
    discovery_picks: list[dict[str, Any]] = []
    discovery_sent_keys = set() if args.force else _load_sent_ledger(discovery_sent_ledger_file)
    if discovery_enabled:
        baseline_rows = _load_json_list(_morning_baseline_file(target_date))
        baseline_keys = {_build_match_dedupe_key(p, target_date) for p in baseline_rows}
        candidate_discoveries = [
            p for p in raw_picks
            if str(p.get("date") or p.get("picked_for") or target_date)[:10] == target_date
            and _build_match_dedupe_key(p, target_date) not in baseline_keys
            and p.get("bucket") in (BUCKET_WL_ODDS, BUCKET_WL_CTX)
        ]
        discovery_picks = _filter_discoveries(candidate_discoveries, target_date, discovery_sent_keys, sent_keys)
        if discovery_picks:
            discovery_message = format_whatsapp_discovery_summary(target_date, discovery_picks)

    # Addendum 24: shadow slate — the streams the old doctrine kept off the
    # phone (SKIPPED_VETO + WATCHLIST). Default ON; kill with
    # EDGE_FACTORY_NOTIFY_SHADOW=0. Independent dedup ledger: main-slate sends
    # must never suppress shadow sends and vice versa.
    shadow_enabled = os.environ.get("EDGE_FACTORY_NOTIFY_SHADOW", "1").strip().lower() not in {"0", "false", "no", "off"}
    shadow_message = None
    shadow_picks: list[dict[str, Any]] = []
    shadow_sent_ledger_file = LOCALDATA / f"whatsapp_shadow_sent_ledger_{target_date}.json"
    shadow_sent_keys = set() if args.force else _load_sent_ledger(shadow_sent_ledger_file)
    if shadow_enabled:
        day_shadow = [
            p for p in raw_picks
            if str(p.get("date") or p.get("picked_for") or target_date)[:10] == target_date
            and p.get("bucket") in SHADOW_BUCKETS
        ]
        unsent_shadow = [p for p in day_shadow if _build_match_dedupe_key(p, target_date) not in shadow_sent_keys]
        candidate_shadow = day_shadow if args.force else unsent_shadow
        if candidate_shadow:
            shadow_picks = candidate_shadow
            shadow_message = format_whatsapp_shadow_summary(
                target_date, shadow_picks, stats=_load_rolling_bucket_stats()
            )

    heartbeat_message = None
    if (args.heartbeat
            and os.environ.get("EDGE_FACTORY_HEARTBEAT", "1").strip().lower() not in {"0", "false", "no", "off"}
            and not notifiable_picks
            and not discovery_message
            and not shadow_message
            and _heartbeat_pending(sent_keys, target_date)):
        # One quiet ping per empty day: distinguishes 'no picks' from 'system dead'
        # for hands-off tracking. Marked in the same dedup ledger, so max 1/day.
        heartbeat_message = f"Date: {target_date}\n{HEARTBEAT_TEXT}"

    if not normal_message and not discovery_message and not shadow_message and not heartbeat_message:
        if not normal_silent_logged:
            logging.info("  [WhatsApp] Nothing new to send. Staying silent.")
        return 0

    any_dispatched = False
    if normal_message:
        logging.info("\n>>> Dispatching operational WhatsApp notification...\n")
        print(normal_message)
        print("\n" + "=" * 60)
        dispatched = _dispatch_message(
            message_text=normal_message,
            meta_token=meta_token,
            meta_phone_id=meta_phone_id,
            meta_recipient=meta_recipient,
            meta_template=meta_template,
            twilio_sid=twilio_sid,
            twilio_token=twilio_token,
            twilio_number=twilio_number,
            callmebot_key=callmebot_key,
            callmebot_phone=callmebot_phone,
        )
        if dispatched or args.force:
            for p in normal_message_picks:
                sent_keys.add(_build_match_dedupe_key(p, target_date))
            _save_sent_ledger(sent_ledger_file, sent_keys)
            logging.info(f"✅ Bet-alert dedupe ledger updated: {len(sent_keys)} items in {sent_ledger_file}")
        any_dispatched = any_dispatched or dispatched

    if discovery_message:
        logging.info("\n>>> Dispatching discovery-watchlist WhatsApp notification...\n")
        print(discovery_message)
        print("\n" + "=" * 60)
        dispatched = _dispatch_message(
            message_text=discovery_message,
            meta_token=meta_token,
            meta_phone_id=meta_phone_id,
            meta_recipient=meta_recipient,
            meta_template=meta_template,
            twilio_sid=twilio_sid,
            twilio_token=twilio_token,
            twilio_number=twilio_number,
            callmebot_key=callmebot_key,
            callmebot_phone=callmebot_phone,
        )
        if dispatched or args.force:
            for p in discovery_picks:
                discovery_sent_keys.add(_build_match_dedupe_key(p, target_date))
            _save_sent_ledger(discovery_sent_ledger_file, discovery_sent_keys)
            logging.info(f"✅ Discovery-alert dedupe ledger updated: {len(discovery_sent_keys)} items in {discovery_sent_ledger_file}")
        any_dispatched = any_dispatched or dispatched

    if shadow_message:
        logging.info("\n>>> Dispatching shadow-slate WhatsApp notification...\n")
        print(shadow_message)
        print("\n" + "=" * 60)
        dispatched = _dispatch_message(
            message_text=shadow_message,
            meta_token=meta_token,
            meta_phone_id=meta_phone_id,
            meta_recipient=meta_recipient,
            meta_template=meta_template,
            twilio_sid=twilio_sid,
            twilio_token=twilio_token,
            twilio_number=twilio_number,
            callmebot_key=callmebot_key,
            callmebot_phone=callmebot_phone,
        )
        if dispatched or args.force:
            for p in shadow_picks:
                shadow_sent_keys.add(_build_match_dedupe_key(p, target_date))
            _save_sent_ledger(shadow_sent_ledger_file, shadow_sent_keys)
            logging.info(f"✅ Shadow-slate dedupe ledger updated: {len(shadow_sent_keys)} items in {shadow_sent_ledger_file}")
        any_dispatched = any_dispatched or dispatched

    if heartbeat_message:
        logging.info("\n>>> Dispatching empty-slate heartbeat...\\n")
        print(heartbeat_message)
        dispatched = _dispatch_message(
            message_text=heartbeat_message,
            meta_token=meta_token,
            meta_phone_id=meta_phone_id,
            meta_recipient=meta_recipient,
            meta_template=None,
            twilio_sid=twilio_sid,
            twilio_token=twilio_token,
            twilio_number=twilio_number,
            callmebot_key=callmebot_key,
            callmebot_phone=callmebot_phone,
        )
        if dispatched or args.force:
            sent_keys.add(_heartbeat_key(target_date))
            _save_sent_ledger(sent_ledger_file, sent_keys)
            logging.info("✅ Heartbeat marker persisted in sent ledger (max 1/day)")
        any_dispatched = any_dispatched or dispatched

    return 0 if any_dispatched or args.force else 1


if __name__ == "__main__":
    sys.exit(main())
