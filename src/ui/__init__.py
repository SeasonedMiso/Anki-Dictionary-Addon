# -*- coding: utf-8 -*-
"""
UI module for Anki Dictionary addon.
"""

from .dictionary_window import DictionaryWindow
from .settings_window import SettingsWindow
from .dictionary_manager import DictionaryManagerWidget
from .editor_integration import EditorIntegration
from .browser_integration import BrowserIntegration
from .menu_manager import MenuManager

__all__ = [
    'DictionaryWindow',
    'SettingsWindow',
    'DictionaryManagerWidget',
    'EditorIntegration',
    'BrowserIntegration',
    'MenuManager'
]
