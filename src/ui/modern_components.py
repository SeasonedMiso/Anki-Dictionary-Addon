# -*- coding: utf-8 -*-
"""
Modern UI Components for Dictionary Window.

This module provides modern, beautiful UI components following the design
specifications from the modern-ui-redesign spec.
"""

from typing import Optional, List, Dict, Any
import logging
import os

try:
    from aqt.qt import (
        QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLineEdit,
        QPushButton, QLabel, QScrollArea, QSizePolicy, pyqtSignal,
        QTimer, Qt, QFont
    )
    # Check if we're in a test environment
    ANKI_AVAILABLE = os.getenv('PYTEST_CURRENT_TEST') is None
except ImportError:
    # Fallback for testing or if aqt not available
    ANKI_AVAILABLE = False
    QWidget = type('QWidget', (object,), {})
    QFrame = type('QFrame', (object,), {})
    QVBoxLayout = type('QVBoxLayout', (object,), {})
    QHBoxLayout = type('QHBoxLayout', (object,), {})
    QLineEdit = type('QLineEdit', (object,), {})
    QPushButton = type('QPushButton', (object,), {})
    QLabel = type('QLabel', (object,), {})
    QScrollArea = type('QScrollArea', (object,), {})
    QSizePolicy = type('QSizePolicy', (object,), {})
    
    class pyqtSignal:
        def __init__(self, *args):
            pass
    
    class QTimer:
        pass
    
    class Qt:
        AlignLeft = 0
        AlignTop = 0
        AlignCenter = 0
        ScrollBarAsNeeded = 0
        WidgetResizable = 0
        ScrollBarPolicy = type('ScrollBarPolicy', (object,), {
            'ScrollBarAsNeeded': 0
        })
    
    class QFont:
        Bold = 0


logger = logging.getLogger(__name__)


class ModernSearchBar(QWidget):
    """
    Modern search bar component with debounced search.
    
    Features:
    - 50px height with rounded corners (12px)
    - Emoji placeholder (🔍)
    - Debounced search (300ms delay)
    - Focus states with blue border (#4a9eff)
    - Signal-based event handling
    
    Signals:
        searchChanged(str): Emitted when search text changes (after debounce)
    """
    
    searchChanged = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize modern search bar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search for a word or phrase...")
        self.search_input.setMinimumHeight(50)
        self.search_input.textChanged.connect(self._on_text_changed)
        
        # Apply styling
        self._apply_styling()
        
        # Set up debounce timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._emit_search)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.search_input)
        
        logger.debug("ModernSearchBar initialized")
    
    def _apply_styling(self) -> None:
        """Apply modern styling to search input."""
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 20px;
                border: 2px solid #444;
                border-radius: 12px;
                background: #2a2a2a;
                color: white;
                font-size: 16px;
            }
            QLineEdit:focus {
                border: 2px solid #4a9eff;
                background: #333;
            }
            QLineEdit::placeholder {
                color: #888;
            }
        """)
    
    def _on_text_changed(self, text: str) -> None:
        """
        Handle text change with debouncing.
        
        Args:
            text: New text value
        """
        # Restart timer on each text change
        self.search_timer.start(300)  # 300ms debounce
    
    def _emit_search(self) -> None:
        """Emit search signal after debounce period."""
        text = self.search_input.text().strip()
        self.searchChanged.emit(text)
        logger.debug(f"Search emitted: {text}")
    
    def text(self) -> str:
        """
        Get current search text.
        
        Returns:
            Current text in search input
        """
        return self.search_input.text()
    
    def setText(self, text: str) -> None:
        """
        Set search text.
        
        Args:
            text: Text to set
        """
        self.search_input.setText(text)
    
    def clear(self) -> None:
        """Clear search input."""
        self.search_input.clear()


class DefinitionCard(QFrame):
    """
    Modern definition card component.
    
    Features:
    - QFrame with rounded corners (12px) and hover effects
    - Word header (28px bold), phonetic (16px), frequency badge (⭐)
    - Color-coded action buttons (50x50px):
      - 🔊 audio (blue #4a9eff)
      - 🖼️ image (green #50c878)
      - 💾 export (purple #9b59b6)
    - Definition frames with part-of-speech badges
    - Left border accent (4px)
    - First definition highlighted (#1a3a5a)
    
    Signals:
        audioRequested(str): Emitted when audio button clicked
        imageRequested(str): Emitted when image button clicked
        exportRequested(str): Emitted when export button clicked
    """
    
    audioRequested = pyqtSignal(str)
    imageRequested = pyqtSignal(str)
    exportRequested = pyqtSignal(str)
    
    def __init__(
        self,
        word_data: Dict[str, Any],
        parent: Optional[QWidget] = None
    ):
        """
        Initialize definition card.
        
        Args:
            word_data: Dictionary containing word information:
                - word: The word/term
                - phonetic: Phonetic pronunciation (optional)
                - frequency: Frequency ranking (optional)
                - definitions: List of definition dicts with 'type' and 'text'
                - examples: List of example sentences (optional)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.word_data = word_data
        
        # Apply card styling
        self._apply_card_styling()
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Add header section
        header_layout = self._create_header()
        layout.addLayout(header_layout)
        
        # Add action buttons
        actions_layout = self._create_action_buttons()
        layout.addLayout(actions_layout)
        
        # Add definitions
        definitions_widget = self._create_definitions()
        layout.addWidget(definitions_widget)
        
        # Add examples if present
        if word_data.get('examples'):
            examples_widget = self._create_examples()
            layout.addWidget(examples_widget)
        
        logger.debug(f"DefinitionCard created for: {word_data.get('word', 'unknown')}")
    
    def _apply_card_styling(self) -> None:
        """Apply modern card styling with hover effects."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            DefinitionCard {
                background: #2a2a2a;
                border: 1px solid #444;
                border-radius: 12px;
            }
            DefinitionCard:hover {
                border: 1px solid #555;
                background: #2d2d2d;
            }
        """)
    
    def _create_header(self) -> QHBoxLayout:
        """
        Create header section with word, phonetic, and frequency.
        
        Returns:
            Layout containing header elements
        """
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # Word label (28px bold)
        word_label = QLabel(self.word_data.get('word', ''))
        word_font = QFont()
        word_font.setPointSize(28)
        word_font.setBold(True)
        word_label.setFont(word_font)
        word_label.setStyleSheet("color: white;")
        layout.addWidget(word_label)
        
        # Phonetic label (16px gray)
        phonetic = self.word_data.get('phonetic', '')
        if phonetic:
            phonetic_label = QLabel(phonetic)
            phonetic_font = QFont()
            phonetic_font.setPointSize(16)
            phonetic_label.setFont(phonetic_font)
            phonetic_label.setStyleSheet("color: #888;")
            layout.addWidget(phonetic_label)
        
        layout.addStretch()
        
        # Frequency badge (⭐ emoji)
        frequency = self.word_data.get('frequency', 'N/A')
        freq_label = QLabel(f"⭐ {frequency}")
        freq_font = QFont()
        freq_font.setPointSize(14)
        freq_label.setFont(freq_font)
        freq_label.setStyleSheet("color: #ffd700;")
        layout.addWidget(freq_label)
        
        return layout
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """
        Create color-coded action buttons.
        
        Returns:
            Layout containing action buttons
        """
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        word = self.word_data.get('word', '')
        
        # Audio button (blue #4a9eff) - using clean Unicode
        audio_btn = QPushButton("♪")  # Musical note
        audio_btn.setMinimumSize(50, 50)
        audio_btn.setMaximumSize(50, 50)
        audio_btn.setStyleSheet("""
            QPushButton {
                background: #4a9eff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
            }
            QPushButton:hover {
                background: #3a8edf;
            }
            QPushButton:pressed {
                background: #2a7ecf;
            }
        """)
        audio_btn.clicked.connect(lambda: self.audioRequested.emit(word))
        layout.addWidget(audio_btn)
        
        # Image button (green #50c878) - using clean Unicode
        image_btn = QPushButton("◈")  # Diamond with dot
        image_btn.setMinimumSize(50, 50)
        image_btn.setMaximumSize(50, 50)
        image_btn.setStyleSheet("""
            QPushButton {
                background: #50c878;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
            }
            QPushButton:hover {
                background: #40b868;
            }
            QPushButton:pressed {
                background: #30a858;
            }
        """)
        image_btn.clicked.connect(lambda: self.imageRequested.emit(word))
        layout.addWidget(image_btn)
        
        # Export button (purple #9b59b6) - using clean Unicode
        export_btn = QPushButton("⊕")  # Circled plus
        export_btn.setMinimumSize(50, 50)
        export_btn.setMaximumSize(50, 50)
        export_btn.setStyleSheet("""
            QPushButton {
                background: #9b59b6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
            }
            QPushButton:hover {
                background: #8b49a6;
            }
            QPushButton:pressed {
                background: #7b3996;
            }
        """)
        export_btn.clicked.connect(lambda: self.exportRequested.emit(word))
        layout.addWidget(export_btn)
        
        layout.addStretch()
        
        return layout
    
    def _create_definitions(self) -> QWidget:
        """
        Create definitions section with badges and highlighting.
        
        Returns:
            Widget containing all definitions
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        definitions = self.word_data.get('definitions', [])
        
        for i, definition in enumerate(definitions):
            def_frame = self._create_definition_frame(definition, is_first=(i == 0))
            layout.addWidget(def_frame)
        
        return container
    
    def _create_definition_frame(
        self,
        definition: Dict[str, str],
        is_first: bool = False
    ) -> QFrame:
        """
        Create a single definition frame.
        
        Args:
            definition: Definition dict with 'type' and 'text'
            is_first: Whether this is the first definition (highlighted)
            
        Returns:
            Frame containing the definition
        """
        frame = QFrame()
        
        # Apply styling with conditional highlighting
        bg_color = '#1a3a5a' if is_first else '#222'
        border_color = '#4a9eff' if is_first else '#555'
        
        frame.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border-left: 4px solid {border_color};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Part of speech badge
        pos_type = definition.get('type', 'noun')
        pos_label = QLabel(pos_type)
        pos_label.setStyleSheet("""
            QLabel {
                background: #4a9eff;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
        """)
        pos_label.setMaximumWidth(100)
        layout.addWidget(pos_label)
        
        # Definition text
        def_text = definition.get('text', '')
        def_label = QLabel(def_text)
        def_label.setWordWrap(True)
        def_label.setStyleSheet("color: white; font-size: 14px; line-height: 1.6;")
        layout.addWidget(def_label)
        
        return frame
    
    def _create_examples(self) -> QWidget:
        """
        Create examples section.
        
        Returns:
            Widget containing example sentences
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Examples header
        header = QLabel("Examples:")
        header.setStyleSheet("color: #aaa; font-size: 12px; font-weight: bold;")
        layout.addWidget(header)
        
        # Example sentences
        examples = self.word_data.get('examples', [])
        for example in examples:
            example_label = QLabel(f"• {example}")
            example_label.setWordWrap(True)
            example_label.setStyleSheet("""
                color: #ccc;
                font-size: 13px;
                font-style: italic;
                background: #1a1a1a;
                padding: 8px;
                border-radius: 4px;
            """)
            layout.addWidget(example_label)
        
        return container


class DictionaryFilterBar(QWidget):
    """
    Modern dictionary filter bar with checkable buttons.
    
    Features:
    - Horizontal layout with checkable QPushButtons
    - Mutual exclusion (only one active at a time)
    - Active state: blue background (#4a9eff)
    - Inactive state: dark gray (#2a2a2a)
    - 40px minimum height for touch targets
    - Hover states for visual feedback
    
    Signals:
        filterChanged(str): Emitted when filter selection changes
    """
    
    filterChanged = pyqtSignal(str)
    
    def __init__(
        self,
        dictionaries: Optional[List[tuple]] = None,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize dictionary filter bar.
        
        Args:
            dictionaries: List of (name, id) tuples for dictionaries
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Default dictionaries if none provided
        if dictionaries is None:
            dictionaries = [
                ("All Dictionaries", "all"),
                ("Webster's", "webster"),
                ("JMDict (JP)", "jmdict"),
                ("CC-CEDICT (CN)", "cedict")
            ]
        
        self.dictionaries = dictionaries
        self.buttons: List[QPushButton] = []
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Create buttons
        for name, dict_id in dictionaries:
            btn = self._create_filter_button(name, dict_id)
            self.buttons.append(btn)
            layout.addWidget(btn)
        
        # Set first button as checked by default
        if self.buttons:
            self.buttons[0].setChecked(True)
        
        layout.addStretch()
        
        logger.debug(f"DictionaryFilterBar initialized with {len(dictionaries)} filters")
    
    def _create_filter_button(self, name: str, dict_id: str) -> QPushButton:
        """
        Create a single filter button.
        
        Args:
            name: Display name
            dict_id: Dictionary identifier
            
        Returns:
            Configured QPushButton
        """
        btn = QPushButton(name)
        btn.setCheckable(True)
        btn.setMinimumHeight(40)
        btn.setProperty('dict_id', dict_id)
        
        # Apply styling
        btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border: 2px solid #444;
                border-radius: 8px;
                background: #2a2a2a;
                color: #aaa;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:checked {
                background: #4a9eff;
                color: white;
                border: 2px solid #4a9eff;
            }
            QPushButton:hover {
                background: #333;
            }
            QPushButton:checked:hover {
                background: #3a8edf;
            }
        """)
        
        # Connect click handler
        btn.clicked.connect(lambda: self._on_filter_click(dict_id))
        
        return btn
    
    def _on_filter_click(self, dict_id: str) -> None:
        """
        Handle filter button click with mutual exclusion.
        
        Args:
            dict_id: ID of clicked dictionary
        """
        # Uncheck all other buttons (mutual exclusion)
        for btn in self.buttons:
            if btn.property('dict_id') != dict_id:
                btn.setChecked(False)
        
        # Emit signal
        self.filterChanged.emit(dict_id)
        logger.debug(f"Filter changed to: {dict_id}")
    
    def get_selected_filter(self) -> Optional[str]:
        """
        Get currently selected filter ID.
        
        Returns:
            Selected dictionary ID or None
        """
        for btn in self.buttons:
            if btn.isChecked():
                return btn.property('dict_id')
        return None
    
    def set_selected_filter(self, dict_id: str) -> None:
        """
        Set selected filter by ID.
        
        Args:
            dict_id: Dictionary ID to select
        """
        for btn in self.buttons:
            btn.setChecked(btn.property('dict_id') == dict_id)


class ModernResultsArea(QScrollArea):
    """
    Modern scrollable results area for definition cards.
    
    Features:
    - QScrollArea with proper styling
    - Vertical layout for definition cards
    - Smooth scrolling
    - Dark theme styling
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize modern results area.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Configure scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Apply styling
        self.setStyleSheet("""
            QScrollArea {
                background: #1a1a1a;
                border: none;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #4a4a4a;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5a5a5a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create container widget
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(15)
        self.layout.addStretch()
        
        self.setWidget(self.container)
        
        logger.debug("ModernResultsArea initialized")
    
    def add_card(self, card: DefinitionCard) -> None:
        """
        Add a definition card to the results area.
        
        Args:
            card: DefinitionCard to add
        """
        # Insert before the stretch
        self.layout.insertWidget(self.layout.count() - 1, card)
    
    def clear_cards(self) -> None:
        """Clear all definition cards from the results area."""
        # Remove all widgets except the stretch
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def get_card_count(self) -> int:
        """
        Get number of cards in results area.
        
        Returns:
            Number of definition cards
        """
        # Subtract 1 for the stretch item
        return max(0, self.layout.count() - 1)
