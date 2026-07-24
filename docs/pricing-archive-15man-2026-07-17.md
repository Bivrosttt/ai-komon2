# AI顧問室 月額15万円モデル 復元メモ

- 保存日: 2026-07-17
- 変更前の公開価格: 月額15万円〜（税別）
- 年額換算: 180万円〜
- 最低契約期間: 3ヶ月
- 旧詳細プラン: ライト15万円 / スタンダード25万円 / プレミアム50万円（すべて月額・税別）

## 2026-07-17からの一時運用

AI顧問契約の公開価格を「月50万円〜（税別・最低3ヶ月）」に統一する。従来の3プラン比較は公開物から外し、診断後に支援範囲と金額を個別提案する。

## 主な変更対象

- 公式サイト: `index.html`, `bivrost.html`, `tokushoho.html`, `llms.txt`
- 広告・訴求ページ: `lp-ai-diagnosis.html` およびAI顧問の旧LP群
- 関連サービス: `ai-product.html`, `ai-shain.html`, `monitor.html`
- 費用・ROI試算: `data.html`, `lp-roi.html`, `lp-cost.html`
- 配布資料: `materials/src/pricing.html`, `materials/src/pitch-deck.html`, `materials/src/contract-draft.html`, `materials/src/hearing-sheet.html` と対応PDF
- 運用記録: `docs/OPERATIONS.md`, `docs/dashboard.html`

## 変更対象外

- `demo-ai-team.html` の「AI部署セット 月15万円」は別サービスの価格のため維持。
- `ai-shain.html` の人件費比較「約10〜15万円」は一般的なコスト例のため維持。
- 工事金額、日付、計算機の初期値など、AI顧問契約と無関係な `15` は維持。
- `assets/meta-ads-creatives/archive/` 配下の過去広告は履歴として維持。

## 旧価格入り広告素材

以下は15万円表記を画像内に含むため、`assets/meta-ads-creatives/archive/price-15-2026-07-17/` に移し、50万円運用中は配信対象外とする。

- `current/design-exploration-6/` の6案
- `current/json-first-5/03-cost-comparison.png`
- `current/lp-top5-5/03-lp-cost.png`
- `current/lp-top5-5/05-lp-simple.png`
- `current/meta-ads-basic-4/03-ai-advisor-choice.png`
- 上記セットの旧コンタクトシート

## 15万円に戻す方法

1. このメモを追加した価格変更コミットを `git revert` する。
2. または上記対象の「月50万円〜 / 年600万円〜」を「月15万円〜 / 年180万円〜」に戻し、必要に応じて旧3プラン表を復元する。
3. PDFは `materials/src/` のHTMLを戻してから再生成する。
4. 旧価格入り広告は `archive/price-15-2026-07-17/` から `current/` へ戻す。
