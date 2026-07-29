#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export const REQUIRED_SCRIPTS = [
  'analytics-config.js',
  'measurement-config.js',
  'meta-pixel-config.js',
  'meta-pixel.js',
  'measurement.js',
  'ga4-events.js'
];

export const REQUIRED_SECTIONS = ['hero', 'final_cta'];

function normalizeScriptSource(source) {
  const normalized = String(source || '')
    .split(/[?#]/, 1)[0]
    .replace(/^\.\//, '')
    .replace(/^\/+/, '');
  return normalized.split('/').pop() || '';
}

export function extractScriptSources(html) {
  const sources = [];
  const pattern = /<script\b[^>]*\bsrc\s*=\s*(["'])(.*?)\1[^>]*>/gi;
  let match;
  while ((match = pattern.exec(html)) !== null) {
    sources.push(normalizeScriptSource(match[2]));
  }
  return sources;
}

function extractAnalyticsSections(html) {
  const sections = [];
  const pattern = /\bdata-analytics-section\s*=\s*(["'])(.*?)\1/gi;
  let match;
  while ((match = pattern.exec(html)) !== null) {
    sections.push(match[2].trim());
  }
  return sections;
}

function extractTimerexAnchors(html) {
  const anchors = [];
  const pattern = /<a\b([^>]*\bhref\s*=\s*(["'])https?:\/\/(?:[^"'\/]+\.)?timerex\.net\/[^"']*\2[^>]*)>/gi;
  let match;
  while ((match = pattern.exec(html)) !== null) {
    anchors.push(match[1]);
  }
  return anchors;
}

export function auditHtml(html) {
  const issues = [];
  const scripts = extractScriptSources(html);

  for (const required of REQUIRED_SCRIPTS) {
    const count = scripts.filter((source) => source === required).length;
    if (count === 0) issues.push(`missing-script:${required}`);
    if (count > 1) issues.push(`duplicate-script:${required}`);
  }

  const presentRequired = REQUIRED_SCRIPTS.filter((required) => scripts.includes(required));
  const actualOrder = scripts.filter((source) => REQUIRED_SCRIPTS.includes(source));
  if (
    presentRequired.length === REQUIRED_SCRIPTS.length &&
    actualOrder.join('|') !== REQUIRED_SCRIPTS.join('|')
  ) {
    issues.push('invalid-script-order');
  }

  if (!/<title>\s*[^<]+\s*<\/title>/i.test(html)) {
    issues.push('missing-title');
  }
  if (!/<meta\b[^>]*\bname\s*=\s*(["'])description\1[^>]*\bcontent\s*=\s*(["'])[^"']+\2/i.test(html) &&
      !/<meta\b[^>]*\bcontent\s*=\s*(["'])[^"']+\1[^>]*\bname\s*=\s*(["'])description\2/i.test(html)) {
    issues.push('missing-meta-description');
  }

  const sections = extractAnalyticsSections(html);
  for (const required of REQUIRED_SECTIONS) {
    if (!sections.includes(required)) issues.push(`missing-section:${required}`);
  }
  const sectionCounts = new Map();
  for (const section of sections) {
    sectionCounts.set(section, (sectionCounts.get(section) || 0) + 1);
  }
  for (const [section, count] of sectionCounts) {
    if (section && count > 1) issues.push(`duplicate-section:${section}`);
  }

  if (/timerex\.net/i.test(html)) {
    const timerexAnchors = extractTimerexAnchors(html);
    if (timerexAnchors.length === 0) {
      issues.push('missing-timerex-anchor');
    } else {
      const insecure = timerexAnchors.some((attributes) => {
        const hasBlankTarget = /\btarget\s*=\s*(["'])_blank\1/i.test(attributes);
        const relMatch = attributes.match(/\brel\s*=\s*(["'])(.*?)\1/i);
        const relValues = relMatch ? relMatch[2].toLowerCase().split(/\s+/) : [];
        return !hasBlankTarget || !relValues.includes('noopener');
      });
      if (insecure) issues.push('unsafe-timerex-anchor');
    }
  }

  return [...new Set(issues)].sort();
}

function walkHtml(directory, root, results) {
  if (!fs.existsSync(directory)) return;
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const absolute = path.join(directory, entry.name);
    const relative = path.relative(root, absolute).split(path.sep).join('/');
    if (entry.isDirectory()) {
      if (relative === 'lp/archive' || relative.startsWith('lp/archive/')) continue;
      walkHtml(absolute, root, results);
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      results.push(relative);
    }
  }
}

export function discoverAnalyticsPages(root) {
  const pages = fs.readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isFile() && /^lp-.+\.html$/.test(entry.name))
    .map((entry) => entry.name);

  if (fs.existsSync(path.join(root, 'diagnosis.html'))) pages.push('diagnosis.html');
  walkHtml(path.join(root, 'lp'), root, pages);
  return [...new Set(pages)].sort();
}

function auditGlobalFiles(root) {
  const issues = [];
  const read = (relative) => fs.readFileSync(path.join(root, relative), 'utf8');
  const propertyValue = (source, key) => {
    const match = source.match(new RegExp(`\\b${key}\\s*:\\s*(['"])(.*?)\\1`));
    return match ? match[2] : '';
  };
  const assignmentValue = (source, variable) => {
    const escaped = variable.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const matches = [...source.matchAll(new RegExp(`${escaped}\\s*=\\s*(['"])(.*?)\\1`, 'g'))];
    return matches.length ? matches[matches.length - 1][2] : '';
  };

  const measurementConfig = read('measurement-config.js');
  for (const key of [
    'productionHosts',
    'measurementId',
    'metaDatasetId',
    'clarityProjectId',
    'clarityConsentMode',
    'eventEndpoint'
  ]) {
    if (!measurementConfig.includes(key)) issues.push(`measurement-config-missing:${key}`);
  }
  if (!measurementConfig.includes('ai-komon.bivrost.co.jp')) {
    issues.push('measurement-config-missing-production-host');
  }

  const analyticsConfig = read('analytics-config.js');
  const gaFromMeasurement = propertyValue(measurementConfig, 'measurementId');
  const gaFromLegacyConfig = assignmentValue(analyticsConfig, 'window.AI_KOMON_GA_MEASUREMENT_ID');
  if (!gaFromMeasurement || !gaFromLegacyConfig || gaFromMeasurement !== gaFromLegacyConfig) {
    issues.push('ga4-measurement-id-mismatch');
  }

  const metaConfig = read('meta-pixel-config.js');
  const metaFromMeasurement = propertyValue(measurementConfig, 'metaDatasetId');
  const metaFromLegacyConfig = assignmentValue(metaConfig, 'window.AI_KOMON_META_PIXEL_ID');
  if (!metaFromMeasurement || !metaFromLegacyConfig || metaFromMeasurement !== metaFromLegacyConfig) {
    issues.push('meta-dataset-id-mismatch');
  }

  const eventEndpoint = propertyValue(measurementConfig, 'eventEndpoint');
  if (!/^https:\/\/script\.google\.com\/macros\/s\/[^/]+\/exec$/.test(eventEndpoint)) {
    issues.push('invalid-google-sheets-event-endpoint');
  }

  const measurement = read('measurement.js');
  for (const eventName of [
    'PageView',
    'ViewContent',
    'CTA_Click',
    'Schedule',
    'DiagnosisStart',
    'DiagnosisComplete',
    'scroll_depth',
    'section_view',
    'engagement_10s'
  ]) {
    if (!measurement.includes(eventName)) issues.push(`measurement-event-missing:${eventName}`);
  }

  const privacy = read('privacy.html');
  for (const service of ['Google Analytics 4', 'Meta Pixel', 'Microsoft Clarity']) {
    if (!privacy.includes(service)) issues.push(`privacy-service-missing:${service}`);
  }

  const manual = read('docs/analytics-and-attribution.md');
  if (!manual.includes('check_analytics_setup.mjs')) {
    issues.push('manual-missing-test-command');
  }
  if (!manual.includes('analytics-audit-baseline.json')) {
    issues.push('manual-missing-baseline-rules');
  }

  return [...new Set(issues)].sort();
}

export function auditRepository(root) {
  const issues = {};
  for (const relative of discoverAnalyticsPages(root)) {
    const html = fs.readFileSync(path.join(root, relative), 'utf8');
    const pageIssues = auditHtml(html);
    if (pageIssues.length) issues[relative] = pageIssues;
  }
  const globalIssues = auditGlobalFiles(root);
  if (globalIssues.length) issues.__global__ = globalIssues;
  return issues;
}

function loadBaseline(root) {
  const baselinePath = path.join(root, 'tests', 'fixtures', 'analytics-audit-baseline.json');
  if (!fs.existsSync(baselinePath)) return { version: 1, knownIssues: {} };
  const parsed = JSON.parse(fs.readFileSync(baselinePath, 'utf8'));
  if (parsed.version !== 1 || typeof parsed.knownIssues !== 'object') {
    throw new Error(`Invalid analytics baseline: ${baselinePath}`);
  }
  return parsed;
}

export function compareWithBaseline(currentIssues, baseline) {
  const unexpected = {};
  const resolved = {};
  const knownIssues = baseline.knownIssues || {};
  const files = new Set([...Object.keys(currentIssues), ...Object.keys(knownIssues)]);

  for (const file of files) {
    const current = new Set(currentIssues[file] || []);
    const known = new Set(knownIssues[file] || []);
    const newIssues = [...current].filter((issue) => !known.has(issue)).sort();
    const fixedIssues = [...known].filter((issue) => !current.has(issue)).sort();
    if (newIssues.length) unexpected[file] = newIssues;
    if (fixedIssues.length) resolved[file] = fixedIssues;
  }
  return { unexpected, resolved };
}

function printIssueGroup(title, issues) {
  const files = Object.keys(issues);
  if (!files.length) return;
  console.log(`\n${title}`);
  for (const file of files.sort()) {
    for (const issue of issues[file]) console.log(`  ${file}: ${issue}`);
  }
}

function main() {
  const root = process.cwd();
  const currentIssues = auditRepository(root);
  if (process.argv.includes('--print-baseline')) {
    console.log(JSON.stringify({
      version: 1,
      note: '既存LPの既知問題のみ。新しい問題はCIで失敗させる。',
      knownIssues: currentIssues
    }, null, 2));
    return;
  }

  const baseline = loadBaseline(root);
  const { unexpected, resolved } = compareWithBaseline(currentIssues, baseline);
  printIssueGroup('解消済みの既知問題（baselineから削除可能）:', resolved);
  printIssueGroup('新しいアナリティクス設定問題:', unexpected);

  const pageCount = discoverAnalyticsPages(root).length;
  const legacyCount = Object.keys(baseline.knownIssues || {}).filter((file) => file !== '__global__').length;
  if (Object.keys(unexpected).length) {
    console.error(`\nAnalytics audit failed: ${pageCount}ページを確認し、新しい設定漏れを検出しました。`);
    process.exitCode = 1;
    return;
  }
  console.log(`Analytics audit passed: ${pageCount}ページを確認（既知問題のある既存LP ${legacyCount}件）。`);
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  main();
}
