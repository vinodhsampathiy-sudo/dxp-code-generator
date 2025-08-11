from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.project_service import ProjectService

router = APIRouter()
project_service = ProjectService()

class ProjectRequest(BaseModel):
    aem_version: str
    archetype_version: str
    app_title: str
    app_id: str
    group_id: str
    artifact_id: str
    package: str
    version: str

@router.post("/generate", summary="Generate project from AEM")
async def generate_project(request: ProjectRequest):
    try:
        result = await project_service.generate_project_structure(request.model_dump_json())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))