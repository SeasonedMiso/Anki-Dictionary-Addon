# -*- coding: utf-8 -*-
"""
Menu Manager module for Anki Dictionary addon.

This module handles centralized menu creation and global hotkey registration,
including platform-specific shortcut handling.
"""

from typing import Any, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ..core.plugin import AnkiDictionaryPlugin

try:
    from aqt.qt import QAction, QShortcut, QKeySequence, QMenu
    from anki.utils import is_mac
    ANKI_AVAILABLE = True
except ImportError:
    # For testing without Anki
    ANKI_AVAILABLE = False
    QAction = type('QAction', (object,), {})
    QShortcut = type('QShortcut', (object,), {})
    QKeySequence = type('QKeySequence', (object,), {})
    QMenu = type('QMenu', (object,), {})
    is_mac = False  # Boolean, not function


logger = logging.getLogger('anki_dictionary.ui.menu_manager')


class MenuManager:
    """
    Manages addon menu and global keyboard shortcuts.
    
    This class handles:
    - Menu creation in Anki's menu bar
    - Global hotkey registration
    - Platform-specific shortcut handling (Mac vs Windows/Linux)
    - Menu action triggers
    """
    
    def __init__(self, mw: Any, plugin: 'AnkiDictionaryPlugin'):
        """
        Initialize menu manager.
        
        Args:
            mw: Anki main window instance
            plugin: Plugin coordinator instance
        """
        self.mw = mw
        self.plugin = plugin
        
        # Menu references
        self._main_menu: Optional[QMenu] = None
        self._menu_actions: list = []
        self._menu_settings: list = []
        
        # Hotkey references
        self._global_hotkeys: list = []
        
        logger.info("Menu manager initialized")
    
    def setup_menu(self) -> None:
        """Create addon menu in Anki's menu bar."""
        if not ANKI_AVAILABLE:
            logger.warning("Anki not available, skipping menu setup")
            return
        
        try:
            # Create main menu if it doesn't exist
            if not hasattr(self.mw, 'DictMainMenu'):
                self._main_menu = QMenu('Dict', self.mw)
                self.mw.DictMainMenu = self._main_menu
                add_menu = True
            else:
                self._main_menu = self.mw.DictMainMenu
                add_menu = False
            
            # Initialize menu action lists on mw for backward compatibility
            if not hasattr(self.mw, 'DictMenuSettings'):
                self.mw.DictMenuSettings = []
            if not hasattr(self.mw, 'DictMenuActions'):
                self.mw.DictMenuActions = []
            
            # Create settings action
            settings_action = QAction("Dictionary Settings", self.mw)
            settings_action.triggered.connect(self.open_settings)
            self.mw.DictMenuSettings.append(settings_action)
            self._menu_settings.append(settings_action)
            
            # Create dictionary toggle action
            shortcut_text = self._get_shortcut_display("Ctrl+W")
            dict_action = QAction(f"Open Dictionary ({shortcut_text})", self.mw)
            dict_action.triggered.connect(self.open_dictionary)
            self.mw.openMiDict = dict_action  # Backward compatibility
            self.mw.DictMenuActions.append(dict_action)
            self._menu_actions.append(dict_action)
            
            # Clear and rebuild menu
            self._main_menu.clear()
            
            # Add settings actions
            for action in self.mw.DictMenuSettings:
                self._main_menu.addAction(action)
            
            # Add separator
            self._main_menu.addSeparator()
            
            # Add main actions
            for action in self.mw.DictMenuActions:
                self._main_menu.addAction(action)
            
            # Add menu to menu bar if new
            if add_menu:
                self.mw.form.menubar.insertMenu(
                    self.mw.form.menuHelp.menuAction(),
                    self._main_menu
                )
            
            logger.info("Menu created successfully")
            
        except Exception as e:
            logger.error(f"Error setting up menu: {e}", exc_info=True)
    
    def setup_global_hotkeys(self) -> None:
        """Register global keyboard shortcuts."""
        if not ANKI_AVAILABLE:
            logger.warning("Anki not available, skipping hotkey setup")
            return
        
        try:
            # Ctrl+W / ⌘W: Toggle dictionary window
            shortcut_str = self._get_platform_shortcut("Ctrl+W")
            logger.info(f"Setting up dictionary hotkey: {shortcut_str}")
            hotkey_w = QShortcut(
                QKeySequence(shortcut_str),
                self.mw
            )
            hotkey_w.activated.connect(lambda: (logger.info("Hotkey W activated!"), self.open_dictionary()))
            self.mw.hotkeyW = hotkey_w  # Backward compatibility
            self._global_hotkeys.append(hotkey_w)
            logger.info(f"Dictionary hotkey registered: {hotkey_w.key().toString()}")
            
            # Ctrl+S / ⌘S: Search selected text
            hotkey_s = QShortcut(
                QKeySequence(self._get_platform_shortcut("Ctrl+S")),
                self.mw
            )
            hotkey_s.activated.connect(self._search_selected_text)
            self.mw.hotkeyS = hotkey_s  # Backward compatibility
            self._global_hotkeys.append(hotkey_s)
            
            # Ctrl+Shift+B / ⌘+Shift+B: Search collection
            hotkey_b = QShortcut(
                QKeySequence(self._get_platform_shortcut("Ctrl+Shift+B")),
                self.mw
            )
            hotkey_b.activated.connect(self._search_collection)
            self.mw.hotkeyB = hotkey_b  # Backward compatibility
            self._global_hotkeys.append(hotkey_b)
            
            logger.info(f"Global hotkeys registered: {len(self._global_hotkeys)} shortcuts")
            
        except Exception as e:
            logger.error(f"Error setting up global hotkeys: {e}", exc_info=True)
    
    def open_dictionary(self) -> None:
        """
        Open or toggle dictionary window.
        
        This method handles opening the dictionary window, toggling its visibility,
        and updating the menu text accordingly.
        """
        logger.info("open_dictionary called")
        try:
            from anki.utils import is_mac
            
            logger.info("Getting dictionary window...")
            # Get dictionary window
            dict_window = self.plugin.get_dictionary_window()
            logger.info(f"Dictionary window obtained: {dict_window}")
            
            # Determine shortcut text for menu
            shortcut_text = "⌘W" if is_mac else "Ctrl+W"
            
            # Toggle visibility
            if dict_window.isVisible():
                # Hide window
                logger.info("Hiding dictionary window")
                dict_window.hide()
                if hasattr(self.mw, 'openMiDict'):
                    self.mw.openMiDict.setText(f"Open Dictionary ({shortcut_text})")
                logger.debug("Dictionary window hidden")
            else:
                # Show window
                logger.info("Showing dictionary window")
                dict_window.show_window()
                if hasattr(self.mw, 'openMiDict'):
                    self.mw.openMiDict.setText(f"Close Dictionary ({shortcut_text})")
                logger.debug("Dictionary window shown")
            
        except Exception as e:
            logger.error(f"Error opening dictionary: {e}", exc_info=True)
            from aqt.utils import showWarning
            showWarning(
                f"Error opening dictionary: {str(e)}",
                parent=self.mw,
                title="Anki Dictionary"
            )
    
    def open_settings(self) -> None:
        """
        Open settings window.
        
        This method opens the settings window and ensures it's visible and focused.
        """
        try:
            from aqt.qt import Qt
            
            # Get settings window
            settings_window = self.plugin.get_settings_window()
            
            # Show window
            settings_window.show()
            
            # Ensure window is not minimized
            if settings_window.windowState() == Qt.WindowState.WindowMinimized:
                settings_window.setWindowState(Qt.WindowState.WindowNoState)
            
            # Focus and activate
            settings_window.setFocus()
            settings_window.activateWindow()
            
            logger.debug("Settings window opened")
            
        except Exception as e:
            logger.error(f"Error opening settings: {e}", exc_info=True)
            from aqt.utils import showWarning
            showWarning(
                f"Error opening settings: {str(e)}",
                parent=self.mw,
                title="Anki Dictionary"
            )
    
    def _search_selected_text(self) -> None:
        """Search for selected text in main window."""
        try:
            # Delegate to editor integration's search functionality
            if hasattr(self.mw, 'web'):
                # Get editor integration
                editor_integration = self.plugin.editor_integration
                if editor_integration:
                    editor_integration._search_term(self.mw.web)
                else:
                    logger.warning("Editor integration not available")
            else:
                logger.warning("Main window web view not available")
        except Exception as e:
            logger.error(f"Error searching selected text: {e}", exc_info=True)
    
    def _search_collection(self) -> None:
        """Search collection for selected text in main window."""
        try:
            # Delegate to editor integration's search collection functionality
            if hasattr(self.mw, 'web'):
                # Get editor integration
                editor_integration = self.plugin.editor_integration
                if editor_integration:
                    editor_integration._search_col(self.mw.web)
                else:
                    logger.warning("Editor integration not available")
            else:
                logger.warning("Main window web view not available")
        except Exception as e:
            logger.error(f"Error searching collection: {e}", exc_info=True)
    
    def _get_platform_shortcut(self, shortcut: str) -> str:
        """
        Get platform-specific shortcut string.
        
        On macOS, converts Ctrl to Cmd (⌘).
        On Windows/Linux, keeps Ctrl as is.
        
        Args:
            shortcut: Shortcut string (e.g., "Ctrl+W")
            
        Returns:
            Platform-specific shortcut string
        """
        try:
            if is_mac:
                # Replace Ctrl with Cmd for Mac
                return shortcut.replace("Ctrl", "Cmd")
            else:
                # Keep as is for Windows/Linux
                return shortcut
        except Exception as e:
            logger.error(f"Error getting platform shortcut: {e}", exc_info=True)
            return shortcut
    
    def _get_shortcut_display(self, shortcut: str) -> str:
        """
        Get display text for shortcut in menu.
        
        Args:
            shortcut: Shortcut string (e.g., "Ctrl+W")
            
        Returns:
            Display text for menu (e.g., "⌘W" on Mac, "Ctrl+W" on Windows/Linux)
        """
        try:
            if is_mac:
                # Use Mac symbols and remove + signs for cleaner display
                return shortcut.replace("Ctrl+", "⌘").replace("Shift+", "⇧").replace("+", "")
            else:
                # Keep as is for Windows/Linux
                return shortcut
        except Exception as e:
            logger.error(f"Error getting shortcut display: {e}", exc_info=True)
            return shortcut
    
    def update_dictionary_menu_text(self, is_visible: bool) -> None:
        """
        Update dictionary menu text based on window visibility.
        
        Args:
            is_visible: Whether dictionary window is visible
        """
        try:
            shortcut_text = self._get_shortcut_display("Ctrl+W")
            
            if hasattr(self.mw, 'openMiDict'):
                if is_visible:
                    self.mw.openMiDict.setText(f"Close Dictionary ({shortcut_text})")
                else:
                    self.mw.openMiDict.setText(f"Open Dictionary ({shortcut_text})")
        except Exception as e:
            logger.error(f"Error updating menu text: {e}", exc_info=True)
    
    def cleanup(self) -> None:
        """Clean up menu and hotkey resources."""
        try:
            # Clear hotkey references
            self._global_hotkeys.clear()
            
            # Clear menu references
            self._menu_actions.clear()
            self._menu_settings.clear()
            
            logger.info("Menu manager cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up menu manager: {e}", exc_info=True)
