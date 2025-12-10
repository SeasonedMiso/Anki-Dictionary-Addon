# -*- coding: utf-8 -*-
"""
Modern UI System for Anki Dictionary Addon.

This module provides a complete modern UI system with clear separation of concerns:

- base_widgets.py: Fundamental reusable UI building blocks (ThemedButton, ThemedLabel, etc.)
- dictionary_widgets.py: Dictionary-specific components (SearchBar, DefinitionCard, etc.)
- styling.py: Centralized theming system with color management
- settings_window.py: Modern settings interface
- ui_mock.py: UI demonstration and testing interface
- keyboard.py: Cross-platform keyboard shortcut management

All components use the centralized theming system for consistent styling.
"""

from .settings_window import ModernSettingsWindow, show_modern_settings
from .ui_mock import UIMockWindow, show_ui_mock
from .styling import ThemeColors, ThemeManager, StyleGenerator, get_theme_manager, THEME_PRESETS
from .keyboard import (
    KeyboardManager, get_keyboard_manager, setup_font_shortcuts,
    setup_navigation_shortcuts, setup_dictionary_shortcuts, get_shortcut_help
)
from .base_widgets import (
    ThemedWidget, ThemedButton, ThemedLabel, ThemedLineEdit, ThemedFrame,
    ActionButton, CopyButton, FrequencyBadge, PitchAccentLabel, StatusMessage,
    ValidationInput
)
from .dictionary_widgets import (
    CollapsibleBox, ModernSearchBar, DefinitionCard, WordSection,
    DictionarySubsection, DictionaryFilterBar, ModernResultsArea
)

__all__ = [
    # Main windows
    'ModernSettingsWindow',
    'show_modern_settings',
    'UIMockWindow', 
    'show_ui_mock',
    
    # Styling system
    'ThemeColors',
    'ThemeManager', 
    'StyleGenerator',
    'get_theme_manager',
    'THEME_PRESETS',
    
    # Keyboard shortcuts
    'KeyboardManager',
    'get_keyboard_manager',
    'setup_font_shortcuts',
    'setup_navigation_shortcuts', 
    'setup_dictionary_shortcuts',
    'get_shortcut_help',
    
    # Reusable components
    'ThemedWidget',
    'ThemedButton',
    'ThemedLabel', 
    'ThemedLineEdit',
    'ThemedFrame',
    'ActionButton',
    'CopyButton',
    'FrequencyBadge',
    'PitchAccentLabel',
    'StatusMessage',
    'ValidationInput',
    
    # Dictionary-specific components
    'CollapsibleBox',
    'ModernSearchBar',
    'DefinitionCard',
    'WordSection',
    'DictionarySubsection',
    'DictionaryFilterBar',
    'ModernResultsArea'
]