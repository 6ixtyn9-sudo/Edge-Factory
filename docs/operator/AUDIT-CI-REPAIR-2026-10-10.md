# Temporary audit CI admission repair — 2026-10-10

Run 38027657811 checked out 5e47c58 on CPython 3.13.16. Its eight
additional failures and ten setup errors waited for READY/FAILED on a
DISABLED temporary recorder. The recorder deliberately admits only the exact
calibrated CPython 3.11.2 Linux build; this was not a worker timeout.

The unchanged admission predicate now has a private function boundary.
Synthetic recorder and parity tests stub only that boundary, exercising the
real worker, storage, serialization and fault paths. Separate unpatched-policy
controls cover the pinned build, changed build, Python 3.13, non-CPython,
non-Linux and disabled GIL. Refused construction must create no spool or
thread, invoke no payload factory, and leave temporary storage empty.

No timeout was increased, assertion weakened, test skipped or xfailed.
Runtime admission remains unchanged; this is not certification of a new
runtime or production activation. Existing six consensus-contract failures
remain unsuppressed. Notification routing and provider access are untouched.

Local verification (CPython 3.11.2):
- Recorder/runtime/storage/parity controls: 37 passed.
- Full tests: 2616 passed, six known consensus-contract failures, 71.01s.
- git diff --check: clean.

Python 3.13 execution has not been reproduced locally. Its runtime refusal
is covered with explicit interpreter metadata controls, not presented as an
actual Python 3.13 run. No operational workflow was dispatched.
