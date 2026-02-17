"""
Image upload and storage service
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta
from fastapi import UploadFile, HTTPException
from app.utils.helper_utils import HelperUtils

logger = HelperUtils.setup_logger("image_service")


class ImageService:
    """Service for handling image uploads and storage"""
    
    # Allowed image types
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.svg', '.webp'}
    ALLOWED_MIME_TYPES = {
        'image/png', 
        'image/jpeg', 
        'image/jpg', 
        'image/svg+xml',
        'image/webp'
    }
    
    # Default max size: 10MB
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    def __init__(self, upload_dir: str = "./uploads/images"):
        """Initialize image service with upload directory"""
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Image service initialized with upload dir: {self.upload_dir}")
    
    def validate_image(self, file: UploadFile) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded image file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Invalid file type. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        # Check MIME type
        if file.content_type not in self.ALLOWED_MIME_TYPES:
            return False, f"Invalid MIME type: {file.content_type}"
        
        return True, None
    
    async def save_upload(self, file: UploadFile) -> dict:
        """
        Save uploaded file to disk
        
        Returns:
            Dict with file info: {imageId, imageUrl, fileName, fileSize, mimeType}
        """
        try:
            # Validate file
            is_valid, error_msg = self.validate_image(file)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
            
            # Generate unique ID and filename
            image_id = str(uuid.uuid4())
            file_ext = Path(file.filename).suffix.lower()
            safe_filename = f"{image_id}{file_ext}"
            file_path = self.upload_dir / safe_filename
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Check file size
            if file_size > self.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File too large. Max size: {self.MAX_FILE_SIZE / (1024*1024)}MB"
                )
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(content)
            
            logger.info(f"Saved image: {safe_filename} ({file_size} bytes)")
            
            # Return file info
            return {
                "imageId": image_id,
                "imageUrl": str(file_path),  # Absolute path for now
                "fileName": file.filename,
                "fileSize": file_size,
                "mimeType": file.content_type
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error saving upload: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")
    
    def get_image_path(self, image_id: str) -> Optional[Path]:
        """Get path to uploaded image by ID"""
        for ext in self.ALLOWED_EXTENSIONS:
            file_path = self.upload_dir / f"{image_id}{ext}"
            if file_path.exists():
                return file_path
        return None
    
    def delete_image(self, image_id: str) -> bool:
        """Delete uploaded image by ID"""
        try:
            file_path = self.get_image_path(image_id)
            if file_path and file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted image: {image_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting image {image_id}: {str(e)}")
            return False
    
    def cleanup_old_images(self, days: int = 7):
        """Delete images older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            for file_path in self.upload_dir.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old images")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return 0
