#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e-Stat統合サービスのテスト
"""

import asyncio
import os
import sys
from pathlib import Path
import json

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# APIキーを設定
os.environ["ESTAT_API_KEY"] = "992fa8d6f43d645c3c767a97410fe89612cfecc7"

from backend.services.estat_integrated_service import EStatIntegratedService
from backend.services.medical_demand_calculator import MedicalDemandCalculator

async def test_estat_api():
    """e-Stat APIの動作確認"""
    print("="*60)
    print("e-Stat API統合テスト")
    print("="*60)
    
    # サービスの初期化
    service = EStatIntegratedService()
    
    if not service.api_key:
        print("[ERROR] APIキーが設定されていません")
        return
    
    print(f"[OK] APIキー設定済み: {service.api_key[:10]}...")
    
    # テスト用の住所リスト
    test_addresses = [
        "東京都千代田区",
        "大阪府大阪市北区",
        "北海道札幌市中央区",
        "福岡県福岡市博多区",
        "京都府京都市中京区"
    ]
    
    for address in test_addresses:
        print(f"\n【{address}のデータ取得】")
        print("-"*40)
        
        try:
            # APIからデータ取得
            data = await service.get_regional_data(address)
            
            if data:
                print(f"[OK] データ取得成功")
                print(f"  地域コード: {data.get('area_code', 'N/A')}")
                pop_total = data.get('population', {}).get('total', 'N/A')
                if isinstance(pop_total, (int, float)):
                    print(f"  人口: {pop_total:,}人")
                else:
                    print(f"  人口: {pop_total}人")
                print(f"  高齢化率: {data.get('demographics', {}).get('aging_rate', 'N/A')}%")
                household_total = data.get('households', {}).get('total', 'N/A')
                if isinstance(household_total, (int, float)):
                    print(f"  世帯数: {household_total:,}世帯")
                else:
                    print(f"  世帯数: {household_total}世帯")
                
                # 医療需要データ
                medical = data.get('medical_demand', {})
                if medical:
                    daily_patients = medical.get('estimated_daily_patients', 'N/A')
                    if isinstance(daily_patients, (int, float)):
                        print(f"  推定外来患者数: {daily_patients:,}人/日")
                    else:
                        print(f"  推定外来患者数: {daily_patients}人/日")
                    print(f"  受療率: {medical.get('consultation_rate', 'N/A')}/10万人")
                
                # キャッシュ状態
                print(f"  データソース: {data.get('data_source', 'unknown')}")
                
            else:
                print("[ERROR] データ取得失敗")
                
        except Exception as e:
            print(f"[ERROR] エラー: {e}")
    
    # キャッシュ情報の表示
    print("\n" + "="*60)
    print("キャッシュ情報")
    print("="*60)
    print(f"キャッシュエントリ数: {len(service.cache)}")
    for key in list(service.cache.keys())[:5]:
        print(f"  - {key}")

async def test_medical_demand_calculator():
    """医療需要計算のテスト"""
    print("\n" + "="*60)
    print("医療需要計算テスト")
    print("="*60)
    
    calculator = MedicalDemandCalculator()
    
    # テストケース：東京都千代田区
    test_case = {
        "population": 66680,
        "age_distribution": {
            "0-14": 11.5,
            "15-64": 67.8,
            "65+": 20.7
        },
        "area_type": "urban_high_density"
    }
    
    print("\n【東京都千代田区のシミュレーション】")
    print(f"人口: {test_case['population']:,}人")
    print(f"高齢化率: {test_case['age_distribution']['65+']}%")
    print(f"地域タイプ: {test_case['area_type']}")
    print("-"*40)
    
    # 医療需要を計算
    demand = calculator.calculate_area_demand(
        population=test_case["population"],
        age_distribution=test_case["age_distribution"],
        area_type=test_case["area_type"]
    )
    
    print(f"\n推定1日外来患者数: {demand['total_daily_patients']:,}人")
    print(f"受療率（10万人対）: {demand['consultation_rate_per_100k']:.1f}")
    
    print("\n診療科別内訳:")
    for dept, info in demand["department_breakdown"].items():
        print(f"  {dept}: {info['患者数/日']:,}人/日 ({info['割合']}%)")
    
    print("\n主要疾患カテゴリ:")
    for category, data in list(demand["disease_prevalence"].items())[:3]:
        print(f"  {category}: {data['合計患者数']:,}人")
    
    print("\n時間帯別ピーク:")
    peak_hours = sorted(
        demand["hourly_pattern"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    for hour, rate in peak_hours:
        print(f"  {hour}: 相対値 {rate}")

async def test_full_integration():
    """統合テスト：e-Stat API + 医療需要計算"""
    print("\n" + "="*60)
    print("統合テスト：e-Stat API + 医療需要計算")
    print("="*60)
    
    estat_service = EStatIntegratedService()
    calculator = MedicalDemandCalculator()
    
    address = "東京都渋谷区"
    print(f"\n【{address}の完全分析】")
    print("-"*40)
    
    try:
        # e-Stat APIからデータ取得
        regional_data = await estat_service.get_regional_data(address)
        
        if regional_data:
            population = regional_data.get("population", {}).get("total", 100000)
            age_dist = regional_data.get("demographics", {}).get("age_distribution", {
                "0-14": 10, "15-64": 70, "65+": 20
            })
            area_type = regional_data.get("area_type", "urban_high_density")
            
            print(f"[OK] 地域データ取得成功")
            print(f"  人口: {population:,}人")
            print(f"  地域タイプ: {area_type}")
            
            # 医療需要を計算
            demand = calculator.calculate_area_demand(
                population=population,
                age_distribution=age_dist,
                area_type=area_type,
                target_department="内科"  # 特定診療科のみ
            )
            
            print(f"\n内科の推定需要:")
            for dept, info in demand["department_breakdown"].items():
                print(f"  {dept}: {info['患者数/日']:,}人/日")
                print(f"  主要疾患: {', '.join(info['主要疾患'][:3])}")
            
            # クリニックシェア推定
            clinic_share = calculator.calculate_clinic_share(
                area_daily_patients=demand["total_daily_patients"],
                num_competitors=15,  # 仮定
                clinic_features={
                    "土曜診療": True,
                    "夜間診療": False,
                    "最新設備": True,
                    "駐車場": False
                }
            )
            
            print(f"\nクリニックシェア推定:")
            print(f"  市場シェア: {clinic_share['market_share_percentage']}%")
            print(f"  推定患者数: {clinic_share['estimated_daily_patients']:,}人/日")
            print(f"  競争優位性スコア: {clinic_share['competitive_advantage_score']}")
            
        else:
            print("[ERROR] 地域データ取得失敗")
            
    except Exception as e:
        print(f"[ERROR] エラー: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("e-Stat API統合システム 総合テスト")
    print("="*60)
    print(f"APIキー: {os.environ.get('ESTAT_API_KEY', 'Not Set')[:10]}...")
    
    # 各テストを実行
    await test_estat_api()
    await test_medical_demand_calculator()
    await test_full_integration()
    
    print("\n" + "="*60)
    print("テスト完了")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())