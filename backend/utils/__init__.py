# utils package
from .config_loader import config_loader, ConfigLoader
from .prompt_builder import prompt_builder, PromptBuilder
from .config_manager import config_manager, ConfigManager

# レート制限モジュールを条件付きでインポート
try:
    from .rate_limiter import (
        RateLimiter,
        competitive_analysis_limiter,
        persona_generation_limiter,
        general_api_limiter,
        check_rate_limit
    )
except ImportError:
    # レート制限モジュールが存在しない場合のダミー実装
    class RateLimiter:
        def __init__(self, max_requests=100, time_window=3600):
            pass
        def is_allowed(self, request, username=None):
            return True
        def get_remaining_requests(self, request, username=None):
            return 100
        def get_reset_time(self, request, username=None):
            return None
    
    competitive_analysis_limiter = RateLimiter()
    persona_generation_limiter = RateLimiter()
    general_api_limiter = RateLimiter()
    
    def check_rate_limit(limiter, request, username=None):
        return {}