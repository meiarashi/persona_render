#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e-Stat APIで実際に取得可能な医療データを調査
"""

import asyncio
import aiohttp
import os
import json
import sys
from pathlib import Path

# Windows環境での文字化け対策
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

async def search_medical_stats():
    """医療関連の統計表を検索"""
    api_key = os.getenv("ESTAT_API_KEY")
    if not api_key:
        print("ESTAT_API_KEYが設定されていません")
        return
    
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    # 患者調査の統計表を検索
    stats_codes = {
        "00450022": "患者調査",
        "00450021": "医療施設調査",
        "00450024": "受療行動調査"
    }
    
    print("="*60)
    print("e-Stat APIで利用可能な医療統計データ")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        for stats_code, name in stats_codes.items():
            print(f"\n【{name}（統計コード: {stats_code}）】")
            print("-"*40)
            
            # 統計表リストを取得
            url = f"{base_url}/getStatsList"
            params = {
                "appId": api_key,
                "statsCode": stats_code,
                "limit": 5
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # リストを解析
                        list_inf = data.get("GET_STATS_LIST", {}).get("DATALIST_INF", {})
                        tables = list_inf.get("TABLE_INF", [])
                        
                        if not isinstance(tables, list):
                            tables = [tables] if tables else []
                        
                        print(f"取得可能な統計表数: {len(tables)}件")
                        
                        # 最新の統計表を表示
                        for i, table in enumerate(tables[:3], 1):
                            table_id = table.get("@id", "")
                            title = table.get("TITLE", {})
                            if isinstance(title, dict):
                                title_text = title.get("$", "")
                            else:
                                title_text = str(title)
                            
                            # 更新日
                            updated = table.get("UPDATED_DATE", "")
                            
                            print(f"\n  {i}. テーブルID: {table_id}")
                            print(f"     タイトル: {title_text[:60]}...")
                            print(f"     更新日: {updated}")
                            
                            # 主要項目を確認
                            main_cat = table.get("MAIN_CATEGORY", {})
                            if isinstance(main_cat, dict):
                                cat_text = main_cat.get("$", "")
                            else:
                                cat_text = str(main_cat)
                            print(f"     カテゴリ: {cat_text}")
                            
                    else:
                        print(f"  エラー: ステータス {response.status}")
                        
            except Exception as e:
                print(f"  エラー: {e}")

async def get_consultation_rate_data():
    """受療率データの詳細を取得"""
    api_key = os.getenv("ESTAT_API_KEY")
    if not api_key:
        return
    
    print("\n" + "="*60)
    print("受療率データの詳細調査")
    print("="*60)
    
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    # 患者調査から受療率関連のデータを探す
    async with aiohttp.ClientSession() as session:
        # 統計表リストから「受療率」を含むものを検索
        url = f"{base_url}/getStatsList"
        params = {
            "appId": api_key,
            "searchWord": "受療率",
            "limit": 10
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    list_inf = data.get("GET_STATS_LIST", {}).get("DATALIST_INF", {})
                    tables = list_inf.get("TABLE_INF", [])
                    
                    if not isinstance(tables, list):
                        tables = [tables] if tables else []
                    
                    print(f"\n「受療率」を含む統計表: {len(tables)}件")
                    
                    for table in tables[:5]:
                        table_id = table.get("@id", "")
                        title = table.get("TITLE", {})
                        if isinstance(title, dict):
                            title_text = title.get("$", "")
                        else:
                            title_text = str(title)
                        
                        stats_name = table.get("STATISTICS_NAME", {})
                        if isinstance(stats_name, dict):
                            stats_text = stats_name.get("$", "")
                        else:
                            stats_text = str(stats_name)
                        
                        print(f"\n  ID: {table_id}")
                        print(f"  統計名: {stats_text}")
                        print(f"  タイトル: {title_text[:80]}...")
                        
        except Exception as e:
            print(f"エラー: {e}")

async def get_disease_classification_data():
    """傷病分類別データを取得"""
    api_key = os.getenv("ESTAT_API_KEY")
    if not api_key:
        return
    
    print("\n" + "="*60)
    print("傷病分類別データの詳細調査")
    print("="*60)
    
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    async with aiohttp.ClientSession() as session:
        # 「傷病」を含む統計表を検索
        url = f"{base_url}/getStatsList"
        params = {
            "appId": api_key,
            "searchWord": "傷病 診療科",
            "limit": 10
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    list_inf = data.get("GET_STATS_LIST", {}).get("DATALIST_INF", {})
                    tables = list_inf.get("TABLE_INF", [])
                    
                    if not isinstance(tables, list):
                        tables = [tables] if tables else []
                    
                    print(f"\n「傷病・診療科」を含む統計表: {len(tables)}件")
                    
                    for table in tables[:5]:
                        table_id = table.get("@id", "")
                        title = table.get("TITLE", {})
                        if isinstance(title, dict):
                            title_text = title.get("$", "")
                        else:
                            title_text = str(title)
                        
                        print(f"\n  ID: {table_id}")
                        print(f"  タイトル: {title_text[:80]}...")
                        
        except Exception as e:
            print(f"エラー: {e}")

async def test_specific_table(table_id: str):
    """特定のテーブルIDのメタ情報を取得"""
    api_key = os.getenv("ESTAT_API_KEY")
    if not api_key:
        return
    
    print(f"\n【テーブル {table_id} のメタ情報】")
    print("-"*40)
    
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    async with aiohttp.ClientSession() as session:
        url = f"{base_url}/getMetaInfo"
        params = {
            "appId": api_key,
            "statsDataId": table_id
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # CLASS情報を取得
                    class_info = data.get("GET_META_INFO", {}).get("METADATA_INF", {}).get("CLASS_INF", {})
                    class_obj = class_info.get("CLASS_OBJ", [])
                    
                    if not isinstance(class_obj, list):
                        class_obj = [class_obj] if class_obj else []
                    
                    print("利用可能な分類:")
                    for cls in class_obj[:5]:
                        cls_id = cls.get("@id", "")
                        cls_name = cls.get("@name", "")
                        print(f"  - {cls_id}: {cls_name}")
                        
                        # CODE情報も確認
                        codes = cls.get("CLASS", [])
                        if not isinstance(codes, list):
                            codes = [codes] if codes else []
                        
                        for code in codes[:3]:
                            code_val = code.get("@code", "")
                            code_name = code.get("@name", "")
                            print(f"    → {code_val}: {code_name}")
                            
        except Exception as e:
            print(f"エラー: {e}")

async def main():
    """メイン処理"""
    print("\n" + "="*60)
    print("e-Stat API 実際のデータ調査")
    print("="*60)
    
    api_key = os.getenv("ESTAT_API_KEY")
    if not api_key:
        print("\n[エラー] ESTAT_API_KEYが設定されていません")
        print("環境変数にe-Stat APIキーを設定してください")
        return
    
    # 各種データを調査
    await search_medical_stats()
    await get_consultation_rate_data()
    await get_disease_classification_data()
    
    # 実際に存在する患者調査のテーブルIDを調べる
    # 例：最新の患者調査のID
    print("\n" + "="*60)
    print("実際のテーブルIDでテスト")
    print("="*60)
    await test_specific_table("0003445026")  # 令和2年患者調査の例

if __name__ == "__main__":
    asyncio.run(main())