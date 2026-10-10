# Release disposition

The temporary ML/consensus recorder, storage implementation, scoring hooks,
and implementation-only tests/resource script have been removed from the
release candidate. Historical design and execution documents remain as
research records, not descriptions of currently installed functionality.
Their implementation remains recoverable from Git history at f6b2166.

Retained: fallback-origin correction, six unsuppressed consensus-contract
regressions, provider diagnostics/retry repairs, deterministic settlement
identity tests, and notification eligibility/chunking repairs.

No recorder is activated or shipped by this release. The six known consensus
qualification/electorate defects remain unresolved; this merge is not model
certification. Main-branch operational records are preserved rather than
publishing the experimental branch run's persisted state.

Final release verification: 2592 passed, six preserved contract failures in
64.46s. No recorder references remain in scripts/src/tests. Operational
localdata tree matches integrated main exactly. No workflow changes.
