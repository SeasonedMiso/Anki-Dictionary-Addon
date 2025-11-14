# -*- coding: utf-8 -*-
"""
Text processing utilities.
"""

import re
from typing import Optional


def strip_html_tags(text: str) -> str:
    """
    Remove all HTML tags from text.
    
    Args:
        text: Text containing HTML tags
        
    Returns:
        Text with HTML tags removed
    """
    return re.sub(r'<[^>]+>', '', text)


def clean_html(html: str) -> str:
    """
    Clean HTML content for display.
    
    Args:
        html: HTML content to clean
        
    Returns:
        Cleaned HTML
    """
    # Remove excessive whitespace
    html = re.sub(r'\s+', ' ', html)
    # Normalize line breaks
    html = html.replace('\r\n', '\n').replace('\r', '\n')
    return html.strip()


def escape_punctuation(text: str) -> str:
    """
    Escape special regex characters in text.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for regex
    """
    return re.sub(r'([.*+(\[\]{}\\?)!])', r'\\\1', text)


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    return ' '.join(text.split())


def truncate_text(text: str, max_length: int = 40, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def is_japanese_text(text: str) -> bool:
    """
    Check if text contains Japanese characters.
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains Japanese characters
    """
    return any(
        '\u4e00' <= c <= '\u9fff' or  # Kanji
        '\u3040' <= c <= '\u309f' or  # Hiragana
        '\u30a0' <= c <= '\u30ff'     # Katakana
        for c in text
    )


def highlight_term(
    text: str,
    term: str,
    css_class: str = "targetTerm"
) -> str:
    """
    Highlight a term in text with HTML span.
    
    Args:
        text: Text to search in
        term: Term to highlight
        css_class: CSS class for highlighting
        
    Returns:
        Text with highlighted term
    """
    if not text or not term:
        return text
    
    try:
        # Split text into HTML tags and content
        parts = re.split(r'(<[^>]*>)', text)
        
        # Only apply highlighting to non-tag parts
        for i in range(0, len(parts), 2):
            if parts[i]:
                # For Japanese text, we don't need word boundaries
                if is_japanese_text(term):
                    pattern = '(' + escape_punctuation(term) + ')'
                else:
                    # For non-Japanese text, use word boundaries
                    pattern = r'\b(' + escape_punctuation(term) + r')\b'
                
                parts[i] = re.sub(
                    pattern,
                    rf'<span class="{css_class}">\1</span>',
                    parts[i]
                )
        
        return ''.join(parts)
    except Exception as e:
        print(f"Error during highlight_term: {e}")
        return text


def highlight_example_sentences(text: str) -> str:
    """
    Highlight Japanese example sentences (text in 「」).
    
    Args:
        text: Text containing example sentences
        
    Returns:
        Text with highlighted example sentences
    """
    return re.sub(
        r'「([^」]+)」(?![^<]*>)',
        r'<span class="exampleSentence">「\1」</span>',
        text
    )


def remove_brackets(text: str) -> str:
    """
    Remove bracketed content from text.
    
    Args:
        text: Text containing brackets
        
    Returns:
        Text with brackets removed
    """
    return re.sub(r'\[[^\]]+?\]', '', text)


def clean_term(term: str) -> str:
    """
    Clean a search term for database queries.
    
    Args:
        term: Term to clean
        
    Returns:
        Cleaned term
    """
    return (term
            .replace("'", "\\'")
            .replace('%', '')
            .replace('_', '')
            .replace('「', '')
            .replace('」', ''))
