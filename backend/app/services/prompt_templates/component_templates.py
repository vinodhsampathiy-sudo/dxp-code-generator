from typing import Dict, Any

# Sling Model Templates
SLING_MODEL_TEMPLATES = {
    "base": """
Generate a Sling Model class for an AEM component with the following specifications:
- Component name: {name}
- Fields: {fields}
- Required functionality: {requirements}

Include:
1. Proper annotations (@Model, @ValueMapValue)
2. Null-safe getters
3. Validation logic
4. Javadoc documentation
5. Common interfaces if applicable
""",

    "complex": """
Generate a comprehensive Sling Model implementation with:
1. Advanced Features:
   - Resource type validation
   - Custom adapters
   - Service injection
   - Component inheritance
2. Best Practices:
   - Lazy initialization
   - Caching computed values
   - Resource resolver handling
3. Documentation:
   - Full Javadoc
   - Usage examples
   - Edge cases
""",

    "performance": """
Generate a high-performance Sling Model focusing on:
1. Optimization:
   - Lazy loading
   - Value caching
   - Resource pooling
2. Memory Management:
   - Efficient data structures
   - Resource cleanup
3. Thread Safety:
   - Synchronized methods
   - Atomic operations
"""
}

# HTL Templates
HTL_TEMPLATES = {
    "base": """
Create HTL markup with:
1. Core Features:
   - data-sly-use model binding
   - Proper null checks
   - BEM class naming
2. Structure:
   - Semantic HTML
   - Accessibility attributes
   - Data attributes
""",

    "complex": """
Create advanced HTL implementation with:
1. Advanced Features:
   - Custom data-sly-* blocks
   - Template composition
   - Dynamic attribute handling
2. Performance:
   - Lazy loading
   - Async loading
   - Resource hints
3. Integration:
   - Client library categories
   - Component dependencies
"""
}

# Dialog Templates
DIALOG_TEMPLATES = {
    "base": """
Create a dialog.xml with:
1. Basic Fields:
   - Text fields
   - Rich text
   - Image upload
2. Structure:
   - Logical grouping
   - Field validation
   - Help text
""",

    "complex": """
Create an advanced dialog with:
1. Advanced Fields:
   - Multi fields
   - Composite fields
   - Dynamic dropdowns
2. Features:
   - Conditional fields
   - Custom validation
   - Field dependencies
3. Organization:
   - Multiple tabs
   - Field sets
   - Nested containers
"""
}

# Client Library Templates
CLIENTLIB_TEMPLATES = {
    "base": """
Generate client libraries with:
1. CSS:
   - BEM methodology
   - Basic responsiveness
   - Component styles
2. JavaScript:
   - Component initialization
   - Event handlers
   - Basic interactions
""",

    "complex": """
Generate advanced client libraries with:
1. CSS:
   - Advanced responsive design
   - Theme variations
   - Animation support
2. JavaScript:
   - Component API
   - State management
   - Advanced interactions
3. Performance:
   - Code splitting
   - Lazy loading
   - Asset optimization
"""
}

def get_template_with_features(template_type: str, features: Dict[str, Any], complexity: str = "base") -> str:
    """Get template content based on type and features"""
    templates = {
        "sling": SLING_MODEL_TEMPLATES,
        "htl": HTL_TEMPLATES,
        "dialog": DIALOG_TEMPLATES,
        "clientlib": CLIENTLIB_TEMPLATES
    }
    
    template = templates.get(template_type, {}).get(complexity, "")
    if not template:
        raise ValueError(f"Template not found for type {template_type} and complexity {complexity}")
    
    return template.format(**features)
