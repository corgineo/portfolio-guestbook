"""AIM 참고 구현: FastAPI + SQLite 방명록. AI 구현 사실은 README에 명시한다."""
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict

from guestbook import router as guestbook_router

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("GUESTBOOK_DB", str(BASE_DIR / "guestbook.db")))


@contextmanager
def database():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with database() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS guestbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
    yield


app = FastAPI(title="포트폴리오 방명록 API", lifespan=lifespan)


class GuestbookCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=10)
    content: str = Field(min_length=1, max_length=500)


class GuestbookEntry(GuestbookCreate):
    id: int
    created_at: str


@app.get("/")
def health():
    return {"status": "ok"}






@app.get("/portfolio", include_in_schema=False)
def portfolio():
    return FileResponse(BASE_DIR / "static" / "index.html")


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


app.include_router(guestbook_router)
