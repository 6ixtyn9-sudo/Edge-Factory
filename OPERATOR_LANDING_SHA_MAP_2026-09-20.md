# Operator landing — pre/post-rebase SHA map (2026-09-20)

Rebase of `arena/01a0bed7-edge-factory` onto `origin/main` (`53a5f1e`);
landing via `git push origin HEAD:main` (fast-forward; no force anywhere).
Pre-rebase session-branch tip:
`b6916f955a58d8457babd0cd25fd75865bf2d452` (referenced by pre-landing receipts).

| subject | pre-rebase SHA | landed SHA on main |
|---|---|---|
| Add automatically validated ML fade slice | 8e7635d31d574929c27ebc72e0b7507fac96fa2b | abf0e902f6b5ec08f93eaf8017544ef49f7642cb |
| Add research-only conditional ml-fade slice scan | bee72e60764939fe3c9e8dc4f985760b3029057a | 3db78136de30be7d4725db738083facd6a82014d |
| Add home-fade price-robustness study (research-only) | efeddb34376ae2cdf07b465c2ab72903a9b8e04f | 173539a67089f74c54682d78b1e0927d2f1d2dec |
| Correct home-fade signal classification to INSUFFICIENT EVIDENCE | b6916f955a58d8457babd0cd25fd75865bf2d452 | 571e7018a57ca5f787cdb1a5e7d7ea538d32594f |
| docs: operator landing authorization 2026-09-20 | d90881d1e9bbde598c729c36bfc995fc7bb93890 | ef773e558b0308288bf83fb092ea5be8d7f3da39 |

Pre-rebase SHAs become unreachable when the session-branch ref is deleted
(operator-authorized deletion, same directive); treat landed SHAs on `main`
as the only permanent references.
