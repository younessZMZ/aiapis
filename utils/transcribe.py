from collections import deque

from fastapi import HTTPException
from tafrigh import Config, TranscriptType, farrigh

from logger.starter import logger
from database import get_session, Task, Status, LANGUAGE_API_KEYS
from exceptions import UnexpectedException


async def save_audio_to_folder(file, task_id):
    """Save the uploaded audio file."""
    file_path = f"audio_files/{task_id}.wav"
    with open(file_path, "wb") as f:
        f.write(await file.read())


def is_wav_file(file_path):
    """Check if the file provided is a .wav file"""
    try:
        with open(file_path, "rb") as file:
            return file.read(4) == b"RIFF"
    except IOError:
        return False


def transcribe_audio(language_sign, task_id):
    """Transcribe the audio file uploaded."""
    logger.info("Starting transcription for task_id: %s", task_id)
    wit_api_key = LANGUAGE_API_KEYS.get(language_sign.upper())
    if not wit_api_key:
        logger.error("API key not found for language: %s", language_sign)
        update_task_status(task_id, Status.ERROR, message=f"API key not found for language: {language_sign}")
        raise HTTPException(status_code=400, detail=f"API key not found for language: {language_sign}")

    config = Config(
        urls_or_paths=[f"audio_files/{task_id}.wav"],
        skip_if_output_exist=False,
        playlist_items="",
        verbose=False,
        model_name_or_path="",
        task="",
        language="",
        use_faster_whisper=False,
        beam_size=0,
        ct2_compute_type="",
        wit_client_access_tokens=[wit_api_key],
        max_cutting_duration=5,
        min_words_per_segment=1,
        save_files_before_compact=False,
        save_yt_dlp_responses=False,
        output_sample=0,
        output_formats=[TranscriptType.TXT],
        output_dir="transcripts",
    )

    try:
        logger.info("Running farrigh for task_id: %s", task_id)
        deque(farrigh(config), maxlen=0)
        logger.info("Transcription successful for task_id: %s", task_id)
        update_task_status(
            task_id,
            Status.DONE,
            file_path=f"transcripts/{task_id}.txt",
            message="Transcription completed successfully.",
        )
    except Exception as e:
        logger.error("Transcription failed for task_id: %s, error: %s", task_id, str(e))
        update_task_status(task_id, Status.ERROR, message=f"Internal server error.")
        raise HTTPException(status_code=500, detail=str(e))


def update_task_status(task_id, status, file_path=None, message=None):
    """Update the task status in the database."""
    session = next(get_session())
    task = session.get(Task, task_id)
    if task:
        task.status = status
        if file_path:
            task.transcript_path = file_path
        if message:
            task.message = message
        session.add(task)
        session.commit()
    else:
        raise UnexpectedException("This shouldn't happen because the task is created in the database.")
