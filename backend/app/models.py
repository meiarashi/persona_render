from pydantic import BaseModel, Field
from typing import Dict, Optional

class ModelSettings(BaseModel):
    text_api_model: Optional[str] = None
    image_api_model: Optional[str] = None

class CharLimits(BaseModel):
    personality: Optional[str] = "500"
    reason: Optional[str] = "300"
    behavior: Optional[str] = "400"
    reviews: Optional[str] = "200"
    values: Optional[str] = "300"
    demands: Optional[str] = "250"
    # Add other fields from admin.html if needed, e.g.:
    # "search_preference": Optional[str] = "some_default_value",
    # "booking_method": Optional[str] = "some_default_value"

class AdminSettings(BaseModel):
    models: Optional[ModelSettings] = Field(default_factory=ModelSettings)
    limits: Optional[Dict[str, str]] = Field(default_factory=dict)

# --- Request body models for specific updates ---

class ModelSettingsUpdate(BaseModel):
    text_api_model: str
    image_api_model: str

class CharLimitsUpdate(BaseModel):
    # Reflects the structure sent from admin_script.js: { limits: { personality: "500", ... } }
    limits: Dict[str, str] 