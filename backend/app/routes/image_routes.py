"""
API routes for image upload and analysis
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from app.services.image_service import ImageService
from app.services.design_analysis_service import DesignAnalysisService
from app.schemas.image_schemas import (
    ImageUploadResponse,
    ImageAnalysisRequest,
    ImageAnalysisResponse
)
from app.utils.helper_utils import HelperUtils

logger = HelperUtils.setup_logger("image_routes")

router = APIRouter()
image_service = ImageService()
design_analysis_service = DesignAnalysisService()


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    analyze: bool = Form(True),
    userContext: Optional[str] = Form(None)
):
    """
    Upload an image file for design analysis
    
    Args:
        file: Image file (PNG, JPG, SVG, WebP)
        analyze: Whether to perform AI design analysis (default: True)
        userContext: Optional context/description from user
        
    Returns:
        ImageUploadResponse with file info and optional design analysis
    """
    try:
        logger.info(f"Received image upload: {file.filename} (analyze={analyze})")
        
        # Save the uploaded file
        file_info = await image_service.save_upload(file)
        
        # Perform design analysis if requested
        design_analysis = None
        if analyze:
            try:
                logger.info("Performing design analysis...")
                design_analysis = design_analysis_service.analyze_design(
                    image_path=file_info["imageUrl"],
                    user_context=userContext
                )
                logger.info(f"Design analysis complete. Block type: {design_analysis.blockType}")
            except Exception as e:
                logger.error(f"Design analysis failed: {str(e)}", exc_info=True)
                # Continue without analysis rather than failing the upload
        
        # Build response
        response = ImageUploadResponse(
            imageUrl=file_info["imageUrl"],
            imageId=file_info["imageId"],
            fileName=file_info["fileName"],
            fileSize=file_info["fileSize"],
            mimeType=file_info["mimeType"],
            designAnalysis=design_analysis
        )
        
        logger.info(f"Image upload successful: {file_info['imageId']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analyze an already-uploaded image
    
    Args:
        request: ImageAnalysisRequest with imageUrl and optional context
        
    Returns:
        ImageAnalysisResponse with design analysis
    """
    try:
        logger.info(f"Analyzing image: {request.imageUrl}")
        
        # Perform design analysis
        design_analysis = design_analysis_service.analyze_design(
            image_path=request.imageUrl,
            user_context=request.userPrompt
        )
        
        # Generate block suggestions based on analysis
        block_suggestions = []
        if design_analysis.blockType:
            block_suggestions.append(design_analysis.blockType)
        
        # Add suggestions based on interactive elements
        for element in design_analysis.interactiveElements:
            element_lower = element.lower()
            if 'carousel' in element_lower or 'slider' in element_lower:
                block_suggestions.append('carousel')
            elif 'accordion' in element_lower:
                block_suggestions.append('accordion')
            elif 'tab' in element_lower:
                block_suggestions.append('tabs')
            elif 'modal' in element_lower or 'dialog' in element_lower:
                block_suggestions.append('modal')
        
        # Remove duplicates
        block_suggestions = list(set(block_suggestions))
        
        response = ImageAnalysisResponse(
            imageUrl=request.imageUrl,
            designAnalysis=design_analysis,
            blockSuggestions=block_suggestions
        )
        
        logger.info(f"Analysis complete. Suggestions: {block_suggestions}")
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{image_id}")
async def delete_image(image_id: str):
    """
    Delete an uploaded image
    
    Args:
        image_id: ID of the image to delete
        
    Returns:
        Success message
    """
    try:
        success = image_service.delete_image(image_id)
        if success:
            return {"message": "Image deleted successfully", "imageId": image_id}
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
