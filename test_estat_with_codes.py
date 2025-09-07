#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
統計コードを使用したe-Stat APIテスト
政府統計コードを使用して正しくデータを取得できるか確認
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

API_KEY = "992fa8d6f43d645c3c767a97410fe89612cfecc7"

async def test_stats_code(stats_code: str, name: str):
    """統計コードでのAPI呼び出しテスト"""
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    print(f"\n【{name}（統計コード: {stats_code}）のテスト】")
    print("-"*50)
    
    async with aiohttp.ClientSession() as session:
        # 統計コードで統計表を検索
        url = f"{base_url}/getStatsList"
        params = {
            "appId": API_KEY,
            "statsCode": stats_code,
            "limit": 3
        }
        
        print(f"URL: {url}")
        print(f"パラメータ: statsCode={stats_code}")
        
        try:
            async with session.get(url, params=params) as response:
                print(f"ステータスコード: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # レスポンス構造を確認
                    stats_list = data.get("GET_STATS_LIST", {})
                    
                    # ステータス確認
                    result = stats_list.get("RESULT", {})
                    status = result.get("STATUS")
                    
                    if status == 0:
                        print("[SUCCESS] APIコール成功")
                        
                        # データリスト情報
                        datalist = stats_list.get("DATALIST_INF", {})
                        total = datalist.get("RESULT_INF", {}).get("TOTAL_NUMBER", 0)
                        print(f"統計表数: {total}件")
                        
                        # テーブル情報を表示
                        tables = datalist.get("TABLE_INF", [])
                        if not isinstance(tables, list):
                            tables = [tables] if tables else []
                        
                        for i, table in enumerate(tables[:3], 1):
                            table_id = table.get("@id", "")
                            title = table.get("TITLE", {})
                            if isinstance(title, dict):
                                title_text = title.get("$", "")
                            else:
                                title_text = str(title)
                            
                            # 統計分野情報
                            stat_name = table.get("STAT_NAME", {})
                            if isinstance(stat_name, dict):
                                stat_name_text = stat_name.get("$", "")
                            else:
                                stat_name_text = str(stat_name)
                            
                            # 調査年月
                            survey_date = table.get("SURVEY_DATE", "")
                            
                            print(f"\n  [{i}] テーブルID: {table_id}")
                            print(f"      タイトル: {title_text[:60]}")
                            print(f"      統計名: {stat_name_text}")
                            print(f"      調査年月: {survey_date}")
                    else:
                        error_msg = result.get("ERROR_MSG", "不明なエラー")
                        print(f"[ERROR] APIエラー: {error_msg}")
                else:
                    print(f"[ERROR] HTTPエラー: {response.status}")
                    
        except Exception as e:
            print(f"[ERROR] 例外発生: {e}")

async def test_area_specific_data():
    """地域を指定したデータ取得テスト"""
    print("\n" + "="*60)
    print("地域指定データ取得テスト")
    print("="*60)
    
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    # 国勢調査から東京都のデータを取得
    async with aiohttp.ClientSession() as session:
        url = f"{base_url}/getStatsList"
        params = {
            "appId": API_KEY,
            "statsCode": "00200521",  # 国勢調査
            "searchWord": "東京都 千代田区",
            "limit": 2
        }
        
        print("\n統計コード + 地域名での検索")
        print(f"検索ワード: 東京都 千代田区")
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    stats_list = data.get("GET_STATS_LIST", {})
                    
                    if stats_list.get("RESULT", {}).get("STATUS") == 0:
                        tables = stats_list.get("DATALIST_INF", {}).get("TABLE_INF", [])
                        if not isinstance(tables, list):
                            tables = [tables] if tables else []
                        
                        if tables:
                            print(f"見つかった統計表: {len(tables)}件")
                            
                            # 最初のテーブルからデータを取得
                            table_id = tables[0].get("@id", "")
                            print(f"\nテーブルID {table_id} からデータ取得...")
                            
                            # データ取得
                            data_url = f"{base_url}/getStatsData"
                            data_params = {
                                "appId": API_KEY,
                                "statsDataId": table_id,
                                "limit": 5
                            }
                            
                            async with session.get(data_url, params=data_params) as data_response:
                                if data_response.status == 200:
                                    stats_data = await data_response.json()
                                    values = stats_data.get("GET_STATS_DATA", {}).get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
                                    
                                    if not isinstance(values, list):
                                        values = [values] if values else []
                                    
                                    print(f"取得データ数: {len(values)}件")
                                    for i, val in enumerate(values[:3], 1):
                                        value = val.get("$", "")
                                        unit = val.get("@unit", "")
                                        print(f"  {i}. {value} {unit}")
                        else:
                            print("該当する統計表が見つかりませんでした")
                            
        except Exception as e:
            print(f"エラー: {e}")

async def main():
    """メイン処理"""
    print("="*60)
    print("e-Stat API 統計コードテスト")
    print("="*60)
    print(f"APIキー: {API_KEY[:10]}...")
    
    # 政府統計コードPDFから取得した統計コードをテスト
    test_cases = [
        ("00200521", "国勢調査"),
        ("00450021", "医療施設調査"),
        ("00450022", "患者調査"),
        ("00450024", "受療行動調査"),
    ]
    
    for stats_code, name in test_cases:
        await test_stats_code(stats_code, name)
        await asyncio.sleep(0.5)  # API制限を考慮
    
    # 地域指定のテスト
    await test_area_specific_data()
    
    print("\n" + "="*60)
    print("テスト完了")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())