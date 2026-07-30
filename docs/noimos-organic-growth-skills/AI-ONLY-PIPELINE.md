# Noimos AI-only公開パイプライン

## 方針

人間の実名承認を公開条件にしない。代わりに、生成物が公開可能になる条件を機械的に記録し、AI-only承認レコードを残す。

## 必須ゲート

1. `claim_evidence`: 数値・事実・実績の主張が主張台帳と出典へ結び付いている
2. `brand_alignment`: 対象読者、語彙、CTA、禁止表現を検査済み
3. `specificity`: 手順、判断条件、例、限界、失敗時の戻し方がある
4. `risk_screen`: 法務、プライバシー、著作権、誇大表現、プラットフォームリスクを確認済み
5. `render_qa`: JSON-LD、リンク、画像、横崩れ、CTA、コンソールを確認済み

## 承認レコード

```json
{
  "mode": "ai_only",
  "status": "ai_approved",
  "pipeline": "Noimos AI Quality Pipeline",
  "reviewed_at": "2026-07-30T18:00:00+09:00",
  "checks": {
    "claim_evidence": true,
    "brand_alignment": true,
    "specificity": true,
    "risk_screen": true,
    "render_qa": true
  }
}
```

`ai_only` は、5チェックがすべて `true` で、パイプライン名と時刻がある場合だけ有効。未検証の実績、未登録の数値、禁止表現、プレースホルダー、リンク切れ、表示崩れが一つでもあればBLOCKする。

## 運用上の境界

- AI-only承認は、事実の真実性を無条件に保証するものではない。証拠URLと取得日を必須にする
- 品質ゲートは判定と記録を行う。デプロイは別の明示されたCI/CDジョブが行う
- 本番公開後はGSC、インデックス、CTR、CVを定期監視し、下落時は自動修復ではなく差分提案へ戻す
- 人間承認へ戻す必要がある場合は、`mode` を `human` に変更し、従来の承認条件を使える
