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
    
    def filter_by_frequency(
        self,
        word_data_list: List[Dict[str, Any]],
        max_frequency: Optional[int] = None,
        min_frequency: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter word data by frequency range.
        
        Args:
            word_data_list: List of word data to filter
            max_frequency: Maximum frequency rank (lower = more common)
            min_frequency: Minimum frequency rank (higher = less common)
            
        Returns:
            Filtered list of word data
        """
        filtered = []
        
        for word_data in word_data_list:
            frequency = word_data.get('frequency')
            
            # Skip entries without frequency data
            if frequency is None:
                continue
            
            # Apply frequency filters
            if max_frequency is not None and frequency > max_frequency:
                continue
            if min_frequency is not None and frequency < min_frequency:
                continue
            
            filtered.append(word_data)
        
        return filtered
    
    def sort_by_relevance(
        self,
        word_data_list: List[Dict[str, Any]],
        search_term: str
    ) -> List[Dict[str, Any]]:
        """
        Sort word data by relevance to search term.
        
        Args:
            word_data_list: List of word data to sort
            search_term: Original search term
            
        Returns:
            Sorted list with most relevant entries first
        """
        def relevance_score(word_data: Dict[str, Any]) -> int:
            score = 0
            word = word_data.get('word', '').lower()
            search_lower = search_term.lower()
            
            # Exact match gets highest score
            if word == search_lower:
                score += 1000
            
            # Starts with search term
            elif word.startswith(search_lower):
                score += 500
            
            # Contains search term
            elif search_lower in word:
                score += 250
            
            # Frequency bonus (lower frequency rank = higher score)
            frequency = word_data.get('frequency')
            if frequency:
                # Invert frequency so lower rank = higher score
                score += max(0, 10000 - frequency) // 100
            
            # Dictionary priority (some dictionaries are more authoritative)
            source_dict = word_data.get('source_dict', '').lower()
            if 'jmdict' in source_dict or 'edict' in source_dict:
                score += 100
            elif 'daijirin' in source_dict or 'daijisen' in source_dict:
                score += 80
            
            return score
        
        return sorted(word_data_list, key=relevance_score, reverse=True)
    
    def extract_examples(
        self,
        word_data_list: List[Dict[str, Any]],
        max_examples: int = 3
    ) -> List[str]:
        """
        Extract example sentences from word data.
        
        Args:
            word_data_list: List of word data
            max_examples: Maximum number of examples to return
            
        Returns:
            List of example sentences
        """
        examples = []
        
        for word_data in word_data_list:
            # Get examples from word data
            word_examples = word_data.get('examples', [])
            examples.extend(word_examples)
            
            # Get examples from definitions
            definitions = word_data.get('definitions', [])
            for definition in definitions:
                def_examples = definition.get('examples', [])
                examples.extend(def_examples)
            
            # Stop if we have enough examples
            if len(examples) >= max_examples:
                break
        
        # Remove duplicates while preserving order
        unique_examples = []
        seen = set()
        for example in examples:
            if example not in seen:
                unique_examples.append(example)
                seen.add(example)
                if len(unique_examples) >= max_examples:
                    break
        
        return unique_examples
    
    def get_summary_stats(
        self,
        word_data_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get summary statistics for word data list.
        
        Args:
            word_data_list: List of word data
            
        Returns:
            Dictionary with summary statistics
        """
        if not word_data_list:
            return {
                'total_entries': 0,
                'unique_words': 0,
                'dictionaries': [],
                'has_frequency': 0,
                'has_pitch_accent': 0,
                'avg_definitions': 0
            }
        
        unique_words = set()
        dictionaries = set()
        frequency_count = 0
        pitch_accent_count = 0
        total_definitions = 0
        
        for word_data in word_data_list:
            word = word_data.get('word', '')
            if word:
                unique_words.add(word)
            
            source_dict = word_data.get('source_dict', '')
            if source_dict:
                dictionaries.add(source_dict)
            
            if word_data.get('frequency') is not None:
                frequency_count += 1
            
            if word_data.get('pitch_accent'):
                pitch_accent_count += 1
            
            definitions = word_data.get('definitions', [])
            total_definitions += len(definitions)
        
        return {
            'total_entries': len(word_data_list),
            'unique_words': len(unique_words),
            'dictionaries': sorted(list(dictionaries)),
            'has_frequency': frequency_count,
            'has_pitch_accent': pitch_accent_count,
            'avg_definitions': total_definitions / len(word_data_list) if word_data_list else 0
        }
