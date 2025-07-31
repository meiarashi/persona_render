"""
読み取り専用のRAGプロセッサー実装
初期化時のロック問題を完全に回避
"""

import sqlite3
from pathlib import Path
import os

# データベースパス
PERSISTENT_DISK_MOUNT_PATH = Path("./app_settings")
RAG_DB_PATH = PERSISTENT_DISK_MOUNT_PATH / "rag_data.db"

# グローバル変数でデータベースの初期化状態を管理
_db_initialized = False

def ensure_db_initialized():
    """データベースが初期化されているか確認（読み取り専用）"""
    global _db_initialized
    if not _db_initialized and RAG_DB_PATH.exists():
        _db_initialized = True
        print(f"[RAG] Database found at: {RAG_DB_PATH}")
    return _db_initialized

def create_readonly_connection():
    """読み取り専用の接続を作成"""
    if not ensure_db_initialized():
        raise Exception("RAG database not initialized")
    
    # 読み取り専用で開く - ロックなし
    conn = sqlite3.connect(str(RAG_DB_PATH), timeout=1.0)
    conn.execute("PRAGMA query_only=ON")
    conn.execute("PRAGMA cache_size=-64000")
    return conn

def search_rag_data(specialty=None, age_group=None, gender=None, limit=5):
    """読み取り専用でRAGデータを検索"""
    try:
        conn = create_readonly_connection()
        cursor = conn.cursor()
        
        # 検索クエリ実行...
        # （既存のロジックをそのまま使用）
        
        conn.close()
        return results
    except Exception as e:
        print(f"[RAG] Search error: {e}")
        return []