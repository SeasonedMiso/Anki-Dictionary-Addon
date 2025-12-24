# -*- coding: utf-8 -*-
"""
Search service for dictionary lookups.
"""

from typing import List, Dict, Optional
import json
import os
from pathlib import Path

from ..database import DictionaryRepository, SearchResult
from ..constants import (
    SEARCH_MODE_FORWARD,
    SEARCH_MODE_EXACT,
    DEFAULT_MAX_SEARCH,
    DEFAULT_DICT_SEARCH
)


class SearchService:
    """Service for performing dictionary searches."""
    
    def __init__(
        self,
        repository: DictionaryRepository,
        addon_path: Path
    ):
        """
        Initialize search service.
        
        Args:
            repository: Dictionary repository instance
            addon_path: Path to addon directory
        """
        self.repository = repository
        self.addon_path = addon_path
        self.conjugations = self._load_conjugations()
    
    def search(
        self,
        term: str,
        dictionary_group: Dict[str, any],
        search_mode: str = SEARCH_MODE_FORWARD,
        deinflect: bool = True,
        dict_limit: int = DEFAULT_DICT_SEARCH,
        max_results: int = DEFAULT_MAX_SEARCH
    ) -> SearchResult:
        """
        Search for a term in dictionaries.
        
        Args:
            term: Term to search for
            dictionary_group: Dictionary group configuration
            search_mode: Search mode to use
            deinflect: Whether to apply deinflection
            dict_limit: Maximum results per dictionary
            max_results: Maximum total results
            
        Returns:
            SearchResult object with results
        """
        if not term or not term.strip():
            return SearchResult(results={}, total_count=0)
        
        term = term.strip()
        dictionaries = dictionary_group.get('dictionaries', [])
        
        if not dictionaries:
            return SearchResult(results={}, total_count=0)
        
        return self.repository.search_term(
            term=term,
            dictionaries=dictionaries,
            search_mode=search_mode,
            deinflect=deinflect,
            conjugations=self.conjugations,
            dict_limit=dict_limit,
            max_defs=max_results
        )
    
    def search_multiple_terms(
        self,
        terms: List[str],
        dictionary_group: Dict[str, any],
        **kwargs
    ) -> Dict[str, SearchResult]:
        """
        Search for multiple terms.
        
        Args:
            terms: List of terms to search
            dictionary_group: Dictionary group configuration
            **kwargs: Additional search parameters
            
        Returns:
            Dictionary mapping terms to their search results
        """
        results = {}
        for term in terms:
            results[term] = self.search(term, dictionary_group, **kwargs)
        return results
    
    def get_definition_for_export(
        self,
        term: str,
        dict_name: str,
        limit: int = 1
    ) -> List[Dict]:
        """
        Get definitions formatted for export.
        
        Args:
            term: Term to look up
            dict_name: Dictionary name
            limit: Maximum number of definitions
            
        Returns:
            List of formatted definitions
        """
        # This would use the repository to get specific definitions
        # Implementation depends on export requirements
        pass
    
    def _load_conjugations(self) -> Dict[str, List]:
        """
        Load conjugation rules for all languages.
        
        Returns:
            Dictionary mapping language to conjugation rules
        """
        conjugations = {}
        languages = self.repository.get_all_languages()
        
        for lang in languages:
            conj_file = self._find_conjugation_file(lang)
            if conj_file and conj_file.exists():
                try:
                    with open(conj_file, 'r', encoding='utf-8') as f:
                        conjugations[lang] = json.load(f)
                except Exception as e:
                    print(f"Error loading conjugations for {lang}: {e}")
        
        return conjugations
    
    def _find_conjugation_file(self, language: str) -> Optional[Path]:
        """
        Find conjugation file for a language.
        
        Args:
            language: Language name
            
        Returns:
            Path to conjugation file or None
        """
        # Check in db/conjugation directory
        db_path = self.addon_path / "user_files" / "db" / "conjugation" / f"{language}.json"
        if db_path.exists():
            return db_path
        
        # Check in dictionaries directory
        dict_path = self.addon_path / "user_files" / "dictionaries" / language / "conjugations.json"
        if dict_path.exists():
            return dict_path
        
        return None
    
    def reload_conjugations(self) -> None:
        """Reload conjugation rules."""
        self.conjugations = self._load_conjugations()
    
    def get_available_languages(self) -> List[str]:
        """
        Get list of available languages.
        
        Returns:
            List of language names
        """
        return self.repository.get_all_languages()
    
    def get_dictionaries_for_language(self, language: str) -> List[str]:
        """
        Get dictionaries available for a language.
        
        Args:
            language: Language name
            
        Returns:
            List of dictionary names
        """
        return self.repository.get_dictionaries_by_language(language)
    
    def validate_search_mode(self, mode: str) -> bool:
        """
        Validate search mode.
        
        Args:
            mode: Search mode to validate
            
        Returns:
            True if valid
        """
        valid_modes = [
            'Forward', 'Backward', 'Anywhere', 'Exact',
            'Definition', 'Example', 'Pronunciation'
        ]
        return mode in valid_modes
