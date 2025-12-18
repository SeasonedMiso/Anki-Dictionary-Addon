# -*- coding: utf-8 -*-
"""
Search Integration - Connects ModernSearchBar to DictionaryService.

This module bridges the UI search bar with the backend dictionary service,
handling word lookups and result display with proper error handling and
user feedback.
"""

from typing import Optional, Dict, Any, List
import logging

try:
    from aqt.qt import QObject, pyqtSignal
except ImportError:
    # Fallback for testing
    class QObject:
        pass
    
    class pyqtSignal:
        def __init__(self, *args):
            pass
        def emit(self, *args):
            pass
        def connect(self, func):
            pass

from ..services.dictionary_service import DictionaryService
from ..services.result_formatter import ResultFormatter
from .dictionary_widgets import ModernSearchBar, ModernResultsArea, WordSection

logger = logging.getLogger(__name__)


class SearchController(QObject):
    """
    Controller for search operations.
    
    Coordinates between ModernSearchBar UI and DictionaryService backend,
    handling lookups, formatting results, and displaying them in ModernResultsArea.
    """
    
    # Signals
    searchStarted = pyqtSignal()
    searchCompleted = pyqtSignal(dict)  # Emits lookup result
    searchError = pyqtSignal(str)  # Emits error message
    
    def __init__(
        self,
        search_bar: ModernSearchBar,
        results_area: ModernResultsArea,
        dictionary_service: DictionaryService,
        result_formatter: Optional[ResultFormatter] = None
    ):
        """
        Initialize search controller.
        
        Args:
            search_bar: ModernSearchBar widget
            results_area: ModernResultsArea widget
            dictionary_service: DictionaryService for lookups
            result_formatter: ResultFormatter for formatting results (optional)
        """
        super().__init__()
        
        self.search_bar = search_bar
        self.results_area = results_area
        self.dictionary_service = dictionary_service
        self.result_formatter = result_formatter or ResultFormatter()
        
        # Connect search bar signals
        self.search_bar.searchChanged.connect(self._on_search_changed)
        self.search_bar.searchRequested.connect(self._on_search_requested)
        
        logger.info("SearchController initialized")
    
    def _on_search_changed(self, text: str) -> None:
        """
        Handle debounced search text changes.
        
        Args:
            text: Search text
        """
        if not text or len(text) < 1:
            self.results_area.clear_cards()
            return
        
        self._perform_search(text)
    
    def _on_search_requested(self, text: str) -> None:
        """
        Handle explicit search request (Enter or button click).
        
        Args:
            text: Search text
        """
        if not text or len(text) < 1:
            return
        
        self._perform_search(text)
    
    def _perform_search(self, word: str) -> None:
        """
        Perform word lookup and display results.
        
        Args:
            word: Word to search for
        """
        try:
            self.searchStarted.emit()
            
            # Perform lookup
            result = self.dictionary_service.lookup_word(word)
            
            if result.get('error'):
                self.searchError.emit(result['error'])
                self.results_area.clear_cards()
                return
            
            # Format and display results
            entries = result.get('entries', [])
            
            if not entries:
                self.searchError.emit(f"No results found for '{word}'")
                self.results_area.clear_cards()
                return
            
            # Clear previous results
            self.results_area.clear_cards()
            
            # Add word section for each unique word
            word_sections = {}
            for entry in entries:
                entry_word = entry.word
                if entry_word not in word_sections:
                    word_data = {
                        'word': entry_word,
                        'phonetic': entry.reading or '',
                        'pitch_accent': entry.pitch_accent or '',
                        'frequencies': {}
                    }
                    word_section = WordSection(word_data)
                    word_sections[entry_word] = word_section
                    self.results_area.add_card(word_section)
                
                # Add dictionary section to word
                word_section = word_sections[entry_word]
                definitions = [
                    {'type': 'definition', 'text': d}
                    for d in entry.definitions
                ]
                examples = entry.examples or []
                
                word_section.add_dictionary_section(
                    entry.source_dict,
                    definitions,
                    examples,
                    is_primary=(entry.source_dict == 'JMdict')
                )
            
            self.searchCompleted.emit(result)
            logger.info(f"Search completed for '{word}': {len(entries)} entries")
            
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.searchError.emit(error_msg)
            self.results_area.clear_cards()
    
    def clear_results(self) -> None:
        """Clear all search results."""
        self.results_area.clear_cards()
        self.search_bar.clear()
