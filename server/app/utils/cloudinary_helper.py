import cloudinary
import cloudinary.uploader
import os
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Cloudinary if credentials are provided
if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    logger.info("Cloudinary configured successfully.")
else:
    logger.warning("Cloudinary credentials are not fully set. File uploads will fail.")

async def upload_video_to_cloudinary(file_path: str) -> Dict[str, Any]:
    """
    Uploads a video to Cloudinary.
    Uses upload_large to support files > 10MB.
    Returns a dict with 'secure_url' and 'public_id'.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found at path: {file_path}")
        
    logger.info(f"Uploading file {file_path} to Cloudinary...")
    
    # Run in a separate thread if needed, but upload_large is synchronous
    # Since we call this from background tasks, running synchronously is fine.
    response = cloudinary.uploader.upload_large(
        file_path,
        resource_type="video",
        folder="videosmart_ai",
        chunk_size=6000000 # 6MB chunks
    )
    
    logger.info(f"Cloudinary upload complete. Public ID: {response.get('public_id')}")
    return {
        "secure_url": response.get("secure_url"),
        "public_id": response.get("public_id")
    }

async def delete_video_from_cloudinary(public_id: str) -> Optional[Dict[str, Any]]:
    """
    Deletes a video from Cloudinary using its public ID.
    """
    if not public_id:
        return None
        
    logger.info(f"Deleting video {public_id} from Cloudinary...")
    response = cloudinary.uploader.destroy(
        public_id,
        resource_type="video"
    )
    return response
