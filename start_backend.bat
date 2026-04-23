@echo off
setlocal

set PYTHON=C:\Users\M7md-\AppData\Local\Programs\Python\Python314\python.exe
set VENV_ACTIVATE=%~dp0backend\venv\Scripts\activate.bat
set BACKEND_DIR=%~dp0backend

echo ================================================
echo  APSF - Starting Backend (FastAPI)
echo ================================================
echo.

cd /d "%BACKEND_DIR%"

IF NOT EXIST "venv\Scripts\uvicorn.exe" (
    echo [1/3] Creating Python virtual environment...
    "%PYTHON%" -m venv venv

    echo [2/3] Installing dependencies...
    venv\Scripts\pip.exe install -r requirements.txt pydantic[email]
) ELSE (
    echo [OK] Virtual environment already set up.
)

echo.
echo  Backend starting at: http://localhost:8009
echo  API Docs at:         http://localhost:8009/docs
echo ================================================
echo.
venv\Scripts\uvicorn.exe main:app --reload --port 8009

