import logging
from typing import Optional, List
from datetime import datetime
from fastapi.responses import JSONResponse

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from ..chatStorage.chat_model import ChatStorage, ChatSession, ChatMessage, GeneratedComponent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/eds", tags=["EDS Chat"])

# Initialize chat storage
chat_storage = ChatStorage()

# Pydantic models
class EDSSessionCreate(BaseModel):
    session_title: str
    user_id: Optional[str] = None
    model_provider: str = "openai"

class EDSMessageRequest(BaseModel):
    message_type: str = "user"
    content: str
    image_data: Optional[str] = None
    metadata: Optional[dict] = None

class SessionResponse(BaseModel):
    success: bool
    session_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

# Chat Session Management Endpoints
@router.post("/chat/sessions", response_model=SessionResponse)
async def create_eds_chat_session(session_data: EDSSessionCreate):
    """Create a new EDS chat session"""
    try:
        session_id = chat_storage.create_chat_session(
            session_title=session_data.session_title,
            user_id=session_data.user_id,
            model_provider=session_data.model_provider,
            platform_type="EDS"  # Set platform type to EDS
        )

        logger.info(f"Created new EDS chat session: {session_id}")
        return SessionResponse(
            success=True,
            session_id=session_id,
            message="EDS chat session created successfully"
        )

    except Exception as e:
        logger.error(f"Failed to create EDS chat session: {str(e)}", exc_info=True)
        return SessionResponse(success=False, error=str(e))

@router.get("/chat/sessions/{session_id}")
async def get_eds_chat_session(session_id: str):
    """Get a specific EDS chat session"""
    try:
        session = chat_storage.get_chat_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Verify it's an EDS session
        if session.platform_type != "EDS":
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert to dict and clean it
        session_dict = session.model_dump()

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
        logger.error(f"Failed to retrieve EDS chat session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions")
async def get_eds_chat_sessions(
        user_id: Optional[str] = Query(None),
        limit: int = Query(20, ge=1, le=100)
):
    """Get EDS chat sessions for a user"""
    try:
        sessions = chat_storage.get_user_chat_sessions(user_id, limit, platform_type="EDS")

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
                'user_id': session.user_id,
                'platform_type': session.platform_type
            }
            sessions_data.append(session_dict)

        response_data = {
            'success': True,
            'sessions': sessions_data
        }

        # Return JSONResponse directly
        return JSONResponse(content=response_data)

    except Exception as e:
        logger.error(f"Failed to retrieve EDS chat sessions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions/search")
async def search_eds_chat_sessions(
        q: str = Query(..., description="Search term"),
        user_id: Optional[str] = Query(None),
        limit: int = Query(10, ge=1, le=50)
):
    """Search EDS chat sessions"""
    try:
        sessions = chat_storage.search_chat_sessions(q, user_id, platform_type="EDS")

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
                'user_id': session.user_id,
                'platform_type': session.platform_type
            }
            sessions_data.append(session_dict)

        return {
            'success': True,
            'sessions': sessions_data
        }

    except Exception as e:
        logger.error(f"Failed to search EDS chat sessions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/sessions/{session_id}")
async def delete_eds_chat_session(session_id: str):
    """Delete an EDS chat session"""
    try:
        # Verify it's an EDS session before deleting
        session = chat_storage.get_chat_session(session_id)
        if session and session.platform_type != "EDS":
            raise HTTPException(status_code=404, detail="Session not found")

        success = chat_storage.delete_chat_session(session_id)

        if success:
            return {
                'success': True,
                'message': 'EDS session deleted successfully'
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found or could not be deleted")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete EDS chat session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions/{session_id}/blocks")
async def get_eds_session_blocks(session_id: str):
    """Get all EDS blocks from a session"""
    try:
        session = chat_storage.get_chat_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Verify it's an EDS session
        if session.platform_type != "EDS":
            raise HTTPException(status_code=404, detail="Session not found")

        # Convert components to dict format
        blocks = []
        for comp in session.generated_components:
            block_dict = {
                'block_id': comp.component_id,
                'block_name': comp.component_name,
                'generation_timestamp': comp.generation_timestamp.isoformat() if hasattr(comp.generation_timestamp, 'isoformat') else str(comp.generation_timestamp),
                'metadata': comp.generation_metadata
            }
            blocks.append(block_dict)

        return {
            'success': True,
            'blocks': blocks
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve EDS blocks for session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/sessions/{session_id}/messages")
async def add_message_to_eds_session(session_id: str, message_data: EDSMessageRequest):
    """Add a message to an EDS session"""
    try:
        # Verify it's an EDS session
        session = chat_storage.get_chat_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.platform_type != "EDS":
            raise HTTPException(status_code=404, detail="Session not found")

        # Create message
        message = ChatMessage(
            message_type=message_data.message_type,
            content=message_data.content,
            image_data=message_data.image_data,
            metadata=message_data.metadata
        )

        success = chat_storage.add_message_to_session(session_id, message)

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
        logger.error(f"Failed to add message to EDS session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint for EDS chat
@router.get("/chat/health")
async def eds_chat_health_check():
    """Health check endpoint for EDS chat functionality"""
    try:
        # Test MongoDB connection by fetching one EDS session
        sessions = chat_storage.get_user_chat_sessions(limit=1, platform_type="EDS")

        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'platform': 'EDS',
            'database': 'connected',
            'services': {
                'chat_storage': 'connected'
            }
        }
    except Exception as e:
        logger.error(f"EDS chat health check failed: {str(e)}")
        return {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'platform': 'EDS',
            'database': 'disconnected',
            'error': str(e)
        }
