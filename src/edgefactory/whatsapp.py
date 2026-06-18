"""WhatsApp Business professional notification engine.

Supports three robust dispatch mechanisms:
1. Official Meta WhatsApp Cloud API (with auto Message Template fallback).
2. Twilio WhatsApp API.
3. CallMeBot API (Free personal operational alerts).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

# Specific operational bucket classifications
BUCKET_CLEAN = "CERTIFIED_CLEAN"
BUCKET_CAUTION = "CAUTION"


def format_kickoff(pick: dict[str, Any]) -> str:
    """Resolve human report kickoff display."""
    for key in ("kickoff", "time", "start_time", "ko"):
        value = pick.get(key)
        if value not in (None, ""):
            return str(value)
    return "n/a"


def format_odds_display(pick: dict[str, Any]) -> str:
    """Compact string representation of enriched odds and bookmaker."""
    odds_val = pick.get("odds")
    if odds_val is None:
        return "@n/a"
    try:
        odds_str = f"@{float(odds_val):.2f}"
    except (TypeError, ValueError):
        odds_str = f"@{odds_val}"

    source = pick.get("odds_source")
    if source == "bzzoiro_odds" and pick.get("bookmaker"):
        odds_str += f" ({pick['bookmaker']})"
    elif source == "zulubet":
        odds_str += " (zulubet)"
    return odds_str


def _pick_rule_label(pick: dict[str, Any]) -> str:
    return str(pick.get("display_rule") or pick.get("rule") or "?")


def format_whatsapp_summary(
    target_date: str,
    picks: list[dict[str, Any]],
    is_late_slate_alert: bool = False,
) -> str:
    """Construct an immaculate, mobile-optimized WhatsApp Business summary."""
    lines: list[str] = []

    if is_late_slate_alert:
        lines.append(f"🚨 *Edge Factory Late-Slate Alert* 🚨\n📅 Date: {target_date}\n⚡ Mode: Intraday Discovery Scan\n")
        lines.append(f"Discovered {len(picks)} newly posted active fixture{'s' if len(picks) > 1 else ''}:\n")
    else:
        lines.append(f"⚽ *Edge Factory Official Picks* ⚽\n📅 Date: {target_date}\n📊 Mode: Morning Slate Ledger\n")

    if not picks and not is_late_slate_alert:
        lines.append("ℹ️ *No matching certified edges found for this window.*")
        lines.append("Active scanners will naturally continue evaluating late-slate fixtures.")
        lines.append("\n📲 Pushed to Supabase / GitHub operational archives.")
        return "\n".join(lines)

    buckets: dict[str, list[dict[str, Any]]] = {}
    for p in picks:
        b = p.get("bucket", "UNKNOWN")
        buckets.setdefault(str(b), []).append(p)

    # 1. Clean Picks
    clean_picks = buckets.get(BUCKET_CLEAN, [])
    if clean_picks:
        lines.append(f"✅ *CERTIFIED CLEAN* ({len(clean_picks)} Strong Edges)")
        for p in sorted(clean_picks, key=lambda x: -float(x.get("avg_p") or 0)):
            match = str(p.get("match", "?"))
            selection = str(p.get("pick", "?")).upper()
            odds = format_odds_display(p)
            ko = format_kickoff(p)
            prob = float(p.get("avg_p") or 0)
            w_score = p.get("w_score")
            w_str = f", w={w_score:.2f}" if w_score is not None else ""
            rule = _pick_rule_label(p)

            lines.append(f"• *{match}* ➡️ *{selection}* {odds}")
            lines.append(f"   └ [KO: {ko}] | Rule: {rule} | Prob: {prob:.0f}%{w_str}\n")

    # 2. Caution Picks
    caution_picks = buckets.get(BUCKET_CAUTION, [])
    if caution_picks:
        lines.append(f"⚠️ *CAUTION* ({len(caution_picks)} Qualitative / Unrated Context Edges)")
        for p in sorted(caution_picks, key=lambda x: -float(x.get("avg_p") or 0)):
            match = str(p.get("match", "?"))
            selection = str(p.get("pick", "?")).upper()
            odds = format_odds_display(p)
            ko = format_kickoff(p)
            prob = float(p.get("avg_p") or 0)
            w_score = p.get("w_score")
            w_str = f", w={w_score:.2f}" if w_score is not None else ""
            rule = _pick_rule_label(p)

            lines.append(f"• *{match}* ➡️ *{selection}* {odds}")
            lines.append(f"   └ [KO: {ko}] | Rule: {rule} | Prob: {prob:.0f}%{w_str}\n")

    # Compact stats for skipped items
    skipped_count = sum(len(buckets[b]) for b in buckets if str(b).startswith("SKIPPED"))
    watchlist_count = sum(len(buckets[b]) for b in buckets if str(b).startswith("WATCHLIST"))
    if skipped_count or watchlist_count:
        meta_str = "ℹ️ Other items evaluated: "
        if watchlist_count:
            meta_str += f"{watchlist_count} on Watchlist (Missing/Unknown context). "
        if skipped_count:
            meta_str += f"{skipped_count} Skipped (Veto/Dead edges)."
        lines.append(meta_str)

    lines.append("\n📲 Live read models synced to your custom Supabase app.")
    lines.append("⚠️ Flat stakes only. Bet only what you can afford to lose.")
    return "\n".join(lines)


def send_meta_whatsapp_cloud(
    token: str,
    phone_number_id: str,
    recipient: str,
    message_text: str,
    template_name: str | None = None,
) -> dict[str, Any]:
    """Dispatch via official Meta WhatsApp Cloud API with template fallback.

    If free-form text fails due to Meta's active customer service window restrictions (#131047),
    instantly retries using the configured utility message template.
    """
    clean_recipient = "".join(filter(str.isdigit, str(recipient)))
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # First attempt: free-form text message
    payload_text = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": clean_recipient,
        "type": "text",
        "text": {"preview_url": False, "body": message_text},
    }

    req = urllib.request.Request(url, data=json.dumps(payload_text).encode("utf-8"), headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8")
        is_template_required = "131047" in err_body or "Message templates are required" in err_body or "outside of an active customer service window" in err_body

        if not is_template_required or not template_name:
            raise RuntimeError(f"WhatsApp Cloud API exact error: {exc.code} - {err_body}") from exc

        # Second attempt: beautiful template fallback
        # Folds our text payload into parameter {{1}} of the utility template
        payload_template = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_recipient,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": message_text[:1024]}  # Meta limits component vars to 1024 chars
                        ],
                    }
                ],
            },
        }

        req_tmpl = urllib.request.Request(url, data=json.dumps(payload_template).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req_tmpl) as resp_tmpl:
            return json.loads(resp_tmpl.read().decode("utf-8"))


def send_twilio_whatsapp(
    account_sid: str,
    auth_token: str,
    from_number: str,
    recipient: str,
    message_text: str,
) -> dict[str, Any]:
    """Dispatch via Twilio WhatsApp API. Never requires template windows."""
    clean_recipient = "".join(filter(str.isdigit, str(recipient)))
    clean_from = "".join(filter(str.isdigit, str(from_number)))

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    data = urllib.parse.urlencode({
        "From": f"whatsapp:+{clean_from}",
        "To": f"whatsapp:+{clean_recipient}",
        "Body": message_text,
    }).encode("utf-8")

    import base64
    auth_str = base64.b64encode(f"{account_sid}:{auth_token}".encode("utf-8")).decode("utf-8")
    headers = {
        "Authorization": f"Basic {auth_str}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_callmebot_whatsapp(
    apikey: str,
    phone: str,
    message_text: str,
) -> str:
    """Dispatch via CallMeBot API (Extremely popular for 100% free personal alerts)."""
    clean_phone = "".join(filter(str.isdigit, str(phone)))
    encoded_text = urllib.parse.quote(message_text)

    url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_text}&apikey={apikey}"

    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")
