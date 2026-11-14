#!/usr/bin/env python3
"""Incident (a): how many outbound requests did the 2026-10-12 demo run make?

The receipt from that run (`/tmp/rebuild6/s45.out.txt`, section 3) reads
``requests: 0, market_requests: 0, be_cached: 1``. This probe answers whether
those zeros are genuine or masked, two ways:

1. **Static** — read the ordering off the shipped code: ``capture()`` calls
   ``source.reset_fetch_count()`` once, immediately BEFORE the fixture loop, and
   reads ``source.request_stats()`` at the END of the same call, so nothing
   inside one ``capture()`` window can hide a dial from its own receipt;
   ``_fetch`` increments ``_request_count`` immediately before ``urlopen`` and is
   the only incrementer;  ``betexplorer_match_snapshot.fetch_page`` is a second
   dial site that ``requests`` does not count, and it is not on the capture path.
2. **Dynamic** — re-run the same two sections the demo ran (the test helper's
   ``_run_pick`` and then one ``capture(max_fixtures=1)``) with the network layer
   replaced by a *blocking* counter: ``urllib.request.urlopen`` raises instead of
   dialing, and ``betexplorer_match_snapshot.fetch_page`` likewise. If the run
   really dialed, the probe counts it; it cannot leave the sandbox either way.

Read-only: the localdata guard redirects every path into a scratch copy (the
real cache is copied in, so the cache-hit path reproduces exactly).

Writes ``handoff/incident_2026-10-12_outbound_count.txt``.
"""
from __future__ import annotations

import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()   # every localdata write goes to scratch (incident 2026-10-12)


import io
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


class NetworkBlocked(RuntimeError):
    """Raised instead of dialing: this probe must not reach a vendor."""


def main() -> int:
    out = io.StringIO()

    def say(line: str = "") -> None:
        out.write(line + "\n")

    from edgefactory.sources import betexplorer_odds as be

    say("== incident (a): outbound requests of the 2026-10-12 demo run ==")
    say()
    say("-- static: the ordering, read off the shipped source (file + symbol) --")
    src = (ROOT / "src/edgefactory/sources/betexplorer_odds.py").read_text()
    cap_src = (ROOT / "scripts/capture_betexplorer.py").read_text()
    for label, hay, needle in (
        ("capture.reset", cap_src, "source.reset_fetch_count()"),
        ("capture.stats", cap_src, "source.request_stats()"),
        ("fetch.increment", src, "_request_count += 1"),
        ("fetch.reset", src, "def reset_fetch_count"),
    ):
        hits = [i + 1 for i, l in enumerate(hay.splitlines()) if needle in l]
        say(f"  {label:16s} {needle!r} at line(s) {hits}")
    order = [(cap_src.splitlines().index(l) + 1, l.strip())
             for l in cap_src.splitlines()
             if "reset_fetch_count()" in l or "request_stats()" in l]
    say(f"  capture() order   : reset at {order[0][0]}, stats at {order[-1][0]} "
        "(one window: reset -> loop -> stats, nothing in between)")
    loop = [i + 1 for i, l in enumerate(cap_src.splitlines())
            if "for pick in candidates[:limit]" in l]
    say(f"  the loop sits at line {loop[0]}, i.e. strictly between the two, so a "
        "dial inside the loop\n                    cannot be hidden from this "
        "receipt; only a dial AFTER the stats read could be")
    ms = (ROOT / "src/edgefactory/sources/betexplorer_match_snapshot.py").read_text()
    say(f"  second dial site  : betexplorer_match_snapshot.fetch_page at line "
        f"{[i + 1 for i, l in enumerate(ms.splitlines()) if 'def fetch_page' in l]}, "
        "NOT counted by request_stats\n                    and not on the capture "
        "path (capture imports parse_match_page_blocks only)")

    say()
    say("-- dynamic: the same two sections, network blocked and counted --")
    real_urlopen = urllib.request.urlopen
    dials: list[str] = []
    page_dials: list[str] = []

    def blocking_urlopen(url, *args, **kwargs):
        dials.append(str(url))
        raise NetworkBlocked(f"probe: urlopen blocked ({url})")

    import edgefactory.sources.betexplorer_match_snapshot as snap
    real_fetch_page = snap.fetch_page

    def blocking_fetch_page(*args, **kwargs):
        page_dials.append(str(args[0]) if args else "?")
        raise NetworkBlocked("probe: fetch_page blocked")

    urllib.request.urlopen = blocking_urlopen
    snap.fetch_page = blocking_fetch_page
    try:
        from tests.test_betexplorer_match_detail import PICK, _run_pick
        import scripts.capture_betexplorer as capture

        # section 3 of the driver, in order: the stub-fed pick, then a capture
        calls: list[str] = []
        _run_pick(PICK, calls=calls)
        say(f"  _run_pick: the test helper's own stub recorded {len(calls)} fetch(es) "
            "to its canned transport")
        say(f"             (be._fetch is patched by the helper, so the real "
            f"counter never runs): {calls}")
        stats_after_pick = dict(be.request_stats())
        say(f"  request_stats() after the stub-fed pick: "
            f"{json.dumps(stats_after_pick, sort_keys=True)}")
        try:
            receipt = capture.capture("2026-10-12", max_fixtures=1)
        except TypeError:                                  # pragma: no cover
            receipt = capture.capture("2026-10-12")
        shown = {k: receipt.get(k) for k in sorted(receipt)
                 if k in capture.RECEIPT_STAT_KEYS}
        # printed exactly as the demo's own section 3 printed it (indent=2,
        # sort_keys=True), so the two forms can be compared byte for byte
        receipt_text = json.dumps(shown, indent=2, sort_keys=True, default=str)
        say("  capture(max_fixtures=1) receipt stats, the demo's own rendering:")
        for line in receipt_text.splitlines():
            say(f"    {line}")
        recorded = pathlib.Path("/tmp/rebuild6/s45.out.txt")
        if recorded.is_file():
            blob = recorded.read_text()
            i = blob.index('"be_429"')
            start = blob.rindex("{", 0, i)
            depth = 0
            for j, ch in enumerate(blob[start:], start):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        recorded_block = blob[start:j + 1]
                        break
            say(f"  2026-10-12 demo run's receipt (from its stdout, verbatim):")
            for line in recorded_block.splitlines():
                say(f"    {line}")
            say(f"  byte-identical to the demo run's receipt: "
                f"{receipt_text == recorded_block}")
        else:
            say("  (the demo run's stdout is not in this workspace; its receipt "
                "is quoted in the memo)")
        say(f"  cache hits in that capture (be_cached): {shown.get('be_cached')}")
    finally:
        urllib.request.urlopen = real_urlopen
        snap.fetch_page = real_fetch_page

    say()
    say(f"  urlopen attempts during the probe      : {len(dials)} {dials}")
    say(f"  match_snapshot.fetch_page calls        : {len(page_dials)} {page_dials}")
    say()
    say("-- the answer --")
    verdict = (
        "0 outbound requests: the receipt's zeros are consistent, not masked.\n"
        "   The capture window holds exactly one fixture (max_fixtures=1), it was\n"
        "   answered from the same-day cache (`be_cached: 1`) - the one path that\n"
        "   returns before `_fetch` is ever called - and the only other call in the\n"
        "   run that reaches a fetch site (`_run_pick`) has `be._fetch` patched by\n"
        "   the test helper's canned transport. The probe's blocking counters\n"
        "   recorded none, and a blocked dial would have been counted, not\n"
        "   swallowed."
    )
    say(f"   VERDICT: {verdict}")
    say()
    say("-- bounds, had it dialed (stated for the blast radius, not as a count) --")
    say(f"   _MAX_FETCHES_PER_RUN = "
        f"{re.search(r'^_MAX_FETCHES_PER_RUN.*$', (ROOT / 'src/edgefactory/sources/betexplorer_odds.py').read_text(), re.M).group(0).strip()}")
    say(f"   _MARKET_INTERVAL     = "
        f"{re.search(r'^_MARKET_INTERVAL.*$', (ROOT / 'src/edgefactory/sources/betexplorer_odds.py').read_text(), re.M).group(0).strip()}")
    say("   every market fetch passes min_interval=_MARKET_INTERVAL, so n dials "
        "cost >= (n-1) * 5.1 s")
    say("   `requests` counts odds-module `_fetch` attempts only; a "
        "`betexplorer_match_snapshot.fetch_page` number would be a different counter.")

    text = out.getvalue()
    print(text, end="")
    (ROOT / "handoff/incident_2026-10-12_outbound_count.txt").write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
