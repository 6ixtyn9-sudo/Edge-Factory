// Exact host/path/query allowlist for the authenticated source relay.
//
// The relay is transport only: it refuses every URL that is not an exact,
// publicly documented source endpoint, so neither deployment can be used as
// an open proxy. Python adapters re-validate the echoed URL and payload
// shape, so a relay can never alter source identity.
const FOREBET_HOST = "www.forebet.com";
const SCOUTING_HOST = "scoutingstats.ai";
const PROSOCCER_HOST = "www.prosoccer.gr";
const SOCCERVISTA_HOST = "www.soccervista.com";

// ProSoccer serves only the rolling prediction week: the today page, the
// yesterday/tomorrow aliases, and one weekday page per nearby day. Anything
// else (archive, static assets, live-scores) is deliberately refused.
const PROSOCCER_PAGES = new Set([
  "/en/football/predictions/",
  "/en/football/predictions/index.html",
  "/en/football/predictions/yesterday.html",
  "/en/football/predictions/tomorrow.html",
  "/en/football/predictions/Monday.html",
  "/en/football/predictions/Tuesday.html",
  "/en/football/predictions/Wednesday.html",
  "/en/football/predictions/Thursday.html",
  "/en/football/predictions/Friday.html",
  "/en/football/predictions/Saturday.html",
  "/en/football/predictions/Sunday.html",
]);

const BROWSER_UA =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36";

export function allowed(url) {
  if (url.protocol !== "https:") return false;
  if (url.hostname === FOREBET_HOST) {
    return url.pathname === "/scripts/getrs.php" &&
      ["1x2", "uo", "bts", "ht"].includes(url.searchParams.get("tp")) &&
      /^\d{4}-\d{2}-\d{2}$/.test(url.searchParams.get("in") || "");
  }
  if (url.hostname === SCOUTING_HOST) {
    return /^\/api\/fixtures\/\d{4}-\d{2}-\d{2}$/.test(url.pathname) ||
      (url.pathname === "/api/odds" && /^[0-9,]+$/.test(url.searchParams.get("fixture_ids") || ""));
  }
  if (url.hostname === PROSOCCER_HOST) {
    // plain HTML pages only; no query surface is needed by the adapter.
    return PROSOCCER_PAGES.has(url.pathname) && url.search === "";
  }
  if (url.hostname === SOCCERVISTA_HOST) {
    // today-only capture: the homepage is the daily predictions table.
    return url.pathname === "/" && url.search === "";
  }
  return false;
}

export function headersFor(url) {
  if (url.hostname === FOREBET_HOST) {
    return {
      "referer": "https://www.forebet.com/en/football-tips-and-predictions-for-today",
      "x-requested-with": "XMLHttpRequest",
      "accept": "application/json,text/plain,*/*",
      "user-agent": BROWSER_UA,
    };
  }
  if (url.hostname === PROSOCCER_HOST || url.hostname === SOCCERVISTA_HOST) {
    return {
      "accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
      "accept-language": "en-US,en;q=0.9",
      "user-agent": BROWSER_UA,
    };
  }
  return {"accept": "application/json", "user-agent": "Mozilla/5.0 Chrome/124.0"};
}
