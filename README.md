ComicCraft - AI Comic Story Creator
ComicCraft is an AI-powered comic story generation application.

It accepts a story idea and creates:

Comic story outline
Panel descriptions
Narration
Dialogue
AI image prompts
Panel images
Complete comic layout
Downloadable PDF
Technology Stack
Python
FastAPI
Jinja2
Google Gemini
Hugging Face Diffusers
Stable Diffusion
Pillow
FPDF2
HTML
CSS
JavaScript
Project Structure
comiccraft/

app/

main.py routes.py config.py schemas.py

services/

gemini_flash.py gemini_pro.py image_generator.py layout_builder.py exporters.py

templates/

index.html comic_preview.html export_success.html

static/

css/style.css js/script.js panels/ exports/

tests/

test_app.py

Windows Installation
Open VS Code terminal.

Create a virtual environment:

python -m venv .venv

Activate it:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Environment Configuration
Copy:

.env.example

to:

.env

Add your Gemini API key:

GEMINI_API_KEY=YOUR_API_KEY

For the first local test, use:

IMAGE_PROVIDER=placeholder

This avoids downloading Stable Diffusion.

Start Application
Run:

uvicorn app.main:app --reload

Open:

http://127.0.0.1:8000

API Documentation
Open:

http://127.0.0.1:8000/docs

Health Check
Open:

http://127.0.0.1:8000/health

Expected response:

{ "status": "ok", "app": "ComicCraft - AI Comic Story Creator" }

Test Image
Open:

http://127.0.0.1:8000/test-image

Run Tests
Run:

pytest -q

Real AI Image Generation
After confirming the application works in placeholder mode, change:

IMAGE_PROVIDER=placeholder

to:

IMAGE_PROVIDER=diffusers

The first generation may take significantly longer because the Stable Diffusion model must be downloaded and loaded.

A GPU is strongly recommended for practical image generation.

API JSON Example
POST:

/generate-comic/json

Example:

{ "story_prompt": "A student discovers a mysterious robot.", "character_name": "Arun", "setting": "A futuristic college laboratory", "tone": "Adventurous", "art_style": "Cinematic comic book", "panel_count": 5 }

Important
Do not upload your .env file to GitHub.

Never expose your Gemini API key publicly.
