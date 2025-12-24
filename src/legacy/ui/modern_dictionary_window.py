# -*- coding: utf-8 -*-
"""
Modern Dictionary Window - Complete UI Redesign.

This is a complete redesign of the dictionary window using modern PyQt6 components.
It replaces the legacy HTML/JavaScript interface with native Qt widgets.
"""

from typing import Any, Optional, List, Dict
from pathlib import Path
import logging
import os

try:
    from aqt.qt import (
        QWidget, QVBoxLayout, QHBoxLayout, QShortcut, QKeySequence,
        QCloseEvent, QHideEvent
    )
    from aqt.utils import showInfo, tooltip
    from anki.utils import is_mac, is_win
    # Check if we're in a test environment
    ANKI_AVAILABLE = os.getenv('PYTEST_CURRENT_TEST') is None
except ImportError:
    # For testing without Anki
    ANKI_AVAILABLE = False
    QWidget = type('QWidget', (object,), {})
    QVBoxLayout = type('QVBoxLayout', (object,), {})
    QHBoxLayout = type('QHBoxLayout', (object,), {})
    QShortcut = type('QShortcut', (object,), {})
    QKeySequence = type('QKeySequence', (object,), {})
    QCloseEvent = type('QCloseEvent', (object,), {})
    QHideEvent = type('QHideEvent', (object,), {})
    showInfo = lambda *args, **kwargs: None
    tooltip = lambda *args, **kwargs: None
    is_mac = False
    is_win = False

from ..services import SearchService, ExportService, MediaService
from ..config import ConfigManager
from ..utils.logging_config import get_logger

logger = get_logger('ui.modern_dictionary_window')

# Import modern components
try:
    from .modern_components import (
        ModernSearchBar,
        DictionaryFilterBar,
        ModernResultsArea,
        DefinitionCard
    )
    MODERN_COMPONENTS_AVAILABLE = True
except ImportError:
    MODERN_COMPONENTS_AVAILABLE = False
    logger.warning("Modern components not available")


class ModernDictionaryWindow(QWidget):
    """
    Modern dictionary window with complete UI redesign.
    
    This window uses only modern PyQt6 components and follows the design
    specifications from the modern-ui-redesign spec. It does not use any
    legacy HTML/JavaScript code.
    
    Features:
    - Modern search bar with debounced input
    - Dictionary filter bar with mutual exclusion
    - Card-based results display
    - Signal-based component communication
    - Clean, testable architecture
    """
    
    def __init__(
        self,
        mw: Any,
        search_service: SearchService,
        export_service: ExportService,
        media_service: MediaService,
        config_manager: ConfigManager,
        addon_path: Path
    ):
        """
        Initialize modern dictionary window.
        
        Args:
            mw: Anki main window instance
            search_service: Service for dictionary searches
            export_service: Service for card exports
            media_service: Service for media downloads
            config_manager: Configuration manager
            addon_path: Path to addon directory
        """
        super().__init__()
        
        # Store dependencies
        self.mw = mw
        self.search_service = search_service
        self.export_service = export_service
        self.media_service = media_service
        self.config_manager = config_manager
        self.addon_path = addon_path
        
        # UI state
        self.current_editor: Optional[Any] = None
        self.current_reviewer: Optional[Any] = None
        
        # Initialize UI
        self._setup_ui()
        
        logger.info("Modern dictionary window initialized")
    
    def _setup_ui(self) -> None:
        """Set up the modern user interface."""
        # Check if we're in test environment
        is_test = os.getenv('PYTEST_CURRENT_TEST') is not None
        
        if not ANKI_AVAILABLE or is_test or not MODERN_COMPONENTS_AVAILABLE:
            # Skip UI setup in test environment or if components unavailable
            logger.info("Skipping UI setup (test mode or components unavailable)")
            return
        
        self.setWindowTitle("Anki Dictionary - Modern UI")
        self.setMinimumSize(400, 400)
        self.resize(900, 700)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add modern search bar
        self.search_bar = ModernSearchBar()
        self.search_bar.searchChanged.connect(self._on_search)
        main_layout.addWidget(self.search_bar)
        logger.info("Modern search bar added")
        
        # Add modern filter bar
        self.filter_bar = self._create_filter_bar()
        if self.filter_bar:
            main_layout.addWidget(self.filter_bar)
            logger.info("Modern filter bar added")
        
        # Add modern results area
        self.results_area = ModernResultsArea()
        main_layout.addWidget(self.results_area)
        logger.info("Modern results area added")
        
        self.setLayout(main_layout)
        
        # Set up hotkeys
        self._setup_hotkeys()
        
        # Restore window position
        self._restore_window_position()
        
        logger.info("Modern UI setup complete")
    
    def _create_filter_bar(self) -> Optional[DictionaryFilterBar]:
        """
        Create dictionary filter bar with available dictionaries.
        
        Returns:
            DictionaryFilterBar instance or None if creation fails
        """
        try:
            # Get dictionary groups from config
            groups = self.config_manager.get_dictionary_groups()
            
            # Build list of (name, id) tuples
            dictionaries = []
            
            # Add "All Dictionaries" option
            dictionaries.append(("All Dictionaries", "All"))
            
            # Add user-defined groups
            for group_name in sorted(groups.keys()):
                dictionaries.append((group_name, group_name))
            
            # Add special dictionaries
            dictionaries.append(("Google Images", "Google Images"))
            dictionaries.append(("Forvo", "Forvo"))
            
            # Create filter bar
            filter_bar = DictionaryFilterBar(dictionaries=dictionaries)
            filter_bar.filterChanged.connect(self._on_filter_changed)
            
            # Set initial selection
            current_group = self.config_manager.get_value('currentGroup', 'All')
            filter_bar.set_selected_filter(current_group)
            
            logger.info(f"Filter bar created with {len(dictionaries)} filters")
            return filter_bar
            
        except Exception as e:
            logger.error(f"Error creating filter bar: {e}", exc_info=True)
            return None
    
    def _setup_hotkeys(self) -> None:
        """Set up keyboard shortcuts."""
        # Escape to hide window
        esc_shortcut = QShortcut(QKeySequence("Esc"), self)
        esc_shortcut.activated.connect(self.hide)
        
        # Ctrl+W to toggle window
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        toggle_shortcut.activated.connect(self.toggle_visibility)
        
        logger.debug("Hotkeys configured")
    
    def _restore_window_position(self) -> None:
        """Restore window size and position from config."""
        size_pos = self.config_manager.get_value('modernDictSizePos')
        
        if size_pos and len(size_pos) == 4:
            try:
                x, y, width, height = size_pos
                self.resize(width, height)
                self.move(x, y)
                logger.debug(f"Window position restored: {size_pos}")
            except Exception as e:
                logger.warning(f"Error restoring window position: {e}")
    
    def _save_window_position(self) -> None:
        """Save window size and position to config."""
        pos = self.pos()
        size = self.size()
        size_pos = [pos.x(), pos.y(), size.width(), size.height()]
        
        try:
            self.config_manager.update_config('modernDictSizePos', size_pos)
            logger.debug(f"Window position saved: {size_pos}")
        except Exception as e:
            logger.warning(f"Error saving window position: {e}")
    
    def _on_search(self, query: str) -> None:
        """
        Handle search from search bar.
        
        Args:
            query: Search query (already debounced)
        """
        logger.info(f"Search triggered: {query}")
        
        if not query:
            self.results_area.clear_cards()
            return
        
        # Perform search
        self.perform_search(query)
    
    def _on_filter_changed(self, filter_id: str) -> None:
        """
        Handle filter change from filter bar.
        
        Args:
            filter_id: Selected dictionary/group ID
        """
        logger.info(f"Filter changed to: {filter_id}")
        
        # Save to config
        try:
            self.config_manager.update_config('currentGroup', filter_id)
        except Exception as e:
            logger.warning(f"Error saving current group: {e}")
        
        # Re-run search if there's a current query
        current_query = self.search_bar.text()
        if current_query:
            self.perform_search(current_query)
    
    def perform_search(self, term: str) -> None:
        """
        Perform a dictionary search.
        
        Args:
            term: Search term
        """
        if not term:
            return
        
        # Clean term
        term = self._clean_term(term)
        if not term:
            return
        
        # Get selected dictionary group
        dict_group = self._get_selected_dictionary_group()
        
        if not dict_group:
            self._show_error("No dictionary group selected")
            return
        
        # Get search settings
        search_mode = self.config_manager.get_value('searchMode', 'Forward')
        deinflect = self.config_manager.get_bool('deinflect', True)
        dict_limit = self.config_manager.get_int('dictSearch', 50)
        max_results = self.config_manager.get_int('maxSearch', 1000)
        
        try:
            # Perform search using service
            result = self.search_service.search(
                term=term,
                dictionary_group=dict_group,
                search_mode=search_mode,
                deinflect=deinflect,
                dict_limit=dict_limit,
                max_results=max_results
            )
            
            # Display results
            self._display_results(term, result)
            
            logger.info(f"Search completed for term: {term}")
            
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            self._show_error(f"Search failed: {str(e)}")
    
    def _display_results(self, term: str, result: Any) -> None:
        """
        Display search results as modern cards.
        
        Args:
            term: Search term
            result: Search result from service
        """
        # Clear existing cards
        self.results_area.clear_cards()
        
        if not result or not result.results or result.is_empty():
            # Show "no results" message
            logger.info(f"No results found for: {term}")
            self._show_no_results_card(term)
            return
        
        # Convert results to cards
        card_count = 0
        for dict_name, entries in result.results.items():
            if not entries:
                continue
            
            for entry in entries:
                # Convert entry to word data
                word_data = self._convert_entry_to_word_data(entry, dict_name)
                
                # Create definition card
                card = DefinitionCard(word_data)
                
                # Connect action signals
                card.audioRequested.connect(self._on_audio_requested)
                card.imageRequested.connect(self._on_image_requested)
                card.exportRequested.connect(self._on_export_requested)
                
                # Add card to results area
                self.results_area.add_card(card)
                card_count += 1
        
        logger.info(f"Displayed {card_count} cards from {len(result.results)} dictionaries")
    
    def _convert_entry_to_word_data(self, entry: Any, dict_name: str) -> Dict[str, Any]:
        """
        Convert database entry to word data for DefinitionCard.
        
        Args:
            entry: Database entry (DictionaryEntry object)
            dict_name: Dictionary name
            
        Returns:
            Dictionary with word data formatted for DefinitionCard
        """
        # Convert entry to dict if needed
        if hasattr(entry, 'to_dict'):
            entry_dict = entry.to_dict()
        elif isinstance(entry, dict):
            entry_dict = entry
        else:
            # Fallback: try to access attributes directly
            entry_dict = {
                'term': getattr(entry, 'term', ''),
                'pronunciation': getattr(entry, 'pronunciation', ''),
                'definition': getattr(entry, 'definition', ''),
                'pos': getattr(entry, 'pos', ''),
                'examples': getattr(entry, 'examples', ''),
                'starCount': getattr(entry, 'star_count', 'N/A'),
            }
        
        # Extract basic data
        word = entry_dict.get('term', '')
        phonetic = entry_dict.get('pronunciation', '')
        definition_text = entry_dict.get('definition', '')
        pos = entry_dict.get('pos', 'noun')
        examples_text = entry_dict.get('examples', '')
        
        # Parse definitions - split by newlines or <br> tags
        definitions = self._parse_definitions(definition_text, pos)
        
        # Parse examples - split by newlines
        examples = self._parse_examples(examples_text)
        
        # Build word data
        word_data = {
            'word': word,
            'phonetic': phonetic,
            'frequency': entry_dict.get('starCount', 'N/A'),
            'definitions': definitions,
            'examples': examples,
            'dictionary': dict_name
        }
        
        return word_data
    
    def _parse_definitions(self, definition_text: str, default_pos: str = 'noun') -> List[Dict[str, str]]:
        """
        Parse definition text into structured definitions.
        
        Args:
            definition_text: Raw definition text
            default_pos: Default part of speech
            
        Returns:
            List of definition dictionaries with 'type' and 'text'
        """
        if not definition_text:
            return []
        
        # Replace <br> tags with newlines
        definition_text = definition_text.replace('<br>', '\n').replace('<br/>', '\n')
        
        # Split by newlines
        lines = [line.strip() for line in definition_text.split('\n') if line.strip()]
        
        if not lines:
            return []
        
        definitions = []
        for line in lines:
            # Try to detect part of speech at start of line
            # Common patterns: "n.", "v.", "adj.", etc.
            pos = default_pos
            text = line
            
            # Simple POS detection
            if line.startswith('n.') or line.startswith('noun'):
                pos = 'noun'
                text = line[2:].strip() if line.startswith('n.') else line[4:].strip()
            elif line.startswith('v.') or line.startswith('verb'):
                pos = 'verb'
                text = line[2:].strip() if line.startswith('v.') else line[4:].strip()
            elif line.startswith('adj.') or line.startswith('adjective'):
                pos = 'adjective'
                text = line[4:].strip() if line.startswith('adj.') else line[9:].strip()
            elif line.startswith('adv.') or line.startswith('adverb'):
                pos = 'adverb'
                text = line[4:].strip() if line.startswith('adv.') else line[6:].strip()
            
            definitions.append({
                'type': pos,
                'text': text
            })
        
        return definitions
    
    def _parse_examples(self, examples_text: str) -> List[str]:
        """
        Parse examples text into list of example sentences.
        
        Args:
            examples_text: Raw examples text
            
        Returns:
            List of example sentences
        """
        if not examples_text:
            return []
        
        # Replace <br> tags with newlines
        examples_text = examples_text.replace('<br>', '\n').replace('<br/>', '\n')
        
        # Split by newlines and filter empty
        examples = [line.strip() for line in examples_text.split('\n') if line.strip()]
        
        return examples
    
    def _show_no_results_card(self, term: str) -> None:
        """
        Show a "no results" card when search returns nothing.
        
        Args:
            term: Search term that returned no results
        """
        # Create a special card for no results
        no_results_data = {
            'word': f'No results for "{term}"',
            'phonetic': '',
            'frequency': '',
            'definitions': [
                {
                    'type': 'info',
                    'text': 'Try searching for a different term or check your dictionary settings.'
                }
            ],
            'examples': [],
            'dictionary': 'System'
        }
        
        card = DefinitionCard(no_results_data)
        self.results_area.add_card(card)
    
    def _on_audio_requested(self, word: str) -> None:
        """
        Handle audio request from definition card.
        
        Downloads audio from Forvo and plays it in Anki.
        
        Args:
            word: Word to get audio for
        """
        logger.info(f"Audio requested for: {word}")
        
        if not word or not word.strip():
            tooltip("No word specified for audio")
            return
        
        # Show loading feedback
        tooltip(f"Downloading audio for '{word}'...")
        
        try:
            # Get language from config (default to Japanese for now)
            # TODO: Make language configurable or auto-detect
            language = self.config_manager.get_value('forvoLanguage', 'Japanese')
            username = self.config_manager.get_value('forvoUsername', None)
            
            # Download audio using media service
            success, filename, error = self.media_service.download_forvo_audio(
                term=word,
                language=language,
                username=username
            )
            
            if success and filename:
                # Play the audio file
                self._play_audio_file(filename)
                tooltip(f"Playing audio for '{word}'")
                logger.info(f"Audio downloaded and playing: {filename}")
            else:
                # Show error to user
                error_msg = error or "Failed to download audio"
                tooltip(f"Audio error: {error_msg}")
                logger.warning(f"Audio download failed for '{word}': {error_msg}")
        
        except Exception as e:
            logger.error(f"Error handling audio request: {e}", exc_info=True)
            tooltip(f"Audio error: {str(e)}")
    
    def _on_image_requested(self, word: str) -> None:
        """
        Handle image request from definition card.
        
        Downloads images from Google Images and displays them.
        
        Args:
            word: Word to get images for
        """
        logger.info(f"Images requested for: {word}")
        
        if not word or not word.strip():
            tooltip("No word specified for images")
            return
        
        # Show loading feedback
        tooltip(f"Searching images for '{word}'...")
        
        try:
            # Get max results from config
            max_results = self.config_manager.get_int('googleImagesMax', 5)
            
            # Download images using media service
            success, filenames, error = self.media_service.download_google_images(
                query=word,
                max_results=max_results
            )
            
            if success and filenames:
                # Show success message with count
                count = len(filenames)
                tooltip(f"Downloaded {count} image{'s' if count != 1 else ''} for '{word}'")
                logger.info(f"Downloaded {count} images: {filenames}")
                
                # TODO: Display images in a preview dialog or add to current card
                # For now, just show success message
            else:
                # Show error to user
                error_msg = error or "Failed to download images"
                tooltip(f"Image error: {error_msg}")
                logger.warning(f"Image download failed for '{word}': {error_msg}")
        
        except Exception as e:
            logger.error(f"Error handling image request: {e}", exc_info=True)
            tooltip(f"Image error: {str(e)}")
    
    def _on_export_requested(self, word: str) -> None:
        """
        Handle export request from definition card.
        
        Creates an Anki card with the word and its definitions.
        
        Args:
            word: Word to export
        """
        logger.info(f"Export requested for: {word}")
        
        if not word or not word.strip():
            tooltip("No word specified for export")
            return
        
        # Show loading feedback
        tooltip(f"Exporting '{word}'...")
        
        try:
            # Get export template from config
            templates = self.config_manager.get_value('exportTemplates', {})
            default_template_name = self.config_manager.get_value('defaultExportTemplate', None)
            
            if not templates:
                tooltip("No export templates configured. Please configure templates in settings.")
                logger.warning("Export failed: No templates configured")
                return
            
            # Get the default template or first available
            template = None
            if default_template_name and default_template_name in templates:
                template = templates[default_template_name]
            elif templates:
                # Use first available template
                template = list(templates.values())[0]
            
            if not template:
                tooltip("No valid export template found")
                logger.warning("Export failed: No valid template")
                return
            
            # Get note type from template
            note_type_name = template.get('noteType', 'Basic')
            
            # Search for the word to get definitions
            dict_group = self._get_selected_dictionary_group()
            if not dict_group:
                tooltip("No dictionary selected")
                return
            
            # Perform search to get definitions
            search_result = self.search_service.search(
                term=word,
                dictionary_group=dict_group,
                search_mode='Forward',
                deinflect=False,
                dict_limit=10,
                max_results=100
            )
            
            if not search_result or search_result.is_empty():
                tooltip(f"No definitions found for '{word}'")
                logger.warning(f"Export failed: No definitions for '{word}'")
                return
            
            # Prepare field values
            definitions_list = []
            for dict_name, entries in search_result.results.items():
                for entry in entries:
                    entry_dict = entry.to_dict() if hasattr(entry, 'to_dict') else entry
                    definitions_list.append((
                        dict_name,
                        entry_dict.get('definition', '')[:100],  # Short version
                        entry_dict.get('definition', '')  # Full version
                    ))
            
            # Prepare field values using export service
            field_values, tags, image_field, audio_field = self.export_service.prepare_field_values(
                template=template,
                word=word,
                definitions=definitions_list,
                tags=template.get('tags', '')
            )
            
            # Get deck ID from template
            deck_name = template.get('deck', 'Default')
            available_decks = self.export_service.get_available_decks()
            deck_id = available_decks.get(deck_name)
            
            # Create note
            success, error = self.export_service.create_note(
                note_type_name=note_type_name,
                field_values=field_values,
                tags=tags,
                deck_id=deck_id
            )
            
            if success:
                tooltip(f"Card created for '{word}'")
                logger.info(f"Successfully exported '{word}' to Anki")
            else:
                error_msg = error or "Failed to create card"
                tooltip(f"Export error: {error_msg}")
                logger.warning(f"Export failed for '{word}': {error_msg}")
        
        except Exception as e:
            logger.error(f"Error handling export request: {e}", exc_info=True)
            tooltip(f"Export error: {str(e)}")
    
    def _play_audio_file(self, filename: str) -> None:
        """
        Play an audio file using Anki's audio player.
        
        Args:
            filename: Name of audio file in media collection
        """
        try:
            # Use Anki's audio player
            from aqt.sound import av_player
            
            # Get full path to audio file
            media_path = self.media_service.get_media_path(filename)
            
            if not media_path.exists():
                logger.warning(f"Audio file not found: {media_path}")
                tooltip("Audio file not found")
                return
            
            # Play the audio
            av_player.play_file(str(media_path))
            logger.debug(f"Playing audio: {filename}")
        
        except ImportError:
            logger.warning("Anki audio player not available")
            tooltip("Audio playback not available")
        except Exception as e:
            logger.error(f"Error playing audio: {e}", exc_info=True)
            tooltip(f"Error playing audio: {str(e)}")
    
    def _get_selected_dictionary_group(self) -> Optional[Dict]:
        """
        Get the currently selected dictionary group.
        
        Returns:
            Dictionary group configuration or None
        """
        if not self.filter_bar:
            return None
        
        group_name = self.filter_bar.get_selected_filter()
        
        if not group_name:
            return None
        
        # Check user groups
        groups = self.config_manager.get_dictionary_groups()
        if group_name in groups:
            return groups[group_name]
        
        # Handle special groups
        if group_name == 'All':
            # Return all dictionaries
            all_dicts = self.search_service.repository.get_all_dictionaries()
            if not all_dicts:
                logger.warning("No dictionaries found in database")
                return None
            return {
                'dictionaries': [{'dict': d, 'lang': ''} for d in all_dicts],
                'customFont': False,
                'font': None
            }
        elif group_name == 'Google Images':
            return {
                'dictionaries': [{'dict': 'Google Images', 'lang': ''}],
                'customFont': False,
                'font': None
            }
        elif group_name == 'Forvo':
            return {
                'dictionaries': [{'dict': 'Forvo', 'lang': ''}],
                'customFont': False,
                'font': None
            }
        
        return None
    
    def _clean_term(self, term: str) -> str:
        """
        Clean a search term.
        
        Args:
            term: Raw search term
            
        Returns:
            Cleaned term
        """
        import re
        
        # Remove brackets and parentheses
        term = re.sub(
            r'(?:\[.*\])|(?:\(.*\))|(?:《.*》)|(?:（.*）)|\(|\)|\[|\]|《|》|（|）',
            '',
            term
        )
        
        # Limit length
        term = term[:30]
        
        return term.strip()
    
    def _show_error(self, message: str) -> None:
        """
        Show error message to user.
        
        Args:
            message: Error message
        """
        showInfo(message, parent=self, title="Dictionary Error")
    
    def show_window(self, terms: Optional[List[str]] = None) -> None:
        """
        Show window and optionally search for terms.
        
        Args:
            terms: Optional list of terms to search
        """
        self.show()
        self.raise_()
        self.activateWindow()
        
        if terms:
            for term in terms:
                self.perform_search(term)
        
        logger.info("Window shown")
    
    def toggle_visibility(self) -> None:
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show_window()
    
    def set_current_editor(self, editor: Any, target: str = '') -> None:
        """
        Set the current editor for field operations.
        
        Args:
            editor: Editor instance
            target: Target description
        """
        self.current_editor = editor
        self.current_reviewer = None
        logger.debug(f"Current editor set: {target}")
    
    def set_current_reviewer(self, reviewer: Any) -> None:
        """
        Set the current reviewer for field operations.
        
        Args:
            reviewer: Reviewer instance
        """
        self.current_reviewer = reviewer
        self.current_editor = None
        logger.debug("Current reviewer set")
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        self.hide()
        event.ignore()  # Don't actually close, just hide
    
    def hideEvent(self, event: QHideEvent) -> None:
        """
        Handle window hide event.
        
        Args:
            event: Hide event
        """
        self._save_window_position()
        event.accept()
        logger.info("Window hidden")
