#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e-Stat統合サービスV3のテスト
正確な地域別データ取得の確認
"""

import asyncio
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# APIキーを設定
os.environ["ESTAT_API_KEY"] = "992fa8d6f43d645c3c767a97410fe89612cfecc7"

from backend.services.estat_integrated_service_v3 import EStatIntegratedServiceV3

async def test_v3_service():
    """V3サービスのテスト"""
    print("="*60)
    print("e-Stat統合サービスV3テスト")
    print("="*60)
    
    service = EStatIntegratedServiceV3()
    
    # テスト用の住所リスト
    test_addresses = [
        "東京都千代田区",
        "東京都世田谷区",
        "大阪府大阪市北区",
        "北海道札幌市中央区",
        "沖縄県那覇市",
        "島根県松江市"
    ]
    
    for address in test_addresses:
        print(f"\n【{address}のデータ取得】")
        print("-"*40)
        
        try:
            # データ取得
            data = await service.get_regional_data(address)
            
            print(f"[基本情報]")
            print(f"  地域コード: {data.get('area_code', 'N/A')}")
            print(f"  地域名: {data.get('area_name', 'N/A')}")
            print(f"  地域タイプ: {data.get('area_type', 'N/A')}")
            
            # 人口データ
            pop = data.get('population', {})
            print(f"\n[人口データ]")
            print(f"  総人口: {pop.get('total', 'N/A'):,}人")
            
            # 年齢分布
            age_dist = data.get('demographics', {}).get('age_distribution', {})
            if age_dist:
                print(f"  年齢分布:")
                print(f"    0-14歳: {age_dist.get('0-14', 'N/A')}%")
                print(f"    15-64歳: {age_dist.get('15-64', 'N/A')}%")
                print(f"    65歳以上: {age_dist.get('65+', 'N/A')}%")
            
            print(f"  高齢化率: {data.get('demographics', {}).get('aging_rate', 'N/A')}%")
            print(f"  世帯数: {data.get('households', {}).get('total', 'N/A'):,}世帯")
            
            # 医療施設
            medical_fac = data.get('medical_facilities', {})
            if medical_fac:
                print(f"\n[医療施設]")
                print(f"  施設数: {medical_fac.get('facilities_count', 'N/A')}施設")
            
            # 医療需要
            medical = data.get('medical_demand', {})
            if medical:
                print(f"\n[医療需要]")
                print(f"  推定外来患者数: {medical.get('estimated_daily_patients', 'N/A'):,}人/日")
                print(f"  受療率: {medical.get('consultation_rate', 'N/A'):.1f}/10万人")
                
                # 診療科別内訳（上位3つ）
                dept_breakdown = medical.get('department_breakdown', {})
                if dept_breakdown:
                    print(f"\n  診療科別（上位3科）:")
                    sorted_depts = sorted(dept_breakdown.items(), 
                                        key=lambda x: x[1].get('患者数/日', 0), 
                                        reverse=True)[:3]
                    for dept, info in sorted_depts:
                        print(f"    {dept}: {info['患者数/日']:,}人/日")
            
            print(f"\nデータソース: {data.get('data_source', 'unknown')}")
                
        except Exception as e:
            print(f"[ERROR] エラー: {e}")
            import traceback
            traceback.print_exc()

async def test_address_parsing():
    """住所解析のテスト"""
    print("\n" + "="*60)
    print("住所解析テスト")
    print("="*60)
    
    service = EStatIntegratedServiceV3()
    
    test_cases = [
        "東京都千代田区丸の内",
        "大阪府大阪市北区梅田1-1-1",
        "京都府京都市中京区",
        "沖縄県那覇市おもろまち",
        "北海道札幌市中央区大通西",
        "福岡県福岡市博多区博多駅前"
    ]
    
    for address in test_cases:
        pref, city, code = service._parse_address_to_names(address)
        print(f"{address:35} -> {pref:8} {city:15} ({code})")

async def comparison_test():
    """同一都道府県内の市区町村比較テスト"""
    print("\n" + "="*60)
    print("東京都内の区別比較")
    print("="*60)
    
    service = EStatIntegratedServiceV3()
    
    tokyo_wards = [
        "東京都千代田区",
        "東京都港区",
        "東京都新宿区",
        "東京都渋谷区",
        "東京都世田谷区"
    ]
    
    print("\n区名              人口        高齢化率  地域タイプ        データソース")
    print("-" * 70)
    
    for ward in tokyo_wards:
        data = await service.get_regional_data(ward)
        
        ward_name = ward.replace("東京都", "")
        population = data.get('population', {}).get('total', 0)
        aging_rate = data.get('demographics', {}).get('aging_rate', 0)
        area_type = data.get('area_type', 'N/A')
        source = data.get('data_source', 'N/A')
        
        print(f"{ward_name:15} {population:10,} {aging_rate:7.1f}%  {area_type:18} {source}")

async def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("e-Stat API統合システム V3 総合テスト")
    print("="*60)
    print(f"APIキー: {os.environ.get('ESTAT_API_KEY', 'Not Set')[:10]}...")
    
    # 各テストを実行
    await test_address_parsing()
    await test_v3_service()
    await comparison_test()
    
    print("\n" + "="*60)
    print("テスト完了")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())