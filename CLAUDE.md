# 医療系ペルソナ自動生成AI - フェーズ2改修プロジェクト

## プロジェクト概要
- クライアント向けにフェーズ2の改修を提案中
- 2024年8月中旬のプレゼンテーションに向けて開発予定
- Claude Codeを活用した効率的な開発を計画

## 重要な決定事項

### 4つの新機能
1. **診療科別アクセス制御**
   - 医科（/medical）、歯科（/dental）、その他（/others）
   - Basic認証による制御
   - 既存システムの基盤を活用

2. **主訴別ペルソナ生成**
   - 診療科→主訴選択→作成目的の3ステップ
   - 静的RAGデータ方式（CSVファイルを事前準備）
   - セキュリティ重視でアップロード機能は廃止

3. **検索キーワード時系列分析**
   - Chart.jsで散布図表示
   - AIによる分析レポート生成
   - Yahoo!ビジネスの時系列データを活用

4. **競合分析（3C/SWOT分析）**
   - Google Maps APIのみ使用（Ahrefs APIは高額なため不採用）
   - 自院情報入力→競合自動検出→SWOT分析生成

### 見積もり概要
- 総額：357,500円（税込）
- 工期：3週間
- 総工数：55時間
- 時間単価：5,000円

### 段階的実装案（予算制約がある場合）
- 第1段階（約20万円）：診療科別アクセス制御＋主訴別ペルソナ生成
- 第2段階（後日）：時系列分析＋競合分析

## 技術的な詳細
- FastAPI + 静的ファイルサーバー構成
- Render.comでのデプロイ
- 環境変数による設定管理

## 次のステップ
1. クライアントへ見積書提出済み
2. 反応を見て必要に応じて段階的実装の交渉
3. 承認後、3週間での開発開始

## 作成済みドキュメント
- フェーズ2壁打ち.md：要件整理
- フェーズ2提案書.md：クライアント向け提案
- フェーズ2見積書.md：費用見積もり

## 必要なAPIとサービス

### Google Cloud Platform - 競合分析機能
以下のAPIを有効化する必要があります：

1. **Geocoding API**
   - 住所を緯度経度に変換するために必要
   - 日本の住所から座標を取得する際に使用

2. **Places API**
   - 近隣の医療機関を検索するために必要
   - 施設の詳細情報（電話番号、営業時間、レビュー等）を取得

#### 設定手順：
1. [Google Cloud Console](https://console.cloud.google.com/)にログイン
2. プロジェクトを選択（または新規作成）
3. 課金アカウントを設定（必須）
4. 「APIとサービス」→「ライブラリ」から以下を検索して有効化：
   - Geocoding API
   - Places API
5. 「APIとサービス」→「認証情報」でAPIキーを作成
6. APIキーの制限（推奨）：
   - アプリケーションの制限：「IPアドレス」
   - Render.comのサーバーIPアドレスを許可リストに追加
7. RenderにGOOGLE_MAPS_API_KEYとして環境変数を設定

### その他の必要なAPI（既存）
- **OPENAI_API_KEY** - ペルソナ生成、SWOT分析（GPT-4）
- **ANTHROPIC_API_KEY** - Claude利用時
- **GOOGLE_API_KEY** - Gemini利用時

### Renderでの環境変数設定
```
OPENAI_API_KEY=sk-...
GOOGLE_MAPS_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
ADMIN_USERNAME=admin
ADMIN_PASSWORD=...
MEDICAL_USERNAME=medical
MEDICAL_PASSWORD=...
DENTAL_USERNAME=dental
DENTAL_PASSWORD=...
OTHERS_USERNAME=others
OTHERS_PASSWORD=...
USER_USERNAME=user
USER_PASSWORD=...
```