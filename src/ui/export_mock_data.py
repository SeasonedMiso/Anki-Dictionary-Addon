# -*- coding: utf-8 -*-
"""
Export System Mock Data.

This module provides sample data for testing and demonstrating the export UI system.
All data structures follow the export system specifications and provide realistic
examples for development and testing.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class ExportQueueItem:
    """Export queue item data structure."""
    id: str
    word: str
    phonetic: Optional[str] = None
    definitions: List[Dict[str, str]] = field(default_factory=list)
    source_dictionary: str = "Unknown"
    template_id: str = "default_japanese"
    custom_fields: Dict[str, str] = field(default_factory=dict)
    added_timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0


@dataclass
class CardTemplate:
    """Card template data structure."""
    id: str
    name: str
    front_template: str
    back_template: str
    css_styling: str
    fields: List[str] = field(default_factory=list)
    is_default: bool = False
    created_date: datetime = field(default_factory=datetime.now)
    modified_date: datetime = field(default_factory=datetime.now)


@dataclass
class ExportHistoryRecord:
    """Export history record data structure."""
    id: str
    word: str
    template_used: str
    target_deck: str
    export_timestamp: datetime
    anki_note_id: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None


# Sample export queue items
SAMPLE_QUEUE_ITEMS = [
    {
        "id": "queue_001",
        "word": "食べる",
        "phonetic": "たべる",
        "definitions": [
            {"type": "verb", "text": "to eat"},
            {"type": "verb", "text": "to live on (e.g. a salary)"},
            {"type": "verb", "text": "to eat away; to corrode"}
        ],
        "source_dictionary": "JMdict",
        "template_id": "default_japanese",
        "custom_fields": {},
        "added_timestamp": datetime.now() - timedelta(minutes=30),
        "priority": 0
    },
    {
        "id": "queue_002", 
        "word": "勉強",
        "phonetic": "べんきょう",
        "definitions": [
            {"type": "noun", "text": "study; diligence"},
            {"type": "verb", "text": "to study; to learn"}
        ],
        "source_dictionary": "JMdict",
        "template_id": "default_japanese",
        "custom_fields": {"frequency": "500"},
        "added_timestamp": datetime.now() - timedelta(minutes=15),
        "priority": 1
    },
    {
        "id": "queue_003",
        "word": "美しい",
        "phonetic": "うつくしい",
        "definitions": [
            {"type": "adjective", "text": "beautiful; lovely; pretty"},
            {"type": "adjective", "text": "fair; clean; pure"}
        ],
        "source_dictionary": "JMdict",
        "template_id": "default_japanese",
        "custom_fields": {"pitch_accent": "3"},
        "added_timestamp": datetime.now() - timedelta(minutes=5),
        "priority": 0
    },
    {
        "id": "queue_004",
        "word": "図書館",
        "phonetic": "としょかん",
        "definitions": [
            {"type": "noun", "text": "library"}
        ],
        "source_dictionary": "JMdict",
        "template_id": "default_japanese",
        "custom_fields": {"frequency": "2500"},
        "added_timestamp": datetime.now() - timedelta(minutes=2),
        "priority": 0
    },
    {
        "id": "queue_005",
        "word": "頑張る",
        "phonetic": "がんばる",
        "definitions": [
            {"type": "verb", "text": "to persevere; to persist"},
            {"type": "verb", "text": "to insist that; to stick to (one's opinion)"},
            {"type": "verb", "text": "to remain in a place; to stick to one's post"}
        ],
        "source_dictionary": "JMdict",
        "template_id": "default_japanese",
        "custom_fields": {"frequency": "800", "pitch_accent": "0"},
        "added_timestamp": datetime.now() - timedelta(seconds=30),
        "priority": 2
    }
]

# Default card templates
DEFAULT_TEMPLATES = {
    "default_japanese": CardTemplate(
        id="default_japanese",
        name="Basic Japanese",
        front_template="""
<div class="card-front">
    <div class="word">{{Word}}</div>
    {{#Phonetic}}
    <div class="phonetic">[{{Phonetic}}]</div>
    {{/Phonetic}}
</div>
        """.strip(),
        back_template="""
<div class="card-back">
    <div class="word">{{Word}}</div>
    {{#Phonetic}}
    <div class="phonetic">[{{Phonetic}}]</div>
    {{/Phonetic}}
    
    <div class="definitions">
        {{#Definitions}}
        <div class="definition">
            <span class="pos-tag">{{Type}}</span>
            <span class="def-text">{{Text}}</span>
        </div>
        {{/Definitions}}
    </div>
    
    {{#Examples}}
    <div class="examples">
        <div class="example-header">Examples:</div>
        {{#ExampleList}}
        <div class="example">• {{.}}</div>
        {{/ExampleList}}
    </div>
    {{/Examples}}
</div>
        """.strip(),
        css_styling="""
.card-front, .card-back {
    font-family: "Hiragino Sans", "Yu Gothic", "Meiryo", sans-serif;
    text-align: center;
    background: #0f0f0f;
    color: #e6e6e6;
    padding: 20px;
}

.word {
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 8px;
    color: #4a9eff;
}

.phonetic {
    font-size: 18px;
    color: #9aa0ad;
    margin-bottom: 16px;
}

.definitions {
    text-align: left;
    margin-top: 16px;
}

.definition {
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}

.pos-tag {
    background: #4a9eff;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 12px;
    font-weight: bold;
    flex-shrink: 0;
}

.def-text {
    flex: 1;
    line-height: 1.4;
}

.examples {
    margin-top: 16px;
    text-align: left;
}

.example-header {
    font-weight: bold;
    margin-bottom: 8px;
    color: #9aa0ad;
}

.example {
    margin-bottom: 4px;
    font-style: italic;
    color: #9aa0ad;
}
        """.strip(),
        fields=["Word", "Phonetic", "Definitions", "Examples", "Audio", "Image"],
        is_default=True
    ),
    
    "minimal_japanese": CardTemplate(
        id="minimal_japanese",
        name="Minimal Japanese",
        front_template="""
<div class="minimal-front">
    {{Word}}
</div>
        """.strip(),
        back_template="""
<div class="minimal-back">
    <div class="word">{{Word}}</div>
    {{#Phonetic}}<div class="phonetic">[{{Phonetic}}]</div>{{/Phonetic}}
    <div class="definition">{{FirstDefinition}}</div>
</div>
        """.strip(),
        css_styling="""
.minimal-front, .minimal-back {
    font-family: "Hiragino Sans", "Yu Gothic", "Meiryo", sans-serif;
    text-align: center;
    background: #ffffff;
    color: #1a1a1a;
    padding: 40px 20px;
}

.minimal-front {
    font-size: 48px;
    font-weight: bold;
}

.word {
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 8px;
}

.phonetic {
    font-size: 16px;
    color: #666666;
    margin-bottom: 16px;
}

.definition {
    font-size: 18px;
    line-height: 1.4;
}
        """.strip(),
        fields=["Word", "Phonetic", "FirstDefinition"],
        is_default=False
    ),
    
    "comprehensive_japanese": CardTemplate(
        id="comprehensive_japanese",
        name="Comprehensive Japanese",
        front_template="""
<div class="comp-front">
    <div class="word">{{Word}}</div>
    {{#Phonetic}}<div class="phonetic">[{{Phonetic}}]</div>{{/Phonetic}}
    {{#PitchAccent}}<div class="pitch">Pitch: {{PitchAccent}}</div>{{/PitchAccent}}
</div>
        """.strip(),
        back_template="""
<div class="comp-back">
    <div class="word">{{Word}}</div>
    {{#Phonetic}}<div class="phonetic">[{{Phonetic}}]</div>{{/Phonetic}}
    
    {{#Frequency}}<div class="frequency">Frequency: {{Frequency}}</div>{{/Frequency}}
    {{#PitchAccent}}<div class="pitch">Pitch Accent: {{PitchAccent}}</div>{{/PitchAccent}}
    
    <div class="definitions">
        {{#Definitions}}
        <div class="definition">
            <span class="pos-tag">{{Type}}</span>
            <span class="def-text">{{Text}}</span>
        </div>
        {{/Definitions}}
    </div>
    
    {{#Examples}}
    <div class="examples">
        <div class="example-header">Examples:</div>
        {{#ExampleList}}
        <div class="example">• {{.}}</div>
        {{/ExampleList}}
    </div>
    {{/Examples}}
    
    {{#Audio}}<div class="audio">🔊 Audio available</div>{{/Audio}}
    {{#Image}}<div class="image">🖼️ Image available</div>{{/Image}}
</div>
        """.strip(),
        css_styling="""
.comp-front, .comp-back {
    font-family: "Hiragino Sans", "Yu Gothic", "Meiryo", sans-serif;
    text-align: center;
    background: #1a1f2e;
    color: #e1e8f0;
    padding: 20px;
}

.word {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 8px;
    color: #3a7afe;
}

.phonetic {
    font-size: 16px;
    color: #8a9bb8;
    margin-bottom: 8px;
}

.frequency, .pitch {
    font-size: 12px;
    color: #8a9bb8;
    margin-bottom: 4px;
}

.definitions {
    text-align: left;
    margin-top: 16px;
}

.definition {
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}

.pos-tag {
    background: #3a7afe;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
    flex-shrink: 0;
}

.def-text {
    flex: 1;
    line-height: 1.4;
}

.examples {
    margin-top: 16px;
    text-align: left;
}

.example-header {
    font-weight: bold;
    margin-bottom: 8px;
    color: #8a9bb8;
}

.example {
    margin-bottom: 4px;
    font-style: italic;
    color: #8a9bb8;
}

.audio, .image {
    margin-top: 8px;
    font-size: 12px;
    color: #8a9bb8;
}
        """.strip(),
        fields=["Word", "Phonetic", "Definitions", "Examples", "Audio", "Image", "Frequency", "PitchAccent"],
        is_default=False
    )
}

# Sample export history
SAMPLE_EXPORT_HISTORY = [
    ExportHistoryRecord(
        id="export_001",
        word="勉強",
        template_used="Basic Japanese",
        target_deck="Japanese Core",
        export_timestamp=datetime.now() - timedelta(days=2, hours=3),
        anki_note_id=1001,
        success=True
    ),
    ExportHistoryRecord(
        id="export_002",
        word="食べる",
        template_used="Basic Japanese", 
        target_deck="Japanese Core",
        export_timestamp=datetime.now() - timedelta(days=1, hours=5),
        anki_note_id=1002,
        success=True
    ),
    ExportHistoryRecord(
        id="export_003",
        word="美しい",
        template_used="Comprehensive Japanese",
        target_deck="Japanese Adjectives",
        export_timestamp=datetime.now() - timedelta(hours=8),
        anki_note_id=1003,
        success=True
    ),
    ExportHistoryRecord(
        id="export_004",
        word="難しい",
        template_used="Basic Japanese",
        target_deck="Japanese Core",
        export_timestamp=datetime.now() - timedelta(hours=2),
        anki_note_id=None,
        success=False,
        error_message="Deck not found: Japanese Core"
    ),
    ExportHistoryRecord(
        id="export_005",
        word="図書館",
        template_used="Minimal Japanese",
        target_deck="Japanese Nouns",
        export_timestamp=datetime.now() - timedelta(minutes=30),
        anki_note_id=1005,
        success=True
    )
]

# Export statistics
EXPORT_STATS = {
    "total_exports": len(SAMPLE_EXPORT_HISTORY),
    "successful_exports": len([r for r in SAMPLE_EXPORT_HISTORY if r.success]),
    "failed_exports": len([r for r in SAMPLE_EXPORT_HISTORY if not r.success]),
    "most_used_template": "Basic Japanese",
    "most_used_deck": "Japanese Core",
    "exports_this_week": 3,
    "exports_this_month": 15,
    "average_exports_per_day": 2.1
}

# Template field mappings
TEMPLATE_FIELD_MAPPINGS = {
    "Word": "word",
    "Phonetic": "phonetic", 
    "Definitions": "definitions",
    "FirstDefinition": "first_definition",
    "Examples": "examples",
    "Audio": "audio_file",
    "Image": "image_file",
    "Frequency": "frequency",
    "PitchAccent": "pitch_accent",
    "SourceDictionary": "source_dictionary"
}

# Export validation rules
EXPORT_VALIDATION_RULES = {
    "required_fields": ["Word"],
    "max_definition_length": 500,
    "max_example_length": 200,
    "allowed_pos_tags": [
        "noun", "verb", "adjective", "adverb", "particle", 
        "conjunction", "interjection", "prefix", "suffix",
        "expression", "pronoun", "counter"
    ],
    "max_examples_per_card": 5,
    "max_definitions_per_card": 10
}


def get_sample_queue_item(word: str) -> Optional[Dict[str, Any]]:
    """
    Get sample queue item by word.
    
    Args:
        word: Word to search for
        
    Returns:
        Queue item dictionary or None if not found
    """
    for item in SAMPLE_QUEUE_ITEMS:
        if item["word"] == word:
            return item
    return None


def get_template_by_id(template_id: str) -> Optional[CardTemplate]:
    """
    Get template by ID.
    
    Args:
        template_id: Template ID to search for
        
    Returns:
        CardTemplate or None if not found
    """
    return DEFAULT_TEMPLATES.get(template_id)


def get_export_history_for_word(word: str) -> List[ExportHistoryRecord]:
    """
    Get export history records for a specific word.
    
    Args:
        word: Word to search for
        
    Returns:
        List of export history records
    """
    return [record for record in SAMPLE_EXPORT_HISTORY if record.word == word]


def validate_export_item(item: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate export item against rules.
    
    Args:
        item: Export item to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    for field in EXPORT_VALIDATION_RULES["required_fields"]:
        if not item.get(field.lower()):
            errors.append(f"Missing required field: {field}")
    
    # Check definition length
    definitions = item.get("definitions", [])
    for i, defn in enumerate(definitions):
        def_text = defn.get("text", "")
        if len(def_text) > EXPORT_VALIDATION_RULES["max_definition_length"]:
            errors.append(f"Definition {i+1} too long ({len(def_text)} chars)")
    
    # Check examples length
    examples = item.get("examples", [])
    for i, example in enumerate(examples):
        if len(example) > EXPORT_VALIDATION_RULES["max_example_length"]:
            errors.append(f"Example {i+1} too long ({len(example)} chars)")
    
    # Check limits
    if len(definitions) > EXPORT_VALIDATION_RULES["max_definitions_per_card"]:
        errors.append(f"Too many definitions ({len(definitions)})")
    
    if len(examples) > EXPORT_VALIDATION_RULES["max_examples_per_card"]:
        errors.append(f"Too many examples ({len(examples)})")
    
    return len(errors) == 0, errors


def generate_mock_export_progress():
    """
    Generator for mock export progress updates.
    
    Yields:
        Progress dictionaries with current item and completion percentage
    """
    items = SAMPLE_QUEUE_ITEMS[:3]  # Export first 3 items
    
    for i, item in enumerate(items):
        # Simulate processing time
        import time
        time.sleep(0.5)
        
        progress = {
            "current_item": item["word"],
            "current_index": i,
            "total_items": len(items),
            "percentage": int((i + 1) / len(items) * 100),
            "status": "processing"
        }
        
        yield progress
    
    # Final completion
    yield {
        "current_item": None,
        "current_index": len(items),
        "total_items": len(items),
        "percentage": 100,
        "status": "completed"
    }