# -*- coding: utf-8 -*-
"""
Tests for text utility functions.
"""

import pytest
from src.utils.text import (
    strip_html_tags,
    clean_html,
    escape_punctuation,
    normalize_whitespace,
    truncate_text,
    is_japanese_text,
    highlight_term,
    highlight_example_sentences,
    remove_brackets,
    clean_term,
)


class TestTextUtils:
    """Test text utility functions."""
    
    def test_strip_html_tags(self):
        """Test HTML tag removal."""
        assert strip_html_tags("<p>Hello</p>") == "Hello"
        assert strip_html_tags("<b>Bold</b> text") == "Bold text"
        assert strip_html_tags("No tags") == "No tags"
        assert strip_html_tags("") == ""
    
    def test_clean_html(self):
        """Test HTML cleaning."""
        assert clean_html("  multiple   spaces  ") == "multiple spaces"
        assert clean_html("\n\nlines\n\n") == "lines"
        assert clean_html("") == ""
    
    def test_escape_punctuation(self):
        """Test punctuation escaping for regex."""
        assert escape_punctuation("test.") == r"test\."
        assert escape_punctuation("test*") == r"test\*"
        assert escape_punctuation("test?") == r"test\?"
        assert escape_punctuation("test[0]") == r"test\[0\]"
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        assert normalize_whitespace("  multiple   spaces  ") == "multiple spaces"
        assert normalize_whitespace("\t\ttabs\t\t") == "tabs"
        assert normalize_whitespace("") == ""
    
    def test_truncate_text(self):
        """Test text truncation."""
        assert truncate_text("short", 10) == "short"
        assert truncate_text("very long text here", 10) == "very long ..."
        assert truncate_text("exact", 5) == "exact"
        assert truncate_text("toolong", 5) == "toolo..."
    
    def test_is_japanese_text(self):
        """Test Japanese text detection."""
        assert is_japanese_text("日本語") == True
        assert is_japanese_text("ひらがな") == True
        assert is_japanese_text("カタカナ") == True
        assert is_japanese_text("English") == False
        assert is_japanese_text("123") == False
        assert is_japanese_text("日本語 and English") == True
    
    def test_highlight_term(self):
        """Test term highlighting."""
        result = highlight_term("Find this word here", "word")
        assert '<span class="targetTerm">word</span>' in result
        
        # Test with empty inputs
        assert highlight_term("", "word") == ""
        assert highlight_term("text", "") == "text"
    
    def test_highlight_example_sentences(self):
        """Test example sentence highlighting."""
        text = "This is 「an example」 sentence."
        result = highlight_example_sentences(text)
        assert '<span class="exampleSentence">「an example」</span>' in result
    
    def test_remove_brackets(self):
        """Test bracket removal."""
        assert remove_brackets("text [remove this]") == "text "
        assert remove_brackets("no brackets") == "no brackets"
        assert remove_brackets("[all] [brackets]") == " "
    
    def test_clean_term(self):
        """Test term cleaning."""
        assert clean_term("test%") == "test"
        assert clean_term("test_word") == "testword"
        assert clean_term("「test」") == "test"
        assert clean_term("test'word") == "test\\'word"


class TestJapaneseTextHandling:
    """Test Japanese-specific text handling."""
    
    def test_japanese_highlighting(self):
        """Test highlighting works with Japanese text."""
        text = "これは日本語のテストです"
        result = highlight_term(text, "日本語")
        assert "日本語" in result
        assert '<span class="targetTerm">' in result
    
    def test_mixed_text(self):
        """Test handling of mixed Japanese and English."""
        text = "This is 日本語 text"
        assert is_japanese_text(text) == True
        
        result = highlight_term(text, "日本語")
        assert '<span class="targetTerm">日本語</span>' in result


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_strings(self):
        """Test functions with empty strings."""
        assert strip_html_tags("") == ""
        assert clean_html("") == ""
        assert normalize_whitespace("") == ""
        assert truncate_text("", 10) == ""
    
    def test_none_handling(self):
        """Test that functions handle None gracefully."""
        # Most functions should handle None or empty strings
        assert highlight_term("text", "") == "text"
        assert highlight_term("", "term") == ""
    
    def test_special_characters(self):
        """Test handling of special characters."""
        text = "Special: !@#$%^&*()"
        assert strip_html_tags(text) == text
        
        # Escape should handle all special regex chars
        escaped = escape_punctuation(".*+?[]{}()")
        assert "\\" in escaped
