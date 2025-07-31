# main.pyの generate_persona 関数を以下のように修正する例

"""
修正箇所：
1. import文に追加
2. generate_persona関数内でasyncio.create_taskを使用
"""

# 1. import文に追加（main.pyの上部）
import asyncio
from .services.async_image_generator import generate_image_async

# 2. generate_persona関数内の修正（行900あたりから）
async def generate_persona(request: Request):
    try:
        data = await request.json()
        
        # 設定読み込み等は同じ...
        
        # ===== ここから非同期処理 =====
        
        # 画像生成タスクを先に開始（バックグラウンドで実行）
        image_generation_task = asyncio.create_task(
            generate_image_async(
                data=data,
                selected_image_model=selected_image_model,
                openai_api_key=openai_api_key,
                google_api_key=google_api_key
            )
        )
        
        # テキスト生成を実行（画像生成と並列）
        generated_text_str = None
        if text_generation_client:
            try:
                generated_text_str = await generate_text_response(
                    prompt_text, 
                    selected_text_model, 
                    text_api_key_to_use
                )
            except Exception as e:
                print(f"[ERROR] Text generation failed: {type(e).__name__}: {e}")
                generated_text_str = None
        
        # テキスト生成結果の処理
        if generated_text_str is None:
            generated_details = {
                "personality": "真面目で責任感が強く...",
                # デフォルト値...
            }
        else:
            generated_details = parse_ai_response(generated_text_str)
        
        # 画像生成の完了を待つ
        try:
            image_url = await image_generation_task
            print(f"[Async] Image generation completed: {image_url[:50]}...")
        except Exception as e:
            print(f"[Async] Image generation task failed: {e}")
            image_url = "https://placehold.jp/300x200/FF0000/FFFFFF?text=Error"
        
        # ===== 以降は元のコードと同じ =====
        
        # PDFとPPT生成...
        persona_data = {
            "name": data.get('name'),
            # 以下同じ...
        }