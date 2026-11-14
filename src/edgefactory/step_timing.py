"""Per-step wall-clock timing for pipeline runs (observability only).

Every timed step prints one line when it finishes::

    STEP_TIMING label=<name> status=ok|error seconds=<n.n>

At interpreter exit a summary is printed, one line per label::

    STEP_TIMING_SUMMARY label=<name> calls=<n> total_seconds=<n.n>

Nested steps are counted inside their parents, so totals overlap by design.
Exceptions are never swallowed: a failing step is recorded with
``status=error`` and the original exception propagates unchanged.
"""

from __future__ import annotations

import atexit
import functools
import time
from contextlib import contextmanager
from typing import Any, Callable, Iterator, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

_LABEL_MAX = 160
_TOTALS: dict[str, list[float]] = {}  # label -> [calls, total_seconds]


def _clip(label: str) -> str:
    text = " ".join(str(label).split())
    return text if len(text) <= _LABEL_MAX else text[: _LABEL_MAX - 3] + "..."


def _record(label: str, seconds: float, ok: bool) -> None:
    entry = _TOTALS.setdefault(label, [0.0, 0.0])
    entry[0] += 1
    entry[1] += seconds
    status = "ok" if ok else "error"
    print(f"STEP_TIMING label={label} status={status} seconds={seconds:.1f}", flush=True)


@contextmanager
def timed_step(label: str) -> Iterator[None]:
    """Time the enclosed block; record it whether it succeeds or raises."""
    name = _clip(label)
    started = time.monotonic()
    ok = False
    try:
        yield
        ok = True
    finally:
        _record(name, time.monotonic() - started, ok)


def timed(label: str | None = None) -> Callable[[F], F]:
    """Decorator form of :func:`timed_step`. Defaults to the function's qualname."""

    def decorate(fn: F) -> F:
        name = label or fn.__qualname__

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with timed_step(name):
                return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorate


def print_summary() -> None:
    if not _TOTALS:
        return
    print("STEP_TIMING_SUMMARY (nested steps are included in their parents)", flush=True)
    ranked = sorted(_TOTALS.items(), key=lambda item: item[1][1], reverse=True)
    for label, (calls, total) in ranked[:60]:
        print(
            f"STEP_TIMING_SUMMARY label={label} calls={int(calls)} total_seconds={total:.1f}",
            flush=True,
        )


atexit.register(print_summary)
