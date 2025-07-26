# Persona Render - 医療系ペルソナ自動生成AI

医療機関向けのペルソナ（架空の患者像）を自動生成するWebアプリケーションです。

## 機能

- **AIによるペルソナ生成**: GPT、Claude、Geminiなど複数のAIモデルに対応
- **診療科別カスタマイズ**: 30以上の診療科に対応
- **患者タイプ分類**: 12種類の患者タイプから選択可能
- **RAGデータ対応**: 診療科ごとの検索キーワードデータを活用
- **PDF/PPTエクスポート**: 生成したペルソナをPDFまたはPowerPoint形式でダウンロード
- **管理画面**: AIモデルの選択、文字数制限の調整、RAGデータのアップロード（保存データはrenderの永久ディスクに保存）

## システム構成

```
persona_render/
├── backend/          # バックエンドAPI (FastAPI)
├── frontend/         # フロントエンド (HTML/CSS/JS)
├── config/           # 設定ファイル (JSON)
├── images/           # 画像アセット
└── docs/            # ドキュメント
```

## クイックスタート（ローカル環境）

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/[your-username]/persona-render.git
   cd persona-render
   ```

2. **Python環境のセットアップ**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **環境変数の設定**
   `.env`ファイルを作成：
   ```
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   ```

4. **アプリケーションの起動**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

5. **アクセス**
   - ユーザー画面: http://localhost:8000
   - 管理画面: http://localhost:8000/admin

## Renderへのデプロイ

詳細な手順は[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)を参照してください。

### 簡単な手順

1. このリポジトリをGitHubにプッシュ
2. Renderでアカウント作成・GitHubと連携
3. 新しいWeb Serviceを作成
4. 環境変数（APIキー）を設定
5. デプロイ完了！

## カスタマイズ

### 診療科の追加
`config/departments.json`を編集して新しい診療科を追加できます。

### AIモデルの追加
`config/ai_models.json`を編集して新しいAIモデルを追加できます。

### プロンプトの調整
`config/prompt_templates.json`を編集してプロンプトをカスタマイズできます。

詳細は[docs/MAINTENANCE_GUIDE.md](docs/MAINTENANCE_GUIDE.md)を参照してください。

## 技術スタック

- **バックエンド**: FastAPI, Python 3.x
- **フロントエンド**: Vanilla JavaScript, HTML5, CSS3
- **AI**: OpenAI API, Anthropic API, Google Gemini API
- **データベース**: SQLite（RAGデータ用）
- **PDF生成**: FPDF2
- **PPT生成**: python-pptx

## ライセンス

本プロジェクトは商用利用可能です。詳細は[LICENSE](LICENSE)を参照してください。

## 貢献

Issue報告やPull Requestを歓迎します！

## サポート

問題が発生した場合は、以下を確認してください：

1. [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - デプロイに関する問題
2. [docs/MAINTENANCE_GUIDE.md](docs/MAINTENANCE_GUIDE.md) - カスタマイズに関する問題
3. GitHubのIssuesセクション

---

Created with ❤️ by THE DOCTOR'S