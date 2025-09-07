#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
改良版e-Stat統合サービスのテスト
"""

import asyncio
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# APIキーを設定
os.environ["ESTAT_API_KEY"] = "992fa8d6f43d645c3c767a97410fe89612cfecc7"

from backend.services.estat_integrated_service_v2 import EStatIntegratedServiceV2
from backend.services.medical_demand_calculator import MedicalDemandCalculator

async def test_v2_service():
    """改良版サービスのテスト"""
    print("="*60)
    print("改良版e-Stat統合サービステスト")
    print("="*60)
    
    service = EStatIntegratedServiceV2()
    
    # テスト用の住所リスト
    test_addresses = [
        "東京都千代田区",
        "大阪府大阪市北区",
        "北海道札幌市中央区"
    ]
    
    for address in test_addresses:
        print(f"\n【{address}のデータ取得】")
        print("-"*40)
        
        try:
            # データ取得
            data = await service.get_regional_data(address)
            
            print(f"[結果]")
            print(f"  地域コード: {data.get('area_code', 'N/A')}")
            print(f"  人口: {data.get('population', {}).get('total', 'N/A'):,}人")
            print(f"  高齢化率: {data.get('demographics', {}).get('aging_rate', 'N/A')}%")
            print(f"  地域タイプ: {data.get('area_type', 'N/A')}")
            print(f"  世帯数: {data.get('households', {}).get('total', 'N/A'):,}世帯")
            
            # 医療需要データ
            medical = data.get('medical_demand', {})
            if medical:
                print(f"\n  [医療需要]")
                print(f"  推定外来患者数: {medical.get('estimated_daily_patients', 'N/A'):,}人/日")
                print(f"  受療率: {medical.get('consultation_rate', 'N/A'):.1f}/10万人")
                
                # 診療科別内訳（上位3つ）
                dept_breakdown = medical.get('department_breakdown', {})
                if dept_breakdown:
                    print(f"\n  [診療科別（上位3科）]")
                    sorted_depts = sorted(dept_breakdown.items(), 
                                        key=lambda x: x[1].get('患者数/日', 0), 
                                        reverse=True)[:3]
                    for dept, info in sorted_depts:
                        print(f"    {dept}: {info['患者数/日']:,}人/日")
            
            print(f"\n  データソース: {data.get('data_source', 'unknown')}")
                
        except Exception as e:
            print(f"[ERROR] エラー: {e}")
            import traceback
            traceback.print_exc()

async def test_area_code_detection():
    """地域コード判定のテスト"""
    print("\n" + "="*60)
    print("地域コード判定テスト")
    print("="*60)
    
    service = EStatIntegratedServiceV2()
    
    test_cases = [
        "東京都千代田区",
        "東京都港区六本木",
        "大阪府大阪市北区梅田",
        "京都府京都市中京区",
        "沖縄県那覇市",
        "北海道札幌市中央区",
        "福岡県福岡市博多区"
    ]
    
    for address in test_cases:
        area_code = service._parse_address_to_code(address)
        print(f"{address:30} -> {area_code}")

async def test_medical_demand_integration():
    """医療需要計算との統合テスト"""
    print("\n" + "="*60)
    print("医療需要計算統合テスト")
    print("="*60)
    
    service = EStatIntegratedServiceV2()
    calculator = MedicalDemandCalculator()
    
    address = "東京都渋谷区"
    print(f"\n【{address}の詳細分析】")
    print("-"*40)
    
    # 地域データ取得
    regional_data = await service.get_regional_data(address)
    
    if regional_data:
        population = regional_data.get("population", {}).get("total", 100000)
        age_dist = regional_data.get("demographics", {}).get("age_distribution", {
            "0-14": 10, "15-64": 70, "65+": 20
        })
        area_type = regional_data.get("area_type", "urban_high_density")
        
        print(f"基本情報:")
        print(f"  人口: {population:,}人")
        print(f"  地域タイプ: {area_type}")
        print(f"  高齢化率: {age_dist.get('65+', 20)}%")
        
        # 内科に特化した分析
        demand = calculator.calculate_area_demand(
            population=population,
            age_distribution=age_dist,
            area_type=area_type,
            target_department="内科"
        )
        
        print(f"\n内科の需要分析:")
        for dept, info in demand["department_breakdown"].items():
            print(f"  推定患者数: {info['患者数/日']:,}人/日")
            print(f"  主要疾患: {', '.join(info['主要疾患'][:3])}")
        
        # 競合分析シミュレーション
        print(f"\n競合環境シミュレーション:")
        scenarios = [
            {"competitors": 5, "features": {"土曜診療": True}},
            {"competitors": 10, "features": {"土曜診療": True, "夜間診療": True}},
            {"competitors": 15, "features": {"土曜診療": True, "最新設備": True, "駐車場": True}}
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            share = calculator.calculate_clinic_share(
                area_daily_patients=demand["total_daily_patients"],
                num_competitors=scenario["competitors"],
                clinic_features=scenario["features"]
            )
            print(f"\n  シナリオ{i} (競合{scenario['competitors']}施設):")
            print(f"    市場シェア: {share['market_share_percentage']}%")
            print(f"    推定患者数: {share['estimated_daily_patients']:,}人/日")

async def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("e-Stat API統合システム V2 総合テスト")
    print("="*60)
    print(f"APIキー: {os.environ.get('ESTAT_API_KEY', 'Not Set')[:10]}...")
    
    # 各テストを実行
    await test_v2_service()
    await test_area_code_detection()
    await test_medical_demand_integration()
    
    print("\n" + "="*60)
    print("テスト完了")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())