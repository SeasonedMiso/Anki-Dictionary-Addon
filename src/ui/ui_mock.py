# -*- coding: utf-8 -*-
"""
UI Mock/Demo for Dictionary Window.

This is a standalone demo that shows the complete UI design with sample data.
Use this to validate the design before building real functionality.
"""

from typing import Optional
import logging
from dataclasses import dataclass

from aqt.qt import QWidget, QVBoxLayout, QHBoxLayout, QLabel, Qt, QSizePolicy, QPushButton

from .modern_components import (
    ModernSearchBar,
    WordSection,
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
        self.setMinimumSize(600, 400)  # Smaller minimum for better usability
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
        # Remove maximum width constraint for responsive design
        # container.setMaximumWidth(1080)  # Removed to allow full width
        outer.addWidget(container)  # Remove alignment to fill available space

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
        
        # Results area - should expand to fill available space
        self.results_area = ModernResultsArea()
        self.results_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        container_layout.addWidget(self.results_area, 1)  # Stretch factor 1 to expand
        
        # Status bar
        self.status_label = QLabel("Ready — Type in search bar or toggle filters (mock only)")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 10px;
            }
        """)
        container_layout.addWidget(self.status_label)
        
        # Floating options button in bottom right corner
        self.options_btn = QPushButton("⚙")
        self.options_btn.setFixedSize(40, 40)
        self.options_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.palette.panel};
                color: {self.palette.text_primary};
                border: 1px solid {self.palette.border};
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: #333;
                border-color: #555;
            }}
            QPushButton:pressed {{
                background: #222;
            }}
        """)
        self.options_btn.clicked.connect(self._on_options_clicked)
        
        # Position the button in bottom right corner
        self.options_btn.setParent(self)
        self.options_btn.move(self.width() - 60, self.height() - 60)
        self.options_btn.raise_()  # Bring to front
    
    def resizeEvent(self, event):
        """Handle window resize to keep options button in corner."""
        super().resizeEvent(event)
        if hasattr(self, 'options_btn'):
            self.options_btn.move(self.width() - 60, self.height() - 60)
    
    def _populate_sample_data(self):
        """Populate with sample word sections (new structure: Word > Dictionary)."""
        
        # Word: 食べる
        taberu_data = {
            'word': '食べる',
            'phonetic': 'たべる',
            'pitch_accent': '2',
            'frequencies': {
                'JLPT': 1250,
                'Anime': 890,
                'News': 2100
            }
        }
        
        taberu_section = WordSection(taberu_data)
        taberu_section.audioRequested.connect(lambda w: self._on_action('Audio', w))
        taberu_section.imageRequested.connect(lambda w: self._on_action('Image', w))
        
        # Add JMdict definition (primary - expanded by default)
        taberu_section.add_dictionary_section(
            "JMdict (Japanese-English)",
            [
                {'type': 'verb', 'text': 'to eat'},
                {'type': 'verb', 'text': 'to live on (e.g. a salary); to live off; to subsist on'}
            ],
            ['毎日野菜を食べる', 'I eat vegetables every day'],
            is_primary=True
        )
        
        # Add 大辞林 definition (collapsed by default)
        taberu_section.add_dictionary_section(
            "大辞林 (Daijirin)",
            [
                {'type': '動詞', 'text': '口に入れて噛み、飲み込む。'},
                {'type': '動詞', 'text': '生活の糧とする。暮らしを立てる。'}
            ],
            ['ご飯を食べる', '魚を食べる'],
            is_primary=False
        )
        
        self.results_area.add_card(taberu_section)
        
        # Word: 勉強
        benkyou_data = {
            'word': '勉強',
            'phonetic': 'べんきょう',
            'pitch_accent': '0',
            'frequencies': {
                'JLPT': 450,
                'Textbooks': 320
            }
        }
        
        benkyou_section = WordSection(benkyou_data)
        benkyou_section.audioRequested.connect(lambda w: self._on_action('Audio', w))
        benkyou_section.imageRequested.connect(lambda w: self._on_action('Image', w))
        
        # Add JMdict definition (primary)
        benkyou_section.add_dictionary_section(
            "JMdict (Japanese-English)",
            [
                {'type': 'noun', 'text': 'study; studying'},
                {'type': 'verb', 'text': 'to study'}
            ],
            ['日本語を勉強する', 'Study Japanese'],
            is_primary=True
        )
        
        # Add 大辞林 definition (collapsed)
        benkyou_section.add_dictionary_section(
            "大辞林 (Daijirin)",
            [
                {'type': '名詞', 'text': '学問や技術を学ぶこと。'},
                {'type': '動詞', 'text': '努力して学習すること。'}
            ],
            ['数学を勉強する', '勉強に励む'],
            is_primary=False
        )
        
        self.results_area.add_card(benkyou_section)
    
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
    
    def _on_options_clicked(self):
        """Handle options button click."""
        self.status_label.setText("Options clicked (mock - would open settings dialog)")


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
    
    # If auto-close flag is set, close after 3 seconds
    if os.environ.get('ANKI_DICT_AUTO_CLOSE') == '1':
        from aqt.qt import QTimer
        QTimer.singleShot(3000, window.close)
    
    return window
