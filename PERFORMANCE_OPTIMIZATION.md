# Performance Optimization Guide for Qwen3-TTS

This guide explains various optimization strategies to improve TTS generation speed, especially important for CPU-only systems.

## Quick Optimizations Applied

### 1. **Model Configuration**
- ✅ **KV-Cache Enabled**: Speeds up autoregressive generation
- ✅ **Model set to eval mode**: Disables training-specific operations
- ✅ **Eager attention**: Optimized for CPU inference

### 2. **Speed Parameter**
All TTS endpoints now support a `speed` parameter (0.5-2.0):
- `speed=1.5`: 50% faster speech (slight quality tradeoff)
- `speed=2.0`: Fastest generation (maximum speed) 
- Default: `speed=1.0` (normal speed)

### 3. **Nginx Timeouts Extended**
- Set to 600 seconds (10 minutes) to accommodate CPU inference
- Located in: `docker/nginx.conf`

## Model Size Selection

The single biggest factor for speed:

| Model | CPU Time (10s audio) | Quality |
|-------|---------------------|---------|
| 0.6B  | ~30-60 seconds      | Good    |
| 1.7B  | ~120-300 seconds    | Better  |

**Recommendation**: Use 0.6B model on CPU (currently default)

## API Usage for Speed

### Custom Voice (Fastest)
```json
{
  "text": "Your text here",
  "voice": "Ryan",
  "language": "Auto",
  "speed": 1.5,
  "instruction": null
}
```

### Voice Cloning (Faster Mode)
```json
{
  "text": "Your text here",
  "language": "Auto",
  "reference_text": "Transcription of reference",
  "x_vector_only_mode": true,
  "speed": 1.5
}
```

Setting `x_vector_only_mode=true` uses only speaker embeddings (much faster, slightly lower quality).

## Text Length Optimization

Generation time scales with text length:
- **Short (< 50 chars)**: 10-30 seconds on CPU
- **Medium (50-200 chars)**: 30-90 seconds on CPU
- **Long (200-1000 chars)**: 90-300+ seconds on CPU

**Tip**: Break long texts into smaller chunks and generate separately.

## Future Optimizations (Advanced)

### Torch Compile (PyTorch 2.0+)
Currently attempted automatically but may not work with all models. If successful, can provide 2-3x speedup on CPU.

### Quantization
Consider using quantized models (INT8/INT4) for significant speed improvements:
- 2-4x faster inference
- 50-75% less memory usage
- Small quality degradation

This requires model conversion and is not implemented yet.

### GPU Acceleration
If you have access to a GPU (even an older one):
```bash
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

Even a modest GPU (GTX 1060+) will be 10-20x faster than CPU.

## Monitoring Performance

Check inference times in logs:
```bash
docker-compose logs -f qwen-tts-api | grep "Generated audio"
```

## Current Limitations

1. **First Request Slow**: Model downloads and loads on first use (~5-10 minutes)
2. **CPU Inference**: Inherently slow for transformer models
3. **No Batching**: Currently processes one request at a time

## Recommended Settings for CPU

For fastest CPU inference with acceptable quality:
1. Use 0.6B model (default)
2. Set speed=1.5 in requests
3. Keep text under 200 characters
4. Use custom_voice (faster than voice_design or voice_clone)
5. For voice cloning, enable x_vector_only_mode

These settings should give you 30-60 second generation times on modern CPUs.
