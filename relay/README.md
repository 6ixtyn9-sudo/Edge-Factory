# Free source-relay failover

These relays fetch **public Forebet and ScoutingStats endpoints only**. They are
not prediction sources and cannot alter source identity. The Python adapters
require an exact echoed URL and then validate provider JSON/schema.

## Security contract

- POST only; the shared token never appears in a URL.
- Exact host/path/query allowlist; neither deployment is an open proxy.
- No repository, provider, GitHub, Supabase, or notification credentials enter a relay.
- Responses are `no-store` and bounded to 12 MiB.
- Use one long random token in both relays and in GitHub Actions.

Generate a token locally or in a trusted shell:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 1. Ordinary Cloudflare Worker relay

From `relay/cloudflare-worker`:

```bash
npm install
npx wrangler login
npx wrangler secret put RELAY_TOKEN
npx wrangler deploy
```

Copy the resulting `https://...workers.dev` URL. The ordinary relay continues to
use Worker `fetch()` for ScoutingStats and for the existing Forebet transport;
it is not a browser and is not expected to pass Forebet's Cloudflare challenge.
The Browser Run diagnostic described below is a separate, explicitly named
operation and is not used by the Python adapters yet.

## 2. Google Apps Script relay (free Google account)

1. Open <https://script.google.com> and create a project.
2. Paste `google-apps-script/Code.gs` into `Code.gs`.
3. In **Project Settings → Script Properties**, add `RELAY_TOKEN` with the same
   random value used by the Worker.
4. **Deploy → New deployment → Web app**.
5. Execute as **Me**; access **Anyone**.
6. Authorize only external requests and copy the `/exec` URL.

Apps Script remains an independent ordinary-HTTP fallback for ScoutingStats. Its
`UrlFetchApp` path was already tested against six Forebet variants and received
Cloudflare challenge HTML/403 responses, so it is not a Browser Run substitute.

The source contains an `appsscript.json` manifest for users who prefer `clasp`,
but no Google credential belongs in this repository.

## 3. Configure GitHub Actions

Create these repository Actions secrets:

```text
EDGE_FACTORY_RELAY_URLS=https://WORKER.workers.dev,https://script.google.com/macros/s/DEPLOYMENT/exec
EDGE_FACTORY_RELAY_TOKEN=<same random token>
```

Order matters: the Worker is attempted first and Apps Script second. The daily
workflow already maps both secrets into the pipeline environment. No workflow
change is made for Browser Run until a one-URL smoke test has returned genuine
Forebet content.

## 4. Cloudflare Browser Run: phase-1 diagnostic only

Cloudflare renamed Browser Rendering to **Browser Run** in the current
2026 documentation. This repository uses the documented Workers binding and
Puppeteer-compatible API, not the REST API. The binding avoids putting an
account ID or Browser Rendering API token in the repository or in GitHub
secrets.

The current worker configuration declares:

```toml
[browser]
binding = "BROWSER"
```

The operation is deliberately bounded:

- POST authentication is still required.
- The caller sends only `{"token":"...","operation":"forebet_browser_diagnostic"}`.
- The Worker derives exactly one fixed URL: `https://www.forebet.com/en/football-tips-and-predictions-for-today`.
- Caller URLs, dates, query strings, cookies, headers, scripts, and arbitrary hosts
  are not accepted by this operation.
- It checks `BROWSER.limits()` before acquisition, launches at most one managed
  browser, performs one navigation with a 45-second timeout, and never retries.
- `browser.close()` runs on success and failure.
- A free Workers KV namespace is used as a one-launch-per-UTC-day gate. It is
  intentionally consumed before navigation, so a failed attempt cannot create a
  retry storm. Ordinary relay traffic never reads or writes this namespace.

### One-time Browser Run setup

The browser binding itself needs no API token. From `relay/cloudflare-worker`:

```bash
npm install
npx wrangler login
npx wrangler kv namespace create BROWSER_DIAGNOSTIC_KV
```

Copy the generated namespace ID into `wrangler.toml` by uncommenting and filling
this block; do not commit credentials or account identifiers beyond the generated
binding ID if the operator's deployment convention permits it:

```toml
[[kv_namespaces]]
binding = "BROWSER_DIAGNOSTIC_KV"
id = "<BINDING_ID>"
```

Then deploy the worker with the existing secret:

```bash
npx wrangler secret put RELAY_TOKEN
npx wrangler deploy
```

The free KV namespace is only for the diagnostic gate. Current Cloudflare KV
documentation lists 100,000 reads/day, 1,000 writes/day, 1 GB storage, and
resets at 00:00 UTC on the Workers Free plan. The diagnostic uses at most one
read and one write per attempted day.

### One-URL smoke test

Run this once, manually, against the deployed Worker. Substitute the already
configured relay URL and secret in the shell; never paste either value into
source, logs, or chat:

```bash
curl --fail-with-body -sS -X POST "$WORKER_URL" \
  -H 'content-type: application/json' \
  --data '{"token":"<RELAY_TOKEN>","operation":"forebet_browser_diagnostic"}'
```

The response is a bounded JSON diagnostic, not page HTML. It includes upstream
HTTP status, final URL, content type, response byte count, title, challenge and
CAPTCHA/Turnstile flags, prediction-markup evidence, timeout state, classification,
and launch/navigation counts. It never returns cookies, headers, session IDs, or
complete HTML.

Accept success only when all of these are true:

```text
classification = genuine_forebet_prediction_content
success = true
contains_cloudflare_challenge = false
contains_forebet_prediction_markup = true
final_url has host www.forebet.com
http_status is 2xx
```

This is only a page-access smoke test. It does **not** certify the JSON endpoint,
all three markets, target-date correctness, or production ingestion. Do not add
Browser Run to `forebet.py` or dispatch a heavy workflow until those later phases
have been separately proven.

### Failure signatures and safe interpretation

- `unresolved_cloudflare_challenge`: challenge HTML was returned, including when
  the upstream status is HTTP 200 or HTTP 403.
- `captcha_or_turnstile_required`: the page requires an interaction this route
  does not perform.
- `explicit_access_denial`: a non-challenge denial or access-denied response.
- `navigation_timeout`: navigation exceeded the hard timeout.
- `quota_or_plan_error`: the KV daily claim, Browser Run acquisition limit, or
  free daily browser allowance prevented a run. Do not retry repeatedly; wait for
  the next UTC day after confirming the account's Browser Run usage.
- `browser_rendering_configuration_or_api_error`: missing `BROWSER` binding,
  missing `BROWSER_DIAGNOSTIC_KV`, or a Browser Run binding/API failure.
- `other`: malformed/unexpected content, an unexpected final host, or the bounded
  response-size guard. HTTP 200 alone is never success.

The current diagnostic budget is one launch per UTC day. A claimed day is not
manually retried. If an operator must reset a test claim, use the Cloudflare KV
command with the operator's namespace ID and then perform at most one new smoke
test; do not put that ID or any secret in a commit.

### Verified free limits as of 2026-09-30

Cloudflare's official Browser Run limits page, last updated 2026-09-26, lists
these Workers Free limits:

- 10 minutes of browser time per day;
- three concurrent Browser Sessions per account;
- one new Browser Session every 20 seconds;
- 60 seconds of browser inactivity timeout;
- Quick Actions, if used, are separately limited to one request every 10 seconds.

This implementation uses one Browser Session, not Quick Actions or the REST API,
and its 45-second navigation timeout plus explicit close is below the service
limits. Browser Run is available on Free and Paid plans, but the Workers Paid
plan has a $5/month minimum and usage charges; it is not part of this design.
Workers Free itself includes 100,000 Worker requests/day. These limits are
account-level service limits, so the KV gate is an additional repository-side
safety limit, not a reason to increase them.

Official documentation:

- <https://developers.cloudflare.com/browser-run/get-started/>
- <https://developers.cloudflare.com/browser-run/puppeteer/>
- <https://developers.cloudflare.com/browser-run/reference/wrangler/>
- <https://developers.cloudflare.com/browser-run/limits/>
- <https://developers.cloudflare.com/browser-run/pricing/>
- <https://developers.cloudflare.com/kv/get-started/>
- <https://developers.cloudflare.com/kv/platform/limits/>
- <https://developers.cloudflare.com/kv/platform/pricing/>

## Rollback and temporary diagnostics

To roll back without touching the working ScoutingStats path, remove the
`[browser]` binding and the optional `[[kv_namespaces]]` block from the operator's
Worker configuration, remove the `forebet_browser_diagnostic` branch and its
`browser-diagnostic.js`/Puppeteer package, and redeploy the ordinary relay. The
POST relay contract, exact allowlists, and both Python adapters remain unchanged.
Do not remove `BROWSER` during a live diagnostic request; wait for it to finish.

After a failed smoke test, keep the bounded classification in the operator's
run notes and stop. After a successful page smoke test, the temporary diagnostic
must be retained only while Phase 2 checks the JSON endpoint and the three
markets; it must be removed or replaced by a separately reviewed, bounded
production transport after validation. No diagnostic operation is mapped into
GitHub Actions by this change.

## Existing relay smoke test

After configuring the ordinary relay secrets, dispatch `official_morning` or wait
for the next heavy run. Confirm all of the following rather than trusting a green
workflow:

- `edge_firing_tripwire.json` reports Forebet and ScoutingStats at target date;
- `forebet_YYYY-MM.csv.gz` and `scoutingstats_YYYY-MM.csv.gz` contain target-day rows;
- picks/research rows contain actual named source votes;
- runtime has not returned to the repeated-timeout failure mode.

A relay error must leave the day retryable. It must never be represented as a
valid empty provider payload.
