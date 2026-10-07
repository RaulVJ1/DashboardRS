@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create the virtual environment. Is Python installed and in PATH?
        pause
        exit /b 1
    )
)

if not exist ".venv\.requirements_installed" (
    echo First run detected: installing requirements...
    call .venv\Scripts\activate.bat
    if exist "requirements.txt" (
        pip install -r requirements.txt
    ) else (
        pip install -r backend\requirements.txt
    )
    if errorlevel 1 (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
    echo installed > ".venv\.requirements_installed"
)

start "HTTP Server" cmd /k "call .venv\Scripts\activate.bat && python -m http.server 8080"
start "FastAPI" cmd /k "call .venv\Scripts\activate.bat && cd backend && uvicorn main:app --reload"