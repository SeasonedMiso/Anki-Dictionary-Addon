# -*- coding: utf-8 -*-
"""
Modern UI components for Anki Dictionary addon.

This module contains the new modern UI implementations that are separate
from the legacy components. These are designed to work with the mock UI
and follow the design document specifications.
"""

from .settings_window import ModernSettingsWindow, show_modern_settings
from .ui_mock import UIMockWindow, show_ui_mock

__all__ = [
    'ModernSettingsWindow',
    'show_modern_settings',
    'UIMockWindow', 
    'show_ui_mock'
]