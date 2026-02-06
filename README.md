# Qwen3-TTS Installation and Usage Guide

## 📋 Project Structure

```
qwentts/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── schemas.py           # Pydantic models
│   │   ├── device_utils.py      # GPU/CPU detection
│   │   ├── model_manager.py     # Model loading/caching
│   │   └── audio_utils.py       # Audio processing
│   ├── requirements.txt
│   └── run.py                   # Server startup script
├── frontend/
│   └── index.html               # Web UI
├── docker/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── .dockerignore
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

#### Prerequisites
- Docker and Docker Compose installed
- NVIDIA GPU with NVIDIA Container Runtime (optional but recommended)
- At least 16GB RAM, 10GB free disk space

#### Steps

1. **Clone and navigate to the project**
```bash
cd qwentts
```

2. **Create directories for volumes**
```bash
mkdir -p models output logs
```

3. **Build and run**
```bash
docker-compose up --build
```

4. **Access the application**
- Web UI: http://localhost (port 80)
- API Documentation: http://localhost/docs
- API ReDoc: http://localhost/redoc

### Option 2: Local Installation (Development)

#### Prerequisites
- Python 3.12+
- CUDA 12.1 (for GPU support)
- ffmpeg and libsndfile1 installed

#### Steps

1. **Create virtual environment**
```bash
conda create -n qwen3-tts python=3.12 -y
conda activate qwen3-tts
```

2. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Install FlashAttention (recommended for GPU)**
```bash
pip install -U flash-attn --no-build-isolation
```

4. **Run the API server**
```bash
python run.py
```

5. **Serve the frontend**
In another terminal:
```bash
cd frontend
python -m http.server 3000
```

6. **Access the application**
- Web UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📚 API Endpoints

### Text-to-Speech Endpoints

#### 1. Custom Voice Synthesis
```
POST /api/tts/custom-voice
Content-Type: application/json

{
  "text": "Hello, world!",
  "voice": "Vivian",
  "language": "English",
  "speed": 1.0,
  "pitch": 1.0,
  "instruction": "Speak with happiness"
}

Response: Audio file (WAV)
```

#### 2. Voice Design Synthesis
```
POST /api/tts/voice-design
Content-Type: application/json

{
  "text": "Your text here",
  "language": "English",
  "voice_description": "Warm, elderly male voice with slight accent"
}

Response: Audio file (WAV)
```

#### 3. Voice Clone Synthesis
```
POST /api/tts/voice-clone
Content-Type: multipart/form-data

Form data:
- text: "Text to synthesize"
- reference_audio: <audio file>
- reference_text: "Transcription of reference audio"
- language: "English"
- x_vector_only_mode: false

Response: Audio file (WAV)
```

### Information Endpoints

#### Get Available Voices
```
GET /api/voices

Response:
{
  "voices": [
    {
      "id": "Vivian",
      "name": "Vivian",
      "description": "Bright, slightly edgy young female voice",
      "native_language": "Chinese"
    },
    ...
  ],
  "count": 9
}
```

#### Get Supported Languages
```
GET /api/languages

Response:
{
  "languages": ["Chinese", "English", "Japanese", "Korean", ...],
  "count": 10
}
```

#### Health Check
```
GET /api/health

Response:
{
  "status": "healthy",
  "models_loaded": ["custom_voice"],
  "device": "cuda:0",
  "cuda_available": true,
  "gpu_memory_gb": 12.5
}
```

#### Model Information
```
GET /api/models

Response:
{
  "loaded_models": ["custom_voice"],
  "device": "cuda:0",
  "dtype": "torch.bfloat16",
  "available_models": ["custom_voice", "voice_design", "voice_clone", "tokenizer"],
  "available_voices": ["Vivian", "Ryan", ...],
  "supported_languages": [...]
}
```

## 🎤 Pre-built Voices

| Voice | Gender | Description | Native Language |
|-------|--------|-------------|-----------------|
| Vivian | Female | Bright, edgy young female | Chinese |
| Serena | Female | Warm, gentle young female | Chinese |
| Uncle_Fu | Male | Seasoned male, low mellow timbre | Chinese |
| Dylan | Male | Youthful Beijing male | Beijing Dialect |
| Eric | Male | Lively Chengdu male | Sichuan Dialect |
| Ryan | Male | Dynamic, strong rhythmic | English |
| Aiden | Male | Sunny American male | English |
| Ono_Anna | Female | Playful Japanese female | Japanese |
| Sohee | Female | Warm Korean female | Korean |

## 🌐 Supported Languages

- Chinese (Mandarin)
- English
- Japanese
- Korean
- German
- French
- Russian
- Portuguese
- Spanish
- Italian

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# GPU Configuration
CUDA_VISIBLE_DEVICES=0

# Model Paths (optional, defaults to HuggingFace)
# QWEN_MODEL_CACHE=/models

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### GPU Memory Optimization

If you encounter GPU memory issues:

1. Use FlashAttention 2 (already in Dockerfile)
2. Use the smaller 0.6B models instead of 1.7B
3. Load only the models you need (on-demand loading)
4. Clear model cache after use

## 🔧 Troubleshooting

### API Won't Start

1. **Check CUDA availability**
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

2. **Check model downloads**
- Models are downloaded from HuggingFace on first use
- Ensure internet connection and sufficient disk space

3. **Check logs**
```bash
docker-compose logs -f qwen-tts-api
```

### Out of Memory Errors

1. Reduce batch size (currently processing one at a time)
2. Use CPU mode instead of GPU (slower)
3. Use smaller 0.6B models

### Frontend Can't Connect to API

1. Check CORS settings in `main.py` (currently allows all origins)
2. Verify API is running: http://localhost:8000/api/health
3. Check browser console for network errors

## 📊 Performance Tips

1. **Pre-load models**: Models are loaded on-demand. Pre-load common models to avoid latency.

2. **Batch processing**: For multiple requests, process together when possible.

3. **Use streaming**: The API supports streaming responses for low-latency audio.

4. **Cache voices**: Voice clone prompts can be reused to avoid re-extraction.

5. **GPU vs CPU**:
   - GPU: Fast inference, requires NVIDIA GPU, high memory
   - CPU: Slower inference, works everywhere, low memory

## 🧪 Testing with cURL

```bash
# Get voices
curl http://localhost:8000/api/voices

# Get languages
curl http://localhost:8000/api/languages

# Health check
curl http://localhost:8000/api/health

# Custom voice synthesis
curl -X POST http://localhost:8000/api/tts/custom-voice \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "voice": "Vivian",
    "language": "English"
  }' \
  --output audio.wav

# Voice design synthesis
curl -X POST http://localhost:8000/api/tts/voice-design \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "language": "English",
    "voice_description": "Warm female voice"
  }' \
  --output audio.wav

# Voice clone synthesis
curl -X POST http://localhost:8000/api/tts/voice-clone \
  -F "text=Hello world" \
  -F "reference_audio=@reference.wav" \
  -F "reference_text=Your reference text" \
  -F "language=English" \
  --output audio.wav
```

## 📝 Notes

- First request to each model type will be slower (model loading)
- Reference audio for voice cloning should be 3+ seconds for best results
- Voice clone requires accurate transcription of reference audio
- All text inputs are limited to 1000 characters
- Audio output is in WAV format (can be converted to MP3/OGG)

## 🔗 Resources

- Qwen3-TTS GitHub: https://github.com/QwenLM/Qwen3-TTS
- HuggingFace Models: https://huggingface.co/collections/Qwen/qwen3-tts
- Official Paper: https://arxiv.org/abs/2601.15621

## 📄 License

This project uses Qwen3-TTS which is licensed under Apache-2.0.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📞 Support

For issues or questions:
1. Check the GitHub issues
2. Refer to the official documentation
3. Check troubleshooting section above
