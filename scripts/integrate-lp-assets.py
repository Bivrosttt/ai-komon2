#!/usr/bin/env python3
"""2026-07-22: LP約束デモ・works・導線の一括統合"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CASES_BAND = """
<section style="padding:28px 0 0;">
  <div class="container">
    <p style="font-size:13.5px;color:var(--gray);">似た会社の変化 → <a href="../cases.html" style="color:var(--blue);font-weight:700;">導入ストーリー</a>｜SaaS3本の整理 → <a href="../systems.html" style="color:var(--blue);font-weight:700;">systems.html</a></p>
  </div>
</section>
"""

LP_DEMOS_BLOCK = """
    <div class="shelf-head">
      <span class="lvbox" style="background:var(--gold);color:var(--navy-deep);">LP</span>
      <h2>LPの約束と、同じ名前のデモ</h2>
      <p>業種LPのヘッドコピーと1:1で刺さる体験デモ</p>
    </div>
    <div class="demo-grid">

      <a class="demo-card" data-ind="kensetsu" href="demo-hankyo-sla.html">
        <div class="demo-visual"><span class="m-badge">体験できます</span><div class="mock"><div class="m-line gold"></div><div class="m-line navy"></div><div class="m-line"></div></div></div>
        <div class="demo-body"><div class="cat">不動産・反響5分</div><h3>反響5分SLAタイマー</h3><p>lp-fudosan「反響5分」と同じ名前。SLAタイマー付きで一次返信の流れを体験。</p><span class="try">▶ デモを試す</span></div>
      </a>

      <a class="demo-card" data-ind="kensetsu sales" href="demo-followup-seq.html">
        <div class="demo-visual"><span class="m-badge">体験できます</span><div class="mock"><div class="m-line gold"></div><div class="m-line navy"></div><div class="m-line"></div></div></div>
        <div class="demo-body"><div class="cat">不動産・追客</div><h3>追客シーケンスAI</h3><p>Day3/7/14の追客メールを状況別に下書き。人は確認して送るだけ。</p><span class="try">▶ デモを試す</span></div>
      </a>

      <a class="demo-card" data-ind="sales" href="demo-brief-box.html">
        <div class="demo-visual"><span class="m-badge">体験できます</span><div class="mock"><div class="m-line gold"></div><div class="m-line navy"></div><div class="m-line"></div></div></div>
        <div class="demo-body"><div class="cat">営業・商談準備</div><h3>商談前リサーチボックス</h3><p>lp-komon-sales「商談準備」と同じ名前。企業調査と論点を1枚のブリーフに。</p><span class="try">▶ デモを試す</span></div>
      </a>

      <a class="demo-card" data-ind="sales" href="demo-proposal-gen.html">
        <div class="demo-visual"><span class="m-badge">体験できます</span><div class="mock"><div class="m-line gold"></div><div class="m-line navy"></div><div class="m-line"></div></div></div>
        <div class="demo-body"><div class="cat">営業・提案書</div><h3>提案書テンプレ生成AI</h3><p>御社テンプレに合わせたBtoB提案書のたたき台を、その場で生成。</p><span class="try">▶ デモを試す</span></div>
      </a>

      <a class="demo-card" data-ind="jimu" href="demo-expense.html">
        <div class="demo-visual"><span class="m-badge">体験できます</span><div class="mock"><div class="m-line gold"></div><div class="m-line navy"></div><div class="m-line"></div></div></div>
        <div class="demo-body"><div class="cat">管理部門・経費</div><h3>経費精算AI</h3><p>領収書と用途から経費申請の下書きまで。承認ルート付きで作成。</p><span class="try">▶ デモを試す</span></div>
      </a>

      <a class="demo-card" data-ind="jimu" href="demo-policy-search.html">
        <div class="demo-visual"><span class="m-badge">体験できます</span><div class="mock"><div class="m-line gold"></div><div class="m-line navy"></div><div class="m-line"></div></div></div>
        <div class="demo-body"><div class="cat">管理部門・規程</div><h3>稟議・規程検索AI</h3><p>就業規則・稟議規程から出典付きで回答。総務への同じ質問を減らす。</p><span class="try">▶ デモを試す</span></div>
      </a>

      <a class="demo-card" data-ind="kensetsu" href="demo-progress-match.html">
        <div class="demo-visual"><span class="m-badge">体験できます</span><div class="mock"><div class="m-line gold"></div><div class="m-line navy"></div><div class="m-line"></div></div></div>
        <div class="demo-body"><div class="cat">建設・請求</div><h3>出来高・請求突合AI</h3><p>出来高表と下請請求の差異を先にフラグ。人が数量・金額を確認。</p><span class="try">▶ デモを試す</span></div>
      </a>

      <a class="demo-card" data-ind="kensetsu" href="demo-safety-patrol.html">
        <div class="demo-visual"><span class="m-badge">体験できます</span><div class="mock"><div class="m-line gold"></div><div class="m-line navy"></div><div class="m-line"></div></div></div>
        <div class="demo-body"><div class="cat">建設・安全</div><h3>安全パトロールAI</h3><p>現場写真から指摘事項・是正期限・共有文案の下書きを作成。</p><span class="try">▶ デモを試す</span></div>
      </a>

      <a class="demo-card" data-ind="keiei" href="demo-ai-portal.html">
        <div class="demo-visual"><span class="m-badge">体験できます</span><div class="mock"><div class="m-line gold"></div><div class="m-line navy"></div><div class="m-line"></div></div></div>
        <div class="demo-body"><div class="cat">攻めAI・商品化</div><h3>AI診断ポータル</h3><p>既存サービスにAI診断を組み込んだBefore/After。ai-product向けPoC体験。</p><span class="try">▶ デモを試す</span></div>
      </a>

    </div>

"""

WORKS_BAND = """
<div class="feature-band" style="background:#fff;border-bottom:1px solid var(--line);">
  <div class="container">
    <span class="fb-label">NEW｜BtoB / 管理部門 / 攻めAI</span>
    <h2>営業・管理部門・商品化向けの成果物。</h2>
    <p class="fb-lead">工務店・不動産に加え、BtoB提案書、営業メールBefore/After、社内報、既存サービス+AIの設計例を追加しました。</p>
    <div class="works-grid">
      <a class="work-card" href="works-btob-proposal.html">
        <div class="work-visual" style="background:linear-gradient(135deg,#0B2447,#19376D);display:flex;align-items:center;justify-content:center;color:#fff;font-family:'Noto Serif JP',serif;font-weight:700;">BtoB提案書</div>
        <div class="work-body"><div class="cat">BtoB営業</div><h3>提案書PDF（御社ロゴ入り）</h3><p>16:9提案書。課題整理・90日ロードマップ・ROI試算まで。</p><span class="try">▶ サンプルを見る</span></div>
      </a>
      <a class="work-card" href="works-sales-mail.html">
        <div class="work-visual" style="background:linear-gradient(135deg,#2D6CB5,#0B2447);display:flex;align-items:center;justify-content:center;color:#fff;font-family:'Noto Serif JP',serif;font-weight:700;">Before/After</div>
        <div class="work-body"><div class="cat">BtoB営業</div><h3>営業メール Before/After</h3><p>追客3通のテンプレ化前後。パーソナライズ下書きへの変化。</p><span class="try">▶ サンプルを見る</span></div>
      </a>
      <a class="work-card" href="works-internal-news.html">
        <div class="work-visual" style="background:linear-gradient(135deg,#059669,#0B2447);display:flex;align-items:center;justify-content:center;color:#fff;font-family:'Noto Serif JP',serif;font-weight:700;">社内報</div>
        <div class="work-body"><div class="cat">管理部門</div><h3>社内報・就業規則改定案</h3><p>研修後に社員が作れる社内文書の品質サンプル。</p><span class="try">▶ サンプルを見る</span></div>
      </a>
      <a class="work-card" href="works-ai-service.html">
        <div class="work-visual" style="background:linear-gradient(135deg,#C9A227,#0B2447);display:flex;align-items:center;justify-content:center;color:#fff;font-family:'Noto Serif JP',serif;font-weight:700;">攻めAI</div>
        <div class="work-body"><div class="cat">商品化</div><h3>既存サービス + AI</h3><p>問い合わせフォームからAI診断ポータルへのBefore/After。</p><span class="try">▶ サンプルを見る</span></div>
      </a>
    </div>
  </div>
</div>
"""


def patch(path: Path, old: str, new: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        print(f"SKIP (not found): {path.name} :: {old[:50]}...")
        return False
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"patched: {path.name}")
    return True


def main():
    demos = ROOT / "demos.html"
    patch(
        demos,
        "    <div class=\"shelf-head goal\">\n      <span class=\"lvbox\">Lv.5</span>",
        LP_DEMOS_BLOCK + "    <div class=\"shelf-head goal\">\n      <span class=\"lvbox\">Lv.5</span>",
    )

    works = ROOT / "works.html"
    patch(
        works,
        "<section>\n  <div class=\"container\">\n    <div class=\"works-grid\">",
        WORKS_BAND + "\n<section>\n  <div class=\"container\">\n    <div class=\"works-grid\">",
    )

    index = ROOT / "index.html"
    patch(
        index,
        "<!-- 2026-07-22: 業種入口(for/)・導入ストーリー(cases.html)導線を追加 -->",
        "<!-- 2026-07-22: systems・攻めAI入口・LP約束デモ・無料ツール導線を追加 -->",
    )
    patch(
        index,
        "      <a class=\"ind-card is-live\" href=\"for/backoffice.html\">\n        <div class=\"ind-tag\">公開中</div>\n        <h3>管理部門</h3>\n        <p>経理・総務・採用前の業務整理。</p>\n        <span class=\"ind-go\">▶ 管理部門向けページを見る</span>\n      </a>\n    </div>",
        "      <a class=\"ind-card is-live\" href=\"for/backoffice.html\">\n        <div class=\"ind-tag\">公開中</div>\n        <h3>管理部門</h3>\n        <p>経理・総務・採用前の業務整理。</p>\n        <span class=\"ind-go\">▶ 管理部門向けページを見る</span>\n      </a>\n      <a class=\"ind-card is-live\" href=\"for/product.html\">\n        <div class=\"ind-tag\">公開中</div>\n        <h3>攻めのAI・商品化</h3>\n        <p>効率化で終わらせない。AIを御社の売り物に。</p>\n        <span class=\"ind-go\">▶ 商品化向けページを見る</span>\n      </a>\n    </div>",
    )
    patch(
        index,
        "    <div class=\"dt-more\" style=\"display:flex; gap:14px; justify-content:center; flex-wrap:wrap;\">\n      <a href=\"demos.html\" class=\"btn btn-navy\">31の構築デモをすべて見る →</a>\n      <a href=\"works.html\" class=\"btn btn-outline\">作品ショーケースを見る →</a>\n    </div>",
        "    <div class=\"dt-more\" style=\"display:flex; gap:14px; justify-content:center; flex-wrap:wrap;\">\n      <a href=\"demos.html\" class=\"btn btn-navy\">40の構築デモをすべて見る →</a>\n      <a href=\"works.html\" class=\"btn btn-outline\">作品ショーケースを見る →</a>\n      <a href=\"systems.html\" class=\"btn btn-outline\">SaaS3本を整理して見る →</a>\n      <a href=\"tools/\" class=\"btn btn-outline\">無料試算ツール →</a>\n    </div>",
    )

    cases = ROOT / "cases.html"
    patch(
        cases,
        "<!-- 2026-07-22: 匿名化した導入ストーリー事例ページ（公式トーン） -->",
        "<!-- 2026-07-22: monitor.html連携・新デモへのリンクを追加 -->",
    )
    patch(
        cases,
        "    <div class=\"disclaimer\">※すべて架空・匿名化したサンプルストーリーです。実在の顧客事例ではありません。効果や削減時間を保証するものではありません。</div>",
        "    <div class=\"disclaimer\">※すべて架空・匿名化したサンプルストーリーです。実在の顧客事例ではありません。効果や削減時間を保証するものではありません。<br><br>本物の事例は <a href=\"monitor.html\" style=\"color:var(--blue);font-weight:700;\">モニター企業募集</a> 完了後にここへ差し替え予定です。</div>",
    )
    patch(
        cases,
        "<a href=\"demo-quote.html\">見積書デモ</a>\n            <a href=\"demo-slides.html\">資料スライドデモ</a>",
        "<a href=\"demo-brief-box.html\">商談前リサーチ</a>\n            <a href=\"demo-proposal-gen.html\">提案書生成</a>",
    )

    monitor = ROOT / "monitor.html"
    patch(
        monitor,
        "<section class=\"cta\" id=\"apply\">",
        "<section style=\"padding:40px 0;background:var(--bg-soft);border-block:1px solid var(--line);\"><div class=\"container\"><p style=\"font-size:14px;color:var(--gray);\">モニター完了後のストーリーは <a href=\"cases.html\" style=\"color:var(--blue);font-weight:700;\">cases.html</a> に掲載予定。現状は匿名サンプルをご覧ください。</p></div></section>\n<section class=\"cta\" id=\"apply\">",
    )

    ai_product = ROOT / "ai-product.html"
    patch(
        ai_product,
        "    <div class=\"hero-ctas\">\n      <a href=\"index.html#contact\" class=\"btn btn-gold\">無料相談を予約する（30分）</a>\n      <a href=\"works.html\" class=\"btn btn-outline\" style=\"border-color:rgba(255,255,255,.5);color:#fff;\">作品ショーケースを見る</a>\n    </div>",
        "    <div class=\"hero-ctas\">\n      <a href=\"for/product.html\" class=\"btn btn-outline\" style=\"border-color:rgba(255,255,255,.5);color:#fff;\">攻めAI入口ページ →</a>\n      <a href=\"index.html?from=ai-product#contact\" class=\"btn btn-gold\">無料相談を予約する（30分）</a>\n      <a href=\"demo-ai-portal.html\" class=\"btn btn-outline\" style=\"border-color:rgba(255,255,255,.5);color:#fff;\">AI診断ポータルデモ</a>\n    </div>",
    )

    data = ROOT / "data.html"
    patch(
        data,
        "<!-- 5. CTA -->\n<section class=\"cta\" id=\"contact\">",
        "<section style=\"padding:56px 0;background:var(--bg-soft);border-top:1px solid var(--line);\"><div class=\"container\"><h2 style=\"font-family:'Noto Serif JP',serif;color:var(--navy);font-size:24px;margin-bottom:10px;\">相談前に、数字で整理する。</h2><p style=\"color:var(--gray);font-size:14px;margin-bottom:18px;\">会議コスト・損益分岐・粗利シミュレーション——登録不要の無料ツールです。</p><p style=\"display:flex;flex-wrap:wrap;gap:10px;font-size:13px;\"><a href=\"tools/meeting-cost-calculator/\" style=\"color:var(--blue);font-weight:700;\">会議コスト計算</a><a href=\"tools/break-even-calculator/\" style=\"color:var(--blue);font-weight:700;\">損益分岐点</a><a href=\"tools/gross-profit-simulator/\" style=\"color:var(--blue);font-weight:700;\">粗利シミュレーター</a><a href=\"tools/\" style=\"color:var(--blue);font-weight:700;\">すべての無料ツール →</a></p></div></section>\n<!-- 5. CTA -->\n<section class=\"cta\" id=\"contact\">",
    )

    lp_roi = ROOT / "lp-roi.html"
    patch(
        lp_roi,
        "<section class=\"cta\" id=\"contact\">",
        "<section style=\"padding:48px 0;background:#F4F7FA;border-top:1px solid #DDE4EC;\"><div class=\"container\" style=\"max-width:860px;margin:0 auto;padding:0 24px;\"><p style=\"font-size:14px;color:#5B6B7F;margin-bottom:12px;\">試算を深める無料ツール:</p><p style=\"display:flex;flex-wrap:wrap;gap:12px;font-size:13px;\"><a href=\"tools/gross-profit-simulator/\" style=\"color:#2D6CB5;font-weight:700;\">粗利シミュレーター</a><a href=\"tools/break-even-calculator/\" style=\"color:#2D6CB5;font-weight:700;\">損益分岐点</a><a href=\"tools/ai-payback-calculator/\" style=\"color:#2D6CB5;font-weight:700;\">AI回収期間</a><a href=\"data.html\" style=\"color:#2D6CB5;font-weight:700;\">データ試算ページ</a></p></div></section>\n<section class=\"cta\" id=\"contact\">",
    )

    lp_cost = ROOT / "lp-cost.html"
    patch(
        lp_cost,
        "<section class=\"final-cta\">",
        "<section style=\"padding:40px 0;background:#fff;border-top:1px solid #e8e8e8;\"><div class=\"container\" style=\"max-width:860px;margin:0 auto;padding:0 24px;\"><p style=\"font-size:14px;color:#666;margin-bottom:10px;\">採用 vs 顧問の試算を補うツール:</p><p style=\"display:flex;flex-wrap:wrap;gap:12px;font-size:13px;\"><a href=\"tools/break-even-calculator/\" style=\"color:#1769aa;font-weight:700;\">損益分岐点計算</a><a href=\"tools/meeting-cost-calculator/\" style=\"color:#1769aa;font-weight:700;\">会議コスト計算</a><a href=\"tools/ai-payback-calculator/\" style=\"color:#1769aa;font-weight:700;\">AI回収期間</a></p></div></section>\n<section class=\"final-cta\">",
    )

    tools_index = ROOT / "tools/index.html"
    new_tools = """
          <li>
            <a class="tool-card" href="./meeting-cost-calculator/">
              <div class="card-main"><span class="category">MEETING COST</span><h3>会議コスト計算</h3></div>
              <span class="card-arrow" aria-hidden="true">↗</span>
            </a>
          </li>
          <li>
            <a class="tool-card" href="./break-even-calculator/">
              <div class="card-main"><span class="category">FINANCE</span><h3>損益分岐点計算</h3></div>
              <span class="card-arrow" aria-hidden="true">↗</span>
            </a>
          </li>
          <li>
            <a class="tool-card" href="./gross-profit-simulator/">
              <div class="card-main"><span class="category">MARGIN</span><h3>粗利シミュレーター</h3></div>
              <span class="card-arrow" aria-hidden="true">↗</span>
            </a>
          </li>"""
    patch(
        tools_index,
        '      {"@type":"ListItem","position":6,"name":"請求書かんたん作成","url":"https://ai-komon.bivrost.co.jp/tools/invoice-maker/"}\n    ]',
        '      {"@type":"ListItem","position":6,"name":"請求書かんたん作成","url":"https://ai-komon.bivrost.co.jp/tools/invoice-maker/"},\n      {"@type":"ListItem","position":7,"name":"会議コスト計算","url":"https://ai-komon.bivrost.co.jp/tools/meeting-cost-calculator/"},\n      {"@type":"ListItem","position":8,"name":"損益分岐点計算","url":"https://ai-komon.bivrost.co.jp/tools/break-even-calculator/"},\n      {"@type":"ListItem","position":9,"name":"粗利シミュレーター","url":"https://ai-komon.bivrost.co.jp/tools/gross-profit-simulator/"}\n    ]',
    )
    patch(
        tools_index,
        "          <li>\n            <a class=\"tool-card\" href=\"./invoice-maker/\">",
        new_tools + "\n          <li>\n            <a class=\"tool-card\" href=\"./invoice-maker/\">",
    )

    for name in ["kensetsu", "fudosan", "sales", "backoffice"]:
        p = ROOT / "for" / f"{name}.html"
        patch(p, "</section>\n\n<section class=\"lp-band\">", "</section>\n" + CASES_BAND + "\n<section class=\"lp-band\">")

    # LP-aligned demo swaps
    patch(ROOT / "for/fudosan.html", 'href="../demo-inquiry.html"', 'href="../demo-hankyo-sla.html"')
    patch(ROOT / "for/fudosan.html", "<h3>問い合わせ返信AI</h3>", "<h3>反響5分SLAタイマー</h3>")
    patch(ROOT / "for/fudosan.html", 'href="../demo-staging.html"', 'href="../demo-followup-seq.html"')
    patch(ROOT / "for/fudosan.html", "<h3>バーチャルステージングAI</h3>", "<h3>追客シーケンスAI</h3>")

    patch(ROOT / "for/sales.html", 'href="../demo-quote.html"', 'href="../demo-brief-box.html"')
    patch(ROOT / "for/sales.html", "<h3>見積書AI</h3>", "<h3>商談前リサーチボックス</h3>")
    patch(ROOT / "for/sales.html", 'href="../demo-slides.html"', 'href="../demo-proposal-gen.html"')
    patch(ROOT / "for/sales.html", "<h3>資料スライドAI</h3>", "<h3>提案書テンプレ生成AI</h3>")
    patch(ROOT / "for/sales.html", 'href="../works-slides.html"', 'href="../works-btob-proposal.html"')
    patch(ROOT / "for/sales.html", "<h3>動くプレゼン（会社紹介）</h3>", "<h3>BtoB提案書PDF</h3>")
    patch(ROOT / "for/sales.html", 'href="../works/proposal-deck.pdf"', 'href="../works-sales-mail.html"')
    patch(ROOT / "for/sales.html", "<h3>顧客提案スライド</h3>", "<h3>営業メール Before/After</h3>")

    patch(ROOT / "for/backoffice.html", 'href="../demo-minutes.html"', 'href="../demo-expense.html"')
    patch(ROOT / "for/backoffice.html", "<h3>議事録AI</h3>", "<h3>経費精算AI</h3>")
    patch(ROOT / "for/backoffice.html", 'href="../demo-keiri.html"', 'href="../demo-policy-search.html"')
    patch(ROOT / "for/backoffice.html", "<h3>AI経理部</h3>", "<h3>稟議・規程検索AI</h3>")
    patch(ROOT / "for/backoffice.html", 'href="../works/user-manual.pdf"', 'href="../works-internal-news.html"')
    patch(ROOT / "for/backoffice.html", "<h3>図解入り操作マニュアル</h3>", "<h3>社内報・就業規則改定案</h3>")

    patch(ROOT / "for/kensetsu.html", 'href="../demo-quote.html"', 'href="../demo-progress-match.html"')
    patch(ROOT / "for/kensetsu.html", "<h3>見積書AI</h3>", "<h3>出来高・請求突合AI</h3>")
    patch(ROOT / "for/kensetsu.html", 'href="../demo-report.html"', 'href="../demo-safety-patrol.html"')
    patch(ROOT / "for/kensetsu.html", "<h3>日報 自動集計ダッシュボード</h3>", "<h3>安全パトロールAI</h3>")

    strategy = ROOT / "docs/strategy-visual.html"
    patch(
        strategy,
        "<!-- 2026-07-22: AI顧問室サイト再設計の方針を、現状→課題→これから作るものを視覚的に説明する内部用ページ -->",
        "<!-- 2026-07-22: 方針マップ（2026-07-22時点で入口・cases・LPデモ・systems・攻めAIレーン完了反映） -->",
    )
    patch(
        strategy,
        "            <div class=\"node highlight\">業種向け入口 1枚<small>これから作る</small></div>",
        "            <div class=\"node highlight\">業種向け入口 4枚<small>for/* 完了</small></div>",
    )
    patch(
        strategy,
        "            <div class=\"node\">事例 2〜3本<small>これから作る</small></div>",
        "            <div class=\"node\">事例 3本<small>cases.html 完了</small></div>",
    )
    patch(
        strategy,
        "      <h2>これから作ろうとしているもの</h2>\n      <p>新しく31本増やすのではなく、「入口」と「証拠」を足して、今ある資産をつなぎます。</p>",
        "      <h2>完了したもの（2026-07-22）</h2>\n      <p>入口・cases・LP約束デモ9本・works4本・systems・攻めAI入口・無料ツール3本まで反映済み。</p>",
    )
    patch(
        strategy,
        "      <div class=\"panel-head\"><span class=\"badge plan\">新規ページ案</span> 業種・役割向け「入口ページ」4枚</div>",
        "      <div class=\"panel-head\"><span class=\"badge goal\">完了</span> 業種・役割向け「入口ページ」4枚 + 攻めAI</div>",
    )
    patch(
        strategy,
        "        <div class=\"panel-head\"><span class=\"badge plan\">新規ページ案</span> cases.html（導入ストーリー）</div>",
        "        <div class=\"panel-head\"><span class=\"badge goal\">完了</span> cases.html（導入ストーリー）</div>",
    )
    patch(
        strategy,
        "        <div class=\"panel-head\"><span class=\"badge plan\">既存資産の整理</span> つなぎ直し</div>",
        "        <div class=\"panel-head\"><span class=\"badge goal\">完了</span> 既存資産の整理</div>",
    )
    patch(
        strategy,
        "      <a href=\"../works.html\">works.html</a>",
        "      <a href=\"../works.html\">works.html</a> · <a href=\"../systems.html\">systems.html</a> · <a href=\"../for/product.html\">for/product.html</a> · <a href=\"../cases.html\">cases.html</a>",
    )

    lp_list = ROOT / "lp-list.html"
    patch(
        lp_list,
        "<!-- 2026-07-22: 社内専用LP武器庫。業種LP旧版は lp/archive/*-legacy.html に退避 -->",
        "<!-- 2026-07-22: 社内専用LP武器庫。お客さん向けは for/* + cases + LP1本 -->",
    )


if __name__ == "__main__":
    main()
