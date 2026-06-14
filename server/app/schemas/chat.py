from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class MessageSchema(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatQuery(BaseModel):
    question: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    answer: str
    conversation_id: str

class ConversationOut(BaseModel):
    id: str
    video_id: str
    user_id: str
    messages: List[MessageSchema] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
