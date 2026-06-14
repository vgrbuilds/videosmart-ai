from fastapi import HTTPException, status
from bson import ObjectId
from datetime import datetime
from app.db.mongodb import get_conversations_collection

class ChatHistoryService:
    @staticmethod
    async def get_history(video_id: str, user_id: str) -> dict:
        if not ObjectId.is_valid(video_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video ID format.")
            
        conversations_collection = get_conversations_collection()
        conversation = await conversations_collection.find_one({
            "video_id": ObjectId(video_id),
            "user_id": ObjectId(user_id)
        })
        
        if not conversation:
            return {
                "id": "",
                "video_id": video_id,
                "user_id": user_id,
                "messages": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
        return {
            "id": str(conversation["_id"]),
            "video_id": str(conversation["video_id"]),
            "user_id": str(conversation["user_id"]),
            "messages": [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg.get("timestamp", datetime.utcnow())
                }
                for msg in conversation.get("messages", [])
            ],
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"]
        }

    @staticmethod
    async def clear_history(video_id: str, user_id: str) -> dict:
        if not ObjectId.is_valid(video_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video ID format.")
            
        conversations_collection = get_conversations_collection()
        await conversations_collection.update_one(
            {
                "video_id": ObjectId(video_id),
                "user_id": ObjectId(user_id)
            },
            {
                "$set": {
                    "messages": [],
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return {"detail": "Chat history cleared successfully."}

chat_history_service = ChatHistoryService()
