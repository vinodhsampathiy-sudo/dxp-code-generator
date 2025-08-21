from typing import Dict, List, Optional, Any
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class ModelType(Enum):
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE = "claude-3-opus-20240229"
    CLAUDE_INSTANT = "claude-3-sonnet-20240229"
    GEMINI_PRO = "gemini-pro"

class ComponentType(Enum):
    SLING_MODEL = "sling_model"
    HTL = "htl"
    DIALOG = "dialog"
    CLIENTLIB = "clientlib"

class PromptTemplate:
    def __init__(self):
        # Base templates for different component types
        self.base_templates = {
            ComponentType.SLING_MODEL: {
                "context": """You are generating a Sling Model for an AEM component.
Key requirements:
- Follow AEM best practices
- Include proper annotations
- Implement getter methods
- Add validation logic
- Handle null values safely
- Include Javadoc documentation""",
                "instruction": "Create a Sling Model class that implements the following requirements:\n{requirements}"
            },
            ComponentType.HTL: {
                "context": """You are generating HTL markup for an AEM component.
Key requirements:
- Use data-sly-* blocks properly
- Include proper null checks
- Follow BEM naming conventions
- Ensure accessibility
- Add proper data attributes""",
                "instruction": "Create HTL markup that implements the following features:\n{requirements}"
            },
            ComponentType.DIALOG: {
                "context": """You are generating a dialog definition for an AEM component.
Key requirements:
- Use correct node structure
- Include field validation
- Group fields logically
- Add help text
- Support multiple tabs if needed""",
                "instruction": "Create a dialog.xml that includes the following fields:\n{requirements}"
            },
            ComponentType.CLIENTLIB: {
                "context": """You are generating client libraries for an AEM component.
Key requirements:
- Implement responsive design
- Follow BEM methodology
- Include JS initialization
- Add event handlers
- Optimize performance""",
                "instruction": "Create client libraries (JS/CSS) with the following features:\n{requirements}"
            }
        }

        # Model-specific optimizations
        self.model_optimizations = {
            ModelType.GPT4: {
                "temperature": 0.2,
                "format": "detailed",
                "examples": True,
                "reasoning": True
            },
            ModelType.GPT4_TURBO: {
                "temperature": 0.3,
                "format": "concise",
                "examples": False,
                "reasoning": False
            },
            ModelType.GPT35_TURBO: {
                "temperature": 0.4,
                "format": "minimal",
                "examples": False,
                "reasoning": False
            },
            ModelType.CLAUDE: {
                "temperature": 0.2,
                "format": "detailed",
                "examples": True,
                "reasoning": True
            },
            ModelType.CLAUDE_INSTANT: {
                "temperature": 0.3,
                "format": "concise",
                "examples": False,
                "reasoning": False
            },
            ModelType.GEMINI_PRO: {
                "temperature": 0.3,
                "format": "structured",
                "examples": True,
                "reasoning": False
            }
        }

    def _get_model_prefix(self, model_type: ModelType) -> str:
        """Get model-specific prefix to optimize response quality"""
        prefixes = {
            ModelType.GPT4: """You are an expert AEM developer. Provide complete, production-ready code with thorough documentation.
Consider edge cases and include error handling.""",
            
            ModelType.GPT4_TURBO: """You are an AEM developer. Generate efficient, clean code following best practices.
Focus on the core requirements.""",
            
            ModelType.GPT35_TURBO: """Generate concise AEM component code based on the requirements.
Keep the implementation simple and direct.""",
            
            ModelType.CLAUDE: """As an AEM architect, create robust component code with comprehensive documentation.
Consider scalability, maintainability, and performance.""",
            
            ModelType.CLAUDE_INSTANT: """Create clean AEM component code following established patterns.
Focus on essential functionality.""",
            
            ModelType.GEMINI_PRO: """Generate structured AEM component code with clear organization.
Include basic documentation and error handling."""
        }
        return prefixes.get(model_type, prefixes[ModelType.GPT4])

    def _get_format_instruction(self, model_type: ModelType, component_type: ComponentType) -> str:
        """Get model-specific format instructions"""
        if component_type == ComponentType.SLING_MODEL:
            if model_type in [ModelType.GPT4, ModelType.CLAUDE]:
                return "\nProvide a complete Java class with imports, annotations, and comprehensive Javadoc."
            else:
                return "\nProvide a Java class implementation focusing on core functionality."
        
        elif component_type == ComponentType.HTL:
            if model_type in [ModelType.GPT4, ModelType.CLAUDE]:
                return "\nInclude detailed comments and data-sly-* usage explanations."
            else:
                return "\nProvide clean HTL markup with essential data-sly-* blocks."
        
        return ""

    def _add_examples(self, model_type: ModelType, component_type: ComponentType) -> str:
        """Add examples if supported by the model"""
        if not self.model_optimizations[model_type]["examples"]:
            return ""

        examples = {
            ComponentType.SLING_MODEL: """
Example structure:
```java
@Model(adaptables = Resource.class, defaultInjectionStrategy = DefaultInjectionStrategy.OPTIONAL)
public class ExampleModel {
    @ValueMapValue
    private String title;
    
    public String getTitle() {
        return title != null ? title : "";
    }
}
```""",
            ComponentType.HTL: """
Example structure:
```html
<div class="cmp-example" data-sly-use.model="com.example.ExampleModel">
    <h1 class="cmp-example__title" data-sly-test="${model.title}">${model.title}</h1>
</div>
```""",
        }
        return examples.get(component_type, "")

    def generate_prompt(
        self,
        model_type: ModelType,
        component_type: ComponentType,
        requirements: Dict[str, Any],
        complexity: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate optimized prompt for specific model and component type"""
        
        # Get base template
        base = self.base_templates[component_type]
        
        # Build requirements string
        req_str = json.dumps(requirements, indent=2) if isinstance(requirements, dict) else str(requirements)
        
        # Combine prompt elements
        prompt = f"{self._get_model_prefix(model_type)}\n\n"
        prompt += f"{base['context']}\n\n"
        prompt += f"{base['instruction'].format(requirements=req_str)}"
        prompt += self._get_format_instruction(model_type, component_type)
        
        if complexity and complexity > 0.7:  # Add extra guidance for complex components
            prompt += "\n\nThis is a complex component. Consider:"
            prompt += "\n- Performance optimization"
            prompt += "\n- Error handling"
            prompt += "\n- Extensive documentation"
        
        if self.model_optimizations[model_type]["examples"]:
            prompt += self._add_examples(model_type, component_type)
        
        return {
            "prompt": prompt,
            "temperature": self.model_optimizations[model_type]["temperature"],
            "format": self.model_optimizations[model_type]["format"],
            "model": model_type.value
        }

    def get_response_format(self, model_type: ModelType) -> str:
        """Get expected response format instruction for each model"""
        formats = {
            ModelType.GPT4: "Provide the complete code without any additional explanation.",
            ModelType.GPT4_TURBO: "Return only the code implementation.",
            ModelType.GPT35_TURBO: "Return code only, no explanations.",
            ModelType.CLAUDE: "Provide code with minimal necessary comments.",
            ModelType.CLAUDE_INSTANT: "Return clean code implementation only.",
            ModelType.GEMINI_PRO: "Return code with brief comments."
        }
        return formats.get(model_type, formats[ModelType.GPT4])

    def get_system_prompt(self, model_type: ModelType) -> str:
        """Get model-specific system prompt"""
        prompts = {
            ModelType.GPT4: "You are an expert AEM developer focusing on clean, efficient, and well-documented code.",
            ModelType.GPT4_TURBO: "You are an AEM developer creating efficient component implementations.",
            ModelType.GPT35_TURBO: "Create simple, functional AEM components.",
            ModelType.CLAUDE: "As an AEM architect, focus on robust and maintainable component code.",
            ModelType.CLAUDE_INSTANT: "Generate clean AEM component code following best practices.",
            ModelType.GEMINI_PRO: "Create structured AEM components with clear organization."
        }
        return prompts.get(model_type, prompts[ModelType.GPT4])
