# デザインガイドライン

## 概要
このドキュメントは、医療系ペルソナ自動生成AIシステムの統一されたデザインルールを定義します。
すべての画面で一貫性のあるユーザー体験を提供するため、以下のガイドラインに従ってください。

## カラーパレット

### プライマリカラー
- **メイン**: `#28a745` (緑) - 成功、アクション、選択状態
- **ホバー**: `#218838` (濃い緑)
- **選択状態の背景**: `#f8fff9` (薄い緑)
- **選択状態の枠線**: `rgba(40, 167, 69, 0.6)`

### セカンダリカラー
- **グレー**: `#6c757d` - 戻るボタン、サブアクション
- **グレーホバー**: `#5a6268`

### UIカラー
- **プライマリブルー**: `#007bff` - リンク、情報系ボタン
- **ブルーホバー**: `#0056b3`
- **エラー**: `#dc3545` (赤)
- **警告**: `#ffc107` (黄)
- **情報**: `#17a2b8` (水色)

### 背景・枠線
- **メイン背景**: `#f8f9fa`
- **カード背景**: `#ffffff`
- **枠線**: `#dee2e6`
- **薄い枠線**: `#e9ecef`
- **テキスト**: `#333`
- **サブテキスト**: `#495057`
- **補助テキスト**: `#6c757d`

## タイポグラフィ

### フォントファミリー
```css
font-family: 'Helvetica Neue', Arial, sans-serif;
```

### フォントサイズ
- **基本**: `13px` (body)
- **通常テキスト**: `1em`
- **見出し (h3)**: `1.3em`
- **見出し (h4)**: `1.1em`
- **小さいテキスト**: `0.9em`
- **極小テキスト**: `0.86em`

### フォントウェイト
- **通常**: `normal`
- **太字**: `bold` (見出し、ボタン、ラベル)

## コンポーネント

### ボタン
```css
.btn {
    padding: 10px 12px;
    border: none;
    border-radius: 5px;
    font-size: 1em;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s ease;
    margin-top: 10px;
    box-sizing: border-box;
}
```

### カード・コンテナ
```css
.card {
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    padding: 20px;
}
```

### フォーム要素
```css
input[type="text"], textarea, select {
    width: 100%;
    padding: 10px 15px;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 14px;
    transition: border-color 0.15s ease-in-out;
}

input:focus, textarea:focus, select:focus {
    outline: none;
    border-color: #80bdff;
    box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}
```

### 選択可能なオプション（ラジオボタン・チェックボックス風）
```css
.option-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 15px;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    background-color: #ffffff;
    text-align: center;
}

.option-card:hover {
    border-color: #28a745;
    background-color: #f8fff9;
}

.option-card.selected {
    border-color: #28a745;
    background-color: #f8fff9;
    box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
}
```

### モーダル
```css
.modal-dialog {
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.modal-header {
    padding: 20px 25px;
    border-bottom: 1px solid #dee2e6;
    background-color: #ffffff;
}

.modal-header h3 {
    color: #333;
    font-size: 1.3em;
    font-weight: bold;
}

/* エラーモーダル */
.modal-dialog.error .modal-header {
    background-color: #fff5f5;
    border-bottom-color: #fecaca;
}

.modal-dialog.error .modal-header h3 {
    color: #dc3545;
}
```

## レイアウト

### グリッドシステム
- **診療科選択**: 8列グリッド（レスポンシブ時は自動調整）
- **作成目的/分析範囲**: 3列固定幅グリッド（216px × 3）
- **フォーム**: 3列グリッド（レスポンシブ時は1列）

### スペーシング
- **セクション間**: `20px`
- **要素間**: `10px` - `15px`
- **パディング（カード内）**: `20px`
- **パディング（ボタン）**: `10px 12px`

### コンテナ幅
- **最大幅**: `1200px`
- **中央寄せ**: `margin: 0 auto`

## アニメーション・トランジション

### 基本トランジション
```css
transition: all 0.2s ease;
/* または */
transition: background-color 0.2s ease;
```

### ホバーエフェクト
- ボタン: 背景色の変更
- カード: `transform: translateY(-2px);`
- 選択可能要素: 背景色と枠線の変更

## レスポンシブデザイン

### ブレークポイント
- タブレット: `@media (max-width: 992px)`
- モバイル: `@media (max-width: 768px)`

### モバイル対応
- グリッドを1列に変更
- ボタンを全幅に
- フォントサイズを14pxに拡大

## アイコン

### サイズ
- 大アイコン: `85px × 85px`
- 中アイコン: `64px × 64px`
- 小アイコン: `30px × 30px`

## 実装上の注意点

1. **一貫性**: すべての画面で同じスタイルを使用する
2. **アクセシビリティ**: 適切なコントラスト比を保つ
3. **パフォーマンス**: 不要なアニメーションは避ける
4. **保守性**: 共通スタイルはベースCSSに定義する

## 更新履歴
- 2024年8月: 初版作成
- 競合分析ページのデザインをペルソナ生成ページに統一