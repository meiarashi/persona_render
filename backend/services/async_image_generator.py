"""
非同期画像生成モジュール
テキスト生成と並列して画像生成を実行するための関数
"""
import asyncio
import base64
import os
from typing import Optional

async def generate_image_async(
    data: dict,
    selected_image_model: str,
    openai_api_key: str = "",
    google_api_key: str = ""
) -> str:
    """
    画像を非同期で生成する
    
    Args:
        data: フォームデータ（name, age, gender, occupation を含む）
        selected_image_model: 使用する画像生成モデル
        openai_api_key: OpenAI APIキー
        google_api_key: Google APIキー
    
    Returns:
        生成された画像のURL（エラー時はプレースホルダー）
    """
    try:
        # デフォルトプレースホルダー
        image_url = "https://placehold.jp/150x150.png"
        
        # プロンプト構築用のデータ抽出
        name = data.get('name', 'person')
        age_raw = data.get('age', 'age unknown')
        gender = data.get('gender', 'gender unknown')
        occupation = data.get('occupation', '')
        
        # 年齢の数値抽出
        age = age_raw
        if isinstance(age_raw, str):
            import re
            age_match = re.search(r'(\d+)', age_raw)
            if age_match:
                age = age_match.group(1)
            else:
                age = "30"
        
        # 性別をより自然な表現に変換
        gender_text = {
            'male': 'man',
            'female': 'woman',
            '男性': 'man',
            '女性': 'woman'
        }.get(gender, gender)
        
        # プロンプト構築
        img_prompt_parts = [
            "Professional headshot portrait photograph,",
            f"a {age} year old Japanese {gender_text},",
            "photorealistic, high resolution, natural lighting,",
            "friendly and approachable expression,",
            "business casual attire,",
            "shallow depth of field with blurred background,",
            "taken with professional camera,"
        ]
        
        # 職業別の詳細追加
        if occupation:
            if '医師' in occupation or '医者' in occupation or 'doctor' in occupation.lower():
                img_prompt_parts.append("wearing a white coat,")
            elif '看護' in occupation or 'nurse' in occupation.lower():
                img_prompt_parts.append("wearing medical scrubs,")
            else:
                img_prompt_parts.append(f"dressed appropriately for {occupation},")
        
        img_prompt_parts.extend([
            "centered composition,",
            "neutral gray background,",
            "professional photography style"
        ])
        
        img_prompt = " ".join(img_prompt_parts)
        
        # DALL-E 3の場合
        if selected_image_model == "dall-e-3" and openai_api_key:
            from openai import OpenAI
            try:
                image_client = OpenAI(api_key=openai_api_key)
                print(f"[Async] Attempting DALL-E 3 image generation")
                
                # 非同期実行のためのラッパー
                loop = asyncio.get_event_loop()
                image_response = await loop.run_in_executor(
                    None,
                    lambda: image_client.images.generate(
                        model="dall-e-3",
                        prompt=img_prompt,
                        size="1024x1024",
                        quality="hd",
                        style="natural",
                        n=1,
                    )
                )
                
                image_url = image_response.data[0].url
                print(f"[Async] DALL-E 3 Image generated successfully")
                
            except Exception as e:
                print(f"[Async] DALL-E 3 Image generation failed: {e}")
                image_url = "https://placehold.jp/300x200/EEE/777?text=DALL-E+Error"
        
        # Geminiの場合
        elif selected_image_model.startswith("gemini") and google_api_key:
            try:
                from google import genai as google_genai_sdk
                from google.genai import types as google_genai_types
                
                client = google_genai_sdk.Client(api_key=google_api_key)
                print(f"[Async] Attempting Gemini image generation")
                
                # 非同期実行のためのラッパー
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model=selected_image_model,
                        contents=img_prompt,
                        config=google_genai_types.GenerateContentConfig(
                            response_modalities=['TEXT', 'IMAGE']
                        )
                    )
                )
                
                # レスポンス処理
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                if hasattr(part.inline_data, 'data'):
                                    image_data = part.inline_data.data
                                    mime_type = getattr(part.inline_data, 'mime_type', 'image/png')
                                    base64_image = base64.b64encode(image_data).decode('utf-8')
                                    image_url = f"data:{mime_type};base64,{base64_image}"
                                    print(f"[Async] Gemini image generated successfully")
                                    break
                                    
            except Exception as e:
                print(f"[Async] Gemini image generation failed: {e}")
                image_url = "https://placehold.jp/300x200/EEE/777?text=Gemini+Error"
        
        return image_url
        
    except Exception as e:
        print(f"[Async] Image generation error: {e}")
        return "https://placehold.jp/300x200/FF0000/FFFFFF?text=Error"