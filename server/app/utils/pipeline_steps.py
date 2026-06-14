from app.core.transcriber import transcribe_all
from app.core.summarizer import summarize, generate_title
from app.core.extractor import extract_action_items, extract_key_decisions, extract_questions
from app.core.vector_store import build_vector_store

def run_transcription(chunks: list, language: str) -> str:
    return transcribe_all(chunks, language)

def run_analysis(transcript: str) -> dict:
    title = generate_title(transcript)
    summary = summarize(transcript)
    return {"title": title, "summary": summary}

def run_extraction(transcript: str) -> dict:
    return {
        "action_items": extract_action_items(transcript),
        "key_decisions": extract_key_decisions(transcript),
        "open_questions": extract_questions(transcript)
    }

def run_indexing(transcript: str, video_id: str):
    build_vector_store(transcript, video_id)
