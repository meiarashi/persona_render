"""
Web Research Service - 競合医院の詳細情報をWebから収集
"""

import os
import aiohttp
import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re
from urllib.parse import quote

logger = logging.getLogger(__name__)

class RateLimiter:
    """APIレート制限管理クラス"""
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window  # seconds
        self.calls = []
    
    async def acquire(self):
        """レート制限に従ってAPI呼び出しを許可"""
        now = time.time()
        # 古い呼び出し記録を削除
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        if len(self.calls) >= self.max_calls:
            # 制限に達した場合は待機
            sleep_time = self.time_window - (now - self.calls[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, waiting {sleep_time:.1f} seconds")
                await asyncio.sleep(sleep_time)
        
        self.calls.append(now)

class WebResearchService:
    """Web検索とスクレイピングによる競合情報収集サービス"""
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        # SerpAPIのレート制限: 1分間に100リクエストまで
        self.serpapi_limiter = RateLimiter(max_calls=100, time_window=60)
        # デフォルトタイムアウト設定
        self.default_timeout = aiohttp.ClientTimeout(total=30)
        
        # 管理画面の設定を読み込み
        try:
            from backend.utils.config_manager import config_manager
            self.settings = config_manager.get_settings()
            # 新しいフィールド名を使用（models.text_api_model）
            if hasattr(self.settings, 'models') and self.settings.models:
                self.selected_model = self.settings.models.text_api_model or "gpt-4-turbo-preview"
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
                # フォールバック設定
                self.selected_model = 'gpt-4-turbo-preview'
                self.selected_provider = 'openai'
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
            self.selected_model = 'gpt-4-turbo-preview'
            self.selected_provider = 'openai'
        
    def _validate_input(self, clinic_name: str, address: str) -> Tuple[bool, str]:
        """入力値のバリデーション"""
        if not clinic_name or len(clinic_name.strip()) < 2:
            return False, "クリニック名は2文字以上必要です"
        
        if not address or len(address.strip()) < 5:
            return False, "住所は5文字以上必要です"
        
        # 危険な文字をチェック
        dangerous_patterns = ['<script', 'javascript:', 'onclick', 'onerror']
        combined_input = (clinic_name + address).lower()
        for pattern in dangerous_patterns:
            if pattern in combined_input:
                return False, "不正な文字が含まれています"
        
        return True, ""
    
    def _sanitize_input(self, text: str) -> str:
        """入力値のサニタイズ"""
        # HTMLタグや特殊文字を除去
        text = re.sub(r'<[^>]+>', '', text)
        # 改行やタブを空白に変換
        text = re.sub(r'[\n\t\r]+', ' ', text)
        # 連続する空白を単一に
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    async def research_competitor(self, clinic_name: str, address: str) -> Dict[str, Any]:
        """
        競合医院の詳細情報をWebから収集
        
        Args:
            clinic_name: クリニック名
            address: 住所
            
        Returns:
            収集した詳細情報
        """
        # 入力値のバリデーション
        is_valid, error_msg = self._validate_input(clinic_name, address)
        if not is_valid:
            logger.warning(f"Invalid input: {error_msg}")
            return {
                "clinic_name": clinic_name,
                "address": address,
                "error": error_msg
            }
        
        # サニタイズ
        clinic_name = self._sanitize_input(clinic_name)
        address = self._sanitize_input(address)
        
        research_results = {
            "clinic_name": clinic_name,
            "address": address,
            "search_results": {},
            "extracted_info": {},
            "online_presence": {},
            "recent_news": [],
            "patient_reviews_summary": {}
        }
        
        try:
            # 1. Google検索で基本情報収集
            search_data = await self._google_search(clinic_name, address)
            research_results["search_results"] = search_data
            
            # 2. 公式サイトから情報抽出
            if website_url := search_data.get("website"):
                website_info = await self._analyze_website(website_url)
                research_results["extracted_info"] = website_info
            
            # 3. SNSプレゼンス調査
            social_presence = await self._check_social_presence(clinic_name)
            research_results["online_presence"] = social_presence
            
            # 4. 最新ニュース・プレスリリース
            news = await self._search_recent_news(clinic_name)
            research_results["recent_news"] = news
            
            # 5. 口コミサイトの評判集約
            reviews = await self._aggregate_reviews(clinic_name, address)
            research_results["patient_reviews_summary"] = reviews
            
        except Exception as e:
            logger.error(f"Error researching competitor {clinic_name}: {e}")
            
        return research_results
    
    async def _google_search(self, clinic_name: str, address: str) -> Dict:
        """Google検索でクリニック情報を取得（改善版）"""
        if not self.serpapi_key:
            logger.info("SERPAPI_KEY not configured, skipping web search")
            return {"warning": "Web検索機能は利用できません（APIキー未設定）", "data": {}}
            
        try:
            query = f"{clinic_name} {address} 医院 クリニック"
            
            # レート制限チェック
            await self.serpapi_limiter.acquire()
            
            async with aiohttp.ClientSession(timeout=self.default_timeout) as session:
                params = {
                    "q": query,
                    "api_key": self.serpapi_key,
                    "engine": "google",
                    "location": "Japan",
                    "hl": "ja",
                    "gl": "jp",
                    "num": 10
                }
                
                url = "https://serpapi.com/search"
                
                # リトライ機能付きリクエスト
                for attempt in range(3):
                    try:
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                logger.info(f"SerpAPI search successful for {clinic_name}")
                                break
                            elif response.status == 429:  # レート制限
                                wait_time = 2 ** attempt  # エクスポネンシャルバックオフ
                                logger.warning(f"SerpAPI rate limited, waiting {wait_time}s")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                logger.warning(f"SerpAPI returned status {response.status}")
                                return {"warning": f"検索APIエラー (status: {response.status})", "data": {}}
                    
                    except asyncio.TimeoutError:
                        logger.warning(f"Search timeout on attempt {attempt + 1} for {clinic_name}")
                        if attempt == 2:  # 最後の試行
                            return {"warning": "検索がタイムアウトしました", "data": {}}
                        await asyncio.sleep(1)  # 少し待ってリトライ
                else:
                    return {"warning": "検索に失敗しました", "data": {}}
                
                # 検索結果から情報抽出
                extracted = {
                    "website": None,
                    "snippets": [],
                    "knowledge_panel": {},
                    "related_searches": [],
                    "local_results": []
                }
                
                # オーガニック検索結果
                for result in data.get("organic_results", [])[:5]:
                    if clinic_name in result.get("title", ""):
                        if not extracted["website"]:
                            extracted["website"] = result.get("link")
                        extracted["snippets"].append(result.get("snippet", ""))
                
                # ローカル検索結果（地図結果）
                for local_result in data.get("local_results", {}).get("places", [])[:3]:
                    if clinic_name in local_result.get("title", ""):
                        extracted["local_results"].append({
                            "title": local_result.get("title"),
                            "address": local_result.get("address"),
                            "rating": local_result.get("rating"),
                            "reviews": local_result.get("reviews"),
                            "hours": local_result.get("hours"),
                            "phone": local_result.get("phone")
                        })
                
                # ナレッジパネル
                if knowledge := data.get("knowledge_graph"):
                    extracted["knowledge_panel"] = {
                        "description": knowledge.get("description"),
                        "type": knowledge.get("type"),
                        "hours": knowledge.get("hours"),
                        "phone": knowledge.get("phone"),
                        "address": knowledge.get("address"),
                        "website": knowledge.get("website")
                    }
                    # ナレッジパネルからウェブサイトを取得
                    if not extracted["website"] and knowledge.get("website"):
                        extracted["website"] = knowledge.get("website")
                
                # 関連検索
                extracted["related_searches"] = [
                    search.get("query", "") 
                    for search in data.get("related_searches", [])[:5]
                ]
                
                return extracted
                        
        except Exception as e:
            logger.error(f"Google search error: {e}")
            return {}
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """HTMLからテキストを抽出（改善版）"""
        # スクリプトとスタイルタグを除去
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # 改行をスペースに変換してからタグを除去
        html_content = re.sub(r'<br\s*/?>', ' ', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</p>', ' ', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</div>', ' ', html_content, flags=re.IGNORECASE)
        
        # すべてのHTMLタグを除去
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # エンティティをデコード
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        
        # 連続する空白を単一に
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    async def _analyze_website(self, url: str) -> Dict:
        """公式サイトから情報を抽出（SerpAPI結果を管理画面設定のAIで解析）"""
        logger.info(f"Analyzing website: {url} using {self.selected_provider}/{self.selected_model}")
            
        try:
            # SerpAPIでサイト固有の検索を実行
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if not domain:
                logger.warning(f"Could not extract domain from URL: {url}")
                return {"error": "URLからドメインを抽出できませんでした"}
            
            # SerpAPIで検索して結果を取得
            if not self.serpapi_key:
                logger.info("SerpAPI key not configured")
                return {"note": "SerpAPIキーが設定されていません"}
            
            search_results = await self._search_site_with_serpapi(domain)
            if not search_results or "error" in search_results:
                return search_results
            
            # 検索結果からテキストを抽出
            text_content = self._extract_text_from_search_results(search_results)
            
            # AIで情報抽出（管理画面の設定に従う）
            prompt = f"""
            以下のウェブサイトの検索結果から医療機関の情報を抽出してください：
            
            {text_content[:3000]}
            
            以下の項目を抽出：
            1. 診療時間
            2. 医師・スタッフ情報
            3. 診療科目・専門分野
            4. 設備・機器
            5. 特徴的なサービス
            6. アクセス情報
            
            JSON形式で返してください。
            """
            
            extracted_info = None
            
            # 管理画面で設定されたプロバイダーとモデルを使用
            if self.selected_provider == "openai" and self.openai_api_key:
                try:
                    from openai import AsyncOpenAI
                    client = AsyncOpenAI(api_key=self.openai_api_key)
                    response = await client.chat.completions.create(
                        model=self.selected_model,
                        messages=[{"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        timeout=10.0
                    )
                    extracted_info = json.loads(response.choices[0].message.content)
                    logger.info(f"Successfully extracted info using OpenAI/{self.selected_model}")
                except Exception as e:
                    logger.warning(f"OpenAI extraction error: {e}")
                    # Anthropicにフォールバック
                    if self.anthropic_api_key:
                        self.selected_provider = "anthropic"
                        self.selected_model = "claude-3-5-sonnet-20241022"
            
            if self.selected_provider == "anthropic" and self.anthropic_api_key and not extracted_info:
                try:
                    from anthropic import AsyncAnthropic
                    client = AsyncAnthropic(api_key=self.anthropic_api_key)
                    response = await client.messages.create(
                        model=self.selected_model,
                        max_tokens=1000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    text = response.content[0].text
                    json_match = re.search(r'\{.*\}', text, re.DOTALL)
                    if json_match:
                        extracted_info = json.loads(json_match.group())
                    logger.info(f"Successfully extracted info using Anthropic/{self.selected_model}")
                except Exception as e:
                    logger.warning(f"Claude extraction error: {e}")
                    # Googleにフォールバック
                    if self.google_api_key:
                        self.selected_provider = "google"
                        self.selected_model = "gemini-2.5-pro-preview-06-05"
            
            if self.selected_provider == "google" and self.google_api_key and not extracted_info:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=self.google_api_key)
                    model = genai.GenerativeModel(self.selected_model)
                    response = model.generate_content(prompt)
                    text = response.text
                    json_match = re.search(r'\{.*\}', text, re.DOTALL)
                    if json_match:
                        extracted_info = json.loads(json_match.group())
                    logger.info(f"Successfully extracted info using Google/{self.selected_model}")
                except Exception as e:
                    logger.warning(f"Gemini extraction error: {e}")
            
            # AI抽出が失敗した場合は基本的な情報を返す
            if not extracted_info:
                extracted_info = {
                    "source": "SerpAPI",
                    "extracted_text": text_content[:1000] if text_content else "情報を取得できませんでした",
                    "特徴的なサービス": "詳細はウェブサイトをご確認ください"
                }
                logger.warning("All AI providers failed, returning basic info")
            
            return extracted_info
                            
        except Exception as e:
            logger.error(f"Website analysis error: {e}")
            return {}
    
    async def _search_site_with_serpapi(self, domain: str) -> Dict:
        """SerpAPIを使用してサイト固有の情報を検索"""
        try:
            await self.serpapi_limiter.acquire()
            
            async with aiohttp.ClientSession(timeout=self.default_timeout) as session:
                params = {
                    "q": f"site:{domain} 診療時間 診療科目 医師 設備 アクセス",
                    "api_key": self.serpapi_key,
                    "engine": "google",
                    "location": "Japan",
                    "hl": "ja",
                    "gl": "jp",
                    "num": 10
                }
                
                url = "https://serpapi.com/search"
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Successfully retrieved site info for {domain}")
                        return data
                    else:
                        logger.warning(f"SerpAPI returned status {response.status}")
                        return {"error": f"検索エラー (status: {response.status})"}
                        
        except Exception as e:
            logger.error(f"Site search error: {str(e)}")
            return {"error": f"サイト検索エラー: {str(e)}"}
    
    def _extract_text_from_search_results(self, search_results: Dict) -> str:
        """SerpAPIの検索結果からテキストを抽出"""
        extracted_text = []
        
        # オーガニック検索結果から情報を抽出
        if "organic_results" in search_results:
            for result in search_results.get("organic_results", [])[:5]:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                
                if title:
                    extracted_text.append(f"タイトル: {title}")
                if snippet:
                    extracted_text.append(f"内容: {snippet}")
                if link:
                    extracted_text.append(f"URL: {link}")
                extracted_text.append("")  # 空行で区切る
        
        # ナレッジパネルがあれば追加
        if "knowledge_graph" in search_results:
            kg = search_results["knowledge_graph"]
            if "title" in kg:
                extracted_text.append(f"施設名: {kg['title']}")
            if "description" in kg:
                extracted_text.append(f"説明: {kg['description']}")
            if "address" in kg:
                extracted_text.append(f"住所: {kg['address']}")
            if "phone" in kg:
                extracted_text.append(f"電話: {kg['phone']}")
            if "hours" in kg:
                extracted_text.append(f"営業時間: {kg['hours']}")
        
        # リッチスニペットがあれば追加
        if "rich_snippet" in search_results:
            rs = search_results["rich_snippet"]
            for key, value in rs.items():
                if value:
                    extracted_text.append(f"{key}: {value}")
        
        return "\n".join(extracted_text) if extracted_text else "検索結果から情報を抽出できませんでした"
    
    async def _check_social_presence(self, clinic_name: str) -> Dict:
        """SNSプレゼンスをチェック（完全実装）"""
        presence = {
            "has_twitter": False,
            "has_instagram": False,
            "has_facebook": False,
            "has_line": False,
            "social_links": [],
            "follower_counts": {}
        }
        
        if not self.serpapi_key:
            logger.info("SerpAPI key not configured, skipping SNS check")
            return presence
        
        # SNS検索クエリ
        search_queries = {
            "twitter": f"site:twitter.com {clinic_name}",
            "instagram": f"site:instagram.com {clinic_name}",
            "facebook": f"site:facebook.com {clinic_name}",
            "line": f"{clinic_name} LINE 公式"
        }
        
        for platform, query in search_queries.items():
            try:
                # レート制限チェック
                await self.serpapi_limiter.acquire()
                
                async with aiohttp.ClientSession(timeout=self.default_timeout) as session:
                    params = {
                        "q": query,
                        "api_key": self.serpapi_key,
                        "engine": "google",
                        "hl": "ja",
                        "gl": "jp",
                        "num": 3
                    }
                    
                    url = "https://serpapi.com/search"
                    
                    try:
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # 検索結果からSNSアカウントを検出
                                for result in data.get("organic_results", []):
                                    link = result.get("link", "")
                                    title = result.get("title", "")
                                    
                                    # 公式アカウントらしきリンクを検出
                                    if platform == "twitter" and "twitter.com" in link:
                                        presence["has_twitter"] = True
                                        presence["social_links"].append({
                                            "platform": "Twitter",
                                            "url": link,
                                            "title": title
                                        })
                                        # フォロワー数を抽出（スニペットから）
                                        snippet = result.get("snippet", "")
                                        if "フォロワー" in snippet:
                                            import re
                                            numbers = re.findall(r'([\d,]+)\s*フォロワー', snippet)
                                            if numbers:
                                                presence["follower_counts"]["twitter"] = numbers[0]
                                        break
                                    
                                    elif platform == "instagram" and "instagram.com" in link:
                                        presence["has_instagram"] = True
                                        presence["social_links"].append({
                                            "platform": "Instagram",
                                            "url": link,
                                            "title": title
                                        })
                                        break
                                    
                                    elif platform == "facebook" and "facebook.com" in link:
                                        presence["has_facebook"] = True
                                        presence["social_links"].append({
                                            "platform": "Facebook",
                                            "url": link,
                                            "title": title
                                        })
                                        break
                                    
                                    elif platform == "line" and ("line.me" in link or "LINE" in title):
                                        presence["has_line"] = True
                                        presence["social_links"].append({
                                            "platform": "LINE",
                                            "url": link if "line.me" in link else "",
                                            "title": title
                                        })
                                        break
                                
                                logger.info(f"SNS check for {platform}: {'Found' if presence[f'has_{platform}'] else 'Not found'}")
                            
                    except asyncio.TimeoutError:
                        logger.warning(f"SNS search timeout for {platform}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Error checking {platform}: {e}")
                continue
        
        # SNSプレゼンスのサマリ
        active_platforms = []
        if presence["has_twitter"]: active_platforms.append("Twitter")
        if presence["has_instagram"]: active_platforms.append("Instagram")
        if presence["has_facebook"]: active_platforms.append("Facebook")
        if presence["has_line"]: active_platforms.append("LINE")
        
        presence["summary"] = {
            "total_platforms": len(active_platforms),
            "active_platforms": active_platforms,
            "engagement_level": "high" if len(active_platforms) >= 3 else "medium" if len(active_platforms) >= 2 else "low"
        }
        
        return presence
    
    async def _search_recent_news(self, clinic_name: str) -> List[Dict]:
        """最新ニュースを検索（改善版）"""
        news = []
        
        if not self.serpapi_key:
            logger.info("SerpAPI key not configured, skipping news search")
            return news
        
        try:
            query = f"{clinic_name} ニュース OR お知らせ OR 新規開業 OR リニューアル"
            
            # レート制限チェック
            await self.serpapi_limiter.acquire()
            
            async with aiohttp.ClientSession(timeout=self.default_timeout) as session:
                params = {
                    "q": query,
                    "api_key": self.serpapi_key,
                    "engine": "google",
                    "tbm": "nws",  # ニュース検索
                    "hl": "ja",
                    "gl": "jp",
                    "tbs": "qdr:y"  # 過去1年
                }
                
                url = "https://serpapi.com/search"
                
                try:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for item in data.get("news_results", [])[:5]:
                                news.append({
                                    "title": item.get("title", ""),
                                    "date": item.get("date", ""),
                                    "source": item.get("source", ""),
                                    "snippet": item.get("snippet", ""),
                                    "link": item.get("link", "")
                                })
                            
                            logger.info(f"Found {len(news)} news articles for {clinic_name}")
                        else:
                            logger.warning(f"News search returned status {response.status}")
                            
                except asyncio.TimeoutError:
                    logger.warning("News search timeout")
                    
        except Exception as e:
            logger.error(f"News search error: {e}")
            
        return news
    
    async def _aggregate_reviews(self, clinic_name: str, address: str) -> Dict:
        """複数の口コミサイトから評判を集約（改善版）"""
        reviews_summary = {
            "total_reviews": 0,
            "average_rating": 0,
            "positive_keywords": [],
            "negative_keywords": [],
            "common_themes": [],
            "sources_checked": []
        }
        
        if not self.serpapi_key:
            logger.info("SerpAPI key not configured, skipping review aggregation")
            return reviews_summary
        
        # 口コミサイトの検索
        review_sites = [
            "Google レビュー",
            "病院なび",
            "Caloo",
            "EPARK"
        ]
        
        all_reviews = []
        
        for site in review_sites:
            try:
                query = f"{clinic_name} {site} 口コミ 評判"
                
                # レート制限チェック
                await self.serpapi_limiter.acquire()
                
                async with aiohttp.ClientSession(timeout=self.default_timeout) as session:
                    params = {
                        "q": query,
                        "api_key": self.serpapi_key,
                        "engine": "google",
                        "hl": "ja",
                        "gl": "jp",
                        "num": 5
                    }
                    
                    url = "https://serpapi.com/search"
                    
                    try:
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # 検索結果から口コミ情報を抽出
                                for result in data.get("organic_results", [])[:3]:
                                    snippet = result.get("snippet", "")
                                    if "口コミ" in snippet or "評判" in snippet or "レビュー" in snippet:
                                        all_reviews.append(snippet)
                                
                                reviews_summary["sources_checked"].append(site)
                                
                    except asyncio.TimeoutError:
                        logger.warning(f"Review search timeout for {site}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Error searching reviews on {site}: {e}")
                continue
        
        # 口コミからキーワードを抽出（簡易分析）
        if all_reviews:
            reviews_text = " ".join(all_reviews)
            
            # ポジティブキーワード
            positive_words = ["優しい", "丁寧", "親切", "きれい", "清潔", "安心", "便利", "早い"]
            for word in positive_words:
                if word in reviews_text:
                    reviews_summary["positive_keywords"].append(word)
            
            # ネガティブキーワード
            negative_words = ["遅い", "混雑", "不親切", "汚い", "高い", "不便", "待ち時間"]
            for word in negative_words:
                if word in reviews_text:
                    reviews_summary["negative_keywords"].append(word)
            
            # 共通テーマを抽出
            themes = ["待ち時間", "診療時間", "スタッフ対応", "設備", "清潔感"]
            for theme in themes:
                if theme in reviews_text:
                    reviews_summary["common_themes"].append(theme)
        
        reviews_summary["total_reviews"] = len(all_reviews)
        logger.info(f"Aggregated {len(all_reviews)} reviews from {len(reviews_summary['sources_checked'])} sources")
        
        return reviews_summary

class RegionalDataService:
    """地域特性データ取得サービス（e-Stat API統合版）"""
    
    def __init__(self):
        # e-Stat API統合サービスを優先的に使用
        self.estat_service = None
        self.json_service = None
        
        # e-Stat API統合サービスのインポート
        try:
            from .estat_integrated_service import EStatIntegratedService
            self.estat_service = EStatIntegratedService()
            logger.info("EStatIntegratedService loaded successfully")
        except ImportError as e:
            logger.warning(f"Failed to import EStatIntegratedService: {e}")
        
        # フォールバック用のJSONサービス
        try:
            from .regional_json_service import RegionalJsonService
            self.json_service = RegionalJsonService()
            logger.info("RegionalJsonService loaded as fallback")
        except ImportError as e:
            logger.error(f"Failed to import RegionalJsonService: {e}")
            self.json_service = None
        
    async def get_regional_data(self, address: str) -> Dict[str, Any]:
        """
        地域の統計データを取得（e-Stat API優先、JSONフォールバック）
        
        Args:
            address: 対象地域の住所
            
        Returns:
            人口統計、医療需要などのデータ
        """
        try:
            # e-Stat API統合サービスを優先的に使用
            if self.estat_service and os.getenv("ESTAT_API_KEY"):
                logger.info(f"e-Stat APIで地域データを取得: {address}")
                try:
                    # e-Stat APIから取得（キャッシュも活用）
                    data = await self.estat_service.get_regional_data(address)
                    if data and data.get("demographics"):
                        logger.info("e-Stat APIからデータ取得成功")
                        return data
                except Exception as e:
                    logger.warning(f"e-Stat API取得失敗、JSONフォールバック: {e}")
            
            # JSONサービスをフォールバックとして使用
            if self.json_service:
                logger.info("JSONデータベースから地域データを取得")
                regional_data = self.json_service.get_regional_data(address)
                competition_data = self.json_service.get_competition_density(address)
                
                # データを統合
                return {
                    "demographics": regional_data.get("demographics", {}),
                    "medical_facilities": regional_data.get("medical_facilities", {}),
                    "medical_demand": regional_data.get("medical_demand", {}),
                    "competition_density": competition_data,
                    "area_info": regional_data.get("area_info", {}),
                    "economic_indicators": {
                        "average_income": "データ準備中",
                        "business_count": "データ準備中"
                    }
                }
            else:
                logger.warning("サービスが利用できません。デフォルトデータを返します。")
                return self._get_default_regional_data()
                
        except Exception as e:
            logger.error(f"地域データ取得エラー: {e}")
            return self._get_default_regional_data()
    
    def _get_default_regional_data(self) -> Dict[str, Any]:
        """デフォルトの地域データ"""
        return {
            "demographics": {
                "total_population": 100000,
                "age_distribution": {
                    "0-14": 12,
                    "15-64": 63,
                    "65+": 25
                },
                "source": "推定値"
            },
            "medical_facilities": {
                "total": 50,
                "per_10000": 5.0
            },
            "medical_demand": {
                "estimated_patients_per_day": 3500,
                "disease_prevalence": {
                    "生活習慣病": 40,
                    "呼吸器疾患": 15,
                    "消化器疾患": 20,
                    "精神疾患": 10,
                    "整形外科疾患": 10,
                    "皮膚科疾患": 5
                },
                "healthcare_accessibility": "medium",
                "avg_waiting_time_minutes": 30
            },
            "competition_density": {
                "total_medical_facilities": 50,
                "clinics": 45,
                "hospitals": 5,
                "clinics_per_10000": 4.5,
                "hospitals_per_10000": 0.5,
                "competition_level": "medium"
            },
            "area_info": {
                "prefecture": "東京都",
                "type": "urban_medium_density"
            },
            "economic_indicators": {
                "average_income": "データ準備中",
                "business_count": "データ準備中"
            }
        }
    
    # 以下のメソッドは後方互換性のために保持（JSONサービスが利用できない場合のフォールバック）
    async def _get_area_code(self, address: str) -> Optional[str]:
        """住所から市区町村コードを取得"""
        # 主要都市のマッピング（拡張可能）
        area_mapping = {
            "渋谷区": "13113",
            "新宿区": "13104",
            "港区": "13103",
            "千代田区": "13101",
            "中央区": "13102",
            "品川区": "13109",
            "世田谷区": "13112",
            "目黒区": "13110",
            "大田区": "13111",
            "横浜市": "14100",
            "大阪市": "27100",
            "名古屋市": "23100",
            "福岡市": "40130",
            "札幌市": "01100"
        }
        
        # 住所から地域名を抽出
        for area_name, code in area_mapping.items():
            if area_name in address:
                logger.info(f"Area code found: {area_name} -> {code}")
                return code
        
        # デフォルトは東京都全体
        logger.info("Using default area code for Tokyo")
        return "13000"
    
    def _get_address_from_code(self, area_code: str) -> str:
        """地域コードから住所を逆引き"""
        # 逆引きマッピング（主要地域のみ）
        code_to_address = {
            "13113": "東京都渋谷区",
            "13104": "東京都新宿区",
            "13103": "東京都港区",
            "13109": "東京都品川区",
            "13112": "東京都世田谷区",
            "14100": "神奈川県横浜市",
            "27100": "大阪府大阪市",
            "23100": "愛知県名古屋市",
            "40130": "福岡県福岡市",
            "01100": "北海道札幌市",
            "13000": "東京都"
        }
        
        return code_to_address.get(area_code, "東京都")
    
    async def _get_demographics(self, area_code: str) -> Dict:
        """人口統計データを取得"""
        # EStatServiceが利用可能な場合は優先的に使用
        if self.estat_service and self.estat_api_key:
            try:
                # レート制限チェック
                await self.estat_limiter.acquire()
                
                # 地域コードから住所を逆引き（簡易実装）
                address = self._get_address_from_code(area_code)
                
                # EStatServiceで人口データを取得
                population_data = await self.estat_service.get_population_data(address)
                
                if population_data and population_data.get("total_population"):
                    return population_data
                    
            except Exception as e:
                logger.warning(f"Failed to get data from EStatService: {e}")
        
        # フォールバック: 従来の実装
        if not self.estat_api_key:
            logger.info("e-Stat API key not configured, using default data")
            return self._get_default_demographics(area_code)
        
        try:
            # レート制限チェック
            await self.estat_limiter.acquire()
            
            # e-Stat APIの実装
            url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
            params = {
                "appId": self.estat_api_key,
                "statsDataId": "0003448237",  # 人口推計データ
                "cdArea": area_code,
                "cdCat01": "00710,00720,00730",  # 総数、男、女
                "limit": 100
            }
            
            async with aiohttp.ClientSession(timeout=self.default_timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_estat_demographics(data, area_code)
                    else:
                        logger.warning(f"e-Stat API returned status {response.status}")
                        return self._get_default_demographics(area_code)
                        
        except asyncio.TimeoutError:
            logger.warning("e-Stat API timeout")
            return self._get_default_demographics(area_code)
        except Exception as e:
            logger.error(f"e-Stat API error: {e}")
            return self._get_default_demographics(area_code)
    
    def _parse_estat_demographics(self, data: Dict, area_code: str) -> Dict:
        """メ-Stat APIレスポンスをパース"""
        try:
            # APIレスポンスからデータを抽出
            values = data.get("GET_STATS_DATA", {}).get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
            
            if not values:
                return self._get_default_demographics(area_code)
            
            # 簡易的な集計（実際にはより詳細な処理が必要）
            total_pop = 0
            for value in values:
                if value.get("$"):
                    try:
                        total_pop += int(value["$"])
                    except ValueError:
                        pass
            
            return {
                "total_population": total_pop if total_pop > 0 else "data-no data",
                "age_distribution": {
                    "0-14": "データ取得中",
                    "15-64": "データ取得中",
                    "65+": "データ取得中"
                },
                "source": "e-Stat API",
                "area_code": area_code
            }
            
        except Exception as e:
            logger.error(f"Error parsing e-Stat data: {e}")
            return self._get_default_demographics(area_code)
    
    def _get_default_demographics(self, area_code: str) -> Dict:
        """フォールバック用のデフォルト人口統計"""
        # 地域コードに基づく概算値
        default_data = {
            "13113": {  # 渋谷区
                "total_population": 230000,
                "age_distribution": {"0-14": 10.5, "15-64": 68.2, "65+": 21.3},
                "household_count": 140000,
                "population_density": 15000
            },
            "13104": {  # 新宿区
                "total_population": 340000,
                "age_distribution": {"0-14": 9.8, "15-64": 67.5, "65+": 22.7},
                "household_count": 220000,
                "population_density": 18000
            },
            "default": {
                "total_population": "データ取得中",
                "age_distribution": {"0-14": "データ取得中", "15-64": "データ取得中", "65+": "データ取得中"},
                "household_count": "データ取得中",
                "population_density": "データ取得中"
            }
        }
        
        data = default_data.get(area_code, default_data["default"]).copy()
        data["note"] = "e-Stat APIキーを設定すると実際のデータを取得できます"
        return data
    
    async def _get_medical_demand(self, area_code: str) -> Dict:
        """医療需要データを推定"""
        # 地域別の医療需要推定（概算値）
        demand_data = {
            "13113": {  # 渋谷区
                "estimated_patients_per_day": 8000,
                "disease_prevalence": {
                    "生活習慣病": 32,
                    "呼吸器疾患": 14,
                    "消化器疾患": 18,
                    "精神疾患": 12,
                    "整形外科疾患": 15,
                    "皮膚科疾患": 9
                },
                "healthcare_accessibility": "high",
                "avg_waiting_time_minutes": 45
            },
            "13104": {  # 新宿区
                "estimated_patients_per_day": 12000,
                "disease_prevalence": {
                    "生活習慣病": 35,
                    "呼吸器疾患": 16,
                    "消化器疾患": 20,
                    "精神疾患": 11,
                    "整形外科疾患": 13,
                    "皮膚科疾患": 5
                },
                "healthcare_accessibility": "very_high",
                "avg_waiting_time_minutes": 60
            },
            "default": {
                "estimated_patients_per_day": "データ取得中",
                "disease_prevalence": {
                    "生活習慣病": "データ取得中",
                    "呼吸器疾患": "データ取得中",
                    "消化器疾患": "データ取得中",
                    "精神疾患": "データ取得中"
                },
                "healthcare_accessibility": "analyzing",
                "note": "詳細データは分析中です"
            }
        }
        
        return demand_data.get(area_code, demand_data["default"])
    
    async def _get_economic_indicators(self, area_code: str) -> Dict:
        """経済指標を取得"""
        return {
            "average_income": 4500000,
            "employment_rate": 95.5,
            "business_count": 15000
        }
    
    async def _calculate_competition_density(self, area_code: str) -> Dict:
        """医療機関の競争密度を計算"""
        return {
            "clinics_per_10000": 8.5,
            "hospitals_per_10000": 0.5,
            "specialty_distribution": {
                "内科": 35,
                "外科": 10,
                "小児科": 15,
                "その他": 40
            }
        }