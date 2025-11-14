# -*- coding: utf-8 -*-
"""
Tests for ConfigManager.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.config.manager import ConfigManager, DEFAULT_CONFIG, CONFIG_VALIDATORS


@pytest.fixture
def mock_addon_manager():
    """Create a mock addon manager."""
    manager = Mock()
    manager.getConfig = Mock(return_value={
        'maxSearch': 500,
        'dictSearch': 25,
        'ForvoLanguage': 'Japanese',
        'highlightSentences': True,
    })
    manager.writeConfig = Mock()
    return manager


@pytest.fixture
def config_manager(mock_addon_manager):
    """Create a ConfigManager instance."""
    return ConfigManager(mock_addon_manager)


class TestConfigManagerInitialization:
    """Test ConfigManager initialization."""
    
    def test_init_creates_instance(self, mock_addon_manager):
        """Test that ConfigManager can be initialized."""
        manager = ConfigManager(mock_addon_manager)
        assert manager is not None
        assert manager.addon_manager == mock_addon_manager
        assert manager._config_cache is None
    
    def test_get_config_loads_from_addon_manager(self, config_manager, mock_addon_manager):
        """Test that get_config loads from addon manager."""
        config = config_manager.get_config()
        
        assert config is not None
        mock_addon_manager.getConfig.assert_called_once()
        assert config_manager._config_cache is not None
    
    def test_get_config_caches_result(self, config_manager, mock_addon_manager):
        """Test that get_config caches the result."""
        config1 = config_manager.get_config()
        config2 = config_manager.get_config()
        
        # Should only call getConfig once
        assert mock_addon_manager.getConfig.call_count == 1
        assert config1 is config2


class TestDefaultValueHandling:
    """Test default value handling."""
    
    def test_get_config_merges_with_defaults(self, config_manager):
        """Test that get_config merges user config with defaults."""
        config = config_manager.get_config()
        
        # User values should be present
        assert config['maxSearch'] == 500
        assert config['dictSearch'] == 25
        
        # Default values should be present for missing keys
        assert config['maxWidth'] == DEFAULT_CONFIG['maxWidth']
        assert config['maxHeight'] == DEFAULT_CONFIG['maxHeight']
        assert config['searchMode'] == DEFAULT_CONFIG['searchMode']
    
    def test_get_value_returns_user_value(self, config_manager):
        """Test that get_value returns user-configured value."""
        value = config_manager.get_value('maxSearch')
        assert value == 500
    
    def test_get_value_returns_default_for_missing_key(self, config_manager):
        """Test that get_value returns default for missing key."""
        value = config_manager.get_value('maxWidth')
        assert value == DEFAULT_CONFIG['maxWidth']
    
    def test_get_value_with_custom_default(self, config_manager):
        """Test that get_value uses custom default."""
        value = config_manager.get_value('nonexistent_key', 'custom_default')
        assert value == 'custom_default'
    
    def test_get_value_returns_none_for_unknown_key(self, config_manager):
        """Test that get_value returns None for unknown key without default."""
        value = config_manager.get_value('totally_unknown_key')
        assert value is None
    
    def test_get_default_value(self, config_manager):
        """Test getting default value for a key."""
        default = config_manager.get_default_value('maxSearch')
        assert default == DEFAULT_CONFIG['maxSearch']
    
    def test_get_default_value_for_unknown_key(self, config_manager):
        """Test getting default value for unknown key."""
        default = config_manager.get_default_value('unknown_key')
        assert default is None


class TestConfigurationValidation:
    """Test configuration validation."""
    
    def test_validate_valid_config(self, config_manager):
        """Test validation of valid configuration."""
        valid_config = {
            'maxSearch': 1000,
            'dictSearch': 50,
            'searchMode': 'Forward',
            'ForvoLanguage': 'Japanese',
        }
        
        errors = config_manager._validate_config(valid_config)
        assert len(errors) == 0
    
    def test_validate_invalid_max_search(self, config_manager):
        """Test validation catches invalid maxSearch."""
        invalid_config = {
            'maxSearch': 20000,  # Too high
        }
        
        errors = config_manager._validate_config(invalid_config)
        assert len(errors) > 0
        assert any('maxSearch' in error for error in errors)
    
    def test_validate_invalid_search_mode(self, config_manager):
        """Test validation catches invalid searchMode."""
        invalid_config = {
            'searchMode': 'InvalidMode',
        }
        
        errors = config_manager._validate_config(invalid_config)
        assert len(errors) > 0
        assert any('searchMode' in error for error in errors)
    
    def test_validate_invalid_font_sizes(self, config_manager):
        """Test validation catches invalid fontSizes."""
        invalid_config = {
            'fontSizes': [12],  # Should have 2 elements
        }
        
        errors = config_manager._validate_config(invalid_config)
        assert len(errors) > 0
        assert any('fontSizes' in error for error in errors)
    
    def test_write_config_validates(self, config_manager, mock_addon_manager):
        """Test that write_config validates before writing."""
        invalid_config = {
            'maxSearch': 50000,  # Invalid
        }
        
        with pytest.raises(ValueError) as exc_info:
            config_manager.write_config(invalid_config)
        
        assert 'validation failed' in str(exc_info.value).lower()
        # Should not have written
        mock_addon_manager.writeConfig.assert_not_called()
    
    def test_write_config_succeeds_with_valid_config(self, config_manager, mock_addon_manager):
        """Test that write_config succeeds with valid config."""
        valid_config = DEFAULT_CONFIG.copy()
        valid_config['maxSearch'] = 800
        
        config_manager.write_config(valid_config)
        
        mock_addon_manager.writeConfig.assert_called_once()
    
    def test_update_config_validates_value(self, config_manager):
        """Test that update_config validates the value."""
        with pytest.raises(ValueError):
            config_manager.update_config('maxSearch', 50000)
    
    def test_update_config_succeeds_with_valid_value(self, config_manager, mock_addon_manager):
        """Test that update_config succeeds with valid value."""
        config_manager.update_config('maxSearch', 800)
        
        mock_addon_manager.writeConfig.assert_called_once()
    
    def test_validate_current_config(self, config_manager):
        """Test validating current configuration."""
        errors = config_manager.validate_current_config()
        # Current config should be valid
        assert len(errors) == 0


class TestTypeSafeAccess:
    """Test type-safe configuration access methods."""
    
    def test_get_int_returns_integer(self, config_manager):
        """Test that get_int returns integer value."""
        value = config_manager.get_int('maxSearch')
        assert isinstance(value, int)
        assert value == 500
    
    def test_get_int_raises_on_non_integer(self, config_manager):
        """Test that get_int raises TypeError for non-integer."""
        with pytest.raises(TypeError):
            config_manager.get_int('ForvoLanguage')  # This is a string
    
    def test_get_bool_returns_boolean(self, config_manager):
        """Test that get_bool returns boolean value."""
        value = config_manager.get_bool('highlightSentences')
        assert isinstance(value, bool)
        assert value is True
    
    def test_get_bool_raises_on_non_boolean(self, config_manager):
        """Test that get_bool raises TypeError for non-boolean."""
        with pytest.raises(TypeError):
            config_manager.get_bool('maxSearch')  # This is an int
    
    def test_get_str_returns_string(self, config_manager):
        """Test that get_str returns string value."""
        value = config_manager.get_str('ForvoLanguage')
        assert isinstance(value, str)
        assert value == 'Japanese'
    
    def test_get_str_raises_on_non_string(self, config_manager):
        """Test that get_str raises TypeError for non-string."""
        with pytest.raises(TypeError):
            config_manager.get_str('maxSearch')  # This is an int
    
    def test_get_list_returns_list(self, config_manager):
        """Test that get_list returns list value."""
        value = config_manager.get_list('fontSizes')
        assert isinstance(value, list)
    
    def test_get_list_raises_on_non_list(self, config_manager):
        """Test that get_list raises TypeError for non-list."""
        with pytest.raises(TypeError):
            config_manager.get_list('maxSearch')  # This is an int
    
    def test_get_dict_returns_dict(self, config_manager):
        """Test that get_dict returns dictionary value."""
        value = config_manager.get_dict('DictionaryGroups')
        assert isinstance(value, dict)
    
    def test_get_dict_raises_on_non_dict(self, config_manager):
        """Test that get_dict raises TypeError for non-dict."""
        with pytest.raises(TypeError):
            config_manager.get_dict('maxSearch')  # This is an int


class TestConfigurationHelpers:
    """Test configuration helper methods."""
    
    def test_has_key_returns_true_for_existing_key(self, config_manager):
        """Test that has_key returns True for existing key."""
        assert config_manager.has_key('maxSearch') is True
    
    def test_has_key_returns_false_for_missing_key(self, config_manager):
        """Test that has_key returns False for missing key."""
        assert config_manager.has_key('nonexistent_key') is False
    
    def test_refresh_clears_cache(self, config_manager):
        """Test that refresh clears the cache."""
        # Load config
        config_manager.get_config()
        assert config_manager._config_cache is not None
        
        # Refresh
        config_manager.refresh()
        assert config_manager._config_cache is None
    
    def test_reset_to_defaults(self, config_manager, mock_addon_manager):
        """Test resetting configuration to defaults."""
        config_manager.reset_to_defaults()
        
        # Should have written default config
        mock_addon_manager.writeConfig.assert_called_once()
        call_args = mock_addon_manager.writeConfig.call_args
        written_config = call_args[0][1]
        
        # Verify it's the default config
        assert written_config['maxSearch'] == DEFAULT_CONFIG['maxSearch']
        assert written_config['dictSearch'] == DEFAULT_CONFIG['dictSearch']


class TestGroupedConfigAccess:
    """Test grouped configuration access methods."""
    
    def test_get_search_settings(self, config_manager):
        """Test getting search settings."""
        settings = config_manager.get_search_settings()
        
        assert 'max_search' in settings
        assert 'dict_search' in settings
        assert 'search_mode' in settings
        assert 'deinflect' in settings
        assert 'current_group' in settings
    
    def test_get_display_settings(self, config_manager):
        """Test getting display settings."""
        settings = config_manager.get_display_settings()
        
        assert 'highlight_sentences' in settings
        assert 'highlight_target' in settings
        assert 'show_target' in settings
        assert 'tooltips' in settings
        assert 'front_bracket' in settings
        assert 'back_bracket' in settings
    
    def test_get_image_settings(self, config_manager):
        """Test getting image settings."""
        settings = config_manager.get_image_settings()
        
        assert 'max_width' in settings
        assert 'max_height' in settings
        assert 'google_search_region' in settings
        assert 'safe_search' in settings
    
    def test_get_audio_settings(self, config_manager):
        """Test getting audio settings."""
        settings = config_manager.get_audio_settings()
        
        assert 'forvo_language' in settings
        assert 'mp3_convert' in settings
        assert 'condensed_audio_directory' in settings
        assert 'disable_condensed' in settings
    
    def test_get_dictionary_groups(self, config_manager):
        """Test getting dictionary groups."""
        groups = config_manager.get_dictionary_groups()
        assert isinstance(groups, dict)
    
    def test_get_export_templates(self, config_manager):
        """Test getting export templates."""
        templates = config_manager.get_export_templates()
        assert isinstance(templates, dict)


class TestInvalidConfigHandling:
    """Test handling of invalid configuration values."""
    
    def test_invalid_value_uses_default(self, mock_addon_manager):
        """Test that invalid values are replaced with defaults."""
        # Set up addon manager to return invalid config
        mock_addon_manager.getConfig = Mock(return_value={
            'maxSearch': 50000,  # Invalid - too high
            'searchMode': 'InvalidMode',  # Invalid mode
        })
        
        manager = ConfigManager(mock_addon_manager)
        config = manager.get_config()
        
        # Should use defaults for invalid values
        assert config['maxSearch'] == DEFAULT_CONFIG['maxSearch']
        assert config['searchMode'] == DEFAULT_CONFIG['searchMode']
    
    def test_unknown_keys_preserved(self, mock_addon_manager):
        """Test that unknown keys are preserved."""
        mock_addon_manager.getConfig = Mock(return_value={
            'customKey': 'customValue',
        })
        
        manager = ConfigManager(mock_addon_manager)
        config = manager.get_config()
        
        # Unknown key should be preserved
        assert config['customKey'] == 'customValue'
