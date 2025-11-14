# -*- coding: utf-8 -*-
"""
Database layer for dictionary data.
"""

from .connection import DatabaseConnection
from .repository import DictionaryRepository
from .models import DictionaryEntry, SearchResult

__all__ = [
    'DatabaseConnection',
    'DictionaryRepository',
    'DictionaryEntry',
    'SearchResult',
]
