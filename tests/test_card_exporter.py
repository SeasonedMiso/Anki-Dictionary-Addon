# -*- coding: utf-8 -*-
"""
Tests for Card Exporter UI component.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import sys

# Note: This test file uses custom Qt mocks specific to CardExporter testing
# rather than the shared mocks in tests/mocks.py due to complex dialog requirements

# Create fake Qt classes
class FakeQWidget:
    """Fake QWidget base class."""
    
    def __init__(self, *args, **kwargs):
        self.parent = kwargs.get('parent', args[0] if args else None)
        self._visible = False
        self._window_title = ""
        self._size = (500, 150)
        self._min_size = (500, 150)
        self._layout = None
        self._modal = False
    
    def setWindowTitle(self, title): self._window_title = title
    def setMinimumSize(self, w, h): self._min_size = (w, h)
    def setMinimumWidth(self, w): self._min_size = (w, self._min_size[1])
    def setMinimumHeight(self, h): self._min_size = (self._min_size[0], h)
    def resize(self, w, h): self._size = (w, h)
    def setModal(self, modal): self._modal = modal
    def show(self): self._visible = True
    def hide(self): self._visible = False
    def close(self): self._visible = False
    def isVisible(self): return self._visible
    def setLayout(self, layout): self._layout = layout


class FakeQDialog(FakeQWidget):
    """Fake QDialog."""
    pass


class FakeQLabel(FakeQWidget):
    """Fake QLabel."""
    
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text
    
    def setText(self, text): self._text = text
    def text(self): return self._text


class FakeQProgressBar(FakeQWidget):
    """Fake QProgressBar."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = 0
        self._minimum = 0
        self._maximum = 100
    
    def setValue(self, value): self._value = value
    def value(self): return self._value
    def setMinimum(self, minimum): self._minimum = minimum
    def setMaximum(self, maximum): self._maximum = maximum
    def minimum(self): return self._minimum
    def maximum(self): return self._maximum


class FakeQPushButton(FakeQWidget):
    """Fake QPushButton."""
    
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text
        self._enabled = True
        self.clicked = Mock()
    
    def setText(self, text): self._text = text
    def text(self): return self._text
    def setEnabled(self, enabled): self._enabled = enabled
    def isEnabled(self): return self._enabled
    def setFixedWidth(self, w): pass


class FakeQVBoxLayout:
    """Fake QVBoxLayout."""
    def __init__(self): 
        self.widgets = []
        self.layouts = []
    def addWidget(self, widget): self.widgets.append(widget)
    def addLayout(self, layout): self.layouts.append(layout)
    def setContentsMargins(self, *args): pass
    def setSpacing(self, spacing): pass


class FakeQHBoxLayout:
    """Fake QHBoxLayout."""
    def __init__(self): 
        self.widgets = []
    def addWidget(self, widget): self.widgets.append(widget)
    def addStretch(self): pass


class FakeQApplication:
    """Fake QApplication."""
    @staticmethod
    def processEvents():
        pass


class FakeQt:
    """Fake Qt namespace."""
    class WindowModality:
        ApplicationModal = 1


# Setup fake Qt module
fake_qt_module = MagicMock()
fake_qt_module.QWidget = FakeQWidget
fake_qt_module.QDialog = FakeQDialog
fake_qt_module.QLabel = FakeQLabel
fake_qt_module.QProgressBar = FakeQProgressBar
fake_qt_module.QPushButton = FakeQPushButton
fake_qt_module.QVBoxLayout = FakeQVBoxLayout
fake_qt_module.QHBoxLayout = FakeQHBoxLayout
fake_qt_module.QApplication = FakeQApplication
fake_qt_module.Qt = FakeQt

fake_aqt = MagicMock()
fake_aqt.qt = fake_qt_module
fake_aqt.utils = MagicMock()
fake_aqt.utils.showInfo = Mock()
fake_aqt.utils.tooltip = Mock()

sys.modules['aqt'] = fake_aqt
sys.modules['aqt.qt'] = fake_qt_module
sys.modules['aqt.utils'] = fake_aqt.utils

# Mock the dialog utilities
sys.modules['src.utils.dialogs'] = MagicMock()
sys.modules['src.utils.dialogs'].ask_user = Mock(return_value=True)

# Now import the module under test
from src.ui.card_exporter import CardExporter


@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.col = Mock()
    mw.col.getNote = Mock()
    return mw


@pytest.fixture
def mock_export_service():
    """Mock export service."""
    service = Mock()
    service.create_note = Mock(return_value=(True, None))
    return service


@pytest.fixture
def mock_search_service():
    """Mock search service."""
    service = Mock()
    service.search = Mock()
    return service


@pytest.fixture
def mock_browser():
    """Mock browser instance."""
    browser = Mock()
    return browser


@pytest.fixture
def card_exporter(mock_mw, mock_export_service, mock_search_service, mock_browser):
    """Create card exporter instance for testing."""
    exporter = CardExporter(
        mw=mock_mw,
        export_service=mock_export_service,
        search_service=mock_search_service,
        browser=mock_browser
    )
    
    # Add mock methods that Qt would normally provide
    exporter.show = Mock()
    exporter.close = Mock()
    exporter.hide = Mock()
    
    return exporter


class TestCardExporterInitialization:
    """Test card exporter initialization."""
    
    def test_exporter_initialized_with_services(
        self,
        card_exporter,
        mock_mw,
        mock_export_service,
        mock_search_service,
        mock_browser
    ):
        """Test that exporter is initialized with all services."""
        assert card_exporter.mw == mock_mw
        assert card_exporter.export_service == mock_export_service
        assert card_exporter.search_service == mock_search_service
        assert card_exporter.browser == mock_browser
    
    def test_window_title_set(self, card_exporter):
        """Test that window title is set correctly."""
        assert "Bulk Export" in card_exporter._window_title
    
    def test_ui_components_created(self, card_exporter):
        """Test that UI components are created."""
        assert card_exporter.progress_bar is not None
        assert card_exporter.status_label is not None
        assert card_exporter.cancel_button is not None
    
    def test_initial_state(self, card_exporter):
        """Test that initial state is correct."""
        assert card_exporter.is_exporting == False
        assert card_exporter.was_cancelled == False
        assert card_exporter._current_progress == 0
        assert card_exporter._total_items == 0


class TestCardExporterExport:
    """Test export functionality."""
    
    def test_export_selected_cards_calls_export_service(
        self,
        card_exporter,
        mock_export_service,
        mock_mw
    ):
        """Test that export calls ExportService for each card."""
        # Setup mock note
        mock_note = Mock()
        mock_note.__contains__ = Mock(return_value=True)
        mock_note.__getitem__ = Mock(return_value='test_term')
        mock_note.keys = Mock(return_value=['Expression'])
        mock_mw.col.getNote.return_value = mock_note
        
        note_ids = [1, 2, 3]
        
        with patch('src.ui.card_exporter.QApplication.processEvents'):
            successful, failed = card_exporter.export_selected_cards(
                note_ids=note_ids,
                template_name='Basic',
                deck_id=1,
                auto_add_definitions=False
            )
        
        # Verify export service was called for each note
        assert mock_export_service.create_note.call_count == 3
        assert successful == 3
        assert failed == 0
    
    def test_export_updates_progress(self, card_exporter, mock_mw):
        """Test that export updates progress bar."""
        # Setup mock note
        mock_note = Mock()
        mock_note.__contains__ = Mock(return_value=True)
        mock_note.__getitem__ = Mock(return_value='test_term')
        mock_note.keys = Mock(return_value=['Expression'])
        mock_mw.col.getNote.return_value = mock_note
        
        note_ids = [1, 2, 3]
        
        with patch('src.ui.card_exporter.QApplication.processEvents'):
            card_exporter.export_selected_cards(
                note_ids=note_ids,
                template_name='Basic',
                deck_id=1
            )
        
        # Verify progress was updated
        assert card_exporter.progress_bar.value() == 3
        assert "3 of 3" in card_exporter.status_label.text()
    
    def test_export_handles_errors(
        self,
        card_exporter,
        mock_export_service,
        mock_mw
    ):
        """Test that export handles errors gracefully."""
        # Setup mock note that raises exception
        mock_mw.col.getNote.side_effect = Exception("Note not found")
        
        note_ids = [1, 2, 3]
        
        with patch('src.ui.card_exporter.QApplication.processEvents'), \
             patch('src.ui.card_exporter.show_info'):
            successful, failed = card_exporter.export_selected_cards(
                note_ids=note_ids,
                template_name='Basic',
                deck_id=1
            )
        
        # All should fail
        assert successful == 0
        assert failed == 3
    
    def test_export_with_empty_list(self, card_exporter):
        """Test export with empty note list."""
        with patch('src.ui.card_exporter.QApplication.processEvents'), \
             patch('src.ui.card_exporter.show_info'):
            successful, failed = card_exporter.export_selected_cards(
                note_ids=[],
                template_name='Basic',
                deck_id=1
            )
        
        assert successful == 0
        assert failed == 0
    
    def test_export_prevents_concurrent_exports(
        self,
        card_exporter,
        mock_mw
    ):
        """Test that concurrent exports are prevented."""
        # Set exporting state
        card_exporter._is_exporting = True
        
        successful, failed = card_exporter.export_selected_cards(
            note_ids=[1, 2, 3],
            template_name='Basic',
            deck_id=1
        )
        
        # Should return immediately
        assert successful == 0
        assert failed == 0
    
    def test_export_shows_completion_message(
        self,
        card_exporter,
        mock_mw
    ):
        """Test that export shows completion message."""
        # Setup mock note
        mock_note = Mock()
        mock_note.__contains__ = Mock(return_value=True)
        mock_note.__getitem__ = Mock(return_value='test_term')
        mock_note.keys = Mock(return_value=['Expression'])
        mock_mw.col.getNote.return_value = mock_note
        
        with patch('src.ui.card_exporter.QApplication.processEvents'), \
             patch('src.ui.card_exporter.show_info') as mock_show:
            card_exporter.export_selected_cards(
                note_ids=[1, 2],
                template_name='Basic',
                deck_id=1
            )
        
        # Verify completion message was shown
        mock_show.assert_called_once()
        call_args = mock_show.call_args[0][0]
        assert "Export complete" in call_args
        assert "Successfully exported: 2" in call_args


class TestCardExporterCancellation:
    """Test cancellation functionality."""
    
    def test_cancel_export_sets_cancelled_flag(self, card_exporter):
        """Test that cancel sets the cancelled flag."""
        card_exporter._is_exporting = True
        
        with patch('src.ui.card_exporter.ask_user', return_value=True):
            card_exporter.cancel_export()
        
        assert card_exporter.was_cancelled == True
    
    def test_cancel_export_requires_confirmation(self, card_exporter):
        """Test that cancel requires user confirmation."""
        card_exporter._is_exporting = True
        
        with patch('src.ui.card_exporter.ask_user', return_value=False):
            card_exporter.cancel_export()
        
        # Should not be cancelled
        assert card_exporter.was_cancelled == False
    
    def test_cancel_export_disables_button(self, card_exporter):
        """Test that cancel disables the cancel button."""
        card_exporter._is_exporting = True
        
        with patch('src.ui.card_exporter.ask_user', return_value=True):
            card_exporter.cancel_export()
        
        assert card_exporter.cancel_button.isEnabled() == False
    
    def test_cancel_export_updates_status(self, card_exporter):
        """Test that cancel updates status label."""
        card_exporter._is_exporting = True
        
        with patch('src.ui.card_exporter.ask_user', return_value=True):
            card_exporter.cancel_export()
        
        assert "Cancelling" in card_exporter.status_label.text()
    
    def test_cancel_when_not_exporting_closes_dialog(self, card_exporter):
        """Test that cancel when not exporting closes dialog."""
        card_exporter._is_exporting = False
        card_exporter.close = Mock()
        
        card_exporter.cancel_export()
        
        card_exporter.close.assert_called_once()
    
    def test_export_stops_when_cancelled(
        self,
        card_exporter,
        mock_export_service,
        mock_mw
    ):
        """Test that export stops when cancelled."""
        # Setup mock note
        mock_note = Mock()
        mock_note.__contains__ = Mock(return_value=True)
        mock_note.__getitem__ = Mock(return_value='test_term')
        mock_note.keys = Mock(return_value=['Expression'])
        mock_mw.col.getNote.return_value = mock_note
        
        # Cancel after first export
        def side_effect(*args, **kwargs):
            card_exporter._cancelled = True
            return (True, None)
        
        mock_export_service.create_note.side_effect = side_effect
        
        note_ids = [1, 2, 3, 4, 5]
        
        with patch('src.ui.card_exporter.QApplication.processEvents'), \
             patch('src.ui.card_exporter.show_info'):
            successful, failed = card_exporter.export_selected_cards(
                note_ids=note_ids,
                template_name='Basic',
                deck_id=1
            )
        
        # Should only export one card before cancelling
        assert mock_export_service.create_note.call_count == 1
        assert successful == 1
    
    def test_cancelled_export_shows_cancellation_message(
        self,
        card_exporter,
        mock_mw,
        mock_export_service
    ):
        """Test that cancelled export shows cancellation message."""
        # Setup mock note
        mock_note = Mock()
        mock_note.__contains__ = Mock(return_value=True)
        mock_note.__getitem__ = Mock(return_value='test_term')
        mock_note.keys = Mock(return_value=['Expression'])
        mock_mw.col.getNote.return_value = mock_note
        
        # Cancel after first export
        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                card_exporter._cancelled = True
            return (True, None)
        
        mock_export_service.create_note.side_effect = side_effect
        
        with patch('src.ui.card_exporter.QApplication.processEvents'), \
             patch('src.ui.card_exporter.show_info') as mock_show:
            card_exporter.export_selected_cards(
                note_ids=[1, 2, 3],
                template_name='Basic',
                deck_id=1
            )
        
        # Verify cancellation message was shown
        mock_show.assert_called_once()
        call_args = mock_show.call_args[0][0]
        assert "cancelled" in call_args.lower()


class TestCardExporterProgressFeedback:
    """Test progress feedback functionality."""
    
    def test_update_progress_updates_bar(self, card_exporter):
        """Test that update_progress updates progress bar."""
        card_exporter.update_progress(5, 10)
        
        assert card_exporter.progress_bar.value() == 5
    
    def test_update_progress_updates_label(self, card_exporter):
        """Test that update_progress updates status label."""
        card_exporter.update_progress(5, 10)
        
        assert "5 of 10" in card_exporter.status_label.text()
    
    def test_progress_bar_maximum_set_correctly(
        self,
        card_exporter,
        mock_mw
    ):
        """Test that progress bar maximum is set to total items."""
        # Setup mock note
        mock_note = Mock()
        mock_note.__contains__ = Mock(return_value=True)
        mock_note.__getitem__ = Mock(return_value='test_term')
        mock_note.keys = Mock(return_value=['Expression'])
        mock_mw.col.getNote.return_value = mock_note
        
        note_ids = [1, 2, 3, 4, 5]
        
        with patch('src.ui.card_exporter.QApplication.processEvents'), \
             patch('src.ui.card_exporter.show_info'):
            card_exporter.export_selected_cards(
                note_ids=note_ids,
                template_name='Basic',
                deck_id=1
            )
        
        assert card_exporter.progress_bar.maximum() == 5


class TestCardExporterHelpers:
    """Test helper methods."""
    
    def test_extract_term_from_note_with_expression_field(self, card_exporter):
        """Test extracting term from note with Expression field."""
        mock_note = Mock()
        mock_note.__contains__ = Mock(side_effect=lambda x: x == 'Expression')
        mock_note.__getitem__ = Mock(return_value='test_term')
        
        term = card_exporter._extract_term_from_note(mock_note)
        
        assert term == 'test_term'
    
    def test_extract_term_from_note_with_word_field(self, card_exporter):
        """Test extracting term from note with Word field."""
        mock_note = Mock()
        mock_note.__contains__ = Mock(side_effect=lambda x: x == 'Word')
        mock_note.__getitem__ = Mock(return_value='test_word')
        
        term = card_exporter._extract_term_from_note(mock_note)
        
        assert term == 'test_word'
    
    def test_extract_term_from_note_falls_back_to_first_field(self, card_exporter):
        """Test extracting term falls back to first non-empty field."""
        mock_note = Mock()
        mock_note.__contains__ = Mock(return_value=False)
        mock_note.keys = Mock(return_value=['CustomField'])
        mock_note.__getitem__ = Mock(return_value='custom_value')
        
        term = card_exporter._extract_term_from_note(mock_note)
        
        assert term == 'custom_value'
    
    def test_extract_term_from_note_strips_whitespace(self, card_exporter):
        """Test that extracted term is stripped of whitespace."""
        mock_note = Mock()
        mock_note.__contains__ = Mock(side_effect=lambda x: x == 'Expression')
        mock_note.__getitem__ = Mock(return_value='  test_term  ')
        
        term = card_exporter._extract_term_from_note(mock_note)
        
        assert term == 'test_term'
    
    def test_extract_term_from_note_returns_none_for_empty(self, card_exporter):
        """Test that extract returns None for empty note."""
        mock_note = Mock()
        mock_note.__contains__ = Mock(return_value=False)
        mock_note.keys = Mock(return_value=['Field1'])
        mock_note.__getitem__ = Mock(return_value='')
        
        term = card_exporter._extract_term_from_note(mock_note)
        
        assert term is None


class TestCardExporterEventHandlers:
    """Test event handlers."""
    
    def test_close_event_prevents_close_during_export(self, card_exporter):
        """Test that close event prevents closing during export."""
        card_exporter._is_exporting = True
        card_exporter._cancelled = False
        
        mock_event = Mock()
        mock_event.ignore = Mock()
        mock_event.accept = Mock()
        
        with patch('src.ui.card_exporter.ask_user', return_value=False):
            card_exporter.closeEvent(mock_event)
        
        # Should ignore the event
        mock_event.ignore.assert_called_once()
        mock_event.accept.assert_not_called()
    
    def test_close_event_allows_close_when_not_exporting(self, card_exporter):
        """Test that close event allows closing when not exporting."""
        card_exporter._is_exporting = False
        
        mock_event = Mock()
        mock_event.ignore = Mock()
        mock_event.accept = Mock()
        
        card_exporter.closeEvent(mock_event)
        
        # Should accept the event
        mock_event.accept.assert_called_once()
        mock_event.ignore.assert_not_called()
    
    def test_close_event_allows_close_when_cancelled(self, card_exporter):
        """Test that close event allows closing when cancelled."""
        card_exporter._is_exporting = True
        card_exporter._cancelled = True
        
        mock_event = Mock()
        mock_event.ignore = Mock()
        mock_event.accept = Mock()
        
        card_exporter.closeEvent(mock_event)
        
        # Should accept the event
        mock_event.accept.assert_called_once()
        mock_event.ignore.assert_not_called()


class TestCardExporterProperties:
    """Test property accessors."""
    
    def test_is_exporting_property(self, card_exporter):
        """Test is_exporting property."""
        assert card_exporter.is_exporting == False
        
        card_exporter._is_exporting = True
        assert card_exporter.is_exporting == True
    
    def test_was_cancelled_property(self, card_exporter):
        """Test was_cancelled property."""
        assert card_exporter.was_cancelled == False
        
        card_exporter._cancelled = True
        assert card_exporter.was_cancelled == True
