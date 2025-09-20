from fastapi import APIRouter, HTTPException, Body, status, Depends
from typing import Dict, List, Optional

from backend.services import crud
from backend.models import schemas
from backend.services import rag_processor
from backend.middleware.auth import verify_admin_credentials

router = APIRouter()

@router.get(
    "/api/admin/settings",
    response_model=schemas.AdminSettings,
    summary="Get all current admin settings",
    tags=["Admin Settings"]
)
async def get_admin_settings(username: str = Depends(verify_admin_credentials)):
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
    model_update: schemas.ModelSettingsUpdate = Body(...),
    username: str = Depends(verify_admin_credentials)
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
    char_limit_update: schemas.CharLimitsUpdate = Body(...),
    username: str = Depends(verify_admin_credentials)
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




