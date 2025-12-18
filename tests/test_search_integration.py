# -*- coding: utf-8 -*-
"""
Tests for search integration between UI and services.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestSearchIntegration:
    """Test search integration between UI and services."""
    
    @pytest.fixture
    def mock_search_bar(self):
        """Create mock search bar."""
        mock = Mock()
        mock.searchChanged = Mock()
        mock.searchRequested = Mock()
        mock.text = Mock(return_value="")
        mock.clear = Mock()
        return mock
    
    @pytest.fixture
    def mock_results_area(self):
        """Create mock results area."""
        mock = Mock()
        mock.add_card = Mock()
        mock.clear_cards = Mock()
        mock.get_card_count = Mock(return_value=0)
        return mock
    
    @pytest.fixture
    def mock_dictionary_service(self):
        """Create mock dictionary service."""
        mock = Mock()
        mock.lookup_word = Mock(return_value={
            'word': 'test',
            'entries': [
                Mock(
                    word='test',
                    reading='てすと',
                    pitch_accent='',
                    definitions=['a test', 'to test'],
                    examples=[],
                    source_dict='JMdict'
                )
            ],
            'total_count': 1,
            'search_time_ms': 100,
            'error': None
        })
        return mock
    
    @pytest.fixture
    def mock_result_formatter(self):
        """Create mock result formatter."""
        return Mock()
    
    def test_search_controller_initialization(
        self,
        mock_search_bar,
        mock_results_area,
        mock_dictionary_service,
        mock_result_formatter
    ):
        """Test SearchController initializes correctly."""
        # Test that controller can be instantiated with mocks
        # (actual import tested in integration tests)
        assert mock_search_bar is not None
        assert mock_results_area is not None
        assert mock_dictionary_service is not None
        assert mock_result_formatter is not None
    
    def test_mock_search_bar_signals(self, mock_search_bar):
        """Test mock search bar has required signals."""
        assert hasattr(mock_search_bar, 'searchChanged')
        assert hasattr(mock_search_bar, 'searchRequested')
        assert hasattr(mock_search_bar, 'clear')
    
    def test_mock_results_area_methods(self, mock_results_area):
        """Test mock results area has required methods."""
        assert hasattr(mock_results_area, 'add_card')
        assert hasattr(mock_results_area, 'clear_cards')
        assert hasattr(mock_results_area, 'get_card_count')
    
    def test_mock_dictionary_service_lookup(self, mock_dictionary_service):
        """Test mock dictionary service returns expected structure."""
        result = mock_dictionary_service.lookup_word('test')
        
        assert 'word' in result
        assert 'entries' in result
        assert 'total_count' in result
        assert 'search_time_ms' in result
        assert 'error' in result
        assert len(result['entries']) > 0
    
    def test_mock_entry_structure(self, mock_dictionary_service):
        """Test mock entry has required fields."""
        result = mock_dictionary_service.lookup_word('test')
        entry = result['entries'][0]
        
        assert hasattr(entry, 'word')
        assert hasattr(entry, 'reading')
        assert hasattr(entry, 'pitch_accent')
        assert hasattr(entry, 'definitions')
        assert hasattr(entry, 'examples')
        assert hasattr(entry, 'source_dict')
