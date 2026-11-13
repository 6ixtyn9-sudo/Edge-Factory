"""Explicit, append-only, pre-kickoff PAPER ticket withdrawals.

Original receipt bytes, quotes and predictions are never changed. A withdrawal
can release a still-unstarted paper reservation, not erase a historical loss.
No live lane or real-money order is read, cancelled or modified here.
"""

from __future__ import annotations

from datetime import timedelta

from .odds_normalization import parse_zoned_timestamp

POLICY = "operator_pre_kickoff_paper_replacement_v1"


def validate_declaration(row):
    if "supersession" not in row:
        return
    s = row["supersession"]
    if (not isinstance(s, dict) or set(s) != {"policy", "reason", "targets"}
            or s.get("policy") != POLICY
            or not isinstance(s.get("reason"), str) or not s["reason"].strip()
            or not isinstance(s.get("targets"), list) or not s["targets"]):
        raise ValueError("invalid paper supersession declaration")
    references = []
    for target in s["targets"]:
        if (not isinstance(target, dict) or set(target) != {"receipt_sha256", "acca_index"}
                or not isinstance(target["receipt_sha256"], str) or len(target["receipt_sha256"]) != 64
                or any(v not in "0123456789abcdef" for v in target["receipt_sha256"])
                or type(target["acca_index"]) is not int or target["acca_index"] < 1):
            raise ValueError("invalid paper supersession target")
        references.append((target["receipt_sha256"], target["acca_index"]))
    if references != sorted(set(references)):
        raise ValueError("duplicate or unordered paper supersession targets")
    captured, published = (parse_zoned_timestamp(row.get(k)) for k in ("captured_at", "persisted_at"))
    if captured is None or published is None or published < captured:
        raise ValueError("unproven paper supersession time")


def withdrawn_tickets(history, *, pending=None):
    """Resolve hash/local-index references in chain order, without mutating rows.

    ``pending`` is used only under the capture lock to budget an atomic
    replacement; the final persisted declaration is independently checked again.
    References are same-day in v1 so every daily card can resolve them itself.
    """
    known, withdrawn = {}, {}
    rows = list(history) + ([pending] if pending is not None else [])
    for row in rows:
        validate_declaration(row)
        if "supersession" in row:
            captured = parse_zoned_timestamp(row["captured_at"])
            published = parse_zoned_timestamp(row["persisted_at"])
            for target in row["supersession"]["targets"]:
                key = (target["receipt_sha256"], target["acca_index"])
                if key in withdrawn:
                    raise ValueError("paper ticket already superseded")
                old = known.get(key[0])
                if old is None or old["date"] != row["date"] or key[1] > len(old["accas"]):
                    raise ValueError("paper supersession references missing or non-prior same-day ticket")
                old_published = parse_zoned_timestamp(old.get("persisted_at"))
                if old_published is None or old_published >= captured:
                    raise ValueError("paper supersession is not later than the original publication")
                acca = old["accas"][key[1]-1]
                kickoffs = [parse_zoned_timestamp(c.get("kickoff_utc")) for c in acca["legs"]]
                if not kickoffs or any(k is None or published + timedelta(minutes=30) > k for k in kickoffs):
                    raise ValueError("paper supersession requires unstarted fixtures and original lead time")
                withdrawn[key] = {
                    "superseded_by": row.get("sha256", "pending"),
                    "superseded_at": row["persisted_at"], "reason": row["supersession"]["reason"],
                }
        if row.get("sha256"):
            known[row["sha256"]] = row
    return withdrawn
