import yt_dlp
import os

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
        return filename
    except Exception as e:
        err_msg = str(e)
        if "confirm" in err_msg and "bot" in err_msg:
            raise ValueError(
                "YouTube download blocked: Render's server IP is flagged as a bot by YouTube. "
                "Please download the audio/video locally and upload it "
                "using the 'Local File Upload' tab instead."
            )
        raise ValueError(f"YouTube download failed: {err_msg}")
