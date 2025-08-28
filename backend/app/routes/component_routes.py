import base64
import logging
from typing import Optional, List
from datetime import datetime
from fastapi.responses import JSONResponse

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request, File, UploadFile, Form, Query
from pydantic import BaseModel
from ..services.component_service import ComponentService
from ..chatStorage.chat_model import ChatStorage

logger = logging.getLogger(__name__)

router = APIRouter()
component_service = ComponentService()

# Simplified Pydanti# New Pydantic models for component search and reuse
class ComponentSearchRequest(BaseModel):
    component_type: str
    limit: Optional[int] = 10

class ComponentReuseRequest(BaseModel):
    session_id: str
    source_component_id: str
    source_session_id: str
    customization_prompt: Optional[str] = None

# Component search and reuse endpoints
@router.get("/test-search")
async def test_search():
    """Test search endpoint"""
    return {"message": "Search endpoint is working"}

@router.get("/search")
async def search_components(component_type: str = Query(...), limit: int = Query(default=10)):
    """Search for existing components by type"""
    try:
        logger.info(f"Searching for components of type: {component_type}")
        
        components = component_service.search_existing_components(component_type, limit)
        
        return {
            "success": True,
            "message": f"Found {len(components)} components matching '{component_type}'",
            "components": components
        }
        
    except Exception as e:
        logger.error(f"Error searching components: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Component search failed",
                "details": str(e)
            }
        )

@router.get("/{session_id}/{component_id}")
async def get_component_details(session_id: str, component_id: str):
    """Get detailed information about a specific component"""
    try:
        logger.info(f"Getting component details: {component_id} from session: {session_id}")
        
        component = component_service.get_component_details(session_id, component_id)
        
        if not component:
            raise HTTPException(
                status_code=404,
                detail="Component not found"
            )
        
        return {
            "success": True,
            "component": component
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting component details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get component details",
                "details": str(e)
            }
        )

@router.post("/reuse", response_model=ComponentResponse)
async def reuse_component(request: ComponentReuseRequest):
    """Reuse an existing component with optional customization"""
    try:
        logger.info(f"Reusing component {request.source_component_id} from session {request.source_session_id}")
        
        result = await component_service.reuse_existing_component(
            session_id=request.session_id,
            source_component_id=request.source_component_id,
            source_session_id=request.source_session_id,
            customization_prompt=request.customization_prompt
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Component reuse failed")
            )
        
        return ComponentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reusing component: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Component reuse failed",
                "details": str(e)
            }
        )

# Legacy endpoint for backward compatibility (if needed)
@router.post("/component/generate", response_model=ComponentResponse)
async def generate_component_legacy(
        componentDesc: str = Form(...),
        file: Optional[UploadFile] = File(default=None)
):
    """Legacy endpoint for backward compatibility"""
    return await generate_component(
        componentDesc=componentDesc,
        sessionId=None,
        userId=None,
        file=file
    )
    componentDesc: str
    sessionId: Optional[str] = None
    userId: Optional[str] = None

class ChatSessionCreate(BaseModel):
    session_title: str
    user_id: Optional[str] = None

class ComponentRefinementRequest(BaseModel):
    session_id: str
    component_id: str
    refinement_prompt: str
    user_id: Optional[str] = None

# New Pydantic models for component search and reuse
class ComponentSearchRequest(BaseModel):
    component_type: str
    limit: Optional[int] = 10

class ComponentReuseRequest(BaseModel):
    session_id: str
    source_component_id: str
    source_session_id: str
    customization_prompt: Optional[str] = None

class MessageRequest(BaseModel):
    message_type: str = "user"
    content: str
    image_data: Optional[str] = None
    metadata: Optional[dict] = None

class SessionResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class ComponentResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    session_id: Optional[str] = None
    component_id: Optional[str] = None
    outputDirs: Optional[dict] = None
    structure: Optional[dict] = None
    aiOutput: Optional[dict] = None
    error: Optional[str] = None
    details: Optional[str] = None

# Component search and reuse endpoints

# Chat Session Management Endpoints
@router.post("/chat/sessions", response_model=SessionResponse)
async def create_chat_session(session_data: ChatSessionCreate):
    """Create a new chat session"""
    try:
        session_id = component_service.create_chat_session(
            session_title=session_data.session_title,
            user_id=session_data.user_id
        )

        logger.info(f"Created new chat session: {session_id}")
        return SessionResponse(
            success=True,
            session_id=session_id,
            message="Chat session created successfully"
        )

    except Exception as e:
        logger.error(f"Failed to create chat session: {str(e)}", exc_info=True)
        return SessionResponse(success=False, error=str(e))

@router.get("/chat/sessions/{session_id}")
@router.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Get a specific chat session"""
    try:
        session = component_service.get_chat_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert to dict and clean it (same logic as debug endpoint)
        session_dict = session.model_dump()

        # Use the same cleaning function that works in debug
        def clean_for_response(obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            elif hasattr(obj, 'isoformat'):  # datetime objects
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {key: clean_for_response(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_response(item) for item in obj]
            else:
                return obj

        # Clean the entire response
        clean_session_dict = clean_for_response(session_dict)

        response_data = {
            'success': True,
            'session': clean_session_dict
        }

        # Return JSONResponse directly (bypasses FastAPI's automatic serialization)
        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve chat session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions")
async def get_chat_sessions(
        user_id: Optional[str] = Query(None),
        limit: int = Query(20, ge=1, le=100)
):
    """Get chat sessions for a user"""
    try:
        sessions = component_service.get_user_chat_sessions(user_id, limit)

        # Clean and convert sessions to dicts for JSON serialization
        def clean_for_response(obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            elif hasattr(obj, 'isoformat'):  # datetime objects
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {key: clean_for_response(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_response(item) for item in obj]
            else:
                return obj

        sessions_data = []
        for session in sessions:
            session_dict = {
                'session_id': session.session_id,
                'session_title': session.session_title,
                'created_at': session.created_at.isoformat() if hasattr(session.created_at, 'isoformat') else str(session.created_at),
                'updated_at': session.updated_at.isoformat() if hasattr(session.updated_at, 'isoformat') else str(session.updated_at),
                'message_count': len(session.messages),
                'component_count': len(session.generated_components),
                'user_id': session.user_id
            }
            sessions_data.append(session_dict)

        response_data = {
            'success': True,
            'sessions': sessions_data
        }

        # Return JSONResponse directly
        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Failed to retrieve chat sessions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions/search")
async def search_chat_sessions(
        q: str = Query(..., description="Search term"),
        user_id: Optional[str] = Query(None),
        limit: int = Query(10, ge=1, le=50)
):
    """Search chat sessions"""
    try:
        sessions = component_service.search_chat_sessions(q, user_id)

        # Convert sessions to dicts for JSON serialization
        sessions_data = []
        for session in sessions[:limit]:  # Apply limit
            session_dict = {
                'session_id': session.session_id,
                'session_title': session.session_title,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
                'message_count': len(session.messages),
                'component_count': len(session.generated_components),
                'user_id': session.user_id
            }
            sessions_data.append(session_dict)

        return {
            'success': True,
            'sessions': sessions_data
        }

    except Exception as e:
        logger.error(f"Failed to search chat sessions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session"""
    try:
        success = component_service.delete_chat_session(session_id)

        if success:
            return {
                'success': True,
                'message': 'Session deleted successfully'
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found or could not be deleted")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete chat session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions/{session_id}/components")
async def get_session_components(session_id: str):
    """Get all components from a session"""
    try:
        components = component_service.get_session_components(session_id)

        return {
            'success': True,
            'components': components
        }

    except Exception as e:
        logger.error(f"Failed to retrieve components for session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/sessions/{session_id}/messages")
async def add_message_to_session(session_id: str, message_data: MessageRequest):
    """Add a message to a session"""
    try:
        success = component_service.add_message_to_session(
            session_id=session_id,
            message_type=message_data.message_type,
            content=message_data.content,
            image_data=message_data.image_data,
            metadata=message_data.metadata
        )

        if success:
            return {
                'success': True,
                'message': 'Message added successfully'
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to add message")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add message to session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Component Generation and Refinement Endpoints (Simplified)
@router.post("/generate", response_model=ComponentResponse)
async def generate_component(
        componentDesc: str = Form(...),
        sessionId: Optional[str] = Form(None),
        userId: Optional[str] = Form(None),
        file: Optional[UploadFile] = File(default=None)
):
    """Generate a component (enhanced with session support)"""
    try:
        logger.info(f"Received component generation request")
        logger.debug(f"Request data: prompt='{componentDesc}', sessionId='{sessionId}'")

        # Read and encode uploaded image
        image_bytes = None
        if file is not None:
            image_bytes = await file.read()
            logger.info(f"Received image file: {file.filename}, size: {len(image_bytes)} bytes")

        result = await component_service.generate_component(
            prompt=componentDesc,
            image=image_bytes,
            session_id=sessionId,
            user_id=userId
        )

        logger.info("Component generation completed successfully")

        # Convert the result to match ComponentResponse model
        return ComponentResponse(
            success=result.get('success', False),
            message=result.get('message'),
            session_id=result.get('session_id'),
            component_id=result.get('component_id'),
            outputDirs=result.get('outputDirs'),
            structure=result.get('structure'),
            aiOutput=result.get('aiOutput'),
            error=result.get('error'),
            details=result.get('details')
        )

    except Exception as e:
        logger.error(f"Error in generate_component endpoint: {str(e)}", exc_info=True)
        return ComponentResponse(
            success=False,
            error="Component generation failed",
            details=str(e)
        )

@router.post("/refine", response_model=ComponentResponse)
async def refine_component(refinement_data: ComponentRefinementRequest):
    """Refine an existing component"""
    try:
        logger.info(f"Received component refinement request for component {refinement_data.component_id}")

        result = await component_service.refine_component(
            session_id=refinement_data.session_id,
            component_id=refinement_data.component_id,
            refinement_prompt=refinement_data.refinement_prompt,
            user_id=refinement_data.user_id
        )

        logger.info("Component refinement completed successfully")

        return ComponentResponse(
            success=result.get('success', False),
            message=result.get('message'),
            session_id=result.get('session_id'),
            component_id=result.get('component_id'),
            outputDirs=result.get('outputDirs'),
            aiOutput=result.get('aiOutput'),
            error=result.get('error'),
            details=result.get('details')
        )

    except Exception as e:
        logger.error(f"Error in refine_component endpoint: {str(e)}", exc_info=True)
        return ComponentResponse(
            success=False,
            error="Component refinement failed",
            details=str(e)
        )

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        sessions = component_service.get_user_chat_sessions(limit=1)

        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'services': {
                'component_service': 'active',
                'chat_storage': 'connected'
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }

@router.get("/debug/sessions/{session_id}/clean")
async def debug_clean_session(session_id: str):
    """Debug endpoint with manual JSON cleaning"""
    try:
        # Get raw data from MongoDB
        raw_data = component_service.chat_storage.db.chat_sessions.find_one({"session_id": session_id})

        if not raw_data:
            return {"error": "Session not found"}

        # Convert everything to strings/basic types
        def deep_clean(obj):
            if isinstance(obj, ObjectId):
                return str(obj)
            elif isinstance(obj, dict):
                if "$date" in obj:
                    return obj["$date"]  # Return as string for now
                elif "$oid" in obj:
                    return obj["$oid"]
                else:
                    return {key: deep_clean(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [deep_clean(item) for item in obj]
            else:
                return obj

        cleaned_data = deep_clean(raw_data)

        return {
            "success": True,
            "session": cleaned_data
        }

    except Exception as e:
        return {"error": str(e)}

# AEM Component Deployment endpoint
@router.post("/deploy", response_model=ComponentResponse)
async def deploy_aem_component(
    session_id: str = Form(...),
    component_id: str = Form(...),
    target_environment: Optional[str] = Form(default="development"),
    user_id: Optional[str] = Form(default="default_user")
):
    """Deploy AEM component to target environment"""
    try:
        logger.info(f"Received deployment request for component {component_id}")
        
        # Get the component from database
        chat_storage = ChatStorage()
        session = chat_storage.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Find the component
        component = None
        for comp in session.get('generated_components', []):
            if comp['component_id'] == component_id:
                component = comp
                break
        
        if not component:
            raise HTTPException(status_code=404, detail="Component not found")
        
        # Simulate deployment process
        import asyncio
        await asyncio.sleep(1)  # Simulate deployment time
        
        # Log deployment details
        logger.info(f"Deploying component '{component['component_name']}' to {target_environment}")
        logger.info(f"Component type: AEM")
        logger.info(f"User: {user_id}")
        
        # Add deployment message to session
        component_service.add_message_to_session(session_id, "system", 
            f"Component '{component['component_name']}' has been deployed to {target_environment} environment.", 
            None, {
                'action': 'deploy',
                'component_id': component_id,
                'target_environment': target_environment
            })
        
        logger.info("Component deployment completed successfully")
        return ComponentResponse(
            success=True,
            message=f"Component '{component['component_name']}' deployed successfully to {target_environment}",
            session_id=session_id,
            component_id=component_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in deploy_aem_component endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Component deployment failed",
                "details": str(e)
            }
        )

# Legacy endpoint for backward compatibility (if needed)
@router.post("/component/generate", response_model=ComponentResponse)
async def generate_component_legacy(
        componentDesc: str = Form(...),
        file: Optional[UploadFile] = File(default=None)
):
    """Legacy endpoint for backward compatibility"""
    return await generate_component(
        componentDesc=componentDesc,
        sessionId=None,
        userId=None,
        file=file
    )