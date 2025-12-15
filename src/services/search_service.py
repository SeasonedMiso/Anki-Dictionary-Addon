# -*- coding: utf-8 -*-
"""
Search service - Clean business logic for dictionary searches.

This module provides search functionality without UI dependencies,
returning structured data that can be used by any UI component.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class SearchService:
    """
    Service for performing dictionary searches.
    
    Provides clean search interface without UI dependencies.
    Returns structured data for consumption by UI components.
    """
    
    def __init__(self, legacy_search_service: Any, config_manager: Any):
        """
        Initialize search service.
        
        Args:
            legacy_search_service: Legacy SearchService instance for actual search
            config_manager: Configuration manager for search settings
        """
        self.legacy_service = legacy_search_service
        self.config_manager = config_manager
    
    def search(
        self,
        term: str,
        dictionary_group: Dict[str, Any],
        search_mode: Optional[str] = None,
        deinflect: Optional[bool] = None,
        dict_limit: Optional[int] = None,
        max_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Perform a dictionary search.
        
        Args:
            term: Search term
            dictionary_group: Dictionary group configuration
            search_mode: Search mode (Forward, Exact, etc.) - uses config if None
            deinflect: Whether to apply deinflection - uses config if None
            dict_limit: Max results per dictionary - uses config if None
            max_results: Max total results - uses config if None
            
        Returns:
            Dictionary with search results in structured format:
            {
                'term': str,
                'results': {
                    'dict_name': [
                        {
                            'word': str,
                            'reading': str,
                            'definitions': [str],
                            'examples': [str],
                            'frequency': int or None,
                            'pitch_accent': str or None
                        }
                    ]
                },
                'total_count': int,
                'search_time_ms': float
            }
        """
        if not term or not term.strip():
            return {
                'term': term,
                'results': {},
                'total_count': 0,
                'search_time_ms': 0
            }
        
        term = term.strip()
        
        # Use provided settings or fall back to config
        if search_mode is None:
            search_mode = self.config_manager.get_value('searchMode', 'Forward')
        if deinflect is None:
            deinflect = self.config_manager.get_bool('deinflect', True)
        if dict_limit is None:
            dict_limit = self.config_manager.get_int('dictSearch', 50)
        if max_results is None:
            max_results = self.config_manager.get_int('maxSearch', 1000)
        
        try:
            # Perform search using legacy service
            result = self.legacy_service.search(
                term=term,
                dictionary_group=dictionary_group,
                search_mode=search_mode,
                deinflect=deinflect,
                dict_limit=dict_limit,
                max_results=max_results
            )
            
            # Convert legacy result to structured format
            structured_result = self._convert_result(term, result)
            
            logger.debug(f"Search completed for '{term}': {structured_result['total_count']} results")
            return structured_result
            
        except Exception as e:
            logger.error(f"Search error for '{term}': {e}", exc_info=True)
            return {
                'term': term,
                'results': {},
                'total_count': 0,
                'search_time_ms': 0,
                'error': str(e)
            }
    
    def _convert_result(self, term: str, legacy_result: Any) -> Dict[str, Any]:
        """
        Convert legacy search result to structured format.
        
        Args:
            term: Original search term
            legacy_result: Result from legacy SearchService
            
        Returns:
            Structured result dictionary
        """
        # Extract results from legacy format
        results = {}
        total_count = 0
        
        if hasattr(legacy_result, 'results'):
            for dict_name, entries in legacy_result.results.items():
                results[dict_name] = []
                for entry in entries:
                    word_data = self._convert_entry(entry)
                    results[dict_name].append(word_data)
                    total_count += 1
        
        return {
            'term': term,
            'results': results,
            'total_count': total_count,
            'search_time_ms': getattr(legacy_result, 'search_time_ms', 0)
        }
    
    def _convert_entry(self, entry: Any) -> Dict[str, Any]:
        """
        Convert a single dictionary entry to structured format.
        
        Args:
            entry: Dictionary entry from legacy service
            
        Returns:
            Structured entry dictionary
        """
        return {
            'word': getattr(entry, 'word', ''),
            'reading': getattr(entry, 'reading', ''),
            'definitions': getattr(entry, 'definitions', []),
            'examples': getattr(entry, 'examples', []),
            'frequency': getattr(entry, 'frequency', None),
            'pitch_accent': getattr(entry, 'pitch_accent', None),
            'source_dict': getattr(entry, 'source_dict', '')
        }
    
    def search_multiple_terms(
        self,
        terms: List[str],
        dictionary_group: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Search for multiple terms.
        
        Args:
            terms: List of search terms
            dictionary_group: Dictionary group configuration
            **kwargs: Additional search parameters
            
        Returns:
            Dictionary mapping each term to its search results
        """
        results = {}
        for term in terms:
            results[term] = self.search(term, dictionary_group, **kwargs)
        return results
