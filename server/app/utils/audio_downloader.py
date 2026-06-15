import os
import static_ffmpeg
from pytubefix import YouTube
from pydub import AudioSegment

static_ffmpeg.add_paths()

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url: str) -> str:
    try:
        yt = YouTube(url, client='WEB')
        audio_stream = yt.streams.get_audio_only()
        if not audio_stream:
            raise ValueError("No audio stream found.")
        
        downloaded_path = audio_stream.download(output_path=DOWNLOAD_DIR)
        
        # Convert to WAV (channels=1, frame_rate=16000)
        wav_path = os.path.splitext(downloaded_path)[0] + ".wav"
        audio = AudioSegment.from_file(downloaded_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(wav_path, format="wav")
        
        # Clean up raw download
        if os.path.exists(downloaded_path) and downloaded_path != wav_path:
            os.remove(downloaded_path)
            
        return wav_path
    except Exception as e:
        raise ValueError(f"YouTube download failed: {str(e)}")
