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

from services.rag_processor import init_rag_database, reload_csv_data, get_uploaded_rag_data

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("Usage: python manage_rag_data.py [init|reload|status]")
        print("  init   - Initialize database and load CSV data")
        print("  reload - Clear existing data and reload from CSV files")
        print("  status - Show current loaded data status")
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
        
    elif command == "status":
        print("Current RAG data status:")
        uploaded_data = get_uploaded_rag_data()
        
        if uploaded_data:
            print(f"\nTotal departments: {len(uploaded_data)}")
            print("\nDepartment details:")
            for data in uploaded_data:
                print(f"  - {data['specialty']}: {data['record_count']} records")
                print(f"    File: {data['filename']}")
                print(f"    Uploaded: {data['uploaded_at']}")
        else:
            print("No RAG data found in database.")
            
    else:
        print(f"Unknown command: {command}")
        print("Use: init, reload, or status")
        sys.exit(1)

if __name__ == "__main__":
    main()