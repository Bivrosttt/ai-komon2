import assert from 'node:assert/strict';
import test from 'node:test';

import {
  REQUIRED_SCRIPTS,
  auditHtml,
  compareWithBaseline,
  extractScriptSources
} from '../scripts/check_analytics_setup.mjs';

function completeHtml(extra = '') {
  const scripts = REQUIRED_SCRIPTS
    .map((source) => `<script src="${source}"></script>`)
    .join('');
  return `<!doctype html>
    <html><head>
      <title>計測テストLP</title>
      <meta name="description" content="テスト説明">
    </head><body>
      <section data-analytics-section="hero"></section>
      <section data-analytics-section="final_cta">
        <a href="https://timerex.net/s/example/calendar" target="_blank" rel="noopener">予約</a>
      </section>
      ${scripts}${extra}
    </body></html>`;
}

test('完全な広告LPは設定問題なし', () => {
  assert.deepEqual(auditHtml(completeHtml()), []);
});

test('必須スクリプトの欠落を検出する', () => {
  const html = completeHtml().replace('<script src="measurement.js"></script>', '');
  assert.ok(auditHtml(html).includes('missing-script:measurement.js'));
});

test('必須スクリプトの重複と順序違反を検出する', () => {
  const duplicated = completeHtml('<script src="measurement.js"></script>');
  assert.ok(auditHtml(duplicated).includes('duplicate-script:measurement.js'));

  const reversed = completeHtml()
    .replace('<script src="measurement.js"></script><script src="ga4-events.js"></script>',
      '<script src="ga4-events.js"></script><script src="measurement.js"></script>');
  assert.ok(auditHtml(reversed).includes('invalid-script-order'));
});

test('heroとfinal_ctaの区画識別子を検出する', () => {
  const html = completeHtml()
    .replace('data-analytics-section="hero"', '')
    .replace('data-analytics-section="final_cta"', '');
  const issues = auditHtml(html);
  assert.ok(issues.includes('missing-section:hero'));
  assert.ok(issues.includes('missing-section:final_cta'));
});

test('TimeRexリンクの安全属性漏れを検出する', () => {
  const html = completeHtml().replace(' target="_blank" rel="noopener"', '');
  assert.ok(auditHtml(html).includes('unsafe-timerex-anchor'));
});

test('script srcのクエリ文字列を除いて判定する', () => {
  const html = '<script src="../measurement.js?v=20260729"></script>';
  assert.deepEqual(extractScriptSources(html), ['measurement.js']);
});

test('既知問題は許容するが新規問題は失敗対象にする', () => {
  const baseline = {
    version: 1,
    knownIssues: { 'legacy.html': ['missing-script:measurement.js'] }
  };
  const current = {
    'legacy.html': ['missing-script:measurement.js'],
    'new.html': ['missing-section:hero']
  };
  const result = compareWithBaseline(current, baseline);
  assert.deepEqual(result.unexpected, { 'new.html': ['missing-section:hero'] });
});
