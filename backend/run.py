#!/usr/bin/env python
"""
Startup script for Qwen3-TTS API server
"""
import uvicorn
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start the API server"""
    logger.info("Starting Qwen3-TTS API Server")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
            timeout_keep_alive=600,  # 10 minutes for long-running CPU inference
            timeout_graceful_shutdown=30,
        )
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
