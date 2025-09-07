"""Configuration manager for reading and writing config files"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import shutil

class ConfigManager:
    """Manage configuration files with backup support"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            # Default to config directory at project root
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            config_dir = project_root / "config"
        
        self.config_dir = Path(config_dir)
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def _create_backup(self, config_file: str):
        """Create a backup of the config file before modifying"""
        source = self.config_dir / config_file
        if source.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source.stem}_{timestamp}{source.suffix}"
            backup_path = self.backup_dir / backup_name
            shutil.copy2(source, backup_path)
            
            # Keep only last 10 backups per file
            self._cleanup_old_backups(source.stem)
    
    def _cleanup_old_backups(self, file_stem: str, keep_count: int = 10):
        """Keep only the most recent backups"""
        backups = sorted(
            [f for f in self.backup_dir.glob(f"{file_stem}_*.json")],
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )
        
        for backup in backups[keep_count:]:
            backup.unlink()
    
    def get_settings(self):
        """Get settings from app_settings.json"""
        settings_file = self.config_dir.parent / "app_settings" / "settings.json"
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert to object-like access
                class Settings:
                    def __init__(self, data):
                        self.models = type('obj', (object,), {
                            'text_api_model': data.get('models', {}).get('text_api_model', 'gpt-4-turbo-preview')
                        })()
                        self.ai_model = data.get('ai_model', {})
                return Settings(data)
        return None
    
    def add_department(self, department: Dict[str, Any]) -> bool:
        """Add a new department to the configuration"""
        try:
            self._create_backup("departments.json")
            
            config_path = self.config_dir / "departments.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if ID already exists
            existing_ids = [d['id'] for d in data['departments']]
            if department['id'] in existing_ids:
                raise ValueError(f"Department ID '{department['id']}' already exists")
            
            # Auto-assign order if not provided
            if 'order' not in department:
                max_order = max([d.get('order', 0) for d in data['departments']], default=0)
                department['order'] = max_order + 1
            
            # Set enabled to True by default
            if 'enabled' not in department:
                department['enabled'] = True
            
            data['departments'].append(department)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding department: {e}")
            return False
    
    def update_department(self, department_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing department"""
        try:
            self._create_backup("departments.json")
            
            config_path = self.config_dir / "departments.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Find and update the department
            for i, dept in enumerate(data['departments']):
                if dept['id'] == department_id:
                    data['departments'][i].update(updates)
                    break
            else:
                raise ValueError(f"Department ID '{department_id}' not found")
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating department: {e}")
            return False
    
    def toggle_department(self, department_id: str, enabled: bool) -> bool:
        """Enable or disable a department"""
        return self.update_department(department_id, {'enabled': enabled})
    
    def add_patient_type(self, patient_type: Dict[str, Any]) -> bool:
        """Add a new patient type to the configuration"""
        try:
            self._create_backup("patient_types.json")
            
            config_path = self.config_dir / "patient_types.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if ID already exists
            existing_ids = [pt['id'] for pt in data['patient_types']]
            if patient_type['id'] in existing_ids:
                raise ValueError(f"Patient type ID '{patient_type['id']}' already exists")
            
            # Auto-assign order if not provided
            if 'order' not in patient_type:
                max_order = max([pt.get('order', 0) for pt in data['patient_types']], default=0)
                patient_type['order'] = max_order + 1
            
            # Set enabled to True by default
            if 'enabled' not in patient_type:
                patient_type['enabled'] = True
            
            data['patient_types'].append(patient_type)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding patient type: {e}")
            return False
    
    def update_prompt_template(self, section: str, template: str) -> bool:
        """Update a prompt template section"""
        try:
            self._create_backup("prompt_templates.json")
            
            config_path = self.config_dir / "prompt_templates.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Navigate to the correct section and update
            if section in data['prompts']['persona_generation']['sections']:
                data['prompts']['persona_generation']['sections'][section]['template'] = template
            else:
                raise ValueError(f"Section '{section}' not found in prompt templates")
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating prompt template: {e}")
            return False
    
    def update_output_field_limits(self, field_id: str, default_limit: int) -> bool:
        """Update default character limit for an output field"""
        try:
            self._create_backup("prompt_templates.json")
            
            config_path = self.config_dir / "prompt_templates.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Find and update the output field
            for field in data['prompts']['output_fields']:
                if field['id'] == field_id:
                    field['default_limit'] = default_limit
                    break
            else:
                raise ValueError(f"Output field '{field_id}' not found")
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating output field limits: {e}")
            return False

# Global instance
config_manager = ConfigManager()