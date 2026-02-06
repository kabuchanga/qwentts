"""
Audio processing utilities for TTS
"""
import numpy as np
import soundfile as sf
from io import BytesIO
from pathlib import Path
import logging
import tempfile
from typing import Tuple, Union

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handles audio processing and format conversion"""
    
    SUPPORTED_FORMATS = ["wav", "mp3", "ogg"]
    DEFAULT_FORMAT = "wav"
    
    @staticmethod
    def save_audio(
        audio_data: np.ndarray,
        sample_rate: int,
        format: str = "wav",
        output_path: Union[str, Path] = None,
    ) -> Union[bytes, str]:
        """
        Save audio data to file or return as bytes
        
        Args:
            audio_data: Audio waveform as numpy array
            sample_rate: Sample rate in Hz
            format: Audio format ('wav', 'mp3', 'ogg')
            output_path: Optional file path to save to
        
        Returns:
            Bytes or file path depending on whether output_path is provided
        """
        if format.lower() not in AudioProcessor.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}. Use {AudioProcessor.SUPPORTED_FORMATS}")
        
        try:
            if format.lower() == "wav":
                if output_path:
                    sf.write(str(output_path), audio_data, sample_rate)
                    logger.info(f"Saved WAV audio to {output_path}")
                    return str(output_path)
                else:
                    # Return as bytes
                    buffer = BytesIO()
                    sf.write(buffer, audio_data, sample_rate, format="WAV")
                    buffer.seek(0)
                    return buffer.getvalue()
            
            elif format.lower() in ["mp3", "ogg"]:
                # For MP3/OGG, convert to temporary WAV first, then use pydub
                try:
                    from pydub import AudioSegment
                except ImportError:
                    logger.warning("pydub not available, returning WAV instead")
                    return AudioProcessor.save_audio(audio_data, sample_rate, "wav", output_path)
                
                # Create temporary WAV file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    sf.write(tmp.name, audio_data, sample_rate)
                    
                    # Load and convert
                    audio = AudioSegment.from_wav(tmp.name)
                    
                    if output_path:
                        audio.export(str(output_path), format=format.lower())
                        logger.info(f"Saved {format.upper()} audio to {output_path}")
                        return str(output_path)
                    else:
                        buffer = BytesIO()
                        audio.export(buffer, format=format.lower())
                        buffer.seek(0)
                        return buffer.getvalue()
        
        except Exception as e:
            logger.error(f"Failed to save audio: {str(e)}")
            raise
    
    @staticmethod
    def load_audio(
        audio_source: Union[str, bytes, np.ndarray],
        sample_rate: int = None,
    ) -> Tuple[np.ndarray, int]:
        """
        Load audio from file path, bytes, or numpy array
        
        Args:
            audio_source: Audio file path (str), audio bytes, or numpy array
            sample_rate: Target sample rate (resamples if provided and different)
        
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            if isinstance(audio_source, np.ndarray):
                # Already loaded
                if sample_rate is None:
                    raise ValueError("sample_rate required when audio_source is numpy array")
                audio_data = audio_source
                loaded_sr = sample_rate
            
            elif isinstance(audio_source, bytes):
                # Load from bytes
                buffer = BytesIO(audio_source)
                audio_data, loaded_sr = sf.read(buffer)
            
            elif isinstance(audio_source, str):
                # Load from file path
                if not Path(audio_source).exists():
                    raise FileNotFoundError(f"Audio file not found: {audio_source}")
                audio_data, loaded_sr = sf.read(audio_source)
            
            else:
                raise TypeError(f"Unsupported audio source type: {type(audio_source)}")
            
            # Ensure mono audio
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
                logger.info("Converted stereo audio to mono")
            
            # Resample if needed
            if sample_rate and loaded_sr != sample_rate:
                try:
                    import librosa
                    audio_data = librosa.resample(audio_data, orig_sr=loaded_sr, target_sr=sample_rate)
                    loaded_sr = sample_rate
                    logger.info(f"Resampled audio from {loaded_sr} to {sample_rate} Hz")
                except ImportError:
                    logger.warning("librosa not available for resampling")
            
            return audio_data, loaded_sr
        
        except Exception as e:
            logger.error(f"Failed to load audio: {str(e)}")
            raise
    
    @staticmethod
    def normalize_audio(audio_data: np.ndarray, target_db: float = -20.0) -> np.ndarray:
        """
        Normalize audio to target loudness
        
        Args:
            audio_data: Audio waveform
            target_db: Target loudness in dB
        
        Returns:
            Normalized audio
        """
        try:
            import librosa
            
            # Compute RMS and normalize
            rms = np.sqrt(np.mean(audio_data ** 2))
            if rms > 0:
                # Convert target_db to linear scale
                target_linear = 10 ** (target_db / 20.0)
                audio_data = audio_data * (target_linear / rms)
                logger.info(f"Normalized audio to {target_db} dB")
            
            return audio_data
        except ImportError:
            logger.warning("librosa not available for normalization")
            return audio_data
    
    @staticmethod
    def validate_audio_duration(audio_data: np.ndarray, sample_rate: int, min_duration: float = 0.1) -> bool:
        """
        Validate audio meets minimum duration
        
        Args:
            audio_data: Audio waveform
            sample_rate: Sample rate in Hz
            min_duration: Minimum duration in seconds
        
        Returns:
            True if audio meets minimum duration
        """
        duration = len(audio_data) / sample_rate
        is_valid = duration >= min_duration
        
        if not is_valid:
            logger.warning(f"Audio duration {duration:.2f}s is less than {min_duration}s")
        
        return is_valid


class AudioMetadata:
    """Extract and store audio metadata"""
    
    @staticmethod
    def get_duration(audio_data: np.ndarray, sample_rate: int) -> float:
        """Get audio duration in seconds"""
        return len(audio_data) / sample_rate
    
    @staticmethod
    def get_info(audio_data: np.ndarray, sample_rate: int) -> dict:
        """Get audio information"""
        return {
            "duration_seconds": AudioMetadata.get_duration(audio_data, sample_rate),
            "sample_rate": sample_rate,
            "num_samples": len(audio_data),
            "rms_level": float(np.sqrt(np.mean(audio_data ** 2))),
            "peak_level": float(np.max(np.abs(audio_data))),
        }
