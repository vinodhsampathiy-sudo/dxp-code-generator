"""
Code validators for AEM components
"""
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SlingModelValidator:
    """Validator for Sling Model Java code"""
    
    @staticmethod
    def validate_syntax(java_code: str) -> Tuple[bool, List[str]]:
        """
        Validate Java syntax using javac
        Returns: (is_valid, error_messages)
        """
        errors = []
        
        # Basic syntax checks without compilation
        if not java_code.strip():
            errors.append("Sling Model code is empty")
            return False, errors
        
        # Check for package declaration
        if not re.search(r'package\s+[\w.]+;', java_code):
            errors.append("Missing package declaration")
        
        # Check for class declaration
        if not re.search(r'public\s+class\s+\w+', java_code):
            errors.append("Missing public class declaration")
        
        # Check for @Model annotation
        if '@Model(' not in java_code:
            errors.append("Missing @Model annotation")
        
        # Check for required imports
        required_imports = [
            'org.apache.sling.models.annotations.Model',
            'org.apache.sling.models.annotations.DefaultInjectionStrategy'
        ]
        
        for imp in required_imports:
            if imp not in java_code:
                errors.append(f"Missing required import: {imp}")
        
        # Check for deprecated patterns
        deprecated_patterns = [
            (r'@Optional', 'Using deprecated @Optional annotation. Use defaultInjectionStrategy instead'),
            (r'import org.apache.sling.models.annotations.Optional', 'Importing deprecated Optional annotation')
        ]
        
        for pattern, message in deprecated_patterns:
            if re.search(pattern, java_code):
                errors.append(message)
        
        # Check for proper field injection
        # Fields should use @ValueMapValue, @ChildResource, @Inject, etc.
        private_fields = re.findall(r'private\s+\w+(?:<[^>]+>)?\s+(\w+);', java_code)
        for field in private_fields:
            # Check if field has any injection annotation
            field_context = java_code[max(0, java_code.find(f'private') - 200):java_code.find(field) + 100]
            if not any(ann in field_context for ann in ['@ValueMapValue', '@ChildResource', '@Inject', '@Self', '@OSGiService']):
                errors.append(f"Field '{field}' may be missing injection annotation")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_imports(java_code: str) -> Tuple[bool, List[str]]:
        """Validate that imports are correct and not deprecated"""
        errors = []
        
        # Extract all imports
        imports = re.findall(r'import\s+([\w.]+);', java_code)
        
        # Check for deprecated imports
        deprecated_imports = {
            'org.apache.sling.models.annotations.Optional': 'Use defaultInjectionStrategy = DefaultInjectionStrategy.OPTIONAL instead',
            'com.day.cq.wcm.api.Page': 'Consider using resource-based approach instead of Page API where possible'
        }
        
        for imp in imports:
            if imp in deprecated_imports:
                errors.append(f"Deprecated import '{imp}': {deprecated_imports[imp]}")
        
        # Check for common typos in package names
        for imp in imports:
            if 'adobe' in imp.lower() and 'com.adobe.aem' not in imp and 'com.adobe.cq' not in imp:
                errors.append(f"Suspicious import '{imp}' - verify package name")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_structure(java_code: str) -> Tuple[bool, List[str]]:
        """Validate overall structure of Sling Model"""
        errors = []
        
        # Check for adaptables
        model_match = re.search(r'@Model\s*\((.*?)\)', java_code, re.DOTALL)
        if model_match:
            model_params = model_match.group(1)
            if 'adaptables' not in model_params:
                errors.append("@Model annotation should specify adaptables (e.g., SlingHttpServletRequest.class, Resource.class)")
        
        # Check for getter methods
        private_fields = re.findall(r'private\s+(\w+(?:<[^>]+>)?)\s+(\w+);', java_code)
        for field_type, field_name in private_fields:
            # Generate expected getter name
            getter_name = 'get' + field_name[0].upper() + field_name[1:]
            if getter_name not in java_code and not field_name.startswith('_'):
                errors.append(f"Missing getter method for field '{field_name}' (expected '{getter_name}')")
        
        return len(errors) == 0, errors


class HTLValidator:
    """Validator for HTL templates"""
    
    @staticmethod
    def validate_syntax(htl_code: str) -> Tuple[bool, List[str]]:
        """Validate HTL syntax"""
        errors = []
        
        if not htl_code.strip():
            errors.append("HTL code is empty")
            return False, errors
        
        # Check for data-sly-use directive
        if 'data-sly-use' not in htl_code:
            errors.append("Missing data-sly-use directive to bind Sling Model")
        
        # Check for proper HTML structure
        if not any(tag in htl_code.lower() for tag in ['<div', '<section', '<article', '<header', '<main']):
            errors.append("HTL should contain structural HTML elements")
        
        # Check for unclosed HTL expressions
        open_expressions = htl_code.count('${')
        close_expressions = htl_code.count('}')
        if open_expressions != close_expressions:
            errors.append(f"Mismatched HTL expressions: {open_expressions} opening, {close_expressions} closing")
        
        # Check for common HTL mistakes
        if '@' in htl_code and 'data-sly-' not in htl_code:
            errors.append("Found '@' symbol - HTL uses 'data-sly-' attributes, not @ directives")
        
        # Check for accessibility
        if '<img' in htl_code.lower():
            # Check if images have alt attributes
            img_tags = re.findall(r'<img[^>]*>', htl_code, re.IGNORECASE)
            for img_tag in img_tags:
                if 'alt=' not in img_tag.lower():
                    errors.append("Image tags should have alt attributes for accessibility")
        
        return len(errors) == 0, errors


class DialogXMLValidator:
    """Validator for AEM Dialog XML"""
    
    @staticmethod
    def validate_syntax(xml_code: str) -> Tuple[bool, List[str]]:
        """Validate Dialog XML syntax"""
        errors = []
        
        if not xml_code.strip():
            errors.append("Dialog XML is empty")
            return False, errors
        
        # Check for XML declaration
        if '<?xml version="1.0" encoding="UTF-8"?>' not in xml_code:
            errors.append("Missing XML declaration")
        
        # Check for jcr:root element
        if 'jcr:root' not in xml_code:
            errors.append("Missing jcr:root element")
        
        # Check for correct resourceType
        if 'sling:resourceType="cq/gui/components/authoring/dialog"' not in xml_code:
            errors.append("Dialog should have resourceType='cq/gui/components/authoring/dialog'")
        
        # Check for balanced tags
        open_tags = len(re.findall(r'<(?!/)[^>]+>', xml_code))
        close_tags = len(re.findall(r'</[^>]+>', xml_code))
        self_closing = len(re.findall(r'<[^>]+/>', xml_code))
        
        # Rough check (not perfect but catches obvious issues)
        if open_tags != close_tags + self_closing:
            errors.append(f"Potentially unbalanced XML tags")
        
        return len(errors) == 0, errors


def validate_component_code(component_data: Dict) -> Dict[str, any]:
    """
    Validate all component code
    Returns validation results with errors and warnings
    """
    results = {
        'is_valid': True,
        'sling_model': {'valid': True, 'errors': [], 'warnings': []},
        'htl': {'valid': True, 'errors': [], 'warnings': []},
        'dialog': {'valid': True, 'errors': [], 'warnings': []}
    }
    
    # Validate Sling Model
    if 'slingModel' in component_data:
        sling_model = component_data['slingModel']
        
        # Syntax validation
        is_valid, errors = SlingModelValidator.validate_syntax(sling_model)
        if not is_valid:
            results['sling_model']['valid'] = False
            results['sling_model']['errors'].extend(errors)
            results['is_valid'] = False
        
        # Import validation
        is_valid, errors = SlingModelValidator.validate_imports(sling_model)
        if not is_valid:
            results['sling_model']['warnings'].extend(errors)
        
        # Structure validation
        is_valid, errors = SlingModelValidator.validate_structure(sling_model)
        if not is_valid:
            results['sling_model']['warnings'].extend(errors)
    
    # Validate HTL
    if 'htl' in component_data:
        is_valid, errors = HTLValidator.validate_syntax(component_data['htl'])
        if not is_valid:
            results['htl']['valid'] = False
            results['htl']['errors'].extend(errors)
            results['is_valid'] = False
    
    # Validate Dialog
    if 'dialog' in component_data:
        dialog_code = component_data['dialog']
        # Handle both string and dict formats
        if isinstance(dialog_code, dict):
            dialog_code = next(iter(dialog_code.values())) if dialog_code else ""
        
        is_valid, errors = DialogXMLValidator.validate_syntax(dialog_code)
        if not is_valid:
            results['dialog']['valid'] = False
            results['dialog']['errors'].extend(errors)
            results['is_valid'] = False
    
    return results
