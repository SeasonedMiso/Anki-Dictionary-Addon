# -*- coding: utf-8 -*-
"""
Services layer - Clean business logic separated from UI.

This module contains optimized service implementations that bridge
the new UI components with the Anki backend and legacy services.
"""

from .search_service import SearchService
from .result_formatter import ResultFormatter
from .media_service import MediaService
from .export_coordinator import ExportCoordinator
from .context_manager import ContextManager, get_context_manager
from .validation_service import ValidationService, get_validation_service
from .dictionary_service import DictionaryService
from .config_service import ConfigService
from .history_service import HistoryService

__all__ = [
    'SearchService',
    'ResultFormatter',
    'MediaService',
    'ExportCoordinator',
    'ContextManager',
    'get_context_manager',
    'ValidationService',
    'get_validation_service',
    'DictionaryService',
    'ConfigService',
    'HistoryService',
]
