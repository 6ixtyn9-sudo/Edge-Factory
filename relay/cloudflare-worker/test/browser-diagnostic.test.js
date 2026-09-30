import assert from "node:assert/strict";
import test from "node:test";

import {
  BROWSER_BUDGET_KEY_PREFIX,
  CLASSIFICATIONS,
  FOREBET_DIAGNOSTIC_URL,
  MAX_DIAGNOSTIC_HTML_BYTES,
  claimDailyBrowserBudget,
  classifyRenderedForebet,
  inspectPageDom,
  observeForebetPage,
  runForebetBrowserDiagnostic,
} from "../src/browser-diagnostic.js";

const FOREBET_HTML = `
  <html><head><title>Today | Forebet</title></head>
  <body><h1>Today | 1X2 Predictions</h1>
  <div>Home team Away team Prob. % Prediction Correct score</div>
  <div>Alpha Beta 30/09/2026 20:00 55 25 20 1 - 0</div></body></html>
`;

const CHALLENGE_HTML = `
  <html><head><title>Just a moment...</title></head>
  <body><div id="challenge-platform">Checking your browser before accessing Forebet.</div></body></html>
`;

const CHALLENGE_WITH_TURNSTILE_SCRIPT_HTML = `
  <html><head><title>Just a moment...</title>
  <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback" async defer></script>
  </head>
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

function makeEnv({
  kv = makeKv(),
  limits = {allowedBrowserAcquisitions: 1, activeSessions: [], maxConcurrentSessions: 3},
} = {}) {
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

function makePage({
  body = FOREBET_HTML,
  status = 200,
  contentType = "text/html; charset=utf-8",
  finalUrl = FOREBET_DIAGNOSTIC_URL,
  title = "Today | Forebet",
  domState = {
    visible_turnstile_widget: false,
    visible_turnstile_categories: [],
    visible_human_verification_text: false,
    visible_human_verification_markers: [],
  },
  evaluateError = null,
} = {}) {
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
    async evaluate(fn) {
      if (evaluateError) throw evaluateError;
      return domState;
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

function observationResponse(status = 200) {
  return {
    status: () => status,
    headers: () => ({"content-type": "text/html; charset=utf-8"}),
  };
}

function pollingPage(ticks) {
  let index = 0;
  return {
    async url() {
      return FOREBET_DIAGNOSTIC_URL;
    },
    async title() {
      const tick = ticks[Math.min(index, ticks.length - 1)];
      if (typeof tick === "object" && tick.title) return tick.title;
      return index < ticks.length - 1 ? "Just a moment..." : "Today | Forebet";
    },
    async content() {
      const tick = ticks[Math.min(index, ticks.length - 1)];
      return typeof tick === "string" ? tick : tick.body;
    },
    async evaluate(fn) {
      const currentTick = ticks[Math.min(index, ticks.length - 1)];
      index += 1;
      if (typeof currentTick === "object") {
        if (currentTick.evaluateError) throw currentTick.evaluateError;
        if (currentTick.domState) return currentTick.domState;
      }
      return {
        visible_turnstile_widget: false,
        visible_turnstile_categories: [],
        visible_human_verification_text: false,
        visible_human_verification_markers: [],
      };
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
  assert.equal(result.candidate_prediction_content, true);
  assert.equal(result.concrete_fixture_row_evidence, true);
  assert.equal(result.response_bytes > 0, true);
  assert.equal(result.turnstile_source_marker, false);
  assert.equal(result.visible_turnstile_widget, false);
  assert.equal(result.visible_human_verification_text, false);
  assert.equal(result.interactive_human_verification_required, false);
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
  assert.equal(result.turnstile_source_marker, false);
  assert.equal(result.interactive_human_verification_required, false);
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

test("source-only Turnstile text does not classify as CAPTCHA from HTML alone", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    contentType: "text/html",
    finalUrl: FOREBET_DIAGNOSTIC_URL,
    body: CHALLENGE_WITH_TURNSTILE_SCRIPT_HTML,
    visibleTurnstileWidget: false,
    visibleHumanVerificationText: false,
  });
  assert.equal(result.classification, CLASSIFICATIONS.CHALLENGE);
  assert.equal(result.turnstile_source_marker, true);
  assert.deepEqual(result.turnstile_source_markers, ["turnstile", "challenge_script"]);
  assert.equal(result.visible_turnstile_widget, false);
  assert.equal(result.visible_human_verification_text, false);
  assert.equal(result.interactive_human_verification_required, false);
  assert.equal(result.captcha_or_turnstile, false);
});

test("visible Turnstile iframe classifies as captcha_or_turnstile_required", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    body: CHALLENGE_WITH_TURNSTILE_SCRIPT_HTML,
    visibleTurnstileWidget: true,
    visibleTurnstileCategories: ["turnstile_iframe"],
    visibleHumanVerificationText: false,
  });
  assert.equal(result.classification, CLASSIFICATIONS.CAPTCHA);
  assert.equal(result.turnstile_source_marker, true);
  assert.equal(result.visible_turnstile_widget, true);
  assert.deepEqual(result.visible_turnstile_categories, ["turnstile_iframe"]);
  assert.equal(result.interactive_human_verification_required, true);
  assert.equal(result.captcha_or_turnstile, true);
});

test("visible Turnstile container classifies as captcha_or_turnstile_required", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    body: CHALLENGE_HTML,
    visibleTurnstileWidget: true,
    visibleTurnstileCategories: ["turnstile_container"],
    visibleHumanVerificationText: false,
  });
  assert.equal(result.classification, CLASSIFICATIONS.CAPTCHA);
  assert.equal(result.visible_turnstile_widget, true);
  assert.deepEqual(result.visible_turnstile_categories, ["turnstile_container"]);
  assert.equal(result.interactive_human_verification_required, true);
});

test("visible [data-sitekey] container classifies as captcha_or_turnstile_required", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    body: CHALLENGE_HTML,
    visibleTurnstileWidget: true,
    visibleTurnstileCategories: ["sitekey_container"],
    visibleHumanVerificationText: false,
  });
  assert.equal(result.classification, CLASSIFICATIONS.CAPTCHA);
  assert.equal(result.visible_turnstile_widget, true);
  assert.deepEqual(result.visible_turnstile_categories, ["sitekey_container"]);
  assert.equal(result.interactive_human_verification_required, true);
});

test("hidden Turnstile candidate does not trigger CAPTCHA classification", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    body: CHALLENGE_WITH_TURNSTILE_SCRIPT_HTML,
    visibleTurnstileWidget: false,
    visibleTurnstileCategories: [],
    visibleHumanVerificationText: false,
  });
  assert.equal(result.classification, CLASSIFICATIONS.CHALLENGE);
  assert.equal(result.visible_turnstile_widget, false);
  assert.equal(result.interactive_human_verification_required, false);
});

test("generic visible challenge iframe is not treated as interactive Turnstile", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    body: CHALLENGE_HTML,
    visibleTurnstileWidget: false,
    visibleTurnstileCategories: [],
    visibleHumanVerificationText: false,
  });
  assert.equal(result.classification, CLASSIFICATIONS.CHALLENGE);
  assert.equal(result.visible_turnstile_widget, false);
  assert.equal(result.interactive_human_verification_required, false);
});

test("visible 'Verify you are human' text in rendered innerText classifies as CAPTCHA", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    body: CHALLENGE_HTML,
    visibleTurnstileWidget: false,
    visibleHumanVerificationText: true,
    visibleHumanVerificationMarkers: ["verify_you_are_human"],
  });
  assert.equal(result.classification, CLASSIFICATIONS.CAPTCHA);
  assert.equal(result.visible_human_verification_text, true);
  assert.deepEqual(result.visible_human_verification_markers, ["verify_you_are_human"]);
  assert.equal(result.interactive_human_verification_required, true);
  assert.equal(result.captcha_or_turnstile, true);
});

test("visible 'Complete the security check' text classifies as CAPTCHA", () => {
  const result = classifyRenderedForebet({
    httpStatus: 200,
    body: CHALLENGE_HTML,
    visibleTurnstileWidget: false,
    visibleHumanVerificationText: true,
    visibleHumanVerificationMarkers: ["complete_the_security_check"],
  });
  assert.equal(result.classification, CLASSIFICATIONS.CAPTCHA);
  assert.equal(result.visible_human_verification_text, true);
  assert.equal(result.interactive_human_verification_required, true);
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

test("waits for a transitional challenge to become concrete Forebet content (concrete resolution)", async () => {
  let clock = 0;
  const sleeps = [];
  const result = await observeForebetPage(pollingPage([
    CHALLENGE_HTML,
    CHALLENGE_HTML,
    FOREBET_HTML,
  ]), {
    initialResponse: observationResponse(),
    deadlineAt: 5_000,
    startedAt: 0,
    now: () => clock,
    sleep: async milliseconds => {
      sleeps.push(milliseconds);
      clock += milliseconds;
    },
  });

  assert.equal(result.classification, CLASSIFICATIONS.CONTENT);
  assert.equal(result.observation_count, 3);
  assert.equal(result.observation_deadline_exceeded, false);
  assert.equal(result.success, true);
  assert.deepEqual(sleeps, [1_500, 1_500]);
});

test("source-only Turnstile marker followed by concrete content continues observation and succeeds", async () => {
  let clock = 0;
  const sleeps = [];
  const result = await observeForebetPage(pollingPage([
    {
      body: CHALLENGE_WITH_TURNSTILE_SCRIPT_HTML,
      domState: {
        visible_turnstile_widget: false,
        visible_turnstile_categories: [],
        visible_human_verification_text: false,
        visible_human_verification_markers: [],
      },
    },
    {
      body: FOREBET_HTML,
      domState: {
        visible_turnstile_widget: false,
        visible_turnstile_categories: [],
        visible_human_verification_text: false,
        visible_human_verification_markers: [],
      },
    },
  ]), {
    initialResponse: observationResponse(),
    deadlineAt: 5_000,
    startedAt: 0,
    now: () => clock,
    sleep: async milliseconds => {
      sleeps.push(milliseconds);
      clock += milliseconds;
    },
  });

  assert.equal(result.classification, CLASSIFICATIONS.CONTENT);
  assert.equal(result.success, true);
  assert.equal(result.observation_count, 2);
  assert.equal(result.observation_deadline_exceeded, false);
  assert.deepEqual(sleeps, [1_500]);
});

test("source-only Turnstile marker remaining until observation deadline reports unresolved challenge", async () => {
  let clock = 0;
  const result = await observeForebetPage(pollingPage([
    {
      body: CHALLENGE_WITH_TURNSTILE_SCRIPT_HTML,
      domState: {
        visible_turnstile_widget: false,
        visible_turnstile_categories: [],
        visible_human_verification_text: false,
        visible_human_verification_markers: [],
      },
    },
  ]), {
    initialResponse: observationResponse(),
    deadlineAt: 3_000,
    startedAt: 0,
    now: () => clock,
    sleep: async milliseconds => {
      clock += milliseconds;
    },
  });

  assert.equal(result.classification, CLASSIFICATIONS.CHALLENGE);
  assert.equal(result.turnstile_source_marker, true);
  assert.equal(result.visible_turnstile_widget, false);
  assert.equal(result.visible_human_verification_text, false);
  assert.equal(result.interactive_human_verification_required, false);
  assert.equal(result.observation_deadline_exceeded, true);
  assert.equal(result.observation_count, 3);
});

test("stops immediately on visible Turnstile widget", async () => {
  let sleepCalls = 0;
  const result = await observeForebetPage(pollingPage([
    {
      body: CHALLENGE_WITH_TURNSTILE_SCRIPT_HTML,
      domState: {
        visible_turnstile_widget: true,
        visible_turnstile_categories: ["turnstile_iframe"],
        visible_human_verification_text: false,
        visible_human_verification_markers: [],
      },
    },
  ]), {
    initialResponse: observationResponse(),
    deadlineAt: 5_000,
    startedAt: 0,
    now: () => 0,
    sleep: async () => {
      sleepCalls += 1;
    },
  });

  assert.equal(result.classification, CLASSIFICATIONS.CAPTCHA);
  assert.equal(result.interactive_human_verification_required, true);
  assert.equal(result.visible_turnstile_widget, true);
  assert.equal(result.observation_count, 1);
  assert.equal(sleepCalls, 0);
});

test("stops immediately on visible human-verification instruction", async () => {
  let sleepCalls = 0;
  const result = await observeForebetPage(pollingPage([
    {
      body: CHALLENGE_HTML,
      domState: {
        visible_turnstile_widget: false,
        visible_turnstile_categories: [],
        visible_human_verification_text: true,
        visible_human_verification_markers: ["verify_you_are_human"],
      },
    },
  ]), {
    initialResponse: observationResponse(),
    deadlineAt: 5_000,
    startedAt: 0,
    now: () => 0,
    sleep: async () => {
      sleepCalls += 1;
    },
  });

  assert.equal(result.classification, CLASSIFICATIONS.CAPTCHA);
  assert.equal(result.interactive_human_verification_required, true);
  assert.equal(result.visible_human_verification_text, true);
  assert.equal(result.observation_count, 1);
  assert.equal(sleepCalls, 0);
});

test("hidden Turnstile candidate does not stop observation early", async () => {
  let clock = 0;
  const sleeps = [];
  const result = await observeForebetPage(pollingPage([
    {
      body: CHALLENGE_WITH_TURNSTILE_SCRIPT_HTML,
      domState: {
        visible_turnstile_widget: false,
        visible_turnstile_categories: [],
        visible_human_verification_text: false,
        visible_human_verification_markers: [],
      },
    },
    {
      body: FOREBET_HTML,
      domState: {
        visible_turnstile_widget: false,
        visible_turnstile_categories: [],
        visible_human_verification_text: false,
        visible_human_verification_markers: [],
      },
    },
  ]), {
    initialResponse: observationResponse(),
    deadlineAt: 5_000,
    startedAt: 0,
    now: () => clock,
    sleep: async milliseconds => {
      sleeps.push(milliseconds);
      clock += milliseconds;
    },
  });

  assert.equal(result.classification, CLASSIFICATIONS.CONTENT);
  assert.equal(result.observation_count, 2);
  assert.deepEqual(sleeps, [1_500]);
});

test("stops immediately on denial and concrete content", async () => {
  for (const [body, status, expected] of [
    ["<html><title>Access denied</title></html>", 403, CLASSIFICATIONS.ACCESS_DENIED],
    [FOREBET_HTML, 200, CLASSIFICATIONS.CONTENT],
  ]) {
    let sleepCalls = 0;
    const result = await observeForebetPage(pollingPage([body]), {
      initialResponse: observationResponse(status),
      deadlineAt: 5_000,
      startedAt: 0,
      now: () => 0,
      sleep: async () => {
        sleepCalls += 1;
      },
    });
    assert.equal(result.classification, expected);
    assert.equal(result.observation_count, 1);
    assert.equal(sleepCalls, 0);
  }
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
  assert.equal(result.turnstile_source_marker, false);
  assert.equal(result.visible_turnstile_widget, false);
  assert.equal(result.visible_human_verification_text, false);
  assert.equal(result.interactive_human_verification_required, false);
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

test("closes the managed browser after a polling error", async () => {
  const events = [];
  const page = {
    setDefaultNavigationTimeout() {},
    async goto() {
      return observationResponse();
    },
    async url() {
      return FOREBET_DIAGNOSTIC_URL;
    },
    async title() {
      return "Just a moment...";
    },
    async content() {
      throw new Error("polling failed");
    },
  };
  const result = await runForebetBrowserDiagnostic(
    makeEnv(),
    {launch: async () => {
      events.push("launch");
      return makeBrowser(page, events);
    }},
    {now: new Date("2026-09-30T08:00:00Z")},
  );

  assert.equal(result.classification, CLASSIFICATIONS.CONFIGURATION);
  assert.deepEqual(events, ["launch", "newPage", "close"]);
});

test("closes the managed browser after a DOM-inspection error", async () => {
  const events = [];
  const page = makePage({
    body: CHALLENGE_HTML,
    evaluateError: new Error("DOM evaluation failed"),
  });
  const env = makeEnv();
  const result = await runForebetBrowserDiagnostic(
    env,
    {launch: async () => {
      events.push("launch");
      return makeBrowser(page, events);
    }},
    {now: new Date("2026-09-30T08:00:00Z")},
  );

  assert.equal(result.classification, CLASSIFICATIONS.CONFIGURATION);
  assert.equal(result.browser_launches, 1);
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

test("reports Browser Run API/configuration failures before consuming the daily gate", async () => {
  const kv = makeKv();
  const result = await runForebetBrowserDiagnostic(
    makeEnv({kv, limits: Object.assign(new Error("binding API unavailable"), {status: 500})}),
    {launch: async () => { throw new Error("must not launch"); }},
  );
  assert.equal(result.classification, CLASSIFICATIONS.CONFIGURATION);
  assert.equal(result.http_response_status, 503);
  assert.equal(result.browser_launch_attempts, 0);
  assert.equal(kv.calls.length, 0);
});

test("reports quota exhaustion before launching Chromium or consuming the gate", async () => {
  const kv = makeKv();
  const result = await runForebetBrowserDiagnostic(
    makeEnv({kv, limits: {allowedBrowserAcquisitions: 0, activeSessions: [], maxConcurrentSessions: 3}}),
    {launch: async () => { throw new Error("must not launch"); }},
  );
  assert.equal(result.classification, CLASSIFICATIONS.QUOTA);
  assert.equal(result.http_response_status, 429);
  assert.equal(result.browser_launch_attempts, 0);
  assert.equal(kv.calls.length, 0);
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

test("inspectPageDom evaluates DOM visibility, Turnstile candidate iframes, containers, and innerText", () => {
  const originalDoc = globalThis.document;
  const originalWin = globalThis.window;
  const originalElement = globalThis.Element;

  try {
    class MockElement {
      constructor({
        tag = "div",
        attrs = {},
        style = {},
        rect = {width: 100, height: 100},
        innerText = "",
        parent = null,
      } = {}) {
        this.tagName = tag.toUpperCase();
        this.attrs = attrs;
        this.style = {display: "block", visibility: "visible", opacity: "1", ...style};
        this.rect = rect;
        this.innerText = innerText;
        this.parentElement = parent;
      }
      getAttribute(name) {
        return this.attrs[name] || null;
      }
      getBoundingClientRect() {
        return this.rect;
      }
      closest(selector) {
        let cur = this;
        while (cur) {
          if (selector.includes(".cf-turnstile") && cur.attrs["class"]?.includes("cf-turnstile")) return cur;
          if (selector.includes("[data-sitekey]") && cur.attrs["data-sitekey"]) return cur;
          cur = cur.parentElement;
        }
        return null;
      }
    }
    globalThis.Element = MockElement;

    // 1. Visible Turnstile iframe
    const tsIframe = new MockElement({
      tag: "iframe",
      attrs: {src: "https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turnstile/if/ov2/av0/rcv0/0/generic"},
      rect: {width: 300, height: 65},
    });
    globalThis.document = {
      documentElement: {},
      body: new MockElement({tag: "body", innerText: "Checking your browser"}),
      querySelectorAll(sel) {
        if (sel === "iframe") return [tsIframe];
        return [];
      },
    };
    globalThis.window = {
      getComputedStyle(el) { return el.style; },
    };

    const res1 = inspectPageDom();
    assert.equal(res1.visible_turnstile_widget, true);
    assert.deepEqual(res1.visible_turnstile_categories, ["turnstile_iframe"]);
    assert.equal(res1.visible_human_verification_text, false);

    // 2. Generic visible challenge iframe (NOT Turnstile candidate)
    const genericIframe = new MockElement({
      tag: "iframe",
      attrs: {id: "cf-chl-widget-123", src: "https://www.forebet.com/cdn-cgi/challenge-platform/h/g/flow"},
      rect: {width: 100, height: 100},
    });
    globalThis.document.querySelectorAll = (sel) => sel === "iframe" ? [genericIframe] : [];
    const res2 = inspectPageDom();
    assert.equal(res2.visible_turnstile_widget, false);
    assert.equal(res2.visible_human_verification_text, false);

    // 3. Visible human verification text phrases
    const phrases = [
      ["Please verify you are human before proceeding.", "verify_you_are_human"],
      ["Human verification required.", "human_verification"],
      ["Please complete the security check to continue.", "complete_the_security_check"],
      ["Click to verify you are a human.", "click_to_verify"],
      ["Press and hold to verify your request.", "press_and_hold_to_verify"],
    ];
    for (const [phrase, expectedMarker] of phrases) {
      globalThis.document.body.innerText = phrase;
      const res = inspectPageDom();
      assert.equal(res.visible_turnstile_widget, false);
      assert.equal(res.visible_human_verification_text, true);
      assert.ok(res.visible_human_verification_markers.includes(expectedMarker));
    }

    // 4. Hidden Turnstile iframe (display: none or rect width 0)
    const hiddenIframe = new MockElement({
      tag: "iframe",
      attrs: {src: "https://challenges.cloudflare.com/turnstile/v0/api.js"},
      style: {display: "none"},
      rect: {width: 0, height: 0},
    });
    globalThis.document.querySelectorAll = (sel) => sel === "iframe" ? [hiddenIframe] : [];
    globalThis.document.body.innerText = "Just a moment...";
    const res4 = inspectPageDom();
    assert.equal(res4.visible_turnstile_widget, false);
    assert.equal(res4.visible_human_verification_text, false);

    // 5. Hidden parent element makes child Turnstile container hidden
    const hiddenParent = new MockElement({
      tag: "div",
      style: {display: "none"},
    });
    const childContainer = new MockElement({
      tag: "div",
      attrs: {class: "cf-turnstile"},
      parent: hiddenParent,
    });
    globalThis.document.querySelectorAll = (sel) => sel.includes(".cf-turnstile") ? [childContainer] : [];
    const res5 = inspectPageDom();
    assert.equal(res5.visible_turnstile_widget, false);

    // 6. Visible [data-sitekey] container
    const sitekeyContainer = new MockElement({
      tag: "div",
      attrs: {"data-sitekey": "0x4AAAAAAABBBBBB"},
      rect: {width: 300, height: 65},
    });
    globalThis.document.querySelectorAll = (sel) => sel.includes("[data-sitekey]") ? [sitekeyContainer] : [];
    const res6 = inspectPageDom();
    assert.equal(res6.visible_turnstile_widget, true);
    assert.deepEqual(res6.visible_turnstile_categories, ["sitekey_container"]);
  } finally {
    globalThis.document = originalDoc;
    globalThis.window = originalWin;
    globalThis.Element = originalElement;
  }
});
