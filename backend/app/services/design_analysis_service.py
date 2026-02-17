"""
Design analysis service using AI vision models
"""
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from openai import OpenAI
from app.schemas.image_schemas import DesignAnalysis
from app.utils.helper_utils import HelperUtils

logger = HelperUtils.setup_logger("design_analysis_service")


class DesignAnalysisService:
    """Service for analyzing design images using AI vision"""
    
    VISION_ANALYSIS_PROMPT = """You are an expert UI/UX designer and frontend developer. Analyze this design image and extract detailed design information.

Your task is to:
1. **Identify the component type**: What kind of UI component is this? (e.g., hero section, carousel, accordion, tabs, card, button, form, navigation, footer, etc.)
2. **Extract color palette**: Identify all colors used with semantic names (primary, secondary, background, text, accent, etc.)
3. **Analyze typography**: Font families (or suggest web-safe alternatives), sizes, weights, line heights
4. **Measure spacing**: Padding, margins, gaps between elements (estimate in px or rem)
5. **Determine layout pattern**: Grid, flexbox, stack, absolute positioning, etc.
6. **Identify interactive elements**: Buttons, links, inputs, carousels, dropdowns, modals, etc.
7. **Detect theme variants**: Light/dark mode, color schemes
8. **Infer responsive behavior**: How should this adapt to mobile/tablet/desktop?
9. **Describe functionality**: What does this component do? How should it behave?

Return a JSON object with this exact structure:
{
  "blockType": "string (e.g., 'hero', 'carousel', 'accordion', 'tabs', 'card')",
  "functionalityDescription": "string (detailed description of what this component does and how it should behave)",
  "colorPalette": {
    "primary": "#hex",
    "secondary": "#hex",
    "background": "#hex",
    "text": "#hex",
    "accent": "#hex"
  },
  "typography": {
    "headingFont": "font-family",
    "headingSize": "size in px or rem",
    "headingWeight": "weight",
    "bodyFont": "font-family",
    "bodySize": "size",
    "bodyWeight": "weight"
  },
  "spacing": {
    "containerPadding": "value",
    "elementGap": "value",
    "sectionMargin": "value"
  },
  "layoutPattern": "string (grid/flex/stack)",
  "interactiveElements": ["array", "of", "interactive", "elements"],
  "themeVariants": ["light", "dark"],
  "responsiveBreakpoints": ["mobile: 0-600px", "tablet: 600-900px", "desktop: 900px+"]
}

Be specific and detailed. If you can't determine something, make a reasonable assumption based on modern web design best practices."""

    def __init__(self):
        """Initialize design analysis service"""
        self.client = OpenAI()
        logger.info("Design analysis service initialized")
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for API"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            raise
    
    def analyze_design(
        self, 
        image_path: str, 
        user_context: Optional[str] = None
    ) -> DesignAnalysis:
        """
        Analyze design image using GPT-4 Vision
        
        Args:
            image_path: Path to the image file
            user_context: Optional additional context from user
            
        Returns:
            DesignAnalysis object with extracted design tokens
        """
        try:
            logger.info(f"Analyzing design image: {image_path}")
            
            # Prepare the prompt
            prompt = self.VISION_ANALYSIS_PROMPT
            if user_context:
                prompt += f"\n\nAdditional context from user: {user_context}"
            
            # Check if image is a URL or local file
            if image_path.startswith('http'):
                # Remote URL
                image_content = {
                    "type": "image_url",
                    "image_url": {"url": image_path}
                }
            else:
                # Local file - encode to base64
                base64_image = self.encode_image(image_path)
                file_ext = Path(image_path).suffix.lower()
                mime_type = self._get_mime_type(file_ext)
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    }
                }
            
            # Call GPT-4 Vision
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4 Turbo with vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            image_content
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parse response
            content = response.choices[0].message.content
            logger.info(f"Received vision analysis response: {content[:200]}...")
            
            # Extract JSON from response
            design_data = self._extract_json(content)
            
            # Create DesignAnalysis object
            analysis = DesignAnalysis(**design_data)
            logger.info(f"Design analysis complete. Block type: {analysis.blockType}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing design: {str(e)}", exc_info=True)
            # Return empty analysis on error
            return DesignAnalysis()
    
    def _get_mime_type(self, file_ext: str) -> str:
        """Get MIME type from file extension"""
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp'
        }
        return mime_types.get(file_ext.lower(), 'image/png')
    
    def _extract_json(self, content: str) -> Dict[str, Any]:
        """Extract JSON from AI response"""
        try:
            # Try to parse as JSON directly
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                json_str = content[start:end].strip()
                return json.loads(json_str)
            elif '```' in content:
                start = content.find('```') + 3
                end = content.find('```', start)
                json_str = content[start:end].strip()
                return json.loads(json_str)
            else:
                # Try to find JSON object in text
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    return json.loads(json_str)
                else:
                    logger.error("Could not extract JSON from response")
                    return {}
