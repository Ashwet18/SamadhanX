"""
File storage service for handling media uploads.

Provides abstraction over storage backends (local, S3, GCS).
"""

import os
import uuid
from pathlib import Path
from typing import BinaryIO, Tuple
from fastapi import UploadFile, HTTPException, status
import mimetypes

from app.core.config import settings


class StorageService:
    """Service for file storage operations."""
    
    # Allowed file types and size limits
    ALLOWED_TYPES = {
        "IMAGE": {
            "mime_types": ["image/jpeg", "image/png", "image/webp"],
            "extensions": [".jpg", ".jpeg", ".png", ".webp"],
            "max_size": 10 * 1024 * 1024  # 10 MB
        },
        "VIDEO": {
            "mime_types": ["video/mp4", "video/webm"],
            "extensions": [".mp4", ".webm"],
            "max_size": 50 * 1024 * 1024  # 50 MB
        },
        "AUDIO": {
            "mime_types": ["audio/mpeg", "audio/wav", "audio/ogg"],
            "extensions": [".mp3", ".wav", ".ogg"],
            "max_size": 20 * 1024 * 1024  # 20 MB
        },
        "DOCUMENT": {
            "mime_types": ["application/pdf"],
            "extensions": [".pdf"],
            "max_size": 10 * 1024 * 1024  # 10 MB
        }
    }
    
    def __init__(self):
        """Initialize storage service."""
        self.storage_backend = settings.STORAGE_BACKEND
        
        # Setup local storage directory
        if self.storage_backend == "local":
            self.upload_dir = Path("uploads")
            self.upload_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            (self.upload_dir / "challenges").mkdir(exist_ok=True)
    
    def validate_file(self, file: UploadFile) -> Tuple[str, str]:
        """
        Validate uploaded file.
        
        Args:
            file: Uploaded file
            
        Returns:
            Tuple of (media_type, mime_type)
            
        Raises:
            HTTPException: If file is invalid
        """
        # Check if file has content
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Get file extension
        file_ext = Path(file.filename).suffix.lower()
        
        # Determine media type from MIME type and extension
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        
        if not content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not determine file type"
            )
        
        # Find matching media type
        media_type = None
        for mtype, config in self.ALLOWED_TYPES.items():
            if content_type in config["mime_types"] and file_ext in config["extensions"]:
                media_type = mtype
                break
        
        if not media_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_TYPES.keys())}"
            )
        
        return media_type, content_type
    
    async def upload_file(
        self,
        file: UploadFile,
        folder: str = "challenges"
    ) -> Tuple[str, str, str, int]:
        """
        Upload file to storage.
        
        Args:
            file: File to upload
            folder: Folder name in storage
            
        Returns:
            Tuple of (file_url, original_filename, mime_type, file_size)
            
        Raises:
            HTTPException: If upload fails or file is invalid
        """
        # Validate file
        media_type, mime_type = self.validate_file(file)
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Check file size
        max_size = self.ALLOWED_TYPES[media_type]["max_size"]
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {max_size / (1024 * 1024):.1f} MB"
            )
        
        # Generate safe filename
        file_ext = Path(file.filename).suffix.lower()
        safe_filename = f"{uuid.uuid4()}{file_ext}"
        
        if self.storage_backend == "local":
            # Save to local filesystem
            folder_path = self.upload_dir / folder
            folder_path.mkdir(exist_ok=True)
            
            file_path = folder_path / safe_filename
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Return relative URL
            file_url = f"/uploads/{folder}/{safe_filename}"
        
        elif self.storage_backend == "s3":
            # TODO: Implement S3 upload
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="S3 storage not yet implemented"
            )
        
        elif self.storage_backend == "gcs":
            # TODO: Implement GCS upload
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="GCS storage not yet implemented"
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unknown storage backend: {self.storage_backend}"
            )
        
        return file_url, file.filename, mime_type, file_size
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            file_url: URL/path of file to delete
            
        Returns:
            True if deleted, False if not found
        """
        if self.storage_backend == "local":
            # Extract path from URL
            if file_url.startswith("/uploads/"):
                rel_path = file_url[len("/uploads/"):]
                file_path = self.upload_dir / rel_path
                
                if file_path.exists():
                    file_path.unlink()
                    return True
                return False
        
        elif self.storage_backend == "s3":
            # TODO: Implement S3 delete
            raise NotImplementedError("S3 storage not yet implemented")
        
        elif self.storage_backend == "gcs":
            # TODO: Implement GCS delete
            raise NotImplementedError("GCS storage not yet implemented")
        
        return False
    
    def get_media_type_from_mime(self, mime_type: str) -> str:
        """
        Get media type enum from MIME type.
        
        Args:
            mime_type: MIME type string
            
        Returns:
            Media type (IMAGE, VIDEO, AUDIO, DOCUMENT)
        """
        for mtype, config in self.ALLOWED_TYPES.items():
            if mime_type in config["mime_types"]:
                return mtype
        
        return "DOCUMENT"  # Default


# Global storage service instance
storage_service = StorageService()
