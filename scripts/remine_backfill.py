#!/usr/bin/env python3
"""Bounded runner-side B1 backfill driver.

This is deliberately a small state machine rather than a second crawler.  It
runs from the existing daily GitHub Actions chain and uses the production
BetExplorer transport for the only multi-run crawl.  Every requested date gets
an append-only ledger receipt; a completed date is never fetched again.

Order and budgets are hard fences:

* three audited Statarea empty days are held without a request;
* at most ten approved BetExplorer result-gap dates are requested per run;
* one Football-Data league/season CSV proof runs only after those 62 dates
  have terminal receipts;
* at most three Legalbet requests are made per run and at most 30 public
  archive pages are sampled in total, with robots checked first.

The script exits zero for a source freeze or an unavailable optional source.
That lets the ordinary official/intraday pipeline continue while the ledger
records what was safely deferred.  It never uses a relay, proxy, CAPTCHA,
or alternate transport.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import html
import io
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.robotparser
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOCALDATA = ROOT / "localdata"
INVENTORY_PATH = LOCALDATA / "coverage_inventory.json"
LEDGER_PATH = LOCALDATA / "backfill_ledger.jsonl"
RAW_ROOT = LOCALDATA / "remine_raw"
BETEXPLORER_BUDGET = 10
LEGALBET_REQUEST_BUDGET = 3
LEGALBET_TOTAL_PAGE_BUDGET = 30

# Only statuses in these sets advance the relevant plan.  Transport failures,
# freezes, and holds remain retryable unless their source has explicitly been
# fenced for the day.
BE_TERMINAL = {"success", "no_matches_day"}
FOOTBALL_COMPLETE = "football_data_complete"


def _run_date() -> str:
    value = os.environ.get("EDGE_FACTORY_RUN_DATE")
    if value:
        dt.date.fromisoformat(value)
        return value
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _norm(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def _json_load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        handle.flush()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                try:
                    value = json.loads(line)
                    if isinstance(value, dict):
                        rows.append(value)
                except json.JSONDecodeError:
                    # A torn trailing line must not prevent the next runner
                    # from reading the durable prefix.
                    continue
    except FileNotFoundError:
        pass
    return rows


def _ledger_rows() -> list[dict[str, Any]]:
    return _read_jsonl(LEDGER_PATH)


def _audit_path(run_date: str) -> Path:
    return LOCALDATA / f"remine_audit_{run_date}.jsonl"


def _record(run_date: str, record: dict[str, Any]) -> None:
    """Append one audit and/or ledger record with common provenance fields."""
    value = {
        "observed_at": _now(),
        "run_date": run_date,
        "driver": "scripts/remine_backfill.py",
        **record,
    }
    _append_jsonl(_audit_path(run_date), value)


def _ledger_once(existing: list[dict[str, Any]], value: dict[str, Any], key: tuple[str, ...]) -> bool:
    """Append an immutable state transition unless its identity already exists."""
    if any(tuple(str(row.get(k, "")) for k in key) == tuple(str(value.get(k, "")) for k in key) for row in existing):
        return False
    _append_jsonl(LEDGER_PATH, value)
    existing.append(value)
    return True


def _write_immutable(path: Path, payload: bytes) -> tuple[str, bool, bool]:
    """Write bytes once; return (checksum, wrote, collision)."""
    digest = _sha256(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        current = path.read_bytes()
        return _sha256(current), False, _sha256(current) != digest
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        # No overwrite: a race or a prior artifact wins and is verified above.
        try:
            os.link(temp_name, path)
            wrote = True
        except FileExistsError:
            wrote = False
        return digest, wrote, False
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def _inventory() -> dict[str, Any]:
    value = _json_load(INVENTORY_PATH, {})
    if not isinstance(value, dict):
        raise RuntimeError(f"invalid coverage inventory: {INVENTORY_PATH}")
    return value


def _approved_betexplorer_days(inventory: dict[str, Any]) -> list[str]:
    plan = inventory.get("crawl_plan_inputs", {}).get("betexplorer_results", {})
    days = plan.get("proposed_internal_gap_days", [])
    if not isinstance(days, list) or len(days) > 62:
        raise RuntimeError("BetExplorer inventory is not the approved 62-date plan")
    return [str(day) for day in days]


def _hold_statarea(run_date: str, inventory: dict[str, Any], ledger: list[dict[str, Any]], dry_run: bool = False) -> int:
    days = inventory.get("sources", {}).get("statarea", {}).get("date_range", {}).get("no_matches_days", [])
    audited: list[dict[str, Any]] = []
    for audit_path in sorted(LOCALDATA.glob("remine_audit_*.jsonl")):
        audited.extend(_read_jsonl(audit_path))
    held = 0
    for day in days:
        # This state is intentionally based only on the already committed
        # audit confirmation.  It never imports a Statarea fetcher.
        confirmations = [
            row for row in audited
            if row.get("source") == "statarea"
            and row.get("date") == day
            and row.get("status") == "no_matches_day"
        ]
        if not confirmations:
            # The audited confirmations live in the date-named audit file in
            # normal operation.  If it is not present, do not manufacture a
            # held day; the operator can restore the committed receipt.
            continue
        confirmation = confirmations[-1]
        value = {
            "observed_at": _now(),
            "run_date": run_date,
            "source": "statarea",
            "date": day,
            "status": "held",
            "source_status": "no_matches_day",
            "terminal": True,
            "request_count": 0,
            "refetch": False,
            "url": confirmation.get("url"),
            "checksum": confirmation.get("checksum"),
            "checksum_status": confirmation.get("checksum_status", "relay_no_raw_bytes"),
            "provenance": "committed audited no-match confirmation; no runner refetch",
        }
        if dry_run:
            held += 1
        elif _ledger_once(ledger, value, ("source", "date", "status")):
            _record(run_date, {**value, "stage": "statarea_hold"})
            held += 1
    return held


def _be_csv_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    # Event IDs are the strongest fence.  Older committed rows do not all
    # have one, so kickoff is the stable fallback for a same-day team pair.
    identity = str(row.get("event_id") or row.get("kickoff") or "")
    return (
        str(row.get("date", "")),
        identity,
        _norm(row.get("home")),
        _norm(row.get("away")),
    )


def _merge_betexplorer_rows(day: str, incoming: list[dict[str, Any]]) -> dict[str, int]:
    """Merge one date into its monthly gzip with existing rows winning."""
    path = LOCALDATA / f"betexplorer_results_{day[:7]}.csv.gz"
    existing_rows: list[dict[str, str]] = []
    fieldnames = [
        "date", "kickoff", "country", "league", "home", "away", "hs", "gs",
        "ht_hs", "ht_gs", "match_url", "event_id", "fetched_at",
    ]
    if path.exists():
        with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = list(reader.fieldnames or fieldnames)
            existing_rows = [dict(row) for row in reader]
    counts: Counter[str] = Counter()
    by_key: dict[tuple[str, str, str, str], dict[str, str]] = {}
    for row in existing_rows:
        key = _be_csv_key(row)
        if key in by_key:
            counts["existing_duplicates"] += 1
            continue
        by_key[key] = row
    for raw in incoming:
        row = {name: str(raw.get(name, "")) for name in fieldnames}
        for name in fieldnames:
            row.setdefault(name, "")
        key = _be_csv_key(row)
        if key in by_key:
            counts["existing_wins_collisions"] += 1
            continue
        by_key[key] = row
        counts["inserted"] += 1
    if counts["inserted"]:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
        try:
            with os.fdopen(fd, "wb") as binary:
                with gzip.GzipFile(fileobj=binary, mode="wb", mtime=0) as gz:
                    text = io.TextIOWrapper(gz, encoding="utf-8", newline="")
                    writer = csv.DictWriter(text, fieldnames=fieldnames, extrasaction="ignore")
                    writer.writeheader()
                    for row in by_key.values():
                        writer.writerow(row)
                    text.flush()
                binary.flush()
                os.fsync(binary.fileno())
            os.replace(temp_name, path)
        finally:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
    counts["rows_after"] = len(by_key)
    return dict(counts)


def _betexplorer(run_date: str, inventory: dict[str, Any], ledger: list[dict[str, Any]], dry_run: bool) -> dict[str, Any]:
    days = _approved_betexplorer_days(inventory)
    terminal = {
        str(row.get("date"))
        for row in ledger
        if row.get("source") == "betexplorer_results" and row.get("status") in BE_TERMINAL
    }
    pending = [day for day in days if day not in terminal]
    if not pending:
        complete = any(row.get("source") == "betexplorer_results" and row.get("status") == "gap_fill_complete" for row in ledger)
        if not complete:
            value = {
                "observed_at": _now(), "run_date": run_date,
                "source": "betexplorer_results", "status": "gap_fill_complete",
                "approved_gap_count": len(days), "terminal_receipt_count": len(terminal),
                "request_count": 0, "provenance": "all approved dates have terminal successful/held receipts",
            }
            if _ledger_once(ledger, value, ("source", "status")):
                _record(run_date, {**value, "stage": "betexplorer_complete"})
        return {"approved": len(days), "pending_before": 0, "requests": 0, "frozen": False, "remaining": 0, "complete": True}

    if dry_run:
        return {"approved": len(days), "pending_before": len(pending), "requests": 0, "frozen": False, "remaining": len(pending), "complete": False, "dry_run": True}

    from edgefactory.sources import betexplorer_odds

    betexplorer_odds.reset_fetch_count()
    requests = 0
    frozen = False
    freeze_reason = None
    for day in pending[:BETEXPLORER_BUDGET]:
        requests += 1
        url = f"{betexplorer_odds.BASE}/football/results/?year={day[:4]}&month={day[5:7]}&day={day[8:10]}"
        try:
            rows = betexplorer_odds.fetch_day_matches(day)
            receipt = dict(betexplorer_odds.LAST_RESULTS_RECEIPT)
            raw = betexplorer_odds.last_response_bytes()
            artifact = RAW_ROOT / "betexplorer_results" / f"{day}.html"
            checksum, wrote, artifact_collision = _write_immutable(artifact, raw) if raw else (None, False, False)
            merge_rows = [{**row, "fetched_at": _now()} for row in rows]
            merge = _merge_betexplorer_rows(day, merge_rows) if receipt.get("status") in BE_TERMINAL and not artifact_collision else {}
            status = str(receipt.get("status", "transport_error"))
            if artifact_collision:
                status = "raw_artifact_collision"
            elif status not in BE_TERMINAL:
                status = "crawl_failure"
            value = {
                "observed_at": _now(), "run_date": run_date,
                "source": "betexplorer_results", "date": day, "status": status,
                "request_count": 1, "url": receipt.get("url", url),
                "response_bytes": receipt.get("response_bytes") or (len(raw) if raw else None),
                "checksum": checksum or receipt.get("sha256"),
                "checksum_status": "sha256_raw_response" if checksum else "unavailable_no_response_bytes",
                "raw_artifact": str(artifact.relative_to(ROOT)) if raw else None,
                "raw_artifact_written": wrote,
                "raw_artifact_collision": artifact_collision,
                "rows": len(rows), "duplicates": merge.get("existing_duplicates", 0),
                "existing_wins_collisions": merge.get("existing_wins_collisions", 0),
                "inserted": merge.get("inserted", 0),
                "provenance": "production edgefactory.sources.betexplorer_odds; single-flight/throttle transport",
            }
            _record(run_date, {**value, "stage": "betexplorer_request"})
            _ledger_once(ledger, value, ("source", "date", "status"))
        except (betexplorer_odds.BetExplorerChallenge, betexplorer_odds.BetExplorerCoolingDown) as exc:
            freeze_reason = type(exc).__name__
            receipt = dict(getattr(betexplorer_odds, "LAST_RESULTS_RECEIPT", {}))
            raw = betexplorer_odds.last_response_bytes()
            artifact = RAW_ROOT / "betexplorer_results" / f"{day}.html"
            checksum, wrote, artifact_collision = _write_immutable(artifact, raw) if raw else (None, False, False)
            request_value = {
                "observed_at": _now(), "run_date": run_date,
                "source": "betexplorer_results", "date": day,
                "status": "challenge" if isinstance(exc, betexplorer_odds.BetExplorerChallenge) else "cooldown",
                "request_count": 1, "url": receipt.get("url", url),
                "response_bytes": receipt.get("response_bytes") or (len(raw) if raw else None),
                "checksum": checksum or receipt.get("sha256"),
                "checksum_status": "sha256_raw_response" if checksum else "unavailable_no_response_bytes",
                "raw_artifact": str(artifact.relative_to(ROOT)) if raw else None,
                "raw_artifact_written": wrote, "raw_artifact_collision": artifact_collision,
                "error": str(exc),
                "provenance": "production edgefactory.sources.betexplorer_odds",
            }
            _record(run_date, {**request_value, "stage": "betexplorer_request"})
            freeze_reason = type(exc).__name__
            frozen = True
            value = {
                "observed_at": _now(), "run_date": run_date,
                "source": "betexplorer_results", "status": "source_freeze",
                "request_count": requests, "url": url,
                "reason": freeze_reason,
                "provenance": "source frozen for this runner day; no bypass or alternate transport",
            }
            _record(run_date, {**value, "stage": "betexplorer_freeze"})
            _ledger_once(ledger, value, ("source", "status", "run_date"))
            break
        except Exception as exc:  # a failed date remains retryable next run
            value = {
                "observed_at": _now(), "run_date": run_date,
                "source": "betexplorer_results", "date": day, "status": "crawl_failure",
                "request_count": 1, "url": url, "response_bytes": None,
                "checksum": None, "checksum_status": "unavailable_no_response_bytes",
                "error": f"{type(exc).__name__}: {exc}",
                "provenance": "production edgefactory.sources.betexplorer_odds",
            }
            _record(run_date, {**value, "stage": "betexplorer_request"})
            _ledger_once(ledger, value, ("source", "date", "observed_at"))

    remaining = len([day for day in days if not any(row.get("source") == "betexplorer_results" and row.get("date") == day and row.get("status") in BE_TERMINAL for row in ledger)])
    complete = remaining == 0
    if complete:
        value = {
            "observed_at": _now(), "run_date": run_date,
            "source": "betexplorer_results", "status": "gap_fill_complete",
            "approved_gap_count": len(days), "terminal_receipt_count": len(terminal) + len(pending),
            "request_count": 0,
            "provenance": "all approved dates have terminal successful/held receipts",
        }
        if _ledger_once(ledger, value, ("source", "status")):
            _record(run_date, {**value, "stage": "betexplorer_complete"})
    return {"approved": len(days), "pending_before": len(pending), "requests": requests, "frozen": frozen, "freeze_reason": freeze_reason, "remaining": remaining, "complete": complete}


def _http_bytes(url: str, *, timeout: int = 25) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": "EdgeFactory-cooperative-audit/1.0 (+operator review)"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(getattr(response, "status", 200) or 200), {str(k): str(v) for k, v in response.headers.items()}, response.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), {str(k): str(v) for k, v in exc.headers.items()}, exc.read() if hasattr(exc, "read") else b""


def _football_donor_coverage(raw: bytes, inventory: dict[str, Any]) -> dict[str, Any]:
    """Report exact fixture-key coverage without altering donor files."""
    text = raw.decode("latin-1", "replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    fixtures: set[tuple[str, str, str]] = set()
    for row in rows:
        date_value = str(row.get("Date", "")).strip()
        parsed = None
        for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                parsed = dt.datetime.strptime(date_value, fmt).date().isoformat()
                break
            except ValueError:
                continue
        if parsed:
            fixtures.add((parsed, _norm(row.get("HomeTeam")), _norm(row.get("AwayTeam"))))
    coverage: dict[str, int] = {}
    donor_rows: dict[str, int] = {}
    for donor in ("statarea", "zulubet", "forebet"):
        count = 0
        path = LOCALDATA / f"{donor}.csv.gz"
        if not path.exists():
            coverage[donor] = 0
            donor_rows[donor] = 0
            continue
        with gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="") as handle:
            donor_reader = csv.DictReader(handle)
            for row in donor_reader:
                donor_rows[donor] = donor_rows.get(donor, 0) + 1
                key = (str(row.get("date", ""))[:10], _norm(row.get("home")), _norm(row.get("away")))
                if key in fixtures:
                    count += 1
        coverage[donor] = count
    return {
        "football_data_rows": len(rows),
        "football_data_fixtures": len(fixtures),
        "donor_rows_scanned": donor_rows,
        "donor_fixture_row_coverage": coverage,
        "coverage_definition": "normalized date + home + away exact fixture key; reporting only",
    }


def _football_data(run_date: str, inventory: dict[str, Any], ledger: list[dict[str, Any]], dry_run: bool) -> dict[str, Any]:
    if any(row.get("source") == "football_data" and row.get("status") == FOOTBALL_COMPLETE for row in ledger):
        return {"status": "complete", "requests": 0}
    if dry_run:
        return {"status": "pending", "requests": 0, "dry_run": True}
    url = "https://www.football-data.co.uk/mmz4281/2425/E0.csv"
    try:
        status_code, headers, raw = _http_bytes(url)
        checksum = _sha256(raw) if raw else None
        artifact = RAW_ROOT / "football-data" / "E0_2425.csv"
        if status_code != 200 or not raw:
            value = {
                "observed_at": _now(), "run_date": run_date, "source": "football_data",
                "status": "hold", "request_count": 1, "url": url,
                "http_status": status_code, "response_bytes": len(raw), "checksum": checksum,
                "checksum_status": "sha256_raw_response" if raw else "unavailable_no_response_bytes",
                "reason": "HTTP failure or empty response; retry on a later runner day",
                "provenance": "one controlled pre-2026 E0 x 2024-25 CSV proof",
            }
            _record(run_date, {**value, "stage": "football_data"})
            _ledger_once(ledger, value, ("source", "status", "run_date"))
            return {"status": "hold", "requests": 1}
        artifact_checksum, wrote, collision = _write_immutable(artifact, raw)
        reader = csv.reader(io.StringIO(raw.decode("latin-1", "replace")))
        header = next(reader, [])
        header_lower = {str(value).strip().lower() for value in header}
        required_open = {"date", "hometeam", "awayteam", "fthg", "ftag", "ftr", "b365h", "b365d", "b365a"}
        close_fields = {"b365ch", "b365cd", "b365ca"}
        missing_open = sorted(required_open - header_lower)
        missing_close = sorted(close_fields - header_lower)
        coverage = _football_donor_coverage(raw, inventory)
        proof_status = "complete" if not missing_open and not missing_close and not collision else "hold"
        value = {
            "observed_at": _now(), "run_date": run_date, "source": "football_data",
            "status": FOOTBALL_COMPLETE if proof_status == "complete" else "header_or_artifact_hold",
            "request_count": 1, "url": url, "http_status": status_code,
            "response_bytes": len(raw), "checksum": artifact_checksum,
            "checksum_status": "sha256_raw_response", "raw_artifact": str(artifact.relative_to(ROOT)),
            "raw_artifact_written": wrote, "raw_artifact_collision": collision,
            "league": "E0", "season": "2024-25", "header_fields": header,
            "missing_open_fields": missing_open, "missing_close_fields": missing_close,
            "open_close_field_check": {"opening_fields_present": not missing_open, "closing_fields_present": not missing_close},
            "donor_coverage": coverage,
            "provenance": "one controlled pre-2026 league×season CSV proof; raw-to-gitignored artifact",
        }
        _record(run_date, {**value, "stage": "football_data"})
        _ledger_once(ledger, value, ("source", "status"))
        return {"status": value["status"], "requests": 1, "missing_open": missing_open, "missing_close": missing_close}
    except Exception as exc:
        value = {
            "observed_at": _now(), "run_date": run_date, "source": "football_data",
            "status": "hold", "request_count": 1, "url": url,
            "error": f"{type(exc).__name__}: {exc}",
            "provenance": "one controlled pre-2026 E0 x 2024-25 CSV proof",
        }
        _record(run_date, {**value, "stage": "football_data"})
        _ledger_once(ledger, value, ("source", "status", "run_date"))
        return {"status": "hold", "requests": 1}


def _legalbet_paths(page: bytes, base_url: str) -> list[str]:
    text = page.decode("utf-8", "replace")
    found: list[str] = []
    excluded = ("/user", "/rating", "/stat", "/statistics", "/login", "/auth", "/subscription")
    for href in re.findall(r"href\s*=\s*[\"']([^\"']+)[\"']", text, flags=re.I):
        href = html.unescape(href).strip()
        absolute = urllib.parse.urljoin(base_url, href)
        parsed = urllib.parse.urlsplit(absolute)
        if parsed.scheme not in {"http", "https"} or parsed.netloc not in {"legalbet.ru", "www.legalbet.ru"}:
            continue
        path = parsed.path.rstrip("/") or "/"
        lower = path.lower()
        if any(piece in lower for piece in excluded) or parsed.query or parsed.fragment:
            continue
        if "/tips/" not in lower and not lower.startswith("/tips"):
            continue
        if absolute not in found:
            found.append(absolute)
    return found


def _legalbet(run_date: str, ledger: list[dict[str, Any]], dry_run: bool) -> dict[str, Any]:
    page_rows = [row for row in ledger if row.get("source") == "legalbet" and row.get("status") == "archive_page"]
    used = len({str(row.get("url")) for row in page_rows})
    if used >= LEGALBET_TOTAL_PAGE_BUDGET:
        return {"status": "complete", "requests": 0, "pages": used, "robots": "previously_checked"}
    if dry_run:
        return {"status": "pending", "requests": 0, "pages": used, "dry_run": True}

    requests = 0
    robots_url = "https://legalbet.ru/robots.txt"
    robots_ok = any(row.get("source") == "legalbet" and row.get("status") == "robots_ok" for row in ledger)
    if not robots_ok and requests < LEGALBET_REQUEST_BUDGET:
        requests += 1
        try:
            code, headers, body = _http_bytes(robots_url)
            digest = _sha256(body) if body else None
            artifact = RAW_ROOT / "legalbet" / "robots.txt"
            artifact_checksum, artifact_written, artifact_collision = _write_immutable(artifact, body) if body else (None, False, False)
            parser = urllib.robotparser.RobotFileParser()
            try:
                parser.parse(body.decode("utf-8", "replace").splitlines())
                allowed = code == 200 and bool(body) and parser.can_fetch("EdgeFactory-cooperative-audit/1.0", "https://legalbet.ru/tips/archive/")
            except Exception:
                allowed = False
            value = {
                "observed_at": _now(), "run_date": run_date, "source": "legalbet",
                "status": "robots_ok" if allowed else "robots_hold", "request_count": 1,
                "url": robots_url, "http_status": code, "response_bytes": len(body),
                "checksum": artifact_checksum or digest, "checksum_status": "sha256_raw_response" if body else "unavailable_no_response_bytes",
                "raw_artifact": str(artifact.relative_to(ROOT)) if body else None,
                "raw_artifact_written": artifact_written, "raw_artifact_collision": artifact_collision,
                "robots_allows_archive": allowed,
                "provenance": "robots checked before any public archive page; no alternate transport",
            }
            _record(run_date, {**value, "stage": "legalbet_robots"})
            _ledger_once(ledger, value, ("source", "status"))
            if not allowed:
                return {"status": "hold", "requests": requests, "pages": used, "reason": "robots unavailable or disallowed"}
            robots_ok = True
        except Exception as exc:
            value = {
                "observed_at": _now(), "run_date": run_date, "source": "legalbet",
                "status": "robots_hold", "request_count": 1, "url": robots_url,
                "error": f"{type(exc).__name__}: {exc}",
                "provenance": "robots checked before any public archive page",
            }
            _record(run_date, {**value, "stage": "legalbet_robots"})
            _ledger_once(ledger, value, ("source", "status", "run_date"))
            return {"status": "hold", "requests": requests, "pages": used, "reason": "robots request failed"}

    if not robots_ok or requests >= LEGALBET_REQUEST_BUDGET:
        return {"status": "hold", "requests": requests, "pages": used, "reason": "robots gate"}

    queue = ["https://legalbet.ru/tips/archive/"]
    seen_urls = {str(row.get("url")) for row in ledger if row.get("source") == "legalbet"}
    while queue and requests < LEGALBET_REQUEST_BUDGET and used < LEGALBET_TOTAL_PAGE_BUDGET:
        url = queue.pop(0)
        if url in seen_urls:
            continue
        requests += 1
        try:
            code, headers, body = _http_bytes(url)
            digest = _sha256(body) if body else None
            artifact = RAW_ROOT / "legalbet" / f"page_{_sha256(url.encode('utf-8'))[:20]}.html"
            artifact_checksum, artifact_written, artifact_collision = _write_immutable(artifact, body) if body else (None, False, False)
            if code != 200 or not body:
                value = {
                    "observed_at": _now(), "run_date": run_date, "source": "legalbet",
                    "status": "hold", "request_count": 1, "url": url,
                    "http_status": code, "response_bytes": len(body), "checksum": digest,
                    "checksum_status": "sha256_raw_response" if body else "unavailable_no_response_bytes",
                    "raw_artifact": str(artifact.relative_to(ROOT)) if body else None,
                    "raw_artifact_written": artifact_written, "raw_artifact_collision": artifact_collision,
                    "reason": "RU host unavailable; no alternate transport or escalation",
                    "provenance": "public archive sampling after robots",
                }
                _record(run_date, {**value, "stage": "legalbet_page"})
                _ledger_once(ledger, value, ("source", "url", "status"))
                continue
            if any(marker in body.lower() for marker in (b"captcha", b"cloudflare", b"checking your browser")):
                value = {
                    "observed_at": _now(), "run_date": run_date, "source": "legalbet",
                    "status": "hold", "request_count": 1, "url": url,
                    "http_status": code, "response_bytes": len(body), "checksum": digest,
                    "checksum_status": "sha256_raw_response",
                    "raw_artifact": str(artifact.relative_to(ROOT)),
                    "raw_artifact_written": artifact_written, "raw_artifact_collision": artifact_collision,
                    "reason": "challenge surface; no alternate transport or escalation",
                    "provenance": "public archive sampling after robots",
                }
                _record(run_date, {**value, "stage": "legalbet_page"})
                _ledger_once(ledger, value, ("source", "url", "status"))
                continue
            if artifact_collision:
                value = {
                    "observed_at": _now(), "run_date": run_date, "source": "legalbet",
                    "status": "hold", "request_count": 1, "url": url,
                    "http_status": code, "response_bytes": len(body), "checksum": digest,
                    "checksum_status": "sha256_raw_response",
                    "raw_artifact": str(artifact.relative_to(ROOT)),
                    "raw_artifact_written": artifact_written, "raw_artifact_collision": True,
                    "reason": "immutable raw artifact checksum collision; page held",
                    "provenance": "public archive sampling after robots",
                }
                _record(run_date, {**value, "stage": "legalbet_page"})
                _ledger_once(ledger, value, ("source", "url", "status"))
                continue
            links = _legalbet_paths(body, url)
            value = {
                "observed_at": _now(), "run_date": run_date, "source": "legalbet",
                "status": "archive_page", "request_count": 1, "url": url,
                "http_status": code, "response_bytes": len(body), "checksum": digest,
                "checksum_status": "sha256_raw_response", "sample_page": True,
                "raw_artifact": str(artifact.relative_to(ROOT)),
                "raw_artifact_written": artifact_written, "raw_artifact_collision": artifact_collision,
                "discovered_archive_links": len(links),
                "parsed_fixture_rows": 0,
                "provenance": "public archive page after robots; user/rating/stat paths excluded",
            }
            _record(run_date, {**value, "stage": "legalbet_page"})
            if _ledger_once(ledger, value, ("source", "url", "status")):
                used += 1
            seen_urls.add(url)
            for link in links:
                if link not in seen_urls and link not in queue:
                    queue.append(link)
        except Exception as exc:
            value = {
                "observed_at": _now(), "run_date": run_date, "source": "legalbet",
                "status": "hold", "request_count": 1, "url": url,
                "error": f"{type(exc).__name__}: {exc}",
                "reason": "RU host failure; no alternate transport or escalation",
                "provenance": "public archive sampling after robots",
            }
            _record(run_date, {**value, "stage": "legalbet_page"})
            _ledger_once(ledger, value, ("source", "url", "status"))
    return {"status": "complete" if used >= LEGALBET_TOTAL_PAGE_BUDGET else "sampled", "requests": requests, "pages": used}


def run(*, dry_run: bool = False) -> dict[str, Any]:
    run_date = _run_date()
    inventory = _inventory()
    ledger = _ledger_rows()
    statarea_held = _hold_statarea(run_date, inventory, ledger, dry_run=dry_run)
    be = _betexplorer(run_date, inventory, ledger, dry_run)
    football = {"status": "gated", "requests": 0}
    legalbet = {"status": "gated", "requests": 0, "pages": sum(1 for row in ledger if row.get("source") == "legalbet" and row.get("status") == "archive_page")}
    # Strict order fence: no Football-Data request before the BetExplorer
    # completion marker, and no Legalbet request before a valid proof.
    be_complete = bool(be.get("complete")) or any(row.get("source") == "betexplorer_results" and row.get("status") == "gap_fill_complete" for row in ledger)
    if be_complete:
        football = _football_data(run_date, inventory, ledger, dry_run)
        if football.get("status") == "complete":
            legalbet = _legalbet(run_date, ledger, dry_run)
    summary = {
        "run_date": run_date,
        "statarea_held": statarea_held,
        "betexplorer": be,
        "football_data": football,
        "legalbet": legalbet,
        "meter": {
            "statarea": {"consumed": 0, "budget": 3, "held": statarea_held},
            "betexplorer": {"consumed": be.get("requests", 0), "budget": BETEXPLORER_BUDGET, "remaining_gaps": be.get("remaining")},
            "football_data": {"consumed": football.get("requests", 0), "budget": 1, "status": football.get("status")},
            "legalbet": {
                "consumed_requests": legalbet.get("requests", 0),
                "request_budget": LEGALBET_REQUEST_BUDGET,
                "sampled_pages": legalbet.get("pages", 0),
                "total_page_budget": LEGALBET_TOTAL_PAGE_BUDGET,
            },
        },
        "ledger_path": str(LEDGER_PATH.relative_to(ROOT)),
        "audit_path": str(_audit_path(run_date).relative_to(ROOT)),
        "raw_root": str(RAW_ROOT.relative_to(ROOT)),
    }
    print("remine_backfill: " + json.dumps(summary, sort_keys=True))
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="read inventory/ledger and print the meter without network or writes")
    args = parser.parse_args(argv)
    try:
        run(dry_run=args.dry_run)
    except Exception as exc:
        # A malformed inventory is an operator/configuration error, but keep
        # the ordinary daily chain alive and make the failure visible in CI.
        print(f"remine_backfill: configuration failure: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
