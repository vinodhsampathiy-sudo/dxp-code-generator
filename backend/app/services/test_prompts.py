from typing import Dict, Any
import logging
from .prompt_template import PromptTemplate, ModelType, ComponentType

logger = logging.getLogger(__name__)

async def test_prompt_generation(component_desc: str) -> Dict[str, Any]:
    """Test endpoint for prompt-based component generation"""
    try:
        # Initialize prompt system
        prompt_engine = PromptTemplate()
        
        # Sample requirements
        requirements = {
            "title": "Test Component",
            "description": component_desc,
            "fields": [
                {"name": "title", "type": "text", "required": True},
                {"name": "description", "type": "richtext"},
                {"name": "image", "type": "image"}
            ]
        }
        
        # Test each model type with Sling Model generation
        results = {}
        for model_type in ModelType:
            prompt_data = prompt_engine.generate_prompt(
                model_type=model_type,
                component_type=ComponentType.SLING_MODEL,
                requirements=requirements
            )
            
            # Log the generated prompt
            logger.info(f"\n=== Generated Prompt for {model_type.value} ===\n{prompt_data['prompt']}")
            
            # Store result
            results[model_type.value] = {
                "prompt": prompt_data["prompt"],
                "temperature": prompt_data["temperature"],
                "format": prompt_data["format"]
            }
        
        return {
            "success": True,
            "message": "Prompts generated successfully",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in prompt generation test: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }
