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
from backend.services import crud

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
            self.settings = crud.read_settings()
            # 新しいフィールド名を使用（models.text_api_model）
            if self.settings and hasattr(self.settings, 'models') and self.settings.models:
                self.selected_model = self.settings.models.text_api_model or "gpt-4-turbo-preview"
                # プロバイダーを自動判定（より確実な判定）
                model_lower = self.selected_model.lower()
                
                # OpenAI models: gpt-*, o1-*, dall-e-*
                if any(prefix in model_lower for prefix in ["gpt-", "o1-", "dall-e"]):
                    self.selected_provider = "openai"
                # Anthropic models: claude-*
                elif "claude" in model_lower:
                    self.selected_provider = "anthropic"
                # Google models: gemini-*, flash
                elif "gemini" in model_lower or "flash" in model_lower:
                    self.selected_provider = "google"
                # Default fallback
                else:
                    # デフォルトはOpenAIとするが、警告を出す
                    logger.warning(f"Unknown model format: {self.selected_model}, defaulting to OpenAI provider")
                    self.selected_provider = "openai"
                
                logger.info(f"CompetitiveAnalysisService initialized with model: {self.selected_model}, provider: {self.selected_provider}")
            else:
                # デフォルト設定
                self.selected_model = "gpt-4-turbo-preview"
                self.selected_provider = "openai"
                logger.info(f"No settings found, using defaults - model: {self.selected_model}, provider: {self.selected_provider}")
        except Exception as e:
            logger.warning(f"Failed to read settings: {e}")
            self.selected_model = "gpt-4-turbo-preview"
            self.selected_provider = "openai"
            logger.info(f"Error reading settings, using defaults - model: {self.selected_model}, provider: {self.selected_provider}")
    
    async def analyze_competition(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """競合分析を実行"""
        try:
            # 基本情報を取得
            clinic_info = request_data.get("clinic_info", request_data.get("clinic", {}))
            address = clinic_info.get("address", "")
            
            # 検索半径を取得（search_radiusまたはradiusフィールドから）
            search_radius = request_data.get("search_radius", clinic_info.get("radius", 3000))
            logger.info(f"Using search radius: {search_radius}m for address: {address}")
            
            # 1. 競合医院を検索
            competitors_data = await self.google_maps.search_nearby_clinics(
                location=address,  # パラメータ名を location に修正
                radius=search_radius,
                department_types=[clinic_info.get("department", "")] if clinic_info.get("department") else None
            )
            
            # 2. 地域データと医療統計を取得
            regional_data = await self.regional_data.get_regional_data(address)
            medical_stats = await self.medical_stats_service.get_comprehensive_medical_stats(address)
            
            # 3. 競合の詳細情報を整理（上位5件のみ、Google Maps APIデータを活用）
            top_competitors = competitors_data.get("competitors", [])[:5]
            competitor_details = []
            
            for comp in top_competitors:
                clinic_name = comp.get("name", "")
                
                # Google Maps APIから取得済みのデータを整理
                competitor_details.append({
                    "clinic_name": clinic_name,
                    "basic_info": comp,
                    "google_maps_data": {
                        "rating": comp.get("rating"),
                        "reviews_count": comp.get("user_ratings_total", 0),
                        "phone": comp.get("phone_number"),
                        "website": comp.get("website"),
                        "opening_hours": comp.get("opening_hours"),
                        "reviews": comp.get("reviews", [])
                    }
                })
            
            # TODO: 将来的にWeb検索機能を追加
            # if self.web_research and self.serpapi_key:
            #     web_info = await self.web_research.research_competitor(...)
            
            logger.info(f"Analyzed {len(competitor_details)} competitors using Google Maps data")
            
            # 分析データを構築
            analysis_data = {
                "clinic": clinic_info,
                "competitors": competitors_data.get("competitors", []),
                "competitor_details": competitor_details,
                "market_stats": competitors_data.get("market_stats", {}),
                "regional_data": regional_data,
                "medical_stats": medical_stats
            }
            
            # 4. SWOT分析と戦略的提案を生成
            swot_analysis, raw_response = await self._generate_swot_analysis(analysis_data)
            
            # 5. 結果を整形して返す
            return {
                "success": True,
                "data": {
                    "clinic": clinic_info,
                    "competitors": competitors_data.get("competitors", []),
                    "competitor_details": competitor_details,
                    "market_analysis": {
                        "total_competitors": competitors_data.get("total_results", 0),
                        "search_radius": search_radius,
                        "market_stats": competitors_data.get("market_stats", {}),
                        "regional_data": regional_data,
                        "medical_stats": medical_stats
                    },
                    "swot_analysis": swot_analysis,
                    "ai_response": raw_response,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Competition analysis error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def _format_number(self, value: Any) -> str:
        """数値をカンマ区切りでフォーマット"""
        if value is None or value == 'N/A':
            return 'N/A'
        try:
            if isinstance(value, (int, float)):
                return f"{int(value):,}"
            return str(value)
        except:
            return str(value)
    
    def _analyze_market_stats(self, competitors: List[Dict], 
                            competitor_details: List[Dict], 
                            regional_data: Dict) -> Dict[str, Any]:
        """市場統計を分析"""
        if not competitors:
            return {
                "average_rating": 0,
                "total_reviews": 0,
                "rating_distribution": {},
                "department_distribution": {}
            }
        
        # 基本統計
        ratings = [c.get("rating", 0) for c in competitors if c.get("rating")]
        total_reviews = sum(c.get("user_ratings_total", 0) for c in competitors)
        
        # 診療科分布
        department_distribution = {}
        for comp in competitors:
            dept = comp.get("department", "不明")
            department_distribution[dept] = department_distribution.get(dept, 0) + 1
        
        # Google Maps APIから取得したレビュー情報を統合
        additional_info = []
        review_insights = []
        
        for detail in competitor_details:
            maps_data = detail.get("google_maps_data", {})
            
            # 追加情報を収集（ウェブサイトの有無、営業時間など）
            if maps_data.get("website") or maps_data.get("opening_hours"):
                info = {
                    "clinic": detail["clinic_name"],
                    "has_website": bool(maps_data.get("website")),
                    "has_hours": bool(maps_data.get("opening_hours"))
                }
                additional_info.append(info)
            
            # Google Mapsのレビューを統合
            if maps_data.get("reviews"):
                for review in maps_data["reviews"][:3]:  # 上位3件のみ
                    review_insights.append({
                        "clinic": detail["clinic_name"],
                        "rating": review.get("rating"),
                        "text": review.get("text", "")[:200] if review.get("text") else ""
                    })
        
        return {
            "average_rating": round(sum(ratings) / len(ratings), 1) if ratings else 0,
            "total_reviews": total_reviews,
            "rating_distribution": {
                "5_star": len([r for r in ratings if r >= 4.5]),
                "4_star": len([r for r in ratings if 3.5 <= r < 4.5]),
                "below_3": len([r for r in ratings if r < 3])
            },
            "department_distribution": department_distribution,
            "review_insights": review_insights,
            "additional_context": additional_info or ""
        }
    
    async def _generate_swot_analysis(self, analysis_data: Dict[str, Any]) -> Tuple[Dict[str, List[str]], str]:
        """SWOT分析と戦略的提案を生成（管理画面設定のモデルを使用）"""
        
        try:
            prompt = self._build_swot_prompt(analysis_data)
            system_prompt = "あなたは医療機関の経営コンサルタントです。提供された情報を基に、具体的で実行可能なSWOT分析と戦略的提案を行ってください。"
            
            # 管理画面で設定されたモデルを使用
            print("="*60)
            print("[CompetitiveAnalysis] ===== GENERATING SWOT ANALYSIS & RECOMMENDATIONS =====")
            print(f"[CompetitiveAnalysis] Provider: {self.selected_provider}")
            print(f"[CompetitiveAnalysis] Model: {self.selected_model}")
            print("="*60)
            
            # APIキーを確認
            api_key = None
            if self.selected_provider == "openai":
                api_key = self.openai_api_key
            elif self.selected_provider == "anthropic":
                api_key = self.anthropic_api_key
            elif self.selected_provider == "google":
                api_key = self.google_api_key
            
            if not api_key:
                logger.error(f"API key not configured for provider: {self.selected_provider}")
                logger.info("Falling back to basic SWOT analysis")
                return self._generate_basic_swot(analysis_data), ""
            
            # 設定されたプロバイダーでSWOT分析を生成
            try:
                content = await self._call_ai_provider(
                    self.selected_provider,
                    self.selected_model,
                    api_key,
                    system_prompt,
                    prompt
                )
                
                # contentがNoneまたは空の場合の処理
                if content and isinstance(content, str) and len(content.strip()) > 0:
                    logger.info(f"Successfully generated SWOT analysis using {self.selected_provider}/{self.selected_model}")
                    return self._parse_swot_response(content), content
                else:
                    logger.warning(f"No content or empty content generated from {self.selected_provider}")
                    logger.info("Falling back to basic SWOT analysis")
                    return self._generate_basic_swot(analysis_data), ""
                    
            except Exception as e:
                error_msg = f"Error with {self.selected_provider}: {str(e)}"
                logger.error(error_msg)
                
                # エラーの種類をログに記録
                if "insufficient_quota" in str(e) or "429" in str(e):
                    logger.error(f"Quota exceeded for {self.selected_provider}")
                elif "timeout" in str(e).lower():
                    logger.error(f"Request timeout for {self.selected_provider}")
                elif "api_key" in str(e).lower():
                    logger.error(f"API key issue for {self.selected_provider}")
                
                # 基本的なSWOT分析にフォールバック
                logger.info("Falling back to basic SWOT analysis")
                return self._generate_basic_swot(analysis_data), ""
            
        except Exception as e:
            error_msg = f"Error generating SWOT analysis: {str(e)}"
            logger.error(error_msg)
            logger.info("Falling back to basic SWOT analysis")
            return self._generate_basic_swot(analysis_data), ""
    
    async def _call_ai_provider(self, provider: str, model: str, api_key: str, system_prompt: str, prompt: str) -> str:
        """AIプロバイダーを呼び出してレスポンスを取得"""
        if provider == "openai" and openai_available:
            client = OpenAI(api_key=api_key, timeout=30.0)
            # GPT-5 uses max_completion_tokens instead of max_tokens
            if "gpt-5" in model:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_completion_tokens=2000
                )
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
            content = response.choices[0].message.content
            logger.info(f"OpenAI response length: {len(content) if content else 0} characters")
            return content
            
        elif provider == "anthropic" and anthropic_available:
            client = Anthropic(api_key=api_key, timeout=30.0)
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
            
        elif provider == "google":
            # 旧SDKも試すため、インポートを確認
            try:
                import google.generativeai as old_gemini_sdk
                old_sdk_available = True
            except ImportError:
                old_sdk_available = False
            
            # 新SDKを優先的に試す（新しいasync APIを使用）
            if google_genai_available:
                try:
                    client = google_genai_sdk.Client(api_key=api_key)
                    
                    logger.info(f"Using new Gemini SDK with model: {model}")
                    # 新しいSDKのasync API: client.models.generate_content
                    response = await client.models.generate_content(
                        model=model,
                        contents=f"{system_prompt}\n\n{prompt}",
                        config=google_genai_types.GenerateContentConfig(
                            temperature=0.7,
                            max_output_tokens=2000
                        )
                    )
                    
                    # レスポンス処理
                    if hasattr(response, 'text') and response.text:
                        logger.info("Successfully got response from new Gemini SDK")
                        return response.text
                    
                    logger.warning(f"New SDK returned empty response for model {model}")
                    
                except Exception as e:
                    logger.warning(f"New SDK failed: {e}")
                    # 旧SDKにフォールバック
            
            # 旧SDKを試す
            if old_sdk_available:
                try:
                    logger.info(f"Trying old Gemini SDK with model: {model}")
                    old_gemini_sdk.configure(api_key=api_key)
                    old_model = old_gemini_sdk.GenerativeModel(model)
                    response = old_model.generate_content(f"{system_prompt}\n\n{prompt}")
                    
                    if hasattr(response, 'text') and response.text:
                        logger.info("Successfully got response from old Gemini SDK")
                        return response.text
                    
                    logger.warning(f"Old SDK returned empty response for model {model}")
                    
                except Exception as e:
                    logger.error(f"Old SDK also failed: {e}")
            
            logger.error(f"Both Gemini SDKs failed or returned empty for model {model}")
            return None
        else:
            raise Exception(f"Provider {provider} not available")
    
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
            
            # Google Maps APIから取得した詳細情報を追加
            for detail in competitor_details:
                if detail.get("clinic_name") == comp.get('name'):
                    maps_data = detail.get("google_maps_data", {})
                    if maps_data.get("website"):
                        top_competitors_info += f"\n   - ウェブサイト: あり"
                    if maps_data.get("phone"):
                        top_competitors_info += f"\n   - 電話番号: {maps_data['phone']}"
                    if maps_data.get("opening_hours"):
                        top_competitors_info += f"\n   - 営業時間情報: あり"
                    if maps_data.get("reviews"):
                        review_count = len(maps_data.get("reviews", []))
                        if review_count > 0:
                            top_competitors_info += f"\n   - 最近のレビュー: {review_count}件"
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
- 推定患者数: {self._format_number(demand.get('estimated_patients'))}人/月
- 需要レベル: {demand.get('demand_level', 'N/A')}"""
        
        prompt = f"""
以下の情報を基に、医療機関のSWOT分析と戦略的提案を行ってください。

【クリニック情報】
- 名称: {clinic.get('name', '未入力')}
- 診療科: {department}
- 住所: {clinic.get('address', '未入力')}
- 強み・特徴: {clinic.get('strengths', '未入力')}
- ターゲット層: {clinic.get('target_patients', '未入力')}

【市場分析】
- 競合数: {len(competitors)}件（半径{clinic.get('radius', 3000)}m内）
- 平均評価: {stats.get('average_rating', 'N/A')}
- 総レビュー数: {stats.get('total_reviews', 0)}件

【主要競合医院】
{top_competitors_info}

{regional_info}

以下の形式でSWOT分析と戦略的提案を作成してください：

## SWOT分析

### 強み（Strengths）
- （最大3項目、各項目は具体的に）

### 弱み（Weaknesses）
- （最大3項目、各項目は具体的に）

### 機会（Opportunities）
- （最大3項目、地域特性や市場動向を踏まえて）

### 脅威（Threats）
- （最大3項目、競合状況を踏まえて）

## 戦略的提案

### 差別化戦略
（競合との差別化を図るための具体的な施策を1つ提案）

### マーケティング戦略
（ターゲット層にリーチするための具体的な施策を1つ提案）

### オペレーション改善
（業務効率化や患者満足度向上のための具体的な施策を1つ提案）
"""
        
        return prompt
    
    def _parse_swot_response(self, response: str) -> Dict[str, List[str]]:
        """AIレスポンスからSWOT要素を抽出"""
        try:
            swot = {
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": [],
                "strategies": []
            }
            
            # Noneチェックと型チェック
            if not response or not isinstance(response, str):
                logger.warning("Invalid response for SWOT parsing")
                return swot
            
            # 各セクションを抽出
            sections = {
                "強み": "strengths",
                "弱み": "weaknesses",
                "機会": "opportunities",
                "脅威": "threats"
            }
            
            lines = response.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # セクションヘッダーを検出
                for jp_name, en_name in sections.items():
                    if jp_name in line:
                        current_section = en_name
                        break
                
                # 戦略セクションの検出
                if any(keyword in line for keyword in ["戦略", "提案"]):
                    current_section = "strategies"
                
                # 項目を抽出（箇条書きの場合）
                if current_section and line.startswith(('-', '・', '●', '○', '■', '□', '*')):
                    item = line.lstrip('-・●○■□* ').strip()
                    if item and len(item) > 5:  # 短すぎる項目は除外
                        swot[current_section].append(item)
            
            # 最小限の項目を確保
            if not swot["strengths"]:
                swot["strengths"] = ["専門性の高い医療サービス", "経験豊富な医療スタッフ"]
            if not swot["weaknesses"]:
                swot["weaknesses"] = ["認知度の向上が必要", "デジタルマーケティングの強化が必要"]
            if not swot["opportunities"]:
                swot["opportunities"] = ["地域の高齢化による需要増", "予防医療への関心の高まり"]
            if not swot["threats"]:
                swot["threats"] = ["近隣競合医院との競争", "患者の大病院志向"]
            if not swot["strategies"]:
                swot["strategies"] = [
                    "SNSを活用した情報発信の強化",
                    "予約システムの導入による利便性向上",
                    "地域連携の強化"
                ]
            
            return swot
            
        except Exception as e:
            logger.error(f"Error parsing SWOT response: {e}")
            return self._generate_basic_swot({})
    
    def _generate_basic_swot(self, analysis_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """基本的なSWOT分析を生成（AIが使えない場合のフォールバック）"""
        competitors = analysis_data.get("competitors", [])
        regional_data = analysis_data.get("regional_data", {})
        
        # 競合状況に基づく基本分析
        competitor_count = len(competitors)
        high_competition = competitor_count > 10
        
        strengths = [
            "地域に密着した医療サービスの提供",
            "患者一人一人に寄り添った診療体制"
        ]
        
        weaknesses = [
            "Web上での情報発信の強化が必要" if high_competition else "認知度向上の余地あり",
            "オンライン予約システムの導入検討"
        ]
        
        opportunities = [
            f"地域人口{regional_data.get('population', {}).get('total', 'N/A')}人の医療ニーズ",
            "高齢化に伴う医療需要の増加",
            "予防医療への関心の高まり"
        ]
        
        threats = [
            f"半径3km圏内に{competitor_count}件の競合医院",
            "大規模病院への患者流出リスク",
            "医療従事者の確保競争"
        ]
        
        strategies = [
            "デジタルマーケティングの強化（SEO対策、SNS活用）",
            "地域住民向けの健康セミナー開催",
            "他医療機関との連携強化",
            "患者満足度向上のための取り組み強化"
        ]
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats,
            "strategies": strategies
        }