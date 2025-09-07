#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
e-Stat API統合サービス
JSONパラメータを使用してAPIを呼び出し、結果をキャッシュ
"""

import os
import json
import aiohttp
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class EStatIntegratedService:
    """e-Stat APIとJSONパラメータを統合したサービス"""
    
    def __init__(self):
        self.api_key = os.getenv("ESTAT_API_KEY")
        self.timeout = aiohttp.ClientTimeout(total=30)
        
        # 統合マスターデータの読み込み
        self.master_data = self._load_master_data()
        self.base_url = self.master_data.get("api_config", {}).get("base_url", "http://api.e-stat.go.jp/rest/3.0/app/json")
        
        # キャッシュの初期化
        self.cache = {}
        self.cache_file = Path(__file__).parent.parent / "data" / "estat_cache.json"
        self._load_cache()
        
    def _load_master_data(self) -> Dict:
        """統合マスターデータをJSONから読み込み"""
        try:
            master_path = Path(__file__).parent.parent / "data" / "japan_regional_master.json"
            with open(master_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stats = data.get("statistics", {})
                logger.info(f"マスターデータをロード: {stats.get('total_prefectures', 0)}都道府県, {stats.get('total_cities', 0)}市区町村")
                return data
        except Exception as e:
            logger.error(f"マスターデータ読み込みエラー: {e}")
            # フォールバック
            return {
                "api_config": {
                    "base_url": "http://api.e-stat.go.jp/rest/3.0/app/json",
                    "stats_tables": {},
                    "cache_settings": {"ttl_minutes": 1440, "max_entries": 1000}
                },
                "regions": {},
                "medical_demand_patterns": {}
            }
    
    def _load_cache(self):
        """キャッシュファイルを読み込み"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # 有効期限チェック
                    cache_settings = self.master_data.get("api_config", {}).get("cache_settings", {})
                    ttl_minutes = cache_settings.get("ttl_minutes", 1440)
                    cutoff_time = datetime.now() - timedelta(minutes=ttl_minutes)
                    
                    for key, value in cache_data.items():
                        if "timestamp" in value:
                            cache_time = datetime.fromisoformat(value["timestamp"])
                            if cache_time > cutoff_time:
                                self.cache[key] = value
                    
                    logger.info(f"キャッシュをロード: {len(self.cache)}件")
        except Exception as e:
            logger.warning(f"キャッシュ読み込みエラー: {e}")
    
    def _save_cache(self):
        """キャッシュをファイルに保存"""
        try:
            # 最大エントリ数を制限
            cache_settings = self.master_data.get("api_config", {}).get("cache_settings", {})
            max_entries = cache_settings.get("max_entries", 1000)
            if len(self.cache) > max_entries:
                # 古いエントリから削除
                sorted_items = sorted(
                    self.cache.items(),
                    key=lambda x: x[1].get("timestamp", ""),
                    reverse=True
                )
                self.cache = dict(sorted_items[:max_entries])
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"キャッシュ保存エラー: {e}")
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """キャッシュキーを生成"""
        key_str = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _parse_address_to_code(self, address: str) -> Optional[str]:
        """住所から地域コードを取得（全国対応）"""
        if not address:
            return "13000"  # デフォルトは東京都
        
        # 全角・半角スペースを統一
        address = address.replace('　', ' ').strip()
        
        # 全都道府県をチェック
        for pref_code, pref_data in self.master_data.get("regions", {}).items():
            pref_name = pref_data.get("name", "")
            
            if pref_name in address:
                # 都道府県内の市区町村をチェック
                cities = pref_data.get("cities", {})
                
                # より詳細な地域から順にチェック（長い名前から）
                sorted_cities = sorted(cities.items(), key=lambda x: len(x[1] if isinstance(x[1], str) else x[1].get("name", "")), reverse=True)
                
                for city_code, city_data in sorted_cities:
                    city_name = city_data if isinstance(city_data, str) else city_data.get("name", "")
                    if city_name and city_name in address:
                        logger.info(f"地域コード判定: {pref_name}{city_name} -> {city_code}")
                        return city_code
                
                # 市区町村が見つからない場合は都道府県コード
                logger.info(f"地域コード判定: {pref_name} -> {pref_data['code']}")
                return pref_data.get("code", f"{pref_code}000")
        
        # 都道府県名が省略されている場合（東京23区など）
        for pref_code, pref_data in self.master_data.get("regions", {}).items():
            cities = pref_data.get("cities", {})
            sorted_cities = sorted(cities.items(), key=lambda x: len(x[1] if isinstance(x[1], str) else x[1].get("name", "")), reverse=True)
            
            for city_code, city_data in sorted_cities:
                city_name = city_data if isinstance(city_data, str) else city_data.get("name", "")
                # 区名や市名だけでマッチする場合
                if city_name and (city_name in address or (city_name.endswith("区") and city_name in address)):
                    logger.info(f"地域コード判定（省略形）: {city_name} -> {city_code}")
                    return city_code
        
        # デフォルトは東京都
        logger.info("地域コード判定: デフォルト（東京都）")
        return "13000"
    
    async def get_regional_data(self, address: str) -> Dict[str, Any]:
        """
        住所から地域統計データを取得
        
        1. 住所から地域コードを判定
        2. キャッシュをチェック
        3. なければAPIを呼び出し
        4. 結果をキャッシュして返却
        """
        if not self.api_key:
            logger.warning("e-Stat APIキーが設定されていません")
            return self._get_fallback_data(address)
        
        area_code = self._parse_address_to_code(address)
        
        result = {
            "demographics": {},
            "medical_facilities": {},
            "medical_demand": {},
            "area_info": {
                "area_code": area_code,
                "address": address
            }
        }
        
        # 並列でAPIを呼び出し
        tasks = [
            self._get_population_data(area_code),
            self._get_medical_facility_data(area_code),
            self._get_patient_data(area_code)
        ]
        
        try:
            population, facilities, patients = await asyncio.gather(*tasks, return_exceptions=True)
            
            # エラーチェックと結果統合
            if not isinstance(population, Exception):
                result["demographics"] = population
            else:
                logger.warning(f"人口データ取得エラー: {population}")
                
            if not isinstance(facilities, Exception):
                result["medical_facilities"] = facilities
            else:
                logger.warning(f"医療施設データ取得エラー: {facilities}")
                
            if not isinstance(patients, Exception):
                result["medical_demand"] = self._calculate_medical_demand(
                    population if not isinstance(population, Exception) else {},
                    patients if not isinstance(patients, Exception) else {}
                )
            else:
                logger.warning(f"患者データ取得エラー: {patients}")
            
            # 競争密度を計算
            result["competition_density"] = self._calculate_competition_density(
                result["demographics"],
                result["medical_facilities"]
            )
            
        except Exception as e:
            logger.error(f"地域データ取得エラー: {e}")
            return self._get_fallback_data(address)
        
        return result
    
    async def _get_population_data(self, area_code: str) -> Dict:
        """人口データをAPIから取得"""
        endpoint = "getStatsData"
        table_info = self.master_data.get("api_config", {}).get("stats_tables", {}).get("population", {})
        
        params = {
            "appId": self.api_key,
            "statsDataId": table_info["statsDataId"],
            "cdArea": area_code,
            "cdCat01": table_info["cdCat01"],
            "limit": 100
        }
        
        # キャッシュチェック
        cache_key = self._get_cache_key(endpoint, params)
        if cache_key in self.cache:
            logger.info(f"キャッシュヒット: 人口データ ({area_code})")
            return self.cache[cache_key]["data"]
        
        # API呼び出し
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/{endpoint}"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = self._parse_population_response(data)
                        
                        # キャッシュに保存
                        self.cache[cache_key] = {
                            "data": result,
                            "timestamp": datetime.now().isoformat()
                        }
                        self._save_cache()
                        
                        logger.info(f"API取得成功: 人口データ ({area_code})")
                        return result
                    else:
                        logger.error(f"API応答エラー: {response.status}")
                        raise Exception(f"API returned status {response.status}")
                        
        except asyncio.TimeoutError:
            logger.error("APIタイムアウト: 人口データ")
            raise
        except Exception as e:
            logger.error(f"API呼び出しエラー: {e}")
            raise
    
    async def _get_medical_facility_data(self, area_code: str) -> Dict:
        """医療施設データをAPIから取得"""
        endpoint = "getStatsData"
        table_info = self.master_data.get("api_config", {}).get("stats_tables", {}).get("medical_facilities", {})
        
        params = {
            "appId": self.api_key,
            "statsDataId": table_info["statsDataId"],
            "cdArea": area_code,
            "cdCat01": table_info["cdCat01"],
            "limit": 100
        }
        
        # キャッシュチェック
        cache_key = self._get_cache_key(endpoint, params)
        if cache_key in self.cache:
            logger.info(f"キャッシュヒット: 医療施設データ ({area_code})")
            return self.cache[cache_key]["data"]
        
        # API呼び出し
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/{endpoint}"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = self._parse_facility_response(data)
                        
                        # キャッシュに保存
                        self.cache[cache_key] = {
                            "data": result,
                            "timestamp": datetime.now().isoformat()
                        }
                        self._save_cache()
                        
                        logger.info(f"API取得成功: 医療施設データ ({area_code})")
                        return result
                    else:
                        raise Exception(f"API returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"医療施設データ取得エラー: {e}")
            raise
    
    async def _get_patient_data(self, area_code: str) -> Dict:
        """患者データをAPIから取得"""
        endpoint = "getStatsData"
        table_info = self.master_data.get("api_config", {}).get("stats_tables", {}).get("patients", {})
        
        params = {
            "appId": self.api_key,
            "statsDataId": table_info["statsDataId"],
            "cdArea": area_code,
            "cdCat01": table_info["cdCat01"],
            "limit": 100
        }
        
        # キャッシュチェック
        cache_key = self._get_cache_key(endpoint, params)
        if cache_key in self.cache:
            logger.info(f"キャッシュヒット: 患者データ ({area_code})")
            return self.cache[cache_key]["data"]
        
        # API呼び出し
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/{endpoint}"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = self._parse_patient_response(data)
                        
                        # キャッシュに保存
                        self.cache[cache_key] = {
                            "data": result,
                            "timestamp": datetime.now().isoformat()
                        }
                        self._save_cache()
                        
                        logger.info(f"API取得成功: 患者データ ({area_code})")
                        return result
                    else:
                        raise Exception(f"API returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"患者データ取得エラー: {e}")
            raise
    
    def _parse_population_response(self, data: Dict) -> Dict:
        """人口データのレスポンスをパース"""
        try:
            values = data.get("GET_STATS_DATA", {}).get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
            
            if not values:
                return {}
            
            total_population = 0
            age_groups = {"0-14": 0, "15-64": 0, "65+": 0}
            
            for value in values:
                if value.get("$"):
                    try:
                        pop = int(value["$"])
                        total_population += pop
                        
                        # 年齢区分の判定（簡易版）
                        cat = value.get("@cat01", "")
                        if "年少" in cat or "0-14" in cat:
                            age_groups["0-14"] += pop
                        elif "生産" in cat or "15-64" in cat:
                            age_groups["15-64"] += pop
                        elif "老年" in cat or "65" in cat:
                            age_groups["65+"] += pop
                    except ValueError:
                        pass
            
            # パーセンテージ計算
            if total_population > 0:
                for key in age_groups:
                    age_groups[key] = round(age_groups[key] / total_population * 100, 1)
            
            return {
                "total_population": total_population,
                "age_distribution": age_groups,
                "source": "e-Stat API（リアルタイム）"
            }
            
        except Exception as e:
            logger.error(f"人口データパースエラー: {e}")
            return {}
    
    def _parse_facility_response(self, data: Dict) -> Dict:
        """医療施設データのレスポンスをパース"""
        try:
            values = data.get("GET_STATS_DATA", {}).get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
            
            total_facilities = 0
            hospitals = 0
            clinics = 0
            
            for value in values:
                if value.get("$"):
                    try:
                        count = int(value["$"])
                        cat = value.get("@cat01", "")
                        
                        if "病院" in cat:
                            hospitals += count
                        elif "診療所" in cat or "クリニック" in cat:
                            clinics += count
                        
                        total_facilities += count
                    except ValueError:
                        pass
            
            # 人口1万人あたりを計算（仮の人口を使用）
            per_10000 = round(total_facilities / 10000 * 10, 1) if total_facilities > 0 else 0
            
            return {
                "total": total_facilities,
                "hospitals": hospitals,
                "clinics": clinics,
                "per_10000": per_10000,
                "source": "e-Stat API（リアルタイム）"
            }
            
        except Exception as e:
            logger.error(f"医療施設データパースエラー: {e}")
            return {}
    
    def _parse_patient_response(self, data: Dict) -> Dict:
        """患者データのレスポンスをパース"""
        try:
            values = data.get("GET_STATS_DATA", {}).get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
            
            total_patients = 0
            disease_types = {}
            
            for value in values:
                if value.get("$"):
                    try:
                        count = int(value["$"])
                        cat = value.get("@cat01", "")
                        
                        total_patients += count
                        
                        # 疾病分類（簡易版）
                        if "循環器" in cat or "心疾患" in cat:
                            disease_types["生活習慣病"] = disease_types.get("生活習慣病", 0) + count
                        elif "呼吸器" in cat:
                            disease_types["呼吸器疾患"] = disease_types.get("呼吸器疾患", 0) + count
                        elif "消化器" in cat:
                            disease_types["消化器疾患"] = disease_types.get("消化器疾患", 0) + count
                        elif "精神" in cat:
                            disease_types["精神疾患"] = disease_types.get("精神疾患", 0) + count
                        elif "筋骨格" in cat or "整形" in cat:
                            disease_types["整形外科疾患"] = disease_types.get("整形外科疾患", 0) + count
                            
                    except ValueError:
                        pass
            
            return {
                "total_patients_per_day": total_patients,
                "disease_distribution": disease_types,
                "source": "e-Stat API（リアルタイム）"
            }
            
        except Exception as e:
            logger.error(f"患者データパースエラー: {e}")
            return {}
    
    def _calculate_medical_demand(self, population_data: Dict, patient_data: Dict) -> Dict:
        """医療需要を計算"""
        total_patients = patient_data.get("total_patients_per_day", 0)
        
        # デフォルト値
        if total_patients == 0:
            total_pop = population_data.get("total_population", 100000)
            age_dist = population_data.get("age_distribution", {})
            senior_rate = age_dist.get("65+", 25)
            
            # 推定患者数（人口の3-5%）
            base_rate = 0.03
            senior_adjustment = senior_rate / 100 * 0.02
            total_patients = int(total_pop * (base_rate + senior_adjustment))
        
        # 疾病分布
        disease_dist = patient_data.get("disease_distribution", {})
        if not disease_dist:
            # デフォルト分布
            disease_dist = {
                "生活習慣病": 35,
                "呼吸器疾患": 15,
                "消化器疾患": 20,
                "精神疾患": 10,
                "整形外科疾患": 15,
                "皮膚科疾患": 5
            }
        else:
            # パーセンテージに変換
            total = sum(disease_dist.values())
            if total > 0:
                disease_dist = {k: round(v/total*100, 1) for k, v in disease_dist.items()}
        
        return {
            "estimated_patients_per_day": total_patients,
            "disease_prevalence": disease_dist,
            "healthcare_accessibility": "high",
            "avg_waiting_time_minutes": 30
        }
    
    def _calculate_competition_density(self, demographics: Dict, facilities: Dict) -> Dict:
        """競争密度を計算"""
        total_facilities = facilities.get("total", 0)
        per_10000 = facilities.get("per_10000", 5.0)
        
        # 競争レベル判定
        if per_10000 > 10:
            level = "very_high"
        elif per_10000 > 7:
            level = "high"
        elif per_10000 > 5:
            level = "medium"
        elif per_10000 > 3:
            level = "low"
        else:
            level = "very_low"
        
        return {
            "total_medical_facilities": total_facilities,
            "clinics": facilities.get("clinics", int(total_facilities * 0.95)),
            "hospitals": facilities.get("hospitals", int(total_facilities * 0.05)),
            "clinics_per_10000": round(per_10000 * 0.95, 1),
            "hospitals_per_10000": round(per_10000 * 0.05, 1),
            "competition_level": level,
            "population": demographics.get("total_population", 0)
        }
    
    def _get_fallback_data(self, address: str) -> Dict:
        """APIが使えない場合のフォールバックデータ"""
        # 既存のJSONデータから取得する処理
        try:
            from .regional_json_service import RegionalJsonService
            json_service = RegionalJsonService()
            return json_service.get_regional_data(address)
        except:
            # 最終的なデフォルト値
            return {
                "demographics": {
                    "total_population": 100000,
                    "age_distribution": {"0-14": 12, "15-64": 63, "65+": 25},
                    "source": "推定値"
                },
                "medical_facilities": {
                    "total": 50,
                    "per_10000": 5.0,
                    "source": "推定値"
                },
                "medical_demand": {
                    "estimated_patients_per_day": 3500,
                    "disease_prevalence": {
                        "生活習慣病": 40,
                        "呼吸器疾患": 15,
                        "消化器疾患": 20,
                        "精神疾患": 10,
                        "整形外科疾患": 10,
                        "皮膚科疾患": 5
                    },
                    "healthcare_accessibility": "medium"
                },
                "competition_density": {
                    "total_medical_facilities": 50,
                    "competition_level": "medium"
                }
            }