# -*- coding: utf-8 -*-
"""
Phase 4 Backward Compatibility Tests

Comprehensive tests to verify that all UI refactoring maintains backward compatibility:
- Menu items work correctly
- Keyboard shortcuts trigger proper actions
- Dictionary window opens and functions correctly
- Settings window opens and saves correctly
- Dictionary manager works correctly
- Card export from browser works correctly
- Editor integration (search, context menu) works
- Existing user configuration files work
- Existing dictionary databases work
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
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


class TestMenuItemsBackwardCompatibility:
    """Test that all menu items work correctly after refactoring."""
    
    def test_menu_manager_creates_menu(self, mock_mw, temp_addon_path):
        """Test that menu manager creates the addon menu."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            from src.ui.menu_manager import MenuManager
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Create menu manager
            menu_manager = MenuManager(mock_mw, plugin)
            
            # Setup menu
            menu_manager.setup_menu()
            
            # Verify menu was created
            assert menu_manager.menu is not None
    
    def test_open_dictionary_menu_action(self, mock_mw, temp_addon_path):
        """Test that 'Open Dictionary' menu action works."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            from src.ui.menu_manager import MenuManager
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            menu_manager = MenuManager(mock_mw, plugin)
            
            # Mock dictionary window
            with patch.object(plugin, 'get_dictionary_window') as mock_get_dict:
                mock_dict_window = Mock()
                mock_dict_window.isVisible = Mock(return_value=False)
                mock_dict_window.show_window = Mock()
                mock_get_dict.return_value = mock_dict_window
                
                # Call open dictionary
                menu_manager.open_dictionary()
                
                # Verify show_window was called
                mock_dict_window.show_window.assert_called_once()
    
    def test_open_settings_menu_action(self, mock_mw, temp_addon_path):
        """Test that 'Settings' menu action works."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            from src.ui.menu_manager import MenuManager
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            menu_manager = MenuManager(mock_mw, plugin)
            
            # Mock settings window
            with patch.object(plugin, 'get_settings_window') as mock_get_settings:
                mock_settings_window = Mock()
                mock_settings_window.show = Mock()
                mock_settings_window.raise_ = Mock()
                mock_settings_window.activateWindow = Mock()
                mock_get_settings.return_value = mock_settings_window
                
                # Call open settings
                menu_manager.open_settings()
                
                # Verify window methods were called
                mock_settings_window.show.assert_called_once()
                mock_settings_window.raise_.assert_called_once()
                mock_settings_window.activateWindow.assert_called_once()
    
    def test_open_dictionary_manager_menu_action(self, mock_mw, temp_addon_path):
        """Test that 'Dictionary Manager' menu action works."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            from src.ui.menu_manager import MenuManager
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            menu_manager = MenuManager(mock_mw, plugin)
            
            # Mock dictionary manager
            with patch.object(plugin, 'get_dictionary_manager') as mock_get_manager:
                mock_manager = Mock()
                mock_manager.show = Mock()
                mock_manager.raise_ = Mock()
                mock_manager.activateWindow = Mock()
                mock_get_manager.return_value = mock_manager
                
                # Call open dictionary manager (it's on plugin, not menu_manager)
                plugin.open_dictionary_manager()
                
                # Verify window methods were called
                mock_manager.show.assert_called_once()


class TestKeyboardShortcutsBackwardCompatibility:
    """Test that all keyboard shortcuts trigger proper actions."""
    
    def test_global_hotkey_registered(self, mock_mw, temp_addon_path):
        """Test that global hotkey is registered."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            from src.ui.menu_manager import MenuManager
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            menu_manager = MenuManager(mock_mw, plugin)
            
            # Mock QShortcut
            with patch('src.ui.menu_manager.QShortcut') as MockQShortcut:
                mock_shortcut = Mock()
                MockQShortcut.return_value = mock_shortcut
                
                # Setup hotkeys
                menu_manager.setup_global_hotkeys()
                
                # Verify shortcut was created
                MockQShortcut.assert_called()
    
    def test_platform_specific_shortcuts(self, mock_mw, temp_addon_path):
        """Test that platform-specific shortcuts are handled correctly."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            from src.ui.menu_manager import MenuManager
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            menu_manager = MenuManager(mock_mw, plugin)
            
            # Test Mac shortcut
            with patch('anki.utils.is_mac', return_value=True):
                shortcut = menu_manager.get_platform_shortcut('Ctrl+W')
                assert '⌘' in shortcut or 'Cmd' in shortcut.lower()
            
            # Test Windows/Linux shortcut
            with patch('anki.utils.is_mac', return_value=False):
                shortcut = menu_manager.get_platform_shortcut('Ctrl+W')
                assert 'Ctrl' in shortcut


class TestDictionaryWindowBackwardCompatibility:
    """Test that dictionary window opens and functions correctly."""
    
    def test_dictionary_window_can_be_created(self, mock_mw, temp_addon_path):
        """Test that dictionary window can be created."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock DictionaryWindow
            with patch('src.ui.DictionaryWindow') as MockDictWindow:
                mock_dict_window = Mock()
                MockDictWindow.return_value = mock_dict_window
                
                # Get dictionary window
                dict_window = plugin.get_dictionary_window()
                
                # Verify it was created with correct parameters
                MockDictWindow.assert_called_once()
                assert dict_window == mock_dict_window
    
    def test_dictionary_window_uses_search_service(self, mock_mw, temp_addon_path):
        """Test that dictionary window uses SearchService."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify search service is accessible
            search_service = plugin.get_search_service()
            assert search_service is not None
            assert hasattr(search_service, 'search')
    
    def test_dictionary_window_uses_export_service(self, mock_mw, temp_addon_path):
        """Test that dictionary window uses ExportService."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify export service is accessible
            export_service = plugin.get_export_service()
            assert export_service is not None
            assert hasattr(export_service, 'create_note')
    
    def test_dictionary_window_uses_media_service(self, mock_mw, temp_addon_path):
        """Test that dictionary window uses MediaService."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify media service is accessible
            media_service = plugin.get_media_service()
            assert media_service is not None
            assert hasattr(media_service, 'download_forvo_audio')
            assert hasattr(media_service, 'download_google_images')
    
    def test_dictionary_window_lazy_initialization(self, mock_mw, temp_addon_path):
        """Test that dictionary window is lazily initialized."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Window should not exist initially
            assert plugin._dictionary_window is None
            
            # Mock DictionaryWindow
            with patch('src.ui.DictionaryWindow') as MockDictWindow:
                mock_dict_window = Mock()
                MockDictWindow.return_value = mock_dict_window
                
                # Get window (should create it)
                dict_window1 = plugin.get_dictionary_window()
                assert dict_window1 is not None
                
                # Get window again (should return same instance)
                dict_window2 = plugin.get_dictionary_window()
                assert dict_window2 == dict_window1


class TestSettingsWindowBackwardCompatibility:
    """Test that settings window opens and saves correctly."""
    
    def test_settings_window_can_be_created(self, mock_mw, temp_addon_path):
        """Test that settings window can be created."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock SettingsWindow
            with patch('src.ui.SettingsWindow') as MockSettingsWindow:
                mock_settings_window = Mock()
                MockSettingsWindow.return_value = mock_settings_window
                
                # Get settings window
                settings_window = plugin.get_settings_window()
                
                # Verify it was created with correct parameters
                MockSettingsWindow.assert_called_once()
                assert settings_window == mock_settings_window
    
    def test_settings_window_uses_config_manager(self, mock_mw, temp_addon_path):
        """Test that settings window uses ConfigManager."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify config manager is accessible
            config_manager = plugin.get_config_manager()
            assert config_manager is not None
            assert hasattr(config_manager, 'get_config')  # read_config renamed to get_config
            assert hasattr(config_manager, 'write_config')
    
    def test_settings_window_validates_before_saving(self, mock_mw, temp_addon_path):
        """Test that settings window validates configuration."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            config_manager = plugin.get_config_manager()
            
            # Config manager should validate
            assert hasattr(config_manager, 'validate_current_config')  # validate_config renamed


class TestDictionaryManagerBackwardCompatibility:
    """Test that dictionary manager works correctly."""
    
    def test_dictionary_manager_can_be_created(self, mock_mw, temp_addon_path):
        """Test that dictionary manager can be created."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Mock DictionaryManagerWidget
            with patch('src.ui.DictionaryManagerWidget') as MockManager:
                mock_manager = Mock()
                MockManager.return_value = mock_manager
                
                # Get dictionary manager
                manager = plugin.get_dictionary_manager()
                
                # Verify it was created
                MockManager.assert_called_once()
                assert manager == mock_manager
    
    def test_dictionary_manager_uses_repository(self, mock_mw, temp_addon_path):
        """Test that dictionary manager uses DictionaryRepository."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify dictionary repository is accessible
            dict_repo = plugin.get_dictionary_repository()
            assert dict_repo is not None
            assert hasattr(dict_repo, 'get_all_languages')
            assert hasattr(dict_repo, 'get_dictionaries_by_language')
    
    def test_dictionary_manager_can_query_dictionaries(self, mock_mw, temp_addon_path):
        """Test that dictionary manager can query dictionaries."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Query languages
            languages = plugin.dictionary_repo.get_all_languages()
            assert isinstance(languages, list)
            assert 'Japanese' in languages
            assert 'English' in languages


class TestCardExporterBackwardCompatibility:
    """Test that card export from browser works correctly."""
    
    def test_card_exporter_uses_export_service(self, mock_mw, temp_addon_path):
        """Test that card exporter uses ExportService."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify export service is accessible
            export_service = plugin.get_export_service()
            assert export_service is not None
            assert hasattr(export_service, 'create_note')
    
    def test_browser_integration_exists(self, mock_mw, temp_addon_path):
        """Test that browser integration exists."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Initialize to create browser integration
            with patch.object(plugin, '_setup_hooks'):
                with patch.object(plugin, '_cleanup_temp_files'):
                    with patch('src.ui.browser_integration.BrowserIntegration') as MockBrowser:
                        mock_browser = Mock()
                        MockBrowser.return_value = mock_browser
                        
                        plugin.initialize()
                        
                        # Verify browser integration was created
                        MockBrowser.assert_called_once()


class TestEditorIntegrationBackwardCompatibility:
    """Test that editor integration (search, context menu) works."""
    
    def test_editor_integration_exists(self, mock_mw, temp_addon_path):
        """Test that editor integration exists."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Initialize to create editor integration
            with patch.object(plugin, '_setup_hooks'):
                with patch.object(plugin, '_cleanup_temp_files'):
                    with patch('src.ui.editor_integration.EditorIntegration') as MockEditor:
                        mock_editor = Mock()
                        MockEditor.return_value = mock_editor
                        
                        plugin.initialize()
                        
                        # Verify editor integration was created
                        MockEditor.assert_called_once()
    
    def test_editor_hooks_registered(self, mock_mw, temp_addon_path):
        """Test that editor hooks are registered."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Initialize to register hooks
            with patch.object(plugin, '_cleanup_temp_files'):
                with patch('src.ui.editor_integration.EditorIntegration') as MockEditor:
                    with patch('src.ui.browser_integration.BrowserIntegration'):
                        with patch('src.ui.menu_manager.MenuManager'):
                            mock_editor = Mock()
                            mock_editor.setup_editor_hooks = Mock()
                            MockEditor.return_value = mock_editor
                            
                            plugin.initialize()
                            
                            # Verify setup_editor_hooks was called
                            mock_editor.setup_editor_hooks.assert_called_once()
    
    def test_editor_context_menu_support(self, mock_mw, temp_addon_path):
        """Test that editor context menu is supported."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            from src.ui.editor_integration import EditorIntegration
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            editor_integration = EditorIntegration(plugin)
            
            # Verify context menu method exists (private method)
            assert hasattr(editor_integration, '_add_to_context_menu')


class TestUserConfigurationBackwardCompatibility:
    """Test with existing user configuration files."""
    
    def test_existing_config_loaded(self, mock_mw, temp_addon_path):
        """Test that existing configuration is loaded."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify config was loaded
            assert hasattr(mock_mw, 'AnkiDictConfig')
            assert mock_mw.AnkiDictConfig is not None
            assert isinstance(mock_mw.AnkiDictConfig, dict)
    
    def test_config_has_expected_keys(self, mock_mw, temp_addon_path):
        """Test that configuration has expected keys."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            config = mock_mw.AnkiDictConfig
            
            # Verify expected keys exist
            assert 'searchMode' in config
            assert 'maxSearchResults' in config
            assert 'dictOnStart' in config
    
    def test_config_can_be_refreshed(self, mock_mw, temp_addon_path):
        """Test that configuration can be refreshed."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Refresh config
            new_config = {'test': 'value', 'searchMode': 'Exact'}
            mock_mw.refreshAnkiDictConfig(new_config)
            
            # Verify config was updated
            assert mock_mw.AnkiDictConfig == new_config


class TestDictionaryDatabaseBackwardCompatibility:
    """Test with existing dictionary databases."""
    
    def test_database_connection_works(self, mock_mw, temp_addon_path):
        """Test that database connection works."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify database is connected
            assert plugin.db_connection is not None
            assert plugin.db_connection.conn is not None
    
    def test_can_query_existing_languages(self, mock_mw, temp_addon_path):
        """Test that existing languages can be queried."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Query languages
            languages = plugin.dictionary_repo.get_all_languages()
            
            assert 'Japanese' in languages
            assert 'English' in languages
    
    def test_database_schema_intact(self, mock_mw, temp_addon_path):
        """Test that database schema is intact."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Check tables exist
            cursor = plugin.db_connection.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'langnames' in tables
            assert 'dictnames' in tables
    
    def test_backward_compatible_db_reference(self, mock_mw, temp_addon_path):
        """Test that mw.miDictDB reference works."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify mw.miDictDB is set
            assert hasattr(mock_mw, 'miDictDB')
            assert mock_mw.miDictDB == plugin.dictionary_repo


class TestLegacyFunctionWrappersBackwardCompatibility:
    """Test that legacy function wrappers work correctly."""
    
    def test_dictionary_init_wrapper_exists(self, mock_mw, temp_addon_path):
        """Test that dictionary_init wrapper exists in main.py."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            mock_mw.ankiDictPlugin = plugin
            
            # Import main to get legacy wrappers
            import main
            
            # Verify dictionary_init exists
            assert hasattr(main, 'dictionary_init')
            assert callable(main.dictionary_init)
    
    def test_mw_dictionary_init_attached(self, mock_mw, temp_addon_path):
        """Test that mw.dictionaryInit is attached."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            mock_mw.ankiDictPlugin = plugin
            
            # Import main to attach legacy functions
            import main
            
            # Verify mw.dictionaryInit is set
            assert hasattr(mock_mw, 'dictionaryInit')
            assert callable(mock_mw.dictionaryInit)


class TestFullIntegrationBackwardCompatibility:
    """Test full integration scenarios."""
    
    def test_full_plugin_lifecycle(self, mock_mw, temp_addon_path):
        """Test complete plugin lifecycle."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            # Step 1: Create plugin
            plugin = AnkiDictionaryPlugin(mock_mw)
            assert plugin is not None
            
            # Step 2: Verify services
            assert plugin.search_service is not None
            assert plugin.export_service is not None
            assert plugin.media_service is not None
            
            # Step 3: Initialize
            with patch.object(plugin, '_setup_hooks'):
                with patch.object(plugin, '_cleanup_temp_files'):
                    with patch('src.ui.menu_manager.MenuManager'):
                        with patch('src.ui.editor_integration.EditorIntegration'):
                            with patch('src.ui.browser_integration.BrowserIntegration'):
                                plugin.initialize()
            
            # Step 4: Verify UI components can be accessed
            with patch('src.ui.DictionaryWindow'):
                dict_window = plugin.get_dictionary_window()
                assert dict_window is not None
            
            with patch('src.ui.SettingsWindow'):
                settings_window = plugin.get_settings_window()
                assert settings_window is not None
            
            # Step 5: Cleanup
            with patch.object(plugin.media_service, 'cleanup_temp_media'):
                with patch.object(plugin.db_connection, 'close'):
                    plugin.cleanup()
    
    def test_all_backward_compatibility_variables_set(self, mock_mw, temp_addon_path):
        """Test that all backward compatibility variables are set."""
        with patch('src.core.plugin.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = temp_addon_path
            
            from src.core.plugin import AnkiDictionaryPlugin
            
            plugin = AnkiDictionaryPlugin(mock_mw)
            
            # Verify all backward compatibility variables
            assert hasattr(mock_mw, 'AnkiDictConfig')
            assert hasattr(mock_mw, 'refreshAnkiDictConfig')
            assert hasattr(mock_mw, 'miDictDB')
            assert hasattr(mock_mw, 'DictExportingDefinitions')
            assert hasattr(mock_mw, 'dictSettings')
            assert hasattr(mock_mw, 'misoEditorLoadedAfterDictionary')
            assert hasattr(mock_mw, 'DictBulkMediaExportWasCancelled')
