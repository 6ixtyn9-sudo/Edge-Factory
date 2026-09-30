const FOREBET_HOST = 'www.forebet.com';
const SCOUTING_HOST = 'scoutingstats.ai';
const PROSOCCER_HOST = 'www.prosoccer.gr';
const SOCCERVISTA_HOST = 'www.soccervista.com';
const PREDICTZ_HOST = 'www.predictz.com';
const WINDRAWWIN_HOST = 'www.windrawwin.com';
const MAX_BODY = 12 * 1024 * 1024;
const BROWSER_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36';

// ProSoccer only serves the rolling prediction week; the adapter never
// requests anything else, so exact pages are allowlisted and nothing more.
const PROSOCCER_PAGES = [
  '/en/football/predictions/',
  '/en/football/predictions/index.html',
  '/en/football/predictions/yesterday.html',
  '/en/football/predictions/tomorrow.html',
  '/en/football/predictions/Monday.html',
  '/en/football/predictions/Tuesday.html',
  '/en/football/predictions/Wednesday.html',
  '/en/football/predictions/Thursday.html',
  '/en/football/predictions/Friday.html',
  '/en/football/predictions/Saturday.html',
  '/en/football/predictions/Sunday.html',
];

const WINDRAWWIN_PAGES = [
  '/predictions/today/',
  '/predictions/tomorrow/',
];

function response_(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

function parseSource_(text) {
  const match = String(text || '').match(/^https:\/\/([^/?#]+)(\/[^?#]*)?(?:\?([^#]*))?$/);
  if (!match) return null;
  const query = {};
  const counts = {};
  String(match[3] || '').split('&').forEach(function(part) {
    if (!part) return;
    const bits = part.split('=');
    const key = decodeURIComponent(bits[0]);
    query[key] = decodeURIComponent(bits.slice(1).join('='));
    counts[key] = (counts[key] || 0) + 1;
  });
  return {hostname: match[1], pathname: match[2] || '/', query: query, counts: counts, text: text};
}

function hasOnlyParams_(source, names) {
  const allowed = {};
  names.forEach(function(name) { allowed[name] = true; });
  const keys = Object.keys(source.query);
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];
    if (!allowed[key] || source.counts[key] !== 1) return false;
  }
  return true;
}

function allowedForebetGetrs_(source) {
  if (source.hostname !== FOREBET_HOST || source.pathname !== '/scripts/getrs.php') return false;
  if (!hasOnlyParams_(source, ['ln', 'tp', 'in', 'ord', 'tz', 'tzs', 'tze', 'output'])) return false;
  if (source.query.ln !== 'en') return false;
  if (['1x2', 'uo', 'bts', 'ht'].indexOf(source.query.tp) === -1) return false;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(source.query.in || '')) return false;
  if (source.query.ord !== '0') return false;
  if (source.query.tz !== '0') return false;
  if (source.query.tzs !== '') return false;
  if (source.query.tze !== '') return false;
  return source.query.output === undefined || source.query.output === '1';
}

function allowed_(source) {
  if (!source) return false;
  if (source.hostname === FOREBET_HOST) {
    return allowedForebetGetrs_(source);
  }
  if (source.hostname === SCOUTING_HOST) {
    return /^\/api\/fixtures\/\d{4}-\d{2}-\d{2}$/.test(source.pathname) ||
      (source.pathname === '/api/odds' && /^[0-9,]+$/.test(source.query.fixture_ids || ''));
  }
  if (source.hostname === PROSOCCER_HOST) {
    // plain HTML prediction pages only; the adapter never uses a query string.
    return PROSOCCER_PAGES.indexOf(source.pathname) !== -1 &&
      Object.keys(source.query).length === 0;
  }
  if (source.hostname === SOCCERVISTA_HOST) {
    // today-only capture: the homepage is the daily predictions table.
    return source.pathname === '/' && Object.keys(source.query).length === 0;
  }
  if (source.hostname === PREDICTZ_HOST) {
    return /^\/predictions\/\d{8}\/$/.test(source.pathname) &&
      Object.keys(source.query).length === 0;
  }
  if (source.hostname === WINDRAWWIN_HOST) {
    return WINDRAWWIN_PAGES.indexOf(source.pathname) !== -1 &&
      Object.keys(source.query).length === 0;
  }
  return false;
}

function headersFor_(url) {
  if (url.hostname === FOREBET_HOST) {
    return {
      Referer: 'https://www.forebet.com/en/football-tips-and-predictions-for-today',
      'X-Requested-With': 'XMLHttpRequest',
      Accept: 'application/json,text/plain,*/*',
      'Accept-Language': 'en-US,en;q=0.9',
      'User-Agent': BROWSER_UA,
    };
  }
  if (url.hostname === SOCCERVISTA_HOST) {
    return {
      Accept: 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.9',
      Referer: 'https://www.soccervista.com/',
      Cookie: 'cookieconsent_status=dismiss; cookie_consent=accepted',
      'User-Agent': BROWSER_UA,
    };
  }
  if (url.hostname === PROSOCCER_HOST || url.hostname === PREDICTZ_HOST || url.hostname === WINDRAWWIN_HOST) {
    return {
      Accept: 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.9',
      'User-Agent': BROWSER_UA,
    };
  }
  return {Accept: 'application/json', 'User-Agent': BROWSER_UA};
}

function doPost(e) {
  let input;
  try { input = JSON.parse(e.postData.contents); }
  catch (_) { return response_({error: 'json'}); }

  const token = PropertiesService.getScriptProperties().getProperty('RELAY_TOKEN');
  if (!token || input.token !== token) return response_({error: 'auth'});
  try {
    const url = parseSource_(input.url);
    if (!allowed_(url)) return response_({error: 'source_not_allowed'});
    const upstream = UrlFetchApp.fetch(url.text, {
      method: 'get', headers: headersFor_(url), followRedirects: true, muteHttpExceptions: true,
    });
    const body = upstream.getContentText();
    if (body.length > MAX_BODY) return response_({error: 'too_large'});
    return response_({
      source_url: url.text,
      status: upstream.getResponseCode(),
      fetched_at: new Date().toISOString(),
      body: body,
    });
  } catch (error) {
    return response_({error: 'upstream_fetch', detail: String(error)});
  }
}
