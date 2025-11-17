# -*- coding: utf-8 -*-
"""
Tests for Browser Integration UI component.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import sys

# Mocks are set up in conftest.py via tests.mocks module
# Import shared mock classes for use in tests
from tests.mocks import FakeQAction, FakeQDialog

# Add additional browser-specific mocks
fake_aqt = sys.modules['aqt']
fake_aqt.browser = MagicMock()
fake_aqt.browser.Browser = MagicMock()
fake_aqt.utils.askUser = Mock(return_value=True)

fake_anki = sys.modules['anki']
fake_anki.find = MagicMock()

sys.modules['aqt.browser'] = fake_aqt.browser
sys.modules['anki.find'] = fake_anki.find

# Now import the module under test
from src.ui.browser_integration import BrowserIntegration


@pytest.fixture
def mock_plugin():
    """Mock plugin coordinator."""
    plugin = Mock()
    plugin.mw = Mock()
    plugin.mw.col = Mock()
    plugin.get_search_service = Mock()
    plugin.get_export_service = Mock()
    return plugin


@pytest.fixture
def browser_integration(mock_plugin):
    """Create browser integration instance."""
    return BrowserIntegration(mock_plugin)


class TestBrowserIntegrationInitialization:
    """Test browser integration initialization."""
    
    def test_initialization(self, mock_plugin):
        """Test that browser integration initializes correctly."""
        integration = BrowserIntegration(mock_plugin)
        
        assert integration.plugin == mock_plugin
        assert integration.mw == mock_plugin.mw
    
    def test_initialization_stores_plugin_reference(self, browser_integration, mock_plugin):
        """Test that plugin reference is stored."""
        assert browser_integration.plugin == mock_plugin


class TestBrowserHookRegistration:
    """Test browser hook registration."""
    
    def test_setup_browser_hooks_registers_menu_hook(self, browser_integration):
        """Test that browser menu hook is registered."""
        with patch('src.ui.browser_integration.addHook') as mock_add_hook:
            with patch('src.ui.browser_integration.ANKI_AVAILABLE', True):
                browser_integration.setup_browser_hooks()
                
                # Check that browser menu hook was registered
                mock_add_hook.assert_called_once_with("browser.setupMenus", browser_integration._setup_browser_menu)
    
    def test_setup_browser_hooks_handles_anki_unavailable(self, browser_integration):
        """Test that hook setup handles Anki being unavailable."""
        with patch('src.ui.browser_integration.ANKI_AVAILABLE', False):
            # Should not raise exception
            browser_integration.setup_browser_hooks()
    
    def test_setup_browser_hooks_handles_errors(self, browser_integration):
        """Test that hook setup handles errors gracefully."""
        with patch('src.ui.browser_integration.addHook', side_effect=Exception("Test error")):
            with patch('src.ui.browser_integration.ANKI_AVAILABLE', True):
                # Should not raise exception
                browser_integration.setup_browser_hooks()


class TestBrowserMenuSetup:
    """Test browser menu setup."""
    
    def test_setup_browser_menu_adds_separator(self, browser_integration):
        """Test that separator is added to menu."""
        mock_browser = Mock()
        mock_browser.form = Mock()
        mock_browser.form.menuEdit = Mock()
        mock_browser.form.menuEdit.addSeparator = Mock()
        mock_browser.form.menuEdit.addAction = Mock()
        
        with patch('src.ui.browser_integration.QAction', FakeQAction):
            browser_integration._setup_browser_menu(mock_browser)
            
            # Verify separator was added
            mock_browser.form.menuEdit.addSeparator.assert_called_once()
    
    def test_setup_browser_menu_adds_export_action(self, browser_integration):
        """Test that export action is added to menu."""
        mock_browser = Mock()
        mock_browser.form = Mock()
        mock_browser.form.menuEdit = Mock()
        mock_browser.form.menuEdit.addSeparator = Mock()
        mock_browser.form.menuEdit.addAction = Mock()
        
        with patch('src.ui.browser_integration.QAction', FakeQAction):
            browser_integration._setup_browser_menu(mock_browser)
            
            # Verify action was added
            mock_browser.form.menuEdit.addAction.assert_called_once()
            
            # Verify action text
            call_args = mock_browser.form.menuEdit.addAction.call_args[0][0]
            assert call_args.text == "Export Definitions"
    
    def test_setup_browser_menu_connects_export_action(self, browser_integration):
        """Test that export action is connected to handler."""
        mock_browser = Mock()
        mock_browser.form = Mock()
        mock_browser.form.menuEdit = Mock()
        mock_browser.form.menuEdit.addSeparator = Mock()
        mock_browser.form.menuEdit.addAction = Mock()
        
        with patch('src.ui.browser_integration.QAction', FakeQAction):
            browser_integration._setup_browser_menu(mock_browser)
            
            # Verify action was connected
            call_args = mock_browser.form.menuEdit.addAction.call_args[0][0]
            assert call_args.triggered.connect.called
    
    def test_setup_browser_menu_handles_errors(self, browser_integration):
        """Test that menu setup handles errors gracefully."""
        mock_browser = Mock()
        mock_browser.form = Mock()
        mock_browser.form.menuEdit = Mock()
        mock_browser.form.menuEdit.addSeparator = Mock(side_effect=Exception("Test error"))
        
        # Should not raise exception
        browser_integration._setup_browser_menu(mock_browser)


class TestBulkExportLaunch:
    """Test bulk export launch."""
    
    def test_launch_bulk_export_shows_error_when_no_selection(self, browser_integration):
        """Test that error is shown when no cards are selected."""
        mock_browser = Mock()
        mock_browser.selectedNotes = Mock(return_value=[])
        
        with patch('aqt.utils.showInfo') as mock_show_info:
            browser_integration._launch_bulk_export(mock_browser)
            
            # Verify error was shown
            mock_show_info.assert_called_once()
            call_args = mock_show_info.call_args[0][0]
            assert 'select some cards' in call_args.lower()
    
    def test_launch_bulk_export_calls_show_dialog_with_selection(self, browser_integration):
        """Test that dialog is shown when cards are selected."""
        mock_browser = Mock()
        mock_browser.selectedNotes = Mock(return_value=[1, 2, 3])
        
        with patch.object(browser_integration, '_show_bulk_export_dialog') as mock_show_dialog:
            browser_integration._launch_bulk_export(mock_browser)
            
            # Verify dialog was shown
            mock_show_dialog.assert_called_once_with(mock_browser, [1, 2, 3])
    
    def test_launch_bulk_export_handles_errors(self, browser_integration):
        """Test that bulk export launch handles errors gracefully."""
        mock_browser = Mock()
        mock_browser.selectedNotes = Mock(side_effect=Exception("Test error"))
        
        with patch('aqt.utils.showWarning') as mock_show_warning:
            browser_integration._launch_bulk_export(mock_browser)
            
            # Verify warning was shown
            mock_show_warning.assert_called_once()


class TestBulkExportDialog:
    """Test bulk export dialog."""
    
    def test_show_bulk_export_dialog_creates_dialog(self, browser_integration):
        """Test that dialog is created."""
        mock_browser = Mock()
        selected_notes = [1, 2, 3]
        
        # Mock note
        mock_note = Mock()
        mock_note.keys = Mock(return_value=['Field1', 'Field2'])
        browser_integration.mw.col.get_note = Mock(return_value=mock_note)
        
        with patch('aqt.qt.QDialog', FakeQDialog):
            with patch('aqt.qt.QVBoxLayout'):
                with patch('aqt.qt.QHBoxLayout'):
                    with patch('aqt.qt.QLabel'):
                        with patch('aqt.qt.QPushButton'):
                            with patch('aqt.qt.QComboBox'):
                                with patch('aqt.qt.QProgressBar'):
                                    browser_integration._show_bulk_export_dialog(mock_browser, selected_notes)
                                    
                                    # Verify note was retrieved (called twice for source and dest field combos)
                                    assert browser_integration.mw.col.get_note.call_count == 2
                                    browser_integration.mw.col.get_note.assert_called_with(1)
    
    def test_show_bulk_export_dialog_handles_errors(self, browser_integration):
        """Test that dialog handles errors gracefully."""
        mock_browser = Mock()
        selected_notes = [1, 2, 3]
        
        browser_integration.mw.col.get_note = Mock(side_effect=Exception("Test error"))
        
        with patch('aqt.utils.showWarning') as mock_show_warning:
            browser_integration._show_bulk_export_dialog(mock_browser, selected_notes)
            
            # Verify warning was shown
            mock_show_warning.assert_called_once()


class TestBulkExportPerform:
    """Test bulk export performance."""
    
    def test_perform_bulk_export_processes_notes(self, browser_integration):
        """Test that bulk export processes notes."""
        note_ids = [1, 2, 3]
        source_field = 'Expression'
        dest_field = 'Definition'
        progress_bar = Mock()
        progress_bar.setValue = Mock()
        cancelled = [False]
        
        # Mock note
        mock_note = Mock()
        mock_note.__getitem__ = Mock(return_value='test')
        mock_note.__setitem__ = Mock()
        mock_note.__contains__ = Mock(return_value=True)
        browser_integration.mw.col.get_note = Mock(return_value=mock_note)
        browser_integration.mw.col.update_note = Mock()
        
        # Mock search service
        mock_search_service = Mock()
        mock_search_service.search = Mock(return_value=[{'definition': 'test definition'}])
        browser_integration.plugin.get_search_service = Mock(return_value=mock_search_service)
        
        # Mock export service
        mock_export_service = Mock()
        browser_integration.plugin.get_export_service = Mock(return_value=mock_export_service)
        
        with patch('aqt.qt.QApplication'):
            browser_integration._perform_bulk_export(
                note_ids,
                source_field,
                dest_field,
                progress_bar,
                cancelled
            )
            
            # Verify notes were processed
            assert browser_integration.mw.col.get_note.call_count == len(note_ids)
            
            # Verify progress was updated
            assert progress_bar.setValue.call_count == len(note_ids)
    
    def test_perform_bulk_export_respects_cancellation(self, browser_integration):
        """Test that bulk export respects cancellation."""
        note_ids = [1, 2, 3]
        source_field = 'Expression'
        dest_field = 'Definition'
        progress_bar = Mock()
        progress_bar.setValue = Mock()
        cancelled = [True]  # Already cancelled
        
        browser_integration.mw.col.get_note = Mock()
        
        with patch('aqt.qt.QApplication'):
            browser_integration._perform_bulk_export(
                note_ids,
                source_field,
                dest_field,
                progress_bar,
                cancelled
            )
            
            # Verify no notes were processed
            browser_integration.mw.col.get_note.assert_not_called()
    
    def test_perform_bulk_export_skips_empty_notes(self, browser_integration):
        """Test that bulk export skips empty notes."""
        note_ids = [1]
        source_field = 'Expression'
        dest_field = 'Definition'
        progress_bar = Mock()
        progress_bar.setValue = Mock()
        cancelled = [False]
        
        # Mock note with empty field
        mock_note = Mock()
        mock_note.__getitem__ = Mock(return_value='')
        mock_note.__contains__ = Mock(return_value=True)
        browser_integration.mw.col.get_note = Mock(return_value=mock_note)
        browser_integration.mw.col.update_note = Mock()
        
        # Mock search service
        mock_search_service = Mock()
        browser_integration.plugin.get_search_service = Mock(return_value=mock_search_service)
        
        with patch('aqt.qt.QApplication'):
            browser_integration._perform_bulk_export(
                note_ids,
                source_field,
                dest_field,
                progress_bar,
                cancelled
            )
            
            # Verify search was not called
            mock_search_service.search.assert_not_called()
            
            # Verify note was not updated
            browser_integration.mw.col.update_note.assert_not_called()
    
    def test_perform_bulk_export_handles_search_errors(self, browser_integration):
        """Test that bulk export handles search errors gracefully."""
        note_ids = [1]
        source_field = 'Expression'
        dest_field = 'Definition'
        progress_bar = Mock()
        progress_bar.setValue = Mock()
        cancelled = [False]
        
        # Mock note
        mock_note = Mock()
        mock_note.__getitem__ = Mock(return_value='test')
        mock_note.__contains__ = Mock(return_value=True)
        browser_integration.mw.col.get_note = Mock(return_value=mock_note)
        
        # Mock search service that raises error
        mock_search_service = Mock()
        mock_search_service.search = Mock(side_effect=Exception("Search error"))
        browser_integration.plugin.get_search_service = Mock(return_value=mock_search_service)
        
        with patch('aqt.qt.QApplication'):
            # Should not raise exception
            browser_integration._perform_bulk_export(
                note_ids,
                source_field,
                dest_field,
                progress_bar,
                cancelled
            )
            
            # Verify progress was still updated
            progress_bar.setValue.assert_called_once()
    
    def test_perform_bulk_export_updates_notes_with_definitions(self, browser_integration):
        """Test that bulk export updates notes with definitions."""
        note_ids = [1]
        source_field = 'Expression'
        dest_field = 'Definition'
        progress_bar = Mock()
        progress_bar.setValue = Mock()
        cancelled = [False]
        
        # Mock note
        mock_note = Mock()
        mock_note.__getitem__ = Mock(return_value='test')
        mock_note.__setitem__ = Mock()
        mock_note.__contains__ = Mock(return_value=True)
        browser_integration.mw.col.get_note = Mock(return_value=mock_note)
        browser_integration.mw.col.update_note = Mock()
        
        # Mock search service
        mock_search_service = Mock()
        mock_search_service.search = Mock(return_value=[{'definition': 'test definition'}])
        browser_integration.plugin.get_search_service = Mock(return_value=mock_search_service)
        
        with patch('aqt.qt.QApplication'):
            browser_integration._perform_bulk_export(
                note_ids,
                source_field,
                dest_field,
                progress_bar,
                cancelled
            )
            
            # Verify note was updated
            browser_integration.mw.col.update_note.assert_called_once_with(mock_note)
    
    def test_perform_bulk_export_cleans_html_from_source(self, browser_integration):
        """Test that bulk export cleans HTML from source text."""
        note_ids = [1]
        source_field = 'Expression'
        dest_field = 'Definition'
        progress_bar = Mock()
        progress_bar.setValue = Mock()
        cancelled = [False]
        
        # Mock note with HTML
        mock_note = Mock()
        mock_note.__getitem__ = Mock(return_value='<b>test</b>')
        mock_note.__setitem__ = Mock()
        mock_note.__contains__ = Mock(return_value=True)
        browser_integration.mw.col.get_note = Mock(return_value=mock_note)
        browser_integration.mw.col.update_note = Mock()
        
        # Mock search service
        mock_search_service = Mock()
        mock_search_service.search = Mock(return_value=[{'definition': 'test definition'}])
        browser_integration.plugin.get_search_service = Mock(return_value=mock_search_service)
        
        with patch('aqt.qt.QApplication'):
            browser_integration._perform_bulk_export(
                note_ids,
                source_field,
                dest_field,
                progress_bar,
                cancelled
            )
            
            # Verify search was called with cleaned text
            mock_search_service.search.assert_called_once_with('test')
