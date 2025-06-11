"""Configuration loader utility for managing JSON config files"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import lru_cache

class ConfigLoader:
    """Load and manage configuration from JSON files"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            # Default to config directory at project root
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            config_dir = project_root / "config"
        
        self.config_dir = Path(config_dir)
        
    @lru_cache(maxsize=None)
    def load_departments(self) -> List[Dict[str, Any]]:
        """Load departments configuration"""
        config_path = self.config_dir / "departments.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter only enabled departments and sort by order
        departments = [d for d in data['departments'] if d.get('enabled', True)]
        return sorted(departments, key=lambda x: x.get('order', 999))
    
    @lru_cache(maxsize=None)
    def load_purposes(self) -> List[Dict[str, Any]]:
        """Load purposes configuration"""
        config_path = self.config_dir / "purposes.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter only enabled purposes and sort by order
        purposes = [p for p in data['purposes'] if p.get('enabled', True)]
        return sorted(purposes, key=lambda x: x.get('order', 999))
    
    @lru_cache(maxsize=None)
    def load_patient_types(self) -> List[Dict[str, Any]]:
        """Load patient types configuration"""
        config_path = self.config_dir / "patient_types.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter only enabled patient types and sort by order
        patient_types = [pt for pt in data['patient_types'] if pt.get('enabled', True)]
        return sorted(patient_types, key=lambda x: x.get('order', 999))
    
    @lru_cache(maxsize=None)
    def load_prompt_templates(self) -> Dict[str, Any]:
        """Load prompt templates configuration"""
        config_path = self.config_dir / "prompt_templates.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @lru_cache(maxsize=None)
    def load_ai_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load AI models configuration"""
        config_path = self.config_dir / "ai_models.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Filter only enabled models and sort by order
        text_models = [m for m in data['text_models'] if m.get('enabled', True)]
        text_models = sorted(text_models, key=lambda x: x.get('order', 999))
        
        image_models = [m for m in data['image_models'] if m.get('enabled', True)]
        image_models = sorted(image_models, key=lambda x: x.get('order', 999))
        
        return {
            'text_models': text_models,
            'image_models': image_models
        }
    
    def get_department_map(self) -> Dict[str, str]:
        """Get department ID to Japanese name mapping"""
        departments = self.load_departments()
        return {d['id']: d['name_ja'] for d in departments}
    
    def get_purpose_map(self) -> Dict[str, str]:
        """Get purpose ID to Japanese name mapping"""
        purposes = self.load_purposes()
        return {p['id']: p['name_ja'] for p in purposes}
    
    def get_patient_type_details_map(self) -> Dict[str, Dict[str, str]]:
        """Get patient type value to details mapping"""
        patient_types = self.load_patient_types()
        return {
            pt['value']: {
                'description': pt['description'],
                'example': pt['example']
            }
            for pt in patient_types
        }
    
    def clear_cache(self):
        """Clear the configuration cache"""
        self.load_departments.cache_clear()
        self.load_purposes.cache_clear()
        self.load_patient_types.cache_clear()
        self.load_prompt_templates.cache_clear()
        self.load_ai_models.cache_clear()

# Global instance
config_loader = ConfigLoader()