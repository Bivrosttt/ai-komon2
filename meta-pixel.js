(function () {
  'use strict';

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
    var keys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'from'];
    var params = new URLSearchParams(window.location.search);
    keys.forEach(function (key) {
      var value = params.get(key);
      if (value) {
        try { sessionStorage.setItem('ak_' + key, value); } catch (e) {}
      }
      try {
        value = value || sessionStorage.getItem('ak_' + key);
      } catch (e) {}
      if (value) result[key] = value;
    });
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

  document.addEventListener('click', function (event) {
    var target = event.target.closest ? event.target.closest('a,button') : null;
    if (!target) return;

    var href = target.getAttribute('href') || '';
    var text = (target.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 100);

    if (href.indexOf('timerex.net') !== -1) {
      window.aiKomonTrack('Schedule', { content_name: window.location.pathname });
      return;
    }

    if (href.indexOf('#contact') !== -1 || href.indexOf('index.html') !== -1 ||
        /無料相談|相談する|予約する|申し込む|診断/.test(text)) {
      window.aiKomonTrackCustom('CTA_Click', {
        content_name: window.location.pathname,
        button_text: text
      });
    }
  });
})();
