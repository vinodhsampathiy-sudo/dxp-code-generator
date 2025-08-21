from pydantic import BaseModel
from fastapi import APIRouter
from ..services.test_prompts import test_prompt_generation

router = APIRouter()

class TestPromptRequest(BaseModel):
    componentDesc: str

class TestPromptResponse(BaseModel):
    success: bool
    message: str
    results: dict = None

@router.post("/test/prompts", response_model=TestPromptResponse)
async def test_prompts(request: TestPromptRequest):
    """Test endpoint for prompt generation system"""
    result = await test_prompt_generation(request.componentDesc)
    return result
