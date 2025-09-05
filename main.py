import json
from logging import exception

import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from google import genai
from pathlib import Path
import aiofiles

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed audio formats
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/ogg",
    "audio/flac",
    "audio/aac",
    "audio/mp4",
    "audio/x-m4a"
}

prompt = """
You are an expert public speaking coach.
I will give you an audio file of someone speaking.
Your task is to analyze the speech and return actionable feedback.

Focus on:
- Clarity
- Pronunciation
- Pacing
- Pauses
- Filler words
- Overall delivery

Rules:
- Output must be valid JSON only.
- No explanations outside the JSON.
- Each feedback item must have: "category", "issue", and "suggestion".

Example format:
{
  "feedback": [
    {
      "category": "Pauses",
      "issue": "The speaker rushed through ideas without pausing.",
      "suggestion": "Take a short pause between sentences."
    },
    {
      "category": "Filler Words",
      "issue": "Too many 'um' and 'uh'.",
      "suggestion": "Practice removing filler words."
    }
  ]
}
"""

MAX_FILE_SIZE = 10 * 1024 * 1024

app = FastAPI()
client =  genai.Client()

@app.get("/")
def home():
    return  {"hello": "world"}

@app.post("/feedback/")
async def upload_audio(audio_file: UploadFile = File(...)):
    if audio_file.content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {",".join(ALLOWED_AUDIO_TYPES)}"
        )

    if audio_file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE/ 1024/ 1024}MB"

        )

    file_extension =  Path(audio_file.filename).suffix
    unique_filename = f"{hash(audio_file)}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    async with aiofiles.open(file_path, "wb") as f:
        content = await  audio_file.read()
        await f.write(content)

    try:
        my_file = client.files.upload(file=file_path)
        response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt, my_file])

        data = json.loads( response.text.replace("```json", "").replace("```", ""))

        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server Error:{e}"
        )


if __name__ == "__main__":
    uvicorn.run(app)