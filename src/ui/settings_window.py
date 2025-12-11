# -*- coding: utf-8 -*-
"""
Modern Settings Window for Anki Dictionary Addon.

This is a new modal dialog implementation following the design document,
separate from the legacy settings window. It integrates with the mock UI
and provides a clean, modern interface for configuring addon settings.
"""

import logging
import json
from pathlib import Path

try:
    from aqt.qt import (
        QDialog, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
        QLabel, QCheckBox, QSpinBox, QComboBox, QLineEdit, QPushButton,
        QColorDialog, QFrame, QScrollArea, QGroupBox, QSizePolicy,
        Qt, QColor, QTimer, QFileDialog, QMessageBox, QTextEdit,
        QListWidget, QListWidgetItem, QProgressBar, QDrag, QMimeData,
        QApplication
    )
    ANKI_AVAILABLE = True
except ImportError:
    # For testing without Anki
    ANKI_AVAILABLE = False
    
    class MockWidget:
        def __init__(self, *args, **kwargs):
            pass
        def setStyleSheet(self, *args): pass
        def setFixedSize(self, *args): pass
        def setFixedWidth(self, *args): pass
        def setFixedHeight(self, *args): pass
        def setText(self, *args): pass
        def text(self): return ""
        def setReadOnly(self, *args): pass
        def setChecked(self, *args): pass
        def isChecked(self): return False
        def setValue(self, *args): pass
        def value(self): return 0
        def setCurrentText(self, *args): pass
        def currentText(self): return ""
        def addWidget(self, *args): pass
        def addLayout(self, *args): pass
        def addStretch(self, *args): pass
        def setContentsMargins(self, *args): pass
        def setSpacing(self, *args): pass
        def setLayout(self, *args): pass
        def layout(self): return self
        def addTab(self, *args): pass
        def setWindowTitle(self, *args): pass
        def setMinimumSize(self, *args): pass
        def resize(self, *args): pass
        def setModal(self, *args): pass
        def setWindowFlags(self, *args): pass
        def exec_(self): return 1
        def accept(self): pass
        def reject(self): pass
        def show(self): pass
        @property
        def clicked(self): return self
        @property  
        def textChanged(self): return self
        @property
        def timeout(self): return self
        def connect(self, *args): pass
        def start(self): pass
        def setInterval(self, *args): pass
        def setSingleShot(self, *args): pass
        def setRange(self, *args): pass
        def setDefault(self, *args): pass
        def name(self): return "#000000"
        def isValid(self): return True
        def getSaveFileName(self, *args): return ("test.json", True)
        def getOpenFileName(self, *args): return ("test.json", True)
        def question(self, *args): return 1
        def information(self, *args): pass
        def warning(self, *args): pass
        def addItem(self, *args): pass
        def clear(self): pass
        def setPlainText(self, *args): pass
        def toPlainText(self): return ""
        def setMaximum(self, *args): pass
        def setWidgetResizable(self, *args): pass
        def setHorizontalScrollBarPolicy(self, *args): pass
        def setVerticalScrollBarPolicy(self, *args): pass
        def setWidget(self, *args): pass
        def setWordWrap(self, *args): pass
        def setMinimumWidth(self, *args): pass
        def setMaximumWidth(self, *args): pass
        def setAlignment(self, *args): pass
        def setSizePolicy(self, *args): pass
        def sizeHint(self): return self
        def setSizeHint(self, *args): pass
        def addSpacing(self, *args): pass
        def setMinimumHeight(self, *args): pass
        def setItemWidget(self, *args): pass
        def setEnabled(self, *args): pass
        def parent(self): return None
        def setToolTip(self, *args): pass
        def setDragDropMode(self, *args): pass
        def setDefaultDropAction(self, *args): pass
        def currentRow(self): return 0
        def dropEvent(self, *args): pass
        def setVisible(self, *args): pass
        def setAcceptDrops(self, *args): pass
        def setDragDropMode(self, *args): pass
        def setDefaultDropAction(self, *args): pass
        def dragEnterEvent(self, *args): pass
        def dragMoveEvent(self, *args): pass
        def dropEvent(self, *args): pass
        def startDrag(self, *args): pass
        @property
        def stateChanged(self): 
            # Mock signal that can be connected
            return MockSignal()
        @property
        def textChanged(self): 
            return MockSignal()
        @property
        def clicked(self): 
            return MockSignal()
        
    class MockSignal:
        def connect(self, *args): pass
        def emit(self, *args): pass
        
    QDialog = MockWidget
    QWidget = MockWidget
    QVBoxLayout = MockWidget
    QHBoxLayout = MockWidget
    QTabWidget = MockWidget
    QLabel = MockWidget
    QCheckBox = MockWidget
    QSpinBox = MockWidget
    QComboBox = MockWidget
    QLineEdit = MockWidget
    QPushButton = MockWidget
    QColorDialog = MockWidget
    QFrame = MockWidget
    QScrollArea = MockWidget
    QGroupBox = MockWidget
    QSizePolicy = MockWidget
    # Create mock Qt with nested classes
    class MockQt:
        class ScrollBarPolicy:
            ScrollBarAlwaysOff = 0
            ScrollBarAsNeeded = 1
        class AlignmentFlag:
            AlignLeft = 0
            AlignVCenter = 1
        class WindowType:
            Dialog = 0
            WindowCloseButtonHint = 1
        class DialogCode:
            Accepted = 1
            Rejected = 0
        class StandardButton:
            Yes = 1
            No = 0
        class DragDropMode:
            InternalMove = 1
        class DropAction:
            MoveAction = 2
    
    class MockSizePolicy:
        class Policy:
            Preferred = 0
            Fixed = 1
            Expanding = 2
    
    Qt = MockQt
    QSizePolicy = MockSizePolicy
    QColor = MockWidget
    QTimer = MockWidget
    QFileDialog = MockWidget
    QMessageBox = MockWidget
    QTextEdit = MockWidget
    QListWidget = MockWidget
    QListWidgetItem = MockWidget
    QProgressBar = MockWidget
    QDrag = MockWidget
    QMimeData = MockWidget
    QApplication = MockWidget
    
    # Make sure MockSignal is available
    MockSignal = MockSignal

from .styling import ThemeColors, StyleGenerator, get_theme_manager, THEME_PRESETS
from .base_widgets import (
    ThemedWidget, ThemedButton, ThemedLabel, ThemedLineEdit, ThemedFrame,
    ValidationInput, StatusMessage
)

logger = logging.getLogger('anki_dictionary.ui.modern_settings_window')


class ProgressDialog(QDialog):
    """Progress dialog for long-running operations."""
    
    def __init__(self, title, message, parent=None):
        """Initialize progress dialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 120)
        
        if ANKI_AVAILABLE:
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Message label
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        if ANKI_AVAILABLE:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)
        
        # Cancel button (optional)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply dark theme styling."""
        if not ANKI_AVAILABLE:
            return
        
        theme = ThemeColors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background_color};
                color: {theme.text_primary};
            }}
            QLabel {{
                color: {theme.text_primary};
                font-size: 13px;
            }}
            QProgressBar {{
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                background-color: {theme.panel_color};
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {theme.accent_color};
                border-radius: 3px;
            }}
            QPushButton {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {StyleGenerator(theme).adjust_color_brightness(theme.panel_color, 1.2)};
            }}
        """)
    
    def update_message(self, message):
        """Update the progress message."""
        self.message_label.setText(message)
    
    def set_progress(self, value):
        """Set progress value (0-100)."""
        if ANKI_AVAILABLE:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(value)


class ValidationErrorDialog(QDialog):
    """Dialog for displaying validation errors with recovery options."""
    
    def __init__(self, title, errors, parent=None):
        """Initialize validation error dialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("The following validation errors were found:")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header_label)
        
        # Error list
        self.error_text = QTextEdit()
        self.error_text.setReadOnly(True)
        self.error_text.setMaximumHeight(200)
        
        error_text = "\n".join([f"• {error}" for error in errors])
        self.error_text.setPlainText(error_text)
        layout.addWidget(self.error_text)
        
        # Recovery suggestions
        recovery_label = QLabel("Suggested actions:")
        recovery_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        layout.addWidget(recovery_label)
        
        suggestions = [
            "Check input formats and correct any invalid values",
            "Ensure all required fields are filled",
            "Verify network connections for online resources",
            "Try resetting to defaults if problems persist"
        ]
        
        suggestion_text = "\n".join([f"• {suggestion}" for suggestion in suggestions])
        suggestion_label = QLabel(suggestion_text)
        suggestion_label.setWordWrap(True)
        theme = get_theme_manager().current_theme
        suggestion_label.setStyleSheet(f"color: {theme.text_muted}; font-size: 12px;")
        layout.addWidget(suggestion_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(self.reset_button)
        
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        self._apply_styling()
    
    def _reset_to_defaults(self):
        """Signal that user wants to reset to defaults."""
        self.done(2)  # Custom return code for reset
    
    def _apply_styling(self):
        """Apply dark theme styling."""
        if not ANKI_AVAILABLE:
            return
        
        theme = ThemeColors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background_color};
                color: {theme.text_primary};
            }}
            QLabel {{
                color: {theme.text_primary};
            }}
            QTextEdit {{
                background-color: {theme.panel_color};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                color: {theme.text_primary};
                font-family: monospace;
            }}
            QPushButton {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {StyleGenerator(theme).adjust_color_brightness(theme.panel_color, 1.2)};
            }}
            QPushButton:default {{
                background-color: {theme.accent_color};
                border-color: {theme.accent_color};
            }}
        """)


logger = logging.getLogger('anki_dictionary.ui.modern_settings_window')


class DraggableListWidget(QListWidget):
    """List widget that supports drag and drop reordering."""
    
    def __init__(self, parent=None):
        """Initialize draggable list widget."""
        super().__init__(parent)
        self.parent_tab = parent
        
        if ANKI_AVAILABLE:
            # Enable drag and drop
            self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
            self.setDefaultDropAction(Qt.DropAction.MoveAction)
            self.setAcceptDrops(True)
    
    def dropEvent(self, event):
        """Handle drop events for reordering."""
        if not ANKI_AVAILABLE:
            return
        
        # Get source and target indices
        source_index = self.currentRow()
        
        # Call parent's drop event to handle the move
        super().dropEvent(event)
        
        # Get new target index after the move
        target_index = self.currentRow()
        
        # Notify parent tab about the reordering
        if hasattr(self.parent_tab, '_on_dictionary_reordered'):
            self.parent_tab._on_dictionary_reordered(source_index, target_index)


# ThemeColors is now imported from styling module


class LivePreview(QWidget):
    """Live preview component showing theme changes in real-time."""
    
    def __init__(self, parent=None):
        """Initialize live preview."""
        super().__init__(parent)
        self.theme = get_theme_manager().current_theme
        self._setup_ui()
        self._apply_theme()
    
    def _setup_ui(self):
        """Set up preview UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Title
        self.title_label = QLabel("Live Preview")
        layout.addWidget(self.title_label)
        
        # Sample search bar
        self.search_preview = QLineEdit("Sample search text")
        self.search_preview.setReadOnly(True)
        layout.addWidget(self.search_preview)
        
        # Sample definition card
        card_frame = QFrame()
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(8, 8, 8, 8)
        
        self.word_label = QLabel("食べる")
        self.phonetic_label = QLabel("たべる")
        self.definition_label = QLabel("to eat; to consume")
        
        # Pitch accent examples
        pitch_layout = QHBoxLayout()
        self.heiban_label = QLabel("平板")
        self.odaka_label = QLabel("尾高")
        self.nakadaka_label = QLabel("中高")
        self.atamadaka_label = QLabel("頭高")
        self.kifuku_label = QLabel("起伏")
        
        pitch_layout.addWidget(self.heiban_label)
        pitch_layout.addWidget(self.odaka_label)
        pitch_layout.addWidget(self.nakadaka_label)
        pitch_layout.addWidget(self.atamadaka_label)
        pitch_layout.addWidget(self.kifuku_label)
        pitch_layout.addStretch()
        
        card_layout.addWidget(self.word_label)
        card_layout.addWidget(self.phonetic_label)
        card_layout.addWidget(self.definition_label)
        card_layout.addLayout(pitch_layout)
        
        layout.addWidget(card_frame)
        layout.addStretch()
        
        # Store references for styling
        self.card_frame = card_frame
    
    def update_theme(self, theme):
        """Update preview with new theme colors."""
        self.theme = theme
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply current theme to preview elements."""
        if not ANKI_AVAILABLE:
            return
        
        # Main container - this will affect the entire preview area
        self.setStyleSheet(f"""
            LivePreview {{
                background-color: {self.theme.background_color};
                color: {self.theme.text_primary};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            QWidget {{
                background-color: {self.theme.background_color};
                color: {self.theme.text_primary};
            }}
        """)
        
        # Title
        self.title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {self.theme.text_primary};
                padding: 4px 0px;
                background-color: {self.theme.background_color};
            }}
        """)
        
        # Search preview
        self.search_preview.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.theme.panel_color};
                border: 1px solid {self.theme.border_color};
                border-radius: 6px;
                padding: 8px 12px;
                color: {self.theme.text_primary};
                font-size: 13px;
            }}
        """)
        
        # Card frame - always show border around the whole definition box
        self.card_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.theme.panel_color};
                border: 1px solid {self.theme.border_color};
                border-radius: 8px;
            }}
        """)
        
        # Word label
        self.word_label.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                color: {self.theme.text_primary};
                background-color: transparent;
            }}
        """)
        
        # Phonetic label
        self.phonetic_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {self.theme.text_muted};
                background-color: transparent;
            }}
        """)
        
        # Definition label
        self.definition_label.setStyleSheet(f"""
            QLabel {{
                font-size: 13px;
                color: {self.theme.text_primary};
                background-color: transparent;
            }}
        """)
        
        # Pitch accent labels
        self.heiban_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {self.theme.heiban_color};
                font-weight: bold;
                background-color: transparent;
                padding: 2px 4px;
                border-radius: 3px;
            }}
        """)
        
        self.odaka_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {self.theme.odaka_color};
                font-weight: bold;
                background-color: transparent;
                padding: 2px 4px;
                border-radius: 3px;
            }}
        """)
        
        self.nakadaka_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {self.theme.nakadaka_color};
                font-weight: bold;
                background-color: transparent;
                padding: 2px 4px;
                border-radius: 3px;
            }}
        """)
        
        self.atamadaka_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {self.theme.atamadaka_color};
                font-weight: bold;
                background-color: transparent;
                padding: 2px 4px;
                border-radius: 3px;
            }}
        """)
        
        self.kifuku_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11px;
                color: {self.theme.kifuku_color};
                font-weight: bold;
                background-color: transparent;
                padding: 2px 4px;
                border-radius: 3px;
            }}
        """)


class ColorPicker(QWidget):
    """Color picker widget with live preview and validation."""
    
    def __init__(self, label, initial_color, parent=None):
        """Initialize color picker."""
        super().__init__(parent)
        self.label = label
        self.color = initial_color
        self.validation_error = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up color picker UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Main row with color picker controls
        main_layout = QHBoxLayout()
        main_layout.setSpacing(8)
        
        # Label - use minimum width instead of fixed width for better responsiveness
        label = QLabel(self.label)
        label.setMinimumWidth(100)  # Reasonable minimum
        label.setMaximumWidth(160)  # Prevent excessive stretching
        label.setWordWrap(False)
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(label)
        
        # Color display button
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 30)
        self.color_button.clicked.connect(self._open_color_dialog)
        if ANKI_AVAILABLE:
            self.color_button.setToolTip("Click to open color picker dialog")
        main_layout.addWidget(self.color_button)
        
        # Color value input
        self.color_input = QLineEdit(self.color)
        self.color_input.setMinimumWidth(80)
        self.color_input.setMaximumWidth(100)
        self.color_input.textChanged.connect(self._on_text_changed)
        if ANKI_AVAILABLE:
            self.color_input.setToolTip("Enter hex color code (e.g., #ff0000)")
        main_layout.addWidget(self.color_input)
        
        main_layout.addStretch(1)  # Add stretch with factor
        layout.addLayout(main_layout)
        
        # Error message label (initially hidden)
        self.error_label = QLabel()
        theme = get_theme_manager().current_theme
        self.error_label.setStyleSheet(f"color: {theme.error_color}; font-size: 11px; margin-left: 100px;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        self._update_button_color()
    
    def _update_button_color(self):
        """Update button background color."""
        if not ANKI_AVAILABLE:
            return
        
        # Add border color based on validation state
        theme = get_theme_manager().current_theme
        border_color = theme.error_color if self.validation_error else theme.border_color
        
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                border: 2px solid {border_color};
                border-radius: 4px;
            }}
        """)
    
    def _open_color_dialog(self):
        """Open color picker dialog."""
        if not ANKI_AVAILABLE:
            return
        
        color = QColorDialog.getColor(QColor(self.color), self)
        if color.isValid():
            self.color = color.name()
            self.color_input.setText(self.color)
            self._clear_validation_error()
            self._update_button_color()
    
    def _on_text_changed(self, text):
        """Handle text input changes with validation."""
        # Clear previous error
        self._clear_validation_error()
        
        # Validate hex color format
        if not text:
            self._set_validation_error("Color value cannot be empty")
            return
        
        if not text.startswith('#'):
            self._set_validation_error("Color must start with #")
            return
        
        if len(text) != 7:
            self._set_validation_error("Color must be 7 characters (#rrggbb)")
            return
        
        try:
            int(text[1:], 16)  # Validate hex
            self.color = text
            self._update_button_color()
        except ValueError:
            self._set_validation_error("Invalid hex color format")
    
    def _set_validation_error(self, message):
        """Set validation error message."""
        self.validation_error = message
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        self._update_button_color()
    
    def _clear_validation_error(self):
        """Clear validation error message."""
        self.validation_error = None
        self.error_label.setVisible(False)
        self._update_button_color()
    
    def is_valid(self):
        """Check if current color value is valid."""
        return self.validation_error is None
    
    def get_validation_error(self):
        """Get current validation error message."""
        return self.validation_error
    
    def get_color(self):
        """Get current color value."""
        return self.color
    
    def set_color(self, color):
        """Set color value."""
        self.color = color
        self.color_input.setText(color)
        self._clear_validation_error()
        self._update_button_color()


class SaveThemeDialog(QDialog):
    """Dialog for saving a new theme."""
    
    def __init__(self, parent=None):
        """Initialize save theme dialog."""
        super().__init__(parent)
        self.setWindowTitle("Save Theme")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Theme name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Theme Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Ocean Blue")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply theme styling."""
        if not ANKI_AVAILABLE:
            return
        
        theme = get_theme_manager().current_theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background_color};
                color: {theme.text_primary};
            }}
            QLabel {{
                color: {theme.text_primary};
            }}
            QLineEdit {{
                background-color: {theme.panel_color};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                color: {theme.text_primary};
                padding: 6px;
            }}
            QPushButton {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: {StyleGenerator(theme).adjust_color_brightness(theme.panel_color, 1.2)};
            }}
        """)
    
    def get_theme_name(self) -> str:
        """Get entered theme name."""
        return self.name_input.text().strip()


class DeleteThemeDialog(QDialog):
    """Dialog for confirming theme deletion."""
    
    def __init__(self, theme_name: str, parent=None):
        """Initialize delete theme dialog."""
        super().__init__(parent)
        self.setWindowTitle("Delete Theme")
        self.setModal(True)
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Warning message
        warning_label = QLabel(f"Delete theme '{theme_name}'?")
        warning_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(warning_label)
        
        # Warning text
        warning_text = QLabel("This action cannot be undone.")
        warning_text.setStyleSheet("color: #ff6b6b;")
        layout.addWidget(warning_text)
        
        layout.addSpacing(12)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete")
        self.cancel_button = QPushButton("Cancel")
        self.delete_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply theme styling."""
        if not ANKI_AVAILABLE:
            return
        
        theme = get_theme_manager().current_theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background_color};
                color: {theme.text_primary};
            }}
            QLabel {{
                color: {theme.text_primary};
            }}
            QPushButton {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: {StyleGenerator(theme).adjust_color_brightness(theme.panel_color, 1.2)};
            }}
        """)


class RenameThemeDialog(QDialog):
    """Dialog for renaming a theme."""
    
    def __init__(self, current_name: str, parent=None):
        """Initialize rename theme dialog."""
        super().__init__(parent)
        self.setWindowTitle("Rename Theme")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Current name
        current_layout = QHBoxLayout()
        current_label = QLabel("Current Name:")
        current_display = QLabel(current_name)
        current_display.setStyleSheet("font-weight: bold;")
        current_layout.addWidget(current_label)
        current_layout.addWidget(current_display)
        current_layout.addStretch()
        layout.addLayout(current_layout)
        
        layout.addSpacing(8)
        
        # New name input
        new_layout = QHBoxLayout()
        new_label = QLabel("New Name:")
        self.name_input = QLineEdit()
        self.name_input.setText(current_name)
        self.name_input.selectAll()
        new_layout.addWidget(new_label)
        new_layout.addWidget(self.name_input)
        layout.addLayout(new_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.rename_button = QPushButton("Rename")
        self.cancel_button = QPushButton("Cancel")
        self.rename_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.rename_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply theme styling."""
        if not ANKI_AVAILABLE:
            return
        
        theme = get_theme_manager().current_theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background_color};
                color: {theme.text_primary};
            }}
            QLabel {{
                color: {theme.text_primary};
            }}
            QLineEdit {{
                background-color: {theme.panel_color};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                color: {theme.text_primary};
                padding: 6px;
            }}
            QPushButton {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: {StyleGenerator(theme).adjust_color_brightness(theme.panel_color, 1.2)};
            }}
        """)
    
    def get_new_name(self) -> str:
        """Get entered theme name."""
        return self.name_input.text().strip()


class ImportPreviewDialog(QDialog):
    """Dialog for previewing imported theme before confirming."""
    
    def __init__(self, theme_name: str, theme: 'ThemeColors', parent=None):
        """Initialize import preview dialog."""
        super().__init__(parent)
        self.setWindowTitle("Import Theme Preview")
        self.setModal(True)
        self.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Theme info
        info_label = QLabel(f"Theme: {theme_name}")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(info_label)
        
        # Color preview
        preview_label = QLabel("Color Preview:")
        layout.addWidget(preview_label)
        
        # Create a simple color grid
        colors_layout = QHBoxLayout()
        colors = [
            ("Background", theme.background_color),
            ("Panel", theme.panel_color),
            ("Text", theme.text_primary),
            ("Accent", theme.accent_color),
        ]
        
        for color_name, color_value in colors:
            color_frame = QFrame()
            color_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color_value};
                    border: 1px solid {theme.border_color};
                    border-radius: 4px;
                }}
            """)
            color_frame.setFixedSize(60, 60)
            
            color_layout = QVBoxLayout()
            color_layout.addWidget(color_frame)
            color_label = QLabel(color_name)
            color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            color_label.setStyleSheet("font-size: 10px;")
            color_layout.addWidget(color_label)
            
            colors_layout.addLayout(color_layout)
        
        colors_layout.addStretch()
        layout.addLayout(colors_layout)
        
        layout.addSpacing(12)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("Import")
        self.cancel_button = QPushButton("Cancel")
        self.import_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply theme styling."""
        if not ANKI_AVAILABLE:
            return
        
        theme = get_theme_manager().current_theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background_color};
                color: {theme.text_primary};
            }}
            QLabel {{
                color: {theme.text_primary};
            }}
            QPushButton {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: {StyleGenerator(theme).adjust_color_brightness(theme.panel_color, 1.2)};
            }}
        """)


class ThemeTab(QWidget):
    """Theme customization tab with live preview."""
    
    def __init__(self, parent=None):
        """Initialize theme tab."""
        super().__init__(parent)
        
        # Timer for live updates (debounced) - MUST be created before _setup_ui()
        # because color picker signals connect to _schedule_update() during setup
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._update_preview)
        if ANKI_AVAILABLE:
            self.update_timer.setInterval(100)  # 100ms debounce
        
        self.theme = get_theme_manager().current_theme
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up theme tab UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Left side - Color controls with scroll area
        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        controls_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        controls_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)
        
        controls_scroll.setWidget(controls_widget)
        
        # Theme selector group (at top)
        theme_selector_group = QGroupBox("Theme")
        theme_selector_layout = QVBoxLayout(theme_selector_group)
        
        # Theme dropdown
        dropdown_layout = QHBoxLayout()
        dropdown_layout.setSpacing(8)
        
        dropdown_label = QLabel("Select Theme:")
        self.theme_dropdown = QComboBox()
        self.theme_dropdown.currentTextChanged.connect(self._on_theme_selected)
        
        dropdown_layout.addWidget(dropdown_label)
        dropdown_layout.addWidget(self.theme_dropdown, 1)
        theme_selector_layout.addLayout(dropdown_layout)
        
        # Theme management buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.save_theme_btn = QPushButton("Save Theme")
        self.delete_theme_btn = QPushButton("Delete")
        self.rename_theme_btn = QPushButton("Rename")
        self.export_theme_btn = QPushButton("Export")
        self.import_theme_btn = QPushButton("Import")
        
        self.save_theme_btn.clicked.connect(self._on_save_theme_clicked)
        self.delete_theme_btn.clicked.connect(self._on_delete_theme_clicked)
        self.rename_theme_btn.clicked.connect(self._on_rename_theme_clicked)
        self.export_theme_btn.clicked.connect(self._on_export_theme_clicked)
        self.import_theme_btn.clicked.connect(self._on_import_theme_clicked)
        
        # Add tooltips
        if ANKI_AVAILABLE:
            self.theme_dropdown.setToolTip("Select a theme to apply")
            self.save_theme_btn.setToolTip("Save current colors as a new theme")
            self.delete_theme_btn.setToolTip("Delete selected user theme (presets cannot be deleted)")
            self.rename_theme_btn.setToolTip("Rename selected user theme")
            self.export_theme_btn.setToolTip("Export theme to file for sharing")
            self.import_theme_btn.setToolTip("Import theme from file")
        
        buttons_layout.addWidget(self.save_theme_btn)
        buttons_layout.addWidget(self.delete_theme_btn)
        buttons_layout.addWidget(self.rename_theme_btn)
        buttons_layout.addWidget(self.export_theme_btn)
        buttons_layout.addWidget(self.import_theme_btn)
        buttons_layout.addStretch(1)
        
        theme_selector_layout.addLayout(buttons_layout)
        controls_layout.addWidget(theme_selector_group)
        
        # Add spacing
        controls_layout.addSpacing(8)
        
        # Color pickers group
        colors_group = QGroupBox("Colors")
        colors_layout = QVBoxLayout(colors_group)
        colors_layout.setSpacing(8)
        
        # Basic colors - initialize with current theme
        self.bg_picker = ColorPicker("Background:", self.theme.background_color)
        self.panel_picker = ColorPicker("Panel:", self.theme.panel_color)
        self.text_picker = ColorPicker("Text:", self.theme.text_primary)
        self.muted_picker = ColorPicker("Muted Text:", self.theme.text_muted)
        self.border_picker = ColorPicker("Border:", self.theme.border_color)
        self.accent_picker = ColorPicker("Accent:", self.theme.accent_color)
        
        colors_layout.addWidget(self.bg_picker)
        colors_layout.addWidget(self.panel_picker)
        colors_layout.addWidget(self.text_picker)
        colors_layout.addWidget(self.muted_picker)
        colors_layout.addWidget(self.border_picker)
        colors_layout.addWidget(self.accent_picker)
        
        controls_layout.addWidget(colors_group)
        
        # Pitch accent colors (Japanese-specific) - separate group at same level
        self.pitch_accent_group = QGroupBox("Pitch Accent Colors")
        pitch_accent_layout = QVBoxLayout(self.pitch_accent_group)
        pitch_accent_layout.setSpacing(8)
        
        # Create pitch accent pickers with shorter labels for better fit
        self.heiban_picker = ColorPicker("Heiban:", self.theme.heiban_color)
        self.odaka_picker = ColorPicker("Odaka:", self.theme.odaka_color)
        self.nakadaka_picker = ColorPicker("Nakadaka:", self.theme.nakadaka_color)
        self.atamadaka_picker = ColorPicker("Atamadaka:", self.theme.atamadaka_color)
        self.kifuku_picker = ColorPicker("Kifuku:", self.theme.kifuku_color)
        
        pitch_accent_layout.addWidget(self.heiban_picker)
        pitch_accent_layout.addWidget(self.odaka_picker)
        pitch_accent_layout.addWidget(self.nakadaka_picker)
        pitch_accent_layout.addWidget(self.atamadaka_picker)
        pitch_accent_layout.addWidget(self.kifuku_picker)
        
        controls_layout.addWidget(self.pitch_accent_group)
        
        # Add comprehensive tooltips for pitch accent explanations
        if ANKI_AVAILABLE:
            self.heiban_picker.setToolTip(
                "Heiban (平板): Flat pitch pattern\n"
                "• Low-High-High-High pattern\n"
                "• Most common pitch accent type\n"
                "• Example: さくら (sakura)"
            )
            self.odaka_picker.setToolTip(
                "Odaka (尾高): Tail-high pitch pattern\n"
                "• Low-High-High-Low pattern\n"
                "• Pitch drops after the word\n"
                "• Example: あたま (atama)"
            )
            self.nakadaka_picker.setToolTip(
                "Nakadaka (中高): Middle-high pitch pattern\n"
                "• Low-High-Low pattern\n"
                "• Peak in the middle of the word\n"
                "• Example: こころ (kokoro)"
            )
            self.atamadaka_picker.setToolTip(
                "Atamadaka (頭高): Head-high pitch pattern\n"
                "• High-Low-Low-Low pattern\n"
                "• Starts high, then drops\n"
                "• Example: いぬ (inu)"
            )
            self.kifuku_picker.setToolTip(
                "Kifuku (起伏): Complex pitch pattern\n"
                "• Multiple pitch changes\n"
                "• Used for compound words\n"
                "• Example: でんしゃ (densha)"
            )
        
        # Add some spacing between major groups
        controls_layout.addSpacing(8)
        
        # Action button colors group
        buttons_group = QGroupBox("Action Button Colors")
        buttons_layout = QVBoxLayout(buttons_group)
        buttons_layout.setSpacing(8)
        
        self.search_btn_picker = ColorPicker("Search Button:", self.theme.accent_color)
        self.audio_btn_picker = ColorPicker("Audio Button:", self.theme.audio_color)
        self.image_btn_picker = ColorPicker("Image Button:", self.theme.image_color)
        self.copy_btn_picker = ColorPicker("Copy Button:", self.theme.copy_color)
        self.export_btn_picker = ColorPicker("Export Button:", self.theme.export_color)
        
        buttons_layout.addWidget(self.search_btn_picker)
        buttons_layout.addWidget(self.audio_btn_picker)
        buttons_layout.addWidget(self.image_btn_picker)
        buttons_layout.addWidget(self.copy_btn_picker)
        buttons_layout.addWidget(self.export_btn_picker)
        
        controls_layout.addWidget(buttons_group)
        
        controls_layout.addStretch()
        # Set size policy for controls to allow expansion
        controls_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(controls_scroll, 2)  # Give more space to controls
        
        # Right side - Live preview with scroll area for better responsive behavior
        preview_scroll = QScrollArea()
        preview_scroll.setWidgetResizable(True)
        preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.preview_widget = QWidget()
        self.preview_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        preview_layout = QVBoxLayout(self.preview_widget)
        preview_layout.setContentsMargins(16, 16, 16, 16)
        preview_layout.setSpacing(12)
        
        self.preview_label = QLabel("Live Preview")
        self.preview_label.setStyleSheet("font-weight: bold; margin-bottom: 8px;")
        preview_layout.addWidget(self.preview_label)
        
        self.live_preview = LivePreview()
        self.live_preview.setMinimumSize(300, 250)  # Slightly smaller minimum for better fit
        self.live_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Add rounded border styling to live preview - fixed alignment
        if ANKI_AVAILABLE:
            theme = get_theme_manager().current_theme
            self.live_preview.setStyleSheet(f"""
                LivePreview {{
                    border: 1px solid {theme.border_color};
                    border-radius: 8px;
                    padding: 8px;
                }}
            """)
        
        preview_layout.addWidget(self.live_preview)
        preview_layout.addStretch()
        
        preview_scroll.setWidget(self.preview_widget)
        preview_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        layout.addWidget(preview_scroll, 1)  # Less space for preview
        
        # Apply scrollbar styling
        if ANKI_AVAILABLE:
            theme = get_theme_manager().current_theme
            scrollbar_style = f"""
                QScrollBar:vertical {{
                    background-color: {theme.panel_color};
                    width: 12px;
                    border: none;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {theme.border_color};
                    border-radius: 6px;
                    min-height: 20px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {theme.accent_color};
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    border: none;
                    background: none;
                }}
            """
            controls_scroll.setStyleSheet(scrollbar_style)
            preview_scroll.setStyleSheet(scrollbar_style)
        
        # Connect color pickers to live update
        for picker in [self.bg_picker, self.panel_picker, self.text_picker, 
                      self.muted_picker, self.border_picker, self.accent_picker,
                      self.heiban_picker, self.odaka_picker, self.nakadaka_picker,
                      self.atamadaka_picker, self.kifuku_picker,
                      self.search_btn_picker, self.audio_btn_picker, self.image_btn_picker,
                      self.copy_btn_picker, self.export_btn_picker]:
            picker.color_input.textChanged.connect(self._schedule_update)
        
        # Check if we should show pitch accent colors based on available dictionaries
        self._update_pitch_accent_visibility()
        
        # Populate theme dropdown (after all pickers are created)
        self._refresh_theme_dropdown()
    
    def _schedule_update(self):
        """Schedule a debounced preview update."""
        if ANKI_AVAILABLE:
            self.update_timer.start()
    
    def _update_preview(self):
        """Update live preview with current colors."""
        # Get current colors from pickers
        theme = ThemeColors(
            background_color=self.bg_picker.get_color(),
            panel_color=self.panel_picker.get_color(),
            text_primary=self.text_picker.get_color(),
            text_muted=self.muted_picker.get_color(),
            border_color=self.border_picker.get_color(),
            accent_color=self.accent_picker.get_color(),
            heiban_color=self.heiban_picker.get_color(),
            odaka_color=self.odaka_picker.get_color(),
            nakadaka_color=self.nakadaka_picker.get_color(),
            atamadaka_color=self.atamadaka_picker.get_color(),
            kifuku_color=self.kifuku_picker.get_color(),
            audio_color=self.audio_btn_picker.get_color(),
            image_color=self.image_btn_picker.get_color(),
            copy_color=self.copy_btn_picker.get_color(),
            export_color=self.export_btn_picker.get_color()
        )
        
        # Set borders to show around major sections only (no individual element borders)
        theme.show_borders = False  # Individual elements don't get borders, only major sections
        
        self.theme = theme
        self.live_preview.update_theme(theme)
        
        # Update the preview container background
        if ANKI_AVAILABLE:
            self.preview_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme.background_color};
                    color: {theme.text_primary};
                }}
            """)
            
            self.preview_label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold;
                    margin-bottom: 8px;
                    color: {theme.text_primary};
                    background-color: {theme.background_color};
                }}
            """)
    
    def _apply_preset(self, preset_name):
        """Apply a theme preset."""
        if preset_name in THEME_PRESETS:
            theme = THEME_PRESETS[preset_name]
            self.theme = theme
            
            # Update color pickers
            self.bg_picker.set_color(theme.background_color)
            self.panel_picker.set_color(theme.panel_color)
            self.text_picker.set_color(theme.text_primary)
            self.muted_picker.set_color(theme.text_muted)
            self.border_picker.set_color(theme.border_color)
            self.accent_picker.set_color(theme.accent_color)
            self.heiban_picker.set_color(theme.heiban_color)
            self.odaka_picker.set_color(theme.odaka_color)
            self.nakadaka_picker.set_color(theme.nakadaka_color)
            self.atamadaka_picker.set_color(theme.atamadaka_color)
            self.kifuku_picker.set_color(theme.kifuku_color)
            
            # Update button color pickers
            self.search_btn_picker.set_color(theme.accent_color)
            self.audio_btn_picker.set_color(theme.audio_color)
            self.image_btn_picker.set_color(theme.image_color)
            self.copy_btn_picker.set_color(theme.copy_color)
            self.export_btn_picker.set_color(theme.export_color)
            
            # No border checkbox to update anymore
            
            # Update preview
            self.live_preview.update_theme(theme)
            
            # Update the preview container background
            if ANKI_AVAILABLE:
                self.preview_widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: {theme.background_color};
                        color: {theme.text_primary};
                    }}
                """)
                
                self.preview_label.setStyleSheet(f"""
                    QLabel {{
                        font-weight: bold;
                        margin-bottom: 8px;
                        color: {theme.text_primary};
                        background-color: {theme.background_color};
                    }}
                """)
            
            # Save theme preference immediately when preset is selected
            get_theme_manager().save_theme_preference(preset_name)
            
            # Apply theme changes to parent mock UI immediately
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, '_apply_theme_settings'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, '_apply_theme_settings'):
                theme_dict = theme.__dict__
                parent_window._apply_theme_settings(theme_dict)
                logger.info(f"Applied {preset_name} theme preset to mock UI")
    
    def get_theme(self):
        """Get current theme configuration."""
        return self.theme
    
    def _validate_theme_name(self, name: str) -> tuple:
        """Validate theme name. Returns (is_valid, error_message)."""
        if not name or not name.strip():
            return (False, "Theme name cannot be empty")
        
        name = name.strip()
        
        if len(name) > 50:
            return (False, "Theme name must be 50 characters or less")
        
        # Allow alphanumeric, spaces, hyphens, underscores
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name):
            return (False, "Theme name can only contain letters, numbers, spaces, hyphens, and underscores")
        
        return (True, "")
    
    def _refresh_theme_dropdown(self):
        """Populate dropdown with all available themes."""
        if not ANKI_AVAILABLE:
            return
        
        theme_manager = get_theme_manager()
        all_themes = theme_manager.get_all_themes()
        
        self.theme_dropdown.clear()
        
        for theme_name in sorted(all_themes.keys()):
            if theme_manager.is_preset_theme(theme_name):
                display_name = f"[Preset] {theme_name.title()}"
            else:
                display_name = f"[Custom] {theme_name}"
            
            self.theme_dropdown.addItem(display_name, theme_name)
    
    def _on_theme_selected(self, display_name: str):
        """Handle theme selection from dropdown."""
        if not ANKI_AVAILABLE or not display_name:
            return
        
        # Get actual theme name from item data
        index = self.theme_dropdown.currentIndex()
        if index < 0:
            return
        
        theme_name = self.theme_dropdown.itemData(index)
        if not theme_name:
            return
        
        theme_manager = get_theme_manager()
        all_themes = theme_manager.get_all_themes()
        
        if theme_name in all_themes:
            theme = all_themes[theme_name]
            self.theme = theme
            
            # Update color pickers
            self.bg_picker.set_color(theme.background_color)
            self.panel_picker.set_color(theme.panel_color)
            self.text_picker.set_color(theme.text_primary)
            self.muted_picker.set_color(theme.text_muted)
            self.border_picker.set_color(theme.border_color)
            self.accent_picker.set_color(theme.accent_color)
            
            # Update live preview (if it exists)
            if hasattr(self, 'live_preview'):
                self.live_preview.update_theme(theme)
            
            # Save preference
            theme_manager.save_theme_preference(theme_name)
            
            logger.info(f"Selected theme: {theme_name}")
    
    def _on_save_theme_clicked(self):
        """Handle save theme button click."""
        if not ANKI_AVAILABLE:
            return
        
        dialog = SaveThemeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            theme_name = dialog.get_theme_name()
            
            # Validate theme name
            is_valid, error_msg = self._validate_theme_name(theme_name)
            if not is_valid:
                QMessageBox.warning(self, "Invalid Theme Name", error_msg)
                return
            
            theme_manager = get_theme_manager()
            
            # Check if theme exists and ask to overwrite
            if theme_manager.theme_exists(theme_name):
                reply = QMessageBox.question(
                    self,
                    "Theme Exists",
                    f"Theme '{theme_name}' already exists.\nDo you want to overwrite it?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            try:
                # Save theme
                if theme_manager.save_user_theme(theme_name, self.theme):
                    self._refresh_theme_dropdown()
                    # Select the newly saved theme
                    for i in range(self.theme_dropdown.count()):
                        if self.theme_dropdown.itemData(i) == theme_name:
                            self.theme_dropdown.setCurrentIndex(i)
                            break
                    QMessageBox.information(self, "Success", f"Theme '{theme_name}' saved successfully")
                    logger.info(f"Saved theme: {theme_name}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to save theme. Check file permissions.")
                    logger.error(f"Failed to save theme: {theme_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
                logger.error(f"Exception saving theme: {e}", exc_info=True)
    
    def _on_delete_theme_clicked(self):
        """Handle delete theme button click."""
        if not ANKI_AVAILABLE:
            return
        
        index = self.theme_dropdown.currentIndex()
        if index < 0:
            QMessageBox.warning(self, "Error", "No theme selected")
            return
        
        theme_name = self.theme_dropdown.itemData(index)
        if not theme_name:
            QMessageBox.warning(self, "Error", "Invalid theme selection")
            return
        
        theme_manager = get_theme_manager()
        
        # Prevent deleting presets
        if theme_manager.is_preset_theme(theme_name):
            QMessageBox.warning(self, "Error", "Cannot delete preset themes. Only custom themes can be deleted.")
            return
        
        dialog = DeleteThemeDialog(theme_name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                if theme_manager.delete_user_theme(theme_name):
                    self._refresh_theme_dropdown()
                    # Fall back to dark preset
                    for i in range(self.theme_dropdown.count()):
                        if self.theme_dropdown.itemData(i) == "dark":
                            self.theme_dropdown.setCurrentIndex(i)
                            break
                    QMessageBox.information(self, "Success", f"Theme '{theme_name}' deleted successfully")
                    logger.info(f"Deleted theme: {theme_name}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete theme. Check file permissions.")
                    logger.error(f"Failed to delete theme: {theme_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
                logger.error(f"Exception deleting theme: {e}", exc_info=True)
    
    def _on_rename_theme_clicked(self):
        """Handle rename theme button click."""
        if not ANKI_AVAILABLE:
            return
        
        index = self.theme_dropdown.currentIndex()
        if index < 0:
            QMessageBox.warning(self, "Error", "No theme selected")
            return
        
        theme_name = self.theme_dropdown.itemData(index)
        if not theme_name:
            QMessageBox.warning(self, "Error", "Invalid theme selection")
            return
        
        theme_manager = get_theme_manager()
        
        # Prevent renaming presets
        if theme_manager.is_preset_theme(theme_name):
            QMessageBox.warning(self, "Error", "Cannot rename preset themes. Only custom themes can be renamed.")
            return
        
        dialog = RenameThemeDialog(theme_name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.get_new_name()
            
            # Validate new name
            is_valid, error_msg = self._validate_theme_name(new_name)
            if not is_valid:
                QMessageBox.warning(self, "Invalid Theme Name", error_msg)
                return
            
            if new_name == theme_name:
                return  # No change
            
            if theme_manager.theme_exists(new_name):
                QMessageBox.warning(self, "Error", f"Theme '{new_name}' already exists")
                return
            
            try:
                # Rename by deleting old and saving new
                user_themes = theme_manager.load_user_themes()
                if theme_name in user_themes:
                    old_theme = user_themes[theme_name]
                    theme_manager.delete_user_theme(theme_name)
                    theme_manager.save_user_theme(new_name, old_theme)
                    
                    self._refresh_theme_dropdown()
                    # Select the renamed theme
                    for i in range(self.theme_dropdown.count()):
                        if self.theme_dropdown.itemData(i) == new_name:
                            self.theme_dropdown.setCurrentIndex(i)
                            break
                    QMessageBox.information(self, "Success", f"Theme renamed to '{new_name}'")
                    logger.info(f"Renamed theme to: {new_name}")
                else:
                    QMessageBox.critical(self, "Error", "Theme not found")
                    logger.error(f"Theme not found for rename: {theme_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
                logger.error(f"Exception renaming theme: {e}", exc_info=True)
    
    def _on_export_theme_clicked(self):
        """Handle export theme button click."""
        if not ANKI_AVAILABLE:
            return
        
        index = self.theme_dropdown.currentIndex()
        if index < 0:
            QMessageBox.warning(self, "Error", "No theme selected")
            return
        
        theme_name = self.theme_dropdown.itemData(index)
        if not theme_name:
            QMessageBox.warning(self, "Error", "Invalid theme selection")
            return
        
        # Open file save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Theme",
            f"{theme_name}.json",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            theme_manager = get_theme_manager()
            if theme_manager.export_theme(theme_name, file_path):
                QMessageBox.information(self, "Success", f"Theme exported successfully to:\n{file_path}")
                logger.info(f"Exported theme to: {file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to export theme. Check file permissions.")
                logger.error(f"Failed to export theme: {theme_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            logger.error(f"Exception exporting theme: {e}", exc_info=True)
    
    def _on_import_theme_clicked(self):
        """Handle import theme button click."""
        if not ANKI_AVAILABLE:
            return
        
        # Open file open dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Theme",
            "",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            theme_manager = get_theme_manager()
            
            # Validate file
            if not theme_manager.validate_theme_file(file_path):
                QMessageBox.critical(
                    self,
                    "Invalid Theme File",
                    "The selected file is not a valid theme file.\nPlease check the file format."
                )
                return
            
            # Import theme
            success, imported_theme = theme_manager.import_theme(file_path)
            if not success or imported_theme is None:
                QMessageBox.critical(self, "Error", "Failed to import theme from file")
                return
            
            # Show preview
            import_name = Path(file_path).stem  # Use filename as default name
            preview_dialog = ImportPreviewDialog(import_name, imported_theme, self)
            if preview_dialog.exec() == QDialog.DialogCode.Accepted:
                # Validate import name
                is_valid, error_msg = self._validate_theme_name(import_name)
                if not is_valid:
                    QMessageBox.warning(self, "Invalid Theme Name", error_msg)
                    return
                
                # Check for conflicts
                if theme_manager.theme_exists(import_name):
                    reply = QMessageBox.question(
                        self,
                        "Theme Exists",
                        f"Theme '{import_name}' already exists.\nOverwrite it?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                
                # Save imported theme
                if theme_manager.save_user_theme(import_name, imported_theme):
                    self._refresh_theme_dropdown()
                    # Select the imported theme
                    for i in range(self.theme_dropdown.count()):
                        if self.theme_dropdown.itemData(i) == import_name:
                            self.theme_dropdown.setCurrentIndex(i)
                            break
                    QMessageBox.information(self, "Success", f"Theme '{import_name}' imported successfully")
                    logger.info(f"Imported theme: {import_name}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to save imported theme. Check file permissions.")
                    logger.error(f"Failed to save imported theme: {import_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            logger.error(f"Exception importing theme: {e}", exc_info=True)
    
    def _update_pitch_accent_visibility(self):
        """Show/hide pitch accent colors based on whether Japanese dictionaries are present."""
        if not ANKI_AVAILABLE:
            return
        
        # Check if parent window has dictionaries tab to get language info
        has_japanese = False
        try:
            # Walk up the widget hierarchy to find the main settings window
            parent_widget = self.parent()
            while parent_widget and not hasattr(parent_widget, 'dictionaries_tab'):
                parent_widget = parent_widget.parent()
            
            if parent_widget and hasattr(parent_widget, 'dictionaries_tab'):
                dictionaries = parent_widget.dictionaries_tab.get_dictionaries()
                has_japanese = any(d.get('language', '').lower() == 'japanese' for d in dictionaries)
            else:
                # Default to showing for now (will be hidden when no Japanese dicts are found)
                has_japanese = True
        except Exception as e:
            logger.warning(f"Could not check dictionary languages: {e}")
            has_japanese = True  # Default to showing
        
        # Show/hide the pitch accent group
        self.pitch_accent_group.setVisible(has_japanese)
        
        if not has_japanese:
            logger.info("No Japanese dictionaries found - hiding pitch accent colors")
    
    def update_pitch_accent_visibility_from_parent(self):
        """Public method for parent window to trigger pitch accent visibility update."""
        self._update_pitch_accent_visibility()


class DictionariesTab(QWidget):
    """Dictionary management tab."""
    
    def __init__(self, parent=None):
        """Initialize dictionaries tab."""
        super().__init__(parent)
        self.dictionaries = []  # List of dictionary configurations
        self._setup_ui()
        self._load_dictionaries()
    
    def _setup_ui(self):
        """Set up dictionaries tab UI."""
        # Use scroll area for better responsive behavior
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Dictionary list group
        dict_list_group = QGroupBox("Configured Dictionaries")
        dict_list_layout = QVBoxLayout(dict_list_group)
        
        # Dictionary list widget with drag-and-drop support
        self.dict_list = DraggableListWidget(self)
        self.dict_list.setMinimumHeight(250)  # Increased minimum height
        self.dict_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        dict_list_layout.addWidget(self.dict_list)
        
        # Add dictionary button
        add_dict_layout = QHBoxLayout()
        self.add_dict_btn = QPushButton("Add Dictionary")
        self.add_dict_btn.setMinimumWidth(120)
        self.add_dict_btn.clicked.connect(self._add_dictionary)
        add_dict_layout.addWidget(self.add_dict_btn)
        add_dict_layout.addStretch()
        dict_list_layout.addLayout(add_dict_layout)
        
        layout.addWidget(dict_list_group)
        
        # Dictionary settings group
        settings_group = QGroupBox("Dictionary Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Search priority info
        priority_label = QLabel("Drag dictionaries to reorder search priority, or use up/down buttons (top = highest priority)")
        theme = get_theme_manager().current_theme
        priority_label.setStyleSheet(f"color: {theme.text_muted}; font-size: 12px;")
        priority_label.setWordWrap(True)  # Allow text wrapping for better responsive behavior
        settings_layout.addWidget(priority_label)
        
        layout.addWidget(settings_group)
        layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        
        # Set up main layout for this tab
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
    
    def _load_dictionaries(self):
        """Load dictionaries from configuration."""
        # Mock dictionary data for now - in production this would load from ConfigManager
        self.dictionaries = [
            {
                'id': 'jmdict',
                'name': 'JMdict (Japanese-English)',
                'type': 'local',
                'enabled': True,
                'priority': 0,
                'language': 'Japanese',
                'entries': 180000
            },
            {
                'id': 'kanjidic',
                'name': 'KANJIDIC2 (Kanji Dictionary)',
                'type': 'local', 
                'enabled': True,
                'priority': 1,
                'language': 'Japanese',
                'entries': 13108
            },
            {
                'id': 'forvo',
                'name': 'Forvo (Audio Pronunciation)',
                'type': 'api',
                'enabled': False,
                'priority': 2,
                'language': 'Multiple',
                'entries': 'Online'
            }
        ]
        self._refresh_dictionary_list()
    
    def _refresh_dictionary_list(self):
        """Refresh the dictionary list display."""
        # Clear existing items
        self.dict_list.clear()
        
        # Sort by priority
        sorted_dicts = sorted(self.dictionaries, key=lambda d: d['priority'])
        
        # Add dictionary items
        for dict_config in sorted_dicts:
            item_widget = self._create_dictionary_item(dict_config)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.dict_list.addItem(list_item)
            self.dict_list.setItemWidget(list_item, item_widget)
        
        # Notify theme tab about dictionary changes (for pitch accent visibility)
        self._notify_theme_tab_of_changes()
    
    def _create_dictionary_item(self, dict_config):
        """Create a dictionary list item widget."""
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(12, 8, 12, 8)
        item_layout.setSpacing(12)
        
        # Enable/disable checkbox
        enable_checkbox = QCheckBox()
        enable_checkbox.setChecked(dict_config['enabled'])
        enable_checkbox.stateChanged.connect(
            lambda state, dict_id=dict_config['id']: self._toggle_dictionary(dict_id, state == 2)
        )
        item_layout.addWidget(enable_checkbox)
        
        # Dictionary info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Name and type
        name_label = QLabel(dict_config['name'])
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(name_label)
        
        # Details
        details = f"{dict_config['language']} • {dict_config['type'].title()} • {dict_config['entries']} entries"
        details_label = QLabel(details)
        theme = get_theme_manager().current_theme
        details_label.setStyleSheet(f"color: {theme.text_muted}; font-size: 12px;")
        info_layout.addWidget(details_label)
        
        item_layout.addLayout(info_layout, 1)
        
        # Up/Down buttons for reordering
        reorder_layout = QVBoxLayout()
        reorder_layout.setSpacing(2)
        
        up_btn = QPushButton("▲")
        up_btn.setFixedSize(25, 20)
        up_btn.setToolTip("Move up in priority")
        up_btn.clicked.connect(
            lambda checked, dict_id=dict_config['id']: self._move_dictionary_up(dict_id)
        )
        reorder_layout.addWidget(up_btn)
        
        down_btn = QPushButton("▼")
        down_btn.setFixedSize(25, 20)
        down_btn.setToolTip("Move down in priority")
        down_btn.clicked.connect(
            lambda checked, dict_id=dict_config['id']: self._move_dictionary_down(dict_id)
        )
        reorder_layout.addWidget(down_btn)
        
        item_layout.addLayout(reorder_layout)
        
        # Remove button with trash icon
        remove_btn = QPushButton("🗑")
        remove_btn.setFixedSize(32, 32)
        remove_btn.setToolTip("Remove dictionary")
        remove_btn.clicked.connect(
            lambda checked, dict_id=dict_config['id']: self._remove_dictionary(dict_id)
        )
        item_layout.addWidget(remove_btn)
        
        # Priority indicator (far right)
        priority_label = QLabel(f"#{dict_config['priority'] + 1}")
        theme = get_theme_manager().current_theme
        priority_label.setStyleSheet(f"color: {theme.text_muted}; font-size: 12px; font-weight: bold;")
        priority_label.setFixedWidth(30)
        item_layout.addWidget(priority_label)
        
        # Style the item using theme manager
        if not ANKI_AVAILABLE:
            return item_widget
        
        theme = get_theme_manager().current_theme
        item_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.panel_color};
                border: 1px solid {theme.border_color};
                border-radius: 6px;
            }}
        """)
        
        return item_widget
    
    def _toggle_dictionary(self, dict_id, enabled):
        """Toggle dictionary enabled state."""
        for dict_config in self.dictionaries:
            if dict_config['id'] == dict_id:
                dict_config['enabled'] = enabled
                logger.info(f"Dictionary {dict_id} {'enabled' if enabled else 'disabled'}")
                break
    
    def _add_dictionary(self):
        """Show add dictionary dialog."""
        if not ANKI_AVAILABLE:
            # Mock implementation for testing
            new_dict = {
                'id': f'dict_{len(self.dictionaries)}',
                'name': 'New Dictionary',
                'type': 'local',
                'enabled': True,
                'priority': len(self.dictionaries),
                'language': 'Unknown',
                'entries': 0
            }
            self.dictionaries.append(new_dict)
            self._refresh_dictionary_list()
            return
        
        # Show add dictionary dialog
        dialog = AddDictionaryDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dict_config = dialog.get_dictionary_config()
            if dict_config:
                dict_config['priority'] = len(self.dictionaries)
                self.dictionaries.append(dict_config)
                self._refresh_dictionary_list()
                logger.info(f"Added dictionary: {dict_config['name']}")
    
    def _remove_dictionary(self, dict_id):
        """Remove a dictionary."""
        if not ANKI_AVAILABLE:
            # Mock implementation for testing
            self.dictionaries = [d for d in self.dictionaries if d['id'] != dict_id]
            self._refresh_dictionary_list()
            return
        
        # Find dictionary
        dict_config = None
        for d in self.dictionaries:
            if d['id'] == dict_id:
                dict_config = d
                break
        
        if not dict_config:
            return
        
        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Remove Dictionary",
            f"Are you sure you want to remove '{dict_config['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.dictionaries = [d for d in self.dictionaries if d['id'] != dict_id]
            # Reorder priorities
            for i, d in enumerate(sorted(self.dictionaries, key=lambda x: x['priority'])):
                d['priority'] = i
            self._refresh_dictionary_list()
            logger.info(f"Removed dictionary: {dict_config['name']}")
    
    def get_dictionaries(self):
        """Get current dictionary configuration."""
        return self.dictionaries.copy()
    
    def _on_dictionary_reordered(self, source_index, target_index):
        """Handle dictionary reordering via drag-and-drop."""
        if source_index == target_index or source_index < 0 or target_index < 0:
            return
        
        # Get sorted dictionaries (same order as displayed)
        sorted_dicts = sorted(self.dictionaries, key=lambda d: d['priority'])
        
        # Move the dictionary in the list
        if source_index < len(sorted_dicts) and target_index < len(sorted_dicts):
            moved_dict = sorted_dicts.pop(source_index)
            sorted_dicts.insert(target_index, moved_dict)
            
            # Update priorities based on new order
            for i, dict_config in enumerate(sorted_dicts):
                dict_config['priority'] = i
            
            logger.info(f"Dictionary reordered: {moved_dict['name']} moved from {source_index} to {target_index}")
            
            # Refresh the display to show updated priorities
            self._refresh_dictionary_list()
    
    def _move_dictionary_up(self, dict_id):
        """Move dictionary up in priority (lower priority number = higher priority)."""
        # Find the dictionary
        dict_config = None
        for d in self.dictionaries:
            if d['id'] == dict_id:
                dict_config = d
                break
        
        if not dict_config or dict_config['priority'] == 0:
            return  # Already at top
        
        # Find dictionary with priority one higher (lower number)
        target_priority = dict_config['priority'] - 1
        for other_dict in self.dictionaries:
            if other_dict['priority'] == target_priority:
                # Swap priorities
                other_dict['priority'] = dict_config['priority']
                dict_config['priority'] = target_priority
                break
        
        self._refresh_dictionary_list()
        logger.info(f"Moved dictionary '{dict_config['name']}' up in priority")
    
    def _move_dictionary_down(self, dict_id):
        """Move dictionary down in priority (higher priority number = lower priority)."""
        # Find the dictionary
        dict_config = None
        for d in self.dictionaries:
            if d['id'] == dict_id:
                dict_config = d
                break
        
        if not dict_config:
            return
        
        # Check if already at bottom
        max_priority = max(d['priority'] for d in self.dictionaries)
        if dict_config['priority'] == max_priority:
            return  # Already at bottom
        
        # Find dictionary with priority one lower (higher number)
        target_priority = dict_config['priority'] + 1
        for other_dict in self.dictionaries:
            if other_dict['priority'] == target_priority:
                # Swap priorities
                other_dict['priority'] = dict_config['priority']
                dict_config['priority'] = target_priority
                break
        
        self._refresh_dictionary_list()
        logger.info(f"Moved dictionary '{dict_config['name']}' down in priority")
    
    def _notify_theme_tab_of_changes(self):
        """Notify theme tab that dictionaries have changed (for pitch accent visibility)."""
        try:
            # Walk up the widget hierarchy to find the main settings window
            parent_widget = self.parent()
            while parent_widget and not hasattr(parent_widget, 'theme_tab'):
                parent_widget = parent_widget.parent()
            
            if parent_widget and hasattr(parent_widget, 'theme_tab'):
                parent_widget.theme_tab.update_pitch_accent_visibility_from_parent()
        except Exception as e:
            logger.warning(f"Could not notify theme tab of dictionary changes: {e}")


class AddDictionaryDialog(QDialog):
    """Dialog for adding a new dictionary."""
    
    def __init__(self, parent=None):
        """Initialize add dictionary dialog."""
        super().__init__(parent)
        self.dict_config = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up dialog UI."""
        self.setWindowTitle("Add Dictionary")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Dictionary details
        details_group = QGroupBox("Dictionary Details")
        details_layout = QVBoxLayout(details_group)
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter dictionary name")
        name_layout.addWidget(self.name_input)
        details_layout.addLayout(name_layout)
        
        # Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Local File", "API", "Web Service"])
        type_layout.addWidget(self.type_combo)
        details_layout.addLayout(type_layout)
        
        # Language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Japanese", "Chinese", "Korean", "Spanish", "French", "German", "Other"])
        lang_layout.addWidget(self.lang_combo)
        details_layout.addLayout(lang_layout)
        
        # Connection string (for API/Web types)
        conn_layout = QHBoxLayout()
        conn_layout.addWidget(QLabel("Connection:"))
        self.conn_input = QLineEdit()
        self.conn_input.setPlaceholderText("File path or API endpoint")
        conn_layout.addWidget(self.conn_input)
        details_layout.addLayout(conn_layout)
        
        layout.addWidget(details_group)
        
        # Validation status
        self.status_label = QLabel("")
        theme = get_theme_manager().current_theme
        self.status_label.setStyleSheet(f"color: {theme.text_muted}; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.validate_btn = QPushButton("Validate Connection")
        self.validate_btn.clicked.connect(self._validate_connection)
        button_layout.addWidget(self.validate_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.add_btn = QPushButton("Add Dictionary")
        self.add_btn.clicked.connect(self._add_dictionary)
        self.add_btn.setDefault(True)
        button_layout.addWidget(self.add_btn)
        
        layout.addLayout(button_layout)
    
    def _validate_connection(self):
        """Validate dictionary connection with progress indicator."""
        conn_str = self.conn_input.text().strip()
        dict_type = self.type_combo.currentText()
        
        # Clear previous status
        self.status_label.setText("")
        
        # Basic validation first
        validation_errors = self._validate_input_format(conn_str, dict_type)
        if validation_errors:
            self._show_validation_errors(validation_errors)
            return
        
        # Show progress dialog for connection testing
        if ANKI_AVAILABLE:
            progress = ProgressDialog(
                "Validating Connection", 
                "Testing dictionary connection...", 
                self
            )
            progress.show()
            QApplication.processEvents()  # Allow UI to update
        
        try:
            # Simulate connection testing with different steps
            validation_result = self._test_connection(conn_str, dict_type, progress if ANKI_AVAILABLE else None)
            
            if ANKI_AVAILABLE:
                progress.close()
            
            if validation_result['success']:
                self.status_label.setText(f"✓ {validation_result['message']}")
                theme = get_theme_manager().current_theme
                self.status_label.setStyleSheet(f"color: {theme.success_color};")
                
                # Enable add button
                self.add_btn.setEnabled(True)
            else:
                self.status_label.setText(f"✗ {validation_result['message']}")
                theme = get_theme_manager().current_theme
                self.status_label.setStyleSheet(f"color: {theme.error_color};")
                
                # Show recovery options
                self._show_connection_error_dialog(validation_result['details'])
                
        except Exception as e:
            if ANKI_AVAILABLE:
                progress.close()
            
            self.status_label.setText(f"✗ Validation failed: {str(e)}")
            theme = get_theme_manager().current_theme
            self.status_label.setStyleSheet(f"color: {theme.error_color};")
            logger.error(f"Dictionary validation error: {e}")
    
    def _validate_input_format(self, conn_str, dict_type):
        """Validate input format and return list of errors."""
        errors = []
        
        if not conn_str:
            errors.append("Connection string cannot be empty")
            return errors
        
        if dict_type == "Local File":
            if not conn_str.endswith(('.zip', '.json', '.db', '.sqlite', '.dict')):
                errors.append("Local files should be .zip, .json, .db, .sqlite, or .dict format")
            
            # Check if path looks valid
            if not any(char in conn_str for char in ['/', '\\', '.']):
                errors.append("Local file path should include directory separators or file extension")
                
        elif dict_type in ["API", "Web Service"]:
            if not conn_str.startswith(('http://', 'https://')):
                errors.append("API/Web connections must start with http:// or https://")
            
            # Basic URL validation
            if ' ' in conn_str:
                errors.append("URLs cannot contain spaces")
            
            if not '.' in conn_str.replace('http://', '').replace('https://', ''):
                errors.append("URL must contain a valid domain")
        
        return errors
    
    def _test_connection(self, conn_str, dict_type, progress=None):
        """Test the actual connection (mock implementation)."""
        import time
        
        if progress:
            progress.update_message("Checking connection format...")
            progress.set_progress(25)
            time.sleep(0.5)  # Simulate work
            QApplication.processEvents()
        
        # Mock different validation scenarios
        if dict_type == "Local File":
            if progress:
                progress.update_message("Checking file accessibility...")
                progress.set_progress(50)
                time.sleep(0.5)
                QApplication.processEvents()
            
            # Mock file validation
            if "nonexistent" in conn_str.lower():
                return {
                    'success': False,
                    'message': "File not found or not accessible",
                    'details': [
                        "The specified file path does not exist",
                        "Check that the file path is correct",
                        "Ensure you have read permissions for the file"
                    ]
                }
            
            if progress:
                progress.update_message("Validating file format...")
                progress.set_progress(75)
                time.sleep(0.5)
                QApplication.processEvents()
            
            # Mock format validation
            if conn_str.endswith('.zip'):
                entries = 50000  # Mock entry count
            elif conn_str.endswith('.json'):
                entries = 25000
            else:
                entries = 100000
            
            if progress:
                progress.set_progress(100)
                time.sleep(0.2)
                QApplication.processEvents()
            
            return {
                'success': True,
                'message': f"Local dictionary validated ({entries:,} entries found)",
                'details': []
            }
            
        elif dict_type in ["API", "Web Service"]:
            if progress:
                progress.update_message("Testing network connection...")
                progress.set_progress(33)
                time.sleep(0.7)
                QApplication.processEvents()
            
            # Mock network issues
            if "timeout" in conn_str.lower():
                return {
                    'success': False,
                    'message': "Connection timeout",
                    'details': [
                        "The server did not respond within the timeout period",
                        "Check your internet connection",
                        "Verify the server URL is correct",
                        "The server may be temporarily unavailable"
                    ]
                }
            
            if progress:
                progress.update_message("Authenticating with service...")
                progress.set_progress(66)
                time.sleep(0.5)
                QApplication.processEvents()
            
            if "unauthorized" in conn_str.lower():
                return {
                    'success': False,
                    'message': "Authentication failed",
                    'details': [
                        "Invalid API key or credentials",
                        "Check your API key is correct",
                        "Verify your account has access to this service",
                        "API key may have expired"
                    ]
                }
            
            if progress:
                progress.update_message("Verifying service capabilities...")
                progress.set_progress(100)
                time.sleep(0.3)
                QApplication.processEvents()
            
            return {
                'success': True,
                'message': "API connection validated successfully",
                'details': []
            }
        
        return {
            'success': True,
            'message': "Connection validated",
            'details': []
        }
    
    def _show_validation_errors(self, errors):
        """Show validation errors to user."""
        self.status_label.setText(f"✗ {errors[0]}")  # Show first error
        theme = get_theme_manager().current_theme
        self.status_label.setStyleSheet(f"color: {theme.error_color};")
        
        # If multiple errors, show them in a dialog
        if len(errors) > 1 and ANKI_AVAILABLE:
            error_dialog = ValidationErrorDialog(
                "Input Validation Errors",
                errors,
                self
            )
            error_dialog.exec()
    
    def _show_connection_error_dialog(self, details):
        """Show connection error details with recovery suggestions."""
        if not details or not ANKI_AVAILABLE:
            return
        
        error_dialog = ValidationErrorDialog(
            "Connection Error",
            details,
            self
        )
        result = error_dialog.exec()
        
        if result == 2:  # Reset button was clicked
            self.conn_input.clear()
            self.status_label.setText("Connection string cleared. Please try again.")
            theme = get_theme_manager().current_theme
            self.status_label.setStyleSheet(f"color: {theme.text_muted};")
    
    def _add_dictionary(self):
        """Add the dictionary."""
        name = self.name_input.text().strip()
        if not name:
            self.status_label.setText("Please enter a dictionary name")
            theme = get_theme_manager().current_theme
            self.status_label.setStyleSheet(f"color: {theme.error_color};")
            return
        
        conn_str = self.conn_input.text().strip()
        if not conn_str:
            self.status_label.setText("Please enter a connection string")
            theme = get_theme_manager().current_theme
            self.status_label.setStyleSheet(f"color: {theme.error_color};")
            return
        
        # Create dictionary configuration
        type_map = {"Local File": "local", "API": "api", "Web Service": "web"}
        
        self.dict_config = {
            'id': name.lower().replace(' ', '_'),
            'name': name,
            'type': type_map[self.type_combo.currentText()],
            'enabled': True,
            'language': self.lang_combo.currentText(),
            'connection_string': conn_str,
            'entries': 'Unknown'
        }
        
        self.accept()
    
    def get_dictionary_config(self):
        """Get the configured dictionary."""
        return self.dict_config


class ImportExportTab(QWidget):
    """Import/Export settings tab."""
    
    def __init__(self, parent=None):
        """Initialize import/export tab."""
        super().__init__(parent)
        self.parent_window = parent
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up import/export tab UI."""
        # Use scroll area for better responsive behavior
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Export settings group
        export_group = QGroupBox("Export Settings")
        export_layout = QVBoxLayout(export_group)
        export_layout.setSpacing(12)
        
        # Export description
        export_desc = QLabel("Export your current settings to a JSON file for backup or sharing.")
        theme = get_theme_manager().current_theme
        export_desc.setStyleSheet(f"color: {theme.text_muted}; font-size: 12px;")
        export_layout.addWidget(export_desc)
        
        # Export options
        export_options_layout = QVBoxLayout()
        
        self.export_all_checkbox = QCheckBox("Export all settings")
        self.export_all_checkbox.setChecked(True)
        self.export_all_checkbox.stateChanged.connect(self._on_export_all_changed)
        export_options_layout.addWidget(self.export_all_checkbox)
        
        # Category checkboxes (initially disabled)
        self.export_theme_checkbox = QCheckBox("Theme settings")
        self.export_theme_checkbox.setEnabled(False)
        export_options_layout.addWidget(self.export_theme_checkbox)
        
        self.export_general_checkbox = QCheckBox("General settings")
        self.export_general_checkbox.setEnabled(False)
        export_options_layout.addWidget(self.export_general_checkbox)
        
        self.export_dict_checkbox = QCheckBox("Dictionary settings")
        self.export_dict_checkbox.setEnabled(False)
        export_options_layout.addWidget(self.export_dict_checkbox)
        
        export_layout.addLayout(export_options_layout)
        
        # Export button
        export_button_layout = QHBoxLayout()
        self.export_button = QPushButton("Export Settings...")
        self.export_button.clicked.connect(self._export_settings)
        export_button_layout.addWidget(self.export_button)
        export_button_layout.addStretch()
        export_layout.addLayout(export_button_layout)
        
        layout.addWidget(export_group)
        
        # Import settings group
        import_group = QGroupBox("Import Settings")
        import_layout = QVBoxLayout(import_group)
        import_layout.setSpacing(12)
        
        # Import description
        import_desc = QLabel("Import settings from a JSON file. You can preview changes before applying them.")
        theme = get_theme_manager().current_theme
        import_desc.setStyleSheet(f"color: {theme.text_muted}; font-size: 12px;")
        import_layout.addWidget(import_desc)
        
        # Import button
        import_button_layout = QHBoxLayout()
        self.import_button = QPushButton("Import Settings...")
        self.import_button.clicked.connect(self._import_settings)
        import_button_layout.addWidget(self.import_button)
        import_button_layout.addStretch()
        import_layout.addLayout(import_button_layout)
        
        layout.addWidget(import_group)
        
        # Backup and restore group
        backup_group = QGroupBox("Backup & Restore")
        backup_layout = QVBoxLayout(backup_group)
        backup_layout.setSpacing(12)
        
        # Backup description
        backup_desc = QLabel("Automatic backups are created before major changes. You can restore from recent backups.")
        theme = get_theme_manager().current_theme
        backup_desc.setStyleSheet(f"color: {theme.text_muted}; font-size: 12px;")
        backup_layout.addWidget(backup_desc)
        
        # Backup buttons
        backup_button_layout = QHBoxLayout()
        
        self.create_backup_button = QPushButton("Create Backup Now")
        self.create_backup_button.clicked.connect(self._create_backup)
        backup_button_layout.addWidget(self.create_backup_button)
        
        self.restore_backup_button = QPushButton("Restore from Backup...")
        self.restore_backup_button.clicked.connect(self._restore_backup)
        backup_button_layout.addWidget(self.restore_backup_button)
        
        backup_button_layout.addStretch()
        backup_layout.addLayout(backup_button_layout)
        
        # Quick restore section
        quick_restore_layout = QHBoxLayout()
        
        self.quick_restore_button = QPushButton("Quick Restore (Most Recent)")
        self.quick_restore_button.clicked.connect(self._quick_restore_from_recent_backup)
        if ANKI_AVAILABLE:
            self.quick_restore_button.setToolTip("Restore from the most recent automatic backup")
        quick_restore_layout.addWidget(self.quick_restore_button)
        
        # Status label for quick restore
        self.quick_restore_status = QLabel("")
        theme = get_theme_manager().current_theme
        self.quick_restore_status.setStyleSheet(f"color: {theme.text_muted}; font-size: 11px;")
        quick_restore_layout.addWidget(self.quick_restore_status)
        
        quick_restore_layout.addStretch()
        backup_layout.addLayout(quick_restore_layout)
        
        # Update quick restore status on initialization
        self._update_quick_restore_status()
        
        layout.addWidget(backup_group)
        layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        
        # Set up main layout for this tab
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
    
    def _on_export_all_changed(self, state):
        """Handle export all checkbox state change."""
        # Handle both Qt and mock implementations
        if ANKI_AVAILABLE:
            is_checked = state == 2  # Qt.Checked = 2
        else:
            # For mock implementation, state might be boolean
            is_checked = bool(state) if isinstance(state, (bool, int)) else state == 2
        
        # Enable/disable individual category checkboxes
        self.export_theme_checkbox.setEnabled(not is_checked)
        self.export_general_checkbox.setEnabled(not is_checked)
        self.export_dict_checkbox.setEnabled(not is_checked)
        
        if is_checked:
            # Check all categories when "export all" is selected
            self.export_theme_checkbox.setChecked(True)
            self.export_general_checkbox.setChecked(True)
            self.export_dict_checkbox.setChecked(True)
        else:
            # When unchecked, leave individual checkboxes as they are
            # but make sure at least one is checked for a valid export
            pass
    
    def _export_settings(self):
        """Export settings to JSON file."""
        if not ANKI_AVAILABLE:
            logger.info("Export settings (mock implementation)")
            return
        
        # Get file path from user - use parent window for proper modal behavior
        parent_widget = self.parent_window if self.parent_window else self
        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Export Settings",
            "anki_dictionary_settings.json",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Get current settings from parent window
            if hasattr(self.parent_window, 'get_current_settings'):
                settings = self.parent_window.get_current_settings()
            else:
                # Fallback to mock settings
                settings = self._get_mock_settings()
            
            # Filter settings based on user selection
            if not self.export_all_checkbox.isChecked():
                filtered_settings = {}
                if self.export_theme_checkbox.isChecked():
                    filtered_settings['theme'] = settings.get('theme', {})
                if self.export_general_checkbox.isChecked():
                    filtered_settings['general'] = settings.get('general', {})
                if self.export_dict_checkbox.isChecked():
                    filtered_settings['dictionaries'] = settings.get('dictionaries', [])
                settings = filtered_settings
            
            # Add metadata
            export_data = {
                'metadata': {
                    'version': '1.0',
                    'exported_at': self._get_current_timestamp(),
                    'addon_version': '2.0.0',  # This would come from addon metadata
                    'categories': self._get_exported_categories()
                },
                'settings': settings
            }
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(
                parent_widget,
                "Export Successful",
                f"Settings exported successfully to:\n{file_path}"
            )
            
            logger.info(f"Settings exported to {file_path}")
            
        except Exception as e:
            QMessageBox.warning(
                parent_widget,
                "Export Failed",
                f"Failed to export settings:\n{str(e)}"
            )
            logger.error(f"Settings export failed: {e}")
    
    def _import_settings(self):
        """Import settings from JSON file with enhanced error handling."""
        if not ANKI_AVAILABLE:
            logger.info("Import settings (mock implementation)")
            return
        
        # Get file path from user - use parent window for proper modal behavior
        parent_widget = self.parent_window if self.parent_window else self
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget,
            "Import Settings",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Show progress dialog for file processing
        progress = ProgressDialog(
            "Importing Settings",
            "Reading and validating settings file...",
            parent_widget
        )
        progress.show()
        QApplication.processEvents()
        
        try:
            # Step 1: Read file
            progress.update_message("Reading settings file...")
            progress.set_progress(25)
            QApplication.processEvents()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Step 2: Validate file format
            progress.update_message("Validating file format...")
            progress.set_progress(50)
            QApplication.processEvents()
            
            validation_errors = self._validate_import_file(import_data)
            if validation_errors:
                progress.close()
                
                # Show detailed validation errors
                error_dialog = ValidationErrorDialog(
                    "Invalid Settings File",
                    validation_errors,
                    parent_widget
                )
                result = error_dialog.exec()
                
                if result == 2:  # Reset button clicked
                    self._show_file_format_help()
                return
            
            # Step 3: Check compatibility
            progress.update_message("Checking compatibility...")
            progress.set_progress(75)
            QApplication.processEvents()
            
            compatibility_warnings = self._check_compatibility(import_data)
            
            progress.update_message("Preparing import preview...")
            progress.set_progress(100)
            QApplication.processEvents()
            
            progress.close()
            
            # Show compatibility warnings if any
            if compatibility_warnings and ANKI_AVAILABLE:
                reply = QMessageBox.question(
                    parent_widget,
                    "Compatibility Warnings",
                    "The following compatibility issues were detected:\n\n" +
                    "\n".join([f"• {warning}" for warning in compatibility_warnings]) +
                    "\n\nDo you want to continue with the import?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Show preview dialog
            preview_dialog = ImportPreviewDialog(import_data, parent_widget)
            if preview_dialog.exec() == QDialog.DialogCode.Accepted:
                # Apply selected settings with progress
                selected_settings = preview_dialog.get_selected_settings()
                self._apply_imported_settings_with_progress(selected_settings, parent_widget)
                
                QMessageBox.information(
                    parent_widget,
                    "Import Successful",
                    "Settings imported successfully. Changes will take effect after applying settings."
                )
                
                logger.info(f"Settings imported from {file_path}")
            
        except json.JSONDecodeError as e:
            progress.close()
            
            # Enhanced JSON error handling
            error_details = [
                f"JSON parsing error: {str(e)}",
                "The file may be corrupted or not a valid JSON file",
                "Try opening the file in a text editor to check for syntax errors"
            ]
            
            error_dialog = ValidationErrorDialog(
                "Invalid JSON File",
                error_details,
                parent_widget
            )
            error_dialog.exec()
            
        except FileNotFoundError:
            progress.close()
            QMessageBox.warning(
                parent_widget,
                "File Not Found",
                f"The selected file could not be found:\n{file_path}\n\n"
                "The file may have been moved or deleted."
            )
            
        except PermissionError:
            progress.close()
            QMessageBox.warning(
                parent_widget,
                "Permission Denied",
                f"Cannot read the selected file:\n{file_path}\n\n"
                "Check that you have permission to read this file."
            )
            
        except Exception as e:
            progress.close()
            
            error_details = [
                f"Unexpected error: {str(e)}",
                "This may be due to file corruption or system issues",
                "Try selecting a different file or restart the application"
            ]
            
            error_dialog = ValidationErrorDialog(
                "Import Failed",
                error_details,
                parent_widget
            )
            error_dialog.exec()
            
            logger.error(f"Settings import failed: {e}")
    
    def _check_compatibility(self, import_data):
        """Check compatibility of imported settings."""
        warnings = []
        
        metadata = import_data.get('metadata', {})
        
        # Check version compatibility
        file_version = metadata.get('version', '1.0')
        if file_version != '1.0':
            warnings.append(f"Settings file version {file_version} may not be fully compatible")
        
        # Check addon version
        addon_version = metadata.get('addon_version', 'unknown')
        if addon_version != '2.0.0' and addon_version != 'unknown':
            warnings.append(f"Settings from addon version {addon_version} may have different features")
        
        # Check for deprecated settings
        settings = import_data.get('settings', {})
        deprecated_keys = []
        
        for category, category_settings in settings.items():
            if isinstance(category_settings, dict):
                for key in category_settings.keys():
                    if key.startswith('deprecated_') or key in ['old_theme_format', 'legacy_mode']:
                        deprecated_keys.append(f"{category}.{key}")
        
        if deprecated_keys:
            warnings.append(f"Deprecated settings will be ignored: {', '.join(deprecated_keys)}")
        
        # Check for missing required fields
        required_categories = ['theme', 'general']
        missing_categories = [cat for cat in required_categories if cat not in settings]
        
        if missing_categories:
            warnings.append(f"Missing settings categories: {', '.join(missing_categories)}")
        
        return warnings
    
    def _apply_imported_settings_with_progress(self, settings, parent_widget):
        """Apply imported settings with progress indicator."""
        progress = ProgressDialog(
            "Applying Settings",
            "Applying imported settings...",
            parent_widget
        )
        progress.show()
        QApplication.processEvents()
        
        try:
            total_steps = len(settings)
            current_step = 0
            
            for category, category_settings in settings.items():
                progress.update_message(f"Applying {category} settings...")
                progress.set_progress(int((current_step / total_steps) * 100))
                QApplication.processEvents()
                
                # Apply category settings
                self._apply_category_settings(category, category_settings)
                
                current_step += 1
            
            progress.set_progress(100)
            QApplication.processEvents()
            
        finally:
            progress.close()
    
    def _apply_category_settings(self, category, settings):
        """Apply settings for a specific category."""
        # This would be implemented in the parent ModernSettingsWindow
        if hasattr(self.parent_window, '_apply_imported_settings'):
            self.parent_window._apply_imported_settings({category: settings})
    
    def _show_file_format_help(self):
        """Show help dialog about correct file format."""
        if not ANKI_AVAILABLE:
            return
        
        help_text = """
Expected JSON format:

{
  "metadata": {
    "version": "1.0",
    "exported_at": "2024-12-10 10:30:00",
    "addon_version": "2.0.0"
  },
  "settings": {
    "theme": { ... },
    "general": { ... },
    "dictionaries": [ ... ]
  }
}

The file must be valid JSON with 'settings' as the main object.
        """.strip()
        
        QMessageBox.information(
            self,
            "Settings File Format",
            help_text
        )
    
    def _create_backup(self):
        """Create a backup of current settings."""
        try:
            # Get current settings
            if hasattr(self.parent_window, 'get_current_settings'):
                settings = self.parent_window.get_current_settings()
            else:
                settings = self._get_mock_settings()
            
            # Create backup directory if it doesn't exist
            backup_dir = Path.home() / ".anki2" / "addons21" / "Anki-Dictionary-Addon" / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = self._get_current_timestamp().replace(':', '-').replace(' ', '_')
            backup_file = backup_dir / f"settings_backup_{timestamp}.json"
            
            # Create backup data
            backup_data = {
                'metadata': {
                    'version': '1.0',
                    'backup_created_at': self._get_current_timestamp(),
                    'addon_version': '2.0.0',
                    'backup_type': 'manual'
                },
                'settings': settings
            }
            
            # Write backup file
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            QMessageBox.information(
                self,
                "Backup Created",
                f"Backup created successfully:\n{backup_file}"
            )
            
            logger.info(f"Manual backup created: {backup_file}")
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Backup Failed",
                f"Failed to create backup:\n{str(e)}"
            )
            logger.error(f"Backup creation failed: {e}")
    
    def _restore_backup(self):
        """Restore settings from a backup file."""
        if not ANKI_AVAILABLE:
            logger.info("Restore backup (mock implementation)")
            return
        
        # Get backup directory
        backup_dir = Path.home() / ".anki2" / "addons21" / "Anki-Dictionary-Addon" / "backups"
        
        # Get backup file from user
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Restore from Backup",
            str(backup_dir) if backup_dir.exists() else "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Read backup file
            with open(file_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Validate backup format
            if 'settings' not in backup_data:
                QMessageBox.warning(
                    self,
                    "Invalid Backup File",
                    "The selected file is not a valid backup file."
                )
                return
            
            # Confirm restoration
            reply = QMessageBox.question(
                self,
                "Confirm Restore",
                "Are you sure you want to restore from this backup?\n"
                "This will replace your current settings.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Apply backup settings
                self._apply_imported_settings(backup_data['settings'])
                
                QMessageBox.information(
                    self,
                    "Restore Successful",
                    "Settings restored successfully from backup."
                )
                
                logger.info(f"Settings restored from backup: {file_path}")
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Restore Failed",
                f"Failed to restore from backup:\n{str(e)}"
            )
            logger.error(f"Backup restore failed: {e}")
    
    def _quick_restore_from_recent_backup(self):
        """Restore settings from the most recent automatic backup with one click."""
        if not ANKI_AVAILABLE:
            logger.info("Quick restore from recent backup (mock implementation)")
            return
        
        try:
            # Find the most recent automatic backup
            recent_backup = self._find_most_recent_backup()
            
            if not recent_backup:
                QMessageBox.information(
                    self,
                    "No Backups Found",
                    "No automatic backups were found.\n\n"
                    "Automatic backups are created before major changes like resetting to defaults. "
                    "You can create a manual backup using the 'Create Backup Now' button."
                )
                return
            
            # Show confirmation with backup details
            backup_info = self._get_backup_info(recent_backup)
            reply = QMessageBox.question(
                self,
                "Quick Restore Confirmation",
                f"Restore from the most recent automatic backup?\n\n"
                f"Backup created: {backup_info['created_at']}\n"
                f"Backup reason: {backup_info['reason']}\n"
                f"File: {recent_backup.name}\n\n"
                f"This will replace your current settings.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Show progress dialog
            progress = ProgressDialog(
                "Quick Restore",
                "Restoring from recent backup...",
                self
            )
            progress.show()
            progress.set_progress(25)
            QApplication.processEvents()
            
            # Read and validate backup file
            progress.update_message("Reading backup file...")
            progress.set_progress(50)
            QApplication.processEvents()
            
            with open(recent_backup, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Validate backup format
            if 'settings' not in backup_data:
                progress.close()
                QMessageBox.warning(
                    self,
                    "Invalid Backup File",
                    "The backup file appears to be corrupted or invalid."
                )
                return
            
            # Apply backup settings
            progress.update_message("Applying backup settings...")
            progress.set_progress(75)
            QApplication.processEvents()
            
            if hasattr(self.parent_window, '_apply_imported_settings'):
                self.parent_window._apply_imported_settings(backup_data['settings'])
            
            progress.update_message("Finalizing restore...")
            progress.set_progress(100)
            QApplication.processEvents()
            
            progress.close()
            
            # Show success message
            QMessageBox.information(
                self,
                "Quick Restore Successful",
                f"Settings restored successfully from backup created on {backup_info['created_at']}.\n\n"
                "Changes will take effect after applying settings."
            )
            
            logger.info(f"Quick restore completed from backup: {recent_backup}")
            
        except Exception as e:
            if 'progress' in locals():
                progress.close()
            
            QMessageBox.warning(
                self,
                "Quick Restore Failed",
                f"Failed to restore from recent backup:\n{str(e)}"
            )
            logger.error(f"Quick restore failed: {e}")
    
    def _find_most_recent_backup(self):
        """Find the most recent automatic backup file."""
        try:
            backup_dir = Path.home() / ".anki2" / "addons21" / "Anki-Dictionary-Addon" / "backups"
            
            if not backup_dir.exists():
                return None
            
            # Find all automatic backup files
            backup_files = []
            for file_path in backup_dir.glob("auto_backup_*.json"):
                if file_path.is_file():
                    backup_files.append(file_path)
            
            if not backup_files:
                return None
            
            # Sort by modification time (most recent first)
            backup_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            return backup_files[0]
            
        except Exception as e:
            logger.warning(f"Failed to find recent backup: {e}")
            return None
    
    def _get_backup_info(self, backup_file):
        """Get information about a backup file."""
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            metadata = backup_data.get('metadata', {})
            
            return {
                'created_at': metadata.get('backup_created_at', 'Unknown'),
                'reason': metadata.get('backup_reason', 'Unknown'),
                'type': metadata.get('backup_type', 'Unknown'),
                'addon_version': metadata.get('addon_version', 'Unknown')
            }
            
        except Exception as e:
            logger.warning(f"Failed to read backup info: {e}")
            return {
                'created_at': 'Unknown',
                'reason': 'Unknown',
                'type': 'Unknown',
                'addon_version': 'Unknown'
            }
    
    def _update_quick_restore_status(self):
        """Update the status text for quick restore button."""
        if not ANKI_AVAILABLE:
            return
        
        try:
            recent_backup = self._find_most_recent_backup()
            
            if recent_backup:
                backup_info = self._get_backup_info(recent_backup)
                self.quick_restore_status.setText(f"Available: {backup_info['created_at']}")
                self.quick_restore_button.setEnabled(True)
            else:
                self.quick_restore_status.setText("No automatic backups found")
                self.quick_restore_button.setEnabled(False)
                
        except Exception as e:
            logger.warning(f"Failed to update quick restore status: {e}")
            self.quick_restore_status.setText("Status unknown")
            self.quick_restore_button.setEnabled(True)  # Enable anyway, let user try
    
    def _validate_import_file(self, import_data):
        """Validate imported settings file format with comprehensive checks."""
        errors = []
        
        # Check if it's a dictionary
        if not isinstance(import_data, dict):
            errors.append("File must contain a JSON object, not " + type(import_data).__name__)
            return errors
        
        # Check for required fields
        if 'settings' not in import_data:
            errors.append("Missing required 'settings' field")
        
        # Validate settings structure
        settings = import_data.get('settings', {})
        if not isinstance(settings, dict):
            errors.append("'settings' must be an object, not " + type(settings).__name__)
            return errors
        
        # Check metadata if present
        if 'metadata' in import_data:
            metadata_errors = self._validate_metadata(import_data['metadata'])
            errors.extend(metadata_errors)
        
        # Validate individual setting categories
        for category, category_settings in settings.items():
            category_errors = self._validate_settings_category(category, category_settings)
            errors.extend(category_errors)
        
        # Check for completely empty settings
        if not settings:
            errors.append("Settings object is empty - nothing to import")
        
        return errors
    
    def _validate_metadata(self, metadata):
        """Validate metadata structure."""
        errors = []
        
        if not isinstance(metadata, dict):
            errors.append("'metadata' must be an object")
            return errors
        
        # Check version
        if 'version' not in metadata:
            errors.append("Missing 'version' in metadata")
        elif not isinstance(metadata['version'], str):
            errors.append("Metadata 'version' must be a string")
        
        # Check exported_at format
        if 'exported_at' in metadata:
            exported_at = metadata['exported_at']
            if not isinstance(exported_at, str):
                errors.append("Metadata 'exported_at' must be a string")
            # Could add date format validation here
        
        # Check addon_version
        if 'addon_version' in metadata:
            addon_version = metadata['addon_version']
            if not isinstance(addon_version, str):
                errors.append("Metadata 'addon_version' must be a string")
        
        return errors
    
    def _validate_settings_category(self, category, category_settings):
        """Validate a specific settings category."""
        errors = []
        
        if category == 'theme':
            errors.extend(self._validate_theme_settings(category_settings))
        elif category == 'general':
            errors.extend(self._validate_general_settings(category_settings))
        elif category == 'dictionaries':
            errors.extend(self._validate_dictionary_settings(category_settings))
        else:
            # Unknown category - warn but don't error
            pass
        
        return errors
    
    def _validate_theme_settings(self, theme_settings):
        """Validate theme settings structure."""
        errors = []
        
        if not isinstance(theme_settings, dict):
            errors.append("Theme settings must be an object")
            return errors
        
        # Check required color fields
        required_colors = [
            'background_color', 'panel_color', 'text_primary', 
            'text_muted', 'border_color'
        ]
        
        for color_field in required_colors:
            if color_field in theme_settings:
                color_value = theme_settings[color_field]
                if not isinstance(color_value, str):
                    errors.append(f"Theme '{color_field}' must be a string")
                elif not self._is_valid_color(color_value):
                    errors.append(f"Theme '{color_field}' has invalid color format: {color_value}")
        
        # Check optional pitch accent colors
        pitch_colors = [
            'heiban_color', 'odaka_color', 'nakadaka_color', 
            'atamadaka_color', 'kifuku_color'
        ]
        
        for color_field in pitch_colors:
            if color_field in theme_settings:
                color_value = theme_settings[color_field]
                if not isinstance(color_value, str):
                    errors.append(f"Theme '{color_field}' must be a string")
                elif not self._is_valid_color(color_value):
                    errors.append(f"Theme '{color_field}' has invalid color format: {color_value}")
        
        return errors
    
    def _validate_general_settings(self, general_settings):
        """Validate general settings structure."""
        errors = []
        
        if not isinstance(general_settings, dict):
            errors.append("General settings must be an object")
            return errors
        
        # Validate numeric settings
        numeric_settings = {
            'search_delay': (0, 5000),
            'max_results': (1, 10000)
        }
        
        for setting_name, (min_val, max_val) in numeric_settings.items():
            if setting_name in general_settings:
                value = general_settings[setting_name]
                if not isinstance(value, int):
                    errors.append(f"General '{setting_name}' must be an integer")
                elif not (min_val <= value <= max_val):
                    errors.append(f"General '{setting_name}' must be between {min_val} and {max_val}")
        
        # Validate boolean settings
        boolean_settings = ['enable_tooltips', 'always_on_top', 'open_on_startup']
        
        for setting_name in boolean_settings:
            if setting_name in general_settings:
                value = general_settings[setting_name]
                if not isinstance(value, bool):
                    errors.append(f"General '{setting_name}' must be a boolean")
        
        return errors
    
    def _validate_dictionary_settings(self, dictionary_settings):
        """Validate dictionary settings structure."""
        errors = []
        
        if not isinstance(dictionary_settings, list):
            errors.append("Dictionary settings must be an array")
            return errors
        
        for i, dict_config in enumerate(dictionary_settings):
            if not isinstance(dict_config, dict):
                errors.append(f"Dictionary {i+1} must be an object")
                continue
            
            # Check required fields
            required_fields = ['id', 'name', 'type', 'enabled']
            for field in required_fields:
                if field not in dict_config:
                    errors.append(f"Dictionary {i+1} missing required field '{field}'")
            
            # Validate field types
            if 'enabled' in dict_config and not isinstance(dict_config['enabled'], bool):
                errors.append(f"Dictionary {i+1} 'enabled' must be a boolean")
            
            if 'priority' in dict_config and not isinstance(dict_config['priority'], int):
                errors.append(f"Dictionary {i+1} 'priority' must be an integer")
            
            if 'type' in dict_config and dict_config['type'] not in ['local', 'api', 'web']:
                errors.append(f"Dictionary {i+1} 'type' must be 'local', 'api', or 'web'")
        
        return errors
    
    def _is_valid_color(self, color_value):
        """Check if a color value is valid hex format."""
        if not isinstance(color_value, str):
            return False
        
        if not color_value.startswith('#'):
            return False
        
        if len(color_value) != 7:
            return False
        
        try:
            int(color_value[1:], 16)
            return True
        except ValueError:
            return False
    
    def _apply_imported_settings(self, settings):
        """Apply imported settings to the current window."""
        if not hasattr(self.parent_window, '_apply_imported_settings'):
            logger.warning("Parent window does not support settings import")
            return
        
        # This would be implemented in the parent ModernSettingsWindow
        self.parent_window._apply_imported_settings(settings)
    
    def _get_exported_categories(self):
        """Get list of categories being exported."""
        categories = []
        if self.export_all_checkbox.isChecked():
            return ['theme', 'general', 'dictionaries']
        
        if self.export_theme_checkbox.isChecked():
            categories.append('theme')
        if self.export_general_checkbox.isChecked():
            categories.append('general')
        if self.export_dict_checkbox.isChecked():
            categories.append('dictionaries')
        
        return categories
    
    def _get_current_timestamp(self):
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_mock_settings(self):
        """Get mock settings for testing."""
        return {
            'theme': {
                'background_color': '#0f0f0f',
                'panel_color': '#1c1c1c',
                'text_primary': '#e6e6e6',
                'text_muted': '#9aa0ad',
                'accent_color': '#4a9eff',
                'border_color': '#2b2f36'
            },
            'general': {
                'search_delay': 300,
                'max_results': 100,
                'enable_tooltips': True,
                'always_on_top': False,
                'open_on_startup': False
            },
            'dictionaries': []
        }


class ImportPreviewDialog(QDialog):
    """Dialog for previewing imported settings before applying."""
    
    def __init__(self, import_data, parent=None):
        """Initialize import preview dialog."""
        super().__init__(parent)
        self.import_data = import_data
        self.selected_settings = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up preview dialog UI."""
        self.setWindowTitle("Import Preview")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header
        header_label = QLabel("Preview Settings Import")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Select which settings categories to import:")
        theme = get_theme_manager().current_theme
        desc_label.setStyleSheet(f"color: {theme.text_muted}; margin-bottom: 12px;")
        layout.addWidget(desc_label)
        
        # Settings preview
        preview_widget = QWidget()
        preview_layout = QHBoxLayout(preview_widget)
        preview_layout.setSpacing(16)
        
        # Left side - Category selection
        categories_group = QGroupBox("Categories to Import")
        categories_layout = QVBoxLayout(categories_group)
        
        self.category_checkboxes = {}
        settings = self.import_data.get('settings', {})
        
        for category in ['theme', 'general', 'dictionaries']:
            if category in settings:
                checkbox = QCheckBox(f"{category.title()} Settings")
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(self._update_preview)
                self.category_checkboxes[category] = checkbox
                categories_layout.addWidget(checkbox)
        
        categories_layout.addStretch()
        preview_layout.addWidget(categories_group, 0)
        
        # Right side - Settings preview
        preview_group = QGroupBox("Settings Preview")
        preview_group_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(300)
        preview_group_layout.addWidget(self.preview_text)
        
        preview_layout.addWidget(preview_group, 1)
        layout.addWidget(preview_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.import_button = QPushButton("Import Selected")
        self.import_button.clicked.connect(self._import_selected)
        self.import_button.setDefault(True)
        button_layout.addWidget(self.import_button)
        
        layout.addLayout(button_layout)
        
        # Initial preview update
        self._update_preview()
    
    def _update_preview(self):
        """Update the settings preview based on selected categories."""
        preview_data = {}
        settings = self.import_data.get('settings', {})
        
        for category, checkbox in self.category_checkboxes.items():
            if checkbox.isChecked() and category in settings:
                preview_data[category] = settings[category]
        
        # Format preview text
        preview_text = json.dumps(preview_data, indent=2, ensure_ascii=False)
        self.preview_text.setPlainText(preview_text)
        
        # Update selected settings
        self.selected_settings = preview_data
    
    def _import_selected(self):
        """Import the selected settings."""
        if not self.selected_settings:
            QMessageBox.warning(
                self,
                "No Settings Selected",
                "Please select at least one category to import."
            )
            return
        
        self.accept()
    
    def get_selected_settings(self):
        """Get the selected settings for import."""
        return self.selected_settings


class GeneralTab(QWidget):
    """General settings tab."""
    
    def __init__(self, parent=None):
        """Initialize general tab."""
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up general tab UI."""
        # Use scroll area for better responsive behavior
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Search settings group
        search_group = QGroupBox("Search Settings")
        search_layout = QVBoxLayout(search_group)
        
        # Auto search delay
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Auto-search delay (ms):")
        delay_label.setMinimumWidth(150)
        if ANKI_AVAILABLE:
            delay_label.setToolTip(
                "Delay before automatic search starts\n"
                "• 0ms = Search immediately as you type\n"
                "• 300ms = Wait 0.3 seconds (recommended)\n"
                "• Higher values reduce server load\n"
                "• Lower values provide faster feedback"
            )
        delay_layout.addWidget(delay_label)
        self.search_delay = QSpinBox()
        self.search_delay.setMinimumWidth(100)
        if ANKI_AVAILABLE:
            self.search_delay.setRange(0, 2000)
            self.search_delay.setValue(300)
            self.search_delay.setToolTip(
                "Milliseconds to wait before searching\n"
                "Range: 0-2000ms\n"
                "Default: 300ms"
            )
        delay_layout.addWidget(self.search_delay)
        delay_layout.addStretch()
        search_layout.addLayout(delay_layout)
        
        # Max results
        results_layout = QHBoxLayout()
        results_label = QLabel("Maximum results:")
        results_label.setMinimumWidth(150)
        if ANKI_AVAILABLE:
            results_label.setToolTip(
                "Maximum number of search results to display\n"
                "• Higher values show more results\n"
                "• Lower values improve performance\n"
                "• Recommended: 50-200 results"
            )
        results_layout.addWidget(results_label)
        self.max_results = QSpinBox()
        self.max_results.setMinimumWidth(100)
        if ANKI_AVAILABLE:
            self.max_results.setRange(1, 1000)
            self.max_results.setValue(100)
            self.max_results.setToolTip(
                "Maximum search results to show\n"
                "Range: 1-1000 results\n"
                "Default: 100 results"
            )
        results_layout.addWidget(self.max_results)
        results_layout.addStretch()
        search_layout.addLayout(results_layout)
        
        layout.addWidget(search_group)
        
        # UI settings group
        ui_group = QGroupBox("UI Settings")
        ui_layout = QVBoxLayout(ui_group)
        
        self.enable_tooltips = QCheckBox("Enable tooltips")
        self.enable_tooltips.setChecked(True)
        if ANKI_AVAILABLE:
            self.enable_tooltips.setToolTip(
                "Show helpful tooltips when hovering over UI elements\n"
                "• Provides contextual help and explanations\n"
                "• Recommended for new users\n"
                "• Can be disabled to reduce visual clutter"
            )
        ui_layout.addWidget(self.enable_tooltips)
        
        self.always_on_top = QCheckBox("Always on top")
        if ANKI_AVAILABLE:
            self.always_on_top.setToolTip(
                "Keep dictionary window above other applications\n"
                "• Useful when working with other programs\n"
                "• May interfere with full-screen applications\n"
                "• Can be toggled with keyboard shortcut"
            )
        ui_layout.addWidget(self.always_on_top)
        
        self.open_on_startup = QCheckBox("Open on startup")
        if ANKI_AVAILABLE:
            self.open_on_startup.setToolTip(
                "Automatically open dictionary when Anki starts\n"
                "• Convenient for frequent users\n"
                "• May slow down Anki startup slightly\n"
                "• Dictionary will be minimized if enabled"
            )
        ui_layout.addWidget(self.open_on_startup)
        
        layout.addWidget(ui_group)
        layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        
        # Set up main layout for this tab
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)


class ModernSettingsWindow(QDialog):
    """
    Modern settings window with modal behavior and tabbed interface.
    
    This is a new implementation separate from the legacy settings window,
    designed to integrate with the mock UI and follow the design document.
    """
    
    def __init__(self, parent=None):
        """Initialize modern settings window."""
        super().__init__(parent)
        self.theme_manager = get_theme_manager()  # Add this
        self.style_generator = StyleGenerator(self.theme_manager.current_theme)  # Add this
        self.theme_manager.register_observer(self._on_theme_changed)  # Add this
        self._setup_window()
        self._create_tabs()
        self._setup_layout()
        self._setup_buttons()
        self._apply_styling()  # This will now use current theme
        
        logger.info("Modern settings window initialized")
    
    def _setup_window(self):
        """Set up window properties."""
        self.setWindowTitle("Dictionary Settings")
        self.setMinimumSize(1000, 600)  # Larger minimum size for better responsive layout
        self.resize(1200, 700)  # Larger default size to prevent UI bunching
        
        if ANKI_AVAILABLE:
            # Modal behavior - stays on top of parent (mock UI) but not all windows
            self.setModal(True)
            self.setWindowFlags(
                Qt.WindowType.Dialog | 
                Qt.WindowType.WindowCloseButtonHint
            )
    
    def _create_tabs(self):
        """Create tab widgets."""
        self.tab_widget = QTabWidget()
        
        # General tab (first)
        self.general_tab = GeneralTab()
        self.tab_widget.addTab(self.general_tab, "General")
        
        # Theme tab (second)
        self.theme_tab = ThemeTab()
        self.tab_widget.addTab(self.theme_tab, "Theme")
        
        # Dictionary management tab (third)
        self.dictionaries_tab = DictionariesTab()
        self.tab_widget.addTab(self.dictionaries_tab, "Dictionaries")
        
        # Import/Export tab (fourth)
        self.import_export_tab = ImportExportTab(self)
        self.tab_widget.addTab(self.import_export_tab, "Import/Export")
    
    def _setup_layout(self):
        """Set up main layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addWidget(self.tab_widget, 1)
    
    def _setup_buttons(self):
        """Set up dialog buttons."""
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(16, 12, 16, 16)
        buttons_layout.setSpacing(8)
        
        # Reset button
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.clicked.connect(self._reset_to_defaults)
        buttons_layout.addWidget(self.reset_button)
        
        buttons_layout.addStretch()
        
        # Cancel and Apply buttons
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_settings)
        self.apply_button.setDefault(True)
        buttons_layout.addWidget(self.apply_button)
        
        # Add buttons to main layout
        self.layout().addWidget(buttons_widget)
    
    def _apply_styling(self):
        """Apply theme styling to the dialog."""
        if not ANKI_AVAILABLE:
            return
        
        # Use current theme instead of hardcoded ThemeColors()
        theme = self.theme_manager.current_theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background_color};
                color: {theme.text_primary};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            
            QTabWidget::pane {{
                border: 1px solid {theme.border_color};
                background-color: {theme.background_color};
            }}
            
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            
            QTabBar::tab {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {theme.background_color};
                border-bottom: 1px solid {theme.background_color};
            }}
            
            QTabBar::tab:hover {{
                background-color: {self.style_generator.adjust_color_brightness(theme.panel_color, 1.2)};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {theme.border_color};
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
                color: {theme.text_primary};
            }}
            
            QLabel {{
                color: {theme.text_primary};
            }}
            
            QCheckBox {{
                color: {theme.text_primary};
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {theme.border_color};
                border-radius: 4px;
                background-color: {theme.panel_color};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {theme.heiban_color};
                border-color: {theme.heiban_color};
                image: none;
            }}
            
            QCheckBox::indicator:checked::after {{
                content: "✓";
                color: white;
                font-weight: bold;
                font-size: 12px;
            }}
            
            QCheckBox:disabled {{
                color: {theme.text_muted};
            }}
            
            QCheckBox::indicator:disabled {{
                background-color: {self.style_generator.adjust_color_brightness(theme.panel_color, 0.8)};
                border-color: {theme.border_color};
            }}
            
            QCheckBox::indicator:checked:disabled {{
                background-color: {theme.border_color};
                border-color: {self.style_generator.adjust_color_brightness(theme.border_color, 1.2)};
            }}
            
            QSpinBox, QLineEdit {{
                background-color: {theme.panel_color};
                border: 1px solid {theme.border_color};
                border-radius: 4px;
                padding: 4px 8px;
                color: {theme.text_primary};
                min-width: 80px;
            }}
            
            QSpinBox:focus, QLineEdit:focus {{
                border-color: {theme.accent_color};
            }}
            
            /* FIXME: Spinbox arrows are still messed up - need better styling */
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: {theme.panel_color};
                border: 1px solid {theme.border_color};
                width: 20px;
                height: 12px;
            }}
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {self.style_generator.adjust_color_brightness(theme.panel_color, 1.2)};
            }}
            
            QSpinBox::up-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 6px solid {theme.text_primary};
                width: 0px;
                height: 0px;
            }}
            
            QSpinBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {theme.text_primary};
                width: 0px;
                height: 0px;
            }}
            
            QPushButton {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {self.style_generator.adjust_color_brightness(theme.panel_color, 1.2)};
                border-color: {self.style_generator.adjust_color_brightness(theme.border_color, 1.2)};
            }}
            
            QPushButton:pressed {{
                background-color: {self.style_generator.adjust_color_brightness(theme.panel_color, 0.8)};
            }}
            
            QPushButton:default {{
                background-color: {theme.accent_color};
                border-color: {theme.accent_color};
            }}
            
            QPushButton:default:hover {{
                background-color: {self.style_generator.adjust_color_brightness(theme.accent_color, 1.2)};
            }}
        """)
    
    def _apply_settings(self):
        """Apply settings with validation and error handling."""
        # Validate all settings before applying
        validation_errors = self._validate_all_settings()
        
        if validation_errors:
            # Show validation errors to user
            if ANKI_AVAILABLE:
                error_dialog = ValidationErrorDialog(
                    "Settings Validation Failed",
                    validation_errors,
                    self
                )
                result = error_dialog.exec()
                
                if result == 2:  # Reset button clicked
                    self._reset_to_defaults()
                    return
            else:
                logger.warning(f"Validation errors: {validation_errors}")
            return
        
        try:
            # Show progress for applying settings
            if ANKI_AVAILABLE:
                progress = ProgressDialog(
                    "Applying Settings",
                    "Saving configuration...",
                    self
                )
                progress.show()
                progress.set_progress(50)
                QApplication.processEvents()
            
            # Apply theme changes to all observers via theme manager
            new_theme = self.theme_tab.get_theme()
            get_theme_manager().update_theme(new_theme)
            logger.info("Applied theme changes via theme manager")
            
            # FIXME: Link dictionary settings to mock search functionality (future PR)
            # FIXME: Implement settings persistence to JSON/config files (future PR)
            # FIXME: Ensure settings persistence across application restarts (future PR)
            
            logger.info("Settings applied successfully")
            
            if ANKI_AVAILABLE:
                progress.set_progress(100)
                QApplication.processEvents()
                progress.close()
            
            self.accept()
            
        except Exception as e:
            if ANKI_AVAILABLE:
                progress.close()
                
                QMessageBox.critical(
                    self,
                    "Settings Apply Failed",
                    f"Failed to apply settings:\n{str(e)}\n\n"
                    "Your settings have not been saved. Please try again or reset to defaults."
                )
            
            logger.error(f"Failed to apply settings: {e}")
    
    def _validate_all_settings(self):
        """Validate all settings and return list of errors."""
        errors = []
        
        # Validate theme settings
        theme_errors = self._validate_theme_tab()
        errors.extend(theme_errors)
        
        # Validate general settings
        general_errors = self._validate_general_tab()
        errors.extend(general_errors)
        
        # Validate dictionary settings
        dict_errors = self._validate_dictionaries_tab()
        errors.extend(dict_errors)
        
        return errors
    
    def _validate_theme_tab(self):
        """Validate theme tab settings."""
        errors = []
        
        # Check all color pickers for validation errors
        color_pickers = [
            ('Background', self.theme_tab.bg_picker),
            ('Panel', self.theme_tab.panel_picker),
            ('Text', self.theme_tab.text_picker),
            ('Muted Text', self.theme_tab.muted_picker),
            ('Border', self.theme_tab.border_picker),
            ('Heiban', self.theme_tab.heiban_picker),
            ('Odaka', self.theme_tab.odaka_picker),
            ('Nakadaka', self.theme_tab.nakadaka_picker),
            ('Atamadaka', self.theme_tab.atamadaka_picker),
            ('Kifuku', self.theme_tab.kifuku_picker),
        ]
        
        for name, picker in color_pickers:
            if not picker.is_valid():
                error_msg = picker.get_validation_error()
                errors.append(f"{name} color: {error_msg}")
        
        return errors
    
    def _validate_general_tab(self):
        """Validate general tab settings."""
        errors = []
        
        if ANKI_AVAILABLE:
            # Validate search delay
            delay = self.general_tab.search_delay.value()
            if delay < 0 or delay > 2000:
                errors.append(f"Search delay must be between 0 and 2000ms (current: {delay}ms)")
            
            # Validate max results
            max_results = self.general_tab.max_results.value()
            if max_results < 1 or max_results > 1000:
                errors.append(f"Maximum results must be between 1 and 1000 (current: {max_results})")
        
        return errors
    
    def _validate_dictionaries_tab(self):
        """Validate dictionaries tab settings."""
        errors = []
        
        dictionaries = self.dictionaries_tab.get_dictionaries()
        
        # Check if at least one dictionary is enabled
        enabled_dicts = [d for d in dictionaries if d.get('enabled', False)]
        if not enabled_dicts:
            errors.append("At least one dictionary must be enabled for search to work")
        
        # Check for duplicate dictionary IDs
        dict_ids = [d.get('id', '') for d in dictionaries]
        duplicate_ids = [id for id in dict_ids if dict_ids.count(id) > 1]
        if duplicate_ids:
            errors.append(f"Duplicate dictionary IDs found: {', '.join(set(duplicate_ids))}")
        
        # Validate individual dictionary configurations
        for i, dict_config in enumerate(dictionaries):
            dict_name = dict_config.get('name', f'Dictionary {i+1}')
            
            # Check required fields
            if not dict_config.get('id'):
                errors.append(f"{dict_name}: Missing dictionary ID")
            
            if not dict_config.get('name'):
                errors.append(f"Dictionary {i+1}: Missing dictionary name")
            
            if not dict_config.get('type'):
                errors.append(f"{dict_name}: Missing dictionary type")
            elif dict_config['type'] not in ['local', 'api', 'web']:
                errors.append(f"{dict_name}: Invalid dictionary type '{dict_config['type']}'")
        
        return errors
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults with confirmation and backup."""
        if not ANKI_AVAILABLE:
            logger.info("Reset to defaults (mock implementation)")
            return
        
        # Show detailed confirmation dialog
        affected_settings = [
            "All theme colors will be reset to dark theme",
            "Search delay will be reset to 300ms",
            "Maximum results will be reset to 100",
            "UI settings will be reset to defaults",
            "Dictionary list will be reset to default dictionaries"
        ]
        
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to defaults?\n\n" +
            "The following settings will be affected:\n" +
            "\n".join([f"• {setting}" for setting in affected_settings]) +
            "\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Show progress dialog
            progress = ProgressDialog(
                "Resetting Settings",
                "Creating backup of current settings...",
                self
            )
            progress.show()
            progress.set_progress(20)
            QApplication.processEvents()
            
            # Create automatic backup before reset
            self._create_automatic_backup()
            
            progress.update_message("Resetting theme settings...")
            progress.set_progress(40)
            QApplication.processEvents()
            
            # Reset theme tab to dark preset
            self.theme_tab._apply_preset("dark")
            
            progress.update_message("Resetting general settings...")
            progress.set_progress(60)
            QApplication.processEvents()
            
            # Reset general settings
            self.general_tab.search_delay.setValue(300)
            self.general_tab.max_results.setValue(100)
            self.general_tab.enable_tooltips.setChecked(True)
            self.general_tab.always_on_top.setChecked(False)
            self.general_tab.open_on_startup.setChecked(False)
            
            progress.update_message("Resetting dictionary settings...")
            progress.set_progress(80)
            QApplication.processEvents()
            
            # Reset dictionaries to defaults
            self.dictionaries_tab._load_dictionaries()
            
            progress.update_message("Finalizing reset...")
            progress.set_progress(100)
            QApplication.processEvents()
            
            progress.close()
            
            # Show success message with backup info
            QMessageBox.information(
                self,
                "Reset Complete",
                "Settings have been reset to defaults.\n\n"
                "A backup of your previous settings has been created automatically. "
                "You can restore from this backup using the Import/Export tab."
            )
            
            logger.info("Settings reset to defaults with backup created")
            
        except Exception as e:
            if 'progress' in locals():
                progress.close()
            
            QMessageBox.critical(
                self,
                "Reset Failed",
                f"Failed to reset settings to defaults:\n{str(e)}\n\n"
                "Your current settings have been preserved."
            )
            
            logger.error(f"Failed to reset settings: {e}")
    
    def _create_automatic_backup(self):
        """Create an automatic backup before major changes."""
        try:
            # Get current settings
            settings = self.get_current_settings()
            
            # Create backup directory if it doesn't exist
            backup_dir = Path.home() / ".anki2" / "addons21" / "Anki-Dictionary-Addon" / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate backup filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"auto_backup_before_reset_{timestamp}.json"
            
            # Create backup data
            backup_data = {
                'metadata': {
                    'version': '1.0',
                    'backup_created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'addon_version': '2.0.0',
                    'backup_type': 'automatic',
                    'backup_reason': 'before_reset_to_defaults'
                },
                'settings': settings
            }
            
            # Write backup file
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Automatic backup created: {backup_file}")
            
        except Exception as e:
            logger.warning(f"Failed to create automatic backup: {e}")
            # Don't fail the reset operation if backup fails
    
    def get_current_settings(self):
        """Get current settings configuration."""
        return {
            'theme': {
                'background_color': self.theme_tab.theme.background_color,
                'panel_color': self.theme_tab.theme.panel_color,
                'text_primary': self.theme_tab.theme.text_primary,
                'text_muted': self.theme_tab.theme.text_muted,
                'border_color': self.theme_tab.theme.border_color,
                'heiban_color': self.theme_tab.theme.heiban_color,
                'odaka_color': self.theme_tab.theme.odaka_color,
                'nakadaka_color': self.theme_tab.theme.nakadaka_color,
                'atamadaka_color': self.theme_tab.theme.atamadaka_color,
                'kifuku_color': self.theme_tab.theme.kifuku_color,
            },
            'general': {
                'search_delay': self.general_tab.search_delay.value() if ANKI_AVAILABLE else 300,
                'max_results': self.general_tab.max_results.value() if ANKI_AVAILABLE else 100,
                'enable_tooltips': self.general_tab.enable_tooltips.isChecked(),
                'always_on_top': self.general_tab.always_on_top.isChecked(),
                'open_on_startup': self.general_tab.open_on_startup.isChecked(),
            },
            'dictionaries': self.dictionaries_tab.get_dictionaries()
        }
    
    def _apply_imported_settings(self, settings):
        """Apply imported settings to the current window."""
        try:
            # Apply theme settings
            if 'theme' in settings:
                theme_settings = settings['theme']
                theme = ThemeColors(
                    background_color=theme_settings.get('background_color', '#0f0f0f'),
                    panel_color=theme_settings.get('panel_color', '#1c1c1c'),
                    text_primary=theme_settings.get('text_primary', '#e6e6e6'),
                    text_muted=theme_settings.get('text_muted', '#9aa0ad'),
                    border_color=theme_settings.get('border_color', '#2b2f36'),
                    heiban_color=theme_settings.get('heiban_color', '#4a9eff'),
                    odaka_color=theme_settings.get('odaka_color', '#51cf66'),
                    nakadaka_color=theme_settings.get('nakadaka_color', '#ffd43b'),
                    atamadaka_color=theme_settings.get('atamadaka_color', '#ff6b6b'),
                    kifuku_color=theme_settings.get('kifuku_color', '#9775fa')
                )
                
                # Update theme tab
                self.theme_tab.bg_picker.set_color(theme.background_color)
                self.theme_tab.panel_picker.set_color(theme.panel_color)
                self.theme_tab.text_picker.set_color(theme.text_primary)
                self.theme_tab.muted_picker.set_color(theme.text_muted)
                self.theme_tab.border_picker.set_color(theme.border_color)
                self.theme_tab.heiban_picker.set_color(theme.heiban_color)
                self.theme_tab.odaka_picker.set_color(theme.odaka_color)
                self.theme_tab.nakadaka_picker.set_color(theme.nakadaka_color)
                self.theme_tab.atamadaka_picker.set_color(theme.atamadaka_color)
                self.theme_tab.kifuku_picker.set_color(theme.kifuku_color)
                self.theme_tab.theme = theme
                self.theme_tab.live_preview.update_theme(theme)
            
            # Apply general settings
            if 'general' in settings:
                general_settings = settings['general']
                
                if ANKI_AVAILABLE:
                    self.general_tab.search_delay.setValue(
                        general_settings.get('search_delay', 300)
                    )
                    self.general_tab.max_results.setValue(
                        general_settings.get('max_results', 100)
                    )
                
                self.general_tab.enable_tooltips.setChecked(
                    general_settings.get('enable_tooltips', True)
                )
                self.general_tab.always_on_top.setChecked(
                    general_settings.get('always_on_top', False)
                )
                self.general_tab.open_on_startup.setChecked(
                    general_settings.get('open_on_startup', False)
                )
            
            # Apply dictionary settings
            if 'dictionaries' in settings:
                dict_settings = settings['dictionaries']
                if isinstance(dict_settings, list):
                    self.dictionaries_tab.dictionaries = dict_settings
                    self.dictionaries_tab._refresh_dictionary_list()
            
            logger.info("Imported settings applied successfully")
            
        except Exception as e:
            logger.error(f"Failed to apply imported settings: {e}")
            raise
    
    def _on_theme_changed(self, new_theme: ThemeColors):
        """Handle theme changes from theme manager."""
        self.style_generator = StyleGenerator(new_theme)
        self._apply_styling()  # Reapply styling with new theme
        # Also update the theme tab if it exists
        if hasattr(self, 'theme_tab'):
            self.theme_tab.update_theme(new_theme)
    
    def closeEvent(self, event):
        """Clean up theme observer on close."""
        self.theme_manager.unregister_observer(self._on_theme_changed)
        super().closeEvent(event)


def show_modern_settings(parent=None):
    """
    Show modern settings dialog and return settings if applied.
    
    Args:
        parent: Parent widget
        
    Returns:
        Settings dictionary if applied, None if cancelled
    """
    dialog = ModernSettingsWindow(parent)
    
    if ANKI_AVAILABLE:
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            return dialog.get_current_settings()
    else:
        # For testing - just show the dialog
        dialog.show()
        return dialog.get_current_settings()
    
    return None