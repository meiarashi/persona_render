#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e-Stat API テストスクリプト
実際の政府統計データ取得をテスト
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

# EStatServiceをインポート
import importlib.util
spec = importlib.util.spec_from_file_location(
    "estat_service", 
    backend_path / "services" / "estat_service.py"
)
estat_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(estat_module)

EStatService = estat_module.EStatService

async def test_stats_list():
    """統計表リストの取得テスト"""
    print("\n" + "="*60)
    print("統計表リスト取得テスト")
    print("="*60)
    
    service = EStatService()
    
    # 人口推計の統計表リストを取得
    stats_code = service.STATS_CODES["人口推計"]
    print(f"\n統計コード: {stats_code} (人口推計)")
    
    stats_list = await service.get_stats_list(stats_code)
    
    if stats_list:
        print(f"[OK] {len(stats_list)}件の統計表を取得")
        
        # 最新の3件を表示
        for i, table in enumerate(stats_list[:3], 1):
            table_id = table.get("@id", "N/A")
            title = table.get("TITLE", {})
            if isinstance(title, dict):
                title_text = title.get("$", "タイトルなし")
            else:
                title_text = str(title)
            
            print(f"\n  {i}. ID: {table_id}")
            print(f"     タイトル: {title_text[:50]}...")
            
            # 統計名
            stats_name = table.get("STATISTICS_NAME", {})
            if isinstance(stats_name, dict):
                stats_name_text = stats_name.get("$", "")
            else:
                stats_name_text = str(stats_name)
            print(f"     統計名: {stats_name_text}")
    else:
        print("[NG] 統計表リストを取得できませんでした")
    
    return stats_list

async def test_meta_info(stats_data_id: str):
    """メタ情報取得テスト"""
    print("\n" + "="*60)
    print("メタ情報取得テスト")
    print("="*60)
    
    service = EStatService()
    
    print(f"\n統計表ID: {stats_data_id}")
    
    meta_info = await service.get_meta_info(stats_data_id)
    
    if meta_info:
        print("[OK] メタ情報を取得")
        
        # CLASS情報を表示
        class_info = meta_info.get("CLASS_INF", {})
        if class_info:
            print("\n【分類情報】")
            class_obj = class_info.get("CLASS_OBJ", [])
            if not isinstance(class_obj, list):
                class_obj = [class_obj]
            
            for cls in class_obj[:3]:  # 最初の3つを表示
                cls_id = cls.get("@id", "")
                cls_name = cls.get("@name", "")
                print(f"  - {cls_id}: {cls_name}")
    else:
        print("[NG] メタ情報を取得できませんでした")
    
    return meta_info

async def test_stats_data(stats_data_id: str):
    """統計データ取得テスト"""
    print("\n" + "="*60)
    print("統計データ取得テスト")
    print("="*60)
    
    service = EStatService()
    
    # 東京都のデータを取得
    area_code = "13000"
    print(f"\n統計表ID: {stats_data_id}")
    print(f"地域コード: {area_code} (東京都)")
    
    data = await service.get_stats_data(stats_data_id, area_code)
    
    if data and data.get("values"):
        values = data["values"]
        print(f"[OK] {len(values)}件のデータポイントを取得")
        
        # 最初の5件を表示
        print("\n【データサンプル】")
        for i, value in enumerate(values[:5], 1):
            val = value.get("value", "N/A")
            time = value.get("time", "N/A")
            area = value.get("area", "N/A")
            unit = value.get("unit", "")
            
            print(f"  {i}. 値: {val}{unit}")
            print(f"     時間: {time}, 地域: {area}")
    else:
        print("[NG] 統計データを取得できませんでした")
    
    return data

async def test_population_data():
    """人口データ取得テスト"""
    print("\n" + "="*60)
    print("人口データ取得テスト")
    print("="*60)
    
    service = EStatService()
    
    test_addresses = [
        "東京都渋谷区",
        "東京都新宿区",
        "大阪府大阪市",
        "愛知県名古屋市"
    ]
    
    for address in test_addresses:
        print(f"\n地域: {address}")
        print("-"*40)
        
        population_data = await service.get_population_data(address)
        
        if population_data:
            total_pop = population_data.get("total_population", "N/A")
            age_dist = population_data.get("age_distribution", {})
            source = population_data.get("source", "N/A")
            
            print(f"  総人口: {total_pop}")
            print(f"  年齢分布:")
            for age_group, percentage in age_dist.items():
                print(f"    - {age_group}: {percentage}")
            print(f"  データソース: {source}")
        else:
            print("  [NG] データ取得失敗")

async def test_medical_facility_data():
    """医療施設データ取得テスト"""
    print("\n" + "="*60)
    print("医療施設データ取得テスト")
    print("="*60)
    
    service = EStatService()
    
    test_addresses = [
        "東京都渋谷区",
        "東京都新宿区"
    ]
    
    for address in test_addresses:
        print(f"\n地域: {address}")
        print("-"*40)
        
        medical_data = await service.get_medical_facility_data(address)
        
        if medical_data:
            total = medical_data.get("total_medical_facilities", "N/A")
            per_10000 = medical_data.get("facilities_per_10000", "N/A")
            source = medical_data.get("source", "N/A")
            
            print(f"  医療施設総数: {total}")
            print(f"  人口1万人あたり: {per_10000}")
            print(f"  データソース: {source}")
        else:
            print("  [NG] データ取得失敗")

async def main():
    """メインテスト関数"""
    print("\n" + "="*60)
    print("e-Stat API 実装テスト")
    print("="*60)
    
    # 環境変数チェック
    print("\n【環境変数チェック】")
    api_key = os.getenv("ESTAT_API_KEY")
    if api_key:
        print(f"  [OK] ESTAT_API_KEY: 設定済み ({len(api_key)}文字)")
    else:
        print("  [NG] ESTAT_API_KEY: 未設定")
        print("\n  ※ e-Stat APIキーを設定してください")
        print("  ※ https://www.e-stat.go.jp/ でユーザー登録後、")
        print("  ※ API利用申請を行ってキーを取得してください")
    
    try:
        # 各テストを実行
        
        # 1. 統計表リスト取得
        stats_list = await test_stats_list()
        
        # 2. メタ情報取得（統計表が取得できた場合）
        if stats_list and len(stats_list) > 0:
            first_table_id = stats_list[0].get("@id", "")
            if first_table_id:
                await test_meta_info(first_table_id)
                await test_stats_data(first_table_id)
        
        # 3. 人口データ取得
        await test_population_data()
        
        # 4. 医療施設データ取得
        await test_medical_facility_data()
        
        print("\n" + "="*60)
        print("テスト完了")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())