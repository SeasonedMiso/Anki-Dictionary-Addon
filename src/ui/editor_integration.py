# -*- coding: utf-8 -*-
"""
Editor Integration module for Anki Dictionary addon.

This module handles integration with Anki's editor (Add Cards, Edit Current, Browser),
including context menus, hotkeys, and selected text search functionality.
"""

from typing import Any, Optional, TYPE_CHECKING
import logging
import re

if TYPE_CHECKING:
    from ..core.plugin import AnkiDictionaryPlugin

try:
    from aqt.qt import QShortcut, QKeySequence, QAction
    from aqt.webview import AnkiWebView
    from aqt.addcards import AddCards
    from aqt.editcurrent import EditCurrent
    from aqt.browser import Browser
    from aqt.tagedit import TagEdit
    from aqt.previewer import Previewer
    from anki.hooks import addHook, wrap
    import aqt.editor
    ANKI_AVAILABLE = True
except ImportError:
    # For testing without Anki
    ANKI_AVAILABLE = False
    QShortcut = type('QShortcut', (object,), {})
    QKeySequence = type('QKeySequence', (object,), {})
    QAction = type('QAction', (object,), {})
    AnkiWebView = type('AnkiWebView', (object,), {})
    AddCards = type('AddCards', (object,), {})
    EditCurrent = type('EditCurrent', (object,), {})
    Browser = type('Browser', (object,), {})
    TagEdit = type('TagEdit', (object,), {})
    Previewer = type('Previewer', (object,), {})
    addHook = lambda *args: None
    wrap = lambda *args: args[0]


logger = logging.getLogger('anki_dictionary.ui.editor_integration')


class EditorIntegration:
    """
    Manages integration with Anki's editor components.
    
    This class handles:
    - Editor button additions
    - Context menu additions
    - Keyboard shortcuts
    - Selected text search functionality
    - Editor lifecycle tracking
    """
    
    def __init__(self, plugin: 'AnkiDictionaryPlugin'):
        """
        Initialize editor integration.
        
        Args:
            plugin: Plugin coordinator instance
        """
        self.plugin = plugin
        self.mw = plugin.mw
        
        # Store original methods for wrapping
        self._original_bridge_cmd: Optional[Any] = None
        
        logger.info("Editor integration initialized")
    
    def setup_editor_hooks(self) -> None:
        """Register all editor-related hooks and wraps."""
        if not ANKI_AVAILABLE:
            logger.warning("Anki not available, skipping editor hook setup")
            return
        
        try:
            # Context menu hooks
            addHook("EditorWebView.contextMenuEvent", self._add_to_context_menu)
            addHook("AnkiWebView.contextMenuEvent", self._add_to_context_menu)
            
            # Editor setup hooks
            aqt.editor.Editor.setupWeb = wrap(
                aqt.editor.Editor.setupWeb,
                self._add_editor_functionality
            )
            
            # Bridge command interception
            self._original_bridge_cmd = aqt.editor.Editor.onBridgeCmd
            aqt.editor.Editor.onBridgeCmd = self._bridge_reroute
            
            # Window lifecycle hooks
            Browser.on_current_row_changed = wrap(
                Browser.on_current_row_changed,
                self._set_browser_editor
            )
            
            AddCards._close = wrap(
                AddCards._close,
                self._check_current_editor
            )
            
            EditCurrent._saveAndClose = wrap(
                EditCurrent._saveAndClose,
                self._check_current_editor
            )
            
            Browser._closeWindow = wrap(
                Browser._closeWindow,
                self._check_current_editor
            )
            
            # Window activation hooks
            AddCards.addCards = wrap(
                AddCards.addCards,
                self._add_edit_activated
            )
            
            AddCards.onHistory = wrap(
                AddCards.onHistory,
                self._add_edit_activated
            )
            
            AddCards.mousePressEvent = self._add_edit_activated
            EditCurrent.mousePressEvent = self._add_edit_activated
            
            # Tag edit focus hook
            TagEdit.focusInEvent = wrap(
                TagEdit.focusInEvent,
                self._announce_parent
            )
            
            # Previewer hooks
            Previewer.open = wrap(
                Previewer.open,
                self._add_hotkeys_to_preview
            )
            
            # Attach search methods to AnkiWebView
            AnkiWebView.searchTerm = self._search_term
            AnkiWebView.searchCol = self._search_col
            self.mw.searchTerm = self._search_term
            self.mw.searchCol = self._search_col
            
            logger.info("Editor hooks registered successfully")
            
        except Exception as e:
            logger.error(f"Error setting up editor hooks: {e}", exc_info=True)
    
    def _add_to_context_menu(self, web_view: Any, menu: Any) -> None:
        """
        Add dictionary options to context menu.
        
        Args:
            web_view: Web view instance
            menu: Context menu to modify
        """
        try:
            # Add search action
            search_action = QAction("Search (Ctrl+S)", menu)
            search_action.triggered.connect(lambda: self._search_term(web_view))
            menu.addAction(search_action)
            
            # Add search collection action
            search_col_action = QAction("Search Collection (Ctrl/⌘+Shift+B)", menu)
            search_col_action.triggered.connect(lambda: self._search_col(web_view))
            menu.addAction(search_col_action)
            
            logger.debug("Context menu items added")
            
        except Exception as e:
            logger.error(f"Error adding context menu items: {e}", exc_info=True)
    
    def _add_editor_functionality(self, editor: Any) -> None:
        """
        Add dictionary functionality to editor.
        
        Args:
            editor: Editor instance
        """
        try:
            # Store reference to parent editor
            editor.web.parentEditor = editor
            
            # Add body click handler
            self._add_body_click(editor)
            
            # Add hotkeys
            self._add_hotkeys(editor)
            
            logger.debug("Editor functionality added")
            
        except Exception as e:
            logger.error(f"Error adding editor functionality: {e}", exc_info=True)
    
    def _add_body_click(self, editor: Any) -> None:
        """
        Add body click handler to editor.
        
        Args:
            editor: Editor instance
        """
        try:
            body_click_js = '''document.addEventListener("click", function (ev) {
                pycmd("bodyClick")
            }, false);'''
            
            editor.web.eval(body_click_js)
            
        except Exception as e:
            logger.error(f"Error adding body click handler: {e}", exc_info=True)
    
    def _add_hotkeys(self, editor: Any) -> None:
        """
        Add keyboard shortcuts to editor window.
        
        Args:
            editor: Editor instance
        """
        try:
            parent_window = editor.parentWindow
            
            # Ctrl+S: Search selected text
            hotkey_s = QShortcut(QKeySequence("Ctrl+S"), parent_window)
            hotkey_s.activated.connect(lambda: self._search_term(editor.web))
            parent_window.hotkeyS = hotkey_s
            
            # Ctrl+Shift+B: Search collection
            hotkey_b = QShortcut(QKeySequence("Ctrl+Shift+B"), parent_window)
            hotkey_b.activated.connect(lambda: self._search_col(editor.web))
            parent_window.hotkeyB = hotkey_b
            
            # Ctrl+W: Toggle dictionary window
            hotkey_w = QShortcut(QKeySequence("Ctrl+W"), parent_window)
            hotkey_w.activated.connect(self._toggle_dictionary)
            parent_window.hotkeyW = hotkey_w
            
            logger.debug("Editor hotkeys added")
            
        except Exception as e:
            logger.error(f"Error adding editor hotkeys: {e}", exc_info=True)
    
    def _add_hotkeys_to_preview(self, previewer: Any) -> None:
        """
        Add keyboard shortcuts to preview window.
        
        Args:
            previewer: Previewer instance
        """
        try:
            web = previewer._web
            
            # Ctrl+S: Search selected text
            hotkey_s = QShortcut(QKeySequence("Ctrl+S"), web)
            hotkey_s.activated.connect(lambda: self._search_term(web))
            web.hotkeyS = hotkey_s
            
            # Ctrl+Shift+B: Search collection
            hotkey_b = QShortcut(QKeySequence("Ctrl+Shift+B"), web)
            hotkey_b.activated.connect(lambda: self._search_col(web))
            web.hotkeyB = hotkey_b
            
            # Ctrl+W: Toggle dictionary window
            hotkey_w = QShortcut(QKeySequence("Ctrl+W"), web)
            hotkey_w.activated.connect(self._toggle_dictionary)
            web.hotkeyW = hotkey_w
            
            logger.debug("Preview hotkeys added")
            
        except Exception as e:
            logger.error(f"Error adding preview hotkeys: {e}", exc_info=True)
    
    def _search_term(self, web_view: Any) -> None:
        """
        Search for selected text in dictionary.
        
        Args:
            web_view: Web view with selected text
        """
        try:
            # Get selected text
            text = self._get_selected_text(web_view)
            if not text:
                logger.debug("No text selected for search")
                return
            
            # Clean the text
            text = re.sub(r'\[[^\]]+?\]', '', text)
            text = text.strip()
            
            if not text:
                return
            
            # Get or create dictionary window
            dict_window = self.plugin.get_dictionary_window()
            
            # Show window if hidden
            if not dict_window.isVisible():
                dict_window.show_window()
            
            # Ensure window is visible and focused
            dict_window.raise_()
            dict_window.activateWindow()
            
            # Perform search
            dict_window.perform_search(text)
            
            # Set current editor context
            if hasattr(web_view, 'title'):
                if web_view.title == 'main webview':
                    # Reviewer context
                    if self.mw.state == 'review':
                        dict_window.set_current_reviewer(self.mw.reviewer)
                elif web_view.title == 'editor':
                    # Editor context
                    if hasattr(web_view, 'parentEditor'):
                        editor = web_view.parentEditor
                        target = self._get_target(type(editor.parentWindow).__name__)
                        dict_window.set_current_editor(editor, target)
            
            logger.info(f"Searched for term: {text}")
            
        except Exception as e:
            logger.error(f"Error searching term: {e}", exc_info=True)
    
    def _search_col(self, web_view: Any) -> None:
        """
        Search collection for selected text.
        
        Args:
            web_view: Web view with selected text
        """
        try:
            import aqt
            from anki.utils import is_win
            from aqt.qt import Qt
            
            # Get selected text
            text = self._get_selected_text(web_view)
            if not text:
                logger.debug("No text selected for collection search")
                return
            
            text = text.strip()
            
            # Get or open browser
            browser = aqt.DialogManager._dialogs.get("Browser", [None, None])[1]
            if not browser:
                self.mw.onBrowse()
                browser = aqt.DialogManager._dialogs.get("Browser", [None, None])[1]
            
            if browser:
                # Set search text
                browser.form.searchEdit.lineEdit().setText(text)
                browser.onSearchActivated()
                
                # Activate and raise window
                browser.activateWindow()
                if not is_win:
                    browser.setWindowState(
                        browser.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive
                    )
                    browser.raise_()
                else:
                    browser.setWindowFlags(
                        browser.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
                    )
                    browser.show()
                    browser.setWindowFlags(
                        browser.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
                    )
                    browser.show()
                
                logger.info(f"Searched collection for: {text}")
            
        except Exception as e:
            logger.error(f"Error searching collection: {e}", exc_info=True)
    
    def _get_selected_text(self, web_view: Any) -> Optional[str]:
        """
        Get selected text from web view.
        
        Args:
            web_view: Web view instance
            
        Returns:
            Selected text or None
        """
        try:
            text = web_view.selectedText()
            return text if text else None
        except Exception as e:
            logger.error(f"Error getting selected text: {e}", exc_info=True)
            return None
    
    def _toggle_dictionary(self) -> None:
        """Toggle dictionary window visibility."""
        try:
            dict_window = self.plugin.get_dictionary_window()
            dict_window.toggle_visibility()
        except Exception as e:
            logger.error(f"Error toggling dictionary: {e}", exc_info=True)
    
    def _bridge_reroute(self, editor: Any, cmd: str) -> None:
        """
        Reroute bridge commands to handle dictionary integration.
        
        Args:
            editor: Editor instance
            cmd: Bridge command
        """
        try:
            # Get dictionary window if it exists
            dict_window = self.plugin.dictionary_window
            
            if cmd == "bodyClick":
                # Handle body click
                if dict_window and dict_window.isVisible() and editor.note:
                    widget = type(editor.widget.parentWidget()).__name__
                    if widget == 'QWidget':
                        widget = 'Browser'
                    target = self._get_target(widget)
                    dict_window.set_current_editor(editor, target)
                
                # Call original handler
                if self._original_bridge_cmd:
                    self._original_bridge_cmd(editor, cmd)
            
            elif cmd.startswith("focus"):
                # Handle focus events
                if dict_window and dict_window.isVisible() and editor.note:
                    widget = type(editor.widget.parentWidget()).__name__
                    if widget == 'QWidget':
                        widget = 'Browser'
                    target = self._get_target(widget)
                    dict_window.set_current_editor(editor, target)
                
                # Call original handler
                if self._original_bridge_cmd:
                    self._original_bridge_cmd(editor, cmd)
            
            else:
                # Pass through to original handler
                if self._original_bridge_cmd:
                    self._original_bridge_cmd(editor, cmd)
        
        except Exception as e:
            logger.error(f"Error in bridge reroute: {e}", exc_info=True)
            # Always call original handler on error
            if self._original_bridge_cmd:
                self._original_bridge_cmd(editor, cmd)
    
    def _set_browser_editor(self, browser: Any) -> None:
        """
        Set browser editor for dictionary.
        
        Args:
            browser: Browser instance
        """
        try:
            dict_window = self.plugin.dictionary_window
            if dict_window and dict_window.isVisible():
                if browser.editor.note:
                    dict_window.set_current_editor(browser.editor, 'Browser')
                else:
                    dict_window.current_editor = None
        except Exception as e:
            logger.error(f"Error setting browser editor: {e}", exc_info=True)
    
    def _check_current_editor(self, window: Any) -> None:
        """
        Check if current editor should be closed.
        
        Args:
            window: Window being closed
        """
        try:
            dict_window = self.plugin.dictionary_window
            if dict_window and dict_window.isVisible():
                if hasattr(window, 'editor'):
                    if dict_window.current_editor == window.editor:
                        dict_window.current_editor = None
        except Exception as e:
            logger.error(f"Error checking current editor: {e}", exc_info=True)
    
    def _add_edit_activated(self, window: Any, event: Any = None) -> None:
        """
        Handle edit window activation.
        
        Args:
            window: Window being activated
            event: Optional event
        """
        try:
            dict_window = self.plugin.dictionary_window
            if dict_window and dict_window.isVisible():
                target = self._get_target(type(window).__name__)
                dict_window.set_current_editor(window.editor, target)
        except Exception as e:
            logger.error(f"Error on edit activated: {e}", exc_info=True)
    
    def _announce_parent(self, tag_edit: Any, event: Any = None) -> None:
        """
        Announce parent window to dictionary.
        
        Args:
            tag_edit: Tag edit widget
            event: Optional event
        """
        try:
            dict_window = self.plugin.dictionary_window
            if dict_window and dict_window.isVisible():
                parent = tag_edit.parentWidget().parentWidget().parentWidget()
                p_name = type(parent).__name__
                
                if p_name not in ['AddCards', 'EditCurrent']:
                    import aqt
                    parent = aqt.DialogManager._dialogs.get("Browser", [None, None])[1]
                    p_name = 'Browser'
                    if not parent:
                        return
                
                target = self._get_target(p_name)
                dict_window.set_current_editor(parent.editor, target)
        except Exception as e:
            logger.error(f"Error announcing parent: {e}", exc_info=True)
    
    def _get_target(self, window_name: str) -> str:
        """
        Get target type from window name.
        
        Args:
            window_name: Name of window class
            
        Returns:
            Target description
        """
        if window_name == 'AddCards':
            return 'Add'
        elif window_name in ("EditCurrent", "DictEditCurrent"):
            return 'Edit'
        elif window_name == 'Browser':
            return 'Browser'
        return ''
