# -*- coding: utf-8 -*-
"""
Tests for platform utility functions.
"""

import pytest
import sys
from src.utils.platform import (
    is_mac,
    is_win,
    is_lin,
    get_platform_name,
    get_platform_version,
)


class TestPlatformDetection:
    """Test platform detection functions."""
    
    def test_platform_detection_returns_bool(self):
        """Test that platform detection returns boolean."""
        assert isinstance(is_mac(), bool)
        assert isinstance(is_win(), bool)
        assert isinstance(is_lin(), bool)
    
    def test_only_one_platform_true(self):
        """Test that only one platform is detected as true."""
        platforms = [is_mac(), is_win(), is_lin()]
        true_count = sum(platforms)
        assert true_count == 1, "Exactly one platform should be detected"
    
    def test_current_platform_detected(self):
        """Test that current platform is correctly detected."""
        if sys.platform == "darwin":
            assert is_mac() == True
            assert is_win() == False
            assert is_lin() == False
        elif sys.platform == "win32":
            assert is_mac() == False
            assert is_win() == True
            assert is_lin() == False
        elif sys.platform.startswith("linux"):
            assert is_mac() == False
            assert is_win() == False
            assert is_lin() == True
    
    def test_get_platform_name(self):
        """Test getting platform name."""
        name = get_platform_name()
        assert isinstance(name, str)
        assert len(name) > 0
        assert name in ["Darwin", "Windows", "Linux"]
    
    def test_get_platform_version(self):
        """Test getting platform version."""
        version = get_platform_version()
        assert isinstance(version, str)
        assert len(version) > 0


class TestPlatformConsistency:
    """Test consistency of platform detection."""
    
    def test_multiple_calls_consistent(self):
        """Test that multiple calls return same result."""
        result1 = is_mac()
        result2 = is_mac()
        assert result1 == result2
        
        result1 = is_win()
        result2 = is_win()
        assert result1 == result2
        
        result1 = is_lin()
        result2 = is_lin()
        assert result1 == result2
