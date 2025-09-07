"""
レート制限ユーティリティ
APIの乱用を防ぐためのレート制限機能
"""

import time
from collections import defaultdict, deque
from typing import Dict, Deque, Optional
import hashlib
from fastapi import HTTPException, Request

class RateLimiter:
    """
    トークンバケットアルゴリズムを使用したレート制限
    """
    
    def __init__(self, max_requests: int = 10, time_window: int = 3600):
        """
        Args:
            max_requests: 時間窓内の最大リクエスト数
            time_window: 時間窓の長さ（秒）
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_history: Dict[str, Deque[float]] = defaultdict(deque)
    
    def _get_client_id(self, request: Request, username: Optional[str] = None) -> str:
        """
        クライアントを識別するIDを生成
        """
        if username:
            return f"user:{username}"
        
        # IPアドレスベースの識別
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        # IPとUser-Agentの組み合わせでクライアントを識別
        identifier = f"{client_ip}:{user_agent}"
        return hashlib.md5(identifier.encode()).hexdigest()
    
    def is_allowed(self, request: Request, username: Optional[str] = None) -> bool:
        """
        リクエストが許可されるかチェック
        
        Returns:
            True if request is allowed, False otherwise
        """
        client_id = self._get_client_id(request, username)
        current_time = time.time()
        
        # 古いリクエスト履歴を削除
        history = self.request_history[client_id]
        while history and history[0] < current_time - self.time_window:
            history.popleft()
        
        # リクエスト数をチェック
        if len(history) >= self.max_requests:
            return False
        
        # リクエストを記録
        history.append(current_time)
        return True
    
    def get_remaining_requests(self, request: Request, username: Optional[str] = None) -> int:
        """
        残りリクエスト数を取得
        """
        client_id = self._get_client_id(request, username)
        current_time = time.time()
        
        history = self.request_history[client_id]
        while history and history[0] < current_time - self.time_window:
            history.popleft()
        
        return max(0, self.max_requests - len(history))
    
    def get_reset_time(self, request: Request, username: Optional[str] = None) -> Optional[float]:
        """
        レート制限がリセットされる時刻を取得
        """
        client_id = self._get_client_id(request, username)
        history = self.request_history[client_id]
        
        if not history:
            return None
        
        # 最も古いリクエストから時間窓分後がリセット時刻
        return history[0] + self.time_window


# 異なる用途向けのレート制限インスタンス
competitive_analysis_limiter = RateLimiter(max_requests=10, time_window=3600)  # 1時間に10回
persona_generation_limiter = RateLimiter(max_requests=20, time_window=3600)    # 1時間に20回
general_api_limiter = RateLimiter(max_requests=100, time_window=3600)         # 1時間に100回


def check_rate_limit(limiter: RateLimiter, request: Request, username: Optional[str] = None):
    """
    レート制限をチェックし、超過時は例外を発生させる
    """
    if not limiter.is_allowed(request, username):
        reset_time = limiter.get_reset_time(request, username)
        wait_seconds = int(reset_time - time.time()) if reset_time else 0
        
        raise HTTPException(
            status_code=429,
            detail=f"レート制限を超過しました。{wait_seconds}秒後に再試行してください。",
            headers={
                "X-RateLimit-Limit": str(limiter.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(reset_time)) if reset_time else "",
                "Retry-After": str(wait_seconds)
            }
        )
    
    # レート制限情報をヘッダーに追加
    remaining = limiter.get_remaining_requests(request, username)
    reset_time = limiter.get_reset_time(request, username)
    
    return {
        "X-RateLimit-Limit": str(limiter.max_requests),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(int(reset_time)) if reset_time else ""
    }