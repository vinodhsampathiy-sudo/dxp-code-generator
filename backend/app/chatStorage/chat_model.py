from datetime import datetime
from typing import Dict, Any, List, Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.functional_validators import BeforeValidator
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from bson import ObjectId
import os
from dotenv import load_dotenv
import logging
import time

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Custom ObjectId type for Pydantic v2
def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str):
        if ObjectId.is_valid(v):
            return ObjectId(v)
    raise ValueError("Invalid ObjectId")

def serialize_object_id(v: ObjectId) -> str:
    return str(v)

# Custom ObjectId type with proper Pydantic v2 annotations
PyObjectId = Annotated[
    ObjectId,
    BeforeValidator(validate_object_id),
    Field(json_schema_extra={"type": "string"})
]

# Pydantic Models for FastAPI
class ChatMessage(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat() if v else None
        }
    )

    id: str = Field(default_factory=lambda: str(ObjectId()))
    message_type: str  # 'user' or 'ai'
    content: str
    image_data: Optional[str] = None  # Base64 encoded image
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class GeneratedComponent(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat() if v else None
        }
    )

    component_id: str = Field(default_factory=lambda: str(ObjectId()))
    component_name: str
    sling_model_name: str
    htl_code: str
    sling_model_code: str
    dialog_code: str
    content_xml: str
    client_lib: Dict[str, Any]
    generation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    generation_metadata: Optional[Dict[str, Any]] = None

class ChatSession(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat() if v else None
        }
    )

    # Remove the _id field from the Pydantic model - let MongoDB handle it
    session_id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: Optional[str] = None
    session_title: str
    messages: List[ChatMessage] = Field(default_factory=list)
    generated_components: List[GeneratedComponent] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    model_provider: str = Field(default="openai")

    @classmethod
    def from_mongo(cls, data: dict):
        """Create ChatSession from MongoDB document"""
        if not data:
            return None

        # Remove the _id field from the data before creating the Pydantic model
        # We don't need it in our application model
        if "_id" in data:
            del data["_id"]

        # Handle datetime fields
        for field in ["created_at", "updated_at"]:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace("Z", "+00:00"))
                except:
                    data[field] = datetime.utcnow()

        # Ensure required fields exist with defaults
        data.setdefault("messages", [])
        data.setdefault("generated_components", [])
        data.setdefault("is_active", True)
        data.setdefault("created_at", datetime.utcnow())
        data.setdefault("updated_at", datetime.utcnow())

        return cls(**data)

def clean_for_json(obj):
    """Recursively clean MongoDB objects for JSON serialization"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        if "$date" in obj:
            # Convert MongoDB date format
            from datetime import datetime
            date_str = obj["$date"]
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        elif "$oid" in obj:
            # Convert MongoDB ObjectId reference
            return obj["$oid"]
        else:
            # Recursively clean dict items
            return {key: clean_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        # Recursively clean list items
        return [clean_for_json(item) for item in obj]
    else:
        return obj

class ChatStorage:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.database_name = os.getenv("MONGODB_DATABASE", "aem_component_generator")
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Initialize MongoDB connection with retry logic"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.client = MongoClient(
                    self.mongo_uri,
                    serverSelectionTimeoutMS=30000,  # 30 seconds timeout
                    connectTimeoutMS=20000,  # 20 seconds connection timeout
                    socketTimeoutMS=20000,   # 20 seconds socket timeout
                )
                
                # Test the connection
                self.client.admin.command('ping')
                
                self.db = self.client[self.database_name]

                # Create indexes for better performance
                self.db.chat_sessions.create_index("session_id", unique=True)
                self.db.chat_sessions.create_index("user_id")
                self.db.chat_sessions.create_index("created_at")
                self.db.chat_sessions.create_index("is_active")

                logger.info(f"Connected to MongoDB: {self.database_name}")
                return
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning(f"MongoDB connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to MongoDB after {max_retries} attempts: {e}")
                    raise e
            except Exception as e:
                logger.error(f"Unexpected error connecting to MongoDB: {e}")
                raise e

    def is_connected(self) -> bool:
        """Check if MongoDB connection is active"""
        try:
            if self.client is None:
                return False
            self.client.admin.command('ping')
            return True
        except Exception:
            return False

    def create_chat_session(self, session_title: str, user_id: Optional[str] = None,
                            model_provider: str = "openai") -> str:
        """Create a new chat session"""
        try:
            # Create session - session_id will be auto-generated by the Field default_factory
            session = ChatSession(
                session_title=session_title,
                user_id=user_id,
                model_provider=model_provider,
                messages=[],
                generated_components=[],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Convert to dict - this will NOT include _id
            session_dict = session.model_dump()

            # Let MongoDB generate the _id automatically by not including it
            # MongoDB will create a proper ObjectId for _id when we insert

            logger.info(f"Inserting session with session_id: {session.session_id}")

            result = self.db.chat_sessions.insert_one(session_dict)
            logger.info(f"Created new chat session with session_id: {session.session_id}, MongoDB _id: {result.inserted_id}")

            return session.session_id

        except Exception as e:
            logger.error(f"Failed to create chat session: {e}")
            raise e

    def get_chat_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a chat session by ID"""
        try:
            session_data = self.db.chat_sessions.find_one({"session_id": session_id})
            if not session_data:
                return None

            # Clean all MongoDB objects
            session_data = clean_for_json(session_data)

            # Remove _id before creating the Pydantic model
            if "_id" in session_data:
                del session_data["_id"]

            # Ensure required fields exist with defaults
            session_data.setdefault("messages", [])
            session_data.setdefault("generated_components", [])
            session_data.setdefault("is_active", True)
            session_data.setdefault("created_at", datetime.utcnow())
            session_data.setdefault("updated_at", datetime.utcnow())

            return ChatSession(**session_data)

        except Exception as e:
            logger.error(f"Failed to retrieve chat session {session_id}: {e}")
            return None

    def update_chat_session(self, session_id: str, session: ChatSession) -> bool:
        """Update an existing chat session"""
        try:
            session.updated_at = datetime.utcnow()
            # Exclude _id and any unset fields
            session_dict = session.model_dump(exclude_unset=True)

            result = self.db.chat_sessions.update_one(
                {"session_id": session_id},
                {"$set": session_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update chat session {session_id}: {e}")
            return False

    def add_message_to_session(self, session_id: str, message: ChatMessage) -> bool:
        """Add a message to a chat session"""
        try:
            message_dict = message.model_dump()

            result = self.db.chat_sessions.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message_dict},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to add message to session {session_id}: {e}")
            return False

    def add_component_to_session(self, session_id: str, component: GeneratedComponent) -> bool:
        """Add a generated component to a chat session"""
        try:
            component_dict = component.model_dump()

            result = self.db.chat_sessions.update_one(
                {"session_id": session_id},
                {
                    "$push": {"generated_components": component_dict},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to add component to session {session_id}: {e}")
            return False

    def get_user_chat_sessions(self, user_id: Optional[str] = None, limit: int = 20) -> List[ChatSession]:
        """Get chat sessions for a user (or all sessions if user_id is None)"""
        try:
            query = {"is_active": True}
            if user_id:
                query["user_id"] = user_id

            sessions_data = self.db.chat_sessions.find(query) \
                .sort("updated_at", -1) \
                .limit(limit)

            result = []
            for session_data in sessions_data:
                try:
                    # Clean all MongoDB objects
                    session_data = clean_for_json(session_data)

                    # Remove _id before creating the Pydantic model
                    if "_id" in session_data:
                        del session_data["_id"]

                    # Add defaults
                    session_data.setdefault("messages", [])
                    session_data.setdefault("generated_components", [])
                    session_data.setdefault("is_active", True)
                    session_data.setdefault("created_at", datetime.utcnow())
                    session_data.setdefault("updated_at", datetime.utcnow())

                    session = ChatSession(**session_data)
                    result.append(session)
                except Exception as e:
                    logger.error(f"Failed to process session {session_data.get('session_id', 'unknown')}: {e}")
                    continue

            return result
        except Exception as e:
            logger.error(f"Failed to retrieve chat sessions for user {user_id}: {e}")
            return []

    def delete_chat_session(self, session_id: str) -> bool:
        """Soft delete a chat session"""
        try:
            result = self.db.chat_sessions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to delete chat session {session_id}: {e}")
            return False

    def search_chat_sessions(self, search_term: str, user_id: Optional[str] = None, limit: int = 10) -> List[ChatSession]:
        """Search chat sessions by title or message content"""
        try:
            query = {
                "is_active": True,
                "$or": [
                    {"session_title": {"$regex": search_term, "$options": "i"}},
                    {"messages.content": {"$regex": search_term, "$options": "i"}}
                ]
            }

            if user_id:
                query["user_id"] = user_id

            sessions_data = self.db.chat_sessions.find(query) \
                .sort("updated_at", -1) \
                .limit(limit)

            result = []
            for session_data in sessions_data:
                # Clean and remove _id
                session_data = clean_for_json(session_data)
                if "_id" in session_data:
                    del session_data["_id"]
                result.append(ChatSession(**session_data))

            return result
        except Exception as e:
            logger.error(f"Failed to search chat sessions: {e}")
            return []

    def get_component_by_id(self, session_id: str, component_id: str) -> Optional[GeneratedComponent]:
        """Get a specific component from a session"""
        try:
            session_data = self.db.chat_sessions.find_one({"session_id": session_id})
            if session_data:
                for component_data in session_data.get("generated_components", []):
                    if component_data.get("component_id") == component_id:
                        return GeneratedComponent(**component_data)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve component {component_id} from session {session_id}: {e}")
            return None

    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def cleanup_null_id_documents(self):
        """Utility method to clean up documents with null _id"""
        try:
            # Find documents with null _id
            null_id_docs = list(self.db.chat_sessions.find({"_id": None}))

            if null_id_docs:
                logger.warning(f"Found {len(null_id_docs)} documents with null _id")

                # Delete documents with null _id
                result = self.db.chat_sessions.delete_many({"_id": None})
                logger.info(f"Deleted {result.deleted_count} documents with null _id")

                return result.deleted_count
            else:
                logger.info("No documents with null _id found")
                return 0

        except Exception as e:
            logger.error(f"Failed to cleanup null _id documents: {e}")
            return 0