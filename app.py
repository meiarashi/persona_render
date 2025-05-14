from flask import Flask, request, jsonify, send_from_directory, send_file, Response
from flask_cors import CORS
import random
import os
import traceback
# --- Import DB and AI Libraries ---
# from flask_sqlalchemy import SQLAlchemy # Removed SQLAlchemy import
from openai import OpenAI
import google.generativeai as genai
from anthropic import Anthropic
from fpdf import FPDF
import io
from urllib.parse import quote
from pptx import Presentation
from pptx.util import Inches, Pt # Inches for image size, Pt for font size
from pptx.enum.text import PP_ALIGN # For text alignment

# --- Flask App Setup ---
app = Flask(__name__, static_url_path='', static_folder='.')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///settings.db' # Removed DB config
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Removed DB config
# db = SQLAlchemy(app) # Removed SQLAlchemy initialization
CORS(app)

# --- Database Model Definition --- (Removed)
# class Setting(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     key = db.Column(db.String(80), unique=True, nullable=False)
#     value = db.Column(db.String(500), nullable=True)
#
#     def __repr__(self):
#         return f'<Setting {self.key}: {self.value}>'

# --- Helper Functions --- (Removed)
# def get_setting(key, default=None):
#     """Gets a setting value from the database."""
#     setting = Setting.query.filter_by(key=key).first()
#     return setting.value if setting else default
#
# def set_setting(key, value):
#     """Sets or updates a setting value in the database."""
#     setting = Setting.query.filter_by(key=key).first()
#     if setting:
#         setting.value = value
#     else:
#         setting = Setting(key=key, value=value)
#         db.session.add(setting)
#     db.session.commit()

# --- Function to initialize DB and load initial settings --- (Removed)
# def initialize_database():
#     with app.app_context():
#         db.create_all() # Create table if it doesn't exist
#
#         # Load initial DEFAULTS for non-sensitive settings if not already in DB
#         if not get_setting("selected_text_model"):
#              set_setting("selected_text_model", "gpt-4.1")
#         if not get_setting("selected_image_model"):
#              set_setting("selected_image_model", "dall-e-3")
#         # Load initial char limits if not already in DB
#         default_limits = {
#             "personality": "100", "reason": "100", "behavior": "100",
#             "reviews": "100", "values": "100", "demands": "100"
#         }
#         for key, default_value in default_limits.items():
#             db_key = f"limit_{key}"
#             if not get_setting(db_key):
#                  set_setting(db_key, default_value)
#
#         # Add default output settings
#         if get_setting("output_pdf_enabled") is None: # Check if None explicitly
#              set_setting("output_pdf_enabled", "true") # Store as string 'true'/'false'
#         if get_setting("output_ppt_enabled") is None:
#              set_setting("output_ppt_enabled", "true")
#         if get_setting("output_gslide_enabled") is None:
#              set_setting("output_gslide_enabled", "false") # Default GSlide to disabled

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

# --- Prompt and Response Parsing Helpers --- 
def build_prompt(data):
    limit_personality = os.environ.get("LIMIT_PERSONALITY", "100")
    limit_reason = os.environ.get("LIMIT_REASON", "100")
    limit_behavior = os.environ.get("LIMIT_BEHAVIOR", "100")
    limit_reviews = os.environ.get("LIMIT_REVIEWS", "100")
    limit_values = os.environ.get("LIMIT_VALUES", "100")
    limit_demands = os.environ.get("LIMIT_DEMANDS", "100")

    # --- Patient Type Descriptions (Copied from script.js) ---
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
        # 以下の重複する可能性のある「選択された患者タイプ」の追加はコメントアウトまたは削除
        # if data.get('setting_type') == 'patient_type' and data.get('patient_type'):
        #     basic_info["選択された患者タイプ"] = data.get('patient_type')


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
        # '診療科', '作成目的', '基本情報設定タイプ' は値がなければ「指定なし」とするか、キー自体含めないか検討。ここでは値がある場合のみ表示。

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
    
    prompt_parts.append("\n回答は、各生成項目の見出しを含めず、項目に対応するテキストのみを以下の形式で記述してください。")
    prompt_parts.append("---性格---")
    prompt_parts.append("[ここに性格のテキスト]")
    prompt_parts.append("---通院理由---")
    prompt_parts.append("[ここに通院理由のテキスト]")
    prompt_parts.append("---行動パターン---")
    prompt_parts.append("[ここに症状通院頻度・行動パターンのテキスト]")
    prompt_parts.append("---口コミ重視点---")
    prompt_parts.append("[ここに口コミの重視ポイントのテキスト]")
    prompt_parts.append("---医療価値観---")
    prompt_parts.append("[ここに医療機関への価値観・行動傾向のテキスト]")
    prompt_parts.append("---医療求めるもの---")
    prompt_parts.append("[ここに医療機関に求めるもののテキスト]")

    return "\n".join(prompt_parts)

def parse_ai_response(text):
    details = {}
    sections = {
        "---性格---": "personality",
        "---通院理由---": "reason",
        "---行動パターン---": "behavior",
        "---口コミ重視点---": "reviews",
        "---医療価値観---": "values",
        "---医療求めるもの---": "demands"
    }
    current_key = None
    current_text = []

    # AIの応答がNoneの場合のフォールバック
    if text is None:
        print("Warning: AI response text is None.")
        for marker, key in sections.items():
            details[key] = "(AIからの応答がありませんでした)"
        return details

    for line in text.splitlines():
        found_key = None
        for marker, key in sections.items():
            if line.strip() == marker:
                found_key = key
                break
        if found_key:
            if current_key and current_text:
                details[sections[current_key]] = "\n".join(current_text).strip()
            current_key = marker # ここを sections[found_key] ではなく marker にする
            current_text = []
        elif current_key: # current_key が None でないことを確認
            current_text.append(line)
    
    if current_key and current_text: # ループ終了後、最後のセクションを処理
        details[sections[current_key]] = "\n".join(current_text).strip()
    
    # 解析できなかったセクションにデフォルト値を設定
    for marker, key in sections.items():
        if key not in details:
            details[key] = "(AIからの応答が解析できませんでした)"
    return details

# --- Static File Serving --- 
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def serve_admin():
     return send_from_directory('.', 'admin.html')

# --- API Endpoints --- 
@app.route('/api/generate', methods=['POST'])
def generate_persona():
    data_from_frontend = request.json
    if not data_from_frontend:
        return jsonify({"error": "No data provided"}), 400

    profile_data = data_from_frontend.copy()

    print(f"--- DEBUG: Received setting_type: '{profile_data.get('setting_type')}' (type: {type(profile_data.get('setting_type'))})")
    is_auto_setting = (profile_data.get('setting_type') == 'auto')
    print(f"--- DEBUG: is_auto_setting evaluated to: {is_auto_setting}")

    if is_auto_setting:
        profile_data['name'] = profile_data.get('name') or "山田 太郎"
        profile_data['gender'] = profile_data.get('gender') or "男性"
        profile_data['age'] = profile_data.get('age') or "30"
        profile_data['location'] = profile_data.get('location') or "東京都 渋谷区"
        profile_data['occupation'] = profile_data.get('occupation') or "会社員"
        profile_data['income'] = profile_data.get('income') or "500-600万円"
        profile_data['hobby'] = profile_data.get('hobby') or "読書"

    selected_text_model = os.environ.get("SELECTED_TEXT_MODEL", "gpt-4.1")
    api_key = None
    if selected_text_model.startswith("gpt"):
        api_key = os.environ.get("OPENAI_API_KEY")
    elif selected_text_model.startswith("claude"):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    elif selected_text_model.startswith("gemini"):
        api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        error_message = f"{selected_text_model} を利用するための APIキーが環境変数に設定されていません。"
        if selected_text_model.startswith("gpt"): error_message += " (環境変数名: OPENAI_API_KEY)"
        elif selected_text_model.startswith("claude"): error_message += " (環境変数名: ANTHROPIC_API_KEY)"
        elif selected_text_model.startswith("gemini"): error_message += " (環境変数名: GOOGLE_API_KEY)"
        return jsonify({"error": error_message}), 500

    try:
        ai_client = get_ai_client(selected_text_model, api_key)
        prompt = build_prompt(profile_data)
        response_text = ""
        if selected_text_model.startswith("gpt"):
            chat_completion = ai_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=selected_text_model,
            )
            response_text = chat_completion.choices[0].message.content
        elif selected_text_model.startswith("claude"):
            message = ai_client.messages.create(
                model=selected_text_model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text
        elif selected_text_model.startswith("gemini"):
            response = ai_client.generate_content(prompt)
            response_text = response.text

        generated_details = parse_ai_response(response_text)
        image_url = None

        # --- Image Generation (常に試行) ---
        # selected_image_model = os.environ.get("SELECTED_IMAGE_MODEL", "dall-e-3")
        # image_api_key_for_dalle = os.environ.get("OPENAI_API_KEY")
        # 
        # if image_api_key_for_dalle and selected_image_model and selected_image_model != "none":
        #     try:
        #         image_client = OpenAI(api_key=image_api_key_for_dalle)
        #         img_name = profile_data.get('name', 'person')
        #         img_age = profile_data.get('age', 'age unknown')
        #         img_gender = profile_data.get('gender', 'gender unknown')
        #         img_occupation = profile_data.get('occupation')
        #
        #         img_prompt_parts = [
        #             f"Create a profile picture for a persona named {img_name}",
        #             f"who is {img_age}, {img_gender}.",
        #             "Style: realistic photo."
        #         ]
        #         if img_occupation and img_occupation.strip():
        #             img_prompt_parts.append(f"Occupation: {img_occupation}.")
        #         
        #         img_prompt = " ".join(img_prompt_parts)
        #         print(f"Attempting image generation with prompt: {img_prompt}")
        #
        #         image_response = image_client.images.generate(
        #             model=selected_image_model,
        #             prompt=img_prompt,
        #             size="1024x1024", 
        #             quality="standard", 
        #             n=1,
        #         )
        #         image_url = image_response.data[0].url
        #         print(f"Image generated successfully: {image_url}")
        #     except Exception as img_e:
        #         print(f"Image generation failed: {img_e}")
        #         traceback.print_exc()
        # else:
        #     print(f"Image generation skipped: OpenAI API key for DALL-E not found or image model is '{selected_image_model}'.")

        # Set a dummy image URL
        image_url = "https://via.placeholder.com/1024" # Example dummy image

        response_data = {
            "profile": profile_data,
            "details": generated_details,
            "image_url": image_url
        }
        return jsonify(response_data)

    except ValueError as ve:
        print(f"Value Error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"Error during AI generation: {e}")
        traceback.print_exc()
        return jsonify({"error": "ペルソナ生成中にエラーが発生しました。"}), 500

# --- Admin API Endpoints (Simplified for Environment Variables) --- 

@app.route('/api/admin/settings', methods=['GET'])
def get_all_settings():
    """Gets settings from environment variables."""
    settings = {
        # API Keys (Return placeholders or indicate if set, DO NOT RETURN ACTUAL KEYS)
        "openai_api_key": "Set" if os.environ.get("OPENAI_API_KEY") else "Not Set",
        "google_api_key": "Set" if os.environ.get("GOOGLE_API_KEY") else "Not Set",
        "anthropic_api_key": "Set" if os.environ.get("ANTHROPIC_API_KEY") else "Not Set",
        # Selected Models
        "selected_text_model": os.environ.get("SELECTED_TEXT_MODEL", "gpt-4.1"),
        "selected_image_model": os.environ.get("SELECTED_IMAGE_MODEL", "dall-e-3"),
        # Limits
        "limit_personality": os.environ.get("LIMIT_PERSONALITY", "100"),
        "limit_reason": os.environ.get("LIMIT_REASON", "100"),
        "limit_behavior": os.environ.get("LIMIT_BEHAVIOR", "100"),
        "limit_reviews": os.environ.get("LIMIT_REVIEWS", "100"),
        "limit_values": os.environ.get("LIMIT_VALUES", "100"),
        "limit_demands": os.environ.get("LIMIT_DEMANDS", "100"),
        # Output Formats Enabled (Read from Env Vars, default to 'true')
        "output_pdf_enabled": os.environ.get("OUTPUT_PDF_ENABLED", "true"),
        "output_ppt_enabled": os.environ.get("OUTPUT_PPT_ENABLED", "true"),
        "output_gslide_enabled": os.environ.get("OUTPUT_GSLIDE_ENABLED", "false") # Default false
    }
    return jsonify(settings)

# --- Settings Saving Endpoints (Removed/Placeholder) --- 
# Saving settings directly via API is not suitable for environment variables.
# These need to be set in the Render dashboard.
@app.route('/api/admin/settings/api', methods=['POST'])
def save_api_settings():
    # This endpoint is now effectively read-only for env vars
    return jsonify({"message": "APIキーはRenderの環境変数で設定してください。"}), 405 # Method Not Allowed

@app.route('/api/admin/settings/limits', methods=['POST'])
def save_limit_settings():
    # This endpoint is now effectively read-only for env vars
    return jsonify({"message": "文字数制限はRenderの環境変数で設定してください。"}), 405 # Method Not Allowed

@app.route('/api/admin/settings/output', methods=['POST'])
def save_output_settings():
     # This endpoint is now effectively read-only for env vars
     return jsonify({"message": "出力設定はRenderの環境変数で設定してください。"}), 405 # Method Not Allowed


# --- User-facing Output Settings Endpoint --- 
@app.route('/api/settings/output', methods=['GET'])
def get_output_settings_for_user():
    """Gets output format enabled status from environment variables."""
    settings = {
        "output_pdf_enabled": os.environ.get("OUTPUT_PDF_ENABLED", "true").lower() == "true",
        "output_ppt_enabled": os.environ.get("OUTPUT_PPT_ENABLED", "true").lower() == "true",
        "output_gslide_enabled": os.environ.get("OUTPUT_GSLIDE_ENABLED", "false").lower() == "true"
    }
    return jsonify(settings)


# --- PDF Generation --- 
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    # Add a font that supports Japanese characters
    # Make sure you have a Japanese font file (e.g., ipag.ttf) accessible
    # You might need to download one if it's not on your system
    # Place the .ttf file in the same directory as app.py or provide a full path
    try:
        # Register Regular font
        pdf.add_font("ipa", "", "ipaexg.ttf", uni=True)
        # Register Bold style using the same file
        pdf.add_font("ipa", "B", "ipaexg.ttf", uni=True)
        pdf.set_font("ipa", size=16)
    except RuntimeError as e: # Catch specific error
        print(f"WARNING: Could not load/register font 'ipaexg.ttf'. Error: {e}. Using default font.")
        pdf.set_font("Arial", size=16) # Fallback font

    profile = data.get('profile', {})
    details = data.get('details', {})

    # --- Profile Section ---
    pdf.set_font_size(18)
    pdf.cell(0, 10, profile.get('name', 'Unknown Persona'), ln=True, align='C')
    pdf.ln(10)

    pdf.set_font_size(12)
    profile_items = [
        ("性別", profile.get('gender')),
        ("年齢", profile.get('age')),
        ("職業", profile.get('occupation')),
        ("居住地", profile.get('location')),
        ("家族構成", profile.get('family')),
        # Add other profile fields if they exist
    ]
    for key, value in profile_items:
        if value: # Only add if value exists
             pdf.set_font(style='B') # Use the same font, set style to Bold
             pdf.cell(40, 8, f"{key}:", border=0)
             pdf.set_font(style='') # Reset font style to regular
             pdf.multi_cell(0, 8, str(value), border=0, ln=True) # Use multi_cell for potential line breaks
    pdf.ln(5)


    # --- Details Section ---
    # Map internal keys to Japanese headers
    header_map = {
        "personality": "性格（価値観・人生観）",
        "reason": "通院理由",
        "behavior": "症状通院頻度・行動パターン",
        "reviews": "口コミの重視ポイント",
        "values": "医療機関への価値観・行動傾向",
        "demands": "医療機関に求めるもの"
    }

    pdf.set_text_color(0,0,0)
    pdf.set_fill_color(230, 230, 230) # Light grey background for headers

    # Iterate through the map to maintain order and use Japanese headers
    for key, japanese_header in header_map.items():
        value = details.get(key) # Get value using the internal key
        if value: # Only add if value exists
            # Explicitly set header font style and size
            pdf.set_font("ipa", style='B', size=14) # Bold, Size 14 for header
            pdf.cell(0, 10, japanese_header, ln=True, fill=True) # Use Japanese header

            # Explicitly set content font style and size
            pdf.set_font("ipa", style='', size=11) # Regular, Size 11 for content
            pdf.multi_cell(0, 7, str(value), ln=True) # Use multi_cell for text wrapping
            pdf.ln(4) # Space between sections

    # Generate PDF in memory
    pdf_output = pdf.output() # Get output as bytes directly
    buffer = io.BytesIO(pdf_output)
    buffer.seek(0)
    return buffer

@app.route('/api/download/pdf', methods=['POST'])
def download_pdf():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        pdf_buffer = generate_pdf(data) # generate_pdf returns a BytesIO buffer
        # Construct filename, handle potential missing name
        profile_name = data.get('profile', {}).get('name', 'persona')
        safe_profile_name = "".join(c if c.isalnum() or c in [' ', '(', ')'] else '_' for c in profile_name)
        filename_utf8 = f"{safe_profile_name}_persona.pdf"
        filename_encoded = quote(filename_utf8) # Use urllib.parse.quote

        # Create Response object manually
        response = Response(pdf_buffer.getvalue(), mimetype='application/pdf')
        # Set headers on the response object
        response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{filename_encoded}"

        return response # Return the Response object

        # --- Previous code using send_file (commented out) ---
        # headers = {
        #     'Content-Disposition': f"attachment; filename*=UTF-8''{filename_encoded}"
        # }
        # return send_file(
        #     pdf_buffer,
        #     mimetype='application/pdf',
        #     as_attachment=True,
        #     headers=headers # Pass the custom header
        # )
    except Exception as e:
        print(f"Error generating PDF: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging
        return jsonify({"error": "Failed to generate PDF"}), 500

# Helper function to generate PPT (basic implementation)
def generate_ppt(data):
    prs = Presentation()
    profile = data.get('profile', {})
    details = data.get('details', {})

    # --- Title Slide ---
    title_slide_layout = prs.slide_layouts[0] # Use title slide layout
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1] # Placeholder for subtitle

    title.text = profile.get('name', 'ペルソナシート')
    subtitle.text = "自動生成されたペルソナの詳細"

    # --- Profile Slide ---
    profile_slide_layout = prs.slide_layouts[5] # Use blank layout
    slide = prs.slides.add_slide(profile_slide_layout)

    # Add a title textbox
    title_shape = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(9), Inches(0.8))
    title_frame = title_shape.text_frame
    title_frame.text = "プロフィール"
    title_frame.paragraphs[0].font.size = Pt(28)
    title_frame.paragraphs[0].font.bold = True

    # Add profile details in a table-like structure (using text boxes)
    left = Inches(0.5)
    top = Inches(1.2)
    width = Inches(8.5)
    height = Inches(0.4) # Height per item

    profile_items = [
        ("名前", profile.get('name')),
        ("性別", profile.get('gender')),
        ("年齢", profile.get('age')),
        ("職業", profile.get('occupation')),
        ("居住地", profile.get('location')),
        ("家族構成", profile.get('family')),
        ("年収", profile.get('income')),
        ("趣味", profile.get('hobby')),
        # Add other profile fields if they exist
    ]

    current_top = top
    for key, value in profile_items:
        if value:
            # Key textbox
            txBox_key = slide.shapes.add_textbox(left, current_top, Inches(2), height)
            tf_key = txBox_key.text_frame
            p_key = tf_key.add_paragraph()
            p_key.text = f"{key}:"
            p_key.font.bold = True
            p_key.font.size = Pt(14)

            # Value textbox
            txBox_val = slide.shapes.add_textbox(left + Inches(2), current_top, Inches(6.5), height)
            tf_val = txBox_val.text_frame
            p_val = tf_val.add_paragraph()
            p_val.text = str(value)
            p_val.font.size = Pt(14)

            current_top += height # Move down for the next item


    # --- Details Slides ---
    header_map = { # Reuse the map from PDF generation
        "personality": "性格（価値観・人生観）",
        "reason": "通院理由",
        "behavior": "症状通院頻度・行動パターン",
        "reviews": "口コミの重視ポイント",
        "values": "医療機関への価値観・行動傾向",
        "demands": "医療機関に求めるもの"
    }

    for key, japanese_header in header_map.items():
        value = details.get(key)
        if value:
            detail_slide_layout = prs.slide_layouts[1] # Title and Content layout
            slide = prs.slides.add_slide(detail_slide_layout)

            title = slide.shapes.title
            body = slide.placeholders[1] # Content placeholder

            title.text = japanese_header
            tf = body.text_frame
            tf.text = str(value) # Set the main content
            # Adjust font size if needed (optional)
            for paragraph in tf.paragraphs:
                 paragraph.font.size = Pt(14)


    # Save presentation to a BytesIO buffer
    ppt_buffer = io.BytesIO()
    prs.save(ppt_buffer)
    ppt_buffer.seek(0)
    return ppt_buffer

@app.route('/api/download/ppt', methods=['POST'])
def download_ppt():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        ppt_buffer = generate_ppt(data)
        profile_name = data.get('profile', {}).get('name', 'persona')
        safe_profile_name = "".join(c if c.isalnum() or c in [' ', '(', ')'] else '_' for c in profile_name)
        filename_utf8 = f"{safe_profile_name}_persona.pptx" # Use .pptx extension
        filename_encoded = quote(filename_utf8)

        response = Response(
            ppt_buffer.getvalue(),
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation' # PPTX mimetype
        )
        response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{filename_encoded}"

        return response

    except Exception as e:
        print(f"Error generating PPT: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to generate PPT"}), 500

# --- Run App --- (Removed)
# if __name__ == '__main__':
#     # initialize_database() # Removed DB initialization call
#     app.run(debug=True, port=5000) 