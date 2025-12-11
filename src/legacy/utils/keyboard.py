# -*- coding: utf-8 -*-
"""
Keyboard shortcuts and hotkey management for modern UI.

Handles cross-platform keyboard shortcuts with proper platform detection
and modifier key mapping for Windows, macOS, and Linux.
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

try:
    from ...ui.styling import get_theme_manager
except ImportError:
    # Fallback if import fails
    get_theme_manager = None

logger = logging.getLogger(__name__)


class KeyboardManager:
    """Cross-platform keyboard shortcut manager."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.shortcuts: List[QShortcut] = []
        self.theme_manager = get_theme_manager()
        
        # Platform-specific modifier keys
        self.ctrl_key = "Cmd" if self.platform == "darwin" else "Ctrl"
        
    def get_key_sequence(self, key_combo: str) -> str:
        """Get platform-appropriate key sequence."""
        # Replace generic modifiers with platform-specific ones
        sequence = key_combo.replace("Ctrl", self.ctrl_key)
        return sequence
    
    def register_shortcut(self, 
                         widget: QWidget, 
                         key_combo: str, 
                         callback: Callable,
                         description: str = "") -> bool:
        """Register a keyboard shortcut."""
        if not ANKI_AVAILABLE or not widget:
            return False
        
        try:
            sequence = self.get_key_sequence(key_combo)
            shortcut = QShortcut(QKeySequence(sequence), widget)
            shortcut.activated.connect(callback)
            
            self.shortcuts.append(shortcut)
            logger.debug(f"Registered shortcut: {sequence} - {description}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to register shortcut {key_combo}: {e}")
            return False
    
    def setup_font_shortcuts(self, widget: QWidget) -> bool:
        """Setup font size keyboard shortcuts."""
        if not widget:
            return False
        
        shortcuts = [
            ("Ctrl++", self.theme_manager.increase_font_size, "Increase font size"),
            ("Ctrl+=", self.theme_manager.increase_font_size, "Increase font size (alt)"),
            ("Ctrl+-", self.theme_manager.decrease_font_size, "Decrease font size"),
            ("Ctrl+0", self.theme_manager.reset_font_size, "Reset font size")
        ]
        
        success_count = 0
        for key_combo, callback, description in shortcuts:
            if self.register_shortcut(widget, key_combo, callback, description):
                success_count += 1
        
        logger.info(f"Registered {success_count}/{len(shortcuts)} font shortcuts")
        return success_count > 0
    
    def setup_navigation_shortcuts(self, widget: QWidget, callbacks: Dict[str, Callable]) -> bool:
        """Setup navigation keyboard shortcuts."""
        if not widget or not callbacks:
            return False
        
        # Common navigation shortcuts
        nav_shortcuts = {
            "Ctrl+F": "focus_search",
            "Ctrl+L": "clear_search", 
            "Ctrl+R": "refresh_results",
            "Ctrl+T": "toggle_theme",
            "Ctrl+,": "open_settings",
            "Escape": "close_dialog",
            "F1": "show_help"
        }
        
        success_count = 0
        for key_combo, action in nav_shortcuts.items():
            if action in callbacks:
                if self.register_shortcut(widget, key_combo, callbacks[action], f"Navigation: {action}"):
                    success_count += 1
        
        logger.info(f"Registered {success_count} navigation shortcuts")
        return success_count > 0
    
    def setup_dictionary_shortcuts(self, widget: QWidget, callbacks: Dict[str, Callable]) -> bool:
        """Setup dictionary-specific keyboard shortcuts."""
        if not widget or not callbacks:
            return False
        
        # Dictionary-specific shortcuts
        dict_shortcuts = {
            "Ctrl+1": "select_dict_1",
            "Ctrl+2": "select_dict_2", 
            "Ctrl+3": "select_dict_3",
            "Ctrl+A": "audio_pronunciation",
            "Ctrl+I": "search_images",
            "Ctrl+C": "copy_definition",
            "Ctrl+E": "export_to_anki",
            "Ctrl+H": "show_history",
            "Ctrl+B": "toggle_conjugation"
        }
        
        success_count = 0
        for key_combo, action in dict_shortcuts.items():
            if action in callbacks:
                if self.register_shortcut(widget, key_combo, callbacks[action], f"Dictionary: {action}"):
                    success_count += 1
        
        logger.info(f"Registered {success_count} dictionary shortcuts")
        return success_count > 0
    
    def clear_shortcuts(self):
        """Clear all registered shortcuts."""
        for shortcut in self.shortcuts:
            try:
                shortcut.setParent(None)
                shortcut.deleteLater()
            except:
                pass
        
        self.shortcuts.clear()
        logger.debug("Cleared all keyboard shortcuts")
    
    def get_platform_info(self) -> Dict[str, str]:
        """Get platform-specific keyboard information."""
        return {
            "platform": self.platform,
            "ctrl_key": self.ctrl_key,
            "alt_key": "Option" if self.platform == "darwin" else "Alt",
            "shift_key": "Shift",
            "meta_key": "Cmd" if self.platform == "darwin" else "Win"
        }


# Global keyboard manager instance
_global_keyboard_manager = None


def get_keyboard_manager() -> KeyboardManager:
    """Get the global keyboard manager instance."""
    global _global_keyboard_manager
    if _global_keyboard_manager is None:
        _global_keyboard_manager = KeyboardManager()
    return _global_keyboard_manager


def setup_font_shortcuts(widget: QWidget) -> bool:
    """Convenience function to setup font size shortcuts."""
    return get_keyboard_manager().setup_font_shortcuts(widget)


def setup_navigation_shortcuts(widget: QWidget, callbacks: Dict[str, Callable]) -> bool:
    """Convenience function to setup navigation shortcuts."""
    return get_keyboard_manager().setup_navigation_shortcuts(widget, callbacks)


def setup_dictionary_shortcuts(widget: QWidget, callbacks: Dict[str, Callable]) -> bool:
    """Convenience function to setup dictionary shortcuts."""
    return get_keyboard_manager().setup_dictionary_shortcuts(widget, callbacks)


def get_shortcut_help() -> Dict[str, List[str]]:
    """Get help text for all available shortcuts."""
    km = get_keyboard_manager()
    ctrl = km.ctrl_key
    
    return {
        "Font Size": [
            f"{ctrl} + Plus: Increase font size",
            f"{ctrl} + Minus: Decrease font size", 
            f"{ctrl} + 0: Reset font size"
        ],
        "Navigation": [
            f"{ctrl} + F: Focus search bar",
            f"{ctrl} + L: Clear search",
            f"{ctrl} + R: Refresh results",
            f"{ctrl} + T: Toggle theme",
            f"{ctrl} + ,: Open settings",
            "Escape: Close dialog",
            "F1: Show help"
        ],
        "Dictionary": [
            f"{ctrl} + 1-3: Select dictionary",
            f"{ctrl} + A: Play audio",
            f"{ctrl} + I: Search images", 
            f"{ctrl} + C: Copy definition",
            f"{ctrl} + E: Export to Anki",
            f"{ctrl} + H: Show history",
            f"{ctrl} + B: Toggle conjugation"
        ]
    }