from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import component_routes, project_routes, eds_block_routes, eds_routes, test_routes
import os
from app.routes.component_routes import router as component_router
from app.routes.project_routes import router as project_router
from app.routes.eds_routes import router as eds_router
from app.routes.test_routes import router as test_router
from app.chatStorage.chat_model import ChatStorage
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


app = FastAPI(title="AEM Component Generator API.", version="1.0.0")

# Mount static directory for serving uploaded images
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add CORS middleware with explicit configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins
        "http://localhost:3000",
        "http://localhost:3002", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3002"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(component_router, prefix="/api/component", tags=["components"])
#app.include_router(project_router, prefix="/api/project", tags=["project"])
app.include_router(project_router, prefix="/api/project", tags=["projects"])
app.include_router(eds_block_routes.router, prefix="/api/component", tags=["edsblocks"])
app.include_router(eds_router)
app.include_router(test_router, prefix="/api/test", tags=["test"])

@app.get("/")
async def root():
    return {"message": "AEM Component Generator API"}

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle preflight OPTIONS requests for CORS"""
    return {"message": "OK"}

@app.get("/health")
async def health_check():
    """Health check endpoint that includes MongoDB connectivity"""
    try:
        # Test MongoDB connection
        chat_storage = ChatStorage()
        mongodb_status = "connected" if chat_storage.is_connected() else "disconnected"
        
        return {
            "status": "healthy",
            "service": "AEM Component Generator API",
            "version": "1.0.0",
            "mongodb": mongodb_status,
            "timestamp": "2025-08-04T07:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "AEM Component Generator API",
            "version": "1.0.0",
            "mongodb": "error",
            "error": str(e),
            "timestamp": "2025-08-04T07:00:00Z"
        }