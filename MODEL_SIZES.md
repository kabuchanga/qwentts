# Qwen3-TTS Model Size Guide

The Qwen3-TTS system supports two model sizes, allowing you to choose between speed/memory efficiency and quality.

## Available Model Sizes

### 0.6B Models (Default)
- **Size**: ~600 million parameters
- **Memory**: ~2-3 GB RAM/VRAM
- **Speed**: Faster inference, 2-3x faster than 1.7B
- **Quality**: Good quality, suitable for most applications
- **Best for**: 
  - CPU-only systems
  - Systems with limited RAM/VRAM
  - Development and testing
  - Real-time applications

**Available models:**
- `Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice` - Pre-built voices
- `Qwen/Qwen3-TTS-12Hz-0.6B-VoiceDesign` - Voice design from text
- `Qwen/Qwen3-TTS-12Hz-0.6B-Base` - Voice cloning

### 1.7B Models
- **Size**: ~1.7 billion parameters
- **Memory**: ~7-8 GB RAM/VRAM
- **Speed**: Slower inference
- **Quality**: Higher quality, more natural speech
- **Best for**: 
  - GPU systems with sufficient VRAM
  - Production deployments where quality is priority
  - Content creation
  - Professional applications

**Available models:**
- `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` - Pre-built voices
- `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` - Voice design from text  
- `Qwen/Qwen3-TTS-12Hz-1.7B-Base` - Voice cloning

## Configuration

### Using Environment Variable

Create a `.env` file in the project root:

```bash
# For 0.6B model (default, faster)
MODEL_SIZE=0.6B

# For 1.7B model (better quality)
MODEL_SIZE=1.7B
```

Or copy from the example:
```bash
cp .env.example .env
```

### Using Docker Compose Directly

CPU mode with 0.6B (default):
```bash
docker-compose up -d --build
```

CPU mode with 1.7B:
```bash
MODEL_SIZE=1.7B docker-compose up -d --build
```

GPU mode with 0.6B:
```bash
MODEL_SIZE=0.6B docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

GPU mode with 1.7B (default for GPU):
```bash
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

## Performance Comparison

| Model | Device | Typical Inference Time* | Memory Usage |
|-------|--------|------------------------|--------------|
| 0.6B  | CPU    | 3-5 seconds            | 2-3 GB       |
| 0.6B  | GPU    | 0.5-1 second           | 2-3 GB VRAM  |
| 1.7B  | CPU    | 10-15 seconds          | 7-8 GB       |
| 1.7B  | GPU    | 1-2 seconds            | 7-8 GB VRAM  |

*For generating ~10 seconds of audio

## Recommendations

### CPU-Only Systems
- **Use 0.6B models** - The 1.7B models will be very slow on CPU
- Ensure you have at least 8GB RAM available
- Consider using the 0.6B models even on powerful CPUs

### GPU Systems
- **4-6 GB VRAM**: Use 0.6B models
- **8+ GB VRAM**: Can use either 0.6B (faster) or 1.7B (better quality)
- **12+ GB VRAM**: Comfortably use 1.7B models

### Development vs Production
- **Development/Testing**: Use 0.6B for faster iteration
- **Production**: Choose based on your quality requirements and hardware

## Changing Model Size at Runtime

You can also switch model sizes through the API (requires API restart):

```bash
# Not yet implemented in API endpoints
# Models are loaded based on MODEL_SIZE environment variable at startup
```

## Model Downloads

Models are automatically downloaded from HuggingFace on first use and cached in the `./models` directory. 

**First-time download sizes:**
- Tokenizer: ~100 MB
- 0.6B models: ~600 MB each
- 1.7B models: ~1.7 GB each

Ensure you have sufficient disk space and a stable internet connection for the initial download.

## More Information

- [0.6B Base Model on HuggingFace](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base)
- [1.7B Base Model on HuggingFace](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)
- [Qwen3-TTS Model Collection](https://huggingface.co/collections/Qwen/qwen3-tts-679af6a44ae39ba1b72f8b7f)
