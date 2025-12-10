# -*- coding: utf-8 -*-
"""
Database models for dictionary entries.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class DictionaryEntry:
    """Represents a single dictionary entry."""
    term: str
    altterm: str
    pronunciation: str
    pos: str  # Part of speech
    definition: str
    examples: str
    audio: str
    frequency: int
    star_count: str
    
    def to_dict(self) -> Dict[str, any]:
        """Convert entry to dictionary."""
        return {
            'term': self.term,
            'altterm': self.altterm,
            'pronunciation': self.pronunciation,
            'pos': self.pos,
            'definition': self.definition.replace('\n', '<br>'),
            'examples': self.examples,
            'audio': self.audio,
            'starCount': self.star_count,
        }


@dataclass
class SearchResult:
    """Represents search results from multiple dictionaries."""
    results: Dict[str, List[DictionaryEntry]]
    total_count: int
    
    def is_empty(self) -> bool:
        """Check if search returned no results."""
        return self.total_count == 0
    
    def get_dictionary_names(self) -> List[str]:
        """Get list of dictionaries that returned results."""
        return list(self.results.keys())


@dataclass
class DictionaryInfo:
    """Information about a dictionary."""
    name: str
    language: str
    table_name: str
    fields: List[str]
    add_type: str
    term_header: List[str]
    duplicate_header: bool
