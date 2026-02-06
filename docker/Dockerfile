FROM pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime

WORKDIR /app

# Set non-interactive mode and configure timezone
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London

# Install tzdata and set timezone (prevent interactive prompt)
RUN apt-get update && apt-get install -y tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    sox \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements 
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install flash-attention for GPU optimization
RUN pip install --no-cache-dir -U flash-attn --no-build-isolation || echo "FlashAttention installation failed, continuing without it"

# Copy backend code
COPY backend/app ./app
COPY backend/run.py .

# Create directories for models and outputs
RUN mkdir -p /models /output /logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health').read()" || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "run.py"]
