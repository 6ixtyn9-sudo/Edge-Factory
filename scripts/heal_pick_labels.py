#!/usr/bin/env python3
"""heal_pick_labels.py — self-heal: rewrite stale display_rule in all
archived pick ledgers from the exact rule string, then re-render the
operator .txt reports for healed dates.

Why: rows archived before the honest-label fix (7f573b48ab) can carry a
pre-qualifier display_rule (e.g. "2WAY-UNANIMOUS>=60" for the bc-confirms
variant). The merge layer retains rows exactly, so the stored data stays
stale forever unless scrubbed — and the .txt report is a static snapshot
that the pipeline only re-renders for the CURRENT day, so a past day's
.txt keeps the old labels unless re-rendered. daily.py now self-heals on
every write; this script does the one-time historical sweep + re-render.

Only touches the display field and the derived .txt report. Never rule,
odds, results, or performance. Idempotent: re-running heals 0 and
re-renders nothing.

Usage:
    python3 scripts/heal_pick_labels.py
    python3 scripts/heal_pick_labels.py --localdata /path/to/localdata
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from edgefactory.util import heal_ledger_labels, honest_display_label  # noqa: E402

GLOBS = ("picks_*.json", "picks_today.json", "picks_morning_*.json")
_DATE_RE = re.compile(r"^picks_(\d{4}-\d{2}-\d{2})\.json$")


def _txt_labels_match(txt_path: Path, data: list) -> bool:
    """True if the .txt report's labels match the JSON's honest labels.

    A .txt rendered by pre-fix code carries the stored (possibly stale)
    labels; the honest set is derived from the exact rule strings. Compare
    as sets so a single stale row triggers re-render.
    """
    if not txt_path.exists():
        return False
    txt_labels = set()
    for line in txt_path.read_text(errors="replace").splitlines():
        m = re.match(r"\s*\[([^\]]+)\]", line)
        if m:
            txt_labels.add(m.group(1).strip())
    honest = {honest_display_label(p) for p in data if isinstance(p, dict)}
    honest.discard("?")
    return txt_labels == honest


def _render_txt(localdata: Path, target_date: str, data: list) -> bool:
    """Re-render picks_{date}.txt from (healed) JSON — honest labels.

    Uses the same renderer the pipeline uses (daily.generate_daily_report),
    which derives labels from the exact rule string — never the stored one.
    """
    try:
        import daily  # scripts/ is on sys.path
        out = localdata / f"picks_{target_date}.txt"
        daily.generate_daily_report(target_date, output_path=out, source_picks=data)
        return True
    except Exception as exc:  # noqa: BLE001 - report must never kill the sweep
        print(f"  (txt re-render skipped for {target_date}: {exc})")
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Self-heal stale pick display labels + re-render .txt")
    ap.add_argument("--localdata", default=str(ROOT / "localdata"),
                    help="localdata dir (default: repo localdata)")
    args = ap.parse_args()

    ld = Path(args.localdata)
    files: list[Path] = []
    for g in GLOBS:
        files.extend(sorted(ld.glob(g)))
    files = sorted(set(files))
    if not files:
        print(f"no pick ledgers found in {ld}")
        return 1

    total_healed = 0
    changed_files = 0
    render_dates: dict[str, list] = {}  # target_date -> pick list
    for path in files:
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"skip {path.name}: {exc}")
            continue
        if not isinstance(data, list):
            continue
        healed = heal_ledger_labels(data)
        if healed:
            path.write_text(json.dumps(data, indent=2, sort_keys=True))
            print(f"{path.name}: healed {healed} row(s)")
            total_healed += healed
            changed_files += 1

        # map this file to a .txt report date (if any)
        m = _DATE_RE.match(path.name)
        if m:
            date = m.group(1)
        elif path.name == "picks_today.json" and data:
            date = str(data[0].get("date") or data[0].get("picked_for") or "")[:10]
            if len(date) != 10:
                date = None
        else:
            date = None
        if not date:
            continue
        txt_path = ld / f"picks_{date}.txt"
        # Re-render when the .txt is stale vs the honest label set — even if
        # the JSON was already healed by a previous run (the Mac's state).
        if healed or (txt_path.exists() and not _txt_labels_match(txt_path, data)):
            render_dates.setdefault(date, data)

    for d, data in sorted(render_dates.items()):
        ok = _render_txt(ld, d, data)
        print(f"{'re-rendered' if ok else 'FAILED to re-render'} picks_{d}.txt")

    print(f"\ndone: {total_healed} stale label(s) healed across {changed_files} file(s), "
          f"{len(render_dates)} .txt report(s) re-rendered")
    if total_healed == 0 and not render_dates:
        print("everything already truthful")
    return 0


if __name__ == "__main__":
    sys.exit(main())

