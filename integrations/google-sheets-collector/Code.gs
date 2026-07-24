const SPREADSHEET_ID = '1LuibxdWft_uc8ACHQX1toXxN2_aJgsCJKYa1ro_maCA';
const SHEET_NAME = 'Raw Events';
const TOKEN = 'bef35216fda793ba42af2a753f681c98';
const ALLOWED_HOST = 'ai-komon.bivrost.co.jp';
const ALLOWED_EVENTS = new Set([
  'page_view', 'view_content', 'cta_click', 'diagnosis_start',
  'diagnosis_complete', 'timerex_click', 'lead'
]);

function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify({ ok: true, service: 'ai-komon-event-collector' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const queryToken = e && e.parameter ? String(e.parameter.token || '') : '';
    if (queryToken !== TOKEN) return json({ ok: false, error: 'unauthorized' });

    const data = JSON.parse((e.postData && e.postData.contents) || '{}');
    if (data.environment !== 'production' || data.hostname !== ALLOWED_HOST) {
      return json({ ok: false, error: 'invalid_environment' });
    }
    if (!ALLOWED_EVENTS.has(String(data.event_name || ''))) {
      return json({ ok: false, error: 'invalid_event' });
    }
    if (!data.event_id || !data.session_id) return json({ ok: false, error: 'missing_identity' });

    const lock = LockService.getScriptLock();
    lock.waitLock(5000);
    try {
      const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_NAME);
      if (!sheet) return json({ ok: false, error: 'sheet_not_found' });
      const attribution = data.attribution || {};
      sheet.appendRow([
        data.event_time || new Date().toISOString(),
        data.event_name || '',
        data.event_id || '',
        data.session_id || '',
        attribution.utm_content || '',
        attribution.utm_source || '',
        attribution.utm_medium || '',
        attribution.utm_campaign || '',
        attribution.fbclid || '',
        data.page || '',
        data.variant || '',
        data.value || '',
        data.level || '',
        'production'
      ]);
    } finally {
      lock.releaseLock();
    }
    return json({ ok: true, event_id: data.event_id });
  } catch (err) {
    return json({ ok: false, error: String(err && err.message || err) });
  }
}

function json(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}
