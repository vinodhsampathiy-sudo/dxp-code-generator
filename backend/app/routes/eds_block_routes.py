from fastapi import APIRouter, HTTPException
from app.services.eds.block_service import EDSBlockService
from app.utils.helper_utils import HelperUtils
from app.chatStorage.chat_model import ChatStorage, ChatMessage, GeneratedComponent
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Initialize logger once
logger = HelperUtils.setup_logger("fastapi_app")

router = APIRouter()
block_service = EDSBlockService()
chat_storage = ChatStorage()

class BlockInput(BaseModel):
    description: str
    sessionId: Optional[str] = None
    userId: Optional[str] = None
    imageUrl: Optional[str] = None  # URL to uploaded design image
    designAnalysis: Optional[dict] = None  # Pre-analyzed design data


@router.post("/generate-eds-block")  # will resolve to /api/component/generate-eds-block
async def generate_block(input_data: BlockInput):
    logger.info("="*80)
    logger.info("🚀 EDS BLOCK GENERATION REQUEST")
    logger.info(f"📝 SessionId: {input_data.sessionId}")
    logger.info(f"📝 UserId: {input_data.userId}")
    logger.info(f"📝 Description: {input_data.description[:100]}...")
    logger.info("="*80)
    try:
        session_id = input_data.sessionId
        logger.info(f"🔑 Extracted session_id: '{session_id}' (type: {type(session_id).__name__})")
        
        # Add user message to session if session exists
        if session_id:
            logger.info(f"✅ Session ID exists, adding user message")
            user_message = ChatMessage(
                message_type="user",
                content=input_data.description,
                timestamp=datetime.utcnow()
            )
            msg_result = chat_storage.add_message_to_session(session_id, user_message)
            logger.info(f"📨 User message added: {msg_result}")
        else:
            logger.warning(f"⚠️  NO SESSION ID - component will NOT be saved!")
        
        
        # Call the service to generate the EDS block files
        logger.info("🔧 Starting block generation workflow...")
        if input_data.imageUrl:
            logger.info(f"🖼️  Using design image: {input_data.imageUrl}")
        if input_data.designAnalysis:
            logger.info(f"🎨 Using design analysis data")
        
        result = block_service.run_workflow(
            description=input_data.description,
            image_url=input_data.imageUrl,
            design_analysis=input_data.designAnalysis
        )
        logger.info(f"✅ Block generated! Result keys: {list(result.keys()) if result else 'None'}")
        
        # Add AI response and generated component to session if session exists
        if session_id and result:
            logger.info("💾 SAVING TO SESSION")
            logger.info(f"💾 Session ID: {session_id}")
            
            # Add AI response message
            ai_message = ChatMessage(
                message_type="ai",
                content="Here's your generated EDS block.",
                timestamp=datetime.utcnow()
            )
            ai_msg_result = chat_storage.add_message_to_session(session_id, ai_message)
            logger.info(f"📨 AI message added: {ai_msg_result}")
            
            # Extract block name from result or use default
            block_name = result.get('file_name', 'EDS Block').replace('.zip', '')
            logger.info(f"📦 Block name: {block_name}")
            
            # Create generated component record
            logger.info("📦 Creating GeneratedComponent object...")
            component = GeneratedComponent(
                component_name=block_name,
                sling_model_name="",  # Not applicable for EDS
                htl_code="",  # Not applicable for EDS
                sling_model_code="",  # Not applicable for EDS
                dialog_code="",  # Not applicable for EDS
                content_xml="",  # Not applicable for EDS
                client_lib={
                    'css': result.get('css', ''),
                    'js': result.get('js', ''),
                    'mkd_table': result.get('mkd_table', ''),
                    'zip_base64': result.get('zip_base64', ''),
                    'file_name': result.get('file_name', '')
                },
                generation_timestamp=datetime.utcnow(),
                generation_metadata={
                    'platform': 'EDS',
                    'description': input_data.description
                }
            )
            logger.info(f"📦 Component created - ID: {component.component_id}")
            logger.info(f"📦 Component name: {component.component_name}")
            logger.info(f"📦 client_lib keys: {list(component.client_lib.keys())}")
            logger.info(f"📦 CSS length: {len(component.client_lib.get('css', ''))}")
            logger.info(f"📦 JS length: {len(component.client_lib.get('js', ''))}")
            
            logger.info(f"💾 Calling add_component_to_session('{session_id}', component)...")
            save_result = chat_storage.add_component_to_session(session_id, component)
            logger.info(f"💾 Save result: {save_result}")
            
            if not save_result:
                logger.error(f"❌ FAILED TO SAVE COMPONENT TO SESSION {session_id}")
            else:
                logger.info(f"✅ COMPONENT SUCCESSFULLY SAVED TO SESSION {session_id}")
            
            # Add session_id, component_id, and name to result
            result['session_id'] = session_id
            result['component_id'] = component.component_id
            result['name'] = block_name
            logger.info(f"✅ Added metadata to result - component_id: {component.component_id}")
        elif not session_id:
            logger.warning("⚠️  Skipping save - NO SESSION ID")
        elif not result:
            logger.error("❌ Skipping save - NO RESULT from generation")

        # Transform result to match frontend expectations
        response_data = {
            'block_name': result.get('block_name', result.get('name', 'generated-block')),
            'css': result.get('css_code', ''),
            'js': result.get('js_code', ''),
            'mkd_table': result.get('markdown_table', ''),
            'zip_base64': result.get('zip_base64', ''),
            'file_name': result.get('file_name', 'block.zip')
        }
        
        # Add session and component info if available
        if 'session_id' in result:
            response_data['session_id'] = result['session_id']
        if 'component_id' in result:
            response_data['component_id'] = result['component_id']
        
        logger.info("="*80)
        logger.info("✅ EDS BLOCK GENERATION COMPLETE")
        logger.info(f"📦 Response data keys: {list(response_data.keys())}")
        logger.info(f"📦 CSS length: {len(response_data['css'])}")
        logger.info(f"📦 JS length: {len(response_data['js'])}")
        logger.info("="*80)
        return response_data
    except Exception as e:
        logger.error("="*80)
        logger.error(f"❌ ERROR DURING BLOCK GENERATION: {str(e)}")
        logger.error("="*80, exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred during block generation: {str(e)}")