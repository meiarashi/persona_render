#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
医療統計拡張サービスのテスト
"""

import asyncio
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.estat_medical_stats import EStatMedicalStatsService

async def test_medical_stats():
    """医療統計サービスのテスト"""
    print("="*70)
    print("医療統計拡張サービステスト")
    print("="*70)
    
    service = EStatMedicalStatsService()
    
    test_addresses = [
        "東京都千代田区",
        "大阪府大阪市北区",
        "島根県松江市"
    ]
    
    for address in test_addresses:
        print(f"\n【{address}の医療統計データ】")
        print("-"*60)
        
        # 包括的な医療統計を取得
        stats = await service.get_comprehensive_medical_stats(address)
        
        # 1. 医療施設情報
        facilities = stats.get("medical_facilities", {})
        if facilities:
            print("\n[医療施設]")
            print(f"  総診療所数: {facilities.get('total_clinics', 'N/A')}施設")
            
            by_specialty = facilities.get("by_specialty", {})
            if by_specialty:
                print("  診療科別内訳:")
                for spec, count in list(by_specialty.items())[:5]:
                    print(f"    {spec}: {count}施設")
            
            print(f"  夜間救急対応: {facilities.get('night_emergency', 'N/A')}施設")
        
        # 2. 患者統計
        patient_stats = stats.get("patient_stats", {})
        if patient_stats:
            print("\n[患者統計]")
            print(f"  外来受療率: {patient_stats.get('outpatient_rate', 'N/A')}/10万人")
            print(f"  入院受療率: {patient_stats.get('hospitalization_rate', 'N/A')}/10万人")
            print(f"  年間平均受診回数: {patient_stats.get('avg_consultation_per_year', 'N/A')}回")
            
            top_diseases = patient_stats.get("top_diseases", [])
            if top_diseases:
                print("  主要疾患（上位3つ）:")
                for disease in top_diseases[:3]:
                    print(f"    {disease['name']}: {disease['percentage']}%")
        
        # 3. 医療従事者
        staff = stats.get("medical_staff", {})
        if staff:
            print("\n[医療従事者]")
            print(f"  医師数: {staff.get('doctors_per_100k', 'N/A')}/10万人")
            print(f"  看護師数: {staff.get('nurses_per_100k', 'N/A')}/10万人")
            print(f"  不足レベル: {staff.get('shortage_level', 'N/A')}")
        
        # 4. 世帯医療費
        household = stats.get("household_medical", {})
        if household:
            print("\n[世帯医療費]")
            print(f"  年間平均医療費: {household.get('avg_annual_medical_expense', 0):,}円")
            print(f"  自己負担割合: {household.get('self_pay_ratio', 0)*100:.0f}%")
        
        # 5. 介護施設
        nursing = stats.get("nursing_facilities", {})
        if nursing:
            print("\n[介護施設]")
            print(f"  総施設数: {nursing.get('total_facilities', 'N/A')}施設")
            print(f"  総定員: {nursing.get('total_capacity', 0):,}人")
            print(f"  稼働率: {nursing.get('occupancy_rate', 0)*100:.0f}%")

async def test_competitive_analysis():
    """競合環境分析のテスト"""
    print("\n" + "="*70)
    print("競合環境分析テスト")
    print("="*70)
    
    service = EStatMedicalStatsService()
    
    # 東京都千代田区のデータで分析
    address = "東京都千代田区"
    print(f"\n【{address}の競合環境分析】")
    print("-"*60)
    
    # データ取得
    stats = await service.get_comprehensive_medical_stats(address)
    
    # 競合環境を分析
    analysis = service.analyze_competitive_landscape(stats)
    
    # 市場飽和度
    saturation = analysis.get("market_saturation", {})
    print("\n[市場飽和度]")
    print(f"  レベル: {saturation.get('level', 'N/A')}")
    print(f"  スコア: {saturation.get('score', 0):.1%}")
    print(f"  競合数: {saturation.get('total_competitors', 'N/A')}施設")
    
    # 機会
    opportunities = analysis.get("opportunity_areas", [])
    if opportunities:
        print("\n[ビジネス機会]")
        for opp in opportunities[:3]:
            print(f"  - {opp['type']}: {opp['description']}")
            print(f"    優先度: {opp['priority']}")
    
    # リスク
    risks = analysis.get("risk_factors", [])
    if risks:
        print("\n[リスク要因]")
        for risk in risks:
            print(f"  - {risk['type']}: {risk['description']}")
            print(f"    深刻度: {risk['severity']}")
    
    # 推奨事項
    recommendations = analysis.get("recommendations", [])
    if recommendations:
        print("\n[推奨事項]")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

async def test_comparison():
    """地域間比較テスト"""
    print("\n" + "="*70)
    print("地域間比較分析")
    print("="*70)
    
    service = EStatMedicalStatsService()
    
    areas = [
        ("東京都千代田区", "都心部"),
        ("埼玉県さいたま市", "郊外"),
        ("島根県松江市", "地方都市")
    ]
    
    print("\n地域タイプ     総診療所  医師数/10万  患者受療率  介護施設  市場飽和度")
    print("-"*70)
    
    for address, area_type in areas:
        stats = await service.get_comprehensive_medical_stats(address)
        analysis = service.analyze_competitive_landscape(stats)
        
        clinics = stats.get("medical_facilities", {}).get("total_clinics", 0)
        doctors = stats.get("medical_staff", {}).get("doctors_per_100k", 0)
        outpatient = stats.get("patient_stats", {}).get("outpatient_rate", 0)
        nursing = stats.get("nursing_facilities", {}).get("total_facilities", 0)
        saturation = analysis.get("market_saturation", {}).get("level", "N/A")
        
        print(f"{area_type:12} {clinics:8} {doctors:11.0f} {outpatient:10} {nursing:9} {saturation:10}")

async def main():
    """メイン処理"""
    print("\n" + "="*70)
    print("e-Stat医療統計拡張サービス 総合テスト")
    print("="*70)
    
    # 各テストを実行
    await test_medical_stats()
    await test_competitive_analysis()
    await test_comparison()
    
    print("\n" + "="*70)
    print("テスト完了")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())