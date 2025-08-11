from fastapi import APIRouter, HTTPException
from app.services.eds.block_service import EDSBlockService
from app.utils.helper_utils import HelperUtils
from pydantic import BaseModel

# Initialize logger once
logger = HelperUtils.setup_logger("fastapi_app")

router = APIRouter()
block_service = EDSBlockService()
class BlockInput(BaseModel):
    description: str

@router.post("/generate-eds-block")  # will resolve to /auth/login
async def generate_block(input_data: BlockInput):
    logger.info(f"Received EDS Block generation request")
    try:
        # Call the service to generate the EDS block files
        result = block_service.run_workflow(input_data.description)

        logger.info("EDS Block generation completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error during block generation: ", e)
        raise HTTPException(status_code=500, detail="An error occurred during block generation.")