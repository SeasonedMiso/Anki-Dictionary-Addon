# -*- coding: utf-8 -*-
"""
Dictionary Service - Core word lookup functionality with legacy integration.

This module provides dictionary lookup operations, handling word searches,
conjugation/deinflection, and multiple dictionary sources. It bridges the
modern UI with legacy dictionary functionality.
"""

from typing import Dict, Any, Optional, List, Tuple
import logging
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WordEntry:
    """Represents a single word entry from a dictionary."""
    word: str
    reading: Optional[str] = None
    pitch_accent: Optional[str] = None
    definitions: List[str] = None
    examples: List[str] = None
    frequency: Optional[int] = None
    source_dict: str = ""
    
    def __post_init__(self):
        if self.definitions is None:
            self.definitions = []
        if self.examples is None:
            self.examples = []


class DictionaryService:
    """
    Service for dictionary operations.
    
    Provides clean dictionary interface without UI dependencies.
    Handles word lookups, conjugation, and multiple dictionary sources.
    """
    
    def __init__(self, legacy_search_service: Any, config_manager: Any):
        """
        Initialize dictionary service.
        
        Args:
            legacy_search_service: Legacy SearchService instance
            config_manager: Configuration manager for dictionary settings
        """
        self.legacy_service = legacy_search_service
        self.config_manager = config_manager
        self._search_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_max_size = 100
    
    def lookup_word(
        self,
        word: str,
        dictionary_group: Optional[Dict[str, Any]] = None,
        search_mode: Optional[str] = None,
        deinflect: Optional[bool] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Look up a word in the dictionary.
        
        Args:
            word: Word to look up
            dictionary_group: Dictionary group configuration
            search_mode: Search mode (Forward, Exact, etc.)
            deinflect: Whether to apply deinflection
            use_cache: Whether to use cached results
            
        Returns:
            Dictionary with lookup results:
            {
                'word': str,
                'entries': [WordEntry],
                'total_count': int,
                'search_time_ms': float,
                'error': str or None
            }
        """
        if not word or not word.strip():
            return {
                'word': word,
                'entries': [],
                'total_count': 0,
                'search_time_ms': 0,
                'error': None
            }
        
        word = word.strip()
        
        # Check cache
        cache_key = f"{word}:{search_mode}:{deinflect}"
        if use_cache and cache_key in self._search_cache:
            logger.debug(f"Cache hit for '{word}'")
            return self._search_cache[cache_key]
        
        # Use config defaults if not provided
        if search_mode is None:
            search_mode = self.config_manager.get_value('searchMode', 'Forward')
        if deinflect is None:
            deinflect = self.config_manager.get_bool('deinflect', True)
        
        start_time = time.time()
        
        try:
            # Perform lookup using legacy service
            result = self.legacy_service.search(
                term=word,
                dictionary_group=dictionary_group or {},
                search_mode=search_mode,
                deinflect=deinflect,
                dict_limit=self.config_manager.get_int('dictSearch', 50),
                max_results=self.config_manager.get_int('maxSearch', 1000)
            )
            
            # Convert to structured format
            entries = self._convert_result(result)
            search_time = (time.time() - start_time) * 1000
            
            response = {
                'word': word,
                'entries': entries,
                'total_count': len(entries),
                'search_time_ms': search_time,
                'error': None
            }
            
            # Cache result
            if use_cache:
                self._manage_cache(cache_key, response)
            
            logger.debug(f"Lookup completed for '{word}': {len(entries)} entries in {search_time:.1f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Lookup error for '{word}': {e}", exc_info=True)
            return {
                'word': word,
                'entries': [],
                'total_count': 0,
                'search_time_ms': (time.time() - start_time) * 1000,
                'error': str(e)
            }
    
    def lookup_multiple(
        self,
        words: List[str],
        dictionary_group: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Look up multiple words.
        
        Args:
            words: List of words to look up
            dictionary_group: Dictionary group configuration
            **kwargs: Additional lookup parameters
            
        Returns:
            Dictionary mapping each word to its lookup results
        """
        results = {}
        for word in words:
            results[word] = self.lookup_word(word, dictionary_group, **kwargs)
        return results
    
    def get_conjugations(
        self,
        word: str,
        part_of_speech: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get conjugations for a word.
        
        Args:
            word: Word to conjugate
            part_of_speech: Part of speech (verb, adjective, etc.)
            
        Returns:
            Dictionary with conjugation information:
            {
                'word': str,
                'conjugations': [
                    {
                        'form': str,
                        'type': str,
                        'reading': str
                    }
                ],
                'error': str or None
            }
        """
        try:
            if hasattr(self.legacy_service, 'get_conjugations'):
                conjugations = self.legacy_service.get_conjugations(word, part_of_speech)
                return {
                    'word': word,
                    'conjugations': conjugations or [],
                    'error': None
                }
            else:
                return {
                    'word': word,
                    'conjugations': [],
                    'error': 'Conjugation service not available'
                }
        except Exception as e:
            logger.error(f"Error getting conjugations for '{word}': {e}")
            return {
                'word': word,
                'conjugations': [],
                'error': str(e)
            }
    
    def get_frequency_info(
        self,
        word: str
    ) -> Dict[str, Any]:
        """
        Get frequency information for a word.
        
        Args:
            word: Word to get frequency for
            
        Returns:
            Dictionary with frequency information:
            {
                'word': str,
                'frequency': int or None,
                'frequency_rank': int or None,
                'frequency_category': str or None,
                'error': str or None
            }
        """
        try:
            if hasattr(self.legacy_service, 'get_frequency'):
                freq_data = self.legacy_service.get_frequency(word)
                return {
                    'word': word,
                    'frequency': freq_data.get('frequency') if freq_data else None,
                    'frequency_rank': freq_data.get('rank') if freq_data else None,
                    'frequency_category': freq_data.get('category') if freq_data else None,
                    'error': None
                }
            else:
                return {
                    'word': word,
                    'frequency': None,
                    'frequency_rank': None,
                    'frequency_category': None,
                    'error': None
                }
        except Exception as e:
            logger.error(f"Error getting frequency for '{word}': {e}")
            return {
                'word': word,
                'frequency': None,
                'frequency_rank': None,
                'frequency_category': None,
                'error': str(e)
            }
    
    def clear_cache(self) -> None:
        """Clear the search cache."""
        self._search_cache.clear()
        logger.debug("Dictionary cache cleared")
    
    def _convert_result(self, legacy_result: Any) -> List[WordEntry]:
        """
        Convert legacy search result to WordEntry list.
        
        Args:
            legacy_result: Result from legacy SearchService
            
        Returns:
            List of WordEntry objects
        """
        entries = []
        
        try:
            if hasattr(legacy_result, 'results'):
                for dict_name, dict_entries in legacy_result.results.items():
                    for entry in dict_entries:
                        word_entry = WordEntry(
                            word=getattr(entry, 'word', ''),
                            reading=getattr(entry, 'reading', None),
                            pitch_accent=getattr(entry, 'pitch_accent', None),
                            definitions=getattr(entry, 'definitions', []),
                            examples=getattr(entry, 'examples', []),
                            frequency=getattr(entry, 'frequency', None),
                            source_dict=dict_name
                        )
                        entries.append(word_entry)
        except Exception as e:
            logger.error(f"Error converting result: {e}")
        
        return entries
    
    def _manage_cache(self, key: str, value: Dict[str, Any]) -> None:
        """
        Manage cache size by removing oldest entries if needed.
        
        Args:
            key: Cache key
            value: Cache value
        """
        if len(self._search_cache) >= self._cache_max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self._search_cache))
            del self._search_cache[oldest_key]
        
        self._search_cache[key] = value
