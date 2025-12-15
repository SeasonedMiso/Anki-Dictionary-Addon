# -*- coding: utf-8 -*-
"""
Standalone tests for Phase 2 services (no src/__init__.py imports).

Tests core functionality of dictionary, config, and history services.
"""

import pytest
import tempfile
import json
import sys
from pathlib import Path
from unittest.mock import Mock
from datetime import datetime

# Add src to path but import services directly
sys.path.insert(0, str(Path(__file__).parent.parent / 'src' / 'services'))

# Import services directly
import importlib.util

def load_module(name, path):
    """Load a module from a file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

services_path = Path(__file__).parent.parent / 'src' / 'services'
dictionary_service = load_module('dictionary_service', services_path / 'dictionary_service.py')
config_service = load_module('config_service', services_path / 'config_service.py')
history_service = load_module('history_service', services_path / 'history_service.py')

DictionaryService = dictionary_service.DictionaryService
WordEntry = dictionary_service.WordEntry
ConfigService = config_service.ConfigService
HistoryService = history_service.HistoryService
HistoryEntry = history_service.HistoryEntry


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_config_manager():
    """Create a mock config manager."""
    manager = Mock()
    manager.get_value = Mock(side_effect=lambda k, d: d)
    manager.get_bool = Mock(return_value=True)
    manager.get_int = Mock(return_value=50)
    manager.set_value = Mock()
    manager.get_all = Mock(return_value={})
    return manager


@pytest.fixture
def mock_legacy_search_service():
    """Create a mock legacy search service."""
    service = Mock()
    service.search = Mock(return_value=Mock(results={}))
    return service


@pytest.fixture
def temp_user_dir():
    """Create a temporary user directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# =============================================================================
# DICTIONARY SERVICE TESTS
# =============================================================================

class TestDictionaryService:
    """Tests for DictionaryService."""
    
    @pytest.fixture
    def service(self, mock_legacy_search_service, mock_config_manager):
        """Create a DictionaryService instance."""
        return DictionaryService(mock_legacy_search_service, mock_config_manager)
    
    def test_lookup_word_returns_valid_structure(self, service):
        """Test that lookup returns valid structure."""
        result = service.lookup_word("test")
        
        assert isinstance(result, dict)
        assert 'word' in result
        assert 'entries' in result
        assert 'total_count' in result
        assert 'search_time_ms' in result
        assert 'error' in result
    
    def test_lookup_empty_word_returns_empty_results(self, service):
        """Test that empty word returns empty results."""
        result = service.lookup_word("")
        
        assert result['total_count'] == 0
        assert result['entries'] == []
        assert result['error'] is None
    
    def test_lookup_caching_works(self, service):
        """Test that caching returns same result."""
        result1 = service.lookup_word("test", use_cache=True)
        result2 = service.lookup_word("test", use_cache=True)
        
        assert result1['word'] == result2['word']
        assert result1['total_count'] == result2['total_count']
    
    def test_lookup_multiple_returns_all_words(self, service):
        """Test that lookup_multiple returns results for all words."""
        words = ["word1", "word2", "word3"]
        results = service.lookup_multiple(words)
        
        assert len(results) == len(words)
        for word in words:
            assert word in results
    
    def test_cache_management_respects_max_size(self, service):
        """Test that cache doesn't exceed maximum size."""
        service._cache_max_size = 5
        
        for i in range(10):
            service.lookup_word(f"word{i}", use_cache=True)
        
        assert len(service._search_cache) <= service._cache_max_size
    
    def test_clear_cache(self, service):
        """Test that cache can be cleared."""
        service.lookup_word("test", use_cache=True)
        assert len(service._search_cache) > 0
        
        service.clear_cache()
        assert len(service._search_cache) == 0


# =============================================================================
# HISTORY SERVICE TESTS
# =============================================================================

class TestHistoryService:
    """Tests for HistoryService."""
    
    @pytest.fixture
    def service(self, temp_user_dir):
        """Create a HistoryService instance."""
        return HistoryService(user_files_dir=temp_user_dir, max_entries=100)
    
    def test_add_entry_returns_valid_structure(self, service):
        """Test that adding entry returns valid structure."""
        result = service.add_entry("test_word")
        
        assert result['success'] is True
        assert result['entry'] is not None
        assert result['entry'].word == "test_word"
        assert isinstance(result['total_entries'], int)
    
    def test_history_ordering_by_recency(self, service):
        """Test that history is ordered by recency."""
        service.add_entry("word_1")
        service.add_entry("word_2")
        service.add_entry("word_3")
        
        history = service.get_history()['entries']
        
        assert history[0].word == "word_3"
        assert history[1].word == "word_2"
        assert history[2].word == "word_1"
    
    def test_history_respects_max_entries(self, service):
        """Test that history respects max entries limit."""
        service.max_entries = 5
        
        for i in range(10):
            service.add_entry(f"word_{i}")
        
        history = service.get_history()['entries']
        assert len(history) <= service.max_entries
    
    def test_history_persistence_round_trip(self, service):
        """Test that history persists across reloads."""
        service.add_entry("persistent_word")
        
        # Create new service instance (simulates reload)
        service2 = HistoryService(
            user_files_dir=service.user_files_dir,
            max_entries=service.max_entries
        )
        
        history = service2.get_history()['entries']
        words_in_history = [e.word for e in history]
        
        assert "persistent_word" in words_in_history
    
    def test_remove_entry_removes_all_occurrences(self, service):
        """Test that removing entry removes all occurrences."""
        service.add_entry("word")
        service.add_entry("word")
        service.add_entry("word")
        
        result = service.remove_entry("word")
        
        assert result['removed_count'] == 3
        
        history = service.get_history()['entries']
        words_in_history = [e.word for e in history]
        assert "word" not in words_in_history
    
    def test_clear_history(self, service):
        """Test that history can be cleared."""
        service.add_entry("word1")
        service.add_entry("word2")
        
        result = service.clear_history()
        
        assert result['success'] is True
        assert result['cleared_count'] == 2
        
        history = service.get_history()['entries']
        assert len(history) == 0
    
    def test_get_statistics(self, service):
        """Test that statistics are calculated correctly."""
        service.add_entry("word1")
        service.add_entry("word2")
        service.add_entry("word1")
        
        stats = service.get_statistics()
        
        assert stats['success'] is True
        assert stats['total_entries'] == 3
        assert stats['unique_words'] == 2
    
    def test_export_history(self, service):
        """Test that history can be exported."""
        service.add_entry("word1")
        service.add_entry("word2")
        
        result = service.export_history()
        
        assert result['success'] is True
        assert result['entries_exported'] == 2
        assert Path(result['filepath']).exists()
    
    def test_search_history(self, service):
        """Test that history can be searched."""
        service.add_entry("apple")
        service.add_entry("application")
        service.add_entry("banana")
        
        result = service.search_history("app")
        
        assert result['success'] is True
        assert len(result['entries']) == 2


# =============================================================================
# CONFIG SERVICE TESTS
# =============================================================================

class TestConfigService:
    """Tests for ConfigService."""
    
    @pytest.fixture
    def service(self, mock_config_manager, temp_user_dir):
        """Create a ConfigService instance."""
        return ConfigService(mock_config_manager, user_files_dir=temp_user_dir)
    
    def test_set_get_setting(self, service):
        """Test setting and getting a configuration."""
        result = service.set_setting("test_key", "test_value")
        assert result['success'] is True
        
        service.config_manager.get_value = Mock(return_value="test_value")
        retrieved = service.get_setting("test_key")
        assert retrieved == "test_value"
    
    def test_update_multiple_settings(self, service):
        """Test updating multiple settings at once."""
        settings = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        
        result = service.update_settings(settings)
        
        assert result['success'] is True
        assert result['updated'] == 3
        assert result['failed'] == 0
    
    def test_export_settings(self, service):
        """Test exporting settings."""
        result = service.export_settings()
        
        assert result['success'] is True
        assert result['filepath'] is not None
        assert Path(result['filepath']).exists()
    
    def test_backup_settings(self, service):
        """Test backing up settings."""
        result = service.backup_settings(label="test_backup")
        
        assert result['success'] is True
        assert result['filepath'] is not None
        assert Path(result['filepath']).exists()
    
    def test_list_backups(self, service):
        """Test listing backups."""
        service.backup_settings(label="backup1")
        service.backup_settings(label="backup2")
        
        result = service.list_backups()
        
        assert result['success'] is True
        assert len(result['backups']) >= 2
    
    def test_import_export_round_trip(self, service):
        """Test exporting and importing settings."""
        # Export
        export_result = service.export_settings()
        assert export_result['success'] is True
        
        # Import
        import_result = service.import_settings(export_result['filepath'])
        assert import_result['success'] is True


# =============================================================================
# WORD ENTRY TESTS
# =============================================================================

class TestWordEntry:
    """Tests for WordEntry dataclass."""
    
    def test_word_entry_creation(self):
        """Test creating a WordEntry."""
        entry = WordEntry(
            word="test",
            reading="てすと",
            definitions=["definition1", "definition2"]
        )
        
        assert entry.word == "test"
        assert entry.reading == "てすと"
        assert len(entry.definitions) == 2
    
    def test_word_entry_defaults(self):
        """Test WordEntry default values."""
        entry = WordEntry(word="test")
        
        assert entry.word == "test"
        assert entry.reading is None
        assert entry.definitions == []
        assert entry.examples == []


# =============================================================================
# HISTORY ENTRY TESTS
# =============================================================================

class TestHistoryEntry:
    """Tests for HistoryEntry dataclass."""
    
    def test_history_entry_creation(self):
        """Test creating a HistoryEntry."""
        entry = HistoryEntry(
            word="test",
            timestamp=datetime.now().isoformat(),
            source_dict="JMdict"
        )
        
        assert entry.word == "test"
        assert entry.source_dict == "JMdict"
    
    def test_history_entry_to_dict(self):
        """Test converting HistoryEntry to dict."""
        entry = HistoryEntry(
            word="test",
            timestamp=datetime.now().isoformat()
        )
        
        entry_dict = entry.to_dict()
        
        assert isinstance(entry_dict, dict)
        assert entry_dict['word'] == "test"
        assert 'timestamp' in entry_dict


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
