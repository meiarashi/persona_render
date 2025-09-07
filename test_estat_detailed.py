#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e-Stat API詳細分析 - 正確なデータ構造の理解
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

async def analyze_census_structure():
    """国勢調査データの構造を詳細分析"""
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    print("="*60)
    print("国勢調査データ構造の詳細分析")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        # まず最新の国勢調査統計表を取得
        url = f"{base_url}/getStatsList"
        params = {
            "appId": API_KEY,
            "statsCode": "00200521",
            "searchWord": "令和2年 市区町村",
            "limit": 1
        }
        
        print("\n1. 最新の市区町村別国勢調査データを検索...")
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    stats_list = data.get("GET_STATS_LIST", {})
                    
                    tables = stats_list.get("DATALIST_INF", {}).get("TABLE_INF", [])
                    if not isinstance(tables, list):
                        tables = [tables] if tables else []
                    
                    if not tables:
                        # 別の検索ワードで試す
                        params["searchWord"] = "人口 市区町村"
                        async with session.get(url, params=params) as response2:
                            if response2.status == 200:
                                data = await response2.json()
                                stats_list = data.get("GET_STATS_LIST", {})
                                tables = stats_list.get("DATALIST_INF", {}).get("TABLE_INF", [])
                                if not isinstance(tables, list):
                                    tables = [tables] if tables else []
                    
                    if tables:
                        table = tables[0]
                        table_id = table.get("@id", "")
                        title = table.get("TITLE", {})
                        if isinstance(title, dict):
                            title_text = title.get("$", "")
                        else:
                            title_text = str(title)
                        
                        print(f"発見: {title_text[:80]}")
                        print(f"テーブルID: {table_id}")
                        
                        # メタ情報を取得
                        print("\n2. メタ情報を取得...")
                        meta_url = f"{base_url}/getMetaInfo"
                        meta_params = {
                            "appId": API_KEY,
                            "statsDataId": table_id
                        }
                        
                        async with session.get(meta_url, params=meta_params) as meta_response:
                            if meta_response.status == 200:
                                meta_data = await meta_response.json()
                                meta_info = meta_data.get("GET_META_INFO", {})
                                
                                # CLASS情報を分析
                                class_objs = meta_info.get("METADATA_INF", {}).get("CLASS_INF", {}).get("CLASS_OBJ", [])
                                if not isinstance(class_objs, list):
                                    class_objs = [class_objs] if class_objs else []
                                
                                print("\n利用可能な分類:")
                                area_class_id = None
                                cat_class_id = None
                                
                                for cls in class_objs:
                                    cls_id = cls.get("@id", "")
                                    cls_name = cls.get("@name", "")
                                    print(f"  - {cls_id}: {cls_name}")
                                    
                                    if "地域" in cls_name or "area" in cls_id.lower():
                                        area_class_id = cls_id
                                    elif "cat" in cls_id.lower():
                                        cat_class_id = cls_id
                                
                                # 東京都千代田区のデータを取得
                                print("\n3. 東京都千代田区のデータを取得...")
                                
                                # まず地域コードを探す
                                if area_class_id:
                                    for cls in class_objs:
                                        if cls.get("@id") == area_class_id:
                                            codes = cls.get("CLASS", [])
                                            if not isinstance(codes, list):
                                                codes = [codes] if codes else []
                                            
                                            for code in codes[:5]:  # 最初の5件を表示
                                                code_val = code.get("@code", "")
                                                code_name = code.get("@name", "")
                                                if "千代田" in code_name:
                                                    print(f"千代田区コード発見: {code_val} = {code_name}")
                                                    
                                                    # このコードでデータを取得
                                                    data_url = f"{base_url}/getStatsData"
                                                    data_params = {
                                                        "appId": API_KEY,
                                                        "statsDataId": table_id,
                                                        f"cd{area_class_id}": code_val,
                                                        "limit": 20
                                                    }
                                                    
                                                    async with session.get(data_url, params=data_params) as data_response:
                                                        if data_response.status == 200:
                                                            result_data = await data_response.json()
                                                            stats_data = result_data.get("GET_STATS_DATA", {})
                                                            
                                                            values = stats_data.get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
                                                            if not isinstance(values, list):
                                                                values = [values] if values else []
                                                            
                                                            print(f"\n取得データ数: {len(values)}件")
                                                            
                                                            # データの内容を分析
                                                            for i, val in enumerate(values[:10]):
                                                                value = val.get("$", "")
                                                                unit = val.get("@unit", "")
                                                                cat01 = val.get("@cat01", "")
                                                                cat02 = val.get("@cat02", "")
                                                                cat03 = val.get("@cat03", "")
                                                                
                                                                # カテゴリ名を取得
                                                                cat_names = []
                                                                for cls in class_objs:
                                                                    if "cat" in cls.get("@id", "").lower():
                                                                        cat_codes = cls.get("CLASS", [])
                                                                        if not isinstance(cat_codes, list):
                                                                            cat_codes = [cat_codes] if cat_codes else []
                                                                        for cat_code in cat_codes:
                                                                            if cat_code.get("@code") in [cat01, cat02, cat03]:
                                                                                cat_names.append(cat_code.get("@name", ""))
                                                                
                                                                print(f"  [{i+1}] {value} {unit}")
                                                                if cat_names:
                                                                    print(f"      カテゴリ: {', '.join(cat_names)}")
                                                    break
                        
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()

async def get_latest_census_data():
    """最新の国勢調査データを取得する簡潔な方法"""
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    print("\n" + "="*60)
    print("簡潔な方法での地域別人口取得")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        # 令和2年国勢調査の人口総数データを直接取得
        # 統計表ID: 0003448237 (これは事前調査で判明した最新の市区町村別人口データ)
        stats_data_id = "0003448237"
        
        print(f"\n統計表ID {stats_data_id} からデータ取得...")
        
        # 東京都千代田区のコード: 13101
        data_url = f"{base_url}/getStatsData"
        data_params = {
            "appId": API_KEY,
            "statsDataId": stats_data_id,
            "cdArea": "13101",  # 東京都千代田区
            "limit": 1
        }
        
        try:
            async with session.get(data_url, params=data_params) as response:
                if response.status == 200:
                    data = await response.json()
                    stats_data = data.get("GET_STATS_DATA", {})
                    
                    if stats_data.get("RESULT", {}).get("STATUS") == 0:
                        values = stats_data.get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
                        if not isinstance(values, list):
                            values = [values] if values else []
                        
                        if values:
                            population = values[0].get("$", "0")
                            print(f"\n東京都千代田区の人口: {population}")
                    else:
                        error = stats_data.get("RESULT", {}).get("ERROR_MSG", "")
                        print(f"エラー: {error}")
                        
                        # エラーの場合、パラメータを調整して再試行
                        print("\nパラメータを調整して再試行...")
                        data_params = {
                            "appId": API_KEY,
                            "statsDataId": "0003448237",
                            "limit": 10
                        }
                        
                        async with session.get(data_url, params=data_params) as response2:
                            if response2.status == 200:
                                data = await response2.json()
                                print("レスポンス構造:")
                                print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
                                
        except Exception as e:
            print(f"エラー: {e}")

async def main():
    """メイン処理"""
    await analyze_census_structure()
    await get_latest_census_data()
    
    print("\n" + "="*60)
    print("分析完了")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())