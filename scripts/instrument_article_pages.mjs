#!/usr/bin/env node

/**
 * Add the canonical, host-gated measurement stack to every SEO article.
 *
 * This is intentionally idempotent so a future article export can be
 * re-run without accumulating duplicate scripts or body attributes.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const ARTICLES = path.join(ROOT, 'articles');
const SCRIPTS = [
  'analytics-config.js',
  'measurement-config.js',
  'meta-pixel-config.js',
  'meta-pixel.js',
  'measurement.js',
  'ga4-events.js'
];

function walk(directory, files = []) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(absolute, files);
    else if (entry.isFile() && entry.name === 'index.html') files.push(absolute);
  }
  return files;
}

function relativeRootPath(file) {
  const relative = path.relative(ROOT, file).split(path.sep).join('/');
  const depth = relative.split('/').length - 1;
  return '../'.repeat(depth);
}

function scriptBlock(prefix) {
  return [
    '  <!-- AI顧問室 canonical analytics: article measurement -->',
    ...SCRIPTS.map((source) => `  <script src="${prefix}${source}"></script>`),
    '  <!-- /AI顧問室 canonical analytics -->'
  ].join('\n');
}

function addScripts(html, prefix) {
  const marker = '<!-- AI顧問室 canonical analytics: article measurement -->';
  if (html.includes(marker)) return html;
  const headClose = html.search(/<\/head\s*>/i);
  if (headClose === -1) throw new Error('missing-head-close');
  return `${html.slice(0, headClose)}${scriptBlock(prefix)}\n${html.slice(headClose)}`;
}

function addBodyAttribute(html, contentType) {
  if (/data-analytics-content-type\s*=\s*["']/i.test(html)) return html;
  const body = html.match(/<body\b([^>]*)>/i);
  if (!body) throw new Error('missing-body');
  const replacement = `<body${body[1]} data-analytics-content-type="${contentType}">`;
  return html.replace(body[0], replacement);
}

let changed = 0;
for (const file of walk(ARTICLES).sort()) {
  const relative = path.relative(ROOT, file).split(path.sep).join('/');
  const prefix = relative === 'articles/index.html' ? '../' : '../../';
  const contentType = relative === 'articles/index.html' ? 'article_index' : 'article';
  const original = fs.readFileSync(file, 'utf8');
  const updated = addBodyAttribute(addScripts(original, prefix), contentType);
  if (updated !== original) {
    fs.writeFileSync(file, updated);
    changed += 1;
  }
}

console.log(`Instrumented ${changed} article page(s).`);
