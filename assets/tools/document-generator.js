(function () {
  'use strict';

  var root = document.querySelector('[data-document-tool]');
  if (!root) return;

  var kind = root.getAttribute('data-document-tool');
  var config = kind === 'invoice'
    ? { prefix: '請求書', secondaryLabel: '支払期限', secondaryId: 'dueDate' }
    : { prefix: '見積書', secondaryLabel: '有効期限', secondaryId: 'validUntil' };

  var form = document.getElementById('tool-form');
  var items = document.getElementById('line-items');
  var number = new Intl.NumberFormat('ja-JP');

  function value(id) {
    var element = document.getElementById(id);
    return element ? element.value.trim() : '';
  }

  function escapeHtml(input) {
    return String(input || '').replace(/[&<>"']/g, function (character) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character];
    });
  }

  function money(amount) {
    return number.format(Math.round(amount || 0));
  }

  function defaultFilename() {
    var date = new Date();
    var y = date.getFullYear();
    var m = String(date.getMonth() + 1).padStart(2, '0');
    var d = String(date.getDate()).padStart(2, '0');
    return config.prefix + '_' + y + m + d;
  }

  function addLine(description, quantity, unitPrice) {
    var row = document.createElement('div');
    row.className = 'line-row';
    row.innerHTML = '<label class="field"><span>品目</span><input class="line-description" type="text" value="' + escapeHtml(description || '') + '" placeholder="例：業務改善支援" aria-label="品目"></label>'
      + '<label class="field"><span>数量</span><input class="line-quantity" type="number" min="0" step="1" value="' + (quantity || 1) + '" aria-label="数量"></label>'
      + '<label class="field"><span>単価（円）</span><input class="line-price" type="number" min="0" step="100" value="' + (unitPrice || 0) + '" aria-label="単価（円）"></label>'
      + '<button type="button" class="button-quiet remove-line" aria-label="この明細を削除">削除</button>';
    items.appendChild(row);
  }

  function collectLines() {
    return Array.from(items.querySelectorAll('.line-row')).map(function (row) {
      var quantity = Number(row.querySelector('.line-quantity').value) || 0;
      var unitPrice = Number(row.querySelector('.line-price').value) || 0;
      return {
        description: row.querySelector('.line-description').value.trim(),
        quantity: quantity,
        unitPrice: unitPrice,
        amount: quantity * unitPrice
      };
    }).filter(function (line) { return line.description || line.amount; });
  }

  function updatePreview() {
    var lines = collectLines();
    var subtotal = lines.reduce(function (total, line) { return total + line.amount; }, 0);
    var taxRate = Number(value('taxRate')) || 0;
    var tax = Math.floor(subtotal * taxRate / 100);
    var total = subtotal + tax;
    var recipient = value('recipientName') || '（宛先名）';
    var issuer = [value('issuerName'), value('issuerAddress'), value('issuerContact')].filter(Boolean).join('\n') || '（発行者情報）';
    var rows = lines.length ? lines.map(function (line) {
      return '<tr><td>' + escapeHtml(line.description || '（品目未入力）') + '</td><td class="number">' + money(line.quantity) + '</td><td class="number">' + money(line.unitPrice) + '</td><td class="number">' + money(line.amount) + '</td></tr>';
    }).join('') : '<tr><td colspan="4" class="muted">明細を入力してください</td></tr>';

    document.getElementById('preview-recipient').textContent = recipient;
    document.getElementById('preview-issuer').textContent = issuer;
    document.getElementById('preview-subject').textContent = value('subject') ? '件名：' + value('subject') : '';
    document.getElementById('preview-number').textContent = value('documentNumber') ? 'No. ' + value('documentNumber') : '';
    document.getElementById('preview-date').textContent = value('issueDate') || '—';
    document.getElementById('preview-secondary-label').textContent = config.secondaryLabel;
    document.getElementById('preview-secondary').textContent = value(config.secondaryId) || '—';
    document.getElementById('preview-items').innerHTML = rows;
    document.getElementById('preview-subtotal').textContent = money(subtotal) + ' 円';
    document.getElementById('preview-tax').textContent = money(tax) + ' 円（' + taxRate + '%）';
    document.getElementById('preview-total').textContent = money(total) + ' 円';
    document.getElementById('preview-notes').textContent = value('notes') || '備考：';
  }

  function safeFilename() {
    var raw = value('filename') || defaultFilename();
    var clean = raw.replace(/[\\/:*?"<>|]/g, '_').replace(/\s+/g, ' ').trim() || defaultFilename();
    return clean.replace(/\.pdf$/i, '') + '.pdf';
  }

  function setStatus(message) {
    var status = document.getElementById('pdf-status');
    if (status) status.textContent = message;
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    updatePreview();
    document.getElementById('document-preview').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  document.getElementById('add-line').addEventListener('click', function () {
    addLine('', 1, 0);
    updatePreview();
    items.lastElementChild.querySelector('.line-description').focus();
  });

  items.addEventListener('click', function (event) {
    if (!event.target.classList.contains('remove-line')) return;
    var rows = items.querySelectorAll('.line-row');
    if (rows.length === 1) {
      rows[0].querySelector('.line-description').value = '';
      rows[0].querySelector('.line-quantity').value = '1';
      rows[0].querySelector('.line-price').value = '0';
    } else {
      event.target.closest('.line-row').remove();
    }
    updatePreview();
  });

  root.addEventListener('input', updatePreview);
  root.addEventListener('change', updatePreview);

  function openPrint(filename) {
    var originalTitle = document.title;
    document.title = filename.replace(/\.pdf$/i, '');
    setStatus('印刷画面を開きます。「PDFに保存」を選ぶと「' + filename + '」で保存できます。');
    window.print();
    window.setTimeout(function () { document.title = originalTitle; }, 1000);
  }

  function collectStyles() {
    return Array.from(document.styleSheets).map(function (sheet) {
      try { return Array.from(sheet.cssRules).map(function (rule) { return rule.cssText; }).join('\n'); }
      catch (error) { return ''; }
    }).join('\n').replace(/<\/style/gi, '<\\/style');
  }

  async function renderPreviewToDataUrl() {
    var preview = document.getElementById('document-preview');
    var rect = preview.getBoundingClientRect();
    var clone = preview.cloneNode(true);
    clone.removeAttribute('id');
    clone.style.boxShadow = 'none';
    clone.style.background = '#fff';
    var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="' + rect.width + '" height="' + rect.height + '" viewBox="0 0 ' + rect.width + ' ' + rect.height + '"><foreignObject width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml" style="width:' + rect.width + 'px;height:' + rect.height + 'px;background:#fff"><style>' + collectStyles() + '</style>' + clone.outerHTML + '</div></foreignObject></svg>';
    var image = new Image();
    var url = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
    await new Promise(function (resolve, reject) { image.onload = resolve; image.onerror = reject; image.src = url; });
    var canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.ceil(rect.width * 2));
    canvas.height = Math.max(1, Math.ceil(rect.height * 2));
    var context = canvas.getContext('2d');
    context.fillStyle = '#fff';
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    return { dataUrl: canvas.toDataURL('image/jpeg', 0.96), width: rect.width, height: rect.height };
  }

  async function savePdf(filename) {
    if (!window.jspdf || !window.jspdf.jsPDF) return false;
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    var image = await renderPreviewToDataUrl();
    var pdf = new window.jspdf.jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' });
    var maxWidth = 190;
    var maxHeight = 277;
    var scale = Math.min(maxWidth / image.width, maxHeight / image.height);
    var width = image.width * scale;
    var height = image.height * scale;
    pdf.addImage(image.dataUrl, 'JPEG', (210 - width) / 2, (297 - height) / 2, width, height, undefined, 'FAST');
    pdf.save(filename);
    return true;
  }

  document.getElementById('download-pdf').addEventListener('click', async function () {
    updatePreview();
    var filename = safeFilename();
    if (window.gtag) window.gtag('event', 'tool_download', { document_type: kind, file_type: 'pdf' });
    setStatus('PDFを作成しています…');
    try {
      if (await savePdf(filename)) {
        setStatus('PDFをダウンロードしました：' + filename);
      } else {
        openPrint(filename);
      }
    } catch (error) {
      openPrint(filename);
    }
  });

  document.getElementById('print-document').addEventListener('click', function () {
    openPrint(safeFilename());
  });

  var filenameInput = document.getElementById('filename');
  if (!filenameInput.value) filenameInput.value = defaultFilename();
  updatePreview();
}());
