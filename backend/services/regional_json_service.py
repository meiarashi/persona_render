#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
地域JSONデータサービス
全国の地域データをJSONファイルから高速に取得
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class RegionalJsonService:
    """地域JSONデータを管理・検索するサービス"""
    
    def __init__(self):
        """初期化"""
        self.data = None
        self.prefecture_mapping = {}
        self.city_mapping = {}
        self.ward_mapping = {}
        self._load_data()
    
    def _load_data(self):
        """統合マスターJSONデータをロード"""
        try:
            json_path = Path(__file__).parent.parent / "data" / "japan_regional_master.json"
            if not json_path.exists():
                logger.error(f"マスターデータファイルが見つかりません: {json_path}")
                self.data = {"regions": {}, "medical_demand_patterns": {}}
                return
            
            with open(json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # マッピングテーブルを構築
            self._build_mappings()
            
            stats = self.data.get("statistics", {})
            logger.info(f"マスターデータをロードしました: {stats.get('total_prefectures', 0)}都道府県, {stats.get('total_cities', 0)}市区町村")
            
        except Exception as e:
            logger.error(f"地域データのロードに失敗: {e}")
            self.data = {"regions": {}, "medical_demand_patterns": {}}
    
    def _build_mappings(self):
        """高速検索用のマッピングテーブルを構築"""
        for pref_code, pref_data in self.data.get("regions", {}).items():
            pref_name = pref_data.get("name", "")
            
            # 都道府県マッピング
            self.prefecture_mapping[pref_name] = pref_code
            # 「都」「道」「府」「県」を除いた名前でもマッピング
            short_name = re.sub(r'(都|道|府|県)$', '', pref_name)
            if short_name != pref_name:
                self.prefecture_mapping[short_name] = pref_code
            
            # 市区町村マッピング
            for city_code, city_data in pref_data.get("major_cities", {}).items():
                city_name = city_data.get("name", "")
                self.city_mapping[city_name] = (pref_code, city_code)
                # 市区町村を除いた名前でもマッピング
                short_city = re.sub(r'(市|区|町|村)$', '', city_name)
                if short_city != city_name:
                    self.city_mapping[short_city] = (pref_code, city_code)
                
                # 区マッピング（政令指定都市）
                for ward_code, ward_data in city_data.get("wards", {}).items():
                    ward_name = ward_data.get("name", "")
                    self.ward_mapping[ward_name] = (pref_code, city_code, ward_code)
    
    def parse_address(self, address: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        住所から都道府県、市区町村、区を抽出
        
        Returns:
            (prefecture_code, city_code, ward_code)
        """
        if not address:
            return (None, None, None)
        
        # 全角・半角スペースを統一
        address = address.replace('　', ' ').strip()
        
        pref_code = None
        city_code = None
        ward_code = None
        
        # 都道府県を検索
        for pref_name, code in self.prefecture_mapping.items():
            if pref_name in address:
                pref_code = code
                # 都道府県名以降の部分を取得
                remaining = address[address.index(pref_name) + len(pref_name):]
                break
        else:
            # 都道府県が見つからない場合
            remaining = address
        
        # 東京23区の特別処理
        tokyo_wards = {
            "千代田区": "13101", "中央区": "13102", "港区": "13103",
            "新宿区": "13104", "文京区": "13105", "台東区": "13106",
            "墨田区": "13107", "江東区": "13108", "品川区": "13109",
            "目黒区": "13110", "大田区": "13111", "世田谷区": "13112",
            "渋谷区": "13113", "中野区": "13114", "杉並区": "13115",
            "豊島区": "13116", "北区": "13117", "荒川区": "13118",
            "板橋区": "13119", "練馬区": "13120", "足立区": "13121",
            "葛飾区": "13122", "江戸川区": "13123"
        }
        
        # 東京23区をチェック
        for ward_name, ward_code_tmp in tokyo_wards.items():
            if ward_name in address:
                # 東京23区の場合は特別扱い
                return ("13", None, ward_code_tmp)
        
        if not pref_code:
            # 市区町村から推測
            for city_name, codes in self.city_mapping.items():
                if city_name in address:
                    return (codes[0], codes[1], None)
            
            # デフォルトは東京都
            pref_code = "13"
            remaining = address
        
        # 市区町村を検索
        if pref_code and remaining:
            pref_data = self.data.get("prefectures", {}).get(pref_code, {})
            
            # 区を先に検索（政令指定都市の場合）
            for city_code_tmp, city_data in pref_data.get("major_cities", {}).items():
                for ward_code_tmp, ward_data in city_data.get("wards", {}).items():
                    ward_name = ward_data.get("name", "")
                    if ward_name in remaining:
                        return (pref_code, city_code_tmp, ward_code_tmp)
            
            # 市を検索
            for city_code_tmp, city_data in pref_data.get("major_cities", {}).items():
                city_name = city_data.get("name", "")
                if city_name in remaining:
                    return (pref_code, city_code_tmp, None)
        
        return (pref_code, city_code, ward_code)
    
    def get_regional_data(self, address: str) -> Dict[str, Any]:
        """
        住所から地域データを取得
        
        Args:
            address: 検索する住所
            
        Returns:
            地域データ（人口統計、医療施設数など）
        """
        pref_code, city_code, ward_code = self.parse_address(address)
        
        if not pref_code:
            # デフォルトは東京都
            pref_code = "13"
        
        result = {
            "demographics": {},
            "medical_facilities": {},
            "medical_demand": {},
            "area_info": {}
        }
        
        # 都道府県データ
        pref_data = self.data.get("regions", {}).get(pref_code, {})
        if pref_data:
            result["area_info"]["prefecture"] = pref_data.get("name", "不明")
            result["area_info"]["prefecture_code"] = pref_data.get("code", pref_code + "000")
            
            # 東京23区の特別処理
            if pref_code == "13" and ward_code and not city_code:
                # 東京23区のデータ
                tokyo_23_wards = {
                    "13101": {"name": "千代田区", "population": 67742, "type": "urban_high_density"},
                    "13102": {"name": "中央区", "population": 173525, "type": "urban_high_density"},
                    "13103": {"name": "港区", "population": 265191, "type": "urban_high_density"},
                    "13104": {"name": "新宿区", "population": 351711, "type": "urban_high_density"},
                    "13105": {"name": "文京区", "population": 245062, "type": "urban_high_density"},
                    "13106": {"name": "台東区", "population": 217412, "type": "urban_high_density"},
                    "13107": {"name": "墨田区", "population": 281551, "type": "urban_high_density"},
                    "13108": {"name": "江東区", "population": 530034, "type": "urban_high_density"},
                    "13109": {"name": "品川区", "population": 426589, "type": "urban_high_density"},
                    "13110": {"name": "目黒区", "population": 286016, "type": "urban_high_density"},
                    "13111": {"name": "大田区", "population": 740444, "type": "urban_high_density"},
                    "13112": {"name": "世田谷区", "population": 942638, "type": "urban_high_density"},
                    "13113": {"name": "渋谷区", "population": 247820, "type": "urban_high_density"},
                    "13114": {"name": "中野区", "population": 347937, "type": "urban_high_density"},
                    "13115": {"name": "杉並区", "population": 593853, "type": "urban_high_density"},
                    "13116": {"name": "豊島区", "population": 302197, "type": "urban_high_density"},
                    "13117": {"name": "北区", "population": 358402, "type": "urban_high_density"},
                    "13118": {"name": "荒川区", "population": 220470, "type": "urban_high_density"},
                    "13119": {"name": "板橋区", "population": 588264, "type": "urban_high_density"},
                    "13120": {"name": "練馬区", "population": 756134, "type": "urban_high_density"},
                    "13121": {"name": "足立区", "population": 696339, "type": "urban_high_density"},
                    "13122": {"name": "葛飾区", "population": 453093, "type": "urban_high_density"},
                    "13123": {"name": "江戸川区", "population": 699825, "type": "urban_high_density"}
                }
                
                ward_data = tokyo_23_wards.get(ward_code, {})
                if ward_data:
                    result["area_info"]["ward"] = ward_data.get("name", "")
                    result["demographics"]["total_population"] = ward_data.get("population", 200000)
                    result["demographics"]["age_distribution"] = {
                        "0-14": 11.5,
                        "15-64": 64.5,
                        "65+": 24.0
                    }
                    result["medical_facilities"]["total"] = int(ward_data.get("population", 200000) / 1000 * 1.2)
                    result["medical_facilities"]["per_10000"] = 12.0
                    result["area_info"]["type"] = ward_data.get("type", "urban_high_density")
            
            # 区データがある場合（政令指定都市）
            elif ward_code and city_code:
                city_data = pref_data.get("major_cities", {}).get(city_code, {})
                ward_data = city_data.get("wards", {}).get(ward_code, {})
                
                if ward_data:
                    result["area_info"]["ward"] = ward_data.get("name", "")
                    result["demographics"]["total_population"] = ward_data.get("population", 
                        city_data.get("population", pref_data.get("population", 0)))
                else:
                    result["demographics"]["total_population"] = city_data.get("population", 
                        pref_data.get("population", 0))
                
                # 市区町村の年齢分布と医療施設データを使用
                result["demographics"]["age_distribution"] = city_data.get("age_distribution", 
                    pref_data.get("age_distribution", {}))
                result["medical_facilities"]["total"] = city_data.get("medical_facilities", 
                    pref_data.get("medical_facilities", 0))
                result["medical_facilities"]["per_10000"] = city_data.get("facilities_per_10000", 
                    pref_data.get("facilities_per_10000", 0))
                
                result["area_info"]["city"] = city_data.get("name", "")
                result["area_info"]["type"] = "urban_high_density"
                
            # 市データがある場合
            elif city_code:
                city_data = pref_data.get("major_cities", {}).get(city_code, {})
                
                result["demographics"]["total_population"] = city_data.get("population", 
                    pref_data.get("population", 0))
                result["demographics"]["age_distribution"] = city_data.get("age_distribution", 
                    pref_data.get("age_distribution", {}))
                result["medical_facilities"]["total"] = city_data.get("medical_facilities", 
                    pref_data.get("medical_facilities", 0))
                result["medical_facilities"]["per_10000"] = city_data.get("facilities_per_10000", 
                    pref_data.get("facilities_per_10000", 0))
                
                result["area_info"]["city"] = city_data.get("name", "")
                
                # 人口から地域タイプを推定
                pop = city_data.get("population", 0)
                if pop > 500000:
                    result["area_info"]["type"] = "urban_high_density"
                elif pop > 200000:
                    result["area_info"]["type"] = "urban_medium_density"
                elif pop > 50000:
                    result["area_info"]["type"] = "suburban"
                else:
                    result["area_info"]["type"] = "rural"
            
            # 都道府県データのみ
            else:
                result["demographics"]["total_population"] = pref_data.get("population", 0)
                result["demographics"]["age_distribution"] = pref_data.get("age_distribution", {})
                result["medical_facilities"]["total"] = pref_data.get("medical_facilities", 0)
                result["medical_facilities"]["per_10000"] = pref_data.get("facilities_per_10000", 0)
                
                # 都道府県の場合は郊外として扱う
                result["area_info"]["type"] = "suburban"
        
        # 医療需要パターンを追加
        area_type = result["area_info"].get("type", "suburban")
        demand_patterns = self.data.get("medical_demand_patterns", {}).get(area_type, {})
        
        result["medical_demand"] = {
            "estimated_patients_per_day": demand_patterns.get("estimated_patients_per_day", 1000),
            "disease_prevalence": demand_patterns.get("disease_prevalence", {}),
            "healthcare_accessibility": demand_patterns.get("healthcare_accessibility", "medium"),
            "avg_waiting_time_minutes": demand_patterns.get("avg_waiting_time_minutes", 30)
        }
        
        # データソースを追加
        result["demographics"]["source"] = "地域統計データベース（2024年推計）"
        result["demographics"]["area_code"] = result["area_info"].get("prefecture_code", "13000")
        
        return result
    
    def get_competition_density(self, address: str) -> Dict[str, Any]:
        """
        地域の競争密度データを取得
        
        Args:
            address: 検索する住所
            
        Returns:
            競争密度データ
        """
        regional_data = self.get_regional_data(address)
        
        total_pop = regional_data.get("demographics", {}).get("total_population", 0)
        medical_facilities = regional_data.get("medical_facilities", {}).get("total", 0)
        per_10000 = regional_data.get("medical_facilities", {}).get("per_10000", 0)
        
        # 病院と診療所の推定配分（一般的な比率）
        hospitals = int(medical_facilities * 0.05)  # 病院は約5%
        clinics = medical_facilities - hospitals
        
        return {
            "total_medical_facilities": medical_facilities,
            "hospitals": hospitals,
            "clinics": clinics,
            "clinics_per_10000": round(per_10000 * 0.95, 1),
            "hospitals_per_10000": round(per_10000 * 0.05, 1),
            "population": total_pop,
            "competition_level": self._calculate_competition_level(per_10000)
        }
    
    def _calculate_competition_level(self, facilities_per_10000: float) -> str:
        """競争レベルを判定"""
        if facilities_per_10000 > 10:
            return "very_high"
        elif facilities_per_10000 > 7:
            return "high"
        elif facilities_per_10000 > 5:
            return "medium"
        elif facilities_per_10000 > 3:
            return "low"
        else:
            return "very_low"
    
    def get_all_prefectures(self) -> Dict[str, str]:
        """全都道府県のコードと名前を取得"""
        result = {}
        for code, data in self.data.get("prefectures", {}).items():
            result[code] = data.get("name", "")
        return result
    
    def get_prefecture_cities(self, prefecture_code: str) -> Dict[str, str]:
        """指定都道府県の主要都市を取得"""
        pref_data = self.data.get("prefectures", {}).get(prefecture_code, {})
        result = {}
        for code, data in pref_data.get("major_cities", {}).items():
            result[code] = data.get("name", "")
        return result