# -*- coding: utf-8 -*-
"""
Dictionary Application Widgets.

This module provides dictionary-specific UI components that compose together
to create the dictionary lookup interface. These widgets are built using
the base themed widgets and implement dictionary-specific functionality.

WIDGETS PROVIDED:

Layout Widgets:
- CollapsibleBox: Expandable/collapsible container with arrow indicator
- ModernResultsArea: Scrollable area for displaying search results

Search Widgets:
- ModernSearchBar: Search input with button and debounced text changes
- DictionaryFilterBar: Dictionary selection and search mode controls

Content Widgets:
- DefinitionCard: Complete word definition with actions (audio, image, copy, export)
- WordSection: Section for a single word with multiple dictionary sources
- DictionarySubsection: Individual dictionary's definition within a word section

All widgets use the centralized theming system and base widgets for consistency.
"""

from typing import Optional, List, Dict, Any
import logging
import os

try:
    from aqt.qt import (
        QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLineEdit,
        QPushButton, QLabel, QScrollArea, QSizePolicy, pyqtSignal,
        QTimer, Qt, QFont, QPropertyAnimation, QEasingCurve, QComboBox
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

from .styling import ThemeColors, StyleGenerator, get_theme_manager
from .base_widgets import (
    ThemedWidget, ThemedButton, ThemedLabel, ActionButton
)

logger = logging.getLogger(__name__)


def _adjust_color_brightness(hex_color: str, factor: float) -> str:
    """
    Adjust the brightness of a hex color.
    
    Args:
        hex_color: Hex color string (e.g., "#1c1c1c")
        factor: Brightness factor (>1 = brighter, <1 = darker)
        
    Returns:
        Adjusted hex color string
    """
    try:
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Adjust brightness
        r = min(255, max(0, int(r * factor)))
        g = min(255, max(0, int(g * factor)))
        b = min(255, max(0, int(b * factor)))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, IndexError):
        # Return original color if parsing fails
        return hex_color


# =============================================================================
# LAYOUT COMPONENTS
# =============================================================================

class CollapsibleBox(ThemedWidget):
    """
    Collapsible container with expand/collapse arrow.
    
    Features:
    - Click header to toggle collapse/expand
    - Smooth animation
    - Arrow rotates (▼ expanded, ▶ collapsed)
    - Customizable title and styling
    """
    
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        """
        Initialize collapsible box.
        
        Args:
            title: Header title text
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.is_expanded = True
        self.content_widget = None
        self.title = title
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header container with title and optional widgets
        self.header_container = QWidget()
        self.header_layout = QHBoxLayout(self.header_container)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(8)
        
        # Header title (clickable)
        self.header = QPushButton()
        self.header.setText(f"▼ {title}")
        self.header.clicked.connect(self.toggle)
        self.header_layout.addWidget(self.header, 1)  # Stretch to fill space
        
        layout.addWidget(self.header_container)
        
        # Content container
        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_layout.setSpacing(12)
        
        layout.addWidget(self.content_frame)
        
        # Animation
        if ANKI_AVAILABLE:
            self.animation = QPropertyAnimation(self.content_frame, b"maximumHeight")
            self.animation.setDuration(200)
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Apply initial styling
        self._apply_styling()
    
    def add_content(self, widget: QWidget) -> None:
        """Add widget to collapsible content area."""
        self.content_layout.addWidget(widget)
        self.content_widget = widget
    
    def add_header_widget(self, widget: QWidget) -> None:
        """Add widget to header (right side)."""
        self.header_layout.addWidget(widget)
    
    def toggle(self) -> None:
        """Toggle expanded/collapsed state with animation."""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()
    
    def collapse(self) -> None:
        """Collapse the content area."""
        if not self.is_expanded:
            return
            
        self.is_expanded = False
        
        # Update arrow
        title = self.header.text()[2:]  # Remove arrow
        self.header.setText(f"▶ {title}")
        
        # Animate collapse
        self.animation.setStartValue(self.content_frame.height())
        self.animation.setEndValue(0)
        self.animation.finished.connect(lambda: self.content_frame.hide())
        self.animation.start()
    
    def expand(self) -> None:
        """Expand the content area."""
        if self.is_expanded:
            return
            
        self.is_expanded = True
        
        # Update arrow
        title = self.header.text()[2:]  # Remove arrow
        self.header.setText(f"▼ {title}")
        
        # Show content frame
        self.content_frame.show()
        
        # Force layout update to get proper size
        self.content_frame.updateGeometry()
        
        # Calculate target height based on content
        content_height = 0
        for i in range(self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item and item.widget():
                content_height += item.widget().sizeHint().height()
        
        # Add margins and spacing
        target_height = content_height + 32 + (self.content_layout.count() - 1) * 12
        target_height = max(target_height, 50)  # Minimum height
        
        # Set up animation
        self.content_frame.setMaximumHeight(0)
        self.animation.setStartValue(0)
        self.animation.setEndValue(target_height)
        
        # Clear any previous connections and add completion handler
        try:
            self.animation.finished.disconnect()
        except:
            pass
        
        self.animation.finished.connect(lambda: self.content_frame.setMaximumHeight(16777215))  # Remove height limit
        self.animation.start()
    
    def _apply_styling(self):
        """Apply styling using centralized theme system."""
        if not ANKI_AVAILABLE:
            return
        
        theme = self.theme_manager.current_theme
        
        # Header button styling - no border, transparent background
        header_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.text_primary};
                border: none;
                padding: 12px 16px;
                text-align: left;
                font-size: {theme.get_font_size('base')}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {self.style_generator.adjust_color_brightness(theme.background_color, 1.05)};
            }}
        """
        self.header.setStyleSheet(header_style)
        
        # Content frame styling - border around content only, panel background
        content_style = f"""
            QFrame {{
                background-color: {theme.panel_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                padding: 0px;
                margin: 0px;
            }}
        """
        self.content_frame.setStyleSheet(content_style)
    
    def update_theme(self, theme: ThemeColors) -> None:
        """Update component styling with new theme."""
        self._apply_styling()


# =============================================================================
# SEARCH COMPONENTS  
# =============================================================================

class ModernSearchBar(ThemedWidget):
    """
    Modern search bar component with search button.
    
    Features:
    - 50px height with rounded corners
    - Clean placeholder text (no emoji)
    - Search button on the right
    - Debounced search (300ms delay)
    - Enter key support
    
    Signals:
        searchChanged(str): Emitted when search text changes (after debounce)
        searchRequested(str): Emitted when search button clicked or Enter pressed
    """
    
    searchChanged = pyqtSignal(str)
    searchRequested = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize modern search bar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Create search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for a word or phrase...")
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.returnPressed.connect(self._on_search_requested)
        
        # Create search button
        self.search_button = QPushButton("⌕")
        self.search_button.setMinimumHeight(36)
        self.search_button.setMinimumWidth(60)
        self.search_button.clicked.connect(self._on_search_requested)
        
        # Set up debounce timer
        if ANKI_AVAILABLE:
            self.search_timer = QTimer()
            self.search_timer.setSingleShot(True)
            self.search_timer.timeout.connect(self._emit_search)
        
        # Layout - with spacing for separate appearance
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)  # Space between search bar and button
        layout.addWidget(self.search_input, 1)  # Stretch to fill
        layout.addWidget(self.search_button)
        
        # Apply initial styling
        self._apply_styling()
        
        logger.debug("ModernSearchBar initialized")
    
    def _apply_styling(self) -> None:
        """Apply modern styling to search components."""
        if not ANKI_AVAILABLE:
            return
        
        # Search input styling
        input_style = self.style_generator.input_style(
            padding="6px 12px",
            size_type="small"
        )
        # Override border radius for search bar
        input_style = input_style.replace(
            f"border-radius: {self.style_generator.theme.border_radius}px",
            "border-radius: 12px"
        )
        self.search_input.setStyleSheet(input_style)
        
        # Search button styling - custom to match search bar height
        theme = self.style_generator.theme
        button_style = f"""
            QPushButton {{
                background-color: {theme.accent_color};
                color: white;
                border: 1px solid {theme.border_color};
                border-radius: 12px;
                padding: 0px 16px;
                font-size: {theme.get_font_size('large')}px;
                font-weight: bold;
                min-width: 60px;
            }}
            QPushButton:hover {{
                background-color: {self.style_generator.adjust_color_brightness(theme.accent_color, 1.2)};
            }}
            QPushButton:pressed {{
                background-color: {self.style_generator.adjust_color_brightness(theme.accent_color, 0.8)};
            }}
        """
        self.search_button.setStyleSheet(button_style)
    
    def _on_text_changed(self, text: str) -> None:
        """
        Handle text change with debouncing.
        
        Args:
            text: New text value
        """
        # Restart timer on each text change
        if ANKI_AVAILABLE:
            self.search_timer.start(300)  # 300ms debounce
    
    def _emit_search(self) -> None:
        """Emit search signal after debounce period."""
        text = self.search_input.text().strip()
        self.searchChanged.emit(text)
        logger.debug(f"Search emitted: {text}")
    
    def _on_search_requested(self) -> None:
        """Handle explicit search request (button click or Enter)."""
        text = self.search_input.text().strip()
        self.searchRequested.emit(text)
        logger.debug(f"Search requested: {text}")
    
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
    
    def update_theme(self, theme: ThemeColors) -> None:
        """
        Update component styling with new theme.
        
        Args:
            theme: New theme colors
        """
        self._apply_styling()
        logger.debug("Updated ModernSearchBar theme")


# =============================================================================
# CARD COMPONENTS
# =============================================================================

class DefinitionCard(QWidget):
    """
    Collapsible definition card component.
    
    Features:
    - Collapsible box with word as title
    - Word header, phonetic, frequency badge
    - Action buttons (audio, image, clipboard, export)
    - Inline definitions with part-of-speech badges
    - Example sentences
    - Click header to collapse/expand
    
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
        
        # Create collapsible box with word as title (with pitch accent coloring)
        word = word_data.get('word', 'Unknown')
        phonetic = word_data.get('phonetic', '')
        pitch_accent = word_data.get('pitch_accent', '')
        
        # Build title with pitch accent notation
        if phonetic and pitch_accent:
            title = f"{word}({phonetic})[{pitch_accent}]"
        elif phonetic:
            title = f"{word}({phonetic})"
        else:
            title = word
        
        self.collapsible_box = CollapsibleBox(title, self)
        
        # Apply pitch accent color and click handler if available
        if pitch_accent:
            pitch_color = self._get_pitch_color(pitch_accent)
            # Update header styling to include pitch accent color
            current_style = self.collapsible_box.header.styleSheet()
            new_style = current_style.replace(
                "color: white;", 
                f"color: white; border-left: 4px solid {pitch_color};"
            )
            self.collapsible_box.header.setStyleSheet(new_style)
            
            # Add right-click handler for pitch graph
            def show_pitch_on_right_click(event):
                if event.button() == Qt.MouseButton.RightButton:
                    self._show_pitch_graph()
                else:
                    # Call original toggle function
                    self.collapsible_box.toggle()
            
            # Override the click handler
            self.collapsible_box.header.mousePressEvent = show_pitch_on_right_click
        
        # Create content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        
        # Add action buttons
        actions_layout = self._create_action_buttons()
        content_layout.addLayout(actions_layout)
        
        # Add definitions
        definitions_widget = self._create_definitions()
        content_layout.addWidget(definitions_widget)
        
        # Add examples if present
        if word_data.get('examples'):
            examples_widget = self._create_examples()
            content_layout.addWidget(examples_widget)
        
        # Add frequency button to header (right side)
        frequencies = word_data.get('frequencies', {})
        if not frequencies and word_data.get('frequency'):
            frequencies = {'General': word_data.get('frequency')}
        
        if frequencies:
            # Calculate average frequency
            avg_freq = sum(frequencies.values()) / len(frequencies)
            freq_text, freq_color = self._get_frequency_label(int(avg_freq))
            
            freq_button = QPushButton(freq_text)
            freq_button.setMinimumHeight(28)
            freq_button.setStyleSheet(f"""
                QPushButton {{
                    background: {freq_color};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
            """)
            freq_button.clicked.connect(lambda: self._show_frequency_breakdown(frequencies))
            self.collapsible_box.add_header_widget(freq_button)
        
        # Add content to collapsible box
        self.collapsible_box.add_content(content_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 8)
        main_layout.addWidget(self.collapsible_box)
        
        logger.debug(f"DefinitionCard created for: {word_data.get('word', 'unknown')}")
    

    

    
    def _get_frequency_label(self, frequency: int) -> tuple[str, str]:
        """
        Convert frequency rank to human-readable label using themed colors.
        
        Args:
            frequency: Frequency ranking (lower = more common)
            
        Returns:
            Tuple of (label_text, color_hex)
        """
        theme = get_theme_manager().current_theme
        
        if frequency <= 500:
            return ("Very Common", theme.freq_very_common)
        elif frequency <= 1500:
            return ("Common", theme.freq_common)
        elif frequency <= 5000:
            return ("Uncommon", theme.freq_uncommon)
        elif frequency <= 15000:
            return ("Rare", theme.freq_rare)
        else:
            return ("Very Rare", theme.freq_very_rare)
    
    def _get_pitch_color(self, pitch_accent: str) -> str:
        """
        Get color for pitch accent pattern using themed colors.
        
        Args:
            pitch_accent: Pitch accent number (0, 1, 2, etc.)
            
        Returns:
            Color hex code from theme
        """
        theme = get_theme_manager().current_theme
        
        try:
            accent_num = int(pitch_accent)
            if accent_num == 0:
                return theme.heiban_color  # Blue - Heiban (flat)
            elif accent_num == 1:
                return theme.atamadaka_color  # Red - Atamadaka (head-high)
            else:
                return theme.nakadaka_color  # Orange/Yellow - Nakadaka (mid-high)
        except (ValueError, TypeError):
            # Handle special patterns
            if pitch_accent.lower() in ['odaka', 'tail-high']:
                return theme.odaka_color  # Green - Odaka (tail-high)
            elif pitch_accent.lower() in ['kifuku', 'rising-falling']:
                return theme.kifuku_color  # Purple - Kifuku (rising-falling)
            else:
                return theme.text_muted  # Gray - Unknown
    
    def _show_frequency_breakdown(self, frequencies: dict) -> None:
        """Show detailed frequency breakdown for all sources."""
        from aqt.utils import showInfo
        
        # Calculate average
        avg_freq = sum(frequencies.values()) / len(frequencies)
        avg_text, _ = self._get_frequency_label(int(avg_freq))
        
        # Build breakdown message
        breakdown_lines = [f"Overall: {avg_text} (avg: {int(avg_freq):,})", ""]
        
        for freq_name, freq_value in frequencies.items():
            freq_text, _ = self._get_frequency_label(freq_value)
            breakdown_lines.append(f"{freq_name}: {freq_value:,} ({freq_text})")
        
        breakdown_lines.append("")
        breakdown_lines.append("(Lower rank = more common)")
        
        message = "\n".join(breakdown_lines)
        showInfo(message, title="Frequency Breakdown")
    
    def _show_pitch_graph(self) -> None:
        """Show pitch accent graph - TODO: Generate actual image."""
        from aqt.utils import showInfo
        
        word = self.word_data.get('word', '')
        pitch = self.word_data.get('pitch_accent', '')
        
        message = f"Pitch Accent Graph for {word}[{pitch}]\n\nTODO: Generate visual pitch accent graph\n\nPlanned features:\n• Visual mora diagram\n• Audio waveform overlay\n• Interactive pitch curve\n• Export as image"
        showInfo(message, title="Pitch Accent Graph (Coming Soon)")
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """
        Create action buttons - full width with equal spacing.
        
        Returns:
            Layout containing action buttons
        """
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        word = self.word_data.get('word', '')
        
        # Audio button (blue)
        audio_btn = ActionButton("Audio", "audio", lambda: self.audioRequested.emit(word), compact=True)
        audio_btn.setToolTip("Play audio pronunciation")
        layout.addWidget(audio_btn, 1)  # Equal stretch
        
        # Image button (green)
        image_btn = ActionButton("Images", "image", lambda: self.imageRequested.emit(word), compact=True)
        image_btn.setToolTip("Search images")
        layout.addWidget(image_btn, 1)  # Equal stretch
        
        # Copy to clipboard button
        copy_btn = ActionButton("Copy", "copy", lambda: self._copy_to_clipboard(copy_btn), compact=True)
        copy_btn.setToolTip("Copy definition to clipboard")
        layout.addWidget(copy_btn, 1)  # Equal stretch
        
        # Export to Anki button (purple)
        export_btn = ActionButton("Export", "export", lambda: self.exportRequested.emit(word), compact=True)
        export_btn.setToolTip("Add to card exporter")
        layout.addWidget(export_btn, 1)  # Equal stretch
        
        return layout
    
    def _copy_to_clipboard(self, button) -> None:
        """Copy definition text to clipboard with visual feedback."""
        from aqt.qt import QApplication
        
        try:
            # Collect all definition text
            definitions = self.word_data.get('definitions', [])
            examples = self.word_data.get('examples', [])
            
            # Format: 勉強[べんきょう]
            text_parts = [self.word_data.get('word', '')]
            phonetic = self.word_data.get('phonetic', '')
            if phonetic:
                text_parts[0] += f"[{phonetic}]"
            
            # Add definitions
            for i, defn in enumerate(definitions, 1):
                def_type = defn.get('type', '')
                def_text = defn.get('text', '')
                text_parts.append(f"{i}. ({def_type}) {def_text}")
            
            # Add examples if present
            if examples:
                text_parts.append("")  # Empty line
                text_parts.append("Examples:")
                for example in examples:
                    text_parts.append(f"• {example}")
            
            clipboard_text = '\n'.join(text_parts)
            if ANKI_AVAILABLE:
                QApplication.clipboard().setText(clipboard_text)
            
            # Use ActionButton's built-in feedback
            if hasattr(button, 'show_feedback'):
                button.show_feedback(success=True)
            
            logger.debug(f"Copied to clipboard: {clipboard_text[:50]}...")
        except Exception as e:
            # Show error feedback
            if hasattr(button, 'show_feedback'):
                button.show_feedback(success=False)
            logger.error(f"Failed to copy to clipboard: {e}")
    
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
    ) -> QWidget:
        """
        Create a single definition line (flat, no nested boxes).
        
        Args:
            definition: Definition dict with 'type' and 'text'
            is_first: Whether this is the first definition (highlighted)
            
        Returns:
            Widget containing the definition
        """
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)
        
        # Part of speech badge (inline, small)
        pos_type = definition.get('type', 'noun')
        pos_label = ThemedLabel(pos_type)
        
        # Apply themed styling for part-of-speech badge
        theme = get_theme_manager().current_theme
        style_gen = StyleGenerator(theme)
        
        badge_color = theme.accent_color if is_first else theme.text_muted
        pos_style = f"""
            QLabel {{
                background: {badge_color};
                color: white;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: {theme.get_font_size('small')}px;
                font-weight: bold;
            }}
        """
        pos_label.setStyleSheet(pos_style)
        pos_label.setFixedHeight(22)
        layout.addWidget(pos_label)
        
        # Definition text (inline, no box, selectable)
        def_text = definition.get('text', '')
        def_label = ThemedLabel(def_text)
        def_label.setWordWrap(True)
        def_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # Apply themed styling for definition text
        text_color = theme.text_primary if is_first else theme.text_muted
        def_style = f"""
            QLabel {{
                color: {text_color};
                font-size: {theme.get_font_size('base')}px;
                line-height: 1.5;
                font-weight: {'600' if is_first else 'normal'};
            }}
        """
        def_label.setStyleSheet(def_style)
        layout.addWidget(def_label, 1)  # Stretch to fill space
        
        return container
    
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
        header = ThemedLabel("Examples:", "muted")
        header.setStyleSheet(f"font-weight: bold; font-size: {get_theme_manager().current_theme.get_font_size('small')}px;")
        layout.addWidget(header)
        
        # Example sentences
        examples = self.word_data.get('examples', [])
        for example in examples:
            example_label = ThemedLabel(f"• {example}")
            example_label.setWordWrap(True)
            example_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            
            # Apply themed styling for examples
            theme = get_theme_manager().current_theme
            example_style = f"""
                QLabel {{
                    color: {theme.text_muted};
                    font-size: {theme.get_font_size('small')}px;
                    font-style: italic;
                    background: {theme.panel_color};
                    padding: 8px;
                    border-radius: 4px;
                }}
            """
            example_label.setStyleSheet(example_style)
            layout.addWidget(example_label)
        
        return container


class WordCollapsibleBox(QFrame):
    """
    Word container with header INSIDE the bordered box and colored pitch accent border.
    
    CRITICAL FIXES:
    1. Header is INSIDE the bordered container (not outside)
    2. Colored left border for pitch accent
    3. Dictionary content boxes have visible borders
    4. Example items have NO borders
    """
    
    def __init__(self, word_text: str, pitch_accent: str = '', parent: Optional[QWidget] = None):
        """Initialize word collapsible box with header INSIDE."""
        super().__init__(parent)
        
        self.word_text = word_text
        self.pitch_accent_type = pitch_accent
        self.is_expanded = True
        
        # Get theme manager and register as observer
        self.theme_manager = get_theme_manager()
        self.style_generator = StyleGenerator(self.theme_manager.current_theme)
        self.theme_manager.register_observer(self._on_theme_changed)
        
        # Main layout for THIS widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header container with layout for title + buttons
        self.header_container = QWidget()
        self.header_layout = QHBoxLayout(self.header_container)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(8)
        
        # Header title button (clickable)
        self.header_button = QPushButton(f"▼ {word_text}")
        self.header_button.clicked.connect(self.toggle)
        self.header_layout.addWidget(self.header_button, 1)  # Stretch to fill
        
        self.main_layout.addWidget(self.header_container)
        
        # Content area goes INSIDE this widget
        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_layout.setSpacing(12)
        self.main_layout.addWidget(self.content_frame)  # ← Inside!
        
        # Apply styling
        self._apply_styling()
    
    def add_content(self, widget: QWidget) -> None:
        """Add widget to content area."""
        self.content_layout.addWidget(widget)
    
    def add_header_widget(self, widget: QWidget) -> None:
        """Add widget to header right side."""
        self.header_layout.addWidget(widget, 0)  # Don't stretch
    
    def toggle(self) -> None:
        """Toggle expanded/collapsed state."""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()
    
    def collapse(self) -> None:
        """Collapse content area."""
        if not self.is_expanded:
            return
        self.is_expanded = False
        self.header_button.setText(f"▶ {self.word_text}")
        self.content_frame.hide()
    
    def expand(self) -> None:
        """Expand content area."""
        if self.is_expanded:
            return
        self.is_expanded = True
        self.header_button.setText(f"▼ {self.word_text}")
        self.content_frame.show()
    
    def _on_theme_changed(self, new_theme: ThemeColors):
        """Handle theme changes from theme manager."""
        self.style_generator = StyleGenerator(new_theme)
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling with colored pitch accent border using current theme."""
        theme = self.theme_manager.current_theme
        
        # Get pitch accent color from theme - Fixed for verbs
        pitch_colors = {
            '0': theme.heiban_color,      # heiban - blue
            '1': theme.atamadaka_color,   # atamadaka - red  
            '2': theme.kifuku_color,      # kifuku - purple (for verbs like taberu)
            '3': theme.nakadaka_color,    # nakadaka - orange
            'odaka': theme.odaka_color,   # odaka - green
            'kifuku': theme.kifuku_color  # kifuku - purple
        }
        pitch_color = pitch_colors.get(self.pitch_accent_type, theme.heiban_color)
        
        # DIAGNOSTIC
        logger.debug(f"[WordCollapsibleBox] Applying pitch accent styling:")
        logger.debug(f"  - pitch_accent_type: {self.pitch_accent_type}")
        logger.debug(f"  - pitch_color: {pitch_color}")
        logger.debug(f"  - theme.panel_color: {theme.panel_color}")
        
        # Apply to SELF (QFrame) - entire container uses panel color with colored left border
        self.setObjectName("WordCollapsibleBox")
        self.setStyleSheet(f"""
            QFrame#WordCollapsibleBox {{
                background-color: {theme.panel_color};
                border: 1px solid {theme.border_color};
                border-left: 5px solid {pitch_color} !important;
                border-radius: {theme.border_radius}px;
                margin: 0px;
                padding: 0px;
            }}
        """)
        
        # Header container styling - transparent
        self.header_container.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }}
        """)
        
        # Header button styling - no border, transparent bg, part of panel
        hover_bg = self.style_generator.adjust_color_brightness(theme.panel_color, 1.1)
        self.header_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.text_primary};
                border: none;
                padding: 14px 16px;
                text-align: left;
                font-size: {theme.get_font_size('base')}px;
                font-weight: 600;
                margin: 0px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
        """)
        
        # Content frame - use panel color to match container
        self.content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {theme.panel_color};
                border: none;
                margin: 0px;
                padding: 0px;
            }}
        """)
    
    def closeEvent(self, event):
        """Clean up theme observer on close."""
        if hasattr(self, 'theme_manager'):
            self.theme_manager.unregister_observer(self._on_theme_changed)
        super().closeEvent(event)


class WordSection(QWidget):
    """
    Section for a single word with multiple dictionary definitions.
    
    FIXED STRUCTURE:
    - WordCollapsibleBox with header INSIDE the bordered container
    - Colored left border for pitch accent
    - Dictionary content boxes with visible borders
    - Example items with NO borders
    """
    
    audioRequested = pyqtSignal(str)
    imageRequested = pyqtSignal(str)
    exportRequested = pyqtSignal(str)
    
    def __init__(self, word_data: Dict[str, Any], parent: Optional[QWidget] = None):
        """Initialize word section with FIXED hierarchy."""
        super().__init__(parent)
        
        self.word_data = word_data
        self.dictionary_sections = []
        
        # Get theme manager and register observer
        self.theme_manager = get_theme_manager()
        self.theme_manager.register_observer(self._on_theme_changed)
        
        # Create word header with improved display
        word = word_data.get('word', 'Unknown')
        phonetic = word_data.get('phonetic', '')
        pitch_accent = word_data.get('pitch_accent', '')
        verb_type = word_data.get('verb_type', '')  # godan/ichidan
        
        # Build better title with furigana-style display and verb type
        title_parts = [word]
        if phonetic:
            title_parts.append(f"[{phonetic}]")
        if pitch_accent:
            title_parts.append(f"({pitch_accent})")
        if verb_type:
            verb_display = "u-verb" if verb_type == "godan" else "iru/eru-verb" if verb_type == "ichidan" else verb_type
            title_parts.append(f"<{verb_display}>")
        
        title = "".join(title_parts)
        
        # Use NEW WordCollapsibleBox with header INSIDE
        self.collapsible_box = WordCollapsibleBox(title, pitch_accent, self)
        
        # Add frequency and audio/image buttons to header
        self._add_word_controls()
        
        # Content container for dictionary sections
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        self.collapsible_box.add_content(self.content_widget)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 12)
        main_layout.addWidget(self.collapsible_box)
    
    def _get_pitch_color(self, pitch_accent: str) -> str:
        """Get color for pitch accent pattern using themed colors."""
        theme = get_theme_manager().current_theme
        
        try:
            accent_num = int(pitch_accent)
            if accent_num == 0:
                return theme.heiban_color  # Blue - Heiban
            elif accent_num == 1:
                return theme.atamadaka_color  # Red - Atamadaka
            else:
                return theme.nakadaka_color  # Orange - Nakadaka
        except (ValueError, TypeError):
            return theme.text_muted  # Gray - Unknown
    
    def _add_word_controls(self) -> None:
        """Add frequency badge and audio/image buttons to word header."""
        # Frequency button
        frequencies = self.word_data.get('frequencies', {})
        if frequencies:
            avg_freq = sum(frequencies.values()) / len(frequencies)
            freq_text, freq_color = self._get_frequency_label(int(avg_freq))
            
            freq_button = QPushButton(freq_text)
            freq_button.setMinimumHeight(24)  # Smaller height
            freq_button.setMinimumWidth(70)  # Minimum width (allows expansion)
            freq_button.setStyleSheet(f"""
                QPushButton {{
                    background: {freq_color};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 2px 8px;
                    font-size: 9px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ opacity: 0.8; }}
            """)
            freq_button.clicked.connect(lambda: self._show_frequency_breakdown(frequencies))
            self.collapsible_box.add_header_widget(freq_button)
        
        # Audio button - COMPACT version
        audio_btn = ActionButton("", "audio", 
                                lambda: self.audioRequested.emit(self.word_data.get('word', '')),
                                compact=True)
        audio_btn.setToolTip("Play audio pronunciation")
        self.collapsible_box.add_header_widget(audio_btn)
        
        # Image button - COMPACT version
        image_btn = ActionButton("", "image", 
                               lambda: self.imageRequested.emit(self.word_data.get('word', '')),
                               compact=True)
        image_btn.setToolTip("Search images")
        self.collapsible_box.add_header_widget(image_btn)
        
        # Export button - COMPACT version
        export_btn = ActionButton("", "export", 
                                lambda: self.exportRequested.emit(self.word_data.get('word', '')),
                                compact=True)
        export_btn.setToolTip("Add to export queue")
        self.collapsible_box.add_header_widget(export_btn)
    
    def _get_frequency_label(self, frequency: int) -> tuple[str, str]:
        """Convert frequency rank to human-readable label using themed colors."""
        theme = get_theme_manager().current_theme
        
        if frequency <= 500:
            return ("Very Common", theme.freq_very_common)
        elif frequency <= 1500:
            return ("Common", theme.freq_common)
        elif frequency <= 5000:
            return ("Uncommon", theme.freq_uncommon)
        elif frequency <= 15000:
            return ("Rare", theme.freq_rare)
        else:
            return ("Very Rare", theme.freq_very_rare)
    
    def _show_frequency_breakdown(self, frequencies: dict) -> None:
        """Show detailed frequency breakdown."""
        from aqt.utils import showInfo
        
        avg_freq = sum(frequencies.values()) / len(frequencies)
        avg_text, _ = self._get_frequency_label(int(avg_freq))
        
        breakdown_lines = [f"Overall: {avg_text} (avg: {int(avg_freq):,})", ""]
        for freq_name, freq_value in frequencies.items():
            freq_text, _ = self._get_frequency_label(freq_value)
            breakdown_lines.append(f"{freq_name}: {freq_value:,} ({freq_text})")
        
        breakdown_lines.extend(["", "(Lower rank = more common)"])
        showInfo("\n".join(breakdown_lines), title="Frequency Breakdown")
    
    def add_dictionary_section(self, dict_name: str, definitions: list, examples: list = None, is_primary: bool = False) -> None:
        """Add a dictionary section to this word."""
        dict_section = DictionarySubsection(dict_name, definitions, examples, is_primary)
        self.dictionary_sections.append(dict_section)
        self.content_layout.addWidget(dict_section)
    
    def _on_theme_changed(self, new_theme: ThemeColors):
        """Handle theme changes from theme manager."""
        # Update collapsible box if it has theme support
        if hasattr(self.collapsible_box, '_apply_styling'):
            self.collapsible_box._apply_styling()
        
        # Update dictionary sections
        for dict_section in self.dictionary_sections:
            if hasattr(dict_section, 'update_theme'):
                dict_section.update_theme(new_theme)
    
    def update_theme(self, theme: ThemeColors) -> None:
        """Update component styling with new theme."""
        # Update dictionary subsections
        for dict_section in self.dictionary_sections:
            if hasattr(dict_section, 'update_theme'):
                dict_section.update_theme(theme)
        
        # Update collapsible box if it has theme support
        if hasattr(self.collapsible_box, '_apply_styling'):
            self.collapsible_box._apply_styling()
    
    def closeEvent(self, event):
        """Clean up theme observer on close."""
        if hasattr(self, 'theme_manager'):
            self.theme_manager.unregister_observer(self._on_theme_changed)
        super().closeEvent(event)


class DictionarySubsection(ThemedWidget):
    """
    Individual dictionary's definition section.
    Creates POS badges and uses theme colors.
    """
    
    def __init__(self, dict_name: str, definitions: list, examples: list = None, is_primary: bool = False, parent: Optional[QWidget] = None):
        """Initialize dictionary subsection."""
        super().__init__(parent)
        
        self.dict_name = dict_name
        self.definitions = definitions
        self.examples = examples or []
        self.is_expanded = is_primary
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Dictionary header container with layout for title + buttons
        self.dict_header_container = QWidget()
        self.dict_header_layout = QHBoxLayout(self.dict_header_container)
        self.dict_header_layout.setContentsMargins(0, 0, 0, 0)
        self.dict_header_layout.setSpacing(8)
        
        # Dictionary header button (clickable)
        self.dict_header_button = QPushButton(f"▼ {dict_name}" if is_primary else f"▶ {dict_name}")
        self.dict_header_button.clicked.connect(self._toggle_expanded)
        self.dict_header_layout.addWidget(self.dict_header_button, 1)  # Stretch to fill
        
        # Add copy button with ThemedButton
        self.copy_btn = ThemedButton("✂", "copy")
        self.copy_btn.setMinimumSize(32, 28)
        self.copy_btn.setMaximumSize(32, 28)
        self.copy_btn.setToolTip("Copy definition")
        self.copy_btn.clicked.connect(self._copy_definition)
        self.dict_header_layout.addWidget(self.copy_btn, 0)
        
        # Add export button with ThemedButton
        self.export_btn = ThemedButton("💾", "export")
        self.export_btn.setMinimumSize(32, 28)
        self.export_btn.setMaximumSize(32, 28)
        self.export_btn.setToolTip("Export definition")
        self.export_btn.clicked.connect(self._export_definition)
        self.dict_header_layout.addWidget(self.export_btn, 0)
        
        layout.addWidget(self.dict_header_container)
        
        # Dictionary content box
        self.dict_content_box = QFrame()
        self.dict_content_layout = QVBoxLayout(self.dict_content_box)
        self.dict_content_layout.setContentsMargins(16, 16, 16, 16)
        self.dict_content_layout.setSpacing(8)
        layout.addWidget(self.dict_content_box)
        
        # Add definitions
        for defn in definitions:
            def_widget = self._create_definition_line(defn)
            self.dict_content_layout.addWidget(def_widget)
        
        # Add examples
        if examples:
            examples_widget = self._create_examples_section()
            self.dict_content_layout.addWidget(examples_widget)
        
        # Apply styling
        self._apply_styling()
        
        # Set initial visibility
        if not is_primary:
            self.dict_content_box.hide()
    
    def add_header_button(self, button: QWidget) -> None:
        """Add button to dictionary header right side."""
        self.dict_header_layout.addWidget(button, 0)  # Don't stretch
    
    def _create_definition_line(self, definition: dict) -> QWidget:
        """Create POS badge + definition text."""
        theme = self.theme_manager.current_theme
        
        # Container - MUST be transparent
        container = QWidget()
        container.setStyleSheet("QWidget { background-color: transparent; border: none; }")
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(12)
        
        # POS BADGE - THIS WAS MISSING!
        pos_label = QLabel(definition.get('type', 'noun'))
        pos_label.setStyleSheet(f"""
            QLabel {{
                background-color: {theme.accent_color};
                color: white;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(pos_label, 0)  # 0 = don't stretch
        
        # Definition text
        def_label = QLabel(definition.get('text', ''))
        def_label.setWordWrap(True)
        def_label.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {theme.text_primary};
                border: none;
            }}
        """)
        layout.addWidget(def_label, 1)  # 1 = stretch to fill
        
        return container
    
    def _create_examples_section(self) -> QWidget:
        """Create examples with ONLY top border."""
        theme = self.theme_manager.current_theme
        
        # Container - only border-top
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border: none;
                border-top: 1px solid {theme.border_color};
                padding-top: 12px;
                margin-top: 12px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # "Examples:" label
        label = QLabel("Examples:")
        label.setStyleSheet(f"""
            QLabel {{
                color: {theme.text_muted};
                font-weight: 600;
                font-size: 13px;
                background-color: transparent;
                border: none;
            }}
        """)
        layout.addWidget(label)
        
        # Example items - NO BORDERS
        for example in self.examples:
            ex_label = QLabel(f"• {example}")
            ex_label.setWordWrap(True)
            ex_label.setStyleSheet(f"""
                QLabel {{
                    color: {theme.text_muted};
                    font-size: 13px;
                    background-color: transparent;
                    border: none;
                    padding: 3px 0;
                }}
            """)
            layout.addWidget(ex_label)
        
        return container
    
    def _toggle_expanded(self):
        """Toggle expanded/collapsed state."""
        self.is_expanded = not self.is_expanded
        self.dict_content_box.setVisible(self.is_expanded)
        arrow = "▼" if self.is_expanded else "▶"
        self.dict_header_button.setText(f"{arrow} {self.dict_name}")
    
    def _copy_definition(self) -> None:
        """Copy this dictionary's definition to clipboard."""
        try:
            from aqt.qt import QApplication
            text_parts = [f"{self.dict_name}:"]
            for i, defn in enumerate(self.definitions, 1):
                def_type = defn.get('type', '')
                def_text = defn.get('text', '')
                text_parts.append(f"{i}. ({def_type}) {def_text}")
            if self.examples:
                text_parts.extend(["", "Examples:"] + [f"• {ex}" for ex in self.examples])
            QApplication.clipboard().setText('\n'.join(text_parts))
        except Exception as e:
            logger.error(f"Failed to copy: {e}")
    
    def _export_definition(self) -> None:
        """Export this dictionary's definition to Anki."""
        logger.info(f"Export requested for {self.dict_name}")
    
    def _apply_styling(self):
        """Apply styling to all components."""
        theme = self.theme_manager.current_theme
        
        # Dictionary header container - transparent
        dict_header_container_style = f"""
            QWidget {{
                background-color: transparent;
                border: none;
                border-top: 1px solid {theme.border_color};
                margin: 0px;
                padding: 0px;
                min-height: 44px;
            }}
        """
        self.dict_header_container.setStyleSheet(dict_header_container_style)
        
        # Dictionary header button - transparent, no border, part of panel
        dict_header_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {theme.text_muted};
                border: none;
                padding: 0px 16px;
                text-align: left;
                line-height: 44px;
                font-size: 13px;
                font-weight: 600;
                margin: 0px;
            }}
            QPushButton:hover {{
                color: {theme.text_primary};
            }}
        """
        self.dict_header_button.setStyleSheet(dict_header_style)
        
        # ThemedButtons (copy_btn and export_btn) handle their own styling
        
        # Dictionary content box - use panel color, no border (it's inside the panel)
        dict_content_style = f"""
            QFrame {{
                background-color: {theme.panel_color};
                border: none;
                margin: 0px;
                padding: 0px;
            }}
        """
        self.dict_content_box.setStyleSheet(dict_content_style)
    



class DictionaryFilterBar(QWidget):
    """
    Dictionary options and search mode selector.
    
    Features:
    - Dropdown to select active dictionary group/profile
    - Dropdown to select search mode (Forward, Backward, etc.)
    - Toggle button for conjugation/deinflection
    - Clean single-line interface
    
    Signals:
        filterChanged(str): Emitted when dictionary group selection changes
        searchModeChanged(str): Emitted when search mode selection changes
        conjugationToggled(bool): Emitted when conjugation is toggled on/off
    """
    
    filterChanged = pyqtSignal(str)
    searchModeChanged = pyqtSignal(str)
    conjugationToggled = pyqtSignal(bool)
    
    def __init__(
        self,
        dictionary_groups: Optional[List[tuple]] = None,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize dictionary options selector.
        
        Args:
            dictionary_groups: List of (name, id) tuples for dictionary groups
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Theme management
        self.theme_manager = get_theme_manager()
        self.style_generator = StyleGenerator(self.theme_manager.current_theme)
        self.theme_manager.register_observer(self._on_theme_changed)
        
        # Default dictionary groups if none provided
        if dictionary_groups is None:
            dictionary_groups = [
                ("All Dictionaries", "all"),
                ("Japanese Learning", "japanese"),
                ("Monolingual Only", "monolingual"),
                ("Bilingual Only", "bilingual"),
                ("Custom Group 1", "custom1")
            ]
        
        self.dictionary_groups = dictionary_groups
        
        # Create horizontal layout with better responsive behavior
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)  # Reduced spacing to fit better
        
        # Dictionary Group section
        dict_label = ThemedLabel("Dictionary Group:", "muted")
        dict_label.setStyleSheet(f"font-weight: 500; min-width: 100px; font-size: {get_theme_manager().current_theme.get_font_size('small')}px;")
        layout.addWidget(dict_label)
        
        # Dictionary group dropdown
        self.dict_dropdown = QComboBox()
        self.dict_dropdown.setMinimumHeight(36)
        self.dict_dropdown.setMaximumWidth(250)  # Add maximum width
        self.dict_dropdown.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Add dictionary group items
        for name, group_id in dictionary_groups:
            self.dict_dropdown.addItem(name, group_id)
        
        # Connect signal
        self.dict_dropdown.currentTextChanged.connect(self._on_dict_selection_changed)
        layout.addWidget(self.dict_dropdown)
        
        # Store arrow reference for positioning
        self.dict_arrow = QLabel("▼", self.dict_dropdown)
        theme = get_theme_manager().current_theme
        self.dict_arrow.setStyleSheet(f"""
            QLabel {{
                color: {theme.text_muted};
                font-size: {theme.get_font_size('small')}px;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }}
        """)
        self.dict_arrow.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.dict_arrow.setFixedSize(12, 12)
        
        # Position arrow using a timer to ensure widget is properly sized
        def position_dict_arrow():
            if self.dict_dropdown.isVisible() and self.dict_dropdown.width() > 0:
                x = self.dict_dropdown.width() - 18
                y = (self.dict_dropdown.height() - 12) // 2
                self.dict_arrow.move(x, y)
        
        # Use QTimer to position after layout is complete
        QTimer.singleShot(0, position_dict_arrow)
        
        # Also position on resize
        original_resize = self.dict_dropdown.resizeEvent
        def new_resize(event):
            original_resize(event)
            QTimer.singleShot(0, position_dict_arrow)
        self.dict_dropdown.resizeEvent = new_resize
        
        # Add spacing
        layout.addSpacing(12)
        
        # Search Mode section
        search_label = ThemedLabel("Search Mode:", "muted")
        search_label.setStyleSheet(f"font-weight: 500; min-width: 80px; font-size: {get_theme_manager().current_theme.get_font_size('small')}px;")
        layout.addWidget(search_label)
        
        # Search mode dropdown
        self.search_dropdown = QComboBox()
        self.search_dropdown.setMinimumHeight(36)
        self.search_dropdown.setMaximumWidth(180)  # Add maximum width
        self.search_dropdown.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Add search mode items
        search_modes = [
            ("Forward", "forward"),
            ("Backward", "backward"),
            ("Exact", "exact"),
            ("Anywhere", "anywhere"),
            ("Definition", "definition"),
            ("Example", "example"),
            ("Pronunciation", "pronunciation")
        ]
        
        for name, mode_id in search_modes:
            self.search_dropdown.addItem(name, mode_id)
        
        # Connect signal
        self.search_dropdown.currentTextChanged.connect(self._on_search_mode_changed)
        layout.addWidget(self.search_dropdown)
        
        # Store arrow reference for positioning
        self.search_arrow = QLabel("▼", self.search_dropdown)
        theme = get_theme_manager().current_theme
        self.search_arrow.setStyleSheet(f"""
            QLabel {{
                color: {theme.text_muted};
                font-size: {theme.get_font_size('small')}px;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }}
        """)
        self.search_arrow.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.search_arrow.setFixedSize(12, 12)
        
        # Position arrow using a timer to ensure widget is properly sized
        def position_search_arrow():
            if self.search_dropdown.isVisible() and self.search_dropdown.width() > 0:
                x = self.search_dropdown.width() - 18
                y = (self.search_dropdown.height() - 12) // 2
                self.search_arrow.move(x, y)
        
        # Use QTimer to position after layout is complete
        QTimer.singleShot(0, position_search_arrow)
        
        # Also position on resize
        original_resize = self.search_dropdown.resizeEvent
        def new_resize(event):
            original_resize(event)
            QTimer.singleShot(0, position_search_arrow)
        self.search_dropdown.resizeEvent = new_resize
        
        # Add some spacing
        layout.addSpacing(12)
        
        # Conjugation toggle button
        self.conjugation_button = QPushButton("活用 ON")
        self.conjugation_button.setCheckable(True)
        self.conjugation_button.setChecked(True)  # Default: conjugation enabled
        self.conjugation_button.setMinimumHeight(36)
        self.conjugation_button.setMinimumWidth(80)
        self.conjugation_button.clicked.connect(self._on_conjugation_toggled)
        layout.addWidget(self.conjugation_button)
        
        # Add stretch to push everything to the left
        layout.addStretch()
        
        # Apply themed styling to conjugation button
        self._apply_conjugation_button_styling()
        

        
        # Apply themed dropdown styling
        self._apply_dropdown_styling()
        
        # Override showPopup to apply dark theme to dropdown views
        def create_dark_dropdown(dropdown):
            original_show_popup = dropdown.showPopup
            
            def dark_show_popup():
                original_show_popup()
                try:
                    # Apply themed styling to the popup view
                    view = dropdown.view()
                    if view:
                        theme = get_theme_manager().current_theme
                        style_gen = StyleGenerator(theme)
                        hover_bg = style_gen.adjust_color_brightness(theme.panel_color, 1.2)
                        
                        view.setStyleSheet(f"""
                            QListView {{
                                background-color: {theme.panel_color} !important;
                                border: 1px solid {theme.border_color} !important;
                                border-radius: 6px !important;
                                color: {theme.text_primary} !important;
                                selection-background-color: {theme.accent_color} !important;
                                selection-color: white !important;
                                outline: none !important;
                            }}
                            QListView::item {{
                                padding: 8px 12px !important;
                                border: none !important;
                                background-color: {theme.panel_color} !important;
                                color: {theme.text_primary} !important;
                                min-height: 20px !important;
                            }}
                            QListView::item:hover {{
                                background-color: {hover_bg} !important;
                                color: {theme.text_primary} !important;
                            }}
                            QListView::item:selected {{
                                background-color: {theme.accent_color} !important;
                                color: white !important;
                            }}
                        """)
                except Exception as e:
                    logger.debug(f"Failed to apply dropdown dark theme: {e}")
            
            dropdown.showPopup = dark_show_popup
        
        create_dark_dropdown(self.dict_dropdown)
        create_dark_dropdown(self.search_dropdown)
        
        logger.debug(f"DictionaryFilterBar initialized with {len(dictionary_groups)} groups")
    
    def _apply_conjugation_button_styling(self):
        """Apply themed styling to conjugation button."""
        theme = get_theme_manager().current_theme
        style_gen = StyleGenerator(theme)
        
        # Use themed button styling with toggle states
        button_style = f"""
            QPushButton {{
                background: {theme.accent_color};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: {theme.get_font_size('small')}px;
                font-weight: bold;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                background: {style_gen.adjust_color_brightness(theme.accent_color, 0.9)};
            }}
            QPushButton:checked {{
                background: {theme.accent_color};
            }}
            QPushButton:!checked {{
                background: {theme.text_muted};
                color: {theme.text_primary};
            }}
            QPushButton:!checked:hover {{
                background: {style_gen.adjust_color_brightness(theme.text_muted, 0.9)};
            }}
        """
        self.conjugation_button.setStyleSheet(button_style)
    
    def _apply_dropdown_styling(self):
        """Apply themed styling to dropdown menus."""
        theme = get_theme_manager().current_theme
        style_gen = StyleGenerator(theme)
        
        # Use centralized dropdown styling with additional constraints
        dropdown_style = style_gen.dropdown_style()
        
        # Additional styling to ensure proper bounds
        enhanced_style = dropdown_style + f"""
QComboBox {{
    qproperty-maximumWidth: 250px;
}}
QComboBox::drop-down {{
    width: 24px;
}}
QComboBox QAbstractItemView {{
    min-width: 200px;
    max-width: 300px;
}}
"""
        
        self.dict_dropdown.setStyleSheet(enhanced_style)
        self.search_dropdown.setStyleSheet(enhanced_style)
    
    def _on_dict_selection_changed(self, text: str) -> None:
        """Handle dictionary group selection change."""
        # Find the group_id for the selected text
        for name, group_id in self.dictionary_groups:
            if name == text:
                self.filterChanged.emit(group_id)
                logger.debug(f"Dictionary group changed to: {group_id}")
                break
    
    def _on_search_mode_changed(self, text: str) -> None:
        """Handle search mode selection change."""
        # Find the mode_id for the selected text
        search_modes = [
            ("Forward", "forward"),
            ("Backward", "backward"),
            ("Exact", "exact"),
            ("Anywhere", "anywhere"),
            ("Definition", "definition"),
            ("Example", "example"),
            ("Pronunciation", "pronunciation")
        ]
        
        for name, mode_id in search_modes:
            if name == text:
                self.searchModeChanged.emit(mode_id)
                logger.debug(f"Search mode changed to: {mode_id}")
                break
    
    def _on_conjugation_toggled(self, checked: bool) -> None:
        """Handle conjugation toggle button."""
        # Update button text
        if checked:
            self.conjugation_button.setText("活用 ON")
        else:
            self.conjugation_button.setText("活用 OFF")
        
        self.conjugationToggled.emit(checked)
        logger.debug(f"Conjugation toggled: {checked}")
    
    def get_selected_group(self) -> Optional[str]:
        """
        Get currently selected dictionary group ID.
        
        Returns:
            Selected group ID or None
        """
        current_index = self.dict_dropdown.currentIndex()
        if current_index >= 0:
            return self.dict_dropdown.itemData(current_index)
        return None
    
    def get_selected_search_mode(self) -> Optional[str]:
        """
        Get currently selected search mode ID.
        
        Returns:
            Selected search mode ID or None
        """
        current_index = self.search_dropdown.currentIndex()
        if current_index >= 0:
            return self.search_dropdown.itemData(current_index)
        return None
    
    def set_selected_group(self, group_id: str) -> None:
        """
        Set selected dictionary group by ID.
        
        Args:
            group_id: Group ID to select
        """
        for i in range(self.dict_dropdown.count()):
            if self.dict_dropdown.itemData(i) == group_id:
                self.dict_dropdown.setCurrentIndex(i)
                break
    
    def set_selected_search_mode(self, mode_id: str) -> None:
        """
        Set selected search mode by ID.
        
        Args:
            mode_id: Search mode ID to select
        """
        for i in range(self.search_dropdown.count()):
            if self.search_dropdown.itemData(i) == mode_id:
                self.search_dropdown.setCurrentIndex(i)
                break
    
    def is_conjugation_enabled(self) -> bool:
        """
        Get current conjugation toggle state.
        
        Returns:
            True if conjugation is enabled, False otherwise
        """
        return self.conjugation_button.isChecked()
    
    def set_conjugation_enabled(self, enabled: bool) -> None:
        """
        Set conjugation toggle state.
        
        Args:
            enabled: Whether to enable conjugation
        """
        self.conjugation_button.setChecked(enabled)
        self._on_conjugation_toggled(enabled)  # Update button text
    
    def _on_theme_changed(self, new_theme: ThemeColors):
        """Handle theme changes from theme manager."""
        self.style_generator = StyleGenerator(new_theme)
        self.update_theme(new_theme)
    
    def closeEvent(self, event):
        """Clean up theme observer on close."""
        if hasattr(self, 'theme_manager'):
            self.theme_manager.unregister_observer(self._on_theme_changed)
        super().closeEvent(event)
    
    def update_theme(self, theme: ThemeColors) -> None:
        """
        Update component styling with new theme.
        
        Args:
            theme: New theme colors
        """
        # Re-apply all themed styling
        self._apply_conjugation_button_styling()
        self._apply_dropdown_styling()
        
        logger.debug("Updated DictionaryFilterBar theme")


# =============================================================================
# LAYOUT COMPONENTS (continued)
# =============================================================================

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
        
        # Apply themed styling
        self._apply_styling()
        
        # Create container widget
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(15)
        self.layout.addStretch()
        
        self.setWidget(self.container)
        
        logger.debug("ModernResultsArea initialized")
    
    def _apply_styling(self):
        """Apply themed styling to scroll area."""
        theme = get_theme_manager().current_theme
        style_gen = StyleGenerator(theme)
        
        # Use darker background for results area
        results_bg = style_gen.adjust_color_brightness(theme.background_color, 1.1)
        handle_color = style_gen.adjust_color_brightness(theme.border_color, 1.5)
        handle_hover = style_gen.adjust_color_brightness(handle_color, 1.3)
        
        scroll_style = f"""
            QScrollArea {{
                background: {results_bg};
                border: none;
            }}
            QScrollBar:vertical {{
                background: {theme.panel_color};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {handle_color};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {handle_hover};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
        self.setStyleSheet(scroll_style)
    
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
    
    def update_theme(self, theme: ThemeColors) -> None:
        """
        Update component styling with new theme.
        
        Args:
            theme: New theme colors
        """
        self._apply_styling()
        logger.debug("Updated ModernResultsArea theme")
