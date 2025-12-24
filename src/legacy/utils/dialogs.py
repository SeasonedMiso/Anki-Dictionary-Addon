# -*- coding: utf-8 -*-
"""
Dialog utilities for user interaction.
"""

from typing import Optional
from os.path import dirname, join

# Try to import Anki modules, but allow running without them
try:
    import aqt
    from aqt.qt import QMessageBox, QIcon
    ANKI_AVAILABLE = True
except ImportError:
    ANKI_AVAILABLE = False
    aqt = None
    QMessageBox = None
    QIcon = None

addon_path = dirname(dirname(dirname(__file__)))


def show_info(
    text: str,
    parent: Optional[object] = None,
    title: str = "Anki Dictionary"
) -> int:
    """
    Show an information dialog.
    
    Args:
        text: Message to display
        parent: Parent widget (defaults to main window)
        title: Dialog title
        
    Returns:
        Result of dialog execution
    """
    if not ANKI_AVAILABLE:
        # Fallback for testing without Anki
        print(f"[{title}] {text}")
        return 0
    
    if parent is None:
        parent = aqt.mw.app.activeWindow() or aqt.mw
    
    icon = QIcon(join(addon_path, 'icons', 'miso.png'))
    mb = QMessageBox(parent)
    mb.setText(text)
    mb.setWindowIcon(icon)
    mb.setWindowTitle(title)
    
    button = mb.addButton(QMessageBox.StandardButton.Ok)
    button.setFixedSize(100, 30)
    button.setDefault(True)
    
    return mb.exec()


def show_warning(
    text: str,
    parent: Optional[object] = None
) -> int:
    """Show a warning dialog."""
    return show_info(text, parent, "Anki Dictionary Warning")


def show_error(
    text: str,
    parent: Optional[object] = None
) -> int:
    """Show an error dialog."""
    return show_info(text, parent, "Anki Dictionary Error")


def show_notice(
    text: str,
    parent: Optional[object] = None
) -> int:
    """Show a notice dialog."""
    return show_info(text, parent, "Anki Dictionary Notice")


def ask_user(
    text: str,
    parent: Optional[object] = None,
    custom_buttons: Optional[tuple[str, str]] = None
) -> bool:
    """
    Ask user a yes/no question.
    
    Args:
        text: Question to ask
        parent: Parent widget
        custom_buttons: Optional tuple of (yes_text, no_text)
        
    Returns:
        True if user clicked yes, False otherwise
    """
    if not ANKI_AVAILABLE:
        # Fallback for testing without Anki
        print(f"[Question] {text}")
        return True  # Default to yes in tests
    
    if parent is None:
        parent = aqt.mw.app.activeWindow() or aqt.mw
    
    msg = QMessageBox(parent)
    msg.setWindowTitle("Anki Dictionary")
    msg.setText(text)
    
    icon = QIcon(join(addon_path, 'icons', 'miso.png'))
    msg.setWindowIcon(icon)
    
    yes_button = msg.addButton(QMessageBox.StandardButton.Yes)
    yes_button.setFixedSize(100, 30)
    yes_button.setDefault(True)
    
    no_button = msg.addButton(QMessageBox.StandardButton.No)
    no_button.setFixedSize(100, 30)
    
    if custom_buttons:
        yes_button.setText(custom_buttons[0])
        no_button.setText(custom_buttons[1])
        yes_button.setFixedSize(120, 40)
        no_button.setFixedSize(120, 40)
    
    msg.exec()
    return msg.clickedButton() == yes_button
