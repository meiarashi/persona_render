from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import json
import os
import random
import traceback

# For AI clients
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    
try:
    import google.generativeai as genai
except ImportError:
    genai = None
    
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

# Import the router from the routers module
from .routers import admin_settings # Assuming admin_settings.py is in a 'routers' subdirectory

# Create a FastAPI app instance
app = FastAPI(
    title="Persona Render Admin API",
    description="API for managing Persona Render application settings.",
    version="0.1.0"
)

# Mount the admin_settings router
app.include_router(admin_settings.router)

# --- Static files hosting (for admin.html, admin_script.js, admin_style.css) ---
# Determine the path to the frontend directory relative to this main.py file.

# Path to the directory where this main.py file is located (e.g., .../backend/app/)
current_file_dir = Path(__file__).resolve().parent
# Path to the 'backend' directory (e.g., .../backend/)
backend_dir = current_file_dir.parent
# Path to the root of the project (e.g., .../)
project_root_dir = backend_dir.parent
# Path to the 'frontend' directory (e.g., .../frontend/)
frontend_dir = project_root_dir / "frontend"

# Check if a common alternative structure is used (e.g. backend and frontend are siblings)
# If not, try to find frontend relative to project root or specific locations.
# This logic might need adjustment based on the *actual* project structure.

# A more robust way to locate frontend if it's not strictly 'sibling to backend':
# Attempt 1: Frontend as a sibling to the backend directory's parent (common for repo root)
# Example: repo_root/frontend and repo_root/backend/app/main.py
if not frontend_dir.exists() or not frontend_dir.is_dir():
    # Attempt 2: Frontend directory directly in the project root (where backend might also be)
    # Example: repo_root/frontend and repo_root/backend (main.py inside backend or backend/app)
    # This assumes backend_dir is .../backend/
    # If project_root_dir is actually the repo root: project_root_dir / 'frontend'
    alt_frontend_dir = project_root_dir / "frontend" # Default assumption
    if (project_root_dir / "backend").exists() and (project_root_dir / "frontend").exists():
        frontend_dir = project_root_dir / "frontend"
    elif (backend_dir.parent / "frontend").exists(): # if backend is one level down from root
         frontend_dir = backend_dir.parent / "frontend"
    else: # Final fallback if backend_dir is the root
        frontend_dir = backend_dir / "frontend"


if frontend_dir.exists() and frontend_dir.is_dir():
    print(f"Serving static files from: {frontend_dir}")
    
    # フロントエンドディレクトリ構造に合わせて静的ファイル提供を設定
    # '/static/user/'で frontend/user のファイルにアクセス
    # '/static/admin/'で frontend/admin のファイルにアクセス
    app.mount("/static/user", StaticFiles(directory=frontend_dir / "user"), name="user_static_assets")
    app.mount("/static/admin", StaticFiles(directory=frontend_dir / "admin"), name="admin_static_assets")
    
    # Serve image files from /images route, pointing to the project root's images directory
    images_dir = project_root_dir / "images"
    if images_dir.exists() and images_dir.is_dir():
        app.mount("/images", StaticFiles(directory=images_dir), name="image_assets")
        print(f"Serving image files from: {images_dir}")

    @app.get("/admin", include_in_schema=False)
    async def serve_admin_html():
        from fastapi.responses import FileResponse
        admin_html_path = frontend_dir / "admin/admin.html"
        if admin_html_path.exists():
            return FileResponse(admin_html_path)
        fallback_html_path = project_root_dir / "frontend/admin/admin.html"
        if fallback_html_path.exists():
            return FileResponse(fallback_html_path)
        raise HTTPException(status_code=404, detail=f"admin.html not found in {frontend_dir}/admin or {project_root_dir}/frontend/admin")

    @app.get("/", include_in_schema=False)
    async def serve_user_html():
        from fastapi.responses import FileResponse
        user_html_path = frontend_dir / "user/index.html"
        if user_html_path.exists():
            return FileResponse(user_html_path)
        fallback_html_path = project_root_dir / "frontend/user/index.html"
        if fallback_html_path.exists():
            return FileResponse(fallback_html_path)
        raise HTTPException(status_code=404, detail=f"index.html not found in {frontend_dir}/user or {project_root_dir}/frontend/user")

    print(f"User UI (index.html) is available at the root path ('/').")
    print(f"Admin UI (admin.html) is available at path ('/admin').")

else:
    print(f"Frontend directory not found at expected location: {frontend_dir} (or alternatives tried). Ensure your 'frontend' directory containing admin.html, admin_script.js, etc., is correctly placed relative to the backend app or define FRONTEND_DIR_PATH environment variable.")
    print("Static file serving for admin UI will be skipped.")

# --- AI Client Initialization Helper --- 
def get_ai_client(model_name, api_key):
    """Initializes and returns the correct AI client based on model name."""
    if model_name.startswith("gpt"):
        if not api_key:
            raise ValueError("OpenAI APIキーが設定されていません。")
        try:
            return OpenAI(api_key=api_key)
        except Exception as e:
            raise ValueError(f"OpenAI Client Error: {e}")
    elif model_name.startswith("claude"):
        if not api_key:
            raise ValueError("Anthropic APIキーが設定されていません。")
        try:
            return Anthropic(api_key=api_key)
        except Exception as e:
            raise ValueError(f"Anthropic Client Error: {e}")
    elif model_name.startswith("gemini"):
        if not api_key:
             raise ValueError("Google APIキーが設定されていません。")
        try:
             genai.configure(api_key=api_key) # Configure library
             # Return the configured model object directly for gemini
             return genai.GenerativeModel('gemini-1.5-pro-latest') 
        except Exception as e:
             raise ValueError(f"Google Client Error: {e}")
    else:
        raise ValueError(f"未対応のモデルです: {model_name}")

# --- Function to build prompts ---
def build_prompt(data):
    limit_personality = os.environ.get("LIMIT_PERSONALITY", "100") 
    limit_reason = os.environ.get("LIMIT_REASON", "100")
    limit_behavior = os.environ.get("LIMIT_BEHAVIOR", "100")
    limit_reviews = os.environ.get("LIMIT_REVIEWS", "100")
    limit_values = os.environ.get("LIMIT_VALUES", "100")
    limit_demands = os.environ.get("LIMIT_DEMANDS", "100")

    # --- Patient Type Descriptions ---
    patient_type_details_map = {
        '利便性重視型': { "description": 'アクセスの良さ、待ち時間の短さ、診療時間の柔軟性など、便利さを最優先', "example": '忙しいビジネスパーソン、オンライン診療を好む患者' },
        '専門医療追求型': { "description": '専門医や高度専門医療機関での治療を希望し、医師の経歴や実績を重視', "example": '難病患者、複雑な症状を持つ患者' },
        '予防健康管理型': { "description": '病気になる前の予防や早期発見、健康維持に関心が高い', "example": '定期健診を欠かさない人、予防接種に積極的な人' },
        '代替医療志向型': { "description": '漢方、鍼灸、ホメオパシーなど、西洋医学以外の選択肢を積極的に取り入れる', "example": '自然療法愛好者、慢性疾患の患者' },
        '経済合理型': { "description": '自己負担額、保険適用の有無、費用対効果を重視', "example": '経済的制約のある患者、医療費控除を意識する人' },
        '情報探求型': { "description": '徹底的な情報収集、セカンドオピニオン取得、比較検討を行う', "example": '高学歴層、慎重な意思決定を好む患者' },
        '革新技術指向型': { "description": '最先端の医療技術、新薬、臨床試験などに積極的に関心を持つ', "example": '既存治療で効果が出なかった患者、医療イノベーションに関心がある人' },
        '対話重視型': { "description": '医師からの丁寧な説明や対話を求め、質問が多い', "example": '不安を感じやすい患者、医療従事者' },
        '信頼基盤型': { "description": 'かかりつけ医との長期的な関係や医療機関の評判を重視', "example": '地域密着型の患者、同じ医師に長期通院する患者' },
        '緊急解決型': { "description": '症状の即時改善を求め、緊急性を重視', "example": '急性疾患患者、痛みに耐性が低い患者' },
        '受動依存型': { "description": '医師の判断に全面的に依存し、自らの決定より医師の指示を優先', "example": '高齢者、医療知識が少ない患者' },
        '自律決定型': { "description": '自分の治療に主体的に関わり、最終決定権を持ちたいと考える', "example": '医療リテラシーが高い患者、自己管理を好む慢性疾患患者' }
    }

    prompt_parts = [
        "以下の情報に基づいて、医療系のペルソナを作成してください。",
        "各項目は自然な文章で記述し、**日本語で、指定されたおおよその文字数制限に従ってください**。",
        "",
        "# 利用者からの入力情報"
    ]

    # 基本情報
    basic_info = {
        "診療科": data.get('department'),
        "ペルソナ作成目的": data.get('purpose'),
        "名前": data.get('name'),
        "性別": data.get('gender'),
        "年齢": data.get('age'),
        "都道府県": data.get('prefecture'),
        "市区町村": data.get('municipality'),
        "家族構成": data.get('family'),
        "職業": data.get('occupation'),
        "年収": data.get('income'),
        "趣味": data.get('hobby'),
        "ライフイベント": data.get('life_events'),
        "患者タイプ": data.get('patient_type')
    }
    # setting_type と patient_type も追加
    if data.get('setting_type'):
        basic_info["基本情報設定タイプ"] = data.get('setting_type')

    for key, value in basic_info.items():
        if value: # 値が存在する場合のみプロンプトに追加
            prompt_parts.append(f"- {key}: {value}")
            if key == "患者タイプ" and value in patient_type_details_map:
                details = patient_type_details_map[value]
                prompt_parts.append(f"  - 患者タイプの特徴: {details['description']}")
                prompt_parts.append(f"  - 患者タイプの例: {details['example']}")
        # 「選択された患者タイプ」の(自動生成)条件から patient_type を除外 (「患者タイプ」で処理されるため)
        elif key in ["名前", "性別", "年齢", "都道府県", "市区町村", "家族構成", "職業", "年収", "趣味", "ライフイベント"] and key != "患者タイプ": 
             prompt_parts.append(f"- {key}: (自動生成)")
        elif key == "患者タイプ" and not value and data.get('setting_type') == 'patient_type': # setting_typeがpatient_typeで患者タイプが未選択の場合
             prompt_parts.append(f"- {key}: (指定なし/自動生成)")

    # Step 4の固定追加項目
    fixed_additional_info = {
        "座右の銘": data.get('motto'),
        "最近の悩み/関心": data.get('concerns'),
        "好きな有名人/尊敬する人物": data.get('favorite_person'),
        "よく見るメディア/SNS": data.get('media_sns'),
        "性格キーワード": data.get('personality_keywords'),
        "最近した健康に関する行動": data.get('health_actions'),
        "休日の過ごし方": data.get('holiday_activities'),
        "キャッチコピー": data.get('catchphrase'),
    }
    has_fixed_additional_info = any(fixed_additional_info.values())
    if has_fixed_additional_info:
        prompt_parts.append("\n## 追加情報（固定項目）")
        for key, value in fixed_additional_info.items():
            if value:
                prompt_parts.append(f"- {key}: {value}")

    # Step 4の動的追加項目
    additional_field_names = data.get('additional_field_name', [])
    additional_field_values = data.get('additional_field_value', [])
    
    dynamic_additional_info = []
    if isinstance(additional_field_names, list) and isinstance(additional_field_values, list):
        for i in range(len(additional_field_names)):
            field_name = additional_field_names[i]
            field_value = additional_field_values[i] if i < len(additional_field_values) else None
            if field_name and field_value: # 項目名と内容の両方がある場合のみ
                dynamic_additional_info.append(f"- {field_name}: {field_value}")
    
    if dynamic_additional_info:
        prompt_parts.append("\n## 追加情報（自由入力項目）")
        prompt_parts.extend(dynamic_additional_info)

    prompt_parts.append("\n# 生成項目 (日本語で、指定文字数程度で)")
    prompt_parts.append("以下の項目について、上記情報に基づいた自然な文章を生成してください。")
    prompt_parts.append(f"\n1.  **性格（価値観・人生観）**: (日本語で{limit_personality}文字程度)")
    prompt_parts.append(f"2.  **通院理由**: (日本語で{limit_reason}文字程度)")
    prompt_parts.append(f"3.  **症状通院頻度・行動パターン**: (日本語で{limit_behavior}文字程度)")
    prompt_parts.append(f"4.  **口コミの重視ポイント**: (日本語で{limit_reviews}文字程度)")
    prompt_parts.append(f"5.  **医療機関への価値観・行動傾向**: (日本語で{limit_values}文字程度)")
    prompt_parts.append(f"6.  **医療機関に求めるもの**: (日本語で{limit_demands}文字程度)")
    
    return "\n".join(prompt_parts)

# --- Function to parse AI response ---
def parse_ai_response(text):
    """Extract sections from AI-generated text response."""
    sections = {
        "personality": "",
        "reason": "",
        "behavior": "",
        "reviews": "",
        "values": "",
        "demands": ""
    }
    
    # Try to parse structured output
    try:
        lines = text.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header for personality section
            if line.startswith("1.") and ("性格" in line or "価値観" in line or "人生観" in line):
                current_section = "personality"
                # Remove the header and keep only content
                content = line.split(':', 1)[1].strip() if ':' in line else ""
                if content:
                    sections[current_section] = content
                continue
                
            # Check for reason section
            elif line.startswith("2.") and "通院理由" in line:
                current_section = "reason"
                content = line.split(':', 1)[1].strip() if ':' in line else ""
                if content:
                    sections[current_section] = content
                continue
                
            # Check for behavior section
            elif line.startswith("3.") and ("症状" in line or "通院頻度" in line or "行動パターン" in line):
                current_section = "behavior"
                content = line.split(':', 1)[1].strip() if ':' in line else ""
                if content:
                    sections[current_section] = content
                continue
                
            # Check for reviews section
            elif line.startswith("4.") and ("口コミ" in line or "重視ポイント" in line):
                current_section = "reviews"
                content = line.split(':', 1)[1].strip() if ':' in line else ""
                if content:
                    sections[current_section] = content
                continue
                
            # Check for values section
            elif line.startswith("5.") and ("医療機関" in line or "価値観" in line or "行動傾向" in line):
                current_section = "values"
                content = line.split(':', 1)[1].strip() if ':' in line else ""
                if content:
                    sections[current_section] = content
                continue
                
            # Check for demands section
            elif line.startswith("6.") and ("医療機関" in line or "求めるもの" in line):
                current_section = "demands"
                content = line.split(':', 1)[1].strip() if ':' in line else ""
                if content:
                    sections[current_section] = content
                continue
                
            # If we're in a section, append text
            if current_section and not line.startswith(("#", "##")):
                if sections[current_section]:
                    sections[current_section] += " " + line
                else:
                    sections[current_section] = line
    
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        traceback.print_exc()
    
    return sections

@app.post("/api/generate")
async def generate_persona(request: Request):
    try:
        data = await request.json()
        
        # Get model and API key from environment variables
        model_name = os.environ.get("AI_MODEL", "gpt-3.5-turbo")
        api_key = None
        
        # Set appropriate API key based on model type
        if model_name.startswith("gpt"):
            api_key = os.environ.get("OPENAI_API_KEY")
        elif model_name.startswith("claude"):
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        elif model_name.startswith("gemini"):
            api_key = os.environ.get("GOOGLE_API_KEY")
        
        # For testing purposes, if no API key is set, return dummy data
        if not api_key:
            print("No API key found. Returning dummy data for testing.")
            return {
                "personality": "真面目で責任感が強く、家族を大切にする。健康意識が高く、予防医療に関心がある。",
                "reason": "定期的な健康診断と、軽度の高血圧の管理のため。",
                "behavior": "3ヶ月に一度の定期検診に欠かさず通院。処方された降圧剤を規則正しく服用している。",
                "reviews": "医師の説明がわかりやすいこと、待ち時間が短いこと、スタッフの対応が丁寧であることを重視する。",
                "values": "信頼できる医師との長期的な関係を望む。予防医療に前向きで、医師のアドバイスを真摯に受け止める。",
                "demands": "わかりやすい説明と、必要に応じて専門医への適切な紹介。予防医療のアドバイスも欲しい。"
            }
            
        # Build prompt
        prompt_text = build_prompt(data)
        
        # Initialize AI client
        try:
            client = get_ai_client(model_name, api_key)
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"AI Client初期化エラー: {str(e)}"}
            )
        
        # Generate response from AI
        try:
            response_text = ""
            if model_name.startswith("gpt"):
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt_text}],
                    temperature=0.7,
                    max_tokens=2000
                )
                response_text = response.choices[0].message.content
            elif model_name.startswith("claude"):
                response = client.messages.create(
                    model=model_name,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt_text}]
                )
                response_text = response.content[0].text
            elif model_name.startswith("gemini"):
                response = client.generate_content(prompt_text)
                response_text = response.text
            
            # Parse AI response
            sections = parse_ai_response(response_text)
            
            # Return parsed response
            return sections
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"AI生成エラー: {str(e)}"}
            )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"サーバーエラー: {str(e)}"}
        )

@app.get("/health", summary="Health check endpoint", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint to confirm the API is running.
    """
    return {"status": "ok"}

# To run this app locally (from the 'backend' directory, assuming main.py is in 'app'):
# Ensure 'app' is a package (has __init__.py if needed, though often not for FastAPI structure like this)
# cd backend
# python -m uvicorn app.main:app --reload --port 8000

# If your structure is flatter, e.g. main.py in 'backend' root:
# cd backend
# uvicorn main:app --reload --port 8000 