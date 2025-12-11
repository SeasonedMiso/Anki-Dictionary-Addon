# -*- coding: utf-8 -*-
"""
Configuration manager for handling addon settings.
"""

from typing import Any, Dict, Optional, Union, List
import json
import logging
from pathlib import Path


logger = logging.getLogger('anki_dictionary.config')


# Default configuration values
DEFAULT_CONFIG = {
    'DictionaryGroups': {},
    'ExportTemplates': {},
    'GoogleImageFields': [],
    'ForvoFields': [],
    'ForvoAddType': 'add',
    'ForvoLanguage': 'Japanese',
    'GoogleImageAddType': 'add',
    'dictOnStart': False,
    'highlightSentences': True,
    'highlightTarget': True,
    'maxSearch': 1000,
    'dictSearch': 50,
    'jReadingCards': True,
    'jReadingEdit': True,
    'googleSearchRegion': 'United States',
    'maxHeight': 400,
    'maxWidth': 400,
    'frontBracket': '【',
    'backBracket': '】',
    'showTarget': False,
    'day': True,
    'currentGroup': 'All',
    'searchMode': 'Forward',
    'currentTemplate': False,
    'currentDeck': False,
    'deinflect': True,
    'onetab': False,
    'dictSizePos': False,
    'exporterSizePos': False,
    'fontSizes': [12, 22],
    'tooltips': True,
    'globalHotkeys': True,
    'openOnGlobal': True,
    'mp3Convert': True,
    'failedFFMPEGInstallation': False,
    'dictAlwaysOnTop': False,
    'displayAgain': True,
    'autoDefinitionSettings': False,
    'autoAddDefinitions': False,
    'autoAddCards': False,
    'unknownsToSearch': 3,
    'massGenerationPreferences': False,
    'safeSearch': True,
    'condensedAudioDirectory': False,
    'disableCondensed': False,
}


# Configuration validation rules
CONFIG_VALIDATORS = {
    'maxSearch': lambda v: isinstance(v, int) and 1 <= v <= 10000,
    'dictSearch': lambda v: isinstance(v, int) and 1 <= v <= 1000,
    'maxHeight': lambda v: isinstance(v, int) and 50 <= v <= 2000,
    'maxWidth': lambda v: isinstance(v, int) and 50 <= v <= 2000,
    'searchMode': lambda v: v in ['Forward', 'Backward', 'Anywhere', 'Exact', 'Definition', 'Example', 'Pronunciation'],
    'ForvoAddType': lambda v: v in ['add', 'overwrite', 'if_empty', 'dont_export'],
    'GoogleImageAddType': lambda v: v in ['add', 'overwrite', 'if_empty', 'dont_export'],
    'ForvoLanguage': lambda v: isinstance(v, str) and len(v) > 0,
    'googleSearchRegion': lambda v: isinstance(v, str) and len(v) > 0,
    'unknownsToSearch': lambda v: isinstance(v, int) and 1 <= v <= 100,
    'fontSizes': lambda v: isinstance(v, list) and len(v) == 2 and all(isinstance(x, int) for x in v),
    'frontBracket': lambda v: isinstance(v, str),
    'backBracket': lambda v: isinstance(v, str),
    'currentGroup': lambda v: isinstance(v, str),
}


class ConfigManager:
    """Manages configuration for the Anki Dictionary addon."""
    
    def __init__(self, addon_manager: Any):
        """
        Initialize the configuration manager.
        
        Args:
            addon_manager: Anki's addon manager instance
        """
        self.addon_manager = addon_manager
        self._config_cache: Optional[Dict[str, Any]] = None
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration with defaults applied.
        
        Returns:
            Configuration dictionary with all keys guaranteed to exist
        """
        if self._config_cache is None:
            raw_config = self.addon_manager.getConfig(__name__) or {}
            self._config_cache = self._merge_with_defaults(raw_config)
            logger.debug("Configuration loaded and merged with defaults")
        return self._config_cache
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge user configuration with default values.
        
        Args:
            config: User configuration
            
        Returns:
            Merged configuration with all defaults applied
        """
        merged = DEFAULT_CONFIG.copy()
        
        # Update with user values
        for key, value in config.items():
            if key in DEFAULT_CONFIG:
                # Validate if validator exists
                if key in CONFIG_VALIDATORS:
                    if CONFIG_VALIDATORS[key](value):
                        merged[key] = value
                    else:
                        logger.warning(
                            f"Invalid value for config key '{key}': {value}. "
                            f"Using default: {DEFAULT_CONFIG[key]}"
                        )
                else:
                    merged[key] = value
            else:
                # Allow unknown keys (for extensibility)
                merged[key] = value
                logger.debug(f"Unknown config key '{key}' preserved")
        
        return merged
    
    def write_config(self, config: Dict[str, Any]) -> None:
        """
        Write configuration to disk with validation.
        
        Args:
            config: Configuration dictionary to write
            
        Raises:
            ValueError: If configuration validation fails
        """
        # Validate configuration before writing
        validation_errors = self._validate_config(config)
        if validation_errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(validation_errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.addon_manager.writeConfig(__name__, config)
        self._config_cache = self._merge_with_defaults(config)
        logger.info("Configuration written successfully")
    
    def _validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate configuration values.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        for key, value in config.items():
            if key in CONFIG_VALIDATORS:
                try:
                    if not CONFIG_VALIDATORS[key](value):
                        errors.append(
                            f"Invalid value for '{key}': {value}"
                        )
                except Exception as e:
                    errors.append(
                        f"Validation error for '{key}': {str(e)}"
                    )
        
        return errors
    
    def update_config(self, key: str, value: Any) -> None:
        """
        Update a single configuration value with validation.
        
        Args:
            key: Configuration key
            value: New value
            
        Raises:
            ValueError: If value validation fails
        """
        # Validate single value if validator exists
        if key in CONFIG_VALIDATORS:
            if not CONFIG_VALIDATORS[key](value):
                raise ValueError(
                    f"Invalid value for config key '{key}': {value}"
                )
        
        config = self.get_config().copy()
        config[key] = value
        self.write_config(config)
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with automatic default handling.
        
        Args:
            key: Configuration key
            default: Override default value (optional)
            
        Returns:
            Configuration value, provided default, or system default
        """
        config = self.get_config()
        
        # If key exists in config, return it
        if key in config:
            return config[key]
        
        # If custom default provided, return it
        if default is not None:
            return default
        
        # Return system default if available
        if key in DEFAULT_CONFIG:
            return DEFAULT_CONFIG[key]
        
        # No default available
        logger.warning(f"Config key '{key}' not found and no default available")
        return None
    
    def refresh(self) -> None:
        """Refresh the configuration cache."""
        self._config_cache = None
    
    def get_dictionary_groups(self) -> Dict[str, Any]:
        """Get dictionary groups configuration."""
        return self.get_value('DictionaryGroups', {})
    
    def get_export_templates(self) -> Dict[str, Any]:
        """Get export templates configuration."""
        return self.get_value('ExportTemplates', {})
    
    def get_search_settings(self) -> Dict[str, Any]:
        """Get search-related settings."""
        return {
            'max_search': self.get_value('maxSearch', 1000),
            'dict_search': self.get_value('dictSearch', 50),
            'search_mode': self.get_value('searchMode', 'Forward'),
            'deinflect': self.get_value('deinflect', True),
            'current_group': self.get_value('currentGroup', 'All'),
        }
    
    def get_display_settings(self) -> Dict[str, Any]:
        """Get display-related settings."""
        return {
            'highlight_sentences': self.get_value('highlightSentences', True),
            'highlight_target': self.get_value('highlightTarget', True),
            'show_target': self.get_value('showTarget', False),
            'tooltips': self.get_value('tooltips', True),
            'front_bracket': self.get_value('frontBracket', '【'),
            'back_bracket': self.get_value('backBracket', '】'),
        }
    
    def get_image_settings(self) -> Dict[str, Any]:
        """Get image-related settings."""
        return {
            'max_width': self.get_value('maxWidth', 400),
            'max_height': self.get_value('maxHeight', 400),
            'google_search_region': self.get_value('googleSearchRegion', 'United States'),
            'safe_search': self.get_value('safeSearch', True),
        }
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """Get audio-related settings."""
        return {
            'forvo_language': self.get_value('ForvoLanguage', 'Japanese'),
            'mp3_convert': self.get_value('mp3Convert', True),
            'condensed_audio_directory': self.get_value('condensedAudioDirectory', False),
            'disable_condensed': self.get_value('disableCondensed', False),
        }
    
    # Type-safe configuration access methods
    
    def get_int(self, key: str, default: Optional[int] = None) -> int:
        """
        Get an integer configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Integer value
            
        Raises:
            TypeError: If value is not an integer
        """
        value = self.get_value(key, default)
        if not isinstance(value, int):
            raise TypeError(f"Config key '{key}' is not an integer: {type(value)}")
        return value
    
    def get_bool(self, key: str, default: Optional[bool] = None) -> bool:
        """
        Get a boolean configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Boolean value
            
        Raises:
            TypeError: If value is not a boolean
        """
        value = self.get_value(key, default)
        if not isinstance(value, bool):
            raise TypeError(f"Config key '{key}' is not a boolean: {type(value)}")
        return value
    
    def get_str(self, key: str, default: Optional[str] = None) -> str:
        """
        Get a string configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            String value
            
        Raises:
            TypeError: If value is not a string
        """
        value = self.get_value(key, default)
        if not isinstance(value, str):
            raise TypeError(f"Config key '{key}' is not a string: {type(value)}")
        return value
    
    def get_list(self, key: str, default: Optional[List] = None) -> List:
        """
        Get a list configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            List value
            
        Raises:
            TypeError: If value is not a list
        """
        value = self.get_value(key, default)
        if not isinstance(value, list):
            raise TypeError(f"Config key '{key}' is not a list: {type(value)}")
        return value
    
    def get_dict(self, key: str, default: Optional[Dict] = None) -> Dict:
        """
        Get a dictionary configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Dictionary value
            
        Raises:
            TypeError: If value is not a dictionary
        """
        value = self.get_value(key, default)
        if not isinstance(value, dict):
            raise TypeError(f"Config key '{key}' is not a dictionary: {type(value)}")
        return value
    
    def has_key(self, key: str) -> bool:
        """
        Check if a configuration key exists.
        
        Args:
            key: Configuration key
            
        Returns:
            True if key exists, False otherwise
        """
        config = self.get_config()
        return key in config
    
    def validate_current_config(self) -> List[str]:
        """
        Validate the current configuration.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        return self._validate_config(self.get_config())
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.write_config(DEFAULT_CONFIG.copy())
        logger.info("Configuration reset to defaults")
    
    def get_default_value(self, key: str) -> Any:
        """
        Get the default value for a configuration key.
        
        Args:
            key: Configuration key
            
        Returns:
            Default value or None if no default exists
        """
        return DEFAULT_CONFIG.get(key)
