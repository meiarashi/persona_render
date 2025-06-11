# メンテナンスガイド

## 概要
このガイドでは、persona_renderシステムのメンテナンス性を向上させるための新しい構造について説明します。

## 新しいディレクトリ構造

```
persona_render/
├── config/                    # 設定ファイル（JSONフォーマット）
│   ├── departments.json       # 診療科設定
│   ├── purposes.json          # 目的設定  
│   ├── patient_types.json     # 患者タイプ設定
│   ├── ai_models.json         # AIモデル設定
│   ├── prompt_templates.json  # プロンプトテンプレート
│   └── backups/              # 設定ファイルの自動バックアップ
│
├── backend/
│   ├── api/                  # APIエンドポイント
│   │   ├── admin_settings.py # 管理設定API
│   │   └── config.py         # 設定読み込みAPI
│   │
│   ├── utils/                # ユーティリティ
│   │   ├── config_loader.py  # 設定ファイル読み込み
│   │   ├── prompt_builder.py # プロンプト構築
│   │   └── config_manager.py # 設定ファイル書き込み・管理
│   │
│   └── main.py              # メインアプリケーション
```

## メンテナンス作業

### 1. 診療科の追加

`config/departments.json`を編集：

```json
{
  "id": "new_department",
  "name_ja": "新診療科",
  "icon": "新診療科.png",
  "order": 31,
  "enabled": true
}
```

注意：
- `id`は他と重複しないこと
- `icon`ファイルを`/images/`に配置すること
- `order`で表示順序を制御

### 2. 患者タイプの追加

`config/patient_types.json`を編集：

```json
{
  "id": "new_type",
  "value": "新患者タイプ",
  "description": "患者タイプの説明",
  "example": "例となる患者像",
  "order": 13,
  "enabled": true
}
```

### 3. プロンプトの変更

`config/prompt_templates.json`を編集：

- 基本テンプレートの変更
- 出力項目の追加・削除
- デフォルト文字数の変更

### 4. AIモデルの追加

`config/ai_models.json`を編集：

```json
{
  "id": "new-model-id",
  "provider": "provider_name",
  "name": "表示名",
  "max_tokens": 100000,
  "default_temperature": 0.7,
  "default_max_tokens": 2000,
  "enabled": true,
  "order": 10
}
```

## API経由での設定取得

### 診療科一覧の取得
```
GET /api/config/departments
```

### 患者タイプ一覧の取得
```
GET /api/config/patient-types
```

### AIモデル一覧の取得
```
GET /api/config/ai-models
```

## プログラムでの使用例

```python
from backend.utils import config_loader

# 診療科マップの取得
dept_map = config_loader.get_department_map()

# 患者タイプ詳細の取得
patient_types = config_loader.get_patient_type_details_map()

# プロンプトの生成
from backend.utils import prompt_builder
prompt = prompt_builder.build_persona_prompt(data, char_limits, rag_context)
```

## 注意事項

1. **JSON形式の維持**: 編集時は必ず有効なJSONフォーマットを維持してください
2. **文字エンコーディング**: UTF-8で保存してください
3. **バックアップ**: 自動的に`backups/`に保存されますが、大きな変更前は手動バックアップも推奨
4. **キャッシュ**: 設定は起動時に読み込まれキャッシュされます。変更後はアプリケーションの再起動が必要です

## トラブルシューティング

### 設定が反映されない
- アプリケーションを再起動してください
- JSON形式が正しいか確認してください

### 画像が表示されない
- アイコンファイルが`/images/`に存在するか確認
- ファイル名が設定と一致しているか確認

### エラーが発生する
- `config/backups/`から最新のバックアップを復元
- JSONの構文エラーをチェック