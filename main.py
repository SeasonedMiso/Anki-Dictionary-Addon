# -*- coding: utf-8 -*-
"""
Anki Dictionary Add-on - Main Entry Point

This module initializes the Anki Dictionary plugin using the plugin coordinator pattern.
All functionality is delegated to the AnkiDictionaryPlugin class for clean separation
of concerns and testability.
"""

from pathlib import Path
from aqt import mw
from aqt.qt import QAction, QShortcut, QKeySequence, QMenu
from anki.hooks import addHook, wrap
from aqt.utils import showInfo
import aqt.editor
from aqt.webview import AnkiWebView
from aqt.addcards import AddCards
from aqt.editcurrent import EditCurrent
from aqt.browser import Browser
from aqt.tagedit import TagEdit
from aqt.reviewer import Reviewer
from aqt.previewer import Previewer

from .src.core.plugin import AnkiDictionaryPlugin
from .src.constants import VERSION

# Initialize plugin coordinator
plugin = AnkiDictionaryPlugin(mw)

# Attach to mw for backward compatibility
mw.ankiDictPlugin = plugin

# Legacy dictionary window reference
mw.ankiDictionary = False


# ============================================================================
# Lifecycle Hooks
# ============================================================================

def on_profile_loaded():
    """Called when Anki profile is loaded."""
    plugin.initialize()
    
    # Initialize dictionary on start if configured
    if mw.AnkiDictConfig.get('dictOnStart', False):
        dictionary_init()


def on_unload_profile():
    """Called when Anki profile is unloaded."""
    close_dictionary()
    plugin.cleanup()


def close_dictionary():
    """Close dictionary window."""
    if mw.ankiDictionary and mw.ankiDictionary.isVisible():
        mw.ankiDictionary.saveSizeAndPos()
        mw.ankiDictionary.hide()
        mw.openMiDict.setText("Open Dictionary (Ctrl+W)")


# Register lifecycle hooks
addHook('profileLoaded', on_profile_loaded)
addHook('unloadProfile', on_unload_profile)


# ============================================================================
# Legacy Functions
# ============================================================================

def ankiDict(text):
    """Legacy function wrapper for showing info dialogs."""
    showInfo(text, False, "", "info", "Anki Dictionary Add-on")


def dictionary_init(terms=False):
    """Legacy function wrapper for opening the dictionary window."""
    from .midict import DictInterface
    from anki.utils import is_mac
    
    if terms and isinstance(terms, str):
        terms = [terms]
    
    shortcut = '(Ctrl+W)'
    if is_mac:
        shortcut = '⌘W'
    
    if not mw.ankiDictionary:
        addon_path = plugin.get_addon_path()
        if is_mac:
            welcome_path = addon_path / 'macwelcome.html'
        else:
            welcome_path = addon_path / 'welcome.html'
        
        with open(welcome_path, 'r', encoding="utf-8") as fh:
            welcome_screen = fh.read()
        
        mw.ankiDictionary = DictInterface(
            mw.miDictDB, mw, str(addon_path), welcome_screen, terms=terms
        )
        mw.openMiDict.setText("Close Dictionary " + shortcut)
        show_after_global_search()
    elif not mw.ankiDictionary.isVisible():
        mw.ankiDictionary.show()
        mw.ankiDictionary.resetConfiguration(terms)
        mw.openMiDict.setText("Close Dictionary " + shortcut)
        show_after_global_search()
    else:
        mw.ankiDictionary.hide()


def show_after_global_search():
    """Show dictionary window after global search."""
    from anki.utils import is_win
    from aqt.qt import Qt
    
    mw.ankiDictionary.activateWindow()
    if not is_win:
        mw.ankiDictionary.setWindowState(
            mw.ankiDictionary.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive
        )
        mw.ankiDictionary.raise_()
    else:
        mw.ankiDictionary.setWindowFlags(
            mw.ankiDictionary.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )
        mw.ankiDictionary.show()
        if not mw.ankiDictionary.alwaysOnTop:
            mw.ankiDictionary.setWindowFlags(
                mw.ankiDictionary.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
            )
            mw.ankiDictionary.show()


def open_dictionary_settings():
    """Open settings window."""
    from .addonSettings import SettingsGui
    from aqt.qt import Qt
    
    addon_path = plugin.get_addon_path()
    
    if not mw.dictSettings:
        mw.dictSettings = SettingsGui(mw, str(addon_path), open_dictionary_settings)
    
    mw.dictSettings.show()
    if mw.dictSettings.windowState() == Qt.WindowState.WindowMinimized:
        mw.dictSettings.setWindowState(Qt.WindowState.WindowNoState)
    mw.dictSettings.setFocus()
    mw.dictSettings.activateWindow()


# Attach legacy functions to mw
mw.dictionaryInit = dictionary_init


# ============================================================================
# Editor Integration
# ============================================================================

def selected_text(page):
    """Get selected text from page."""
    text = page.selectedText()
    return text if text else False


def search_term(self):
    """Search for selected term in dictionary."""
    import re
    text = selected_text(self)
    if text:
        text = re.sub(r'\[[^\]]+?\]', '', text)
        text = text.strip()
        if not mw.ankiDictionary or not mw.ankiDictionary.isVisible():
            dictionary_init([text])
        mw.ankiDictionary.ensureVisible()
        mw.ankiDictionary.initSearch(text)
        if self.title == 'main webview':
            if mw.state == 'review':
                mw.ankiDictionary.dict.setReviewer(mw.reviewer)
        elif self.title == 'editor':
            target = get_target(type(self.parentEditor.parentWindow).__name__)
            mw.ankiDictionary.dict.setCurrentEditor(self.parentEditor, target)
        show_after_global_search()


def search_col(self):
    """Search collection for selected text."""
    import aqt
    from anki.utils import is_win
    from aqt.qt import Qt
    
    text = selected_text(self)
    if text:
        text = text.strip()
        browser = aqt.DialogManager._dialogs["Browser"][1]
        if not browser:
            mw.onBrowse()
            browser = aqt.DialogManager._dialogs["Browser"][1]
        if browser:
            browser.form.searchEdit.lineEdit().setText(text)
            browser.onSearchActivated()
            browser.activateWindow()
            if not is_win:
                browser.setWindowState(browser.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
                browser.raise_()
            else:
                browser.setWindowFlags(browser.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
                browser.show()
                browser.setWindowFlags(browser.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
                browser.show()


def add_to_context_menu(self, m):
    """Add dictionary options to context menu."""
    a = m.addAction("Search (Ctrl+S)")
    a.triggered.connect(self.searchTerm)
    b = m.addAction("Search Collection (Ctrl/⌘+Shift+B)")
    b.triggered.connect(self.searchCol)


def get_target(name):
    """Get target type from window name."""
    if name == 'AddCards':
        return 'Add'
    elif name == "EditCurrent" or name == "DictEditCurrent":
        return 'Edit'
    elif name == 'Browser':
        return name
    return None


# Attach to AnkiWebView
AnkiWebView.searchTerm = search_term
AnkiWebView.searchCol = search_col
mw.searchTerm = search_term
mw.searchCol = search_col


# ============================================================================
# Editor Wrapping and Hooks
# ============================================================================

def bridge_reroute(self, cmd):
    """Reroute bridge commands to handle dictionary integration."""
    if cmd == "bodyClick":
        if mw.ankiDictionary and mw.ankiDictionary.isVisible() and self.note:
            widget = type(self.widget.parentWidget()).__name__
            if widget == 'QWidget':
                widget = 'Browser'
            target = get_target(widget)
            mw.ankiDictionary.dict.setCurrentEditor(self, target)
        if hasattr(mw, "DictEditorLoaded"):
            og_reroute(self, cmd)
    else:
        if cmd.startswith("focus"):
            if mw.ankiDictionary and mw.ankiDictionary.isVisible() and self.note:
                widget = type(self.widget.parentWidget()).__name__
                if widget == 'QWidget':
                    widget = 'Browser'
                target = get_target(widget)
                mw.ankiDictionary.dict.setCurrentEditor(self, target)
        og_reroute(self, cmd)


og_reroute = aqt.editor.Editor.onBridgeCmd
aqt.editor.Editor.onBridgeCmd = bridge_reroute


def set_browser_editor(browser):
    """Set browser editor for dictionary."""
    if mw.ankiDictionary and mw.ankiDictionary.isVisible():
        if browser.editor.note:
            mw.ankiDictionary.dict.setCurrentEditor(browser.editor, 'Browser')
        else:
            mw.ankiDictionary.dict.closeEditor()


def check_current_editor(self):
    """Check if current editor should be closed."""
    if mw.ankiDictionary and mw.ankiDictionary.isVisible():
        mw.ankiDictionary.dict.checkEditorClose(self.editor)


def add_edit_activated(self, event=False):
    """Handle edit window activation."""
    if mw.ankiDictionary and mw.ankiDictionary.isVisible():
        mw.ankiDictionary.dict.setCurrentEditor(self.editor, get_target(type(self).__name__))


body_click = '''document.addEventListener("click", function (ev) {
        pycmd("bodyClick")
    }, false);'''


def add_body_click(self):
    """Add body click handler."""
    self.web.eval(body_click)


def add_hotkeys(self):
    """Add hotkeys to editor window."""
    self.parentWindow.hotkeyS = QShortcut(QKeySequence("Ctrl+S"), self.parentWindow)
    self.parentWindow.hotkeyS.activated.connect(lambda: search_term(self.web))
    self.parentWindow.hotkeyS = QShortcut(QKeySequence("Ctrl+Shift+B"), self.parentWindow)
    self.parentWindow.hotkeyS.activated.connect(lambda: search_col(self.web))
    self.parentWindow.hotkeyW = QShortcut(QKeySequence("Ctrl+W"), self.parentWindow)
    self.parentWindow.hotkeyW.activated.connect(dictionary_init)


def add_hotkeys_to_preview(self):
    """Add hotkeys to preview window."""
    self._web.hotkeyS = QShortcut(QKeySequence("Ctrl+S"), self._web)
    self._web.hotkeyS.activated.connect(lambda: search_term(self._web))
    self._web.hotkeyS = QShortcut(QKeySequence("Ctrl+Shift+B"), self._web)
    self._web.hotkeyS.activated.connect(lambda: search_col(self._web))
    self._web.hotkeyW = QShortcut(QKeySequence("Ctrl+W"), self._web)
    self._web.hotkeyW.activated.connect(dictionary_init)


def add_editor_functionality(self):
    """Add dictionary functionality to editor."""
    self.web.parentEditor = self
    add_body_click(self)
    add_hotkeys(self)


def announce_parent(self, event=False):
    """Announce parent window to dictionary."""
    if mw.ankiDictionary and mw.ankiDictionary.isVisible():
        parent = self.parentWidget().parentWidget().parentWidget()
        p_name = type(parent).__name__
        if p_name not in ['AddCards', 'EditCurrent']:
            parent = aqt.DialogManager._dialogs["Browser"][1]
            p_name = 'Browser'
            if not parent:
                return
        mw.ankiDictionary.dict.setCurrentEditor(parent.editor, get_target(p_name))


def mi_links(self, cmd):
    """Handle reviewer links."""
    if mw.ankiDictionary and mw.ankiDictionary.isVisible():
        mw.ankiDictionary.dict.setReviewer(self)
    return og_links(self, cmd)


# Apply wraps and hooks
Browser.on_current_row_changed = wrap(Browser.on_current_row_changed, set_browser_editor)
AddCards._close = wrap(AddCards._close, check_current_editor)
EditCurrent._saveAndClose = wrap(EditCurrent._saveAndClose, check_current_editor)
Browser._closeWindow = wrap(Browser._closeWindow, check_current_editor)
AddCards.addCards = wrap(AddCards.addCards, add_edit_activated)
AddCards.onHistory = wrap(AddCards.onHistory, add_edit_activated)
Previewer.open = wrap(Previewer.open, add_hotkeys_to_preview)
TagEdit.focusInEvent = wrap(TagEdit.focusInEvent, announce_parent)
aqt.editor.Editor.setupWeb = wrap(aqt.editor.Editor.setupWeb, add_editor_functionality)
AddCards.mousePressEvent = add_edit_activated
EditCurrent.mousePressEvent = add_edit_activated

og_links = Reviewer._linkHandler
Reviewer._linkHandler = mi_links
Reviewer.show = wrap(Reviewer.show, add_body_click)

addHook("EditorWebView.contextMenuEvent", add_to_context_menu)
addHook("AnkiWebView.contextMenuEvent", add_to_context_menu)


# ============================================================================
# Browser Integration
# ============================================================================

def setup_browser_menu(browser):
    """Set up browser menu items."""
    # Import the bulk export functionality
    # This will be refactored into a service in Phase 4
    try:
        from . import main_old_backup
        if hasattr(main_old_backup, 'exportDefinitionsWidget'):
            a = QAction("Export Definitions", browser)
            a.triggered.connect(lambda: main_old_backup.exportDefinitionsWidget(browser))
            browser.form.menuEdit.addSeparator()
            browser.form.menuEdit.addAction(a)
    except (ImportError, AttributeError):
        # If old backup doesn't exist, skip this feature
        pass


addHook("browser.setupMenus", setup_browser_menu)


# ============================================================================
# Menu Setup
# ============================================================================

def setup_gui_menu():
    """Set up the addon menu."""
    add_menu = False
    if not hasattr(mw, 'DictMainMenu'):
        mw.DictMainMenu = QMenu('Dict', mw)
        add_menu = True
    
    if not hasattr(mw, 'DictMenuSettings'):
        mw.DictMenuSettings = []
    if not hasattr(mw, 'DictMenuActions'):
        mw.DictMenuActions = []
    
    setting = QAction("Dictionary Settings", mw)
    setting.triggered.connect(open_dictionary_settings)
    mw.DictMenuSettings.append(setting)
    
    mw.openMiDict = QAction("Open Dictionary (Ctrl+W)", mw)
    mw.openMiDict.triggered.connect(dictionary_init)
    mw.DictMenuActions.append(mw.openMiDict)
    
    mw.DictMainMenu.clear()
    for act in mw.DictMenuSettings:
        mw.DictMainMenu.addAction(act)
    mw.DictMainMenu.addSeparator()
    for act in mw.DictMenuActions:
        mw.DictMainMenu.addAction(act)
    
    if add_menu:
        mw.form.menubar.insertMenu(mw.form.menuHelp.menuAction(), mw.DictMainMenu)


setup_gui_menu()


# ============================================================================
# Global Hotkeys
# ============================================================================

mw.hotkeyW = QShortcut(QKeySequence("Ctrl+W"), mw)
mw.hotkeyW.activated.connect(dictionary_init)

mw.hotkeyS = QShortcut(QKeySequence("Ctrl+S"), mw)
mw.hotkeyS.activated.connect(lambda: search_term(mw.web))

mw.hotkeyS = QShortcut(QKeySequence("Ctrl+Shift+B"), mw)
mw.hotkeyS.activated.connect(lambda: search_col(mw.web))


# Export for other modules
__all__ = ['plugin', 'ankiDict', 'dictionary_init', 'open_dictionary_settings']
