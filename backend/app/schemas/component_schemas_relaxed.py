"""
Relaxed Pydantic schemas for component generation - minimal validation
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
import re


class DesignAnalysis(BaseModel):
    """Design analysis extracted from image"""
    colorPalette: Optional[Dict[str, str]] = Field(default_factory=dict)
    typography: Optional[Dict[str, str]] = Field(default_factory=dict)
    spacing: Optional[Dict[str, str]] = Field(default_factory=dict)
    layoutPattern: Optional[str] = None
    interactiveElements: Optional[List[str]] = Field(default_factory=list)
    themeVariants: Optional[List[str]] = Field(default_factory=list)
    responsiveBreakpoints: Optional[List[str]] = Field(default_factory=list)


class ImageAnalysisResponse(BaseModel):
    """Response from image-to-code agent"""
    htmlCode: str = Field(..., min_length=10)
    cssCode: str = Field(..., min_length=10)
    designAnalysis: Optional[DesignAnalysis] = None


class SharedContext(BaseModel):
    """Shared context object from Agent 1"""
    requirement: str
    componentName: str
    componentType: str
    properties: List[str] = Field(default_factory=list)
    complexity: str
    dependencies: List[str] = Field(default_factory=list)
    designPatterns: List[str] = Field(default_factory=list)
    accessibility: List[str] = Field(default_factory=list)
    responsive: bool = True
    interactions: List[str] = Field(default_factory=list)
    validation: List[str] = Field(default_factory=list)
    seoRequirements: List[str] = Field(default_factory=list)
    slingModelName: str
    
    @field_validator('componentName', mode='before')
    @classmethod
    def clean_component_name(cls, v):
        """Auto-clean component name"""
        if isinstance(v, str):
            # Remove spaces and convert to PascalCase
            if ' ' in v:
                v = ''.join(word.capitalize() for word in v.split())
        return v


class SlingModelResponse(BaseModel):
    """Response from Agent 1 - Requirements and Sling Model"""
    sharedContext: SharedContext
    slingModel: str = Field(..., min_length=50)


class HTLResponse(BaseModel):
    """Response from Agent 2 - HTL Template"""
    htl: str = Field(..., min_length=20)


class DialogResponse(BaseModel):
    """Response from Agent 3 - Dialog XML"""
    dialog: Any  # Accept any type
    content_xml: Any = Field(..., alias='.content.xml')  # Accept any type
    
    @field_validator('dialog', mode='before')
    @classmethod
    def extract_dialog(cls, v):
        """Extract dialog XML from dict if needed"""
        if isinstance(v, dict):
            # Extract first XML value
            for key, value in v.items():
                if isinstance(value, str):
                    return value
            return str(v)
        return str(v) if v else ""
    
    @field_validator('content_xml', mode='before')
    @classmethod
    def extract_content_xml(cls, v):
        """Extract content.xml from dict if needed"""
        if isinstance(v, dict):
            for key, value in v.items():
                if isinstance(value, str):
                    return value
            return str(v)
        return str(v) if v else ""


class ClientLibResponse(BaseModel):
    """Response from Agent 4 - Client Library"""
    clientLib: Dict[str, Any]


class ComponentGenerationResponse(BaseModel):
    """Complete component generation response"""
    htl: str
    slingModel: str
    dialog: Any
    content_xml: str
    clientLib: Dict[str, Any]
    slingModelName: str
    componentName: str
    validation: Optional[Dict[str, Any]] = None


class ComponentGenerationError(Exception):
    """Custom exception for component generation errors"""
    def __init__(self, agent: str, error: str, context: Dict[str, Any]):
        self.agent = agent
        self.error = error
        self.context = context
        super().__init__(f"[{agent}] {error}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API response"""
        return {
            "agent": self.agent,
            "error": self.error,
            "context": self.context,
            "error_type": "component_generation_error"
        }
