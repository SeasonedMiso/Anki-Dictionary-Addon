# -*- coding: utf-8 -*-
"""
Result formatter service - Convert search results to UI-ready data structures.

This module handles formatting dictionary search results into data structures
that can be directly consumed by UI components.
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class ResultFormatter:
    """
    Service for formatting search results for UI consumption.
    
    Converts raw search results into structured WordData objects
    that UI components can display.
    """
    
    def format_search_results(
        self,
        search_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Format search results into UI-ready word data.
        
        Args:
            search_result: Result from SearchService.search()
            
        Returns:
            List of WordData dictionaries:
            [
                {
                    'word': str,
                    'phonetic': str,
                    'pitch_accent': str or None,
                    'source_dict': str,
                    'definitions': [
                        {
                            'type': str,
                            'text': str,
                            'examples': [str]
                        }
                    ],
                    'frequency': int or None,
                    'raw_entry': Any  # Original entry for reference
                }
            ]
        """
        word_data_list = []
        
        if not search_result or 'results' not in search_result:
            return word_data_list
        
        results = search_result.get('results', {})
        
        # Process each dictionary's results
        for dict_name, entries in results.items():
            for entry in entries:
                word_data = self._format_entry(entry, dict_name)
                word_data_list.append(word_data)
        
        logger.debug(f"Formatted {len(word_data_list)} word entries")
        return word_data_list
    
    def _format_entry(self, entry: Dict[str, Any], dict_name: str) -> Dict[str, Any]:
        """
        Format a single dictionary entry.
        
        Args:
            entry: Entry from search results
            dict_name: Name of source dictionary
            
        Returns:
            Formatted WordData dictionary
        """
        definitions = self._format_definitions(entry.get('definitions', []))
        
        return {
            'word': entry.get('word', ''),
            'phonetic': entry.get('reading', ''),
            'pitch_accent': entry.get('pitch_accent'),
            'source_dict': dict_name,
            'definitions': definitions,
            'frequency': entry.get('frequency'),
            'examples': entry.get('examples', []),
            'raw_entry': entry
        }
    
    def _format_definitions(self, definitions: List[Any]) -> List[Dict[str, Any]]:
        """
        Format definition list.
        
        Args:
            definitions: List of definitions from entry
            
        Returns:
            List of formatted definition dictionaries
        """
        formatted = []
        
        for defn in definitions:
            if isinstance(defn, dict):
                formatted.append({
                    'type': defn.get('type', ''),
                    'text': defn.get('text', ''),
                    'examples': defn.get('examples', [])
                })
            elif isinstance(defn, str):
                # Simple string definition
                formatted.append({
                    'type': '',
                    'text': defn,
                    'examples': []
                })
        
        return formatted
    
    def group_by_word(
        self,
        word_data_list: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group word data by word/term.
        
        Useful for combining results from multiple dictionaries
        for the same word.
        
        Args:
            word_data_list: List of formatted word data
            
        Returns:
            Dictionary mapping word to list of entries from different dicts
        """
        grouped = {}
        
        for word_data in word_data_list:
            word = word_data.get('word', '')
            if word not in grouped:
                grouped[word] = []
            grouped[word].append(word_data)
        
        return grouped
    
    def merge_definitions(
        self,
        word_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge multiple dictionary entries for the same word.
        
        Combines definitions from different dictionaries into a single
        entry, preserving source information.
        
        Args:
            word_entries: List of entries for the same word from different dicts
            
        Returns:
            Merged WordData dictionary with combined definitions
        """
        if not word_entries:
            return {}
        
        # Use first entry as base
        merged = word_entries[0].copy()
        merged['definitions'] = []
        merged['sources'] = []
        
        # Combine definitions from all entries
        for entry in word_entries:
            merged['definitions'].extend(entry.get('definitions', []))
            source = entry.get('source_dict', '')
            if source and source not in merged['sources']:
                merged['sources'].append(source)
        
        return merged
