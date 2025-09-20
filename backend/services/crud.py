import json
import os
from pathlib import Path
from typing import Dict, Union

from backend.models.schemas import AdminSettings, ModelSettings

# 永続ディスクのマウントパス (Renderで設定したものに合わせる)
# /var/app_settings で設定済みとのこと
PERSISTENT_DISK_MOUNT_PATH = Path(os.getenv("PERSISTENT_DISK_PATH", "/var/app_settings"))
SETTINGS_FILE_NAME = "admin_settings.json"
SETTINGS_FILE_PATH = PERSISTENT_DISK_MOUNT_PATH / SETTINGS_FILE_NAME

DEFAULT_SETTINGS = AdminSettings(
    models=ModelSettings(text_api_model="gpt-4.1-2025-04-14", image_api_model="dall-e-3"),
    limits={
        "personality": "500",
        "reason": "300",
        "behavior": "400",
        "reviews": "200",
        "values": "300",
        "demands": "250"
    }
)

def ensure_settings_dir_exists():
    """Ensures the directory for the settings file exists."""
    if not PERSISTENT_DISK_MOUNT_PATH.exists():
        try:
            PERSISTENT_DISK_MOUNT_PATH.mkdir(parents=True, exist_ok=True)
            print(f"Created settings directory: {PERSISTENT_DISK_MOUNT_PATH}")
        except Exception as e:
            print(f"Error creating settings directory {PERSISTENT_DISK_MOUNT_PATH}: {e}")
            raise

def read_settings() -> AdminSettings:
    """Reads admin settings from the JSON file. Returns default settings if file not found or invalid."""
    ensure_settings_dir_exists()

    if not SETTINGS_FILE_PATH.exists():
        print(f"Settings file not found at {SETTINGS_FILE_PATH}. Using default settings and creating file.")
        write_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    try:
        with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return AdminSettings(**data)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {SETTINGS_FILE_PATH}. Overwriting with default settings.")
        write_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    except Exception as e:
        print(f"An unexpected error occurred while reading settings: {e}. Overwriting with default settings.")
        write_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS

def write_settings(settings_data: Union[AdminSettings, Dict]) -> bool:
    """Writes admin settings to the JSON file."""
    ensure_settings_dir_exists()
    try:
        if isinstance(settings_data, AdminSettings):
            data_to_write = settings_data.model_dump(mode="json")
        elif isinstance(settings_data, dict):
            data_to_write = settings_data
        else:
            print("Invalid data type for settings. Must be AdminSettings instance or dict.")
            return False

        with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data_to_write, f, indent=4, ensure_ascii=False)
        print(f"Admin settings successfully written to {SETTINGS_FILE_PATH}")
        return True
    except Exception as e:
        print(f"Error writing admin settings to {SETTINGS_FILE_PATH}: {e}")
        return False

# --- Specific update functions --- #

def update_model_settings(new_models_data: ModelSettings) -> bool:
    current_settings = read_settings()
    current_settings.models = new_models_data
    return write_settings(current_settings)

def update_char_limits(new_limits_data: Dict[str, str]) -> bool:
    current_settings = read_settings()
    current_settings.limits = new_limits_data
    return write_settings(current_settings)


if __name__ == "__main__":
    print("Testing CRUD operations...")
    
    ensure_settings_dir_exists()
    print(f"Settings file will be at: {SETTINGS_FILE_PATH}")

    initial_settings = read_settings()
    print("\nInitial or Read Settings:")
    print(initial_settings.model_dump_json(indent=4))

    print("\nUpdating model settings...")
    updated_models = ModelSettings(text_api_model="claude-3-opus", image_api_model="none")
    if update_model_settings(updated_models):
        print("Model settings updated.")
    
    reread_settings = read_settings()
    print("\nSettings after model update:")
    print(reread_settings.model_dump_json(indent=4))
    if reread_settings.models:
        assert reread_settings.models.text_api_model == "claude-3-opus"

    print("\nUpdating char limits...")
    updated_limits = {"personality": "1000", "reason": "100", "new_custom_limit": "50"}
    if update_char_limits(updated_limits):
        print("Char limits updated.")
    
    reread_settings = read_settings()
    print("\nSettings after limits update:")
    print(reread_settings.model_dump_json(indent=4))
    if reread_settings.limits:
        assert reread_settings.limits.get("personality") == "1000"
        assert reread_settings.limits.get("new_custom_limit") == "50"
    
    print("\nCRUD tests completed.")