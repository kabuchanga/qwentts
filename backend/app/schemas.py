"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class TTSCustomVoiceRequest(BaseModel):
    """Request model for custom voice TTS"""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to synthesize")
    voice: str = Field(..., description="Voice profile (Vivian, Ryan, Aiden, etc.)")
    language: str = Field(default="Auto", description="Language code or 'Auto' for auto-detection")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")
    pitch: float = Field(default=1.0, ge=0.5, le=2.0, description="Pitch adjustment (0.5-2.0)")
    instruction: Optional[str] = Field(default=None, description="Voice control instruction for tone/emotion")


class TTSVoiceDesignRequest(BaseModel):
    """Request model for voice design TTS"""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to synthesize")
    language: str = Field(default="Auto", description="Language code or 'Auto'")
    voice_description: str = Field(..., min_length=10, max_length=500, description="Natural language description of desired voice")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")


class TTSVoiceCloneRequest(BaseModel):
    """Request model for voice clone TTS"""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to synthesize")
    language: str = Field(default="Auto", description="Language code or 'Auto'")
    reference_text: str = Field(..., description="Transcription of reference audio")
    x_vector_only_mode: bool = Field(default=False, description="Use speaker embedding only (lower quality, faster)")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed (0.5-2.0)")
    # reference_audio is handled as FormData in the endpoint


class TTSResponseBase(BaseModel):
    """Base response model for TTS"""
    status: str = Field(default="success", description="Response status")
    duration_seconds: float = Field(description="Duration of generated audio")
    message: Optional[str] = Field(default=None, description="Additional message")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Service status")
    models_loaded: List[str] = Field(description="List of loaded models")
    device: str = Field(description="Device being used (cuda:0 or cpu)")
    cuda_available: bool = Field(description="CUDA availability")
    gpu_memory_gb: Optional[float] = Field(default=None, description="Available GPU memory in GB")


class VoiceInfo(BaseModel):
    """Information about a single voice"""
    id: str = Field(description="Voice identifier")
    name: str = Field(description="Display name")
    description: str = Field(description="Voice description")
    native_language: str = Field(description="Native language of the voice")


class VoicesResponse(BaseModel):
    """Response containing list of available voices"""
    voices: List[VoiceInfo] = Field(description="List of available voices")
    count: int = Field(description="Number of available voices")


class LanguagesResponse(BaseModel):
    """Response containing list of supported languages"""
    languages: List[str] = Field(description="List of supported languages")
    count: int = Field(description="Number of supported languages")


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = Field(default="error", description="Error status")
    message: str = Field(description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")
