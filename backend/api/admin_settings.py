from fastapi import APIRouter, HTTPException, Body, status, UploadFile, File, Form
from typing import Dict, List, Optional
import pandas as pd
import io

from ..services import crud
from ..models import schemas
from ..services import rag_processor

router = APIRouter()

@router.get(
    "/api/admin/settings",
    response_model=schemas.AdminSettings,
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
    response_model=schemas.AdminSettings,
    summary="Update model selection settings",
    tags=["Admin Settings"]
)
async def update_model_settings_endpoint(
    model_update: schemas.ModelSettingsUpdate = Body(...)
):
    try:
        success = crud.update_model_settings(schemas.ModelSettings(**model_update.model_dump()))
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

@router.post(
    "/api/admin/settings/char-limits",
    response_model=schemas.AdminSettings,
    summary="Update character limit settings",
    tags=["Admin Settings"]
)
async def update_char_limits_endpoint(
    char_limit_update: schemas.CharLimitsUpdate = Body(...)
):
    try:
        new_limits = char_limit_update.limits
        success = crud.update_char_limits(new_limits)
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

@router.post(
    "/api/admin/rag/upload",
    response_model=schemas.RAGUploadResponse,
    summary="Upload CSV data for RAG",
    tags=["RAG Settings"]
)
async def upload_rag_data(
    file: UploadFile = File(...),
    table_name: Optional[str] = Form(None)
):
    """
    Upload a CSV file to be stored in the RAG database.
    If table_name is not provided, it defaults to the filename without extension.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    # Default table name to filename without extension if not provided
    if not table_name:
        table_name = file.filename.rsplit('.', 1)[0]
    
    try:
        # Read CSV content
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        
        # Upload to RAG processor
        success = rag_processor.upload_csv_to_db(df, table_name)
        
        if success:
            return schemas.RAGUploadResponse(
                success=True,
                message=f"Successfully uploaded {len(df)} rows to table '{table_name}'",
                table_name=table_name,
                row_count=len(df)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload data to RAG database"
            )
            
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The CSV file is empty or invalid"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the file: {str(e)}"
        )

@router.get(
    "/api/admin/rag/tables",
    summary="List all RAG tables",
    tags=["RAG Settings"]
)
async def list_rag_tables():
    """Get a list of all uploaded RAG data with their metadata."""
    try:
        # 既存のRAGデータを取得
        rag_data = rag_processor.get_uploaded_rag_data()
        
        # RAGTableInfoフォーマットに変換
        table_info = []
        for item in rag_data:
            table_info.append({
                "table_name": item.get("specialty", ""),
                "row_count": item.get("current_records", 0),
                "created_at": item.get("uploaded_at", None),
                "filename": item.get("filename", ""),
                "specialty_code": item.get("specialty_code", "")
            })
        
        return table_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list RAG tables: {str(e)}"
        )

@router.delete(
    "/api/admin/rag/tables/{table_name}",
    response_model=Dict[str, str],
    summary="Delete RAG data",
    tags=["RAG Settings"]
)
async def delete_rag_table(table_name: str):
    """Delete RAG data for a specific specialty."""
    try:
        # table_nameは実際にはspecialty_codeとして使用
        success = rag_processor.delete_rag_data(table_name)
        if success:
            return {"success": "true", "message": f"RAGデータ（{table_name}）を削除しました"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"RAGデータ '{table_name}' が見つかりません"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete RAG data: {str(e)}"
        )