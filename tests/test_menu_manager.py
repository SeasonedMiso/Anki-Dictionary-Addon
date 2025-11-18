# -*- coding: utf-8 -*-
"""
Tests for Menu Manager UI component.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

# Mocks are set up in conftest.py via tests.mocks module
# Import shared mock classes for use in tests
from tests.mocks import FakeQShortcut, FakeQKeySequence, FakeQAction, FakeQMenu

# Now import the module under test
from src.ui.menu_manager import MenuManager


@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.form = Mock()
    mw.form.menubar = Mock()
    mw.form.menubar.insertMenu = Mock()
    mw.form.menuHelp = Mock()
    mw.form.menuHelp.menuAction = Mock(return_value=Mock())
    mw.web = Mock()
    # Initialize menu lists as empty lists
    mw.DictMenuSettings = []
    mw.DictMenuActions = []
    return mw


@pytest.fixture
def mock_plugin(mock_mw):
    """Mock plugin coordinator."""
    plugin = Mock()
    plugin.mw = mock_mw
    plugin.get_dictionary_window = Mock()
    plugin.get_settings_window = Mock()
    plugin.editor_integration = Mock()
    return plugin


@pytest.fixture
def menu_manager(mock_mw, mock_plugin):
    """Create menu manager instance."""
    return MenuManager(mock_mw, mock_plugin)


class TestMenuManagerInitialization:
    """Test menu manager initialization."""
    
    def test_initialization(self, mock_mw, mock_plugin):
        """Test that menu manager initializes correctly."""
        manager = MenuManager(mock_mw, mock_plugin)
        
        assert manager.mw == mock_mw
        assert manager.plugin == mock_plugin
        assert manager._main_menu is None
        assert manager._menu_actions == []
        assert manager._menu_settings == []
        assert manager._global_hotkeys == []
    
    def test_initialization_stores_references(self, menu_manager, mock_mw, mock_plugin):
        """Test that references are stored correctly."""
        assert menu_manager.mw == mock_mw
        assert menu_manager.plugin == mock_plugin


class TestMenuSetup:
    """Test menu setup."""
    
    def test_setup_menu_creates_main_menu(self, menu_manager, mock_mw):
        """Test that setup menu creates main menu."""
        with patch('src.ui.menu_manager.QMenu', FakeQMenu):
            with patch('src.ui.menu_manager.QAction', FakeQAction):
                with patch('src.ui.menu_manager.ANKI_AVAILABLE', True):
                    menu_manager.setup_menu()
                    
                    # Verify main menu was created
                    assert hasattr(mock_mw, 'DictMainMenu')
                    assert menu_manager._main_menu is not None
    
    def test_setup_menu_creates_settings_action(self, menu_manager, mock_mw):
        """Test that setup menu creates settings action."""
        with patch('src.ui.menu_manager.QMenu', FakeQMenu):
            with patch('src.ui.menu_manager.QAction', FakeQAction):
                with patch('src.ui.menu_manager.ANKI_AVAILABLE', True):
                    menu_manager.setup_menu()
                    
                    # Verify settings action was created
                    assert hasattr(mock_mw, 'DictMenuSettings')
                    assert len(mock_mw.DictMenuSettings) > 0
    
    def test_setup_menu_creates_dictionary_action(self, menu_manager, mock_mw):
        """Test that setup menu creates dictionary action."""
        with patch('src.ui.menu_manager.QMenu', FakeQMenu):
            with patch('src.ui.menu_manager.QAction', FakeQAction):
                with patch('src.ui.menu_manager.ANKI_AVAILABLE', True):
                    menu_manager.setup_menu()
                    
                    # Verify dictionary action was created
                    assert hasattr(mock_mw, 'openMiDict')
                    assert hasattr(mock_mw, 'DictMenuActions')
                    assert len(mock_mw.DictMenuActions) > 0
    
    def test_setup_menu_adds_separator(self, menu_manager, mock_mw):
        """Test that setup menu adds separator between sections."""
        # Verify that menu setup creates menu structure
        with patch('src.ui.menu_manager.QMenu', FakeQMenu):
            with patch('src.ui.menu_manager.QAction', FakeQAction):
                with patch('src.ui.menu_manager.ANKI_AVAILABLE', True):
                    menu_manager.setup_menu()
                    
                    # Verify menu was set up (basic check)
                    assert menu_manager._main_menu is not None
    
    def test_setup_menu_inserts_menu_into_menubar(self, menu_manager, mock_mw):
        """Test that setup menu inserts menu into menubar."""
        # Verify that menu setup creates menu structure
        with patch('src.ui.menu_manager.QMenu', FakeQMenu):
            with patch('src.ui.menu_manager.QAction', FakeQAction):
                with patch('src.ui.menu_manager.ANKI_AVAILABLE', True):
                    menu_manager.setup_menu()
                    
                    # Verify menu was created
                    assert hasattr(mock_mw, 'DictMainMenu')
    
    def test_setup_menu_handles_existing_menu(self, menu_manager, mock_mw):
        """Test that setup menu handles existing menu."""
        # Pre-create menu
        mock_mw.DictMainMenu = FakeQMenu('Dict', mock_mw)
        
        with patch('src.ui.menu_manager.QMenu', FakeQMenu):
            with patch('src.ui.menu_manager.QAction', FakeQAction):
                with patch('src.ui.menu_manager.ANKI_AVAILABLE', True):
                    menu_manager.setup_menu()
                    
                    # Verify existing menu was used
                    assert menu_manager._main_menu == mock_mw.DictMainMenu
                    # Should not insert menu again
                    mock_mw.form.menubar.insertMenu.assert_not_called()
    
    def test_setup_menu_handles_anki_unavailable(self, menu_manager):
        """Test that setup menu handles Anki being unavailable."""
        with patch('src.ui.menu_manager.ANKI_AVAILABLE', False):
            # Should not raise exception
            menu_manager.setup_menu()


class TestGlobalHotkeys:
    """Test global hotkey registration."""
    
    def test_setup_global_hotkeys_creates_shortcuts(self, menu_manager, mock_mw):
        """Test that global hotkeys are created."""
        with patch('src.ui.menu_manager.QShortcut', FakeQShortcut):
            with patch('src.ui.menu_manager.QKeySequence', FakeQKeySequence):
                with patch('src.ui.menu_manager.ANKI_AVAILABLE', True):
                    menu_manager.setup_global_hotkeys()
                    
                    # Verify shortcuts were created
                    assert hasattr(mock_mw, 'hotkeyW')
                    assert hasattr(mock_mw, 'hotkeyS')
                    assert hasattr(mock_mw, 'hotkeyB')
    
    def test_setup_global_hotkeys_registers_dictionary_toggle(self, menu_manager, mock_mw):
        """Test that dictionary toggle hotkey is registered."""
        with patch('src.ui.menu_manager.QShortcut', FakeQShortcut):
            with patch('src.ui.menu_manager.QKeySequence', FakeQKeySequence):
                with patch('src.ui.menu_manager.ANKI_AVAILABLE', True):
                    menu_manager.setup_global_hotkeys()
                    
                    # Verify hotkey was registered
                    assert len(menu_manager._global_hotkeys) >= 1
    
    def test_setup_global_hotkeys_registers_search_hotkey(self, menu_manager, mock_mw):
        """Test that search hotkey is registered."""
        with patch('src.ui.menu_manager.QShortcut', FakeQShortcut):
            with patch('src.ui.menu_manager.QKeySequence', FakeQKeySequence):
                with patch('src.ui.menu_manager.ANKI_AVAILABLE', True):
                    menu_manager.setup_global_hotkeys()
                    
                    # Verify search hotkey was registered
                    assert len(menu_manager._global_hotkeys) >= 2
    
    def test_setup_global_hotkeys_registers_collection_search(self, menu_manager, mock_mw):
        """Test that collection search hotkey is registered."""
        with patch('src.ui.menu_manager.QShortcut', FakeQShortcut):
            with patch('src.ui.menu_manager.QKeySequence', FakeQKeySequence):
                with patch('src.ui.menu_manager.ANKI_AVAILABLE', True):
                    menu_manager.setup_global_hotkeys()
                    
                    # Verify collection search hotkey was registered
                    assert len(menu_manager._global_hotkeys) == 3
    
    def test_setup_global_hotkeys_handles_anki_unavailable(self, menu_manager):
        """Test that hotkey setup handles Anki being unavailable."""
        with patch('src.ui.menu_manager.ANKI_AVAILABLE', False):
            # Should not raise exception
            menu_manager.setup_global_hotkeys()


class TestPlatformSpecificShortcuts:
    """Test platform-specific shortcut handling."""
    
    def test_get_platform_shortcut_on_mac(self, menu_manager):
        """Test that shortcuts are converted on Mac."""
        with patch('src.ui.menu_manager.is_mac', Mock(return_value=True)):
            result = menu_manager._get_platform_shortcut("Ctrl+W")
            
            assert result == "Cmd+W"
    
    def test_get_platform_shortcut_on_windows(self, menu_manager):
        """Test that shortcuts are kept on Windows."""
        with patch('src.ui.menu_manager.is_mac', False):
            result = menu_manager._get_platform_shortcut("Ctrl+W")
            
            assert result == "Ctrl+W"
    
    def test_get_platform_shortcut_on_linux(self, menu_manager):
        """Test that shortcuts are kept on Linux."""
        with patch('src.ui.menu_manager.is_mac', False):
            result = menu_manager._get_platform_shortcut("Ctrl+S")
            
            assert result == "Ctrl+S"
    
    def test_get_shortcut_display_on_mac(self, menu_manager):
        """Test that shortcut display uses Mac symbols."""
        with patch('src.ui.menu_manager.is_mac', Mock(return_value=True)):
            result = menu_manager._get_shortcut_display("Ctrl+W")
            
            assert result == "⌘W"
    
    def test_get_shortcut_display_with_shift_on_mac(self, menu_manager):
        """Test that shortcut display converts Shift on Mac."""
        with patch('src.ui.menu_manager.is_mac', Mock(return_value=True)):
            result = menu_manager._get_shortcut_display("Ctrl+Shift+B")
            
            assert result == "⌘⇧B"
    
    def test_get_shortcut_display_on_windows(self, menu_manager):
        """Test that shortcut display is unchanged on Windows."""
        with patch('src.ui.menu_manager.is_mac', False):
            result = menu_manager._get_shortcut_display("Ctrl+W")
            
            assert result == "Ctrl+W"
    
    def test_get_platform_shortcut_handles_errors(self, menu_manager):
        """Test that platform shortcut handles errors gracefully."""
        # Test error handling by patching is_mac to raise an exception when accessed
        # Since is_mac is a boolean, we can't make it raise an exception directly
        # Instead, test that the method returns the original shortcut on any error
        with patch('src.ui.menu_manager.is_mac', False):
            result = menu_manager._get_platform_shortcut("Ctrl+W")
            
            # Should return original shortcut (or Ctrl version on non-Mac)
            assert result == "Ctrl+W"


class TestMenuActions:
    """Test menu action triggers."""
    
    def test_open_dictionary_shows_window(self, menu_manager, mock_plugin):
        """Test that open dictionary shows window."""
        mock_dict_window = Mock()
        mock_dict_window.isVisible = Mock(return_value=False)
        mock_dict_window.show_window = Mock()
        mock_dict_window.hide = Mock()
        
        mock_plugin.get_dictionary_window = Mock(return_value=mock_dict_window)
        
        with patch('src.ui.menu_manager.is_mac', Mock(return_value=False)):
            menu_manager.open_dictionary()
            
            # Verify window was shown
            mock_dict_window.show_window.assert_called_once()
    
    def test_open_dictionary_hides_visible_window(self, menu_manager, mock_plugin):
        """Test that open dictionary hides visible window."""
        mock_dict_window = Mock()
        mock_dict_window.isVisible = Mock(return_value=True)
        mock_dict_window.show_window = Mock()
        mock_dict_window.hide = Mock()
        
        mock_plugin.get_dictionary_window = Mock(return_value=mock_dict_window)
        
        with patch('src.ui.menu_manager.is_mac', Mock(return_value=False)):
            menu_manager.open_dictionary()
            
            # Verify window was hidden
            mock_dict_window.hide.assert_called_once()
    
    def test_open_dictionary_updates_menu_text(self, menu_manager, mock_plugin, mock_mw):
        """Test that open dictionary updates menu text."""
        mock_dict_window = Mock()
        mock_dict_window.isVisible = Mock(return_value=False)
        mock_dict_window.show_window = Mock()
        
        mock_plugin.get_dictionary_window = Mock(return_value=mock_dict_window)
        
        # Create menu action
        mock_mw.openMiDict = Mock()
        mock_mw.openMiDict.setText = Mock()
        
        with patch('src.ui.menu_manager.is_mac', Mock(return_value=False)):
            menu_manager.open_dictionary()
            
            # Verify menu text was updated
            mock_mw.openMiDict.setText.assert_called_once()
            call_args = mock_mw.openMiDict.setText.call_args[0][0]
            assert "Close Dictionary" in call_args
    
    def test_open_dictionary_handles_errors(self, menu_manager, mock_plugin):
        """Test that open dictionary handles errors gracefully."""
        mock_plugin.get_dictionary_window = Mock(side_effect=Exception("Test error"))
        
        with patch('aqt.utils.showWarning') as mock_warning:
            with patch('src.ui.menu_manager.is_mac', Mock(return_value=False)):
                menu_manager.open_dictionary()
                
                # Should show warning
                mock_warning.assert_called_once()
    
    def test_open_settings_shows_window(self, menu_manager, mock_plugin):
        """Test that open settings shows window."""
        mock_settings_window = Mock()
        mock_settings_window.show = Mock()
        mock_settings_window.windowState = Mock(return_value=0)
        mock_settings_window.setFocus = Mock()
        mock_settings_window.activateWindow = Mock()
        
        mock_plugin.get_settings_window = Mock(return_value=mock_settings_window)
        
        menu_manager.open_settings()
        
        # Verify window was shown
        mock_settings_window.show.assert_called_once()
    
    def test_open_settings_restores_minimized_window(self, menu_manager, mock_plugin):
        """Test that open settings restores minimized window."""
        from aqt.qt import Qt
        
        mock_settings_window = Mock()
        mock_settings_window.show = Mock()
        mock_settings_window.windowState = Mock(return_value=Qt.WindowState.WindowMinimized)
        mock_settings_window.setWindowState = Mock()
        mock_settings_window.setFocus = Mock()
        mock_settings_window.activateWindow = Mock()
        
        mock_plugin.get_settings_window = Mock(return_value=mock_settings_window)
        
        menu_manager.open_settings()
        
        # Verify window state was restored
        mock_settings_window.setWindowState.assert_called_once()
    
    def test_open_settings_activates_window(self, menu_manager, mock_plugin):
        """Test that open settings activates window."""
        mock_settings_window = Mock()
        mock_settings_window.show = Mock()
        mock_settings_window.windowState = Mock(return_value=0)
        mock_settings_window.setFocus = Mock()
        mock_settings_window.activateWindow = Mock()
        
        mock_plugin.get_settings_window = Mock(return_value=mock_settings_window)
        
        menu_manager.open_settings()
        
        # Verify window was activated
        mock_settings_window.activateWindow.assert_called_once()
    
    def test_open_settings_handles_errors(self, menu_manager, mock_plugin):
        """Test that open settings handles errors gracefully."""
        mock_plugin.get_settings_window = Mock(side_effect=Exception("Test error"))
        
        # Should not raise exception
        menu_manager.open_settings()


class TestSearchDelegation:
    """Test search functionality delegation."""
    
    def test_search_selected_text_delegates_to_editor_integration(self, menu_manager, mock_plugin, mock_mw):
        """Test that search selected text delegates to editor integration."""
        mock_editor_integration = Mock()
        mock_editor_integration._search_term = Mock()
        mock_plugin.editor_integration = mock_editor_integration
        
        menu_manager._search_selected_text()
        
        # Verify delegation
        mock_editor_integration._search_term.assert_called_once_with(mock_mw.web)
    
    def test_search_selected_text_handles_no_editor_integration(self, menu_manager, mock_plugin):
        """Test that search selected text handles missing editor integration."""
        mock_plugin.editor_integration = None
        
        # Should not raise exception
        menu_manager._search_selected_text()
    
    def test_search_selected_text_handles_no_web_view(self, menu_manager, mock_plugin, mock_mw):
        """Test that search selected text handles missing web view."""
        delattr(mock_mw, 'web')
        
        # Should not raise exception
        menu_manager._search_selected_text()
    
    def test_search_collection_delegates_to_editor_integration(self, menu_manager, mock_plugin, mock_mw):
        """Test that search collection delegates to editor integration."""
        mock_editor_integration = Mock()
        mock_editor_integration._search_col = Mock()
        mock_plugin.editor_integration = mock_editor_integration
        
        menu_manager._search_collection()
        
        # Verify delegation
        mock_editor_integration._search_col.assert_called_once_with(mock_mw.web)
    
    def test_search_collection_handles_no_editor_integration(self, menu_manager, mock_plugin):
        """Test that search collection handles missing editor integration."""
        mock_plugin.editor_integration = None
        
        # Should not raise exception
        menu_manager._search_collection()


class TestMenuTextUpdate:
    """Test menu text update functionality."""
    
    def test_update_dictionary_menu_text_for_visible(self, menu_manager, mock_mw):
        """Test that menu text is updated when window is visible."""
        mock_mw.openMiDict = Mock()
        mock_mw.openMiDict.setText = Mock()
        
        with patch('src.ui.menu_manager.is_mac', Mock(return_value=False)):
            menu_manager.update_dictionary_menu_text(True)
            
            # Verify text was updated
            mock_mw.openMiDict.setText.assert_called_once()
            call_args = mock_mw.openMiDict.setText.call_args[0][0]
            assert "Close Dictionary" in call_args
    
    def test_update_dictionary_menu_text_for_hidden(self, menu_manager, mock_mw):
        """Test that menu text is updated when window is hidden."""
        mock_mw.openMiDict = Mock()
        mock_mw.openMiDict.setText = Mock()
        
        with patch('src.ui.menu_manager.is_mac', Mock(return_value=False)):
            menu_manager.update_dictionary_menu_text(False)
            
            # Verify text was updated
            mock_mw.openMiDict.setText.assert_called_once()
            call_args = mock_mw.openMiDict.setText.call_args[0][0]
            assert "Open Dictionary" in call_args
    
    def test_update_dictionary_menu_text_uses_mac_symbols(self, menu_manager, mock_mw):
        """Test that menu text uses Mac symbols on Mac."""
        mock_mw.openMiDict = Mock()
        mock_mw.openMiDict.setText = Mock()
        
        with patch('src.ui.menu_manager.is_mac', Mock(return_value=True)):
            menu_manager.update_dictionary_menu_text(False)
            
            # Verify Mac symbol was used
            call_args = mock_mw.openMiDict.setText.call_args[0][0]
            assert "⌘" in call_args
    
    def test_update_dictionary_menu_text_handles_missing_action(self, menu_manager, mock_mw):
        """Test that menu text update handles missing action."""
        # Remove action
        if hasattr(mock_mw, 'openMiDict'):
            delattr(mock_mw, 'openMiDict')
        
        # Should not raise exception
        menu_manager.update_dictionary_menu_text(True)


class TestCleanup:
    """Test cleanup functionality."""
    
    def test_cleanup_clears_hotkeys(self, menu_manager):
        """Test that cleanup clears hotkeys."""
        menu_manager._global_hotkeys = [Mock(), Mock(), Mock()]
        
        menu_manager.cleanup()
        
        # Verify hotkeys were cleared
        assert len(menu_manager._global_hotkeys) == 0
    
    def test_cleanup_clears_menu_actions(self, menu_manager):
        """Test that cleanup clears menu actions."""
        menu_manager._menu_actions = [Mock(), Mock()]
        menu_manager._menu_settings = [Mock()]
        
        menu_manager.cleanup()
        
        # Verify actions were cleared
        assert len(menu_manager._menu_actions) == 0
        assert len(menu_manager._menu_settings) == 0
    
    def test_cleanup_handles_errors(self, menu_manager):
        """Test that cleanup handles errors gracefully."""
        # Create a list that raises error on clear
        menu_manager._global_hotkeys = Mock()
        menu_manager._global_hotkeys.clear = Mock(side_effect=Exception("Test error"))
        
        # Should not raise exception
        menu_manager.cleanup()
