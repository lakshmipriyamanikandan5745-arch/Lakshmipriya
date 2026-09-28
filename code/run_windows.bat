@echo off

echo ==========================================
echo ComicCraft - AI Comic Story Creator
echo ==========================================

echo.

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo.

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.

if not exist ".env" (
    echo Creating .env from .env.example...
    copy .env.example .env
)

echo.
echo Starting ComicCraft...
echo.

uvicorn app.main:app --reload

pause