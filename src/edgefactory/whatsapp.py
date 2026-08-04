"""WhatsApp Business professional notification engine.

Supports three robust dispatch mechanisms:
1. Official Meta WhatsApp Cloud API (with auto Message Template fallback).
2. Twilio WhatsApp API.
3. CallMeBot API (Free personal operational alerts).
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BUCKET_CLEAN = "CERTIFIED_CLEAN"
BUCKET_CAUTION = "CAUTION"
BUCKET_WL_ODDS = "WATCHLIST_NO_ODDS"
BUCKET_WL_CTX = "WATCHLIST_UNKNOWN_CTX"
BUCKET_WL_UNCORROBORATED_PRICE = "WATCHLIST_UNCORROBORATED_PRICE"
BUCKET_WL_SUSPECT_PRICE = "WATCHLIST_SUSPECT_PRICE"


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
                lines.append(f"   {enhancement_marker(p)} *Combo:* {enh_label} ({enh_prob:.1%})\n")
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
                lines.append(f"   {enhancement_marker(p)} *Combo:* {enh_label} ({enh_prob:.1%})\n")
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


def callmebot_request_len(phone: str, apikey: str, message_text: str) -> int:
    """Addendum 25.1: total GET request length CallMeBot receives, including
    host/path/query overhead — the length the pipe actually sees. Returns a
    LENGTH ONLY: the URL embeds phone + apikey and must never be logged."""
    clean_phone = "".join(filter(str.isdigit, str(phone)))
    url = (
        f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}"
        f"&text={urllib.parse.quote(message_text)}&apikey={apikey}"
    )
    return len(url)


# --- Addendum 25.2: provider-ack honesty --------------------------------------
# 2026-08-04 incident: an Actions run wrote the shadow dedupe ledger although
# nothing reached the handset. HTTP-200 from CallMeBot is NOT delivery
# acceptance: the free API answers several failure modes (invalid key, expired
# activation, throttle) with a 200-class body. We therefore classify the
# response body and accept ONLY the observed success class. The raw body is
# never logged — it echoes the message text and could echo request parameters.

_CALLMEBOT_REJECT_HINTS = (
    "error", "invalid", "fail", "not queued", "activat", "throttl", "exceed", "denied",
)
# 25.2.1: STRUCTURAL acceptance. The success body echoes the outbound text
# ("Text to send: ..."), so a loose substring check confuses echo for ack —
# reproduced on the deployed 25.2 classifier: bodies echoing 'Success' /
# 'message queued', an 'unsuccessful' error, and a wrong-tag '<i>Message
# queued.</i>' were ALL falsely accepted. The real ack carries the phrase as
# markup: '<b>Message queued.</b>'. Our outbound text is WhatsApp markdown —
# it never contains that HTML tag. Legacy 'Success' fixture passes only when
# it IS the whole body. False-rejects fail closed (loud retry, no ledger);
# false-accepts write false ledgers. Closed is the safe side.
_CALLMEBOT_QUEUED_TAG = re.compile(r"<b>\s*message\s+queued\.?\s*</b>", re.IGNORECASE)


def _callmebot_normalize(body: str | None) -> str:
    """Strip HTML tags, collapse whitespace, lowercase. CallMeBot answers with
    small HTML fragments ('<p>...<b>Message queued.</b>...')."""
    if not body:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(body))
    return re.sub(r"\s+", " ", text).strip().lower()


def _callmebot_structurally_accepted(body: str) -> bool:
    """25.2.1: the sharp signal. Real ack: '<b>Message queued.</b>' markup.
    Legacy fixture: normalized body IS exactly 'success'. Nothing else."""
    if _CALLMEBOT_QUEUED_TAG.search(str(body)):
        return True
    return _callmebot_normalize(body) == "success"


def callmebot_body_category(body: str | None) -> str:
    """Sanitized ack category for logs — one of accepted / error-class /
    empty-body / unknown-class. Never the raw body."""
    norm = _callmebot_normalize(body)
    if not norm:
        return "empty-body"
    if any(h in norm for h in _CALLMEBOT_REJECT_HINTS):
        return "error-class"
    if _callmebot_structurally_accepted(body):
        return "accepted"
    return "unknown-class"


def callmebot_body_accepted(body: str | None) -> bool:
    """Addendum 25.2.1: accept only the observed success class — the
    structural '<b>Message queued.</b>' tag (2026-08-04 production ack) or a
    body that IS 'Success' — and never when an error hint is present anywhere
    (an 'ERROR: message not queued' style body must not sneak through)."""
    norm = _callmebot_normalize(body)
    if not norm:
        return False
    if any(h in norm for h in _CALLMEBOT_REJECT_HINTS):
        return False
    return _callmebot_structurally_accepted(body)


def send_callmebot_whatsapp(
    apikey: str,
    phone: str,
    message_text: str,
) -> str:
    clean_phone = "".join(filter(str.isdigit, str(phone)))
    encoded_text = urllib.parse.quote(message_text)
    url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_text}&apikey={apikey}"
    with urllib.request.urlopen(url) as resp:
        body = resp.read().decode("utf-8", "replace")
    if not callmebot_body_accepted(body):
        # 25.2: exception carries the sanitized category ONLY — never the URL
        # (embeds phone+key), never the raw body.
        raise RuntimeError(f"CallMeBot ack rejected: {callmebot_body_category(body)}")
    return body


# --- Addendum 24: shadow slate (every stream reaches the phone) --------------
BUCKET_VETO = "SKIPPED_VETO"
SHADOW_BUCKETS = (
    BUCKET_VETO,
    BUCKET_WL_ODDS,
    BUCKET_WL_UNCORROBORATED_PRICE,
    BUCKET_WL_SUSPECT_PRICE,
    BUCKET_WL_CTX,
)
SHADOW_MAX_LINES = 12
# Addendum 25.1: CallMeBot carries text as a URL parameter, so ENCODED TEXT
# length — not character count, not the full URL — is the budgeted unit here
# (the full request adds ~90 chars of host/path/phone/apikey on top; the
# dispatch log tracks both). Measured production cut (2026-08-04, received-
# prefix reconstruction): ~1,415 encoded text chars ≈ ~1,500 full-URL chars.
# Budget rule: encoded text <= ~0.78 x observed cut. The Addendum 25 estimate
# ("~2k") was wrong; HANDOVER records the correction and the method.
SHADOW_ENCODED_TEXT_BUDGET = 1100


def encoded_len(text: str) -> int:
    """URL-encoded length of text — the unit the CallMeBot pipe bills on."""
    return len(urllib.parse.quote(text))


def enhancement_marker(pick: dict[str, Any]) -> str:
    """Addendum 25.1: state-honest combo marker, SHARED by the main and shadow
    slate formatters (single helper, so the renderers cannot drift again).

    🔥 is reserved for the actionable case: the enhancement TYPE is registry-
    ELIGIBLE (price-history certified) AND the current fixture has a valid
    captured price. Everything else — SHADOW/PAPER/BENCHED types, types with no
    registry entry, or ELIGIBLE but currently unpriced — renders 🔬
    (research-grade), because an unpriced current fixture is not an actionable
    recommendation. Resolution happens upstream (notify injects _enh_status /
    _enh_priced onto the pick); absent fields degrade to 🔬, never to 🔥."""
    status = str(pick.get("_enh_status") or "")
    priced = bool(pick.get("_enh_priced"))
    return "🔥" if status == "ELIGIBLE" and priced else "🔬"


def format_stream_record(bucket: str, stats: dict[str, Any] | None) -> str:
    """One-line rolling 30d record for a stream label. Reads by_bucket from the
    rolling audit payload; degrades to an honest 'no record yet' when absent."""
    s = (stats or {}).get(bucket) or {}
    n = s.get("settled_picks")
    if not n:
        return "30d: no settled record yet"
    hr, roi = s.get("hit_rate"), s.get("roi")
    hr_txt = f"{float(hr) * 100:.0f}% hit" if hr is not None else "hit n/a"
    roi_txt = f"{float(roi) * 100:+.1f}% ROI" if roi is not None else "ROI n/a"
    return f"30d: {hr_txt} · {roi_txt} ({int(n)} settled)"


def _format_shadow_pick_line(p: dict[str, Any]) -> str:
    """Addendum 25: one logical line per pick. Same information the old two-line
    layout carried (odds · prob · KO · rule) plus the certified 🔥 combo token
    when the engine has one. The per-line 'Stream:' label is gone — section
    headers are restated on every chunk, so a line can never arrive stripped
    of its stream context."""
    line = (
        f"• *{p.get('match', '?')}* ➡️ *{str(p.get('pick', '?')).upper()}* "
        f"{format_odds_display(p)} · {float(p.get('avg_p') or 0):.0f}% · "
        f"KO {format_kickoff(p)} · {_pick_rule_label(p)}"
    )
    enh_label = p.get("enhancement_label")
    enh_prob = p.get("enhancement_probability")
    if enh_label:
        prob_txt = ""
        if enh_prob is not None:
            try:
                prob_txt = f" ({float(enh_prob):.0%})"
            except (TypeError, ValueError):
                prob_txt = ""
        line += f" · {enhancement_marker(p)} {enh_label}{prob_txt}"
    return line


def _shadow_blocks(
    target_date: str,
    picks: list[dict[str, Any]],
    stats: dict[str, Any] | None,
) -> tuple[list[str], list[tuple[str, list[str]]], list[str]]:
    """Structural form of the slate: (header lines, [(section title, pick lines)],
    footer lines). Single source of truth for both the flat formatter and the
    Addendum 25 chunker, so they can never drift apart."""
    picks = [p for p in picks if p.get("bucket") in SHADOW_BUCKETS]
    header = [
        "🌑 *Edge Factory Shadow Slate* 🌑",
        f"📅 Date: {target_date}",
        "⚠️ Shadow streams — NOT pushed as bets. Section labels = rolling 30d audit record.",
        "",
    ]
    section_defs = [
        ("🚫 *SKIPPED_VETO* (disagreement-vetoed)", BUCKET_VETO),
        ("🔎 *WATCHLIST_NO_ODDS* (no matched price)", BUCKET_WL_ODDS),
        ("🧪 *WATCHLIST_UNCORROBORATED_PRICE* (ScoutingStats-only price)",
         BUCKET_WL_UNCORROBORATED_PRICE),
        ("⚠️ *WATCHLIST_SUSPECT_PRICE* (fuzzy price match)",
         BUCKET_WL_SUSPECT_PRICE),
        ("🧩 *WATCHLIST_UNKNOWN_CTX* (unknown league context)", BUCKET_WL_CTX),
    ]
    sections: list[tuple[str, list[str]]] = []
    shown = 0
    for title, bucket in section_defs:
        if shown >= SHADOW_MAX_LINES:
            break
        rows = sorted(
            (p for p in picks if p.get("bucket") == bucket),
            key=lambda x: -float(x.get("avg_p") or 0),
        )
        if not rows:
            continue
        pick_lines: list[str] = []
        for p in rows:
            if shown >= SHADOW_MAX_LINES:
                break
            pick_lines.append(_format_shadow_pick_line(p))
            shown += 1
        if pick_lines:
            sections.append((f"{title} — _{format_stream_record(bucket, stats)}_", pick_lines))
    footer: list[str] = []
    if not picks:
        footer = ["ℹ️ Shadow slate empty — no vetoed or watchlist selections today."]
    else:
        if len(picks) > shown:
            footer.append(f"… +{len(picks) - shown} more on the slate file (localdata/picks_next_2days.json)")
        footer.append("ℹ️ Shown for transparency; graded per-stream in the rolling audit. Weight them yourself.")
    return header, sections, footer


def format_whatsapp_shadow_summary(
    target_date: str,
    picks: list[dict[str, Any]],
    stats: dict[str, Any] | None = None,
) -> str:
    """Second daily message (Addendum 24, slim-lined in Addendum 25): SKIPPED_VETO
    + WATCHLIST streams. These were not pushed as bets. Every section header
    carries the stream's rolling 30d audit record so the operator can weight
    streams themselves — calibration ≠ edge, and stream records differ (the
    reason this exists: the veto stream was the most profitable stream of the
    2026-08 window while receiving zero pushes)."""
    header, sections, footer = _shadow_blocks(target_date, picks, stats)
    lines: list[str] = list(header)
    for title, pick_lines in sections:
        lines.append(title)
        lines.extend(pick_lines)
        lines.append("")
    lines.extend(footer)
    return "\n".join(lines).rstrip("\n")


def _fit_line(line: str, prefix_lines: list[str], budget: int) -> str:
    """Addendum 25: hard-truncate a single line that cannot fit even in a fresh
    chunk. ALWAYS marked '(cut)' — content is never silently dropped."""
    if encoded_len("\n".join(prefix_lines + [line])) <= budget:
        return line
    keep = len(line)
    while keep > 0:
        cand = line[:keep].rstrip() + " …(cut)"
        if encoded_len("\n".join(prefix_lines + [cand])) <= budget:
            return cand
        keep -= 8
    return "…(cut)"


def chunk_whatsapp_shadow_summary(
    target_date: str,
    picks: list[dict[str, Any]],
    stats: dict[str, Any] | None = None,
    *,
    budget: int = SHADOW_ENCODED_TEXT_BUDGET,
) -> list[str]:
    """Addendum 25: split the shadow slate into pipe-safe messages.

    Invariants (battery-enforced, text-vs-behavior class):
    - every chunk's URL-encoded length <= budget (CallMeBot bills encoded chars)
    - atomic unit = one rendered line; slim picks are one line, so a split can
      never tear a pick apart (the 2026-08-04 truncation failure mode)
    - a section header is never orphaned at a chunk end; when a section spans
      chunks its header is restated as '(cont.)'
    - a single line that alone exceeds the budget is hard-truncated and MARKED
    - chunks carry '(k/n)' numbering so completeness is visible from the phone
    - when everything fits, the single chunk equals format_whatsapp_shadow_summary
    """
    header, sections, footer = _shadow_blocks(target_date, picks, stats)
    chunks: list[list[str]] = []
    cur: list[str] = list(header)

    # Numbering (" — 🌑 (k/n)") is applied AFTER packing, so the packer must
    # reserve encoded space for it — otherwise a chunk that fit when packed
    # sails over budget once numbered (caught by the monster-slate test).
    numbering_reserve = 48
    eff_budget = budget - numbering_reserve if budget > 2 * numbering_reserve else budget

    def fits(lines: list[str]) -> bool:
        return encoded_len("\n".join(lines)) <= eff_budget

    for title, pick_lines in sections:
        # Orphan guard: a section header must share its chunk with >= 1 pick line.
        if not fits(cur + [title, pick_lines[0]]):
            chunks.append(cur)
            cur = []
        cur.append(title)
        for ln in pick_lines:
            if not fits(cur + [ln]):
                chunks.append(cur)
                cur = [f"{title} (cont.)"]
                if not fits(cur + [ln]):
                    ln = _fit_line(ln, cur, eff_budget)
            cur.append(ln)
        cur.append("")

    for ln in footer:
        if not fits(cur + [ln]):
            chunks.append(cur)
            cur = []
        cur.append(ln)

    chunks.append(cur)
    n = len(chunks)
    out: list[str] = []
    for k, chunk_lines in enumerate(chunks, 1):
        chunk_lines = list(chunk_lines)
        if n > 1:
            if k == 1:
                chunk_lines[0] = f"{chunk_lines[0]} ({k}/{n})"
            else:
                chunk_lines[0] = f"{chunk_lines[0]} — 🌑 ({k}/{n})"
        out.append("\n".join(chunk_lines).rstrip("\n"))
    return out
