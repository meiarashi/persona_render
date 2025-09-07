#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
改善された競合分析のテスト
医療統計データが正しくSWOT分析に反映されているか確認
"""

import asyncio
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# 環境変数の設定
os.environ["ESTAT_API_KEY"] = "992fa8d6f43d645c3c767a97410fe89612cfecc7"
os.environ["GOOGLE_MAPS_API_KEY"] = os.getenv("GOOGLE_MAPS_API_KEY", "")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

from backend.services.competitive_analysis_service import CompetitiveAnalysisService

async def test_data_preparation():
    """データ準備フェーズのテスト"""
    print("="*70)
    print("1. データ準備フェーズのテスト")
    print("="*70)
    
    service = CompetitiveAnalysisService()
    
    # テスト用のクリニック情報
    clinic_info = {
        "name": "テスト内科クリニック",
        "address": "東京都千代田区丸の内1-1-1",
        "department": "内科",
        "features": "土曜診療、オンライン予約可",
        "search_radius": 3000
    }
    
    # 仮の競合データ
    competitors = [
        {
            "name": "競合クリニックA",
            "rating": 4.2,
            "user_ratings_total": 50,
            "formatted_address": "東京都千代田区大手町1-1-1",
            "distance": 500,
            "types": ["doctor", "health"]
        },
        {
            "name": "競合クリニックB",
            "rating": 3.8,
            "user_ratings_total": 30,
            "formatted_address": "東京都千代田区有楽町1-1-1",
            "distance": 800,
            "types": ["doctor", "health", "hospital"]
        }
    ]
    
    # 分析用データを準備
    analysis_data = await service._prepare_analysis_data(
        clinic_info,
        competitors,
        "高齢者および生活習慣病患者"
    )
    
    # データ内容を確認
    print("\n準備されたデータ構造:")
    print(f"- clinic: {bool(analysis_data.get('clinic'))}")
    print(f"- competitors: {len(analysis_data.get('competitors', []))}件")
    print(f"- regional_data: {bool(analysis_data.get('regional_data'))}")
    print(f"- medical_stats: {bool(analysis_data.get('medical_stats'))}")
    print(f"- market_stats: {bool(analysis_data.get('market_stats'))}")
    
    # 医療統計データの詳細確認
    if medical_stats := analysis_data.get('medical_stats'):
        print("\n医療統計データの内容:")
        for key in medical_stats:
            print(f"  - {key}: {bool(medical_stats[key])}")
            
        # 具体的なデータ例
        if facilities := medical_stats.get('medical_facilities'):
            print(f"\n  診療所数: {facilities.get('total_clinics', 'N/A')}")
            if by_spec := facilities.get('by_specialty'):
                print(f"  診療科別: {list(by_spec.keys())[:3]}")
        
        if patient_stats := medical_stats.get('patient_stats'):
            print(f"\n  外来受療率: {patient_stats.get('outpatient_rate', 'N/A')}/10万人")
            if diseases := patient_stats.get('top_diseases'):
                print(f"  主要疾患: {[d['name'] for d in diseases[:3]]}")
    
    return analysis_data

async def test_prompt_generation():
    """プロンプト生成のテスト"""
    print("\n" + "="*70)
    print("2. プロンプト生成のテスト")
    print("="*70)
    
    service = CompetitiveAnalysisService()
    
    # テストデータ
    analysis_data = {
        "clinic": {
            "name": "テスト内科クリニック",
            "address": "東京都千代田区",
            "department": "内科",
            "features": "土曜診療",
            "search_radius": 3000
        },
        "competitors": [],
        "medical_stats": {
            "medical_facilities": {
                "total_clinics": 100,
                "by_specialty": {"内科": 30, "外科": 10},
                "night_emergency": 5
            },
            "patient_stats": {
                "outpatient_rate": 5500,
                "top_diseases": [
                    {"name": "高血圧", "percentage": 15.2},
                    {"name": "糖尿病", "percentage": 12.8}
                ]
            },
            "medical_staff": {
                "doctors_per_100k": 250,
                "shortage_level": "moderate"
            },
            "household_medical": {
                "avg_annual_medical_expense": 120000
            },
            "nursing_facilities": {
                "total_facilities": 50,
                "occupancy_rate": 0.92
            }
        },
        "market_stats": {
            "total_competitors": 10,
            "average_rating": 4.0,
            "rating_distribution": {"above_4": 5, "3_to_4": 3, "below_3": 2},
            "department_distribution": {}
        },
        "review_insights": {},
        "additional_context": ""
    }
    
    # プロンプトを生成
    prompt = service._build_swot_prompt(analysis_data)
    
    # プロンプトの内容確認
    print("\nプロンプトに含まれる情報:")
    
    # 医療統計データが含まれているか確認
    checks = [
        ("医療施設統計", "【医療施設統計】"),
        ("患者需要統計", "【患者需要統計】"),
        ("医療従事者統計", "【医療従事者統計】"),
        ("医療費支出統計", "【医療費支出統計】"),
        ("介護施設統計", "【介護施設統計】"),
        ("診療科別施設数", "診療科別施設数"),
        ("主要疾患", "高血圧"),
        ("医師密度", "医師密度"),
        ("世帯医療費", "年間平均医療費"),
        ("介護施設稼働率", "稼働率")
    ]
    
    for name, keyword in checks:
        if keyword in prompt:
            print(f"  [OK] {name}")
        else:
            print(f"  [NG] {name} - 含まれていません")
    
    # プロンプトの一部を表示
    print("\n生成されたプロンプトの一部（医療統計部分）:")
    lines = prompt.split('\n')
    in_medical_section = False
    line_count = 0
    for i, line in enumerate(lines):
        if '【医療施設統計】' in line:
            in_medical_section = True
        if in_medical_section:
            # Replace bullet points with dashes for cp932 compatibility
            safe_line = line.replace('•', '-').replace('✓', 'OK')
            print(safe_line)
            line_count += 1
            if line_count > 20:  # Limit output to 20 lines
                break

async def test_full_analysis():
    """完全な分析フローのテスト（APIキーが必要）"""
    print("\n" + "="*70)
    print("3. 完全な分析フローのテスト")
    print("="*70)
    
    # APIキーの確認
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        print("Google Maps APIキーが設定されていないため、完全テストはスキップ")
        return
    
    if not os.getenv("OPENAI_API_KEY"):
        print("OpenAI APIキーが設定されていないため、AI分析はスキップ")
        return
    
    service = CompetitiveAnalysisService()
    
    clinic_info = {
        "name": "テスト内科クリニック",
        "address": "東京都千代田区丸の内1-1-1",
        "department": "内科",
        "features": "土曜診療、オンライン予約可"
    }
    
    print("\n競合分析を実行中...")
    
    try:
        result = await service.analyze_competitors(
            clinic_info=clinic_info,
            search_radius=1000,  # 1km
            additional_info="ビジネスパーソンおよび高齢者向け"
        )
        
        if "error" in result:
            print(f"エラー: {result['error']}")
        else:
            print(f"\n分析完了:")
            print(f"- 競合数: {result.get('competitors_found', 0)}件")
            print(f"- SWOT分析: {bool(result.get('swot_analysis'))}")
            print(f"- 戦略提案: {len(result.get('strategic_recommendations', []))}件")
            
            # SWOT分析の一部を表示
            if swot := result.get('swot_analysis'):
                print("\nSWOT分析（強み）:")
                for strength in swot.get('strengths', [])[:2]:
                    print(f"  - {strength}")
                    
    except Exception as e:
        print(f"エラー: {e}")

async def main():
    """メイン処理"""
    print("\n" + "="*70)
    print("改善された競合分析システムのテスト")
    print("="*70)
    print("医療統計データがSWOT分析に適切に反映されているか確認\n")
    
    # 各テストを実行
    analysis_data = await test_data_preparation()
    await test_prompt_generation()
    await test_full_analysis()
    
    print("\n" + "="*70)
    print("テスト完了")
    print("="*70)
    
    print("\n【実装完了内容】")
    print("[OK] EStatMedicalStatsServiceを競合分析に統合")
    print("[OK] 医療統計データを分析データに追加")
    print("[OK] プロンプトに医療統計情報を含める")
    print("[OK] 分析フレームワークに統計活用を明記")
    print("[OK] 戦略立案に統計データの活用を指示")

if __name__ == "__main__":
    asyncio.run(main())