import logging
import os
from logging.handlers import RotatingFileHandler
from backend.config import LOG_LEVEL, LOG_DIR

def setup_logging(app):
    """Configure centralized logging"""
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler
    log_file = LOG_DIR / "musync.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(LOG_LEVEL)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=[console_handler, file_handler]
    )
    
    app.logger.setLevel(LOG_LEVEL)
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    
    return app.logger
