#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e-Stat APIから取得可能な医療関連統計の探索
競合分析に有用なデータを特定
"""

import asyncio
import aiohttp
import json
import sys

# Windows環境での文字化け対策
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

API_KEY = "992fa8d6f43d645c3c767a97410fe89612cfecc7"

async def explore_medical_statistics():
    """医療関連統計の探索"""
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    print("="*70)
    print("e-Statから取得可能な医療・競合分析関連データ")
    print("="*70)
    
    # 調査する統計コード（政府統計コードPDFより）
    stats_codes = [
        ("00450021", "医療施設調査", "医療施設数、診療科目、病床数等"),
        ("00450022", "患者調査", "患者数、受療率、疾患別患者数"),
        ("00450024", "受療行動調査", "患者の受療行動、満足度"),
        ("00450025", "医師・歯科医師・薬剤師統計", "医療従事者数"),
        ("00450027", "病院報告", "患者数の動向、病床利用率"),
        ("00450091", "介護サービス施設・事業所調査", "介護施設数"),
        ("00200502", "経済センサス", "事業所数、従業者数"),
        ("00200572", "家計調査", "医療費支出"),
        ("00450412", "国民医療費", "医療費総額、一人当たり医療費"),
        ("00450023", "医療経済実態調査", "医療機関の経営状況")
    ]
    
    async with aiohttp.ClientSession() as session:
        for stats_code, name, description in stats_codes:
            print(f"\n【{name}】")
            print(f"統計コード: {stats_code}")
            print(f"説明: {description}")
            print("-"*50)
            
            # 統計表を検索
            url = f"{base_url}/getStatsList"
            params = {
                "appId": API_KEY,
                "statsCode": stats_code,
                "limit": 3
            }
            
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
                                print("利用可能なデータ例:")
                                for i, table in enumerate(tables[:3], 1):
                                    title = table.get("TITLE", {})
                                    if isinstance(title, dict):
                                        title_text = title.get("$", "")
                                    else:
                                        title_text = str(title)
                                    
                                    survey_date = table.get("SURVEY_DATE", "")
                                    table_id = table.get("@id", "")
                                    
                                    print(f"  {i}. {title_text[:60]}")
                                    if survey_date:
                                        year = str(survey_date)[:4] if len(str(survey_date)) >= 4 else survey_date
                                        print(f"     調査年: {year}年")
                                    
                                # 最初のテーブルの詳細を取得
                                if tables:
                                    await get_table_details(session, tables[0].get("@id", ""), name)
                            else:
                                print("  データなし")
                        else:
                            error_msg = stats_list.get("RESULT", {}).get("ERROR_MSG", "")
                            if "該当データはありません" not in error_msg:
                                print(f"  エラー: {error_msg}")
                            else:
                                print("  データなし")
                    
            except Exception as e:
                print(f"  取得エラー: {e}")
            
            await asyncio.sleep(0.5)  # API制限対策

async def get_table_details(session, table_id, stat_name):
    """統計表の詳細情報を取得"""
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    try:
        # メタ情報を取得
        meta_url = f"{base_url}/getMetaInfo"
        params = {
            "appId": API_KEY,
            "statsDataId": table_id
        }
        
        async with session.get(meta_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                meta_info = data.get("GET_META_INFO", {})
                
                if meta_info.get("RESULT", {}).get("STATUS") == 0:
                    class_objs = meta_info.get("METADATA_INF", {}).get("CLASS_INF", {}).get("CLASS_OBJ", [])
                    if not isinstance(class_objs, list):
                        class_objs = [class_objs] if class_objs else []
                    
                    print("\n  取得可能な分類項目:")
                    for cls in class_objs[:5]:
                        cls_name = cls.get("@name", "")
                        if cls_name and cls_name not in ["表章項目", "時間軸"]:
                            print(f"    - {cls_name}")
                            
                            # いくつかのコード例を表示
                            codes = cls.get("CLASS", [])
                            if not isinstance(codes, list):
                                codes = [codes] if codes else []
                            
                            if codes and len(codes) > 1:
                                examples = []
                                for code in codes[:3]:
                                    code_name = code.get("@name", "")
                                    if code_name:
                                        examples.append(code_name)
                                if examples:
                                    print(f"      例: {', '.join(examples)}")
    
    except Exception as e:
        pass  # エラーは無視

async def analyze_competition_data():
    """競合分析に特に有用なデータの詳細分析"""
    print("\n" + "="*70)
    print("競合分析に特に有用なデータの詳細")
    print("="*70)
    
    useful_searches = [
        {
            "statsCode": "00450021",
            "searchWord": "診療科目別",
            "title": "診療科目別の医療施設数",
            "use_case": "地域の診療科別競合数を把握"
        },
        {
            "statsCode": "00450022", 
            "searchWord": "傷病別",
            "title": "傷病別患者数",
            "use_case": "需要の高い疾患を特定"
        },
        {
            "statsCode": "00450025",
            "searchWord": "市区町村",
            "title": "市区町村別医師数",
            "use_case": "医師不足地域の特定"
        },
        {
            "statsCode": "00200502",
            "searchWord": "医療 診療所",
            "title": "経済センサス - 医療事業所",
            "use_case": "開業・廃業の動向把握"
        },
        {
            "statsCode": "00450027",
            "searchWord": "外来患者",
            "title": "外来患者数の推移",
            "use_case": "患者数のトレンド分析"
        }
    ]
    
    base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
    
    async with aiohttp.ClientSession() as session:
        for search_info in useful_searches:
            print(f"\n【{search_info['title']}】")
            print(f"活用方法: {search_info['use_case']}")
            print("-"*50)
            
            url = f"{base_url}/getStatsList"
            params = {
                "appId": API_KEY,
                "statsCode": search_info["statsCode"],
                "searchWord": search_info["searchWord"],
                "limit": 2
            }
            
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
                                for table in tables[:1]:
                                    title = table.get("TITLE", {})
                                    if isinstance(title, dict):
                                        title_text = title.get("$", "")
                                    else:
                                        title_text = str(title)
                                    
                                    print(f"データ例: {title_text[:80]}")
                                    print(f"テーブルID: {table.get('@id', '')}")
                            else:
                                print("該当データなし")
                        else:
                            print("該当データなし")
            
            except Exception as e:
                print(f"取得エラー: {e}")
            
            await asyncio.sleep(0.5)

async def main():
    """メイン処理"""
    print("\n競合分析の精度向上に活用可能なe-Statデータ調査\n")
    
    # 基本的な医療統計の探索
    await explore_medical_statistics()
    
    # 競合分析に特化したデータの分析
    await analyze_competition_data()
    
    print("\n" + "="*70)
    print("調査完了 - 実装可能な追加データ")
    print("="*70)
    
    print("""
以下のデータを追加実装することで競合分析の精度を向上できます：

1. 【診療科目別医療施設数】
   - 地域の診療科別の競合数を正確に把握
   - 供給過多/不足の診療科を特定

2. 【疾患別患者数・受療率】
   - 地域で需要の高い疾患を特定
   - ターゲット患者層の明確化

3. 【医師・医療従事者数】
   - 医師不足地域の特定
   - 人材確保の難易度評価

4. 【外来患者数の推移】
   - 患者数のトレンド分析
   - 将来の需要予測

5. 【世帯構成・家族類型】
   - ファミリー層vs高齢者世帯の比率
   - ターゲット層の世帯特性把握

6. 【所得・消費支出】
   - 地域の経済力評価
   - 自費診療の需要推定

7. 【介護施設数】
   - 高齢者医療の競合/連携先把握
   - 在宅医療の需要推定
    """)

if __name__ == "__main__":
    asyncio.run(main())