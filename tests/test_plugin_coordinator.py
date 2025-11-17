# -*- coding: utf-8 -*-
"""
Tests for plugin coordinator module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from pathlib import Path
import tempfile
import sqlite3

from src.core.plugin import AnkiDictionaryPlugin
from src.config.manager import ConfigManager
from src.database.connection import DatabaseConnection
from src.database.repository import DictionaryRepository
from src.services.search_service import SearchService
from src.services.export_service import ExportService
from src.services.media_service import MediaService


@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.addonManager = Mock()
    mw.addonManager.getConfig = Mock(return_value={
        'dictionaries': [],
        'searchMode': 'Forward',
        'maxSearchResults': 100
    })
    mw.addonManager.writeConfig = Mock()
    mw.col = Mock()
    mw.col.media = Mock()
    mw.col.media.dir = Mock(return_value='/fake/media/dir')
    mw.col.media.addFile = Mock()
    mw.col.models = Mock()
    mw.col.decks = Mock()
    mw.reset = Mock()
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
def plugin(mock_mw, temp_addon_path, monkeypatch):
    """Create plugin instance for testing."""
    # Mock the addon path
    with patch('src.core.plugin.Path') as mock_path:
        mock_path.return_value.parent.parent.parent = temp_addon_path
        
        # Create plugin with mocked path
        plugin = AnkiDictionaryPlugin.__new__(AnkiDictionaryPlugin)
        plugin.mw = mock_mw
        plugin.addon_path = temp_addon_path
        plugin.version = "1.0.0"
        
        # Initialize components
        plugin.config_manager = ConfigManager(mock_mw.addonManager)
        
        db_path = temp_addon_path / 'user_files' / 'db' / 'dictionaries.db'
        plugin.db_connection = DatabaseConnection(str(db_path))
        plugin.dictionary_repo = DictionaryRepository(plugin.db_connection)
        
        plugin.search_service = SearchService(
            plugin.dictionary_repo,
            temp_addon_path
        )
        plugin.export_service = ExportService(mock_mw)
        plugin.media_service = MediaService(
            mock_mw,
            plugin.config_manager,
            temp_addon_path
        )
        
        # UI Components (lazy initialization)
        plugin._dictionary_window = None
        plugin._settings_window = None
        plugin._dictionary_manager = None
        plugin._editor_integration = None
        plugin._browser_integration = None
        plugin._menu_manager = None
        
        # Initialize state
        plugin._initialize_state()
        
        yield plugin
        
        # Cleanup
        plugin.cleanup()


class TestPluginInitialization:
    """Test plugin initialization."""
    
    def test_plugin_creation(self, plugin, mock_mw, temp_addon_path):
        """Test creating a plugin instance."""
        assert plugin.mw == mock_mw
        assert plugin.addon_path == temp_addon_path
        assert plugin.version == "1.0.0"
        assert plugin.config_manager is not None
        assert plugin.db_connection is not None
        assert plugin.dictionary_repo is not None
        assert plugin.search_service is not None
        assert plugin.export_service is not None
        assert plugin.media_service is not None
    
    def test_state_initialization(self, plugin, mock_mw):
        """Test that state is properly initialized."""
        assert hasattr(mock_mw, 'AnkiDictConfig')
        assert hasattr(mock_mw, 'DictExportingDefinitions')
        assert hasattr(mock_mw, 'dictSettings')
        assert hasattr(mock_mw, 'misoEditorLoadedAfterDictionary')
        assert hasattr(mock_mw, 'DictBulkMediaExportWasCancelled')
        assert hasattr(mock_mw, 'refreshAnkiDictConfig')
        assert hasattr(mock_mw, 'miDictDB')
        
        assert mock_mw.DictExportingDefinitions is False
        assert mock_mw.dictSettings is False
        assert mock_mw.misoEditorLoadedAfterDictionary is False
        assert mock_mw.DictBulkMediaExportWasCancelled is False
        assert mock_mw.miDictDB == plugin.dictionary_repo
    
    def test_services_initialized(self, plugin):
        """Test that all services are properly initialized."""
        assert isinstance(plugin.search_service, SearchService)
        assert isinstance(plugin.export_service, ExportService)
        assert isinstance(plugin.media_service, MediaService)
        assert isinstance(plugin.dictionary_repo, DictionaryRepository)
        assert isinstance(plugin.config_manager, ConfigManager)


class TestServiceAccessors:
    """Test service accessor methods."""
    
    def test_get_search_service(self, plugin):
        """Test getting search service."""
        service = plugin.get_search_service()
        
        assert service is plugin.search_service
        assert isinstance(service, SearchService)
    
    def test_get_export_service(self, plugin):
        """Test getting export service."""
        service = plugin.get_export_service()
        
        assert service is plugin.export_service
        assert isinstance(service, ExportService)
    
    def test_get_media_service(self, plugin):
        """Test getting media service."""
        service = plugin.get_media_service()
        
        assert service is plugin.media_service
        assert isinstance(service, MediaService)
    
    def test_get_dictionary_repository(self, plugin):
        """Test getting dictionary repository."""
        repo = plugin.get_dictionary_repository()
        
        assert repo is plugin.dictionary_repo
        assert isinstance(repo, DictionaryRepository)
    
    def test_get_config_manager(self, plugin):
        """Test getting config manager."""
        manager = plugin.get_config_manager()
        
        assert manager is plugin.config_manager
        assert isinstance(manager, ConfigManager)


class TestConfigurationManagement:
    """Test configuration management."""
    
    def test_refresh_config_without_param(self, plugin, mock_mw):
        """Test refreshing config without providing new config."""
        initial_config = mock_mw.AnkiDictConfig
        
        plugin.refresh_config()
        
        # Config should be refreshed
        assert mock_mw.AnkiDictConfig is not None
    
    def test_refresh_config_with_param(self, plugin, mock_mw):
        """Test refreshing config with new config."""
        new_config = {'test': 'value', 'searchMode': 'Exact'}
        
        plugin.refresh_config(new_config)
        
        assert mock_mw.AnkiDictConfig == new_config
        # ConfigManager.write_config is called with module name and config
        assert mock_mw.addonManager.writeConfig.called
    
    def test_config_change_notification(self, plugin):
        """Test that config changes notify services."""
        with patch.object(plugin.search_service, 'reload_conjugations') as mock_reload:
            plugin.refresh_config({'test': 'value'})
            
            # Should trigger conjugation reload
            mock_reload.assert_called_once()


class TestHookRegistration:
    """Test hook registration."""
    
    def test_setup_hooks(self, plugin):
        """Test that hooks are registered."""
        # Mock addHook at the module level where it's imported
        import sys
        mock_anki = Mock()
        mock_anki.hooks = Mock()
        mock_add_hook = Mock()
        mock_anki.hooks.addHook = mock_add_hook
        sys.modules['anki'] = mock_anki
        sys.modules['anki.hooks'] = mock_anki.hooks
        
        try:
            plugin._setup_hooks()
            
            # Verify hooks were registered
            hook_names = [call[0][0] for call in mock_add_hook.call_args_list]
            
            assert 'setupEditorButtons' in hook_names
            assert 'EditorWebView.contextMenuEvent' in hook_names
            assert 'showQuestion' in hook_names
            assert 'showAnswer' in hook_names
            assert 'browser.setupMenus' in hook_names
            assert 'profileLoaded' in hook_names
            assert 'unloadProfile' in hook_names
            assert 'prepareFields' in hook_names
        finally:
            # Cleanup
            if 'anki' in sys.modules:
                del sys.modules['anki']
            if 'anki.hooks' in sys.modules:
                del sys.modules['anki.hooks']
    
    def test_hook_handlers_exist(self, plugin):
        """Test that hook handler methods exist."""
        assert hasattr(plugin, '_on_setup_editor_buttons')
        assert hasattr(plugin, '_on_editor_context_menu')
        assert hasattr(plugin, '_on_show_question')
        assert hasattr(plugin, '_on_show_answer')
        assert hasattr(plugin, '_on_browser_setup_menus')
        assert hasattr(plugin, '_on_profile_loaded')
        assert hasattr(plugin, '_on_unload_profile')
        assert hasattr(plugin, '_on_prepare_fields')
    
    def test_profile_loaded_hook(self, plugin):
        """Test profile loaded hook handler."""
        with patch.object(plugin.search_service, 'reload_conjugations') as mock_reload:
            plugin._on_profile_loaded()
            
            # Should reload conjugations
            mock_reload.assert_called_once()
    
    def test_unload_profile_hook(self, plugin):
        """Test unload profile hook handler."""
        with patch.object(plugin, 'cleanup') as mock_cleanup:
            plugin._on_unload_profile()
            
            # Should trigger cleanup
            mock_cleanup.assert_called_once()


class TestCleanup:
    """Test cleanup functionality."""
    
    def test_cleanup_method(self, plugin):
        """Test cleanup method."""
        with patch.object(plugin.media_service, 'cleanup_temp_media') as mock_media_cleanup:
            with patch.object(plugin.db_connection, 'close') as mock_db_close:
                plugin.cleanup()
                
                # Should clean up media and close database
                mock_media_cleanup.assert_called_once()
                mock_db_close.assert_called_once()
    
    def test_cleanup_temp_files(self, plugin):
        """Test temporary file cleanup."""
        with patch.object(plugin.media_service, 'cleanup_temp_media') as mock_cleanup:
            plugin._cleanup_temp_files()
            
            mock_cleanup.assert_called_once()
    
    def test_cleanup_handles_errors(self, plugin):
        """Test that cleanup handles errors gracefully."""
        with patch.object(plugin.media_service, 'cleanup_temp_media', side_effect=Exception("Test error")):
            # Should not raise exception
            plugin.cleanup()


class TestInitializeMethod:
    """Test initialize method."""
    
    def test_initialize_calls_setup_methods(self, plugin):
        """Test that initialize calls all setup methods."""
        with patch.object(plugin, '_setup_hooks') as mock_hooks:
            with patch.object(plugin, '_setup_ui') as mock_ui:
                with patch.object(plugin, '_cleanup_temp_files') as mock_cleanup:
                    plugin.initialize()
                    
                    mock_hooks.assert_called_once()
                    mock_ui.assert_called_once()
                    mock_cleanup.assert_called_once()
    
    def test_initialize_handles_errors(self, plugin):
        """Test that initialize handles errors gracefully."""
        with patch.object(plugin, '_setup_hooks', side_effect=Exception("Test error")):
            # Should not raise exception
            plugin.initialize()


class TestBackwardCompatibility:
    """Test backward compatibility features."""
    
    def test_mw_attachments(self, plugin, mock_mw):
        """Test that required attributes are attached to mw."""
        assert hasattr(mock_mw, 'AnkiDictConfig')
        assert hasattr(mock_mw, 'refreshAnkiDictConfig')
        assert hasattr(mock_mw, 'miDictDB')
        
        # Test that refresh callback works
        assert callable(mock_mw.refreshAnkiDictConfig)
        mock_mw.refreshAnkiDictConfig()  # Should not raise
    
    def test_dictionary_repo_accessible_via_mw(self, plugin, mock_mw):
        """Test that dictionary repo is accessible via mw for backward compatibility."""
        assert mock_mw.miDictDB == plugin.dictionary_repo


class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_database_connection_established(self, plugin):
        """Test that database connection is established."""
        assert plugin.db_connection is not None
        assert plugin.db_connection.conn is not None
    
    def test_can_query_database(self, plugin):
        """Test that we can query the database."""
        languages = plugin.dictionary_repo.get_all_languages()
        
        assert isinstance(languages, list)
        assert 'Japanese' in languages
        assert 'English' in languages
    
    def test_database_closed_on_cleanup(self, plugin):
        """Test that database is closed on cleanup."""
        # Get connection reference
        conn = plugin.db_connection.conn
        
        # Cleanup
        plugin.cleanup()
        
        # Connection should be closed
        assert plugin.db_connection.conn is None


class TestUIComponentInitialization:
    """Test UI component initialization."""
    
    def test_setup_ui_creates_ui_components(self, plugin):
        """Test that _setup_ui creates UI components."""
        # Call _setup_ui
        plugin._setup_ui()
        
        # UI components should be initialized
        assert plugin._menu_manager is not None
        assert plugin._editor_integration is not None
        assert plugin._browser_integration is not None
    
    def test_setup_ui_handles_errors(self, plugin):
        """Test that _setup_ui handles errors gracefully."""
        # Temporarily break the UI module import
        import sys
        original_ui = sys.modules.get('src.ui')
        
        # Create a mock that raises an error
        mock_ui = Mock()
        mock_ui.MenuManager = Mock(side_effect=Exception("UI error"))
        sys.modules['src.ui'] = mock_ui
        
        try:
            # Should not raise exception
            plugin._setup_ui()
        finally:
            # Restore original module
            if original_ui is not None:
                sys.modules['src.ui'] = original_ui
            elif 'src.ui' in sys.modules:
                del sys.modules['src.ui']


class TestUIComponentAccessors:
    """Test UI component accessor methods."""
    
    def test_get_dictionary_window_lazy_initialization(self, plugin):
        """Test that dictionary window is lazily initialized."""
        assert plugin._dictionary_window is None
        
        # Get window - should create it
        window = plugin.get_dictionary_window()
        
        # Window should be created
        assert window is not None
        assert plugin._dictionary_window is window
    
    def test_get_dictionary_window_returns_existing(self, plugin):
        """Test that get_dictionary_window returns existing instance."""
        mock_window = Mock()
        plugin._dictionary_window = mock_window
        
        window = plugin.get_dictionary_window()
        
        assert window == mock_window
    
    def test_get_settings_window_lazy_initialization(self, plugin):
        """Test that settings window is lazily initialized."""
        assert plugin._settings_window is None
        
        # Get window - should create it
        window = plugin.get_settings_window()
        
        # Window should be created
        assert window is not None
        assert plugin._settings_window is window
    
    def test_get_settings_window_returns_existing(self, plugin):
        """Test that get_settings_window returns existing instance."""
        mock_window = Mock()
        plugin._settings_window = mock_window
        
        window = plugin.get_settings_window()
        
        assert window == mock_window
    
    def test_get_dictionary_manager_lazy_initialization(self, plugin):
        """Test that dictionary manager is lazily initialized."""
        assert plugin._dictionary_manager is None
        
        # Get manager - should create it
        manager = plugin.get_dictionary_manager()
        
        # Manager should be created
        assert manager is not None
        assert plugin._dictionary_manager is manager
    
    def test_get_dictionary_manager_returns_existing(self, plugin):
        """Test that get_dictionary_manager returns existing instance."""
        mock_manager = Mock()
        plugin._dictionary_manager = mock_manager
        
        manager = plugin.get_dictionary_manager()
        
        assert manager == mock_manager
    
    def test_get_menu_manager(self, plugin):
        """Test getting menu manager."""
        mock_menu = Mock()
        plugin._menu_manager = mock_menu
        
        menu = plugin.get_menu_manager()
        
        assert menu == mock_menu
    
    def test_get_editor_integration(self, plugin):
        """Test getting editor integration."""
        mock_editor = Mock()
        plugin._editor_integration = mock_editor
        
        editor = plugin.get_editor_integration()
        
        assert editor == mock_editor
    
    def test_get_browser_integration(self, plugin):
        """Test getting browser integration."""
        mock_browser = Mock()
        plugin._browser_integration = mock_browser
        
        browser = plugin.get_browser_integration()
        
        assert browser == mock_browser


class TestUIWindowOperations:
    """Test UI window opening and closing operations."""
    
    def test_open_dictionary(self, plugin):
        """Test opening dictionary window."""
        mock_window = Mock()
        plugin._dictionary_window = mock_window
        
        plugin.open_dictionary(['test', 'terms'])
        
        mock_window.show_window.assert_called_once_with(['test', 'terms'])
    
    def test_open_dictionary_without_terms(self, plugin):
        """Test opening dictionary window without terms."""
        mock_window = Mock()
        plugin._dictionary_window = mock_window
        
        plugin.open_dictionary()
        
        mock_window.show_window.assert_called_once_with(None)
    
    def test_close_dictionary(self, plugin):
        """Test closing dictionary window."""
        mock_window = Mock()
        mock_window.isVisible.return_value = True
        plugin._dictionary_window = mock_window
        
        plugin.close_dictionary()
        
        mock_window.hide.assert_called_once()
    
    def test_close_dictionary_when_not_visible(self, plugin):
        """Test closing dictionary window when not visible."""
        mock_window = Mock()
        mock_window.isVisible.return_value = False
        plugin._dictionary_window = mock_window
        
        plugin.close_dictionary()
        
        mock_window.hide.assert_not_called()
    
    def test_close_dictionary_when_none(self, plugin):
        """Test closing dictionary window when it doesn't exist."""
        plugin._dictionary_window = None
        
        # Should not raise exception
        plugin.close_dictionary()
    
    def test_open_settings(self, plugin):
        """Test opening settings window."""
        mock_window = Mock()
        plugin._settings_window = mock_window
        
        plugin.open_settings()
        
        mock_window.show.assert_called_once()
        mock_window.raise_.assert_called_once()
        mock_window.activateWindow.assert_called_once()
    
    def test_open_dictionary_manager(self, plugin):
        """Test opening dictionary manager."""
        mock_manager = Mock()
        plugin._dictionary_manager = mock_manager
        
        plugin.open_dictionary_manager()
        
        mock_manager.show.assert_called_once()
        mock_manager.raise_.assert_called_once()
        mock_manager.activateWindow.assert_called_once()


class TestUICleanup:
    """Test UI resource cleanup."""
    
    def test_cleanup_ui_resources_closes_dictionary_window(self, plugin):
        """Test that cleanup closes dictionary window."""
        mock_window = Mock()
        plugin._dictionary_window = mock_window
        
        plugin._cleanup_ui_resources()
        
        mock_window.close.assert_called_once()
        assert plugin._dictionary_window is None
    
    def test_cleanup_ui_resources_closes_settings_window(self, plugin):
        """Test that cleanup closes settings window."""
        mock_window = Mock()
        plugin._settings_window = mock_window
        
        plugin._cleanup_ui_resources()
        
        mock_window.close.assert_called_once()
        assert plugin._settings_window is None
    
    def test_cleanup_ui_resources_closes_dictionary_manager(self, plugin):
        """Test that cleanup closes dictionary manager."""
        mock_manager = Mock()
        plugin._dictionary_manager = mock_manager
        
        plugin._cleanup_ui_resources()
        
        mock_manager.close.assert_called_once()
        assert plugin._dictionary_manager is None
    
    def test_cleanup_ui_resources_handles_errors(self, plugin):
        """Test that UI cleanup handles errors gracefully."""
        mock_window = Mock()
        mock_window.close.side_effect = Exception("Close error")
        plugin._dictionary_window = mock_window
        
        # Should not raise exception
        plugin._cleanup_ui_resources()
        
        # Window reference should still be cleared
        assert plugin._dictionary_window is None
    
    def test_cleanup_calls_cleanup_ui_resources(self, plugin):
        """Test that cleanup calls _cleanup_ui_resources."""
        with patch.object(plugin, '_cleanup_ui_resources') as mock_ui_cleanup:
            with patch.object(plugin.media_service, 'cleanup_temp_media'):
                with patch.object(plugin.db_connection, 'close'):
                    plugin.cleanup()
                    
                    mock_ui_cleanup.assert_called_once()


class TestBackwardCompatibilityProperties:
    """Test backward compatibility properties."""
    
    def test_dictionary_window_property_getter(self, plugin):
        """Test dictionary_window property getter."""
        mock_window = Mock()
        plugin._dictionary_window = mock_window
        
        assert plugin.dictionary_window == mock_window
    
    def test_dictionary_window_property_setter(self, plugin):
        """Test dictionary_window property setter."""
        mock_window = Mock()
        plugin.dictionary_window = mock_window
        
        assert plugin._dictionary_window == mock_window
    
    def test_settings_window_property_getter(self, plugin):
        """Test settings_window property getter."""
        mock_window = Mock()
        plugin._settings_window = mock_window
        
        assert plugin.settings_window == mock_window
    
    def test_settings_window_property_setter(self, plugin):
        """Test settings_window property setter."""
        mock_window = Mock()
        plugin.settings_window = mock_window
        
        assert plugin._settings_window == mock_window
    
    def test_editor_integration_property_getter(self, plugin):
        """Test editor_integration property getter."""
        mock_editor = Mock()
        plugin._editor_integration = mock_editor
        
        assert plugin.editor_integration == mock_editor
    
    def test_editor_integration_property_setter(self, plugin):
        """Test editor_integration property setter."""
        mock_editor = Mock()
        plugin.editor_integration = mock_editor
        
        assert plugin._editor_integration == mock_editor


class TestErrorHandling:
    """Test error handling."""
    
    def test_hook_registration_error_handling(self, plugin):
        """Test that hook registration errors are handled."""
        # Mock addHook to raise an exception
        import sys
        mock_anki = Mock()
        mock_anki.hooks = Mock()
        mock_anki.hooks.addHook = Mock(side_effect=Exception("Hook error"))
        sys.modules['anki'] = mock_anki
        sys.modules['anki.hooks'] = mock_anki.hooks
        
        try:
            # Should not raise exception
            plugin._setup_hooks()
        finally:
            # Cleanup
            if 'anki' in sys.modules:
                del sys.modules['anki']
            if 'anki.hooks' in sys.modules:
                del sys.modules['anki.hooks']
    
    def test_config_notification_error_handling(self, plugin):
        """Test that config notification errors are handled."""
        with patch.object(plugin.search_service, 'reload_conjugations', side_effect=Exception("Reload error")):
            # Should not raise exception
            plugin._notify_config_change()
    
    def test_cleanup_error_handling(self, plugin):
        """Test that cleanup errors are handled."""
        with patch.object(plugin.media_service, 'cleanup_temp_media', side_effect=Exception("Cleanup error")):
            with patch.object(plugin.db_connection, 'close', side_effect=Exception("Close error")):
                # Should not raise exception
                plugin.cleanup()
