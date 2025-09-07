#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e-Stat API統合サービス（改良版）
実際のAPIレスポンスに基づいた正確な実装
"""

import os
import json
import asyncio
import aiohttp
import hashlib
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class EStatIntegratedService:
    """e-Stat APIを使用した地域データ取得サービス（改良版）"""
    
    def __init__(self):
        """初期化"""
        self.api_key = os.getenv("ESTAT_API_KEY")
        self.base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
        self.cache_ttl = timedelta(hours=24)
        self.timeout = aiohttp.ClientTimeout(total=60)
        self.master_data = self._load_master_data()
        self.cache = self._load_cache()
    
    def _load_master_data(self) -> Dict:
        """マスターデータを読み込み"""
        try:
            master_path = Path(__file__).parent.parent / "data" / "japan_regional_master.json"
            with open(master_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"マスターデータ読み込みエラー: {e}")
            return {}
    
    def _load_cache(self) -> Dict:
        """キャッシュを読み込み"""
        cache_path = Path(__file__).parent.parent / "cache" / "estat_cache.json"
        
        try:
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                    # 期限切れエントリを削除
                    now = datetime.now()
                    valid_cache = {}
                    for key, value in cache_data.items():
                        timestamp = datetime.fromisoformat(value.get("timestamp", ""))
                        if now - timestamp < self.cache_ttl:
                            valid_cache[key] = value
                    
                    return valid_cache
        except Exception as e:
            logger.error(f"キャッシュ読み込みエラー: {e}")
        
        return {}
    
    def _save_cache(self):
        """キャッシュを保存"""
        cache_path = Path(__file__).parent.parent / "cache" / "estat_cache.json"
        cache_path.parent.mkdir(exist_ok=True)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"キャッシュ保存エラー: {e}")
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """キャッシュキーを生成"""
        key_str = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _parse_address_to_code(self, address: str) -> Optional[str]:
        """住所から地域コードを取得"""
        if not address:
            return "13101"  # デフォルトは東京都千代田区
        
        # 全角・半角スペースを統一
        address = address.replace('　', ' ').strip()
        
        # 全都道府県をチェック
        for pref_code, pref_data in self.master_data.get("regions", {}).items():
            pref_name = pref_data.get("name", "")
            
            if pref_name in address:
                # 都道府県内の市区町村をチェック
                cities = pref_data.get("cities", {})
                
                # より詳細な地域から順にチェック（長い名前から）
                for city_code, city_data in cities.items():
                    city_name = city_data if isinstance(city_data, str) else city_data.get("name", "")
                    if city_name and city_name in address:
                        logger.info(f"地域コード判定: {pref_name}{city_name} -> {city_code}")
                        return city_code
                
                # 市区町村が見つからない場合は都道府県コード
                pref_code_num = pref_data.get("code", f"{pref_code}000")
                logger.info(f"地域コード判定: {pref_name} -> {pref_code_num}")
                return pref_code_num
        
        # デフォルト
        logger.info("地域コード判定: デフォルト（東京都千代田区）")
        return "13101"
    
    async def get_regional_data(self, address: str) -> Dict[str, Any]:
        """住所から地域統計データを取得（シンプル版）"""
        
        # APIキーがない場合はフォールバックデータを返す
        if not self.api_key:
            logger.warning("e-Stat APIキーが設定されていません")
            return self._get_fallback_data(address)
        
        area_code = self._parse_address_to_code(address)
        
        # 人口データを取得（実際のAPIを使用）
        population_data = await self._get_simple_population_data(area_code)
        
        # 医療需要を計算（MedicalDemandCalculatorと連携）
        from .medical_demand_calculator import MedicalDemandCalculator
        calculator = MedicalDemandCalculator()
        
        # 地域タイプを判定
        area_type = self._determine_area_type(address, population_data.get("total", 100000))
        
        # 医療需要を計算
        age_dist = population_data.get("age_distribution", {
            "0-14": 12.5,
            "15-64": 62.5,
            "65+": 25.0
        })
        
        medical_demand = calculator.calculate_area_demand(
            population=population_data.get("total", 100000),
            age_distribution=age_dist,
            area_type=area_type
        )
        
        return {
            "area_code": area_code,
            "population": population_data,
            "demographics": {
                "age_distribution": age_dist,
                "aging_rate": age_dist.get("65+", 25.0)
            },
            "area_type": area_type,
            "medical_demand": {
                "estimated_daily_patients": medical_demand["total_daily_patients"],
                "consultation_rate": medical_demand["consultation_rate_per_100k"],
                "department_breakdown": medical_demand["department_breakdown"]
            },
            "households": {
                "total": population_data.get("households", 40000)
            },
            "data_source": "e-Stat API" if population_data.get("from_api") else "fallback"
        }
    
    async def _get_simple_population_data(self, area_code: str) -> Dict:
        """シンプルな人口データ取得（実際のAPIを使用）"""
        
        # キャッシュチェック
        cache_key = f"pop_{area_code}"
        if cache_key in self.cache:
            logger.info(f"キャッシュヒット: 人口データ ({area_code})")
            return self.cache[cache_key]["data"]
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # 人口統計を検索
                search_url = f"{self.base_url}/getStatsList"
                search_params = {
                    "appId": self.api_key,
                    "searchWord": "人口推計",
                    "limit": 1
                }
                
                async with session.get(search_url, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        stats_list = data.get("GET_STATS_LIST", {})
                        
                        # エラーチェック
                        if stats_list.get("RESULT", {}).get("STATUS") != 0:
                            logger.error(f"統計表検索エラー: {stats_list.get('RESULT', {}).get('ERROR_MSG', '')}")
                            return self._get_default_population_data()
                        
                        tables = stats_list.get("DATALIST_INF", {}).get("TABLE_INF", [])
                        if not isinstance(tables, list):
                            tables = [tables] if tables else []
                        
                        if tables:
                            # 最初のテーブルから実データを取得
                            stats_data_id = tables[0].get("@id", "")
                            
                            # 実データを取得
                            data_url = f"{self.base_url}/getStatsData"
                            data_params = {
                                "appId": self.api_key,
                                "statsDataId": stats_data_id,
                                "limit": 10
                            }
                            
                            async with session.get(data_url, params=data_params) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    result = self._parse_simple_population(data)
                                    result["from_api"] = True
                                    
                                    # キャッシュに保存
                                    self.cache[cache_key] = {
                                        "data": result,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                    self._save_cache()
                                    
                                    return result
        
        except Exception as e:
            logger.error(f"人口データ取得エラー: {e}")
        
        return self._get_default_population_data()
    
    def _parse_simple_population(self, data: Dict) -> Dict:
        """APIレスポンスから人口データを抽出"""
        result = self._get_default_population_data()
        
        try:
            stats_data = data.get("GET_STATS_DATA", {})
            
            # エラーチェック
            if stats_data.get("RESULT", {}).get("STATUS") != 0:
                return result
            
            # VALUE配列から人口データを抽出
            values = stats_data.get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
            if not isinstance(values, list):
                values = [values] if values else []
            
            # 最初の値を総人口として使用
            if values:
                try:
                    value_str = str(values[0].get("$", "0"))
                    # カンマと単位を除去
                    value_str = value_str.replace(",", "").replace("人", "")
                    result["total"] = int(float(value_str))
                except (ValueError, AttributeError):
                    pass
        
        except Exception as e:
            logger.error(f"人口データパースエラー: {e}")
        
        return result
    
    def _get_default_population_data(self) -> Dict:
        """デフォルトの人口データ"""
        return {
            "total": 100000,
            "age_distribution": {
                "0-14": 12.5,
                "15-64": 62.5,
                "65+": 25.0
            },
            "households": 40000,
            "from_api": False
        }
    
    def _determine_area_type(self, address: str, population: int) -> str:
        """地域タイプを判定"""
        # 主要都市の判定
        major_cities = ["東京", "大阪", "名古屋", "横浜", "福岡", "札幌", "神戸", "京都", "さいたま", "千葉"]
        
        for city in major_cities:
            if city in address:
                if "区" in address:
                    return "urban_high_density"
                else:
                    return "urban_medium_density"
        
        # 人口による判定
        if population > 500000:
            return "urban_medium_density"
        elif population > 100000:
            return "suburban"
        else:
            return "rural"
    
    def _get_fallback_data(self, address: str) -> Dict:
        """フォールバックデータを返す"""
        area_code = self._parse_address_to_code(address)
        
        # マスターデータから基本情報を取得
        for pref_code, pref_data in self.master_data.get("regions", {}).items():
            cities = pref_data.get("cities", {})
            if area_code in cities:
                city_data = cities[area_code]
                if isinstance(city_data, dict):
                    return {
                        "area_code": area_code,
                        "population": {
                            "total": city_data.get("population", 100000)
                        },
                        "demographics": {
                            "aging_rate": city_data.get("aging_rate", 25.0)
                        },
                        "area_type": city_data.get("area_type", "suburban"),
                        "medical_demand": {
                            "estimated_daily_patients": city_data.get("medical_demand", {}).get("estimated_daily_patients", 1000)
                        },
                        "data_source": "master_data"
                    }
        
        # デフォルト値
        return {
            "area_code": area_code,
            "population": {"total": 100000},
            "demographics": {"aging_rate": 25.0},
            "area_type": "suburban",
            "medical_demand": {"estimated_daily_patients": 1000},
            "data_source": "default"
        }