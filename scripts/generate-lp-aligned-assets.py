#!/usr/bin/env python3
"""2026-07-22: LP約束1:1デモ・works成果物ページを一括生成"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEMO_CSS = """
  :root { --navy:#0B2447; --navy-deep:#071A35; --blue:#2D6CB5; --gold:#C9A227; --ink:#1A2433; --gray:#5B6B7F; --line:#DDE4EC; --bg:#F4F7FA; --white:#FFF; --ok:#2F7A4F; --warn:#B45309; }
  *{margin:0;padding:0;box-sizing:border-box} body{font-family:'Noto Sans JP',sans-serif;color:var(--ink);line-height:1.85;background:var(--white)}
  h1,h2{font-family:'Noto Serif JP',serif;line-height:1.45} a{text-decoration:none;color:inherit}
  .container{max-width:960px;margin:0 auto;padding:0 24px}
  header{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.96);border-bottom:1px solid var(--line)}
  .header-inner{display:flex;align-items:center;justify-content:space-between;height:64px;gap:12px}
  .logo{font-family:'Noto Serif JP',serif;font-size:20px;font-weight:700;color:var(--navy)}
  .back{font-size:13px;color:var(--blue);font-weight:600}
  .hero{background:linear-gradient(135deg,var(--navy-deep),var(--navy));color:#fff;padding:72px 0 56px}
  .tag{display:inline-block;border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:5px 14px;font-size:12px;color:#dce6f5;margin-bottom:16px}
  .hero h1{font-size:clamp(26px,4vw,36px);margin-bottom:12px}.hero h1 em{font-style:normal;color:var(--gold)}
  .hero p{color:#c7d3e4;max-width:640px;font-size:15px}
  .note{background:var(--bg);border-bottom:1px solid var(--line);padding:14px 0;font-size:13px;color:var(--gray)}
  .panel{margin:40px 0;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--white)}
  .panel-head{background:var(--navy);color:#fff;padding:16px 20px;font-size:14px;font-weight:700}
  .panel-body{padding:22px 20px}
  .row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:14px}
  .chip{border:1px solid var(--line);border-radius:999px;padding:8px 14px;font-size:13px;cursor:pointer;background:#fff}
  .chip.active{background:var(--navy);color:#fff;border-color:var(--navy)}
  .out{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:16px;min-height:120px;font-size:14px;white-space:pre-wrap}
  .stat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:14px}
  .stat{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:12px;text-align:center}
  .stat b{display:block;font-family:'Noto Serif JP',serif;font-size:22px;color:var(--navy)}
  .stat small{font-size:11px;color:var(--gray)}
  .btn{display:inline-block;padding:12px 26px;border-radius:4px;font-weight:700;font-size:14px;border:none;cursor:pointer;font-family:inherit}
  .btn-gold{background:var(--gold);color:var(--navy-deep)} .btn-navy{background:var(--navy);color:#fff}
  .cta{text-align:center;padding:56px 0;background:var(--bg);border-top:1px solid var(--line)}
  footer{background:var(--navy-deep);color:#9fb0c7;font-size:13px;padding:28px 0;text-align:center}
  footer a{text-decoration:underline}
  @media(max-width:720px){.stat-grid{grid-template-columns:1fr}}
"""

DEMOS = [
    {
        "file": "demo-hankyo-sla.html",
        "title": "反響5分SLAタイマー 体験デモ",
        "meta": "不動産反響の一次返信を5分以内に。SLAタイマーと返信下書きを体験できるデモ。",
        "hero": "反響が来た瞬間、<em>5分以内</em>に一次返信。",
        "sub": "lp-fudosan.html の「反響5分」と同じ名前のデモ。問い合わせ受信から返信案までの流れを、SLAタイマー付きで体験できます。",
        "panel": "反響SLAダッシュボード（サンプル）",
        "chips": ["内見希望・マンション", "賃貸・初期費用", "売却査定・戸建"],
        "outputs": [
            "⏱ SLA: 04:32 残り（目標5分）\n📩 反響: 内見希望（港区・2LDK・予算15万）\n✉ 返信案:\n「お問い合わせありがとうございます。本日17:00 / 明日10:00に内見枠をご用意できます。ご都合をお知らせください。」",
            "⏱ SLA: 02:18 残り\n📩 反響: 賃貸・初期費用の質問\n✉ 返信案:\n「初期費用の目安は家賃の4〜5ヶ月分です。物件URLをお送りいただければ、内訳表付きでご案内します。」",
            "⏱ SLA: 03:05 残り\n📩 反響: 売却査定（築18年・戸建）\n✉ 返信案:\n「査定のため、延床面積と築年を確認させてください。オンライン査定と現地査定、どちらをご希望ですか？」",
        ],
        "stats": [("4:32", "平均一次返信"), ("92%", "5分以内率"), ("0件", "返信漏れ")],
    },
    {
        "file": "demo-followup-seq.html",
        "title": "追客シーケンスAI 体験デモ",
        "meta": "不動産・BtoBの追客メールを、状況別シーケンスで自動下書き。",
        "hero": "追客は、<em>型</em>で回す。",
        "sub": "反響後3日・7日・14日の追客メールを、顧客の温度感に合わせて下書き。人は確認して送るだけ。",
        "panel": "追客シーケンス（サンプル）",
        "chips": ["Day3・内見後", "Day7・資料送付後", "Day14・休眠"],
        "outputs": [
            "Day3｜件名: 内見のご感想をお聞かせください\n本文: 先日は内見ありがとうございました。気になる点（日当たり・収納・騒音）があれば、類似物件もご提案します。",
            "Day7｜件名: ご検討状況の確認\n本文: 資料はご確認いただけましたでしょうか。比較検討中の物件があれば、条件をお知らせください。",
            "Day14｜件名: タイミングが合えば\n本文: 一度ご連絡のみ。近隣で新着が出た際に、優先的にお知らせします。",
        ],
        "stats": [("3通", "自動下書き"), ("12分", "確認時間"), ("+18%", "返信率目安")],
    },
    {
        "file": "demo-brief-box.html",
        "title": "商談前リサーチボックス 体験デモ",
        "meta": "BtoB商談前に、企業情報・論点・質問案を1枚にまとめる体験デモ。",
        "hero": "商談前の30分を、<em>3分の確認</em>に。",
        "sub": "lp-komon-sales.html の「商談準備」と同じ名前のデモ。企業調査と仮説を、商談ブリーフ1枚に。",
        "panel": "商談ブリーフ（サンプル）",
        "chips": ["Sテクノロジー", "Aホールディングス", "K製作所"],
        "outputs": [
            "■ Sテクノロジー（従業員120名）\n課題仮説: 営業の提案品質が担当者依存\n確認論点: 決裁者 / 予算時期 / 既存CRM\n質問案: 「商談後の議事録入力に何分かかっていますか？」",
            "■ Aホールディングス\n課題仮説: グループ横断の情報共有\n確認論点: 子会社数 / 共有ルール\n質問案: 「同じ質問が各社に来ていませんか？」",
            "■ K製作所\n課題仮説: 見積の下準備が属人化\n確認論点: 月間見積件数 / テンプレ有無\n質問案: 「過去案件を探すのに誰に聞いていますか？」",
        ],
        "stats": [("28分", "準備時間削減"), ("1枚", "共通ブリーフ"), ("3社", "同時準備可")],
    },
    {
        "file": "demo-proposal-gen.html",
        "title": "提案書テンプレ生成AI 体験デモ",
        "meta": "御社テンプレに合わせたBtoB提案書のたたき台を、その場で生成。",
        "hero": "白紙の提案書から、<em>初稿</em>へ。",
        "sub": "商談メモと勝ち筋から、構成・見出し・本文のたたき台を生成。人が磨き込む前提の下書きです。",
        "panel": "提案書たたき台（サンプル）",
        "chips": ["IT導入提案", "物流効率化", "人材採用支援"],
        "outputs": [
            "1. 現状整理\n2. 課題（属人化・入力負荷）\n3. 提案概要（AI下ごしらえ＋人の確認）\n4. 90日ロードマップ\n5. 投資対効果（悲観/標準/楽観）",
            "1. 物流コストの現状\n2. ボトルネック（手入力・照合）\n3. 段階導入案\n4. KPI（処理時間・ミス率）",
            "1. 採用課題\n2. 母集団形成の改善\n3. 選考フローAI化\n4. 定着支援",
        ],
        "stats": [("2h→20分", "初稿作成"), ("御社", "テンプレ準拠"), ("PDF", "出力可")],
    },
    {
        "file": "demo-expense.html",
        "title": "経費精算AI 体験デモ",
        "meta": "領収書・交通費から経費申請の下書きまで。管理部門向けの下ごしらえデモ。",
        "hero": "経費精算の、<em>下書き</em>まで。",
        "sub": "lp-komon-backoffice.html の「採用前に業務整理」と連動。レシートと申請理由から、承認用の下書きを作成。",
        "panel": "経費申請下書き（サンプル）",
        "chips": ["交通費・新幹線", "交際費・会食", "消耗品・事務用品"],
        "outputs": [
            "科目: 旅費交通費\n金額: 14,200円\n用途: 大阪出張（客先訪問）\n添付: 領収書3枚\n→ 承認ルート: 上長→経理",
            "科目: 交際費\n金額: 24,800円\n用途: A社との会食（4名）\n→ 参加者・目的を記載済み",
            "科目: 消耗品費\n金額: 3,280円\n用途: 事務所備品\n→ 勘定科目候補を2案提示",
        ],
        "stats": [("15分→3分", "1件あたり"), ("0件", "科目漏れ"), ("CSV", "会計連携")],
    },
    {
        "file": "demo-policy-search.html",
        "title": "稟議・規程検索AI 体験デモ",
        "meta": "就業規則・稟議規程から、出典付きで回答。総務への同じ質問を減らす。",
        "hero": "「規程どこ？」を、<em>10秒</em>で。",
        "sub": "稟議・就業規則・社内ルールを横断検索。回答には条文の出典を付けます。",
        "panel": "規程検索（サンプル）",
        "chips": ["有給の申請方法", "10万円超の稟議", "在宅勤務ルール"],
        "outputs": [
            "回答: 有給は事前申請。3日前までに上長承認。\n出典: 就業規則 第12条",
            "回答: 10万円超は部長→役員の2段階稟議。\n出典: 稟議規程 別表1",
            "回答: 週2日まで。コアタイム10-15時。\n出典: テレワーク規程 第3条",
        ],
        "stats": [("10秒", "平均回答"), ("出典", "条文リンク"), ("-40%", "総務問合せ")],
    },
    {
        "file": "demo-progress-match.html",
        "title": "出来高・請求突合AI 体験デモ",
        "meta": "建設現場の出来高と下請請求を突合。差異を先に洗い出すデモ。",
        "hero": "請求の突合を、<em>先回り</em>。",
        "sub": "lp-komon-kensetsu.html の見積・現場支援と連動。出来高表と請求書の差異をAIがフラグ。",
        "panel": "出来高突合（サンプル）",
        "chips": ["鉄筋工事", "内装工事", "設備工事"],
        "outputs": [
            "⚠ 差異: 数量 +2t（請求側多め）\n確認: 追加変更の有無\n→ 現場写真・日報と照合推奨",
            "✓ 一致: 内装一式\n→ 承認候補",
            "⚠ 差異: 単価不一致\n→ 契約単価表 2024-03 を参照",
        ],
        "stats": [("3件", "差異検知"), ("45分", "確認時間削減"), ("人", "最終承認")],
    },
    {
        "file": "demo-safety-patrol.html",
        "title": "安全パトロールAI 体験デモ",
        "meta": "現場写真から安全指摘の下書きと是正指示案を作成。",
        "hero": "安全確認を、<em>記録</em>まで。",
        "sub": "パトロール写真とメモから、指摘事項・是正期限・共有文案の下書きを作成。判断は有資格者が行います。",
        "panel": "安全パトロール記録（サンプル）",
        "chips": ["足場・手すり", "ヘルメット着用", "資材置場"],
        "outputs": [
            "指摘: 足場手すりの欠落\n是正期限: 本日中\n文案: 該当箇所を停止し、手すり補修後に再開",
            "指摘: ヘルメット未着用 2名\n是正: 即時指導・再発防止周知",
            "指摘: 資材の通路占有\n是正: 搬入経路を確保",
        ],
        "stats": [("5分", "記録作成"), ("共有", "現場全員"), ("人", "最終判断")],
    },
    {
        "file": "demo-ai-portal.html",
        "title": "AI診断ポータル 体験デモ",
        "meta": "既存サービスにAI診断を組み込んだPoC体験。攻めのAI活用の入口デモ。",
        "hero": "御社のサービスに、<em>AIを組み込む</em>。",
        "sub": "ai-product.html の攻めAIレーン向け。会員ポータルにAI診断を追加したBefore/Afterを体験。",
        "panel": "AI診断ポータル（サンプル）",
        "chips": ["保険見直し", "不動産査定", "設備診断"],
        "outputs": [
            "Before: 問い合わせフォームのみ\nAfter: 3問診断→パーソナライズ提案→担当者へ\n→ CVR +22%（サンプル値）",
            "Before: 固定LP\nAfter: 条件入力→概算レンジ→内見予約\n→ 反響の質が向上",
            "Before: PDFカタログ\nAfter: 症状選択→推奨メンテ→見積たたき台",
        ],
        "stats": [("PoC", "50万〜"), ("4週", "試作目安"), ("売上", "新商品化")],
    },
]


def demo_html(d):
    chips_html = "".join(
        f'<button type="button" class="chip{" active" if i == 0 else ""}" data-i="{i}">{c}</button>'
        for i, c in enumerate(d["chips"])
    )
    stats_html = "".join(
        f'<div class="stat"><b>{b}</b><small>{s}</small></div>' for b, s in d["stats"]
    )
    outputs_js = ",\n    ".join(repr(o) for o in d["outputs"])
    slug = d["file"].replace(".html", "")
    return f"""<!-- 2026-07-22: LP約束1:1デモ（{d['file']}） -->
<!DOCTYPE html>
<html lang="ja">
<head>
<script>(function(){{var h=location.hostname;if(h==='rakansens.github.io'||h==='bivrosttt.github.io'){{location.replace('https://ai-komon.bivrost.co.jp'+location.pathname.replace(/^\\/ai-komon2/,'')+location.search+location.hash);}}}})();</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{d['title']}｜AI顧問室</title>
<meta name="description" content="{d['meta']}">
<meta property="og:title" content="{d['title']}｜AI顧問室">
<meta property="og:description" content="{d['meta']}">
<meta property="og:url" content="https://ai-komon.bivrost.co.jp/{d['file']}">
<meta property="og:image" content="https://ai-komon.bivrost.co.jp/assets/ogp.png">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@600;700&display=swap" rel="stylesheet">
<style>{DEMO_CSS}</style>
</head>
<body>
<header><div class="container header-inner"><a href="index.html" class="logo">AI顧問室</a><div style="display:flex;gap:16px;align-items:center"><a href="demos.html" class="back">← デモ一覧</a><a href="index.html?from={slug}#contact" class="btn btn-gold" style="padding:9px 20px;font-size:13px">無料相談</a></div></div></header>
<div class="hero"><div class="container"><span class="tag">EXPERIENCE DEMO</span><h1>{d['hero']}</h1><p>{d['sub']}</p></div></div>
<div class="note"><div class="container">※サンプルデータの体験デモです。実際は御社の書式・ルールに合わせて構築します。</div></div>
<main class="container">
  <div class="panel"><div class="panel-head">{d['panel']}</div><div class="panel-body">
    <div class="row" id="chips">{chips_html}</div>
    <div class="out" id="out"></div>
    <div class="stat-grid">{stats_html}</div>
  </div></div>
</main>
<section class="cta"><div class="container"><h2>御社仕様で構築する</h2><p style="color:var(--gray);margin:10px 0 20px">デモは入口です。本番は御社の業務フローに合わせて設計・定着まで伴走します。</p><a href="index.html?from={slug}#contact" class="btn btn-navy">無料相談を予約 →</a></div></section>
<footer><div class="container"><a href="index.html">AI顧問室</a> · <a href="demos.html">デモ一覧</a> · <a href="privacy.html">プライバシー</a></div></footer>
<script>
const outputs = [
    {outputs_js}
];
const out = document.getElementById('out');
const chips = document.querySelectorAll('.chip');
function show(i){{ out.textContent = outputs[i]; chips.forEach((c,j)=>c.classList.toggle('active', j===i)); }}
chips.forEach(c=>c.addEventListener('click',()=>show(Number(c.dataset.i))));
show(0);
</script>
</body>
</html>
"""


WORKS = [
    {
        "file": "works-btob-proposal.html",
        "title": "BtoB提案書PDF（御社ロゴ入り）",
        "meta": "AI+デザインツールで制作した16:9提案書サンプル。営業組織向け成果物。",
        "cat": "BtoB営業・提案書",
        "desc": "架空のIT導入提案書。表紙・課題整理・90日ロードマップ・ROI試算まで、PowerPoint不使用で制作。",
        "tags": ["16:9 PDF", "御社ロゴ差替可", "約2時間"],
        "sections": [
            ("01 表紙", "御社ロゴ / 提案タイトル / 日付"),
            ("02 現状と課題", "商談メモから抽出した3つの論点"),
            ("03 提案概要", "AI下ごしらえ＋人の確認体制"),
            ("04 90日ロードマップ", "試行→定着→拡張"),
            ("05 ROI", "悲観/標準/楽観の3ケース"),
        ],
    },
    {
        "file": "works-sales-mail.html",
        "title": "営業メール Before/After",
        "meta": "追客・フォローメールのBefore/Afterサンプル。テンプレ化前後の比較。",
        "cat": "BtoB営業・メール",
        "desc": "毎回ゼロから書いていた追客メールを、顧客別の下書きから磨き込む流れに。",
        "tags": ["Before/After", "追客3通", "テンプレ化"],
        "sections": [
            ("Before", "「お世話になっております。進捗いかがでしょうか…」（毎回同文）"),
            ("After Day3", "内見の論点を引用したパーソナライズ文"),
            ("After Day7", "比較検討中の条件を確認する一文"),
            ("After Day14", "休眠顧客向け・新着通知オプトイン"),
        ],
    },
    {
        "file": "works-internal-news.html",
        "title": "社内報・就業規則改定案",
        "meta": "管理部門向け。社内報1号と就業規則改定のたたき台サンプル。",
        "cat": "管理部門・社内文書",
        "desc": "AI活用定着後に社員が作れるようになる、社内報と規程改定の品質サンプル。",
        "tags": ["社内報", "就業規則", "研修後成果物"],
        "sections": [
            ("社内報 第1号", "AI活用の進捗・成功事例・次の一手"),
            ("改定案 概要", "テレワーク規程の追加条項"),
            ("FAQ 3問", "社員が迷いやすいポイント"),
        ],
    },
    {
        "file": "works-ai-service.html",
        "title": "既存サービス + AI Before/After",
        "meta": "攻めのAI活用。会員ポータルにAI診断を組み込んだBefore/After成果物。",
        "cat": "攻めAI・商品化",
        "desc": "ai-product.html 向け。問い合わせフォームだけだったLPを、AI診断→提案→予約までつなぐ設計例。",
        "tags": ["PoC", "CVR改善", "新商品化"],
        "sections": [
            ("Before", "静的LP + 問い合わせフォーム"),
            ("After", "3問診断 → パーソナライズ結果 → 担当者へ"),
            ("PoC範囲", "4週間 / 50万円〜 / 本番判断は別途"),
        ],
    },
]


def works_html(w):
    sections = "".join(
        f'<article style="border:1px solid var(--line);border-radius:6px;padding:16px;margin-bottom:12px"><h3 style="font-size:16px;color:var(--navy);margin-bottom:6px">{t}</h3><p style="font-size:14px;color:var(--gray)">{b}</p></article>'
        for t, b in w["sections"]
    )
    tags = "".join(f'<span style="font-size:11px;background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:3px 12px">{t}</span>' for t in w["tags"])
    return f"""<!-- 2026-07-22: {w['title']} 成果物サンプル -->
<!DOCTYPE html>
<html lang="ja">
<head>
<script>(function(){{var h=location.hostname;if(h==='rakansens.github.io'||h==='bivrosttt.github.io'){{location.replace('https://ai-komon.bivrost.co.jp'+location.pathname.replace(/^\\/ai-komon2/,'')+location.search+location.hash);}}}})();</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{w['title']}｜作品ショーケース｜AI顧問室</title>
<meta name="description" content="{w['meta']}">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@600;700&display=swap" rel="stylesheet">
<style>
:root{{--navy:#0B2447;--gold:#C9A227;--ink:#1A2433;--gray:#5B6B7F;--line:#DDE4EC;--bg:#F4F7FA}}
*{{margin:0;padding:0;box-sizing:border-box}} body{{font-family:'Noto Sans JP',sans-serif;color:var(--ink);line-height:1.85}}
h1,h2{{font-family:'Noto Serif JP',serif}} a{{color:var(--navy)}}
.container{{max-width:880px;margin:0 auto;padding:0 24px}}
header{{border-bottom:1px solid var(--line);padding:16px 0}} .back{{font-size:13px;color:#2D6CB5}}
.hero{{padding:48px 0 32px}} .cat{{font-size:12px;color:#2D6CB5;font-weight:700;letter-spacing:.08em}}
.hero h1{{font-size:clamp(26px,4vw,34px);margin:8px 0 12px;color:var(--navy)}}
.preview{{background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:28px;margin:24px 0}}
.cta{{text-align:center;padding:40px 0 56px;border-top:1px solid var(--line)}}
.btn{{display:inline-block;background:var(--gold);color:#071A35;padding:12px 28px;border-radius:4px;font-weight:700;text-decoration:none}}
footer{{background:#071A35;color:#9fb0c7;text-align:center;padding:24px;font-size:13px}}
</style>
</head>
<body>
<header><div class="container"><a href="works.html" class="back">← 作品ショーケース</a></div></header>
<main class="container">
  <div class="hero"><div class="cat">{w['cat']}</div><h1>{w['title']}</h1><p style="color:var(--gray);max-width:640px">{w['desc']}</p><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:14px">{tags}</div></div>
  <div class="preview">{sections}</div>
  <p style="font-size:13px;color:var(--gray);border-left:4px solid var(--gold);padding-left:14px">※架空サンプルです。実際は御社のブランド・書式・承認フローに合わせて制作します。</p>
</main>
<div class="cta"><a href="index.html?from={w['file'].replace('.html','')}#contact" class="btn">同じ品質を相談する →</a></div>
<footer><a href="index.html" style="color:#9fb0c7">AI顧問室</a></footer>
</body>
</html>
"""


def main():
    for d in DEMOS:
        path = ROOT / d["file"]
        path.write_text(demo_html(d), encoding="utf-8")
        print("wrote", path.name)
    for w in WORKS:
        path = ROOT / w["file"]
        path.write_text(works_html(w), encoding="utf-8")
        print("wrote", path.name)


if __name__ == "__main__":
    main()
