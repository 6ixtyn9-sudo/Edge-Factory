const FOREBET_HOST = "www.forebet.com";

// Phase 1 is deliberately one fixed public page. Callers cannot provide a URL,
// date, query string, cookies, headers, or scripts to this diagnostic.
export const FOREBET_DIAGNOSTIC_URL =
  "https://www.forebet.com/en/football-tips-and-predictions-for-today";

export const NAVIGATION_TIMEOUT_MS = 45_000;
// Browser Run's default inactivity timeout is 60 seconds. The overall deadline
// leaves margin below it; the observation interval also keeps the page active.
export const OVERALL_DEADLINE_MS = 55_000;
export const OBSERVATION_WINDOW_MS = 20_000;
export const OBSERVATION_INTERVAL_MS = 1_500;
export const MAX_DIAGNOSTIC_HTML_BYTES = 4 * 1024 * 1024;
export const BROWSER_BUDGET_KV_BINDING = "BROWSER_DIAGNOSTIC_KV";
export const BROWSER_BUDGET_KEY_PREFIX = "forebet-browser-diagnostic";
export const BROWSER_BUDGET_TTL_SECONDS = 172_800;

export const CLASSIFICATIONS = Object.freeze({
  CONTENT: "genuine_forebet_prediction_content",
  CHALLENGE: "unresolved_cloudflare_challenge",
  CAPTCHA: "captcha_or_turnstile_required",
  ACCESS_DENIED: "explicit_access_denial",
  TIMEOUT: "navigation_timeout",
  CONFIGURATION: "browser_rendering_configuration_or_api_error",
  QUOTA: "quota_or_plan_error",
  OTHER: "other",
});

const CHALLENGE_MARKERS = Object.freeze([
  ["just_a_moment", /just a moment/i],
  ["checking_browser", /checking your browser/i],
  ["challenge_platform", /challenge-platform|cf-chl-/i],
  ["enable_javascript_cookies", /enable javascript and cookies/i],
  ["performing_security_verification", /performing security verification/i],
]);

const TURNSTILE_SOURCE_MARKERS = Object.freeze([
  ["turnstile", /\bturnstile\b/i],
  ["cf_turnstile", /cf-turnstile/i],
  ["challenge_script", /challenges\.cloudflare\.com/i],
]);

const ACCESS_DENIAL_MARKERS = Object.freeze([
  ["access_denied", /access denied/i],
  ["error_1020", /error\s*1020/i],
  ["forbidden", /\bforbidden\b/i],
  ["blocked_request", /you have been blocked|request blocked/i],
]);

const PREDICTION_MARKERS = Object.freeze([
  ["forebet_brand", /\bforebet\b/i],
  ["home_team_label", /\bhome\s+team\b/i],
  ["away_team_label", /\baway\s+team\b/i],
  ["probability_label", /\bprob(?:ability)?\.?\b/i],
  ["prediction_label", /\bpredictions?\b/i],
  ["correct_score_label", /\bcorrect\s+score\b/i],
]);

// These are deliberately textual/structural signals visible in Forebet's
// rendered page, not invented CSS selectors. A candidate must contain a date,
// a probability triplet, and a scoreline in addition to the generic labels.
const FIXTURE_MARKERS = Object.freeze([
  ["fixture_date", /\b(?:20\d{2}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]20\d{2})\b/i],
  ["probability_triplet", /\b\d{1,3}\s+\d{1,3}\s+\d{1,3}\b/],
  ["scoreline", /\b\d{1,2}\s*-\s*\d{1,2}\b/],
]);

function utcDate(now = new Date()) {
  return now.toISOString().slice(0, 10);
}

function byteLength(text) {
  return new TextEncoder().encode(text).byteLength;
}

function truncate(value, limit = 240) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  return text.length > limit ? `${text.slice(0, limit - 1)}…` : text;
}

function safeErrorMessage(error) {
  // Do not return browser/session identifiers or arbitrary URLs in the relay
  // envelope. The classification and error type are the useful diagnostics.
  return truncate(
    String(error?.message || error || "unknown error")
      .replace(/https?:\/\/\S+/gi, "<url>")
      .replace(/bearer\s+\S+/gi, "Bearer <redacted>")
      .replace(/[0-9a-f]{8}-[0-9a-f-]{27,}/gi, "<id>")
      .replace(/\b[0-9a-f]{32,}\b/gi, "<id>"),
  );
}

function errorStatus(error) {
  const value = error?.status ?? error?.statusCode ?? error?.code;
  return Number.isFinite(Number(value)) ? Number(value) : null;
}

function hasAnyMarker(body, markers) {
  return markers.filter(([, pattern]) => pattern.test(body)).map(([name]) => name);
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

function isForebetFinalUrl(finalUrl) {
  if (!finalUrl) return false;
  try {
    const parsed = new URL(finalUrl);
    return parsed.protocol === "https:" && parsed.hostname === FOREBET_HOST;
  } catch {
    return false;
  }
}

export function predictionMarkupEvidence(body) {
  const matched = hasAnyMarker(body, PREDICTION_MARKERS);
  const fixtureMatched = hasAnyMarker(body, FIXTURE_MARKERS);
  const required = new Set([
    "forebet_brand",
    "home_team_label",
    "away_team_label",
  ]);
  const hasCoreLabels = [...required].every((marker) => matched.includes(marker));
  const hasPredictionField = matched.includes("probability_label") ||
    matched.includes("prediction_label") || matched.includes("correct_score_label");
  const generic = hasCoreLabels && hasPredictionField;
  const candidate = generic && fixtureMatched.includes("fixture_date");
  const concrete = candidate &&
    fixtureMatched.includes("probability_triplet") &&
    fixtureMatched.includes("scoreline");
  return {
    matched,
    fixture_matched: fixtureMatched,
    generic,
    candidate,
    concrete,
    valid: concrete,
  };
}

export function inspectPageDom() {
  function isElementVisible(el) {
    if (!el || !(el instanceof Element)) return false;
    try {
      let current = el;
      while (current && current !== document.documentElement) {
        const style = window.getComputedStyle(current);
        if (!style) return false;
        if (style.display === "none") return false;
        if (style.visibility === "hidden" || style.visibility === "collapse") return false;
        if (parseFloat(style.opacity || "1") === 0) return false;
        current = current.parentElement;
      }
      const rect = el.getBoundingClientRect();
      if (!rect || rect.width <= 0 || rect.height <= 0) return false;
      return true;
    } catch {
      return false;
    }
  }

  const matchedCategories = [];

  const iframes = Array.from(document.querySelectorAll("iframe"));
  for (const iframe of iframes) {
    try {
      const src = (iframe.getAttribute("src") || "").toLowerCase();
      const title = (iframe.getAttribute("title") || "").toLowerCase();
      const id = (iframe.getAttribute("id") || "").toLowerCase();
      const name = (iframe.getAttribute("name") || "").toLowerCase();

      const isTurnstileSrc = src.includes("challenges.cloudflare.com") ||
        src.includes("turnstile") ||
        src.includes("/cf-turnstile/");
      const isTurnstileTitle = title.includes("turnstile") ||
        title.includes("cloudflare security challenge") ||
        title.includes("widget containing a cloudflare security challenge") ||
        title.includes("security challenge");
      const isTurnstileIdOrName = id.includes("cf-turnstile") ||
        id.includes("turnstile") ||
        name.includes("cf-turnstile") ||
        name.includes("turnstile");

      const insideTurnstileContainer = Boolean(
        iframe.closest(".cf-turnstile, [data-turnstile], [data-sitekey], #turnstile-wrapper, .turnstile-container")
      );

      const isTurnstileCandidate = isTurnstileSrc || isTurnstileTitle || isTurnstileIdOrName || insideTurnstileContainer;

      if (isTurnstileCandidate && isElementVisible(iframe)) {
        if ((isTurnstileSrc || isTurnstileTitle || isTurnstileIdOrName) && !matchedCategories.includes("turnstile_iframe")) {
          matchedCategories.push("turnstile_iframe");
        }
        if (insideTurnstileContainer && !matchedCategories.includes("turnstile_container")) {
          matchedCategories.push("turnstile_container");
        }
      }
    } catch {}
  }

  const containers = Array.from(document.querySelectorAll(".cf-turnstile, [data-turnstile], #turnstile-wrapper, .turnstile-container"));
  for (const container of containers) {
    try {
      if (isElementVisible(container) && !matchedCategories.includes("turnstile_container")) {
        matchedCategories.push("turnstile_container");
      }
    } catch {}
  }

  const sitekeyContainers = Array.from(document.querySelectorAll("[data-sitekey]"));
  for (const container of sitekeyContainers) {
    try {
      if (isElementVisible(container) && !matchedCategories.includes("sitekey_container")) {
        matchedCategories.push("sitekey_container");
      }
    } catch {}
  }

  const innerText = (document.body && typeof document.body.innerText === "string")
    ? document.body.innerText
    : "";

  const textPatterns = [
    ["verify_you_are_human", /verify you are human/i],
    ["human_verification", /human verification/i],
    ["complete_the_security_check", /complete the security check/i],
    ["click_to_verify", /click to verify/i],
    ["press_and_hold_to_verify", /press and hold to verify/i],
  ];

  const matchedTextMarkers = [];
  for (const [name, pattern] of textPatterns) {
    if (pattern.test(innerText)) {
      matchedTextMarkers.push(name);
    }
  }

  return {
    visible_turnstile_widget: matchedCategories.length > 0,
    visible_turnstile_categories: matchedCategories,
    visible_human_verification_text: matchedTextMarkers.length > 0,
    visible_human_verification_markers: matchedTextMarkers,
  };
}

export async function inspectRenderedDom(page) {
  if (typeof page?.evaluate !== "function") {
    return {
      visible_turnstile_widget: false,
      visible_turnstile_categories: [],
      visible_human_verification_text: false,
      visible_human_verification_markers: [],
    };
  }
  const result = await page.evaluate(inspectPageDom);
  return {
    visible_turnstile_widget: Boolean(result?.visible_turnstile_widget),
    visible_turnstile_categories: Array.isArray(result?.visible_turnstile_categories)
      ? result.visible_turnstile_categories
      : [],
    visible_human_verification_text: Boolean(result?.visible_human_verification_text),
    visible_human_verification_markers: Array.isArray(result?.visible_human_verification_markers)
      ? result.visible_human_verification_markers
      : [],
  };
}

export function classifyRenderedForebet({
  httpStatus = null,
  contentType = null,
  finalUrl = null,
  body = "",
  responseBytes = null,
  navigationTimedOut = false,
  responseSizeOverflow = false,
  visibleTurnstileWidget = false,
  visibleTurnstileCategories = [],
  visibleHumanVerificationText = false,
  visibleHumanVerificationMarkers = [],
}) {
  const text = String(body || "");
  const challengeMarkers = hasAnyMarker(text, CHALLENGE_MARKERS);
  const turnstileSourceMarkers = hasAnyMarker(text, TURNSTILE_SOURCE_MARKERS);
  const denialMarkers = hasAnyMarker(text, ACCESS_DENIAL_MARKERS);
  const markup = predictionMarkupEvidence(text);
  const status = Number(httpStatus);
  const statusDenial = [401, 403, 451].includes(status);

  const turnstileSourceMarker = turnstileSourceMarkers.length > 0;
  const visibleWidget = Boolean(visibleTurnstileWidget);
  const visibleText = Boolean(visibleHumanVerificationText);
  const interactiveHumanVerificationRequired = visibleWidget || visibleText;

  let classification = CLASSIFICATIONS.OTHER;
  if (navigationTimedOut) {
    classification = CLASSIFICATIONS.TIMEOUT;
  } else if (interactiveHumanVerificationRequired) {
    classification = CLASSIFICATIONS.CAPTCHA;
  } else if (challengeMarkers.length > 0 || turnstileSourceMarker) {
    classification = CLASSIFICATIONS.CHALLENGE;
  } else if (statusDenial || denialMarkers.length > 0) {
    classification = CLASSIFICATIONS.ACCESS_DENIED;
  } else if (
    !responseSizeOverflow &&
    markup.valid &&
    status >= 200 &&
    status < 300 &&
    isForebetFinalUrl(finalUrl)
  ) {
    classification = CLASSIFICATIONS.CONTENT;
  } else if (responseSizeOverflow) {
    classification = CLASSIFICATIONS.OTHER;
  }

  const captchaMarkers = [
    ...visibleTurnstileCategories,
    ...visibleHumanVerificationMarkers,
  ];

  return {
    classification,
    success: classification === CLASSIFICATIONS.CONTENT,
    http_status: Number.isFinite(status) ? status : null,
    final_url: truncate(finalUrl, 500),
    content_type: truncate(contentType, 160) || null,
    response_bytes: responseBytes ?? byteLength(text),
    page_title: null,
    contains_cloudflare_challenge: challengeMarkers.length > 0 || turnstileSourceMarker,
    cloudflare_challenge_markers: challengeMarkers,
    turnstile_source_marker: turnstileSourceMarker,
    turnstile_source_markers: turnstileSourceMarkers,
    visible_turnstile_widget: visibleWidget,
    visible_turnstile_categories: Array.isArray(visibleTurnstileCategories)
      ? visibleTurnstileCategories
      : [],
    visible_human_verification_text: visibleText,
    visible_human_verification_markers: Array.isArray(visibleHumanVerificationMarkers)
      ? visibleHumanVerificationMarkers
      : [],
    interactive_human_verification_required: interactiveHumanVerificationRequired,
    contains_forebet_prediction_markup: markup.generic,
    candidate_prediction_content: markup.candidate,
    concrete_fixture_row_evidence: markup.concrete,
    prediction_markup_markers: markup.matched,
    fixture_evidence_markers: markup.fixture_matched,
    navigation_timed_out: Boolean(navigationTimedOut),
    captcha_or_turnstile: interactiveHumanVerificationRequired,
    captcha_markers: captchaMarkers,
    access_denied: statusDenial || denialMarkers.length > 0,
    access_denial_markers: denialMarkers,
    response_size_overflow: Boolean(responseSizeOverflow),
  };
}

function baseResult(overrides = {}) {
  return {
    operation: "forebet_browser_diagnostic",
    target_url: FOREBET_DIAGNOSTIC_URL,
    classification: CLASSIFICATIONS.OTHER,
    success: false,
    http_response_status: 200,
    http_status: null,
    final_url: null,
    content_type: null,
    response_bytes: 0,
    page_title: null,
    contains_cloudflare_challenge: false,
    cloudflare_challenge_markers: [],
    turnstile_source_marker: false,
    turnstile_source_markers: [],
    visible_turnstile_widget: false,
    visible_turnstile_categories: [],
    visible_human_verification_text: false,
    visible_human_verification_markers: [],
    interactive_human_verification_required: false,
    contains_forebet_prediction_markup: false,
    candidate_prediction_content: false,
    concrete_fixture_row_evidence: false,
    prediction_markup_markers: [],
    fixture_evidence_markers: [],
    navigation_timed_out: false,
    captcha_or_turnstile: false,
    captcha_markers: [],
    access_denied: false,
    access_denial_markers: [],
    response_size_overflow: false,
    observation_count: 0,
    observation_elapsed_ms: 0,
    observation_deadline_exceeded: false,
    browser_launch_attempts: 0,
    browser_launches: 0,
    navigation_attempts: 0,
    daily_budget_date: utcDate(),
    ...overrides,
  };
}

function browserErrorResult(error, attempts) {
  const message = safeErrorMessage(error);
  const lower = message.toLowerCase();
  const status = errorStatus(error);
  let classification = CLASSIFICATIONS.CONFIGURATION;
  let responseStatus = 503;

  if (
    status === 429 ||
    /quota|rate limit|too many requests|time limit exceeded|plan limit|daily limit/.test(lower)
  ) {
    classification = CLASSIFICATIONS.QUOTA;
    responseStatus = 429;
  } else if (/timeout|timed out|timeoute?rror/.test(lower)) {
    classification = CLASSIFICATIONS.TIMEOUT;
    responseStatus = 504;
  }

  return baseResult({
    classification,
    http_response_status: responseStatus,
    navigation_timed_out: classification === CLASSIFICATIONS.TIMEOUT,
    browser_launch_attempts: attempts.launchAttempts,
    browser_launches: attempts.browserLaunches,
    navigation_attempts: attempts.navigationAttempts,
    error_type: error?.name || typeof error,
    error_message: message,
  });
}

async function pageUrl(page) {
  try {
    return typeof page?.url === "function" ? await page.url() : null;
  } catch {
    return null;
  }
}

async function pageTitle(page) {
  try {
    return typeof page?.title === "function" ? truncate(await page.title(), 200) : null;
  } catch {
    return null;
  }
}

function responseStatus(response) {
  return typeof response?.status === "function" ? response.status() : null;
}

function sleepForObservation(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

export async function observeForebetPage(page, {
  initialResponse = null,
  documentResponse = () => initialResponse,
  deadlineAt = Date.now() + OBSERVATION_WINDOW_MS,
  startedAt = Date.now(),
  now = Date.now,
  sleep = sleepForObservation,
} = {}) {
  let observation;
  let observationCount = 0;

  while (true) {
    observationCount += 1;
    const finalUrl = await pageUrl(page);
    const title = await pageTitle(page);
    // The HTML is used only in memory for bounded marker classification. It is
    // never logged or returned to the caller.
    const body = await page.content();
    const response = documentResponse() || initialResponse;
    const responseBytes = byteLength(body);

    const domInspection = typeof page?.evaluate === "function"
      ? await inspectRenderedDom(page)
      : {
          visible_turnstile_widget: false,
          visible_turnstile_categories: [],
          visible_human_verification_text: false,
          visible_human_verification_markers: [],
        };

    observation = classifyRenderedForebet({
      httpStatus: responseStatus(response),
      contentType: responseHeader(response, "content-type"),
      finalUrl,
      body,
      responseBytes,
      responseSizeOverflow: responseBytes > MAX_DIAGNOSTIC_HTML_BYTES,
      visibleTurnstileWidget: domInspection.visible_turnstile_widget,
      visibleTurnstileCategories: domInspection.visible_turnstile_categories,
      visibleHumanVerificationText: domInspection.visible_human_verification_text,
      visibleHumanVerificationMarkers: domInspection.visible_human_verification_markers,
    });
    observation.page_title = title;
    observation.observation_count = observationCount;
    observation.observation_elapsed_ms = Math.max(0, now() - startedAt);

    // A challenge may be transitional; all other terminal classifications are
    // returned immediately. In particular, CAPTCHA/Turnstile is never retried.
    const challengeMayContinue = observation.classification === CLASSIFICATIONS.CHALLENGE;
    if (!challengeMayContinue || observation.success || now() >= deadlineAt) {
      observation.observation_deadline_exceeded =
        challengeMayContinue && now() >= deadlineAt;
      return observation;
    }

    const remaining = deadlineAt - now();
    if (remaining <= 0) {
      observation.observation_deadline_exceeded = true;
      return observation;
    }
    await sleep(Math.min(OBSERVATION_INTERVAL_MS, remaining));
  }
}

export async function claimDailyBrowserBudget(kv, now = new Date()) {
  const date = utcDate(now);
  const key = `${BROWSER_BUDGET_KEY_PREFIX}:${date}`;
  const existing = await kv.get(key);
  if (existing !== null && existing !== undefined) {
    return {allowed: false, date, key};
  }
  // Consume the claim before launching. A failed navigation therefore does not
  // trigger an expensive retry storm; the next attempt is intentionally next UTC day.
  await kv.put(key, "claimed", {expirationTtl: BROWSER_BUDGET_TTL_SECONDS});
  return {allowed: true, date, key};
}

export async function runForebetBrowserDiagnostic(
  env,
  browserClient,
  {now = new Date(), sleep = sleepForObservation} = {},
) {
  if (!env?.BROWSER) {
    return baseResult({
      classification: CLASSIFICATIONS.CONFIGURATION,
      http_response_status: 503,
      error_code: "missing_browser_binding",
      error_message: "Browser Run binding BROWSER is not configured",
    });
  }

  const attempts = {launchAttempts: 0, browserLaunches: 0, navigationAttempts: 0};
  const startedAt = Date.now();
  const overallDeadline = startedAt + OVERALL_DEADLINE_MS;
  let limits;

  // These checks do not launch a browser, so do them before consuming the
  // once-per-day launch gate. A bad binding or already-exhausted acquisition
  // limit should not spend the day's browser attempt.
  try {
    if (typeof env.BROWSER.limits !== "function") {
      throw Object.assign(new Error("Browser Run binding does not expose limits()"), {
        name: "BrowserBindingError",
      });
    }
    limits = await env.BROWSER.limits();
  } catch (error) {
    return browserErrorResult(error, attempts);
  }

  const active = Array.isArray(limits?.activeSessions) ? limits.activeSessions.length : 0;
  const maximum = Number(limits?.maxConcurrentSessions);
  if (limits?.allowedBrowserAcquisitions === 0 || (maximum > 0 && active >= maximum)) {
    return browserErrorResult(Object.assign(
      new Error("Browser Run acquisition limit is exhausted"),
      {name: "BrowserQuotaError", status: 429},
    ), attempts);
  }

  const kv = env[BROWSER_BUDGET_KV_BINDING];
  if (!kv) {
    return baseResult({
      classification: CLASSIFICATIONS.CONFIGURATION,
      http_response_status: 503,
      error_code: "missing_daily_budget_binding",
      error_message: `Free daily budget binding ${BROWSER_BUDGET_KV_BINDING} is not configured`,
    });
  }

  let budget;
  try {
    budget = await claimDailyBrowserBudget(kv, now);
  } catch (error) {
    return browserErrorResult(error, attempts);
  }
  if (!budget.allowed) {
    return baseResult({
      classification: CLASSIFICATIONS.QUOTA,
      http_response_status: 429,
      daily_budget_date: budget.date,
      budget_exhausted: true,
      error_code: "daily_browser_budget_exhausted",
      error_message: "The one-launch Forebet diagnostic budget is already claimed for this UTC day",
    });
  }

  let browser = null;
  let observation = null;
  let primaryError = null;
  let cleanupError = null;

  try {
    attempts.launchAttempts = 1;
    browser = await browserClient.launch(env.BROWSER);
    attempts.browserLaunches = 1;
    const page = await browser.newPage();
    if (typeof page.setDefaultNavigationTimeout === "function") {
      page.setDefaultNavigationTimeout(NAVIGATION_TIMEOUT_MS);
    }

    let latestDocumentResponse = null;
    const onResponse = (candidate) => {
      try {
        const request = typeof candidate?.request === "function" ? candidate.request() : null;
        const resourceType = typeof request?.resourceType === "function"
          ? request.resourceType()
          : "document";
        if (resourceType === "document") latestDocumentResponse = candidate;
      } catch {
        // A response event is diagnostic enrichment only; navigation remains authoritative.
      }
    };
    if (typeof page.on === "function") page.on("response", onResponse);

    try {
      attempts.navigationAttempts = 1;
      const remaining = Math.max(1, overallDeadline - Date.now());
      const response = await page.goto(FOREBET_DIAGNOSTIC_URL, {
        waitUntil: "domcontentloaded",
        timeout: Math.min(NAVIGATION_TIMEOUT_MS, remaining),
      });
      latestDocumentResponse = latestDocumentResponse || response;
      observation = await observeForebetPage(page, {
        initialResponse: response,
        documentResponse: () => latestDocumentResponse || response,
        deadlineAt: Math.min(overallDeadline, Date.now() + OBSERVATION_WINDOW_MS),
        startedAt,
        sleep,
      });
    } finally {
      if (typeof page.off === "function") page.off("response", onResponse);
    }
  } catch (error) {
    primaryError = error;
  } finally {
    if (browser && typeof browser.close === "function") {
      try {
        await browser.close();
      } catch (error) {
        cleanupError = error;
      }
    }
  }

  if (primaryError) {
    return baseResult({
      ...browserErrorResult(primaryError, attempts),
      daily_budget_date: budget.date,
    });
  }
  if (cleanupError) {
    return baseResult({
      ...browserErrorResult(cleanupError, attempts),
      daily_budget_date: budget.date,
      error_code: "browser_cleanup_failed",
    });
  }
  return baseResult({
    ...observation,
    daily_budget_date: budget.date,
    browser_launch_attempts: attempts.launchAttempts,
    browser_launches: attempts.browserLaunches,
    navigation_attempts: attempts.navigationAttempts,
    http_response_status: 200,
  });
}
