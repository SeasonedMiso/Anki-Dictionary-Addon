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


class ThemeColors:
    """Theme color configuration."""
    
    def __init__(self, 
                 background_color="#0f0f0f",
                 panel_color="#1c1c1c", 
                 text_primary="#e6e6e6",
                 text_muted="#9aa0ad",
                 accent_color="#4a9eff",
                 border_color="#2b2f36",
                 # Pitch accent colors
                 heiban_color="#4a9eff",      # Blue for heiban (flat)
                 odaka_color="#51cf66",       # Green for odaka (tail-high)
                 nakadaka_color="#ffd43b",    # Yellow/orange for nakadaka (middle-high)
                 atamadaka_color="#ff6b6b",   # Red for atamadaka (head-high)
                 kifuku_color="#9775fa",      # Purple for kifuku (complex)
                 # Border options
                 show_borders=True):          # Whether to show borders around individual elements
        self.background_color = background_color
        self.panel_color = panel_color
        self.text_primary = text_primary
        self.text_muted = text_muted
        self.accent_color = accent_color
        self.border_color = border_color
        # Pitch accent colors
        self.heiban_color = heiban_color
        self.odaka_color = odaka_color
        self.nakadaka_color = nakadaka_color
        self.atamadaka_color = atamadaka_color
        self.kifuku_color = kifuku_color
        self.show_borders = show_borders


class LivePreview(QWidget):
    """Live preview component showing theme changes in real-time."""
    
    def __init__(self, parent=None):
        """Initialize live preview."""
        super().__init__(parent)
        self.theme = ThemeColors()
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
    """Color picker widget with live preview."""
    
    def __init__(self, label, initial_color, parent=None):
        """Initialize color picker."""
        super().__init__(parent)
        self.label = label
        self.color = initial_color
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up color picker UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label - use minimum width instead of fixed width for better responsiveness
        label = QLabel(self.label)
        label.setMinimumWidth(100)  # Reasonable minimum
        label.setMaximumWidth(160)  # Prevent excessive stretching
        label.setWordWrap(False)
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(label)
        
        # Color display button
        self.color_button = QPushButton()
        self.color_button.setFixedSize(40, 30)
        self.color_button.clicked.connect(self._open_color_dialog)
        layout.addWidget(self.color_button)
        
        # Color value input
        self.color_input = QLineEdit(self.color)
        self.color_input.setMinimumWidth(80)
        self.color_input.setMaximumWidth(100)
        self.color_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.color_input)
        
        layout.addStretch(1)  # Add stretch with factor
        self._update_button_color()
    
    def _update_button_color(self):
        """Update button background color."""
        if not ANKI_AVAILABLE:
            return
        
        self.color_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                border: 1px solid #555;
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
            self._update_button_color()
    
    def _on_text_changed(self, text):
        """Handle text input changes."""
        # Validate hex color format
        if text.startswith('#') and len(text) == 7:
            try:
                int(text[1:], 16)  # Validate hex
                self.color = text
                self._update_button_color()
            except ValueError:
                pass
    
    def get_color(self):
        """Get current color value."""
        return self.color
    
    def set_color(self, color):
        """Set color value."""
        self.color = color
        self.color_input.setText(color)
        self._update_button_color()


class ThemeTab(QWidget):
    """Theme customization tab with live preview."""
    
    def __init__(self, parent=None):
        """Initialize theme tab."""
        super().__init__(parent)
        self.theme = ThemeColors()
        self._setup_ui()
        
        # Timer for live updates (debounced)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._update_preview)
        if ANKI_AVAILABLE:
            self.update_timer.setInterval(100)  # 100ms debounce
    
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
        
        # Color pickers group
        colors_group = QGroupBox("Colors")
        colors_layout = QVBoxLayout(colors_group)
        colors_layout.setSpacing(8)
        
        # Basic colors
        self.bg_picker = ColorPicker("Background:", self.theme.background_color)
        self.panel_picker = ColorPicker("Panel:", self.theme.panel_color)
        self.text_picker = ColorPicker("Text:", self.theme.text_primary)
        self.muted_picker = ColorPicker("Muted Text:", self.theme.text_muted)
        self.border_picker = ColorPicker("Border:", self.theme.border_color)
        
        colors_layout.addWidget(self.bg_picker)
        colors_layout.addWidget(self.panel_picker)
        colors_layout.addWidget(self.text_picker)
        colors_layout.addWidget(self.muted_picker)
        colors_layout.addWidget(self.border_picker)
        
        # Pitch accent colors (Japanese-specific) - only show if Japanese dictionaries are present
        self.pitch_accent_group = QGroupBox("Pitch Accent Colors (Japanese)")
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
        
        # Add tooltips for pitch accent explanations
        if ANKI_AVAILABLE:
            self.heiban_picker.setToolTip("Heiban (平板): Flat pitch pattern")
            self.odaka_picker.setToolTip("Odaka (尾高): Tail-high pitch pattern")
            self.nakadaka_picker.setToolTip("Nakadaka (中高): Middle-high pitch pattern")
            self.atamadaka_picker.setToolTip("Atamadaka (頭高): Head-high pitch pattern")
            self.kifuku_picker.setToolTip("Kifuku (起伏): Complex pitch pattern")
        
        # Initially show pitch accent colors (will be hidden/shown based on language detection)
        colors_layout.addWidget(self.pitch_accent_group)
        
        controls_layout.addWidget(colors_group)
        
        # Add some spacing between major groups
        controls_layout.addSpacing(8)
        
        # Theme presets group
        presets_group = QGroupBox("Presets")
        presets_layout = QVBoxLayout(presets_group)
        
        preset_buttons_layout = QHBoxLayout()
        preset_buttons_layout.setSpacing(8)
        
        self.dark_preset_btn = QPushButton("Dark")
        self.light_preset_btn = QPushButton("Light")
        self.blue_preset_btn = QPushButton("Blue")
        
        # Set consistent button sizes
        for btn in [self.dark_preset_btn, self.light_preset_btn, self.blue_preset_btn]:
            btn.setMinimumWidth(80)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        self.dark_preset_btn.clicked.connect(lambda: self._apply_preset("dark"))
        self.light_preset_btn.clicked.connect(lambda: self._apply_preset("light"))
        self.blue_preset_btn.clicked.connect(lambda: self._apply_preset("blue"))
        
        preset_buttons_layout.addWidget(self.dark_preset_btn)
        preset_buttons_layout.addWidget(self.light_preset_btn)
        preset_buttons_layout.addWidget(self.blue_preset_btn)
        preset_buttons_layout.addStretch(1)
        
        presets_layout.addLayout(preset_buttons_layout)
        controls_layout.addWidget(presets_group)
        
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
            self.live_preview.setStyleSheet("""
                LivePreview {
                    border: 1px solid #2b2f36;
                    border-radius: 8px;
                    padding: 8px;
                }
            """)
        
        preview_layout.addWidget(self.live_preview)
        preview_layout.addStretch()
        
        preview_scroll.setWidget(self.preview_widget)
        preview_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        layout.addWidget(preview_scroll, 1)  # Less space for preview
        
        # Connect color pickers to live update
        for picker in [self.bg_picker, self.panel_picker, self.text_picker, 
                      self.muted_picker, self.border_picker,
                      self.heiban_picker, self.odaka_picker, self.nakadaka_picker,
                      self.atamadaka_picker, self.kifuku_picker]:
            picker.color_input.textChanged.connect(self._schedule_update)
        
        # Check if we should show pitch accent colors based on available dictionaries
        self._update_pitch_accent_visibility()
    
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
            heiban_color=self.heiban_picker.get_color(),
            odaka_color=self.odaka_picker.get_color(),
            nakadaka_color=self.nakadaka_picker.get_color(),
            atamadaka_color=self.atamadaka_picker.get_color(),
            kifuku_color=self.kifuku_picker.get_color()
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
        presets = {
            "dark": ThemeColors(
                background_color="#0f0f0f",
                panel_color="#1c1c1c",
                text_primary="#e6e6e6",
                text_muted="#9aa0ad",
                border_color="#2b2f36",
                heiban_color="#4a9eff",
                odaka_color="#51cf66",
                nakadaka_color="#ffd43b",
                atamadaka_color="#ff6b6b",
                kifuku_color="#9775fa"
            ),
            "light": ThemeColors(
                background_color="#ffffff",
                panel_color="#f5f5f5",
                text_primary="#1a1a1a",
                text_muted="#666666",
                border_color="#d0d0d0",
                heiban_color="#0066cc",
                odaka_color="#2b8a3e",
                nakadaka_color="#e67700",
                atamadaka_color="#c92a2a",
                kifuku_color="#7048e8"
            ),
            "blue": ThemeColors(
                background_color="#0a0e1a",
                panel_color="#1a1f2e",
                text_primary="#e1e8f0",
                text_muted="#8a9bb8",
                border_color="#2a3441",
                heiban_color="#3a7afe",
                odaka_color="#40c057",
                nakadaka_color="#fab005",
                atamadaka_color="#fa5252",
                kifuku_color="#9775fa"
            )
        }
        
        if preset_name in presets:
            theme = presets[preset_name]
            self.theme = theme
            
            # Update color pickers
            self.bg_picker.set_color(theme.background_color)
            self.panel_picker.set_color(theme.panel_color)
            self.text_picker.set_color(theme.text_primary)
            self.muted_picker.set_color(theme.text_muted)
            self.border_picker.set_color(theme.border_color)
            self.heiban_picker.set_color(theme.heiban_color)
            self.odaka_picker.set_color(theme.odaka_color)
            self.nakadaka_picker.set_color(theme.nakadaka_color)
            self.atamadaka_picker.set_color(theme.atamadaka_color)
            self.kifuku_picker.set_color(theme.kifuku_color)
            
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
    
    def get_theme(self):
        """Get current theme configuration."""
        return self.theme
    
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
        priority_label.setStyleSheet("color: #9aa0ad; font-size: 12px;")
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
        details_label.setStyleSheet("color: #9aa0ad; font-size: 12px;")
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
        
        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.setFixedWidth(80)
        remove_btn.clicked.connect(
            lambda checked, dict_id=dict_config['id']: self._remove_dictionary(dict_id)
        )
        item_layout.addWidget(remove_btn)
        
        # Priority indicator (far right)
        priority_label = QLabel(f"#{dict_config['priority'] + 1}")
        priority_label.setStyleSheet("color: #9aa0ad; font-size: 12px; font-weight: bold;")
        priority_label.setFixedWidth(30)
        item_layout.addWidget(priority_label)
        
        # Style the item
        if not ANKI_AVAILABLE:
            return item_widget
        
        item_widget.setStyleSheet(f"""
            QWidget {{
                background-color: #1c1c1c;
                border: 1px solid #2b2f36;
                border-radius: 6px;
            }}
            QWidget:hover {{
                border-color: #4a9eff;
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
        self.status_label.setStyleSheet("color: #9aa0ad; font-size: 12px;")
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
        """Validate dictionary connection."""
        conn_str = self.conn_input.text().strip()
        dict_type = self.type_combo.currentText()
        
        if not conn_str:
            self.status_label.setText("Please enter a connection string")
            self.status_label.setStyleSheet("color: #ff6b6b;")
            return
        
        # Mock validation - in production this would actually test the connection
        if dict_type == "Local File":
            if not conn_str.endswith(('.zip', '.json', '.db')):
                self.status_label.setText("Local files should be .zip, .json, or .db format")
                self.status_label.setStyleSheet("color: #ff6b6b;")
                return
        elif dict_type in ["API", "Web Service"]:
            if not conn_str.startswith(('http://', 'https://')):
                self.status_label.setText("API/Web connections should start with http:// or https://")
                self.status_label.setStyleSheet("color: #ff6b6b;")
                return
        
        self.status_label.setText("✓ Connection validated successfully")
        self.status_label.setStyleSheet("color: #51cf66;")
    
    def _add_dictionary(self):
        """Add the dictionary."""
        name = self.name_input.text().strip()
        if not name:
            self.status_label.setText("Please enter a dictionary name")
            self.status_label.setStyleSheet("color: #ff6b6b;")
            return
        
        conn_str = self.conn_input.text().strip()
        if not conn_str:
            self.status_label.setText("Please enter a connection string")
            self.status_label.setStyleSheet("color: #ff6b6b;")
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
        export_desc.setStyleSheet("color: #9aa0ad; font-size: 12px;")
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
        import_desc.setStyleSheet("color: #9aa0ad; font-size: 12px;")
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
        backup_desc.setStyleSheet("color: #9aa0ad; font-size: 12px;")
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
        """Import settings from JSON file."""
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
        
        try:
            # Read and validate file
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Validate file format
            validation_errors = self._validate_import_file(import_data)
            if validation_errors:
                QMessageBox.warning(
                    self,
                    "Invalid File Format",
                    "The selected file is not a valid settings export:\n" + 
                    "\n".join(validation_errors)
                )
                return
            
            # Show preview dialog
            preview_dialog = ImportPreviewDialog(import_data, self)
            if preview_dialog.exec() == QDialog.DialogCode.Accepted:
                # Apply selected settings
                selected_settings = preview_dialog.get_selected_settings()
                self._apply_imported_settings(selected_settings)
                
                QMessageBox.information(
                    self,
                    "Import Successful",
                    "Settings imported successfully. Changes will take effect after applying settings."
                )
                
                logger.info(f"Settings imported from {file_path}")
            
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "Invalid JSON File",
                f"The selected file is not valid JSON:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Import Failed",
                f"Failed to import settings:\n{str(e)}"
            )
            logger.error(f"Settings import failed: {e}")
    
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
    
    def _validate_import_file(self, import_data):
        """Validate imported settings file format."""
        errors = []
        
        # Check if it's a dictionary
        if not isinstance(import_data, dict):
            errors.append("File must contain a JSON object")
            return errors
        
        # Check for required fields
        if 'settings' not in import_data:
            errors.append("Missing 'settings' field")
        
        # Check metadata if present
        if 'metadata' in import_data:
            metadata = import_data['metadata']
            if not isinstance(metadata, dict):
                errors.append("'metadata' must be an object")
            elif 'version' not in metadata:
                errors.append("Missing version in metadata")
        
        # Validate settings structure
        settings = import_data.get('settings', {})
        if not isinstance(settings, dict):
            errors.append("'settings' must be an object")
        
        return errors
    
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
        desc_label.setStyleSheet("color: #9aa0ad; margin-bottom: 12px;")
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
        delay_layout.addWidget(delay_label)
        self.search_delay = QSpinBox()
        self.search_delay.setMinimumWidth(100)
        if ANKI_AVAILABLE:
            self.search_delay.setRange(0, 2000)
            self.search_delay.setValue(300)
        delay_layout.addWidget(self.search_delay)
        delay_layout.addStretch()
        search_layout.addLayout(delay_layout)
        
        # Max results
        results_layout = QHBoxLayout()
        results_label = QLabel("Maximum results:")
        results_label.setMinimumWidth(150)
        results_layout.addWidget(results_label)
        self.max_results = QSpinBox()
        self.max_results.setMinimumWidth(100)
        if ANKI_AVAILABLE:
            self.max_results.setRange(1, 1000)
            self.max_results.setValue(100)
        results_layout.addWidget(self.max_results)
        results_layout.addStretch()
        search_layout.addLayout(results_layout)
        
        layout.addWidget(search_group)
        
        # UI settings group
        ui_group = QGroupBox("UI Settings")
        ui_layout = QVBoxLayout(ui_group)
        
        self.enable_tooltips = QCheckBox("Enable tooltips")
        self.enable_tooltips.setChecked(True)
        ui_layout.addWidget(self.enable_tooltips)
        
        self.always_on_top = QCheckBox("Always on top")
        ui_layout.addWidget(self.always_on_top)
        
        self.open_on_startup = QCheckBox("Open on startup")
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
        self._setup_window()
        self._create_tabs()
        self._setup_layout()
        self._setup_buttons()
        self._apply_styling()
        
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
        """Apply dark theme styling to the dialog."""
        if not ANKI_AVAILABLE:
            return
        
        theme = ThemeColors()
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
                background-color: #333;
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
                color: #555;
            }}
            
            QCheckBox::indicator:disabled {{
                background-color: #333;
                border-color: #555;
            }}
            
            QCheckBox::indicator:checked:disabled {{
                background-color: #555;
                border-color: #666;
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
                background-color: #333;
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
                background-color: #333;
                border-color: #555;
            }}
            
            QPushButton:pressed {{
                background-color: #222;
            }}
            
            QPushButton:default {{
                background-color: {theme.accent_color};
                border-color: {theme.accent_color};
            }}
            
            QPushButton:default:hover {{
                background-color: #5a9fff;
            }}
        """)
    
    def _apply_settings(self):
        """Apply settings and close dialog."""
        # FIXME: Connect theme changes to update mock UI styling (future PR)
        # FIXME: Link dictionary settings to mock search functionality (future PR)
        # FIXME: Implement settings persistence to JSON/config files (future PR)
        # FIXME: Ensure settings persistence across application restarts (future PR)
        
        # Current: Mock implementation only
        logger.info("Settings applied (mock implementation)")
        self.accept()
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        # Reset theme tab to dark preset
        self.theme_tab._apply_preset("dark")
        
        # Reset general settings
        if ANKI_AVAILABLE:
            self.general_tab.search_delay.setValue(300)
            self.general_tab.max_results.setValue(100)
        self.general_tab.enable_tooltips.setChecked(True)
        self.general_tab.always_on_top.setChecked(False)
        self.general_tab.open_on_startup.setChecked(False)
        
        # Reset dictionaries to defaults
        self.dictionaries_tab._load_dictionaries()
        
        logger.info("Settings reset to defaults")
    
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