"""
Main FastAPI application for Qwen3-TTS API
"""
import logging
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import soundfile as sf
from io import BytesIO
from pathlib import Path
import tempfile
import torch

from .device_utils import device_manager
from .model_manager import model_manager, AVAILABLE_VOICES
from .audio_utils import AudioProcessor, AudioMetadata
from .schemas import (
    TTSCustomVoiceRequest,
    TTSVoiceDesignRequest,
    TTSVoiceCloneRequest,
    HealthResponse,
    VoiceInfo,
    VoicesResponse,
    LanguagesResponse,
    ErrorResponse,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Qwen3-TTS API",
    description="API for Qwen3 Text-to-Speech synthesis with voice cloning and design",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Qwen3-TTS API")
    logger.info(f"Device: {device_manager.get_device()}")
    logger.info(f"Device Info: {device_manager.get_device_info()}")
    # Pre-load tokenizer and main model in background to reduce first request latency
    # This allows the server to start immediately while models load
    async def background_model_load():
        try:
            await asyncio.to_thread(model_manager.load_tokenizer)
            logger.info("Tokenizer loaded successfully")
            await asyncio.to_thread(model_manager.load_model, "custom_voice")
            logger.info("Custom voice model pre-loaded successfully")
        except Exception as e:
            logger.warning(f"Background model pre-load skipped: {str(e)}")
    
    # Start background loading without waiting
    asyncio.create_task(background_model_load())


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Qwen3-TTS API")
    model_manager.clear_cache()


# ============ HEALTH & INFO ENDPOINTS ============

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check service health and status"""
    try:
        available_memory = device_manager.get_available_memory_gb() if device_manager.is_cuda_available() else None
        
        return HealthResponse(
            status="healthy",
            models_loaded=model_manager.get_model_info()["loaded_models"],
            device=device_manager.get_device(),
            cuda_available=device_manager.is_cuda_available(),
            gpu_memory_gb=available_memory,
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service health check failed")


@app.get("/health", response_model=HealthResponse)
async def health_check_root():
    """Health check endpoint (alias for /api/health for backward compatibility)"""
    return await health_check()


@app.get("/api/voices", response_model=VoicesResponse)
async def get_voices():
    """Get list of available voices"""
    try:
        voices_dict = model_manager.get_available_voices()
        voices = [
            VoiceInfo(
                id=voice_id,
                name=voice_id,
                description=info["description"],
                native_language=info["native_language"],
            )
            for voice_id, info in voices_dict.items()
        ]
        return VoicesResponse(voices=voices, count=len(voices))
    except Exception as e:
        logger.error(f"Failed to get voices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve voices")


@app.get("/api/languages", response_model=LanguagesResponse)
async def get_languages():
    """Get list of supported languages"""
    try:
        languages = model_manager.get_supported_languages()
        return LanguagesResponse(languages=languages, count=len(languages))
    except Exception as e:
        logger.error(f"Failed to get languages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve languages")


@app.get("/api/models")
async def get_models_info():
    """Get information about all models"""
    try:
        return model_manager.get_model_info()
    except Exception as e:
        logger.error(f"Failed to get model info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve model information")


# ============ TTS ENDPOINTS ============

@app.post("/api/tts/custom-voice")
async def synthesize_custom_voice(request: TTSCustomVoiceRequest):
    """
    Synthesize speech using a pre-built custom voice
    
    Args:
        request: TTSCustomVoiceRequest containing text, voice, language, etc.
    
    Returns:
        Audio file (WAV format)
    """
    try:
        # Validate voice
        available_voices = model_manager.get_available_voices()
        if request.voice not in available_voices:
            raise ValueError(f"Invalid voice: {request.voice}. Available: {list(available_voices.keys())}")
        
        logger.info(f"Synthesizing: '{request.text[:50]}...' with voice '{request.voice}'")
        
        # Load model (may take time on first request - downloading + loading)
        logger.info("Loading custom_voice model (this may take a few minutes on first request)...")
        model = model_manager.load_model("custom_voice")
        logger.info("Model loaded successfully, generating speech...")
        
        # Generate speech with optimization parameters
        with torch.no_grad():
            wavs, sr = model.generate_custom_voice(
                text=request.text,
                language=request.language,
                speaker=request.voice,
                instruct=request.instruction,
                speed=request.speed,  # Speech speed control
            )
        
        audio_data = wavs[0]
        
        # Save to bytes
        audio_bytes = AudioProcessor.save_audio(audio_data, sr, format="wav")
        
        # Get duration for response
        duration = AudioMetadata.get_duration(audio_data, sr)
        
        logger.info(f"Generated audio: {duration:.2f}s")
        
        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/wav",
            headers={"Content-Disposition": f"attachment; filename=audio_{request.voice}.wav"},
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"TTS generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Speech synthesis failed")


@app.post("/api/tts/voice-design")
async def synthesize_voice_design(request: TTSVoiceDesignRequest):
    """
    Synthesize speech with a voice designed from natural language description
    
    Args:
        request: TTSVoiceDesignRequest containing text, language, and voice_description
    
    Returns:
        Audio file (WAV format)
    """
    try:
        logger.info(f"Voice design: '{request.text[:50]}...'")
        logger.info(f"Voice description: {request.voice_description[:100]}...")
        
        # Load model (may take time on first request)
        logger.info("Loading voice_design model (this may take a few minutes on first request)...")
        model = model_manager.load_model("voice_design")
        logger.info("Model loaded successfully, generating speech...")
        
        # Generate speech with optimization parameters
        with torch.no_grad():
            wavs, sr = model.generate_voice_design(
                text=request.text,
                language=request.language,
                instruct=request.voice_description,
            )
        
        audio_data = wavs[0]
        
        # Save to bytes
        audio_bytes = AudioProcessor.save_audio(audio_data, sr, format="wav")
        
        # Get duration
        duration = AudioMetadata.get_duration(audio_data, sr)
        
        logger.info(f"Generated audio: {duration:.2f}s")
        
        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=audio_voice_design.wav"},
        )
    
    except Exception as e:
        logger.error(f"Voice design synthesis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Voice design synthesis failed")


@app.post("/api/tts/voice-clone")
async def synthesize_voice_clone(
    text: str = Form(...),
    reference_audio: UploadFile = File(...),
    reference_text: str = Form(...),
    language: str = Form(default="Auto"),
    x_vector_only_mode: bool = Form(default=False),
):
    """
    Synthesize speech by cloning a voice from reference audio
    
    Args:
        text: Text to synthesize
        reference_audio: Reference audio file (3+ seconds recommended)
        reference_text: Transcription of reference audio
        language: Language code or 'Auto'
        x_vector_only_mode: Use speaker embedding only (faster but lower quality)
    
    Returns:
        Audio file (WAV format)
    """
    try:
        logger.info(f"Voice clone: '{text[:50]}...'")
        
        # Load and validate reference audio
        reference_audio_bytes = await reference_audio.read()
        ref_audio_data, ref_sr = AudioProcessor.load_audio(reference_audio_bytes)
        
        # Validate minimum duration
        if not AudioProcessor.validate_audio_duration(ref_audio_data, ref_sr, min_duration=1.0):
            raise ValueError("Reference audio too short. Minimum 1 second required (3+ seconds recommended)")
        
        logger.info(f"Reference audio duration: {AudioMetadata.get_duration(ref_audio_data, ref_sr):.2f}s")
        
        # Load model
        model = model_manager.load_model("voice_clone")
        
        # Generate speech
        with torch.no_grad():
            wavs, sr = model.generate_voice_clone(
                text=text,
                language=language,
                ref_audio=(ref_audio_data, ref_sr),
                ref_text=reference_text,
                x_vector_only_mode=x_vector_only_mode,
            )
        
        audio_data = wavs[0]
        
        # Save to bytes
        audio_bytes = AudioProcessor.save_audio(audio_data, sr, format="wav")
        
        # Get duration
        duration = AudioMetadata.get_duration(audio_data, sr)
        
        logger.info(f"Generated audio: {duration:.2f}s")
        
        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=audio_voice_clone.wav"},
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Voice clone synthesis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Voice clone synthesis failed")


# ============ ERROR HANDLERS ============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "code": exc.status_code,
        }
    )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Qwen3-TTS API",
        "version": "1.0.0",
        "description": "Text-to-Speech synthesis with voice cloning and design",
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
