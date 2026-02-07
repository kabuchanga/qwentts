# CPU and GPU Support

This application supports both CPU and GPU execution modes. The backend automatically detects available hardware and configures itself accordingly.

## Model Sizes

The application supports two model sizes:
- **0.6B** (default for CPU): Faster, smaller, uses ~2-3GB memory - ideal for CPU mode
- **1.7B** (default for GPU): Better quality, uses ~7-8GB memory - recommended for GPU mode

See [MODEL_SIZES.md](MODEL_SIZES.md) for detailed information about model sizes and configuration.

## Running on CPU (Default)

The default configuration runs on CPU, which works on any system:

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

Or manually:
```bash
docker-compose up -d --build
```

## Running on GPU

For systems with NVIDIA GPU and proper CUDA support:

### Windows
```bash
start-gpu.bat
```

### Linux/Mac
```bash
chmod +x start-gpu.sh
./start-gpu.sh
```

Or manually:
```bash
docker-compose -f docker-compose.yml -f docker-compose.gpu.yml up -d --build
```

## Prerequisites for GPU Support

1. **NVIDIA GPU** with CUDA support
2. **NVIDIA Docker Runtime** installed
3. **WSL2** (Windows only) with GPU passthrough configured
4. **CUDA drivers** properly installed on host system

## Performance Comparison

- **GPU Mode**: Significantly faster inference, recommended for production use
- **CPU Mode**: Slower but works on any system, suitable for development and testing

## Automatic Device Detection

The application automatically detects and uses the best available device:
- If GPU is available and configured, it will use GPU
- If GPU is not available or configured, it will fall back to CPU
- Check the logs at startup to see which device is being used

## Troubleshooting

### GPU not detected in Docker
If you see errors like "nvidia-container-cli: initialization error", this means:
- NVIDIA Docker runtime is not installed
- WSL2 GPU passthrough is not configured (Windows)
- CUDA drivers are missing

**Solution**: Use CPU mode (default docker-compose.yml) instead.

### Checking device in use
Check the application logs to see which device is being used:
```bash
docker-compose logs qwen-tts-api | grep "Device"
```

You should see output like:
- `Device Manager initialized: cuda:0` (GPU mode)
- `Device Manager initialized: cpu` (CPU mode)
