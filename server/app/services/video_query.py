from fastapi import HTTPException, status
from typing import List
from bson import ObjectId
from app.db.mongodb import get_videos_collection, get_conversations_collection
from app.core.vector_store import delete_vector_store_chunks
from app.utils.cloudinary_helper import delete_video_from_cloudinary
import logging

logger = logging.getLogger(__name__)

class VideoQueryService:
    @staticmethod
    async def list_user_videos(user_id: str) -> List[dict]:
        videos_collection = get_videos_collection()
        cursor = videos_collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1)
        videos = []
        async for doc in cursor:
            videos.append({
                "id": str(doc["_id"]),
                "title": doc.get("title"),
                "url": doc.get("url"),
                "status": doc.get("status"),
                "language": doc.get("language"),
                "created_at": doc.get("created_at"),
                "summary": doc.get("summary")
            })
        return videos

    @staticmethod
    async def get_video(video_id: str, user_id: str) -> dict:
        if not ObjectId.is_valid(video_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video ID format.")
        video = await get_videos_collection().find_one({
            "_id": ObjectId(video_id),
            "user_id": ObjectId(user_id)
        })
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")
        return {
            "id": str(video["_id"]),
            "title": video.get("title"),
            "url": video.get("url"),
            "cloudinary_public_id": video.get("cloudinary_public_id"),
            "status": video.get("status"),
            "language": video.get("language"),
            "created_at": video.get("created_at"),
            "transcript": video.get("transcript"),
            "summary": video.get("summary"),
            "action_items": video.get("action_items"),
            "key_decisions": video.get("key_decisions"),
            "open_questions": video.get("open_questions"),
            "error_message": video.get("error_message")
        }

    @staticmethod
    async def delete_video(video_id: str, user_id: str) -> dict:
        if not ObjectId.is_valid(video_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video ID format.")
        
        videos_collection = get_videos_collection()
        video = await videos_collection.find_one({"_id": ObjectId(video_id), "user_id": ObjectId(user_id)})
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")
            
        await delete_vector_store_chunks(video_id)
        if video.get("cloudinary_public_id"):
            try:
                await delete_video_from_cloudinary(video["cloudinary_public_id"])
            except Exception as e:
                logger.error(f"Failed to delete Cloudinary asset: {e}")
                
        await get_conversations_collection().delete_many({"video_id": ObjectId(video_id), "user_id": ObjectId(user_id)})
        await videos_collection.delete_one({"_id": ObjectId(video_id)})
        return {"detail": "Video and all associated data deleted successfully."}

video_query_service = VideoQueryService()
