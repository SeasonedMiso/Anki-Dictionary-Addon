# -*- coding: utf-8 -*-
"""
Export Dialog - Simple word export interface.

This module provides a focused export dialog for adding words to Anki cards.
Users can:
- Edit the word/term
- Add example sentences
- Paste images onto the card
- Paste audio onto the card
- Configure dictionary auto-add settings
"""

from typing import Optional, Dict, Any
import logging

try:
    from aqt.qt import (
        QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QLineEdit, QTextEdit, QCheckBox, QComboBox, Qt, QApplication,
        QMessageBox, QClipboard, QPixmap, QTabWidget, QScrollArea
    )
    ANKI_AVAILABLE = True
except ImportError:
    ANKI_AVAILABLE = False
    class QDialog: pass
    class QWidget: pass
    class QVBoxLayout: pass
    class QHBoxLayout: pass
    class QLabel: pass
    class QPushButton: pass
    class QLineEdit: pass
    class QTextEdit: pass
    class QCheckBox: pass
    class QComboBox: pass
    class QApplication: pass
    class QMessageBox: pass
    class QClipboard: pass
    class QPixmap: pass
    class QTabWidget: pass
    class QScrollArea: pass
    class Qt: pass

from .styling import get_theme_manager
from .base_widgets import ThemedButton, ThemedLabel, ThemedFrame

logger = logging.getLogger(__name__)


class ExportDialog(QDialog):
    """
    Export dialog for adding words to Anki cards.
    
    Features:
    - Edit word/term
    - Add example sentence
    - Paste image from clipboard
    - Paste audio from clipboard
    - Auto-add definitions from selected dictionaries
    - Select card template
    - Validate all required fields
    - Export to Anki
    """
    
    # Default card templates
    DEFAULT_TEMPLATES = {
        "basic": {
            "name": "Basic",
            "fields": ["Front", "Back"],
            "front_template": "{{Front}}",
            "back_template": "{{Back}}"
        },
        "basic_japanese": {
            "name": "Basic Japanese",
            "fields": ["Word", "Phonetic", "Definition", "Example"],
            "front_template": "{{Word}}<br><small>{{Phonetic}}</small>",
            "back_template": "{{Definition}}<br><br><i>{{Example}}</i>"
        },
        "cloze": {
            "name": "Cloze",
            "fields": ["Text", "Extra"],
            "front_template": "{{cloze:Text}}",
            "back_template": "{{cloze:Text}}<br><br>{{Extra}}"
        }
    }
    
    def __init__(self, word: str = "", source_dict: str = "", definitions: list = None, 
                 templates: Optional[Dict[str, Dict]] = None, parent: Optional[QWidget] = None):
        """
        Initialize export dialog.
        
        Args:
            word: Initial word to export (auto-assigned from export button)
            source_dict: Source dictionary name (e.g., "JMdict", "大辞林")
            definitions: List of definitions from source dictionary
            templates: Custom card templates (uses defaults if None)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.word = word
        self.source_dict = source_dict
        self.definitions = definitions or []
        self.image_data = None
        self.audio_data = None
        self.templates = templates or self.DEFAULT_TEMPLATES
        self.selected_template = None
        self.field_inputs = {}
        
        # Initialize theme
        self.theme_manager = get_theme_manager()
        self.theme = self.theme_manager.current_theme
        
        self.setWindowTitle(f"Export: {word}" if word else "Export Word")
        self.setMinimumSize(700, 750)
        self.setMaximumSize(1000, 1200)
        self.resize(800, 900)
        self.setModal(True)
        
        self._setup_ui()
        self._apply_styling()
        
        logger.debug(f"ExportDialog initialized for word: {word}")
    
    def _setup_ui(self):
        """Set up the dialog UI with tabs."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(600)
        main_layout.addWidget(self.tabs, 1)  # Add stretch factor
        
        # Tab 1: Word & Media
        word_tab = self._create_word_tab()
        self.tabs.addTab(word_tab, "Word & Media")
        
        # Tab 2: Template & Fields
        template_tab = self._create_template_tab()
        self.tabs.addTab(template_tab, "Template & Fields")
        
        # Validation status
        self.validation_status = ThemedLabel("", "muted")
        main_layout.addWidget(self.validation_status)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.addStretch()
        
        cancel_btn = ThemedButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setFixedHeight(40)
        cancel_btn.setMinimumWidth(120)
        button_layout.addWidget(cancel_btn)
        
        export_btn = ThemedButton("Export to Anki", "primary")
        export_btn.clicked.connect(self._export)
        export_btn.setFixedHeight(40)
        export_btn.setMinimumWidth(200)
        # Override the style to use success color with proper sizing
        if ANKI_AVAILABLE:
            theme = self.theme_manager.current_theme
            success_color = theme.success_color
            hover_color = self._adjust_color_brightness(success_color, 1.2)
            pressed_color = self._adjust_color_brightness(success_color, 0.8)
            export_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {success_color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {pressed_color};
                }}
            """)
        button_layout.addWidget(export_btn)
        
        main_layout.addLayout(button_layout)
        
        # Initialize template fields
        self._on_template_changed()
    
    def _create_word_tab(self) -> QWidget:
        """Create the Word & Media tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Word field
        layout.addWidget(ThemedLabel("Word/Term:", "muted"))
        self.word_input = QLineEdit()
        self.word_input.setText(self.word)
        self.word_input.setFixedHeight(40)
        layout.addWidget(self.word_input)
        
        # Example sentence
        layout.addWidget(ThemedLabel("Example Sentence:", "muted"))
        self.example_input = QTextEdit()
        self.example_input.setMinimumHeight(80)
        self.example_input.setMaximumHeight(150)
        self.example_input.setPlaceholderText("Paste or type an example sentence...")
        self.example_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.example_input)
        
        # Source dictionary display
        if self.source_dict:
            layout.addWidget(ThemedLabel(f"Source: {self.source_dict}", "muted"))
            
            # Show definitions from source
            if self.definitions:
                for defn in self.definitions:
                    def_type = defn.get('type', '')
                    def_text = defn.get('text', '')
                    def_label = ThemedLabel(f"• ({def_type}) {def_text}", "muted")
                    layout.addWidget(def_label)
        
        # Media section
        layout.addWidget(ThemedLabel("Media:", "muted"))
        
        media_layout = QHBoxLayout()
        media_layout.setSpacing(12)
        
        self.image_btn = ThemedButton("📷 Paste Image", "secondary")
        self.image_btn.clicked.connect(self._paste_image)
        self.image_btn.setFixedHeight(40)
        self.image_btn.setMinimumWidth(140)
        media_layout.addWidget(self.image_btn)
        
        self.audio_btn = ThemedButton("🔊 Paste Audio", "secondary")
        self.audio_btn.clicked.connect(self._paste_audio)
        self.audio_btn.setFixedHeight(40)
        self.audio_btn.setMinimumWidth(140)
        media_layout.addWidget(self.audio_btn)
        
        media_layout.addStretch()
        layout.addLayout(media_layout)
        
        # Status indicators
        self.image_status = ThemedLabel("No image", "muted")
        layout.addWidget(self.image_status)
        
        self.audio_status = ThemedLabel("No audio", "muted")
        layout.addWidget(self.audio_status)
        
        layout.addStretch()
        return tab
    
    def _create_template_tab(self) -> QWidget:
        """Create the Template & Fields tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Deck selection
        layout.addWidget(ThemedLabel("Target Deck:", "muted"))
        self.deck_combo = QComboBox()
        self.deck_combo.setFixedHeight(40)
        self.deck_combo.setMinimumWidth(200)
        # Add sample decks (will be populated from Anki in real implementation)
        self.deck_combo.addItem("Default", "Default")
        self.deck_combo.addItem("Japanese", "Japanese")
        self.deck_combo.addItem("Vocabulary", "Vocabulary")
        self.deck_combo.addItem("Japanese::Vocabulary", "Japanese::Vocabulary")
        self.deck_combo.addItem("Japanese::Grammar", "Japanese::Grammar")
        layout.addWidget(self.deck_combo)
        
        # Card template selection
        layout.addWidget(ThemedLabel("Card Template:", "muted"))
        self.template_combo = QComboBox()
        self.template_combo.setFixedHeight(40)
        self.template_combo.setMinimumWidth(200)
        for template_id, template_data in self.templates.items():
            self.template_combo.addItem(template_data["name"], template_id)
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        layout.addWidget(self.template_combo)
        
        # Field mapping section
        layout.addWidget(ThemedLabel("Field Mapping (Dictionary → Card):", "muted"))
        
        # Scrollable mapping container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(300)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameStyle(0)  # Remove frame
        
        self.mapping_container = QWidget()
        self.mapping_container.setObjectName("mappingContainer")
        self.mapping_layout = QVBoxLayout(self.mapping_container)
        self.mapping_layout.setContentsMargins(8, 8, 8, 8)
        self.mapping_layout.setSpacing(8)
        self.mapping_layout.addStretch()  # Add stretch at end
        
        scroll.setWidget(self.mapping_container)
        layout.addWidget(scroll, 1)  # Add stretch factor
        
        # Dictionary auto-add settings
        layout.addWidget(ThemedLabel("Auto-add Dictionary Definitions:", "muted"))
        
        # Dictionary list with reordering
        dict_frame = ThemedFrame()
        dict_layout = QVBoxLayout(dict_frame)
        dict_layout.setContentsMargins(12, 12, 12, 12)
        dict_layout.setSpacing(8)
        
        self.dict_checks = {}
        self.dict_order = ["JMdict", "大辞林", "Weblio"]
        self.dict_frame = dict_frame  # Store frame for rebuilding
        self.dict_layout_ref = dict_layout  # Store layout for rebuilding
        self._create_dict_items(dict_layout)
        
        layout.addWidget(dict_frame)
        
        # Order info
        order_info = ThemedLabel("✓ Checked dictionaries will auto-add definitions in order shown", "muted")
        layout.addWidget(order_info)
        
        layout.addStretch()
        return tab
    
    def _apply_styling(self):
        """Apply theme styling to dialog."""
        if not ANKI_AVAILABLE:
            return
        
        theme = self.theme
        
        # Calculate colors for scroll bars
        handle_color = self._adjust_color_brightness(theme.border_color, 1.3)
        handle_hover = self._adjust_color_brightness(theme.accent_color, 0.8)
        
        # Dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme.background_color};
                color: {theme.text_primary};
            }}
            QLineEdit, QTextEdit {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {theme.accent_color};
            }}
            QCheckBox {{
                color: {theme.text_primary};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {theme.border_color};
                border-radius: 3px;
                background-color: {theme.panel_color};
            }}
            QCheckBox::indicator:checked {{
                background-color: {theme.accent_color};
                border-color: {theme.accent_color};
            }}
            QComboBox {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                padding: 8px 12px;
                min-width: 120px;
                min-height: 24px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {theme.border_color};
                background-color: {theme.panel_color};
                border-top-right-radius: {theme.border_radius}px;
                border-bottom-right-radius: {theme.border_radius}px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid {theme.text_primary};
                width: 6px;
                height: 6px;
                border-top: none;
                border-left: none;
                margin-top: -2px;
            }}
            QScrollArea {{
                background: {theme.panel_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
            }}
            QWidget#mappingContainer {{
                background: {theme.panel_color};
            }}
            QScrollBar:vertical {{
                background: {theme.panel_color};
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {handle_color};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {handle_hover};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: {theme.panel_color};
                height: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background: {handle_color};
                border-radius: 6px;
                min-width: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {handle_hover};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)
    
    def _adjust_color_brightness(self, hex_color: str, factor: float) -> str:
        """Adjust the brightness of a hex color."""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return hex_color
    
    def _on_template_changed(self):
        """Handle card template selection change."""
        # Clear previous mapping widgets
        while self.mapping_layout.count():
            item = self.mapping_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.field_mappings = {}
        
        # Get selected template
        template_id = self.template_combo.currentData()
        if not template_id:
            return
        
        template = self.templates.get(template_id)
        if not template:
            return
        
        self.selected_template = template_id
        
        # Available dictionary outputs
        dict_outputs = [
            "Word", "Phonetic", "Definition", "Example Sentence", 
            "Image", "Audio", "Google Image", "Forvo Audio"
        ]
        
        # Create field mapping for each template field
        fields = template.get("fields", [])
        
        # Remove the stretch before adding new items
        if self.mapping_layout.count() > 0:
            self.mapping_layout.takeAt(self.mapping_layout.count() - 1)
        
        for i, field_name in enumerate(fields):
            # Create mapping row
            mapping_frame = ThemedFrame()
            mapping_frame.setMaximumHeight(60)
            mapping_layout = QHBoxLayout(mapping_frame)
            mapping_layout.setContentsMargins(16, 12, 16, 12)
            mapping_layout.setSpacing(16)
            
            # Card field label (fixed width for alignment)
            field_label = ThemedLabel(f"{field_name}:", "primary")
            field_label.setFixedWidth(100)
            field_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            mapping_layout.addWidget(field_label)
            
            # Arrow
            arrow_label = ThemedLabel("←", "muted")
            arrow_label.setFixedWidth(20)
            arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            mapping_layout.addWidget(arrow_label)
            
            # Dictionary source dropdown
            source_combo = QComboBox()
            source_combo.setFixedHeight(32)
            source_combo.setFixedWidth(160)
            source_combo.addItem("Select source...", "")
            
            # Add dictionary outputs
            for output in dict_outputs:
                source_combo.addItem(output, output.lower().replace(" ", "_"))
            
            # Auto-select logical mappings
            if field_name.lower() in ["word", "front"]:
                source_combo.setCurrentText("Word")
            elif field_name.lower() in ["phonetic", "reading"]:
                source_combo.setCurrentText("Phonetic")
            elif field_name.lower() in ["definition", "meaning", "back"]:
                source_combo.setCurrentText("Definition")
            elif field_name.lower() in ["example", "sentence"]:
                source_combo.setCurrentText("Example Sentence")
            
            mapping_layout.addWidget(source_combo)
            
            # "OR" label
            or_label = ThemedLabel("OR", "muted")
            or_label.setFixedWidth(30)
            or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            mapping_layout.addWidget(or_label)
            
            # Custom input (optional override)
            custom_input = QLineEdit()
            custom_input.setFixedHeight(32)
            custom_input.setPlaceholderText("Manual override (optional)...")
            custom_input.setToolTip("Enter custom text to override dictionary data for this field")
            mapping_layout.addWidget(custom_input, 1)
            
            # Insert before the stretch
            self.mapping_layout.insertWidget(i, mapping_frame)
            
            # Store mapping controls
            self.field_mappings[field_name] = {
                'source_combo': source_combo,
                'custom_input': custom_input
            }
        
        # Re-add stretch at the end
        self.mapping_layout.addStretch()
        
        logger.debug(f"Template changed to: {template_id} with {len(fields)} field mappings")
    
    def _validate_fields(self) -> tuple[bool, str]:
        """
        Validate that all required fields are filled.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check word field
        word = self.word_input.text().strip()
        if not word:
            return False, "Please enter a word to export"
        
        # Check dictionaries selected
        selected_dicts = [d for d in self.dict_order if self.dict_checks[d].isChecked()]
        if not selected_dicts:
            return False, "Please select at least one dictionary"
        
        # Check template selected
        if not self.selected_template:
            return False, "Please select a card template"
        
        # Check required template fields have mappings
        template = self.templates.get(self.selected_template, {})
        required_fields = template.get("fields", [])
        
        for field_name in required_fields:
            if field_name in self.field_mappings:
                mapping = self.field_mappings[field_name]
                source_selected = mapping['source_combo'].currentData()
                custom_text = mapping['custom_input'].text().strip()
                
                if not source_selected and not custom_text:
                    return False, f"Please map a source for '{field_name}' field"
        
        return True, ""
    
    def _create_dict_items(self, dict_layout: QVBoxLayout):
        """Create dictionary items in the layout."""
        self.dict_checks = {}
        
        for i, dict_name in enumerate(self.dict_order):
            is_checked = (dict_name == self.source_dict)
            
            dict_row = QHBoxLayout()
            dict_row.setSpacing(6)
            
            # Up button (small)
            up_btn = QPushButton("▲")
            up_btn.setFixedSize(20, 20)
            up_btn.setEnabled(i > 0)
            up_btn.clicked.connect(lambda checked, idx=i: self._move_dict_up(idx))
            dict_row.addWidget(up_btn)
            
            # Down button (small)
            down_btn = QPushButton("▼")
            down_btn.setFixedSize(20, 20)
            down_btn.setEnabled(i < len(self.dict_order) - 1)
            down_btn.clicked.connect(lambda checked, idx=i: self._move_dict_down(idx))
            dict_row.addWidget(down_btn)
            
            # Checkbox
            check = QCheckBox(dict_name)
            check.setChecked(is_checked)
            self.dict_checks[dict_name] = check
            dict_row.addWidget(check)
            
            dict_row.addStretch()
            dict_layout.addLayout(dict_row)
    
    def _move_dict_up(self, index: int):
        """Move dictionary up in priority order."""
        if index > 0:
            self.dict_order[index], self.dict_order[index - 1] = self.dict_order[index - 1], self.dict_order[index]
            self._rebuild_dict_list()
    
    def _move_dict_down(self, index: int):
        """Move dictionary down in priority order."""
        if index < len(self.dict_order) - 1:
            self.dict_order[index], self.dict_order[index + 1] = self.dict_order[index + 1], self.dict_order[index]
            self._rebuild_dict_list()
    
    def _rebuild_dict_list(self):
        """Rebuild the dictionary list after reordering."""
        # Clear existing items
        while self.dict_layout_ref.count():
            item = self.dict_layout_ref.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
        
        # Recreate items
        self._create_dict_items(self.dict_layout_ref)
    
    def _paste_image(self):
        """Paste image from clipboard."""
        if not ANKI_AVAILABLE:
            return
        
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()
        
        if pixmap.isNull():
            self.image_status.setText("No image in clipboard")
            logger.warning("No image found in clipboard")
            return
        
        self.image_data = pixmap
        self.image_status.setText(f"Image pasted ({pixmap.width()}x{pixmap.height()}px)")
        logger.debug(f"Image pasted: {pixmap.width()}x{pixmap.height()}")
    
    def _paste_audio(self):
        """Paste audio from clipboard."""
        if not ANKI_AVAILABLE:
            return
        
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        # Check for audio file paths or data
        if mime_data.hasUrls():
            urls = mime_data.urls()
            for url in urls:
                path = url.toLocalFile()
                if path.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a')):
                    self.audio_data = path
                    self.audio_status.setText(f"Audio pasted ({path.split('/')[-1]})")
                    logger.debug(f"Audio pasted: {path}")
                    return
        
        self.audio_status.setText("No audio file in clipboard")
        logger.warning("No audio file found in clipboard")
    
    def _export(self):
        """Export word to Anki."""
        # Validate all fields
        is_valid, error_msg = self._validate_fields()
        if not is_valid:
            self.validation_status.setText(f"❌ {error_msg}")
            QMessageBox.warning(self, "Export Error", error_msg)
            return
        
        word = self.word_input.text().strip()
        example = self.example_input.toPlainText().strip()
        
        # Get selected dictionaries in order
        selected_dicts = [d for d in self.dict_order if self.dict_checks[d].isChecked()]
        
        # Get template field mappings
        template_fields = {}
        for field_name, mapping in self.field_mappings.items():
            source = mapping['source_combo'].currentData()
            custom = mapping['custom_input'].text().strip()
            
            # Use custom text if provided, otherwise use mapped source
            if custom:
                template_fields[field_name] = custom
            elif source:
                template_fields[field_name] = f"{{mapped:{source}}}"
            else:
                template_fields[field_name] = ""
        
        # Get selected deck
        selected_deck = self.deck_combo.currentData()
        
        # Prepare export data
        export_data = {
            "word": word,
            "example": example,
            "deck": selected_deck,
            "dictionaries": selected_dicts,
            "template": self.selected_template,
            "template_fields": template_fields,
            "image": self.image_data,
            "audio": self.audio_data
        }
        
        logger.info(f"Exporting word: {word} with template: {self.selected_template}")
        logger.debug(f"Export data: {export_data}")
        
        # Show success message
        dict_list = ", ".join(selected_dicts)
        template_name = self.templates.get(self.selected_template, {}).get("name", "Unknown")
        QMessageBox.information(
            self,
            "Export Successful",
            f"Word '{word}' has been exported to Anki!\n\n"
            f"Deck: {selected_deck}\n"
            f"Template: {template_name}\n"
            f"Dictionaries: {dict_list}\n"
            f"Image: {'Yes' if self.image_data else 'No'}\n"
            f"Audio: {'Yes' if self.audio_data else 'No'}"
        )
        
        self.validation_status.setText("✅ Export successful!")
        self.accept()
    
    def get_export_data(self) -> Dict[str, Any]:
        """Get the export data."""
        selected_dicts = [d for d in self.dict_order if self.dict_checks[d].isChecked()]
        selected_deck = self.deck_combo.currentData()
        
        # Get template field mappings
        template_fields = {}
        for field_name, mapping in self.field_mappings.items():
            source = mapping['source_combo'].currentData()
            custom = mapping['custom_input'].text().strip()
            
            if custom:
                template_fields[field_name] = custom
            elif source:
                template_fields[field_name] = f"{{mapped:{source}}}"
            else:
                template_fields[field_name] = ""
        
        return {
            "word": self.word_input.text().strip(),
            "example": self.example_input.toPlainText().strip(),
            "deck": selected_deck,
            "dictionaries": selected_dicts,
            "template": self.selected_template,
            "template_fields": template_fields,
            "image": self.image_data,
            "audio": self.audio_data
        }


def show_export_dialog(word: str = "", source_dict: str = "", definitions: list = None, 
                       templates: Optional[Dict[str, Dict]] = None, parent: Optional[QWidget] = None) -> Optional[Dict[str, Any]]:
    """
    Show export dialog and return export data if accepted.
    
    Args:
        word: Initial word to export
        source_dict: Source dictionary name (e.g., "JMdict", "大辞林")
        definitions: List of definitions from source dictionary
        templates: Custom card templates (uses defaults if None)
        parent: Parent widget
        
    Returns:
        Export data dictionary if accepted, None if cancelled
    """
    dialog = ExportDialog(word, source_dict, definitions, templates, parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_export_data()
    return None
