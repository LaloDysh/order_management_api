# app/utils/logging_config.py
import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def configure_logging(app):
    """Configure logging for the application."""
    
    log_dir = os.path.join(app.root_path, '../logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_level = app.config.get('LOG_LEVEL', logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Configure SQL Alchemy logging
    if app.config.get('SQLALCHEMY_ECHO', False):
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # Configure Flask app logger
    app.logger.handlers = root_logger.handlers
    app.logger.setLevel(log_level)
    
    app.logger.info("Logging configured")