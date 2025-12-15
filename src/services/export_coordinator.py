# -*- coding: utf-8 -*-
"""
Export coordinator service - Bridge between export UI and Anki backend.

This module coordinates the export process by taking data from the export dialog
and orchestrating the creation of Anki cards through the legacy export service.
"""

from typing import Dict, Any, Optional, List, Callable
import logging

logger = logging.getLogger(__name__)


class ExportCoordinator:
    """
    Service for coordinating export operations.
    
    Bridges the export dialog UI with the Anki backend, handling
    data transformation, validation, and card creation.
    """
    
    def __init__(
        self,
        legacy_export_service: Any,
        search_service: Any,
        media_service: Any,
        config_manager: Any
    ):
        """
        Initialize export coordinator.
        
        Args:
            legacy_export_service: Legacy ExportService for Anki operations
            search_service: SearchService for definition lookup
            media_service: MediaService for media handling
            config_manager: Configuration manager
        """
        self.legacy_export_service = legacy_export_service
        self.search_service = search_service
        self.media_service = media_service
        self.config_manager = config_manager
    
    def export_word(
        self,
        export_data: Dict[str, Any],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Export a word to Anki using the provided export data.
        
        Args:
            export_data: Export data from ExportDialog:
                {
                    'word': str,
                    'example': str,
                    'deck': str,
                    'dictionaries': [str],
                    'template': str,
                    'template_fields': {field_name: source_or_custom},
                    'image': QPixmap or None,
                    'audio': str or None
                }
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with export result:
            {
                'success': bool,
                'note_id': int or None,
                'cards_created': int,
                'error': str or None,
                'word': str,
                'deck': str,
                'template': str
            }
        """
        if not export_data:
            return {
                'success': False,
                'note_id': None,
                'cards_created': 0,
                'error': 'Export data cannot be empty',
                'word': '',
                'deck': '',
                'template': ''
            }
        
        word = export_data.get('word', '').strip()
        deck = export_data.get('deck', '')
        template = export_data.get('template', '')
        
        if not word:
            return {
                'success': False,
                'note_id': None,
                'cards_created': 0,
                'error': 'Word cannot be empty',
                'word': word,
                'deck': deck,
                'template': template
            }
        
        if progress_callback:
            progress_callback(f"Preparing export for '{word}'...")
        
        try:
            # Step 1: Gather definitions from selected dictionaries
            definitions = self._gather_definitions(
                word,
                export_data.get('dictionaries', []),
                progress_callback
            )
            
            # Step 2: Prepare field values based on template mapping
            field_values = self._prepare_field_values(
                export_data,
                definitions,
                progress_callback
            )
            
            # Step 3: Handle media (image/audio)
            media_result = self._handle_media(
                export_data,
                progress_callback
            )
            
            # Step 4: Get deck ID
            deck_id = self._get_deck_id(deck)
            if deck_id is None:
                return {
                    'success': False,
                    'note_id': None,
                    'cards_created': 0,
                    'error': f"Deck '{deck}' not found",
                    'word': word,
                    'deck': deck,
                    'template': template
                }
            
            # Step 5: Create the Anki note
            if progress_callback:
                progress_callback(f"Creating Anki card for '{word}'...")
            
            success, error = self.legacy_export_service.create_note(
                note_type_name=template,
                field_values=field_values,
                tags="",  # TODO: Add tag support
                deck_id=deck_id
            )
            
            if success:
                logger.info(f"Successfully exported '{word}' to deck '{deck}'")
                if progress_callback:
                    progress_callback(f"Successfully exported '{word}'!")
                
                return {
                    'success': True,
                    'note_id': None,  # Legacy service doesn't return note ID
                    'cards_created': 1,
                    'error': None,
                    'word': word,
                    'deck': deck,
                    'template': template
                }
            else:
                logger.error(f"Failed to export '{word}': {error}")
                if progress_callback:
                    progress_callback(f"Export failed: {error}")
                
                return {
                    'success': False,
                    'note_id': None,
                    'cards_created': 0,
                    'error': error,
                    'word': word,
                    'deck': deck,
                    'template': template
                }
                
        except Exception as e:
            error_msg = f"Export error: {str(e)}"
            logger.error(f"Error exporting '{word}': {e}", exc_info=True)
            
            if progress_callback:
                progress_callback(f"Export error: {str(e)}")
            
            return {
                'success': False,
                'note_id': None,
                'cards_created': 0,
                'error': error_msg,
                'word': word,
                'deck': deck,
                'template': template
            }
    
    def _gather_definitions(
        self,
        word: str,
        dictionaries: List[str],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Gather definitions from selected dictionaries.
        
        Args:
            word: Word to look up
            dictionaries: List of dictionary names in priority order
            progress_callback: Optional progress callback
            
        Returns:
            List of definition dictionaries
        """
        if not dictionaries:
            return []
        
        if progress_callback:
            progress_callback(f"Looking up definitions for '{word}'...")
        
        try:
            # Create dictionary group for search
            dict_group = {
                'dictionaries': [{'dict': d, 'lang': ''} for d in dictionaries],
                'customFont': False,
                'font': None
            }
            
            # Perform search
            search_result = self.search_service.search(
                term=word,
                dictionary_group=dict_group
            )
            
            # Extract definitions
            definitions = []
            if search_result and 'results' in search_result:
                for dict_name, entries in search_result['results'].items():
                    for entry in entries:
                        definitions.append({
                            'dictionary': dict_name,
                            'word': entry.get('word', word),
                            'reading': entry.get('reading', ''),
                            'definitions': entry.get('definitions', []),
                            'examples': entry.get('examples', [])
                        })
            
            logger.debug(f"Gathered {len(definitions)} definitions for '{word}'")
            return definitions
            
        except Exception as e:
            logger.error(f"Error gathering definitions for '{word}': {e}", exc_info=True)
            return []
    
    def _prepare_field_values(
        self,
        export_data: Dict[str, Any],
        definitions: List[Dict[str, Any]],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, List[str]]:
        """
        Prepare field values based on template mapping.
        
        Args:
            export_data: Export data from dialog
            definitions: Gathered definitions
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary mapping field names to value lists
        """
        if progress_callback:
            progress_callback("Preparing card fields...")
        
        field_values = {}
        template_fields = export_data.get('template_fields', {})
        word = export_data.get('word', '')
        example = export_data.get('example', '')
        
        for field_name, source in template_fields.items():
            values = []
            
            if source.startswith('{mapped:'):
                # Extract mapped source
                mapped_source = source[8:-1]  # Remove {mapped: and }
                
                if mapped_source == 'word':
                    values.append(word)
                elif mapped_source == 'phonetic':
                    # Get reading from first definition
                    if definitions:
                        reading = definitions[0].get('reading', '')
                        if reading:
                            values.append(reading)
                elif mapped_source == 'definition':
                    # Combine definitions from all dictionaries
                    for defn_entry in definitions:
                        for defn in defn_entry.get('definitions', []):
                            if isinstance(defn, dict):
                                text = defn.get('text', '')
                            else:
                                text = str(defn)
                            if text:
                                values.append(text)
                elif mapped_source == 'example_sentence':
                    if example:
                        values.append(example)
                    # Also add examples from definitions
                    for defn_entry in definitions:
                        values.extend(defn_entry.get('examples', []))
                elif mapped_source == 'image':
                    # Handle image data
                    image_data = export_data.get('image')
                    if image_data:
                        # TODO: Convert QPixmap to file and add to media
                        values.append('[Image]')  # Placeholder
                elif mapped_source == 'audio':
                    # Handle audio data
                    audio_data = export_data.get('audio')
                    if audio_data:
                        values.append(f'[sound:{audio_data}]')
            else:
                # Custom text
                if source:
                    values.append(source)
            
            if values:
                field_values[field_name] = values
        
        logger.debug(f"Prepared {len(field_values)} field mappings")
        return field_values
    
    def _handle_media(
        self,
        export_data: Dict[str, Any],
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Handle media (image/audio) for the export.
        
        Args:
            export_data: Export data from dialog
            progress_callback: Optional progress callback
            
        Returns:
            Dictionary with media handling results
        """
        result = {
            'image_filename': None,
            'audio_filename': None,
            'errors': []
        }
        
        # Handle image
        image_data = export_data.get('image')
        if image_data:
            if progress_callback:
                progress_callback("Processing image...")
            
            try:
                # TODO: Convert QPixmap to file and add to Anki media
                # For now, just log that we have image data
                logger.debug("Image data present but not yet implemented")
                result['errors'].append("Image processing not yet implemented")
            except Exception as e:
                logger.error(f"Error processing image: {e}")
                result['errors'].append(f"Image error: {str(e)}")
        
        # Handle audio
        audio_data = export_data.get('audio')
        if audio_data:
            if progress_callback:
                progress_callback("Processing audio...")
            
            try:
                # Audio is already a filename in Anki media
                result['audio_filename'] = audio_data
                logger.debug(f"Audio filename: {audio_data}")
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
                result['errors'].append(f"Audio error: {str(e)}")
        
        return result
    
    def _get_deck_id(self, deck_name: str) -> Optional[int]:
        """
        Get deck ID by name.
        
        Args:
            deck_name: Name of the deck
            
        Returns:
            Deck ID or None if not found
        """
        try:
            decks = self.legacy_export_service.get_available_decks()
            return decks.get(deck_name)
        except Exception as e:
            logger.error(f"Error getting deck ID for '{deck_name}': {e}")
            return None
    
    def get_available_decks(self) -> Dict[str, Any]:
        """
        Get available Anki decks.
        
        Returns:
            Dictionary with deck information:
            {
                'success': bool,
                'decks': {deck_name: deck_id},
                'error': str or None
            }
        """
        try:
            decks = self.legacy_export_service.get_available_decks()
            return {
                'success': True,
                'decks': decks,
                'error': None
            }
        except Exception as e:
            error_msg = f"Error getting decks: {str(e)}"
            logger.error(f"Error getting available decks: {e}", exc_info=True)
            return {
                'success': False,
                'decks': {},
                'error': error_msg
            }
    
    def get_available_templates(self) -> Dict[str, Any]:
        """
        Get available note types/templates.
        
        Returns:
            Dictionary with template information:
            {
                'success': bool,
                'templates': [template_name],
                'error': str or None
            }
        """
        try:
            templates = self.legacy_export_service.get_note_types()
            return {
                'success': True,
                'templates': templates,
                'error': None
            }
        except Exception as e:
            error_msg = f"Error getting templates: {str(e)}"
            logger.error(f"Error getting available templates: {e}", exc_info=True)
            return {
                'success': False,
                'templates': [],
                'error': error_msg
            }
    
    def get_template_fields(self, template_name: str) -> Dict[str, Any]:
        """
        Get fields for a specific template.
        
        Args:
            template_name: Name of the note type/template
            
        Returns:
            Dictionary with field information:
            {
                'success': bool,
                'fields': [field_name],
                'error': str or None
            }
        """
        try:
            fields = self.legacy_export_service.get_fields_for_note_type(template_name)
            return {
                'success': True,
                'fields': fields,
                'error': None
            }
        except Exception as e:
            error_msg = f"Error getting fields for '{template_name}': {str(e)}"
            logger.error(f"Error getting template fields: {e}", exc_info=True)
            return {
                'success': False,
                'fields': [],
                'error': error_msg
            }