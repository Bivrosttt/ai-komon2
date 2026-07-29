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

  function getQueryValue(params, key) {
    return params.get(key) || '';
  }

  function getAttribution() {
    var result = {};
    var params = new URLSearchParams(window.location.search);
    attributionKeys.forEach(function (key) {
      var queryValue = getQueryValue(params, key);
      var storedValue = getStored('ak_' + key);
      var value = key === 'from' ? queryValue || storedValue : storedValue || queryValue;

      // UTM / click identifiers are first-touch values. This prevents an
      // internal link or a later page from replacing the original ad source.
      // `from` is intentionally allowed to follow the current LP handoff.
      if (queryValue && (key === 'from' || !storedValue)) {
        setStored('ak_' + key, queryValue);
        if (key === 'from') setStored('ai_komon_from', queryValue);
      }
      if (value) {
        result[key] = value;
      }
    });

    // A fbclid is a reliable signal that the click came through Meta, but it
    // does not contain campaign or creative information. Fill only the
    // source/medium that can be inferred; never invent campaign/content.
    if (result.fbclid && !result.utm_source) {
      result.utm_source = 'meta';
      setStored('ak_utm_source', 'meta');
    }
    if (result.fbclid && !result.utm_medium) {
      result.utm_medium = 'paid_social';
      setStored('ak_utm_medium', 'paid_social');
    }
    result.attribution_status = result.utm_campaign || result.utm_content ? 'explicit' :
      (result.fbclid ? 'inferred_meta' : 'direct_or_unknown');

    return result;
  }

  function decorateUrl(rawHref) {
    if (!rawHref || rawHref.indexOf('mailto:') === 0 || rawHref.indexOf('tel:') === 0 ||
        rawHref.indexOf('javascript:') === 0) return null;
    var url;
    try { url = new URL(rawHref, window.location.href); } catch (e) { return null; }
    var isInternal = url.hostname === window.location.hostname ||
      url.hostname === 'ai-komon.bivrost.co.jp' || url.hostname === 'www.ai-komon.bivrost.co.jp';
    var isTimerex = url.hostname === 'timerex.net' || url.hostname.endsWith('.timerex.net');
    if (!isInternal && !isTimerex) return null;

    var attribution = getAttribution();
    attributionKeys.forEach(function (key) {
      if (attribution[key] && !url.searchParams.has(key)) {
        url.searchParams.set(key, attribution[key]);
      }
    });
    if (isTimerex && !url.searchParams.has('ak_session_id')) {
      url.searchParams.set('ak_session_id', getSessionId());
    }
    return url.toString();
  }

  function decorateLinks() {
    var links = document.querySelectorAll('a[href]');
    Array.prototype.forEach.call(links, function (link) {
      var decorated = decorateUrl(link.getAttribute('href'));
      if (decorated) link.setAttribute('href', decorated);
    });
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
  window.aiKomonMeasure('ViewContent', {
    content_name: window.location.pathname,
    content_type: 'website'
  });

  // Keep attribution on every internal handoff, including the external
  // booking link. This also repairs links injected after initial page load.
  decorateLinks();
  if (window.MutationObserver) {
    new MutationObserver(decorateLinks).observe(document.documentElement, {
      childList: true,
      subtree: true
    });
  }

  // Engagement signals for LP analysis. These are intentionally emitted only
  // once per session/page threshold so they remain useful for creative tests.
  function initBehaviorTracking() {
    var depthThresholds = [25, 50, 75, 90];
    var sentDepths = {};
    var ticking = false;
    var scheduleFrame = window.requestAnimationFrame || function (callback) {
      return window.setTimeout(callback, 16);
    };

    function sendDepth() {
      ticking = false;
      var scrollable = document.documentElement.scrollHeight - window.innerHeight;
      if (scrollable <= 0) return;
      var percent = Math.round((window.scrollY / scrollable) * 100);
      depthThresholds.forEach(function (threshold) {
        if (percent < threshold || sentDepths[threshold]) return;
        sentDepths[threshold] = true;
        window.aiKomonMeasure('scroll_depth', {
          value: String(threshold),
          depth_percent: threshold
        });
      });
    }

    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      scheduleFrame(sendDepth);
    }, { passive: true });

    if (window.IntersectionObserver) {
      var seenSections = {};
      var sections = document.querySelectorAll('[data-analytics-section]');
      var sectionObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var name = entry.target.getAttribute('data-analytics-section');
          if (!name || seenSections[name]) return;
          seenSections[name] = true;
          window.aiKomonMeasure('section_view', {
            value: name,
            section_name: name
          });
          sectionObserver.unobserve(entry.target);
        });
      }, { threshold: 0.35 });
      Array.prototype.forEach.call(sections, function (section) { sectionObserver.observe(section); });
    }

    window.setTimeout(function () {
      if (document.visibilityState !== 'hidden') {
        window.aiKomonMeasure('engagement_10s', {
          value: '10',
          engagement_seconds: 10
        });
      }
    }, 10000);
  }

  initBehaviorTracking();

  // Centralized CTA tracking makes GA4/Sheets work even when the Meta Pixel
  // script is blocked by a browser extension or consent setting.
  document.addEventListener('click', function (event) {
    var target = event.target.closest ? event.target.closest('a,button') : null;
    if (!target) return;
    var href = target.getAttribute('href') || '';
    var text = (target.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 100);
    var isTimerex = false;
    try {
      var targetUrl = new URL(href, window.location.href);
      isTimerex = targetUrl.hostname === 'timerex.net' || targetUrl.hostname.endsWith('.timerex.net');
    } catch (e) {}

    var params = {
      content_name: window.location.pathname,
      button_text: text,
      destination_url: href
    };
    if (isTimerex) {
      if (typeof window.aiKomonTrack === 'function') window.aiKomonTrack('Schedule', params);
      else window.aiKomonMeasure('Schedule', params);
      return;
    }

    if (href.indexOf('#contact') !== -1 || href.indexOf('index.html') !== -1 ||
        /無料相談|相談する|予約する|申し込む|診断/.test(text)) {
      if (typeof window.aiKomonTrackCustom === 'function') window.aiKomonTrackCustom('CTA_Click', params);
      else window.aiKomonMeasure('CTA_Click', params);
    }
  }, true);
})();
