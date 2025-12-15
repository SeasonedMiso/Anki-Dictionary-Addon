# -*- coding: utf-8 -*-
"""
Card Exporter UI component for bulk card export operations.
"""

from typing import Any, Optional, List, Dict, Tuple
from pathlib import Path
import logging

from aqt.qt import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QApplication, Qt
)
from aqt.utils import showInfo as show_info, tooltip

from ..services import ExportService, SearchService
from ..utils.dialogs import ask_user


logger = logging.getLogger('anki_dictionary.ui.card_exporter')


class CardExporter(QDialog):
    """
    Bulk card export dialog for browser integration.
    
    This component provides a UI for exporting multiple cards at once,
    with progress feedback and cancellation support.
    """
    
    def __init__(
        self,
        mw: Any,
        export_service: ExportService,
        search_service: SearchService,
        browser: Any,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize card exporter dialog.
        
        Args:
            mw: Anki main window instance
            export_service: Export service for creating cards
            search_service: Search service for looking up definitions
            browser: Browser instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.mw = mw
        self.export_service = export_service
        self.search_service = search_service
        self.browser = browser
        
        # State
        self._is_exporting = False
        self._cancelled = False
        self._current_progress = 0
        self._total_items = 0
        
        # UI components
        self.progress_bar: Optional[QProgressBar] = None
        self.status_label: Optional[QLabel] = None
        self.cancel_button: Optional[QPushButton] = None
        
        self._setup_ui()
        
        logger.debug("CardExporter initialized")
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Anki Dictionary - Bulk Export")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(150)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Status label
        self.status_label = QLabel("Preparing export...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedWidth(100)
        self.cancel_button.clicked.connect(self.cancel_export)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def export_selected_cards(
        self,
        note_ids: List[int],
        template_name: str,
        deck_id: int,
        auto_add_definitions: bool = False
    ) -> Tuple[int, int]:
        """
        Export definitions for selected cards.
        
        Args:
            note_ids: List of note IDs to export
            template_name: Export template name
            deck_id: Target deck ID
            auto_add_definitions: Whether to automatically add definitions
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        if self._is_exporting:
            logger.warning("Export already in progress")
            return 0, 0
        
        self._is_exporting = True
        self._cancelled = False
        self._current_progress = 0
        self._total_items = len(note_ids)
        
        logger.info(f"Starting bulk export of {self._total_items} cards")
        
        # Update UI
        self.progress_bar.setMaximum(self._total_items)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Exporting 0 of {self._total_items} cards...")
        
        # Show dialog
        self.show()
        QApplication.processEvents()
        
        successful = 0
        failed = 0
        
        try:
            for idx, note_id in enumerate(note_ids):
                # Check for cancellation (including before first iteration)
                if self._cancelled:
                    logger.info(f"Export cancelled at {idx}/{self._total_items}")
                    break
                
                # Export card
                try:
                    success = self._export_single_card(
                        note_id,
                        template_name,
                        deck_id,
                        auto_add_definitions
                    )
                    
                    if success:
                        successful += 1
                    else:
                        failed += 1
                
                except Exception as e:
                    logger.error(f"Error exporting card {note_id}: {e}", exc_info=True)
                    failed += 1
                
                # Update progress
                self._current_progress = idx + 1
                self.update_progress(self._current_progress, self._total_items)
                QApplication.processEvents()
        
        finally:
            self._is_exporting = False
            self.close()
        
        # Show completion message
        if self._cancelled:
            show_info(
                f"Export cancelled.\n\n"
                f"Successfully exported: {successful}\n"
                f"Failed: {failed}",
                parent=self.browser
            )
        else:
            show_info(
                f"Export complete!\n\n"
                f"Successfully exported: {successful}\n"
                f"Failed: {failed}",
                parent=self.browser
            )
        
        logger.info(f"Export complete: {successful} successful, {failed} failed")
        
        return successful, failed
    
    def _export_single_card(
        self,
        note_id: int,
        template_name: str,
        deck_id: int,
        auto_add_definitions: bool
    ) -> bool:
        """
        Export a single card.
        
        Args:
            note_id: Note ID to export
            template_name: Export template name
            deck_id: Target deck ID
            auto_add_definitions: Whether to automatically add definitions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get note
            note = self.mw.col.getNote(note_id)
            if not note:
                logger.warning(f"Note {note_id} not found")
                return False
            
            # Extract term from note (implementation depends on field structure)
            term = self._extract_term_from_note(note)
            if not term:
                logger.warning(f"Could not extract term from note {note_id}")
                return False
            
            # Search for definitions if auto-add is enabled
            definitions = []
            if auto_add_definitions:
                # This would use search_service to find definitions
                # For now, placeholder
                pass
            
            # Create export note using ExportService
            # This is a simplified version - actual implementation would need
            # to get template configuration and prepare field values
            success, error = self.export_service.create_note(
                note_type_name=template_name,
                field_values={'Expression': [term]},
                tags="",
                deck_id=deck_id
            )
            
            if not success:
                logger.warning(f"Failed to export note {note_id}: {error}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error in _export_single_card: {e}", exc_info=True)
            return False
    
    def _extract_term_from_note(self, note: Any) -> Optional[str]:
        """
        Extract term from a note.
        
        Args:
            note: Anki note object
            
        Returns:
            Extracted term or None
        """
        # Try common field names
        common_fields = ['Expression', 'Word', 'Front', 'Question', 'Term']
        
        for field_name in common_fields:
            if field_name in note:
                term = note[field_name]
                if term and term.strip():
                    return term.strip()
        
        # Fall back to first non-empty field
        for field_name in note.keys():
            term = note[field_name]
            if term and term.strip():
                return term.strip()
        
        return None
    
    def update_progress(self, current: int, total: int) -> None:
        """
        Update progress bar and status label.
        
        Args:
            current: Current progress value
            total: Total items
        """
        if self.progress_bar:
            self.progress_bar.setValue(current)
        
        if self.status_label:
            self.status_label.setText(f"Exporting {current} of {total} cards...")
        
        QApplication.processEvents()
    
    def cancel_export(self) -> None:
        """Cancel the ongoing export operation."""
        if not self._is_exporting:
            self.close()
            return
        
        # Confirm cancellation
        if not ask_user(
            "Are you sure you want to cancel the export?",
            parent=self
        ):
            # User declined cancellation
            return
        
        self._cancelled = True
        self.status_label.setText("Cancelling...")
        self.cancel_button.setEnabled(False)
        logger.info("Export cancellation requested")
    
    def closeEvent(self, event) -> None:
        """
        Handle close event.
        
        Args:
            event: Close event
        """
        if self._is_exporting and not self._cancelled:
            # Prevent closing during export
            event.ignore()
            self.cancel_export()
        else:
            event.accept()
    
    @property
    def is_exporting(self) -> bool:
        """Check if export is in progress."""
        return self._is_exporting
    
    @property
    def was_cancelled(self) -> bool:
        """Check if export was cancelled."""
        return self._cancelled
