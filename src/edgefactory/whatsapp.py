"""WhatsApp Business professional notification engine.

Supports three robust dispatch mechanisms:
1. Official Meta WhatsApp Cloud API (with auto Message Template fallback).
2. Twilio WhatsApp API.
3. CallMeBot API (Free personal operational alerts).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BUCKET_CLEAN = "CERTIFIED_CLEAN"
BUCKET_CAUTION = "CAUTION"
BUCKET_WL_ODDS = "WATCHLIST_NO_ODDS"
BUCKET_WL_CTX = "WATCHLIST_UNKNOWN_CTX"


def format_kickoff(pick: dict[str, Any]) -> str:
    for key in ("kickoff", "time", "start_time", "ko"):
        value = pick.get(key)
        if value not in (None, ""):
            return str(value)
    return "n/a"


def format_odds_display(pick: dict[str, Any]) -> str:
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
    lines: list[str] = []

    if is_late_slate_alert:
        lines.append(
            f"🚨 *Edge Factory Late-Slate Alert* 🚨\n📅 Date: {target_date}\n⚡ Mode: Intraday Discovery Scan\n"
        )
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
            enh_label = p.get("enhancement_label")
            enh_prob = p.get("enhancement_probability")
            
            lines.append(f"• *{match}* ➡️ *{selection}* {odds}")
            if enh_label and enh_prob:
                lines.append(f"   └ [KO: {ko}] | Rule: {rule} | Prob: {prob:.0f}%{w_str}")
                lines.append(f"   🔥 *Combo:* {enh_label} ({enh_prob:.1%})\n")
            else:
                lines.append(f"   └ [KO: {ko}] | Rule: {rule} | Prob: {prob:.0f}%{w_str}\n")

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
            enh_label = p.get("enhancement_label")
            enh_prob = p.get("enhancement_probability")
            
            lines.append(f"• *{match}* ➡️ *{selection}* {odds}")
            if enh_label and enh_prob:
                lines.append(f"   └ [KO: {ko}] | Rule: {rule} | Prob: {prob:.0f}%{w_str}")
                lines.append(f"   🔥 *Combo:* {enh_label} ({enh_prob:.1%})\n")
            else:
                lines.append(f"   └ [KO: {ko}] | Rule: {rule} | Prob: {prob:.0f}%{w_str}\n")

    skipped_count = sum(len(v) for k, v in buckets.items() if str(k).startswith("SKIPPED"))
    watchlist_count = sum(len(v) for k, v in buckets.items() if str(k).startswith("WATCHLIST"))
    if skipped_count or watchlist_count:
        meta_str = "ℹ️ Other items evaluated: "
        if watchlist_count:
            meta_str += f"{watchlist_count} on Watchlist (No matched odds / unknown context). "
        if skipped_count:
            meta_str += f"{skipped_count} Skipped (Veto/Dead edges)."
        lines.append(meta_str)

    lines.append("\n📲 Live read models synced to your custom Supabase app.")
    lines.append("⚠️ Flat stakes only. Bet only what you can afford to lose.")
    return "\n".join(lines)


def format_whatsapp_discovery_summary(target_date: str, picks: list[dict[str, Any]]) -> str:
    lines: list[str] = [
        f"🛰️ *Edge Factory Discovery Watchlist* 🛰️\n📅 Date: {target_date}\n⚠️ New same-day selections not present in the morning run\n"
    ]

    no_odds = [p for p in picks if p.get("bucket") == BUCKET_WL_ODDS]
    unknown_ctx = [p for p in picks if p.get("bucket") == BUCKET_WL_CTX]

    if no_odds:
        lines.append(f"🔎 *NO MATCHED ODDS* ({len(no_odds)})")
        for p in sorted(no_odds, key=lambda x: -float(x.get("avg_p") or 0)):
            lines.append(f"• *{p.get('match', '?')}* ➡️ *{str(p.get('pick', '?')).upper()}* @n/a")
            lines.append(
                f"   └ [KO: {format_kickoff(p)}] | Rule: {_pick_rule_label(p)} | Prob: {float(p.get('avg_p') or 0):.0f}%\n"
            )

    if unknown_ctx:
        lines.append(f"🧩 *UNKNOWN CONTEXT* ({len(unknown_ctx)})")
        for p in sorted(unknown_ctx, key=lambda x: -float(x.get("avg_p") or 0)):
            lines.append(f"• *{p.get('match', '?')}* ➡️ *{str(p.get('pick', '?')).upper()}* {format_odds_display(p)}")
            lines.append(
                f"   └ [KO: {format_kickoff(p)}] | Rule: {_pick_rule_label(p)} | Prob: {float(p.get('avg_p') or 0):.0f}%\n"
            )

    if not picks:
        lines.append("ℹ️ No new same-day discovery-watchlist selections were found.")
    else:
        lines.append("ℹ️ These are discovery alerts only. The pipeline has not attached a fully actionable bet state yet.")
    return "\n".join(lines)

def send_meta_whatsapp_cloud(
    token: str,
    phone_number_id: str,
    recipient: str,
    message_text: str,
    template_name: str | None = None,
) -> dict[str, Any]:
    clean_recipient = "".join(filter(str.isdigit, str(recipient)))
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
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
        is_template_required = (
            "131047" in err_body
            or "Message templates are required" in err_body
            or "outside of an active customer service window" in err_body
        )
        if not is_template_required or not template_name:
            raise RuntimeError(f"WhatsApp Cloud API exact error: {exc.code} - {err_body}") from exc
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
                        "parameters": [{"type": "text", "text": message_text[:1024]}],
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
    clean_recipient = "".join(filter(str.isdigit, str(recipient)))
    clean_from = "".join(filter(str.isdigit, str(from_number)))
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = urllib.parse.urlencode(
        {
            "From": f"whatsapp:+{clean_from}",
            "To": f"whatsapp:+{clean_recipient}",
            "Body": message_text,
        }
    ).encode("utf-8")
    import base64
    auth_str = base64.b64encode(f"{account_sid}:{auth_token}".encode("utf-8")).decode("utf-8")
    headers = {"Authorization": f"Basic {auth_str}", "Content-Type": "application/x-www-form-urlencoded"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_callmebot_whatsapp(
    apikey: str,
    phone: str,
    message_text: str,
) -> str:
    clean_phone = "".join(filter(str.isdigit, str(phone)))
    encoded_text = urllib.parse.quote(message_text)
    url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_text}&apikey={apikey}"
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode("utf-8", "replace")
