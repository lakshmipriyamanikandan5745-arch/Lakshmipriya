from pathlib import Path
from uuid import uuid4

from fpdf import FPDF

from app.config import settings


def _clean_text(value: str) -> str:
    """
    FPDF's built-in Helvetica font does not support
    every Unicode character. Convert unsupported
    characters safely for the default PDF font.
    """

    if not value:
        return ""

    return value.encode(
        "latin-1",
        "replace",
    ).decode("latin-1")


def export_pdf(
    comic: dict,
) -> str:
    """
    Export the generated comic into a PDF.
    """

    filename = (
        f"comic_{uuid4().hex[:10]}.pdf"
    )

    output_path = (
        settings.exports_dir / filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    title = comic.get(
        "title",
        "AI Comic",
    )

    panels = comic.get(
        "panels",
        [],
    )

    for panel in panels:
        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        pdf.cell(
            0,
            12,
            _clean_text(
                f"{title} - Panel {panel['panel_number']}"
            ),
            ln=True,
        )

        image_url = panel.get(
            "image_url",
            "",
        )

        if image_url.startswith(
            "/static/"
        ):
            relative_path = image_url[
                len("/static/") :
            ]

            image_path = (
                settings.static_dir
                / relative_path
            )

            if image_path.exists():
                pdf.image(
                    str(image_path),
                    x=15,
                    y=30,
                    w=180,
                )

        pdf.ln(105)

        pdf.set_font(
            "Helvetica",
            "B",
            12,
        )

        pdf.cell(
            0,
            8,
            "Scene",
            ln=True,
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                panel.get(
                    "scene",
                    "",
                )
            ),
        )

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "B",
            12,
        )

        pdf.cell(
            0,
            8,
            "Caption",
            ln=True,
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                panel.get(
                    "caption",
                    "",
                )
            ),
        )

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "B",
            12,
        )

        pdf.cell(
            0,
            8,
            "Narration",
            ln=True,
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                panel.get(
                    "narration",
                    "",
                )
            ),
        )

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "B",
            12,
        )

        pdf.cell(
            0,
            8,
            "Dialogue",
            ln=True,
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            _clean_text(
                panel.get(
                    "dialogue",
                    "",
                )
            ),
        )

    pdf.output(
        str(output_path)
    )

    return f"/static/exports/{filename}"