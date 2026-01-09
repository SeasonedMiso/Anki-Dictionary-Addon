# -*- coding: utf-8 -*-
"""
Unit tests for the hotkey manager.

Tests configuration, profile management, and hotkey registration.
"""

import pytest
import platform
import sys
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Add src to path to avoid import issues
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly from the module to avoid circular imports
import importlib.util
spec = importlib.util.spec_from_file_location(
    "hotkey_manager",
    Path(__file__).parent.parent / "src" / "ui" / "hotkey_manager.py"
)
hotkey_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hotkey_module)

HotkeyManager = hotkey_module.HotkeyManager
HotkeyConfig = hotkey_module.HotkeyConfig
HotkeyProfile = hotkey_module.HotkeyProfile
get_hotkey_manager = hotkey_module.get_hotkey_manager
create_default_profile = hotkey_module.create_default_profile


class TestHotkeyConfig:
    """Test HotkeyConfig dataclass."""
    
    def test_hotkey_config_creation(self):
        """Test creating a hotkey configuration."""
        callback = Mock()
        config = HotkeyConfig(
            key_sequence="Ctrl+S",
            callback=callback,
            description="Search"
        )
        
        assert config.key_sequence == "Ctrl+S"
        assert config.callback == callback
        assert config.description == "Search"
        assert config.enabled is True
    
    def test_hotkey_config_disabled(self):
        """Test creating a disabled hotkey configuration."""
        config = HotkeyConfig(
            key_sequence="Ctrl+W",
            callback=Mock(),
            enabled=False
        )
        
        assert config.enabled is False


class TestHotkeyProfile:
    """Test HotkeyProfile class."""
    
    def test_profile_creation(self):
        """Test creating a hotkey profile."""
        profile = HotkeyProfile(name="test_profile")
        
        assert profile.name == "test_profile"
        assert len(profile.hotkeys) == 0
    
    def test_add_hotkey(self):
        """Test adding a hotkey to a profile."""
        profile = HotkeyProfile(name="test")
        callback = Mock()
        
        profile.add_hotkey("search", "Ctrl+S", callback, "Search")
        
        assert "search" in profile.hotkeys
        assert profile.hotkeys["search"].key_sequence == "Ctrl+S"
        assert profile.hotkeys["search"].description == "Search"
    
    def test_remove_hotkey(self):
        """Test removing a hotkey from a profile."""
        profile = HotkeyProfile(name="test")
        profile.add_hotkey("search", "Ctrl+S", Mock())
        
        result = profile.remove_hotkey("search")
        
        assert result is True
        assert "search" not in profile.hotkeys
    
    def test_remove_nonexistent_hotkey(self):
        """Test removing a hotkey that doesn't exist."""
        profile = HotkeyProfile(name="test")
        
        result = profile.remove_hotkey("nonexistent")
        
        assert result is False
    
    def test_get_hotkey(self):
        """Test getting a hotkey from a profile."""
        profile = HotkeyProfile(name="test")
        callback = Mock()
        profile.add_hotkey("search", "Ctrl+S", callback)
        
        config = profile.get_hotkey("search")
        
        assert config is not None
        assert config.key_sequence == "Ctrl+S"
    
    def test_get_nonexistent_hotkey(self):
        """Test getting a hotkey that doesn't exist."""
        profile = HotkeyProfile(name="test")
        
        config = profile.get_hotkey("nonexistent")
        
        assert config is None
    
    def test_update_hotkey(self):
        """Test updating a hotkey's key sequence."""
        profile = HotkeyProfile(name="test")
        profile.add_hotkey("search", "Ctrl+S", Mock())
        
        result = profile.update_hotkey("search", "Ctrl+Shift+S")
        
        assert result is True
        assert profile.hotkeys["search"].key_sequence == "Ctrl+Shift+S"
    
    def test_update_nonexistent_hotkey(self):
        """Test updating a hotkey that doesn't exist."""
        profile = HotkeyProfile(name="test")
        
        result = profile.update_hotkey("nonexistent", "Ctrl+S")
        
        assert result is False


class TestHotkeyManager:
    """Test HotkeyManager class."""
    
    def test_manager_creation(self):
        """Test creating a hotkey manager."""
        manager = HotkeyManager()
        
        assert manager.platform in ["darwin", "windows", "linux"]
        assert len(manager.shortcuts) == 0
        assert len(manager.profiles) == 0
    
    def test_platform_specific_keys(self):
        """Test platform-specific key mapping."""
        manager = HotkeyManager()
        
        if manager.platform == "darwin":
            assert manager.ctrl_key == "Cmd"
            assert manager.alt_key == "Option"
            assert manager.meta_key == "Cmd"
        else:
            assert manager.ctrl_key == "Ctrl"
            assert manager.alt_key == "Alt"
            assert manager.meta_key == "Win"
    
    def test_create_profile(self):
        """Test creating a profile."""
        manager = HotkeyManager()
        
        profile = manager.create_profile("test")
        
        assert profile.name == "test"
        assert "test" in manager.profiles
    
    def test_get_profile(self):
        """Test getting a profile."""
        manager = HotkeyManager()
        manager.create_profile("test")
        
        profile = manager.get_profile("test")
        
        assert profile is not None
        assert profile.name == "test"
    
    def test_get_nonexistent_profile(self):
        """Test getting a profile that doesn't exist."""
        manager = HotkeyManager()
        
        profile = manager.get_profile("nonexistent")
        
        assert profile is None
    
    def test_set_active_profile(self):
        """Test setting the active profile."""
        manager = HotkeyManager()
        manager.create_profile("test")
        
        result = manager.set_active_profile("test")
        
        assert result is True
        assert manager.active_profile == "test"
    
    def test_set_nonexistent_active_profile(self):
        """Test setting a nonexistent profile as active."""
        manager = HotkeyManager()
        
        result = manager.set_active_profile("nonexistent")
        
        assert result is False
        assert manager.active_profile is None
    
    def test_get_active_profile(self):
        """Test getting the active profile."""
        manager = HotkeyManager()
        manager.create_profile("test")
        manager.set_active_profile("test")
        
        profile = manager.get_active_profile()
        
        assert profile is not None
        assert profile.name == "test"
    
    def test_normalize_key_sequence(self):
        """Test key sequence normalization."""
        manager = HotkeyManager()
        
        normalized = manager._normalize_key_sequence("Ctrl+S")
        
        if manager.platform == "darwin":
            assert "Cmd" in normalized
        else:
            assert "Ctrl" in normalized
    
    def test_get_platform_info(self):
        """Test getting platform information."""
        manager = HotkeyManager()
        
        info = manager.get_platform_info()
        
        assert "platform" in info
        assert "ctrl_key" in info
        assert "alt_key" in info
        assert "shift_key" in info
        assert "meta_key" in info
    
    def test_list_profiles(self):
        """Test listing all profiles."""
        manager = HotkeyManager()
        manager.create_profile("profile1")
        manager.create_profile("profile2")
        
        profiles = manager.list_profiles()
        
        assert len(profiles) == 2
        assert "profile1" in profiles
        assert "profile2" in profiles
    
    def test_export_profile(self):
        """Test exporting a profile."""
        manager = HotkeyManager()
        profile = manager.create_profile("test")
        profile.add_hotkey("search", "Ctrl+S", Mock(), "Search")
        
        exported = manager.export_profile("test")
        
        assert exported["name"] == "test"
        assert "search" in exported["hotkeys"]
        assert exported["hotkeys"]["search"]["key_sequence"] == "Ctrl+S"
    
    def test_export_nonexistent_profile(self):
        """Test exporting a profile that doesn't exist."""
        manager = HotkeyManager()
        
        exported = manager.export_profile("nonexistent")
        
        assert exported == {}
    
    def test_enable_disable_hotkey(self):
        """Test enabling and disabling hotkeys."""
        manager = HotkeyManager()
        profile = manager.create_profile("test")
        profile.add_hotkey("search", "Ctrl+S", Mock())
        
        # Disable
        result = manager.disable_hotkey("search", "test")
        assert result is True
        assert profile.hotkeys["search"].enabled is False
        
        # Enable
        result = manager.enable_hotkey("search", "test")
        assert result is True
        assert profile.hotkeys["search"].enabled is True
    
    def test_enable_disable_nonexistent_hotkey(self):
        """Test enabling/disabling a hotkey that doesn't exist."""
        manager = HotkeyManager()
        manager.create_profile("test")
        
        result = manager.disable_hotkey("nonexistent", "test")
        assert result is False
        
        result = manager.enable_hotkey("nonexistent", "test")
        assert result is False


class TestGlobalHotkeyManager:
    """Test global hotkey manager functions."""
    
    def test_get_hotkey_manager_singleton(self):
        """Test that get_hotkey_manager returns a singleton."""
        manager1 = get_hotkey_manager()
        manager2 = get_hotkey_manager()
        
        assert manager1 is manager2
    
    def test_create_default_profile(self):
        """Test creating the default profile."""
        # Reset the global manager
        hotkey_module._global_hotkey_manager = None
        
        profile = create_default_profile()
        
        assert profile.name == "default"
        assert len(profile.hotkeys) > 0
        assert "search" in profile.hotkeys
        assert "close_window" in profile.hotkeys
        assert "escape" in profile.hotkeys
    
    def test_default_profile_hotkeys(self):
        """Test that default profile contains expected hotkeys."""
        # Reset the global manager
        hotkey_module._global_hotkey_manager = None
        
        profile = create_default_profile()
        
        expected_hotkeys = [
            "search", "search_collection", "close_window", "escape",
            "focus_search", "clear_search", "refresh", "toggle_theme",
            "settings", "help", "audio", "images", "copy", "export",
            "history", "conjugation"
        ]
        
        for hotkey in expected_hotkeys:
            assert hotkey in profile.hotkeys
            config = profile.hotkeys[hotkey]
            assert config.key_sequence
            assert config.description
