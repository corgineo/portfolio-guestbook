from contextlib import contextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
import sqlite3

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field


router = APIRouter(tags=["guestbook"])


class Message(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1, max_length=10)
    content: str = Field(min_length=1, max_length=500)


def database_path() -> Path:
    return Path(os.environ.get("GUESTBOOK_DB", str(Path(__file__).with_name("guestbook.db"))))


@contextmanager
def open_database():
    connection = sqlite3.connect(database_path(), timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def init_database() -> None:
    database_path().parent.mkdir(parents=True, exist_ok=True)
    with open_database() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS guestbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


@router.post("/guestbook")
def add_message(message: Message) -> dict:
    created_at = datetime.now(timezone.utc).isoformat()
    with open_database() as db:
        cursor = db.execute(
            "INSERT INTO guestbook (name, content, created_at) VALUES (?, ?, ?)",
            (message.name, message.content, created_at),
        )
        row = db.execute(
            "SELECT id, name, content, created_at FROM guestbook WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)


@router.get("/guestbook")
def list_messages() -> list[dict]:
    with open_database() as db:
        rows = db.execute(
            "SELECT id, name, content, created_at FROM guestbook ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
