from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft - AI Comic Story Creator"

    gemini_api_key: str = ""

    gemini_outline_model: str = "gemini-3.8-flash"
    gemini_story_model: str = "gemini-3.8-flash"

    hf_token: str = ""

    image_provider: str = "placeholder"

    image_model: str = (
        "stable-diffusion-v1-5/stable-diffusion-v1-5"
    )

    image_width: int = 512
    image_height: int = 512
    image_steps: int = 20

    static_dir: Path = BASE_DIR / "static"
    panels_dir: Path = BASE_DIR / "static" / "panels"
    exports_dir: Path = BASE_DIR / "static" / "exports"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

settings.panels_dir.mkdir(parents=True, exist_ok=True)
settings.exports_dir.mkdir(parents=True, exist_ok=True)