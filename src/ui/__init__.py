# -*- coding: utf-8 -*-
"""
UI module for Anki Dictionary addon.
"""

from .dictionary_window import DictionaryWindow
from .modern_dictionary_window import ModernDictionaryWindow
from .settings_window import SettingsWindow
from .dictionary_manager import DictionaryManagerWidget
from .editor_integration import EditorIntegration
from .browser_integration import BrowserIntegration
from .menu_manager import MenuManager
from .modern_components import (
    ModernSearchBar,
    DefinitionCard,
    DictionaryFilterBar,
    ModernResultsArea
)

__all__ = [
    'DictionaryWindow',
    'ModernDictionaryWindow',
    'SettingsWindow',
    'DictionaryManagerWidget',
    'EditorIntegration',
    'BrowserIntegration',
    'MenuManager',
    'ModernSearchBar',
    'DefinitionCard',
    'DictionaryFilterBar',
    'ModernResultsArea'
]
