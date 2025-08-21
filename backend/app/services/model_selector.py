from typing import Dict, Optional
import os
from enum import Enum

class ModelType(Enum):
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo-preview"
    GPT35_TURBO = "gpt-3.5-turbo"
    CLAUDE = "claude-3-opus-20240229"
    CLAUDE_INSTANT = "claude-3-sonnet-20240229"
    GEMINI_PRO = "gemini-pro"

class ModelSelector:
    def __init__(self):
        self.model_capabilities = {
            ModelType.GPT4: {
                "max_complexity": float('inf'),
                "specialties": ["complex_logic", "architecture", "optimization"],
                "cost_per_token": 0.03,
                "speed": 1.0  # Base speed reference
            },
            ModelType.GPT4_TURBO: {
                "max_complexity": 15,
                "specialties": ["code_generation", "dialog_creation"],
                "cost_per_token": 0.01,
                "speed": 1.5
            },
            ModelType.GPT35_TURBO: {
                "max_complexity": 8,
                "specialties": ["simple_components", "styling"],
                "cost_per_token": 0.002,
                "speed": 2.0
            },
            ModelType.CLAUDE: {
                "max_complexity": float('inf'),
                "specialties": ["complex_logic", "documentation"],
                "cost_per_token": 0.015,
                "speed": 1.2
            },
            ModelType.CLAUDE_INSTANT: {
                "max_complexity": 12,
                "specialties": ["rapid_prototyping", "simple_logic"],
                "cost_per_token": 0.008,
                "speed": 1.8
            },
            ModelType.GEMINI_PRO: {
                "max_complexity": 10,
                "specialties": ["code_generation", "simple_components"],
                "cost_per_token": 0.005,
                "speed": 1.7
            }
        }
        
        # Load environment config
        self.preferred_model = os.getenv('PREFERRED_AI_MODEL', 'gpt-4')
        self.cost_sensitive = os.getenv('COST_SENSITIVE', 'false').lower() == 'true'
        self.speed_priority = os.getenv('SPEED_PRIORITY', 'false').lower() == 'true'

    def select_model(self, 
                    complexity_score: float, 
                    task_type: str,
                    features: Dict,
                    optimize_for: Optional[str] = None) -> ModelType:
        """
        Selects the most appropriate model based on task requirements
        
        Args:
            complexity_score: Numerical score of task complexity
            task_type: Type of task (e.g., "sling_model", "dialog", "clientlib")
            features: Dict of component features
            optimize_for: Optional priority ("speed", "cost", or "quality")
        """
        
        if optimize_for is None:
            if self.speed_priority:
                optimize_for = "speed"
            elif self.cost_sensitive:
                optimize_for = "cost"
            else:
                optimize_for = "quality"

        # Filter models that can handle the complexity
        suitable_models = [
            model for model in ModelType
            if self.model_capabilities[model]["max_complexity"] >= complexity_score
        ]

        if not suitable_models:
            return ModelType.GPT4  # Default to most capable model

        # Score each model based on optimization priority
        model_scores = {}
        for model in suitable_models:
            score = 0
            capabilities = self.model_capabilities[model]

            if optimize_for == "speed":
                score += capabilities["speed"] * 3
                score -= complexity_score * 0.2  # Penalty for complex tasks
            elif optimize_for == "cost":
                score += (1 / capabilities["cost_per_token"]) * 2
                score += capabilities["speed"]
            else:  # quality
                score += (10 - capabilities["max_complexity"]) * 0.5
                if task_type in capabilities["specialties"]:
                    score += 2

            # Adjust for feature compatibility
            if features.get('interactive', False) and "code_generation" in capabilities["specialties"]:
                score += 1
            if features.get('fields', []) and len(features['fields']) > 5 and model in [ModelType.GPT4, ModelType.CLAUDE]:
                score += 2

            model_scores[model] = score

        # Select model with highest score
        selected_model = max(model_scores.items(), key=lambda x: x[1])[0]
        
        # Override with preferred model if specified and capable
        if (self.preferred_model in [m.value for m in suitable_models] and 
            not optimize_for in ["speed", "cost"]):
            return ModelType(self.preferred_model)

        return selected_model

    def get_model_config(self, model_type: ModelType, task_type: str) -> Dict:
        """Get model-specific configuration parameters"""
        base_config = {
            "temperature": 0.2,  # Default to low temperature for code generation
            "max_tokens": 4000,
            "stop": None,
            "presence_penalty": 0,
            "frequency_penalty": 0
        }

        # Task-specific adjustments
        if task_type == "clientlib":
            base_config["temperature"] = 0.3  # Slightly more creative for UI code
        elif task_type == "dialog":
            base_config["temperature"] = 0.1  # Very precise for dialog XML
        elif task_type == "sling_model":
            base_config["temperature"] = 0.1  # Very precise for Java code

        # Model-specific adjustments
        if model_type in [ModelType.GPT35_TURBO, ModelType.CLAUDE_INSTANT, ModelType.GEMINI_PRO]:
            base_config["temperature"] *= 0.8  # Reduce temperature for less capable models

        return base_config
