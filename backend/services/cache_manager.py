"""
改善版インメモリキャッシュマネージャー
スレッドセーフティとメモリ管理を強化
"""
from functools import lru_cache
import json
from pathlib import Path
from typing import Dict, List, Optional
import time
import threading
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self):
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttls = {}  # 個別TTL管理
        self._lock = threading.RLock()  # 並行処理対応
        self._default_ttl = 3600  # デフォルト1時間
        self._max_size = 1000  # 最大キャッシュ数
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5分ごとにクリーンアップ
    
    def get(self, key: str) -> Optional[any]:
        """キャッシュからデータを取得（スレッドセーフ）"""
        with self._lock:
            # 定期クリーンアップ
            self._periodic_cleanup()
            
            if key in self._cache:
                ttl = self._cache_ttls.get(key, self._default_ttl)
                if time.time() - self._cache_timestamps.get(key, 0) < ttl:
                    # アクセス統計を更新（LRU実装用）
                    self._cache_timestamps[key] = time.time()
                    return self._cache[key]
                else:
                    # 期限切れのキャッシュを安全に削除
                    self._remove_expired_key(key)
            return None
    
    def set(self, key: str, value: any, ttl: Optional[int] = None) -> None:
        """キャッシュにデータを保存（個別TTL対応）"""
        with self._lock:
            # キャッシュサイズ制限チェック
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_lru()
            
            self._cache[key] = value
            self._cache_timestamps[key] = time.time()
            self._cache_ttls[key] = ttl if ttl is not None else self._default_ttl
    
    def _remove_expired_key(self, key: str) -> None:
        """期限切れキーの安全な削除"""
        self._cache.pop(key, None)
        self._cache_timestamps.pop(key, None)
        self._cache_ttls.pop(key, None)
    
    def _evict_lru(self) -> None:
        """LRU方式で最も古いキャッシュを削除"""
        if not self._cache_timestamps:
            return
        
        # 最も古いアクセスのキーを特定
        oldest_key = min(self._cache_timestamps, key=self._cache_timestamps.get)
        self._remove_expired_key(oldest_key)
    
    def _periodic_cleanup(self) -> None:
        """定期的なクリーンアップ"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        self._last_cleanup = current_time
        self.cleanup_expired()
    
    def cleanup_expired(self) -> None:
        """期限切れキャッシュの一括削除"""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in list(self._cache_timestamps.items()):
            ttl = self._cache_ttls.get(key, self._default_ttl)
            if current_time - timestamp >= ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_expired_key(key)
        
        if expired_keys:
            print(f"[Cache] Cleaned up {len(expired_keys)} expired entries")
    
    def clear(self) -> None:
        """キャッシュを完全クリア"""
        with self._lock:
            self._cache.clear()
            self._cache_timestamps.clear()
            self._cache_ttls.clear()
    
    def invalidate_pattern(self, pattern: str) -> None:
        """パターンに一致するキャッシュを無効化"""
        with self._lock:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                self._remove_expired_key(key)
    
    def get_stats(self) -> Dict:
        """キャッシュ統計情報を取得"""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "hit_rate": "N/A",  # 実装可能
                "oldest_entry": min(self._cache_timestamps.values()) if self._cache_timestamps else None,
                "newest_entry": max(self._cache_timestamps.values()) if self._cache_timestamps else None
            }

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
    if cached is not None:
        return cached
    
    # キャッシュになければロード
    try:
        data = load_chief_complaints_data()
        
        if category in data and department in data[category]:
            result = data[category][department]
            cache_manager.set(cache_key, result)
            return result
    except Exception as e:
        print(f"[Cache] Error loading chief complaints: {e}")
    
    return []

def get_all_chief_complaints() -> Dict[str, Dict[str, List[str]]]:
    """全主訴データを取得（起動時のプリロード用）"""
    try:
        return load_chief_complaints_data()
    except Exception as e:
        print(f"[Cache] Error loading all chief complaints: {e}")
        return {}

def preload_cache():
    """アプリケーション起動時にキャッシュをプリロード"""
    print("[Cache] Preloading chief complaints data...")
    try:
        chief_complaints = load_chief_complaints_data()
        departments = load_departments_data()
        
        # 全データをキャッシュに登録
        loaded_count = 0
        for category, dept_complaints in chief_complaints.items():
            for department, complaints in dept_complaints.items():
                cache_key = f"chief_complaints_{category}_{department}"
                cache_manager.set(cache_key, complaints)
                loaded_count += 1
        
        print(f"[Cache] Preloaded {loaded_count} items")
        return True
    except Exception as e:
        print(f"[Cache] Preload failed: {e}")
        return False

# バックグラウンドクリーンアップタスク（オプション）
def start_cleanup_task():
    """定期的なクリーンアップタスクを開始"""
    import threading
    
    def cleanup_worker():
        while True:
            time.sleep(300)  # 5分ごと
            cache_manager.cleanup_expired()
    
    thread = threading.Thread(target=cleanup_worker, daemon=True)
    thread.start()