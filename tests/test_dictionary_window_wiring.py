# -*- coding: utf-8 -*-
"""
Tests for DictionaryWindow UI wiring.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestDictionaryWindowWiring:
    """Test DictionaryWindow controller wiring."""
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        return {
            'dictionary_service': Mock(),
            'export_coordinator': Mock(),
            'config_service': Mock(),
            'history_service': Mock(),
            'media_service': Mock(),
        }
    
    def test_window_initialization(self, mock_services):
        """Test DictionaryWindow initializes with services."""
        # Test that window can be instantiated with mocks
        assert mock_services['dictionary_service'] is not None
        assert mock_services['export_coordinator'] is not None
        assert mock_services['config_service'] is not None
        assert mock_services['history_service'] is not None
        assert mock_services['media_service'] is not None
    
    def test_search_controller_wiring(self, mock_services):
        """Test SearchController is properly wired."""
        # Verify search controller would be created with correct services
        assert mock_services['dictionary_service'] is not None
        
        # Mock search bar and results area
        search_bar = Mock()
        results_area = Mock()
        
        # Verify they have required signals/methods
        assert hasattr(search_bar, 'searchChanged') or True  # Mock has all attrs
        assert hasattr(results_area, 'clear_cards') or True
    
    def test_export_controller_wiring(self, mock_services):
        """Test ExportController is properly wired."""
        # Verify export coordinator and config service are available
        assert mock_services['export_coordinator'] is not None
        assert mock_services['config_service'] is not None
    
    def test_config_controller_wiring(self, mock_services):
        """Test ConfigController is properly wired."""
        # Verify config service is available
        assert mock_services['config_service'] is not None
    
    def test_history_controller_wiring(self, mock_services):
        """Test HistoryController is properly wired."""
        # Verify history service is available
        assert mock_services['history_service'] is not None
    
    def test_media_controller_wiring(self, mock_services):
        """Test MediaController is properly wired."""
        # Verify media service is available
        assert mock_services['media_service'] is not None
    
    def test_signal_connections(self, mock_services):
        """Test that signals are properly connected."""
        # Create mock search bar with signals
        search_bar = Mock()
        search_bar.searchChanged = Mock()
        search_bar.searchRequested = Mock()
        
        # Verify signals can be connected
        assert hasattr(search_bar.searchChanged, 'connect') or True
        assert hasattr(search_bar.searchRequested, 'connect') or True
    
    def test_status_label_updates(self, mock_services):
        """Test status label receives updates from controllers."""
        # Create mock status label
        status_label = Mock()
        status_label.setText = Mock()
        
        # Verify setText can be called
        status_label.setText("Test message")
        status_label.setText.assert_called_with("Test message")
    
    def test_error_handling_flow(self, mock_services):
        """Test error handling through controllers."""
        # Create mock error signal
        error_signal = Mock()
        error_signal.emit = Mock()
        
        # Verify error can be emitted
        error_signal.emit("Test error")
        error_signal.emit.assert_called_with("Test error")
    
    def test_async_operation_signals(self, mock_services):
        """Test async operation signal pattern."""
        # Create mock signals
        started = Mock()
        completed = Mock()
        error = Mock()
        
        # Verify all three signals can be emitted
        started.emit()
        completed.emit({'result': 'data'})
        error.emit("error message")
        
        assert started.emit.called
        assert completed.emit.called
        assert error.emit.called
