from typing import Dict, Any, Optional
import json
import re
from enum import Enum

class ModelType(Enum):
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE = "claude-3-opus-20240229"
    CLAUDE_INSTANT = "claude-3-sonnet-20240229"
    GEMINI_PRO = "gemini-pro"

class ResponseHandler:
    @staticmethod
    def extract_code_block(response: str) -> str:
        """Extract code from response"""
        # Look for code blocks with language specifier
        code_block_match = re.search(r'```(?:java|html|xml|javascript|css)\n(.*?)```', response, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()
        
        # Look for any code blocks
        code_block_match = re.search(r'```(.*?)```', response, re.DOTALL)
        if code_block_match:
            return code_block_match.group(1).strip()
        
        return response.strip()

    @staticmethod
    def clean_gpt_response(response: str) -> str:
        """Clean GPT model response"""
        # Remove any conversation markers
        response = re.sub(r'^(Assistant:|GPT:|A:)', '', response, flags=re.MULTILINE)
        
        # Extract code
        code = ResponseHandler.extract_code_block(response)
        
        # Clean up any remaining markdown
        code = code.replace('```', '').strip()
        
        return code

    @staticmethod
    def clean_claude_response(response: str) -> str:
        """Clean Claude model response"""
        # Remove Claude's natural language
        response = re.sub(r'Here\'s the (implementation|code|solution):', '', response)
        
        # Extract code
        code = ResponseHandler.extract_code_block(response)
        
        # Remove Claude's explanatory comments
        code = re.sub(r'^#\s*Note:.*$', '', code, flags=re.MULTILINE)
        
        return code.strip()

    @staticmethod
    def clean_gemini_response(response: str) -> str:
        """Clean Gemini model response"""
        # Remove Gemini's natural language
        response = re.sub(r'Here\'s the (generated|requested) code:', '', response)
        
        # Extract code
        code = ResponseHandler.extract_code_block(response)
        
        return code.strip()

    @staticmethod
    def parse_json_response(response: str) -> Dict[str, Any]:
        """Parse JSON from response"""
        # Find JSON block
        json_match = re.search(r'{.*}', response, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")
        
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {str(e)}")

    @classmethod
    def process_response(cls, response: str, model_type: ModelType) -> str:
        """Process response based on model type"""
        if model_type in [ModelType.GPT4, ModelType.GPT4_TURBO, ModelType.GPT35_TURBO]:
            return cls.clean_gpt_response(response)
        elif model_type in [ModelType.CLAUDE, ModelType.CLAUDE_INSTANT]:
            return cls.clean_claude_response(response)
        elif model_type == ModelType.GEMINI_PRO:
            return cls.clean_gemini_response(response)
        else:
            return cls.extract_code_block(response)

    @classmethod
    def validate_response(cls, 
                         response: str, 
                         model_type: ModelType, 
                         expected_type: str) -> Optional[str]:
        """Validate response content"""
        code = cls.process_response(response, model_type)
        
        # Validate Java code
        if expected_type == 'java':
            if not re.search(r'class\s+\w+', code):
                return "Missing class definition"
            if not re.search(r'@Model', code):
                return "Missing @Model annotation"
                
        # Validate HTL code
        elif expected_type == 'html':
            if not re.search(r'data-sly-use', code):
                return "Missing data-sly-use attribute"
                
        # Validate Dialog XML
        elif expected_type == 'xml':
            if not re.search(r'jcr:root', code):
                return "Missing jcr:root element"
                
        # Validate JavaScript code
        elif expected_type == 'javascript':
            if not re.search(r'function|class|const|let|var', code):
                return "Missing code structure"
                
        # Validate CSS code
        elif expected_type == 'css':
            if not re.search(r'\{.*?\}', code, re.DOTALL):
                return "Missing CSS rules"
                
        return None  # No validation errors

    @classmethod
    def enhance_response(cls, code: str, model_type: ModelType) -> str:
        """Add enhancements based on model type"""
        if model_type in [ModelType.GPT4, ModelType.CLAUDE]:
            # Add extensive documentation
            return cls._add_documentation(code)
        elif model_type in [ModelType.GPT4_TURBO, ModelType.GEMINI_PRO]:
            # Add basic documentation
            return cls._add_basic_documentation(code)
        return code

    @staticmethod
    def _add_documentation(code: str) -> str:
        """Add extensive documentation to code"""
        # Implementation for adding detailed documentation
        pass

    @staticmethod
    def _add_basic_documentation(code: str) -> str:
        """Add basic documentation to code"""
        # Implementation for adding basic documentation
        pass
