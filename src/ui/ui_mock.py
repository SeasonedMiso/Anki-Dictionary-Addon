# -*- coding: utf-8 -*-
"""
UI Mock/Demo for Dictionary Window.

This is a standalone demo that shows the complete UI design with sample data.
Use this to validate the design before building real functionality.
"""

from typing import Optional
import logging

from aqt.qt import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    Qt, QSizePolicy
)

from .modern_components import (
    ModernSearchBar,
    DefinitionCard,
    DictionaryFilterBar,
    ModernResultsArea
)

logger = logging.getLogger(__name__)


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
        
        # Apply dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """)
        
        self._setup_ui()
        self._populate_sample_data()
    
    def _setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title label
        title = QLabel("🎨 UI Design Preview - This is a mock with sample data")
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #888888;
                padding: 10px;
                background-color: #2a2a2a;
                border-radius: 8px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Search bar
        self.search_bar = ModernSearchBar()
        self.search_bar.searchChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_bar)
        
        # Filter bar
        self.filter_bar = DictionaryFilterBar()
        self.filter_bar.filtersChanged.connect(self._on_filters_changed)
        layout.addWidget(self.filter_bar)
        
        # Results area
        self.results_area = ModernResultsArea()
        layout.addWidget(self.results_area)
        
        # Status bar
        self.status_label = QLabel("Ready - Type in search bar to see interaction")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #888888;
                padding: 8px;
            }
        """)
        layout.addWidget(self.status_label)
    
    def _populate_sample_data(self):
        """Populate with sample definition cards."""
        # Sample data for different dictionary types
        sample_definitions = [
            {
                'word': '食べる',
                'reading': 'たべる',
                'dictionary': 'JMdict',
                'definitions': [
                    '1. to eat',
                    '2. to live on (e.g. a salary); to live off; to subsist on'
                ],
                'has_audio': True,
                'has_image': False
            },
            {
                'word': '食べる',
                'reading': 'taberu',
                'dictionary': 'Forvo',
                'definitions': ['Audio pronunciation available'],
                'has_audio': True,
                'has_image': False
            },
            {
                'word': '食べる',
                'reading': '',
                'dictionary': 'Google Images',
                'definitions': ['Visual reference available'],
                'has_audio': False,
                'has_image': True
            },
            {
                'word': '食事',
                'reading': 'しょくじ',
                'dictionary': 'JMdict',
                'definitions': [
                    '1. meal; dinner',
                    '2. diet'
                ],
                'has_audio': True,
                'has_image': False
            }
        ]
        
        # Create cards for each sample
        for data in sample_definitions:
            card = DefinitionCard(
                word=data['word'],
                reading=data['reading'],
                dictionary=data['dictionary'],
                definitions=data['definitions']
            )
            
            # Connect action buttons (just for demo feedback)
            card.audioRequested.connect(
                lambda w=data['word']: self._on_action('Audio', w)
            )
            card.imageRequested.connect(
                lambda w=data['word']: self._on_action('Image', w)
            )
            card.exportRequested.connect(
                lambda w=data['word']: self._on_action('Export', w)
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
    window = UIMockWindow(parent)
    window.show()
    return window
