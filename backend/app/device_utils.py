"""
Device utilities for detecting and managing GPU/CPU resources
"""
import os
import torch
import logging

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages device selection (GPU/CPU) for Qwen TTS models"""
    
    def __init__(self):
        self.device = self._detect_device()
        self.device_info = self._get_device_info()
        logger.info(f"Device Manager initialized: {self.device}")
        logger.info(f"Device info: {self.device_info}")
    
    def _detect_device(self) -> str:
        """
        Detect available device (CUDA GPU or CPU)
        Returns: "cuda:0" if CUDA available, else "cpu"
        """
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            logger.info(f"CUDA available with {device_count} GPU(s)")
            return "cuda:0"
        else:
            logger.warning("CUDA not available, falling back to CPU")
            return "cpu"
    
    def _get_device_info(self) -> dict:
        """Get detailed device information"""
        info = {
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "pytorch_version": torch.__version__,
        }
        
        if torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_count"] = torch.cuda.device_count()
            info["cuda_capability"] = torch.cuda.get_device_capability(0)
            # Get available GPU memory in GB
            total_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            info["total_gpu_memory_gb"] = round(total_memory, 2)
        
        return info
    
    def get_device(self) -> str:
        """Get the device to use for inference"""
        return self.device
    
    def get_device_info(self) -> dict:
        """Get device information"""
        return self.device_info
    
    def is_cuda_available(self) -> bool:
        """Check if CUDA is available"""
        return torch.cuda.is_available()
    
    def get_optimal_dtype(self):
        """
        Get optimal data type based on device
        Returns: torch.bfloat16 for CUDA, torch.float32 for CPU
        """
        if self.is_cuda_available():
            return torch.bfloat16
        return torch.float32
    
    def enable_cpu_optimizations(self):
        """Enable CPU-specific optimizations for faster inference"""
        if not self.is_cuda_available():
            # Enable thread optimization for CPU inference
            cpu_count = os.cpu_count() or 1
            torch.set_num_threads(cpu_count)
            try:
                torch.set_num_interop_threads(max(1, cpu_count // 2))
            except Exception:
                pass
            # Enable MKL optimizations if available
            try:
                torch.backends.mkl.enabled = True
                logger.info("MKL optimizations enabled for CPU inference")
            except:
                pass
            # Enable cuDNN benchmark (no effect on CPU but safe to set)
            torch.backends.cudnn.benchmark = False
    
    def get_inference_context(self):
        """Get appropriate context manager for inference (no_grad + inference_mode)"""
        return torch.inference_mode()
    
    def get_available_memory_gb(self) -> float:
        """Get available GPU memory in GB (returns 0 for CPU)"""
        if not self.is_cuda_available():
            return 0.0
        
        reserved = torch.cuda.memory_reserved(0) / (1024**3)
        allocated = torch.cuda.memory_allocated(0) / (1024**3)
        available = torch.cuda.get_device_properties(0).total_memory / (1024**3) - (reserved + allocated)
        
        return max(0, available)


# Global device manager instance
device_manager = DeviceManager()
