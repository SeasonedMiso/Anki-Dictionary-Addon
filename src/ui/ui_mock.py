# -*- coding: utf-8 -*-
"""
UI Mock/Demo for Dictionary Window.

This is a standalone demo that shows the complete UI design with sample data.
Use this to validate the design before building real functionality.
"""

from typing import Optional
import logging
from dataclasses import dataclass

from aqt.qt import QWidget, QVBoxLayout, QLabel, Qt, QSizePolicy

from .modern_components import (
    ModernSearchBar,
    DefinitionCard,
    DictionaryFilterBar,
    ModernResultsArea
)

logger = logging.getLogger(__name__)


@dataclass
class _Palette:
    bg: str = "#0f0f0f"
    panel: str = "#1c1c1c"
    accent: str = "#3a7afe"
    text_primary: str = "#e6e6e6"
    text_muted: str = "#9aa0ad"
    border: str = "#2b2f36"


class UIMockWindow(QWidget):
    """
    Mock/demo window showing complete UI design with sample data.
    
    This window demonstrates:
    - Modern search bar
    - Dictionary filter bar
    - Results area with definition cards
    - Action buttons
    - Dark theme styling
    - Complete layout and spacing
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize UI mock window."""
        super().__init__(parent)
        
        self.setWindowTitle("Dictionary UI Mock - Design Preview")
        self.setMinimumSize(800, 600)
        palette = _Palette()
        self.palette = palette  # keep for later tweaks
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {palette.bg};
                color: {palette.text_primary};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            QLabel#subtitle {{
                color: {palette.text_muted};
                font-size: 13px;
            }}
        """)

        self._setup_ui()
        self._populate_sample_data()
    
    def _setup_ui(self):
        """Set up the UI layout."""
        # Alignment helpers for PyQt6 / Qt versions
        Align = getattr(Qt, "AlignmentFlag", Qt)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(14)
        container.setMaximumWidth(1080)
        outer.addWidget(
            container,
            alignment=Align.AlignHCenter | Align.AlignTop,
        )

        # Title label
        title = QLabel("🎨 UI Design Preview (mock / sample data)")
        title.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                color: {self.palette.text_primary};
                padding: 12px;
                background-color: {self.palette.panel};
                border: 1px solid {self.palette.border};
                border-radius: 10px;
                font-weight: 600;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(title)

        # Subtitle with branch/base info
        subtitle = QLabel("Branch: ui/mock-refresh → dev · Visual-only mock (no real data)")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            QLabel#subtitle {{
                padding: 6px 10px;
                background-color: {self.palette.panel};
                border: 1px dashed {self.palette.border};
                border-radius: 8px;
            }}
        """)
        container_layout.addWidget(subtitle)
        
        # Search bar
        self.search_bar = ModernSearchBar()
        self.search_bar.searchChanged.connect(self._on_search_changed)
        container_layout.addWidget(self.search_bar)
        
        # Filter bar
        self.filter_bar = DictionaryFilterBar()
        self.filter_bar.filterChanged.connect(self._on_filters_changed)
        container_layout.addWidget(self.filter_bar)
        
        # Results area
        self.results_area = ModernResultsArea()
        container_layout.addWidget(self.results_area)
        
        # Status bar
        self.status_label = QLabel("Ready — Type in search bar or toggle filters (mock only)")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 10px;
            }
        """)
        container_layout.addWidget(self.status_label)
    
    def _populate_sample_data(self):
        """Populate with sample definition cards."""
        # Sample data matching DefinitionCard's expected format
        sample_definitions = [
            {
                'word': '食べる',
                'phonetic': 'たべる',
                'frequency': 1250,
                'definitions': [
                    {'type': 'verb', 'text': 'to eat'},
                    {'type': 'verb', 'text': 'to live on (e.g. a salary); to live off; to subsist on'}
                ],
                'examples': ['毎日野菜を食べる', 'I eat vegetables every day']
            },
            {
                'word': '食事',
                'phonetic': 'しょくじ',
                'frequency': 890,
                'definitions': [
                    {'type': 'noun', 'text': 'meal; dinner'},
                    {'type': 'noun', 'text': 'diet'}
                ],
                'examples': ['朝食事をする', 'Have breakfast']
            },
            {
                'word': '勉強',
                'phonetic': 'べんきょう',
                'frequency': 450,
                'definitions': [
                    {'type': 'noun', 'text': 'study; studying'},
                    {'type': 'verb', 'text': 'to study'}
                ],
                'examples': ['日本語を勉強する', 'Study Japanese']
            }
        ]
        
        # Create cards for each sample
        for word_data in sample_definitions:
            card = DefinitionCard(word_data=word_data)
            
            # Connect action buttons (just for demo feedback)
            card.audioRequested.connect(
                lambda w=word_data['word']: self._on_action('Audio', w)
            )
            card.imageRequested.connect(
                lambda w=word_data['word']: self._on_action('Image', w)
            )
            card.exportRequested.connect(
                lambda w=word_data['word']: self._on_action('Export', w)
            )
            
            self.results_area.add_card(card)
    
    def _on_search_changed(self, text: str):
        """Handle search text changes."""
        if text:
            self.status_label.setText(f"Search changed: '{text}' (mock - no real search)")
        else:
            self.status_label.setText("Ready - Type in search bar to see interaction")
    
    def _on_filters_changed(self, filters: list):
        """Handle filter changes."""
        if filters:
            filter_text = ", ".join(filters)
            self.status_label.setText(f"Filters active: {filter_text} (mock - no real filtering)")
        else:
            self.status_label.setText("All filters cleared")
    
    def _on_action(self, action: str, word: str):
        """Handle action button clicks."""
        self.status_label.setText(f"{action} clicked for '{word}' (mock - no real action)")


def show_ui_mock(parent: Optional[QWidget] = None) -> UIMockWindow:
    """
    Show the UI mock window.
    
    Args:
        parent: Parent widget
        
    Returns:
        The mock window instance
    """
    import os
    
    window = UIMockWindow(parent)
    window.show()
    
    # If auto-opened via debug script, close after 3 seconds
    if os.environ.get('ANKI_DICT_AUTO_OPEN') == '1':
        from aqt.qt import QTimer
        QTimer.singleShot(3000, window.close)
    
    return window
