# -*- coding: utf-8 -*-
"""
Tests for UI base utilities.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
from src.ui.base import UIComponent, get_icon_path, load_stylesheet


class TestGetIconPath:
    """Tests for get_icon_path function."""
    
    def test_get_icon_path_day_theme(self, tmp_path):
        """Test getting icon path for day theme."""
        # Create test icon structure
        icon_dir = tmp_path / "icons" / "dictsvgs"
        icon_dir.mkdir(parents=True)
        (icon_dir / "search.svg").touch()
        
        result = get_icon_path(tmp_path, "search", "day")
        
        assert result == icon_dir / "search.svg"
        assert result.exists()
    
    def test_get_icon_path_night_theme(self, tmp_path):
        """Test getting icon path for night theme."""
        # Create test icon structure
        icon_dir = tmp_path / "icons" / "dictsvgs"
        icon_dir.mkdir(parents=True)
        (icon_dir / "search.svg").touch()
        (icon_dir / "searchnight.svg").touch()
        
        result = get_icon_path(tmp_path, "search", "night")
        
        assert result == icon_dir / "searchnight.svg"
        assert result.exists()
    
    def test_get_icon_path_fallback_to_default(self, tmp_path):
        """Test fallback to default icon when themed icon doesn't exist."""
        # Create test icon structure
        icon_dir = tmp_path / "icons" / "dictsvgs"
        icon_dir.mkdir(parents=True)
        (icon_dir / "search.svg").touch()
        
        result = get_icon_path(tmp_path, "search", "night")
        
        # Should fall back to day version
        assert result == icon_dir / "search.svg"
        assert result.exists()
    
    def test_get_icon_path_fallback_to_png(self, tmp_path):
        """Test fallback to PNG when SVG doesn't exist."""
        # Create test icon structure
        icon_dir = tmp_path / "icons"
        icon_dir.mkdir(parents=True)
        (icon_dir / "search.png").touch()
        
        result = get_icon_path(tmp_path, "search", "day")
        
        # Should fall back to PNG
        assert result == icon_dir / "search.png"


class TestLoadStylesheet:
    """Tests for load_stylesheet function."""
    
    def test_load_stylesheet_exists(self, tmp_path):
        """Test loading an existing stylesheet."""
        stylesheet_path = tmp_path / "style.css"
        stylesheet_content = "body { color: red; }"
        stylesheet_path.write_text(stylesheet_content, encoding='utf-8')
        
        result = load_stylesheet(tmp_path, "style.css")
        
        assert result == stylesheet_content
    
    def test_load_stylesheet_not_exists(self, tmp_path):
        """Test loading a non-existent stylesheet."""
        result = load_stylesheet(tmp_path, "nonexistent.css")
        
        assert result == ""


class TestUIComponent:
    """Tests for UIComponent base class."""
    
    def test_init(self, tmp_path):
        """Test UIComponent initialization."""
        mock_mw = Mock()
        
        component = UIComponent(mock_mw, tmp_path)
        
        assert component.mw == mock_mw
        assert component.addon_path == tmp_path
    
    def test_get_icon(self, tmp_path):
        """Test get_icon method."""
        mock_mw = Mock()
        icon_dir = tmp_path / "icons" / "dictsvgs"
        icon_dir.mkdir(parents=True)
        (icon_dir / "test.svg").touch()
        
        component = UIComponent(mock_mw, tmp_path)
        result = component.get_icon("test")
        
        assert result == icon_dir / "test.svg"
    
    def test_get_icon_with_theme(self, tmp_path):
        """Test get_icon method with theme override."""
        mock_mw = Mock()
        icon_dir = tmp_path / "icons" / "dictsvgs"
        icon_dir.mkdir(parents=True)
        (icon_dir / "test.svg").touch()
        (icon_dir / "testnight.svg").touch()
        
        component = UIComponent(mock_mw, tmp_path)
        result = component.get_icon("test", theme="night")
        
        assert result == icon_dir / "testnight.svg"
