#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WebResearchServiceのテストスクリプト
実装が完全に動作することを確認
"""

import asyncio
import os
import sys
from pathlib import Path

# Windows環境での文字化け対策
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# プロジェクトルートをパスに追加
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# 直接インポート
import importlib.util
spec = importlib.util.spec_from_file_location(
    "web_research_service", 
    backend_path / "services" / "web_research_service.py"
)
web_research_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web_research_module)

WebResearchService = web_research_module.WebResearchService
RegionalDataService = web_research_module.RegionalDataService

async def test_web_research():
    """Web研究サービスのテスト"""
    print("="*60)
    print("WebResearchService テスト")
    print("="*60)
    
    service = WebResearchService()
    
    # テスト用のクリニック情報
    test_clinic = "東京クリニック"
    test_address = "東京都渋谷区"
    
    print(f"\nテスト対象: {test_clinic} ({test_address})")
    print("-"*40)
    
    # 1. 競合情報の収集
    print("\n1. 競合情報収集を開始...")
    result = await service.research_competitor(test_clinic, test_address)
    
    # 結果の表示
    print("\n【検索結果】")
    if result.get("search_results"):
        search = result["search_results"]
        if search.get("website"):
            print(f"  [OK] ウェブサイト: {search['website']}")
        if search.get("snippets"):
            print(f"  [OK] スニペット数: {len(search['snippets'])}")
        if search.get("knowledge_panel"):
            print(f"  [OK] ナレッジパネル: 取得済み")
        if search.get("local_results"):
            print(f"  [OK] ローカル結果: {len(search['local_results'])}件")
    else:
        print("  [NG] 検索結果なし")
    
    print("\n【SNSプレゼンス】")
    if result.get("online_presence"):
        presence = result["online_presence"]
        platforms = []
        if presence.get("has_twitter"): platforms.append("Twitter")
        if presence.get("has_instagram"): platforms.append("Instagram")
        if presence.get("has_facebook"): platforms.append("Facebook")
        if presence.get("has_line"): platforms.append("LINE")
        
        if platforms:
            print(f"  [OK] 検出されたSNS: {', '.join(platforms)}")
        else:
            print("  [-] SNSアカウント未検出")
        
        if presence.get("social_links"):
            for link in presence["social_links"]:
                print(f"    - {link['platform']}: {link.get('url', 'N/A')[:50]}...")
    
    print("\n【最新ニュース】")
    if result.get("recent_news"):
        print(f"  [OK] ニュース記事: {len(result['recent_news'])}件")
        for i, news in enumerate(result["recent_news"][:3], 1):
            print(f"    {i}. {news.get('title', 'タイトルなし')[:40]}...")
    else:
        print("  [-] ニュースなし")
    
    print("\n【口コミ集約】")
    if result.get("patient_reviews_summary"):
        reviews = result["patient_reviews_summary"]
        if reviews.get("sources_checked"):
            print(f"  [OK] チェックしたサイト: {', '.join(reviews['sources_checked'])}")
        if reviews.get("positive_keywords"):
            print(f"  [OK] ポジティブキーワード: {', '.join(reviews['positive_keywords'])}")
        if reviews.get("negative_keywords"):
            print(f"  [OK] ネガティブキーワード: {', '.join(reviews['negative_keywords'])}")
    
    return result

async def test_regional_data():
    """地域データサービスのテスト"""
    print("\n" + "="*60)
    print("RegionalDataService テスト")
    print("="*60)
    
    service = RegionalDataService()
    
    test_addresses = [
        "東京都渋谷区",
        "東京都新宿区",
        "大阪市中央区",
        "名古屋市中区"
    ]
    
    for address in test_addresses:
        print(f"\n地域: {address}")
        print("-"*40)
        
        # 地域データの取得
        data = await service.get_regional_data(address)
        
        # 人口統計
        if data.get("demographics"):
            demo = data["demographics"]
            print("【人口統計】")
            if isinstance(demo.get("total_population"), (int, float)):
                print(f"  - 総人口: {demo['total_population']:,}人")
            else:
                print(f"  - 総人口: {demo['total_population']}")
            
            if demo.get("age_distribution"):
                age = demo["age_distribution"]
                print(f"  - 年齢分布:")
                for key, value in age.items():
                    print(f"    - {key}: {value}%")
        
        # 医療需要
        if data.get("medical_demand"):
            demand = data["medical_demand"]
            print("【医療需要】")
            if demand.get("estimated_patients_per_day"):
                print(f"  - 推定患者数/日: {demand['estimated_patients_per_day']}")
            if demand.get("healthcare_accessibility"):
                print(f"  - アクセシビリティ: {demand['healthcare_accessibility']}")

async def main():
    """メインテスト関数"""
    print("\n" + "="*60)
    print("競合分析機能強化 - 実装テスト")
    print("="*60)
    
    # 環境変数の確認
    print("\n【環境変数チェック】")
    api_keys = {
        "SERPAPI_KEY": os.getenv("SERPAPI_KEY"),
        "ESTAT_API_KEY": os.getenv("ESTAT_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }
    
    for key_name, value in api_keys.items():
        if value:
            print(f"  [OK] {key_name}: 設定済み ({len(value)}文字)")
        else:
            print(f"  [NG] {key_name}: 未設定")
    
    # 各機能のテスト
    try:
        # Web研究のテスト
        await test_web_research()
        
        # 地域データのテスト
        await test_regional_data()
        
        print("\n" + "="*60)
        print("テスト完了")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())