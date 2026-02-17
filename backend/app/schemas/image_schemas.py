"""
Pydantic schemas for image upload and design analysis
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, HttpUrl
import re


class DesignAnalysis(BaseModel):
    """Design analysis extracted from image"""
    colorPalette: Dict[str, str] = Field(default_factory=dict, description="Color palette with semantic names")
    typography: Dict[str, str] = Field(default_factory=dict, description="Typography styles")
    spacing: Dict[str, str] = Field(default_factory=dict, description="Spacing patterns")
    layoutPattern: Optional[str] = Field(None, description="Layout type: grid, flex, stack, etc.")
    interactiveElements: List[str] = Field(default_factory=list, description="Detected interactive elements")
    themeVariants: List[str] = Field(default_factory=list, description="Theme variants: dark, light, etc.")
    responsiveBreakpoints: List[str] = Field(default_factory=list, description="Responsive breakpoints")
    blockType: Optional[str] = Field(None, description="Inferred block type")
    functionalityDescription: Optional[str] = Field(None, description="Inferred functionality")


class ImageUploadResponse(BaseModel):
    """Response from image upload"""
    imageUrl: str = Field(..., description="URL/path to uploaded image")
    imageId: str = Field(..., description="Unique identifier for the image")
    fileName: str = Field(..., description="Original filename")
    fileSize: int = Field(..., description="File size in bytes")
    mimeType: str = Field(..., description="MIME type of the image")
    designAnalysis: Optional[DesignAnalysis] = Field(None, description="AI-generated design analysis")


class ImageAnalysisRequest(BaseModel):
    """Request to analyze an uploaded image"""
    imageUrl: str = Field(..., description="URL/path to the image")
    userPrompt: Optional[str] = Field(None, description="Additional context from user")
    analyzeDesign: bool = Field(True, description="Whether to perform design analysis")


class ImageAnalysisResponse(BaseModel):
    """Response from image analysis"""
    imageUrl: str
    designAnalysis: DesignAnalysis
    blockSuggestions: List[str] = Field(default_factory=list, description="Suggested block types")


class FigmaParseRequest(BaseModel):
    """Request to parse Figma URL"""
    figmaUrl: str = Field(..., description="Figma file or frame URL")
    apiToken: Optional[str] = Field(None, description="Figma API token (optional if set in env)")
    
    @field_validator('figmaUrl')
    @classmethod
    def validate_figma_url(cls, v):
        """Validate Figma URL format"""
        if not v.startswith('https://www.figma.com/'):
            raise ValueError('Invalid Figma URL. Must start with https://www.figma.com/')
        return v


class FigmaParseResponse(BaseModel):
    """Response from Figma URL parsing"""
    fileId: str = Field(..., description="Figma file ID")
    nodeId: Optional[str] = Field(None, description="Figma node ID if specific frame")
    imageUrl: str = Field(..., description="Rendered image URL from Figma")
    designTokens: Optional[DesignAnalysis] = Field(None, description="Extracted design tokens")
    fileName: Optional[str] = Field(None, description="Figma file name")


class BlockGenerationWithImageRequest(BaseModel):
    """Extended block generation request with image support"""
    description: str = Field(..., description="Text description of the block")
    sessionId: Optional[str] = Field(None, description="Chat session ID")
    userId: Optional[str] = Field(None, description="User ID")
    imageUrl: Optional[str] = Field(None, description="URL to design image")
    figmaUrl: Optional[str] = Field(None, description="Figma URL")
    designAnalysis: Optional[DesignAnalysis] = Field(None, description="Pre-analyzed design data")
