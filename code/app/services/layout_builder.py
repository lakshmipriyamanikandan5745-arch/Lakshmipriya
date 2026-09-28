from typing import Any, Dict


def build_layout(
    outline: Dict[str, Any],
    story: Dict[str, Any],
    image_urls: list[str],
) -> Dict[str, Any]:
    """
    Combine story information and generated images
    into the final comic layout structure.
    """

    story_panels = story.get(
        "panels",
        [],
    )

    result_panels = []

    for index, panel in enumerate(
        story_panels
    ):
        image_url = ""

        if index < len(image_urls):
            image_url = image_urls[index]

        result_panels.append(
            {
                "panel_number": index + 1,
                "scene": panel.get(
                    "scene",
                    "",
                ),
                "caption": panel.get(
                    "caption",
                    "",
                ),
                "narration": panel.get(
                    "narration",
                    "",
                ),
                "dialogue": panel.get(
                    "dialogue",
                    "",
                ),
                "image_prompt": panel.get(
                    "image_prompt",
                    "",
                ),
                "image_url": image_url,
            }
        )

    return {
        "title": story.get(
            "title",
            outline.get(
                "title",
                "AI Comic",
            ),
        ),
        "panels": result_panels,
    }