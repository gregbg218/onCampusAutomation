import logging
import os
import sys
from datetime import datetime

def setup_logger(log_level=logging.INFO, log_file=None, console_output=True, log_format=None):
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    if log_format is None:
        log_format = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    
    formatter = logging.Formatter(log_format)
    
    handlers = []
    
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)
    
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    for handler in handlers:
        root_logger.addHandler(handler)
    
    return root_logger

def get_logger(name):
    return logging.getLogger(name)

def configure_logging(config=None):
    if config is None:
        config = {}
    
    log_level_str = config.get('log_level', 'INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Default to console-only logging (file logging disabled)
    log_file = config.get('log_file', None)
    enable_file_logging = config.get('enable_file_logging', False)
    
    # Only create a log file if explicitly enabled
    if enable_file_logging and log_file is None and config.get('timestamp_file', True):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f'parking_automation_{timestamp}.log'
    elif not enable_file_logging:
        log_file = None
    
    console_output = config.get('console_output', True)
    log_format = config.get('log_format', '%(asctime)s | %(levelname)s | %(name)s | %(message)s')
    
    return setup_logger(log_level, log_file, console_output, log_format)