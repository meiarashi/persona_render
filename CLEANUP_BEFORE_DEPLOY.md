# デプロイ前のクリーンアップ

デプロイ前に以下のクリーンアップを実行することを推奨します。

## 削除推奨ディレクトリ/ファイル

### 1. 重複している画像ディレクトリ
```bash
# これらは削除可能（/images/に統合済み）
rm -rf assets/images/
rm -rf frontend/images/
```

### 2. 古いバックエンドディレクトリ
```bash
# 旧構造の残骸
rm -rf backend/app/
```

### 3. ローカル開発用ファイル
```bash
# もし存在する場合
rm -rf __pycache__/
rm -rf .pytest_cache/
rm -rf .coverage
rm -rf htmlcov/
rm -rf *.pyc
```

### 4. 設定バックアップ（必要に応じて）
```bash
# ローカルのバックアップは削除
rm -rf config/backups/*
```

## 確認事項

### 必須ファイル/ディレクトリ
- [x] `/backend/` - バックエンドコード
- [x] `/frontend/` - フロントエンドコード
- [x] `/images/` - 画像ファイル（フラット構造）
- [x] `/config/` - 設定ファイル
- [x] `/assets/fonts/` - フォントファイル
- [x] `requirements.txt` - Python依存関係
- [x] `render.yaml` - Render設定
- [x] `.gitignore` - Git除外設定
- [x] `README.md` - プロジェクト説明
- [x] `DEPLOYMENT_GUIDE.md` - デプロイ手順

### オプション（開発用）
- [ ] `/docs/` - 追加ドキュメント
- [ ] `/instance/` - ローカルDB（.gitignoreに含まれる）

## コマンド一覧

一括クリーンアップ（Linux/Mac）:
```bash
# 重複ディレクトリの削除
rm -rf assets/images/ frontend/images/ backend/app/

# Pythonキャッシュの削除
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete

# 一時ファイルの削除
find . -type f -name "*.tmp" -delete
find . -type f -name "*.bak" -delete
```

Windows (PowerShell):
```powershell
# 重複ディレクトリの削除
Remove-Item -Recurse -Force assets\images, frontend\images, backend\app -ErrorAction SilentlyContinue

# Pythonキャッシュの削除
Get-ChildItem -Directory -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -File -Recurse -Filter "*.pyc" | Remove-Item -Force

# 一時ファイルの削除
Get-ChildItem -File -Recurse -Filter "*.tmp" | Remove-Item -Force
Get-ChildItem -File -Recurse -Filter "*.bak" | Remove-Item -Force
```

## 最終チェック

デプロイ前に以下を確認：

1. **画像アクセス**
   - `/images/owl.png`が存在するか
   - 診療科アイコンがすべて存在するか

2. **設定ファイル**
   - `/config/*.json`がすべて有効なJSONか
   - 文字エンコーディングがUTF-8か

3. **環境変数**
   - `.env`ファイルがGitに含まれていないか
   - APIキーがコードに含まれていないか

4. **依存関係**
   - `requirements.txt`が最新か
   - 不要な依存関係が含まれていないか

これらの確認が完了したら、GitHubにプッシュしてRenderでデプロイできます！