# -*- coding: utf-8 -*-
# 
# DEPRECATED: This module is kept for backward compatibility.
# New code should use src.utils.dialogs instead.
#
# This file now acts as a compatibility shim, forwarding calls to the new location.

from typing import Optional, Tuple
from src.utils.dialogs import show_info, show_warning, show_error, show_notice, ask_user


def show_info_dialog(
    text: str,
    parent: Optional[object] = False,
    level: str = 'msg',
    day: bool = True
) -> int:
    """
    Show an information dialog.
    
    DEPRECATED: Use src.utils.dialogs.show_info() instead.
    
    Args:
        text: Message to display
        parent: Parent widget
        level: Message level ('msg', 'wrn', 'not', 'err')
        day: Whether to use day theme (deprecated parameter)
        
    Returns:
        Result of dialog execution
    """
    # Map level to appropriate function
    if level == 'wrn':
        return show_warning(text, parent if parent is not False else None)
    elif level == 'not':
        return show_notice(text, parent if parent is not False else None)
    elif level == 'err':
        return show_error(text, parent if parent is not False else None)
    else:
        return show_info(text, parent if parent is not False else None)


def ask_user_dialog(
    text: str,
    parent: Optional[object] = None,
    day: bool = True,
    customText: Optional[Tuple[str, str]] = False
) -> bool:
    """
    Ask user a yes/no question.
    
    DEPRECATED: Use src.utils.dialogs.ask_user() instead.
    
    Args:
        text: Question to ask
        parent: Parent widget
        day: Whether to use day theme (deprecated parameter)
        customText: Optional tuple of (yes_text, no_text)
        
    Returns:
        True if user clicked yes, False otherwise
    """
    custom_buttons = customText if customText else None
    return ask_user(text, parent, custom_buttons)
