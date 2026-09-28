from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from app.config import settings


_PIPELINE = None


def _load_font(size: int):
    """
    Try to load a common font.
    Falls back to Pillow's default font.
    """

    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial.ttf",
    ]

    for font_path in candidates:
        path = Path(font_path)

        if path.exists():
            try:
                return ImageFont.truetype(
                    str(path),
                    size=size,
                )
            except Exception:
                pass

    return ImageFont.load_default()


def _create_placeholder_image(
    prompt: str,
    output_path: Path,
    panel_number: int,
) -> str:
    """
    Create a placeholder image so the complete
    application can be tested without downloading
    a Stable Diffusion model.
    """

    width = settings.image_width
    height = settings.image_height

    image = Image.new(
        "RGB",
        (width, height),
        "#20252f",
    )

    draw = ImageDraw.Draw(image)

    # Border
    draw.rectangle(
        [8, 8, width - 8, height - 8],
        outline="#f5c542",
        width=5,
    )

    title_font = _load_font(32)
    body_font = _load_font(18)

    draw.text(
        (25, 25),
        f"COMIC PANEL {panel_number}",
        fill="white",
        font=title_font,
    )

    # Wrap prompt.
    words = prompt.split()
    lines = []
    current = ""

    for word in words:
        test = (
            f"{current} {word}"
            if current
            else word
        )

        if len(test) > 42:
            lines.append(current)
            current = word
        else:
            current = test

    if current:
        lines.append(current)

    y = 100

    for line in lines[:12]:
        draw.text(
            (25, y),
            line,
            fill="#d9e1f2",
            font=body_font,
        )

        y += 28

    draw.text(
        (25, height - 50),
        "Placeholder mode",
        fill="#f5c542",
        font=body_font,
    )

    image.save(
        output_path,
        format="PNG",
    )

    return f"/static/panels/{output_path.name}"


def _get_pipeline():
    """
    Lazy-load Stable Diffusion so the application
    can start without loading the model immediately.
    """

    global _PIPELINE

    if _PIPELINE is not None:
        return _PIPELINE

    import torch
    from diffusers import StableDiffusionPipeline

    dtype = (
        torch.float16
        if torch.cuda.is_available()
        else torch.float32
    )

    kwargs = {
        "torch_dtype": dtype,
    }

    if settings.hf_token:
        kwargs["token"] = settings.hf_token

    _PIPELINE = StableDiffusionPipeline.from_pretrained(
        settings.image_model,
        **kwargs,
    )

    if torch.cuda.is_available():
        _PIPELINE = _PIPELINE.to("cuda")
    else:
        _PIPELINE = _PIPELINE.to("cpu")

    return _PIPELINE


def generate_image(
    prompt: str,
    panel_number: int,
    filename: Optional[str] = None,
) -> str:
    """
    Generate one image for a comic panel.
    """

    if filename is None:
        filename = (
            f"panel_{panel_number}.png"
        )

    output_path = (
        settings.panels_dir / filename
    )

    provider = (
        settings.image_provider
        .strip()
        .lower()
    )

    if provider == "placeholder":
        return _create_placeholder_image(
            prompt=prompt,
            output_path=output_path,
            panel_number=panel_number,
        )

    if provider != "diffusers":
        raise ValueError(
            f"Unsupported IMAGE_PROVIDER: {provider}"
        )

    pipeline = _get_pipeline()

    image = pipeline(
        prompt=prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=7.0,
    ).images[0]

    image.save(
        output_path,
        format="PNG",
    )

    return f"/static/panels/{output_path.name}"