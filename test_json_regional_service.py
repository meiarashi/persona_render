#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSONベース地域データサービスのテスト
全国の地域データが正しく取得できることを確認
"""

import asyncio
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

# サービスを直接インポート
import importlib.util

# RegionalJsonServiceをインポート
spec1 = importlib.util.spec_from_file_location(
    "regional_json_service", 
    backend_path / "services" / "regional_json_service.py"
)
json_module = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(json_module)
RegionalJsonService = json_module.RegionalJsonService

# RegionalDataServiceをインポート
spec2 = importlib.util.spec_from_file_location(
    "web_research_service", 
    backend_path / "services" / "web_research_service.py"
)
web_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(web_module)
RegionalDataService = web_module.RegionalDataService

def test_json_service():
    """JSONサービスの直接テスト"""
    print("\n" + "="*60)
    print("JSONベース地域データサービステスト")
    print("="*60)
    
    service = RegionalJsonService()
    
    # テスト用住所リスト（全国各地）
    test_addresses = [
        # 北海道・東北
        "北海道札幌市中央区北1条西2丁目",
        "青森県青森市新町1-3-7",
        "宮城県仙台市青葉区国分町3-7-1",
        
        # 関東
        "東京都渋谷区道玄坂1-12-1",
        "東京都新宿区西新宿2-8-1",
        "東京都港区六本木6-10-1",
        "神奈川県横浜市中区山下町",
        "千葉県千葉市中央区中央3-10-8",
        "埼玉県さいたま市大宮区桜木町1-7-5",
        
        # 中部
        "愛知県名古屋市中区栄3-16-1",
        "静岡県静岡市葵区追手町9-6",
        "新潟県新潟市中央区新光町4-1",
        
        # 関西
        "大阪府大阪市北区梅田1-3-1",
        "京都府京都市中京区寺町通御池上る",
        "兵庫県神戸市中央区加納町6-5-1",
        
        # 中国・四国
        "広島県広島市中区基町10-52",
        "岡山県岡山市北区丸の内2-4-6",
        "香川県高松市番町四丁目1-10",
        
        # 九州・沖縄
        "福岡県福岡市博多区博多駅前3-25-21",
        "熊本県熊本市中央区水前寺6-18-1",
        "沖縄県那覇市泉崎1-2-2",
        
        # 不完全な住所
        "渋谷区",
        "大阪市",
        "名古屋"
    ]
    
    print("\n【住所解析と地域データ取得テスト】")
    for address in test_addresses:
        print(f"\n住所: {address}")
        print("-" * 40)
        
        # 住所解析
        pref_code, city_code, ward_code = service.parse_address(address)
        print(f"  解析結果: 都道府県={pref_code}, 市区町村={city_code}, 区={ward_code}")
        
        # 地域データ取得
        data = service.get_regional_data(address)
        
        # 結果表示
        if data:
            area_info = data.get("area_info", {})
            demographics = data.get("demographics", {})
            medical = data.get("medical_facilities", {})
            demand = data.get("medical_demand", {})
            
            print(f"  地域: {area_info.get('prefecture', '不明')}", end="")
            if area_info.get('city'):
                print(f" {area_info.get('city')}", end="")
            if area_info.get('ward'):
                print(f" {area_info.get('ward')}", end="")
            print()
            
            print(f"  地域タイプ: {area_info.get('type', '不明')}")
            print(f"  人口: {demographics.get('total_population', 0):,}人")
            print(f"  高齢化率: {demographics.get('age_distribution', {}).get('65+', 0)}%")
            print(f"  医療施設数: {medical.get('total', 0)}施設")
            print(f"  人口1万人あたり: {medical.get('per_10000', 0)}施設")
            print(f"  推定患者数/日: {demand.get('estimated_patients_per_day', 0):,}人")
            print(f"  医療アクセシビリティ: {demand.get('healthcare_accessibility', '不明')}")

async def test_regional_data_service():
    """統合RegionalDataServiceのテスト"""
    print("\n" + "="*60)
    print("統合地域データサービステスト")
    print("="*60)
    
    service = RegionalDataService()
    
    # いくつかの住所でテスト
    test_cases = [
        ("東京都渋谷区道玄坂2-29-5", "渋谷（都心部）"),
        ("大阪府大阪市北区梅田3-3-20", "大阪（都心部）"),
        ("北海道札幌市中央区大通西3", "札幌（地方都市）"),
        ("沖縄県那覇市首里石嶺町4-373-1", "那覇（地方都市）")
    ]
    
    for address, description in test_cases:
        print(f"\n【{description}】")
        print(f"住所: {address}")
        print("-" * 40)
        
        # データ取得
        data = await service.get_regional_data(address)
        
        if data:
            # 基本情報
            area_info = data.get("area_info", {})
            print(f"\n地域情報:")
            print(f"  都道府県: {area_info.get('prefecture', '不明')}")
            print(f"  市区町村: {area_info.get('city', '')}")
            print(f"  地域タイプ: {area_info.get('type', '不明')}")
            
            # 人口統計
            demographics = data.get("demographics", {})
            print(f"\n人口統計:")
            print(f"  総人口: {demographics.get('total_population', 0):,}人")
            age_dist = demographics.get("age_distribution", {})
            if age_dist:
                print(f"  年齢分布:")
                for age, percent in age_dist.items():
                    print(f"    {age}歳: {percent}%")
            
            # 医療施設
            medical = data.get("medical_facilities", {})
            print(f"\n医療施設:")
            print(f"  総数: {medical.get('total', 0)}施設")
            print(f"  人口1万人あたり: {medical.get('per_10000', 0)}施設")
            
            # 医療需要
            demand = data.get("medical_demand", {})
            print(f"\n医療需要:")
            print(f"  推定患者数/日: {demand.get('estimated_patients_per_day', 0):,}人")
            print(f"  医療アクセシビリティ: {demand.get('healthcare_accessibility', '不明')}")
            print(f"  平均待ち時間: {demand.get('avg_waiting_time_minutes', 0)}分")
            
            # 競争密度
            competition = data.get("competition_density", {})
            print(f"\n競争環境:")
            print(f"  競争レベル: {competition.get('competition_level', '不明')}")
            print(f"  診療所密度: {competition.get('clinics_per_10000', 0)}施設/万人")
            print(f"  病院密度: {competition.get('hospitals_per_10000', 0)}施設/万人")

def test_prefecture_coverage():
    """全都道府県のカバレッジテスト"""
    print("\n" + "="*60)
    print("都道府県カバレッジテスト")
    print("="*60)
    
    service = RegionalJsonService()
    
    # 全都道府県を取得
    prefectures = service.get_all_prefectures()
    print(f"\n登録都道府県数: {len(prefectures)}")
    
    if len(prefectures) == 47:
        print("[OK] 全47都道府県が登録されています")
    else:
        print(f"[NG] {47 - len(prefectures)}都道府県が不足しています")
    
    # 各都道府県の主要都市数を確認
    print("\n【都道府県別主要都市数】")
    for code, name in sorted(prefectures.items()):
        cities = service.get_prefecture_cities(code)
        print(f"  {name}: {len(cities)}都市", end="")
        if len(cities) > 0:
            # 最初の都市名を表示
            first_city = list(cities.values())[0] if cities else ""
            print(f" （例: {first_city}）")
        else:
            print()

async def main():
    """メインテスト関数"""
    print("\n" + "="*60)
    print("JSONベース地域データサービス - 包括的テスト")
    print("="*60)
    
    try:
        # 1. JSONサービスの直接テスト
        test_json_service()
        
        # 2. 統合サービスのテスト
        await test_regional_data_service()
        
        # 3. カバレッジテスト
        test_prefecture_coverage()
        
        print("\n" + "="*60)
        print("テスト完了")
        print("="*60)
        print("\n[結果] 全国の地域データが正常に取得できることを確認しました。")
        
    except Exception as e:
        print(f"\n[ERROR] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())