"""
Qwen3 TTS Model Manager
Handles loading and management of Qwen3-TTS models
"""
import os
import torch
import logging
from typing import Optional, Tuple
from qwen_tts import Qwen3TTSModel, Qwen3TTSTokenizer
from .device_utils import device_manager

logger = logging.getLogger(__name__)

# Model sizes configuration - Multiple sizes available on HuggingFace
MODEL_SIZES = {
    "0.6B": {
        "custom_voice": "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
        "voice_design": "Qwen/Qwen3-TTS-12Hz-0.6B-VoiceDesign",
        "voice_clone": "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
    },
    "1.7B": {
        "custom_voice": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        "voice_design": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        "voice_clone": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    }
}

# Default model size - 0.6B is smaller and faster, especially good for CPU mode
# Can be overridden with MODEL_SIZE environment variable
DEFAULT_MODEL_SIZE = os.environ.get("MODEL_SIZE", "1.7B")

# Tokenizer is shared across all model sizes
TOKENIZER_MODEL = "Qwen/Qwen3-TTS-Tokenizer-12Hz"

# AVAILABLE_MODELS - for backwards compatibility (uses default model size)
def get_available_models(model_size: str = DEFAULT_MODEL_SIZE) -> dict:
    """Get available models for a specific size"""
    return {
        **MODEL_SIZES.get(model_size, MODEL_SIZES[DEFAULT_MODEL_SIZE]),
        "tokenizer": TOKENIZER_MODEL,
    }

AVAILABLE_MODELS = get_available_models()

# Pre-built voices for CustomVoice model
AVAILABLE_VOICES = {
    "Vivian": {"description": "Bright, slightly edgy young female voice", "native_language": "Chinese"},
    "Serena": {"description": "Warm, gentle young female voice", "native_language": "Chinese"},
    "Uncle_Fu": {"description": "Seasoned male voice with a low, mellow timbre", "native_language": "Chinese"},
    "Dylan": {"description": "Youthful Beijing male voice with a clear, natural timbre", "native_language": "Chinese (Beijing Dialect)"},
    "Eric": {"description": "Lively Chengdu male voice with a slightly husky brightness", "native_language": "Chinese (Sichuan Dialect)"},
    "Ryan": {"description": "Dynamic male voice with strong rhythmic drive", "native_language": "English"},
    "Aiden": {"description": "Sunny American male voice with a clear midrange", "native_language": "English"},
    "Ono_Anna": {"description": "Playful Japanese female voice with a light, nimble timbre", "native_language": "Japanese"},
    "Sohee": {"description": "Warm Korean female voice with rich emotion", "native_language": "Korean"},
}

# Supported languages
SUPPORTED_LANGUAGES = [
    "Chinese",
    "English",
    "Japanese",
    "Korean",
    "German",
    "French",
    "Russian",
    "Portuguese",
    "Spanish",
    "Italian",
]


class Qwen3TTSModelManager:
    """Manages loading and caching of Qwen3-TTS models"""
    
    def __init__(self, model_size: str = DEFAULT_MODEL_SIZE):
        self.models = {}
        self.model_size = model_size
        self.device = device_manager.get_device()
        self.dtype = device_manager.get_optimal_dtype()
        
        # Enable CPU optimizations if on CPU
        if not device_manager.is_cuda_available():
            device_manager.enable_cpu_optimizations()
        
        logger.info(f"Model Manager initialized - Device: {self.device}, DType: {self.dtype}, Model Size: {self.model_size}")
    
    def load_model(self, model_type: str, force_reload: bool = False) -> Qwen3TTSModel:
        """
        Load a Qwen3-TTS model
        
        Args:
            model_type: Type of model to load ("custom_voice", "voice_design", "voice_clone")
            force_reload: Force reload even if already cached
        
        Returns:
            Loaded model instance
        """
        if model_type in self.models and not force_reload:
            logger.info(f"Using cached {model_type} model")
            return self.models[model_type]
        
        if model_type not in MODEL_SIZES[self.model_size]:
            raise ValueError(f"Unknown model type: {model_type}. Available: {list(MODEL_SIZES[self.model_size].keys())}")
        
        model_id = MODEL_SIZES[self.model_size][model_type]
        logger.info(f"Loading {model_type} model ({self.model_size}) from {model_id}")
        
        try:
            # Load model with optimized settings for speed
            # Use eager attention (flash_attention_2 requires flash-attn package)
            # use_cache=True enables KV-cache for faster inference
            model = Qwen3TTSModel.from_pretrained(
                model_id,
                device_map=self.device,
                dtype=self.dtype,
                attn_implementation="eager",
                use_cache=True,  # Enable KV-cache for faster generation
            )
            
            # Set model to eval mode for inference optimization
            model.eval()
            
            # Optimize for CPU if needed
            if not device_manager.is_cuda_available():
                try:
                    # Enable torch.compile for faster inference (PyTorch 2.0+)
                    # This can provide 2-3x speedup on CPU
                    import torch._dynamo
                    torch._dynamo.config.suppress_errors = True
                    logger.info("Attempting torch.compile optimization for CPU...")
                    # Note: torch.compile may not work well with all models
                    # Keeping it optional and catching errors
                except Exception as e:
                    logger.info(f"Torch compile not available: {e}")
            
            self.models[model_type] = model
            logger.info(f"Successfully loaded {model_type} model ({self.model_size})")
            return model
        except Exception as e:
            logger.error(f"Failed to load {model_type} model: {str(e)}")
            raise
    
    def load_tokenizer(self, force_reload: bool = False) -> Qwen3TTSTokenizer:
        """
        Load the Qwen3-TTS tokenizer
        
        Args:
            force_reload: Force reload even if already cached
        
        Returns:
            Loaded tokenizer instance
        """
        if "tokenizer" in self.models and not force_reload:
            logger.info("Using cached tokenizer")
            return self.models["tokenizer"]
        
        logger.info(f"Loading tokenizer from {TOKENIZER_MODEL}")
        
        try:
            tokenizer = Qwen3TTSTokenizer.from_pretrained(
                TOKENIZER_MODEL,
                device_map=self.device,
            )
            self.models["tokenizer"] = tokenizer
            logger.info("Successfully loaded tokenizer")
            return tokenizer
        except Exception as e:
            logger.error(f"Failed to load tokenizer: {str(e)}")
            raise
    
    def get_available_voices(self) -> dict:
        """Get list of available pre-built voices"""
        return AVAILABLE_VOICES
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return SUPPORTED_LANGUAGES
    
    def get_model_info(self) -> dict:
        """Get information about loaded models"""
        return {
            "loaded_models": list(self.models.keys()),
            "model_size": self.model_size,
            "available_sizes": list(MODEL_SIZES.keys()),
            "device": self.device,
            "dtype": str(self.dtype),
            "available_models": list(MODEL_SIZES[self.model_size].keys()),
            "available_voices": list(AVAILABLE_VOICES.keys()),
            "supported_languages": SUPPORTED_LANGUAGES,
        }
    
    def set_model_size(self, size: str):
        """
        Change the model size (requires reloading models)
        
        Args:
            size: Model size to use ("0.6B" or "1.7B")
        """
        if size not in MODEL_SIZES:
            raise ValueError(f"Invalid model size: {size}. Available: {list(MODEL_SIZES.keys())}")
        
        if size != self.model_size:
            logger.info(f"Changing model size from {self.model_size} to {size}")
            self.clear_cache()  # Clear cache when changing size
            self.model_size = size
    
    def get_model_size(self) -> str:
        """Get current model size"""
        return self.model_size
    
    def unload_model(self, model_type: str):
        """Unload a specific model to free memory"""
        if model_type in self.models:
            del self.models[model_type]
            logger.info(f"Unloaded {model_type} model")
    
    def clear_cache(self):
        """Clear all cached models"""
        self.models.clear()
        if device_manager.is_cuda_available():
            torch.cuda.empty_cache()
        logger.info("Cleared model cache")


# Global model manager instance
model_manager = Qwen3TTSModelManager()
