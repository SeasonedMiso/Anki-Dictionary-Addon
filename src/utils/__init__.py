# -*- coding: utf-8 -*-
"""
Utilities layer - Clean utility functions separated from business logic.

This module contains optimized utility functions that can be used
across the application without dependencies on UI or business logic.
"""

from .text import (
    strip_html_tags,
    clean_html,
    escape_punctuation,
    normalize_whitespace,
    truncate_text,
    is_japanese_text,
    highlight_term,
    highlight_example_sentences,
    remove_brackets,
    clean_term,
    format_definition_text,
    extract_reading,
    split_compound_word,
    validate_search_term,
    format_frequency_display
)

from .keyboard import (
    KeyboardManager,
    get_keyboard_manager,
    register_standard_shortcuts,
    clear_all_shortcuts
)

__all__ = [
    # Text utilities
    'strip_html_tags',
    'clean_html',
    'escape_punctuation',
    'normalize_whitespace',
    'truncate_text',
    'is_japanese_text',
    'highlight_term',
    'highlight_example_sentences',
    'remove_brackets',
    'clean_term',
    'format_definition_text',
    'extract_reading',
    'split_compound_word',
    'validate_search_term',
    'format_frequency_display',
    
    # Keyboard utilities
    'KeyboardManager',
    'get_keyboard_manager',
    'register_standard_shortcuts',
    'clear_all_shortcuts'
]
