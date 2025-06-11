"""Prompt builder utility using configuration files"""
from typing import Dict, List, Optional, Any
from .config_loader import config_loader

class PromptBuilder:
    """Build prompts for persona generation using configuration"""
    
    def __init__(self):
        self.config_loader = config_loader
        
    def build_persona_prompt(self, 
                           data: Dict[str, Any],
                           char_limits: Dict[str, str],
                           rag_context: Optional[str] = None) -> str:
        """Build persona generation prompt from data and configuration"""
        
        # Load configurations
        patient_type_details = self.config_loader.get_patient_type_details_map()
        templates = self.config_loader.load_prompt_templates()
        prompt_config = templates['prompts']['persona_generation']
        output_fields = templates['prompts']['output_fields']
        
        # Start building prompt
        prompt_parts = [prompt_config['base_template'], ""]
        
        # Section 1: Basic Information
        section_config = prompt_config['sections']['basic_info']
        prompt_parts.append(f"# {section_config['label']}")
        
        # Add basic info fields
        basic_info = self._build_basic_info_section(data, patient_type_details)
        prompt_parts.extend(basic_info)
        
        # Section 2: Fixed Additional Information
        if self._has_fixed_additional_info(data):
            section_config = prompt_config['sections']['additional_info_fixed']
            prompt_parts.append(f"\n## {section_config['label']}")
            fixed_info = self._build_fixed_additional_info_section(data)
            prompt_parts.extend(fixed_info)
        
        # Section 3: Dynamic Additional Information
        dynamic_info = self._build_dynamic_additional_info_section(data)
        if dynamic_info:
            section_config = prompt_config['sections']['additional_info_dynamic']
            prompt_parts.append(f"\n## {section_config['label']}")
            prompt_parts.extend(dynamic_info)
        
        # Section 4: RAG Context (if provided)
        if rag_context:
            section_config = prompt_config['sections']['rag_context']
            prompt_parts.append(f"\n\n# {section_config['label']}")
            prompt_parts.append(section_config['template'])
            prompt_parts.append(rag_context)
        
        # Section 5: Generation Items
        section_config = prompt_config['sections']['generation_items']
        prompt_parts.append(f"\n# {section_config['label']}")
        prompt_parts.append(section_config['template'])
        
        # Add output fields with character limits
        for i, field in enumerate(output_fields, 1):
            field_id = field['id']
            field_label = field['label']
            limit = char_limits.get(field_id, str(field['default_limit']))
            prompt_parts.append(f"\n{i}. **{field_label}**: {limit}文字程度で記述")
        
        return "\n".join(prompt_parts)
    
    def _build_basic_info_section(self, data: Dict[str, Any], 
                                 patient_type_details: Dict[str, Dict[str, str]]) -> List[str]:
        """Build basic information section"""
        info_parts = []
        
        # Basic fields mapping
        fields = [
            ("診療科", "department"),
            ("ペルソナ作成目的", "purpose"),
            ("名前", "name"),
            ("性別", "gender"),
            ("年齢", "age"),
            ("都道府県", "prefecture"),
            ("市区町村", "municipality"),
            ("家族構成", "family"),
            ("職業", "occupation"),
            ("年収", "income"),
            ("趣味", "hobby"),
            ("ライフイベント", "life_events"),
            ("患者タイプ", "patient_type")
        ]
        
        # Add setting type if present
        if data.get('setting_type'):
            info_parts.append(f"- 基本情報設定タイプ: {data['setting_type']}")
        
        # Add each field
        for label, key in fields:
            value = data.get(key)
            if value:
                info_parts.append(f"- {label}: {value}")
                
                # Add patient type details if applicable
                if key == "patient_type" and value in patient_type_details:
                    details = patient_type_details[value]
                    info_parts.append(f"  - 患者タイプの特徴: {details['description']}")
                    info_parts.append(f"  - 患者タイプの例: {details['example']}")
            elif key in ["name", "gender", "age", "prefecture", "municipality", 
                        "family", "occupation", "income", "hobby", "life_events"] and key != "patient_type":
                info_parts.append(f"- {label}: (自動生成)")
            elif key == "patient_type" and not value and data.get('setting_type') == 'patient_type':
                info_parts.append(f"- {label}: (指定なし/自動生成)")
        
        return info_parts
    
    def _has_fixed_additional_info(self, data: Dict[str, Any]) -> bool:
        """Check if there are fixed additional info fields"""
        fixed_fields = ['motto', 'concerns', 'favorite_person', 'media_sns',
                       'personality_keywords', 'health_actions', 'holiday_activities', 'catchphrase']
        return any(data.get(field) for field in fixed_fields)
    
    def _build_fixed_additional_info_section(self, data: Dict[str, Any]) -> List[str]:
        """Build fixed additional information section"""
        info_parts = []
        
        fixed_fields = [
            ("座右の銘", "motto"),
            ("最近の悩み/関心", "concerns"),
            ("好きな有名人/尊敬する人物", "favorite_person"),
            ("よく見るメディア/SNS", "media_sns"),
            ("性格キーワード", "personality_keywords"),
            ("最近した健康に関する行動", "health_actions"),
            ("休日の過ごし方", "holiday_activities"),
            ("キャッチコピー", "catchphrase")
        ]
        
        for label, key in fixed_fields:
            value = data.get(key)
            if value:
                info_parts.append(f"- {label}: {value}")
        
        return info_parts
    
    def _build_dynamic_additional_info_section(self, data: Dict[str, Any]) -> List[str]:
        """Build dynamic additional information section"""
        info_parts = []
        
        field_names = data.get('additional_field_name', [])
        field_values = data.get('additional_field_value', [])
        
        if isinstance(field_names, list) and isinstance(field_values, list):
            for i in range(len(field_names)):
                field_name = field_names[i]
                field_value = field_values[i] if i < len(field_values) else None
                if field_name and field_value:
                    info_parts.append(f"- {field_name}: {field_value}")
        
        return info_parts

# Global instance
prompt_builder = PromptBuilder()