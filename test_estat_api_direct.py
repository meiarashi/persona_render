#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e-Stat APIを直接呼び出してレスポンスを確認
"""

import asyncio
import aiohttp
import os
import json
import sys

# Windows環境での文字化け対策
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

async def test_direct_api_call():
    """e-Stat APIの直接呼び出しテスト"""
    api_key = "992fa8d6f43d645c3c767a97410fe89612cfecc7"
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    print("="*60)
    print("e-Stat API直接呼び出しテスト")
    print("="*60)
    
    # 1. まず利用可能な統計表を検索
    print("\n【STEP 1: 統計表検索】")
    print("-"*40)
    
    async with aiohttp.ClientSession() as session:
        # 人口統計を検索
        url = f"{base_url}/getStatsList"
        params = {
            "appId": api_key,
            "searchWord": "人口",
            "limit": 5
        }
        
        print(f"リクエストURL: {url}")
        print(f"パラメータ: {json.dumps(params, ensure_ascii=False, indent=2)}")
        
        try:
            async with session.get(url, params=params) as response:
                print(f"ステータスコード: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # レスポンス構造を確認
                    print("\nレスポンス構造:")
                    print(json.dumps(data, ensure_ascii=False, indent=2)[:1000])
                    
                    # 統計表リストを解析
                    if "GET_STATS_LIST" in data:
                        stats_list = data["GET_STATS_LIST"]
                        
                        if "STATUS" in stats_list:
                            status = stats_list["STATUS"]
                            print(f"\nAPIステータス: {status}")
                            
                            if status != "0":
                                error_msg = stats_list.get("ERROR_MSG", "不明なエラー")
                                print(f"エラーメッセージ: {error_msg}")
                                return
                        
                        if "DATALIST_INF" in stats_list:
                            datalist = stats_list["DATALIST_INF"]
                            
                            # 総件数
                            result_count = datalist.get("RESULT_INF", {}).get("TOTAL_NUMBER", 0)
                            print(f"\n検索結果: {result_count}件")
                            
                            # テーブル情報
                            tables = datalist.get("TABLE_INF", [])
                            if not isinstance(tables, list):
                                tables = [tables] if tables else []
                            
                            print(f"取得テーブル数: {len(tables)}件")
                            
                            # 最初のテーブルの詳細を表示
                            if tables:
                                first_table = tables[0]
                                table_id = first_table.get("@id", "")
                                title = first_table.get("TITLE", {})
                                if isinstance(title, dict):
                                    title_text = title.get("$", "")
                                else:
                                    title_text = str(title)
                                
                                print(f"\n最初のテーブル:")
                                print(f"  ID: {table_id}")
                                print(f"  タイトル: {title_text}")
                                
                                # このテーブルIDでデータを取得してみる
                                await test_get_stats_data(api_key, table_id)
                else:
                    print(f"エラー: HTTPステータス {response.status}")
                    text = await response.text()
                    print(f"レスポンス: {text[:500]}")
                    
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()

async def test_get_stats_data(api_key: str, stats_data_id: str):
    """統計データの取得テスト"""
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    print("\n【STEP 2: 統計データ取得】")
    print("-"*40)
    
    async with aiohttp.ClientSession() as session:
        # メタ情報を先に取得
        url = f"{base_url}/getMetaInfo"
        params = {
            "appId": api_key,
            "statsDataId": stats_data_id
        }
        
        print(f"メタ情報取得URL: {url}")
        print(f"パラメータ: {json.dumps(params, ensure_ascii=False, indent=2)}")
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # メタ情報を解析
                    meta_info = data.get("GET_META_INFO", {})
                    if "STATUS" in meta_info and meta_info["STATUS"] != "0":
                        print(f"メタ情報取得エラー: {meta_info.get('ERROR_MSG', '')}")
                        return
                    
                    # CLASS情報を表示
                    class_info = meta_info.get("METADATA_INF", {}).get("CLASS_INF", {})
                    class_objs = class_info.get("CLASS_OBJ", [])
                    if not isinstance(class_objs, list):
                        class_objs = [class_objs] if class_objs else []
                    
                    print("\n利用可能な分類:")
                    for cls in class_objs[:3]:
                        cls_id = cls.get("@id", "")
                        cls_name = cls.get("@name", "")
                        print(f"  {cls_id}: {cls_name}")
                    
                    # 実データを取得
                    print("\n実データ取得:")
                    url = f"{base_url}/getStatsData"
                    params = {
                        "appId": api_key,
                        "statsDataId": stats_data_id,
                        "limit": 10
                    }
                    
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            stats_data = data.get("GET_STATS_DATA", {})
                            if "STATUS" in stats_data and stats_data["STATUS"] != "0":
                                print(f"データ取得エラー: {stats_data.get('ERROR_MSG', '')}")
                                return
                            
                            # データ値を表示
                            data_inf = stats_data.get("STATISTICAL_DATA", {}).get("DATA_INF", {})
                            values = data_inf.get("VALUE", [])
                            if not isinstance(values, list):
                                values = [values] if values else []
                            
                            print(f"取得データ数: {len(values)}件")
                            
                            # 最初の5件を表示
                            for i, val in enumerate(values[:5], 1):
                                value = val.get("$", "")
                                unit = val.get("@unit", "")
                                print(f"  {i}. 値: {value} {unit}")
                                
        except Exception as e:
            print(f"エラー: {e}")
            import traceback
            traceback.print_exc()

async def test_specific_api():
    """特定の統計表IDで直接テスト"""
    api_key = "992fa8d6f43d645c3c767a97410fe89612cfecc7"
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    print("\n【特定統計表テスト: 国勢調査】")
    print("-"*40)
    
    # 国勢調査の統計表を検索
    async with aiohttp.ClientSession() as session:
        url = f"{base_url}/getStatsList"
        params = {
            "appId": api_key,
            "searchWord": "国勢調査 市区町村",
            "limit": 3
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    stats_list = data.get("GET_STATS_LIST", {})
                    tables = stats_list.get("DATALIST_INF", {}).get("TABLE_INF", [])
                    
                    if not isinstance(tables, list):
                        tables = [tables] if tables else []
                    
                    for table in tables:
                        table_id = table.get("@id", "")
                        title = table.get("TITLE", {})
                        if isinstance(title, dict):
                            title_text = title.get("$", "")
                        else:
                            title_text = str(title)
                        
                        print(f"\nテーブルID: {table_id}")
                        print(f"タイトル: {title_text[:80]}")
                        
        except Exception as e:
            print(f"エラー: {e}")

async def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("e-Stat API 詳細調査")
    print("="*60)
    
    # 各種テストを実行
    await test_direct_api_call()
    await test_specific_api()
    
    print("\n" + "="*60)
    print("調査完了")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())