# -*- coding: utf-8 -*-
"""
Constants and configuration values for the Anki Dictionary addon.
"""

from typing import Final

# Version
VERSION: Final[str] = "0.1.0"

# Field Export Options
FIELD_EXPORT_DONT_EXPORT: Final[str] = "Don't Export"
FIELD_EXPORT_ADD: Final[str] = "add"
FIELD_EXPORT_OVERWRITE: Final[str] = "overwrite"
FIELD_EXPORT_IF_EMPTY: Final[str] = "no"

# Search Modes
SEARCH_MODE_FORWARD: Final[str] = "Forward"
SEARCH_MODE_BACKWARD: Final[str] = "Backward"
SEARCH_MODE_ANYWHERE: Final[str] = "Anywhere"
SEARCH_MODE_EXACT: Final[str] = "Exact"
SEARCH_MODE_DEFINITION: Final[str] = "Definition"
SEARCH_MODE_EXAMPLE: Final[str] = "Example"
SEARCH_MODE_PRONUNCIATION: Final[str] = "Pronunciation"

# Special Dictionary Names
DICT_GOOGLE_IMAGES: Final[str] = "Google Images"
DICT_FORVO: Final[str] = "Forvo"

# Default Limits
DEFAULT_MAX_SEARCH: Final[int] = 1000
DEFAULT_DICT_SEARCH: Final[int] = 50
DEFAULT_MAX_WIDTH: Final[int] = 400
DEFAULT_MAX_HEIGHT: Final[int] = 400
DEFAULT_UNKNOWNS_TO_SEARCH: Final[int] = 3

# UI Messages
MSG_NO_RESULTS: Final[str] = "No dictionary entries were found for"
MSG_DUPLICATE_DEFINITION: Final[str] = "A card cannot contain duplicate definitions."
MSG_INVALID_CARD: Final[str] = "The currently selected template and values will lead to an invalid card. Please try again."
MSG_NOTETYPE_NOT_FOUND: Final[str] = "The notetype for the currently selected template does not exist in the currently loaded profile."
MSG_CARD_ADD_FAILED: Final[str] = "A card could not be added with this current configuration. Please ensure that your template is configured correctly for this collection."

# File Paths
TEMP_DIR_NAME: Final[str] = "temp"
USER_FILES_DIR: Final[str] = "user_files"
DB_DIR: Final[str] = "db"
DICTIONARIES_DIR: Final[str] = "dictionaries"
THEMES_DIR: Final[str] = "themes"
ICONS_DIR: Final[str] = "icons"
FONTS_DIR: Final[str] = "fonts"

# Database
DB_FILENAME: Final[str] = "dictionaries.sqlite"
CONJUGATION_DIR: Final[str] = "conjugation"

# Hotkeys (Platform-specific will be handled in UI layer)
HOTKEY_SEARCH: Final[str] = "Ctrl+S"
HOTKEY_SEARCH_COLLECTION: Final[str] = "Ctrl+Shift+B"
HOTKEY_CLOSE_DICT: Final[str] = "Ctrl+W"
HOTKEY_ESCAPE: Final[str] = "Esc"

# HTML/CSS Classes
CSS_CLASS_TERM: Final[str] = "term"
CSS_CLASS_ALTTERM: Final[str] = "altterm"
CSS_CLASS_PRONUNCIATION: Final[str] = "pronunciation"
CSS_CLASS_TARGET_TERM: Final[str] = "targetTerm"
CSS_CLASS_EXAMPLE_SENTENCE: Final[str] = "exampleSentence"

# Regex Patterns
PATTERN_HTML_TAGS: Final[str] = r"<[^>]+>"
PATTERN_BRACKETS: Final[str] = r'\[[^\]]+?\]'
PATTERN_JAPANESE_QUOTES: Final[str] = r'「([^」]+)」'

# Window Titles
WINDOW_TITLE_DICT: Final[str] = "Anki Dictionary"
WINDOW_TITLE_SETTINGS: Final[str] = "Anki Dictionary Settings"
WINDOW_TITLE_EXPORTER: Final[str] = "Anki Card Exporter"
WINDOW_TITLE_EXPORT_DEFS: Final[str] = "Anki Dictionary: Export Definitions"

# Default Brackets
DEFAULT_FRONT_BRACKET: Final[str] = "【"
DEFAULT_BACK_BRACKET: Final[str] = "】"

# Separators
DEFAULT_SEPARATOR: Final[str] = "<br><br>"
