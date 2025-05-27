from fastapi import APIRouter, HTTPException, Body, status, UploadFile, File, Form
from typing import Dict, List, Optional
import pandas as pd
import io

from .. import crud
from .. import models
from .. import rag_processor

router = APIRouter()

@router.get(
    "/api/admin/settings",
    response_model=models.AdminSettings,
    summary="Get all current admin settings",
    tags=["Admin Settings"]
)
async def get_admin_settings():
    try:
        settings = crud.read_settings()
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read settings: {str(e)}"
        )

@router.post(
    "/api/admin/settings/models",
    response_model=models.AdminSettings,
    summary="Update model selection settings",
    tags=["Admin Settings"]
)
async def update_model_settings_endpoint(
    model_update: models.ModelSettingsUpdate = Body(...)
):
    try:
        success = crud.update_model_settings(models.ModelSettings(**model_update.model_dump()))
        if success:
            return crud.read_settings()
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to write model settings to file."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating model settings: {str(e)}"
        )

# Output settings are now part of the main /api/admin/settings GET endpoint
# and are read-only (controlled by environment variables).
# No separate POST endpoint is needed for output settings.

@router.post(
    "/api/admin/settings/limits",
    response_model=models.AdminSettings,
    summary="Update character limit目安 settings",
    tags=["Admin Settings"]
)
async def update_char_limits_endpoint(
    limits_update: models.CharLimitsUpdate = Body(...)
):
    try:
        success = crud.update_char_limits(limits_update.limits)
        if success:
            return crud.read_settings()
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to write character limit settings to file."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating character limits: {str(e)}"
        )

# RAG関連のエンドポイント
@router.post(
    "/api/admin/rag/upload",
    summary="Upload RAG data CSV file",
    tags=["RAG"]
)
async def upload_rag_data(
    specialty: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        # ファイルサイズ制限（10MB）
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="ファイルサイズが大きすぎます。10MB以下のファイルをアップロードしてください。"
            )
        
        # ファイルタイプチェック
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSVファイルのみアップロード可能です。"
            )
        
        # RAGデータベースの初期化
        rag_processor.init_rag_database()
        
        # pandasでCSVを読み込み（エンコーディングを試行）
        try:
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(io.StringIO(contents.decode('shift-jis')))
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CSVファイルのエンコーディングを認識できません。UTF-8またはShift-JISで保存してください。"
                )
        
        # CSVのカラムチェック
        required_columns = ['出力キーワード', '検索ボリューム(人)']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"必須カラムが不足しています: {', '.join(missing_columns)}"
            )
        
        # カラム名の確認（警告のため）
        expected_columns = [
            '順位', '出力キーワード', '検索ボリューム(人)', '重複ボリューム(人)',
            '特徴度', '検索時間差(日)', '男性割合(%)', '女性割合(%)',
            '10代（13歳〜）割合(%)', '20代割合(%)', '30代割合(%)', '40代割合(%)',
            '50代割合(%)', '60代割合(%)', '70代以上割合(%)', 'カテゴリー'
        ]
        
        unexpected_columns = [col for col in df.columns if col not in expected_columns]
        if unexpected_columns:
            print(f"Warning: 予期しないカラムが含まれています: {', '.join(unexpected_columns)}")
        
        # データを保存
        result = rag_processor.save_rag_data(specialty, df, file.filename)
        
        if result["success"]:
            message = f"RAGデータを正常にアップロードしました。"
            
            # カラムの不足を警告として追加
            missing_optional_columns = [col for col in expected_columns if col not in df.columns and col not in required_columns]
            if missing_optional_columns:
                message += f"\n警告: 一部のカラムが不足しています（{', '.join(missing_optional_columns)}）。デフォルト値が使用されます。"
            
            return {
                "message": message,
                "specialty": result["specialty"],
                "inserted_count": result["inserted_count"],
                "skipped_count": result["skipped_count"],
                "warnings": missing_optional_columns if missing_optional_columns else None
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"RAGデータの保存中にエラーが発生しました: {result.get('error', 'Unknown error')}"
            )
            
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="アップロードされたCSVファイルが空です。"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAGデータのアップロード中にエラーが発生しました: {str(e)}"
        )

@router.get(
    "/api/admin/rag/list",
    summary="Get list of uploaded RAG data",
    tags=["RAG"]
)
async def list_rag_data():
    try:
        # RAGデータベースの初期化（念のため）
        rag_processor.init_rag_database()
        
        # アップロード済みデータの一覧を取得
        uploaded_data = rag_processor.get_uploaded_rag_data()
        
        return {
            "rag_data": uploaded_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAGデータ一覧の取得中にエラーが発生しました: {str(e)}"
        )

@router.delete(
    "/api/admin/rag/{specialty}",
    summary="Delete RAG data for a specific specialty",
    tags=["RAG"]
)
async def delete_rag_data(specialty: str):
    try:
        success = rag_processor.delete_rag_data(specialty)
        
        if success:
            return {
                "message": f"{specialty}のRAGデータを削除しました。"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="RAGデータの削除に失敗しました。"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAGデータの削除中にエラーが発生しました: {str(e)}"
        )

@router.get(
    "/api/admin/rag/search",
    summary="Search RAG data",
    tags=["RAG"]
)
async def search_rag_data(
    specialty: str,
    age_group: Optional[str] = None,
    gender: Optional[str] = None,
    limit: int = 10
):
    try:
        results = rag_processor.search_rag_data(
            specialty=specialty,
            age_group=age_group,
            gender=gender,
            limit=limit
        )
        
        return {
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAGデータの検索中にエラーが発生しました: {str(e)}"
        ) 