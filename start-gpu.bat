@echo off
REM Start Qwen TTS with GPU support

echo Starting Qwen TTS API with GPU support...
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build

echo.
echo GPU-enabled Qwen TTS is starting up...
echo API will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost
echo.
echo To view logs: docker-compose logs -f qwen-tts-api
pause
