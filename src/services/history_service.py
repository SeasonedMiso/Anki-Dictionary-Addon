# -*- coding: utf-8 -*-
"""
History Service - Search history management.

This module provides search history tracking, storage, and retrieval
with ordering by recency and optional filtering.
"""

from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class HistoryEntry:
    """Represents a single search history entry."""
    word: str
    timestamp: str
    source_dict: Optional[str] = None
    search_mode: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class HistoryService:
    """
    Service for managing search history.
    
    Provides history tracking, storage, retrieval, and management.
    """
    
    def __init__(self, user_files_dir: Optional[str] = None, max_entries: int = 1000):
        """
        Initialize history service.
        
        Args:
            user_files_dir: Directory for storing history file
            max_entries: Maximum number of history entries to keep
        """
        self.user_files_dir = Path(user_files_dir) if user_files_dir else Path.home() / '.anki_dict'
        self.user_files_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.user_files_dir / 'search_history.json'
        self.max_entries = max_entries
        self._history: List[HistoryEntry] = []
        self._load_history()
    
    def add_entry(
        self,
        word: str,
        source_dict: Optional[str] = None,
        search_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add an entry to search history.
        
        Args:
            word: Word that was searched
            source_dict: Source dictionary used
            search_mode: Search mode used
            
        Returns:
            Result dictionary:
            {
                'success': bool,
                'entry': HistoryEntry,
                'total_entries': int,
                'error': str or None
            }
        """
        try:
            if not word or not word.strip():
                return {
                    'success': False,
                    'entry': None,
                    'total_entries': len(self._history),
                    'error': 'Word cannot be empty'
                }
            
            word = word.strip()
            
            # Create new entry
            entry = HistoryEntry(
                word=word,
                timestamp=datetime.now().isoformat(),
                source_dict=source_dict,
                search_mode=search_mode
            )
            
            # Add to beginning (most recent first)
            self._history.insert(0, entry)
            
            # Trim if exceeds max
            if len(self._history) > self.max_entries:
                self._history = self._history[:self.max_entries]
            
            # Save to file
            self._save_history()
            
            logger.debug(f"History entry added: {word}")
            
            return {
                'success': True,
                'entry': entry,
                'total_entries': len(self._history),
                'error': None
            }
        except Exception as e:
            logger.error(f"Error adding history entry: {e}")
            return {
                'success': False,
                'entry': None,
                'total_entries': len(self._history),
                'error': str(e)
            }
    
    def get_history(
        self,
        limit: Optional[int] = None,
        word_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get search history.
        
        Args:
            limit: Maximum number of entries to return
            word_filter: Optional filter to match words containing this string
            
        Returns:
            Result dictionary:
            {
                'success': bool,
                'entries': [HistoryEntry],
                'total_count': int,
                'error': str or None
            }
        """
        try:
            entries = self._history
            
            # Apply word filter if provided
            if word_filter:
                word_filter = word_filter.lower()
                entries = [e for e in entries if word_filter in e.word.lower()]
            
            # Apply limit
            if limit:
                entries = entries[:limit]
            
            return {
                'success': True,
                'entries': entries,
                'total_count': len(self._history),
                'error': None
            }
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return {
                'success': False,
                'entries': [],
                'total_count': 0,
                'error': str(e)
            }
    
    def get_recent(self, count: int = 10) -> Dict[str, Any]:
        """
        Get most recent history entries.
        
        Args:
            count: Number of recent entries to return
            
        Returns:
            Result dictionary with recent entries
        """
        return self.get_history(limit=count)
    
    def search_history(self, query: str) -> Dict[str, Any]:
        """
        Search history for entries matching a query.
        
        Args:
            query: Search query
            
        Returns:
            Result dictionary with matching entries
        """
        return self.get_history(word_filter=query)
    
    def remove_entry(self, word: str) -> Dict[str, Any]:
        """
        Remove all entries for a specific word.
        
        Args:
            word: Word to remove from history
            
        Returns:
            Result dictionary:
            {
                'success': bool,
                'removed_count': int,
                'total_entries': int,
                'error': str or None
            }
        """
        try:
            original_count = len(self._history)
            self._history = [e for e in self._history if e.word != word]
            removed_count = original_count - len(self._history)
            
            if removed_count > 0:
                self._save_history()
                logger.debug(f"Removed {removed_count} entries for '{word}'")
            
            return {
                'success': True,
                'removed_count': removed_count,
                'total_entries': len(self._history),
                'error': None
            }
        except Exception as e:
            logger.error(f"Error removing history entry: {e}")
            return {
                'success': False,
                'removed_count': 0,
                'total_entries': len(self._history),
                'error': str(e)
            }
    
    def clear_history(self) -> Dict[str, Any]:
        """
        Clear all search history.
        
        Returns:
            Result dictionary:
            {
                'success': bool,
                'cleared_count': int,
                'error': str or None
            }
        """
        try:
            cleared_count = len(self._history)
            self._history.clear()
            self._save_history()
            
            logger.info(f"History cleared: {cleared_count} entries removed")
            
            return {
                'success': True,
                'cleared_count': cleared_count,
                'error': None
            }
        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return {
                'success': False,
                'cleared_count': 0,
                'error': str(e)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get history statistics.
        
        Returns:
            Result dictionary:
            {
                'success': bool,
                'total_entries': int,
                'unique_words': int,
                'oldest_entry': str or None,
                'newest_entry': str or None,
                'error': str or None
            }
        """
        try:
            unique_words = len(set(e.word for e in self._history))
            oldest = self._history[-1].timestamp if self._history else None
            newest = self._history[0].timestamp if self._history else None
            
            return {
                'success': True,
                'total_entries': len(self._history),
                'unique_words': unique_words,
                'oldest_entry': oldest,
                'newest_entry': newest,
                'error': None
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                'success': False,
                'total_entries': 0,
                'unique_words': 0,
                'oldest_entry': None,
                'newest_entry': None,
                'error': str(e)
            }
    
    def export_history(self, filepath: Optional[str] = None) -> Dict[str, Any]:
        """
        Export history to a JSON file.
        
        Args:
            filepath: Optional custom filepath
            
        Returns:
            Result dictionary:
            {
                'success': bool,
                'filepath': str or None,
                'entries_exported': int,
                'error': str or None
            }
        """
        try:
            if filepath is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filepath = str(self.user_files_dir / f'history_export_{timestamp}.json')
            
            filepath = Path(filepath)
            
            # Prepare export data
            export_data = {
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'version': '1.0',
                    'total_entries': len(self._history)
                },
                'history': [e.to_dict() for e in self._history]
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"History exported to {filepath}")
            
            return {
                'success': True,
                'filepath': str(filepath),
                'entries_exported': len(self._history),
                'error': None
            }
        except Exception as e:
            logger.error(f"Error exporting history: {e}")
            return {
                'success': False,
                'filepath': None,
                'entries_exported': 0,
                'error': str(e)
            }
    
    def _load_history(self) -> None:
        """Load history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle both old and new formats
                if isinstance(data, list):
                    # Old format: direct list
                    entries_data = data
                else:
                    # New format: with metadata
                    entries_data = data.get('history', [])
                
                self._history = [
                    HistoryEntry(
                        word=e.get('word', ''),
                        timestamp=e.get('timestamp', datetime.now().isoformat()),
                        source_dict=e.get('source_dict'),
                        search_mode=e.get('search_mode')
                    )
                    for e in entries_data
                ]
                
                logger.debug(f"Loaded {len(self._history)} history entries")
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            self._history = []
    
    def _save_history(self) -> None:
        """Save history to file."""
        try:
            export_data = {
                'metadata': {
                    'saved_at': datetime.now().isoformat(),
                    'version': '1.0',
                    'total_entries': len(self._history)
                },
                'history': [e.to_dict() for e in self._history]
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(self._history)} history entries")
        except Exception as e:
            logger.error(f"Error saving history: {e}")
