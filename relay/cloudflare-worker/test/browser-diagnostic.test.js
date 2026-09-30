import assert from "node:assert/strict";
import test from "node:test";

import {
  BROWSER_BUDGET_KEY_PREFIX,
  CLASSIFICATIONS,
  FOREBET_DIAGNOSTIC_URL,
  MAX_DIAGNOSTIC_HTML_BYTES,
  claimDailyBrowserBudget,
  classifyRenderedForebet,
  runForebetBrowserDiagnostic,
} from "../src/browser-diagnostic.js";

const FOREBET_HTML = `
  <html><head><title>Today | Forebet</title></head>
  <body><h1>Today | 1X2 Predictions</h1>
  <div>Home team Away team Prob. % Prediction Correct score</div>
  <div>Alpha Beta 30/09/2026 20:00 55 25 20</div></body></html>
`;

const CHALLENGE_HTML = `
  <html><head><title>Just a moment...</title></head>
  <body><div id="challenge-platform">Checking your browser before accessing Forebet.</div></body></html>
`;

function makeKv({existing = null, fail = null} = {}) {
  const calls = [];
  return {
    calls,
    async get(key) {
      calls.push(["get", key]);
      if (fail) throw fail;
      return existing;
    },
    async put(key, value, options) {
      calls.push(["put", key, value, options]);
      if (fail) throw fail;
    },
  };
}

function makeEnv({kv = makeKv(), limits = {allowedBrowserAcquisitions: 1, activeSessions: [], maxConcurrentSessions: 3}} = {}) {
  return {
    BROWSER_DIAGNOSTIC_KV: kv,
    BROWSER: {
      async limits() {
        if (limits instanceof Error) throw limits;
        return limits;
      },
    },
  };
}

function makePage({body = FOREBET_HTML, status = 200, contentType = "text/html; charset=utf-8", finalUrl = FOREBET_DIAGNOSTIC_URL, title = "Today | Forebet"} = {}) {
  return {
    timeout: null,
    setDefaultNavigationTimeout(value) {
      this.timeout = value;
    },
    async goto(url, options) {
      assert.equal(url, FOREBET_DIAGNOSTIC_URL);
      assert.equal(options.waitUntil, "domcontentloaded");
      assert.equal(options.timeout, 45_000);
      return {
        status: () => status,
        headers: () => ({"content-type": contentType}),
      };
    },
    async content() {
      return body;
    },
    async url() {
      return finalUrl;
    },
    async title() {
      return title;
    },
  };
}

function makeBrowser(page, events) {
  return {
    async newPage() {
      events.push("newPage");
      return page;
    },
    async close() {
      events.push("close");
    },
  };
}

test("classifies genuine rendered Forebet prediction content", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    contentType: "text/html",
    finalUrl: FOREBET_DIAGNOSTIC_URL,
    body: FOREBET_HTML,
  });
  assert.equal(result.classification, CLASSIFICATIONS.CONTENT);
  assert.equal(result.success, true);
  assert.equal(result.contains_forebet_prediction_markup, true);
  assert.equal(result.response_bytes > 0, true);
});

test("classifies challenge HTML returned with HTTP 200", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    contentType: "text/html",
    finalUrl: FOREBET_DIAGNOSTIC_URL,
    body: CHALLENGE_HTML,
  });
  assert.equal(result.classification, CLASSIFICATIONS.CHALLENGE);
  assert.equal(result.contains_cloudflare_challenge, true);
});

test("classifies challenge HTML returned with HTTP 403", () => {
  const result = classifyRenderedForebet({
    httpStatus: 403,
    contentType: "text/html",
    finalUrl: FOREBET_DIAGNOSTIC_URL,
    body: CHALLENGE_HTML,
  });
  assert.equal(result.classification, CLASSIFICATIONS.CHALLENGE);
  assert.equal(result.http_status, 403);
});

test("classifies CAPTCHA or Turnstile before generic denial", () => {
  const result = classifyRenderedForebet({
    httpStatus: 403,
    body: "<html><title>Verify you are human</title><div>Turnstile</div></html>",
  });
  assert.equal(result.classification, CLASSIFICATIONS.CAPTCHA);
  assert.equal(result.captcha_or_turnstile, true);
});

test("classifies explicit access denial without challenge markers", () => {
  const result = classifyRenderedForebet({
    httpStatus: 403,
    body: "<html><title>Access denied</title><p>Error 1020</p></html>",
  });
  assert.equal(result.classification, CLASSIFICATIONS.ACCESS_DENIED);
  assert.equal(result.access_denied, true);
});

test("classifies response-size overflow without accepting the page", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    body: FOREBET_HTML,
    responseSizeOverflow: true,
  });
  assert.equal(result.classification, CLASSIFICATIONS.OTHER);
  assert.equal(result.response_size_overflow, true);
  assert.equal(result.success, false);
  assert.ok(MAX_DIAGNOSTIC_HTML_BYTES > 0);
});

test("uses one launch and closes the managed browser after genuine content", async () => {
  const kv = makeKv();
  const events = [];
  const page = makePage();
  const env = makeEnv({kv});
  const result = await runForebetBrowserDiagnostic(
    env,
    {launch: async binding => {
      assert.equal(binding, env.BROWSER);
      events.push("launch");
      return makeBrowser(page, events);
    }},
    {now: new Date("2026-09-30T08:00:00Z")},
  );

  assert.equal(result.classification, CLASSIFICATIONS.CONTENT);
  assert.equal(result.browser_launch_attempts, 1);
  assert.equal(result.browser_launches, 1);
  assert.equal(result.navigation_attempts, 1);
  assert.equal(result.page_title, "Today | Forebet");
  assert.deepEqual(events, ["launch", "newPage", "close"]);
  assert.equal(kv.calls[0][0], "get");
  assert.equal(kv.calls[1][0], "put");
});

test("closes the managed browser when navigation times out and does not retry", async () => {
  const events = [];
  const page = {
    setDefaultNavigationTimeout() {},
    async goto() {
      const error = new Error("Navigation timeout of 45000 ms exceeded");
      error.name = "TimeoutError";
      throw error;
    },
  };
  const env = makeEnv();
  const result = await runForebetBrowserDiagnostic(
    env,
    {launch: async () => {
      events.push("launch");
      return makeBrowser(page, events);
    }},
    {now: new Date("2026-09-30T08:00:00Z")},
  );

  assert.equal(result.classification, CLASSIFICATIONS.TIMEOUT);
  assert.equal(result.navigation_timed_out, true);
  assert.equal(result.navigation_attempts, 1);
  assert.deepEqual(events, ["launch", "newPage", "close"]);
});

test("reports missing Browser Run binding without touching the budget", async () => {
  const kv = makeKv();
  const result = await runForebetBrowserDiagnostic(
    {BROWSER_DIAGNOSTIC_KV: kv},
    {launch: async () => { throw new Error("must not launch"); }},
  );
  assert.equal(result.classification, CLASSIFICATIONS.CONFIGURATION);
  assert.equal(result.error_code, "missing_browser_binding");
  assert.equal(kv.calls.length, 0);
});

test("reports missing daily budget binding without launching", async () => {
  const result = await runForebetBrowserDiagnostic(
    {BROWSER: {limits: async () => ({allowedBrowserAcquisitions: 1})}},
    {launch: async () => { throw new Error("must not launch"); }},
  );
  assert.equal(result.classification, CLASSIFICATIONS.CONFIGURATION);
  assert.equal(result.error_code, "missing_daily_budget_binding");
});

test("reports Browser Run API/configuration failures", async () => {
  const result = await runForebetBrowserDiagnostic(
    makeEnv({limits: Object.assign(new Error("binding API unavailable"), {status: 500})}),
    {launch: async () => { throw new Error("must not launch"); }},
  );
  assert.equal(result.classification, CLASSIFICATIONS.CONFIGURATION);
  assert.equal(result.http_response_status, 503);
  assert.equal(result.browser_launch_attempts, 0);
});

test("reports quota exhaustion before launching Chromium", async () => {
  const result = await runForebetBrowserDiagnostic(
    makeEnv({limits: {allowedBrowserAcquisitions: 0, activeSessions: [], maxConcurrentSessions: 3}}),
    {launch: async () => { throw new Error("must not launch"); }},
  );
  assert.equal(result.classification, CLASSIFICATIONS.QUOTA);
  assert.equal(result.http_response_status, 429);
  assert.equal(result.browser_launch_attempts, 0);
});

test("enforces one diagnostic budget claim per UTC day", async () => {
  const kv = makeKv({existing: "claimed"});
  const result = await claimDailyBrowserBudget(kv, new Date("2026-09-30T23:59:59Z"));
  assert.equal(result.allowed, false);
  assert.equal(result.key, `${BROWSER_BUDGET_KEY_PREFIX}:2026-09-30`);
  assert.equal(kv.calls.length, 1);
});

test("reports a previously claimed daily browser budget", async () => {
  const result = await runForebetBrowserDiagnostic(
    makeEnv({kv: makeKv({existing: "claimed"})}),
    {launch: async () => { throw new Error("must not launch"); }},
    {now: new Date("2026-09-30T08:00:00Z")},
  );
  assert.equal(result.classification, CLASSIFICATIONS.QUOTA);
  assert.equal(result.budget_exhausted, true);
  assert.equal(result.browser_launches, 0);
});

test("does not accept a page from an unexpected final host", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    finalUrl: "https://example.com/redirected",
    body: FOREBET_HTML,
  });
  assert.equal(result.classification, CLASSIFICATIONS.OTHER);
  assert.equal(result.contains_forebet_prediction_markup, true);
  assert.equal(result.success, false);
});
