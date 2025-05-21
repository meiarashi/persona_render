from fastapi import APIRouter, HTTPException, Body, status
from typing import Dict

from .. import crud
from .. import models

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

# Output settings endpoint removed

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