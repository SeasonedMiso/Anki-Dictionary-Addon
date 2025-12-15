# -*- coding: utf-8 -*-
"""
UI Mock/Demo for Dictionary Window.

This is a standalone demo that shows the complete UI design with sample data.
Use this to validate the design before building real functionality.
"""

from typing import Optional
import logging
from aqt.qt import QWidget, QVBoxLayout, QHBoxLayout, QLabel, Qt, QSizePolicy, QPushButton

from .dictionary_widgets import (
    ModernSearchBar,
    WordSection, 
    DictionaryFilterBar,
    ModernResultsArea
)
from .styling import get_theme_manager, StyleGenerator

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
        
        # Load saved theme preference or default to dark
        from .styling import THEME_PRESETS
        from pathlib import Path
        
        theme_manager = get_theme_manager()
        config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
        theme_manager.config_path = str(config_path)
        
        saved_theme = theme_manager.load_theme_preference()
        
        # Get all available themes (presets + user themes)
        all_themes = theme_manager.get_all_themes()
        
        # Use saved theme if it exists, otherwise default to dark
        if saved_theme and saved_theme in all_themes:
            theme_manager.update_theme(all_themes[saved_theme])
        else:
            theme_manager.update_theme(THEME_PRESETS["dark"])
        
        self.setWindowTitle("Dictionary")
        self.setMinimumSize(600, 400)  # Smaller minimum for better usability
        
        # Use centralized theming system
        self.theme_manager = get_theme_manager()
        self.style_generator = StyleGenerator(self.theme_manager.current_theme)
        self.theme_manager.register_observer(self._on_theme_changed)

        self._setup_ui()
        self._apply_theme_styling()
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
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 10px;
            }
        """)
        container_layout.addWidget(self.status_label)
        
        # Floating action buttons in bottom right corner
        self.options_btn = QPushButton("⚙")
        self.options_btn.setFixedSize(40, 40)
        self.options_btn.clicked.connect(self._on_options_clicked)
        
        self.export_btn = QPushButton("📤")
        self.export_btn.setFixedSize(40, 40)
        self.export_btn.clicked.connect(self._on_export_clicked)
        
        # Position the buttons in bottom right corner with padding
        self.options_btn.setParent(self)
        self.export_btn.setParent(self)
        # Position will be set in showEvent when window size is known
        self.options_btn.raise_()  # Bring to front
        self.export_btn.raise_()  # Bring to front
    
    def showEvent(self, event):
        """Position buttons when window is shown."""
        super().showEvent(event)
        self._position_floating_buttons()
    
    def resizeEvent(self, event):
        """Handle window resize to keep buttons in corner."""
        super().resizeEvent(event)
        self._position_floating_buttons()
    
    def _position_floating_buttons(self):
        """Position floating action buttons in bottom right corner."""
        if hasattr(self, 'options_btn') and hasattr(self, 'export_btn'):
            # Stack buttons vertically with spacing
            button_spacing = 50
            margin = 20
            
            self.options_btn.move(
                self.width() - self.options_btn.width() - margin,
                self.height() - self.options_btn.height() - margin
            )
            
            self.export_btn.move(
                self.width() - self.export_btn.width() - margin,
                self.height() - self.export_btn.height() - margin - button_spacing
            )
    
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
        taberu_section.exportRequested.connect(lambda w: self._on_export_word(w))
        
        # DIAGNOSTIC CODE
        print("========== DIAGNOSTIC START ==========")
        print(f"WordSection type: {type(taberu_section)}")
        print(f"WordSection class: {taberu_section.__class__.__name__}")
        
        if hasattr(taberu_section, 'collapsible_box'):
            print(f"✓ Has collapsible_box attribute")
            print(f"  Type: {type(taberu_section.collapsible_box)}")
            print(f"  Class: {taberu_section.collapsible_box.__class__.__name__}")
            
            if hasattr(taberu_section.collapsible_box, 'header'):
                print(f"  ✓ Has header attribute")
                print(f"    Header parent: {taberu_section.collapsible_box.header.parent()}")
                print(f"    Header stylesheet: {taberu_section.collapsible_box.header.styleSheet()[:100]}...")
            else:
                print(f"  ✗ NO header attribute!")
            
            if hasattr(taberu_section.collapsible_box, 'content_frame'):
                print(f"  ✓ Has content_frame attribute")
                print(f"    Content frame parent: {taberu_section.collapsible_box.content_frame.parent()}")
            else:
                print(f"  ✗ NO content_frame attribute!")
            
            container_style = taberu_section.collapsible_box.styleSheet()
            print(f"  Container stylesheet length: {len(container_style)}")
            if "border-left" in container_style:
                print(f"  ✓ Has border-left styling")
            else:
                print(f"  ✗ NO border-left styling!")
        else:
            print(f"✗ NO collapsible_box attribute!")
        
        print("========== DIAGNOSTIC END ==========\n")
        
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
        benkyou_section.exportRequested.connect(lambda w: self._on_export_word(w))
        
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
    
    def _on_theme_changed(self, new_theme):
        """Handle theme changes from the centralized theme manager."""
        self.style_generator = StyleGenerator(new_theme)
        self._apply_theme_styling()
        
        # Update all child components
        for component in [self.search_bar, self.filter_bar, self.results_area]:
            if hasattr(component, 'update_theme'):
                component.update_theme(new_theme)
        
        # Update all word sections in results area
        if hasattr(self, 'results_area') and hasattr(self.results_area, 'layout'):
            layout = self.results_area.layout
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget and hasattr(widget, 'update_theme'):
                        widget.update_theme(new_theme)
        
        logger.info("Applied theme changes to mock UI")
    
    def _apply_theme_styling(self):
        """Apply current theme styling to all UI elements."""
        theme = self.theme_manager.current_theme
        
        # Apply main window styling with comprehensive stylesheet
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.background_color};
                color: {theme.text_primary};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            QMainWindow {{
                background-color: {theme.background_color};
            }}
            QLabel {{
                color: {theme.text_primary};
                background-color: transparent;
            }}
            QLabel#subtitle {{
                color: {theme.text_muted};
                font-size: {theme.get_font_size('small')}px;
            }}
            QPushButton {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                padding: 8px 8px;
            }}
            QPushButton:hover {{
                background-color: {theme.accent_color};
            }}
        """)
        
        # Update title styling
        if hasattr(self, 'title'):
            title_style = f"""
                QLabel {{
                    font-size: {theme.get_font_size('medium')}px;
                    color: {theme.text_primary};
                    padding: 12px;
                    background-color: {theme.panel_color};
                    border: 1px solid {theme.border_color};
                    border-radius: 10px;
                    font-weight: 600;
                }}
            """
            self.title.setStyleSheet(title_style)
        
        # Update subtitle styling
        if hasattr(self, 'subtitle'):
            subtitle_style = f"""
                QLabel#subtitle {{
                    padding: 6px 10px;
                    background-color: {theme.panel_color};
                    border: 1px dashed {theme.border_color};
                    border-radius: 8px;
                    color: {theme.text_muted};
                    font-size: {theme.get_font_size('small')}px;
                }}
            """
            self.subtitle.setStyleSheet(subtitle_style)
        
        # Update options button styling
        self._update_options_button_style()
        
        # Update components with new theme
        if hasattr(self, 'search_bar') and hasattr(self.search_bar, 'update_theme'):
            self.search_bar.update_theme(theme)
        
        if hasattr(self, 'filter_bar') and hasattr(self.filter_bar, 'update_theme'):
            self.filter_bar.update_theme(theme)
        
        if hasattr(self, 'results_area') and hasattr(self.results_area, 'update_theme'):
            self.results_area.update_theme(theme)
    
    def _update_options_button_style(self):
        """Update floating button styling with current theme colors."""
        theme = self.theme_manager.current_theme
        
        # Custom square button style for floating buttons
        button_style = f"""
            QPushButton {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: 20px;
                padding: 0px;
                font-size: 16px;
                font-weight: bold;
                width: 40px;
                height: 40px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {theme.accent_color};
                transform: scale(1.05);
            }}
        """
        
        self.options_btn.setStyleSheet(button_style)
        if hasattr(self, 'export_btn'):
            self.export_btn.setStyleSheet(button_style)



    def _on_options_clicked(self):
        """Handle options button click."""
        try:
            from .settings_window import show_modern_settings
            
            # Show modern settings dialog
            settings = show_modern_settings(self)
            
            if settings:
                self.status_label.setText("Settings applied successfully!")
                # Theme changes are automatically applied via the theme manager observer
            else:
                self.status_label.setText("Settings cancelled")
                
        except Exception as e:
            logger.error(f"Error opening settings: {e}", exc_info=True)
            self.status_label.setText(f"Error opening settings: {str(e)}")
    
    def _on_export_clicked(self):
        """Handle export button click."""
        try:
            from .export_dialog import show_export_dialog
            
            # Show export dialog
            export_data = show_export_dialog(parent=self)
            if export_data:
                self.status_label.setText(f"Exported '{export_data['word']}' to Anki")
            else:
                self.status_label.setText("Export cancelled")
            
        except Exception as e:
            logger.error(f"Error opening export dialog: {e}", exc_info=True)
            self.status_label.setText(f"Error opening export dialog: {str(e)}")
    
    def _on_export_word(self, word: str):
        """Handle export request for specific word."""
        try:
            from .export_dialog import show_export_dialog
            
            # Get word data with definitions
            source_dict = "JMdict"
            definitions = []
            
            if word == "食べる":
                definitions = [
                    {"type": "verb", "text": "to eat"},
                    {"type": "verb", "text": "to live on (e.g. a salary); to live off; to subsist on"}
                ]
            elif word == "勉強":
                definitions = [
                    {"type": "noun", "text": "study; studying"},
                    {"type": "verb", "text": "to study"}
                ]
            
            # Show export dialog with word and definitions pre-filled
            export_data = show_export_dialog(word=word, source_dict=source_dict, definitions=definitions, parent=self)
            if export_data:
                self.status_label.setText(f"Exported '{export_data['word']}' to Anki")
            else:
                self.status_label.setText(f"Export cancelled for '{word}'")
            
        except Exception as e:
            logger.error(f"Error exporting word: {e}", exc_info=True)
            self.status_label.setText(f"Error exporting '{word}': {str(e)}")


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
        
    return window
