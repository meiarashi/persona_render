"""
e-Stat API サービス
政府統計データの取得と解析
"""

import os
import aiohttp
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class EStatService:
    """e-Stat APIを使用した統計データ取得サービス"""
    
    # 医療・健康関連の統計コード
    STATS_CODES = {
        "人口推計": "00200524",  # 人口推計
        "国勢調査": "00200521",  # 国勢調査
        "人口動態調査": "00450011",  # 人口動態調査
        "患者調査": "00450022",  # 患者調査
        "医療施設調査": "00450021",  # 医療施設調査
        "受療行動調査": "00450024",  # 受療行動調査
        "医師歯科医師薬剤師調査": "00450026",  # 医師・歯科医師・薬剤師調査
        "国民生活基礎調査": "00450061",  # 国民生活基礎調査（健康）
    }
    
    # 都道府県コード
    PREFECTURE_CODES = {
        "北海道": "01000", "青森県": "02000", "岩手県": "03000", "宮城県": "04000",
        "秋田県": "05000", "山形県": "06000", "福島県": "07000", "茨城県": "08000",
        "栃木県": "09000", "群馬県": "10000", "埼玉県": "11000", "千葉県": "12000",
        "東京都": "13000", "神奈川県": "14000", "新潟県": "15000", "富山県": "16000",
        "石川県": "17000", "福井県": "18000", "山梨県": "19000", "長野県": "20000",
        "岐阜県": "21000", "静岡県": "22000", "愛知県": "23000", "三重県": "24000",
        "滋賀県": "25000", "京都府": "26000", "大阪府": "27000", "兵庫県": "28000",
        "奈良県": "29000", "和歌山県": "30000", "鳥取県": "31000", "島根県": "32000",
        "岡山県": "33000", "広島県": "34000", "山口県": "35000", "徳島県": "36000",
        "香川県": "37000", "愛媛県": "38000", "高知県": "39000", "福岡県": "40000",
        "佐賀県": "41000", "長崎県": "42000", "熊本県": "43000", "大分県": "44000",
        "宮崎県": "45000", "鹿児島県": "46000", "沖縄県": "47000"
    }
    
    # 主要市区町村コード（拡張版）
    CITY_CODES = {
        # 東京23区
        "千代田区": "13101", "中央区": "13102", "港区": "13103", "新宿区": "13104",
        "文京区": "13105", "台東区": "13106", "墨田区": "13107", "江東区": "13108",
        "品川区": "13109", "目黒区": "13110", "大田区": "13111", "世田谷区": "13112",
        "渋谷区": "13113", "中野区": "13114", "杉並区": "13115", "豊島区": "13116",
        "北区": "13117", "荒川区": "13118", "板橋区": "13119", "練馬区": "13120",
        "足立区": "13121", "葛飾区": "13122", "江戸川区": "13123",
        # 政令指定都市
        "横浜市": "14100", "川崎市": "14130", "相模原市": "14150",
        "さいたま市": "11100", "千葉市": "12100", "名古屋市": "23100",
        "京都市": "26100", "大阪市": "27100", "堺市": "27140",
        "神戸市": "28100", "岡山市": "33100", "広島市": "34100",
        "北九州市": "40100", "福岡市": "40130", "熊本市": "43100",
        "札幌市": "01100", "仙台市": "04100", "新潟市": "15100",
        "静岡市": "22100", "浜松市": "22130"
    }
    
    def __init__(self):
        self.api_key = os.getenv("ESTAT_API_KEY")
        self.base_url = "http://api.e-stat.go.jp/rest/3.0/app/json"
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    def _get_area_code_from_address(self, address: str) -> Optional[str]:
        """住所から地域コードを取得（改善版）"""
        # 大阪市の区を先にチェック（東京の区と区別するため）
        osaka_wards = {
            "大阪市北区": "27127", "大阪市中央区": "27128", "大阪市西区": "27125",
            "大阪市浪速区": "27111", "大阪市淀川区": "27123", "大阪市東淀川区": "27122",
            "大阪市天王寺区": "27109", "大阪市阿倍野区": "27119", "大阪市住吉区": "27120"
        }
        
        for ward_name, code in osaka_wards.items():
            if ward_name in address or ward_name.replace("大阪市", "") in address and "大阪" in address:
                logger.info(f"Found Osaka ward: {ward_name} -> {code}")
                return code
        
        # 横浜市の区をチェック
        yokohama_wards = {
            "横浜市中区": "14104", "横浜市西区": "14103", "横浜市南区": "14105",
            "横浜市港北区": "14109", "横浜市青葉区": "14117", "横浜市都筑区": "14118"
        }
        
        for ward_name, code in yokohama_wards.items():
            if ward_name in address or ward_name.replace("横浜市", "") in address and "横浜" in address:
                logger.info(f"Found Yokohama ward: {ward_name} -> {code}")
                return code
        
        # 名古屋市の区をチェック
        nagoya_wards = {
            "名古屋市中区": "23106", "名古屋市東区": "23103", "名古屋市北区": "23104",
            "名古屋市西区": "23105", "名古屋市中村区": "23107", "名古屋市昭和区": "23109"
        }
        
        for ward_name, code in nagoya_wards.items():
            if ward_name in address or ward_name.replace("名古屋市", "") in address and "名古屋" in address:
                logger.info(f"Found Nagoya ward: {ward_name} -> {code}")
                return code
        
        # 東京23区と他の市区町村をチェック
        for city_name, code in self.CITY_CODES.items():
            if city_name in address:
                logger.info(f"Found city code: {city_name} -> {code}")
                return code
        
        # 次に都道府県をチェック
        for pref_name, code in self.PREFECTURE_CODES.items():
            if pref_name in address:
                logger.info(f"Found prefecture code: {pref_name} -> {code}")
                return code
        
        # デフォルトは東京都
        logger.info("Using default area code for Tokyo")
        return "13000"
    
    async def get_stats_list(self, stats_code: str) -> List[Dict]:
        """統計表リストを取得"""
        if not self.api_key:
            logger.warning("e-Stat API key not configured")
            return []
        
        try:
            url = f"{self.base_url}/getStatsList"
            params = {
                "appId": self.api_key,
                "statsCode": stats_code,
                "limit": 100
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "GET_STATS_LIST" in data:
                            stats_list = data["GET_STATS_LIST"]
                            if "DATALIST_INF" in stats_list:
                                table_info = stats_list["DATALIST_INF"].get("TABLE_INF", [])
                                if not isinstance(table_info, list):
                                    table_info = [table_info]
                                return table_info
                    else:
                        logger.error(f"e-Stat API error: status {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting stats list: {e}")
            
        return []
    
    async def get_meta_info(self, stats_data_id: str) -> Dict:
        """統計データのメタ情報を取得"""
        if not self.api_key:
            return {}
        
        try:
            url = f"{self.base_url}/getMetaInfo"
            params = {
                "appId": self.api_key,
                "statsDataId": stats_data_id
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "GET_META_INFO" in data:
                            return data["GET_META_INFO"]["METADATA_INF"]
                            
        except Exception as e:
            logger.error(f"Error getting meta info: {e}")
            
        return {}
    
    async def get_stats_data(self, stats_data_id: str, area_code: Optional[str] = None,
                            category_code: Optional[str] = None) -> Dict:
        """統計データを取得"""
        if not self.api_key:
            return {}
        
        try:
            url = f"{self.base_url}/getStatsData"
            params = {
                "appId": self.api_key,
                "statsDataId": stats_data_id,
                "limit": 500
            }
            
            if area_code:
                params["cdArea"] = area_code
            if category_code:
                params["cdCat01"] = category_code
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_stats_data(data)
                    else:
                        logger.error(f"e-Stat API error: status {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting stats data: {e}")
            
        return {}
    
    def _parse_stats_data(self, data: Dict) -> Dict:
        """統計データをパース"""
        parsed_data = {
            "values": [],
            "metadata": {}
        }
        
        try:
            if "GET_STATS_DATA" in data:
                stats_data = data["GET_STATS_DATA"]
                
                # メタデータ
                if "STATISTICAL_DATA" in stats_data:
                    stat_data = stats_data["STATISTICAL_DATA"]
                    
                    # データ値
                    if "DATA_INF" in stat_data:
                        values = stat_data["DATA_INF"].get("VALUE", [])
                        if not isinstance(values, list):
                            values = [values]
                        
                        for value in values:
                            if isinstance(value, dict):
                                parsed_data["values"].append({
                                    "value": value.get("$", 0),
                                    "unit": value.get("@unit", ""),
                                    "time": value.get("@time", ""),
                                    "area": value.get("@area", ""),
                                    "cat": value.get("@cat01", "")
                                })
                    
                    # テーブル情報
                    if "TABLE_INF" in stat_data:
                        table_inf = stat_data["TABLE_INF"]
                        parsed_data["metadata"]["title"] = table_inf.get("TITLE", "")
                        parsed_data["metadata"]["survey_date"] = table_inf.get("SURVEY_DATE", "")
                        
        except Exception as e:
            logger.error(f"Error parsing stats data: {e}")
            
        return parsed_data
    
    async def get_population_data(self, address: str) -> Dict:
        """人口統計データを取得（改善版）"""
        area_code = self._get_area_code_from_address(address)
        
        if not self.api_key:
            logger.info("e-Stat API key not configured, using estimated data")
            return self._get_estimated_population(area_code)
        
        try:
            # 人口推計の統計表IDを使用（最新のものを取得）
            stats_list = await self.get_stats_list(self.STATS_CODES["人口推計"])
            
            if stats_list:
                # 最新の統計表を選択
                latest_table = stats_list[0] if stats_list else None
                if latest_table:
                    stats_data_id = latest_table.get("@id", "")
                    
                    # 統計データを取得
                    data = await self.get_stats_data(stats_data_id, area_code)
                    
                    if data.get("values"):
                        return self._format_population_data(data, area_code)
            
            # データが取得できない場合は推定値を使用
            return self._get_estimated_population(area_code)
            
        except Exception as e:
            logger.error(f"Error getting population data: {e}")
            return self._get_estimated_population(area_code)
    
    def _format_population_data(self, data: Dict, area_code: str) -> Dict:
        """人口データをフォーマット"""
        try:
            total_population = 0
            age_distribution = {}
            
            for value in data.get("values", []):
                pop_value = int(float(value.get("value", 0)))
                total_population += pop_value
            
            return {
                "total_population": total_population if total_population > 0 else "データ取得中",
                "age_distribution": {
                    "0-14": "データ処理中",
                    "15-64": "データ処理中",
                    "65+": "データ処理中"
                },
                "area_code": area_code,
                "source": "e-Stat API",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error formatting population data: {e}")
            return self._get_estimated_population(area_code)
    
    def _get_estimated_population(self, area_code: str) -> Dict:
        """推定人口データを返す（フォールバック）"""
        # 地域別の推定データ（拡張版）
        estimated_data = {
            # 東京23区
            "13113": {"total": 243000, "0-14": 10.8, "15-64": 67.9, "65+": 21.3},  # 渋谷区
            "13104": {"total": 348000, "0-14": 9.9, "15-64": 67.3, "65+": 22.8},   # 新宿区
            "13103": {"total": 260000, "0-14": 12.1, "15-64": 69.2, "65+": 18.7},  # 港区
            "13101": {"total": 66000, "0-14": 11.5, "15-64": 68.8, "65+": 19.7},   # 千代田区
            "13112": {"total": 940000, "0-14": 11.2, "15-64": 66.5, "65+": 22.3},  # 世田谷区
            
            # 横浜市の区
            "14104": {"total": 150000, "0-14": 10.5, "15-64": 64.2, "65+": 25.3},  # 横浜市中区
            "14100": {"total": 3750000, "0-14": 11.8, "15-64": 63.4, "65+": 24.8}, # 横浜市全体
            
            # 大阪市の区
            "27127": {"total": 135000, "0-14": 9.8, "15-64": 68.5, "65+": 21.7},   # 大阪市北区
            "27128": {"total": 100000, "0-14": 8.5, "15-64": 70.2, "65+": 21.3},   # 大阪市中央区
            "27100": {"total": 2740000, "0-14": 10.7, "15-64": 63.9, "65+": 25.4}, # 大阪市全体
            
            # 名古屋市の区
            "23106": {"total": 90000, "0-14": 9.2, "15-64": 67.8, "65+": 23.0},    # 名古屋市中区
            "23100": {"total": 2330000, "0-14": 12.1, "15-64": 63.6, "65+": 24.3}, # 名古屋市全体
            
            # その他主要都市
            "40130": {"total": 1620000, "0-14": 12.9, "15-64": 64.8, "65+": 22.3}, # 福岡市
            "01100": {"total": 1970000, "0-14": 10.2, "15-64": 63.1, "65+": 26.7}, # 札幌市
            
            # 都道府県
            "13000": {"total": 14000000, "0-14": 11.0, "15-64": 65.0, "65+": 24.0}, # 東京都
            "27000": {"total": 8800000, "0-14": 11.2, "15-64": 62.8, "65+": 26.0},  # 大阪府
            "14000": {"total": 9200000, "0-14": 11.8, "15-64": 62.9, "65+": 25.3},  # 神奈川県
            "23000": {"total": 7500000, "0-14": 12.5, "15-64": 62.8, "65+": 24.7}   # 愛知県
        }
        
        data = estimated_data.get(area_code, estimated_data["13000"])
        
        return {
            "total_population": data["total"],
            "age_distribution": {
                "0-14": f"{data['0-14']}%",
                "15-64": f"{data['15-64']}%",
                "65+": f"{data['65+']}%"
            },
            "area_code": area_code,
            "source": "推定値",
            "note": "e-Stat APIキーを設定すると実際のデータを取得できます"
        }
    
    async def get_medical_facility_data(self, address: str) -> Dict:
        """医療施設データを取得"""
        area_code = self._get_area_code_from_address(address)
        
        if not self.api_key:
            return self._get_estimated_medical_data(area_code)
        
        try:
            # 医療施設調査の統計データを取得
            stats_list = await self.get_stats_list(self.STATS_CODES["医療施設調査"])
            
            if stats_list:
                latest_table = stats_list[0] if stats_list else None
                if latest_table:
                    stats_data_id = latest_table.get("@id", "")
                    data = await self.get_stats_data(stats_data_id, area_code)
                    
                    if data.get("values"):
                        return self._format_medical_data(data, area_code)
            
            return self._get_estimated_medical_data(area_code)
            
        except Exception as e:
            logger.error(f"Error getting medical facility data: {e}")
            return self._get_estimated_medical_data(area_code)
    
    def _format_medical_data(self, data: Dict, area_code: str) -> Dict:
        """医療施設データをフォーマット"""
        try:
            total_facilities = 0
            
            for value in data.get("values", []):
                facilities = int(float(value.get("value", 0)))
                total_facilities += facilities
            
            return {
                "total_medical_facilities": total_facilities,
                "facilities_per_10000": round(total_facilities / 1.0, 1),  # 仮の計算
                "area_code": area_code,
                "source": "e-Stat API",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error formatting medical data: {e}")
            return self._get_estimated_medical_data(area_code)
    
    def _get_estimated_medical_data(self, area_code: str) -> Dict:
        """推定医療施設データを返す（拡張版）"""
        estimated_data = {
            # 東京23区
            "13113": {"total": 450, "per_10000": 18.5},  # 渋谷区
            "13104": {"total": 520, "per_10000": 14.9},  # 新宿区
            "13103": {"total": 380, "per_10000": 14.6},  # 港区
            "13101": {"total": 150, "per_10000": 22.7},  # 千代田区
            "13112": {"total": 680, "per_10000": 7.2},   # 世田谷区
            
            # 横浜市の区
            "14104": {"total": 180, "per_10000": 12.0},  # 横浜市中区
            
            # 大阪市の区
            "27127": {"total": 250, "per_10000": 18.5},  # 大阪市北区
            "27128": {"total": 210, "per_10000": 21.0},  # 大阪市中央区
            
            # 名古屋市の区
            "23106": {"total": 190, "per_10000": 21.1},  # 名古屋市中区
            
            # デフォルト
            "default": {"total": "データ取得中", "per_10000": "データ取得中"}
        }
        
        data = estimated_data.get(area_code, estimated_data["default"])
        
        return {
            "total_medical_facilities": data["total"],
            "facilities_per_10000": data["per_10000"],
            "area_code": area_code,
            "source": "推定値",
            "note": "e-Stat APIキーを設定すると実際のデータを取得できます"
        }