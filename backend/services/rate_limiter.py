import time
import asyncio
from typing import Dict, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    レート制限を実装するクラス
    Token Bucket アルゴリズムを使用
    """
    def __init__(self, max_calls: int, time_window: int, burst_size: Optional[int] = None):
        """
        Args:
            max_calls: 時間窓内の最大呼び出し回数
            time_window: 時間窓（秒）
            burst_size: バーストサイズ（デフォルトはmax_callsと同じ）
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.burst_size = burst_size or max_calls
        self.calls = deque()
        self._lock = asyncio.Lock()
        
    async def acquire(self) -> bool:
        """
        レート制限をチェックし、呼び出しを記録
        
        Returns:
            True: 呼び出し可能
            False: レート制限に達している
        """
        async with self._lock:
            now = time.time()
            
            # 古いエントリを削除
            while self.calls and self.calls[0] <= now - self.time_window:
                self.calls.popleft()
            
            # レート制限チェック
            if len(self.calls) >= self.max_calls:
                # 次に呼び出し可能になるまでの時間を計算
                wait_time = self.time_window - (now - self.calls[0])
                logger.warning(f"Rate limit reached. Need to wait {wait_time:.2f} seconds")
                return False
            
            # 呼び出しを記録
            self.calls.append(now)
            return True
    
    async def acquire_with_wait(self):
        """
        レート制限に達している場合は待機してから実行
        """
        while not await self.acquire():
            # 最も古い呼び出しが時間窓から外れるまで待機
            async with self._lock:
                if self.calls:
                    now = time.time()
                    wait_time = self.time_window - (now - self.calls[0]) + 0.1
                    logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
                else:
                    await asyncio.sleep(1)
    
    def get_remaining_calls(self) -> int:
        """
        残りの呼び出し可能回数を取得
        """
        now = time.time()
        # 古いエントリを考慮
        valid_calls = [call for call in self.calls if call > now - self.time_window]
        return max(0, self.max_calls - len(valid_calls))


class GlobalRateLimiter:
    """
    アプリケーション全体で共有されるレート制限マネージャー
    """
    _instances: Dict[str, RateLimiter] = {}
    
    @classmethod
    def get_limiter(cls, name: str, max_calls: int = 50, time_window: int = 60) -> RateLimiter:
        """
        名前付きレート制限インスタンスを取得
        
        Args:
            name: レート制限の名前（例: "google_maps", "openai"）
            max_calls: 時間窓内の最大呼び出し回数
            time_window: 時間窓（秒）
        """
        if name not in cls._instances:
            cls._instances[name] = RateLimiter(max_calls, time_window)
        return cls._instances[name]