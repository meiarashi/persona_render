"""
インメモリキャッシュマネージャー
主訴データなど頻繁にアクセスされるデータをメモリにキャッシュ
"""
from functools import lru_cache
import json
from pathlib import Path
from typing import Dict, List, Optional
import time

class CacheManager:
    def __init__(self):
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 3600  # 1時間のTTL
    
    def get(self, key: str) -> Optional[any]:
        """キャッシュからデータを取得"""
        if key in self._cache:
            # TTLチェック
            if time.time() - self._cache_timestamps.get(key, 0) < self._cache_ttl:
                return self._cache[key]
            else:
                # 期限切れのキャッシュを削除
                del self._cache[key]
                del self._cache_timestamps[key]
        return None
    
    def set(self, key: str, value: any, ttl: Optional[int] = None) -> None:
        """キャッシュにデータを保存"""
        self._cache[key] = value
        self._cache_timestamps[key] = time.time()
        if ttl:
            self._cache_ttl = ttl
    
    def clear(self) -> None:
        """キャッシュをクリア"""
        self._cache.clear()
        self._cache_timestamps.clear()

# グローバルキャッシュインスタンス
cache_manager = CacheManager()

@lru_cache(maxsize=1)
def load_chief_complaints_data() -> Dict[str, Dict[str, List[str]]]:
    """主訴データを一度だけ読み込んでメモリに保持"""
    config_path = Path(__file__).parent.parent.parent / "config" / "chief_complaints.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@lru_cache(maxsize=1)
def load_departments_data() -> Dict[str, List[Dict]]:
    """診療科データを一度だけ読み込んでメモリに保持"""
    config_path = Path(__file__).parent.parent.parent / "config" / "departments_by_category.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_chief_complaints(category: str, department: str) -> List[str]:
    """キャッシュから主訴リストを取得"""
    cache_key = f"chief_complaints_{category}_{department}"
    
    # キャッシュチェック
    cached = cache_manager.get(cache_key)
    if cached:
        return cached
    
    # キャッシュになければロード
    data = load_chief_complaints_data()
    
    if category in data and department in data[category]:
        result = data[category][department]
        cache_manager.set(cache_key, result)
        return result
    
    return []

def get_all_chief_complaints() -> Dict[str, Dict[str, List[str]]]:
    """全主訴データを取得（起動時のプリロード用）"""
    return load_chief_complaints_data()

def preload_cache():
    """アプリケーション起動時にキャッシュをプリロード"""
    print("[Cache] Preloading chief complaints data...")
    chief_complaints = load_chief_complaints_data()
    departments = load_departments_data()
    
    # 全データをキャッシュに登録
    for category, dept_complaints in chief_complaints.items():
        for department, complaints in dept_complaints.items():
            cache_key = f"chief_complaints_{category}_{department}"
            cache_manager.set(cache_key, complaints)
    
    print(f"[Cache] Preloaded {len(cache_manager._cache)} items")
    return True