"""
キーワード分析のためのユーティリティ関数
"""
from typing import List, Dict, Tuple
import re

def categorize_keywords(keywords: List[Dict]) -> Dict[str, List[Dict]]:
    """検索キーワードをカテゴリ別に分類"""
    categories = {
        "症状・不安": [],
        "原因・理解": [],
        "治療・対策": [],
        "医療機関": [],
        "費用・保険": [],
        "体験談・口コミ": [],
        "予防・生活習慣": [],
        "その他": []
    }
    
    # カテゴリ判定のキーワードパターン
    patterns = {
        "症状・不安": ["症状", "痛み", "つらい", "不安", "心配", "怖い", "悪化"],
        "原因・理解": ["原因", "なぜ", "理由", "メカニズム", "仕組み", "とは"],
        "治療・対策": ["治療", "手術", "薬", "改善", "対策", "方法", "治す"],
        "医療機関": ["病院", "クリニック", "医院", "名医", "評判", "どこ"],
        "費用・保険": ["費用", "料金", "保険", "値段", "価格", "いくら"],
        "体験談・口コミ": ["体験", "口コミ", "評価", "ブログ", "感想", "レビュー"],
        "予防・生活習慣": ["予防", "運動", "食事", "生活", "習慣", "ケア"]
    }
    
    for keyword_data in keywords:
        keyword = keyword_data.get('keyword', '')
        categorized = False
        
        for category, pattern_list in patterns.items():
            if any(pattern in keyword for pattern in pattern_list):
                categories[category].append(keyword_data)
                categorized = True
                break
        
        if not categorized:
            categories["その他"].append(keyword_data)
    
    return categories

def calculate_demographic_match(keywords: List[Dict], target_gender: str, target_age: str) -> float:
    """ペルソナの属性とキーワードの検索者属性のマッチ度を計算"""
    if not keywords:
        return 0.0
    
    total_match_score = 0
    valid_keywords = 0
    
    for keyword in keywords:
        # 性別マッチ度
        gender_match = 0
        if target_gender == "男性":
            gender_match = keyword.get('男性割合(%)', 0) / 100
        elif target_gender == "女性":
            gender_match = keyword.get('女性割合(%)', 0) / 100
        
        # 年齢マッチ度
        age_match = 0
        age_column_map = {
            "10代": "10代割合(%)",
            "20代": "20代割合(%)",
            "30代": "30代割合(%)", 
            "40代": "40代割合(%)",
            "50代": "50代割合(%)",
            "60代": "60代割合(%)",
            "70代": "70代以上割合(%)"
        }
        
        if target_age in age_column_map:
            age_match = keyword.get(age_column_map[target_age], 0) / 100
        
        # 総合マッチ度（性別と年齢の平均）
        if gender_match > 0 or age_match > 0:
            total_match_score += (gender_match + age_match) / 2
            valid_keywords += 1
    
    return total_match_score / valid_keywords if valid_keywords > 0 else 0.0

def analyze_search_patterns(pre_keywords: List[Dict], post_keywords: List[Dict]) -> Dict:
    """診断前後の検索パターンを分析"""
    pre_categories = categorize_keywords(pre_keywords)
    post_categories = categorize_keywords(post_keywords)
    
    analysis = {
        "pre_diagnosis_focus": [],
        "post_diagnosis_focus": [],
        "category_shift": {},
        "urgency_level": "low",
        "solution_seeking_rate": 0
    }
    
    # 診断前の主要な関心事を特定
    for category, keywords in pre_categories.items():
        if len(keywords) > len(pre_keywords) * 0.2:  # 20%以上を占める
            analysis["pre_diagnosis_focus"].append(category)
    
    # 診断後の主要な関心事を特定
    for category, keywords in post_categories.items():
        if len(keywords) > len(post_keywords) * 0.2:
            analysis["post_diagnosis_focus"].append(category)
    
    # カテゴリシフトを計算
    for category in categories.keys():
        pre_ratio = len(pre_categories[category]) / max(len(pre_keywords), 1)
        post_ratio = len(post_categories[category]) / max(len(post_keywords), 1)
        shift = post_ratio - pre_ratio
        if abs(shift) > 0.1:  # 10%以上の変化
            analysis["category_shift"][category] = shift
    
    # 緊急度を判定（短期間に集中した検索があるか）
    if pre_keywords:
        time_diffs = [abs(k['time_diff_days']) for k in pre_keywords]
        if min(time_diffs) < 7 and len(pre_keywords) > 10:
            analysis["urgency_level"] = "high"
        elif min(time_diffs) < 14 and len(pre_keywords) > 5:
            analysis["urgency_level"] = "medium"
    
    # 解決志向度を計算
    solution_keywords = len(post_categories["治療・対策"]) + len(post_categories["医療機関"])
    if post_keywords:
        analysis["solution_seeking_rate"] = solution_keywords / len(post_keywords)
    
    return analysis

def extract_emotional_keywords(keywords: List[Dict]) -> List[str]:
    """感情的なキーワードを抽出"""
    emotional_patterns = [
        "不安", "心配", "怖い", "つらい", "痛い", "苦しい",
        "悩み", "ストレス", "うつ", "イライラ", "焦り",
        "希望", "安心", "改善", "治る", "良くなる"
    ]
    
    emotional_keywords = []
    for keyword_data in keywords:
        keyword = keyword_data.get('keyword', '')
        for pattern in emotional_patterns:
            if pattern in keyword:
                emotional_keywords.append(keyword)
                break
    
    return emotional_keywords