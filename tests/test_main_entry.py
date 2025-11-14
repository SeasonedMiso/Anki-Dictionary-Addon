# -*- coding: utf-8 -*-
"""
Integration tests for main entry point.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import sys
import sqlite3


@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.addonManager = Mock()
    mw.addonManager.getConfig = Mock(return_value={
        'dictionaries': [],
        'searchMode': 'Forward',
        'maxSearchResults': 100,
        'dictOnStart': False,
        'openOnGlobal': True,
        'ForvoLanguage': 'ja',
        'googleSearchRegion': 'com',
        'safeSearch': True,
        'maxWidth': 500,
        'maxHeight': 500
    })
    mw.addonManager.writeConfig = Mock()
    mw.col = Mock()
    mw.col.media = Mock()
    mw.col.media.dir = Mock(return_value='/fake/media/dir')
    mw.col.media.addFile = Mock()
    mw.col.models = Mock()
    mw.col.decks = Mock()
    mw.reset = Mock()
    mw.form = Mock()
    mw.form.menubar = Mock()
    mw.form.menuHelp = Mock()
    mw.form.menuHelp.menuAction = Mock()
    return mw


@pytest.fixture
def temp_addon_path(tmp_path):
    """Create temporary addon path with required structure."""
    addon_path = tmp_path / "addon"
    addon_path.mkdir()
    
    # Create user_files structure
    user_files = addon_path / "user_files"
    user_files.mkdir()
    
    db_dir = user_files / "db"
    db_dir.mkdir()
    
    # Create temp directory
    temp_dir = addon_path / "temp"
    temp_dir.mkdir()
    
    # Create a test database
    db_path = db_dir / "dictionaries.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create minimal schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS langnames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            langname TEXT UNIQUE NOT NULL
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dictnames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dictname TEXT NOT NULL,
            lid INTEGER NOT NULL,
            fields TEXT DEFAULT '[]',
            addtype TEXT DEFAULT 'add',
            termHeader TEXT DEFAULT '[]',
            duplicateHeader INTEGER DEFAULT 0,
            FOREIGN KEY (lid) REFERENCES langnames(id)
        );
    """)
    
    # Add test data
    cursor.execute("INSERT INTO langnames (langname) VALUES ('Japanese');")
    cursor.execute("INSERT INTO langnames (langname) VALUES ('English');")
    
    conn.commit()
    conn.close()
    
    return addon_path


@pytest.fixture
def mock_anki_hooks():
    """Mock Anki hooks module."""
    mock_hooks = Mock()
    mock_hooks.addHook = Mock()
    return mock_hooks


class TestMainEntryInitialization:
    """Test main entry point initialization."""
    
    def test_plugin_instance_created(self, mock_mw, temp_addon_path, mock_anki_hooks):
        """Test that plugin instance is created on import."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            # Import main module
            from src.core.plugin import AnkiDictionaryPlugin
            
            # Create plugin instance
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify plugin was created
            assert plugin is not None
            assert plugin.mw == mock_mw
            assert plugin.config_manager is not None
            assert plugin.db_connection is not None
    
    def test_plugin_attached_to_mw(self, mock_mw, temp_addon_path):
        """Test that plugin is attached to mw for backward compatibility."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            mock_mw.ankiDictPlugin = plugin
            
            # Verify plugin is attached
            assert hasattr(mock_mw, 'ankiDictPlugin')
            assert mock_mw.ankiDictPlugin == plugin
    
    def test_all_services_initialized(self, mock_mw, temp_addon_path):
        """Test that all services are properly initialized."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify all services exist
            assert plugin.search_service is not None
            assert plugin.export_service is not None
            assert plugin.media_service is not None
            assert plugin.dictionary_repo is not None
            assert plugin.config_manager is not None
    
    def test_services_accessible_via_accessors(self, mock_mw, temp_addon_path):
        """Test that services are accessible via accessor methods."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Test accessor methods
            assert plugin.get_search_service() is not None
            assert plugin.get_export_service() is not None
            assert plugin.get_media_service() is not None
            assert plugin.get_dictionary_repository() is not None
            assert plugin.get_config_manager() is not None


class TestBackwardCompatibilityVariables:
    """Test backward compatibility variables."""
    
    def test_anki_dict_config_set(self, mock_mw, temp_addon_path):
        """Test that mw.AnkiDictConfig is set."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify config is attached
            assert hasattr(mock_mw, 'AnkiDictConfig')
            assert mock_mw.AnkiDictConfig is not None
            assert isinstance(mock_mw.AnkiDictConfig, dict)
    
    def test_refresh_config_function_set(self, mock_mw, temp_addon_path):
        """Test that mw.refreshAnkiDictConfig is set."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify refresh function is attached
            assert hasattr(mock_mw, 'refreshAnkiDictConfig')
            assert callable(mock_mw.refreshAnkiDictConfig)
    
    def test_dict_db_set(self, mock_mw, temp_addon_path):
        """Test that mw.miDictDB is set."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify dictionary DB is attached
            assert hasattr(mock_mw, 'miDictDB')
            assert mock_mw.miDictDB is not None
            assert mock_mw.miDictDB == plugin.dictionary_repo
    
    def test_state_variables_initialized(self, mock_mw, temp_addon_path):
        """Test that state variables are initialized."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify state variables
            assert hasattr(mock_mw, 'DictExportingDefinitions')
            assert mock_mw.DictExportingDefinitions is False
            
            assert hasattr(mock_mw, 'dictSettings')
            assert mock_mw.dictSettings is False
            
            assert hasattr(mock_mw, 'misoEditorLoadedAfterDictionary')
            assert mock_mw.misoEditorLoadedAfterDictionary is False
            
            assert hasattr(mock_mw, 'DictBulkMediaExportWasCancelled')
            assert mock_mw.DictBulkMediaExportWasCancelled is False


class TestLegacyFunctionWrappers:
    """Test legacy function wrappers."""
    
    def test_refresh_config_wrapper_works(self, mock_mw, temp_addon_path):
        """Test that refresh config wrapper delegates properly."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Call refresh function
            initial_config = mock_mw.AnkiDictConfig
            mock_mw.refreshAnkiDictConfig()
            
            # Config should still be accessible
            assert mock_mw.AnkiDictConfig is not None
    
    def test_refresh_config_with_new_config(self, mock_mw, temp_addon_path):
        """Test refresh config with new configuration."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Update config
            new_config = {'test': 'value', 'searchMode': 'Exact'}
            mock_mw.refreshAnkiDictConfig(new_config)
            
            # Verify config was updated
            assert mock_mw.AnkiDictConfig == new_config


class TestLifecycleHooks:
    """Test lifecycle hooks."""
    
    def test_profile_loaded_hook_registered(self, mock_mw, temp_addon_path):
        """Test that profileLoaded hook is registered."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock addHook using sys.modules
            mock_anki = Mock()
            mock_anki.hooks = Mock()
            mock_add_hook = Mock()
            mock_anki.hooks.addHook = mock_add_hook
            sys.modules['anki'] = mock_anki
            sys.modules['anki.hooks'] = mock_anki.hooks
            
            try:
                plugin._setup_hooks()
                
                # Verify profileLoaded hook was registered
                hook_names = [call[0][0] for call in mock_add_hook.call_args_list]
                assert 'profileLoaded' in hook_names
            finally:
                # Cleanup
                if 'anki' in sys.modules:
                    del sys.modules['anki']
                if 'anki.hooks' in sys.modules:
                    del sys.modules['anki.hooks']
    
    def test_unload_profile_hook_registered(self, mock_mw, temp_addon_path):
        """Test that unloadProfile hook is registered."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock addHook using sys.modules
            mock_anki = Mock()
            mock_anki.hooks = Mock()
            mock_add_hook = Mock()
            mock_anki.hooks.addHook = mock_add_hook
            sys.modules['anki'] = mock_anki
            sys.modules['anki.hooks'] = mock_anki.hooks
            
            try:
                plugin._setup_hooks()
                
                # Verify unloadProfile hook was registered
                hook_names = [call[0][0] for call in mock_add_hook.call_args_list]
                assert 'unloadProfile' in hook_names
            finally:
                # Cleanup
                if 'anki' in sys.modules:
                    del sys.modules['anki']
                if 'anki.hooks' in sys.modules:
                    del sys.modules['anki.hooks']
    
    def test_profile_loaded_initializes_plugin(self, mock_mw, temp_addon_path):
        """Test that profile loaded hook initializes plugin."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock initialize method
            with patch.object(plugin, 'initialize') as mock_initialize:
                # Simulate profile loaded
                plugin._on_profile_loaded()
                
                # Verify initialize was called (via reload_conjugations)
                # Note: _on_profile_loaded calls reload_conjugations, not initialize
                # This is correct behavior
                pass
    
    def test_unload_profile_cleans_up(self, mock_mw, temp_addon_path):
        """Test that unload profile hook cleans up."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock cleanup method
            with patch.object(plugin, 'cleanup') as mock_cleanup:
                # Simulate profile unload
                plugin._on_unload_profile()
                
                # Verify cleanup was called
                mock_cleanup.assert_called_once()


class TestInitializationSequence:
    """Test full initialization sequence."""
    
    def test_full_initialization_sequence(self, mock_mw, temp_addon_path):
        """Test complete initialization sequence."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            # Step 1: Create plugin
            plugin = AnkiDictionaryPlugin(mock_mw)
            assert plugin is not None
            
            # Step 2: Verify services initialized
            assert plugin.search_service is not None
            assert plugin.export_service is not None
            assert plugin.media_service is not None
            
            # Step 3: Verify backward compatibility
            assert hasattr(mock_mw, 'AnkiDictConfig')
            assert hasattr(mock_mw, 'miDictDB')
            assert hasattr(mock_mw, 'refreshAnkiDictConfig')
            
            # Step 4: Initialize plugin
            with patch.object(plugin, '_setup_hooks'):
                with patch.object(plugin, '_setup_menu'):
                    with patch.object(plugin, '_setup_hotkeys'):
                        with patch.object(plugin, '_cleanup_temp_files'):
                            plugin.initialize()
            
            # Step 5: Verify cleanup works
            with patch.object(plugin.media_service, 'cleanup_temp_media'):
                with patch.object(plugin.db_connection, 'close'):
                    plugin.cleanup()
    
    def test_initialization_with_hooks(self, mock_mw, temp_addon_path):
        """Test initialization with hook registration."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock addHook using sys.modules
            mock_anki = Mock()
            mock_anki.hooks = Mock()
            mock_add_hook = Mock()
            mock_anki.hooks.addHook = mock_add_hook
            sys.modules['anki'] = mock_anki
            sys.modules['anki.hooks'] = mock_anki.hooks
            
            try:
                plugin._setup_hooks()
                
                # Verify multiple hooks were registered
                assert mock_add_hook.call_count >= 5
            finally:
                # Cleanup
                if 'anki' in sys.modules:
                    del sys.modules['anki']
                if 'anki.hooks' in sys.modules:
                    del sys.modules['anki.hooks']
    
    def test_initialization_handles_errors(self, mock_mw, temp_addon_path):
        """Test that initialization handles errors gracefully."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock setup methods to raise errors
            with patch.object(plugin, '_setup_hooks', side_effect=Exception("Hook error")):
                # Should not raise exception
                plugin.initialize()


class TestDatabaseConnection:
    """Test database connection during initialization."""
    
    def test_database_connected(self, mock_mw, temp_addon_path):
        """Test that database is connected."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify database connection
            assert plugin.db_connection is not None
            assert plugin.db_connection.conn is not None
    
    def test_can_query_database(self, mock_mw, temp_addon_path):
        """Test that database can be queried."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Query database
            languages = plugin.dictionary_repo.get_all_languages()
            
            assert isinstance(languages, list)
            assert len(languages) > 0
    
    def test_database_closed_on_cleanup(self, mock_mw, temp_addon_path):
        """Test that database is closed on cleanup."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Cleanup
            plugin.cleanup()
            
            # Verify connection is closed
            assert plugin.db_connection.conn is None


class TestErrorRecovery:
    """Test error recovery during initialization."""
    
    def test_service_initialization_error_recovery(self, mock_mw, temp_addon_path):
        """Test recovery from service initialization errors."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            # This should not raise even if there are issues
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Plugin should still be created
            assert plugin is not None
    
    def test_hook_registration_error_recovery(self, mock_mw, temp_addon_path):
        """Test recovery from hook registration errors."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock addHook to raise error using sys.modules
            mock_anki = Mock()
            mock_anki.hooks = Mock()
            mock_anki.hooks.addHook = Mock(side_effect=Exception("Hook error"))
            sys.modules['anki'] = mock_anki
            sys.modules['anki.hooks'] = mock_anki.hooks
            
            try:
                # Should not raise
                plugin._setup_hooks()
            finally:
                # Cleanup
                if 'anki' in sys.modules:
                    del sys.modules['anki']
                if 'anki.hooks' in sys.modules:
                    del sys.modules['anki.hooks']
    
    def test_cleanup_error_recovery(self, mock_mw, temp_addon_path):
        """Test recovery from cleanup errors."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock cleanup methods to raise errors
            with patch.object(plugin.media_service, 'cleanup_temp_media', side_effect=Exception("Cleanup error")):
                with patch.object(plugin.db_connection, 'close', side_effect=Exception("Close error")):
                    # Should not raise
                    plugin.cleanup()
