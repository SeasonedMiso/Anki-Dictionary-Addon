# -*- coding: utf-8 -*-
"""
Shared mock objects for Anki Dictionary tests.

This module provides mock implementations of Anki and Qt classes
to allow testing without requiring the full Anki environment.
"""

import sys
from unittest.mock import Mock, MagicMock


# Fake Qt Classes
class FakeQShortcut:
    """Mock QShortcut class."""
    def __init__(self, *args, **kwargs):
        self.activated = Mock()


class FakeQKeySequence:
    """Mock QKeySequence class."""
    def __init__(self, key):
        self.key = key


class FakeQAction:
    """Mock QAction class."""
    def __init__(self, text, parent=None):
        self.text = text
        self.parent = parent
        self.triggered = Mock()


class FakeQMenu:
    """Mock QMenu class."""
    def __init__(self, text, parent=None):
        self.text = text
        self.parent = parent
        self.actions = []
    
    def addAction(self, action):
        self.actions.append(action)
    
    def addSeparator(self):
        self.actions.append('separator')
    
    def clear(self):
        self.actions.clear()


class FakeQWidget:
    """Mock QWidget class."""
    def __init__(self, parent=None):
        self.parent = parent
        self._visible = False
        self._layout = None
        self._title = ""
        self._size = (800, 600)
        self._min_size = (0, 0)
    
    def show(self):
        self._visible = True
    
    def hide(self):
        self._visible = False
    
    def close(self):
        self._visible = False
    
    def isVisible(self):
        return self._visible
    
    def raise_(self):
        pass
    
    def activateWindow(self):
        pass
    
    def setLayout(self, layout):
        self._layout = layout
    
    def layout(self):
        return self._layout
    
    def setWindowTitle(self, title):
        self._title = title
    
    def setMinimumSize(self, width, height):
        self._min_size = (width, height)
    
    def resize(self, width, height):
        self._size = (width, height)


class FakeQDialog:
    """Mock QDialog class."""
    def __init__(self, parent=None):
        self.parent = parent
        self._layout = None
    
    def setWindowTitle(self, title):
        self.title = title
    
    def setWindowModality(self, modality):
        self.modality = modality
    
    def setMinimumWidth(self, width):
        self.min_width = width
    
    def setLayout(self, layout):
        self._layout = layout
    
    def exec(self):
        return 1
    
    def accept(self):
        pass
    
    def reject(self):
        pass


def setup_aqt_mocks():
    """
    Set up mock Anki and Qt modules in sys.modules.
    
    This should be called before importing any modules that depend on aqt.
    Returns the mock modules for further customization if needed.
    """
    # Create fake Qt module
    fake_qt_module = MagicMock()
    fake_qt_module.QShortcut = FakeQShortcut
    fake_qt_module.QKeySequence = FakeQKeySequence
    fake_qt_module.QAction = FakeQAction
    fake_qt_module.QMenu = FakeQMenu
    fake_qt_module.QWidget = FakeQWidget
    
    # Add layout classes
    fake_qt_module.QVBoxLayout = MagicMock
    fake_qt_module.QHBoxLayout = MagicMock
    fake_qt_module.QGridLayout = MagicMock
    fake_qt_module.QFormLayout = MagicMock
    
    # Create mock widgets with signals
    def create_widget_with_signals(*signal_names):
        """Create a MagicMock widget with specified signals that support connect/emit."""
        widget = MagicMock()
        for signal_name in signal_names:
            signal = Mock()
            signal.connect = Mock()
            signal.emit = Mock()
            setattr(widget.return_value, signal_name, signal)
        return widget
    
    # Add other common Qt widgets with their signals
    fake_qt_module.QLabel = MagicMock
    fake_qt_module.QPushButton = create_widget_with_signals('clicked', 'pressed', 'released')
    fake_qt_module.QLineEdit = create_widget_with_signals('textChanged', 'editingFinished', 'returnPressed')
    fake_qt_module.QTextEdit = create_widget_with_signals('textChanged')
    fake_qt_module.QCheckBox = create_widget_with_signals('stateChanged', 'toggled')
    fake_qt_module.QComboBox = create_widget_with_signals('currentIndexChanged', 'currentTextChanged')
    fake_qt_module.QListWidget = create_widget_with_signals('itemClicked', 'itemDoubleClicked', 'currentItemChanged')
    fake_qt_module.QTableWidget = create_widget_with_signals('itemClicked', 'itemDoubleClicked', 'currentItemChanged')
    fake_qt_module.QDialog = MagicMock
    fake_qt_module.QMainWindow = MagicMock
    fake_qt_module.QSplitter = MagicMock
    fake_qt_module.QScrollArea = MagicMock
    
    # Qt namespace with common enums and constants
    fake_qt_module.Qt = MagicMock()
    
    # Window states - create WindowState enum-like class
    class WindowState:
        WindowMinimized = 1
        WindowNoState = 0
        WindowMaximized = 2
        WindowFullScreen = 4
    
    fake_qt_module.Qt.WindowState = WindowState
    fake_qt_module.Qt.WindowMinimized = 1
    fake_qt_module.Qt.WindowNoState = 0
    fake_qt_module.Qt.WindowMaximized = 2
    fake_qt_module.Qt.WindowFullScreen = 4
    
    # Orientations
    fake_qt_module.Qt.Horizontal = 1
    fake_qt_module.Qt.Vertical = 2
    
    # Alignments
    fake_qt_module.Qt.AlignLeft = 0x0001
    fake_qt_module.Qt.AlignRight = 0x0002
    fake_qt_module.Qt.AlignCenter = 0x0004
    fake_qt_module.Qt.AlignTop = 0x0020
    fake_qt_module.Qt.AlignBottom = 0x0040
    
    # Other common constants
    fake_qt_module.Qt.KeepAspectRatio = 0
    fake_qt_module.Qt.IgnoreAspectRatio = 1
    
    # QApplication
    fake_qt_module.QApplication = MagicMock()
    fake_qt_module.QApplication.instance = Mock(return_value=MagicMock())
    
    # Create fake aqt module
    fake_aqt = MagicMock()
    fake_aqt.qt = fake_qt_module
    fake_aqt.mw = MagicMock()  # Main window
    fake_aqt.utils = MagicMock()
    fake_aqt.utils.showWarning = Mock()
    fake_aqt.utils.showInfo = Mock()
    fake_aqt.utils.tooltip = Mock()
    fake_aqt.editor = MagicMock()  # Editor module
    
    # Create fake anki module
    fake_anki = MagicMock()
    fake_anki.utils = MagicMock()
    # Platform detection: These are module-level booleans in actual Anki, not functions
    fake_anki.utils.is_mac = sys.platform == "darwin"
    fake_anki.utils.is_win = sys.platform == "win32"
    fake_anki.utils.is_lin = not fake_anki.utils.is_mac and not fake_anki.utils.is_win
    fake_anki.hooks = MagicMock()
    fake_anki.hooks.addHook = Mock()
    fake_anki.hooks.wrap = Mock(side_effect=lambda func, wrapper: wrapper)
    fake_anki.hooks.runHook = Mock()
    
    # Install mocks in sys.modules
    sys.modules['aqt'] = fake_aqt
    sys.modules['aqt.qt'] = fake_qt_module
    sys.modules['aqt.utils'] = fake_aqt.utils
    sys.modules['aqt.editor'] = fake_aqt.editor
    sys.modules['anki'] = fake_anki
    sys.modules['anki.utils'] = fake_anki.utils
    sys.modules['anki.hooks'] = fake_anki.hooks
    
    return {
        'aqt': fake_aqt,
        'qt': fake_qt_module,
        'anki': fake_anki
    }


def cleanup_aqt_mocks():
    """
    Remove mock Anki and Qt modules from sys.modules.
    
    This should be called after tests that use the mocks to clean up.
    """
    modules_to_remove = [
        'aqt',
        'aqt.qt',
        'aqt.utils',
        'anki',
        'anki.utils',
        'anki.hooks'
    ]
    
    for module in modules_to_remove:
        if module in sys.modules:
            del sys.modules[module]
