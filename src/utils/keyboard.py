# -*- coding: utf-8 -*-
"""
Optimized keyboard shortcuts and hotkey management.

Provides cross-platform keyboard shortcut handling with proper platform detection
and modifier key mapping. This is the optimized version of keyboard utilities.
"""

import logging
import platform
from typing import Optional, Callable, Dict, List

try:
    from aqt.qt import QShortcut, QKeySequence, QWidget
    ANKI_AVAILABLE = True
except ImportError:
    ANKI_AVAILABLE = False
    QShortcut = None
    QKeySequence = None
    QWidget = None

logger = logging.getLogger(__name__)


class KeyboardManager:
    """Optimized cross-platform keyboard shortcut manager."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.shortcuts: List[QShortcut] = []
        
        # Platform-specific modifier keys
        self.ctrl_key = "Cmd" if self.platform == "darwin" else "Ctrl"
        self.alt_key = "Option" if self.platform == "darwin" else "Alt"
        
        logger.debug(f"KeyboardManager initialized for {self.platform}")
    
    def get_platform_key_sequence(self, key_combo: str) -> str:
        """
        Convert generic key combination to platform-specific sequence.
        
        Args:
            key_combo: Generic key combination (e.g., "Ctrl+F")
            
        Returns:
            Platform-specific key sequence
        """
        # Replace generic modifiers with platform-specific ones
        sequence = key_combo.replace("Ctrl", self.ctrl_key)
        sequence = sequence.replace("Alt", self.alt_key)
        return sequence
    
    def register_shortcut(self, 
                         widget: QWidget, 
                         key_combo: str, 
                         callback: Callable,
                         description: str = "") -> bool:
        """
        Register a keyboard shortcut for a widget.
        
        Args:
            widget: Widget to register shortcut for
            key_combo: Key combination (e.g., "Ctrl+F")
            callback: Function to call when shortcut is activated
            description: Optional description for logging
            
        Returns:
            True if shortcut was registered successfully
        """
        if not ANKI_AVAILABLE or not widget:
            logger.warning("Cannot register shortcut: Anki not available or widget is None")
            return False
        
        try:
            sequence = self.get_platform_key_sequence(key_combo)
            shortcut = QShortcut(QKeySequence(sequence), widget)
            shortcut.activated.connect(callback)
            
            self.shortcuts.append(shortcut)
            logger.debug(f"Registered shortcut: {sequence} - {description}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register shortcut {key_combo}: {e}")
            return False
    
    def register_multiple_shortcuts(self, 
                                  widget: QWidget, 
                                  shortcuts: Dict[str, tuple[Callable, str]]) -> int:
        """
        Register multiple shortcuts at once.
        
        Args:
            widget: Widget to register shortcuts for
            shortcuts: Dict mapping key_combo to (callback, description)
            
        Returns:
            Number of shortcuts successfully registered
        """
        success_count = 0
        for key_combo, (callback, description) in shortcuts.items():
            if self.register_shortcut(widget, key_combo, callback, description):
                success_count += 1
        
        logger.info(f"Registered {success_count}/{len(shortcuts)} shortcuts")
        return success_count
    
    def setup_font_shortcuts(self, widget: QWidget, theme_manager) -> bool:
        """
        Setup standard font size keyboard shortcuts.
        
        Args:
            widget: Widget to register shortcuts for
            theme_manager: Theme manager with font size methods
            
        Returns:
            True if at least one shortcut was registered
        """
        if not widget or not theme_manager:
            return False
        
        shortcuts = {
            "Ctrl++": (theme_manager.increase_font_size, "Increase font size"),
            "Ctrl+=": (theme_manager.increase_font_size, "Increase font size (alt)"),
            "Ctrl+-": (theme_manager.decrease_font_size, "Decrease font size"),
            "Ctrl+0": (theme_manager.reset_font_size, "Reset font size")
        }
        
        return self.register_multiple_shortcuts(widget, shortcuts) > 0
    
    def setup_navigation_shortcuts(self, widget: QWidget, callbacks: Dict[str, Callable]) -> bool:
        """
        Setup standard navigation keyboard shortcuts.
        
        Args:
            widget: Widget to register shortcuts for
            callbacks: Dict mapping action names to callback functions
            
        Returns:
            True if at least one shortcut was registered
        """
        if not widget or not callbacks:
            return False
        
        # Map standard shortcuts to callback names
        shortcut_map = {
            "Ctrl+F": ("focus_search", "Focus search field"),
            "Ctrl+L": ("clear_search", "Clear search"),
            "Ctrl+R": ("refresh_results", "Refresh results"),
            "Ctrl+T": ("toggle_theme", "Toggle theme"),
            "Escape": ("close_dialog", "Close dialog"),
            "Ctrl+W": ("close_window", "Close window"),
            "Ctrl+Enter": ("submit_form", "Submit form"),
            "F5": ("refresh", "Refresh")
        }
        
        # Build shortcuts dict with available callbacks
        shortcuts = {}
        for key_combo, (action_name, description) in shortcut_map.items():
            if action_name in callbacks:
                shortcuts[key_combo] = (callbacks[action_name], description)
        
        return self.register_multiple_shortcuts(widget, shortcuts) > 0
    
    def setup_export_shortcuts(self, widget: QWidget, callbacks: Dict[str, Callable]) -> bool:
        """
        Setup export-specific keyboard shortcuts.
        
        Args:
            widget: Widget to register shortcuts for
            callbacks: Dict mapping action names to callback functions
            
        Returns:
            True if at least one shortcut was registered
        """
        if not widget or not callbacks:
            return False
        
        shortcut_map = {
            "Ctrl+S": ("save_export", "Save/Export"),
            "Ctrl+Shift+S": ("save_as", "Save As"),
            "Ctrl+E": ("export_current", "Export current item"),
            "Ctrl+A": ("select_all", "Select all"),
            "Ctrl+D": ("duplicate", "Duplicate"),
            "Delete": ("delete_selected", "Delete selected")
        }
        
        shortcuts = {}
        for key_combo, (action_name, description) in shortcut_map.items():
            if action_name in callbacks:
                shortcuts[key_combo] = (callbacks[action_name], description)
        
        return self.register_multiple_shortcuts(widget, shortcuts) > 0
    
    def clear_shortcuts(self):
        """Clear all registered shortcuts."""
        for shortcut in self.shortcuts:
            try:
                shortcut.setEnabled(False)
                shortcut.deleteLater()
            except Exception as e:
                logger.warning(f"Error clearing shortcut: {e}")
        
        self.shortcuts.clear()
        logger.debug("Cleared all shortcuts")
    
    def get_shortcut_info(self) -> List[Dict[str, str]]:
        """
        Get information about all registered shortcuts.
        
        Returns:
            List of shortcut info dictionaries
        """
        info = []
        for shortcut in self.shortcuts:
            try:
                sequence = shortcut.key().toString()
                info.append({
                    'sequence': sequence,
                    'enabled': shortcut.isEnabled()
                })
            except Exception as e:
                logger.warning(f"Error getting shortcut info: {e}")
        
        return info


# Global keyboard manager instance
_global_keyboard_manager: Optional[KeyboardManager] = None


def get_keyboard_manager() -> KeyboardManager:
    """
    Get or create the global keyboard manager instance.
    
    Returns:
        The global KeyboardManager instance
    """
    global _global_keyboard_manager
    if _global_keyboard_manager is None:
        _global_keyboard_manager = KeyboardManager()
    return _global_keyboard_manager


def register_standard_shortcuts(widget: QWidget, 
                               theme_manager=None,
                               nav_callbacks: Optional[Dict[str, Callable]] = None,
                               export_callbacks: Optional[Dict[str, Callable]] = None) -> bool:
    """
    Convenience function to register all standard shortcuts.
    
    Args:
        widget: Widget to register shortcuts for
        theme_manager: Optional theme manager for font shortcuts
        nav_callbacks: Optional navigation callbacks
        export_callbacks: Optional export callbacks
        
    Returns:
        True if any shortcuts were registered
    """
    manager = get_keyboard_manager()
    success = False
    
    # Font shortcuts
    if theme_manager:
        if manager.setup_font_shortcuts(widget, theme_manager):
            success = True
    
    # Navigation shortcuts
    if nav_callbacks:
        if manager.setup_navigation_shortcuts(widget, nav_callbacks):
            success = True
    
    # Export shortcuts
    if export_callbacks:
        if manager.setup_export_shortcuts(widget, export_callbacks):
            success = True
    
    return success


def clear_all_shortcuts():
    """Clear all shortcuts from the global manager."""
    manager = get_keyboard_manager()
    manager.clear_shortcuts()