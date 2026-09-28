import json
import re
from typing import Any, Dict, List

from app.config import settings


def _extract_json(text: str) -> Any:
    text = text.strip()

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

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if match:
        return json.loads(match.group(0))

    raise ValueError(
        "Gemini returned invalid story JSON."
    )


def expand_story(
    outline: Dict[str, Any],
    character_name: str,
    setting: str,
    tone: str,
) -> Dict[str, Any]:
    """
    Expand the short panel outline into narration,
    captions and dialogue.
    """

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file."
        )

    from google import genai

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    panel_count = len(
        outline.get("panels", [])
    )

    prompt = f"""
You are an expert comic-book script writer.

Expand the following comic outline into a complete
short comic script.

Character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Outline:
{json.dumps(outline, ensure_ascii=False, indent=2)}

Return ONLY valid JSON.

Required format:

{{
  "title": "Comic title",
  "panels": [
    {{
      "panel_number": 1,
      "scene": "Visual scene description",
      "caption": "Short caption",
      "narration": "Short narration",
      "dialogue": "Short spoken dialogue",
      "image_prompt": "Detailed image generation prompt"
    }}
  ]
}}

Rules:

1. Return exactly {panel_count} panels.
2. Preserve the original story idea.
3. Keep the character consistent.
4. Dialogue should be short enough for a comic panel.
5. Captions should be concise.
6. Narration should move the story forward.
7. Do not use Markdown.
"""

    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
    )

    raw_text = getattr(response, "text", None)

    if not raw_text:
        raise RuntimeError(
            "Gemini did not return story content."
        )

    data = _extract_json(raw_text)

    if not isinstance(data, dict):
        raise ValueError(
            "Gemini story response must be a JSON object."
        )

    panels: List[Dict[str, Any]] = data.get(
        "panels",
        [],
    )

    if len(panels) != panel_count:
        raise ValueError(
            f"Expected {panel_count} panels, "
            f"but received {len(panels)}."
        )

    for index, panel in enumerate(
        panels,
        start=1,
    ):
        panel["panel_number"] = index

        panel.setdefault(
            "scene",
            "",
        )

        panel.setdefault(
            "caption",
            "",
        )

        panel.setdefault(
            "narration",
            "",
        )

        panel.setdefault(
            "dialogue",
            "",
        )

        panel.setdefault(
            "image_prompt",
            panel["scene"],
        )

    data.setdefault(
        "title",
        outline.get(
            "title",
            "AI Comic",
        ),
    )

    data["panels"] = panels

    return data