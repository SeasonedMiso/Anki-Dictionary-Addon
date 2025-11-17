# -*- coding: utf-8 -*-
"""
Tests for Dictionary Manager UI component.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path
import json
import sys

# Note: This test file uses custom Qt mocks specific to DictionaryManager testing
# rather than the shared mocks in tests/mocks.py due to complex widget requirements

# Create fake Qt classes
class FakeQWidget:
    """Fake QWidget."""
    
    def __init__(self, *args, **kwargs):
        self.parent = kwargs.get('parent', args[0] if args else None)
        self._layout = None
    
    def setLayout(self, layout):
        self._layout = layout


class FakeQVBoxLayout:
    def __init__(self, *args, **kwargs):
        self.widgets = []
        self.layouts = []
    
    def setContentsMargins(self, *args): pass
    def addWidget(self, widget): self.widgets.append(widget)
    def addLayout(self, layout): self.layouts.append(layout)
    def addStretch(self): pass


class FakeQHBoxLayout:
    def __init__(self, *args, **kwargs):
        self.widgets = []
    
    def addWidget(self, widget): self.widgets.append(widget)
    def addStretch(self): pass


class FakeQSplitter:
    def __init__(self, *args, **kwargs):
        self.widgets = []
    
    def addWidget(self, widget): self.widgets.append(widget)
    def setChildrenCollapsible(self, val): pass
    def setStretchFactor(self, idx, val): pass


class FakeQTreeWidget:
    def __init__(self, *args, **kwargs):
        self.items = []
        self.current_item = None
        self.currentItemChanged = Mock()
    
    def setHeaderHidden(self, val): pass
    def addTopLevelItem(self, item): self.items.append(item)
    def clear(self): self.items = []
    def currentItem(self): return self.current_item
    def setCurrentItem(self, item): self.current_item = item


class FakeQTreeWidgetItem:
    def __init__(self, labels):
        self.labels = labels
        self.data_storage = {}
        self.children = []
        self._parent = None
        self._expanded = False
    
    def setData(self, col, role, data):
        self.data_storage[(col, role)] = data
    
    def data(self, col, role):
        return self.data_storage.get((col, role))
    
    def addChild(self, child):
        self.children.append(child)
        child._parent = self
    
    def parent(self):
        return self._parent
    
    def child(self, idx):
        return self.children[idx] if idx < len(self.children) else None
    
    def childCount(self):
        return len(self.children)
    
    def setExpanded(self, val):
        self._expanded = val


class FakeQPushButton:
    def __init__(self, text="", *args, **kwargs):
        self._text = text
        self.clicked = Mock()


class FakeQGroupBox:
    def __init__(self, title="", *args, **kwargs):
        self._title = title
        self._enabled = True
        self._layout = None
    
    def setLayout(self, layout):
        self._layout = layout
    
    def setEnabled(self, val):
        self._enabled = val


class FakeQMessageBox:
    Icon = type('Icon', (), {
        'Information': 1,
        'Question': 2,
        'Warning': 3,
        'Critical': 4
    })
    StandardButton = type('StandardButton', (), {
        'Ok': 1,
        'Yes': 2,
        'No': 4,
        'Cancel': 8
    })
    
    def __init__(self, *args, **kwargs):
        self.result_value = FakeQMessageBox.StandardButton.Yes
    
    def exec(self):
        return self.result_value
    
    @staticmethod
    def question(parent, title, text, buttons):
        return FakeQMessageBox.StandardButton.Yes


class FakeQInputDialog:
    def __init__(self, *args, **kwargs):
        self._text = ""
        self._ok = True
    
    def setWindowTitle(self, title): pass
    def setLabelText(self, text): pass
    def setTextValue(self, text): self._text = text
    def resize(self, w, h): pass
    def sizeHint(self): return Mock(height=Mock(return_value=100))
    def exec(self): return self._ok
    def textValue(self): return self._text


class FakeQFileDialog:
    @staticmethod
    def getOpenFileName(parent, caption, directory, filter):
        return ('/fake/path/dict.zip', 'ZIP Files (*.zip)')
    
    @staticmethod
    def getOpenFileNames(parent, caption, directory, filter):
        return (['/fake/path/dict1.zip', '/fake/path/dict2.zip'], 'ZIP Files (*.zip)')


class FakeQProgressDialog:
    def __init__(self, *args, **kwargs):
        self._value = 0
        self._canceled = False
    
    def setWindowTitle(self, title): pass
    def setWindowModality(self, mode): pass
    def setValue(self, val): self._value = val
    def wasCanceled(self): return self._canceled
    def close(self): pass


class FakeQt:
    ItemDataRole = type('ItemDataRole', (), {
        'UserRole': 256,
        'DisplayRole': 0
    })
    WindowModality = type('WindowModality', (), {
        'WindowModal': 1
    })


# Patch sys.modules before importing
fake_qt_module = MagicMock()
fake_qt_module.QWidget = FakeQWidget
fake_qt_module.QVBoxLayout = FakeQVBoxLayout
fake_qt_module.QHBoxLayout = FakeQHBoxLayout
fake_qt_module.QSplitter = FakeQSplitter
fake_qt_module.QTreeWidget = FakeQTreeWidget
fake_qt_module.QTreeWidgetItem = FakeQTreeWidgetItem
fake_qt_module.QPushButton = FakeQPushButton
fake_qt_module.QGroupBox = FakeQGroupBox
fake_qt_module.QMessageBox = FakeQMessageBox
fake_qt_module.QInputDialog = FakeQInputDialog
fake_qt_module.QFileDialog = FakeQFileDialog
fake_qt_module.QProgressDialog = FakeQProgressDialog
fake_qt_module.Qt = FakeQt

fake_aqt = MagicMock()
fake_aqt.qt = fake_qt_module
fake_aqt.qt.sip = MagicMock()
fake_aqt.qt.sip.delete = Mock()

sys.modules['aqt'] = fake_aqt
sys.modules['aqt.qt'] = fake_qt_module

# Now import the module under test
from src.ui.dictionary_manager import DictionaryManagerWidget


@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    return mw


@pytest.fixture
def mock_dictionary_repo():
    """Mock dictionary repository."""
    repo = Mock()
    repo.get_all_languages = Mock(return_value=['Japanese', 'Spanish'])
    repo.get_all_dictionaries_with_language = Mock(return_value=[
        {'dict': 'l1nameJMDict', 'lang': 'Japanese'},
        {'dict': 'l2nameSpanishDict', 'lang': 'Spanish'}
    ])
    repo.get_language_id = Mock(return_value=1)
    repo.get_dictionaries_by_language = Mock(return_value=['JMDict'])
    repo.add_dictionary = Mock(return_value=(True, "Success", "test_dict"))
    repo.delete_dictionary = Mock()
    repo.get_dictionary_info = Mock()
    repo.db = Mock()
    repo.db.execute = Mock()
    repo.db.commit = Mock()
    return repo


@pytest.fixture
def mock_config_manager():
    """Mock configuration manager."""
    config = Mock()
    config.get_dictionary_groups = Mock(return_value={})
    return config


@pytest.fixture
def temp_addon_path(tmp_path):
    """Create temporary addon path."""
    (tmp_path / 'user_files' / 'db' / 'frequency').mkdir(parents=True, exist_ok=True)
    (tmp_path / 'user_files' / 'db' / 'conjugation').mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def dictionary_manager(
    mock_mw,
    mock_dictionary_repo,
    mock_config_manager,
    temp_addon_path
):
    """Create dictionary manager instance for testing."""
    manager = DictionaryManagerWidget(
        mw=mock_mw,
        dictionary_repo=mock_dictionary_repo,
        config_manager=mock_config_manager,
        addon_path=temp_addon_path
    )
    return manager


class TestDictionaryManagerInitialization:
    """Test dictionary manager initialization."""
    
    def test_manager_initialized_with_dependencies(
        self,
        dictionary_manager,
        mock_dictionary_repo,
        mock_config_manager
    ):
        """Test that manager is initialized with all dependencies."""
        assert dictionary_manager.dictionary_repo == mock_dictionary_repo
        assert dictionary_manager.config_manager == mock_config_manager
    
    def test_tree_widget_loaded_on_init(
        self,
        dictionary_manager,
        mock_dictionary_repo
    ):
        """Test that tree widget is loaded on initialization."""
        mock_dictionary_repo.get_all_languages.assert_called()
        mock_dictionary_repo.get_all_dictionaries_with_language.assert_called()


class TestDictionaryLoading:
    """Test dictionary loading functionality."""
    
    def test_reload_tree_widget_calls_repository(
        self,
        dictionary_manager,
        mock_dictionary_repo
    ):
        """Test that reload calls repository methods."""
        dictionary_manager.reload_tree_widget()
        
        mock_dictionary_repo.get_all_languages.assert_called()
        mock_dictionary_repo.get_all_dictionaries_with_language.assert_called()
    
    def test_reload_tree_widget_handles_errors(
        self,
        dictionary_manager,
        mock_dictionary_repo
    ):
        """Test that reload handles repository errors gracefully."""
        mock_dictionary_repo.get_all_languages.side_effect = Exception("DB error")
        
        # Should not raise exception
        dictionary_manager.reload_tree_widget()


class TestLanguageManagement:
    """Test language add/remove functionality."""
    
    def test_add_language_calls_repository(
        self,
        dictionary_manager,
        mock_dictionary_repo
    ):
        """Test that add language uses repository."""
        # Mock get_language_id to return None (language doesn't exist)
        mock_dictionary_repo.get_language_id.return_value = None
        
        with patch.object(dictionary_manager, 'get_string', return_value=('NewLang', True)):
            dictionary_manager.add_lang()
        
        mock_dictionary_repo.db.execute.assert_called()
        mock_dictionary_repo.db.commit.assert_called()
    
    def test_add_language_validates_empty_name(
        self,
        dictionary_manager
    ):
        """Test that empty language name is rejected."""
        with patch.object(dictionary_manager, 'get_string', return_value=('', True)):
            with patch.object(dictionary_manager, 'info') as mock_info:
                dictionary_manager.add_lang()
                mock_info.assert_called_once()
    
    def test_remove_language_calls_repository(
        self,
        dictionary_manager,
        mock_dictionary_repo
    ):
        """Test that remove language uses repository."""
        # Set up tree item
        lang_item = FakeQTreeWidgetItem(['Japanese'])
        lang_item.setData(0, FakeQt.ItemDataRole.UserRole, 'Japanese')
        dictionary_manager.dict_tree.setCurrentItem(lang_item)
        
        with patch.object(FakeQMessageBox, 'question', return_value=FakeQMessageBox.StandardButton.Yes):
            dictionary_manager.remove_lang()
        
        mock_dictionary_repo.get_language_id.assert_called_with('Japanese')
        mock_dictionary_repo.db.execute.assert_called()


class TestDictionaryAddition:
    """Test dictionary addition functionality."""
    
    def test_import_dicts_validates_files(
        self,
        dictionary_manager,
        mock_dictionary_repo
    ):
        """Test that dictionary files are validated."""
        lang_item = FakeQTreeWidgetItem(['Japanese'])
        lang_item.setData(0, FakeQt.ItemDataRole.UserRole, 'Japanese')
        dictionary_manager.dict_tree.setCurrentItem(lang_item)
        
        with patch.object(FakeQFileDialog, 'getOpenFileNames', return_value=([], '')):
            dictionary_manager.import_dicts()
        
        # Should not call repository if no files selected
        mock_dictionary_repo.add_dictionary.assert_not_called()
    
    def test_validate_dictionary_file_checks_zip(
        self,
        dictionary_manager
    ):
        """Test that dictionary file validation checks ZIP format."""
        error = dictionary_manager._validate_dictionary_file('/nonexistent/file.zip')
        assert error is not None
        assert 'exist' in error.lower()


class TestDictionaryRemoval:
    """Test dictionary removal functionality."""
    
    def test_remove_dict_calls_repository(
        self,
        dictionary_manager,
        mock_dictionary_repo
    ):
        """Test that remove dictionary uses repository."""
        # Set up tree items
        lang_item = FakeQTreeWidgetItem(['Japanese'])
        dict_item = FakeQTreeWidgetItem(['JMDict'])
        dict_item.setData(0, FakeQt.ItemDataRole.UserRole+1, 'l1nameJMDict')
        lang_item.addChild(dict_item)
        dictionary_manager.dict_tree.setCurrentItem(dict_item)
        
        with patch.object(FakeQMessageBox, 'question', return_value=FakeQMessageBox.StandardButton.Yes):
            dictionary_manager.remove_dict()
        
        mock_dictionary_repo.delete_dictionary.assert_called_once_with('l1nameJMDict')


class TestFrequencyData:
    """Test frequency data management."""
    
    def test_set_freq_data_validates_json(
        self,
        dictionary_manager,
        temp_addon_path
    ):
        """Test that frequency data file is validated."""
        lang_item = FakeQTreeWidgetItem(['Japanese'])
        lang_item.setData(0, FakeQt.ItemDataRole.UserRole, 'Japanese')
        dictionary_manager.dict_tree.setCurrentItem(lang_item)
        
        # Create invalid JSON file
        invalid_file = temp_addon_path / 'invalid.json'
        invalid_file.write_text('not valid json')
        
        with patch.object(FakeQFileDialog, 'getOpenFileName', return_value=(str(invalid_file), '')):
            with patch.object(dictionary_manager, 'info') as mock_info:
                dictionary_manager.set_freq_data()
                mock_info.assert_called()
    
    def test_get_frequency_list_returns_none_if_missing(
        self,
        dictionary_manager
    ):
        """Test that missing frequency file returns None."""
        result = dictionary_manager._get_frequency_list('NonexistentLang')
        assert result is None


class TestConjugationData:
    """Test conjugation data management."""
    
    def test_set_conj_data_validates_json(
        self,
        dictionary_manager,
        temp_addon_path
    ):
        """Test that conjugation data file is validated."""
        lang_item = FakeQTreeWidgetItem(['Japanese'])
        lang_item.setData(0, FakeQt.ItemDataRole.UserRole, 'Japanese')
        dictionary_manager.dict_tree.setCurrentItem(lang_item)
        
        # Create invalid JSON file
        invalid_file = temp_addon_path / 'invalid.json'
        invalid_file.write_text('not valid json')
        
        with patch.object(FakeQFileDialog, 'getOpenFileName', return_value=(str(invalid_file), '')):
            with patch.object(dictionary_manager, 'info') as mock_info:
                dictionary_manager.set_conj_data()
                mock_info.assert_called()


class TestTermHeader:
    """Test term header configuration."""
    
    def test_set_term_header_validates_parts(
        self,
        dictionary_manager,
        mock_dictionary_repo
    ):
        """Test that term header parts are validated."""
        dict_item = FakeQTreeWidgetItem(['JMDict'])
        dict_item.setData(0, FakeQt.ItemDataRole.UserRole+1, 'l1nameJMDict')
        dictionary_manager.dict_tree.setCurrentItem(dict_item)
        
        # Mock dictionary info
        mock_info = Mock()
        mock_info.term_header = ['term', 'pronunciation']
        mock_dictionary_repo.get_dictionary_info.return_value = mock_info
        
        with patch.object(dictionary_manager, 'get_string', return_value=('invalid_part', True)):
            with patch.object(dictionary_manager, 'info') as mock_info_dlg:
                dictionary_manager.set_term_header()
                mock_info_dlg.assert_called()


class TestHelperMethods:
    """Test helper methods."""
    
    def test_clean_dict_name_removes_prefix(
        self,
        dictionary_manager
    ):
        """Test that clean dict name removes language prefix."""
        result = dictionary_manager._clean_dict_name('l1nameJMDict')
        assert result == 'JMDict'
    
    def test_natural_sort_handles_numbers(
        self,
        dictionary_manager
    ):
        """Test that natural sort handles numbers correctly."""
        items = ['term_bank_10.json', 'term_bank_2.json', 'term_bank_1.json']
        result = dictionary_manager._natural_sort(items)
        assert result == ['term_bank_1.json', 'term_bank_2.json', 'term_bank_10.json']
    
    def test_get_current_lang_dict_returns_selection(
        self,
        dictionary_manager
    ):
        """Test getting current language and dictionary."""
        dict_item = FakeQTreeWidgetItem(['JMDict'])
        dict_item.setData(0, FakeQt.ItemDataRole.UserRole, 'Japanese')
        dict_item.setData(0, FakeQt.ItemDataRole.UserRole+1, 'l1nameJMDict')
        dictionary_manager.dict_tree.setCurrentItem(dict_item)
        
        lang, dict_name = dictionary_manager.get_current_lang_dict()
        assert lang == 'Japanese'
        assert dict_name == 'l1nameJMDict'


class TestErrorHandling:
    """Test error handling."""
    
    def test_reload_displays_error_on_failure(
        self,
        dictionary_manager,
        mock_dictionary_repo
    ):
        """Test that reload errors are displayed to user."""
        mock_dictionary_repo.get_all_languages.side_effect = Exception("DB error")
        
        with patch.object(dictionary_manager, 'info') as mock_info:
            dictionary_manager.reload_tree_widget()
            mock_info.assert_called()
    
    def test_add_language_handles_database_errors(
        self,
        dictionary_manager,
        mock_dictionary_repo
    ):
        """Test that add language handles database errors."""
        mock_dictionary_repo.db.execute.side_effect = Exception("DB error")
        
        with patch.object(dictionary_manager, 'get_string', return_value=('NewLang', True)):
            with patch.object(dictionary_manager, 'info') as mock_info:
                dictionary_manager.add_lang()
                mock_info.assert_called()
