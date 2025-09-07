import os
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
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
from .web_research_service import WebResearchService, RegionalDataService
from .estat_medical_stats import EStatMedicalStatsService
from backend.utils.config_manager import config_manager

logger = logging.getLogger(__name__)

class CompetitiveAnalysisService:
    def __init__(self):
        self.google_maps = GoogleMapsService()
        self.web_research = WebResearchService()
        self.regional_data = RegionalDataService()
        self.medical_stats_service = EStatMedicalStatsService()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # 管理画面の設定を読み込み
        try:
            self.settings = config_manager.get_settings()
            # 新しいフィールド名を使用（models.text_api_model）
            if hasattr(self.settings, 'models') and self.settings.models:
                self.selected_model = self.settings.models.text_api_model or "gpt-5-2025-08-07"
                # プロバイダーを自動判定
                if "gpt" in self.selected_model.lower():
                    self.selected_provider = "openai"
                elif "claude" in self.selected_model.lower():
                    self.selected_provider = "anthropic"
                elif "gemini" in self.selected_model.lower():
                    self.selected_provider = "google"
                else:
                    self.selected_provider = "openai"
            else:
                # 古いフィールド名にフォールバック
                self.selected_model = getattr(self.settings.model_settings, 'selected_model', "gpt-4-turbo-preview") if hasattr(self.settings, 'model_settings') else "gpt-4-turbo-preview"
                self.selected_provider = getattr(self.settings.model_settings, 'selected_provider', "openai") if hasattr(self.settings, 'model_settings') else "openai"
            
            logger.info(f"[CompetitiveAnalysis] Using model: {self.selected_model} (provider: {self.selected_provider})")
        except Exception as e:
            logger.warning(f"Failed to read settings: {e}")
            self.selected_model = "gpt-4-turbo-preview"
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
            
            # 3. SWOT分析と戦略提案を生成
            swot_analysis, ai_response = await self._generate_swot_analysis(analysis_data)
            
            # 4. 戦略提案を抽出（AIレスポンスから）または生成（フォールバック）
            strategic_recommendations = await self._generate_strategic_recommendations(
                swot_analysis,
                analysis_data,
                ai_response
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
    
    async def _safe_execute_task(self, task, default_value=None, task_name="task"):
        """タスクを安全に実行し、エラー時はデフォルト値を返す"""
        try:
            return await task
        except Exception as e:
            logger.error(f"Failed to execute {task_name}: {e}")
            return default_value if default_value is not None else {}
    
    def _format_number(self, value, default='N/A'):
        """数値を安全にフォーマット（カンマ区切り）"""
        if value == 'N/A' or value is None:
            return default
        try:
            if isinstance(value, (int, float)):
                return f"{value:,}"
            return str(value)
        except:
            return default
    
    async def _prepare_analysis_data(
        self,
        clinic_info: Dict[str, Any],
        competitors: List[Dict[str, Any]],
        additional_info: Optional[str]
    ) -> Dict[str, Any]:
        """分析用データの準備（Web検索と地域データを含む）"""
        
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
        
        # 並列タスクを準備
        import asyncio
        tasks = []
        
        # 地域特性データ取得タスク
        regional_task = self.regional_data.get_regional_data(
            clinic_info.get("address", "")
        )
        tasks.append(('regional_data', regional_task))
        
        # 医療統計データ取得タスク
        medical_task = self.medical_stats_service.get_comprehensive_medical_stats(
            clinic_info.get("address", "")
        )
        tasks.append(('medical_stats', medical_task))
        
        # タスクを並列実行（エラーハンドリング付き）
        results = {}
        for name, task in tasks:
            results[name] = await self._safe_execute_task(task, {}, name)
        
        regional_data = results.get('regional_data', {})
        medical_stats = results.get('medical_stats', {})
        
        logger.info(f"Regional data keys: {list(regional_data.keys())}")
        logger.info(f"Medical stats keys: {list(medical_stats.keys())}")
        
        # 上位競合のWeb詳細情報を取得（並列処理）
        competitor_details = []
        if self.web_research.serpapi_key:  # SerpAPIキーがある場合のみ実行
            research_tasks = []
            for comp in competitors[:3]:  # 上位3件のみ詳細調査
                task = self.web_research.research_competitor(
                    comp.get("name", ""),
                    comp.get("formatted_address", comp.get("address", ""))
                )
                research_tasks.append(task)
            
            try:
                competitor_details = await asyncio.gather(*research_tasks, return_exceptions=True)
                # エラーを除外
                competitor_details = [d for d in competitor_details if not isinstance(d, Exception)]
                logger.info(f"Retrieved detailed info for {len(competitor_details)} competitors")
            except Exception as e:
                logger.warning(f"Failed to get competitor details: {e}")
        
        return {
            "clinic": clinic_info,
            "competitors": competitors,
            "competitor_details": competitor_details,  # 詳細な競合情報
            "regional_data": regional_data,  # 地域特性データ
            "medical_stats": medical_stats,  # 医療統計データ（新規追加）
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
    
    async def _generate_swot_analysis(self, analysis_data: Dict[str, Any]) -> Tuple[Dict[str, List[str]], str]:
        """SWOT分析と戦略的提案を生成"""
        
        try:
            prompt = self._build_swot_prompt(analysis_data)
            system_prompt = "あなたは医療機関の経営コンサルタントです。提供された情報を基に、具体的で実行可能なSWOT分析と戦略的提案を行ってください。"
            
            # モデル使用ログ
            print("="*60)
            print("[CompetitiveAnalysis] ===== GENERATING SWOT ANALYSIS & RECOMMENDATIONS =====")
            print(f"[CompetitiveAnalysis] Model: {self.selected_model}")
            print(f"[CompetitiveAnalysis] Provider: {self.selected_provider}")
            print("="*60)
            
            # 選択されたプロバイダーに応じてAIを使用
            if self.selected_provider == "openai" and self.openai_api_key and openai_available:
                client = OpenAI(api_key=self.openai_api_key, timeout=30.0)  # 30秒のタイムアウトに最適化
                # GPT-5 uses max_completion_tokens instead of max_tokens and temperature must be 1.0
                if "gpt-5" in self.selected_model:
                    response = client.chat.completions.create(
                        model=self.selected_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=1.0,  # GPT-5 only supports default temperature of 1.0
                        max_completion_tokens=1500  # レスポンスを最適化して処理時間短縮
                    )
                else:
                    response = client.chat.completions.create(
                        model=self.selected_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1500  # レスポンスを最適化して処理時間短縮
                    )
                content = response.choices[0].message.content
                
            elif self.selected_provider == "anthropic" and self.anthropic_api_key and anthropic_available:
                client = Anthropic(api_key=self.anthropic_api_key, timeout=30.0)  # 30秒のタイムアウトに最適化
                response = client.messages.create(
                    model=self.selected_model,
                    max_tokens=1500,  # レスポンスを最適化して処理時間短縮
                    temperature=0.7,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
                
            elif self.selected_provider == "google" and self.google_api_key and google_genai_available:
                import asyncio
                client = google_genai_sdk.Client(api_key=self.google_api_key)
                # Google Gemini APIは同期的なので、asyncioで実行
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model=self.selected_model,
                        contents=f"{system_prompt}\n\n{prompt}",
                        config=google_genai_types.GenerateContentConfig(
                            temperature=0.7,
                            max_output_tokens=2000  # 戦略提案3つに削減したため
                        )
                    )
                )
                content = response.text
                
            else:
                logger.warning(f"Selected provider {self.selected_provider} not available, using basic SWOT")
                return self._generate_basic_swot(analysis_data), ""
            
            # AIレスポンスを保存して返す（パース処理は後で）
            return self._parse_swot_response(content), content
            
        except Exception as e:
            error_msg = f"Error generating SWOT analysis with AI: {str(e)}"
            logger.error(error_msg)
            # エラーの種類に応じて詳細なログを出力
            if "api_key" in str(e).lower():
                logger.error(f"API key issue for provider {self.selected_provider}")
            elif "quota" in str(e).lower() or "429" in str(e):
                logger.error(f"Rate limit or quota exceeded for {self.selected_provider}")
            elif "timeout" in str(e).lower():
                logger.error(f"Request timeout for {self.selected_provider}")
            else:
                logger.error(f"Unexpected error with {self.selected_provider}: {type(e).__name__}")
            
            # 基本的なSWOT分析にフォールバック
            logger.info("Falling back to basic SWOT analysis")
            return self._generate_basic_swot(analysis_data), ""
    
    def _build_swot_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """SWOT分析用のプロンプトを構築（詳細データ統合版）"""
        clinic = analysis_data["clinic"]
        stats = analysis_data["market_stats"]
        competitors = analysis_data["competitors"]
        competitor_details = analysis_data.get("competitor_details", [])
        regional_data = analysis_data.get("regional_data", {})
        
        # 診療科の取得（新しいdepartmentフィールドまたは古いdepartmentsフィールドに対応）
        department = clinic.get('department') or ', '.join(clinic.get('departments', []))
        
        # トップ5件の競合情報を詳細に記載（Web検索情報も含む）
        top_competitors_info = ""
        for i, comp in enumerate(competitors[:5], 1):
            top_competitors_info += f"""
{i}. {comp.get('name', '不明')}
   - 評価: {comp.get('rating', 'N/A')} ({comp.get('user_ratings_total', 0)}件のレビュー)
   - 住所: {comp.get('formatted_address', comp.get('address', '不明'))}
   - 距離: {comp.get('distance', '不明')}m"""
            
            # Web検索で取得した詳細情報があれば追加
            for detail in competitor_details:
                if detail.get("clinic_name") == comp.get('name'):
                    if detail.get("extracted_info"):
                        top_competitors_info += "\n   - 特徴: " + str(detail["extracted_info"].get("特徴的なサービス", "詳細情報なし"))[:100]
                    if detail.get("online_presence"):
                        online = detail["online_presence"]
                        sns_presence = []
                        if online.get("has_twitter"): sns_presence.append("Twitter")
                        if online.get("has_instagram"): sns_presence.append("Instagram")
                        if online.get("has_facebook"): sns_presence.append("Facebook")
                        if sns_presence:
                            top_competitors_info += f"\n   - SNS展開: {', '.join(sns_presence)}"
            top_competitors_info += "\n"
        
        # 地域特性情報の整形
        regional_info = ""
        if regional_data.get("demographics"):
            demo = regional_data["demographics"]
            regional_info += f"""
【地域特性データ】
- 総人口: {self._format_number(demo.get('total_population'))}人
- 高齢化率（65歳以上）: {demo.get('age_distribution', {}).get('65+', 'N/A')}%
- 世帯数: {self._format_number(demo.get('household_count'))}世帯
- 人口密度: {self._format_number(demo.get('population_density'))}人/km²"""
        
        if regional_data.get("medical_demand"):
            demand = regional_data["medical_demand"]
            regional_info += f"""
- 推定患者数/日: {self._format_number(demand.get('estimated_patients_per_day'))}人
- 医療アクセシビリティ: {demand.get('healthcare_accessibility', 'N/A')}"""
        
        if regional_data.get("competition_density"):
            density = regional_data["competition_density"]
            regional_info += f"""
- 医療機関密度: {density.get('clinics_per_10000', 'N/A')}施設/万人"""
        
        # 医療統計データの整形（e-Stat API）
        medical_stats_info = ""
        medical_stats = analysis_data.get("medical_stats", {})
        
        if medical_stats:
            # 医療施設データ
            if facilities := medical_stats.get("medical_facilities", {}):
                medical_stats_info += "\n【医療施設統計】"
                medical_stats_info += f"\n- 地域内総診療所数: {facilities.get('total_clinics', 'N/A')}施設"
                if by_specialty := facilities.get("by_specialty", {}):
                    medical_stats_info += "\n- 診療科別施設数:"
                    for spec, count in list(by_specialty.items())[:5]:
                        medical_stats_info += f"\n  • {spec}: {count}施設"
                medical_stats_info += f"\n- 夜間救急対応: {facilities.get('night_emergency', 'N/A')}施設"
            
            # 患者統計データ
            if patient_stats := medical_stats.get("patient_stats", {}):
                medical_stats_info += "\n\n【患者需要統計】"
                medical_stats_info += f"\n- 外来受療率: {patient_stats.get('outpatient_rate', 'N/A')}/10万人"
                medical_stats_info += f"\n- 入院受療率: {patient_stats.get('hospitalization_rate', 'N/A')}/10万人"
                medical_stats_info += f"\n- 年間平均受診回数: {patient_stats.get('avg_consultation_per_year', 'N/A')}回"
                if top_diseases := patient_stats.get("top_diseases", []):
                    medical_stats_info += "\n- 主要疾患（受診理由）:"
                    for disease in top_diseases[:5]:
                        medical_stats_info += f"\n  • {disease['name']}: {disease['percentage']}%"
            
            # 医療従事者データ
            if medical_staff := medical_stats.get("medical_staff", {}):
                medical_stats_info += "\n\n【医療従事者統計】"
                medical_stats_info += f"\n- 医師密度: {medical_staff.get('doctors_per_100k', 'N/A')}/10万人"
                medical_stats_info += f"\n- 看護師密度: {medical_staff.get('nurses_per_100k', 'N/A')}/10万人"
                medical_stats_info += f"\n- 人材不足レベル: {medical_staff.get('shortage_level', 'N/A')}"
            
            # 世帯医療費データ
            if household := medical_stats.get("household_medical", {}):
                medical_stats_info += "\n\n【医療費支出統計】"
                medical_stats_info += f"\n- 年間平均医療費: {self._format_number(household.get('avg_annual_medical_expense', 0))}円"
                medical_stats_info += f"\n- 月間平均医療費: {self._format_number(household.get('avg_monthly_medical_expense', 0))}円"
                medical_stats_info += f"\n- 自己負担割合: {household.get('self_pay_ratio', 0)*100:.0f}%"
            
            # 介護施設データ
            if nursing := medical_stats.get("nursing_facilities", {}):
                medical_stats_info += "\n\n【介護施設統計】"
                medical_stats_info += f"\n- 総施設数: {nursing.get('total_facilities', 'N/A')}施設"
                medical_stats_info += f"\n- 総定員: {self._format_number(nursing.get('total_capacity', 0))}人"
                medical_stats_info += f"\n- 稼働率: {nursing.get('occupancy_rate', 0)*100:.0f}%"
        
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
医療経営コンサルタントとして、以下の包括的なデータから戦略的なSWOT分析と競争戦略を立案してください。

【自院プロファイル】
- 医療機関名: {clinic.get('name', '')}
- 立地: {clinic.get('address', '')}
- 標榜診療科: {department}
- 差別化要素: {clinic.get('features', '')}
- 主要ターゲット: {analysis_data.get('additional_context', '')}
{regional_info}

【医療圏分析データ】
- 診療圏域: 半径{analysis_data['clinic'].get('search_radius', 3000) / 1000}km
- 競合医療機関数: {stats['total_competitors']}院（同一診療圏内）
- 市場競争強度: {'高' if stats['total_competitors'] > 10 else '中' if stats['total_competitors'] > 5 else '低'}
- 平均患者満足度: {stats['average_rating']}/5.0
- 市場成熟度指標:
  - 高評価施設（4.0+）: {stats['rating_distribution']['above_4']}院（{stats['rating_distribution']['above_4'] / max(stats['total_competitors'], 1) * 100:.1f}%）
  - 中評価施設（3.0-4.0）: {stats['rating_distribution']['3_to_4']}院
  - 改善余地施設（<3.0）: {stats['rating_distribution']['below_3']}院

【競合ベンチマーク（上位施設・詳細分析付き）】
{top_competitors_info}

【診療科別競争環境】
{dept_distribution_info if dept_distribution_info else '- データ取得中'}
{medical_stats_info}

【患者ニーズ分析（口コミインサイト）】{review_analysis_info if review_analysis_info else chr(10) + '- 詳細データ取得中'}

【分析フレームワーク】
以下の医療経営指標と統計データを総合的に考慮して分析してください：
1. 患者アクセシビリティ（立地、診療時間、予約システム）
2. 医療サービスの質（専門性、設備、スタッフ対応）
3. 患者体験価値（待ち時間、院内環境、コミュニケーション）
4. 地域医療連携（病診連携、介護連携、在宅医療）
5. 経営効率性（集患力、リピート率、単価向上）
6. 市場需給バランス（受療率、医師密度、施設数から見た需給）
7. 疾患別需要（主要疾患の割合から見た専門性の機会）
8. 医療費市場規模（世帯医療費支出から見た市場ポテンシャル）

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

---

SWOT分析に基づき、以下の競争戦略を提案してください：

**競争優位戦略（3つの重点施策）**

1. **[施策名（20文字以内）]**
   - 実施内容: [具体的なアクションプラン（100文字程度）]
   - 優先度: [high/medium/lowのいずれか]
   - KPI: [測定可能な成果指標]
   - 想定ROI: [投資対効果の見込み]

2. **[施策名]**
   - 実施内容: [具体的なアクションプラン]
   - 優先度: [high/medium/lowのいずれか]
   - KPI: [測定可能な成果指標]
   - 想定ROI: [投資対効果の見込み]

3. **[施策名]**
   - 実施内容: [具体的なアクションプラン]
   - 優先度: [high/medium/lowのいずれか]
   - KPI: [測定可能な成果指標]
   - 想定ROI: [投資対効果の見込み]

【戦略立案の観点】
- SO戦略（強み×機会）：強みを活かして機会を最大化
- WO戦略（弱み×機会）：弱みを克服して機会を掴む
- ST戦略（強み×脅威）：強みを活かして脅威を回避
- WT戦略（弱み×脅威）：弱みを最小化し脅威を回避

特に以下の統計データから導かれる戦略を重視してください：
- 主要疾患データ → 専門性強化の方向性
- 医師不足レベル → 人材確保・差別化戦略
- 介護施設稼働率 → 連携強化の可能性
- 世帯医療費 → 価格戦略・サービス設計
"""
        return prompt
    
    def _parse_swot_and_recommendations_response(self, content: str) -> Dict[str, Any]:
        """AIの応答をパースしてSWOTと戦略的提案を抽出"""
        result = {
            "swot": {
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": []
            },
            "recommendations": []
        }
        
        # Nullチェックとデフォルト値の返却
        if not content:
            logger.warning("Content is None or empty, returning default SWOT structure")
            return result
        
        current_section = None
        in_recommendations = False
        current_recommendation = None
        
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
            line_stripped = line.strip()
            
            # 戦略的提案セクションの開始を識別
            if "戦略的提案" in line_stripped and "**" in line_stripped:
                in_recommendations = True
                current_section = None
                continue
            
            # SWOT分析セクションの処理
            if not in_recommendations:
                # セクションの識別
                for key, section in section_map.items():
                    if key in line_stripped and "**" in line_stripped:
                        current_section = section
                        break
                
                # SWOT項目の抽出
                if current_section and line_stripped.startswith('- '):
                    item = line_stripped[2:].strip()
                    if item and not item.startswith('['):
                        result["swot"][current_section].append(item)
            
            # 戦略的提案セクションの処理
            else:
                # 新しい提案の開始（番号付きタイトル）
                if line_stripped and (line_stripped[0].isdigit() and '.' in line_stripped[:3]):
                    if current_recommendation:
                        result["recommendations"].append(current_recommendation)
                    
                    # タイトルを抽出
                    title = line_stripped.split('**')[1] if '**' in line_stripped else line_stripped[3:].strip()
                    current_recommendation = {
                        "title": title,
                        "description": "",
                        "priority": "medium",
                        "expected_effect": ""
                    }
                
                # 提案の詳細情報を抽出
                elif current_recommendation and line_stripped.startswith('- '):
                    detail = line_stripped[2:].strip()
                    if detail.startswith('内容:'):
                        current_recommendation["description"] = detail[3:].strip()
                    elif detail.startswith('優先度:'):
                        priority_text = detail[4:].strip().lower()
                        if 'high' in priority_text or '高' in priority_text:
                            current_recommendation["priority"] = "high"
                        elif 'low' in priority_text or '低' in priority_text:
                            current_recommendation["priority"] = "low"
                        else:
                            current_recommendation["priority"] = "medium"
                    elif detail.startswith('期待効果:'):
                        current_recommendation["expected_effect"] = detail[5:].strip()
        
        # 最後の提案を追加
        if current_recommendation:
            result["recommendations"].append(current_recommendation)
        
        return result
    
    def _parse_swot_response(self, content: str) -> Dict[str, List[str]]:
        """AIの応答をパースしてSWOT辞書に変換（後方互換性のため維持）"""
        parsed = self._parse_swot_and_recommendations_response(content)
        return parsed["swot"]
    
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
        analysis_data: Dict[str, Any],
        ai_response: str = ""
    ) -> List[Dict[str, str]]:
        """戦略的提案を生成（AIレスポンスから抽出またはフォールバック）"""
        
        recommendations = []
        
        # AIレスポンスから戦略提案を抽出
        if ai_response:
            try:
                parsed = self._parse_swot_and_recommendations_response(ai_response)
                if parsed["recommendations"]:
                    # AIが生成した提案を使用
                    for rec in parsed["recommendations"]:
                        # descriptionが空の場合はexpected_effectを使用
                        description = rec["description"] if rec["description"] else rec.get("expected_effect", "")
                        recommendations.append({
                            "title": rec["title"],
                            "description": description,
                            "priority": rec["priority"]
                        })
                    
                    # AIの提案がある場合はそれを返す
                    if recommendations:
                        return recommendations
            except Exception as e:
                logger.warning(f"Failed to parse recommendations from AI response: {e}")
        
        # フォールバック：基本的な戦略提案を生成
        if analysis_data["market_stats"]["total_competitors"] > 10:
            recommendations.append({
                "title": "差別化戦略の強化",
                "description": "競合が多いエリアでは、独自の強みを明確に打ち出す必要があります。専門性の高い診療や独自のサービスを検討しましょう。",
                "priority": "high"
            })
        
        if analysis_data["market_stats"]["average_rating"] > 4:
            recommendations.append({
                "title": "サービス品質の向上",
                "description": "競合の評価が高いため、患者満足度を向上させる取り組みが重要です。待ち時間短縮や接遇改善を実施しましょう。",
                "priority": "high"
            })
        
        # SWOT分析の内容を活用した提案
        if swot_analysis.get("opportunities"):
            for opportunity in swot_analysis["opportunities"][:1]:  # 最初の機会を活用
                recommendations.append({
                    "title": "市場機会の活用",
                    "description": f"{opportunity}を活かした戦略的な施策を展開しましょう。",
                    "priority": "high"
                })
        
        if swot_analysis.get("weaknesses"):
            recommendations.append({
                "title": "弱点の改善",
                "description": f"課題となっている{swot_analysis['weaknesses'][0]}の改善に取り組みましょう。",
                "priority": "medium"
            })
        
        # デフォルトの提案
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
        
        return recommendations[:3]  # 最大3つの提案を返す