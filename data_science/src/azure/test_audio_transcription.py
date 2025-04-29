import os
import requests
from moviepy.editor import VideoFileClip
from utils import load_env_variables

# Load environment variables
load_env_variables()

# === CONFIG ===
VIDEO_PATH = VIDEO_PATH = os.path.join("../../../dataset_local", "exit1_20250403093329.avi")
AUDIO_PATH = "extracted_audio.wav"

# Whisper specific config
AZURE_WHISPER_ENDPOINT = os.getenv("AZURE_WHISPER_ENDPOINT")
AZURE_WHISPER_API_KEY = os.getenv("AZURE_WHISPER_API_KEY")
AZURE_WHISPER_DEPLOYMENT = os.getenv("AZURE_WHISPER_DEPLOYMENT")

# === STEP 1: Extract audio from video ===
def extract_audio(video_path: str, audio_output_path: str):
    print(f"Extracting audio from {video_path}...")
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_output_path, codec="pcm_s16le")
    print(f"Audio saved to {audio_output_path}")

# === STEP 2: Send audio to Whisper ===
def transcribe_audio(audio_path: str):
    url = f"{AZURE_WHISPER_ENDPOINT }/openai/deployments/{AZURE_WHISPER_DEPLOYMENT }/audio/transcriptions"
    headers = {
        "api-key": AZURE_WHISPER_API_KEY ,
    }
    params = {
        "api-version": "2024-04-01-preview"
    }
    files = {
        "file": (audio_path, open(audio_path, "rb"), "audio/wav")
    }

    print("Sending audio to Azure Whisper...")
    response = requests.post(url, headers=headers, params=params, files=files)

    if response.ok:
        print("Transcription Result:")
        print(response.json()["text"])
    else:
        print("Error:")
        print(response.status_code, response.text)

# === MAIN ===
if __name__ == "__main__":
    extract_audio(VIDEO_PATH, AUDIO_PATH)
    transcribe_audio(AUDIO_PATH)
