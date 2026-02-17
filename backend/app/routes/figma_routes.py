from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.services.figma_service import FigmaService
from app.schemas.image_schemas import FigmaParseRequest, FigmaParseResponse
from app.utils.helper_utils import HelperUtils

logger = HelperUtils.setup_logger("figma_routes")
router = APIRouter()
figma_service = FigmaService()

@router.post("/parse", response_model=FigmaParseResponse)
async def parse_figma_url(
    request: FigmaParseRequest,
    x_figma_token: Optional[str] = Header(None)
):
    """
    Parse a Figma URL and return design data and rendered image
    """
    try:
        logger.info(f"Parsing Figma URL: {request.figmaUrl}")
        
        # Use token from header if provided, otherwise service will use env var
        api_token = request.apiToken or x_figma_token
        
        response = await figma_service.get_design_data(
            figma_url=request.figmaUrl,
            user_token=api_token
        )
        
        logger.info(f"Figma URL parsed successfully. File: {response.fileName}")
        return response
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error parsing Figma URL: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process Figma URL: {str(e)}")
