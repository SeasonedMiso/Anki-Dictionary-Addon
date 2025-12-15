# -*- coding: utf-8 -*-
"""
Text utility functions for the dictionary application.

Provides functions for text cleaning, formatting, and processing including:
- HTML tag removal and cleaning
- Bracket and special character removal
- Text truncation and normalization
- Japanese text detection and highlighting
"""

import re


def strip_html_tags(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: Text potentially containing HTML tags
        
    Returns:
        Text with HTML tags removed
    """
    if not text:
        return text
    return re.sub(r'<[^>]+>', '', text)


def clean_html(text: str) -> str:
    """
    Clean HTML by removing extra whitespace and newlines.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text with normalized whitespace
    """
    if not text:
        return text
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def escape_punctuation(text: str) -> str:
    """
    Escape special regex characters in text.
    
    Args:
        text: Text containing special characters
        
    Returns:
        Text with special regex characters escaped
    """
    if not text:
        return text
    # Escape all special regex characters
    special_chars = r'\.^$*+?{}[]|()'
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text (tabs, multiple spaces, newlines).
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return text
    # Replace all whitespace sequences with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add if truncated (default: "...")
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    # Account for suffix length
    truncate_at = max_length - len(suffix)
    if truncate_at <= 0:
        return text[:max_length]
    
    return text[:truncate_at] + suffix


def is_japanese_text(text: str) -> bool:
    """
    Detect if text contains Japanese characters.
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains Japanese characters (hiragana, katakana, or kanji)
    """
    if not text:
        return False
    
    # Check for hiragana, katakana, or kanji
    for char in text:
        code = ord(char)
        # Hiragana: U+3040 to U+309F
        # Katakana: U+30A0 to U+30FF
        # Kanji: U+4E00 to U+9FFF
        if (0x3040 <= code <= 0x309F or
            0x30A0 <= code <= 0x30FF or
            0x4E00 <= code <= 0x9FFF):
            return True
    
    return False


def highlight_term(text: str, term: str) -> str:
    """
    Highlight a search term in text with HTML span.
    
    Args:
        text: Text containing the term
        term: Term to highlight
        
    Returns:
        Text with term wrapped in highlight span
    """
    if not text or not term:
        return text
    
    # Escape special regex characters in term
    escaped_term = escape_punctuation(term)
    # Use case-insensitive matching
    pattern = f'({escaped_term})'
    replacement = r'<span class="targetTerm">\1</span>'
    
    return re.sub(pattern, replacement, text, flags=re.IGNORECASE)


def highlight_example_sentences(text: str) -> str:
    """
    Highlight example sentences (text within 「」 brackets) with HTML span.
    
    Args:
        text: Text containing example sentences
        
    Returns:
        Text with example sentences wrapped in highlight span
    """
    if not text:
        return text
    
    # Match text within 「」 brackets
    pattern = r'(「[^」]*」)'
    replacement = r'<span class="exampleSentence">\1</span>'
    
    return re.sub(pattern, replacement, text)


def remove_brackets(text: str) -> str:
    """
    Remove all bracket content from text.
    
    Removes content within: [], (), 《》, （）
    Keeps content but removes brackets for: 「」
    
    Args:
        text: Text containing brackets
        
    Returns:
        Text with bracket content removed (except 「」 which keeps content)
    """
    if not text:
        return text
    
    # Remove content within various bracket types
    text = re.sub(r'\[[^\]]*\]', '', text)  # []
    text = re.sub(r'\([^)]*\)', '', text)   # ()
    text = re.sub(r'《[^》]*》', '', text)   # 《》
    text = re.sub(r'（[^）]*）', '', text)   # （）
    # For 「」, remove brackets but keep content
    text = re.sub(r'「|」', '', text)  # Remove 「」 brackets only
    
    return text


def clean_term(term: str, max_length: int = 30, remove_special: bool = True) -> str:
    """
    Clean a search term for lookup.
    
    Removes:
    - HTML tags
    - Bracket content ([], (), 《》, （）, 「」)
    - Special characters (if remove_special=True)
    - Extra whitespace
    - Truncates to max_length
    
    Args:
        term: Raw search term
        max_length: Maximum length for cleaned term (default: 30)
        remove_special: Whether to remove special characters (default: True)
        
    Returns:
        Cleaned term ready for search
    """
    if not term:
        return term
    
    # Remove HTML tags
    term = strip_html_tags(term)
    
    # Remove bracket content (including all bracket types)
    term = remove_brackets(term)
    
    # Remove special characters if requested
    if remove_special:
        # Keep alphanumeric, Japanese characters, and basic punctuation
        # Remove: % _ and other special chars, but escape quotes
        term = re.sub(r'[%_]', '', term)
        # Escape single quotes instead of removing them
        term = term.replace("'", "\\'")
    
    # Normalize whitespace
    term = normalize_whitespace(term)
    
    # Limit length
    term = term[:max_length]
    
    return term.strip()


def format_definition_text(text: str, max_length: int = 200) -> str:
    """
    Format definition text for display.
    
    Args:
        text: Raw definition text
        max_length: Maximum length for display
        
    Returns:
        Formatted definition text
    """
    if not text:
        return text
    
    # Clean HTML and normalize
    text = clean_html(text)
    text = normalize_whitespace(text)
    
    # Truncate if needed
    if len(text) > max_length:
        text = truncate_text(text, max_length)
    
    return text


def extract_reading(text: str) -> str:
    """
    Extract reading/phonetic information from text.
    
    Looks for patterns like [reading], (reading), 【reading】
    
    Args:
        text: Text containing reading information
        
    Returns:
        Extracted reading or empty string
    """
    if not text:
        return ""
    
    # Try different bracket patterns for readings
    patterns = [
        r'\[([^\]]+)\]',    # [reading]
        r'\(([^)]+)\)',     # (reading)
        r'【([^】]+)】',      # 【reading】
        r'〔([^〕]+)〕'       # 〔reading〕
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            reading = match.group(1).strip()
            # Check if it looks like a reading (contains hiragana/katakana)
            if is_japanese_text(reading):
                return reading
    
    return ""


def split_compound_word(word: str) -> list[str]:
    """
    Split compound Japanese words at likely boundaries.
    
    Args:
        word: Japanese compound word
        
    Returns:
        List of word parts
    """
    if not word or not is_japanese_text(word):
        return [word]
    
    # Simple heuristic: split at hiragana-kanji boundaries
    parts = []
    current_part = ""
    prev_type = None
    
    for char in word:
        code = ord(char)
        
        # Determine character type
        if 0x3040 <= code <= 0x309F:  # Hiragana
            char_type = 'hiragana'
        elif 0x30A0 <= code <= 0x30FF:  # Katakana
            char_type = 'katakana'
        elif 0x4E00 <= code <= 0x9FFF:  # Kanji
            char_type = 'kanji'
        else:
            char_type = 'other'
        
        # Split at type boundaries (except hiragana-hiragana)
        if (prev_type and prev_type != char_type and 
            not (prev_type == 'hiragana' and char_type == 'hiragana')):
            if current_part:
                parts.append(current_part)
                current_part = ""
        
        current_part += char
        prev_type = char_type
    
    if current_part:
        parts.append(current_part)
    
    return parts if len(parts) > 1 else [word]


def validate_search_term(term: str) -> tuple[bool, str]:
    """
    Validate a search term.
    
    Args:
        term: Search term to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not term or not term.strip():
        return False, "Search term cannot be empty"
    
    cleaned = clean_term(term)
    if not cleaned:
        return False, "Search term contains no valid characters"
    
    if len(cleaned) > 100:
        return False, "Search term is too long (max 100 characters)"
    
    # Check for potentially problematic patterns
    if re.search(r'[<>"\']', cleaned):
        return False, "Search term contains invalid characters"
    
    return True, ""


def format_frequency_display(frequency: int) -> str:
    """
    Format frequency number for display.
    
    Args:
        frequency: Frequency rank number
        
    Returns:
        Formatted frequency string
    """
    if frequency <= 0:
        return "Unknown"
    
    # Add thousand separators
    formatted = f"{frequency:,}"
    
    # Add descriptive label
    if frequency <= 500:
        return f"{formatted} (Very Common)"
    elif frequency <= 1500:
        return f"{formatted} (Common)"
    elif frequency <= 5000:
        return f"{formatted} (Uncommon)"
    elif frequency <= 15000:
        return f"{formatted} (Rare)"
    else:
        return f"{formatted} (Very Rare)"
