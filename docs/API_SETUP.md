# Google Maps API 設定ガイド

## 概要
競合分析機能で使用するGoogle Maps APIの設定手順です。

## 必要なAPI
1. **Geocoding API** - 住所を座標に変換
2. **Places API** - 近隣施設の検索と詳細情報取得
3. **Maps JavaScript API** - ブラウザ上での地図表示

## 設定手順

### 1. Google Cloud Consoleにアクセス
https://console.cloud.google.com/

### 2. プロジェクトの準備
- 既存のプロジェクトを選択、または新規作成
- プロジェクト名: 例）persona-render-prod

### 3. 課金の有効化（必須）
- 左メニュー「お支払い」
- 課金アカウントを作成または既存のものを選択
- ※無料枠あり（月$200相当）

### 4. APIの有効化
1. 左メニュー「APIとサービス」→「ライブラリ」
2. 以下を検索して「有効にする」をクリック：
   - **Geocoding API**
   - **Places API**
   - **Maps JavaScript API**

### 5. APIキーの作成
1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「APIキー」
3. 作成されたAPIキーをコピー

### 6. APIキーの制限（推奨）
1. 作成したAPIキーをクリック
2. 「アプリケーションの制限」セクション：
   - 「IPアドレス」を選択
   - Render.comのサーバーIPアドレスを追加
3. 「APIの制限」セクション：
   - 「キーを制限」を選択
   - Geocoding API、Places API、Maps JavaScript APIをチェック

### 7. Renderに環境変数を設定
1. Renderダッシュボードにログイン
2. 該当のWeb Serviceを選択
3. 「Environment」タブ
4. 以下を追加：
   ```
   GOOGLE_MAPS_API_KEY=AIza...（コピーしたAPIキー）
   ```

## トラブルシューティング

### REQUEST_DENIED エラーの場合
- Geocoding APIとPlaces APIが有効になっているか確認
- 課金が有効になっているか確認
- APIキーの制限が厳しすぎないか確認

### OVER_QUERY_LIMIT エラーの場合
- 無料枠を超えている可能性
- Google Cloud Consoleで使用量を確認

### ZERO_RESULTS エラーの場合
- 入力された住所が正しいか確認
- 日本の住所形式で入力されているか確認

## 料金の目安
- Geocoding API: $5 per 1,000 requests
- Places Nearby Search: $32 per 1,000 requests
- Places Details: $17 per 1,000 requests
- Maps JavaScript API: $7 per 1,000 map loads
- ※月$200の無料クレジットあり

## セキュリティ注意事項
- APIキーを公開リポジトリにコミットしない
- 本番環境では必ずIPアドレス制限を設定
- 定期的に使用量をモニタリング