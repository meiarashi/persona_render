#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
3つのJSONファイルを統合して、マスターJSONファイルを作成
"""

import json
from pathlib import Path

def create_master_json():
    base_path = Path('backend/data')
    
    # 既存のJSONファイルを読み込み
    with open(base_path / 'japan_area_codes.json', 'r', encoding='utf-8') as f:
        area_codes = json.load(f)
    
    with open(base_path / 'japan_regions.json', 'r', encoding='utf-8') as f:
        regions = json.load(f)
    
    with open(base_path / 'estat_api_params.json', 'r', encoding='utf-8') as f:
        api_params = json.load(f)
    
    # 統合マスターデータを作成
    master = {
        "description": "日本全国地域マスターデータ（e-Stat API連携・統合版）",
        "version": "3.0.0",
        "updated": "2024-01",
        
        # API設定（estat_api_params.jsonから）
        "api_config": {
            "base_url": "http://api.e-stat.go.jp/rest/3.0/app/json",
            "endpoints": api_params.get("api_endpoints", {}),
            "stats_tables": api_params.get("stats_tables", {}),
            "cache_settings": api_params.get("cache_settings", {})
        },
        
        # 医療需要パターン（japan_regions.jsonから）
        "medical_demand_patterns": regions.get("medical_demand_patterns", {}),
        
        # 全国市区町村データ（統合）
        "regions": {}
    }
    
    # area_codesとregionsのデータを統合
    for pref_code, pref_data in area_codes["prefectures"].items():
        pref_name = pref_data["name"]
        
        # regionsからフォールバックデータを取得
        regions_pref_data = regions["prefectures"].get(pref_code, {})
        
        master["regions"][pref_code] = {
            "name": pref_name,
            "code": pref_data["code"],
            "fallback_data": {
                "population": regions_pref_data.get("population", 0),
                "age_distribution": regions_pref_data.get("age_distribution", {}),
                "medical_facilities": regions_pref_data.get("medical_facilities", 0),
                "facilities_per_10000": regions_pref_data.get("facilities_per_10000", 0)
            },
            "cities": {}
        }
        
        # 市区町村データを追加
        cities = pref_data.get("cities", {})
        for city_code, city_name in cities.items():
            # 東京23区の特別処理
            if pref_code == "13" and city_code.startswith("131") and len(city_code) == 5:
                city_type = "special_ward"
                # 東京23区のフォールバックデータ（例）
                if city_code == "13113":  # 渋谷区
                    fallback_pop = 247820
                elif city_code == "13104":  # 新宿区
                    fallback_pop = 351711
                elif city_code == "13103":  # 港区
                    fallback_pop = 265191
                else:
                    fallback_pop = 200000  # デフォルト
            # 政令指定都市の区
            elif len(city_code) == 5 and city_code.endswith("00"):
                city_type = "designated_city"
                fallback_pop = 500000
            elif len(city_code) == 5 and not city_code.endswith("00"):
                city_type = "ward"
                fallback_pop = 100000
            # 一般市
            else:
                city_type = "city"
                fallback_pop = 50000
            
            # regionsから詳細データを取得（あれば）
            city_detail = None
            if pref_code in regions["prefectures"]:
                major_cities = regions_pref_data.get("major_cities", {})
                for mc_code, mc_data in major_cities.items():
                    if mc_data.get("name") == city_name:
                        city_detail = mc_data
                        break
            
            master["regions"][pref_code]["cities"][city_code] = {
                "name": city_name,
                "type": city_type,
                "fallback_data": {
                    "population": city_detail.get("population", fallback_pop) if city_detail else fallback_pop,
                    "age_distribution": city_detail.get("age_distribution", 
                        regions_pref_data.get("age_distribution", {})) if city_detail else 
                        regions_pref_data.get("age_distribution", {}),
                    "medical_facilities": city_detail.get("medical_facilities", 0) if city_detail else 0,
                    "facilities_per_10000": city_detail.get("facilities_per_10000", 0) if city_detail else 0
                }
            }
    
    # 統計情報を追加
    total_cities = sum(len(pref["cities"]) for pref in master["regions"].values())
    master["statistics"] = {
        "total_prefectures": len(master["regions"]),
        "total_cities": total_cities,
        "data_sources": [
            "総務省 全国地方公共団体コード",
            "e-Stat 政府統計の総合窓口",
            "2024年推計値"
        ]
    }
    
    # ファイルに保存
    output_path = base_path / 'japan_regional_master.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    
    print(f"統合マスターファイル作成完了: {output_path}")
    print(f"都道府県数: {master['statistics']['total_prefectures']}")
    print(f"市区町村数: {master['statistics']['total_cities']}")
    
    return master

if __name__ == "__main__":
    create_master_json()