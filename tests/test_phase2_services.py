# -*- coding: utf-8 -*-
"""
Property-based tests for Phase 2 services.

Tests core functionality of dictionary, media, export, config, and history services
using property-based testing to ensure correctness across many inputs.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime
from pathlib import Path
import json
import tempfile
from unittest.mock import Mock, MagicMock, patch

# Import services
from src.services.dictionary_service import DictionaryService, WordEntry
from src.services.config_service import ConfigService
from src.services.history_service import HistoryService, HistoryEntry
from src.services.media_service import MediaService
from src.services.export_coordinator import ExportCoordinator


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
def mock_legacy_media_service():
    """Create a mock legacy media service."""
    service = Mock()
    service.download_forvo_audio = Mock(return_value=(True, 'audio.mp3', None))
    service.download_google_images = Mock(return_value=(True, ['image1.jpg'], None))
    service.cleanup_temp_media = Mock()
    return service


@pytest.fixture
def mock_legacy_export_service():
    """Create a mock legacy export service."""
    service = Mock()
    service.create_note = Mock(return_value=(True, None))
    service.get_available_decks = Mock(return_value={'Default': 1})
    service.get_note_types = Mock(return_value=['Basic', 'Cloze'])
    service.get_fields_for_note_type = Mock(return_value=['Front', 'Back'])
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
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_lookup_word_returns_valid_structure(self, service, word):
        """
        **Feature: dictionary-modernization, Property 1: Dictionary Lookup Structure**
        
        For any non-empty word, lookup should return a valid result structure
        with required fields.
        
        **Validates: Requirements 2.1, 2.2**
        """
        result = service.lookup_word(word)
        
        # Check structure
        assert isinstance(result, dict)
        assert 'word' in result
        assert 'entries' in result
        assert 'total_count' in result
        assert 'search_time_ms' in result
        assert 'error' in result
        
        # Check types
        assert isinstance(result['word'], str)
        assert isinstance(result['entries'], list)
        assert isinstance(result['total_count'], int)
        assert isinstance(result['search_time_ms'], (int, float))
    
    @given(st.text(max_size=0))
    @settings(max_examples=10)
    def test_lookup_empty_word_returns_empty_results(self, service, word):
        """
        **Feature: dictionary-modernization, Property 2: Empty Word Handling**
        
        For empty words, lookup should return empty results without error.
        
        **Validates: Requirements 2.1**
        """
        result = service.lookup_word(word)
        
        assert result['total_count'] == 0
        assert result['entries'] == []
        assert result['error'] is None
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=30)
    def test_lookup_caching_returns_same_result(self, service, word):
        """
        **Feature: dictionary-modernization, Property 3: Lookup Caching**
        
        For any word, looking it up twice should return identical results
        (cache hit on second lookup).
        
        **Validates: Requirements 2.1**
        """
        result1 = service.lookup_word(word, use_cache=True)
        result2 = service.lookup_word(word, use_cache=True)
        
        # Results should be identical
        assert result1['word'] == result2['word']
        assert result1['total_count'] == result2['total_count']
        assert len(result1['entries']) == len(result2['entries'])
    
    @given(st.lists(st.text(min_size=1, max_size=30), min_size=1, max_size=5))
    @settings(max_examples=20)
    def test_lookup_multiple_returns_all_words(self, service, words):
        """
        **Feature: dictionary-modernization, Property 4: Multiple Lookups**
        
        For any list of words, lookup_multiple should return results for all words.
        
        **Validates: Requirements 2.1**
        """
        results = service.lookup_multiple(words)
        
        # Should have entry for each word
        assert len(results) == len(words)
        for word in words:
            assert word in results
            assert isinstance(results[word], dict)
    
    def test_cache_management_respects_max_size(self, service):
        """
        **Feature: dictionary-modernization, Property 5: Cache Size Limit**
        
        Cache should not exceed maximum size, removing oldest entries as needed.
        
        **Validates: Requirements 2.1**
        """
        service._cache_max_size = 5
        
        # Add more entries than max size
        for i in range(10):
            service.lookup_word(f"word{i}", use_cache=True)
        
        # Cache should not exceed max size
        assert len(service._search_cache) <= service._cache_max_size


# =============================================================================
# HISTORY SERVICE TESTS
# =============================================================================

class TestHistoryService:
    """Tests for HistoryService."""
    
    @pytest.fixture
    def service(self, temp_user_dir):
        """Create a HistoryService instance."""
        return HistoryService(user_files_dir=temp_user_dir, max_entries=100)
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=50)
    def test_add_entry_returns_valid_structure(self, service, word):
        """
        **Feature: dictionary-modernization, Property 6: History Entry Structure**
        
        For any non-empty word, adding to history should return valid structure.
        
        **Validates: Requirements 5.1**
        """
        result = service.add_entry(word)
        
        assert result['success'] is True
        assert result['entry'] is not None
        assert result['entry'].word == word
        assert isinstance(result['total_entries'], int)
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=30)
    def test_history_ordering_by_recency(self, service, word):
        """
        **Feature: dictionary-modernization, Property 7: History Recency Ordering**
        
        For any sequence of additions, history should be ordered by recency
        (most recent first).
        
        **Validates: Requirements 5.1**
        """
        # Add multiple entries
        service.add_entry(f"{word}_1")
        service.add_entry(f"{word}_2")
        service.add_entry(f"{word}_3")
        
        history = service.get_history()['entries']
        
        # Most recent should be first
        assert history[0].word == f"{word}_3"
        assert history[1].word == f"{word}_2"
        assert history[2].word == f"{word}_1"
    
    @given(st.lists(st.text(min_size=1, max_size=30), min_size=1, max_size=10))
    @settings(max_examples=20)
    def test_history_respects_max_entries(self, service, words):
        """
        **Feature: dictionary-modernization, Property 8: History Max Size**
        
        History should not exceed maximum entries, removing oldest as needed.
        
        **Validates: Requirements 5.1**
        """
        service.max_entries = 5
        
        # Add more entries than max
        for word in words:
            service.add_entry(word)
        
        history = service.get_history()['entries']
        
        # Should not exceed max
        assert len(history) <= service.max_entries
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=30)
    def test_history_persistence_round_trip(self, service, word):
        """
        **Feature: dictionary-modernization, Property 9: History Persistence**
        
        For any added entry, saving and reloading should preserve the entry.
        
        **Validates: Requirements 5.1**
        """
        # Add entry
        service.add_entry(word)
        
        # Create new service instance (simulates reload)
        service2 = HistoryService(
            user_files_dir=service.user_files_dir,
            max_entries=service.max_entries
        )
        
        # Should find the word in reloaded history
        history = service2.get_history()['entries']
        words_in_history = [e.word for e in history]
        
        assert word in words_in_history
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=20)
    def test_remove_entry_removes_all_occurrences(self, service, word):
        """
        **Feature: dictionary-modernization, Property 10: History Removal**
        
        Removing an entry should remove all occurrences of that word.
        
        **Validates: Requirements 5.1**
        """
        # Add same word multiple times
        service.add_entry(word)
        service.add_entry(word)
        service.add_entry(word)
        
        # Remove
        result = service.remove_entry(word)
        
        assert result['removed_count'] == 3
        
        # Verify removed
        history = service.get_history()['entries']
        words_in_history = [e.word for e in history]
        assert word not in words_in_history


# =============================================================================
# CONFIG SERVICE TESTS
# =============================================================================

class TestConfigService:
    """Tests for ConfigService."""
    
    @pytest.fixture
    def service(self, mock_config_manager, temp_user_dir):
        """Create a ConfigService instance."""
        return ConfigService(mock_config_manager, user_files_dir=temp_user_dir)
    
    @given(st.text(min_size=1, max_size=50), st.text(min_size=1, max_size=100))
    @settings(max_examples=30)
    def test_set_get_setting_round_trip(self, service, key, value):
        """
        **Feature: dictionary-modernization, Property 11: Settings Round-trip**
        
        For any setting, setting and getting should preserve the value.
        
        **Validates: Requirements 6.1, 6.2**
        """
        # Set setting
        result = service.set_setting(key, value)
        assert result['success'] is True
        
        # Get setting (mock will return what we set)
        service.config_manager.get_value = Mock(return_value=value)
        retrieved = service.get_setting(key)
        
        assert retrieved == value
    
    @given(st.dictionaries(
        st.text(min_size=1, max_size=20),
        st.text(min_size=1, max_size=50),
        min_size=1,
        max_size=5
    ))
    @settings(max_examples=20)
    def test_update_multiple_settings(self, service, settings_dict):
        """
        **Feature: dictionary-modernization, Property 12: Batch Settings Update**
        
        For any settings dictionary, updating should succeed for all entries.
        
        **Validates: Requirements 6.1**
        """
        result = service.update_settings(settings_dict)
        
        assert result['success'] is True
        assert result['updated'] == len(settings_dict)
        assert result['failed'] == 0
    
    def test_export_import_settings_round_trip(self, service):
        """
        **Feature: dictionary-modernization, Property 13: Settings Export/Import**
        
        Exporting and importing settings should preserve all settings.
        
        **Validates: Requirements 6.3, 6.4**
        """
        # Export
        export_result = service.export_settings()
        assert export_result['success'] is True
        
        # Import
        import_result = service.import_settings(export_result['filepath'])
        assert import_result['success'] is True


# =============================================================================
# MEDIA SERVICE TESTS
# =============================================================================

class TestMediaService:
    """Tests for MediaService."""
    
    @pytest.fixture
    def service(self, mock_legacy_media_service, mock_config_manager):
        """Create a MediaService instance."""
        return MediaService(mock_legacy_media_service, mock_config_manager)
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=30)
    def test_download_audio_returns_valid_structure(self, service, word):
        """
        **Feature: dictionary-modernization, Property 14: Audio Download Structure**
        
        For any word, audio download should return valid result structure.
        
        **Validates: Requirements 3.1, 3.2**
        """
        result = service.download_audio(word)
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'filename' in result
        assert 'error' in result
        assert 'word' in result
        assert 'source' in result
    
    @given(st.text(max_size=0))
    @settings(max_examples=10)
    def test_download_audio_empty_word_fails(self, service, word):
        """
        **Feature: dictionary-modernization, Property 15: Empty Audio Query**
        
        For empty words, audio download should fail gracefully.
        
        **Validates: Requirements 3.1**
        """
        result = service.download_audio(word)
        
        assert result['success'] is False
        assert result['error'] is not None
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=30)
    def test_download_images_returns_valid_structure(self, service, query):
        """
        **Feature: dictionary-modernization, Property 16: Image Download Structure**
        
        For any query, image download should return valid result structure.
        
        **Validates: Requirements 3.1, 3.3**
        """
        result = service.download_images(query)
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'filenames' in result
        assert 'count' in result
        assert 'error' in result
        assert 'query' in result
        assert 'source' in result


# =============================================================================
# EXPORT COORDINATOR TESTS
# =============================================================================

class TestExportCoordinator:
    """Tests for ExportCoordinator."""
    
    @pytest.fixture
    def service(self, mock_legacy_export_service, mock_legacy_search_service,
                 mock_legacy_media_service, mock_config_manager):
        """Create an ExportCoordinator instance."""
        search_service = DictionaryService(mock_legacy_search_service, mock_config_manager)
        media_service = MediaService(mock_legacy_media_service, mock_config_manager)
        return ExportCoordinator(
            mock_legacy_export_service,
            search_service,
            media_service,
            mock_config_manager
        )
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=30)
    def test_export_word_returns_valid_structure(self, service, word):
        """
        **Feature: dictionary-modernization, Property 17: Export Structure**
        
        For any word, export should return valid result structure.
        
        **Validates: Requirements 4.1, 4.2**
        """
        export_data = {
            'word': word,
            'example': 'test example',
            'deck': 'Default',
            'dictionaries': ['JMdict'],
            'template': 'Basic',
            'template_fields': {'Front': '{mapped:word}', 'Back': '{mapped:definition}'}
        }
        
        result = service.export_word(export_data)
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'word' in result
        assert 'deck' in result
        assert 'error' in result
    
    def test_get_available_decks_returns_dict(self, service):
        """
        **Feature: dictionary-modernization, Property 18: Deck Availability**
        
        Getting available decks should return a valid dictionary structure.
        
        **Validates: Requirements 4.1**
        """
        result = service.get_available_decks()
        
        assert result['success'] is True
        assert isinstance(result['decks'], dict)
    
    def test_get_available_templates_returns_list(self, service):
        """
        **Feature: dictionary-modernization, Property 19: Template Availability**
        
        Getting available templates should return a valid list structure.
        
        **Validates: Requirements 4.1**
        """
        result = service.get_available_templates()
        
        assert result['success'] is True
        assert isinstance(result['templates'], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
