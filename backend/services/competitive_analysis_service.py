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
try:
    from anthropic import Anthropic
    anthropic_available = True
except ImportError:
    anthropic_available = False
try:
    from google import genai as google_genai_sdk
    from google.genai import types as google_genai_types
    google_genai_available = True
except ImportError:
    google_genai_available = False
from .google_maps_service import GoogleMapsService
from .crud import read_settings

logger = logging.getLogger(__name__)

class CompetitiveAnalysisService:
    def __init__(self):
        self.google_maps = GoogleMapsService()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # 管理画面の設定を読み込み
        try:
            self.settings = read_settings()
            self.selected_model = self.settings.model_settings.selected_model
            self.selected_provider = self.settings.model_settings.selected_provider
        except Exception as e:
            logger.warning(f"Failed to read settings: {e}")
            self.selected_model = "gpt-4"
            self.selected_provider = "openai"
    
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
            # 診療科の取得（新しいdepartmentフィールドまたは古いdepartmentsフィールドに対応）
            department = clinic_info.get("department")
            department_types = [department] if department else clinic_info.get("departments", [])
            
            competitors = await self.google_maps.search_nearby_clinics(
                location=clinic_info.get("address", ""),
                radius=search_radius,
                department_types=department_types,
                limit=20  # より多くの結果を取得
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
        
        # 口コミデータの整理（上位5件の競合のみ）
        review_insights = self._analyze_reviews(competitors[:5])
        
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
            "review_insights": review_insights,
            "additional_context": additional_info or ""
        }
    
    async def _generate_swot_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """SWOT分析を生成"""
        
        try:
            prompt = self._build_swot_prompt(analysis_data)
            system_prompt = "あなたは医療機関の経営コンサルタントです。提供された情報を基に、具体的で実行可能なSWOT分析を行ってください。"
            
            # 選択されたプロバイダーに応じてAIを使用
            if self.selected_provider == "openai" and self.openai_api_key and openai_available:
                client = OpenAI(api_key=self.openai_api_key)
                # GPT-5 uses max_completion_tokens instead of max_tokens
                if "gpt-5" in self.selected_model:
                    response = client.chat.completions.create(
                        model=self.selected_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_completion_tokens=2000
                    )
                else:
                    response = client.chat.completions.create(
                        model=self.selected_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=2000
                    )
                content = response.choices[0].message.content
                
            elif self.selected_provider == "anthropic" and self.anthropic_api_key and anthropic_available:
                client = Anthropic(api_key=self.anthropic_api_key)
                response = client.messages.create(
                    model=self.selected_model,
                    max_tokens=2000,
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
                
            elif self.selected_provider == "google" and self.google_api_key and google_genai_available:
                client = google_genai_sdk.Client(api_key=self.google_api_key)
                response = await client.models.generate_content_async(
                    model=self.selected_model,
                    contents=f"{system_prompt}\n\n{prompt}",
                    config=google_genai_types.GenerateContentConfig(
                        temperature=0.7,
                        max_output_tokens=2000
                    )
                )
                content = response.text
                
            else:
                logger.warning(f"Selected provider {self.selected_provider} not available, using basic SWOT")
                return self._generate_basic_swot(analysis_data)
            
            return self._parse_swot_response(content)
            
        except Exception as e:
            logger.error(f"Error generating SWOT analysis with AI: {str(e)}")
            return self._generate_basic_swot(analysis_data)
    
    def _build_swot_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """SWOT分析用のプロンプトを構築"""
        clinic = analysis_data["clinic"]
        stats = analysis_data["market_stats"]
        competitors = analysis_data["competitors"]
        
        # 診療科の取得（新しいdepartmentフィールドまたは古いdepartmentsフィールドに対応）
        department = clinic.get('department') or ', '.join(clinic.get('departments', []))
        
        # トップ5件の競合情報を詳細に記載
        top_competitors_info = ""
        for i, comp in enumerate(competitors[:5], 1):
            top_competitors_info += f"""
{i}. {comp.get('name', '不明')}
   - 評価: {comp.get('rating', 'N/A')} ({comp.get('user_ratings_total', 0)}件のレビュー)
   - 住所: {comp.get('formatted_address', comp.get('address', '不明'))}
   - 距離: {comp.get('distance', '不明')}m
"""
        
        # 診療科タイプの分布情報
        dept_distribution_info = ""
        if stats['department_distribution']:
            sorted_depts = sorted(stats['department_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]
            for dept_type, count in sorted_depts:
                dept_distribution_info += f"- {dept_type}: {count}件\n"
        
        # 口コミ分析の情報を整形
        review_insights = analysis_data.get('review_insights', {})
        review_analysis_info = ""
        
        # ポジティブなテーマ
        if review_insights.get('positive_themes'):
            review_analysis_info += "\n【競合の口コミで評価されている点】\n"
            for theme, count in list(review_insights['positive_themes'].items())[:5]:
                review_analysis_info += f"- {theme}: {count}件の言及\n"
        
        # ネガティブなテーマ
        if review_insights.get('negative_themes'):
            review_analysis_info += "\n【競合の口コミで指摘されている問題点】\n"
            for theme, count in list(review_insights['negative_themes'].items())[:5]:
                review_analysis_info += f"- {theme}: {count}件の言及\n"
        
        # 主要競合の口コミハイライト
        if review_insights.get('competitor_highlights'):
            review_analysis_info += "\n【主要競合の口コミ傾向】\n"
            for comp in review_insights['competitor_highlights'][:3]:
                review_analysis_info += f"\n{comp['name']} (評価: {comp['rating']})\n"
                for point in comp['key_points']:
                    review_analysis_info += f"  {point}\n"
        
        prompt = f"""
以下の詳細情報を基に、医療機関の具体的で実行可能なSWOT分析を行ってください。

【自院情報】
- 名称: {clinic.get('name', '')}
- 住所: {clinic.get('address', '')}
- 診療科: {department}
- 特徴・強み: {clinic.get('features', '')}
- ターゲット層: {analysis_data.get('additional_context', '')}

【市場環境分析】
- 半径{analysis_data['clinic'].get('search_radius', 3000)/1000}km圏内の競合数: {stats['total_competitors']}院
- 競合の平均評価: {stats['average_rating']}
- 評価分布:
  - 高評価（4.0以上）: {stats['rating_distribution']['above_4']}院
  - 中評価（3.0-4.0）: {stats['rating_distribution']['3_to_4']}院
  - 低評価（3.0未満）: {stats['rating_distribution']['below_3']}院

【主要競合の詳細情報】
{top_competitors_info}

【診療科タイプの分布】
{dept_distribution_info if dept_distribution_info else 'データなし'}
{review_analysis_info}
【分析の注意点】
1. 競合の具体的な名前や評価を踏まえた分析を行う
2. 地域の医療ニーズや競合状況を具体的に考慮する
3. 口コミで評価されている点や問題点を踏まえ、自院の差別化戦略に活用する
4. 自院の特徴・強みとターゲット層を重視した分析を行う
5. 実行可能で具体的な施策につながる分析を心がける

以下の形式でSWOT分析を提供してください：

**強み（Strengths）**
- [具体的な強み1]
- [具体的な強み2]
- [具体的な強み3]
- [具体的な強み4]

**弱み（Weaknesses）**
- [具体的な弱み1]
- [具体的な弱み2]
- [具体的な弱み3]
- [具体的な弱み4]

**機会（Opportunities）**
- [具体的な機会1]
- [具体的な機会2]
- [具体的な機会3]
- [具体的な機会4]

**脅威（Threats）**
- [具体的な脅威1]
- [具体的な脅威2]
- [具体的な脅威3]
- [具体的な脅威4]
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
    
    def _analyze_reviews(self, top_competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """口コミデータを分析してインサイトを抽出"""
        review_insights = {
            "positive_themes": {},  # ポジティブなテーマと出現回数
            "negative_themes": {},  # ネガティブなテーマと出現回数
            "competitor_highlights": []  # 各競合の主要な口コミポイント
        }
        
        # ポジティブ/ネガティブなキーワード
        positive_keywords = [
            "優しい", "丁寧", "親切", "きれい", "清潔", "新しい", "早い", "安心",
            "信頼", "良い", "感じがいい", "おすすめ", "便利", "わかりやすい"
        ]
        negative_keywords = [
            "待つ", "遅い", "高い", "不親切", "汚い", "古い", "分かりにくい",
            "混む", "混雑", "態度", "高圧的", "冷たい", "不安"
        ]
        
        for competitor in top_competitors:
            comp_name = competitor.get('name', '不明')
            reviews = competitor.get('reviews', [])
            
            if not reviews:
                continue
                
            positive_count = 0
            negative_count = 0
            key_points = []
            
            for review in reviews[:3]:  # 最新3件のレビューを分析
                text = review.get('text', '')
                rating = review.get('rating', 0)
                
                # ポジティブ/ネガティブなテーマをカウント
                for keyword in positive_keywords:
                    if keyword in text:
                        review_insights['positive_themes'][keyword] = review_insights['positive_themes'].get(keyword, 0) + 1
                        positive_count += 1
                
                for keyword in negative_keywords:
                    if keyword in text:
                        review_insights['negative_themes'][keyword] = review_insights['negative_themes'].get(keyword, 0) + 1
                        negative_count += 1
                
                # 高評価または低評価のレビューからポイントを抽出
                if rating >= 4 and text:
                    key_points.append(f"◎高評価: {text[:50]}...")
                elif rating <= 2 and text:
                    key_points.append(f"◎低評価: {text[:50]}...")
            
            if key_points:
                review_insights['competitor_highlights'].append({
                    'name': comp_name,
                    'rating': competitor.get('rating', 'N/A'),
                    'key_points': key_points[:2],  # 最大2つのポイント
                    'positive_mentions': positive_count,
                    'negative_mentions': negative_count
                })
        
        # 最も頻出するテーマをソート
        review_insights['positive_themes'] = dict(sorted(
            review_insights['positive_themes'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5])  # トップ5
        
        review_insights['negative_themes'] = dict(sorted(
            review_insights['negative_themes'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5])  # トップ5
        
        return review_insights
    
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