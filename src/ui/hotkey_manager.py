# -*- coding: utf-8 -*-
"""
Configurable hotkey manager for the dictionary UI.

Provides a clean, configurable interface for managing keyboard shortcuts
without hardcoding key combinations. Supports cross-platform key mapping
and dynamic hotkey registration.
"""

import logging
import platform
from typing import Optional, Callable, Dict, List, Tuple
from dataclasses import dataclass, field

try:
    from aqt.qt import QShortcut, QKeySequence, QWidget
    ANKI_AVAILABLE = True
except ImportError:
    ANKI_AVAILABLE = False
    QShortcut = None
    QKeySequence = None
    QWidget = None

logger = logging.getLogger(__name__)


@dataclass
class HotkeyConfig:
    """Configuration for a single hotkey."""
    key_sequence: str
    callback: Callable
    description: str = ""
    enabled: bool = True


@dataclass
class HotkeyProfile:
    """A profile containing multiple hotkey configurations."""
    name: str
    hotkeys: Dict[str, HotkeyConfig] = field(default_factory=dict)
    
    def add_hotkey(self, action_id: str, key_sequence: str, 
                   callback: Callable, description: str = "") -> None:
        """Add a hotkey to this profile."""
        self.hotkeys[action_id] = HotkeyConfig(
            key_sequence=key_sequence,
            callback=callback,
            description=description
        )
    
    def remove_hotkey(self, action_id: str) -> bool:
        """Remove a hotkey from this profile."""
        if action_id in self.hotkeys:
            del self.hotkeys[action_id]
            return True
        return False
    
    def get_hotkey(self, action_id: str) -> Optional[HotkeyConfig]:
        """Get a hotkey configuration by action ID."""
        return self.hotkeys.get(action_id)
    
    def update_hotkey(self, action_id: str, key_sequence: str) -> bool:
        """Update the key sequence for an existing hotkey."""
        if action_id in self.hotkeys:
            self.hotkeys[action_id].key_sequence = key_sequence
            return True
        return False


class HotkeyManager:
    """Manages configurable keyboard shortcuts for the UI."""
    
    def __init__(self):
        """Initialize the hotkey manager."""
        self.platform = platform.system().lower()
        self.shortcuts: List[QShortcut] = []
        self.profiles: Dict[str, HotkeyProfile] = {}
        self.active_profile: Optional[str] = None
        
        # Platform-specific modifier keys
        self.ctrl_key = "Cmd" if self.platform == "darwin" else "Ctrl"
        self.alt_key = "Option" if self.platform == "darwin" else "Alt"
        self.shift_key = "Shift"
        self.meta_key = "Cmd" if self.platform == "darwin" else "Win"
    
    def create_profile(self, name: str) -> HotkeyProfile:
        """Create a new hotkey profile."""
        profile = HotkeyProfile(name=name)
        self.profiles[name] = profile
        logger.debug(f"Created hotkey profile: {name}")
        return profile
    
    def get_profile(self, name: str) -> Optional[HotkeyProfile]:
        """Get a hotkey profile by name."""
        return self.profiles.get(name)
    
    def set_active_profile(self, name: str) -> bool:
        """Set the active hotkey profile."""
        if name in self.profiles:
            self.active_profile = name
            logger.debug(f"Set active hotkey profile: {name}")
            return True
        logger.warning(f"Profile not found: {name}")
        return False
    
    def get_active_profile(self) -> Optional[HotkeyProfile]:
        """Get the currently active hotkey profile."""
        if self.active_profile:
            return self.profiles.get(self.active_profile)
        return None
    
    def _normalize_key_sequence(self, key_sequence: str) -> str:
        """Normalize key sequence for the current platform."""
        # Replace generic modifiers with platform-specific ones
        sequence = key_sequence.replace("Ctrl", self.ctrl_key)
        sequence = sequence.replace("Alt", self.alt_key)
        return sequence
    
    def register_hotkey(self, widget: QWidget, action_id: str, 
                       key_sequence: str, callback: Callable,
                       description: str = "") -> bool:
        """Register a single hotkey on a widget."""
        if not ANKI_AVAILABLE or not widget:
            logger.warning("Cannot register hotkey: Anki not available or widget is None")
            return False
        
        try:
            normalized_sequence = self._normalize_key_sequence(key_sequence)
            shortcut = QShortcut(QKeySequence(normalized_sequence), widget)
            shortcut.activated.connect(callback)
            
            self.shortcuts.append(shortcut)
            logger.debug(f"Registered hotkey '{action_id}': {normalized_sequence} - {description}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to register hotkey '{action_id}' ({key_sequence}): {e}")
            return False
    
    def register_profile_hotkeys(self, widget: QWidget, 
                                profile_name: str) -> int:
        """Register all hotkeys from a profile on a widget."""
        profile = self.get_profile(profile_name)
        if not profile:
            logger.warning(f"Profile not found: {profile_name}")
            return 0
        
        success_count = 0
        for action_id, config in profile.hotkeys.items():
            if config.enabled:
                if self.register_hotkey(widget, action_id, config.key_sequence,
                                       config.callback, config.description):
                    success_count += 1
        
        logger.info(f"Registered {success_count}/{len(profile.hotkeys)} hotkeys from profile '{profile_name}'")
        return success_count
    
    def unregister_hotkey(self, action_id: str) -> bool:
        """Unregister a hotkey by action ID."""
        # Find and remove the shortcut
        for i, shortcut in enumerate(self.shortcuts):
            try:
                shortcut.setParent(None)
                shortcut.deleteLater()
                self.shortcuts.pop(i)
                logger.debug(f"Unregistered hotkey: {action_id}")
                return True
            except:
                pass
        return False
    
    def clear_all_hotkeys(self) -> None:
        """Clear all registered hotkeys."""
        for shortcut in self.shortcuts:
            try:
                shortcut.setParent(None)
                shortcut.deleteLater()
            except:
                pass
        
        self.shortcuts.clear()
        logger.debug("Cleared all hotkeys")
    
    def enable_hotkey(self, action_id: str, profile_name: str) -> bool:
        """Enable a hotkey in a profile."""
        profile = self.get_profile(profile_name)
        if profile and action_id in profile.hotkeys:
            profile.hotkeys[action_id].enabled = True
            logger.debug(f"Enabled hotkey '{action_id}' in profile '{profile_name}'")
            return True
        return False
    
    def disable_hotkey(self, action_id: str, profile_name: str) -> bool:
        """Disable a hotkey in a profile."""
        profile = self.get_profile(profile_name)
        if profile and action_id in profile.hotkeys:
            profile.hotkeys[action_id].enabled = False
            logger.debug(f"Disabled hotkey '{action_id}' in profile '{profile_name}'")
            return True
        return False
    
    def get_platform_info(self) -> Dict[str, str]:
        """Get platform-specific keyboard information."""
        return {
            "platform": self.platform,
            "ctrl_key": self.ctrl_key,
            "alt_key": self.alt_key,
            "shift_key": self.shift_key,
            "meta_key": self.meta_key
        }
    
    def list_profiles(self) -> List[str]:
        """List all available hotkey profiles."""
        return list(self.profiles.keys())
    
    def export_profile(self, profile_name: str) -> Dict:
        """Export a profile as a dictionary."""
        profile = self.get_profile(profile_name)
        if not profile:
            return {}
        
        return {
            "name": profile.name,
            "hotkeys": {
                action_id: {
                    "key_sequence": config.key_sequence,
                    "description": config.description,
                    "enabled": config.enabled
                }
                for action_id, config in profile.hotkeys.items()
            }
        }


# Global hotkey manager instance
_global_hotkey_manager = None


def get_hotkey_manager() -> HotkeyManager:
    """Get the global hotkey manager instance."""
    global _global_hotkey_manager
    if _global_hotkey_manager is None:
        _global_hotkey_manager = HotkeyManager()
    return _global_hotkey_manager


def create_default_profile() -> HotkeyProfile:
    """Create and return the default hotkey profile."""
    manager = get_hotkey_manager()
    profile = manager.create_profile("default")
    
    # Add default hotkeys
    default_hotkeys = {
        "search": ("Ctrl+S", "Search dictionary"),
        "search_collection": ("Ctrl+Shift+B", "Search collection"),
        "close_window": ("Ctrl+W", "Close dictionary window"),
        "escape": ("Esc", "Close/Cancel"),
        "focus_search": ("Ctrl+F", "Focus search bar"),
        "clear_search": ("Ctrl+L", "Clear search"),
        "refresh": ("Ctrl+R", "Refresh results"),
        "toggle_theme": ("Ctrl+T", "Toggle theme"),
        "settings": ("Ctrl+,", "Open settings"),
        "help": ("F1", "Show help"),
        "audio": ("Ctrl+A", "Play audio"),
        "images": ("Ctrl+I", "Search images"),
        "copy": ("Ctrl+C", "Copy definition"),
        "export": ("Ctrl+E", "Export to Anki"),
        "history": ("Ctrl+H", "Show history"),
        "conjugation": ("Ctrl+B", "Toggle conjugation"),
    }
    
    for action_id, (key_seq, description) in default_hotkeys.items():
        profile.add_hotkey(action_id, key_seq, lambda: None, description)
    
    manager.set_active_profile("default")
    logger.info("Created default hotkey profile")
    return profile
