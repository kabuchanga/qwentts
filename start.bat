@echo off
REM Quick start script for Qwen3-TTS with Docker (Windows)

setlocal enabledelayedexpansion

echo.
echo 🚀 Qwen3-TTS Quick Start
echo ========================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop for Windows.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Desktop for Windows.
    pause
    exit /b 1
)

REM Create directories
echo 📁 Creating directories...
if not exist "models" mkdir models
if not exist "output" mkdir output
if not exist "logs" mkdir logs
echo ✓ Directories created
echo.

REM Build and run
echo 🔨 Building Docker images...
docker-compose build
if %errorlevel% neq 0 (
    echo ❌ Build failed
    pause
    exit /b 1
)
echo ✓ Build complete
echo.

echo ▶️ Starting services...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Failed to start services
    pause
    exit /b 1
)
echo ✓ Services started
echo.

REM Wait for API to be ready
echo ⏳ Waiting for API to be ready...
setlocal enabledelayedexpansion
for /L %%i in (1,1,30) do (
    timeout /t 2 /nobreak >nul
    curl -s http://localhost:8000/api/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo.
        echo ✓ API is ready!
        goto :api_ready
    )
    echo -n "."
)

:api_ready
echo.
echo.
echo ✨ Qwen3-TTS is now running!
echo.
echo 📍 Access points:
echo    - Web UI:        http://localhost
echo    - API Docs:      http://localhost/docs
echo    - API ReDoc:     http://localhost/redoc
echo    - API Base URL:  http://localhost/api
echo.
echo 📊 Check status:
echo    docker-compose ps
echo.
echo 📖 View logs:
echo    docker-compose logs -f qwen-tts-api
echo.
echo 🛑 Stop services:
echo    docker-compose down
echo.
echo 🗑️ Stop and remove volumes:
echo    docker-compose down -v
echo.
echo Press any key to continue...
pause >nul
