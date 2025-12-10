# -*- coding: utf-8 -*-
"""
Anki Dictionary Add-on - Main Entry Point

This module initializes the Anki Dictionary plugin using the plugin coordinator pattern.
All functionality is delegated to the AnkiDictionaryPlugin class and UI modules for clean
separation of concerns and testability.

The main.py file is kept minimal (<200 lines) with all UI code moved to src/ui/ modules.
"""

from pathlib import Path
from aqt import mw
from anki.hooks import addHook

from .src.core.plugin import AnkiDictionaryPlugin
from .src.constants import VERSION

# ============================================================================
# Plugin Initialization
# ============================================================================

# Initialize plugin coordinator
plugin = AnkiDictionaryPlugin(mw)

# Attach to mw for backward compatibility
mw.ankiDictPlugin = plugin

# Legacy dictionary window reference (for backward compatibility)
# The actual window is now managed by the plugin coordinator
mw.ankiDictionary = False


# ============================================================================
# Lifecycle Hooks
# ============================================================================

def on_profile_loaded():
    """
    Called when Anki profile is loaded.
    
    Initializes the plugin and optionally opens dictionary on start.
    """
    import os
    
    plugin.initialize()
    
    # Check if we should auto-open
    auto_open = mw.AnkiDictConfig.get('dictOnStart', False)
    debug_mode = os.environ.get('ANKI_DICT_AUTO_OPEN') == '1'
    
    if auto_open or debug_mode:
        # If ANKI_DICT_OPEN_MOCK is set, open mock window instead
        if os.environ.get('ANKI_DICT_OPEN_MOCK') == '1':
            from .src.ui.modern import show_ui_mock
            show_ui_mock(None)  # No parent = independent window
        else:
            plugin.open_dictionary()


def on_unload_profile():
    """
    Called when Anki profile is unloaded.
    
    Closes dictionary window and cleans up plugin resources.
    """
    plugin.close_dictionary()
    plugin.cleanup()


# Register lifecycle hooks
addHook('profileLoaded', on_profile_loaded)
addHook('unloadProfile', on_unload_profile)


# ============================================================================
# Legacy Function Wrappers
# ============================================================================
# These functions maintain backward compatibility with older code that may
# call them directly. All functionality is delegated to the plugin coordinator
# and UI modules.

def ankiDict(text):
    """
    Legacy function wrapper for showing info dialogs.
    
    Args:
        text: Text to display in dialog
    """
    from aqt.utils import showInfo
    showInfo(text, parent=None, help=None, type="info", title="Anki Dictionary Add-on")


def dictionary_init(terms=False):
    """
    Legacy function wrapper for opening the dictionary window.
    
    This function maintains backward compatibility while delegating to the
    plugin coordinator's UI management.
    
    Args:
        terms: Optional term(s) to search. Can be a string or list of strings.
    """
    from anki.utils import is_mac
    
    # Convert single term to list
    if terms and isinstance(terms, str):
        terms = [terms]
    
    # Get dictionary window via plugin
    dict_window = plugin.get_dictionary_window()
    
    # Update menu text
    shortcut = '⌘W' if is_mac else 'Ctrl+W'
    
    # Toggle window visibility
    if not mw.ankiDictionary or not dict_window.isVisible():
        # Show window
        dict_window.show_window(terms)
        
        # Update legacy reference
        mw.ankiDictionary = dict_window
        
        # Update menu text
        if hasattr(mw, 'openMiDict'):
            mw.openMiDict.setText(f"Close Dictionary ({shortcut})")
    else:
        # Hide window
        dict_window.hide()
        
        # Update menu text
        if hasattr(mw, 'openMiDict'):
            mw.openMiDict.setText(f"Open Dictionary ({shortcut})")


def close_dictionary():
    """
    Legacy function wrapper for closing dictionary window.
    
    Delegates to plugin coordinator.
    """
    dict_window = plugin.dictionary_window
    if dict_window and dict_window.isVisible():
        if hasattr(dict_window, 'saveSizeAndPos'):
            dict_window.saveSizeAndPos()
        dict_window.hide()
        
        from anki.utils import is_mac
        shortcut = '⌘W' if is_mac else 'Ctrl+W'
        if hasattr(mw, 'openMiDict'):
            mw.openMiDict.setText(f"Open Dictionary ({shortcut})")


def open_dictionary_settings():
    """
    Legacy function wrapper for opening settings window.
    
    Delegates to plugin coordinator.
    """
    plugin.open_settings()


# Attach legacy functions to mw for backward compatibility
mw.dictionaryInit = dictionary_init


# ============================================================================
# Export for Other Modules
# ============================================================================

__all__ = [
    'plugin',
    'ankiDict',
    'dictionary_init',
    'open_dictionary_settings',
    'close_dictionary'
]
