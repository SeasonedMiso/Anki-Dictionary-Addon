# -*- coding: utf-8 -*-
"""
Export service for creating Anki cards.
"""

from typing import Dict, List, Optional, Any, Tuple
import re
from pathlib import Path

from ..constants import (
    FIELD_EXPORT_DONT_EXPORT,
    FIELD_EXPORT_ADD,
    FIELD_EXPORT_OVERWRITE,
    FIELD_EXPORT_IF_EMPTY,
    DEFAULT_SEPARATOR
)


class ExportService:
    """Service for exporting dictionary data to Anki cards."""
    
    def __init__(self, mw: Any):
        """
        Initialize export service.
        
        Args:
            mw: Anki main window instance
        """
        self.mw = mw
    
    def create_note(
        self,
        note_type_name: str,
        field_values: Dict[str, List[str]],
        tags: str = "",
        deck_id: Optional[int] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Create a new Anki note.
        
        Args:
            note_type_name: Name of the note type
            field_values: Dictionary mapping field names to values
            tags: Space-separated tags
            deck_id: Target deck ID
            
        Returns:
            Tuple of (success, error_message)
        """
        from anki.notes import Note
        
        # Get note type
        model = self.mw.col.models.byName(note_type_name)
        if not model:
            return False, f"Note type '{note_type_name}' not found"
        
        # Create note
        note = Note(self.mw.col, model)
        model_fields = self.mw.col.models.field_names(note.model())
        
        # Set field values
        for field_name, values in field_values.items():
            if field_name in model_fields and values:
                note[field_name] = DEFAULT_SEPARATOR.join(values)
        
        # Set tags
        if tags:
            note.set_tags_from_str(tags)
        
        # Set deck
        if deck_id:
            note.note_type()['did'] = int(deck_id)
        
        # Validate note
        ret = note.dupeOrEmpty()
        if ret == 1:
            return False, "Note's sorting field is empty"
        
        # Check for cloze
        if '{{cloze:' in note.note_type()['tmpls'][0]['qfmt']:
            if not self.mw.col.models._availClozeOrds(
                note.model(), note.joinedFields(), False
            ):
                return False, "Cloze note type but no cloze deletions found"
        
        # Add note
        cards = self.mw.col.addNote(note)
        if not cards:
            return False, "Note would create blank card"
        
        self.mw.reset()
        return True, None
    
    def prepare_field_values(
        self,
        template: Dict[str, Any],
        sentence: str = "",
        secondary: str = "",
        word: str = "",
        notes: str = "",
        definitions: List[Tuple[str, str, str]] = None,
        image_tag: str = "",
        audio_tag: str = "",
        tags: str = ""
    ) -> Tuple[Dict[str, List[str]], str, Optional[str], Optional[str]]:
        """
        Prepare field values according to template.
        
        Args:
            template: Export template configuration
            sentence: Sentence text
            secondary: Secondary text (e.g., translation)
            word: Target word
            notes: User notes
            definitions: List of (dict_name, short_def, full_def) tuples
            image_tag: Image HTML tag
            audio_tag: Audio tag
            tags: Tags string
            
        Returns:
            Tuple of (field_values, tags, image_field, audio_field)
        """
        if definitions is None:
            definitions = []
        
        fields = {}
        image_field = None
        audio_field = None
        
        # Sentence
        if sentence and self._is_valid_field(template.get('sentence')):
            field_name = template['sentence']
            if field_name != FIELD_EXPORT_DONT_EXPORT:
                fields[field_name] = [sentence]
        
        # Secondary
        if secondary and self._is_valid_field(template.get('secondary')):
            field_name = template['secondary']
            if field_name != FIELD_EXPORT_DONT_EXPORT:
                fields[field_name] = [secondary]
        
        # Word
        if word and self._is_valid_field(template.get('word')):
            field_name = template['word']
            if field_name != FIELD_EXPORT_DONT_EXPORT:
                if field_name not in fields:
                    fields[field_name] = []
                fields[field_name].append(word)
        
        # Notes
        if notes and self._is_valid_field(template.get('notes')):
            field_name = template['notes']
            if field_name != FIELD_EXPORT_DONT_EXPORT:
                fields[field_name] = [notes]
        
        # Image
        if image_tag and self._is_valid_field(template.get('image')):
            field_name = template['image']
            if field_name != FIELD_EXPORT_DONT_EXPORT:
                image_field = field_name
                if field_name not in fields:
                    fields[field_name] = []
                fields[field_name].append(image_tag)
        
        # Audio
        if audio_tag and self._is_valid_field(template.get('audio')):
            field_name = template['audio']
            if field_name != FIELD_EXPORT_DONT_EXPORT:
                audio_field = field_name
                if field_name not in fields:
                    fields[field_name] = []
                fields[field_name].append(audio_tag)
        
        # Definitions - specific fields
        specific = template.get('specific', {})
        for field_name, dict_names in specific.items():
            for dict_name in dict_names:
                matching_defs = [
                    d[2] for d in definitions if d[0] == dict_name
                ]
                if matching_defs:
                    if field_name not in fields:
                        fields[field_name] = []
                    fields[field_name].extend(matching_defs)
                    # Remove from definitions list
                    definitions = [
                        d for d in definitions if d[0] != dict_name
                    ]
        
        # Definitions - unspecified field
        unspecified = template.get('unspecified')
        if unspecified and unspecified != FIELD_EXPORT_DONT_EXPORT:
            remaining_defs = [d[2] for d in definitions]
            if remaining_defs:
                if unspecified not in fields:
                    fields[unspecified] = []
                fields[unspecified].extend(remaining_defs)
        
        return fields, tags, image_field, audio_field
    
    def add_definitions_to_note(
        self,
        note: Any,
        term: str,
        dictionary_configs: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> Any:
        """
        Automatically add definitions to a note.
        
        Args:
            note: Anki note object
            term: Term to look up
            dictionary_configs: List of dictionary configurations
            config: Addon configuration
            
        Returns:
            Modified note
        """
        # Clean term
        term = self._clean_term(term)
        if not term:
            return note
        
        fields = self.mw.col.models.field_names(note.note_type())
        
        for dict_config in dictionary_configs:
            table_name = dict_config['tableName']
            target_field = dict_config['field']
            
            if target_field not in fields:
                continue
            
            # Get definitions (this would use the search service)
            # For now, this is a placeholder
            definitions = self._get_definitions_for_term(
                term, table_name, dict_config
            )
            
            if definitions:
                self._add_to_field(
                    note,
                    target_field,
                    definitions,
                    dict_config.get('addType', FIELD_EXPORT_ADD)
                )
        
        return note
    
    def _get_definitions_for_term(
        self,
        term: str,
        table_name: str,
        config: Dict[str, Any]
    ) -> str:
        """Get formatted definitions for a term."""
        # This would use the search service
        # Placeholder for now
        return ""
    
    def _add_to_field(
        self,
        note: Any,
        field_name: str,
        content: str,
        add_type: str
    ) -> None:
        """
        Add content to a note field.
        
        Args:
            note: Anki note
            field_name: Field to add to
            content: Content to add
            add_type: How to add (add, overwrite, if_empty)
        """
        current = note[field_name]
        
        if add_type == FIELD_EXPORT_OVERWRITE:
            note[field_name] = content
        elif add_type == FIELD_EXPORT_ADD:
            if current and current != '<br>':
                note[field_name] = current + DEFAULT_SEPARATOR + content
            else:
                note[field_name] = content
        elif add_type == FIELD_EXPORT_IF_EMPTY:
            if not current or current == '<br>':
                note[field_name] = content
    
    @staticmethod
    def _is_valid_field(field_name: Optional[str]) -> bool:
        """Check if field name is valid for export."""
        return (
            field_name is not None and
            field_name != FIELD_EXPORT_DONT_EXPORT and
            field_name.strip() != ""
        )
    
    @staticmethod
    def _clean_term(term: str) -> str:
        """Clean a term for lookup."""
        # Remove HTML tags
        term = re.sub(r'<[^>]+>', '', term)
        # Remove brackets
        term = re.sub(r'\[[^\]]+?\]', '', term)
        return term.strip()
    
    def get_available_decks(self) -> Dict[str, int]:
        """
        Get available decks.
        
        Returns:
            Dictionary mapping deck names to IDs
        """
        decks_raw = self.mw.col.decks.decks
        decks = {}
        
        for did, deck in decks_raw.items():
            if not deck.get('dyn', False):
                decks[deck['name']] = did
        
        return decks
    
    def get_note_types(self) -> List[str]:
        """
        Get available note types.
        
        Returns:
            List of note type names
        """
        return [m['name'] for m in self.mw.col.models.all()]
    
    def get_fields_for_note_type(self, note_type_name: str) -> List[str]:
        """
        Get fields for a note type.
        
        Args:
            note_type_name: Note type name
            
        Returns:
            List of field names
        """
        model = self.mw.col.models.byName(note_type_name)
        if not model:
            return []
        
        return self.mw.col.models.field_names(model)
