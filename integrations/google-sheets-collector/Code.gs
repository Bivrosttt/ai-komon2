const SPREADSHEET_ID = '1LuibxdWft_uc8ACHQX1toXxN2_aJgsCJKYa1ro_maCA';
const SHEET_NAME = 'Raw Events';
const GA4_PROPERTY_ID = '545222887';
const GA4_SHEET_NAME = 'GA4 Daily';
const TOKEN = 'bef35216fda793ba42af2a753f681c98';
const ALLOWED_HOST = 'ai-komon.bivrost.co.jp';
const ALLOWED_EVENTS = new Set([
  'page_view', 'view_content', 'cta_click', 'diagnosis_start',
  'diagnosis_complete', 'timerex_click', 'lead', 'scroll_depth',
  'section_view', 'engagement_10s'
]);
const RAW_EVENTS_HEADERS = [
  'event_time', 'event_name', 'event_id', 'session_id',
  'utm_content', 'utm_source', 'utm_medium', 'utm_campaign',
  'utm_term', 'utm_id', 'fbclid', 'gclid', 'from',
  'attribution_status', 'page', 'url', 'referrer', 'variant',
  'value', 'level', 'environment'
];
const LEGACY_RAW_EVENTS_HEADERS = [
  'event_time', 'event_name', 'event_id', 'session_id',
  'utm_content', 'utm_source', 'utm_medium', 'utm_campaign',
  'fbclid', 'page', 'variant', 'value', 'level', 'environment'
];

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
      ensureHeaders(sheet);
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
        attribution.utm_term || '',
        attribution.utm_id || '',
        attribution.fbclid || '',
        attribution.gclid || '',
        attribution.from || '',
        attribution.attribution_status || '',
        data.page || '',
        data.url || '',
        data.referrer || '',
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

function ensureHeaders(sheet) {
  const scanRows = Math.min(Math.max(sheet.getLastRow(), 1), 10);
  const scan = sheet.getRange(1, 1, scanRows, Math.max(sheet.getLastColumn(), RAW_EVENTS_HEADERS.length)).getValues();
  let headerRow = 0;
  scan.forEach((row, index) => {
    if (row.map(String).indexOf('event_time') !== -1 && !headerRow) headerRow = index + 1;
  });
  if (!headerRow) headerRow = 3;
  const currentHeaders = sheet.getRange(headerRow, 1, 1, RAW_EVENTS_HEADERS.length).getValues()[0].map(String);
  const matches = RAW_EVENTS_HEADERS.every((header, index) => currentHeaders[index] === header);
  if (matches) return;

  // The first collector version used a 14-column schema. Map historical
  // values by header name before expanding the header so fbclid/page/etc.
  // cannot be relabeled under the newly inserted columns.
  const isLegacy = LEGACY_RAW_EVENTS_HEADERS.every((header, index) => currentHeaders[index] === header);
  if (isLegacy) {
    migrateRowsToCanonicalSchema(sheet, headerRow, LEGACY_RAW_EVENTS_HEADERS);
    return;
  }

  // Never silently relabel an unknown layout. A manual migration is safer
  // than appending new events into a schema we cannot identify.
  throw new Error('Unsupported Raw Events schema; migrate existing headers before collecting new events.');
}

function migrateRowsToCanonicalSchema(sheet, headerRow, sourceHeaders) {
  const lastRow = sheet.getLastRow();
  const rowCount = Math.max(lastRow - headerRow, 0);
  const sourceIndexes = {};
  sourceHeaders.forEach((header, index) => { sourceIndexes[header] = index; });
  const migratedRows = rowCount > 0
    ? sheet.getRange(headerRow + 1, 1, rowCount, sourceHeaders.length).getValues().map(row => {
        return RAW_EVENTS_HEADERS.map(header => {
          const index = sourceIndexes[header];
          return index == null ? '' : row[index];
        });
      })
    : [];

  sheet.getRange(headerRow, 1, 1, RAW_EVENTS_HEADERS.length).setValues([RAW_EVENTS_HEADERS]);
  if (migratedRows.length > 0) {
    sheet.getRange(headerRow + 1, 1, migratedRows.length, RAW_EVENTS_HEADERS.length).setValues(migratedRows);
  }
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('AI顧問室 分析')
    .addItem('GA4を直近7日分同期', 'syncGa4Report')
    .addItem('GA4日次同期を設定', 'installDailyGa4Trigger')
    .addToUi();
}

/** GA4 Dailyを毎日一度更新する時間主導トリガーを1つだけ登録する。 */
function installDailyGa4Trigger() {
  ScriptApp.getProjectTriggers()
    .filter(trigger => trigger.getHandlerFunction() === 'syncGa4Report')
    .forEach(trigger => ScriptApp.deleteTrigger(trigger));
  ScriptApp.newTrigger('syncGa4Report')
    .timeBased()
    .everyDays(1)
    .atHour(3)
    .create();
  return { ok: true, schedule: 'daily around 03:00 Asia/Tokyo' };
}

/**
 * GA4 Data APIから広告・LP分析に必要な日次イベント粒度を取得し、
 * Google SheetsのGA4 Dailyタブへ置き換え保存する。
 * 初回実行時はAnalytics Data APIの有効化とOAuth承認が必要。
 */
function syncGa4Report() {
  const request = {
    dateRanges: [{ startDate: '7daysAgo', endDate: 'today' }],
    dimensions: [
      { name: 'date' },
      { name: 'eventName' },
      { name: 'sessionManualCampaignName' },
      { name: 'sessionManualAdContent' },
      { name: 'pagePath' }
    ],
    metrics: [
      { name: 'eventCount' },
      { name: 'totalUsers' },
      { name: 'sessions' }
    ],
    limit: '100000',
    keepEmptyRows: false
  };
  const report = AnalyticsData.Properties.runReport(request, 'properties/' + GA4_PROPERTY_ID);
  const header = [
    'synced_at', 'date', 'event_name', 'session_campaign',
    'session_ad_content', 'page_path', 'event_count', 'total_users', 'sessions'
  ];
  const values = [header].concat((report.rows || []).map(row => {
    const dimensions = (row.dimensionValues || []).map(value => value.value || '');
    const metrics = (row.metricValues || []).map(value => value.value || '0');
    return [new Date().toISOString()].concat(dimensions, metrics);
  }));

  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = spreadsheet.getSheetByName(GA4_SHEET_NAME) || spreadsheet.insertSheet(GA4_SHEET_NAME);
  sheet.clearContents();
  sheet.getRange(1, 1, values.length, header.length).setValues(values);
  return { ok: true, rows: values.length - 1, sheet: GA4_SHEET_NAME };
}

function json(value) {
  return ContentService
    .createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}
