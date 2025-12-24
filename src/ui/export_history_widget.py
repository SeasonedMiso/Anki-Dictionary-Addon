# -*- coding: utf-8 -*-
"""
Export History Widget - Track and manage previously exported cards.

This widget provides a complete history view of all card exports with filtering,
search, and management capabilities. It integrates with the export system to
provide insights into export patterns and allow re-export of previous items.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

try:
    from aqt.qt import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
        QComboBox, QDateEdit, QCheckBox, pyqtSignal, Qt, QMenu, QAction
    )
    ANKI_AVAILABLE = True
except ImportError:
    # Mock classes for testing
    ANKI_AVAILABLE = False
    class QWidget: pass
    class QVBoxLayout: pass
    class QHBoxLayout: pass
    class QLabel: pass
    class QPushButton: pass
    class QTableWidget: pass
    class QTableWidgetItem: pass
    class QHeaderView: pass
    class QAbstractItemView: pass
    class QComboBox: pass
    class QDateEdit: pass
    class QCheckBox: pass
    class QMenu: pass
    class QAction: pass
    class pyqtSignal:
        def __init__(self, *args): pass
    class Qt: pass

from .styling import ThemeColors, StyleGenerator, get_theme_manager
from .base_widgets import (
    ThemedWidget, ThemedButton, ThemedLabel, ThemedLineEdit, ThemedFrame,
    StatusMessage
)
from .export_mock_data import SAMPLE_EXPORT_HISTORY, ExportHistoryRecord

logger = logging.getLogger(__name__)


class ExportHistoryWidget(ThemedWidget):
    """
    Export history management widget.
    
    Features:
    - Tabular view of export history
    - Filtering by date, template, deck, success status
    - Search by word
    - Re-export functionality
    - Export statistics
    - Context menu for individual records
    
    Signals:
        reExportRequested(str): Re-export specific word
        recordSelected(dict): History record selected
        statisticsRequested(): Show detailed statistics
    """
    
    reExportRequested = pyqtSignal(str)
    recordSelected = pyqtSignal(dict)
    statisticsRequested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize export history widget."""
        super().__init__(parent)
        
        self.history_records = []
        self.filtered_records = []
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Header with title and controls
        header_layout = self._create_header()
        layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = self._create_filters()
        layout.addLayout(filter_layout)
        
        # History table
        self.history_table = self._create_history_table()
        layout.addWidget(self.history_table, 1)
        
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
        
        logger.debug("ExportHistoryWidget initialized")
    
    def _create_header(self) -> QHBoxLayout:
        """Create header with title and summary stats."""
        layout = QHBoxLayout()
        layout.setSpacing(12)
        
        # Title
        title = ThemedLabel("Export History", "header")
        layout.addWidget(title)
        
        # Stats summary
        self.stats_label = ThemedLabel("0 exports", "muted")
        layout.addWidget(self.stats_label)
        
        layout.addStretch()
        
        # Statistics button
        stats_btn = ThemedButton("📊 Statistics", "primary")
        stats_btn.clicked.connect(self._show_statistics)
        layout.addWidget(stats_btn)
        
        # Clear history button
        clear_btn = ThemedButton("Clear History", "error")
        clear_btn.clicked.connect(self._clear_history)
        layout.addWidget(clear_btn)
        
        return layout
    
    def _create_filters(self) -> QHBoxLayout:
        """Create filter controls."""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Search by word
        search_label = ThemedLabel("Search:")
        layout.addWidget(search_label)
        
        self.search_input = ThemedLineEdit()
        self.search_input.setPlaceholderText("Search by word...")
        self.search_input.textChanged.connect(self._apply_filters)
        layout.addWidget(self.search_input)
        
        # Template filter
        template_label = ThemedLabel("Template:")
        layout.addWidget(template_label)
        
        self.template_filter = QComboBox()
        self.template_filter.addItem("All Templates")
        self.template_filter.currentTextChanged.connect(self._apply_filters)
        layout.addWidget(self.template_filter)
        
        # Status filter
        status_label = ThemedLabel("Status:")
        layout.addWidget(status_label)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Success", "Failed"])
        self.status_filter.currentTextChanged.connect(self._apply_filters)
        layout.addWidget(self.status_filter)
        
        # Show only recent
        self.recent_only = QCheckBox("Last 7 days")
        self.recent_only.stateChanged.connect(self._apply_filters)
        layout.addWidget(self.recent_only)
        
        layout.addStretch()
        
        return layout
    
    def _create_history_table(self) -> QTableWidget:
        """Create history table widget."""
        table = QTableWidget()
        
        # Set up columns
        headers = ["Word", "Template", "Deck", "Date", "Status", "Note ID"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Table settings
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        
        # Column sizing
        header = table.horizontalHeader()
        if hasattr(header, 'setSectionResizeMode'):
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Word
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Template
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # Deck
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Date
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Status
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Note ID
        
        # Connect signals
        table.itemSelectionChanged.connect(self._on_selection_changed)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self._show_context_menu)
        
        return table
    
    def _create_action_buttons(self) -> QHBoxLayout:
        """Create action buttons."""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Re-export selected
        self.reexport_btn = ThemedButton("Re-export Selected", "success")
        self.reexport_btn.clicked.connect(self._reexport_selected)
        self.reexport_btn.setEnabled(False)
        layout.addWidget(self.reexport_btn)
        
        # View in Anki
        self.view_anki_btn = ThemedButton("View in Anki", "primary")
        self.view_anki_btn.clicked.connect(self._view_in_anki)
        self.view_anki_btn.setEnabled(False)
        layout.addWidget(self.view_anki_btn)
        
        layout.addStretch()
        
        # Refresh button
        refresh_btn = ThemedButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_history)
        layout.addWidget(refresh_btn)
        
        return layout
    
    def _apply_styling(self):
        """Apply themed styling to table and filters."""
        if not ANKI_AVAILABLE:
            return
        
        theme = self.theme_manager.current_theme
        style_gen = StyleGenerator(theme)
        
        # Table styling
        table_style = f"""
            QTableWidget {{
                background-color: {theme.panel_color};
                alternate-background-color: {style_gen.adjust_color_brightness(theme.panel_color, 0.95)};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                gridline-color: {theme.border_color};
                selection-background-color: {theme.accent_color};
                selection-color: white;
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {theme.accent_color};
            }}
            QHeaderView::section {{
                background-color: {style_gen.adjust_color_brightness(theme.panel_color, 1.1)};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                padding: 8px;
                font-weight: bold;
            }}
        """
        self.history_table.setStyleSheet(table_style)
        
        # Filter controls styling
        filter_style = f"""
            QComboBox {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: {theme.border_radius}px;
                padding: 4px 8px;
                min-width: 100px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {theme.text_primary};
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
        """
        
        self.template_filter.setStyleSheet(filter_style)
        self.status_filter.setStyleSheet(filter_style)
        self.recent_only.setStyleSheet(filter_style)
    
    def _load_sample_data(self):
        """Load sample history data."""
        self.history_records = SAMPLE_EXPORT_HISTORY.copy()
        self.filtered_records = self.history_records.copy()
        
        # Populate template filter
        templates = set(record.template_used for record in self.history_records)
        for template in sorted(templates):
            self.template_filter.addItem(template)
        
        self._update_table()
        self._update_stats()
    
    def add_export_record(self, record: ExportHistoryRecord) -> None:
        """
        Add new export record to history.
        
        Args:
            record: Export history record to add
        """
        self.history_records.insert(0, record)  # Add to beginning (most recent first)
        self._apply_filters()
        self._update_stats()
        
        logger.debug(f"Added export record: {record.word}")
    
    def _update_table(self):
        """Update table with filtered records."""
        self.history_table.setRowCount(len(self.filtered_records))
        
        for row, record in enumerate(self.filtered_records):
            # Word
            word_item = QTableWidgetItem(record.word)
            self.history_table.setItem(row, 0, word_item)
            
            # Template
            template_item = QTableWidgetItem(record.template_used)
            self.history_table.setItem(row, 1, template_item)
            
            # Deck
            deck_item = QTableWidgetItem(record.target_deck)
            self.history_table.setItem(row, 2, deck_item)
            
            # Date
            date_str = record.export_timestamp.strftime("%Y-%m-%d %H:%M")
            date_item = QTableWidgetItem(date_str)
            self.history_table.setItem(row, 3, date_item)
            
            # Status
            status_text = "✅ Success" if record.success else "❌ Failed"
            status_item = QTableWidgetItem(status_text)
            if not record.success:
                status_item.setToolTip(record.error_message or "Unknown error")
            self.history_table.setItem(row, 4, status_item)
            
            # Note ID
            note_id = str(record.anki_note_id) if record.anki_note_id else "—"
            note_item = QTableWidgetItem(note_id)
            self.history_table.setItem(row, 5, note_item)
            
            # Store record data
            word_item.setData(Qt.ItemDataRole.UserRole, record)
    
    def _update_stats(self):
        """Update statistics display."""
        total = len(self.history_records)
        successful = len([r for r in self.history_records if r.success])
        failed = total - successful
        
        if total == 0:
            self.stats_label.setText("No exports")
        else:
            success_rate = int(successful / total * 100)
            self.stats_label.setText(f"{total} exports • {success_rate}% success rate")
    
    def _apply_filters(self):
        """Apply current filters to history records."""
        filtered = self.history_records.copy()
        
        # Search filter
        search_text = self.search_input.text().lower().strip()
        if search_text:
            filtered = [r for r in filtered if search_text in r.word.lower()]
        
        # Template filter
        template = self.template_filter.currentText()
        if template and template != "All Templates":
            filtered = [r for r in filtered if r.template_used == template]
        
        # Status filter
        status = self.status_filter.currentText()
        if status == "Success":
            filtered = [r for r in filtered if r.success]
        elif status == "Failed":
            filtered = [r for r in filtered if not r.success]
        
        # Recent filter
        if self.recent_only.isChecked():
            week_ago = datetime.now() - timedelta(days=7)
            filtered = [r for r in filtered if r.export_timestamp >= week_ago]
        
        self.filtered_records = filtered
        self._update_table()
    
    def _on_selection_changed(self):
        """Handle table selection changes."""
        selected_items = self.history_table.selectedItems()
        has_selection = len(selected_items) > 0
        
        self.reexport_btn.setEnabled(has_selection)
        
        if has_selection:
            # Get selected record
            row = selected_items[0].row()
            word_item = self.history_table.item(row, 0)
            record = word_item.data(Qt.ItemDataRole.UserRole)
            
            # Enable/disable view in Anki based on note ID
            self.view_anki_btn.setEnabled(record.anki_note_id is not None)
            
            # Emit selection signal
            record_dict = {
                'id': record.id,
                'word': record.word,
                'template_used': record.template_used,
                'target_deck': record.target_deck,
                'export_timestamp': record.export_timestamp.isoformat(),
                'anki_note_id': record.anki_note_id,
                'success': record.success,
                'error_message': record.error_message
            }
            self.recordSelected.emit(record_dict)
        else:
            self.view_anki_btn.setEnabled(False)
    
    def _show_context_menu(self, position):
        """Show context menu for table items."""
        item = self.history_table.itemAt(position)
        if not item:
            return
        
        record = self.history_table.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        # Re-export action
        reexport_action = QAction("Re-export", self)
        reexport_action.triggered.connect(lambda: self.reExportRequested.emit(record.word))
        menu.addAction(reexport_action)
        
        # View in Anki (if note exists)
        if record.anki_note_id:
            view_action = QAction("View in Anki", self)
            view_action.triggered.connect(self._view_in_anki)
            menu.addAction(view_action)
        
        menu.addSeparator()
        
        # Copy word
        copy_action = QAction("Copy Word", self)
        copy_action.triggered.connect(lambda: self._copy_to_clipboard(record.word))
        menu.addAction(copy_action)
        
        # Show error (if failed)
        if not record.success and record.error_message:
            error_action = QAction("Show Error", self)
            error_action.triggered.connect(lambda: self._show_error_details(record))
            menu.addAction(error_action)
        
        menu.exec(self.history_table.mapToGlobal(position))
    
    def _reexport_selected(self):
        """Re-export selected record."""
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        record = self.history_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.reExportRequested.emit(record.word)
        
        self.status_message.show_info(f"Re-export requested for '{record.word}'")
    
    def _view_in_anki(self):
        """View selected record in Anki."""
        selected_items = self.history_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        record = self.history_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        if record.anki_note_id:
            # TODO: Integrate with Anki to show note
            self.status_message.show_info(f"Opening note {record.anki_note_id} in Anki (coming soon)")
        else:
            self.status_message.show_warning("No Anki note ID available")
    
    def _show_statistics(self):
        """Show detailed statistics."""
        self.statisticsRequested.emit()
        self.status_message.show_info("Detailed statistics (coming soon)")
    
    def _clear_history(self):
        """Clear export history."""
        if not self.history_records:
            return
        
        # TODO: Add confirmation dialog
        count = len(self.history_records)
        self.history_records.clear()
        self.filtered_records.clear()
        self._update_table()
        self._update_stats()
        
        self.status_message.show_info(f"Cleared {count} history records")
    
    def _refresh_history(self):
        """Refresh history from data source."""
        # TODO: Reload from actual data source
        self.status_message.show_info("History refreshed")
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        try:
            from aqt.qt import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_message.show_success(f"Copied '{text}' to clipboard")
        except Exception as e:
            self.status_message.show_error(f"Failed to copy: {str(e)}")
    
    def _show_error_details(self, record: ExportHistoryRecord):
        """Show error details for failed export."""
        error_msg = record.error_message or "Unknown error"
        self.status_message.show_error(f"Export failed: {error_msg}")
    
    def update_theme(self, theme: ThemeColors):
        """Update widget styling with new theme."""
        self._apply_styling()