#!/usr/bin/env python3
"""
RAGデータ管理スクリプト
CSVファイルからRAGデータをロード・管理するためのユーティリティ
"""

import sys
import os
from pathlib import Path

# プロジェクトのルートディレクトリをPythonパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.rag_processor import init_rag_database, reload_csv_data

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("Usage: python manage_rag_data.py [init|reload]")
        print("  init   - Initialize database and load CSV data")
        print("  reload - Clear existing data and reload from CSV files")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "init":
        print("Initializing RAG database and loading CSV data...")
        init_rag_database()
        print("Done!")
        
    elif command == "reload":
        print("Reloading RAG data from CSV files...")
        reload_csv_data()
        print("Done!")
            
    else:
        print(f"Unknown command: {command}")
        print("Use: init or reload")
        sys.exit(1)

if __name__ == "__main__":
    main()