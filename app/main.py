import cv2
import os

# Add FFmpeg to PATH for whisper and other tools
ffmpeg_dir = r"C:\Users\Tilak Rajora\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
os.environ['PATH'] = ffmpeg_dir + ';' + os.environ.get('PATH', '')

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import shutil
import yt_dlp
import uuid
from pydantic import BaseModel

from .clipper import generate_clips

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.abspath(".")), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    try:
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(html_content)
    except Exception as e:
        return HTMLResponse(f"<h1>Error</h1><p>{str(e)}</p><p>CWD: {os.getcwd()}</p>", status_code=500)

class VideoRequest(BaseModel):
    url: str

def download_video(url: str, output_path: str):
    FFMPEG_PATH = r"C:\Users\Tilak Rajora\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin\ffmpeg.exe"
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'best',  # Best quality available
        'ffmpeg_location': FFMPEG_PATH
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

@app.post("/process/")
async def process_video(request: VideoRequest):
    try:
        print(f"Processing URL: {request.url}")
        # Generate unique filename
        video_id = str(uuid.uuid4())[:8]
        video_filename = f"video_{video_id}.mp4"
        video_path = os.path.join(UPLOAD_DIR, video_filename)
        
        print(f"Downloading to: {video_path}")
        # Download video
        download_video(request.url, video_path)
        
        if not os.path.exists(video_path):
            raise Exception(f"Video file not found after download: {video_path}")
        
        print("Download complete")
        
        # Get video duration using OpenCV
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps if fps > 0 else 0
        cap.release()
        print(f"Video duration: {duration} seconds")
        
        # Skip scene detection for time-based clips
        # print("Starting scene detection")
        # scenes = detect_scenes(video_path)
        # print(f"Found {len(scenes)} scenes")
        scenes = []

        # Skip transcription for now
        # print("Starting transcription")
        # text = transcribe(video_path)
        # print(f"Transcription length: {len(text)}")
        text = ""

        print("Picking highlights")
        # Step 3: Highlight selection - create 20-second clips
        clip_length = 20  # seconds
        highlights = []
        for start in range(0, int(duration), clip_length):
            end = min(start + clip_length, duration)
            if end - start >= 5:  # minimum 5 seconds
                highlights.append({"start": float(start), "end": float(end)})
        print(f"Created {len(highlights)} highlight clips")

        print("Generating clips")
        # Step 4: Clip generation
        clips = generate_clips(video_path, highlights)
        print(f"Generated {len(clips)} clips")

        return {
            "video_filename": video_filename,
            "scenes": scenes,
            "transcript": text[:1000],  # More characters
            "highlights": highlights,
            "clips": clips
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))