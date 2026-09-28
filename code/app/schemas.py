from typing import List

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=3,
        description="Main comic story idea",
    )

    character_name: str = Field(
        default="Alex",
        min_length=1,
    )

    setting: str = Field(
        default="A futuristic city",
    )

    tone: str = Field(
        default="Adventurous",
    )

    art_style: str = Field(
        default="Cinematic comic book",
    )

    panel_count: int = Field(
        default=5,
        ge=3,
        le=5,
    )


class Panel(BaseModel):
    panel_number: int
    scene: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str
    image_url: str = ""


class ComicResult(BaseModel):
    title: str
    panels: List[Panel]
    pdf_url: str = ""