"""Configuration API endpoints"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any

from backend.utils import config_loader

router = APIRouter()

@router.get(
    "/api/config/departments",
    response_model=List[Dict[str, Any]],
    summary="Get all available departments",
    tags=["Configuration"]
)
async def get_departments():
    """Get list of all enabled departments"""
    try:
        return config_loader.load_departments()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load departments: {str(e)}"
        )

@router.get(
    "/api/config/purposes",
    response_model=List[Dict[str, Any]],
    summary="Get all available purposes",
    tags=["Configuration"]
)
async def get_purposes():
    """Get list of all enabled purposes"""
    try:
        return config_loader.load_purposes()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load purposes: {str(e)}"
        )

@router.get(
    "/api/config/patient-types",
    response_model=List[Dict[str, Any]],
    summary="Get all available patient types",
    tags=["Configuration"]
)
async def get_patient_types():
    """Get list of all enabled patient types"""
    try:
        return config_loader.load_patient_types()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load patient types: {str(e)}"
        )

@router.get(
    "/api/config/ai-models",
    response_model=Dict[str, List[Dict[str, Any]]],
    summary="Get all available AI models",
    tags=["Configuration"]
)
async def get_ai_models():
    """Get list of all enabled AI models (text and image)"""
    try:
        return config_loader.load_ai_models()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load AI models: {str(e)}"
        )

@router.get(
    "/api/config/output-fields",
    response_model=List[Dict[str, Any]],
    summary="Get all output field definitions",
    tags=["Configuration"]
)
async def get_output_fields():
    """Get list of all output fields for persona generation"""
    try:
        templates = config_loader.load_prompt_templates()
        return templates['prompts']['output_fields']
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load output fields: {str(e)}"
        )