# -*- coding: utf-8 -*-
"""
Tests for constants module.
"""

import pytest
from src.constants import (
    DICT_GOOGLE_IMAGES,
    DICT_FORVO,
    SEARCH_MODE_FORWARD,
    SEARCH_MODE_EXACT,
    DEFAULT_MAX_SEARCH,
    DEFAULT_DICT_SEARCH,
    FIELD_EXPORT_DONT_EXPORT,
    FIELD_EXPORT_ADD,
)


class TestConstants:
    """Test that constants are defined correctly."""
    
    def test_special_dict_names(self):
        """Test special dictionary name constants."""
        assert DICT_GOOGLE_IMAGES == "Google Images"
        assert DICT_FORVO == "Forvo"
    
    def test_search_modes(self):
        """Test search mode constants."""
        assert SEARCH_MODE_FORWARD == "Forward"
        assert SEARCH_MODE_EXACT == "Exact"
    
    def test_default_limits(self):
        """Test default limit constants."""
        assert DEFAULT_MAX_SEARCH == 1000
        assert DEFAULT_DICT_SEARCH == 50
        assert isinstance(DEFAULT_MAX_SEARCH, int)
        assert isinstance(DEFAULT_DICT_SEARCH, int)
    
    def test_field_export_options(self):
        """Test field export option constants."""
        assert FIELD_EXPORT_DONT_EXPORT == "Don't Export"
        assert FIELD_EXPORT_ADD == "add"
    
    def test_constants_are_strings_or_ints(self):
        """Test that constants have appropriate types."""
        string_constants = [
            DICT_GOOGLE_IMAGES,
            DICT_FORVO,
            SEARCH_MODE_FORWARD,
            FIELD_EXPORT_DONT_EXPORT,
        ]
        
        for const in string_constants:
            assert isinstance(const, str)
            assert len(const) > 0
        
        int_constants = [DEFAULT_MAX_SEARCH, DEFAULT_DICT_SEARCH]
        
        for const in int_constants:
            assert isinstance(const, int)
            assert const > 0
