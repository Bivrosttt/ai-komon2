(function () {
  'use strict';

  if (typeof window.gtag !== 'function') return;

  function track(name, params) {
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
