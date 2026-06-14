from fastapi import HTTPException, status
from bson import ObjectId
from datetime import datetime
import logging
from app.db.mongodb import get_conversations_collection, get_videos_collection
from app.core.rag_engine import ask_question

logger = logging.getLogger(__name__)

class ChatQueryService:
    @staticmethod
    async def query(video_id: str, question: str, user_id: str) -> dict:
        if not ObjectId.is_valid(video_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid video ID format.")
            
        video = await get_videos_collection().find_one({"_id": ObjectId(video_id), "user_id": ObjectId(user_id)})
        if not video:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")
            
        if video["status"] == "processing":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Video is still processing. Please wait until analysis completes before chatting."
            )
        elif video["status"] == "failed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Video analysis failed, cannot initiate chat."
            )
            
        conversations_collection = get_conversations_collection()
        conversation = await conversations_collection.find_one({
            "video_id": ObjectId(video_id), "user_id": ObjectId(user_id)
        })
        
        if not conversation:
            conversation_id = ObjectId()
            conversation = {
                "_id": conversation_id,
                "video_id": ObjectId(video_id),
                "user_id": ObjectId(user_id),
                "messages": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await conversations_collection.insert_one(conversation)
        else:
            conversation_id = conversation["_id"]
            
        try:
            chat_history = conversation.get("messages", [])
            history_list = [{"role": msg["role"], "content": msg["content"]} for msg in chat_history]
            answer = await ask_question(video_id, history_list, question)
        except Exception as e:
            logger.error(f"Error during RAG execution: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while answering your question: {str(e)}"
            )
            
        now = datetime.utcnow()
        user_msg = {"role": "user", "content": question, "timestamp": now}
        assistant_msg = {"role": "assistant", "content": answer, "timestamp": now}
        
        await conversations_collection.update_one(
            {"_id": conversation_id},
            {
                "$push": {"messages": {"$each": [user_msg, assistant_msg]}},
                "$set": {"updated_at": now}
            }
        )
        return {"answer": answer, "conversation_id": str(conversation_id)}

chat_query_service = ChatQueryService()
