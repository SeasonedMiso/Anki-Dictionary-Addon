# -*- coding: utf-8 -*-
"""
Configuration data models.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class DictionaryGroup:
    """Configuration for a dictionary group."""
    dictionaries: List[str] = field(default_factory=list)
    custom_font: bool = False
    font: Optional[str] = None


@dataclass
class ExportTemplate:
    """Configuration for an export template."""
    note_type: str
    sentence: str
    secondary: str
    notes: str
    word: str
    image: str
    audio: str
    unspecified: str
    specific: Dict[str, List[str]] = field(default_factory=dict)
    separator: str = "<br><br>"


@dataclass
class AutoDefinitionSetting:
    """Configuration for automatic definition addition."""
    name: str
    limit: int = 1


@dataclass
class DictionaryConfig:
    """Main configuration for the dictionary addon."""
    
    # Dictionary Groups
    dictionary_groups: Dict[str, DictionaryGroup] = field(default_factory=dict)
    
    # Export Templates
    export_templates: Dict[str, ExportTemplate] = field(default_factory=dict)
    
    # Google Images Settings
    google_image_fields: List[str] = field(default_factory=list)
    google_image_add_type: str = "add"
    google_search_region: str = "United States"
    safe_search: bool = True
    
    # Forvo Settings
    forvo_fields: List[str] = field(default_factory=list)
    forvo_add_type: str = "add"
    forvo_language: str = "Japanese"
    
    # Display Settings
    dict_on_start: bool = False
    highlight_sentences: bool = True
    highlight_target: bool = True
    show_target: bool = False
    tooltips: bool = True
    dict_always_on_top: bool = False
    
    # Search Settings
    max_search: int = 1000
    dict_search: int = 50
    search_mode: str = "Forward"
    deinflect: bool = True
    current_group: str = "All"
    
    # Japanese Settings
    j_reading_cards: bool = True
    j_reading_edit: bool = True
    
    # Image Settings
    max_height: int = 400
    max_width: int = 400
    
    # Brackets
    front_bracket: str = "【"
    back_bracket: str = "】"
    
    # UI Settings
    day: bool = True
    one_tab: bool = False
    dict_size_pos: Optional[List[int]] = None
    exporter_size_pos: Optional[List[int]] = None
    font_sizes: List[int] = field(default_factory=lambda: [12, 22])
    
    # Hotkeys
    global_hotkeys: bool = True
    open_on_global: bool = True
    
    # Audio Settings
    mp3_convert: bool = True
    failed_ffmpeg_installation: bool = False
    condensed_audio_directory: Optional[str] = None
    disable_condensed: bool = False
    
    # Current State
    current_template: Optional[str] = None
    current_deck: Optional[str] = None
    
    # Auto Features
    display_again: bool = True
    auto_definition_settings: Optional[List[AutoDefinitionSetting]] = None
    auto_add_definitions: bool = False
    auto_add_cards: bool = False
    unknowns_to_search: int = 3
    
    # Mass Generation
    mass_generation_preferences: Optional[Dict[str, Any]] = None
    
    # Last Used
    exporter_last_tags: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for JSON serialization."""
        # This would need proper implementation based on your needs
        return self.__dict__
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DictionaryConfig':
        """Create config from dictionary."""
        # This would need proper implementation based on your needs
        return cls(**data)
