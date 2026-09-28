from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.routes import router


BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered comic story creator "
        "using Gemini and Stable Diffusion."
    ),
    version="1.0.0",
)


templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)

app.state.templates = templates


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            settings.static_dir
        )
    ),
    name="static",
)


app.include_router(
    router
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
    }