from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from app.services.aem_core_components_service import aem_core_components_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/aem/core-components", tags=["AEM Core Components"])

class ComponentSearchRequest(BaseModel):
    description: str
    component_type: Optional[str] = None

class CoreComponentsConfigResponse(BaseModel):
    configured: bool
    github_token_available: bool
    cache_dir: str
    repo_info: Dict[str, str]

@router.get("/config", response_model=CoreComponentsConfigResponse)
async def get_core_components_config():
    """Get configuration status for AEM Core Components integration"""
    try:
        service = aem_core_components_service
        return CoreComponentsConfigResponse(
            configured=bool(service.github_token),
            github_token_available=bool(service.github_token),
            cache_dir=str(service.cache_dir),
            repo_info={
                "owner": service.repo_owner,
                "name": service.repo_name,
                "url": f"https://github.com/{service.repo_owner}/{service.repo_name}"
            }
        )
    except Exception as e:
        logger.error(f"Error getting core components config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/components")
async def list_core_components():
    """Get list of available AEM Core Components"""
    try:
        components = await aem_core_components_service.fetch_component_list()
        return {
            "success": True,
            "components": components,
            "total": len(components)
        }
    except Exception as e:
        logger.error(f"Error fetching component list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch components: {str(e)}")

@router.get("/components/{component_name}")
async def get_component_details(component_name: str):
    """Get detailed information about a specific core component"""
    try:
        details = await aem_core_components_service.fetch_component_details(component_name)
        if not details:
            raise HTTPException(status_code=404, detail=f"Component '{component_name}' not found")
        
        return {
            "success": True,
            "component": details
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching component details for {component_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch component details: {str(e)}")

@router.post("/search")
async def search_relevant_components(request: ComponentSearchRequest):
    """Search for relevant core components based on description"""
    try:
        examples = await aem_core_components_service.get_relevant_examples(
            request.description, 
            request.component_type
        )
        
        formatted_examples = aem_core_components_service.format_examples_for_prompt(examples)
        
        return {
            "success": True,
            "examples": examples,
            "formatted_prompt": formatted_examples,
            "total_found": len(examples)
        }
    except Exception as e:
        logger.error(f"Error searching components: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search components: {str(e)}")

@router.post("/clear-cache")
async def clear_components_cache():
    """Clear the core components cache"""
    try:
        import shutil
        cache_dir = aem_core_components_service.cache_dir
        
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            
        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/categories")
async def get_component_categories():
    """Get available component categories"""
    try:
        return {
            "success": True,
            "categories": aem_core_components_service.component_categories
        }
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))
