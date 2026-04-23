@echo off
echo ================================================
echo  APSF - Starting Frontend (Next.js)
echo ================================================
echo.

cd /d "%~dp0frontend"

IF NOT EXIST "node_modules" (
    echo [1/2] Installing Node.js dependencies...
    npm install
)

echo [2/2] Starting development server...
echo.
echo  Dashboard at: http://localhost:3000
echo ================================================
echo.
npm run dev
