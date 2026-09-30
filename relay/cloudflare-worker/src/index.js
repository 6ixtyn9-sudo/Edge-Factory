import puppeteer from "@cloudflare/puppeteer";
import {runForebetBrowserDiagnostic} from "./browser-diagnostic.js";
import {allowed, headersFor} from "./allowlist.js";

const MAX_BODY = 12 * 1024 * 1024;
const MAX_REQUEST_BODY = 64 * 1024;

function reply(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {"content-type": "application/json", "cache-control": "no-store"},
  });
}

export default {
  async fetch(request, env) {
    if (request.method !== "POST") return reply({error: "method"}, 405);
    const contentLength = Number(request.headers.get("content-length") || 0);
    if (contentLength > MAX_REQUEST_BODY) return reply({error: "request_too_large"}, 413);

    let input;
    try { input = await request.json(); } catch { return reply({error: "json"}, 400); }
    if (!input || typeof input !== "object" || Array.isArray(input)) {
      return reply({error: "json_shape"}, 400);
    }
    if (!env.RELAY_TOKEN || input.token !== env.RELAY_TOKEN) return reply({error: "auth"}, 403);

    // Phase 1 only: a fixed, authenticated, one-URL Browser Run diagnostic.
    // There is intentionally no caller-provided URL or production adapter path.
    if (input.operation === "forebet_browser_diagnostic") {
      const result = await runForebetBrowserDiagnostic(env, puppeteer);
      return reply(result, result.http_response_status || 200);
    }

    let source;
    try { source = new URL(input.url); } catch { return reply({error: "url"}, 400); }
    if (!allowed(source)) return reply({error: "source_not_allowed"}, 403);

    const headers = headersFor(source);

    try {
      const upstream = await fetch(source.toString(), {headers, redirect: "follow"});
      const body = await upstream.text();
      if (body.length > MAX_BODY) return reply({error: "too_large"}, 502);
      return reply({
        source_url: source.toString(),
        status: upstream.status,
        fetched_at: new Date().toISOString(),
        body,
      }, upstream.ok ? 200 : 502);
    } catch (error) {
      return reply({error: "upstream_fetch", detail: String(error)}, 502);
    }
  },
};
