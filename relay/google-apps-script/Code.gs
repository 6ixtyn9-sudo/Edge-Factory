const FOREBET_HOST = 'www.forebet.com';
const SCOUTING_HOST = 'scoutingstats.ai';
const MAX_BODY = 12 * 1024 * 1024;

function response_(payload) {
  return ContentService.createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

function parseSource_(text) {
  const match = String(text || '').match(/^https:\/\/([^/?#]+)(\/[^?#]*)?(?:\?([^#]*))?$/);
  if (!match) return null;
  const query = {};
  String(match[3] || '').split('&').forEach(function(part) {
    if (!part) return;
    const bits = part.split('=');
    query[decodeURIComponent(bits[0])] = decodeURIComponent(bits.slice(1).join('='));
  });
  return {hostname: match[1], pathname: match[2] || '/', query: query, text: text};
}

function allowed_(source) {
  if (!source) return false;
  if (source.hostname === FOREBET_HOST) {
    return source.pathname === '/scripts/getrs.php' &&
      ['1x2', 'uo', 'bts', 'ht'].includes(source.query.tp) &&
      /^\d{4}-\d{2}-\d{2}$/.test(source.query.in || '');
  }
  if (source.hostname === SCOUTING_HOST) {
    return /^\/api\/fixtures\/\d{4}-\d{2}-\d{2}$/.test(source.pathname) ||
      (source.pathname === '/api/odds' && /^[0-9,]+$/.test(source.query.fixture_ids || ''));
  }
  return false;
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
    const headers = url.hostname === FOREBET_HOST
      ? {
          Referer: 'https://www.forebet.com/en/football-tips-and-predictions-for-today',
          'X-Requested-With': 'XMLHttpRequest',
          Accept: 'application/json,text/plain,*/*',
        }
      : {Accept: 'application/json'};
    const upstream = UrlFetchApp.fetch(url.text, {
      method: 'get', headers: headers, followRedirects: true, muteHttpExceptions: true,
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
