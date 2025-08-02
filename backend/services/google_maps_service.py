import os
import logging
from typing import List, Dict, Optional, Any
import aiohttp
from urllib.parse import quote
from .rate_limiter import GlobalRateLimiter

logger = logging.getLogger(__name__)

class GoogleMapsService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_MAPS_API_KEY not found in environment variables")
        self.places_url = "https://maps.googleapis.com/maps/api/place"
        self.geocoding_url = "https://maps.googleapis.com/maps/api/geocode/json"
        # Google Maps APIのレート制限: 1分間に50リクエスト
        self.rate_limiter = GlobalRateLimiter.get_limiter("google_maps", max_calls=50, time_window=60)
        
    async def search_nearby_clinics(
        self,
        location: str,
        radius: int = 3000,
        department_types: Optional[List[str]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        指定された場所の近くの医療機関を検索
        
        Args:
            location: 中心地の住所または座標
            radius: 検索半径（メートル）
            department_types: 診療科タイプのリスト
            limit: 最大結果数
            
        Returns:
            検索結果を含む辞書
        """
        try:
            # 住所を座標に変換
            coordinates = await self._geocode_address(location)
            if not coordinates:
                return {"error": "住所を座標に変換できませんでした", "results": []}
            
            # Places API で近隣の医療機関を検索
            places_results = await self._search_places(
                coordinates,
                radius,
                department_types or ["医院", "クリニック", "病院"],
                limit
            )
            
            # 結果を整形
            formatted_results = []
            for place in places_results:
                formatted_place = await self._format_place_data(place)
                if formatted_place:
                    formatted_results.append(formatted_place)
            
            return {
                "center": coordinates,
                "radius": radius,
                "total_results": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            logger.error(f"Error searching nearby clinics: {str(e)}")
            return {"error": f"検索中にエラーが発生しました: {str(e)}", "results": []}
    
    async def _geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """住所を座標に変換"""
        try:
            # レート制限を適用
            await self.rate_limiter.acquire_with_wait()
            
            async with aiohttp.ClientSession() as session:
                params = {
                    "address": address,
                    "key": self.api_key,
                    "language": "ja"
                }
                
                async with session.get(self.geocoding_url, params=params) as response:
                    data = await response.json()
                    
                    if data.get("status") == "OK" and data.get("results"):
                        location = data["results"][0]["geometry"]["location"]
                        return {
                            "lat": location["lat"],
                            "lng": location["lng"]
                        }
                    else:
                        logger.warning(f"Geocoding failed for address: {address}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error geocoding address: {str(e)}")
            return None
    
    async def _search_places(
        self,
        location: Dict[str, float],
        radius: int,
        keywords: List[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Places API で医療機関を検索"""
        all_results = []
        
        try:
            async with aiohttp.ClientSession() as session:
                for keyword in keywords:
                    # レート制限を適用
                    await self.rate_limiter.acquire_with_wait()
                    
                    params = {
                        "location": f"{location['lat']},{location['lng']}",
                        "radius": radius,
                        "keyword": keyword,
                        "type": "hospital|doctor|health",
                        "key": self.api_key,
                        "language": "ja"
                    }
                    
                    url = f"{self.places_url}/nearbysearch/json"
                    async with session.get(url, params=params) as response:
                        data = await response.json()
                        
                        if data.get("status") == "OK":
                            results = data.get("results", [])
                            all_results.extend(results[:limit])
                        else:
                            logger.warning(f"Places search failed with status: {data.get('status')}")
                
                # 重複を除去
                unique_results = []
                seen_ids = set()
                for result in all_results:
                    place_id = result.get("place_id")
                    if place_id and place_id not in seen_ids:
                        seen_ids.add(place_id)
                        unique_results.append(result)
                
                return unique_results[:limit]
                
        except Exception as e:
            logger.error(f"Error searching places: {str(e)}")
            return []
    
    async def _format_place_data(self, place: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """場所データを整形"""
        try:
            # 詳細情報を取得
            details = await self._get_place_details(place.get("place_id"))
            
            return {
                "place_id": place.get("place_id"),
                "name": place.get("name"),
                "address": place.get("vicinity", ""),
                "formatted_address": details.get("formatted_address", ""),
                "phone_number": details.get("formatted_phone_number", ""),
                "website": details.get("website", ""),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total", 0),
                "business_status": place.get("business_status", ""),
                "types": place.get("types", []),
                "location": {
                    "lat": place.get("geometry", {}).get("location", {}).get("lat"),
                    "lng": place.get("geometry", {}).get("location", {}).get("lng")
                },
                "opening_hours": details.get("opening_hours", {}),
                "reviews": details.get("reviews", [])[:3]  # 最新の3件のレビュー
            }
            
        except Exception as e:
            logger.error(f"Error formatting place data: {str(e)}")
            return None
    
    async def _get_place_details(self, place_id: str) -> Dict[str, Any]:
        """場所の詳細情報を取得"""
        try:
            # レート制限を適用
            await self.rate_limiter.acquire_with_wait()
            
            async with aiohttp.ClientSession() as session:
                params = {
                    "place_id": place_id,
                    "fields": "formatted_address,formatted_phone_number,website,opening_hours,reviews",
                    "key": self.api_key,
                    "language": "ja"
                }
                
                url = f"{self.places_url}/details/json"
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data.get("status") == "OK":
                        return data.get("result", {})
                    else:
                        return {}
                        
        except Exception as e:
            logger.error(f"Error getting place details: {str(e)}")
            return {}
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        2点間の距離を計算（km）
        Haversine formula を使用
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # 地球の半径（km）
        
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c