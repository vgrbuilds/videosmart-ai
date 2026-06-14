from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class VideoCreate(BaseModel):
    youtube_url: Optional[str] = Field(None, description="Optional YouTube URL to process.")
    language: str = Field("english", description="Language: english or hinglish")

class VideoOut(BaseModel):
    id: str
    title: Optional[str] = None
    url: Optional[str] = None
    cloudinary_public_id: Optional[str] = None
    status: str # processing, completed, failed
    language: str
    created_at: datetime
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[str] = None
    key_decisions: Optional[str] = None
    open_questions: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class VideoListItem(BaseModel):
    id: str
    title: Optional[str] = None
    url: Optional[str] = None
    status: str
    language: str
    created_at: datetime
    summary: Optional[str] = None

    class Config:
        from_attributes = True
