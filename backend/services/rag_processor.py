import sqlite3
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json
import glob
import platform

# 診療科の英語→日本語マッピング
DEPARTMENT_MAP = {
    "internal_medicine": "内科", "surgery": "外科", "pediatrics": "小児科",
    "orthopedics": "整形外科", "dermatology": "皮膚科", "ophthalmology": "眼科",
    "cardiology": "循環器内科", "psychiatry": "精神科", "dentistry": "歯科",
    "pediatric_dentistry": "小児歯科", "otorhinolaryngology": "耳鼻咽喉科",
    "ent": "耳鼻咽喉科", "gynecology": "婦人科", "urology": "泌尿器科",
    "neurosurgery": "脳神経外科", "general_dentistry": "一般歯科",
    "orthodontics": "矯正歯科", "cosmetic_dentistry": "審美歯科",
    "oral_surgery": "口腔外科", "anesthesiology": "麻酔科",
    "radiology": "放射線科", "rehabilitation": "リハビリテーション科",
    "allergy": "アレルギー科", "gastroenterology": "消化器内科",
    "respiratory_medicine": "呼吸器内科", "diabetes_medicine": "糖尿病内科",
    "nephrology": "腎臓内科", "neurology": "神経内科",
    "hematology": "血液内科", "plastic_surgery": "形成外科",
    "beauty_surgery": "美容外科", "endocrinology": "内分泌科"
}

# データベースパスの設定
# すべての環境でコードベースのapp_settingsディレクトリを使用
PERSISTENT_DISK_MOUNT_PATH = Path("./app_settings")
RAG_DB_PATH = PERSISTENT_DISK_MOUNT_PATH / "rag_data.db"

# 本番環境でもローカルDBを使用することを明示
print(f"[RAG] Using code-based database at: {RAG_DB_PATH}")

def ensure_rag_directories():
    """RAG関連のディレクトリを確保"""
    try:
        PERSISTENT_DISK_MOUNT_PATH.mkdir(parents=True, exist_ok=True)
        print(f"RAG directories ensured: {PERSISTENT_DISK_MOUNT_PATH}")
    except Exception as e:
        print(f"Error creating RAG directories: {e}")
        raise

def create_connection():
    """WALモードを有効にしたデータベース接続を作成"""
    conn = sqlite3.connect(str(RAG_DB_PATH), timeout=30.0)
    # WAL（Write-Ahead Logging）モードを有効化 - 読み書きの同時実行を可能にする
    conn.execute("PRAGMA journal_mode=WAL")
    # 同期モードをNORMALに設定（パフォーマンスと安全性のバランス）
    conn.execute("PRAGMA synchronous=NORMAL")
    # キャッシュサイズを増やす（パフォーマンス向上）
    conn.execute("PRAGMA cache_size=-64000")  # 64MB
    return conn

def init_rag_database():
    """RAGデータベースの初期化"""
    ensure_rag_directories()
    
    # 使用するデータベースパスを明示的にログ出力
    print("="*60)
    print(f"[RAG] Database Path: {RAG_DB_PATH}")
    print(f"[RAG] Using {'LOCAL' if 'app_settings' in str(RAG_DB_PATH) else 'RENDER'} database")
    print("="*60)
    
    try:
        conn = create_connection()
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
        
        # CSVファイルから自動的にデータをロード
        load_csv_data_from_directory()
        
    except Exception as e:
        print(f"Error initializing RAG database: {e}")
        raise

def _save_rag_data_internal(specialty: str, df: pd.DataFrame, original_filename: str) -> Dict:
    """内部使用のみ: CSVファイルからRAGデータをデータベースに保存"""
    conn = None
    try:
        # データベース接続
        conn = create_connection()
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
                    'category': ''  # カテゴリーカラムは存在しない場合は空文字
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

def search_rag_data(specialty: str, age_group: str = None, gender: str = None, limit: int = 10) -> List[Dict]:
    """RAGデータから関連キーワードを検索"""
    try:
        conn = create_connection()
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





def get_rag_context(department: str) -> str:
    """指定された診療科のRAGコンテキストを取得"""
    # 診療科名の正規化（英語名の場合は日本語に変換）
    department_ja = DEPARTMENT_MAP.get(department, department)
    
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # テーブル名の生成（診療科名を使用）
        table_name = f"rag_{department_ja.replace('/', '_').replace(' ', '_')}"
        
        # テーブルが存在するか確認
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        
        if not cursor.fetchone():
            print(f"RAG table for {department_ja} not found")
            return ""
        
        # データを取得
        cursor.execute(f"SELECT content FROM {table_name}")
        rows = cursor.fetchall()
        
        if rows:
            # すべてのコンテンツを結合
            context = "\n\n".join([row[0] for row in rows if row[0]])
            return context
        else:
            return ""
            
    except Exception as e:
        print(f"Error getting RAG context: {e}")
        return ""
    finally:
        conn.close()

def get_rag_base_dir():
    """RAGディレクトリパスを取得"""
    # 本番環境ではプロジェクトルートからの相対パスを使用
    return Path("./rag/各診療科")

def load_csv_data_from_directory():
    """CSVファイルをディレクトリから自動的にロード"""
    # RAGデータのベースディレクトリ
    base_dir = get_rag_base_dir()
    
    if not base_dir.exists():
        print(f"RAG directory not found: {base_dir}")
        return
    
    # データベース接続
    conn = sqlite3.connect(str(RAG_DB_PATH))
    cursor = conn.cursor()
    
    try:
        # CSVファイルの更新をチェック
        if should_update_rag_data(conn, base_dir):
            print("[RAG] CSV files have been updated. Reloading data...")
            # 既存データをクリア
            cursor.execute("DELETE FROM rag_data")
            cursor.execute("DELETE FROM upload_history")
            conn.commit()
        else:
            # 既存のデータがあり、更新も不要な場合
            cursor.execute("SELECT COUNT(*) FROM rag_data")
            if cursor.fetchone()[0] > 0:
                print("[RAG] Data is up to date. Skipping CSV load.")
                conn.close()
                return
        
        # 各診療科のディレクトリを処理
        loaded_departments = []
        for dept_dir in base_dir.iterdir():
            if dept_dir.is_dir():
                department_name = dept_dir.name
                csv_file = dept_dir / f"{department_name}_全体.csv"
                
                if csv_file.exists():
                    print(f"Loading CSV for department: {department_name}")
                    try:
                        # CSVファイルを読み込み
                        df = pd.read_csv(csv_file, encoding='utf-8-sig')
                        
                        # _save_rag_data_internal関数を使用してデータを保存
                        result = _save_rag_data_internal(department_name, df, csv_file.name)
                        
                        if result['success']:
                            loaded_departments.append({
                                'department': department_name,
                                'inserted_count': result['inserted_count'],
                                'skipped_count': result['skipped_count']
                            })
                        else:
                            print(f"Failed to load data for {department_name}: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        print(f"Error loading CSV file {csv_file}: {e}")
                        continue
        
        # 成功したロードの概要を表示
        if loaded_departments:
            print("\nCSV data loading summary:")
            for dept in loaded_departments:
                print(f"  - {dept['department']}: {dept['inserted_count']} records loaded")
            print(f"\nTotal departments loaded: {len(loaded_departments)}")
        else:
            print("No CSV data was loaded.")
            
    except Exception as e:
        print(f"Error during CSV loading: {e}")
        conn.close()
        raise

def should_update_rag_data(conn, base_dir):
    """CSVファイルが更新されているかチェック"""
    cursor = conn.cursor()
    
    # アップロード履歴から最終更新時刻を取得
    cursor.execute("""
        SELECT specialty, uploaded_at 
        FROM upload_history 
        ORDER BY uploaded_at DESC 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if not result:
        # データがない場合は更新が必要
        return True
    
    # 最後のアップロード時刻を取得
    last_upload_str = result[1]
    last_upload = datetime.fromisoformat(last_upload_str.replace(' ', 'T'))
    
    # CSVファイルの最終更新時刻をチェック
    for dept_dir in base_dir.iterdir():
        if dept_dir.is_dir():
            csv_file = dept_dir / f"{dept_dir.name}_全体.csv"
            if csv_file.exists():
                # ファイルの更新時刻を取得
                file_mtime = datetime.fromtimestamp(csv_file.stat().st_mtime)
                
                # CSVファイルがデータベースより新しい場合
                if file_mtime > last_upload:
                    print(f"[RAG] Updated CSV found: {csv_file.name} (modified: {file_mtime})")
                    return True
    
    return False

def reload_csv_data():
    """CSVデータを再ロード（開発/更新用）"""
    conn = sqlite3.connect(str(RAG_DB_PATH))
    cursor = conn.cursor()
    
    try:
        # 既存のデータを削除
        cursor.execute("DELETE FROM rag_data")
        cursor.execute("DELETE FROM upload_history")
        conn.commit()
        print("Existing RAG data cleared.")
        
    except Exception as e:
        print(f"Error clearing existing data: {e}")
        conn.rollback()
        conn.close()
        raise
    finally:
        conn.close()
    
    # CSVデータを再ロード
    load_csv_data_from_directory()

# テスト用関数
if __name__ == "__main__":
    print("RAG Manager Test")
    init_rag_database()
    print("Database initialized successfully!")
