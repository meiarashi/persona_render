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
                "medical_stats": medical_stats,
                "search_radius": search_radius  # 検索半径を追加
            }
            
            # 4. SWOT分析と戦略的提案を生成
            swot_analysis, raw_response = await self._generate_swot_analysis(analysis_data)

            # 戦略提案を抽出
            strategic_recommendations = self._parse_strategic_recommendations(raw_response)

            # 5. 結果を整形して返す
            return {
                "success": True,
                "data": {
                    "clinic": clinic_info,
                    "center": competitors_data.get("center"),  # 自院の座標を追加
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
                    "strategic_recommendations": strategic_recommendations,  # 構造化された戦略提案
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
                    
                    # 弱みセクションが含まれているか事前チェック
                    if "弱み" not in content and "Weaknesses" not in content:
                        logger.error("[SWOT Parser] WARNING: AI response does not contain '弱み' keyword!")
                    
                    # AI応答全体を一時的にファイルに保存してデバッグ
                    import os
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='_swot_response.txt', delete=False, encoding='utf-8') as f:
                        f.write(content)
                        logger.info(f"[SWOT Parser] Full AI response saved to: {f.name} for debugging")
                    
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
                    logger.error(f"Request timeout for {self.selected_provider} - consider using a faster model or reducing prompt size")
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
            client = OpenAI(api_key=api_key, timeout=90.0)  # タイムアウトを90秒に延長

            # GPT-5は新しいresponses APIを使用（ペルソナ生成と同じパターン）
            if "gpt-5" in model:
                try:
                    # 新しいresponses APIを使用（システムプロンプトとユーザープロンプトを結合）
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                    response = client.responses.create(
                        model="gpt-5",
                        input=full_prompt,
                        reasoning={"effort": "high"}  # 競合分析も詳細な推論が必要なのでhighに変更
                    )
                    content = response.output_text
                    logger.info(f"GPT-5 responses API - response length: {len(content) if content else 0} characters")
                    return content
                except Exception as e:
                    logger.error(f"GPT-5 responses API error: {str(e)}")

                    # chat.completions APIでリトライ（ペルソナ生成と同じパターン）
                    try:
                        # GPT-5では role: user のみを使用（システムプロンプトも含めて単一メッセージ）
                        full_prompt = f"{system_prompt}\n\n{prompt}"
                        response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": full_prompt}],  # ユーザーロールのみ
                            temperature=1.0,  # GPT-5はデフォルト値のみサポート
                            max_completion_tokens=4000  # SWOT分析は詳細な出力が必要なため増加
                        )
                        content = response.choices[0].message.content if response.choices else None
                        logger.info(f"GPT-5 chat API fallback - response length: {len(content) if content else 0} characters")
                        return content
                    except Exception as e2:
                        logger.error(f"GPT-5 chat API error: {str(e2)}")
                        return None
            else:
                # GPT-4以前のモデル（従来通りシステムとユーザーを分ける）
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=128000  # GPT-5最大値
                )
                content = response.choices[0].message.content if response.choices else None
                logger.info(f"OpenAI response length: {len(content) if content else 0} characters")
                return content
            
        elif provider == "anthropic" and anthropic_available:
            client = Anthropic(api_key=api_key, timeout=90.0)  # タイムアウトを90秒に延長
            # ペルソナ生成と同じパターン：システムプロンプトとユーザープロンプトを結合
            full_prompt = f"{system_prompt}\n\n{prompt}"
            response = client.messages.create(
                model=model,
                max_tokens=64000,  # Claude Sonnet 4最大値
                temperature=0.7,
                messages=[{"role": "user", "content": full_prompt}]  # systemパラメータを使わない
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
                    # タイムアウト設定付きのクライアントを作成
                    import httpx
                    http_client = httpx.Client(timeout=90.0)  # 90秒のタイムアウト
                    client = google_genai_sdk.Client(api_key=api_key, http_client=http_client)
                    
                    logger.info(f"Using new Gemini SDK with model: {model} (timeout: 90s)")
                    # 新しいSDKは同期API（awaitは不要）
                    # ペルソナ生成と同じパターン：システムプロンプトとユーザープロンプトを結合
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                    response = client.models.generate_content(
                        model=model,
                        contents=full_prompt,  # ペルソナ生成と同じ形式
                        config=google_genai_types.GenerateContentConfig(
                            temperature=0.7,
                            max_output_tokens=8192  # Gemini Pro実際の制限
                        )
                    )

                    # レスポンス処理（ペルソナ生成と同じパターン）
                    logger.info(f"[Gemini] Response type: {type(response)}")
                    if hasattr(response, 'candidates'):
                        logger.info(f"[Gemini] Candidates count: {len(response.candidates) if response.candidates else 0}")

                    if response.candidates and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if candidate.content and candidate.content.parts:
                            generated_text = candidate.content.parts[0].text
                            logger.info(f"[Gemini] Successfully got response from new SDK: {len(generated_text)} chars")
                            
                            # 弱みセクションが完全に含まれているかチェック
                            if "弱み" in generated_text:
                                weaknesses_idx = generated_text.find("弱み")
                                logger.info(f"[Gemini] '弱み' found at index {weaknesses_idx}")
                                # 弱みセクション周辺を確認
                                context = generated_text[max(0, weaknesses_idx-50):min(len(generated_text), weaknesses_idx+500)]
                                logger.info(f"[Gemini] Context around '弱み': {repr(context)}")
                                
                                # "..."で終わっているかチェック
                                if "..." in context:
                                    logger.warning("[Gemini] Found '...' in weaknesses context - possible truncation!")
                                    
                                # 次のセクション（機会）があるかチェック  
                                if "機会" in generated_text[weaknesses_idx:]:
                                    opportunities_idx = generated_text[weaknesses_idx:].find("機会") + weaknesses_idx
                                    logger.info(f"[Gemini] '機会' found after '弱み' at index {opportunities_idx}")
                                    weaknesses_content = generated_text[weaknesses_idx:opportunities_idx]
                                    logger.info(f"[Gemini] Weaknesses section length: {len(weaknesses_content)} chars")
                                    # 弱みセクションに複数の改行があるかチェック
                                    newline_count = weaknesses_content.count('\n')
                                    logger.info(f"[Gemini] Newlines in weaknesses section: {newline_count}")
                            return generated_text
                        else:
                            logger.warning(f"[Gemini] Candidate has no content or parts")
                    else:
                        logger.warning(f"[Gemini] Response has no candidates")

                    logger.warning(f"[Gemini] New SDK returned empty response for model {model}")
                    
                except Exception as e:
                    logger.warning(f"New SDK failed: {e}")
                    # 旧SDKにフォールバック
            
            # 旧SDKを試す
            if old_sdk_available:
                try:
                    logger.info(f"Trying old Gemini SDK with model: {model}")
                    old_gemini_sdk.configure(api_key=api_key)

                    # 生成設定を追加
                    generation_config = {
                        "temperature": 0.7,
                        "max_output_tokens": 64000,  # Gemini 2.5 Pro最大値（実際の制限）
                    }

                    old_model = old_gemini_sdk.GenerativeModel(
                        model_name=model,
                        generation_config=generation_config
                    )
                    # ペルソナ生成と同じパターン：システムプロンプトとユーザープロンプトを結合
                    full_prompt = f"{system_prompt}\n\n{prompt}"
                    response = old_model.generate_content(full_prompt)
                    
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
        
        # デバッグ用：プロンプトに含まれるデータを確認
        logger.info(f"Building SWOT prompt with data:")
        logger.info(f"- Clinic name: {clinic.get('name', 'Not provided')}")
        logger.info(f"- Department: {department or 'Not specified'}")
        logger.info(f"- Address: {clinic.get('address', 'Not provided')}")
        logger.info(f"- Number of competitors: {len(competitors)}")
        logger.info(f"- Regional data available: {bool(regional_data)}")
        if regional_data.get("demographics"):
            logger.info(f"  - Population: {regional_data['demographics'].get('total_population', 'N/A')}")
            logger.info(f"  - Aging rate: {regional_data['demographics'].get('age_distribution', {}).get('65+', 'N/A')}%")
        
        prompt = f"""
以下の情報を基に、医療機関のSWOT分析と戦略的提案をJSON形式で出力してください。

【クリニック情報】
- 名称: {clinic.get('name', '未入力')}
- 診療科: {department}
- 住所: {clinic.get('address', '未入力')}
- 強み・特徴: {clinic.get('features', clinic.get('strengths', '未入力'))}
- ターゲット層: {clinic.get('target_patients', '未入力')}

【市場分析】
- 競合数: {len(competitors)}件（半径{analysis_data.get('search_radius', clinic.get('radius', 3000))}m内）
- 平均評価: {stats.get('average_rating', 'N/A')}
- 総レビュー数: {stats.get('total_reviews', 0)}件

【主要競合医院】
{top_competitors_info if top_competitors_info else "競合医院情報なし"}

{regional_info if regional_info else "【地域特性データ】" + chr(10) + "地域データ取得できませんでした"}

必ず以下のJSON形式で出力してください。余計な説明や前置きは不要です：
{{
    "強み": [
        "具体的な強み1の説明",
        "具体的な強み2の説明",
        "具体的な強み3の説明"
    ],
    "弱み": [
        "入力された課題や競合比較での劣位点1",
        "改善が必要な領域1",
        "その他の弱み1"
    ],
    "機会": [
        "地域特性を踏まえた機会1",
        "市場動向から見た機会1",
        "その他の機会1"
    ],
    "脅威": [
        "競合状況から見た脅威1",
        "市場環境の脅威1",
        "その他の脅威1"
    ],
    "差別化戦略": [
        "競合との差別化ポイント1と実現方法",
        "競合との差別化ポイント2と実現方法",
        "競合との差別化ポイント3と実現方法"
    ],
    "マーケティング戦略": [
        "集患・集客のための具体的施策1とターゲット層",
        "集患・集客のための具体的施策2とターゲット層",
        "集患・集客のための具体的施策3とターゲット層"
    ],
    "オペレーション改善": [
        "業務効率化や患者満足度向上のための施策1と改善方法",
        "業務効率化や患者満足度向上のための施策2と改善方法",
        "業務効率化や患者満足度向上のための施策3と改善方法"
    ]
}}
"""
        
        return prompt
    
    def _parse_strategic_recommendations(self, response: str) -> List[Dict[str, str]]:
        """AIレスポンスから戦略提案を抽出して構造化"""
        logger.info("="*60)
        logger.info("[Strategy Parser] Starting to parse strategic recommendations")

        recommendations = []

        if not response or not isinstance(response, str):
            logger.warning("[Strategy Parser] Invalid response, using defaults")
            return self._get_default_recommendations()

        try:
            lines = response.split('\n')
            current_strategy = None
            current_content = []

            for line in lines:
                line = line.strip()

                # 戦略カテゴリを検出（### で始まるか、戦略名が含まれる行）
                strategy_found = False
                if ("### 差別化戦略" in line or "##差別化戦略" in line or
                    "## 差別化戦略" in line or "###差別化戦略" in line or
                    line == "差別化戦略" or
                    (line.startswith("差別化戦略") and len(line) < 30)):
                    # 前の戦略を保存
                    if current_strategy and current_content:
                        logger.info(f"[Strategy Parser] Saving {current_strategy}: {len(current_content)} lines")
                        recommendations.append({
                            "title": current_strategy,
                            "description": " ".join(current_content),
                            "priority": "high"
                        })
                    logger.info(f"[Strategy Parser] Found 差別化戦略 in line: {line[:100]}")
                    current_strategy = "差別化戦略"
                    current_content = []
                    strategy_found = True

                elif ("### マーケティング戦略" in line or "##マーケティング戦略" in line or
                      "## マーケティング戦略" in line or "###マーケティング戦略" in line or
                      line == "マーケティング戦略" or
                      (line.startswith("マーケティング戦略") and len(line) < 30)):
                    if current_strategy and current_content:
                        logger.info(f"[Strategy Parser] Saving {current_strategy}: {len(current_content)} lines")
                        recommendations.append({
                            "title": current_strategy,
                            "description": " ".join(current_content),
                            "priority": "high" if current_strategy == "差別化戦略" else "medium"
                        })
                    logger.info(f"[Strategy Parser] Found マーケティング戦略 in line: {line[:100]}")
                    current_strategy = "マーケティング戦略"
                    current_content = []
                    strategy_found = True

                elif ("### オペレーション改善" in line or "##オペレーション改善" in line or
                      "## オペレーション改善" in line or "###オペレーション改善" in line or
                      line == "オペレーション改善" or
                      (line.startswith("オペレーション改善") and len(line) < 30)):
                    if current_strategy and current_content:
                        logger.info(f"[Strategy Parser] Saving {current_strategy}: {len(current_content)} lines")
                        recommendations.append({
                            "title": current_strategy,
                            "description": " ".join(current_content),
                            "priority": "high" if current_strategy == "差別化戦略" else "medium"
                        })
                    logger.info(f"[Strategy Parser] Found オペレーション改善 in line: {line[:100]}")
                    current_strategy = "オペレーション改善"
                    current_content = []
                    strategy_found = True

                # 内容を収集（戦略ヘッダーでない場合）
                if not strategy_found and current_strategy and line and not line.startswith('#'):
                    # 箇条書き記号を除去
                    content = line
                    for marker in ['・', '-', '●', '○', '■', '□', '*']:
                        if line.startswith(marker):
                            content = line[len(marker):].strip()
                            break
                    # 括弧も除去
                    content = content.lstrip('（(').rstrip('）)')

                    if content and len(content) > 3:
                        current_content.append(content)

            # 最後の戦略を保存
            if current_strategy and current_content:
                priority = "high" if current_strategy == "差別化戦略" else "medium"
                recommendations.append({
                    "title": current_strategy,
                    "description": " ".join(current_content),
                    "priority": priority
                })

            # 重複をチェックして削除
            unique_recommendations = []
            seen_titles = set()
            for rec in recommendations:
                if rec['title'] not in seen_titles:
                    unique_recommendations.append(rec)
                    seen_titles.add(rec['title'])
                else:
                    logger.warning(f"[Strategy Parser] Duplicate strategy found and removed: {rec['title']}")

            # 結果をログ出力
            logger.info("="*60)
            logger.info(f"[Strategy Parser] Found {len(unique_recommendations)} unique strategies:")
            for i, rec in enumerate(unique_recommendations, 1):
                logger.info(f"  {i}. {rec['title']} (priority: {rec['priority']})")
                logger.info(f"     Description preview: {rec['description'][:100]}...")

            # 戦略提案が見つからない場合はデフォルトを返す
            if not unique_recommendations:
                logger.warning("[Strategy Parser] No recommendations found, using defaults")
                return self._get_default_recommendations()

            return unique_recommendations

        except Exception as e:
            logger.error(f"Error parsing strategic recommendations: {e}")
            return self._get_default_recommendations()

    def _get_default_recommendations(self) -> List[Dict[str, str]]:
        """デフォルトの戦略提案を返す"""
        return [
            {
                "title": "差別化戦略",
                "description": "専門性を活かした特色ある診療メニューの開発と、地域のニーズに合わせた医療サービスの提供により、競合医院との差別化を図ります。",
                "priority": "high"
            },
            {
                "title": "マーケティング戦略",
                "description": "SNSやウェブサイトを活用した情報発信の強化と、地域イベントへの積極的な参加により、認知度向上を目指します。",
                "priority": "medium"
            },
            {
                "title": "オペレーション改善",
                "description": "オンライン予約システムの導入と待ち時間の短縮により、患者満足度の向上と業務効率化を実現します。",
                "priority": "medium"
            }
        ]

    def _parse_swot_response(self, response: str) -> Dict[str, List[str]]:
        """AIレスポンスからSWOT要素を抽出（JSON形式対応）"""
        logger.info("="*60)
        logger.info("[SWOT Parser] Starting to parse SWOT response")
        logger.info(f"[SWOT Parser] Response length: {len(response) if response else 0} characters")

        try:
            import json
            import re
            
            swot = {
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
                "threats": [],
                "strategies": []
            }

            # Noneチェックと型チェック
            if not response or not isinstance(response, str):
                logger.warning("[SWOT Parser] Invalid response for SWOT parsing")
                return self._generate_basic_swot({})

            # レスポンスの最初の500文字をログ出力
            logger.info(f"[SWOT Parser] Response preview (first 500 chars): {response[:500]}...")
            
            # JSONを抽出（余計なテキストがあるかもしれないので）
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                logger.info(f"[SWOT Parser] Found JSON string, length: {len(json_str)}")
                
                try:
                    # JSONパース
                    parsed = json.loads(json_str)
                    logger.info(f"[SWOT Parser] Successfully parsed JSON")
                    
                    # データを変換
                    if "強み" in parsed:
                        swot["strengths"] = [str(item) for item in parsed.get("強み", []) if item]
                    if "弱み" in parsed:
                        swot["weaknesses"] = [str(item) for item in parsed.get("弱み", []) if item]
                    if "機会" in parsed:
                        swot["opportunities"] = [str(item) for item in parsed.get("機会", []) if item]
                    if "脅威" in parsed:
                        swot["threats"] = [str(item) for item in parsed.get("脅威", []) if item]
                    
                    # 戦略を結合
                    strategies = []
                    if "差別化戦略" in parsed:
                        strategies.extend([str(item) for item in parsed.get("差別化戦略", []) if item])
                    if "マーケティング戦略" in parsed:
                        strategies.extend([str(item) for item in parsed.get("マーケティング戦略", []) if item])
                    if "オペレーション改善" in parsed:
                        strategies.extend([str(item) for item in parsed.get("オペレーション改善", []) if item])
                    swot["strategies"] = strategies
                    
                    # パース結果をログ出力
                    logger.info("="*60)
                    logger.info("[SWOT Parser] JSON parsing completed. Results:")
                    logger.info(f"  - Strengths: {len(swot['strengths'])} items")
                    logger.info(f"  - Weaknesses: {len(swot['weaknesses'])} items")
                    logger.info(f"  - Opportunities: {len(swot['opportunities'])} items")
                    logger.info(f"  - Threats: {len(swot['threats'])} items")
                    logger.info(f"  - Strategies: {len(swot['strategies'])} items")
                    
                    # 各項目が空でないか確認
                    if swot["weaknesses"]:
                        logger.info(f"[SWOT Parser] Weaknesses items: {swot['weaknesses'][:2]}...")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"[SWOT Parser] JSON parse error: {e}")
                    logger.error(f"[SWOT Parser] Failed JSON string: {json_str[:500]}...")
                    # フォールバック処理
                    return self._fallback_parse_swot(response)
            else:
                logger.warning("[SWOT Parser] No JSON structure found in response")
                # フォールバック処理
                return self._fallback_parse_swot(response)
            
            # 最小限の項目を確保
            if not swot["strengths"]:
                logger.warning("[SWOT Parser] No strengths found, using defaults")
                swot["strengths"] = ["専門性の高い医療サービス", "経験豊富な医療スタッフ"]
            if not swot["weaknesses"]:
                logger.warning("[SWOT Parser] No weaknesses found, using defaults")
                swot["weaknesses"] = ["認知度の向上が必要", "デジタルマーケティングの強化が必要"]
            if not swot["opportunities"]:
                logger.warning("[SWOT Parser] No opportunities found, using defaults")
                swot["opportunities"] = ["地域の高齢化による需要増", "予防医療への関心の高まり"]
            if not swot["threats"]:
                logger.warning("[SWOT Parser] No threats found, using defaults")
                swot["threats"] = ["近隣競合医院との競争", "患者の大病院志向"]
            if not swot["strategies"]:
                logger.warning("[SWOT Parser] No strategies found, using defaults")
                swot["strategies"] = [
                    "SNSを活用した情報発信の強化",
                    "予約システムの導入による利便性向上",
                    "地域連携の強化"
                ]
            
            return swot
            
        except Exception as e:
            logger.error(f"Error parsing SWOT response: {e}")
            return self._generate_basic_swot({})
    
    def _fallback_parse_swot(self, response: str) -> Dict[str, List[str]]:
        """フォールバック: テキスト形式のレスポンスをパース"""
        logger.info("[SWOT Parser] Fallback: Trying text-based parsing")
        
        swot = {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": [],
            "strategies": []
        }
        
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
            
            # セクション検出
            for jp_name, en_name in sections.items():
                if jp_name in line and any(line.startswith(prefix) for prefix in ["###", "##", "#"]):
                    current_section = en_name
                    break
            
            # 戦略セクション検出
            if any(keyword in line for keyword in ["戦略", "提案"]) and any(line.startswith(prefix) for prefix in ["###", "##", "#"]):
                current_section = "strategies"
            
            # 項目収集（簡略化）
            if current_section and line.startswith(('-', '・', '*', '●', '○')):
                content = line.lstrip('-・*●○').strip()
                if content and len(content) > 5:
                    swot[current_section].append(content)
        
        logger.info(f"[SWOT Parser] Fallback results: S={len(swot['strengths'])}, W={len(swot['weaknesses'])}, O={len(swot['opportunities'])}, T={len(swot['threats'])}")
        return swot
    
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