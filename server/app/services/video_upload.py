from fastapi import BackgroundTasks, UploadFile, HTTPException, status
from typing import Optional
import uuid
import os
from datetime import datetime
from bson import ObjectId
from app.core.config import settings
from app.db.mongodb import get_videos_collection
from app.utils.pipeline import process_video_pipeline

class VideoUploadService:
    @staticmethod
    async def upload(
        background_tasks: BackgroundTasks,
        user_id: str,
        youtube_url: Optional[str] = None,
        language: str = "english",
        file: Optional[UploadFile] = None
    ) -> dict:
        videos_collection = get_videos_collection()
        video_id = ObjectId()
        created_at = datetime.utcnow()
        
        source = youtube_url
        if file:
            os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
            ext = os.path.splitext(file.filename)[1] or ".mp4"
            source = os.path.join(settings.DOWNLOAD_DIR, f"{uuid.uuid4()}{ext}")
            try:
                with open(source, "wb") as f:
                    while chunk := await file.read(1024 * 1024):
                        f.write(chunk)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to write uploaded file to disk: {str(e)}"
                )
                
        video_doc = {
            "_id": video_id,
            "user_id": ObjectId(user_id),
            "title": file.filename if file else "YouTube Video Analysis",
            "url": None if file else youtube_url,
            "cloudinary_public_id": None,
            "status": "processing",
            "language": language.lower(),
            "created_at": created_at,
            "updated_at": created_at
        }
        await videos_collection.insert_one(video_doc)
        
        background_tasks.add_task(
            process_video_pipeline,
            video_id=str(video_id),
            source=source,
            language=language.lower(),
            is_upload=bool(file)
        )
        return {
            "id": str(video_id),
            "title": video_doc["title"],
            "url": video_doc["url"],
            "status": video_doc["status"],
            "language": video_doc["language"],
            "created_at": video_doc["created_at"]
        }

video_upload_service = VideoUploadService()
