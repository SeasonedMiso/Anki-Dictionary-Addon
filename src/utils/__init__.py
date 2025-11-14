# -*- coding: utf-8 -*-
"""
Utility functions for the Anki Dictionary addon.
"""

# Import text and platform utilities (no Anki dependencies)
from .text import clean_html, strip_html_tags, escape_punctuation
from .platform import is_mac, is_win, is_lin

# Import dialogs only if aqt is available
try:
    from .dialogs import show_info, show_warning, show_error, ask_user
    _dialogs_available = True
except ImportError:
    # Running without Anki environment (e.g., in tests)
    _dialogs_available = False
    show_info = None
    show_warning = None
    show_error = None
    ask_user = None

__all__ = [
    'show_info',
    'show_warning',
    'show_error',
    'ask_user',
    'clean_html',
    'strip_html_tags',
    'escape_punctuation',
    'is_mac',
    'is_win',
    'is_lin',
]
