# Performance Optimizations for Qwen3-TTS

## Overview
The following optimizations have been implemented to improve model inference speed, particularly on CPU environments:

## 1. **CPU-Specific Optimizations** (device_utils.py)
- **MKL Optimization**: Enables Intel Math Kernel Library (MKL) for faster CPU computations
- **Thread Optimization**: Automatically uses all available CPU threads for inference
- **Inference Context**: Provides `torch.inference_mode()` context for all model inference

### Implementation:
```python
torch.backends.mkl.enabled = True  # Enable MKL when on CPU
torch.set_num_threads(torch.get_num_threads())  # Use all available threads
```

## 2. **Inference Mode Optimization** (model_manager.py & main.py)
- **Gradient Disabling**: Sets `requires_grad=False` for all model parameters
- **Eval Mode**: Models are explicitly set to evaluation mode (`model.eval()`)
- **No-Gradient Context**: All inference calls wrapped in `torch.inference_mode()`

### Benefits:
- Reduces memory overhead (no gradient computation)
- Faster forward pass without backward computation graph
- Automatic optimization by PyTorch

### Code Changes:
```python
# In model loading:
for param in model.parameters():
    param.requires_grad = False

# In inference:
with torch.inference_mode():
    wavs, sr = model.generate_custom_voice(...)
```

## 3. **Model Configuration**
- **Default Model Size**: 0.6B (smaller, faster)
- **Alternative**: 1.7B available for higher quality (slower)
- **Tensor Dtype**: 
  - CPU: `torch.float32` (more stable)
  - GPU: `torch.bfloat16` (faster, lower memory)

## 4. **Model Caching**
- Once loaded, models stay in memory for subsequent requests
- No need to reload models between API calls
- Cache cleared only when switching model sizes

## Expected Performance Improvements

### CPU Inference (estimated):
- **First inference**: ~30-60 seconds (model download + loading)
- **Subsequent requests**: 10-30 seconds (cached model)
- **With optimizations**: 5-15 seconds reduction on subsequent requests

### GPU Inference (estimated):
- **First inference**: ~5-10 seconds
- **Subsequent requests**: 2-5 seconds

## Recommendations for Further Optimization

### If Performance is Still Slow:

1. **Model Quantization** (advanced):
   - Convert 0.6B model to int8 quantization
   - Can reduce memory by 75% and speed up inference
   - Slight quality reduction

2. **Hardware Upgrade**:
   - GPU acceleration provides 5-10x faster inference
   - NVIDIA GPUs with CUDA support recommended

3. **Batch Processing**:
   - Process multiple requests together
   - Amortizes model loading overhead

4. **Request Optimization**:
   - Shorter text = faster synthesis
   - Reduce text length from 100+ words to 20-50 words

## Monitoring Performance

### Check CPU usage:
```bash
docker stats qwen-tts-api
```

### Check model loading:
```bash
docker logs qwen-tts-api | grep "Loading\|Successfully loaded"
```

### Check inference speed:
```bash
docker logs qwen-tts-api | grep "Generated audio"
```

## Configuration Files Modified

1. **device_utils.py**
   - Added `enable_cpu_optimizations()` method
   - Added `get_inference_context()` method

2. **model_manager.py**
   - Updated `__init__()` to call CPU optimizations
   - Updated `load_model()` to use inference mode
   - Disabled gradients for all model parameters

3. **main.py** (All TTS endpoints)
   - Wrapped inference calls in `torch.inference_mode()`
   - Applied to: custom-voice, voice-design, voice-clone

## Future Enhancements

- [ ] Add `torch.compile()` for JIT compilation (PyTorch 2.0+)
- [ ] Implement model quantization option
- [ ] Add multi-worker inference processing
- [ ] Profile and optimize audio processing pipeline
