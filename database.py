import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, Field, Session, create_engine
from logger.starter import logger

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")
logger.warning(f"Database url : {DATABASE_URL}")

engine = create_engine(DATABASE_URL)


class Task(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    status: str = Field(index=True)
    transcript_path: str = ""
    message: str = ""


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    """Provide a session to the endpoints to use for database connection."""
    with Session(engine) as session:
        yield session


class Status:
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    ERROR = "ERROR"


LANGUAGE_API_KEYS = {
    "EN": os.getenv("WIT_API_KEY_ENGLISH"),
    "AR": os.getenv("WIT_API_KEY_ARABIC"),
    "FR": os.getenv("WIT_API_KEY_FRENCH"),
    "JA": os.getenv("WIT_API_KEY_JAPANESE"),
}
