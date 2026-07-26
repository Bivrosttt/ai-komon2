(function () {
  'use strict';

  var config = window.AI_KOMON_MEASUREMENT_CONFIG || {};
  var productionHosts = config.productionHosts || ['ai-komon.bivrost.co.jp', 'www.ai-komon.bivrost.co.jp'];
  if (productionHosts.indexOf(window.location.hostname) === -1) return;

  var pixelId = window.AI_KOMON_META_PIXEL_ID;
  if (!pixelId || window.__AI_KOMON_META_PIXEL_INITIALIZED) return;
  window.__AI_KOMON_META_PIXEL_INITIALIZED = true;

  // Meta's browser pixel base code.
  !(function (f, b, e, v, n, t, s) {
    if (f.fbq) return;
    n = f.fbq = function () {
      n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
    };
    if (!f._fbq) f._fbq = n;
    n.push = n;
    n.loaded = true;
    n.version = '2.0';
    n.queue = [];
    t = b.createElement(e);
    t.async = true;
    t.src = v;
    s = b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t, s);
  })(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

  window.fbq('init', pixelId);
  window.fbq('track', 'PageView');

  function getAttribution() {
    var result = {};
    var keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'utm_id', 'fbclid', 'gclid', 'from'];
    var params = new URLSearchParams(window.location.search);
    keys.forEach(function (key) {
      var queryValue = params.get(key);
      var value = queryValue;
      var storedValue = '';
      try { storedValue = sessionStorage.getItem('ak_' + key) || ''; } catch (e) {}
      if (queryValue && (key === 'from' || !storedValue)) {
        try { sessionStorage.setItem('ak_' + key, queryValue); } catch (e) {}
      }
      value = queryValue || storedValue;
      if (value) result[key] = value;
    });
    if (result.fbclid && !result.utm_source) result.utm_source = 'meta';
    if (result.fbclid && !result.utm_medium) result.utm_medium = 'paid_social';
    result.attribution_status = result.utm_campaign || result.utm_content ? 'explicit' :
      (result.fbclid ? 'inferred_meta' : 'direct_or_unknown');
    return result;
  }

  function eventParams(params) {
    var merged = getAttribution();
    Object.keys(params || {}).forEach(function (key) { merged[key] = params[key]; });
    return merged;
  }

  window.aiKomonTrack = function (eventName, params) {
    if (typeof window.fbq === 'function') {
      window.fbq('track', eventName, eventParams(params));
    }
  };

  window.aiKomonTrackCustom = function (eventName, params) {
    if (typeof window.fbq === 'function') {
      window.fbq('trackCustom', eventName, eventParams(params));
    }
  };

  window.fbq('track', 'ViewContent', eventParams({
    content_name: window.location.pathname,
    content_type: 'website'
  }));

})();
