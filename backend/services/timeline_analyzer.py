"""
検索キーワード時系列分析サービス
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import os

def get_timeline_csv_path(department: str, chief_complaint: str) -> Path:
    """主訴別CSVまたはExcelファイルのパスを取得"""
    print(f"[DEBUG] get_timeline_csv_path called with department='{department}', chief_complaint='{chief_complaint}'")
    
    # パストラバーサル攻撃を防ぐためのサニタイゼーション
    if not department or not chief_complaint:
        raise ValueError("診療科または主訴が指定されていません")
    
    # 危険な文字をチェック（パス区切り文字は除外）
    dangerous_chars = ['..', '\x00']
    if any(char in str(department) + str(chief_complaint) for char in dangerous_chars):
        raise ValueError("不正な文字が含まれています")
    
    # プロジェクトルートからの絶対パスを使用
    import os
    project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    base_dir = project_root / "rag" / "各診療科"
    print(f"[DEBUG] Project root: {project_root}")
    print(f"[DEBUG] Base directory: {base_dir}")
    print(f"[DEBUG] Base directory exists: {base_dir.exists()}")
    
    # デバッグ: 診療科ディレクトリの内容を確認
    dept_dir = base_dir / department
    print(f"[DEBUG] Department directory: {dept_dir}")
    print(f"[DEBUG] Department directory exists: {dept_dir.exists()}")
    
    if dept_dir.exists():
        print(f"[DEBUG] Contents of {dept_dir}:")
        for item in dept_dir.iterdir():
            print(f"[DEBUG]   - {item.name}")
            if item.name == "主訴" and item.is_dir():
                print(f"[DEBUG]   Contents of 主訴:")
                for subitem in item.iterdir():
                    print(f"[DEBUG]     - {subitem.name}")
    
    # まずCSVファイルを探す
    csv_path = base_dir / department / "主訴" / f"{chief_complaint}_全体.csv"
    print(f"[DEBUG] Looking for CSV file: {csv_path.absolute()}")
    print(f"[DEBUG] CSV file exists: {csv_path.exists()}")
    
    if csv_path.exists():
        return csv_path
    
    # CSVが見つからない場合はExcelファイルを探す
    xlsx_path = base_dir / department / "主訴" / f"{chief_complaint}_全体.xlsx"
    print(f"[DEBUG] Looking for Excel file: {xlsx_path.absolute()}")
    print(f"[DEBUG] Excel file exists: {xlsx_path.exists()}")
    
    if xlsx_path.exists():
        return xlsx_path
    
    # どちらも見つからない場合はCSVパスを返す（後でエラーハンドリング）
    print(f"[DEBUG] No file found, returning CSV path: {csv_path.absolute()}")
    return csv_path

def filter_keywords_by_demographics(keywords_df: pd.DataFrame, gender: str, age: str) -> pd.DataFrame:
    """性別・年齢でキーワードをフィルタリング"""
    filtered_df = keywords_df.copy()
    
    # 性別フィルタ（日本語・英語両方に対応）
    if gender in ["male", "男性"]:
        # 男性比率が40%以上のキーワードを優先
        filtered_df = filtered_df[filtered_df['男性割合(%)'] >= 40]
    elif gender in ["female", "女性"]:
        # 女性比率が40%以上のキーワードを優先
        filtered_df = filtered_df[filtered_df['女性割合(%)'] >= 40]
    
    # 年齢フィルタ
    age_mapping = {
        "20代": "20代割合(%)",
        "30代": "30代割合(%)",
        "40代": "40代割合(%)",
        "50代": "50代割合(%)",
        "60代": "60代割合(%)",
        "70代以上": "70代以上割合(%)"
    }
    
    if age in age_mapping:
        age_column = age_mapping[age]
        # 該当年代の割合が15%以上のキーワードを優先
        filtered_df = filtered_df[filtered_df[age_column] >= 15]
    
    return filtered_df

def calculate_estimated_volume(row: pd.Series, gender: str, age: str) -> int:
    """性別・年齢を考慮した検索ボリュームを推定"""
    try:
        base_volume = float(row.get('検索ボリューム(人)', 0))
        if pd.isna(base_volume) or base_volume < 0:
            base_volume = 0
    except (ValueError, TypeError):
        base_volume = 0
    
    # 性別による調整（日本語・英語両方に対応）
    try:
        if gender in ["male", "男性"]:
            gender_ratio = float(row.get('男性割合(%)', 100)) / 100
        elif gender in ["female", "女性"]:
            gender_ratio = float(row.get('女性割合(%)', 100)) / 100
        else:
            gender_ratio = 1.0
        
        # 比率の妥当性チェック
        if pd.isna(gender_ratio) or gender_ratio < 0 or gender_ratio > 1:
            gender_ratio = 1.0
    except (ValueError, TypeError):
        gender_ratio = 1.0
    
    # 年齢による調整
    age_mapping = {
        "10代": "10代（13歳〜）割合(%)",
        "20代": "20代割合(%)",
        "30代": "30代割合(%)",
        "40代": "40代割合(%)",
        "50代": "50代割合(%)",
        "60代": "60代割合(%)",
        "70代以上": "70代以上割合(%)"
    }
    
    try:
        if age in age_mapping:
            age_column = age_mapping[age]
            if age_column in row:
                age_ratio = float(row.get(age_column, 100)) / 100
            else:
                age_ratio = 1.0
            
            # 比率の妥当性チェック
            if pd.isna(age_ratio) or age_ratio < 0 or age_ratio > 1:
                age_ratio = 1.0
        else:
            age_ratio = 1.0
    except (ValueError, TypeError):
        age_ratio = 1.0
    
    # 推定ボリューム = 基本ボリューム × 性別比率 × 年齢比率
    try:
        estimated_volume = int(base_volume * gender_ratio * age_ratio)
        return max(estimated_volume, 1)  # 最小値は1
    except (ValueError, TypeError):
        return 1

def analyze_search_timeline(department: str, chief_complaint: str, 
                          gender: Optional[str] = None, 
                          age: Optional[str] = None) -> Dict:
    """検索タイムラインを分析"""
    
    print(f"[DEBUG] Analyzing timeline for: department='{department}', chief_complaint='{chief_complaint}'")
    
    csv_path = get_timeline_csv_path(department, chief_complaint)
    
    if not csv_path.exists():
        return {
            "error": f"データファイルが見つかりません: {department}/{chief_complaint}",
            "filtered_keywords": [],
            "summary": {}
        }
    
    try:
        # ファイル形式に応じて読み込み
        if csv_path.suffix == '.csv':
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
        elif csv_path.suffix == '.xlsx':
            df = pd.read_excel(csv_path)
        else:
            return {
                "error": f"サポートされていないファイル形式: {csv_path.suffix}",
                "filtered_keywords": [],
                "summary": {}
            }
        
        # 性別・年齢でフィルタリング
        if gender or age:
            df = filter_keywords_by_demographics(df, gender, age)
        
        # 必須カラムの存在確認
        required_columns = ['出力キーワード', '検索ボリューム(人)', '検索時間差(日)', 
                          '特徴度', '男性割合(%)', '女性割合(%)']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {
                "error": f"必須カラムが不足しています: {', '.join(missing_columns)}",
                "filtered_keywords": [],
                "summary": {}
            }
        
        # 数値カラムの型変換（エラーハンドリング付き）
        numeric_columns = ['検索ボリューム(人)', '検索時間差(日)', '特徴度', 
                          '男性割合(%)', '女性割合(%)']
        for col in numeric_columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            except Exception as e:
                print(f"Warning: Failed to convert column {col} to numeric: {e}")
        
        # NaN値を持つ行を除外
        df = df.dropna(subset=required_columns)
        
        # 各行に推定ボリュームを追加
        df['推定検索ボリューム'] = df.apply(
            lambda row: calculate_estimated_volume(row, gender, age), 
            axis=1
        )
        
        # 時間差でソート
        df = df.sort_values('検索時間差(日)')
        
        # 結果を整形
        keywords = []
        for _, row in df.iterrows():
            keywords.append({
                "keyword": row['出力キーワード'],
                "search_volume": int(row['検索ボリューム(人)']),
                "estimated_volume": int(row['推定検索ボリューム']),
                "time_diff_days": float(row['検索時間差(日)']),
                "distinctiveness": float(row['特徴度']),
                "male_ratio": int(row['男性割合(%)']),
                "female_ratio": int(row['女性割合(%)']),
                "age_groups": {
                    "10s": int(row.get('10代（13歳〜）割合(%)', 0)),
                    "20s": int(row.get('20代割合(%)', 0)),
                    "30s": int(row.get('30代割合(%)', 0)),
                    "40s": int(row.get('40代割合(%)', 0)),
                    "50s": int(row.get('50代割合(%)', 0)),
                    "60s": int(row.get('60代割合(%)', 0)),
                    "70s_plus": int(row.get('70代以上割合(%)', 0))
                }
            })
        
        # サマリー情報
        pre_diagnosis = [k for k in keywords if k['time_diff_days'] < 0]
        post_diagnosis = [k for k in keywords if k['time_diff_days'] >= 0]
        
        # サマリー情報の安全な計算
        peak_search_day = 0
        if len(df) > 0 and '推定検索ボリューム' in df.columns:
            try:
                # 最大値のインデックスが存在するか確認
                max_volume = df['推定検索ボリューム'].max()
                if pd.notna(max_volume) and max_volume > 0:
                    peak_search_day = float(df.loc[df['推定検索ボリューム'].idxmax()]['検索時間差(日)'])
            except Exception as e:
                print(f"Warning: Failed to calculate peak search day: {e}")
                peak_search_day = 0
        
        summary = {
            "total_keywords": len(keywords),
            "pre_diagnosis_count": len(pre_diagnosis),
            "post_diagnosis_count": len(post_diagnosis),
            "peak_search_day": peak_search_day
        }
        
        return {
            "filtered_keywords": keywords,
            "summary": summary,
            "filters_applied": {
                "gender": gender,
                "age": age
            }
        }
        
    except Exception as e:
        return {
            "error": f"データ処理エラー: {str(e)}",
            "filtered_keywords": [],
            "summary": {}
        }