import yt_dlp
import os
import base64

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
    
    # Handle optional cookies from env to bypass botguard
    cookie_content = os.environ.get("YOUTUBE_COOKIES")
    if cookie_content:
        try:
            # Try to decode base64 if it is encoded
            decoded = base64.b64decode(cookie_content.encode("utf-8")).decode("utf-8")
            if "# Netscape" in decoded or "youtube.com" in decoded:
                cookie_content = decoded
        except Exception:
            pass
            
        cookie_file_path = os.path.join(DOWNLOAD_DIR, "cookies.txt")
        with open(cookie_file_path, "w", encoding="utf-8") as f:
            f.write(cookie_content)
        ydl_opts["cookiefile"] = cookie_file_path
    else:
        # If no cookies, emulate iOS player client to bypass bot checks
        ydl_opts["extractor_args"] = {
            "youtube": {
                "player_client": ["ios", "default"]
            }
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
                "YouTube download blocked: Render's server IP is flagged as a bot. "
                "To fix this, please add your YouTube cookies in the Render Environment settings "
                "under YOUTUBE_COOKIES, or upload the file directly using 'Local File Upload'."
            )
        raise ValueError(f"YouTube download failed: {err_msg}")
