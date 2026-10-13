#!/usr/bin/env python3
"""R3 — the capture's 429 handlers must record what they catch: three arms.

The change under proof is one call, ``_record_rate_limit(exc)``, added to the
two handlers in ``scripts/capture_oddspapi.py`` that read
``rate_limit_diagnostics()`` after catching an ``HTTPError`` (the fixtures
board, and the per-fixture odds call). In production the transport records
first, so the read finds the evidence already there; the call exists so that a
429 raised **directly at the seam** (a stub, a caller change, a future
refactor) cannot leave the receipt with no quota evidence — the 2026-10-10
failure mode, where a quota day read as a quiet slate.

The three arms the round requires:

1. **transport recording in place → BYTE-IDENTICAL receipt** with and without
   the added call (the production path cannot change);
2. **transport bypassed** (the 429 raised at the seam) → with the call the
   receipt carries the provider's headers; without it the receipt is empty,
   which is the incident reproduced;
3. **no path double-counts**: transport dials and every receipt counter are
   identical with and without the call in both arms; the recorder is
   idempotent (the same exception twice gives the same dict, a different one
   replaces rather than accumulates); and the per-fixture handler behaves
   exactly like the board handler.

Guarded: every localdata path is redirected to scratch by
``handoff/scratch_localdata.py``, and the receipts this driver inspects are
written to a temporary ``OUT_DIR``. Nothing here dials the network —
``urlopen`` is replaced by a counter that raises.

Writes ``handoff/r3_capture_429_proof.txt``.
"""
from __future__ import annotations

import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()

import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

HEADERS = {
    "Retry-After": "3600",
    "X-RateLimit-Remaining-Day": "0",
    "X-RateLimit-Limit-Day": "500",
    "X-RateLimit-Reset-Day": "2026-10-11T00:00:00Z",
}
FIXTURE = [{"fixtureId": "f1", "participant1Name": "Alpha", "participant2Name": "Beta"}]
#: A DIFFERENT 429 the run may hit first: the catalogue fetch
#: (``load_market_type_map`` dials ``/markets`` when its cache is absent). It
#: carries its own headers so a stale-evidence read is visible as a value.
CACHE_HEADERS = {"Retry-After": "60"}


class _FrozenDatetime:
    """A clock frozen so a receipt can be compared byte for byte."""

    @staticmethod
    def now(tz=None):  # noqa: ARG004 - mirrors datetime.now(tz)
        return datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)


def _http_429(headers: dict | None = None) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "https://api.oddspapi.io/v4/fixtures", 429, "Too Many Requests",
        hdrs=(headers or {}), fp=None)


def main() -> int:
    out = io.StringIO()

    def say(line: str = "") -> None:
        out.write(line + "\n")

    failures: list[str] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        say(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    def report() -> None:
        text = out.getvalue()
        (ROOT / "handoff" / "r3_capture_429_proof.txt").write_text(text)
        print(text, end="")

    from edgefactory.sources import oddspapi_odds as op
    import scripts.capture_oddspapi as cap

    day = "2026-10-10"
    say("== R3: the capture's 429 handlers record what they catch ==")
    say("")
    src = (ROOT / "scripts" / "capture_oddspapi.py").read_bytes()
    import hashlib
    say(f"source under test: scripts/capture_oddspapi.py  "
        f"sha256 {hashlib.sha256(src).hexdigest()[:16]}…")
    say("the added calls, as they appear in the working tree:")
    for n, line in enumerate(src.decode().splitlines(), start=1):
        if "_record_rate_limit(exc)" in line:
            say(f"  {n}: {line.strip()}")
    say("")

    def run(*, bypass_board: bool, odds_boom: bool, neuter_handler: bool,
            outdir: pathlib.Path, frozen: bool = True, record_transport: bool = True):
        """One capture run under the chosen stubs.

        Returns (receipt dict, persisted bytes, dials, stubbed-out state).
        """
        dials = {"n": 0}
        op._RATE_LIMIT_DIAG.clear()          # a fresh process holds no evidence
        os.environ["ODDSPAPI_API_KEYS"] = "k1"
        saved = {
            "OUT_DIR": cap.OUT_DIR,
            "api_keys": cap.api_keys,
            "fetch_fixtures": cap.fetch_fixtures,
            "fetch_odds": cap.fetch_odds,
            "record": cap._record_rate_limit,
            "op_record": op._record_rate_limit,
            "datetime": cap.datetime,
            "urlopen": urllib.request.urlopen,
        }
        try:
            cap.OUT_DIR = pathlib.Path(outdir)
            cap.api_keys = lambda: ("k1",)
            if frozen:
                cap.datetime = _FrozenDatetime
            if neuter_handler:
                cap._record_rate_limit = lambda exc: None
            if not record_transport:
                # the transport's own recorder silenced: what is left is the
                # handler's read (and the handler's call, when not neutered).
                op._record_rate_limit = lambda exc: None
            if bypass_board:
                cap.fetch_fixtures = lambda day_: (_ for _ in ()).throw(_http_429(HEADERS))
            if odds_boom:
                cap.fetch_fixtures = lambda day_: list(FIXTURE)
                cap.fetch_odds = lambda fid: (_ for _ in ()).throw(_http_429(HEADERS))

            def counted(req, timeout=None, **kw):  # noqa: ARG001
                dials["n"] += 1
                url = getattr(req, "full_url", str(req))
                raise _http_429(CACHE_HEADERS if "/markets" in url else HEADERS)

            urllib.request.urlopen = counted
            receipt = cap.capture(day)
        finally:
            cap.OUT_DIR = saved["OUT_DIR"]
            cap.api_keys = saved["api_keys"]
            cap.fetch_fixtures = saved["fetch_fixtures"]
            cap.fetch_odds = saved["fetch_odds"]
            cap._record_rate_limit = saved["record"]
            op._record_rate_limit = saved["op_record"]
            cap.datetime = saved["datetime"]
            urllib.request.urlopen = saved["urlopen"]
        path = pathlib.Path(outdir) / f"oddspapi_capture_{day}.json"
        return receipt, (path.read_bytes() if path.exists() else b""), dials["n"]

    def brief(receipt: dict) -> str:
        keys = ("status", "http_status", "attempted", "fixtures", "rows", "matched")
        return " ".join(f"{k}={receipt.get(k)!r}" for k in keys)

    with tempfile.TemporaryDirectory() as td:
        base = pathlib.Path(td)
        # ---------------------------------------------------------------- arm 1
        say("-- arm 1: the 429 comes through the transport (production path) --")
        r_fix, b_fix, d_fix = run(bypass_board=False, odds_boom=False,
                                  neuter_handler=False, outdir=base / "a1fix")
        r_pre, b_pre, d_pre = run(bypass_board=False, odds_boom=False,
                                  neuter_handler=True, outdir=base / "a1pre")
        say(f"  with the handler call:    {brief(r_fix)}  dials={d_fix}")
        say(f"  without it (pre-fix):     {brief(r_pre)}  dials={d_pre}")
        say(f"  rate_limit (with):    {json.dumps(r_fix.get('rate_limit'), sort_keys=True)}")
        say(f"  rate_limit (without): {json.dumps(r_pre.get('rate_limit'), sort_keys=True)}")
        say(f"  persisted bytes: with={len(b_fix)} without={len(b_pre)} "
            f"(clock frozen so byte-identity is meaningful)")
        check("arm 1: the receipt is BYTE-IDENTICAL with and without the added call",
              b_fix == b_pre and len(b_fix) > 0, f"{len(b_fix)} bytes each")
        check("arm 1: the transport's evidence is what the receipt carries",
              r_fix.get("rate_limit", {}).get("retry_after_s") == "3600"
              and r_pre.get("rate_limit", {}).get("retry_after_s") == "3600")
        say("")

        # ---------------------------------------------------------------- arm 2
        say("-- arm 2: the 429 is raised at the seam (transport bypassed) --")
        r2_fix, b2_fix, d2_fix = run(bypass_board=True, odds_boom=False,
                                     neuter_handler=False, outdir=base / "a2fix")
        r2_pre, b2_pre, d2_pre = run(bypass_board=True, odds_boom=False,
                                     neuter_handler=True, outdir=base / "a2pre")
        say(f"  with the handler call:    {brief(r2_fix)}  dials={d2_fix}")
        say(f"  without it (pre-fix):     {brief(r2_pre)}  dials={d2_pre}")
        say(f"  rate_limit (with):    {json.dumps(r2_fix.get('rate_limit'), sort_keys=True)}")
        say(f"  rate_limit (without): {json.dumps(r2_pre.get('rate_limit'), sort_keys=True)}")
        say(f"  persisted receipt WITH the call, whole:")
        for line in json.dumps(json.loads(b2_fix.decode()), indent=2, sort_keys=True).splitlines():
            say(f"    {line}")
        check("arm 2: with the call the receipt carries the provider's retry_after",
              r2_fix.get("rate_limit", {}).get("retry_after_s") == "3600")
        check("arm 2: without it the receipt has no quota evidence (the incident)",
              not r2_pre.get("rate_limit"))
        say("")

        # ---------------------------------------------------------------- arm 3
        say("-- arm 3: no path double-counts --")
        check("arm 3: transport dials identical with/without the call (transport path)",
              d_fix == d_pre, f"{d_fix} vs {d_pre}")
        check("arm 3: transport dials identical with/without the call (bypass path)",
              d2_fix == d2_pre, f"{d2_fix} vs {d2_pre}")
        strip = lambda r: {k: v for k, v in r.items() if k != "rate_limit"}
        check("arm 3: every receipt counter identical (transport path, ignoring rate_limit)",
              strip(r_fix) == strip(r_pre))
        check("arm 3: the bypass receipts differ ONLY in rate_limit",
              strip(r2_fix) == strip(r2_pre),
              "with=" + json.dumps(r2_fix.get("rate_limit"), sort_keys=True))

        say("  recorder idempotence (the double-count question directly):")
        exc = _http_429(HEADERS)
        op._RATE_LIMIT_DIAG.clear()
        op._record_rate_limit(exc)
        first = op.rate_limit_diagnostics()
        op._record_rate_limit(exc)
        second = op.rate_limit_diagnostics()
        say(f"    once:  {json.dumps(first, sort_keys=True)}")
        say(f"    twice: {json.dumps(second, sort_keys=True)}")
        check("arm 3: recording the same exception twice yields the same dict",
              first == second and len(second) == 5)
        other = _http_429({"Retry-After": "60"})
        op._record_rate_limit(other)
        third = op.rate_limit_diagnostics()
        say(f"    then a different 429: {json.dumps(third, sort_keys=True)}")
        check("arm 3: a different 429 REPLACES the dict (no accumulation)",
              len(third) == 5 and third["retry_after_s"] == "60")

        say("  the per-fixture handler (the second site), where the run also")
        say("  dials the catalogue first (`/markets`, its own 429 with Retry-After 60):")
        b_fix_on, _, bd_fix_on = run(bypass_board=False, odds_boom=True,
                                     neuter_handler=False, outdir=base / "b1",
                                     record_transport=True)
        b_pre_on, _, bd_pre_on = run(bypass_board=False, odds_boom=True,
                                     neuter_handler=True, outdir=base / "b2",
                                     record_transport=True)
        b_fix_off, _, bd_fix_off = run(bypass_board=False, odds_boom=True,
                                       neuter_handler=False, outdir=base / "b3",
                                       record_transport=False)
        b_pre_off, _, bd_pre_off = run(bypass_board=False, odds_boom=True,
                                       neuter_handler=True, outdir=base / "b4",
                                       record_transport=False)
        say(f"    call ON,  transport recorder ON : "
            f"{json.dumps(b_fix_on.get('rate_limit'), sort_keys=True)}  dials={bd_fix_on}")
        say(f"    call OFF, transport recorder ON : "
            f"{json.dumps(b_pre_on.get('rate_limit'), sort_keys=True)}  dials={bd_pre_on}")
        say(f"    call ON,  transport recorder OFF: "
            f"{json.dumps(b_fix_off.get('rate_limit'), sort_keys=True)}  dials={bd_fix_off}")
        say(f"    call OFF, transport recorder OFF: "
            f"{json.dumps(b_pre_off.get('rate_limit'), sort_keys=True)}  dials={bd_pre_off}")
        check("arm 3: parity — a stale 429 loses to the one this handler caught",
              b_fix_on.get("rate_limit", {}).get("retry_after_s") == "3600"
              and b_pre_on.get("rate_limit", {}).get("retry_after_s") == "60",
              "with=3600 (the caught exception) / without=60 (an earlier, unrelated 429)")
        check("arm 3: the call alone is sufficient (transport recorder silenced)",
              b_fix_off.get("rate_limit", {}).get("retry_after_s") == "3600"
              and not b_pre_off.get("rate_limit"))
        check("arm 3: all four variants agree on every counter and on the dial count",
              strip(b_fix_on) == strip(b_pre_on) == strip(b_fix_off) == strip(b_pre_off)
              and len({bd_fix_on, bd_pre_on, bd_fix_off, bd_pre_off}) == 1,
              f"dials={bd_fix_on}")
        say("")

        # ------------------------------------------------------- real-clock check
        say("-- control: the same arms on a real clock, captured_at dropped --")
        r4_fix, b4_fix, d4_fix = run(bypass_board=False, odds_boom=False,
                                     neuter_handler=False, outdir=base / "a4fix", frozen=False)
        r4_pre, b4_pre, d4_pre = run(bypass_board=False, odds_boom=False,
                                     neuter_handler=True, outdir=base / "a4pre", frozen=False)
        drop = lambda r: {k: v for k, v in r.items() if k != "captured_at"}
        check("control: with the real clock the receipts still match field for field",
              drop(r4_fix) == drop(r4_pre) and d4_fix == d4_pre)
        say("")

    # ------------------------------------------------------------------- suite
    say("-- the file's own tests, at this tree --")
    proc = subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), "-m", "pytest",
         "tests/test_oddspapi_quota_honesty.py", "-q", "-p", "no:randomly"],
        cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": "src"})
    tail = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()][-2:]
    for line in tail:
        say(f"  {line}")
    check("the quota-honesty file passes at this tree", proc.returncode == 0)
    say("")

    say(f"== verdict: {'ALL ARMS PASS' if not failures else 'ARM FAILURE — ' + '; '.join(failures)} ==")
    report()
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
