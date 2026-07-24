(function () {
  'use strict';

  var config = window.AI_KOMON_MEASUREMENT_CONFIG || {};
  var hosts = config.productionHosts || [];
  var isProduction = hosts.indexOf(window.location.hostname) !== -1;
  if (!isProduction || window.__AI_KOMON_MEASUREMENT_INITIALIZED) return;
  window.__AI_KOMON_MEASUREMENT_INITIALIZED = true;

  var storage = window.sessionStorage;
  var attributionKeys = [
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
    'utm_id', 'fbclid', 'gclid', 'from'
  ];

  function uuid() {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') return window.crypto.randomUUID();
    return 'ak-' + Date.now() + '-' + Math.random().toString(36).slice(2);
  }

  function getStored(key) {
    try { return storage.getItem(key) || ''; } catch (e) { return ''; }
  }

  function setStored(key, value) {
    try { storage.setItem(key, value); } catch (e) {}
  }

  function getSessionId() {
    var id = getStored('ak_session_id');
    if (!id) { id = uuid(); setStored('ak_session_id', id); }
    return id;
  }

  function getAttribution() {
    var result = {};
    var params = new URLSearchParams(window.location.search);
    attributionKeys.forEach(function (key) {
      var value = params.get(key) || getStored('ak_' + key);
      if (params.get(key)) {
        setStored('ak_' + key, params.get(key));
        if (key === 'from') setStored('ai_komon_from', params.get(key));
      }
      if (value) result[key] = value;
    });
    return result;
  }

  function toCollector(eventName, params) {
    if (!config.eventEndpoint) return;
    var attribution = getAttribution();
    var payload = {
      event_time: new Date().toISOString(),
      event_name: eventName,
      event_id: uuid(),
      session_id: getSessionId(),
      page: window.location.pathname,
      url: window.location.href,
      hostname: window.location.hostname,
      referrer: document.referrer || '',
      environment: 'production',
      variant: attribution.utm_content || '',
      value: params && params.value != null ? String(params.value) : '',
      level: params && params.level != null ? String(params.level) : '',
      attribution: attribution
    };
    var body = JSON.stringify(payload);
    var endpoint = config.eventEndpoint + (config.eventEndpoint.indexOf('?') === -1 ? '?' : '&') +
      'token=' + encodeURIComponent(config.eventToken || '');
    try {
      var blob = new Blob([body], { type: 'text/plain;charset=utf-8' });
      if (navigator.sendBeacon && navigator.sendBeacon(endpoint, blob)) return;
    } catch (e) {}
    try {
      fetch(endpoint, {
        method: 'POST',
        body: body,
        mode: 'no-cors',
        keepalive: true,
        headers: { 'Content-Type': 'text/plain;charset=utf-8' }
      });
    } catch (e) {}
  }

  function toGa4(eventName, params) {
    // GA4's config tag already emits its automatic page_view. Keep page_view
    // in the collector for the spreadsheet, but avoid a duplicate GA4 event.
    if (eventName === 'page_view' || typeof window.gtag !== 'function') return;
    var attribution = getAttribution();
    var payload = {
      page: window.location.pathname,
      session_id: getSessionId(),
      variant: attribution.utm_content || '',
      lead_from: attribution.from || 'direct'
    };
    Object.keys(attribution).forEach(function (key) { payload[key] = attribution[key]; });
    Object.keys(params || {}).forEach(function (key) { payload[key] = params[key]; });
    try { window.gtag('event', eventName, payload); } catch (e) {}
  }

  function normalizeEventName(name) {
    return {
      PageView: 'page_view',
      ViewContent: 'view_content',
      CTA_Click: 'cta_click',
      Schedule: 'timerex_click',
      Lead: 'lead',
      DiagnosisStart: 'diagnosis_start',
      DiagnosisComplete: 'diagnosis_complete'
    }[name] || String(name || '').toLowerCase();
  }

  window.aiKomonMeasure = function (eventName, params) {
    var normalized = normalizeEventName(eventName);
    toGa4(normalized, params || {});
    toCollector(normalized, params || {});
  };

  function wrap(name) {
    var original = window[name];
    if (typeof original !== 'function' || original.__aiKomonWrapped) return;
    var wrapped = function (eventName, params) {
      var result = original.apply(this, arguments);
      window.aiKomonMeasure(eventName, params || {});
      return result;
    };
    wrapped.__aiKomonWrapped = true;
    window[name] = wrapped;
  }

  wrap('aiKomonTrack');
  wrap('aiKomonTrackCustom');

  // GA4が未初期化のページでも、公開LPでは同じ計測IDを使う。
  if (config.measurementId && typeof window.gtag !== 'function') {
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(config.measurementId);
    document.head.appendChild(script);
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', config.measurementId, { anonymize_ip: true });
  }

  window.aiKomonMeasure('PageView', {});
})();
