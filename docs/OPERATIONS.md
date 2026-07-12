# AI顧問室 運用手順書（OPERATIONS）

後任者向けの引き継ぎドキュメント。最終更新: 2026-07-12

## 全体像

- **本番サイト**: https://ai-komon.bivrost.co.jp/ （GitHub Pages＋独自ドメイン）
- **ページ一覧**: [docs/dashboard.html](https://ai-komon.bivrost.co.jp/docs/dashboard.html)（`python3 docs/build-dashboard.py` で再生成）
- 静的サイト。フレームワーク・ビルド不要（PDFと一部素材のみ生成スクリプトあり）

## リポジトリとデプロイ

| リモート | リポジトリ | 役割 |
|---|---|---|
| origin | `Bivrosttt/ai-komon2`（public） | **SSOT（正本）**。GitHub ActionsでPages配信（.github/workflows/pages.yml） |
| pages | `rakansens/ai-komon2`（public） | 旧URL互換ミラー。旧URLアクセスは全ページのJSリダイレクトで新ドメインへ転送 |

**リリース手順**:
```bash
git push origin main && git push pages main
# デプロイ確認（反映まで1〜2分）
curl -s -o /dev/null -w "%{http_code}" https://ai-komon.bivrost.co.jp/
```

## ドメイン / DNS

- `ai-komon.bivrost.co.jp` … Xdomain（エックスサーバー）のDNSで CNAME → `bivrosttt.github.io`
- bivrost.co.jp 本体（apex/www）はVercel稼働の会社サイト。**触らないこと**
- カスタムドメイン設定は GitHub → Bivrosttt/ai-komon2 → Settings → Pages
- 教訓: ドメイン変更時は「DNSレコードを先に作成→GitHubに設定」の順（逆にするとNXDOMAINが最大1時間キャッシュされ証明書発行が止まる）

## 問い合わせ導線（CTA）

- **予約**: TimeRex `https://timerex.net/s/koki.otsuka_bfac/4b686119`（大塚名義・Google Meet自動発行）
- **フォーム**: Googleフォームへ直接POST（index.html末尾のJS）。entry ID: 会社=1831717163 / 名前=1528434750 / 電話=1216521943 / メール=486964774 / 相談内容=146547974 / 従業員数=1104944249 / 経由=254574837
- **?from=計測**: LPのCTAは `?from={lp名}` 付き。index側JSがsessionStorageに保持し、経由欄に「AI顧問室/{from}」で送信
- **テスト時の注意**: 本物のフォームに送信しない。`window.fetch` をスタブして検証する

## 価格（2026-07-12改定）

- 顧問プラン（月額・税別・最低3ヶ月）: ライト15万 / スタンダード25万 / プレミアム50万
- AI研修（単発・税別）: ライト〜10名 50万 / スタンダード〜25名 100万 / 全社〜50名 180万（50名超は個別）
- 導入支援: ツール導入・自動化 80万〜 / **システム開発 300万〜** / 基幹連携 個別見積（目安800万〜）
- 価格変更時の反映先: index.html（#pricing・#products）/ training.html / implementation.html / materials/src/pricing.html / materials/src/pitch-deck.html → PDF再生成

## 資料PDF

```bash
./materials/build.sh   # materials/src/*.html → materials/*.pdf（要Google Chrome）
./works/build.sh       # 作品系PDF
```

## コンテンツの決まりごと（誠実表記）

- 実績・データは検証可能な出典のみ（出典行を必ず付ける）。架空のデモ・企業は「架空」「サンプル」を明記
- 保証表現・補助金の採択断定は禁止
- AI生成の人物・画像・音声はその旨を明記
- 技術名は出してよいが、プロンプト全文などコピペ再現可能なレシピは「無料相談でお見せします」フックに置き換える
- 代表プロフィール（佐藤啓英）の表記ルール: 年商は「数億円規模」、飲食は「複数店舗」、米国法人は原則不掲載

## 会社情報

- 株式会社Bivrost / 〒160-0022 東京都新宿区新宿5-10-10 海老沢ビル202 / koki.otsuka@bivrost.co.jp / 070-3848-1352
- 会社ページ: bivrost.html ／ 特商法: tokushoho.html ／ プライバシー: privacy.html

## 生成系ツール（admin/tools/ ※ローカルのみ・非コミット）

- 画像生成・TTS: Gemini API（キーは別リポジトリ mangaagent4 の .env）
- 動画生成: Veo 3.1（同キー。写真+セリフ→リップシンク動画）
- 詳細な手順は開発マシンの `.claude/skills/` 配下（ai-media-gen / dreamina-video / hf-movie / gsplat-demo / lp-build / site-release 等）
