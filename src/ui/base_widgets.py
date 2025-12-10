# -*- coding: utf-8 -*-
"""
Base Themed Widgets.

This module provides fundamental, reusable UI building blocks that use the
centralized styling system. These are generic widgets that can be used
across any part of the application.

WIDGETS PROVIDED:
- ThemedWidget: Base class for theme-aware widgets
- ThemedButton: Styled button with theme support
- ThemedLabel: Styled label with different types (default, muted, header, error, success)
- ThemedLineEdit: Styled input field with theme support
- ThemedFrame: Styled panel/container with optional borders
- ActionButton: Button with icon, feedback, and action-specific styling
- CopyButton: Specialized button for clipboard operations
- FrequencyBadge: Color-coded frequency indicator button
- PitchAccentLabel: Japanese pitch accent display with color coding
- StatusMessage: Auto-hiding status messages with type-based styling
- ValidationInput: Input field with built-in validation and error display
"""

from typing import Optional, Callable, Dict, Any
import logging

try:
    from aqt.qt import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QLineEdit, QFrame, pyqtSignal, Qt, QTimer, QApplication
    )
    ANKI_AVAILABLE = True
except ImportError:
    # Mock classes for testing - define minimal mocks
    ANKI_AVAILABLE = False
    
    class QWidget: pass
    class QVBoxLayout: pass
    class QHBoxLayout: pass
    class QLabel: pass
    class QPushButton: pass
    class QLineEdit: pass
    class QFrame: pass
    class QApplication: pass
    class QTimer: pass
    class pyqtSignal:
        def __init__(self, *args): pass
    class Qt: pass

from .styling import ThemeColors, StyleGenerator, get_theme_manager

logger = logging.getLogger(__name__)


class ThemedWidget(QWidget):
    """Base class for widgets that support theming."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.theme_manager = get_theme_manager()
        self.style_generator = StyleGenerator(self.theme_manager.current_theme)
        self.theme_manager.register_observer(self._on_theme_changed)
    
    def _on_theme_changed(self, new_theme: ThemeColors):
        self.style_generator = StyleGenerator(new_theme)
        self.update_theme(new_theme)
    
    def update_theme(self, theme: ThemeColors):
        """Override in subclasses to handle theme updates."""
        pass
    
    def closeEvent(self, event):
        self.theme_manager.unregister_observer(self._on_theme_changed)
        super().closeEvent(event)


class ThemedButton(QPushButton):
    """Themed button with consistent styling."""
    
    def __init__(self, 
                 text: str = "",
                 button_type: str = "default",
                 parent: Optional[QWidget] = None):
        """
        Initialize themed button.
        
        Args:
            text: Button text
            button_type: Button type (default, primary, success, warning, error, audio, image, copy, export)
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        self.button_type = button_type
        self.theme_manager = get_theme_manager()
        self.style_generator = StyleGenerator(self.theme_manager.current_theme)
        
        # Register for theme updates
        self.theme_manager.register_observer(self._on_theme_changed)
        
        self._apply_styling()
    
    def _on_theme_changed(self, new_theme: ThemeColors):
        """Handle theme changes."""
        self.style_generator = StyleGenerator(new_theme)
        self.update_theme(new_theme)
    
    def _apply_styling(self):
        """Apply button styling based on type."""
        if self.button_type == "primary":
            style = self.style_generator.button_style(
                bg_color=self.style_generator.theme.accent_color
            )
        elif self.button_type in ["success", "warning", "error", "audio", "image", "copy", "export"]:
            style = self.style_generator.action_button_style(self.button_type)
        else:
            style = self.style_generator.button_style()
        
        self.setStyleSheet(style)
    
    def update_theme(self, theme: ThemeColors):
        """Update button styling with new theme."""
        self._apply_styling()
    
    def closeEvent(self, event):
        """Clean up theme observer on close."""
        self.theme_manager.unregister_observer(self._on_theme_changed)
        super().closeEvent(event)


class ThemedLabel(QLabel):
    """Themed label with consistent styling."""
    
    def __init__(self, 
                 text: str = "",
                 label_type: str = "default",
                 parent: Optional[QWidget] = None):
        """
        Initialize themed label.
        
        Args:
            text: Label text
            label_type: Label type (default, muted, header, error, success)
            parent: Parent widget
        """
        super().__init__(text, parent)
        
        self.label_type = label_type
        self.theme_manager = get_theme_manager()
        self.style_generator = StyleGenerator(self.theme_manager.current_theme)
        
        # Register for theme updates
        self.theme_manager.register_observer(self._on_theme_changed)
        
        self._apply_styling()
    
    def _on_theme_changed(self, new_theme: ThemeColors):
        """Handle theme changes."""
        self.style_generator = StyleGenerator(new_theme)
        self.update_theme(new_theme)
    
    def _apply_styling(self):
        """Apply label styling based on type."""
        if self.label_type == "muted":
            style = self.style_generator.label_style(
                color=self.style_generator.theme.text_muted,
                size_type="small"
            )
        elif self.label_type == "header":
            style = self.style_generator.label_style(
                size_type="medium",
                font_weight="bold"
            )
        elif self.label_type == "error":
            style = self.style_generator.label_style(
                color=self.style_generator.theme.error_color
            )
        elif self.label_type == "success":
            style = self.style_generator.label_style(
                color=self.style_generator.theme.success_color
            )
        else:
            style = self.style_generator.label_style()
        
        self.setStyleSheet(style)
    
    def update_theme(self, theme: ThemeColors):
        """Update label styling with new theme."""
        self._apply_styling()
    
    def closeEvent(self, event):
        """Clean up theme observer on close."""
        self.theme_manager.unregister_observer(self._on_theme_changed)
        super().closeEvent(event)


class ThemedLineEdit(QLineEdit):
    """Themed line edit with consistent styling."""
    
    def __init__(self, 
                 placeholder: str = "",
                 parent: Optional[QWidget] = None):
        """
        Initialize themed line edit.
        
        Args:
            placeholder: Placeholder text
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.theme_manager = get_theme_manager()
        self.style_generator = StyleGenerator(self.theme_manager.current_theme)
        
        # Register for theme updates
        self.theme_manager.register_observer(self._on_theme_changed)
        
        if placeholder:
            self.setPlaceholderText(placeholder)
        
        self._apply_styling()
    
    def _on_theme_changed(self, new_theme: ThemeColors):
        """Handle theme changes."""
        self.style_generator = StyleGenerator(new_theme)
        self.update_theme(new_theme)
    
    def _apply_styling(self):
        """Apply input styling."""
        style = self.style_generator.input_style()
        self.setStyleSheet(style)
    
    def update_theme(self, theme: ThemeColors):
        """Update input styling with new theme."""
        self._apply_styling()
    
    def closeEvent(self, event):
        """Clean up theme observer on close."""
        self.theme_manager.unregister_observer(self._on_theme_changed)
        super().closeEvent(event)


class ThemedFrame(QFrame):
    """Themed frame/panel with consistent styling."""
    
    def __init__(self, 
                 show_border: bool = True,
                 parent: Optional[QWidget] = None):
        """
        Initialize themed frame.
        
        Args:
            show_border: Whether to show border
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.show_border = show_border
        self.theme_manager = get_theme_manager()
        self.style_generator = StyleGenerator(self.theme_manager.current_theme)
        
        # Register for theme updates
        self.theme_manager.register_observer(self._on_theme_changed)
        
        self._apply_styling()
    
    def _on_theme_changed(self, new_theme: ThemeColors):
        """Handle theme changes."""
        self.style_generator = StyleGenerator(new_theme)
        self.update_theme(new_theme)
    
    def _apply_styling(self):
        """Apply frame styling."""
        style = self.style_generator.panel_style(show_border=self.show_border)
        self.setStyleSheet(style)
    
    def update_theme(self, theme: ThemeColors):
        """Update frame styling with new theme."""
        self._apply_styling()
    
    def closeEvent(self, event):
        """Clean up theme observer on close."""
        self.theme_manager.unregister_observer(self._on_theme_changed)
        super().closeEvent(event)


class ActionButton(ThemedButton):
    """Specialized action button with icon and feedback."""
    
    def __init__(self, 
                 text: str,
                 icon: str,
                 action_type: str,
                 callback: Optional[Callable] = None,
                 parent: Optional[QWidget] = None):
        """
        Initialize action button.
        
        Args:
            text: Button text
            icon: Icon character/emoji
            action_type: Action type for styling
            callback: Click callback function
            parent: Parent widget
        """
        super().__init__(f"{icon} {text}", action_type, parent)
        
        self.original_text = f"{icon} {text}"
        self.icon = icon
        self.action_type = action_type
        
        if callback:
            self.clicked.connect(callback)
        
        self.setMinimumHeight(40)
    
    def show_feedback(self, success: bool = True, duration: int = 800):
        """Show visual feedback for action completion."""
        if not ANKI_AVAILABLE:
            return
        
        # Store original styling
        original_text = self.text()
        original_style = self.styleSheet()
        
        # Show feedback
        if success:
            self.setText("✓")
            feedback_style = self.style_generator.action_button_style("success")
        else:
            self.setText("✗")
            feedback_style = self.style_generator.action_button_style("error")
        
        self.setStyleSheet(feedback_style)
        
        # Reset after duration
        QTimer.singleShot(duration, lambda: [
            self.setText(original_text),
            self.setStyleSheet(original_style)
        ])


class CopyButton(ActionButton):
    """Specialized copy button with clipboard functionality."""
    
    def __init__(self, 
                 get_text_callback: Callable[[], str],
                 parent: Optional[QWidget] = None):
        """
        Initialize copy button.
        
        Args:
            get_text_callback: Function that returns text to copy
            parent: Parent widget
        """
        super().__init__(
            text="Copy",
            icon="✂",
            action_type="copy",
            callback=self._copy_to_clipboard,
            parent=parent
        )
        
        self.get_text_callback = get_text_callback
        self.setToolTip("Copy to clipboard")
    
    def _copy_to_clipboard(self):
        """Copy text to clipboard with feedback."""
        try:
            text = self.get_text_callback()
            if ANKI_AVAILABLE:
                QApplication.clipboard().setText(text)
            
            self.show_feedback(success=True)
            logger.debug(f"Copied to clipboard: {text[:50]}...")
        except Exception as e:
            self.show_feedback(success=False)
            logger.error(f"Failed to copy to clipboard: {e}")


class FrequencyBadge(ThemedButton):
    """Frequency badge button with color coding."""
    
    def __init__(self, 
                 frequency: int,
                 frequencies: Optional[Dict[str, int]] = None,
                 parent: Optional[QWidget] = None):
        """
        Initialize frequency badge.
        
        Args:
            frequency: Primary frequency value
            frequencies: Dictionary of all frequency sources
            parent: Parent widget
        """
        self.frequency = frequency
        self.frequencies = frequencies or {"General": frequency}
        
        # Get frequency label and color
        label_text = self._get_frequency_label(frequency)
        
        super().__init__(label_text, parent)
        
        self.setMinimumHeight(28)
        self.clicked.connect(self._show_breakdown)
        self._apply_frequency_styling()
    
    def _get_frequency_label(self, freq: int) -> str:
        """Get human-readable frequency label."""
        if freq <= 500:
            return "Very Common"
        elif freq <= 1500:
            return "Common"
        elif freq <= 5000:
            return "Uncommon"
        elif freq <= 15000:
            return "Rare"
        else:
            return "Very Rare"
    
    def _apply_frequency_styling(self):
        """Apply frequency-specific styling."""
        style = self.style_generator.frequency_badge_style(self.frequency)
        self.setStyleSheet(style)
    
    def _show_breakdown(self):
        """Show detailed frequency breakdown."""
        if not ANKI_AVAILABLE:
            return
        
        from aqt.utils import showInfo
        
        avg_freq = sum(self.frequencies.values()) / len(self.frequencies)
        avg_text = self._get_frequency_label(int(avg_freq))
        
        breakdown_lines = [f"Overall: {avg_text} (avg: {int(avg_freq):,})", ""]
        
        for freq_name, freq_value in self.frequencies.items():
            freq_text = self._get_frequency_label(freq_value)
            breakdown_lines.append(f"{freq_name}: {freq_value:,} ({freq_text})")
        
        breakdown_lines.extend(["", "(Lower rank = more common)"])
        showInfo("\n".join(breakdown_lines), title="Frequency Breakdown")
    
    def update_theme(self, theme: ThemeColors):
        """Update frequency badge styling with new theme."""
        self._apply_frequency_styling()


class PitchAccentLabel(ThemedLabel):
    """Pitch accent label with color coding."""
    
    def __init__(self, 
                 pitch_accent: str,
                 pitch_type: str,
                 parent: Optional[QWidget] = None):
        """
        Initialize pitch accent label.
        
        Args:
            pitch_accent: Pitch accent text
            pitch_type: Pitch type (heiban, odaka, nakadaka, atamadaka, kifuku)
            parent: Parent widget
        """
        super().__init__(pitch_accent, parent)
        
        self.pitch_type = pitch_type
        self._apply_pitch_styling()
        self._setup_tooltip()
    
    def _apply_pitch_styling(self):
        """Apply pitch accent specific styling."""
        style = self.style_generator.pitch_accent_style(self.pitch_type)
        self.setStyleSheet(style)
    
    def _setup_tooltip(self):
        """Setup informative tooltip."""
        if not ANKI_AVAILABLE:
            return
        
        tooltips = {
            'heiban': "Heiban (平板): Flat pitch pattern\n• Low-High-High-High pattern\n• Most common pitch accent type",
            'odaka': "Odaka (尾高): Tail-high pitch pattern\n• Low-High-High-Low pattern\n• Pitch drops after the word",
            'nakadaka': "Nakadaka (中高): Middle-high pitch pattern\n• Low-High-Low pattern\n• Peak in the middle of the word",
            'atamadaka': "Atamadaka (頭高): Head-high pitch pattern\n• High-Low-Low-Low pattern\n• Starts high, then drops",
            'kifuku': "Kifuku (起伏): Complex pitch pattern\n• Multiple pitch changes\n• Used for compound words"
        }
        
        tooltip = tooltips.get(self.pitch_type, "Unknown pitch accent pattern")
        self.setToolTip(tooltip)
    
    def update_theme(self, theme: ThemeColors):
        """Update pitch accent styling with new theme."""
        self._apply_pitch_styling()


class StatusMessage(ThemedLabel):
    """Status message with auto-hide and type-based styling."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize status message."""
        super().__init__("", "muted", parent)
        
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)
    
    def show_message(self, 
                    message: str, 
                    message_type: str = "info",
                    duration: int = 3000):
        """
        Show status message with auto-hide.
        
        Args:
            message: Message text
            message_type: Message type (info, success, warning, error)
            duration: Duration in milliseconds (0 = no auto-hide)
        """
        self.setText(message)
        
        # Apply type-specific styling
        if message_type == "success":
            color = self.style_generator.theme.success_color
            prefix = "✓ "
        elif message_type == "warning":
            color = self.style_generator.theme.warning_color
            prefix = "⚠ "
        elif message_type == "error":
            color = self.style_generator.theme.error_color
            prefix = "✗ "
        else:
            color = self.style_generator.theme.info_color
            prefix = "ℹ "
        
        self.setText(f"{prefix}{message}")
        
        style = self.style_generator.label_style(
            color=color,
            size_type="small"
        )
        self.setStyleSheet(style)
        
        self.show()
        
        # Auto-hide if duration specified
        if duration > 0:
            self.hide_timer.start(duration)
    
    def show_success(self, message: str, duration: int = 3000):
        """Show success message."""
        self.show_message(message, "success", duration)
    
    def show_error(self, message: str, duration: int = 5000):
        """Show error message."""
        self.show_message(message, "error", duration)
    
    def show_warning(self, message: str, duration: int = 4000):
        """Show warning message."""
        self.show_message(message, "warning", duration)
    
    def show_info(self, message: str, duration: int = 3000):
        """Show info message."""
        self.show_message(message, "info", duration)


class ValidationInput(ThemedLineEdit):
    """Input field with built-in validation and error display."""
    
    def __init__(self, 
                 placeholder: str = "",
                 validator: Optional[Callable[[str], tuple[bool, str]]] = None,
                 parent: Optional[QWidget] = None):
        """
        Initialize validation input.
        
        Args:
            placeholder: Placeholder text
            validator: Function that returns (is_valid, error_message)
            parent: Parent widget
        """
        super().__init__(placeholder, parent)
        
        self.validator_func = validator
        self.is_valid = True
        self.error_message = ""
        
        # Connect validation
        self.textChanged.connect(self._validate)
    
    def _validate(self):
        """Validate current input."""
        if not self.validator_func:
            return
        
        text = self.text()
        self.is_valid, self.error_message = self.validator_func(text)
        
        # Update styling based on validation
        if self.is_valid:
            style = self.style_generator.input_style()
        else:
            # Error styling
            style = self.style_generator.input_style()
            style = style.replace(
                f"border: 1px solid {self.style_generator.theme.border_color}",
                f"border: 2px solid {self.style_generator.theme.error_color}"
            )
        
        self.setStyleSheet(style)
    
    def get_validation_error(self) -> Optional[str]:
        """Get current validation error message."""
        return self.error_message if not self.is_valid else None