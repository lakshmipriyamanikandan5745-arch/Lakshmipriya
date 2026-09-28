from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.schemas import PromptRequest
from app.services.exporters import export_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import expand_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_layout

router = APIRouter()


def create_comic(request_data: PromptRequest):
    outline = generate_outline(
        story_prompt=request_data.story_prompt,
        character_name=request_data.character_name,
        setting=request_data.setting,
        tone=request_data.tone,
        art_style=request_data.art_style,
        panel_count=request_data.panel_count,
    )

    story = expand_story(
        outline=outline,
        character_name=request_data.character_name,
        setting=request_data.setting,
        tone=request_data.tone,
    )

    image_urls = []

    for panel in story["panels"]:
        image_url = generate_image(
            prompt=panel["image_prompt"],
            panel_number=panel["panel_number"],
        )
        image_urls.append(image_url)

    comic = build_layout(
        outline=outline,
        story=story,
        image_urls=image_urls,
    )

    pdf_url = export_pdf(comic)

    comic["pdf_url"] = pdf_url

    return comic


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form("Alex"),
    setting: str = Form("A futuristic city"),
    tone: str = Form("Adventurous"),
    art_style: str = Form("Cinematic comic book"),
    panel_count: int = Form(5),
):
    request_data = PromptRequest(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
        panel_count=panel_count,
    )

    try:
        comic = create_comic(request_data)

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "comic": comic,
            },
        )

    except Exception as exc:
        import traceback

        traceback.print_exc()

        return request.app.state.templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc),
                "form_data": request_data.model_dump(),
            },
            status_code=500,
        )


@router.post("/generate-comic/json")
async def generate_comic_json(
    request_data: PromptRequest,
):
    try:
        comic = create_comic(request_data)

        return JSONResponse(
            content=comic,
        )

    except Exception as exc:
        import traceback

        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc),
            },
        )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    pdf_url = request.query_params.get("pdf", "")

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_url": pdf_url,
        },
    )


@router.get("/test-image")
async def test_image():
    image_url = generate_image(
        prompt=(
            "A futuristic comic book city "
            "at sunset, cinematic lighting"
        ),
        panel_number=999,
        filename="test_image.png",
    )

    return {
        "status": "ok",
        "image_url": image_url,
    }