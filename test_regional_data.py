#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
地域統計データ取得の詳細テスト
実際に医院の住所から正しい地域データを取得できているか確認
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

# プロジェクトパスを追加
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# サービスをインポート
import importlib.util

# EStatServiceをインポート
spec = importlib.util.spec_from_file_location(
    "estat_service", 
    backend_path / "services" / "estat_service.py"
)
estat_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(estat_module)
EStatService = estat_module.EStatService

# WebResearchServiceをインポート
spec2 = importlib.util.spec_from_file_location(
    "web_research_service", 
    backend_path / "services" / "web_research_service.py"
)
web_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(web_module)
RegionalDataService = web_module.RegionalDataService

async def test_address_to_code_mapping():
    """住所から地域コードへの変換テスト"""
    print("\n" + "="*60)
    print("住所 → 地域コード変換テスト")
    print("="*60)
    
    estat_service = EStatService()
    
    test_addresses = [
        # 東京23区
        "東京都渋谷区道玄坂1-1-1",
        "東京都新宿区西新宿2-8-1",
        "東京都港区六本木6-10-1",
        "東京都千代田区丸の内1-1-1",
        "東京都世田谷区太子堂1-1-1",
        
        # 政令指定都市
        "神奈川県横浜市中区日本大通1",
        "大阪府大阪市北区梅田1-1-1",
        "愛知県名古屋市中区三の丸3-1-1",
        "福岡県福岡市博多区博多駅前1-1-1",
        
        # 一般市町村
        "東京都八王子市元本郷町3-24-1",
        "埼玉県川越市元町1-3-1",
        "千葉県船橋市湊町2-10-25",
        
        # 不完全な住所
        "渋谷区",
        "新宿",
        "東京都"
    ]
    
    print("\n【地域コード判定結果】")
    for address in test_addresses:
        code = estat_service._get_area_code_from_address(address)
        print(f"\n住所: {address}")
        print(f"  → コード: {code}")
        
        # コードから地域名を逆引き
        if code in estat_service.CITY_CODES.values():
            for name, c in estat_service.CITY_CODES.items():
                if c == code:
                    print(f"  → 判定地域: {name}")
                    break
        elif code in estat_service.PREFECTURE_CODES.values():
            for name, c in estat_service.PREFECTURE_CODES.items():
                if c == code:
                    print(f"  → 判定地域: {name}")
                    break
        else:
            print(f"  → 判定地域: デフォルト（東京都）")

async def test_regional_data_acquisition():
    """地域データ取得の詳細テスト"""
    print("\n" + "="*60)
    print("地域統計データ取得テスト")
    print("="*60)
    
    regional_service = RegionalDataService()
    
    # 実際の医院住所を想定したテストケース
    test_clinics = [
        {
            "name": "渋谷内科クリニック",
            "address": "東京都渋谷区道玄坂2-25-12"
        },
        {
            "name": "新宿メディカルセンター",
            "address": "東京都新宿区歌舞伎町1-1-1"
        },
        {
            "name": "横浜みなと診療所",
            "address": "神奈川県横浜市中区山下町123"
        },
        {
            "name": "大阪梅田クリニック",
            "address": "大阪府大阪市北区梅田3-3-3"
        },
        {
            "name": "名古屋栄医院",
            "address": "愛知県名古屋市中区栄3-5-1"
        }
    ]
    
    for clinic in test_clinics:
        print(f"\n【{clinic['name']}】")
        print(f"住所: {clinic['address']}")
        print("-" * 40)
        
        # 地域データを取得
        regional_data = await regional_service.get_regional_data(clinic['address'])
        
        # 人口統計
        if regional_data.get("demographics"):
            demo = regional_data["demographics"]
            print("\n人口統計:")
            print(f"  総人口: {demo.get('total_population', 'N/A')}")
            
            age_dist = demo.get('age_distribution', {})
            if age_dist:
                print("  年齢分布:")
                for age, value in age_dist.items():
                    print(f"    {age}: {value}")
            
            if demo.get('area_code'):
                print(f"  地域コード: {demo.get('area_code')}")
            if demo.get('source'):
                print(f"  データソース: {demo.get('source')}")
        
        # 医療需要
        if regional_data.get("medical_demand"):
            demand = regional_data["medical_demand"]
            print("\n医療需要:")
            print(f"  推定患者数/日: {demand.get('estimated_patients_per_day', 'N/A')}")
            print(f"  医療アクセシビリティ: {demand.get('healthcare_accessibility', 'N/A')}")
            
            if demand.get('disease_prevalence'):
                print("  疾病別需要:")
                for disease, rate in demand['disease_prevalence'].items():
                    if isinstance(rate, (int, float)):
                        print(f"    {disease}: {rate}%")
        
        # 競争密度
        if regional_data.get("competition_density"):
            density = regional_data["competition_density"]
            print("\n競争環境:")
            print(f"  医療機関密度: {density.get('clinics_per_10000', 'N/A')}施設/万人")
            print(f"  病院密度: {density.get('hospitals_per_10000', 'N/A')}施設/万人")

async def test_competitive_analysis_integration():
    """競合分析での地域データ統合テスト"""
    print("\n" + "="*60)
    print("競合分析統合テスト")
    print("="*60)
    
    # CompetitiveAnalysisServiceの模擬テスト
    clinic_info = {
        "name": "テスト内科クリニック",
        "address": "東京都港区南青山5-10-1",
        "department": "内科",
        "features": "最新設備、土曜診療"
    }
    
    print(f"\n自院情報:")
    print(f"  名称: {clinic_info['name']}")
    print(f"  住所: {clinic_info['address']}")
    print(f"  診療科: {clinic_info['department']}")
    
    # 地域データ取得
    regional_service = RegionalDataService()
    regional_data = await regional_service.get_regional_data(clinic_info['address'])
    
    print("\n取得された地域データ:")
    
    # データの妥当性チェック
    if regional_data.get("demographics"):
        demo = regional_data["demographics"]
        
        # 港区の想定値と比較
        print("\n【データ妥当性チェック】")
        
        total_pop = demo.get('total_population')
        if isinstance(total_pop, int):
            if 200000 < total_pop < 300000:
                print(f"  [OK] 総人口 {total_pop:,}人 (港区の妥当な範囲)")
            else:
                print(f"  [?] 総人口 {total_pop:,}人 (港区としては異常値の可能性)")
        else:
            print(f"  [INFO] 総人口: {total_pop}")
        
        # 高齢化率チェック
        age_dist = demo.get('age_distribution', {})
        senior_rate = age_dist.get('65+', 'N/A')
        print(f"  高齢化率: {senior_rate}")
        
        # 地域コードの確認
        area_code = demo.get('area_code')
        if area_code == "13103":
            print(f"  [OK] 地域コード {area_code} (港区)")
        else:
            print(f"  [NG] 地域コード {area_code} (港区は13103であるべき)")

async def main():
    """メインテスト関数"""
    print("\n" + "="*60)
    print("地域統計データ取得 - 詳細検証")
    print("="*60)
    
    # 環境変数チェック
    print("\n【環境変数】")
    estat_key = os.getenv("ESTAT_API_KEY")
    if estat_key:
        print(f"  [OK] ESTAT_API_KEY: 設定済み")
    else:
        print(f"  [INFO] ESTAT_API_KEY: 未設定（推定値を使用）")
    
    try:
        # 1. 住所→コード変換テスト
        await test_address_to_code_mapping()
        
        # 2. 地域データ取得テスト
        await test_regional_data_acquisition()
        
        # 3. 競合分析統合テスト
        await test_competitive_analysis_integration()
        
        print("\n" + "="*60)
        print("テスト完了")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())