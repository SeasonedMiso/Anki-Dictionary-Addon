# -*- coding: utf-8 -*-
"""
Context Manager Service - Thread-safe context tracking for editor and reviewer.

This module provides centralized context management for tracking the current
editor and reviewer states, allowing services to access context information
without direct UI dependencies.
"""

from typing import Optional, Any, Dict
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class EditorContext:
    """
    Represents the current editor context.
    
    Tracks information about the active editor window and its state.
    """
    
    def __init__(
        self,
        editor: Any,
        editor_type: str,
        note: Optional[Any] = None,
        field_index: Optional[int] = None
    ):
        """
        Initialize editor context.
        
        Args:
            editor: The editor instance (AddCards, EditCurrent, etc.)
            editor_type: Type of editor ('add', 'edit', 'browser', etc.)
            note: Current note being edited (if available)
            field_index: Currently focused field index (if available)
        """
        self.editor = editor
        self.editor_type = editor_type
        self.note = note
        self.field_index = field_index
        self.selected_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary representation.
        
        Returns:
            Dictionary with context information
        """
        return {
            'editor_type': self.editor_type,
            'has_note': self.note is not None,
            'field_index': self.field_index,
            'selected_text': self.selected_text
        }


class ReviewerContext:
    """
    Represents the current reviewer context.
    
    Tracks information about the active reviewer window and card state.
    """
    
    def __init__(
        self,
        reviewer: Any,
        card: Optional[Any] = None,
        is_showing_answer: bool = False
    ):
        """
        Initialize reviewer context.
        
        Args:
            reviewer: The reviewer instance
            card: Current card being reviewed (if available)
            is_showing_answer: Whether the answer is currently shown
        """
        self.reviewer = reviewer
        self.card = card
        self.is_showing_answer = is_showing_answer
        self.selected_text: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary representation.
        
        Returns:
            Dictionary with context information
        """
        return {
            'has_card': self.card is not None,
            'is_showing_answer': self.is_showing_answer,
            'selected_text': self.selected_text
        }


class ContextManager:
    """
    Thread-safe manager for tracking editor and reviewer contexts.
    
    Provides centralized access to current editor and reviewer states,
    allowing services to query context without direct UI dependencies.
    """
    
    def __init__(self):
        """Initialize context manager."""
        self._lock = Lock()
        self._editor_context: Optional[EditorContext] = None
        self._reviewer_context: Optional[ReviewerContext] = None
        logger.debug("ContextManager initialized")
    
    # Editor Context Methods
    
    def set_editor_context(
        self,
        editor: Any,
        editor_type: str,
        note: Optional[Any] = None,
        field_index: Optional[int] = None
    ) -> None:
        """
        Set the current editor context.
        
        Args:
            editor: The editor instance
            editor_type: Type of editor ('add', 'edit', 'browser', etc.)
            note: Current note being edited (if available)
            field_index: Currently focused field index (if available)
        """
        with self._lock:
            self._editor_context = EditorContext(
                editor=editor,
                editor_type=editor_type,
                note=note,
                field_index=field_index
            )
            logger.debug(f"Editor context set: {editor_type}")
    
    def get_editor_context(self) -> Optional[EditorContext]:
        """
        Get the current editor context.
        
        Returns:
            Current EditorContext or None if no editor is active
        """
        with self._lock:
            return self._editor_context
    
    def clear_editor_context(self) -> None:
        """Clear the current editor context."""
        with self._lock:
            self._editor_context = None
            logger.debug("Editor context cleared")
    
    def update_editor_selected_text(self, text: str) -> None:
        """
        Update the selected text in the current editor.
        
        Args:
            text: The selected text
        """
        with self._lock:
            if self._editor_context:
                self._editor_context.selected_text = text
                logger.debug(f"Editor selected text updated: {len(text)} chars")
    
    def update_editor_field_index(self, field_index: int) -> None:
        """
        Update the currently focused field index.
        
        Args:
            field_index: Index of the focused field
        """
        with self._lock:
            if self._editor_context:
                self._editor_context.field_index = field_index
                logger.debug(f"Editor field index updated: {field_index}")
    
    def is_editor_active(self) -> bool:
        """
        Check if an editor is currently active.
        
        Returns:
            True if editor context exists, False otherwise
        """
        with self._lock:
            return self._editor_context is not None
    
    def get_editor_type(self) -> Optional[str]:
        """
        Get the type of the current editor.
        
        Returns:
            Editor type string or None if no editor is active
        """
        with self._lock:
            if self._editor_context:
                return self._editor_context.editor_type
            return None
    
    # Reviewer Context Methods
    
    def set_reviewer_context(
        self,
        reviewer: Any,
        card: Optional[Any] = None,
        is_showing_answer: bool = False
    ) -> None:
        """
        Set the current reviewer context.
        
        Args:
            reviewer: The reviewer instance
            card: Current card being reviewed (if available)
            is_showing_answer: Whether the answer is currently shown
        """
        with self._lock:
            self._reviewer_context = ReviewerContext(
                reviewer=reviewer,
                card=card,
                is_showing_answer=is_showing_answer
            )
            logger.debug(f"Reviewer context set: showing_answer={is_showing_answer}")
    
    def get_reviewer_context(self) -> Optional[ReviewerContext]:
        """
        Get the current reviewer context.
        
        Returns:
            Current ReviewerContext or None if no reviewer is active
        """
        with self._lock:
            return self._reviewer_context
    
    def clear_reviewer_context(self) -> None:
        """Clear the current reviewer context."""
        with self._lock:
            self._reviewer_context = None
            logger.debug("Reviewer context cleared")
    
    def update_reviewer_selected_text(self, text: str) -> None:
        """
        Update the selected text in the current reviewer.
        
        Args:
            text: The selected text
        """
        with self._lock:
            if self._reviewer_context:
                self._reviewer_context.selected_text = text
                logger.debug(f"Reviewer selected text updated: {len(text)} chars")
    
    def update_reviewer_answer_state(self, is_showing_answer: bool) -> None:
        """
        Update whether the answer is being shown.
        
        Args:
            is_showing_answer: True if answer is shown, False otherwise
        """
        with self._lock:
            if self._reviewer_context:
                self._reviewer_context.is_showing_answer = is_showing_answer
                logger.debug(f"Reviewer answer state updated: {is_showing_answer}")
    
    def is_reviewer_active(self) -> bool:
        """
        Check if a reviewer is currently active.
        
        Returns:
            True if reviewer context exists, False otherwise
        """
        with self._lock:
            return self._reviewer_context is not None
    
    def is_showing_answer(self) -> bool:
        """
        Check if the reviewer is currently showing the answer.
        
        Returns:
            True if answer is shown, False otherwise
        """
        with self._lock:
            if self._reviewer_context:
                return self._reviewer_context.is_showing_answer
            return False
    
    # General Context Methods
    
    def get_active_context_type(self) -> Optional[str]:
        """
        Get the type of currently active context.
        
        Returns:
            'editor', 'reviewer', or None if no context is active
        """
        with self._lock:
            if self._editor_context:
                return 'editor'
            elif self._reviewer_context:
                return 'reviewer'
            return None
    
    def get_selected_text(self) -> Optional[str]:
        """
        Get selected text from the currently active context.
        
        Returns:
            Selected text from editor or reviewer, or None
        """
        with self._lock:
            if self._editor_context:
                return self._editor_context.selected_text
            elif self._reviewer_context:
                return self._reviewer_context.selected_text
            return None
    
    def clear_all_contexts(self) -> None:
        """Clear all contexts."""
        with self._lock:
            self._editor_context = None
            self._reviewer_context = None
            logger.debug("All contexts cleared")
    
    def get_context_info(self) -> Dict[str, Any]:
        """
        Get information about all current contexts.
        
        Returns:
            Dictionary with context information
        """
        with self._lock:
            # Determine active type without calling get_active_context_type() to avoid deadlock
            active_type = None
            if self._editor_context:
                active_type = 'editor'
            elif self._reviewer_context:
                active_type = 'reviewer'
            
            return {
                'editor': self._editor_context.to_dict() if self._editor_context else None,
                'reviewer': self._reviewer_context.to_dict() if self._reviewer_context else None,
                'active_type': active_type
            }


# Global context manager instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """
    Get or create the global context manager instance.
    
    Returns:
        The global ContextManager instance
    """
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
