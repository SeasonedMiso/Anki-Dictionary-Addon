# -*- coding: utf-8 -*-
"""
Export UI System - Main Components.

This module provides the complete export UI system for managing Anki card exports.
Following the UI-first approach, these components work with mock data to provide
a complete export workflow before connecting to real Anki integration.

COMPONENTS PROVIDED:
- ExportQueueWidget: Manage pending card exports with drag-and-drop
- ExportPreviewPanel: Preview cards before export with Anki-accurate rendering
- ExportHistoryWidget: Track and manage previously exported cards
- ExportControlPanel: Main control interface for export operations

All components use the centralized theming system and integrate with the
existing modern UI architecture.
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import logging
import json

try:
    from aqt.qt import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QListWidget, QListWidgetItem, QScrollArea, QFrame,
        QProgressBar, QTextEdit, QSplitter, pyqtSignal, Qt,
        QSizePolicy, QTimer, QApplication, QMenu, QAction
    )
    ANKI_AVAILABLE = True
except ImportError:
    # Mock classes for testing - define minimal mocks
    ANKI_AVAILABLE = False
    
    class QWidget: pass
    class QVBoxLayout: pass
    class QHBoxLayout: pass
    class QLabel: pass
    class QPushButton: pass
    class QListWidget: pass
    class QListWidgetItem: pass
    class QScrollArea: pass
    class QFrame: pass
    class QProgressBar: pass
    class QTextEdit: pass
    class QSplitter: pass
    class QMenu: pass
    class QAction: pass
    class QApplication: pass
    class QSizePolicy: pass
    class QTimer: pass
    class pyqtSignal:
        def __init__(self, *args): pass
    class Qt: pass

from .styling import ThemeColors, StyleGenerator, get_theme_manager
from .base_widgets import (
    ThemedWidget, ThemedButton, ThemedLabel, ThemedLineEdit, ThemedFrame,
    ActionButton, StatusMessage
)
from .export_mock_data import (
    SAMPLE_QUEUE_ITEMS, SAMPLE_EXPORT_HISTORY, DEFAULT_TEMPLATES,
    ExportQueueItem, ExportHistoryRecord, CardTemplate
)

# LEGACY INTEGRATION: Import existing services (to be optimized later)
try:
    from ..legacy.services import ExportService, SearchService
    from ..legacy.config import ConfigManager
    LEGACY_SERVICES_AVAILABLE = True
except ImportError:
    # Fallback for development/testing
    LEGACY_SERVICES_AVAILABLE = False
    ExportService = None
    SearchService = None
    ConfigManager = None

logger = logging.getLogger(__name__)


class ExportQueueWidget(ThemedWidget):
    """
    Export queue management widget with drag-and-drop reordering.
    
    Features:
    - List view of queued export items
    - Individual item preview and editing
    - Batch selection and operations
    - Duplicate detection and merging
    - Queue persistence across sessions
    
    Signals:
        itemAdded(dict): New item added to queue
        itemRemoved(str): Item removed from queue
        batchExportRequested(list): Batch export initiated
        itemSelected(dict): Item selected for preview
    """
    
    itemAdded = pyqtSignal(dict)
    itemRemoved = pyqtSignal(str)
    batchExportRequested = pyqtSignal(list)
    itemSelected = pyqtSignal(dict)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize export queue widget."""
        super().__init__(parent)
        
        self.queue_items = []
        self.selected_items = []
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Header with title and controls
        header_layout = self._create_header()
        layout.addLayout(header_layout)
        
        # Queue list
        self.queue_list = QListWidget()
        self.queue_list.setMinimumHeight(200)
        self.queue_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.queue_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.queue_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.queue_list)
        
        # Action buttons
        actions_layout = self._create_action_buttons()
        layout.addLayout(actions_layout)
        
        # Status message
        self.status_message = StatusMessage()
        layout.addWidget(self.status_message)
        
        # Load sample data
        self._load_sample_data()
        
        # Apply styling
        self._apply_styling()
        
        logger.debug("ExportQueueWidget initialized")
    
    def _create_header(self) -> QHBoxLayout:
        """Create header with title and queue controls."""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        # Title
        title = ThemedLabel("Export Queue", "header")
        layout.addWidget(title)
        
        # Queue count
        self.count_label = ThemedLabel("0 items", "muted")
        layout.addWidget(self.count_label)
        
        layout.addStretch()
        
        # Clear all button
        clear_btn = ThemedButton("Clear All", "error")
        clear_btn.clicked.connect(self.clear_queue)
        layout.addWidget(clear_btn)
        
        return layout
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Create action buttons for queue operations."""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Remove selected
        self.remove_btn = ThemedButton("Remove Selected", "warning")
        self.remove_btn.clicked.connect(self._remove_selected)
        self.remove_btn.setEnabled(False)
        layout.addWidget(self.remove_btn)
        
        # Export selected
        self.export_btn = ThemedButton("Export Selected", "success")
        self.export_btn.clicked.connect(self._export_selected)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
        
        layout.addStretch()
        
        # Export all
        export_all_btn = ThemedButton("Export All", "primary")
        export_all_btn.clicked.connect(self._export_all)
        layout.addWidget(export_all_btn)
        
        return layout
    
    def _apply_styling(self):
        """Apply themed styling to queue list."""
        if not ANKI_AVAILABLE:
            return
        
        theme = self.theme_manager.current_theme
        style_gen = StyleGenerator(theme)
        
        # Queue list styling
        list_style = f"""
            QListWidget {{
                background-color: {theme.panel_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                color: {theme.text_primary};
                font-size: {theme.get_font_size('base')}px;
                selection-background-color: {theme.accent_color};
                selection-color: white;
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {style_gen.adjust_color_brightness(theme.border_color, 0.7)};
                background-color: transparent;
            }}
            QListWidget::item:hover {{
                background-color: {style_gen.adjust_color_brightness(theme.panel_color, 1.1)};
            }}
            QListWidget::item:selected {{
                background-color: {theme.accent_color};
                color: white;
            }}
        """
        self.queue_list.setStyleSheet(list_style)
    
    def _load_sample_data(self):
        """Load sample queue items for demonstration."""
        for item_data in SAMPLE_QUEUE_ITEMS:
            self.add_item(item_data)
    
    def add_item(self, word_data: dict) -> None:
        """
        Add item to export queue.
        
        Args:
            word_data: Dictionary containing word information
        """
        # Check for duplicates
        word = word_data.get('word', '')
        existing_item = self._find_item_by_word(word)
        
        if existing_item:
            self._handle_duplicate(existing_item, word_data)
            return
        
        # Create queue item
        queue_item = ExportQueueItem(
            id=f"queue_{len(self.queue_items):03d}",
            word=word,
            phonetic=word_data.get('phonetic', ''),
            definitions=word_data.get('definitions', []),
            source_dictionary=word_data.get('source_dictionary', 'Unknown'),
            template_id=word_data.get('template_id', 'default_japanese'),
            custom_fields=word_data.get('custom_fields', {}),
            added_timestamp=datetime.now()
        )
        
        self.queue_items.append(queue_item)
        
        # Add to list widget
        list_item = QListWidgetItem()
        list_item.setText(self._format_queue_item(queue_item))
        list_item.setData(Qt.ItemDataRole.UserRole, queue_item.id)
        self.queue_list.addItem(list_item)
        
        # Update count
        self._update_count()
        
        # Emit signal
        self.itemAdded.emit(word_data)
        
        self.status_message.show_success(f"Added '{word}' to export queue")
        logger.debug(f"Added item to queue: {word}")
    
    def remove_item(self, word_id: str) -> None:
        """
        Remove item from export queue.
        
        Args:
            word_id: ID of item to remove
        """
        # Find and remove from queue_items
        item_to_remove = None
        for item in self.queue_items:
            if item.id == word_id:
                item_to_remove = item
                break
        
        if not item_to_remove:
            return
        
        self.queue_items.remove(item_to_remove)
        
        # Remove from list widget
        for i in range(self.queue_list.count()):
            list_item = self.queue_list.item(i)
            if list_item.data(Qt.ItemDataRole.UserRole) == word_id:
                self.queue_list.takeItem(i)
                break
        
        # Update count
        self._update_count()
        
        # Emit signal
        self.itemRemoved.emit(word_id)
        
        self.status_message.show_info(f"Removed '{item_to_remove.word}' from queue")
        logger.debug(f"Removed item from queue: {item_to_remove.word}")
    
    def get_selected_items(self) -> List[dict]:
        """
        Get currently selected queue items.
        
        Returns:
            List of selected item dictionaries
        """
        selected_items = []
        for list_item in self.queue_list.selectedItems():
            item_id = list_item.data(Qt.ItemDataRole.UserRole)
            queue_item = self._find_item_by_id(item_id)
            if queue_item:
                selected_items.append(self._queue_item_to_dict(queue_item))
        
        return selected_items
    
    def clear_queue(self) -> None:
        """Clear all items from export queue."""
        if not self.queue_items:
            return
        
        count = len(self.queue_items)
        self.queue_items.clear()
        self.queue_list.clear()
        self._update_count()
        
        self.status_message.show_info(f"Cleared {count} items from queue")
        logger.debug(f"Cleared export queue ({count} items)")
    
    def _find_item_by_word(self, word: str) -> Optional[ExportQueueItem]:
        """Find queue item by word."""
        for item in self.queue_items:
            if item.word == word:
                return item
        return None
    
    def _find_item_by_id(self, item_id: str) -> Optional[ExportQueueItem]:
        """Find queue item by ID."""
        for item in self.queue_items:
            if item.id == item_id:
                return item
        return None
    
    def _handle_duplicate(self, existing_item: ExportQueueItem, new_data: dict):
        """Handle duplicate word in queue."""
        # For now, just show a message - could implement merge dialog
        self.status_message.show_warning(
            f"'{existing_item.word}' is already in queue"
        )
    
    def _format_queue_item(self, item: ExportQueueItem) -> str:
        """Format queue item for display in list."""
        phonetic = f"[{item.phonetic}]" if item.phonetic else ""
        def_count = len(item.definitions)
        def_text = f"{def_count} definition{'s' if def_count != 1 else ''}"
        
        return f"{item.word} {phonetic}\n{def_text} • {item.source_dictionary}"
    
    def _queue_item_to_dict(self, item: ExportQueueItem) -> dict:
        """Convert queue item to dictionary."""
        return {
            'id': item.id,
            'word': item.word,
            'phonetic': item.phonetic,
            'definitions': item.definitions,
            'source_dictionary': item.source_dictionary,
            'template_id': item.template_id,
            'custom_fields': item.custom_fields,
            'added_timestamp': item.added_timestamp.isoformat()
        }
    
    def _update_count(self):
        """Update queue count display."""
        count = len(self.queue_items)
        self.count_label.setText(f"{count} item{'s' if count != 1 else ''}")
    
    def _on_selection_changed(self):
        """Handle selection change in queue list."""
        selected_items = self.queue_list.selectedItems()
        has_selection = len(selected_items) > 0
        
        # Update button states
        self.remove_btn.setEnabled(has_selection)
        self.export_btn.setEnabled(has_selection)
        
        # Emit selection signal for preview
        if selected_items:
            item_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
            queue_item = self._find_item_by_id(item_id)
            if queue_item:
                self.itemSelected.emit(self._queue_item_to_dict(queue_item))
    
    def _on_item_double_clicked(self, list_item: QListWidgetItem):
        """Handle double-click on queue item."""
        item_id = list_item.data(Qt.ItemDataRole.UserRole)
        queue_item = self._find_item_by_id(item_id)
        if queue_item:
            # TODO: Open item editor dialog
            self.status_message.show_info(f"Edit '{queue_item.word}' (coming soon)")
    
    def _remove_selected(self):
        """Remove selected items from queue."""
        selected_items = self.queue_list.selectedItems()
        if not selected_items:
            return
        
        # Remove items (in reverse order to maintain indices)
        for list_item in reversed(selected_items):
            item_id = list_item.data(Qt.ItemDataRole.UserRole)
            self.remove_item(item_id)
    
    def _export_selected(self):
        """Export selected items."""
        selected_data = self.get_selected_items()
        if selected_data:
            self.batchExportRequested.emit(selected_data)
    
    def _export_all(self):
        """Export all items in queue."""
        if self.queue_items:
            all_items = [self._queue_item_to_dict(item) for item in self.queue_items]
            self.batchExportRequested.emit(all_items)
    
    def update_theme(self, theme: ThemeColors):
        """Update widget styling with new theme."""
        self._apply_styling()


class ExportPreviewPanel(ThemedWidget):
    """
    Export preview panel with Anki-accurate card rendering.
    
    Features:
    - Anki-accurate card rendering
    - Navigation through queued items
    - Error detection and highlighting
    - Individual card editing
    - Export confirmation workflow
    
    Signals:
        exportConfirmed(list): User confirmed export
        editRequested(str): Edit specific card
        navigationChanged(int): Current item index changed
    """
    
    exportConfirmed = pyqtSignal(list)
    editRequested = pyqtSignal(str)
    navigationChanged = pyqtSignal(int)
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize export preview panel."""
        super().__init__(parent)
        
        self.preview_items = []
        self.current_index = 0
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Header with navigation
        header_layout = self._create_header()
        layout.addLayout(header_layout)
        
        # Preview area
        self.preview_area = self._create_preview_area()
        layout.addWidget(self.preview_area, 1)
        
        # Confirmation buttons
        confirm_layout = self._create_confirmation_buttons()
        layout.addLayout(confirm_layout)
        
        # Status message
        self.status_message = StatusMessage()
        layout.addWidget(self.status_message)
        
        # Load sample preview
        self._load_sample_preview()
        
        logger.debug("ExportPreviewPanel initialized")
    
    def _create_header(self) -> QHBoxLayout:
        """Create header with navigation controls."""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        # Title
        title = ThemedLabel("Export Preview", "header")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Navigation controls
        self.prev_btn = ThemedButton("◀ Previous")
        self.prev_btn.clicked.connect(self._navigate_previous)
        layout.addWidget(self.prev_btn)
        
        self.nav_label = ThemedLabel("1 of 1", "muted")
        layout.addWidget(self.nav_label)
        
        self.next_btn = ThemedButton("Next ▶")
        self.next_btn.clicked.connect(self._navigate_next)
        layout.addWidget(self.next_btn)
        
        return layout
    
    def _create_preview_area(self) -> QWidget:
        """Create card preview area."""
        container = ThemedFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Card front
        front_label = ThemedLabel("Front:", "muted")
        layout.addWidget(front_label)
        
        self.front_preview = QTextEdit()
        self.front_preview.setMaximumHeight(150)
        self.front_preview.setReadOnly(True)
        layout.addWidget(self.front_preview)
        
        # Card back
        back_label = ThemedLabel("Back:", "muted")
        layout.addWidget(back_label)
        
        self.back_preview = QTextEdit()
        self.back_preview.setMaximumHeight(200)
        self.back_preview.setReadOnly(True)
        layout.addWidget(self.back_preview)
        
        # Apply styling
        self._apply_preview_styling()
        
        return container
    
    def _create_confirmation_buttons(self) -> QHBoxLayout:
        """Create export confirmation buttons."""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Edit button
        edit_btn = ThemedButton("Edit Card", "warning")
        edit_btn.clicked.connect(self._edit_current_card)
        layout.addWidget(edit_btn)
        
        layout.addStretch()
        
        # Cancel button
        cancel_btn = ThemedButton("Cancel")
        cancel_btn.clicked.connect(self._cancel_export)
        layout.addWidget(cancel_btn)
        
        # Confirm export button
        self.confirm_btn = ThemedButton("Confirm Export", "success")
        self.confirm_btn.clicked.connect(self._confirm_export)
        layout.addWidget(self.confirm_btn)
        
        return layout
    
    def _apply_preview_styling(self):
        """Apply styling to preview text areas."""
        if not ANKI_AVAILABLE:
            return
        
        theme = self.theme_manager.current_theme
        
        preview_style = f"""
            QTextEdit {{
                background-color: {theme.background_color};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                color: {theme.text_primary};
                font-size: {theme.get_font_size('base')}px;
                padding: 12px;
            }}
        """
        
        self.front_preview.setStyleSheet(preview_style)
        self.back_preview.setStyleSheet(preview_style)
    
    def _load_sample_preview(self):
        """Load sample preview data."""
        # Use first sample queue item
        if SAMPLE_QUEUE_ITEMS:
            self.load_queue_items([SAMPLE_QUEUE_ITEMS[0]])
    
    def load_queue_items(self, items: List[dict]) -> None:
        """
        Load queue items for preview.
        
        Args:
            items: List of queue item dictionaries
        """
        self.preview_items = items
        self.current_index = 0
        self._update_navigation()
        self._update_preview()
        
        logger.debug(f"Loaded {len(items)} items for preview")
    
    def navigate_to_item(self, index: int) -> None:
        """
        Navigate to specific item index.
        
        Args:
            index: Item index to navigate to
        """
        if 0 <= index < len(self.preview_items):
            self.current_index = index
            self._update_navigation()
            self._update_preview()
            self.navigationChanged.emit(index)
    
    def _navigate_previous(self):
        """Navigate to previous item."""
        if self.current_index > 0:
            self.navigate_to_item(self.current_index - 1)
    
    def _navigate_next(self):
        """Navigate to next item."""
        if self.current_index < len(self.preview_items) - 1:
            self.navigate_to_item(self.current_index + 1)
    
    def _update_navigation(self):
        """Update navigation controls."""
        if not self.preview_items:
            self.nav_label.setText("No items")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.confirm_btn.setEnabled(False)
            return
        
        total = len(self.preview_items)
        current = self.current_index + 1
        
        self.nav_label.setText(f"{current} of {total}")
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < total - 1)
        self.confirm_btn.setEnabled(True)
    
    def _update_preview(self):
        """Update card preview display."""
        if not self.preview_items or self.current_index >= len(self.preview_items):
            self.front_preview.setHtml("<p>No item to preview</p>")
            self.back_preview.setHtml("<p>No item to preview</p>")
            return
        
        item = self.preview_items[self.current_index]
        
        # Generate card preview using template
        front_html = self._generate_card_front(item)
        back_html = self._generate_card_back(item)
        
        self.front_preview.setHtml(front_html)
        self.back_preview.setHtml(back_html)
    
    def _generate_card_front(self, item: dict) -> str:
        """Generate front side of card."""
        word = item.get('word', '')
        phonetic = item.get('phonetic', '')
        
        if phonetic:
            return f"""
            <div style="text-align: center; font-size: 24px; color: #e6e6e6;">
                <div style="font-size: 32px; margin-bottom: 8px;">{word}</div>
                <div style="font-size: 18px; color: #9aa0ad;">[{phonetic}]</div>
            </div>
            """
        else:
            return f"""
            <div style="text-align: center; font-size: 32px; color: #e6e6e6;">
                {word}
            </div>
            """
    
    def _generate_card_back(self, item: dict) -> str:
        """Generate back side of card."""
        word = item.get('word', '')
        phonetic = item.get('phonetic', '')
        definitions = item.get('definitions', [])
        
        html_parts = []
        
        # Word and phonetic
        if phonetic:
            html_parts.append(f"""
            <div style="text-align: center; margin-bottom: 16px;">
                <div style="font-size: 24px; color: #e6e6e6;">{word}</div>
                <div style="font-size: 16px; color: #9aa0ad;">[{phonetic}]</div>
            </div>
            """)
        else:
            html_parts.append(f"""
            <div style="text-align: center; font-size: 24px; color: #e6e6e6; margin-bottom: 16px;">
                {word}
            </div>
            """)
        
        # Definitions
        if definitions:
            html_parts.append('<div style="color: #e6e6e6;">')
            for i, defn in enumerate(definitions, 1):
                def_type = defn.get('type', '')
                def_text = defn.get('text', '')
                html_parts.append(f"""
                <div style="margin-bottom: 8px;">
                    <span style="background: #4a9eff; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; font-weight: bold;">{def_type}</span>
                    <span style="margin-left: 8px;">{def_text}</span>
                </div>
                """)
            html_parts.append('</div>')
        
        return ''.join(html_parts)
    
    def _edit_current_card(self):
        """Edit current card."""
        if self.preview_items and self.current_index < len(self.preview_items):
            item = self.preview_items[self.current_index]
            item_id = item.get('id', '')
            self.editRequested.emit(item_id)
    
    def _cancel_export(self):
        """Cancel export operation."""
        self.status_message.show_info("Export cancelled")
    
    def _confirm_export(self):
        """Confirm export of all items."""
        if self.preview_items:
            self.exportConfirmed.emit(self.preview_items)
            self.status_message.show_success(f"Confirmed export of {len(self.preview_items)} items")
    
    def update_theme(self, theme: ThemeColors):
        """Update widget styling with new theme."""
        self._apply_preview_styling()