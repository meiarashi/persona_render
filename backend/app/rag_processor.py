import sqlite3
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json

# 永続ストレージのパス（既存設定と同じ場所）
PERSISTENT_DISK_MOUNT_PATH = Path(os.getenv("PERSISTENT_DISK_PATH", "/var/app_settings"))
RAG_DB_PATH = PERSISTENT_DISK_MOUNT_PATH / "rag_data.db"
UPLOADED_FILES_DIR = PERSISTENT_DISK_MOUNT_PATH / "uploaded_files"

def ensure_rag_directories():
    """RAG関連のディレクトリを確保"""
    try:
        PERSISTENT_DISK_MOUNT_PATH.mkdir(parents=True, exist_ok=True)
        UPLOADED_FILES_DIR.mkdir(parents=True, exist_ok=True)
        print(f"RAG directories ensured: {PERSISTENT_DISK_MOUNT_PATH}")
    except Exception as e:
        print(f"Error creating RAG directories: {e}")
        raise

def init_rag_database():
    """RAGデータベースの初期化"""
    ensure_rag_directories()
    
    try:
        conn = sqlite3.connect(RAG_DB_PATH)
        cursor = conn.cursor()
        
        # RAGデータテーブル作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rag_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                specialty TEXT NOT NULL,
                rank_order INTEGER,
                keyword TEXT NOT NULL,
                search_volume INTEGER,
                duplicate_volume INTEGER,
                distinctiveness REAL,
                time_difference REAL,
                male_ratio INTEGER,
                female_ratio INTEGER,
                age_10s INTEGER,
                age_20s INTEGER,
                age_30s INTEGER,
                age_40s INTEGER,
                age_50s INTEGER,
                age_60s INTEGER,
                age_70s INTEGER,
                category TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(specialty, keyword)
            )
        ''')
        
        # アップロード履歴テーブル作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS upload_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                specialty TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_size INTEGER,
                record_count INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"RAG database initialized at: {RAG_DB_PATH}")
        
    except Exception as e:
        print(f"Error initializing RAG database: {e}")
        raise

def save_rag_data(specialty: str, df: pd.DataFrame, original_filename: str) -> Dict:
    """RAGデータをデータベースに保存"""
    conn = None
    try:
        # データベース接続
        conn = sqlite3.connect(RAG_DB_PATH)
        cursor = conn.cursor()
        
        # トランザクション開始
        conn.execute("BEGIN TRANSACTION")
        
        # 既存データの削除（同じ診療科の古いデータを置換）
        cursor.execute("DELETE FROM rag_data WHERE specialty = ?", (specialty,))
        
        # 新しいデータの挿入
        inserted_count = 0
        skipped_count = 0
        
        for _, row in df.iterrows():
            try:
                # CSVの列名を予想されるものにマッピング
                data_to_insert = {
                    'specialty': specialty,
                    'rank_order': int(row.get('順位', 0)) if pd.notna(row.get('順位')) else None,
                    'keyword': str(row.get('出力キーワード', '')) if pd.notna(row.get('出力キーワード')) else '',
                    'search_volume': int(row.get('検索ボリューム(人)', 0)) if pd.notna(row.get('検索ボリューム(人)')) else 0,
                    'duplicate_volume': int(row.get('重複ボリューム(人)', 0)) if pd.notna(row.get('重複ボリューム(人)')) else 0,
                    'distinctiveness': float(row.get('特徴度', 0.0)) if pd.notna(row.get('特徴度')) else 0.0,
                    'time_difference': float(row.get('検索時間差(日)', 0.0)) if pd.notna(row.get('検索時間差(日)')) else 0.0,
                    'male_ratio': int(row.get('男性割合(%)', 0)) if pd.notna(row.get('男性割合(%)')) else 0,
                    'female_ratio': int(row.get('女性割合(%)', 0)) if pd.notna(row.get('女性割合(%)')) else 0,
                    'age_10s': int(row.get('10代（13歳〜）割合(%)', 0)) if pd.notna(row.get('10代（13歳〜）割合(%)')) else 0,
                    'age_20s': int(row.get('20代割合(%)', 0)) if pd.notna(row.get('20代割合(%)')) else 0,
                    'age_30s': int(row.get('30代割合(%)', 0)) if pd.notna(row.get('30代割合(%)')) else 0,
                    'age_40s': int(row.get('40代割合(%)', 0)) if pd.notna(row.get('40代割合(%)')) else 0,
                    'age_50s': int(row.get('50代割合(%)', 0)) if pd.notna(row.get('50代割合(%)')) else 0,
                    'age_60s': int(row.get('60代割合(%)', 0)) if pd.notna(row.get('60代割合(%)')) else 0,
                    'age_70s': int(row.get('70代以上割合(%)', 0)) if pd.notna(row.get('70代以上割合(%)')) else 0,
                    'category': str(row.get('カテゴリー', '')) if pd.notna(row.get('カテゴリー')) else ''
                }
                
                cursor.execute('''
                    INSERT INTO rag_data (
                        specialty, rank_order, keyword, search_volume, duplicate_volume,
                        distinctiveness, time_difference, male_ratio, female_ratio,
                        age_10s, age_20s, age_30s, age_40s, age_50s, age_60s, age_70s, category
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data_to_insert['specialty'], data_to_insert['rank_order'], 
                    data_to_insert['keyword'], data_to_insert['search_volume'],
                    data_to_insert['duplicate_volume'], data_to_insert['distinctiveness'],
                    data_to_insert['time_difference'], data_to_insert['male_ratio'],
                    data_to_insert['female_ratio'], data_to_insert['age_10s'],
                    data_to_insert['age_20s'], data_to_insert['age_30s'],
                    data_to_insert['age_40s'], data_to_insert['age_50s'],
                    data_to_insert['age_60s'], data_to_insert['age_70s'],
                    data_to_insert['category']
                ))
                inserted_count += 1
                
            except Exception as row_error:
                print(f"Error inserting row: {row_error}")
                skipped_count += 1
                continue
        
        # アップロード履歴を記録
        cursor.execute('''
            INSERT INTO upload_history (specialty, filename, file_size, record_count)
            VALUES (?, ?, ?, ?)
        ''', (specialty, original_filename, len(df) * 100, inserted_count))  # 概算ファイルサイズ
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "inserted_count": inserted_count,
            "skipped_count": skipped_count,
            "specialty": specialty
        }
        
    except Exception as e:
        print(f"Error saving RAG data: {e}")
        # ロールバック
        if conn:
            conn.rollback()
            conn.close()
        return {
            "success": False,
            "error": str(e)
        }

def get_uploaded_rag_data() -> List[Dict]:
    """アップロード済みのRAGデータ一覧を取得"""
    try:
        conn = sqlite3.connect(RAG_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                h.specialty,
                h.filename,
                h.record_count,
                h.uploaded_at,
                COUNT(r.id) as current_records
            FROM upload_history h
            LEFT JOIN rag_data r ON h.specialty = r.specialty
            GROUP BY h.specialty, h.filename, h.record_count, h.uploaded_at
            ORDER BY h.uploaded_at DESC
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "specialty": row[0],
                "filename": row[1],
                "record_count": row[2],
                "uploaded_at": row[3],
                "current_records": row[4]
            })
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error getting uploaded RAG data: {e}")
        return []

def search_rag_data(specialty: str, age_group: str = None, gender: str = None, limit: int = 10) -> List[Dict]:
    """RAGデータから関連キーワードを検索"""
    try:
        conn = sqlite3.connect(RAG_DB_PATH)
        cursor = conn.cursor()
        
        # 基本クエリ
        base_query = '''
            SELECT keyword, search_volume, male_ratio, female_ratio,
                   age_10s, age_20s, age_30s, age_40s, age_50s, age_60s, age_70s,
                   category, distinctiveness
            FROM rag_data 
            WHERE specialty = ?
        '''
        
        params = [specialty]
        
        # 年代フィルタリング（該当年代の割合が平均以上）
        if age_group:
            age_column_map = {
                "10s": "age_10s", "20s": "age_20s", "30s": "age_30s",
                "40s": "age_40s", "50s": "age_50s", "60s": "age_60s", "70s": "age_70s"
            }
            if age_group in age_column_map:
                base_query += f" AND {age_column_map[age_group]} > 15"  # 15%以上の割合
        
        # 性別フィルタリング
        if gender:
            if gender == "male":
                base_query += " AND male_ratio > female_ratio"
            elif gender == "female":
                base_query += " AND female_ratio > male_ratio"
        
        # 検索ボリュームと特徴度で並び替え
        base_query += " ORDER BY distinctiveness DESC, search_volume DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(base_query, params)
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "keyword": row[0],
                "search_volume": row[1],
                "male_ratio": row[2],
                "female_ratio": row[3],
                "age_demographics": {
                    "10s": row[4], "20s": row[5], "30s": row[6],
                    "40s": row[7], "50s": row[8], "60s": row[9], "70s": row[10]
                },
                "category": row[11],
                "distinctiveness": row[12]
            })
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error searching RAG data: {e}")
        return []

def delete_rag_data(specialty: str) -> bool:
    """指定した診療科のRAGデータを削除"""
    try:
        conn = sqlite3.connect(RAG_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM rag_data WHERE specialty = ?", (specialty,))
        cursor.execute("DELETE FROM upload_history WHERE specialty = ?", (specialty,))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error deleting RAG data: {e}")
        return False

# テスト用関数
if __name__ == "__main__":
    print("RAG Manager Test")
    init_rag_database()
    print("Database initialized successfully!")
