from typing import Dict, List, Tuple
import re

class ComplexityAnalyzer:
    def __init__(self):
        self.complexity_weights = {
            'fields': {
                'text': 1,
                'textarea': 1,
                'richtext': 2,
                'number': 1,
                'checkbox': 1,
                'select': 2,
                'multifield': 3,
                'image': 2,
                'pathfield': 2
            },
            'features': {
                'responsive': 2,
                'animation': 3,
                'interactive': 3,
                'lazy_loading': 2,
                'lightbox': 3,
                'accessibility': 2
            }
        }

    def analyze_requirements(self, prompt: str) -> Tuple[int, Dict, List[str]]:
        """Analyzes component requirements and returns complexity score and features"""
        score = 0
        features = {
            'fields': [],
            'responsive': False,
            'interactive': False,
            'styling': [],
            'layout': []
        }
        optimizations = []

        # Detect fields
        fields = self._detect_fields(prompt)
        features['fields'] = fields
        score += sum(self.complexity_weights['fields'].get(field_type, 1) for field_type in fields)

        # Detect responsive requirements
        if re.search(r'responsive|mobile|tablet|desktop|breakpoint', prompt, re.I):
            features['responsive'] = True
            score += self.complexity_weights['features']['responsive']
            optimizations.append('parallel_responsive_css')

        # Detect interactive features
        if re.search(r'click|hover|animation|transition|lightbox|lazy|loading', prompt, re.I):
            features['interactive'] = True
            score += self.complexity_weights['features']['interactive']
            optimizations.append('separate_js_generation')

        # Analyze styling complexity
        styling_patterns = [r'theme', r'style', r'color', r'background', r'border', r'shadow']
        styling_matches = [p for p in styling_patterns if re.search(p, prompt, re.I)]
        features['styling'] = styling_matches
        score += len(styling_matches)

        # Analyze layout complexity
        layout_patterns = [r'grid', r'flex', r'position', r'alignment', r'spacing']
        layout_matches = [p for p in layout_patterns if re.search(p, prompt, re.I)]
        features['layout'] = layout_matches
        score += len(layout_matches)

        # Determine optimal model selection
        if score <= 5:
            optimizations.append('use_gpt35_turbo')  # Simple components
        elif score <= 10:
            optimizations.append('use_gpt4_turbo')   # Medium complexity
        else:
            optimizations.append('use_gpt4')         # Complex components

        # Add parallel processing optimizations
        if len(features['fields']) > 3:
            optimizations.append('parallel_dialog_generation')
        
        if features['interactive']:
            optimizations.append('cache_interactive_patterns')

        return score, features, optimizations

    def _detect_fields(self, prompt: str) -> List[str]:
        """Detects field types from the prompt"""
        field_patterns = {
            'text': r'text\s+field|title|label|heading',
            'textarea': r'textarea|description|long text',
            'richtext': r'rich\s*text|rte|formatted text',
            'number': r'number|count|quantity',
            'checkbox': r'checkbox|toggle|boolean',
            'select': r'select|dropdown|choice',
            'multifield': r'multifield|multiple|repeatable',
            'image': r'image|picture|photo',
            'pathfield': r'path|link|url'
        }
        
        detected_fields = []
        for field_type, pattern in field_patterns.items():
            if re.search(pattern, prompt, re.I):
                detected_fields.append(field_type)
        
        return detected_fields
