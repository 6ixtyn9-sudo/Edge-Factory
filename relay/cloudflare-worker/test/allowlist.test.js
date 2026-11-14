import assert from "node:assert/strict";
import test from "node:test";

import {allowed, allowedForebetGetrs, headersFor} from "../src/allowlist.js";

function url(text) {
  return new URL(text);
}

test("forebet and scoutingstats allowlists stay exact", () => {
  const canonical = "https://www.forebet.com/scripts/getrs.php?ln=en&tp=1x2&in=2026-09-30&ord=0&tz=0&tzs=&tze=&output=1";
  assert.equal(allowed(url(canonical)), true);
  assert.equal(allowedForebetGetrs(url(canonical)), true);
  assert.equal(allowed(url("https://www.forebet.com/scripts/getrs.php?ln=en&tp=uo&in=2026-09-30&ord=0&tz=0&tzs=&tze=")), true);
  assert.equal(allowed(url("https://www.forebet.com/scripts/getrs.php?tp=cs&in=2026-09-30")), false);
  assert.equal(allowed(url("https://www.forebet.com/scripts/getrs.php?ln=en&tp=1x2&in=2026-09-30&ord=0&tz=0&tzs=&tze=&output=2")), false);
  assert.equal(allowed(url("https://www.forebet.com/scripts/getrs.php?ln=en&tp=1x2&in=2026-09-30&ord=0&tz=0&tzs=&tze=&debug=1")), false);
  assert.equal(allowed(url("https://www.forebet.com/en/football-tips-and-predictions-for-today")), false);
  assert.equal(allowed(url("http://www.forebet.com/scripts/getrs.php?tp=1x2&in=2026-09-30")), false);
  assert.equal(allowed(url("https://scoutingstats.ai/api/fixtures/2026-09-30")), true);
  assert.equal(allowed(url("https://scoutingstats.ai/api/odds?fixture_ids=1,2,3")), true);
  assert.equal(allowed(url("https://scoutingstats.ai/api/private")), false);
  assert.equal(allowed(url("https://api.scoutingstats.ai/api/fixtures/2026-09-30")), false);
});

test("prosoccer allowlist covers only the prediction-week pages", () => {
  assert.equal(allowed(url("https://www.prosoccer.gr/en/football/predictions/")), true);
  assert.equal(allowed(url("https://www.prosoccer.gr/en/football/predictions/index.html")), true);
  assert.equal(allowed(url("https://www.prosoccer.gr/en/football/predictions/yesterday.html")), true);
  assert.equal(allowed(url("https://www.prosoccer.gr/en/football/predictions/tomorrow.html")), true);
  for (const day of ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]) {
    assert.equal(allowed(url(`https://www.prosoccer.gr/en/football/predictions/${day}.html`)), true);
  }
});

test("prosoccer rejects queries and out-of-scope paths", () => {
  assert.equal(allowed(url("https://www.prosoccer.gr/en/football/predictions/?force_date=2024-06-15")), false);
  assert.equal(allowed(url("https://www.prosoccer.gr/en/football/archive/")), false);
  assert.equal(allowed(url("https://www.prosoccer.gr/en/football/live-scores.html")), false);
  assert.equal(allowed(url("https://www.prosoccer.gr/")), false);
  assert.equal(allowed(url("http://www.prosoccer.gr/en/football/predictions/")), false);
  assert.equal(allowed(url("https://prosoccer.gr/en/football/predictions/")), false);
});

test("soccervista allowlist is the homepage only", () => {
  assert.equal(allowed(url("https://www.soccervista.com/")), true);
  assert.equal(allowed(url("https://www.soccervista.com/?date=2026-09-29")), false);
  assert.equal(allowed(url("https://www.soccervista.com/soccer_games.php?date=2026-09-29")), false);
  assert.equal(allowed(url("https://www.soccervista.com/usa/mls/CQv5qrFt/")), false);
  assert.equal(allowed(url("https://www.soccervista.com/event/eritrea-south-africa/WUlqTSd2/")), false);
  assert.equal(allowed(url("http://www.soccervista.com/")), false);
  assert.equal(allowed(url("https://soccervista.com/")), false);
});

test("predictz and windrawwin allowlists cover only production prediction pages", () => {
  assert.equal(allowed(url("https://www.predictz.com/predictions/20260930/")), true);
  assert.equal(allowed(url("https://www.predictz.com/predictions/20260930/?x=1")), false);
  assert.equal(allowed(url("https://www.predictz.com/predictions/")), false);
  assert.equal(allowed(url("https://predictz.com/predictions/20260930/")), false);

  assert.equal(allowed(url("https://www.windrawwin.com/predictions/today/")), true);
  assert.equal(allowed(url("https://www.windrawwin.com/predictions/tomorrow/")), true);
  assert.equal(allowed(url("https://www.windrawwin.com/predictions/future/20261002/")), false);
  assert.equal(allowed(url("https://www.windrawwin.com/predictions/today/?x=1")), false);
  assert.equal(allowed(url("https://windrawwin.com/predictions/today/")), false);
});

test("unrelated hosts are refused", () => {
  assert.equal(allowed(url("https://example.com/")), false);
  assert.equal(allowed(url("https://www.prosoccer.gr.evil/en/football/predictions/")), false);
  assert.equal(allowed(url("https://www.soccervista.com.evil/")), false);
});

test("headersFor matches each source transport contract", () => {
  const forebet = headersFor(url("https://www.forebet.com/scripts/getrs.php?ln=en&tp=1x2&in=2026-09-30&ord=0&tz=0&tzs=&tze=&output=1"));
  assert.equal(forebet["x-requested-with"], "XMLHttpRequest");
  assert.match(forebet.accept, /application\/json/);

  const prosoccer = headersFor(url("https://www.prosoccer.gr/en/football/predictions/"));
  assert.match(prosoccer.accept, /text\/html/);
  assert.match(prosoccer["accept-language"], /en-US/);

  const soccervista = headersFor(url("https://www.soccervista.com/"));
  assert.match(soccervista.accept, /text\/html/);

  const scouting = headersFor(url("https://scoutingstats.ai/api/fixtures/2026-09-30"));
  assert.equal(scouting.accept, "application/json");
});
