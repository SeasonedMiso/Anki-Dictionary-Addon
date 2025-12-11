# -*- coding: utf-8 -*-
"""
Database layer for dictionary data.
"""

from .connection import DatabaseConnection
from .repository import DictionaryRepository
from .models import DictionaryEntry, SearchResult
from . import dictdb

__all__ = [
    'DatabaseConnection',
    'DictionaryRepository',
    'DictionaryEntry',
    'SearchResult',
    'dictdb',
]
