# -*- coding: utf-8 -*-
"""
Tests for the Context Manager Service.

Tests thread-safe context tracking for editor and reviewer contexts.
"""

import pytest
import sys
from pathlib import Path
from threading import Thread
from unittest.mock import Mock, MagicMock

# Add src to path to import services directly
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from services.context_manager import (
    ContextManager,
    EditorContext,
    ReviewerContext,
    get_context_manager
)


class TestEditorContext:
    """Tests for EditorContext class."""
    
    def test_editor_context_creation(self):
        """Test creating an editor context."""
        editor = Mock()
        context = EditorContext(
            editor=editor,
            editor_type='add',
            note=Mock(),
            field_index=0
        )
        
        assert context.editor is editor
        assert context.editor_type == 'add'
        assert context.note is not None
        assert context.field_index == 0
        assert context.selected_text is None
    
    def test_editor_context_to_dict(self):
        """Test converting editor context to dictionary."""
        editor = Mock()
        note = Mock()
        context = EditorContext(
            editor=editor,
            editor_type='edit',
            note=note,
            field_index=1
        )
        context.selected_text = "test text"
        
        result = context.to_dict()
        
        assert result['editor_type'] == 'edit'
        assert result['has_note'] is True
        assert result['field_index'] == 1
        assert result['selected_text'] == "test text"
    
    def test_editor_context_without_note(self):
        """Test editor context without a note."""
        editor = Mock()
        context = EditorContext(
            editor=editor,
            editor_type='browser'
        )
        
        result = context.to_dict()
        
        assert result['has_note'] is False
        assert result['field_index'] is None


class TestReviewerContext:
    """Tests for ReviewerContext class."""
    
    def test_reviewer_context_creation(self):
        """Test creating a reviewer context."""
        reviewer = Mock()
        card = Mock()
        context = ReviewerContext(
            reviewer=reviewer,
            card=card,
            is_showing_answer=False
        )
        
        assert context.reviewer is reviewer
        assert context.card is card
        assert context.is_showing_answer is False
        assert context.selected_text is None
    
    def test_reviewer_context_to_dict(self):
        """Test converting reviewer context to dictionary."""
        reviewer = Mock()
        card = Mock()
        context = ReviewerContext(
            reviewer=reviewer,
            card=card,
            is_showing_answer=True
        )
        context.selected_text = "answer text"
        
        result = context.to_dict()
        
        assert result['has_card'] is True
        assert result['is_showing_answer'] is True
        assert result['selected_text'] == "answer text"
    
    def test_reviewer_context_without_card(self):
        """Test reviewer context without a card."""
        reviewer = Mock()
        context = ReviewerContext(reviewer=reviewer)
        
        result = context.to_dict()
        
        assert result['has_card'] is False
        assert result['is_showing_answer'] is False


class TestContextManager:
    """Tests for ContextManager class."""
    
    def test_context_manager_initialization(self):
        """Test context manager initialization."""
        manager = ContextManager()
        
        assert manager.get_editor_context() is None
        assert manager.get_reviewer_context() is None
        assert manager.is_editor_active() is False
        assert manager.is_reviewer_active() is False
    
    # Editor Context Tests
    
    def test_set_and_get_editor_context(self):
        """Test setting and getting editor context."""
        manager = ContextManager()
        editor = Mock()
        note = Mock()
        
        manager.set_editor_context(
            editor=editor,
            editor_type='add',
            note=note,
            field_index=0
        )
        
        context = manager.get_editor_context()
        assert context is not None
        assert context.editor is editor
        assert context.editor_type == 'add'
        assert context.note is note
        assert context.field_index == 0
    
    def test_clear_editor_context(self):
        """Test clearing editor context."""
        manager = ContextManager()
        editor = Mock()
        
        manager.set_editor_context(editor, 'add')
        assert manager.is_editor_active() is True
        
        manager.clear_editor_context()
        assert manager.is_editor_active() is False
        assert manager.get_editor_context() is None
    
    def test_update_editor_selected_text(self):
        """Test updating selected text in editor."""
        manager = ContextManager()
        editor = Mock()
        
        manager.set_editor_context(editor, 'add')
        manager.update_editor_selected_text("selected text")
        
        context = manager.get_editor_context()
        assert context.selected_text == "selected text"
    
    def test_update_editor_selected_text_no_context(self):
        """Test updating selected text when no editor context exists."""
        manager = ContextManager()
        
        # Should not raise an error
        manager.update_editor_selected_text("text")
    
    def test_update_editor_field_index(self):
        """Test updating field index in editor."""
        manager = ContextManager()
        editor = Mock()
        
        manager.set_editor_context(editor, 'add', field_index=0)
        manager.update_editor_field_index(2)
        
        context = manager.get_editor_context()
        assert context.field_index == 2
    
    def test_get_editor_type(self):
        """Test getting editor type."""
        manager = ContextManager()
        editor = Mock()
        
        manager.set_editor_context(editor, 'edit')
        assert manager.get_editor_type() == 'edit'
    
    def test_get_editor_type_no_context(self):
        """Test getting editor type when no context exists."""
        manager = ContextManager()
        assert manager.get_editor_type() is None
    
    # Reviewer Context Tests
    
    def test_set_and_get_reviewer_context(self):
        """Test setting and getting reviewer context."""
        manager = ContextManager()
        reviewer = Mock()
        card = Mock()
        
        manager.set_reviewer_context(
            reviewer=reviewer,
            card=card,
            is_showing_answer=True
        )
        
        context = manager.get_reviewer_context()
        assert context is not None
        assert context.reviewer is reviewer
        assert context.card is card
        assert context.is_showing_answer is True
    
    def test_clear_reviewer_context(self):
        """Test clearing reviewer context."""
        manager = ContextManager()
        reviewer = Mock()
        
        manager.set_reviewer_context(reviewer)
        assert manager.is_reviewer_active() is True
        
        manager.clear_reviewer_context()
        assert manager.is_reviewer_active() is False
        assert manager.get_reviewer_context() is None
    
    def test_update_reviewer_selected_text(self):
        """Test updating selected text in reviewer."""
        manager = ContextManager()
        reviewer = Mock()
        
        manager.set_reviewer_context(reviewer)
        manager.update_reviewer_selected_text("answer text")
        
        context = manager.get_reviewer_context()
        assert context.selected_text == "answer text"
    
    def test_update_reviewer_answer_state(self):
        """Test updating answer state in reviewer."""
        manager = ContextManager()
        reviewer = Mock()
        
        manager.set_reviewer_context(reviewer, is_showing_answer=False)
        manager.update_reviewer_answer_state(True)
        
        context = manager.get_reviewer_context()
        assert context.is_showing_answer is True
    
    def test_is_showing_answer(self):
        """Test checking if answer is shown."""
        manager = ContextManager()
        reviewer = Mock()
        
        manager.set_reviewer_context(reviewer, is_showing_answer=False)
        assert manager.is_showing_answer() is False
        
        manager.update_reviewer_answer_state(True)
        assert manager.is_showing_answer() is True
    
    def test_is_showing_answer_no_context(self):
        """Test checking answer state when no reviewer context exists."""
        manager = ContextManager()
        assert manager.is_showing_answer() is False
    
    # General Context Tests
    
    def test_get_active_context_type_editor(self):
        """Test getting active context type when editor is active."""
        manager = ContextManager()
        editor = Mock()
        
        manager.set_editor_context(editor, 'add')
        assert manager.get_active_context_type() == 'editor'
    
    def test_get_active_context_type_reviewer(self):
        """Test getting active context type when reviewer is active."""
        manager = ContextManager()
        reviewer = Mock()
        
        manager.set_reviewer_context(reviewer)
        assert manager.get_active_context_type() == 'reviewer'
    
    def test_get_active_context_type_none(self):
        """Test getting active context type when no context is active."""
        manager = ContextManager()
        assert manager.get_active_context_type() is None
    
    def test_get_active_context_type_editor_takes_precedence(self):
        """Test that editor context takes precedence when both are active."""
        manager = ContextManager()
        editor = Mock()
        reviewer = Mock()
        
        manager.set_editor_context(editor, 'add')
        manager.set_reviewer_context(reviewer)
        
        # Editor should take precedence
        assert manager.get_active_context_type() == 'editor'
    
    def test_get_selected_text_from_editor(self):
        """Test getting selected text from editor context."""
        manager = ContextManager()
        editor = Mock()
        
        manager.set_editor_context(editor, 'add')
        manager.update_editor_selected_text("editor text")
        
        assert manager.get_selected_text() == "editor text"
    
    def test_get_selected_text_from_reviewer(self):
        """Test getting selected text from reviewer context."""
        manager = ContextManager()
        reviewer = Mock()
        
        manager.set_reviewer_context(reviewer)
        manager.update_reviewer_selected_text("reviewer text")
        
        assert manager.get_selected_text() == "reviewer text"
    
    def test_get_selected_text_none(self):
        """Test getting selected text when no context is active."""
        manager = ContextManager()
        assert manager.get_selected_text() is None
    
    def test_clear_all_contexts(self):
        """Test clearing all contexts."""
        manager = ContextManager()
        editor = Mock()
        reviewer = Mock()
        
        manager.set_editor_context(editor, 'add')
        manager.set_reviewer_context(reviewer)
        
        assert manager.is_editor_active() is True
        assert manager.is_reviewer_active() is True
        
        manager.clear_all_contexts()
        
        assert manager.is_editor_active() is False
        assert manager.is_reviewer_active() is False
    
    def test_get_context_info(self):
        """Test getting context information."""
        manager = ContextManager()
        editor = Mock()
        note = Mock()
        
        manager.set_editor_context(editor, 'add', note=note, field_index=0)
        manager.update_editor_selected_text("test")
        
        info = manager.get_context_info()
        
        assert info['active_type'] == 'editor'
        assert info['editor'] is not None
        assert info['editor']['editor_type'] == 'add'
        assert info['editor']['has_note'] is True
        assert info['editor']['selected_text'] == "test"
        assert info['reviewer'] is None
    
    # Thread Safety Tests
    
    def test_thread_safe_editor_context_updates(self):
        """Test thread-safe editor context updates."""
        manager = ContextManager()
        results = []
        
        def update_context(index):
            editor = Mock()
            manager.set_editor_context(editor, f'type_{index}')
            context = manager.get_editor_context()
            results.append(context.editor_type)
        
        threads = [Thread(target=update_context, args=(i,)) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All updates should have completed without errors
        assert len(results) == 10
    
    def test_thread_safe_reviewer_context_updates(self):
        """Test thread-safe reviewer context updates."""
        manager = ContextManager()
        results = []
        
        def update_context(index):
            reviewer = Mock()
            manager.set_reviewer_context(reviewer, is_showing_answer=(index % 2 == 0))
            is_showing = manager.is_showing_answer()
            results.append(is_showing)
        
        threads = [Thread(target=update_context, args=(i,)) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All updates should have completed without errors
        assert len(results) == 10
    
    def test_thread_safe_mixed_context_operations(self):
        """Test thread-safe mixed context operations."""
        manager = ContextManager()
        results = []
        
        def mixed_operations(index):
            if index % 2 == 0:
                editor = Mock()
                manager.set_editor_context(editor, 'add')
                manager.update_editor_selected_text(f"text_{index}")
                text = manager.get_selected_text()
                results.append(('editor', text))
            else:
                reviewer = Mock()
                manager.set_reviewer_context(reviewer)
                manager.update_reviewer_answer_state(True)
                is_showing = manager.is_showing_answer()
                results.append(('reviewer', is_showing))
        
        threads = [Thread(target=mixed_operations, args=(i,)) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All operations should have completed without errors
        assert len(results) == 10


class TestGlobalContextManager:
    """Tests for global context manager instance."""
    
    def test_get_context_manager_singleton(self):
        """Test that get_context_manager returns a singleton."""
        manager1 = get_context_manager()
        manager2 = get_context_manager()
        
        assert manager1 is manager2
    
    def test_global_context_manager_persistence(self):
        """Test that global context manager persists state."""
        manager = get_context_manager()
        editor = Mock()
        
        manager.set_editor_context(editor, 'add')
        
        # Get the manager again and verify state persists
        manager2 = get_context_manager()
        assert manager2.is_editor_active() is True
        assert manager2.get_editor_type() == 'add'
