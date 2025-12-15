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
    
    def __init__(self, initial_theme: Optional[ThemeColors] = None, config_path: Optional[str] = None):
        """Initialize theme manager with optional initial theme and config path."""
        self.current_theme = initial_theme or ThemeColors()
        self._observers = []
        self.config_path = config_path
    
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
    
    def save_theme_preference(self, theme_name: str):
        """Save the current theme preference to config."""
        if not self.config_path:
            return
        
        try:
            import json
            from pathlib import Path
            
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                config['currentTheme'] = theme_name
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=4)
                
                logger.info(f"Saved theme preference: {theme_name}")
        except Exception as e:
            logger.warning(f"Failed to save theme preference: {e}")
    
    def load_theme_preference(self) -> Optional[str]:
        """Load the saved theme preference from config."""
        if not self.config_path:
            return None
        
        try:
            import json
            from pathlib import Path
            
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                theme_name = config.get('currentTheme')
                if theme_name:
                    logger.info(f"Loaded theme preference: {theme_name}")
                    return theme_name
        except Exception as e:
            logger.warning(f"Failed to load theme preference: {e}")
        
        return None
    
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
    
    def _ensure_themes_directory(self):
        """Ensure user_files/themes directory exists."""
        from pathlib import Path
        themes_dir = Path(__file__).parent.parent.parent / "user_files" / "themes"
        themes_dir.mkdir(parents=True, exist_ok=True)
        return themes_dir
    
    def load_user_themes(self) -> Dict[str, ThemeColors]:
        """Load user-created themes from user_themes.json."""
        try:
            import json
            from pathlib import Path
            
            themes_dir = self._ensure_themes_directory()
            user_themes_file = themes_dir / "user_themes.json"
            
            if not user_themes_file.exists():
                return {}
            
            with open(user_themes_file, 'r') as f:
                data = json.load(f)
            
            themes = {}
            for theme_name, theme_data in data.get('themes', {}).items():
                try:
                    colors = theme_data.get('colors', {})
                    # Convert numeric strings back to numbers
                    if 'base_font_size' in colors and isinstance(colors['base_font_size'], str):
                        colors['base_font_size'] = int(colors['base_font_size'])
                    if 'font_scale_factor' in colors and isinstance(colors['font_scale_factor'], str):
                        colors['font_scale_factor'] = float(colors['font_scale_factor'])
                    if 'border_radius' in colors and isinstance(colors['border_radius'], str):
                        colors['border_radius'] = int(colors['border_radius'])
                    if 'spacing' in colors and isinstance(colors['spacing'], str):
                        colors['spacing'] = int(colors['spacing'])
                    if 'padding' in colors and isinstance(colors['padding'], str):
                        colors['padding'] = int(colors['padding'])
                    if 'show_borders' in colors and isinstance(colors['show_borders'], str):
                        colors['show_borders'] = colors['show_borders'].lower() == 'true'
                    
                    themes[theme_name] = ThemeColors(**colors)
                except Exception as e:
                    logger.warning(f"Failed to load theme {theme_name}: {e}")
            
            return themes
        except Exception as e:
            logger.warning(f"Failed to load user themes: {e}")
            return {}
    
    def save_user_theme(self, name: str, theme: ThemeColors) -> bool:
        """Save a user-created theme."""
        try:
            import json
            from datetime import datetime
            
            if not name or not isinstance(name, str):
                logger.warning("Invalid theme name")
                return False
            
            themes_dir = self._ensure_themes_directory()
            user_themes_file = themes_dir / "user_themes.json"
            
            # Load existing themes
            if user_themes_file.exists():
                with open(user_themes_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {'themes': {}}
            
            # Add/update theme
            data['themes'][name] = {
                'name': name,
                'created': datetime.now().isoformat(),
                'modified': datetime.now().isoformat(),
                'colors': self._theme_to_dict(theme)
            }
            
            # Write back
            with open(user_themes_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved user theme: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save user theme: {e}")
            return False
    
    def delete_user_theme(self, name: str) -> bool:
        """Delete a user-created theme."""
        try:
            import json
            
            if self.is_preset_theme(name):
                logger.warning(f"Cannot delete preset theme: {name}")
                return False
            
            themes_dir = self._ensure_themes_directory()
            user_themes_file = themes_dir / "user_themes.json"
            
            if not user_themes_file.exists():
                return False
            
            with open(user_themes_file, 'r') as f:
                data = json.load(f)
            
            if name in data.get('themes', {}):
                del data['themes'][name]
                
                with open(user_themes_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Deleted user theme: {name}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to delete user theme: {e}")
            return False
    
    def export_theme(self, theme_name: str, file_path: str) -> bool:
        """Export a theme to a JSON file."""
        try:
            import json
            from pathlib import Path
            from datetime import datetime
            
            # Get theme
            all_themes = self.get_all_themes()
            if theme_name not in all_themes:
                logger.warning(f"Theme not found: {theme_name}")
                return False
            
            theme = all_themes[theme_name]
            
            # Create export data
            export_data = {
                'metadata': {
                    'name': theme_name,
                    'version': '1.0',
                    'created': datetime.now().isoformat(),
                    'description': f'Theme: {theme_name}'
                },
                'colors': self._theme_to_dict(theme)
            }
            
            # Write to file
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported theme to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export theme: {e}")
            return False
    
    def import_theme(self, file_path: str, import_name: str = None) -> tuple:
        """Import a theme from a JSON file. Returns (success, ThemeColors)."""
        try:
            import json
            from pathlib import Path
            
            if not Path(file_path).exists():
                logger.warning(f"Theme file not found: {file_path}")
                return (False, None)
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Validate structure
            if 'colors' not in data:
                logger.warning("Invalid theme file: missing 'colors' field")
                return (False, None)
            
            # Create ThemeColors from imported data
            colors = data['colors']
            
            # Convert numeric strings back to numbers
            if 'base_font_size' in colors and isinstance(colors['base_font_size'], str):
                colors['base_font_size'] = int(colors['base_font_size'])
            if 'font_scale_factor' in colors and isinstance(colors['font_scale_factor'], str):
                colors['font_scale_factor'] = float(colors['font_scale_factor'])
            if 'border_radius' in colors and isinstance(colors['border_radius'], str):
                colors['border_radius'] = int(colors['border_radius'])
            if 'spacing' in colors and isinstance(colors['spacing'], str):
                colors['spacing'] = int(colors['spacing'])
            if 'padding' in colors and isinstance(colors['padding'], str):
                colors['padding'] = int(colors['padding'])
            if 'show_borders' in colors and isinstance(colors['show_borders'], str):
                colors['show_borders'] = colors['show_borders'].lower() == 'true'
            
            theme = ThemeColors(**colors)
            
            logger.info(f"Imported theme from: {file_path}")
            return (True, theme)
        except Exception as e:
            logger.error(f"Failed to import theme: {e}")
            return (False, None)
    
    def validate_theme_file(self, file_path: str) -> bool:
        """Validate a theme file format."""
        try:
            import json
            from pathlib import Path
            
            if not Path(file_path).exists():
                return False
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check required fields
            if 'colors' not in data:
                return False
            
            # Try to create ThemeColors to validate all fields
            ThemeColors(**data['colors'])
            return True
        except Exception as e:
            logger.warning(f"Theme file validation failed: {e}")
            return False
    
    def get_all_themes(self) -> Dict[str, ThemeColors]:
        """Get all available themes (presets + user themes)."""
        all_themes = {}
        
        # Add presets
        all_themes.update(THEME_PRESETS)
        
        # Add user themes
        all_themes.update(self.load_user_themes())
        
        return all_themes
    
    def is_preset_theme(self, name: str) -> bool:
        """Check if theme is a built-in preset."""
        return name in THEME_PRESETS
    
    def is_user_theme(self, name: str) -> bool:
        """Check if theme is user-created."""
        user_themes = self.load_user_themes()
        return name in user_themes
    
    def theme_exists(self, name: str) -> bool:
        """Check if theme exists (preset or user)."""
        return name in self.get_all_themes()
    
    def _theme_to_dict(self, theme: ThemeColors) -> Dict[str, Any]:
        """Convert ThemeColors to dictionary."""
        return {
            'background_color': theme.background_color,
            'panel_color': theme.panel_color,
            'text_primary': theme.text_primary,
            'text_muted': theme.text_muted,
            'accent_color': theme.accent_color,
            'border_color': theme.border_color,
            'success_color': theme.success_color,
            'warning_color': theme.warning_color,
            'error_color': theme.error_color,
            'info_color': theme.info_color,
            'heiban_color': theme.heiban_color,
            'odaka_color': theme.odaka_color,
            'nakadaka_color': theme.nakadaka_color,
            'atamadaka_color': theme.atamadaka_color,
            'kifuku_color': theme.kifuku_color,
            'freq_very_common': theme.freq_very_common,
            'freq_common': theme.freq_common,
            'freq_uncommon': theme.freq_uncommon,
            'freq_rare': theme.freq_rare,
            'freq_very_rare': theme.freq_very_rare,
            'audio_color': theme.audio_color,
            'image_color': theme.image_color,
            'copy_color': theme.copy_color,
            'export_color': theme.export_color,
            'base_font_size': theme.base_font_size,
            'font_scale_factor': theme.font_scale_factor,
            'border_radius': theme.border_radius,
            'spacing': theme.spacing,
            'padding': theme.padding,
            'show_borders': theme.show_borders
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


def create_theme_from_base(base_theme: ThemeColors, overrides: Dict[str, Any]) -> ThemeColors:
    """
    Create a new theme by overriding specific colors in a base theme.
    
    Args:
        base_theme: Base theme to start from
        overrides: Dictionary of color overrides
        
    Returns:
        New ThemeColors instance with overrides applied
    """
    # Convert base theme to dict
    theme_dict = {}
    for field in base_theme.__dataclass_fields__:
        theme_dict[field] = getattr(base_theme, field)
    
    # Apply overrides
    theme_dict.update(overrides)
    
    # Create new theme
    return ThemeColors(**theme_dict)


def interpolate_colors(color1: str, color2: str, factor: float) -> str:
    """
    Interpolate between two hex colors.
    
    Args:
        color1: First hex color (e.g., "#ff0000")
        color2: Second hex color (e.g., "#0000ff")
        factor: Interpolation factor (0.0 = color1, 1.0 = color2)
        
    Returns:
        Interpolated hex color
    """
    try:
        # Remove # if present
        color1 = color1.lstrip('#')
        color2 = color2.lstrip('#')
        
        # Convert to RGB
        r1, g1, b1 = int(color1[0:2], 16), int(color1[2:4], 16), int(color1[4:6], 16)
        r2, g2, b2 = int(color2[0:2], 16), int(color2[2:4], 16), int(color2[4:6], 16)
        
        # Interpolate
        factor = max(0.0, min(1.0, factor))  # Clamp to [0, 1]
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, IndexError):
        return color1  # Return first color if interpolation fails