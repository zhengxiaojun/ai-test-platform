@echo off
echo ========================================
echo AI Test Platform - Setup Script
echo ========================================
echo.

echo [1/5] Setting up Backend...
cd backend

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo Installing Playwright...
playwright install chromium

echo.
echo [2/5] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo .env file created! Please edit it and add your OPENAI_API_KEY
) else (
    echo .env file already exists
)

echo.
echo [3/5] Setting up Frontend...
cd ..\frontend

echo Installing Node.js dependencies...
call npm install

echo.
echo [4/5] Setup Complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo 1. Edit backend\.env and configure:
echo    - OPENAI_API_KEY
echo    - DATABASE_URL (if using external PostgreSQL)
echo    - SECRET_KEY
echo.
echo 2. Start Backend:
echo    cd backend
echo    venv\Scripts\activate
echo    python main.py
echo.
echo 3. Start Frontend (in new terminal):
echo    cd frontend
echo    npm run dev
echo.
echo 4. Access the application:
echo    Frontend: http://localhost:8000
echo    Backend API: http://localhost:8000/docs
echo.
echo ========================================

pause

