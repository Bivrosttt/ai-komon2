(function () {
  'use strict';

  var measurementId = window.AI_KOMON_GA_MEASUREMENT_ID;
  if (!measurementId || !/^G-[A-Z0-9]+$/.test(measurementId)) return;

  var script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(measurementId);
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', measurementId, { anonymize_ip: true });

  var toolMatch = window.location.pathname.match(/\/tools\/([^/]+)\/?$/);
  if (!toolMatch || !toolMatch[1] || toolMatch[1] === 'index.html') return;

  var toolSlug = toolMatch[1];
  window.gtag('event', 'tool_open', { tool_slug: toolSlug });
  document.addEventListener('submit', function () {
    window.gtag('event', 'tool_submit', { tool_slug: toolSlug });
  }, true);
}());
