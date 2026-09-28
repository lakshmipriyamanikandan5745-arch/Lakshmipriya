import json
import random
import re
import time
from typing import Any

from google import genai

from app.config import settings


def _extract_json(text: str) -> Any:
    """
    Extract JSON from Gemini response.

    Handles:
    - plain JSON
    - ```json ... ```
    - ``` ... ```
    - JSON surrounded by extra text
    """

    if not text:
        raise ValueError("Gemini returned an empty response.")

    text = text.strip()

    # Remove Markdown code fences.
    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    text = text.strip()

    # First attempt: parse the entire response.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Second attempt: find the first JSON object.
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]

        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Third attempt: find the first JSON array.
    start = text.find("[")
    end = text.rfind("]")

    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]

        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    raise ValueError(
        "Could not extract valid JSON from Gemini response.\n"
        f"Response:\n{text[:3000]}"
    )


def _generate_with_retry(
    client,
    model: str,
    prompt: str,
    max_retries: int = 5,
):
    """
    Call Gemini with retry handling for temporary 503/429 errors.

    The google-genai SDK already performs its own internal retries,
    so this is an additional application-level retry layer.
    """

    last_error = None

    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=model,
                contents=prompt,
            )

        except Exception as exc:
            last_error = exc
            error_text = str(exc).lower()

            retryable = any(
                phrase in error_text
                for phrase in [
                    "503",
                    "unavailable",
                    "high demand",
                    "service unavailable",
                    "internal server error",
                    "temporarily",
                    "429",
                    "resource exhausted",
                ]
            )

            if not retryable:
                raise

            if attempt == max_retries - 1:
                break

            # Exponential backoff:
            # approximately 4-6, 8-10, 16-18, 32-34 seconds.
            delay = (2 ** (attempt + 2)) + random.uniform(0, 2)

            print(
                "Gemini temporarily unavailable. "
                f"Retry {attempt + 1}/{max_retries - 1} "
                f"in {delay:.1f} seconds..."
            )

            time.sleep(delay)

    raise RuntimeError(
        "Gemini is temporarily unavailable after "
        f"{max_retries} attempts. "
        "Please try again in a few moments."
    ) from last_error


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    panel_count: int,
) -> dict:
    """
    Generate a structured comic outline using Gemini.

    Returns:

    {
        "title": "...",
        "panels": [
            {
                "panel_number": 1,
                "scene": "...",
                "image_prompt": "..."
            }
        ]
    }
    """

    if not story_prompt.strip():
        raise ValueError("Story prompt cannot be empty.")

    if panel_count < 1 or panel_count > 10:
        raise ValueError(
            "Panel count must be between 1 and 10."
        )

    api_key = settings.gemini_api_key.strip()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please check your .env file."
        )

    client = genai.Client(
        api_key=api_key
    )

    prompt = f"""
You are an expert comic book story planner.

Create a complete comic story outline based on the user's idea.

USER STORY IDEA:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

NUMBER OF PANELS:
{panel_count}

Return ONLY valid JSON.

Do not use Markdown.
Do not use code fences.
Do not add explanations before or after the JSON.

The JSON must have exactly this structure:

{{
  "title": "A compelling comic title",
  "panels": [
    {{
      "panel_number": 1,
      "scene": "Detailed description of what happens in this panel.",
      "image_prompt": "Detailed visual prompt for generating the artwork."
    }}
  ]
}}

IMPORTANT RULES:

1. The panels array MUST contain exactly {panel_count} panels.
2. panel_number must start at 1.
3. panel_number must increase sequentially.
4. Every panel must advance the story.
5. Keep the same character appearance throughout all panels.
6. Make each image_prompt visually detailed.
7. Include environment, lighting, camera angle, composition,
   character appearance, emotions, action and art style.
8. Avoid text, speech bubbles and captions inside the generated artwork.
9. Make the story coherent from beginning to end.
10. The final panel should provide a meaningful ending or cliffhanger.
"""

    response = _generate_with_retry(
        client=client,
        model=settings.gemini_outline_model,
        prompt=prompt,
        max_retries=5,
    )

    response_text = getattr(
        response,
        "text",
        None,
    )

    if not response_text:
        raise RuntimeError(
            "Gemini returned an empty outline response."
        )

    data = _extract_json(
        response_text
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Gemini outline response must be a JSON object."
        )

    title = data.get("title")

    panels = data.get("panels")

    if not title:
        raise ValueError(
            "Gemini outline is missing 'title'."
        )

    if not isinstance(panels, list):
        raise ValueError(
            "Gemini outline is missing 'panels' array."
        )

    if len(panels) != panel_count:
        raise ValueError(
            f"Gemini returned {len(panels)} panels, "
            f"but {panel_count} were requested."
        )

    normalized_panels = []

    for index, panel in enumerate(panels, start=1):
        if not isinstance(panel, dict):
            raise ValueError(
                f"Panel {index} is not a JSON object."
            )

        scene = str(
            panel.get("scene", "")
        ).strip()

        image_prompt = str(
            panel.get("image_prompt", "")
        ).strip()

        if not scene:
            raise ValueError(
                f"Panel {index} is missing 'scene'."
            )

        if not image_prompt:
            raise ValueError(
                f"Panel {index} is missing "
                "'image_prompt'."
            )

        normalized_panels.append(
            {
                "panel_number": index,
                "scene": scene,
                "image_prompt": image_prompt,
            }
        )

    return {
        "title": str(title).strip(),
        "panels": normalized_panels,
    }