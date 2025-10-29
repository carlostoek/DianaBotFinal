"""
DianaBot - Logging Configuration
"""
import logging
import sys
from datetime import datetime
from .settings import settings


def get_logger(name: str) -> logging.Logger:
    """Create and configure a logger with the specified name"""
    logger = logging.getLogger(name)
    
    # Prevent adding multiple handlers if logger already exists
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if settings.environment == "production":
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            f"logs/dianabot_{datetime.now().strftime('%Y%m%d')}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger