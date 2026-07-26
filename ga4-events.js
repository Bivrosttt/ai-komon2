(function () {
  'use strict';

  function track(name, params) {
    if (typeof window.gtag !== 'function') return;
    try { window.gtag('event', name, params || {}); } catch (e) {}
  }

  function leadFrom() {
    try {
      var params = new URLSearchParams(window.location.search);
      return params.get('from') || sessionStorage.getItem('ai_komon_from') || 'direct';
    } catch (e) {
      return 'direct';
    }
  }

  function textOf(el) {
    return (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80);
  }

  window.aiKomonGaTrack = track;

  // measurement.js is the canonical handler on migrated pages. Keep this
  // listener as a fallback for legacy pages that still load ga4-events.js and
  // meta-pixel.js without measurement.js.
  document.addEventListener('click', function (event) {
    if (typeof window.aiKomonMeasure === 'function') return;

    var target = event.target && event.target.closest
      ? event.target.closest('a, button')
      : null;
    if (!target) return;
    if (event.__aiKomonLegacyGaClickTracked) return;
    event.__aiKomonLegacyGaClickTracked = true;

    var href = target.getAttribute('href') || '';
    var label = textOf(target);
    var common = {
      page: window.location.pathname,
      label: label,
      lead_from: leadFrom()
    };
    var isTimerex = href.indexOf('timerex.net') !== -1;
    var isCta = href.indexOf('#contact') !== -1 || /相談|予約/.test(label);

    if (isTimerex) {
      track('timerex_click', common);
      return;
    }

    if (/diagnosis\.html/i.test(href)) {
      track('diagnosis_cta_click', common);
    }

    if (isCta) {
      track('cta_click', Object.assign({ destination: href || 'button' }, common));
    }
  }, true);

  if (/\/diagnosis\.html$/.test(window.location.pathname)) {
    var started = false;
    document.querySelectorAll('.opt').forEach(function (button) {
      button.addEventListener('click', function () {
        if (started) return;
        started = true;
        track('diagnosis_start', { page: 'diagnosis.html', lead_from: leadFrom() });
      }, true);
    });

    var judge = document.getElementById('judge');
    if (judge) {
      judge.addEventListener('click', function () {
        window.setTimeout(function () {
          var level = document.getElementById('r-lv');
          var name = document.getElementById('r-name');
          track('diagnosis_complete', {
            level: level ? textOf(level) : '',
            level_name: name ? textOf(name) : '',
            lead_from: leadFrom()
          });
        }, 0);
      }, true);
    }
  }
}());
