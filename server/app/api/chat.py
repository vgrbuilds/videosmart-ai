from fastapi import APIRouter, Depends, status
from app.core.security import get_current_user
from app.services.chat_query import chat_query_service
from app.services.chat_history import chat_history_service
from app.schemas.chat import ChatQuery, ChatResponse, ConversationOut

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/query/{video_id}", response_model=ChatResponse)
async def query_video(
    video_id: str,
    query: ChatQuery,
    current_user: dict = Depends(get_current_user)
):
    return await chat_query_service.query(video_id, query.question, current_user["id"])

@router.get("/history/{video_id}", response_model=ConversationOut)
async def get_chat_history(video_id: str, current_user: dict = Depends(get_current_user)):
    return await chat_history_service.get_history(video_id, current_user["id"])

@router.delete("/clear/{video_id}", status_code=status.HTTP_200_OK)
async def clear_chat_history(video_id: str, current_user: dict = Depends(get_current_user)):
    return await chat_history_service.clear_history(video_id, current_user["id"])
