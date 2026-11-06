"""포트폴리오 페이지와 방명록 API를 제공하는 FastAPI 앱."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from guestbook import init_database, router as guestbook_router

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(title="포트폴리오 방명록 API", lifespan=lifespan)


@app.get("/", include_in_schema=False)
def portfolio():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/portfolio", include_in_schema=False)
def old_portfolio_address():
    return RedirectResponse("/")


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(guestbook_router)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
