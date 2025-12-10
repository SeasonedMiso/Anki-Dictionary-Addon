# -*- coding: utf-8 -*-
"""
Utility modules for the modern optimized components.

OPTIMIZED: Clean utility functions and helpers.
"""

from .keyboard import (
    KeyboardManager, get_keyboard_manager, setup_font_shortcuts,
    setup_navigation_shortcuts, setup_dictionary_shortcuts, get_shortcut_help
)

__all__ = [
    'KeyboardManager', 'get_keyboard_manager', 'setup_font_shortcuts',
    'setup_navigation_shortcuts', 'setup_dictionary_shortcuts', 'get_shortcut_help'
]