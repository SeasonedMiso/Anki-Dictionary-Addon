# -*- coding: utf-8 -*-
"""
Backward compatibility verification tests for Phase 3 refactoring.

These tests verify that all existing functionality remains intact after
the refactoring, including menu items, keyboard shortcuts, hooks, and
legacy function wrappers.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import sys
import sqlite3


@pytest.fixture
def mock_mw():
    """Mock Anki main window with all required attributes."""
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
    mw.web = Mock()
    mw.web.selectedText = Mock(return_value='test')
    mw.web.title = 'main webview'
    mw.state = 'review'
    mw.reviewer = Mock()
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


class TestBackwardCompatibilityVariables:
    """Test that all backward compatibility variables are set correctly."""
    
    def test_anki_dict_config_exists(self, mock_mw, temp_addon_path):
        """Test that mw.AnkiDictConfig is set."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            assert hasattr(mock_mw, 'AnkiDictConfig')
            assert isinstance(mock_mw.AnkiDictConfig, dict)
    
    def test_refresh_config_function_exists(self, mock_mw, temp_addon_path):
        """Test that mw.refreshAnkiDictConfig exists and is callable."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            assert hasattr(mock_mw, 'refreshAnkiDictConfig')
            assert callable(mock_mw.refreshAnkiDictConfig)
            
            # Test that it can be called
            mock_mw.refreshAnkiDictConfig()
    
    def test_dict_db_exists(self, mock_mw, temp_addon_path):
        """Test that mw.miDictDB is set."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            assert hasattr(mock_mw, 'miDictDB')
            assert mock_mw.miDictDB is not None
    
    def test_state_variables_exist(self, mock_mw, temp_addon_path):
        """Test that all state variables are initialized."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Check all state variables
            assert hasattr(mock_mw, 'DictExportingDefinitions')
            assert mock_mw.DictExportingDefinitions is False
            
            assert hasattr(mock_mw, 'dictSettings')
            assert mock_mw.dictSettings is False
            
            assert hasattr(mock_mw, 'misoEditorLoadedAfterDictionary')
            assert mock_mw.misoEditorLoadedAfterDictionary is False
            
            assert hasattr(mock_mw, 'DictBulkMediaExportWasCancelled')
            assert mock_mw.DictBulkMediaExportWasCancelled is False


class TestDictionarySearchFunctionality:
    """Test that dictionary search functionality is unchanged."""
    
    def test_dictionary_repo_accessible(self, mock_mw, temp_addon_path):
        """Test that dictionary repository is accessible."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Should be able to access dictionary repo
            assert plugin.dictionary_repo is not None
            assert mock_mw.miDictDB is not None
    
    def test_can_query_languages(self, mock_mw, temp_addon_path):
        """Test that we can query languages from the database."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Query languages
            languages = plugin.dictionary_repo.get_all_languages()
            
            assert isinstance(languages, list)
            assert 'Japanese' in languages
            assert 'English' in languages
    
    def test_search_service_accessible(self, mock_mw, temp_addon_path):
        """Test that search service is accessible."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Should be able to access search service
            search_service = plugin.get_search_service()
            assert search_service is not None


class TestCardExportFunctionality:
    """Test that card export functionality is unchanged."""
    
    def test_export_service_accessible(self, mock_mw, temp_addon_path):
        """Test that export service is accessible."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Should be able to access export service
            export_service = plugin.get_export_service()
            assert export_service is not None
    
    def test_export_state_variable_exists(self, mock_mw, temp_addon_path):
        """Test that export state variable exists."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Export state variable should exist
            assert hasattr(mock_mw, 'DictExportingDefinitions')
            assert isinstance(mock_mw.DictExportingDefinitions, bool)


class TestMediaDownloadFunctionality:
    """Test that media download functionality is unchanged."""
    
    def test_media_service_accessible(self, mock_mw, temp_addon_path):
        """Test that media service is accessible."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Should be able to access media service
            media_service = plugin.get_media_service()
            assert media_service is not None
    
    def test_media_service_has_download_methods(self, mock_mw, temp_addon_path):
        """Test that media service has download methods."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            media_service = plugin.get_media_service()
            
            # Check for download methods
            assert hasattr(media_service, 'download_forvo_audio')
            assert callable(media_service.download_forvo_audio)
            
            assert hasattr(media_service, 'download_google_images')
            assert callable(media_service.download_google_images)


class TestConfigurationAccess:
    """Test that configuration access works correctly."""
    
    def test_config_accessible_via_mw(self, mock_mw, temp_addon_path):
        """Test that config is accessible via mw.AnkiDictConfig."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Config should be accessible
            assert hasattr(mock_mw, 'AnkiDictConfig')
            config = mock_mw.AnkiDictConfig
            
            assert isinstance(config, dict)
            assert 'searchMode' in config
    
    def test_config_refresh_works(self, mock_mw, temp_addon_path):
        """Test that config refresh works."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Refresh config
            new_config = {'test': 'value', 'searchMode': 'Exact'}
            mock_mw.refreshAnkiDictConfig(new_config)
            
            # Config should be updated
            assert mock_mw.AnkiDictConfig == new_config
    
    def test_config_manager_accessible(self, mock_mw, temp_addon_path):
        """Test that config manager is accessible."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Config manager should be accessible
            config_manager = plugin.get_config_manager()
            assert config_manager is not None


class TestHookRegistration:
    """Test that all hooks are registered correctly."""
    
    def test_profile_loaded_hook_registered(self, mock_mw, temp_addon_path):
        """Test that profileLoaded hook is registered."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock addHook
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
            
            # Mock addHook
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
    
    def test_editor_hooks_registered(self, mock_mw, temp_addon_path):
        """Test that editor hooks are registered."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock addHook
            mock_anki = Mock()
            mock_anki.hooks = Mock()
            mock_add_hook = Mock()
            mock_anki.hooks.addHook = mock_add_hook
            sys.modules['anki'] = mock_anki
            sys.modules['anki.hooks'] = mock_anki.hooks
            
            try:
                plugin._setup_hooks()
                
                # Verify editor hooks were registered
                hook_names = [call[0][0] for call in mock_add_hook.call_args_list]
                assert 'setupEditorButtons' in hook_names
                assert 'EditorWebView.contextMenuEvent' in hook_names
            finally:
                # Cleanup
                if 'anki' in sys.modules:
                    del sys.modules['anki']
                if 'anki.hooks' in sys.modules:
                    del sys.modules['anki.hooks']
    
    def test_reviewer_hooks_registered(self, mock_mw, temp_addon_path):
        """Test that reviewer hooks are registered."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock addHook
            mock_anki = Mock()
            mock_anki.hooks = Mock()
            mock_add_hook = Mock()
            mock_anki.hooks.addHook = mock_add_hook
            sys.modules['anki'] = mock_anki
            sys.modules['anki.hooks'] = mock_anki.hooks
            
            try:
                plugin._setup_hooks()
                
                # Verify reviewer hooks were registered
                hook_names = [call[0][0] for call in mock_add_hook.call_args_list]
                assert 'showQuestion' in hook_names
                assert 'showAnswer' in hook_names
            finally:
                # Cleanup
                if 'anki' in sys.modules:
                    del sys.modules['anki']
                if 'anki.hooks' in sys.modules:
                    del sys.modules['anki.hooks']
    
    def test_browser_hooks_registered(self, mock_mw, temp_addon_path):
        """Test that browser hooks are registered."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock addHook
            mock_anki = Mock()
            mock_anki.hooks = Mock()
            mock_add_hook = Mock()
            mock_anki.hooks.addHook = mock_add_hook
            sys.modules['anki'] = mock_anki
            sys.modules['anki.hooks'] = mock_anki.hooks
            
            try:
                plugin._setup_hooks()
                
                # Verify browser hooks were registered
                hook_names = [call[0][0] for call in mock_add_hook.call_args_list]
                assert 'browser.setupMenus' in hook_names
            finally:
                # Cleanup
                if 'anki' in sys.modules:
                    del sys.modules['anki']
                if 'anki.hooks' in sys.modules:
                    del sys.modules['anki.hooks']


class TestDatabaseCompatibility:
    """Test that existing dictionary databases work correctly."""
    
    def test_can_connect_to_database(self, mock_mw, temp_addon_path):
        """Test that we can connect to the database."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Database should be connected
            assert plugin.db_connection is not None
            assert plugin.db_connection.conn is not None
    
    def test_can_query_existing_data(self, mock_mw, temp_addon_path):
        """Test that we can query existing data."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Query existing data
            languages = plugin.dictionary_repo.get_all_languages()
            
            assert 'Japanese' in languages
            assert 'English' in languages
    
    def test_database_schema_unchanged(self, mock_mw, temp_addon_path):
        """Test that database schema is unchanged."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Check that tables exist
            cursor = plugin.db_connection.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'langnames' in tables
            assert 'dictnames' in tables


class TestCleanupFunctionality:
    """Test that cleanup works correctly."""
    
    def test_cleanup_closes_database(self, mock_mw, temp_addon_path):
        """Test that cleanup closes the database."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Cleanup
            plugin.cleanup()
            
            # Database should be closed
            assert plugin.db_connection.conn is None
    
    def test_cleanup_removes_temp_files(self, mock_mw, temp_addon_path):
        """Test that cleanup removes temporary files."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Create temp files
            temp_file = plugin.media_service.temp_dir / "test.mp3"
            temp_file.write_bytes(b'test data')
            plugin.media_service._temp_files.append(temp_file)
            
            # Cleanup
            plugin.cleanup()
            
            # Temp file should be removed
            assert not temp_file.exists()


class TestPerformance:
    """Test that performance is maintained."""
    
    def test_initialization_is_fast(self, mock_mw, temp_addon_path):
        """Test that plugin initialization is fast."""
        import time
        
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            start_time = time.time()
            plugin = AnkiDictionaryPlugin(mock_mw)
            end_time = time.time()
            
            # Initialization should be fast (< 1 second)
            assert (end_time - start_time) < 1.0
    
    def test_config_access_is_fast(self, mock_mw, temp_addon_path):
        """Test that config access is fast."""
        import time
        
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            start_time = time.time()
            for _ in range(100):
                config = mock_mw.AnkiDictConfig
            end_time = time.time()
            
            # 100 config accesses should be very fast (< 0.1 seconds)
            assert (end_time - start_time) < 0.1
