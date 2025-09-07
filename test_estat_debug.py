#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e-Stat APIデバッグテスト - 地域別データの正確な取得
"""

import asyncio
import aiohttp
import json
import sys
import os

# Windows環境での文字化け対策
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

API_KEY = "992fa8d6f43d645c3c767a97410fe89612cfecc7"

async def search_area_census_data(area_name: str):
    """特定地域の国勢調査データを検索"""
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    print(f"\n【{area_name}の国勢調査データ検索】")
    print("-"*50)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: 統計表を検索
        url = f"{base_url}/getStatsList"
        params = {
            "appId": API_KEY,
            "statsCode": "00200521",  # 国勢調査
            "searchWord": f"{area_name} 人口",
            "limit": 3
        }
        
        print(f"検索ワード: {area_name} 人口")
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    stats_list = data.get("GET_STATS_LIST", {})
                    
                    if stats_list.get("RESULT", {}).get("STATUS") == 0:
                        tables = stats_list.get("DATALIST_INF", {}).get("TABLE_INF", [])
                        if not isinstance(tables, list):
                            tables = [tables] if tables else []
                        
                        if not tables:
                            print("該当する統計表が見つかりませんでした")
                            return None
                        
                        # 最新のテーブルを選択
                        best_table = None
                        for table in tables:
                            title = table.get("TITLE", {})
                            if isinstance(title, dict):
                                title_text = title.get("$", "")
                            else:
                                title_text = str(title)
                            
                            # 市区町村データを優先
                            if "市区町村" in title_text or area_name in title_text:
                                best_table = table
                                break
                        
                        if not best_table:
                            best_table = tables[0]
                        
                        table_id = best_table.get("@id", "")
                        title = best_table.get("TITLE", {})
                        if isinstance(title, dict):
                            title_text = title.get("$", "")
                        else:
                            title_text = str(title)
                        
                        print(f"選択された統計表: {title_text[:60]}")
                        print(f"テーブルID: {table_id}")
                        
                        # Step 2: メタ情報を取得して地域コードを確認
                        meta_url = f"{base_url}/getMetaInfo"
                        meta_params = {
                            "appId": API_KEY,
                            "statsDataId": table_id
                        }
                        
                        async with session.get(meta_url, params=meta_params) as meta_response:
                            if meta_response.status == 200:
                                meta_data = await meta_response.json()
                                meta_info = meta_data.get("GET_META_INFO", {})
                                
                                # 地域分類を探す
                                class_objs = meta_info.get("METADATA_INF", {}).get("CLASS_INF", {}).get("CLASS_OBJ", [])
                                if not isinstance(class_objs, list):
                                    class_objs = [class_objs] if class_objs else []
                                
                                area_class = None
                                for cls in class_objs:
                                    if "地域" in cls.get("@name", "") or "area" in cls.get("@id", "").lower():
                                        area_class = cls
                                        break
                                
                                if area_class:
                                    print(f"\n地域分類ID: {area_class.get('@id', '')}")
                                    
                                    # 地域コードリストから該当地域を探す
                                    codes = area_class.get("CLASS", [])
                                    if not isinstance(codes, list):
                                        codes = [codes] if codes else []
                                    
                                    target_code = None
                                    for code in codes:
                                        code_name = code.get("@name", "")
                                        if area_name in code_name:
                                            target_code = code.get("@code", "")
                                            print(f"地域コード発見: {code_name} -> {target_code}")
                                            break
                                    
                                    # Step 3: 実データを取得
                                    data_url = f"{base_url}/getStatsData"
                                    data_params = {
                                        "appId": API_KEY,
                                        "statsDataId": table_id,
                                        "limit": 10
                                    }
                                    
                                    if target_code and area_class.get("@id"):
                                        # 地域コードでフィルタ
                                        data_params[f"cd{area_class.get('@id')}"] = target_code
                                        print(f"フィルタ適用: cd{area_class.get('@id')}={target_code}")
                                    
                                    async with session.get(data_url, params=data_params) as data_response:
                                        if data_response.status == 200:
                                            result_data = await data_response.json()
                                            stats_data = result_data.get("GET_STATS_DATA", {})
                                            
                                            if stats_data.get("RESULT", {}).get("STATUS") == 0:
                                                values = stats_data.get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
                                                if not isinstance(values, list):
                                                    values = [values] if values else []
                                                
                                                if values:
                                                    # 総人口を探す
                                                    for val in values:
                                                        cat_obj = val.get("@cat01", "")
                                                        if "総数" in str(cat_obj) or "総人口" in str(cat_obj) or not cat_obj:
                                                            population = val.get("$", "0")
                                                            unit = val.get("@unit", "")
                                                            print(f"\n人口データ: {population} {unit}")
                                                            
                                                            try:
                                                                pop_value = int(str(population).replace(",", "").replace("人", ""))
                                                                return pop_value
                                                            except:
                                                                pass
                                                
                                                # 最初の値を返す
                                                if values:
                                                    first_val = values[0].get("$", "0")
                                                    try:
                                                        return int(str(first_val).replace(",", "").replace("人", ""))
                                                    except:
                                                        return 100000
                    else:
                        print(f"エラー: {stats_list.get('RESULT', {}).get('ERROR_MSG', '')}")
                        
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()
    
    return None

async def main():
    """メイン処理"""
    print("="*60)
    print("e-Stat API 地域別データ取得デバッグ")
    print("="*60)
    
    test_areas = [
        "東京都千代田区",
        "大阪府大阪市",
        "北海道札幌市",
        "沖縄県那覇市"
    ]
    
    for area in test_areas:
        population = await search_area_census_data(area)
        if population:
            print(f"\n結果: {area}の人口 = {population:,}人")
        else:
            print(f"\n結果: {area}のデータ取得失敗")
        
        await asyncio.sleep(0.5)
    
    print("\n" + "="*60)
    print("デバッグ完了")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())