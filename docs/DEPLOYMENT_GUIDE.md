# Persona Render - Renderデプロイガイド

このガイドでは、Persona RenderシステムをRenderにデプロイする手順を説明します。

## 前提条件

- GitHubアカウント
- Renderアカウント（無料プランでOK）
- 各種APIキー（必要に応じて）
  - OpenAI API Key（GPTモデル使用時）
  - Anthropic API Key（Claudeモデル使用時）
  - Google API Key（Geminiモデル使用時）

## 手順

### 1. GitHubリポジトリの作成

1. GitHubにログイン
2. 新しいリポジトリを作成（例：`persona-render`）
3. このプロジェクトのファイルをすべてアップロード(コミット)


### 2. Renderアカウントの設定

1. [Render](https://render.com/)にサインアップ/ログイン
2. GitHubアカウントと連携

### 3. 新しいWeb Serviceの作成

1. Renderダッシュボードで「New +」→「Web Service」をクリック
2. GitHubリポジトリを選択
3. 以下の設定を入力：

#### 基本設定
- **Name**: `persona-render`（任意の名前）
- **Region**: `Singapore (Southeast Asia)`（日本から近い）
- **Branch**: `main`
- **Root Directory**: （空欄のまま）
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd backend && gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

#### 環境変数の設定

「Environment」タブで以下の環境変数を追加：

```
# APIキー（使用するものだけ設定）
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxx

```

### 4. 永続ディスクの設定

RAGデータやアップロードファイルを保存するため：

1. Renderダッシュボードでサービスを選択
2. 左メニューの「Disks」をクリック
3. 「Add Disk」をクリック
4. 以下を設定：
   - **Name**: `app-settings`
   - **Mount Path**: `/var/app_settings`
   - **Size**: `1 GB`（無料プランの上限）

### 5. デプロイ

1. 「Create Web Service」をクリック
2. 自動的にビルドとデプロイが開始されます
3. 完了まで5-10分程度待ちます

### 6. デプロイ後の確認

1. デプロイ完了後、提供されたURL（例：`https://persona-render.onrender.com`）にアクセス
2. ユーザー画面が表示されることを確認
3. `https://persona-render.onrender.com/admin`にアクセスして管理画面を確認

## トラブルシューティング

### ビルドエラーが発生する場合

1. **requirements.txtの確認**
   - すべての依存関係が正しく記載されているか確認
   - バージョンの競合がないか確認

2. **Pythonバージョン**
   - Renderのデフォルトは最新のPython 3.x
   - 特定のバージョンが必要な場合は`runtime.txt`を作成：
     ```
     python-3.11.0
     ```

### 画像が表示されない場合

1. 画像ファイルが`/images/`ディレクトリに存在することを確認
2. ファイル名の大文字小文字が一致しているか確認
3. 日本語ファイル名は避ける（または適切にエンコード）

### RAGデータが保存されない場合

1. 永続ディスクが正しくマウントされているか確認
2. 管理画面でRAGデータがアップロードされているか確認
3. Renderのログでエラーメッセージを確認

### 500エラーが発生する場合

1. Renderのログを確認
2. 環境変数（APIキーなど）が正しく設定されているか確認
3. `backend/main.py`の相対インポートが正しいか確認

## 設定のカスタマイズ

### 診療科・患者タイプ・AIモデルの追加

`backend/config/`ディレクトリ内のJSONファイルを編集：

- `departments.json` - 診療科の追加・編集
- `patient_types.json` - 患者タイプの追加・編集
- `ai_models.json` - AIモデルの追加・編集
- `purposes.json` - 作成目的の追加・編集
- `prompt_templates.json` - プロンプトのカスタマイズ

編集後、GitHubにプッシュすると自動的に再デプロイされます。

### 管理画面での設定

1. `/admin`にアクセス
2. 以下の設定が可能：
   - 使用するAIモデルの選択
   - 文字数制限の調整
   - RAGデータのアップロード

## セキュリティに関する注意

1. **APIキーの管理**
   - 絶対にコードにハードコーディングしない
   - 環境変数で管理する

2. **アクセス制限**
   - 必要に応じて管理画面にBasic認証を追加
   - RenderのカスタムドメインでHTTPS化

3. **データの保護**
   - 永続ディスクのデータは定期的にバックアップ
   - 機密情報は暗号化を検討

## 参考リンク

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Render Python Deployment Guide](https://render.com/docs/deploy-python)

## サポート

問題が発生した場合：

1. Renderのログを確認
2. このREADMEのトラブルシューティングを参照
3. GitHubのIssuesで質問

---

最終更新日: 2025年6月11日