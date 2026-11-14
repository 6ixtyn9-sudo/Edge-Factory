import {allowedForebetGetrs, headersFor, BROWSER_UA} from "./allowlist.js";

export const FOREBET_GETRS_OPERATION = "forebet_getrs";
export const FOREBET_GETRS_TRANSPORT = "cloudflare_browser_rendering";
export const FOREBET_BROWSER_TIMEOUT_MS = 45_000;
export const FOREBET_BROWSER_MAX_BODY = 12 * 1024 * 1024;

function byteLength(text) {
  return new TextEncoder().encode(String(text || "")).byteLength;
}

function truncate(value, limit = 240) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  return text.length > limit ? `${text.slice(0, limit - 1)}…` : text;
}

function responseHeader(response, name) {
  if (!response) return null;
  const headers = typeof response.headers === "function" ? response.headers() : response.headers;
  if (!headers) return null;
  if (typeof headers.get === "function") return headers.get(name);
  const wanted = name.toLowerCase();
  const key = Object.keys(headers).find((candidate) => candidate.toLowerCase() === wanted);
  return key ? String(headers[key]) : null;
}

function responseStatus(response) {
  const status = typeof response?.status === "function" ? response.status() : response?.status;
  return Number.isFinite(Number(status)) ? Number(status) : 0;
}

function safeError(error) {
  return truncate(
    String(error?.message || error || "unknown error")
      .replace(/https?:\/\/\S+/gi, "<url>")
      .replace(/bearer\s+\S+/gi, "Bearer <redacted>")
      .replace(/[0-9a-f]{8}-[0-9a-f-]{27,}/gi, "<id>")
      .replace(/\b[0-9a-f]{32,}\b/gi, "<id>"),
  );
}

function basePayload(fields = {}) {
  return {
    operation: FOREBET_GETRS_OPERATION,
    transport: FOREBET_GETRS_TRANSPORT,
    ...fields,
  };
}

function inspectJsonBody(body) {
  let parsed;
  try {
    parsed = JSON.parse(body);
  } catch {
    return {ok: false, body_shape: "non_json_body"};
  }
  if (!Array.isArray(parsed) || !Array.isArray(parsed[0])) {
    return {ok: false, body_shape: "unexpected_json_shape"};
  }
  return {ok: true, body_shape: "forebet_getrs", row_count: parsed[0].length};
}

async function extractBodyText(page) {
  if (typeof page?.evaluate === "function") {
    return await page.evaluate(() => {
      const body = document.body;
      if (body && typeof body.innerText === "string") return body.innerText;
      const root = document.documentElement;
      return root && typeof root.innerText === "string" ? root.innerText : "";
    });
  }
  if (typeof page?.content === "function") return await page.content();
  return "";
}

export async function runForebetGetrsBrowser(env, browserClient, input = {}) {
  let source;
  try {
    source = new URL(input.url);
  } catch {
    return {payload: basePayload({error: "url"}), httpResponseStatus: 400};
  }
  if (!allowedForebetGetrs(source)) {
    return {payload: basePayload({error: "source_not_allowed"}), httpResponseStatus: 403};
  }
  if (!env?.BROWSER) {
    return {payload: basePayload({error: "missing_browser_binding"}), httpResponseStatus: 503};
  }

  try {
    if (typeof env.BROWSER.limits === "function") {
      const limits = await env.BROWSER.limits();
      const active = Array.isArray(limits?.activeSessions) ? limits.activeSessions.length : 0;
      const maximum = Number(limits?.maxConcurrentSessions);
      if (limits?.allowedBrowserAcquisitions === 0 || (maximum > 0 && active >= maximum)) {
        return {payload: basePayload({error: "browser_quota_exhausted"}), httpResponseStatus: 429};
      }
    }
  } catch (error) {
    return {
      payload: basePayload({error: "browser_limits", detail: safeError(error)}),
      httpResponseStatus: 503,
    };
  }

  let browser = null;
  try {
    browser = await browserClient.launch(env.BROWSER);
    const page = await browser.newPage();
    if (typeof page.setDefaultNavigationTimeout === "function") {
      page.setDefaultNavigationTimeout(FOREBET_BROWSER_TIMEOUT_MS);
    }
    if (typeof page.setUserAgent === "function") {
      await page.setUserAgent(BROWSER_UA);
    }
    if (typeof page.setExtraHTTPHeaders === "function") {
      const extraHeaders = {...headersFor(source)};
      delete extraHeaders["user-agent"];
      await page.setExtraHTTPHeaders(extraHeaders);
    }

    const response = await page.goto(source.toString(), {
      waitUntil: "domcontentloaded",
      timeout: FOREBET_BROWSER_TIMEOUT_MS,
    });
    const status = responseStatus(response);
    const body = String(await extractBodyText(page) || "").trim();
    const fetchedAt = new Date().toISOString();
    if (byteLength(body) > FOREBET_BROWSER_MAX_BODY) {
      return {
        payload: basePayload({
          error: "too_large",
          source_url: source.toString(),
          status,
          fetched_at: fetchedAt,
        }),
        httpResponseStatus: 502,
      };
    }
    // Keep the relay honest: a solved browser run must expose the JSON endpoint
    // body, not challenge HTML rendered inside a 200 page. The failure envelope
    // is deliberately metadata-only so logs can distinguish a deployed Browser
    // Run operation from the legacy generic relay without leaking challenge HTML.
    const inspected = inspectJsonBody(body);
    if (!inspected.ok) {
      return {
        payload: basePayload({
          error: "browser_response_not_forebet_getrs_json",
          source_url: source.toString(),
          status,
          content_type: responseHeader(response, "content-type"),
          body_shape: inspected.body_shape,
          fetched_at: fetchedAt,
        }),
        httpResponseStatus: 502,
      };
    }
    return {
      payload: basePayload({
        source_url: source.toString(),
        status,
        fetched_at: fetchedAt,
        body_shape: inspected.body_shape,
        row_count: inspected.row_count,
        body,
      }),
      httpResponseStatus: status >= 200 && status < 300 ? 200 : 502,
    };
  } catch (error) {
    return {
      payload: basePayload({
        error: "browser_fetch",
        detail: safeError(error),
        source_url: source.toString(),
      }),
      httpResponseStatus: 502,
    };
  } finally {
    if (browser && typeof browser.close === "function") {
      try { await browser.close(); } catch {}
    }
  }
}
