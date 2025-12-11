# -*- coding: utf-8 -*-
"""
Logging configuration for Anki Dictionary Plugin.

This module provides centralized logging configuration with:
- File and console output
- Configurable log levels
- Rotating file handler to prevent log files from growing too large
- Structured logging format with timestamps and module names
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import sys


# Default log format with timestamp, level, module, and message
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Default log level
DEFAULT_LOG_LEVEL = logging.INFO


def setup_logging(
    log_dir: Optional[Path] = None,
    log_level: int = DEFAULT_LOG_LEVEL,
    console_output: bool = True,
    file_output: bool = True
) -> None:
    """
    Set up logging configuration for the plugin.
    
    Args:
        log_dir: Directory for log files (defaults to user_files/logs)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to output logs to console
        file_output: Whether to output logs to file
    """
    # Get root logger for the plugin
    root_logger = logging.getLogger('anki_dictionary')
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_output and log_dir:
        try:
            # Ensure log directory exists
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create rotating file handler (max 5MB per file, keep 3 backups)
            log_file = log_dir / 'anki_dictionary.log'
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
            
            root_logger.info(f"Logging initialized - log file: {log_file}")
            
        except Exception as e:
            # If file logging fails, log to console only
            root_logger.error(f"Failed to set up file logging: {e}", exc_info=True)
    
    # Log initial setup info
    root_logger.info("=" * 80)
    root_logger.info("Anki Dictionary Plugin - Logging System Initialized")
    root_logger.info(f"Log Level: {logging.getLevelName(log_level)}")
    root_logger.info(f"Console Output: {console_output}")
    root_logger.info(f"File Output: {file_output}")
    if log_dir:
        root_logger.info(f"Log Directory: {log_dir}")
    root_logger.info("=" * 80)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically module name)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f'anki_dictionary.{name}')


def set_log_level(level: int) -> None:
    """
    Change the log level for all plugin loggers.
    
    Args:
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    root_logger = logging.getLogger('anki_dictionary')
    root_logger.setLevel(level)
    
    # Update all handlers
    for handler in root_logger.handlers:
        handler.setLevel(level)
    
    root_logger.info(f"Log level changed to: {logging.getLevelName(level)}")


def log_html_content(logger: logging.Logger, html: str, term: str = "", max_length: int = 1000) -> None:
    """
    Log HTML content with truncation for readability.
    
    Args:
        logger: Logger instance to use
        html: HTML content to log
        term: Associated search term (optional)
        max_length: Maximum length of HTML to log (default 1000 chars)
    """
    html_length = len(html)
    
    if term:
        logger.info(f"HTML rendered for term '{term}' ({html_length} chars)")
    else:
        logger.info(f"HTML rendered ({html_length} chars)")
    
    # Log truncated HTML at debug level
    if html_length > max_length:
        logger.debug(f"HTML content (first {max_length} chars):\n{html[:max_length]}...")
        logger.debug(f"HTML content (last 200 chars):\n...{html[-200:]}")
    else:
        logger.debug(f"HTML content:\n{html}")


def log_svg_load(logger: logging.Logger, icon_name: str, icon_path: Path, success: bool, error: Optional[str] = None) -> None:
    """
    Log SVG icon loading attempt.
    
    Args:
        logger: Logger instance to use
        icon_name: Name of the icon
        icon_path: Path to the SVG file
        success: Whether loading was successful
        error: Error message if loading failed
    """
    if success:
        logger.info(f"✓ SVG icon loaded: {icon_name} from {icon_path}")
    else:
        logger.error(f"✗ SVG icon load failed: {icon_name} from {icon_path}")
        if error:
            logger.error(f"  Error: {error}")


def log_bridge_command(logger: logging.Logger, command: str) -> None:
    """
    Log JavaScript bridge command received.
    
    Args:
        logger: Logger instance to use
        command: Bridge command string
    """
    logger.info(f"Bridge command received: {command!r}")
    logger.debug(f"  Command type: {type(command).__name__}")
    logger.debug(f"  Command length: {len(command)}")
    
    # Parse and log command details
    if ':' in command:
        cmd_type, cmd_data = command.split(':', 1)
        logger.debug(f"  Command type: {cmd_type}")
        logger.debug(f"  Command data length: {len(cmd_data)}")


def log_window_state(logger: logging.Logger, window_name: str, state: str, **kwargs) -> None:
    """
    Log window state change.
    
    Args:
        logger: Logger instance to use
        window_name: Name of the window
        state: State description (e.g., "shown", "hidden", "resized")
        **kwargs: Additional state information
    """
    logger.info(f"Window state change: {window_name} - {state}")
    
    for key, value in kwargs.items():
        logger.debug(f"  {key}: {value}")
