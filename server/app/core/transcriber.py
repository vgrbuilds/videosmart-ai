from google import genai
import os
import time
from app.core.config import settings

# Initialize the new Google GenAI Client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def transcribe_chunk_gemini(chunk_path: str) -> str:
    if not os.path.exists(chunk_path):
        raise FileNotFoundError(f"Chunk file not found: {chunk_path}")
        
    print(f"Uploading {os.path.basename(chunk_path)} to Gemini...")
    audio_file = client.files.upload(file=chunk_path)
    
    # Wait for processing if the state is PROCESSING
    while str(audio_file.state) == "PROCESSING" or getattr(audio_file.state, "name", "") == "PROCESSING":
        time.sleep(1)
        audio_file = client.files.get(name=audio_file.name)
        
    if str(audio_file.state) == "FAILED" or getattr(audio_file.state, "name", "") == "FAILED":
        raise RuntimeError(f"Gemini transcription failed for: {chunk_path}")
        
    prompt = "Transcribe this audio file accurately. Return only the transcription text, nothing else."
    response = client.models.generate_content(
        model=settings.gemini_model_to_use,
        contents=[audio_file, prompt]
    )
    
    # Clean up the file from the Gemini cloud
    client.files.delete(name=audio_file.name)
    return response.text.strip()

def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    return transcribe_chunk_gemini(chunk_path)

def transcribe_all(chunks: list, language: str = "english") -> str:
    full_transcript = ""
    print("Using Gemini for STT.")
    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")
        text = transcribe_chunk(chunk, language=language)
        full_transcript += text + " "
    return full_transcript.strip()