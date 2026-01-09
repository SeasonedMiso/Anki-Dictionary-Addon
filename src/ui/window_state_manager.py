# -*- coding: utf-8 -*-
"""
Window State Manager - Persistent window size and position management.

Provides a clean interface for saving and restoring window state (size and position)
with graceful handling of missing or invalid configuration. Thread-safe implementation
ensures reliable state management across multiple windows.
"""

import logging
import json
from typing import Optional, Dict, Tuple, Any
from threading import Lock
from pathlib import Path

try:
    from aqt.qt import QWidget, QRect, QScreen
    ANKI_AVAILABLE = True
except ImportError:
    ANKI_AVAILABLE = False
    QWidget = None
    QRect = None
    QScreen = None

logger = logging.getLogger(__name__)


class WindowState:
    """
    Represents the saved state of a window.
    
    Stores position (x, y) and size (width, height) information.
    """
    
    def __init__(self, x: int = 0, y: int = 0, width: int = 800, height: int = 600):
        """
        Initialize window state.
        
        Args:
            x: X coordinate of window position
            y: Y coordinate of window position
            width: Window width in pixels
            height: Window height in pixels
        """
        self.x = max(0, x)
        self.y = max(0, y)
        self.width = max(100, width)  # Minimum width
        self.height = max(100, height)  # Minimum height
    
    def to_dict(self) -> Dict[str, int]:
        """
        Convert window state to dictionary.
        
        Returns:
            Dictionary with x, y, width, height keys
        """
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'WindowState':
        """
        Create WindowState from dictionary.
        
        Args:
            data: Dictionary with x, y, width, height keys
            
        Returns:
            WindowState instance with validated values
        """
        try:
            return WindowState(
                x=int(data.get('x', 0)),
                y=int(data.get('y', 0)),
                width=int(data.get('width', 800)),
                height=int(data.get('height', 600))
            )
        except (ValueError, TypeError):
            logger.warning(f"Invalid window state data: {data}, using defaults")
            return WindowState()
    
    def is_valid(self) -> bool:
        """
        Check if window state is valid.
        
        Returns:
            True if state has valid dimensions
        """
        # Note: dimensions are already clamped in __init__, so this always returns True
        # This method is kept for API compatibility and future validation needs
        return True


class WindowStateManager:
    """
    Thread-safe manager for saving and restoring window state.
    
    Handles persistence of window size and position with graceful
    degradation when configuration is missing or invalid.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize window state manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        self._lock = Lock()
        self._states: Dict[str, WindowState] = {}
        self._config_path = config_path or self._get_default_config_path()
        self._load_states()
        logger.debug(f"WindowStateManager initialized with config: {self._config_path}")
    
    @staticmethod
    def _get_default_config_path() -> Path:
        """
        Get the default configuration file path.
        
        Returns:
            Path to default config file
        """
        # Try to use user_files directory if it exists
        user_files = Path(__file__).parent.parent.parent / 'user_files'
        if user_files.exists():
            return user_files / 'window_states.json'
        
        # Fall back to config directory
        config_dir = Path(__file__).parent.parent.parent / 'config'
        if config_dir.exists():
            return config_dir / 'window_states.json'
        
        # Last resort: use current directory
        return Path('window_states.json')
    
    def _load_states(self) -> None:
        """Load window states from configuration file."""
        if not self._config_path.exists():
            logger.debug(f"Config file not found: {self._config_path}")
            return
        
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                logger.warning(f"Invalid config format in {self._config_path}")
                return
            
            for window_id, state_data in data.items():
                try:
                    self._states[window_id] = WindowState.from_dict(state_data)
                except Exception as e:
                    logger.warning(f"Failed to load state for window '{window_id}': {e}")
            
            logger.debug(f"Loaded {len(self._states)} window states")
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse config file {self._config_path}: {e}")
        except Exception as e:
            logger.warning(f"Failed to load window states: {e}")
    
    def _save_states(self) -> None:
        """Save window states to configuration file."""
        try:
            # Ensure directory exists
            self._config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert states to dictionary
            data = {
                window_id: state.to_dict()
                for window_id, state in self._states.items()
            }
            
            # Write to file
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved {len(self._states)} window states to {self._config_path}")
            
        except Exception as e:
            logger.warning(f"Failed to save window states: {e}")
    
    def save_window_state(self, window_id: str, widget: QWidget) -> bool:
        """
        Save the state of a window.
        
        Args:
            window_id: Unique identifier for the window
            widget: QWidget instance to save state from
            
        Returns:
            True if state was saved successfully, False otherwise
        """
        if not widget:
            logger.warning("Cannot save window state: widget is None")
            return False
        
        try:
            geometry = widget.geometry()
            # Handle both real QRect and mock objects
            if hasattr(geometry, 'x') and callable(geometry.x):
                x, y, width, height = geometry.x(), geometry.y(), geometry.width(), geometry.height()
            else:
                x, y, width, height = geometry.x, geometry.y, geometry.width, geometry.height
            
            state = WindowState(x=x, y=y, width=width, height=height)
            
            with self._lock:
                self._states[window_id] = state
                self._save_states()
            
            logger.debug(f"Saved state for window '{window_id}': {state.to_dict()}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to save window state for '{window_id}': {e}")
            return False
    
    def restore_window_state(self, window_id: str, widget: QWidget,
                            default_state: Optional[WindowState] = None) -> bool:
        """
        Restore the state of a window.
        
        Args:
            window_id: Unique identifier for the window
            widget: QWidget instance to restore state to
            default_state: Default state to use if saved state not found
            
        Returns:
            True if state was restored successfully, False otherwise
        """
        if not ANKI_AVAILABLE or not widget:
            logger.warning("Cannot restore window state: Anki not available or widget is None")
            return False
        
        try:
            with self._lock:
                state = self._states.get(window_id)
            
            if state is None:
                if default_state is None:
                    logger.debug(f"No saved state for window '{window_id}', using defaults")
                    return False
                state = default_state
            
            if not state.is_valid():
                logger.warning(f"Invalid state for window '{window_id}', using defaults")
                return False
            
            # Apply state to widget
            widget.setGeometry(state.x, state.y, state.width, state.height)
            
            # Ensure window is visible on screen
            self._ensure_visible_on_screen(widget)
            
            logger.debug(f"Restored state for window '{window_id}': {state.to_dict()}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to restore window state for '{window_id}': {e}")
            return False
    
    def _ensure_visible_on_screen(self, widget: QWidget) -> None:
        """
        Ensure the widget is visible on the current screen.
        
        Adjusts position if window is off-screen.
        
        Args:
            widget: QWidget to check and adjust
        """
        if not ANKI_AVAILABLE:
            return
        
        try:
            geometry = widget.geometry()
            
            # Get available screens
            from aqt.qt import QApplication
            app = QApplication.instance()
            if not app:
                return
            
            screens = app.screens()
            if not screens:
                return
            
            # Check if window is on any screen
            for screen in screens:
                screen_geometry = screen.geometry()
                if geometry.intersects(screen_geometry):
                    return  # Window is visible on at least one screen
            
            # Window is off-screen, move it to primary screen
            primary_screen = screens[0]
            screen_geometry = primary_screen.geometry()
            
            # Center window on primary screen
            new_x = screen_geometry.x() + (screen_geometry.width() - geometry.width()) // 2
            new_y = screen_geometry.y() + (screen_geometry.height() - geometry.height()) // 2
            
            widget.move(new_x, new_y)
            logger.debug(f"Adjusted window position to be visible on screen")
            
        except Exception as e:
            logger.debug(f"Could not ensure window is visible on screen: {e}")
    
    def get_window_state(self, window_id: str) -> Optional[WindowState]:
        """
        Get the saved state for a window.
        
        Args:
            window_id: Unique identifier for the window
            
        Returns:
            WindowState if found, None otherwise
        """
        with self._lock:
            return self._states.get(window_id)
    
    def has_window_state(self, window_id: str) -> bool:
        """
        Check if a window state is saved.
        
        Args:
            window_id: Unique identifier for the window
            
        Returns:
            True if state exists, False otherwise
        """
        with self._lock:
            return window_id in self._states
    
    def delete_window_state(self, window_id: str) -> bool:
        """
        Delete the saved state for a window.
        
        Args:
            window_id: Unique identifier for the window
            
        Returns:
            True if state was deleted, False if not found
        """
        with self._lock:
            if window_id in self._states:
                del self._states[window_id]
                self._save_states()
                logger.debug(f"Deleted state for window '{window_id}'")
                return True
            return False
    
    def clear_all_states(self) -> None:
        """Clear all saved window states."""
        with self._lock:
            self._states.clear()
            self._save_states()
            logger.debug("Cleared all window states")
    
    def list_window_ids(self) -> list:
        """
        Get list of all saved window IDs.
        
        Returns:
            List of window IDs
        """
        with self._lock:
            return list(self._states.keys())
    
    def get_all_states(self) -> Dict[str, Dict[str, int]]:
        """
        Get all window states as dictionaries.
        
        Returns:
            Dictionary mapping window IDs to state dictionaries
        """
        with self._lock:
            return {
                window_id: state.to_dict()
                for window_id, state in self._states.items()
            }
    
    def reload_states(self) -> None:
        """Reload window states from configuration file."""
        with self._lock:
            self._states.clear()
            self._load_states()
            logger.debug("Reloaded window states from file")


# Global window state manager instance
_global_window_state_manager: Optional[WindowStateManager] = None


def get_window_state_manager(config_path: Optional[Path] = None) -> WindowStateManager:
    """
    Get or create the global window state manager instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        The global WindowStateManager instance
    """
    global _global_window_state_manager
    if _global_window_state_manager is None:
        _global_window_state_manager = WindowStateManager(config_path)
    return _global_window_state_manager
