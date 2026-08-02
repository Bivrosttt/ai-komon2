import assert from 'node:assert/strict';
import test from 'node:test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  ARTICLE_REQUIRED_SCRIPTS,
  auditArticleHtml,
  auditArticleRepository,
  discoverArticlePages
} from '../scripts/check_article_analytics.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

test('全SEO記事に共通計測スタックが入っている', () => {
  const pages = discoverArticlePages(ROOT);
  const issues = auditArticleRepository(ROOT);
  assert.equal(pages.length, 35);
  assert.deepEqual(issues, {});
});

test('記事監査は欠落・順序違反・種別違いを検出する', () => {
  const scripts = ARTICLE_REQUIRED_SCRIPTS.map((source) => `<script src="${source}"></script>`).join('');
  const html = `<html><head><title>記事</title><meta name="description" content="説明"><link rel="canonical" href="https://example.com"></head><body data-analytics-content-type="article"><script src="ga4-events.js"></script>${scripts}</body></html>`;
  const issues = auditArticleHtml(html, 'articles/example/index.html');
  assert.ok(issues.includes('duplicate-script:ga4-events.js'));
  assert.ok(!issues.includes('missing-article-content-type'));

  const reversed = `<html><head><title>記事</title><meta name="description" content="説明"><link rel="canonical" href="https://example.com"><script src="${ARTICLE_REQUIRED_SCRIPTS.slice(0, -2).join('"></script><script src="')}"></script><script src="ga4-events.js"></script><script src="measurement.js"></script></head><body data-analytics-content-type="article"></body></html>`;
  assert.ok(auditArticleHtml(reversed, 'articles/example/index.html').includes('invalid-script-order'));
});
