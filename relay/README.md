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

## 1. Cloudflare Worker (free)

From `relay/cloudflare-worker`:

```bash
npx wrangler login
npx wrangler secret put RELAY_TOKEN
npx wrangler deploy
```

Copy the resulting `https://...workers.dev` URL. Cloudflare may itself be
challenged by Forebet; that is expected and is why Apps Script is independent
fallback number two. It should still be useful for ScoutingStats.

## 2. Google Apps Script web app (free Gmail account)

1. Open <https://script.google.com> and create a project.
2. Paste `google-apps-script/Code.gs` into `Code.gs`.
3. In **Project Settings → Script Properties**, add `RELAY_TOKEN` with the same
   random value used by the Worker.
4. **Deploy → New deployment → Web app**.
5. Execute as **Me**; access **Anyone**.
6. Authorize only external requests and copy the `/exec` URL.

The source contains an `appsscript.json` manifest for users who prefer `clasp`,
but no Google credential belongs in this repository.

## 3. Configure GitHub Actions

Create these repository Actions secrets:

```text
EDGE_FACTORY_RELAY_URLS=https://WORKER.workers.dev,https://script.google.com/macros/s/DEPLOYMENT/exec
EDGE_FACTORY_RELAY_TOKEN=<same random token>
```

Order matters: the Worker is attempted first and Apps Script second. The daily
workflow already maps both secrets into the pipeline environment.

## Smoke test

After configuring secrets, dispatch `official_morning` or wait for the next
heavy run. Confirm all of the following rather than trusting a green workflow:

- `edge_firing_tripwire.json` reports Forebet and ScoutingStats at target date;
- `forebet_YYYY-MM.csv.gz` and `scoutingstats_YYYY-MM.csv.gz` contain target-day rows;
- picks/research rows contain actual named source votes;
- runtime has not returned to the repeated-timeout failure mode.

A relay error must leave the day retryable. It must never be represented as a
valid empty provider payload.
