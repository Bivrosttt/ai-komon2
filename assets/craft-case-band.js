/* 2026-07-23: 成果物ページ用「似た90日」ミニ帯。#craft-case-slot[data-case] に描画 */
(function () {
  var CASES = {
    manufacturing: {
      no: 'CASE 01',
      title: '部品加工メーカー',
      line: '日報・報告書が終業後に残る現場が、90日でどう変わったか。',
      href: 'cases.html#case-manufacturing'
    },
    realestate: {
      no: 'CASE 02',
      title: '地域密着の不動産',
      line: '反響返信の遅れと夜間取りこぼしが、90日でどう変わったか。',
      href: 'cases.html#case-realestate'
    },
    sales: {
      no: 'CASE 03',
      title: 'BtoB営業チーム',
      line: '提案準備と追客の属人化が、90日でどう変わったか。',
      href: 'cases.html#case-sales'
    }
  };

  var style = document.createElement('style');
  style.textContent = [
    '#craft-case-slot{margin:0;padding:0}',
    '.craft-case-band{border:1px solid #DDE4EC;border-radius:10px;background:linear-gradient(135deg,#F8FAFC,#EEF3F8);padding:20px 22px;margin:8px 0 28px}',
    '.craft-case-band .k{font-size:11px;font-weight:700;letter-spacing:.14em;color:#C9A227;margin-bottom:6px}',
    '.craft-case-band .row{display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap}',
    '.craft-case-band .no{font-size:11px;font-weight:700;color:#2D6CB5;letter-spacing:.08em}',
    '.craft-case-band h3{font-family:\'Noto Serif JP\',serif;font-size:18px;color:#0B2447;margin:2px 0 6px}',
    '.craft-case-band p{font-size:13px;color:#5B6B7F;line-height:1.65;max-width:560px}',
    '.craft-case-band a{display:inline-block;font-size:13px;font-weight:700;color:#0B2447;background:#C9A227;padding:10px 16px;border-radius:4px;text-decoration:none;white-space:nowrap}',
    '.craft-case-band a:hover{opacity:.88}'
  ].join('');
  document.head.appendChild(style);

  function mount(slot) {
    var key = (slot.getAttribute('data-case') || '').trim();
    var c = CASES[key];
    if (!c) { slot.style.display = 'none'; return; }
    slot.innerHTML =
      '<div class="craft-case-band">' +
      '<div class="k">この成果物が効く、90日の変化</div>' +
      '<div class="row"><div>' +
      '<div class="no">' + c.no + '</div>' +
      '<h3>' + c.title + '</h3>' +
      '<p>' + c.line + '</p>' +
      '</div><a href="' + c.href + '">90日をスクラブする →</a></div></div>';
  }

  function run() {
    document.querySelectorAll('#craft-case-slot, [data-craft-case]').forEach(function (el) {
      if (el.id !== 'craft-case-slot' && el.hasAttribute('data-craft-case')) {
        el.setAttribute('data-case', el.getAttribute('data-craft-case'));
      }
      mount(el);
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
})();
