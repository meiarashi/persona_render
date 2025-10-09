# パフォーマンス最適化ガイド

## システム特性

### アーキテクチャ
- **フレームワーク**: FastAPI（非同期）
- **Webサーバー**: Gunicorn + Uvicorn Workers
- **処理タイプ**: I/O Bound（AI API待機が主）
- **並列処理**: asyncio.create_task（テキスト・画像生成が並列）

### 処理時間の内訳
| 処理 | 平均時間 | CPU使用率 | ボトルネック |
|------|----------|-----------|--------------|
| RAGデータ検索 | 0.1秒 | 低 | SQLite I/O |
| AI生成（テキスト） | 3-15秒 | **なし** | 外部API待ち |
| AI生成（画像） | 10-30秒 | **なし** | 外部API待ち |
| タイムライン分析 | 5-10秒 | **なし** | 外部API待ち |
| PDF生成 | 1-2秒 | 中 | CPU処理 |
| 競合分析 | 10-20秒 | **なし** | Google Maps API待ち |

**重要**: システム全体の約95%の時間が「外部API待ち」= CPU使用なし

---

## Worker設定の最適化

### 現在の環境
- **サーバー**: Render Standard
- **CPU**: 1 Core
- **メモリ**: 2 GB
- **Worker平均メモリ**: 500-700MB/worker

### Worker数の計算式

#### I/O Bound + 非同期処理の場合
```
最適Worker数 = min(
    CPU × 4-8,                    # 非同期I/O boundの推奨範囲
    利用可能メモリ / Worker平均メモリ,  # メモリ制約
    ピーク同時ユーザー数 / 10         # 経験則
)
```

#### 本システムの計算
```
CPU基準: 1 × 4-8 = 4-8 workers
メモリ基準: 2048MB / 600MB = 3.4 workers → 3 workers（安全）
ユーザー基準: 50人 / 10 = 5 workers

結果: min(4-8, 3, 5) = 3 workers
```

---

## 推奨設定

### ✅ 最適設定（推奨）

```bash
gunicorn backend.main:app \
  --workers 3 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:10000 \
  --timeout 300 \
  --graceful-timeout 120 \
  --worker-connections 500 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

**特徴**:
- メモリ使用量: 1.5-2.1GB（安全マージン20%）
- 同時AI生成: 3リクエスト
- 同時軽量リクエスト: 1500接続（500 × 3）
- OOMリスク: 低

**期待されるパフォーマンス**:
- ペルソナ生成中でも他ユーザーがスムーズにログイン可能
- 同時3ユーザーがペルソナ生成可能
- 閲覧のみのユーザー: 数百人同時対応

---

### ⚠️ 現在の設定（workers 4）

```bash
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:10000 \
  --timeout 300 \
  --graceful-timeout 120 \
  --worker-connections 300 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

**リスク**:
- メモリ使用量: 2.0-2.8GB（**容量超過の可能性**）
- OOMキラーが発動する可能性: 中（通常のAI生成のみなら低、画像/PDF生成が重なると高）
- 複数ユーザーが同時に**画像生成・PDF生成**した場合、メモリ不足で503エラー
- AI生成（テキストのみ）は1リクエスト約30MBと軽量なため、通常は問題なし

**症状**:
```
# Renderログに以下が表示される場合はOOM発生
[WARNING] Worker (pid:XXX) was sent SIGKILL! Perhaps out of memory?
```

---

### 💡 代替案1: Worker数を減らして接続数を増やす

```bash
gunicorn backend.main:app \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:10000 \
  --timeout 300 \
  --graceful-timeout 120 \
  --worker-connections 1000 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

**メリット**:
- メモリ使用量: 1.0-1.4GB（**非常に安全**）
- OOMリスク: ほぼなし
- 非同期処理のため、connection数を増やせば同時処理可能

**デメリット**:
- 同時AI生成: 2リクエストまで（worker数に依存）

---

## モニタリング指標

### 正常な状態
| 指標 | 目標値 |
|------|--------|
| CPU使用率 | 10-30%（AI待ち時間が長いため低くて正常） |
| メモリ使用率 | 70-80%以下 |
| レスポンスタイム（P95） | 30秒以内 |
| エラー率 | 1%未満 |

### 警告サイン
- **メモリ使用率 > 90%**: Worker数を減らす
- **CPU使用率 > 80%**: ボトルネックを調査（通常発生しないはず）
- **503エラー頻発**: Worker数を減らすか、タイムアウトを延長
- **ログに "SIGKILL" 出現**: OOM発生、Worker数を即座に削減

---

## パフォーマンスチューニング

### シナリオ別の最適設定

#### 1. 通常利用（10-30人/日）
```bash
--workers 2 --worker-connections 1000
```
- 最も安定
- メモリ余裕あり

#### 2. ピーク時（50-100人/日）
```bash
--workers 3 --worker-connections 500
```
- バランス型（本推奨設定）
- メモリギリギリだが対応可能

#### 3. 大量アクセス（100人以上/日）
**Renderプランをアップグレード推奨**
```
Standard → Pro (2 CPU, 4 GB)
--workers 6 --worker-connections 500
```

---

## トラブルシューティング

### 問題: ペルソナ生成中に他ユーザーがログインできない
**原因**: Worker数が不足
**解決**: Workers 2以上に設定

### 問題: 503 Service Unavailable エラー
**原因**:
1. 全workerがAI生成で占有されている
2. タイムアウト設定が短すぎる

**解決**:
1. Worker数を増やす（メモリ許す限り）
2. `--timeout` を延長（現在300秒）

### 問題: メモリ不足でアプリケーションが再起動
**原因**: Worker数が多すぎる
**解決**: Worker数を減らす（3 → 2）

### 問題: AI生成が遅い
**原因**: 外部APIの応答時間（システム側では改善不可）
**確認方法**:
```python
# ログで確認
[AI] Response time: X seconds
```

**対策**:
1. より高速なAIモデルを選択（例: gpt-4o-mini）
2. 並列処理は既に実装済み（テキスト・画像同時生成）

---

## 推奨アクション

### 即座に実施
1. **Worker数を4から3に変更**（OOM回避）
2. Renderダッシュボードでメモリ使用率を監視

### 今後の改善
1. **キャッシュ強化**:
   - 主訴データのメモリキャッシュ（既に実装済み）
   - ペルソナ画像のCDN配信

2. **外部API最適化**:
   - APIレスポンスのストリーミング処理
   - タイムアウト設定の最適化

3. **スケールアウト検討**:
   - ユーザー数が100人/日を超えたらプランアップグレード
   - 2 CPU, 4 GB RAM → workers 6-8に増強可能

---

## まとめ

### あなたのシステムに最適な設定

```bash
gunicorn backend.main:app \
  --workers 3 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:10000 \
  --timeout 300 \
  --graceful-timeout 120 \
  --worker-connections 500 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

### なぜWorker 3が最適か

1. **メモリ制約**: 2GB ÷ 600MB = 3.3 workers（安全マージン20%で3）
2. **I/O Bound**: CPUではなくAPI待ちがボトルネック → Worker増やしても効果薄い
3. **並列処理済み**: asyncioで既に効率化されている
4. **実用性**: 同時3ユーザーのAI生成に対応、十分なパフォーマンス

### Workers 4のリスク

- メモリ: 2.0-2.8GB使用（**2GBを超える可能性**）
- OOM Killerの発動リスク
- 複数ユーザー同時アクセス時に503エラー

### 結論

**Worker 3に変更することを強く推奨します。**

現在の設定（Worker 4）は理論的には動作しますが、実際の運用では**メモリ不足による予期せぬダウンタイムのリスク**があります。
