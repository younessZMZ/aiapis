import os
import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi import UploadFile, File, Depends, HTTPException, APIRouter
from sqlmodel import Session
from starlette.responses import FileResponse

from logger.starter import logger
from utils.transcribe import save_audio_to_folder, transcribe_audio
from database import get_session, Task, Status

router = APIRouter(prefix="/transcribe")

executor = ThreadPoolExecutor(max_workers=2)


@router.post("/upload/")
async def upload(file: UploadFile = File(...), language_sign: str = "EN", session: Session = Depends(get_session)):
    logger.info("Starting uploading the audio file")

    if file.content_type not in ["audio/wav", "audio/x-wav", "audio/wave"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only .wav files are accepted.")

    task_id = str(uuid.uuid4())
    await save_audio_to_folder(file, task_id)
    logger.info("file uploaded is saved to the folder.")
    task = Task(id=task_id, status=Status.IN_PROGRESS)
    session.add(task)
    session.commit()
    logger.info("passing the audio to background task to be processed.")
    executor.submit(transcribe_audio, language_sign, task_id)
    logger.info("Returning the message of upload endpoint.")
    return {"message": "File uploaded successfully, processing started.", "task_id": task_id}


@router.get("/status/{task_id}")
def get_status(task_id: str, session: Session = Depends(get_session)):
    """
    Endpoint to check the status of a transcription task.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump()


@router.get("/download/{task_id}")
def download_transcription(task_id: str, session: Session = Depends(get_session)):
    """
    Endpoint to download the transcription file for a given task.
    """
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != Status.DONE:
        raise HTTPException(status_code=404, detail="Transcription not available or not completed")

    file_path = task.transcript_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Transcription file does not exist")

    return FileResponse(path=file_path, filename=os.path.basename(file_path), media_type="text/plain")
