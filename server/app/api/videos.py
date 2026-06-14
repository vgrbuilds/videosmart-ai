from fastapi import APIRouter, Depends, status, BackgroundTasks, UploadFile, File, Form, HTTPException
from typing import List, Optional
from app.core.security import get_current_user
from app.services.video_upload import video_upload_service
from app.services.video_query import video_query_service
from app.schemas.video import VideoOut, VideoListItem

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("/upload", response_model=VideoOut, status_code=status.HTTP_202_ACCEPTED)
async def upload_video(
    background_tasks: BackgroundTasks,
    youtube_url: Optional[str] = Form(None),
    language: str = Form("english"),
    file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    if not file and not youtube_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must provide either a video file upload or a youtube_url."
        )
        
    return await video_upload_service.upload(
        background_tasks=background_tasks,
        user_id=current_user["id"],
        youtube_url=youtube_url,
        language=language,
        file=file
    )

@router.get("/", response_model=List[VideoListItem])
async def list_videos(current_user: dict = Depends(get_current_user)):
    return await video_query_service.list_user_videos(current_user["id"])

@router.get("/{video_id}", response_model=VideoOut)
async def get_video(video_id: str, current_user: dict = Depends(get_current_user)):
    return await video_query_service.get_video(video_id, current_user["id"])

@router.delete("/{video_id}", status_code=status.HTTP_200_OK)
async def delete_video(video_id: str, current_user: dict = Depends(get_current_user)):
    return await video_query_service.delete_video(video_id, current_user["id"])
