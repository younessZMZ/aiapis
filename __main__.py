import os

from dotenv import load_dotenv
from fastapi import FastAPI

from database import create_db_and_tables
from api.transcribe import router

app = FastAPI(title="NLP Applications")
app.include_router(router=router, tags=["Transcription"])

# Load environment variables from .env file
load_dotenv()

# Directory for storing audio files and transcriptions
os.makedirs("audio_files", exist_ok=True)
os.makedirs("transcripts", exist_ok=True)


@app.on_event("startup")
def on_startup():
    """Create all models if not already created in database when the app is starting."""
    create_db_and_tables()


@app.get("/")
def hello():
    return "The API is up!"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)
