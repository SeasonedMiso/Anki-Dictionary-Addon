# -*- coding: utf-8 -*-
"""
Legacy UI Components.

This package contains legacy UI code. Modern optimized components are in src/ui/.
Import from src/ui/ for new code instead of using these legacy components.
"""

# Legacy UI components - import only what's needed for backward compatibility
from .menu_manager import MenuManager
from .editor_integration import EditorIntegration
from .browser_integration import BrowserIntegration

__all__ = [
    'MenuManager',
    'EditorIntegration', 
    'BrowserIntegration'
]