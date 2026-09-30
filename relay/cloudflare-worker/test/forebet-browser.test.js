import assert from "node:assert/strict";
import test from "node:test";

import {FOREBET_GETRS_OPERATION, FOREBET_GETRS_TRANSPORT, runForebetGetrsBrowser} from "../src/forebet-browser.js";

const SOURCE = "https://www.forebet.com/scripts/getrs.php?ln=en&tp=1x2&in=2026-09-30&ord=0&tz=0&tzs=&tze=&output=1";
const BODY = JSON.stringify([[{id: "1", HOST_NAME: "Alpha", GUEST_NAME: "Beta"}], {ok: true}]);

function env(limits = {allowedBrowserAcquisitions: 1, activeSessions: [], maxConcurrentSessions: 3}) {
  return {
    BROWSER: {
      async limits() {
        return limits;
      },
    },
  };
}

function browserClient({body = BODY, status = 200, events = []} = {}) {
  return {
    async launch(binding) {
      assert.ok(binding);
      events.push("launch");
      return {
        async newPage() {
          events.push("newPage");
          return {
            timeout: null,
            headers: null,
            ua: null,
            setDefaultNavigationTimeout(value) {
              this.timeout = value;
            },
            async setUserAgent(value) {
              this.ua = value;
              events.push("ua");
            },
            async setExtraHTTPHeaders(value) {
              this.headers = value;
              events.push("headers");
            },
            async goto(url, options) {
              assert.equal(url, SOURCE);
              assert.equal(options.waitUntil, "domcontentloaded");
              assert.equal(options.timeout, 45_000);
              events.push("goto");
              return {
                status: () => status,
                headers: () => ({"content-type": "application/json"}),
              };
            },
            async evaluate(fn) {
              events.push("evaluate");
              return body;
            },
          };
        },
        async close() {
          events.push("close");
        },
      };
    },
  };
}

test("forebet browser operation markers are stable", () => {
  assert.equal(FOREBET_GETRS_OPERATION, "forebet_getrs");
  assert.equal(FOREBET_GETRS_TRANSPORT, "cloudflare_browser_rendering");
});

test("browser getrs operation validates exact source and returns relay contract", async () => {
  const events = [];
  const result = await runForebetGetrsBrowser(env(), browserClient({events}), {url: SOURCE});

  assert.equal(result.httpResponseStatus, 200);
  assert.equal(result.payload.operation, FOREBET_GETRS_OPERATION);
  assert.equal(result.payload.transport, FOREBET_GETRS_TRANSPORT);
  assert.equal(result.payload.source_url, SOURCE);
  assert.equal(result.payload.status, 200);
  assert.equal(result.payload.body_shape, "forebet_getrs");
  assert.equal(result.payload.row_count, 1);
  assert.equal(result.payload.body, BODY);
  assert.match(result.payload.fetched_at, /^\d{4}-\d{2}-\d{2}T/);
  assert.deepEqual(events, ["launch", "newPage", "ua", "headers", "goto", "evaluate", "close"]);
});

test("browser getrs operation refuses non-allowlisted urls before launch", async () => {
  const events = [];
  const result = await runForebetGetrsBrowser(
    env(),
    browserClient({events}),
    {url: "https://www.forebet.com/en/football-tips-and-predictions-for-today"},
  );

  assert.equal(result.httpResponseStatus, 403);
  assert.deepEqual(result.payload, {
    operation: FOREBET_GETRS_OPERATION,
    transport: FOREBET_GETRS_TRANSPORT,
    error: "source_not_allowed",
  });
  assert.deepEqual(events, []);
});

test("browser getrs operation rejects challenge html shape and closes browser", async () => {
  const events = [];
  const result = await runForebetGetrsBrowser(
    env(),
    browserClient({events, body: "<html>Just a moment</html>"}),
    {url: SOURCE},
  );

  assert.equal(result.httpResponseStatus, 502);
  assert.equal(result.payload.operation, FOREBET_GETRS_OPERATION);
  assert.equal(result.payload.transport, FOREBET_GETRS_TRANSPORT);
  assert.equal(result.payload.error, "browser_response_not_forebet_getrs_json");
  assert.equal(result.payload.body_shape, "non_json_body");
  assert.equal(result.payload.source_url, SOURCE);
  assert.ok(events.includes("close"));
});

test("browser getrs operation respects binding limits", async () => {
  const result = await runForebetGetrsBrowser(
    env({allowedBrowserAcquisitions: 0, activeSessions: [], maxConcurrentSessions: 3}),
    browserClient(),
    {url: SOURCE},
  );

  assert.equal(result.httpResponseStatus, 429);
  assert.deepEqual(result.payload, {
    operation: FOREBET_GETRS_OPERATION,
    transport: FOREBET_GETRS_TRANSPORT,
    error: "browser_quota_exhausted",
  });
});

test("browser getrs operation identifies itself on binding errors", async () => {
  const result = await runForebetGetrsBrowser({}, browserClient(), {url: SOURCE});

  assert.equal(result.httpResponseStatus, 503);
  assert.deepEqual(result.payload, {
    operation: FOREBET_GETRS_OPERATION,
    transport: FOREBET_GETRS_TRANSPORT,
    error: "missing_browser_binding",
  });
});
