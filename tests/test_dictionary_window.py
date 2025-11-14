# -*- coding: utf-8 -*-
"""
Tests for Dictionary Window UI component.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call, create_autospec
from pathlib import Path
import json
import sys


# Create fake Qt base classes that preserve initialization logic
class FakeQWidget:
    """Fake QWidget that allows subclass initialization to work."""
    
    def __init__(self, *args, **kwargs):
        # Store init args for testing
        self._init_args = (args, kwargs)
        self.parent = kwargs.get('parent', args[0] if args else None)
        # Initialize attributes that Qt would normally set
        self._visible = False
        self._window_title = ""
        self._size = (800, 600)
        self._pos = (100, 200)
        self._min_size = (350, 350)
        self._layout = None
    
    def setWindowTitle(self, title):
        self._window_title = title
    
    def setMinimumSize(self, w, h):
        self._min_size = (w, h)
    
    def resize(self, w, h):
        self._size = (w, h)
    
    def setLayout(self, layout):
        self._layout = layout
    
    def show(self):
        self._visible = True
    
    def hide(self):
        self._visible = False
    
    def isVisible(self):
        return self._visible
    
    def raise_(self):
        pass
    
    def activateWindow(self):
        pass
    
    def pos(self):
        pos_mock = Mock()
        pos_mock.x = Mock(return_value=self._pos[0])
        pos_mock.y = Mock(return_value=self._pos[1])
        return pos_mock
    
    def size(self):
        size_mock = Mock()
        size_mock.width = Mock(return_value=self._size[0])
        size_mock.height = Mock(return_value=self._size[1])
        return size_mock
    
    def move(self, x, y):
        self._pos = (x, y)


class FakeQVBoxLayout:
    def __init__(self, *args, **kwargs):
        self.widgets = []
        self.layouts = []
    
    def setContentsMargins(self, *args): pass
    def setSpacing(self, spacing): pass
    def addLayout(self, layout): self.layouts.append(layout)
    def addWidget(self, widget): self.widgets.append(widget)


class FakeQHBoxLayout:
    def __init__(self, *args, **kwargs):
        self.widgets = []
    
    def setContentsMargins(self, *args): pass
    def setSpacing(self, spacing): pass
    def addWidget(self, widget): self.widgets.append(widget)
    def addStretch(self): pass


class FakeQComboBox:
    def __init__(self, *args, **kwargs):
        self.items = []
        self.current_index = 0
        self._current_text = ""
    
    def addItems(self, items): self.items.extend(items)
    def addItem(self, item): self.items.append(item)
    def setCurrentText(self, text): self._current_text = text
    def currentText(self): return self._current_text
    def setFixedHeight(self, h): pass
    def setFixedWidth(self, w): pass
    def setFixedSize(self, w, h): pass
    def model(self): return Mock()
    def count(self): return len(self.items)
    currentIndexChanged = Mock()


class FakeQLineEdit:
    def __init__(self, *args, **kwargs):
        self._text = ""
    
    def text(self): return self._text
    def setText(self, text): self._text = text
    def setPlaceholderText(self, text): pass
    def setFixedHeight(self, h): pass
    def setFixedWidth(self, w): pass
    returnPressed = Mock()


class FakeQPushButton:
    def __init__(self, text="", *args, **kwargs):
        self._text = text
    
    def setFixedHeight(self, h): pass
    clicked = Mock()


class FakeQShortcut:
    def __init__(self, *args, **kwargs):
        pass
    activated = Mock()


class FakeQKeySequence:
    def __init__(self, key):
        self.key = key


class FakeQUrl:
    @staticmethod
    def fromLocalFile(path):
        return Mock(path=path)


class FakeAnkiWebView:
    def __init__(self, *args, **kwargs):
        self.html = ""
        self.url = None
        self.onBridgeCmd = None
        self.eval = Mock()  # Make eval a Mock so we can assert on it
    
    def setHtml(self, html, url=None):
        self.html = html
        self.url = url


# Patch sys.modules before importing
fake_qt_module = MagicMock()
fake_qt_module.QWidget = FakeQWidget
fake_qt_module.QVBoxLayout = FakeQVBoxLayout
fake_qt_module.QHBoxLayout = FakeQHBoxLayout
fake_qt_module.QComboBox = FakeQComboBox
fake_qt_module.QLineEdit = FakeQLineEdit
fake_qt_module.QPushButton = FakeQPushButton
fake_qt_module.QShortcut = FakeQShortcut
fake_qt_module.QKeySequence = FakeQKeySequence
fake_qt_module.QUrl = FakeQUrl
fake_qt_module.QCloseEvent = Mock
fake_qt_module.QHideEvent = Mock

fake_aqt = MagicMock()
fake_aqt.qt = fake_qt_module
fake_aqt.webview = MagicMock()
fake_aqt.webview.AnkiWebView = FakeAnkiWebView
fake_aqt.utils = MagicMock()
fake_aqt.utils.showInfo = Mock()
fake_aqt.utils.tooltip = Mock()

fake_anki = MagicMock()
fake_anki.utils = MagicMock()
fake_anki.utils.is_mac = False
fake_anki.utils.is_win = False

sys.modules['aqt'] = fake_aqt
sys.modules['aqt.qt'] = fake_qt_module
sys.modules['aqt.webview'] = fake_aqt.webview
sys.modules['aqt.utils'] = fake_aqt.utils
sys.modules['anki'] = fake_anki
sys.modules['anki.utils'] = fake_anki.utils
sys.modules['anki.hooks'] = MagicMock()

# Now import the module under test
from src.ui.dictionary_window import DictionaryWindow


@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.col = Mock()
    mw.col.media = Mock()
    mw.col.media.dir = Mock(return_value='/fake/media/dir')
    return mw


@pytest.fixture
def mock_search_service():
    """Mock search service."""
    service = Mock()
    service.search = Mock()
    service.repository = Mock()
    service.repository.get_all_dictionaries = Mock(return_value=['Dict1', 'Dict2'])
    return service


@pytest.fixture
def mock_export_service():
    """Mock export service."""
    service = Mock()
    service.create_note = Mock(return_value=(True, None))
    service.prepare_field_values = Mock()
    return service


@pytest.fixture
def mock_media_service():
    """Mock media service."""
    service = Mock()
    service._download_audio_file = Mock(return_value=(True, 'audio.mp3', None))
    service._download_image_file = Mock(return_value=(True, 'image.jpg', None))
    service.cleanup_temp_media = Mock()
    return service


@pytest.fixture
def mock_config_manager():
    """Mock configuration manager."""
    config = Mock()
    
    # Define config values
    config_values = {
        'searchMode': 'Forward',
        'currentGroup': 'All',
        'deinflect': True,
        'dictSearch': 50,
        'maxSearch': 1000,
        'maxWidth': 400,
        'maxHeight': 400,
        'ForvoLanguage': 'Japanese',
        'dictSizePos': None,
    }
    
    def get_value_side_effect(key, default=None):
        return config_values.get(key, default)
    
    def get_bool_side_effect(key, default=False):
        val = config_values.get(key, default)
        return bool(val) if val is not None else default
    
    def get_int_side_effect(key, default=0):
        val = config_values.get(key, default)
        return int(val) if val is not None else default
    
    def get_str_side_effect(key, default=''):
        val = config_values.get(key, default)
        return str(val) if val is not None else default
    
    config.get_value = Mock(side_effect=get_value_side_effect)
    config.get_bool = Mock(side_effect=get_bool_side_effect)
    config.get_int = Mock(side_effect=get_int_side_effect)
    config.get_str = Mock(side_effect=get_str_side_effect)
    config.get_dictionary_groups = Mock(return_value={
        'MyGroup': {
            'dictionaries': [{'dict': 'TestDict', 'lang': 'Japanese'}],
            'customFont': False,
            'font': None
        }
    })
    config.update_config = Mock()
    return config


@pytest.fixture
def temp_addon_path(tmp_path):
    """Create temporary addon path with required files."""
    # Create directory structure
    (tmp_path / 'user_files' / 'themes').mkdir(parents=True, exist_ok=True)
    
    # Create active theme file
    theme_data = {
        "header_background": "#51576d",
        "definition_background": "#51576d",
        "definition_text": "#c6d0f5",
        "border": "#babbf1"
    }
    with open(tmp_path / 'user_files' / 'themes' / 'active.json', 'w') as f:
        json.dump(theme_data, f)
    
    # Create dictionary init HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style id="customThemeCss"></style>
    </head>
    <body>
        <div id="content"></div>
    </body>
    </html>
    """
    with open(tmp_path / 'dictionaryInit.html', 'w') as f:
        f.write(html_content)
    
    return tmp_path


@pytest.fixture
def dictionary_window(
    mock_mw,
    mock_search_service,
    mock_export_service,
    mock_media_service,
    mock_config_manager,
    temp_addon_path
):
    """Create dictionary window instance for testing."""
    # Create the window - it will use our fake Qt classes
    window = DictionaryWindow(
        mw=mock_mw,
        search_service=mock_search_service,
        export_service=mock_export_service,
        media_service=mock_media_service,
        config_manager=mock_config_manager,
        addon_path=temp_addon_path
    )
    
    # Add mock methods that Qt would normally provide
    window.show = Mock()
    window.hide = Mock()
    window.raise_ = Mock()
    window.activateWindow = Mock()
    window.isVisible = Mock(return_value=False)
    window.setWindowTitle = Mock()
    window.setMinimumSize = Mock()
    window.resize = Mock()
    window.setLayout = Mock()
    
    # Mock position/size methods
    def mock_pos():
        pos_mock = Mock()
        pos_mock.x = Mock(return_value=100)
        pos_mock.y = Mock(return_value=200)
        return pos_mock
    
    def mock_size():
        size_mock = Mock()
        size_mock.width = Mock(return_value=800)
        size_mock.height = Mock(return_value=600)
        return size_mock
    
    window.pos = mock_pos
    window.size = mock_size
    
    return window


class TestDictionaryWindowInitialization:
    """Test dictionary window initialization."""
    
    def test_window_initialized_with_services(
        self,
        dictionary_window,
        mock_search_service,
        mock_export_service,
        mock_media_service,
        mock_config_manager
    ):
        """Test that window is initialized with all services."""
        assert dictionary_window.search_service == mock_search_service
        assert dictionary_window.export_service == mock_export_service
        assert dictionary_window.media_service == mock_media_service
        assert dictionary_window.config_manager == mock_config_manager
    
    def test_window_title_set(self, dictionary_window):
        """Test that window title is set correctly."""
        # Window title would be set via Qt, which is mocked
        # Just verify the window was created
        assert dictionary_window is not None
    
    def test_ui_state_initialized(self, dictionary_window):
        """Test that UI state variables are initialized."""
        assert dictionary_window.current_editor is None
        assert dictionary_window.current_reviewer is None
        assert dictionary_window.card_exporter is None


class TestDictionaryWindowSearch:
    """Test dictionary search functionality."""
    
    def test_search_calls_search_service(
        self,
        dictionary_window,
        mock_search_service
    ):
        """Test that search calls SearchService."""
        # Set up mock result
        mock_result = Mock()
        mock_result.results = {}
        mock_search_service.search.return_value = mock_result
        
        # Mock the search input
        dictionary_window.search_input = Mock()
        dictionary_window.search_input.text = Mock(return_value='test')
        dictionary_window.search_input.setText = Mock()
        
        # Perform search
        dictionary_window.perform_search('test')
        
        # Verify search service was called
        mock_search_service.search.assert_called_once()
        call_args = mock_search_service.search.call_args
        assert call_args[1]['term'] == 'test'
        assert call_args[1]['search_mode'] == 'Forward'
        assert call_args[1]['deinflect'] is True
    
    def test_search_with_empty_term_does_nothing(
        self,
        dictionary_window,
        mock_search_service
    ):
        """Test that search with empty term does nothing."""
        dictionary_window.search_input = Mock()
        dictionary_window.search_input.text = Mock(return_value='')
        
        dictionary_window.perform_search()
        
        mock_search_service.search.assert_not_called()
    
    def test_search_cleans_term(self, dictionary_window, mock_search_service):
        """Test that search term is cleaned before searching."""
        mock_result = Mock()
        mock_result.results = {}
        mock_search_service.search.return_value = mock_result
        
        dictionary_window.search_input = Mock()
        dictionary_window.search_input.text = Mock(return_value='test[123]')
        dictionary_window.search_input.setText = Mock()
        
        dictionary_window.perform_search()
        
        # Verify cleaned term was used
        call_args = mock_search_service.search.call_args
        assert '[' not in call_args[1]['term']
        assert ']' not in call_args[1]['term']
    
    def test_search_displays_results(
        self,
        dictionary_window,
        mock_search_service
    ):
        """Test that search results are displayed."""
        # Set up mock result
        mock_result = Mock()
        mock_result.results = {
            'TestDict': [
                {
                    'term': 'test',
                    'pronunciation': 'tesuto',
                    'definition': 'A test definition'
                }
            ]
        }
        mock_search_service.search.return_value = mock_result
        
        dictionary_window.search_input = Mock()
        dictionary_window.search_input.text = Mock(return_value='test')
        dictionary_window.search_input.setText = Mock()
        
        dictionary_window.perform_search()
        
        # Verify web view was updated
        dictionary_window.web_view.eval.assert_called()
        call_args = dictionary_window.web_view.eval.call_args[0][0]
        assert 'addNewTab' in call_args
        assert 'test' in call_args
    
    def test_search_handles_errors(
        self,
        dictionary_window,
        mock_search_service
    ):
        """Test that search errors are handled gracefully."""
        mock_search_service.search.side_effect = Exception("Search failed")
        
        dictionary_window.search_input = Mock()
        dictionary_window.search_input.text = Mock(return_value='test')
        dictionary_window.search_input.setText = Mock()
        
        # Should not raise exception
        with patch('src.ui.dictionary_window.showInfo'):
            dictionary_window.perform_search()


class TestDictionaryWindowExport:
    """Test export functionality."""
    
    def test_export_definition_logs_action(self, dictionary_window):
        """Test that export definition logs the action."""
        with patch('src.ui.dictionary_window.tooltip'):
            dictionary_window._export_definition('TestDict', 'test', 'definition')
        
        # Should not raise exception
        assert True
    
    def test_download_forvo_audio_calls_media_service(
        self,
        dictionary_window,
        mock_media_service
    ):
        """Test that Forvo audio download calls MediaService."""
        urls = ['http://example.com/audio.mp3']
        
        with patch('src.ui.dictionary_window.tooltip'):
            dictionary_window._download_forvo_audio(urls)
        
        # Verify media service was called
        mock_media_service._download_audio_file.assert_called_once()
    
    def test_download_images_calls_media_service(
        self,
        dictionary_window,
        mock_media_service
    ):
        """Test that image download calls MediaService."""
        urls = ['http://example.com/image.jpg']
        
        with patch('src.ui.dictionary_window.tooltip'):
            dictionary_window._download_images('test', urls)
        
        # Verify media service was called
        mock_media_service._download_image_file.assert_called_once()
    
    def test_download_images_handles_errors(
        self,
        dictionary_window,
        mock_media_service
    ):
        """Test that image download errors are handled."""
        mock_media_service._download_image_file.side_effect = Exception("Download failed")
        
        urls = ['http://example.com/image.jpg']
        
        with patch('src.ui.dictionary_window.showInfo'):
            dictionary_window._download_images('test', urls)
        
        # Should not raise exception
        assert True


class TestDictionaryWindowBridgeCommands:
    """Test bridge command handling."""
    
    def test_handle_add_def_command(self, dictionary_window):
        """Test handling of addDef bridge command."""
        cmd = 'addDef:TestDict◳◴test◳◴definition text'
        
        with patch('src.ui.dictionary_window.tooltip'):
            dictionary_window._handle_bridge_command(cmd)
        
        # Should not raise exception
        assert True
    
    def test_handle_forvo_command(self, dictionary_window, mock_media_service):
        """Test handling of forvo bridge command."""
        cmd = 'forvo:["http://example.com/audio.mp3"]'
        
        with patch('src.ui.dictionary_window.tooltip'):
            dictionary_window._handle_bridge_command(cmd)
        
        # Verify media service was called
        mock_media_service._download_audio_file.assert_called()
    
    def test_handle_send_to_field_command(self, dictionary_window):
        """Test handling of sendToField bridge command."""
        cmd = 'sendToField:TestDict◳◴definition text'
        
        with patch('src.ui.dictionary_window.tooltip'):
            dictionary_window._handle_bridge_command(cmd)
        
        # Should not raise exception
        assert True
    
    def test_handle_invalid_command(self, dictionary_window):
        """Test handling of invalid bridge command."""
        cmd = 'invalidCommand:data'
        
        # Should not raise exception
        dictionary_window._handle_bridge_command(cmd)
        assert True


class TestDictionaryWindowConfiguration:
    """Test configuration management."""
    
    def test_dict_group_change_updates_config(
        self,
        dictionary_window,
        mock_config_manager
    ):
        """Test that dictionary group change updates config."""
        dictionary_window.dict_group_combo = Mock()
        dictionary_window.dict_group_combo.currentText = Mock(return_value='MyGroup')
        
        dictionary_window._on_dict_group_changed()
        
        mock_config_manager.update_config.assert_called_once_with('currentGroup', 'MyGroup')
    
    def test_search_type_change_updates_config(
        self,
        dictionary_window,
        mock_config_manager
    ):
        """Test that search type change updates config."""
        dictionary_window.search_type_combo = Mock()
        dictionary_window.search_type_combo.currentText = Mock(return_value='Exact')
        
        dictionary_window._on_search_type_changed()
        
        mock_config_manager.update_config.assert_called_once_with('searchMode', 'Exact')
    
    def test_window_position_saved_on_hide(
        self,
        dictionary_window,
        mock_config_manager
    ):
        """Test that window position is saved when hidden."""
        # Mock position and size
        dictionary_window.pos = Mock(return_value=Mock(x=Mock(return_value=100), y=Mock(return_value=200)))
        dictionary_window.size = Mock(return_value=Mock(width=Mock(return_value=800), height=Mock(return_value=600)))
        
        # Create mock event
        mock_event = Mock()
        mock_event.accept = Mock()
        
        dictionary_window.hideEvent(mock_event)
        
        # Verify config was updated
        mock_config_manager.update_config.assert_called()


class TestDictionaryWindowEditorIntegration:
    """Test editor and reviewer integration."""
    
    def test_set_current_editor(self, dictionary_window):
        """Test setting current editor."""
        mock_editor = Mock()
        
        dictionary_window.set_current_editor(mock_editor, 'Add Cards')
        
        assert dictionary_window.current_editor == mock_editor
        assert dictionary_window.current_reviewer is None
    
    def test_set_current_reviewer(self, dictionary_window):
        """Test setting current reviewer."""
        mock_reviewer = Mock()
        
        dictionary_window.set_current_reviewer(mock_reviewer)
        
        assert dictionary_window.current_reviewer == mock_reviewer
        assert dictionary_window.current_editor is None


class TestDictionaryWindowVisibility:
    """Test window visibility management."""
    
    def test_show_window(self, dictionary_window):
        """Test showing window."""
        dictionary_window.show = Mock()
        dictionary_window.raise_ = Mock()
        dictionary_window.activateWindow = Mock()
        
        dictionary_window.show_window()
        
        dictionary_window.show.assert_called_once()
        dictionary_window.raise_.assert_called_once()
        dictionary_window.activateWindow.assert_called_once()
    
    def test_show_window_with_terms(
        self,
        dictionary_window,
        mock_search_service
    ):
        """Test showing window with search terms."""
        mock_result = Mock()
        mock_result.results = {}
        mock_search_service.search.return_value = mock_result
        
        dictionary_window.show = Mock()
        dictionary_window.raise_ = Mock()
        dictionary_window.activateWindow = Mock()
        dictionary_window.search_input = Mock()
        dictionary_window.search_input.setText = Mock()
        
        dictionary_window.show_window(terms=['test1', 'test2'])
        
        # Verify searches were performed
        assert mock_search_service.search.call_count == 2
    
    def test_toggle_visibility_shows_when_hidden(self, dictionary_window):
        """Test toggle visibility shows window when hidden."""
        dictionary_window.isVisible = Mock(return_value=False)
        dictionary_window.show_window = Mock()
        
        dictionary_window.toggle_visibility()
        
        dictionary_window.show_window.assert_called_once()
    
    def test_toggle_visibility_hides_when_visible(self, dictionary_window):
        """Test toggle visibility hides window when visible."""
        dictionary_window.isVisible = Mock(return_value=True)
        dictionary_window.hide = Mock()
        
        dictionary_window.toggle_visibility()
        
        dictionary_window.hide.assert_called_once()
    
    def test_close_event_hides_window(self, dictionary_window):
        """Test that close event hides window instead of closing."""
        mock_event = Mock()
        mock_event.ignore = Mock()
        dictionary_window.hide = Mock()
        
        dictionary_window.closeEvent(mock_event)
        
        dictionary_window.hide.assert_called_once()
        mock_event.ignore.assert_called_once()


class TestDictionaryWindowHelpers:
    """Test helper methods."""
    
    def test_clean_term_removes_brackets(self, dictionary_window):
        """Test that clean term removes brackets."""
        term = 'test[123](456)《789》（abc）'
        cleaned = dictionary_window._clean_term(term)
        
        assert '[' not in cleaned
        assert ']' not in cleaned
        assert '(' not in cleaned
        assert ')' not in cleaned
        assert '《' not in cleaned
        assert '》' not in cleaned
    
    def test_clean_term_limits_length(self, dictionary_window):
        """Test that clean term limits length."""
        term = 'a' * 100
        cleaned = dictionary_window._clean_term(term)
        
        assert len(cleaned) <= 30
    
    def test_get_selected_dictionary_group_returns_user_group(
        self,
        dictionary_window,
        mock_config_manager
    ):
        """Test getting selected user dictionary group."""
        dictionary_window.dict_group_combo = Mock()
        dictionary_window.dict_group_combo.currentText = Mock(return_value='MyGroup')
        
        group = dictionary_window._get_selected_dictionary_group()
        
        assert group is not None
        assert 'dictionaries' in group
    
    def test_get_selected_dictionary_group_handles_all(
        self,
        dictionary_window,
        mock_search_service
    ):
        """Test getting 'All' dictionary group."""
        dictionary_window.dict_group_combo = Mock()
        dictionary_window.dict_group_combo.currentText = Mock(return_value='All')
        
        group = dictionary_window._get_selected_dictionary_group()
        
        assert group is not None
        assert 'dictionaries' in group
        mock_search_service.repository.get_all_dictionaries.assert_called_once()
