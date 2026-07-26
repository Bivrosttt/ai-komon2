(function () {
  'use strict';

  var prompts = window.AI_KOMON_PROMPTS || [];
  var grid = document.getElementById('prompt-grid');
  var search = document.getElementById('prompt-search');
  var category = document.getElementById('prompt-category');
  var count = document.getElementById('prompt-count');
  var empty = document.getElementById('prompt-empty');
  var clear = document.getElementById('prompt-clear');
  var categories = Array.from(new Set(prompts.map(function (item) { return item.category; })));
  var searchHints = ['営業', 'メール', '商談', '提案', '議事録', '会議', '採用', '顧客', '問い合わせ', 'マーケティング', '広告', '業務改善', '自動化', '優先順位', 'FAQ', 'ナレッジ', '経営', 'KPI', '契約', '請求', '見積', '研修', '広報', '文章', 'SNS'];

  categories.forEach(function (name) {
    var option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    category.appendChild(option);
  });

  function esc(value) {
    return String(value || '').replace(/[&<>"']/g, function (char) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char];
    });
  }

  function searchable(item) {
    return [item.title, item.description, item.category, item.prompt].concat(item.tags || []).join(' ').toLowerCase();
  }

  function copyPrompt(text, button) {
    var done = function () {
      var original = button.textContent;
      button.textContent = 'コピーしました';
      button.setAttribute('aria-label', 'プロンプトをコピーしました');
      window.setTimeout(function () {
        button.textContent = original;
        button.setAttribute('aria-label', 'このプロンプトをコピー');
      }, 1600);
      if (typeof window.aiKomonMeasure === 'function') {
        window.aiKomonMeasure('lead_magnet_prompt_copy', { prompt_id: button.dataset.promptId || '' });
      }
    };

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done).catch(function () { fallbackCopy(text, done); });
      return;
    }
    fallbackCopy(text, done);
  }

  function fallbackCopy(text, done) {
    var area = document.createElement('textarea');
    area.value = text;
    area.setAttribute('readonly', '');
    area.style.position = 'fixed';
    area.style.opacity = '0';
    document.body.appendChild(area);
    area.select();
    try { document.execCommand('copy'); done(); } catch (e) {}
    document.body.removeChild(area);
  }

  function render() {
    var query = (search.value || '').trim().toLowerCase();
    var queryTerms = query.split(/\s+/).filter(Boolean);
    if (queryTerms.length === 1 && !queryTerms[0].match(/\s/) && queryTerms[0].length > 2) {
      var hintedTerms = searchHints.filter(function (term) { return queryTerms[0].indexOf(term) !== -1; });
      if (hintedTerms.length > 1) queryTerms = hintedTerms;
    }
    var selected = category.value;
    var visible = prompts.filter(function (item) {
      var haystack = searchable(item);
      var matchesQuery = !queryTerms.length || queryTerms.every(function (term) { return haystack.indexOf(term) !== -1; });
      return (!selected || item.category === selected) && matchesQuery;
    });

    grid.innerHTML = visible.map(function (item) {
      return '<article class="prompt-card" data-prompt-id="' + item.id + '">' +
        '<div class="prompt-card-top"><div><span class="prompt-category">' + esc(item.category) + '</span><h2>' + esc(item.title) + '</h2></div><span class="prompt-id">No.' + String(item.id).padStart(3, '0') + '</span></div>' +
        '<p class="prompt-description">' + esc(item.description) + '</p>' +
        '<details><summary>説明とプロンプトを見る</summary><div class="prompt-body"><p class="prompt-use"><strong>使いどころ:</strong> ' + esc(item.description) + '</p><pre>' + esc(item.prompt) + '</pre><div class="prompt-actions"><div class="prompt-tags">' + (item.tags || []).map(function (tag) { return '<span>#' + esc(tag) + '</span>'; }).join('') + '</div><button type="button" class="button small gold copy-prompt" data-prompt-id="' + item.id + '" aria-label="このプロンプトをコピー">コピー</button></div></div></details>' +
        '</article>';
    }).join('');

    empty.hidden = visible.length !== 0;
    count.textContent = visible.length + ' / ' + prompts.length + '件を表示中';
    clear.hidden = !query && !selected;
    grid.querySelectorAll('.copy-prompt').forEach(function (button) {
      var item = prompts.find(function (entry) { return String(entry.id) === String(button.dataset.promptId); });
      button.addEventListener('click', function () { copyPrompt(item.prompt, button); });
    });
  }

  function syncUrl() {
    try {
      var params = new URLSearchParams(window.location.search);
      if (search.value) params.set('q', search.value); else params.delete('q');
      if (category.value) params.set('category', category.value); else params.delete('category');
      var query = params.toString();
      window.history.replaceState({}, '', window.location.pathname + (query ? '?' + query : '') + '#prompt-library');
    } catch (e) {}
  }

  function update() { render(); syncUrl(); }
  search.addEventListener('input', update);
  category.addEventListener('change', update);
  clear.addEventListener('click', function () { search.value = ''; category.value = ''; update(); search.focus(); });

  try {
    var initial = new URLSearchParams(window.location.search);
    search.value = initial.get('q') || '';
    category.value = initial.get('category') || '';
  } catch (e) {}

  render();
}());
