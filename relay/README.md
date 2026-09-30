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

The commands below are an optional CLI route. A browser-only GitHub/Cloudflare
Dashboard route is documented in section 4 and does not require these commands.

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

Order matters: the Worker is attempted first and Apps Script second. The daily workflow already maps both secrets into the pipeline environment. The
separate `Forebet Browser Run diagnostic` workflow is manual-only, has no schedule,
and never runs the normal pipeline.

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
- After `DOMContentLoaded`, it polls title, URL, and in-memory page markers every
  1.5 seconds while a normal Cloudflare challenge remains transitional. It stops
  immediately on concrete fixture evidence, CAPTCHA/Turnstile, denial, generic
  non-challenge content, or the hard deadline.
- The post-navigation observation window is at most 20 seconds and the overall
  deadline is 55 seconds, below the documented 60-second Browser Run inactivity
  timeout. `browser.close()` runs on success and failure.
- A free Workers KV namespace is used as a best-effort one-launch-per-UTC-day gate.
  The `get` followed by `put` is **not atomic**; this is not described as a lock.
  The diagnostic is authenticated and manual-only, so the operator must invoke it
  once. Ordinary relay traffic never reads or writes this namespace.

### Browser-only deployment through GitHub and Cloudflare dashboards

No terminal, npm, Wrangler, curl, jq, Codespaces, or always-on computer is
required for this route.

#### A. Merge the repository change in GitHub

1. Open the repository on GitHub.
2. Open the pull request for branch `arena/01a0f031-edge-factory`.
3. Review and merge it into the repository's production branch, normally `main`.
4. Do not run the normal daily workflow for this diagnostic.

If the workflow file cannot be pushed by the GitHub App because of missing
`workflows` permission, create `.github/workflows/forebet-browser-diagnostic.yml`
with the version in this commit using GitHub's **Add file → Create new file** web
editor, commit it to the production branch, and then continue. The workflow has
only `workflow_dispatch`, `contents: read`, a three-minute job timeout, one POST,
and no retry or artifact step.

#### B. Connect the existing Worker to Workers Builds

Cloudflare's current dashboard path is:

1. Open **Workers & Pages** and select the existing ordinary relay Worker.
2. Open **Settings → Builds → Connect**.
3. Authorize the public GitHub repository `6ixtyn9-sudo/Edge-Factory`.
4. Select the production branch (`main` after the merge).
5. Set **Root directory** to `relay/cloudflare-worker`.
6. Leave **Build command** blank; `package.json` dependencies are installed for
   the project and no compile step is required.
7. Set **Deploy command** to `npx wrangler deploy`.
8. Save the build settings and use **Deploy** or push the merged commit.

Workers Builds uses the repository's `wrangler.toml`, including the managed
Browser Run binding and `nodejs_compat_v2` flag. The Browser Run binding does not
need an API token. Cloudflare may generate and manage the build authorization
itself; do not paste a Cloudflare API token into the repository or GitHub Actions.

Official dashboard documentation:

- <https://developers.cloudflare.com/workers/ci-cd/builds/>
- <https://developers.cloudflare.com/workers/ci-cd/builds/git-integration/>
- <https://developers.cloudflare.com/workers/ci-cd/builds/configuration/>

#### C. Create and bind the free KV namespace in Cloudflare

1. In Cloudflare, open **Workers & Pages → KV**.
2. Select **Create namespace** and name it something like
   `edge-factory-browser-diagnostic`.
3. Open the relay Worker and go to **Settings → Variables and Secrets** or
   **Bindings**.
4. Add a **KV namespace binding** with variable name exactly
   `BROWSER_DIAGNOSTIC_KV`.
5. Select the namespace created above and save/deploy the binding.
6. Confirm the Worker also has the Browser Run binding named exactly `BROWSER`.
   It is declared in `wrangler.toml`; if the dashboard presents it under
   **Bindings**, add/select the managed Browser Run binding with that name.

If Workers Builds requires all bindings to be present in the Wrangler file, use
GitHub's web editor to uncomment the existing `[[kv_namespaces]]` block in
`relay/cloudflare-worker/wrangler.toml` and enter only the KV namespace ID shown
by the Cloudflare dashboard. This ID is not a secret, but do not paste account
IDs or tokens into source.

#### D. Preserve the existing relay secret

In the Worker dashboard's **Settings → Variables and Secrets**, confirm the
encrypted secret named `RELAY_TOKEN` still exists. If it does not, add the same
value already used by the existing relay. Do not reveal it in an issue, pull
request, workflow input, URL, or chat.

In the GitHub repository, confirm these existing encrypted Actions secrets are
present under **Settings → Secrets and variables → Actions**:

- `EDGE_FACTORY_RELAY_URLS`, with the Cloudflare Worker URL first;
- `EDGE_FACTORY_RELAY_TOKEN`, with the same relay token.

The diagnostic workflow reads these secrets only at runtime. It does not print
them, construct a URL containing the token, upload artifacts, or dump its
environment. ScoutingStats continues to use the ordinary relay path.

The free KV namespace is only for the diagnostic gate. Current Cloudflare KV
documentation lists 100,000 reads/day, 1,000 writes/day, 1 GB storage, and
resets at 00:00 UTC on the Workers Free plan. The diagnostic uses at most one
read and one write per attempted day. The get-then-put gate is not atomic, so
invoke the workflow only once and treat the Browser Run account limit as the
final quota backstop.

### One-URL smoke test without a terminal

Use the GitHub web UI rather than a third-party request tester:

1. Open the repository's **Actions** tab.
2. Select **Forebet Browser Run diagnostic**.
3. Select **Run workflow** on the production branch.
4. Do not enter any token or URL as an input; this workflow has no inputs.
5. Open the single job and read its one bounded JSON diagnostic output.
6. Do not click **Run workflow** a second time on the same UTC day, including after
   a configuration failure. Configuration checks now happen before the KV claim,
   but a launch or navigation failure consumes the attempt deliberately.

The workflow uses Python's standard library on the hosted runner. It performs
exactly one POST, has a 75-second HTTP timeout and a three-minute job timeout, and
never uses curl, jq, npm, Wrangler, a shell-expanded token, or an artifact. The
secret remains in the runner process environment and is never printed.

The response is a bounded JSON diagnostic, not page HTML. It includes upstream
HTTP status, final URL, content type, response byte count, title, challenge and
CAPTCHA/Turnstile flags, generic/candidate/concrete fixture evidence, observation
count and elapsed time, timeout state, classification, and launch/navigation counts.
It never returns cookies, headers, session IDs, or complete HTML.

Accept success only when all of these are true:

```text
classification = genuine_forebet_prediction_content
success = true
contains_cloudflare_challenge = false
contains_forebet_prediction_markup = true
candidate_prediction_content = true
concrete_fixture_row_evidence = true
final_url has host www.forebet.com
http_status is 2xx
observation_deadline_exceeded = false
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
- `unresolved_cloudflare_challenge` with `observation_deadline_exceeded=true`:
  the challenge remained after the bounded post-navigation observation window.
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

### npm advisory audit for the pinned Puppeteer dependency

As of 2026-09-30, `npm audit --omit=dev --json` reports three high-severity
findings in the install dependency graph:

- Direct package: `@cloudflare/puppeteer@1.4.0`.
- Dependency path:
  `@cloudflare/puppeteer@1.4.0 → @puppeteer/browsers@2.2.4 → extract-zip@2.0.1`.
- `extract-zip` advisories:
  - `GHSA-jmr9-qjv8-65gv`, unvalidated symlink path traversal;
  - `GHSA-7pqw-9j4j-h8q3`, arbitrary file writes through symlink archive entries.

The flagged code belongs to Puppeteer's Node browser-download/archive path. The
Cloudflare package's Worker entry point imports `PuppeteerWorkers`, not the Node
launcher modules that use `@puppeteer/browsers`; the Wrangler dry-run bundle was
checked and contains no `extract-zip` or `@puppeteer/browsers` code. This is still
an install/build audit finding and should be monitored, but it is not an observed
runtime path for this Worker. Do not run `npm audit fix --force`: that would change
the Cloudflare-supported package graph without a tested compatible release.

`npm view @cloudflare/puppeteer` currently reports `1.4.0` as the latest release;
no newer compatible Cloudflare package was available during this review. Recheck
before any future dependency update.

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
production transport after validation. The manual diagnostic workflow may remain
as an operator tool, but it must not be scheduled or connected to the normal
pipeline.

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
