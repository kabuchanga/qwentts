#!/bin/bash
# Quick start script for Qwen3-TTS with Docker

set -e

echo "🚀 Qwen3-TTS Quick Start"
echo "========================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p models output logs
echo "✓ Directories created"
echo ""

# Build and run
echo "🔨 Building Docker images..."
docker-compose build
echo "✓ Build complete"
echo ""

echo "▶️ Starting services..."
docker-compose up -d
echo "✓ Services started"
echo ""

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✓ API is ready!"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Display information
echo ""
echo "✨ Qwen3-TTS is now running!"
echo ""
echo "📍 Access points:"
echo "   - Web UI:        http://localhost"
echo "   - API Docs:      http://localhost/docs"
echo "   - API ReDoc:     http://localhost/redoc"
echo "   - API Base URL:  http://localhost/api"
echo ""
echo "📊 Check status:"
echo "   docker-compose ps"
echo ""
echo "📖 View logs:"
echo "   docker-compose logs -f qwen-tts-api"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
echo "🗑️ Stop and remove volumes:"
echo "   docker-compose down -v"
echo ""
