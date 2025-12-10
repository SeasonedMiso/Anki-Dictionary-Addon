# -*- coding: utf-8 -*-
"""
Base UI utilities and common functionality for UI components.

This module provides common utilities, base classes, and helper functions
that are shared across multiple UI components.
"""

from typing import Optional, Any
from pathlib import Path


def get_icon_path(addon_path: Path, icon_name: str, theme: str = "day") -> Path:
    """
    Get the full path to an icon file.
    
    Args:
        addon_path: Path to the addon directory
        icon_name: Name of the icon (without extension)
        theme: Theme name ("day" or "night")
        
    Returns:
        Path to the icon file
    """
    icon_dir = addon_path / "icons" / "dictsvgs"
    
    # Try theme-specific icon first
    if theme == "night":
        themed_icon = icon_dir / f"{icon_name}night.svg"
        if themed_icon.exists():
            return themed_icon
    
    # Fall back to default icon
    default_icon = icon_dir / f"{icon_name}.svg"
    if default_icon.exists():
        return default_icon
    
    # Fall back to PNG if SVG doesn't exist
    png_icon = addon_path / "icons" / f"{icon_name}.png"
    return png_icon


def load_stylesheet(addon_path: Path, stylesheet_name: str) -> str:
    """
    Load a CSS stylesheet file.
    
    Args:
        addon_path: Path to the addon directory
        stylesheet_name: Name of the stylesheet file
        
    Returns:
        Stylesheet content as string
    """
    stylesheet_path = addon_path / stylesheet_name
    if stylesheet_path.exists():
        return stylesheet_path.read_text(encoding='utf-8')
    return ""


class UIComponent:
    """
    Base class for UI components.
    
    Provides common functionality for UI components including
    reference to main window and addon path.
    """
    
    def __init__(self, mw: Any, addon_path: Path):
        """
        Initialize UI component.
        
        Args:
            mw: Anki main window
            addon_path: Path to addon directory
        """
        self.mw = mw
        self.addon_path = addon_path
    
    def get_icon(self, icon_name: str, theme: Optional[str] = None) -> Path:
        """
        Get icon path for this component.
        
        Args:
            icon_name: Name of the icon
            theme: Optional theme override
            
        Returns:
            Path to icon file
        """
        if theme is None:
            # Could get theme from config here
            theme = "day"
        return get_icon_path(self.addon_path, icon_name, theme)
