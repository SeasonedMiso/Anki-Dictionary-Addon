# -*- coding: utf-8 -*-
"""
Tests for the Window State Manager.

Tests persistent window state management with graceful handling of
missing or invalid configuration and thread-safe operations.
"""

import pytest
import sys
import json
import tempfile
from pathlib import Path
from threading import Thread
from unittest.mock import Mock, MagicMock, patch

# Add src to path to import UI modules directly
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import directly from the module to avoid __init__.py issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "window_state_manager",
    Path(__file__).parent.parent / 'src' / 'ui' / 'window_state_manager.py'
)
window_state_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(window_state_manager_module)

WindowState = window_state_manager_module.WindowState
WindowStateManager = window_state_manager_module.WindowStateManager
get_window_state_manager = window_state_manager_module.get_window_state_manager


class TestWindowState:
    """Tests for WindowState class."""
    
    def test_window_state_creation(self):
        """Test creating a window state."""
        state = WindowState(x=100, y=200, width=800, height=600)
        
        assert state.x == 100
        assert state.y == 200
        assert state.width == 800
        assert state.height == 600
    
    def test_window_state_defaults(self):
        """Test window state with default values."""
        state = WindowState()
        
        assert state.x == 0
        assert state.y == 0
        assert state.width == 800
        assert state.height == 600
    
    def test_window_state_negative_coordinates_clamped(self):
        """Test that negative coordinates are clamped to 0."""
        state = WindowState(x=-100, y=-50, width=800, height=600)
        
        assert state.x == 0
        assert state.y == 0
    
    def test_window_state_minimum_dimensions(self):
        """Test that dimensions are enforced to minimum values."""
        state = WindowState(x=0, y=0, width=50, height=50)
        
        assert state.width == 100
        assert state.height == 100
    
    def test_window_state_to_dict(self):
        """Test converting window state to dictionary."""
        state = WindowState(x=100, y=200, width=800, height=600)
        result = state.to_dict()
        
        assert result == {
            'x': 100,
            'y': 200,
            'width': 800,
            'height': 600
        }
    
    def test_window_state_from_dict(self):
        """Test creating window state from dictionary."""
        data = {'x': 100, 'y': 200, 'width': 800, 'height': 600}
        state = WindowState.from_dict(data)
        
        assert state.x == 100
        assert state.y == 200
        assert state.width == 800
        assert state.height == 600
    
    def test_window_state_from_dict_missing_keys(self):
        """Test creating window state from incomplete dictionary."""
        data = {'x': 100, 'y': 200}
        state = WindowState.from_dict(data)
        
        assert state.x == 100
        assert state.y == 200
        assert state.width == 800  # Default
        assert state.height == 600  # Default
    
    def test_window_state_from_dict_invalid_values(self):
        """Test creating window state from dictionary with invalid values."""
        data = {'x': 'invalid', 'y': 200, 'width': 800, 'height': 600}
        state = WindowState.from_dict(data)
        
        # Should use all defaults when any value is invalid
        assert state.x == 0
        assert state.y == 0
        assert state.width == 800
        assert state.height == 600
    
    def test_window_state_from_dict_empty(self):
        """Test creating window state from empty dictionary."""
        state = WindowState.from_dict({})
        
        assert state.x == 0
        assert state.y == 0
        assert state.width == 800
        assert state.height == 600
    
    def test_window_state_is_valid(self):
        """Test checking if window state is valid."""
        valid_state = WindowState(x=0, y=0, width=800, height=600)
        assert valid_state.is_valid() is True
        
        # Dimensions are clamped in __init__, so even small values become valid
        small_state = WindowState(x=0, y=0, width=50, height=50)
        assert small_state.width == 100  # Clamped to minimum
        assert small_state.height == 100  # Clamped to minimum
        assert small_state.is_valid() is True


class TestWindowStateManager:
    """Tests for WindowStateManager class."""
    
    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        yield temp_path
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
    
    def test_window_state_manager_initialization(self, temp_config_file):
        """Test window state manager initialization."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        assert manager._config_path == temp_config_file
        assert len(manager.list_window_ids()) == 0
    
    def test_window_state_manager_initialization_no_config(self):
        """Test window state manager initialization without config file."""
        manager = WindowStateManager(config_path=Path('/nonexistent/path/config.json'))
        
        assert len(manager.list_window_ids()) == 0
    
    def test_save_and_get_window_state(self, temp_config_file):
        """Test saving and retrieving window state."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        widget = Mock()
        widget.geometry.return_value = Mock(x=100, y=200, width=800, height=600)
        
        result = manager.save_window_state('test_window', widget)
        assert result is True
        
        state = manager.get_window_state('test_window')
        assert state is not None
        assert state.x == 100
        assert state.y == 200
        assert state.width == 800
        assert state.height == 600
    
    def test_save_window_state_no_widget(self, temp_config_file):
        """Test saving window state with no widget."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        result = manager.save_window_state('test_window', None)
        assert result is False
    
    def test_has_window_state(self, temp_config_file):
        """Test checking if window state exists."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        assert manager.has_window_state('test_window') is False
        
        widget = Mock()
        widget.geometry.return_value = Mock(x=0, y=0, width=800, height=600)
        manager.save_window_state('test_window', widget)
        
        assert manager.has_window_state('test_window') is True
    
    def test_delete_window_state(self, temp_config_file):
        """Test deleting window state."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        widget = Mock()
        widget.geometry.return_value = Mock(x=0, y=0, width=800, height=600)
        manager.save_window_state('test_window', widget)
        
        assert manager.has_window_state('test_window') is True
        
        result = manager.delete_window_state('test_window')
        assert result is True
        assert manager.has_window_state('test_window') is False
    
    def test_delete_nonexistent_window_state(self, temp_config_file):
        """Test deleting a window state that doesn't exist."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        result = manager.delete_window_state('nonexistent')
        assert result is False
    
    def test_clear_all_states(self, temp_config_file):
        """Test clearing all window states."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        widget = Mock()
        widget.geometry.return_value = Mock(x=0, y=0, width=800, height=600)
        
        manager.save_window_state('window1', widget)
        manager.save_window_state('window2', widget)
        
        assert len(manager.list_window_ids()) == 2
        
        manager.clear_all_states()
        
        assert len(manager.list_window_ids()) == 0
    
    def test_list_window_ids(self, temp_config_file):
        """Test listing all window IDs."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        widget = Mock()
        widget.geometry.return_value = Mock(x=0, y=0, width=800, height=600)
        
        manager.save_window_state('window1', widget)
        manager.save_window_state('window2', widget)
        manager.save_window_state('window3', widget)
        
        ids = manager.list_window_ids()
        assert len(ids) == 3
        assert 'window1' in ids
        assert 'window2' in ids
        assert 'window3' in ids
    
    def test_get_all_states(self, temp_config_file):
        """Test getting all window states as dictionaries."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        widget = Mock()
        widget.geometry.return_value = Mock(x=100, y=200, width=800, height=600)
        
        manager.save_window_state('window1', widget)
        
        all_states = manager.get_all_states()
        
        assert 'window1' in all_states
        assert all_states['window1']['x'] == 100
        assert all_states['window1']['y'] == 200
    
    def test_load_states_from_file(self, temp_config_file):
        """Test loading window states from file."""
        # Write test data to file
        test_data = {
            'window1': {'x': 100, 'y': 200, 'width': 800, 'height': 600},
            'window2': {'x': 50, 'y': 75, 'width': 1024, 'height': 768}
        }
        with open(temp_config_file, 'w') as f:
            json.dump(test_data, f)
        
        # Create manager and verify states are loaded
        manager = WindowStateManager(config_path=temp_config_file)
        
        assert manager.has_window_state('window1') is True
        assert manager.has_window_state('window2') is True
        
        state1 = manager.get_window_state('window1')
        assert state1.x == 100
        assert state1.y == 200
    
    def test_load_states_invalid_json(self, temp_config_file):
        """Test loading window states from invalid JSON file."""
        # Write invalid JSON
        with open(temp_config_file, 'w') as f:
            f.write('{ invalid json }')
        
        # Should not raise error, just log warning
        manager = WindowStateManager(config_path=temp_config_file)
        assert len(manager.list_window_ids()) == 0
    
    def test_load_states_invalid_format(self, temp_config_file):
        """Test loading window states from file with invalid format."""
        # Write non-dict JSON
        with open(temp_config_file, 'w') as f:
            json.dump(['not', 'a', 'dict'], f)
        
        # Should not raise error, just log warning
        manager = WindowStateManager(config_path=temp_config_file)
        assert len(manager.list_window_ids()) == 0
    
    def test_reload_states(self, temp_config_file):
        """Test reloading window states from file."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        widget = Mock()
        widget.geometry.return_value = Mock(x=0, y=0, width=800, height=600)
        manager.save_window_state('window1', widget)
        
        # Manually modify file
        test_data = {
            'window2': {'x': 50, 'y': 75, 'width': 1024, 'height': 768}
        }
        with open(temp_config_file, 'w') as f:
            json.dump(test_data, f)
        
        # Reload and verify
        manager.reload_states()
        
        assert manager.has_window_state('window1') is False
        assert manager.has_window_state('window2') is True
    
    def test_restore_window_state_no_widget(self, temp_config_file):
        """Test restoring window state with no widget."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        result = manager.restore_window_state('test_window', None)
        assert result is False
    
    def test_restore_window_state_not_found_no_default(self, temp_config_file):
        """Test restoring window state that doesn't exist without default."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        widget = Mock()
        
        result = manager.restore_window_state('nonexistent', widget)
        assert result is False
    
    def test_restore_window_state_not_found_with_default(self, temp_config_file):
        """Test restoring window state that doesn't exist with default."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        widget = Mock()
        default_state = WindowState(x=50, y=75, width=1024, height=768)
        
        result = manager.restore_window_state('nonexistent', widget, default_state)
        assert result is True
        
        widget.setGeometry.assert_called_once()
    
    def test_restore_window_state_success(self, temp_config_file):
        """Test successfully restoring window state."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        # Save state
        save_widget = Mock()
        save_widget.geometry.return_value = Mock(x=100, y=200, width=800, height=600)
        manager.save_window_state('test_window', save_widget)
        
        # Restore state
        restore_widget = Mock()
        result = manager.restore_window_state('test_window', restore_widget)
        
        assert result is True
        restore_widget.setGeometry.assert_called_once_with(100, 200, 800, 600)
    
    def test_restore_window_state_invalid_state(self, temp_config_file):
        """Test restoring window state that is clamped to minimum dimensions."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        # Manually create state with small dimensions (will be clamped)
        manager._states['test_window'] = WindowState(x=0, y=0, width=50, height=50)
        
        widget = Mock()
        result = manager.restore_window_state('test_window', widget)
        
        # Should succeed because dimensions are clamped to valid values
        assert result is True
        widget.setGeometry.assert_called_once_with(0, 0, 100, 100)
    
    def test_multiple_windows(self, temp_config_file):
        """Test managing multiple windows."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        widget1 = Mock()
        widget1.geometry.return_value = Mock(x=0, y=0, width=800, height=600)
        
        widget2 = Mock()
        widget2.geometry.return_value = Mock(x=100, y=100, width=1024, height=768)
        
        manager.save_window_state('window1', widget1)
        manager.save_window_state('window2', widget2)
        
        state1 = manager.get_window_state('window1')
        state2 = manager.get_window_state('window2')
        
        assert state1.width == 800
        assert state2.width == 1024
    
    # Thread Safety Tests
    
    def test_thread_safe_save_operations(self, temp_config_file):
        """Test thread-safe save operations."""
        manager = WindowStateManager(config_path=temp_config_file)
        results = []
        
        def save_state(index):
            widget = Mock()
            widget.geometry.return_value = Mock(
                x=index*10, y=index*20, width=800, height=600
            )
            success = manager.save_window_state(f'window_{index}', widget)
            results.append(success)
        
        threads = [Thread(target=save_state, args=(i,)) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        assert all(results)
        assert len(manager.list_window_ids()) == 10
    
    def test_thread_safe_restore_operations(self, temp_config_file):
        """Test thread-safe restore operations."""
        manager = WindowStateManager(config_path=temp_config_file)
        
        # Pre-populate states
        for i in range(10):
            manager._states[f'window_{i}'] = WindowState(
                x=i*10, y=i*20, width=800, height=600
            )
        
        results = []
        
        def restore_state(index):
            widget = Mock()
            success = manager.restore_window_state(f'window_{index}', widget)
            results.append(success)
        
        threads = [Thread(target=restore_state, args=(i,)) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        assert all(results)
    
    def test_thread_safe_mixed_operations(self, temp_config_file):
        """Test thread-safe mixed operations."""
        manager = WindowStateManager(config_path=temp_config_file)
        results = []
        
        def mixed_operations(index):
            if index % 2 == 0:
                widget = Mock()
                widget.geometry.return_value = Mock(
                    x=index*10, y=index*20, width=800, height=600
                )
                success = manager.save_window_state(f'window_{index}', widget)
                results.append(('save', success))
            else:
                widget = Mock()
                success = manager.restore_window_state(f'window_{index-1}', widget)
                results.append(('restore', success))
        
        threads = [Thread(target=mixed_operations, args=(i,)) for i in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        assert len(results) == 10


class TestGlobalWindowStateManager:
    """Tests for global window state manager instance."""
    
    def test_get_window_state_manager_singleton(self):
        """Test that get_window_state_manager returns a singleton."""
        # Reset global manager for this test
        window_state_manager_module._global_window_state_manager = None
        
        manager1 = get_window_state_manager()
        manager2 = get_window_state_manager()
        
        assert manager1 is manager2
    
    def test_get_window_state_manager_with_config_path(self):
        """Test getting window state manager with custom config path."""
        # Reset global manager for this test
        window_state_manager_module._global_window_state_manager = None
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            manager = get_window_state_manager(config_path=temp_path)
            assert manager._config_path == temp_path
        finally:
            if temp_path.exists():
                temp_path.unlink()
            # Reset for other tests
            window_state_manager_module._global_window_state_manager = None
