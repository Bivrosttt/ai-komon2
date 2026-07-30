#!/usr/bin/env python3
"""Apply the observed Noimos article components to existing article HTML.

This is an idempotent, scoped refresh. It only adds marked components and does
not replace article copy, canonical URLs, redirects, or source claims.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

KEY_POINTS = {
    "ai-advisor-comparison": [
        "料金だけでなく、対象業務・実装範囲・人の確認・総費用・定着支援を同じ条件で比べる",
        "顧客送信、契約・請求、権限変更、削除は人の承認を残す",
        "提案書に成果物、追加費用、停止条件、引き継ぎ方法を書いてもらう",
    ],
    "ai-advisor-cost": [
        "初期費用・月額・従量費・追加作業・社内確認工数を年間総額へ入れる",
        "公開価格は市場平均と混同せず、支援範囲と契約期間の前提を確認する",
        "月額が自社の対象業務と成果物に合わない場合は、研修や単発支援も比較する",
    ],
    "ai-business-cases": [
        "事例は困りごと・入力・AI処理・人の確認・業務へ戻す工程に分けて読む",
        "派手な成果数値ではなく、自社で確認できる小さな業務から試す",
        "実績・体験デモ・想定例を区別し、導入前後の測定条件をそろえる",
    ],
    "ai-introduction-benefits": [
        "メリットを時間・品質・知識共有・対応速度に分け、導入前の状態を測る",
        "AIの出力だけでなく、確認・修正・引き継ぎまで含めて効果を判断する",
        "効果が確認できないときに縮小・停止できる小さな試行から始める",
    ],
    "ai-introduction-risk": [
        "入力データ、出力の誤り、権限、契約、運用を別々のリスクとして確認する",
        "外部送信・重要判断・削除は、人が承認してログを残す",
        "漏えい・誤回答・停止時の連絡先と切り戻し手順を先に決める",
    ],
    "ai-recruiting-efficiency": [
        "求人票・日程調整・候補者連絡はAI補助に置き、採用判断は人が行う",
        "候補者情報の入力範囲、保存先、閲覧権限を先に決める",
        "返信時間だけでなく、誤送信・修正・候補者体験を一緒に確認する",
    ],
    "ai-roi": [
        "削減時間を金額へ換算する前に、作業・確認・修正の時間を分けて測る",
        "月間効果、導入費用、回収期間を同じ前提で試算する",
        "標準ケースだけでなく、保守ケースと効果が出ない場合も置く",
    ],
    "business-efficiency-ideas": [
        "業務名ではなく、繰り返し・転記・確認・待ち時間の多い工程から探す",
        "AIに任せる部分と、人が承認する部分を工程ごとに分ける",
        "一つの業務で時間・修正・停止を測ってから、対象範囲を広げる",
    ],
    "business-manual-howto": [
        "手順だけでなく、開始条件・判断基準・例外・完了条件を残す",
        "担当者の暗黙知を、後任が実行して確認できる単位へ分解する",
        "更新担当と見直しのトリガーを決め、古い手順を残さない",
    ],
    "customer-support-ai": [
        "問い合わせを分類・回答案・人の確認・エスカレーションに分ける",
        "顧客への送信前に、根拠資料と最新性を担当者が確認する",
        "正解率だけでなく、返信時間・修正・再問い合わせ・停止を測る",
    ],
    "estimate-time-reduction": [
        "受付・転記・確認・送付の工程ごとに現在の時間を測る",
        "金額・納期・顧客条件はAIに確定させず、人の承認点を残す",
        "自動化後も差し戻しと手動へ戻す経路を記録する",
    ],
    "generative-ai-internal-rules": [
        "入力情報を利用可・要確認・入力禁止の3分類へ分ける",
        "迷ったときに誰へ確認し、どのログを残すかを決める",
        "社内ルールはツール名ではなく、業務と情報の種類で更新する",
    ],
    "gijiroku-ai": [
        "文字起こし・要約・決定事項・人の確認・共有を別工程にする",
        "固有名詞・数字・否定表現・担当者・期限は人が確定する",
        "機密情報の入力範囲と正式記録へ移す責任者を決める",
    ],
    "gijiroku-template": [
        "議事録を目的・決定事項・保留・ToDo・担当者・期限に分ける",
        "発言の全文ではなく、次の行動が分かる記録を残す",
        "会議後に人が決定事項と期限を確認してから共有する",
    ],
    "internal-faq-howto": [
        "質問履歴から頻度の高いものを集め、結論・条件・根拠・窓口で答える",
        "AIは分類と回答候補に置き、根拠資料と更新日を人が確認する",
        "未解決質問、古い回答、制度変更を更新トリガーにする",
    ],
    "proposal-ai": [
        "商談情報・顧客条件・提案構成・下書き・提出前確認を分ける",
        "AIには構成と下書きを任せ、価格・納期・約束は人が確定する",
        "提出後の修正と失注理由を次のテンプレート改善へ戻す",
    ],
    "sales-efficiency": [
        "営業の受付・見積・提案・追客を工程ごとに棚卸しする",
        "顧客向けの約束や送信は人の確認を残し、社内作業から効率化する",
        "時間だけでなく、差し戻し・返信遅延・引き継ぎの欠落を測る",
    ],
    "work-handover-manual": [
        "業務一覧を作り、期限・影響・頻度から引き継ぎ順を決める",
        "手順・判断基準・例外・連絡先を後任の実行単位で残す",
        "後任が実行した結果を確認し、手順書へ更新する",
    ],
}

HERO = {
    "ai-advisor-comparison": ("AI顧問を比較するときは、料金より業務の完了条件からそろえる。", ["対象業務", "実装範囲", "承認", "総費用"]),
    "ai-advisor-cost": ("AI顧問の費用は、月額ではなく初期・従量・社内工数まで総額で見る。", ["初期費用", "月額", "従量費", "社内工数"]),
    "ai-email-writing": ("営業メールは、目的を決めてからAIに下書きを任せる。", ["目的", "材料", "条件", "送信前確認"]),
    "internal-knowledge-search": ("社内検索は、回答より根拠と更新責任を残す。", ["質問", "根拠資料", "人の確認", "更新"]),
    "task-priority": ("優先順位は、緊急度だけでなく期限と影響で決める。", ["期限", "影響", "待ち時間", "再利用"]),
}

RELATED = {
    "ai-advisor-comparison": [("/articles/ai-advisor-cost/", "AI顧問の費用", "初期・月額・従量まで総額で見る"), ("/articles/ai-introduction-roadmap/", "AI導入の進め方", "30日で小さく試す"), ("/articles/ai-roi/", "AI導入の費用対効果", "回収期間を試算する")],
    "ai-advisor-cost": [("/articles/ai-advisor-comparison/", "AI顧問の比較基準", "支援範囲を同じ条件で比べる"), ("/articles/ai-roi/", "AI導入の費用対効果", "削減時間と回収期間を見る"), ("/articles/ai-introduction-roadmap/", "AI導入の進め方", "小さく試して定着させる")],
}


def key_points_html(slug: str) -> str:
    items = "".join(f"<li>{html.escape(point)}</li>" for point in KEY_POINTS[slug])
    return f'<!-- noimos-refresh:key-points -->\n<div class="key-points"><strong>この記事の要点</strong><ul>{items}</ul></div>'


def hero_html(slug: str) -> str:
    title, badges = HERO[slug]
    badge_html = "".join(f"<span>{html.escape(badge)}</span>" for badge in badges)
    label = slug.replace("-", " ").upper()
    return f'<!-- noimos-refresh:hero -->\n<div class="hero-visual"><span class="hero-kicker">AI KOMONSHITSU / {label}</span><span class="hero-title">{html.escape(title)}</span><div class="hero-badges">{badge_html}</div></div>'


def related_html(slug: str) -> str:
    cards = "".join(f'<a href="{href}"><strong>{html.escape(title)}</strong><span>{html.escape(summary)}</span></a>' for href, title, summary in RELATED[slug])
    return f'<!-- noimos-refresh:related -->\n<h2>次に読む・使う</h2><div class="related">{cards}</div>'


def add_external_css(html_text: str) -> str:
    if "assets/articles/article.css" in html_text:
        return html_text
    marker = "</head>"
    link = '<link rel="stylesheet" href="../../assets/articles/article.css?v=20260730-refresh">\n  '
    return html_text.replace(marker, link + marker, 1)


def add_after_answer(html_text: str, block: str) -> str:
    if "noimos-refresh:" in block and block.split(":", 1)[1].split("-->", 1)[0] in html_text:
        return html_text
    match = re.search(r'(<div[^>]*class=["\'][^"\']*\banswer\b[^"\']*["\'][^>]*>.*?</div>)', html_text, re.S | re.I)
    if not match:
        return html_text
    return html_text[:match.end()] + "\n  " + block + html_text[match.end():]


def add_after_meta(html_text: str, block: str) -> str:
    if "noimos-refresh:hero" in html_text:
        return html_text
    match = re.search(r'(<p[^>]*>[^<]*公開日:[\s\S]*?</p>)', html_text, re.S | re.I)
    if not match:
        return html_text
    return html_text[:match.end()] + "\n  " + block + html_text[match.end():]


def add_toc(html_text: str) -> str:
    if "noimos-refresh:toc" in html_text:
        return html_text
    headings = []
    counter = 0

    def replace_heading(match: re.Match[str]) -> str:
        nonlocal counter
        attrs, inner = match.group(1), re.sub(r"<[^>]+>", "", match.group(2)).strip()
        if re.search(r"\bid=", attrs, re.I):
            ident = re.search(r'\bid=["\']([^"\']+)', attrs, re.I).group(1)
        else:
            counter += 1
            ident = f"refresh-section-{counter}"
            attrs += f' id="{ident}"'
        if inner not in {"よくある質問", "出典", "AI導入の相談はサービスから"} and not inner.startswith("AI導入の相談"):
            headings.append((ident, inner))
        return f"<h2{attrs}>{match.group(2)}</h2>"

    updated = re.sub(r"<h2([^>]*)>(.*?)</h2>", replace_heading, html_text, flags=re.S | re.I)
    items = "".join(f'<li><a href="#{ident}">{html.escape(title)}</a></li>' for ident, title in headings[:8])
    toc = f'<!-- noimos-refresh:toc -->\n<div class="toc"><strong>この記事の目次</strong><ol>{items}</ol></div>'
    figure_end = updated.find("</figure>")
    if figure_end >= 0:
        figure_end += len("</figure>")
        return updated[:figure_end] + "\n  " + toc + updated[figure_end:]
    return add_after_answer(updated, toc)


def add_related(html_text: str, slug: str) -> str:
    if "noimos-refresh:related" in html_text:
        return html_text
    marker = re.search(r'<div[^>]*class=["\'][^"\']*(?:tool-cta|service-cta)[^"\']*["\'][^>]*>', html_text, re.I)
    if not marker:
        return html_text
    block = related_html(slug)
    return html_text[:marker.start()] + block + "\n  " + html_text[marker.start():]


def add_steps(html_text: str, slug: str) -> str:
    if "noimos-refresh:steps" in html_text:
        return html_text
    if slug != "gijiroku-ai" or 'class="steps"' in html_text:
        return html_text
    block = '<!-- noimos-refresh:steps -->\n<div class="steps"><div class="step"><b>01 / TRANSCRIBE</b><h3>文字起こし</h3><p>音声から候補を作る。</p></div><div class="step"><b>02 / CHECK</b><h3>人が確認</h3><p>固有名詞と決定事項を確定する。</p></div><div class="step"><b>03 / SHARE</b><h3>共有・更新</h3><p>正式記録へ戻し、次の行動を残す。</p></div></div>'
    figure_end = html_text.find("</figure>")
    if figure_end >= 0:
        figure_end += len("</figure>")
        return html_text[:figure_end] + "\n  " + block + html_text[figure_end:]
    return html_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    changed = []
    for slug in sorted(KEY_POINTS):
        path = root / "articles" / slug / "index.html"
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        updated = original
        if slug in HERO:
            updated = add_external_css(updated)
            updated = add_after_meta(updated, hero_html(slug))
        updated = add_after_answer(updated, key_points_html(slug))
        if slug in {"ai-advisor-comparison", "ai-advisor-cost"}:
            updated = add_external_css(updated)
            updated = add_toc(updated)
        if slug in RELATED:
            updated = add_related(updated, slug)
        updated = add_steps(updated, slug)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(slug)
    print({"changed": changed, "count": len(changed)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
