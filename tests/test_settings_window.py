# -*- coding: utf-8 -*-
"""
Tests for Settings Window UI component.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import sys


# Create fake Qt classes
class FakeQWidget:
    """Fake QWidget base class."""
    
    def __init__(self, *args, **kwargs):
        self.parent = kwargs.get('parent', args[0] if args else None)
        self._visible = False
        self._window_title = ""
        self._size = (850, 550)
        self._min_size = (850, 550)
        self._layout = None
    
    def setWindowTitle(self, title): self._window_title = title
    def setMinimumSize(self, w, h): self._min_size = (w, h)
    def resize(self, w, h): self._size = (w, h)
    def setContextMenuPolicy(self, policy): pass
    def setWindowIcon(self, icon): pass
    def show(self): self._visible = True
    def hide(self): self._visible = False
    def close(self): self._visible = False
    def isVisible(self): return self._visible
    def setLayout(self, layout): self._layout = layout


class FakeQTabWidget(FakeQWidget):
    """Fake QTabWidget."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tabs = []
    
    def addTab(self, widget, title):
        self.tabs.append((widget, title))


class FakeQCheckBox(FakeQWidget):
    """Fake QCheckBox."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._checked = False
    
    def isChecked(self): return self._checked
    def setChecked(self, checked): self._checked = checked
    def setFixedHeight(self, h): pass


class FakeQSpinBox(FakeQWidget):
    """Fake QSpinBox."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = 0
        self._range = (0, 100)
    
    def value(self): return self._value
    def setValue(self, value): self._value = value
    def setRange(self, min_val, max_val): self._range = (min_val, max_val)
    def setFixedWidth(self, w): pass


class FakeQComboBox(FakeQWidget):
    """Fake QComboBox."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self._current_text = ""
    
    def addItems(self, items): self.items.extend(items)
    def currentText(self): return self._current_text
    def setCurrentText(self, text): self._current_text = text
    def setFixedWidth(self, w): pass


class FakeQLineEdit(FakeQWidget):
    """Fake QLineEdit."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = ""
    
    def text(self): return self._text
    def setText(self, text): self._text = text


class FakeQPushButton(FakeQWidget):
    """Fake QPushButton."""
    
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text
        self.clicked = Mock()
    
    def setFixedWidth(self, w): pass
    def setFixedHeight(self, h): pass
    def setToolTip(self, text): pass


class FakeQTableWidget(FakeQWidget):
    """Fake QTableWidget."""
    
    class EditTrigger:
        NoEditTriggers = 0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rows = []
        self._row_count = 0
        self._col_count = 0
    
    def setColumnCount(self, count): self._col_count = count
    def setRowCount(self, count): self._row_count = count
    def rowCount(self): return self._row_count
    def setItem(self, row, col, item): pass
    def item(self, row, col): 
        mock_item = Mock()
        mock_item.text = Mock(return_value=f"Item{row}")
        return mock_item
    def setCellWidget(self, row, col, widget): pass
    def removeRow(self, row): self._row_count -= 1
    def horizontalHeader(self): return Mock()
    def setSortingEnabled(self, enabled): pass
    def setEditTriggers(self, triggers): pass
    def setSelectionBehavior(self, behavior): pass
    def setColumnWidth(self, col, width): pass


class FakeQLabel(FakeQWidget):
    """Fake QLabel."""
    
    def __init__(self, text="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text = text
    
    def setFixedHeight(self, h): pass
    def setFixedWidth(self, w): pass
    def setToolTip(self, tip): pass


class FakeQGroupBox(FakeQWidget):
    """Fake QGroupBox."""
    
    def __init__(self, title="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._title = title
        self._layout = None
    
    def setLayout(self, layout): self._layout = layout


class FakeQVBoxLayout:
    """Fake QVBoxLayout."""
    def __init__(self): pass
    def addWidget(self, widget): pass
    def addLayout(self, layout): pass
    def addStretch(self): pass


class FakeQHBoxLayout:
    """Fake QHBoxLayout."""
    def __init__(self): pass
    def addWidget(self, widget): pass
    def addLayout(self, layout): pass
    def addStretch(self): pass


class FakeQFrame(FakeQWidget):
    """Fake QFrame."""
    class Shape:
        VLine = 5
    class Shadow:
        Plain = 1
    
    def setFrameShape(self, shape): pass
    def setFrameShadow(self, shadow): pass
    def setStyleSheet(self, style): pass


class FakeQShortcut:
    """Fake QShortcut."""
    def __init__(self, *args, **kwargs):
        self.activated = Mock()


class FakeQKeySequence:
    """Fake QKeySequence."""
    def __init__(self, key): self.key = key


class FakeQIcon:
    """Fake QIcon."""
    def __init__(self, path): self.path = path


class FakeQFileDialog:
    """Fake QFileDialog."""
    @staticmethod
    def getExistingDirectory(*args, **kwargs):
        return "/fake/directory"


class FakeQt:
    """Fake Qt namespace."""
    class ContextMenuPolicy:
        NoContextMenu = 0
    class ResizeMode:
        Stretch = 0
        Fixed = 1
    class EditTrigger:
        NoEditTriggers = 0
    class SelectionBehavior:
        SelectRows = 0


class FakeQHeaderView:
    """Fake QHeaderView."""
    class ResizeMode:
        Stretch = 0
        Fixed = 1


class FakeQAbstractItemView:
    """Fake QAbstractItemView."""
    class SelectionBehavior:
        SelectRows = 0


class FakeQTableWidgetItem:
    """Fake QTableWidgetItem."""
    def __init__(self, text=""):
        self._text = text
    def text(self): return self._text


# Setup fake Qt module
fake_qt_module = MagicMock()
fake_qt_module.QWidget = FakeQWidget
fake_qt_module.QTabWidget = FakeQTabWidget
fake_qt_module.QCheckBox = FakeQCheckBox
fake_qt_module.QSpinBox = FakeQSpinBox
fake_qt_module.QComboBox = FakeQComboBox
fake_qt_module.QLineEdit = FakeQLineEdit
fake_qt_module.QPushButton = FakeQPushButton
fake_qt_module.QTableWidget = FakeQTableWidget
fake_qt_module.QLabel = FakeQLabel
fake_qt_module.QGroupBox = FakeQGroupBox
fake_qt_module.QVBoxLayout = FakeQVBoxLayout
fake_qt_module.QHBoxLayout = FakeQHBoxLayout
fake_qt_module.QFrame = FakeQFrame
fake_qt_module.QShortcut = FakeQShortcut
fake_qt_module.QKeySequence = FakeQKeySequence
fake_qt_module.QIcon = FakeQIcon
fake_qt_module.QFileDialog = FakeQFileDialog
fake_qt_module.Qt = FakeQt
fake_qt_module.QHeaderView = FakeQHeaderView
fake_qt_module.QAbstractItemView = FakeQAbstractItemView
fake_qt_module.QTableWidgetItem = FakeQTableWidgetItem

fake_aqt = MagicMock()
fake_aqt.qt = fake_qt_module
fake_aqt.utils = MagicMock()
fake_aqt.utils.showInfo = Mock()
fake_aqt.utils.tooltip = Mock()

fake_anki = MagicMock()
fake_anki.utils = MagicMock()
fake_anki.utils.is_mac = False
fake_anki.utils.is_win = False
fake_anki.utils.is_lin = False

sys.modules['aqt'] = fake_aqt
sys.modules['aqt.qt'] = fake_qt_module
sys.modules['aqt.utils'] = fake_aqt.utils
sys.modules['anki'] = fake_anki
sys.modules['anki.utils'] = fake_anki.utils

# Mock the dialog utilities
sys.modules['src.utils.dialogs'] = MagicMock()

# Now import the module under test
from src.ui.settings_window import SettingsWindow
from src.config.manager import ConfigManager



@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.dictSettings = None
    mw.ankiDictionary = None
    mw.miDictDB = Mock()
    mw.miDictDB.getAllDictsWithLang = Mock(return_value=[
        {'dict': 'TestDict', 'lang': 'Japanese'},
        {'dict': 'AnotherDict', 'lang': 'English'}
    ])
    return mw


@pytest.fixture
def mock_config_manager():
    """Mock configuration manager."""
    config = Mock(spec=ConfigManager)
    
    # Default config values
    config_values = {
        'dictOnStart': False,
        'highlightSentences': True,
        'highlightTarget': True,
        'maxSearch': 1000,
        'dictSearch': 50,
        'jReadingCards': True,
        'jReadingEdit': True,
        'googleSearchRegion': 'United States',
        'ForvoLanguage': 'Japanese',
        'maxWidth': 400,
        'maxHeight': 400,
        'frontBracket': '【',
        'backBracket': '】',
        'showTarget': False,
        'tooltips': True,
        'globalHotkeys': True,
        'openOnGlobal': True,
        'safeSearch': True,
        'mp3Convert': True,
        'disableCondensed': False,
        'dictAlwaysOnTop': False,
        'condensedAudioDirectory': False,
        'DictionaryGroups': {
            'TestGroup': {
                'dictionaries': [{'dict': 'TestDict', 'lang': 'Japanese'}],
                'customFont': False
            }
        },
        'ExportTemplates': {
            'TestTemplate': {
                'noteType': 'Basic',
                'fields': {}
            }
        }
    }
    
    def get_config_side_effect():
        return config_values.copy()
    
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
    
    config.get_config = Mock(side_effect=get_config_side_effect)
    config.get_value = Mock(side_effect=get_value_side_effect)
    config.get_bool = Mock(side_effect=get_bool_side_effect)
    config.get_int = Mock(side_effect=get_int_side_effect)
    config.get_str = Mock(side_effect=get_str_side_effect)
    config.get_dictionary_groups = Mock(return_value=config_values['DictionaryGroups'])
    config.get_export_templates = Mock(return_value=config_values['ExportTemplates'])
    config.write_config = Mock()
    config.reset_to_defaults = Mock()
    
    return config


@pytest.fixture
def mock_plugin():
    """Mock plugin coordinator."""
    plugin = Mock()
    plugin.refresh_config = Mock()
    plugin.ffmpeg_installer = Mock()
    plugin.ffmpeg_installer.installFFMPEG = Mock()
    return plugin


@pytest.fixture
def temp_addon_path(tmp_path):
    """Create temporary addon path."""
    icons_dir = tmp_path / 'icons'
    icons_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a fake icon file
    (icons_dir / 'miso.png').touch()
    
    return tmp_path


@pytest.fixture
def settings_window(mock_mw, mock_config_manager, mock_plugin, temp_addon_path):
    """Create settings window instance for testing."""
    with patch('src.ui.settings_window.miInfo'), \
         patch('src.ui.settings_window.miAsk'):
        window = SettingsWindow(
            mw=mock_mw,
            config_manager=mock_config_manager,
            plugin=mock_plugin,
            addon_path=temp_addon_path,
            reboot_callback=None
        )
    return window


class TestSettingsWindowInitialization:
    """Test settings window initialization."""
    
    def test_window_initialized_with_dependencies(
        self,
        settings_window,
        mock_mw,
        mock_config_manager,
        mock_plugin
    ):
        """Test that window is initialized with all dependencies."""
        assert settings_window.mw == mock_mw
        assert settings_window.config_manager == mock_config_manager
        assert settings_window.plugin == mock_plugin
    
    def test_window_title_set(self, settings_window):
        """Test that window title is set correctly."""
        assert settings_window._window_title == "Anki Dictionary Settings"
    
    def test_widgets_created(self, settings_window):
        """Test that all widgets are created."""
        assert settings_window.tooltip_cb is not None
        assert settings_window.max_img_width is not None
        assert settings_window.max_img_height is not None
        assert settings_window.google_country is not None
        assert settings_window.forvo_lang is not None
        assert settings_window.front_bracket is not None
        assert settings_window.back_bracket is not None


class TestSettingsWindowLoadSettings:
    """Test settings loading functionality."""
    
    def test_load_settings_from_config_manager(
        self,
        settings_window,
        mock_config_manager
    ):
        """Test that settings are loaded from ConfigManager."""
        # Verify ConfigManager methods were called
        assert mock_config_manager.get_bool.called
        assert mock_config_manager.get_int.called
        assert mock_config_manager.get_str.called
    
    def test_boolean_settings_loaded(self, settings_window):
        """Test that boolean settings are loaded correctly."""
        assert settings_window.open_on_start.isChecked() == False
        assert settings_window.highlight_sentence.isChecked() == True
        assert settings_window.highlight_target.isChecked() == True
        assert settings_window.tooltip_cb.isChecked() == True
    
    def test_integer_settings_loaded(self, settings_window):
        """Test that integer settings are loaded correctly."""
        assert settings_window.total_defs.value() == 1000
        assert settings_window.dict_defs.value() == 50
        assert settings_window.max_img_width.value() == 400
        assert settings_window.max_img_height.value() == 400
    
    def test_string_settings_loaded(self, settings_window):
        """Test that string settings are loaded correctly."""
        assert settings_window.google_country.currentText() == 'United States'
        assert settings_window.forvo_lang.currentText() == 'Japanese'
        assert settings_window.front_bracket.text() == '【'
        assert settings_window.back_bracket.text() == '】'
    
    def test_audio_directory_loaded(self, settings_window):
        """Test that audio directory is loaded correctly."""
        # Default is False, so button should show "Choose Directory"
        assert settings_window.choose_audio_directory.text() == "Choose Directory"


class TestSettingsWindowValidation:
    """Test settings validation functionality."""
    
    def test_validate_settings_success(self, settings_window):
        """Test that valid settings pass validation."""
        is_valid, error = settings_window.validate_settings()
        assert is_valid == True
        assert error is None
    
    def test_validate_total_defs_minimum(self, settings_window):
        """Test validation of total defs minimum value."""
        settings_window.total_defs.setValue(0)
        is_valid, error = settings_window.validate_settings()
        assert is_valid == False
        assert "Max Total Search Results" in error
    
    def test_validate_dict_defs_minimum(self, settings_window):
        """Test validation of dict defs minimum value."""
        settings_window.dict_defs.setValue(0)
        is_valid, error = settings_window.validate_settings()
        assert is_valid == False
        assert "Max Dictionary Search Results" in error
    
    def test_validate_image_width_minimum(self, settings_window):
        """Test validation of image width minimum value."""
        settings_window.max_img_width.setValue(10)
        is_valid, error = settings_window.validate_settings()
        assert is_valid == False
        assert "Maximum Image Width" in error
    
    def test_validate_image_height_minimum(self, settings_window):
        """Test validation of image height minimum value."""
        settings_window.max_img_height.setValue(10)
        is_valid, error = settings_window.validate_settings()
        assert is_valid == False
        assert "Maximum Image Height" in error
    
    def test_validate_bracket_length(self, settings_window):
        """Test validation of bracket text length."""
        settings_window.front_bracket.setText("a" * 20)
        is_valid, error = settings_window.validate_settings()
        assert is_valid == False
        assert "bracket" in error.lower()


class TestSettingsWindowSaveSettings:
    """Test settings saving functionality."""
    
    def test_save_settings_calls_config_manager(
        self,
        settings_window,
        mock_config_manager
    ):
        """Test that save settings calls ConfigManager.write_config."""
        with patch('src.ui.settings_window.showInfo'):
            result = settings_window.save_settings()
        
        assert result == True
        mock_config_manager.write_config.assert_called_once()
    
    def test_save_settings_validates_first(
        self,
        settings_window,
        mock_config_manager
    ):
        """Test that save settings validates before saving."""
        settings_window.total_defs.setValue(0)  # Invalid value
        
        with patch('src.ui.settings_window.showInfo'):
            result = settings_window.save_settings()
        
        assert result == False
        mock_config_manager.write_config.assert_not_called()
    
    def test_save_settings_updates_all_values(
        self,
        settings_window,
        mock_config_manager
    ):
        """Test that save settings updates all configuration values."""
        # Change some values
        settings_window.open_on_start.setChecked(True)
        settings_window.total_defs.setValue(500)
        settings_window.front_bracket.setText('《')
        
        with patch('src.ui.settings_window.showInfo'):
            settings_window.save_settings()
        
        # Verify write_config was called with updated values
        call_args = mock_config_manager.write_config.call_args[0][0]
        assert call_args['dictOnStart'] == True
        assert call_args['maxSearch'] == 500
        assert call_args['frontBracket'] == '《'
    
    def test_save_settings_notifies_plugin(
        self,
        settings_window,
        mock_plugin
    ):
        """Test that save settings notifies plugin of changes."""
        with patch('src.ui.settings_window.showInfo'):
            settings_window.save_settings()
        
        mock_plugin.refresh_config.assert_called_once()
    
    def test_save_settings_installs_ffmpeg_if_enabled(
        self,
        settings_window,
        mock_plugin
    ):
        """Test that FFMPEG is installed if mp3Convert is enabled."""
        settings_window.convert_to_mp3.setChecked(True)
        
        with patch('src.ui.settings_window.showInfo'):
            settings_window.save_settings()
        
        mock_plugin.ffmpeg_installer.installFFMPEG.assert_called_once()
    
    def test_save_settings_handles_validation_error(
        self,
        settings_window,
        mock_config_manager
    ):
        """Test that save settings handles validation errors."""
        mock_config_manager.write_config.side_effect = ValueError("Invalid config")
        
        with patch('src.ui.settings_window.showInfo') as mock_show:
            result = settings_window.save_settings()
        
        assert result == False
        mock_show.assert_called()
        assert "validation failed" in mock_show.call_args[0][0].lower()


class TestSettingsWindowResetDefaults:
    """Test reset to defaults functionality."""
    
    def test_reset_to_defaults_calls_config_manager(
        self,
        settings_window,
        mock_config_manager
    ):
        """Test that reset to defaults calls ConfigManager.reset_to_defaults."""
        with patch('src.ui.settings_window.miAsk', return_value=True):
            settings_window.reset_to_defaults()
        
        mock_config_manager.reset_to_defaults.assert_called_once()
    
    def test_reset_to_defaults_requires_confirmation(
        self,
        settings_window,
        mock_config_manager
    ):
        """Test that reset to defaults requires user confirmation."""
        with patch('src.ui.settings_window.miAsk', return_value=False):
            settings_window.reset_to_defaults()
        
        mock_config_manager.reset_to_defaults.assert_not_called()
    
    def test_reset_to_defaults_closes_window(self, settings_window):
        """Test that reset to defaults closes the window."""
        with patch('src.ui.settings_window.miAsk', return_value=True):
            settings_window.reset_to_defaults()
        
        assert settings_window.isVisible() == False


class TestSettingsWindowGroupManagement:
    """Test dictionary group management."""
    
    def test_load_group_table(self, settings_window, mock_config_manager):
        """Test loading dictionary groups into table."""
        # Groups should be loaded during initialization
        assert mock_config_manager.get_dictionary_groups.called
    
    def test_remove_group_updates_config(
        self,
        settings_window,
        mock_config_manager
    ):
        """Test that removing a group updates configuration."""
        with patch('src.ui.settings_window.miAsk', return_value=True):
            settings_window._remove_group(0)
        
        mock_config_manager.write_config.assert_called()


class TestSettingsWindowTemplateManagement:
    """Test export template management."""
    
    def test_load_template_table(self, settings_window, mock_config_manager):
        """Test loading export templates into table."""
        # Templates should be loaded during initialization
        assert mock_config_manager.get_export_templates.called
    
    def test_remove_template_updates_config(
        self,
        settings_window,
        mock_config_manager
    ):
        """Test that removing a template updates configuration."""
        with patch('src.ui.settings_window.miAsk', return_value=True):
            settings_window._remove_template(0)
        
        mock_config_manager.write_config.assert_called()


class TestSettingsWindowAudioDirectory:
    """Test audio directory selection."""
    
    def test_update_audio_directory_sets_path(self, settings_window):
        """Test that updating audio directory sets the path."""
        with patch('src.ui.settings_window.QFileDialog.getExistingDirectory', return_value='/test/path'):
            settings_window._update_audio_directory()
        
        assert settings_window.choose_audio_directory.text() == '/test/path'
    
    def test_update_audio_directory_handles_cancel(self, settings_window):
        """Test that canceling directory selection keeps default."""
        with patch('src.ui.settings_window.QFileDialog.getExistingDirectory', return_value=''):
            settings_window._update_audio_directory()
        
        assert settings_window.choose_audio_directory.text() == "Choose Directory"


class TestSettingsWindowEventHandlers:
    """Test event handlers."""
    
    def test_hide_event_clears_reference(self, settings_window, mock_mw):
        """Test that hide event clears mw.dictSettings reference."""
        mock_event = Mock()
        mock_event.accept = Mock()
        
        settings_window.hideEvent(mock_event)
        
        assert mock_mw.dictSettings is None
        mock_event.accept.assert_called_once()
    
    def test_close_event_clears_reference(self, settings_window, mock_mw):
        """Test that close event clears mw.dictSettings reference."""
        mock_event = Mock()
        mock_event.accept = Mock()
        
        settings_window.closeEvent(mock_event)
        
        assert mock_mw.dictSettings is None
        mock_event.accept.assert_called_once()


class TestSettingsWindowHelpers:
    """Test helper methods."""
    
    def test_get_dictionary_names(self, settings_window):
        """Test getting dictionary names."""
        names = settings_window._get_dictionary_names()
        
        assert 'TestDict' in names
        assert 'AnotherDict' in names
    
    def test_clean_dict_name(self, settings_window):
        """Test cleaning dictionary name."""
        cleaned = settings_window._clean_dict_name('TestDictl1name')
        assert cleaned == 'TestDict'
    
    def test_get_google_countries_returns_list(self):
        """Test that Google countries list is returned."""
        countries = SettingsWindow._get_google_countries()
        assert isinstance(countries, list)
        assert len(countries) > 0
        assert 'United States' in countries
    
    def test_get_forvo_languages_returns_list(self):
        """Test that Forvo languages list is returned."""
        languages = SettingsWindow._get_forvo_languages()
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert 'Japanese' in languages
