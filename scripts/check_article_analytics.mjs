#!/usr/bin/env node

/**
 * Read-only audit for the SEO article measurement contract.
 *
 * This checks source instrumentation (HTML and shared scripts). It does not
 * pretend to prove that a production event was received; use the Google
 * Sheets MCP / Raw Events query for that second, independent check.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { extractScriptSources } from './check_analytics_setup.mjs';

export const ARTICLE_REQUIRED_SCRIPTS = [
  'analytics-config.js',
  'measurement-config.js',
  'meta-pixel-config.js',
  'meta-pixel.js',
  'measurement.js',
  'ga4-events.js'
];

function walk(directory, files = []) {
  if (!fs.existsSync(directory)) return files;
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(absolute, files);
    else if (entry.isFile() && entry.name.endsWith('.html')) files.push(absolute);
  }
  return files;
}

export function discoverArticlePages(root) {
  return walk(path.join(root, 'articles'))
    .map((file) => path.relative(root, file).split(path.sep).join('/'))
    .sort();
}

function isArticleIndex(relative) {
  return relative === 'articles/index.html';
}

function auditScripts(html) {
  const issues = [];
  const scripts = extractScriptSources(html);
  for (const required of ARTICLE_REQUIRED_SCRIPTS) {
    const count = scripts.filter((source) => source === required).length;
    if (count === 0) issues.push(`missing-script:${required}`);
    if (count > 1) issues.push(`duplicate-script:${required}`);
  }
  const actual = scripts.filter((source) => ARTICLE_REQUIRED_SCRIPTS.includes(source));
  if (actual.length === ARTICLE_REQUIRED_SCRIPTS.length &&
      actual.join('|') !== ARTICLE_REQUIRED_SCRIPTS.join('|')) {
    issues.push('invalid-script-order');
  }
  return issues;
}

export function auditArticleHtml(html, relative = '') {
  const issues = auditScripts(html);
  const contentType = html.match(/data-analytics-content-type\s*=\s*(["'])(.*?)\1/i);
  if (!contentType) issues.push('missing-article-content-type');
  else if (isArticleIndex(relative) && contentType[2] !== 'article_index') {
    issues.push('invalid-article-index-content-type');
  } else if (!isArticleIndex(relative) && contentType[2] !== 'article') {
    issues.push('invalid-article-content-type');
  }
  if (!/<title>\s*[^<]+\s*<\/title>/i.test(html)) issues.push('missing-title');
  if (!/<meta\b[^>]*\bname\s*=\s*(["'])description\1[^>]*\bcontent\s*=\s*(["'])[^"']+\2/i.test(html) &&
      !/<meta\b[^>]*\bcontent\s*=\s*(["'])[^"']+\1[^>]*\bname\s*=\s*(["'])description\2/i.test(html)) {
    issues.push('missing-meta-description');
  }
  if (!/<link\b[^>]*\brel\s*=\s*(["'])canonical\1/i.test(html)) issues.push('missing-canonical');
  if (!isArticleIndex(relative) && !/"@type"\s*:\s*"Article"/i.test(html)) {
    issues.push('missing-article-jsonld');
  }
  if (/timerex\.net/i.test(html)) {
    const timerexAnchors = [...html.matchAll(/<a\b([^>]*\bhref\s*=\s*(["'])https?:\/\/(?:[^"'\/]+\.)?timerex\.net\/[^"']*\2[^>]*)>/gi)];
    if (!timerexAnchors.length) issues.push('missing-timerex-anchor');
  }
  return [...new Set(issues)].sort();
}

export function auditArticleRepository(root) {
  const issues = {};
  for (const relative of discoverArticlePages(root)) {
    const pageIssues = auditArticleHtml(fs.readFileSync(path.join(root, relative), 'utf8'), relative);
    if (pageIssues.length) issues[relative] = pageIssues;
  }
  return issues;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const issues = auditArticleRepository(root);
  const pages = discoverArticlePages(root);
  const json = process.argv.includes('--json');
  if (json) {
    console.log(JSON.stringify({ ok: Object.keys(issues).length === 0, pages: pages.length, issues }, null, 2));
  } else {
    console.log(`SEO article analytics audit: ${pages.length} page(s)`);
    if (Object.keys(issues).length) {
      for (const [file, fileIssues] of Object.entries(issues)) console.log(`- ${file}: ${fileIssues.join(', ')}`);
      process.exitCode = 1;
    } else {
      console.log('OK: canonical analytics stack and article metadata are present on every page.');
    }
  }
}
