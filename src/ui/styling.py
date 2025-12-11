# -*- coding: utf-8 -*-
"""
Centralized Styling System for Modern UI Components.

This module provides a centralized theme management system that eliminates
hardcoded styles throughout the codebase and provides consistent theming
across all modern UI components.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ThemeColors:
    """Complete theme color configuration."""
    
    # Basic Colors
    background_color: str = "#0f0f0f"
    panel_color: str = "#1c1c1c"
    text_primary: str = "#e6e6e6"
    text_muted: str = "#9aa0ad"
    accent_color: str = "#4a9eff"
    border_color: str = "#2b2f36"
    
    # Status Colors
    success_color: str = "#22c55e"
    warning_color: str = "#fbbf24"
    error_color: str = "#ef4444"
    info_color: str = "#3b82f6"
    
    # Pitch Accent Colors (Japanese-specific)
    heiban_color: str = "#4a9eff"
    odaka_color: str = "#51cf66"
    nakadaka_color: str = "#ffd43b"
    atamadaka_color: str = "#ff6b6b"
    kifuku_color: str = "#9775fa"
    
    # Frequency Colors
    freq_very_common: str = "#4ade80"
    freq_common: str = "#60a5fa"
    freq_uncommon: str = "#fbbf24"
    freq_rare: str = "#fb923c"
    freq_very_rare: str = "#f87171"
    
    # Action Button Colors
    audio_color: str = "#4a9eff"
    image_color: str = "#50c878"
    copy_color: str = "#64748b"
    export_color: str = "#9b59b6"
    
    # Typography (configurable font sizes)
    base_font_size: int = 14          # Base font size in px
    font_scale_factor: float = 1.0    # Scale multiplier (0.8-2.0)
    
    # Layout Options
    border_radius: int = 8
    spacing: int = 12
    padding: int = 16
    show_borders: bool = True
    
    def get_font_size(self, size_type: str = "base") -> int:
        """Get scaled font size for different UI elements."""
        size_map = {
            "small": 0.85,      # 12px at base 14px
            "base": 1.0,        # 14px at base 14px  
            "medium": 1.14,     # 16px at base 14px
            "large": 1.43,      # 20px at base 14px
            "header": 1.71      # 24px at base 14px
        }
        multiplier = size_map.get(size_type, 1.0)
        return int(self.base_font_size * self.font_scale_factor * multiplier)


class ThemeManager:
    """Centralized theme management system with font size controls."""
    
    def __init__(self, initial_theme: Optional[ThemeColors] = None):
        """Initialize theme manager with optional initial theme."""
        self.current_theme = initial_theme or ThemeColors()
        self._observers = []
    
    def register_observer(self, callback):
        """Register a callback to be notified of theme changes."""
        self._observers.append(callback)
    
    def unregister_observer(self, callback):
        """Unregister a theme change observer."""
        if callback in self._observers:
            self._observers.remove(callback)
    
    def update_theme(self, new_theme: ThemeColors):
        """Update the current theme and notify all observers."""
        self.current_theme = new_theme
        self._notify_observers()
    
    def increase_font_size(self):
        """Increase font scale factor (Ctrl/Cmd + Plus)."""
        new_scale = min(2.0, self.current_theme.font_scale_factor + 0.1)
        if new_scale != self.current_theme.font_scale_factor:
            self.current_theme.font_scale_factor = new_scale
            self._notify_observers()
            logger.info(f"Font size increased to {new_scale:.1f}x")
    
    def decrease_font_size(self):
        """Decrease font scale factor (Ctrl/Cmd + Minus)."""
        new_scale = max(0.8, self.current_theme.font_scale_factor - 0.1)
        if new_scale != self.current_theme.font_scale_factor:
            self.current_theme.font_scale_factor = new_scale
            self._notify_observers()
            logger.info(f"Font size decreased to {new_scale:.1f}x")
    
    def reset_font_size(self):
        """Reset font scale to default (Ctrl/Cmd + 0)."""
        if self.current_theme.font_scale_factor != 1.0:
            self.current_theme.font_scale_factor = 1.0
            self._notify_observers()
            logger.info("Font size reset to default")
    
    def _notify_observers(self):
        """Notify all registered observers of theme changes."""
        for callback in self._observers:
            try:
                callback(self.current_theme)
            except Exception as e:
                logger.warning(f"Error notifying theme observer: {e}")
    
    def get_theme_dict(self) -> Dict[str, Any]:
        """Get current theme as dictionary for backward compatibility."""
        return {
            'background_color': self.current_theme.background_color,
            'panel_color': self.current_theme.panel_color,
            'text_primary': self.current_theme.text_primary,
            'text_muted': self.current_theme.text_muted,
            'accent_color': self.current_theme.accent_color,
            'border_color': self.current_theme.border_color,
            'success_color': self.current_theme.success_color,
            'warning_color': self.current_theme.warning_color,
            'error_color': self.current_theme.error_color,
            'info_color': self.current_theme.info_color,
            'heiban_color': self.current_theme.heiban_color,
            'odaka_color': self.current_theme.odaka_color,
            'nakadaka_color': self.current_theme.nakadaka_color,
            'atamadaka_color': self.current_theme.atamadaka_color,
            'kifuku_color': self.current_theme.kifuku_color,
            'base_font_size': self.current_theme.base_font_size,
            'font_scale_factor': self.current_theme.font_scale_factor,
            'border_radius': self.current_theme.border_radius,
            'spacing': self.current_theme.spacing,
            'padding': self.current_theme.padding,
            'show_borders': self.current_theme.show_borders
        }


class StyleGenerator:
    """Generates consistent CSS styles for UI components."""
    
    def __init__(self, theme: ThemeColors):
        """Initialize style generator with theme."""
        self.theme = theme
    
    def adjust_color_brightness(self, hex_color: str, factor: float) -> str:
        """
        Adjust the brightness of a hex color.
        
        Args:
            hex_color: Hex color string (e.g., "#1c1c1c")
            factor: Brightness factor (>1 = brighter, <1 = darker)
            
        Returns:
            Adjusted hex color string
        """
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Adjust brightness
            r = min(255, max(0, int(r * factor)))
            g = min(255, max(0, int(g * factor)))
            b = min(255, max(0, int(b * factor)))
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            # Return original color if parsing fails
            return hex_color
    
    def button_style(self, 
                    bg_color: Optional[str] = None,
                    text_color: str = "white",
                    border_radius: Optional[int] = None,
                    padding: str = "10px 20px",
                    size_type: str = "base",
                    font_weight: str = "bold") -> str:
        """Generate button style with responsive font sizing."""
        bg = bg_color or self.theme.panel_color
        radius = border_radius or self.theme.border_radius
        font_size = self.theme.get_font_size(size_type)
        
        hover_bg = self.adjust_color_brightness(bg, 1.2)
        pressed_bg = self.adjust_color_brightness(bg, 0.8)
        
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: 1px solid {self.theme.border_color};
                border-radius: {radius}px;
                padding: {padding};
                font-size: {font_size}px;
                font-weight: {font_weight};
                min-width: 60px;
                min-height: 32px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
            }}
        """
    
    def input_style(self, 
                   bg_color: Optional[str] = None,
                   border_radius: Optional[int] = None,
                   padding: str = "8px 12px",
                   size_type: str = "base") -> str:
        """Generate input field style with responsive font sizing."""
        bg = bg_color or self.theme.panel_color
        radius = border_radius or self.theme.border_radius
        font_size = self.theme.get_font_size(size_type)
        
        return f"""
            QLineEdit {{
                background-color: {bg};
                color: {self.theme.text_primary};
                border: 1px solid {self.theme.border_color};
                border-radius: {radius}px;
                padding: {padding};
                font-size: {font_size}px;
            }}
            QLineEdit:focus {{
                border-color: {self.theme.accent_color};
            }}
            QLineEdit::placeholder {{
                color: {self.theme.text_muted};
            }}
        """
    
    def label_style(self,
                   color: Optional[str] = None,
                   size_type: str = "base",
                   font_weight: str = "normal") -> str:
        """Generate label style with responsive font sizing."""
        text_color = color or self.theme.text_primary
        font_size = self.theme.get_font_size(size_type)
        
        return f"""
            QLabel {{
                color: {text_color};
                font-size: {font_size}px;
                font-weight: {font_weight};
                background-color: transparent;
            }}
        """
    
    def panel_style(self,
                   bg_color: Optional[str] = None,
                   border_radius: Optional[int] = None,
                   show_border: bool = True) -> str:
        """Generate panel/frame style."""
        bg = bg_color or self.theme.panel_color
        radius = border_radius or self.theme.border_radius
        border = f"1px solid {self.theme.border_color}" if show_border else "none"
        
        return f"""
            QFrame {{
                background-color: {bg};
                border: {border};
                border-radius: {radius}px;
            }}
        """
    
    def dropdown_style(self) -> str:
        """Generate dropdown/combobox style with proper bounds."""
        hover_bg = self.adjust_color_brightness(self.theme.panel_color, 1.2)
        return f"""
QComboBox {{
    background-color: {self.theme.panel_color};
    border: 1px solid {self.theme.border_color};
    border-radius: {self.theme.border_radius}px;
    padding: 4px 12px;
    padding-right: 30px;
    color: {self.theme.text_primary};
    font-size: {self.theme.get_font_size('small')}px;
    min-height: 36px;
    max-height: 36px;
    max-width: 400px;  /* Prevent excessive width */
}}
QComboBox:hover {{
    border-color: {self.adjust_color_brightness(self.theme.border_color, 1.5)};
    background-color: {hover_bg};
}}
QComboBox:focus {{
    border-color: {self.theme.accent_color};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border: none;
    background: transparent;
}}
QComboBox::down-arrow {{
    image: none;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {self.theme.text_muted};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {self.theme.panel_color};
    border: 1px solid {self.theme.border_color};
    border-radius: {self.theme.border_radius}px;
    selection-background-color: {self.theme.accent_color};
    selection-color: white;
    color: {self.theme.text_primary};
    outline: none;
    /* Prevent dropdown from being too wide */
    min-width: 200px;
    max-width: 400px;
}}
QComboBox QAbstractItemView::item {{
    padding: 8px 12px;
    border: none;
    background-color: {self.theme.panel_color};
    color: {self.theme.text_primary};
    min-height: 20px;
    /* Ensure text doesn't overflow */
    text-overflow: ellipsis;
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: {hover_bg};
}}
QComboBox QAbstractItemView::item:selected {{
    background-color: {self.theme.accent_color};
    color: white;
}}
"""
    
    def action_button_style(self, action_type: str) -> str:
        """Generate action button style for specific actions."""
        color_map = {
            'audio': self.theme.audio_color,
            'image': self.theme.image_color,
            'copy': self.theme.copy_color,
            'export': self.theme.export_color,
            'success': self.theme.success_color,
            'warning': self.theme.warning_color,
            'error': self.theme.error_color,
            'info': self.theme.info_color
        }
        
        bg_color = color_map.get(action_type, self.theme.accent_color)
        hover_bg = self.adjust_color_brightness(bg_color, 1.2)
        pressed_bg = self.adjust_color_brightness(bg_color, 0.8)
        font_size = self.theme.get_font_size("small")
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 4px 8px;
                font-size: {font_size}px;
                font-weight: bold;
                min-width: 24px;
                min-height: 24px;
                max-width: 24px;
                max-height: 24px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
            }}
        """
    
    def compact_icon_button_style(self, action_type: str) -> str:
        """Generate very compact icon button style for small header buttons."""
        color_map = {
            'audio': self.theme.audio_color,
            'image': self.theme.image_color,
            'copy': self.theme.copy_color,
            'export': self.theme.export_color
        }
        
        bg_color = color_map.get(action_type, self.theme.accent_color)
        hover_bg = self.adjust_color_brightness(bg_color, 1.2)
        pressed_bg = self.adjust_color_brightness(bg_color, 0.8)
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 2px;
                font-size: 8px;
                min-width: 20px;
                min-height: 20px;
                max-width: 24px;
                max-height: 24px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
            }}
        """
    
    def frequency_badge_style(self, frequency: int) -> str:
        """Generate frequency badge style based on frequency value."""
        if frequency <= 500:
            bg_color = self.theme.freq_very_common
        elif frequency <= 1500:
            bg_color = self.theme.freq_common
        elif frequency <= 5000:
            bg_color = self.theme.freq_uncommon
        elif frequency <= 15000:
            bg_color = self.theme.freq_rare
        else:
            bg_color = self.theme.freq_very_rare
        
        return f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 2px 12px;
                font-size: 11px;
                font-weight: bold;
                min-width: 60px;
                min-height: 24px;
                max-height: 24px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """
    
    def pitch_accent_style(self, pitch_type: str) -> str:
        """Generate pitch accent label style."""
        color_map = {
            'heiban': self.theme.heiban_color,
            'odaka': self.theme.odaka_color,
            'nakadaka': self.theme.nakadaka_color,
            'atamadaka': self.theme.atamadaka_color,
            'kifuku': self.theme.kifuku_color
        }
        
        color = color_map.get(pitch_type, self.theme.text_muted)
        
        return f"""
            QLabel {{
                font-size: 11px;
                color: {color};
                font-weight: bold;
                background-color: transparent;
                padding: 2px 4px;
                border-radius: 3px;
            }}
        """


# Predefined theme presets
THEME_PRESETS = {
    "dark": ThemeColors(
        background_color="#0f0f0f",
        panel_color="#1c1c1c",
        text_primary="#e6e6e6",
        text_muted="#9aa0ad",
        border_color="#2b2f36",
        accent_color="#4a9eff",
        success_color="#22c55e",
        warning_color="#fbbf24",
        error_color="#ef4444",
        info_color="#3b82f6",
        heiban_color="#4a9eff",
        odaka_color="#51cf66",
        nakadaka_color="#ffd43b",
        atamadaka_color="#ff6b6b",
        kifuku_color="#9775fa",
        freq_very_common="#4ade80",
        freq_common="#60a5fa",
        freq_uncommon="#fbbf24",
        freq_rare="#fb923c",
        freq_very_rare="#f87171",
        audio_color="#4a9eff",
        image_color="#50c878",
        copy_color="#64748b",
        export_color="#9b59b6"
    ),
    "light": ThemeColors(
        background_color="#ffffff",
        panel_color="#f5f5f5",
        text_primary="#1a1a1a",
        text_muted="#666666",
        border_color="#d0d0d0",
        accent_color="#0066cc",
        success_color="#2b8a3e",
        warning_color="#e67700",
        error_color="#c92a2a",
        info_color="#0066cc",
        heiban_color="#0066cc",
        odaka_color="#2b8a3e",
        nakadaka_color="#e67700",
        atamadaka_color="#c92a2a",
        kifuku_color="#7048e8",
        freq_very_common="#2b8a3e",
        freq_common="#0066cc",
        freq_uncommon="#e67700",
        freq_rare="#d9480f",
        freq_very_rare="#c92a2a",
        audio_color="#0066cc",
        image_color="#2b8a3e",
        copy_color="#666666",
        export_color="#7048e8"
    ),
    "blue": ThemeColors(
        background_color="#0a0e1a",
        panel_color="#1a1f2e",
        text_primary="#e1e8f0",
        text_muted="#8a9bb8",
        border_color="#2a3441",
        accent_color="#3a7afe",
        success_color="#22c55e",
        warning_color="#fbbf24",
        error_color="#ef4444",
        info_color="#3b82f6",
        heiban_color="#3a7afe",
        odaka_color="#51cf66",
        nakadaka_color="#ffd43b",
        atamadaka_color="#ff6b6b",
        kifuku_color="#9775fa",
        freq_very_common="#4ade80",
        freq_common="#60a5fa",
        freq_uncommon="#fbbf24",
        freq_rare="#fb923c",
        freq_very_rare="#f87171",
        audio_color="#3a7afe",
        image_color="#50c878",
        copy_color="#64748b",
        export_color="#9b59b6"
    )
}


# Global theme manager instance
_global_theme_manager = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    global _global_theme_manager
    if _global_theme_manager is None:
        _global_theme_manager = ThemeManager()
    return _global_theme_manager


def apply_theme_to_widget(widget, theme: ThemeColors):
    """Apply theme to a widget if it has update_theme method."""
    if hasattr(widget, 'update_theme'):
        try:
            widget.update_theme(theme)
        except Exception as e:
            logger.warning(f"Failed to apply theme to {widget.__class__.__name__}: {e}")


# Font shortcuts moved to keyboard.py module