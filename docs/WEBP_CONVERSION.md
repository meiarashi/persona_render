# WebP画像変換ガイド

## 概要
このプロジェクトはWebP画像形式を優先的に使用し、非対応ブラウザのためにPNGフォールバックを提供します。

## 現在の実装

### 1. 自動フォールバック機能
- **診療科アイコン**: JavaScript（`applyWebPFallback()`）で自動的にWebP→PNGフォールバック
- **患者タイプアイコン**: 既存の実装でWebP→PNGフォールバック対応済み
- **その他の画像（owl.png等）**: DOMContentLoadedで自動的にWebP変換を試行

### 2. 動作の流れ
1. ページ読み込み時、すべての画像URLを`.webp`に変更
2. WebP画像の読み込みに失敗した場合、自動的に`.png`にフォールバック
3. ユーザーには透過的に動作（エラーは表示されない）

## WebP画像の作成方法

### 方法1: オンラインツール
1. [Squoosh](https://squoosh.app/) - Googleの画像最適化ツール
2. [CloudConvert](https://cloudconvert.com/png-to-webp) - 一括変換対応
3. [Convertio](https://convertio.co/ja/png-webp/) - ドラッグ&ドロップ対応

### 方法2: コマンドライン（Linux/Mac）

```bash
# cwebpツールのインストール
# Ubuntu/Debian
sudo apt-get install webp

# Mac (Homebrew)
brew install webp

# PNG → WebP変換（品質90%）
for file in *.png; do
    cwebp -q 90 "$file" -o "${file%.png}.webp"
done
```

### 方法3: Python スクリプト

```python
from PIL import Image
import os

def convert_to_webp(source_dir, quality=90):
    for filename in os.listdir(source_dir):
        if filename.endswith('.png'):
            png_path = os.path.join(source_dir, filename)
            webp_path = os.path.join(source_dir, filename.replace('.png', '.webp'))
            
            img = Image.open(png_path)
            img.save(webp_path, 'WEBP', quality=quality)
            print(f"Converted: {filename} -> {filename.replace('.png', '.webp')}")

# 使用例
convert_to_webp('/path/to/images/', quality=85)
```

## 推奨設定

### 画質設定
- アイコン画像: 85-90%（ファイルサイズと品質のバランス）
- 写真: 80-85%（より高い圧縮率）
- ロゴ・テキスト含む画像: 90-95%（品質優先）

### ファイルサイズの目安
- PNG: 平均 50-100KB
- WebP: 平均 15-40KB（60-70%削減）

## メリット

1. **ファイルサイズ削減**: 通常30-70%のサイズ削減
2. **読み込み速度向上**: 特にモバイルユーザーに効果的
3. **Render無料プランに最適**: 帯域幅とストレージの節約
4. **透過対応**: PNGと同様にアルファチャンネル対応

## 注意事項

1. **ブラウザ対応**
   - Chrome, Edge, Firefox: 完全対応
   - Safari: iOS 14以降、macOS Big Sur以降で対応
   - IE: 非対応（PNGフォールバックが動作）

2. **デプロイ時の確認**
   - WebPファイルが正しくアップロードされているか確認
   - フォールバックが正常に動作するかテスト

3. **新しい画像の追加時**
   - 必ずPNG版も保持する（フォールバック用）
   - 可能な限りWebP版も作成する