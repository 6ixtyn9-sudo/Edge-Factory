# SportsGameOdds probe-first quota memo (SHADOW-03 W3-T2)

**Verdict: SKIP for this wave. No adapter is authorized.**

The provider's own [FAQ](https://sportsgameodds.com/docs/faq) defines an
*object* as a top-level item returned by a request; an `/events` response with
10 events consumes 10 objects. Odds markets and bookmakers bundled inside one
event do not multiply the object count. The free Amateur plan is 2,500
objects/month and 10 requests/minute. The provider pricing page also describes
this as one object per event.

## Arithmetic

A full-board daily snapshot is not acceptable: its event count is not bounded
by our slate and can consume 2,500 objects before the month ends. Targeting
only our daily slate is better:

- 40 fixtures/day × 30 days = **1,200 objects/month**; 2× headroom = **2,400**
  → passes narrowly.
- 70 fixtures/day × 30 days = **2,100 objects/month**; 2× headroom = **4,200**
  → fails.
- Our observed operating range is approximately 40–70 fixtures/day, therefore
  the required 2× headroom cannot be guaranteed without a separate hard cap and
  an operator-approved cadence change.

**Decision:** SKIP rather than ship an adapter that would silently exceed the
free quota on ordinary high-slate days. Re-open only with a proven lower slate
cap, a measured object receipt, and explicit operator approval. No requests,
keys, or adapter are introduced by this ticket.
