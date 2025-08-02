import os
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False
from .google_maps_service import GoogleMapsService

logger = logging.getLogger(__name__)

class CompetitiveAnalysisService:
    def __init__(self):
        self.google_maps = GoogleMapsService()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key or not openai_available:
            logger.warning("OPENAI_API_KEY not found in environment variables or OpenAI not available")
    
    async def analyze_competitors(
        self,
        clinic_info: Dict[str, Any],
        search_radius: int = 3000,
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        競合分析を実行
        
        Args:
            clinic_info: 自院の情報
            search_radius: 検索半径（メートル）
            additional_info: 追加情報
            
        Returns:
            競合分析結果
        """
        try:
            # 1. 近隣の競合医療機関を検索
            competitors = await self.google_maps.search_nearby_clinics(
                location=clinic_info.get("address", ""),
                radius=search_radius,
                department_types=clinic_info.get("departments", []),
                limit=10
            )
            
            if competitors.get("error"):
                logger.error(f"Google Maps search failed: {competitors['error']}")
                return {"error": competitors["error"]}
            
            # 2. 競合分析データを準備
            analysis_data = await self._prepare_analysis_data(
                clinic_info,
                competitors.get("results", []),
                additional_info
            )
            
            # 3. SWOT分析を生成
            swot_analysis = await self._generate_swot_analysis(analysis_data)
            
            # 4. 戦略提案を生成
            strategic_recommendations = await self._generate_strategic_recommendations(
                swot_analysis,
                analysis_data
            )
            
            return {
                "clinic_info": clinic_info,
                "center": competitors.get("center"),  # 自院の座標を追加
                "search_radius": search_radius,
                "competitors_found": len(competitors.get("results", [])),
                "competitors": competitors.get("results", []),
                "swot_analysis": swot_analysis,
                "strategic_recommendations": strategic_recommendations,
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in competitive analysis: {str(e)}")
            return {"error": f"競合分析中にエラーが発生しました: {str(e)}"}
    
    async def _prepare_analysis_data(
        self,
        clinic_info: Dict[str, Any],
        competitors: List[Dict[str, Any]],
        additional_info: Optional[str]
    ) -> Dict[str, Any]:
        """分析用データの準備"""
        
        # 競合の統計情報を計算
        ratings = [c.get("rating", 0) for c in competitors if c.get("rating")]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # 診療科の分布を分析
        department_distribution = {}
        for competitor in competitors:
            types = competitor.get("types", [])
            for t in types:
                department_distribution[t] = department_distribution.get(t, 0) + 1
        
        return {
            "clinic": clinic_info,
            "competitors": competitors,
            "market_stats": {
                "total_competitors": len(competitors),
                "average_rating": round(avg_rating, 2),
                "rating_distribution": {
                    "above_4": len([r for r in ratings if r >= 4]),
                    "3_to_4": len([r for r in ratings if 3 <= r < 4]),
                    "below_3": len([r for r in ratings if r < 3])
                },
                "department_distribution": department_distribution
            },
            "additional_context": additional_info or ""
        }
    
    async def _generate_swot_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """SWOT分析を生成"""
        
        if not self.openai_api_key:
            return self._generate_basic_swot(analysis_data)
        
        try:
            prompt = self._build_swot_prompt(analysis_data)
            
            client = OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "あなたは医療機関の経営コンサルタントです。提供された情報を基に、具体的で実行可能なSWOT分析を行ってください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # レスポンスをパース
            content = response.choices[0].message.content
            return self._parse_swot_response(content)
            
        except Exception as e:
            logger.error(f"Error generating SWOT analysis with AI: {str(e)}")
            return self._generate_basic_swot(analysis_data)
    
    def _build_swot_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """SWOT分析用のプロンプトを構築"""
        clinic = analysis_data["clinic"]
        stats = analysis_data["market_stats"]
        
        prompt = f"""
以下の情報を基に、医療機関のSWOT分析を行ってください。

【自院情報】
- 名称: {clinic.get('name', '')}
- 住所: {clinic.get('address', '')}
- 診療科: {', '.join(clinic.get('departments', []))}
- 特徴: {clinic.get('features', '')}

【市場環境】
- 半径{clinic.get('search_radius', 3000)/1000}km圏内の競合数: {stats['total_competitors']}
- 競合の平均評価: {stats['average_rating']}
- 高評価（4以上）の競合: {stats['rating_distribution']['above_4']}院

【追加情報】
{analysis_data.get('additional_context', '')}

以下の形式でSWOT分析を提供してください：

**強み（Strengths）**
- [具体的な強み1]
- [具体的な強み2]
- [具体的な強み3]

**弱み（Weaknesses）**
- [具体的な弱み1]
- [具体的な弱み2]
- [具体的な弱み3]

**機会（Opportunities）**
- [具体的な機会1]
- [具体的な機会2]
- [具体的な機会3]

**脅威（Threats）**
- [具体的な脅威1]
- [具体的な脅威2]
- [具体的な脅威3]
"""
        return prompt
    
    def _parse_swot_response(self, content: str) -> Dict[str, List[str]]:
        """AIの応答をパースしてSWOT辞書に変換"""
        swot = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
        
        current_section = None
        section_map = {
            "強み": "strengths",
            "Strengths": "strengths",
            "弱み": "weaknesses",
            "Weaknesses": "weaknesses",
            "機会": "opportunities",
            "Opportunities": "opportunities",
            "脅威": "threats",
            "Threats": "threats"
        }
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # セクションの識別
            for key, section in section_map.items():
                if key in line and "**" in line:
                    current_section = section
                    break
            
            # 項目の抽出
            if current_section and line.startswith('- '):
                item = line[2:].strip()
                if item:
                    swot[current_section].append(item)
        
        return swot
    
    def _generate_basic_swot(self, analysis_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """基本的なSWOT分析を生成（AI不使用時）"""
        stats = analysis_data["market_stats"]
        
        swot = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
        
        # 競合数に基づく分析
        if stats["total_competitors"] < 5:
            swot["opportunities"].append("競合が少ないエリアでの展開機会")
        else:
            swot["threats"].append(f"半径内に{stats['total_competitors']}の競合が存在")
        
        # 評価に基づく分析
        if stats["average_rating"] < 3.5:
            swot["opportunities"].append("競合の評価が低く、差別化の機会")
        else:
            swot["threats"].append(f"競合の平均評価が{stats['average_rating']}と高い")
        
        # デフォルトの項目を追加
        swot["strengths"].extend([
            "立地条件の優位性",
            "専門性の高い診療体制"
        ])
        
        swot["weaknesses"].extend([
            "認知度向上の必要性",
            "デジタルマーケティングの強化余地"
        ])
        
        swot["opportunities"].extend([
            "地域医療連携の強化",
            "オンライン診療の導入"
        ])
        
        swot["threats"].extend([
            "医療制度改革による影響",
            "医療従事者の確保競争"
        ])
        
        return swot
    
    async def _generate_strategic_recommendations(
        self,
        swot_analysis: Dict[str, List[str]],
        analysis_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """戦略的提案を生成"""
        
        recommendations = []
        
        # 基本的な戦略提案
        if analysis_data["market_stats"]["total_competitors"] > 10:
            recommendations.append({
                "title": "差別化戦略の強化",
                "description": "競合が多いエリアでは、独自の強みを明確に打ち出す必要があります。",
                "priority": "high"
            })
        
        if analysis_data["market_stats"]["average_rating"] > 4:
            recommendations.append({
                "title": "サービス品質の向上",
                "description": "競合の評価が高いため、患者満足度を向上させる取り組みが重要です。",
                "priority": "high"
            })
        
        recommendations.append({
            "title": "デジタルプレゼンスの強化",
            "description": "ウェブサイトの充実やSNS活用により、オンラインでの認知度を高めましょう。",
            "priority": "medium"
        })
        
        recommendations.append({
            "title": "地域連携の推進",
            "description": "他の医療機関との連携を強化し、紹介患者の増加を図りましょう。",
            "priority": "medium"
        })
        
        return recommendations