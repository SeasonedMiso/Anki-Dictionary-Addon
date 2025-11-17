# -*- coding: utf-8 -*-
"""
Browser Integration module for Anki Dictionary addon.

This module handles integration with Anki's card browser,
including menu additions and bulk export functionality.
"""

from typing import Any, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..core.plugin import AnkiDictionaryPlugin

try:
    from aqt.qt import QAction
    from aqt.browser import Browser
    from anki.hooks import addHook
    ANKI_AVAILABLE = True
except ImportError:
    # For testing without Anki
    ANKI_AVAILABLE = False
    QAction = type('QAction', (object,), {})
    Browser = type('Browser', (object,), {})
    addHook = lambda *args: None


logger = logging.getLogger('anki_dictionary.ui.browser_integration')


class BrowserIntegration:
    """
    Manages integration with Anki's card browser.
    
    This class handles:
    - Browser menu additions
    - Bulk export functionality
    - Progress feedback for bulk operations
    """
    
    def __init__(self, plugin: 'AnkiDictionaryPlugin'):
        """
        Initialize browser integration.
        
        Args:
            plugin: Plugin coordinator instance
        """
        self.plugin = plugin
        self.mw = plugin.mw
        
        logger.info("Browser integration initialized")
    
    def setup_browser_hooks(self) -> None:
        """Register all browser-related hooks."""
        if not ANKI_AVAILABLE:
            logger.warning("Anki not available, skipping browser hook setup")
            return
        
        try:
            # Register browser menu setup hook
            addHook("browser.setupMenus", self._setup_browser_menu)
            
            logger.info("Browser hooks registered successfully")
            
        except Exception as e:
            logger.error(f"Error setting up browser hooks: {e}", exc_info=True)
    
    def _setup_browser_menu(self, browser: Any) -> None:
        """
        Set up browser menu items.
        
        Args:
            browser: Browser instance
        """
        try:
            # Add separator before our menu items
            browser.form.menuEdit.addSeparator()
            
            # Add "Export Definitions" action
            export_action = QAction("Export Definitions", browser)
            export_action.triggered.connect(lambda: self._launch_bulk_export(browser))
            browser.form.menuEdit.addAction(export_action)
            
            logger.debug("Browser menu items added")
            
        except Exception as e:
            logger.error(f"Error setting up browser menu: {e}", exc_info=True)
    
    def _launch_bulk_export(self, browser: Any) -> None:
        """
        Launch bulk export dialog for selected cards.
        
        Args:
            browser: Browser instance
        """
        try:
            # Get selected notes
            selected_notes = browser.selectedNotes()
            
            if not selected_notes:
                from aqt.utils import showInfo
                showInfo(
                    'Please select some cards before attempting to export definitions.',
                    parent=browser,
                    title="Anki Dictionary"
                )
                logger.debug("No cards selected for bulk export")
                return
            
            logger.info(f"Launching bulk export for {len(selected_notes)} notes")
            
            # Import and launch the bulk export widget
            self._show_bulk_export_dialog(browser, selected_notes)
            
        except Exception as e:
            logger.error(f"Error launching bulk export: {e}", exc_info=True)
            from aqt.utils import showWarning
            showWarning(
                f"Error launching bulk export: {str(e)}",
                parent=browser,
                title="Anki Dictionary"
            )
    
    def _show_bulk_export_dialog(self, browser: Any, selected_notes: list) -> None:
        """
        Show the bulk export dialog.
        
        Args:
            browser: Browser instance
            selected_notes: List of selected note IDs
        """
        try:
            from aqt.qt import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
            from aqt.qt import QComboBox, QProgressBar, Qt
            from aqt.utils import showInfo
            import anki.find
            
            # Create dialog
            dialog = QDialog(browser)
            dialog.setWindowTitle("Anki Dictionary: Export Definitions")
            dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
            dialog.setMinimumWidth(400)
            
            # Create layout
            layout = QVBoxLayout()
            layout.setContentsMargins(10, 6, 10, 6)
            
            # Info label
            info_label = QLabel(f"Export definitions for {len(selected_notes)} selected cards")
            layout.addWidget(info_label)
            
            # Field selection
            field_layout = QHBoxLayout()
            field_layout.addWidget(QLabel("Source Field:"))
            
            source_field_combo = QComboBox()
            # Get fields from first note
            if selected_notes:
                note = self.mw.col.get_note(selected_notes[0])
                source_field_combo.addItems(note.keys())
            field_layout.addWidget(source_field_combo)
            
            layout.addLayout(field_layout)
            
            # Destination field selection
            dest_field_layout = QHBoxLayout()
            dest_field_layout.addWidget(QLabel("Destination Field:"))
            
            dest_field_combo = QComboBox()
            if selected_notes:
                note = self.mw.col.get_note(selected_notes[0])
                dest_field_combo.addItems(note.keys())
            dest_field_layout.addWidget(dest_field_combo)
            
            layout.addLayout(dest_field_layout)
            
            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setVisible(False)
            layout.addWidget(progress_bar)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            export_button = QPushButton("Export")
            cancel_button = QPushButton("Cancel")
            
            button_layout.addWidget(export_button)
            button_layout.addWidget(cancel_button)
            
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            # Track cancellation
            cancelled = [False]
            
            def on_export():
                """Handle export button click."""
                source_field = source_field_combo.currentText()
                dest_field = dest_field_combo.currentText()
                
                if not source_field or not dest_field:
                    showInfo("Please select source and destination fields", parent=dialog)
                    return
                
                if source_field == dest_field:
                    from aqt.utils import askUser
                    if not askUser(
                        f'Are you sure you want to export definitions for the "{source_field}" field into the same field?',
                        parent=dialog
                    ):
                        return
                
                # Show progress
                progress_bar.setVisible(True)
                progress_bar.setMaximum(len(selected_notes))
                progress_bar.setValue(0)
                
                export_button.setEnabled(False)
                
                # Perform export
                self._perform_bulk_export(
                    selected_notes,
                    source_field,
                    dest_field,
                    progress_bar,
                    cancelled
                )
                
                if not cancelled[0]:
                    showInfo(
                        f"Successfully exported definitions for {len(selected_notes)} cards",
                        parent=dialog
                    )
                    dialog.accept()
                else:
                    export_button.setEnabled(True)
                    progress_bar.setVisible(False)
            
            def on_cancel():
                """Handle cancel button click."""
                cancelled[0] = True
                dialog.reject()
            
            export_button.clicked.connect(on_export)
            cancel_button.clicked.connect(on_cancel)
            
            # Show dialog
            dialog.exec()
            
        except Exception as e:
            logger.error(f"Error showing bulk export dialog: {e}", exc_info=True)
            from aqt.utils import showWarning
            showWarning(
                f"Error showing bulk export dialog: {str(e)}",
                parent=browser,
                title="Anki Dictionary"
            )
    
    def _perform_bulk_export(
        self,
        note_ids: list,
        source_field: str,
        dest_field: str,
        progress_bar: Any,
        cancelled: list
    ) -> None:
        """
        Perform bulk export operation.
        
        Args:
            note_ids: List of note IDs to export
            source_field: Source field name
            dest_field: Destination field name
            progress_bar: Progress bar widget
            cancelled: List with cancellation flag
        """
        try:
            search_service = self.plugin.get_search_service()
            export_service = self.plugin.get_export_service()
            
            exported_count = 0
            
            for i, note_id in enumerate(note_ids):
                # Check for cancellation
                if cancelled[0]:
                    logger.info(f"Bulk export cancelled after {exported_count} cards")
                    break
                
                try:
                    # Get note
                    note = self.mw.col.get_note(note_id)
                    
                    # Get source text
                    source_text = note[source_field] if source_field in note else ""
                    
                    if not source_text or not source_text.strip():
                        continue
                    
                    # Clean source text (remove HTML tags)
                    import re
                    clean_text = re.sub(r'<[^>]+>', '', source_text).strip()
                    
                    if not clean_text:
                        continue
                    
                    # Search for definition
                    results = search_service.search(clean_text)
                    
                    if results and len(results) > 0:
                        # Get first result
                        first_result = results[0]
                        
                        # Format definition
                        definition = first_result.get('definition', '')
                        
                        if definition:
                            # Update destination field
                            note[dest_field] = definition
                            self.mw.col.update_note(note)
                            exported_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error exporting note {note_id}: {e}")
                    continue
                
                finally:
                    # Update progress
                    progress_bar.setValue(i + 1)
                    # Process events to keep UI responsive
                    from aqt.qt import QApplication
                    QApplication.processEvents()
            
            logger.info(f"Bulk export completed: {exported_count}/{len(note_ids)} cards exported")
            
        except Exception as e:
            logger.error(f"Error performing bulk export: {e}", exc_info=True)
            raise
