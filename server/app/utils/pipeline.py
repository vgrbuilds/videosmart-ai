import os
import logging
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import get_videos_collection
from app.utils.audio_processor import process_input
from app.utils.cloudinary_helper import upload_video_to_cloudinary
from app.utils.pipeline_steps import run_transcription, run_analysis, run_extraction, run_indexing

logger = logging.getLogger(__name__)

async def process_video_pipeline(video_id: str, source: str, language: str, is_upload: bool = False):
    videos_collection = get_videos_collection()
    temp_files = []
    try:
        if is_upload:
            temp_files.append(source)
            cloud_res = await upload_video_to_cloudinary(source)
            await videos_collection.update_one(
                {"_id": ObjectId(video_id)},
                {"$set": {"url": cloud_res["secure_url"], "cloudinary_public_id": cloud_res["public_id"]}}
            )
        
        chunks = process_input(source)
        if not chunks:
            raise ValueError("No audio chunks were created.")
        temp_files.extend(chunks)
        
        base_wav = chunks[0].split("_chunk_")[0]
        if os.path.exists(base_wav) and base_wav not in temp_files:
            temp_files.append(base_wav)
            
        transcript = run_transcription(chunks, language)
        analysis = run_analysis(transcript)
        ext = run_extraction(transcript)
        run_indexing(transcript, video_id)
        
        await videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {
                "status": "completed",
                "title": analysis["title"],
                "transcript": transcript,
                "summary": analysis["summary"],
                "action_items": ext["action_items"],
                "key_decisions": ext["key_decisions"],
                "open_questions": ext["open_questions"],
                "updated_at": datetime.utcnow()
            }}
        )
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        await videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {"status": "failed", "error_message": str(e), "updated_at": datetime.utcnow()}}
        )
    finally:
        for f in temp_files:
            if os.path.exists(f):
                os.remove(f)
