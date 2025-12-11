# -*- coding: utf-8 -*-
"""
Anki Dictionary Addon - Modern Optimized Components.

This package contains the new, clean architecture components built with modern
design patterns and proper separation of concerns.

Structure:
- ui/: Modern UI components with theming system and clean patterns
- legacy/: Legacy services and components (temporary integration)

Integration Strategy:
- New optimized code lives in main src/
- Legacy code clearly separated in src/legacy/
- Import from legacy/ as needed until we replace with optimized versions
"""

# OPTIMIZED: Modern UI components
from .ui import *

# Legacy services are imported explicitly when needed
# from .legacy.services import ExportService, SearchService
# from .legacy.config import ConfigManager