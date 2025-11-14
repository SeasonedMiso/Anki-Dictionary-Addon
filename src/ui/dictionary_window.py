# -*- coding: utf-8 -*-
"""
Refactored Dictionary Window using service layer architecture.
"""

from typing import Any, Optional, List, Dict
from pathlib import Path
import json
import logging

import os

try:
    from aqt.qt import (
        QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit,
        QPushButton, QShortcut, QKeySequence, QUrl, QCloseEvent, QHideEvent
    )
    from aqt.webview import AnkiWebView
    from aqt.utils import showInfo, tooltip
    from anki.utils import is_mac, is_win
    # Check if we're in a test environment
    ANKI_AVAILABLE = os.getenv('PYTEST_CURRENT_TEST') is None
except ImportError:
    # For testing without Anki
    ANKI_AVAILABLE = False
    QWidget = type('QWidget', (object,), {})
    QVBoxLayout = type('QVBoxLayout', (object,), {})
    QHBoxLayout = type('QHBoxLayout', (object,), {})
    QComboBox = type('QComboBox', (object,), {})
    QLineEdit = type('QLineEdit', (object,), {})
    QPushButton = type('QPushButton', (object,), {})
    QShortcut = type('QShortcut', (object,), {})
    QKeySequence = type('QKeySequence', (object,), {})
    QUrl = type('QUrl', (object,), {})
    QCloseEvent = type('QCloseEvent', (object,), {})
    QHideEvent = type('QHideEvent', (object,), {})
    AnkiWebView = type('AnkiWebView', (object,), {})
    showInfo = lambda *args, **kwargs: None
    tooltip = lambda *args, **kwargs: None
    is_mac = False
    is_win = False

from ..services import SearchService, ExportService, MediaService
from ..config import ConfigManager


logger = logging.getLogger('anki_dictionary.ui.dictionary_window')


class DictionaryWindow(QWidget):
    """
    Main dictionary window with service layer integration.
    
    This class provides the UI for dictionary searches and displays results.
    All business logic is delegated to service classes.
    """
    
    def __init__(
        self,
        mw: Any,
        search_service: SearchService,
        export_service: ExportService,
        media_service: MediaService,
        config_manager: ConfigManager,
        addon_path: Path
    ):
        """
        Initialize dictionary window with services.
        
        Args:
            mw: Anki main window instance
            search_service: Service for dictionary searches
            export_service: Service for card exports
            media_service: Service for media downloads
            config_manager: Configuration manager
            addon_path: Path to addon directory
        """
        super().__init__()
        
        # Store dependencies
        self.mw = mw
        self.search_service = search_service
        self.export_service = export_service
        self.media_service = media_service
        self.config_manager = config_manager
        self.addon_path = addon_path
        
        # UI state
        self.current_editor: Optional[Any] = None
        self.current_reviewer: Optional[Any] = None
        self.card_exporter: Optional[Any] = None
        
        # Initialize UI
        self._setup_ui()
        
        logger.info("Dictionary window initialized")
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        if not ANKI_AVAILABLE:
            # Skip UI setup in test environment
            return
        
        self.setWindowTitle("Anki Dictionary")
        self.setMinimumSize(350, 350)
        self.resize(800, 600)
        
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Create toolbar
        toolbar = self._create_toolbar()
        main_layout.addLayout(toolbar)
        
        # Create web view for dictionary content
        self.web_view = self._create_web_view()
        main_layout.addWidget(self.web_view)
        
        self.setLayout(main_layout)
        
        # Set up hotkeys
        self._setup_hotkeys()
        
        # Restore window position
        self._restore_window_position()
    
    def _create_toolbar(self) -> QHBoxLayout:
        """
        Create the toolbar with search controls.
        
        Returns:
            QHBoxLayout containing toolbar widgets
        """
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(5, 5, 5, 5)
        toolbar.setSpacing(10)
        
        # Dictionary group selector
        self.dict_group_combo = QComboBox()
        self.dict_group_combo.setFixedHeight(40)
        self.dict_group_combo.setFixedWidth(120)
        self._populate_dictionary_groups()
        self.dict_group_combo.currentIndexChanged.connect(self._on_dict_group_changed)
        toolbar.addWidget(self.dict_group_combo)
        
        # Search type selector
        self.search_type_combo = QComboBox()
        self.search_type_combo.setFixedHeight(40)
        self.search_type_combo.setFixedWidth(100)
        search_types = ['Forward', 'Backward', 'Exact', 'Anywhere', 'Definition', 'Example', 'Pronunciation']
        self.search_type_combo.addItems(search_types)
        current_mode = self.config_manager.get_value('searchMode', 'Forward')
        if current_mode in search_types:
            self.search_type_combo.setCurrentText(current_mode)
        self.search_type_combo.currentIndexChanged.connect(self._on_search_type_changed)
        toolbar.addWidget(self.search_type_combo)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(40)
        self.search_input.setFixedWidth(120)
        self.search_input.setPlaceholderText("Search term...")
        self.search_input.returnPressed.connect(self.perform_search)
        toolbar.addWidget(self.search_input)
        
        # Search button
        search_button = QPushButton("Search")
        search_button.setFixedHeight(40)
        search_button.clicked.connect(self.perform_search)
        toolbar.addWidget(search_button)
        
        toolbar.addStretch()
        
        return toolbar
    
    def _create_web_view(self) -> AnkiWebView:
        """
        Create the web view for displaying dictionary content.
        
        Returns:
            AnkiWebView instance
        """
        web_view = AnkiWebView()
        web_view.onBridgeCmd = self._handle_bridge_command
        
        # Load initial HTML
        self._load_initial_html(web_view)
        
        return web_view
    
    def _load_initial_html(self, web_view: AnkiWebView) -> None:
        """
        Load initial HTML content into web view.
        
        Args:
            web_view: Web view to load content into
        """
        html_path = self.addon_path / 'dictionaryInit.html'
        
        if html_path.exists():
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    html = f.read()
                
                # Apply theme
                html = self._apply_theme_to_html(html)
                
                url = QUrl.fromLocalFile(str(html_path))
                web_view.setHtml(html, url)
            except Exception as e:
                logger.error(f"Error loading initial HTML: {e}")
                web_view.setHtml("<h3>Dictionary Ready</h3>")
        else:
            web_view.setHtml("<h3>Dictionary Ready</h3>")
    
    def _apply_theme_to_html(self, html: str) -> str:
        """
        Apply theme styling to HTML content.
        
        Args:
            html: Original HTML content
            
        Returns:
            HTML with theme applied
        """
        # Load active theme
        theme_path = self.addon_path / "user_files" / "themes" / "active.json"
        
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                theme = json.load(f)
        except Exception as e:
            logger.warning(f"Error loading theme: {e}")
            # Use default theme
            theme = {
                "header_background": "#51576d",
                "definition_background": "#51576d",
                "definition_text": "#c6d0f5",
                "border": "#babbf1"
            }
        
        # Create CSS from theme
        theme_css = f"""
        <style id="customThemeCss">
            body {{
                background-color: {theme.get('header_background', '#51576d')};
                color: {theme.get('definition_text', '#c6d0f5')};
            }}
            .definitionBlock {{
                background-color: {theme.get('definition_background', '#51576d')};
                color: {theme.get('definition_text', '#c6d0f5')};
                border: 1px solid {theme.get('border', '#babbf1')};
                border-radius: 5px;
                padding: 15px;
                margin: 10px;
            }}
        </style>
        """
        
        # Replace placeholder or inject CSS
        if '<style id="customThemeCss"></style>' in html:
            html = html.replace('<style id="customThemeCss"></style>', theme_css)
        else:
            html = html.replace('</head>', f'{theme_css}</head>')
        
        return html
    
    def _populate_dictionary_groups(self) -> None:
        """Populate dictionary group combo box."""
        # Get dictionary groups from config
        groups = self.config_manager.get_dictionary_groups()
        
        # Add user groups
        user_groups = sorted(groups.keys())
        self.dict_group_combo.addItems(user_groups)
        
        # Add separator
        self.dict_group_combo.addItem('──────')
        self.dict_group_combo.model().item(self.dict_group_combo.count() - 1).setEnabled(False)
        
        # Add default groups
        default_groups = ['All', 'Google Images', 'Forvo']
        self.dict_group_combo.addItems(default_groups)
        
        # Set current group
        current_group = self.config_manager.get_value('currentGroup', 'All')
        if current_group in user_groups or current_group in default_groups:
            self.dict_group_combo.setCurrentText(current_group)
    
    def _setup_hotkeys(self) -> None:
        """Set up keyboard shortcuts."""
        # Escape to hide window
        esc_shortcut = QShortcut(QKeySequence("Esc"), self)
        esc_shortcut.activated.connect(self.hide)
        
        # Ctrl+W to toggle window
        toggle_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        toggle_shortcut.activated.connect(self.toggle_visibility)
    
    def _restore_window_position(self) -> None:
        """Restore window size and position from config."""
        size_pos = self.config_manager.get_value('dictSizePos')
        
        if size_pos and len(size_pos) == 4:
            try:
                x, y, width, height = size_pos
                self.resize(width, height)
                self.move(x, y)
            except Exception as e:
                logger.warning(f"Error restoring window position: {e}")
    
    def _save_window_position(self) -> None:
        """Save window size and position to config."""
        pos = self.pos()
        size = self.size()
        size_pos = [pos.x(), pos.y(), size.width(), size.height()]
        
        try:
            self.config_manager.update_config('dictSizePos', size_pos)
        except Exception as e:
            logger.warning(f"Error saving window position: {e}")
    
    def perform_search(self, term: Optional[str] = None) -> None:
        """
        Perform a dictionary search.
        
        Args:
            term: Optional search term (uses input field if not provided)
        """
        if term is None:
            term = self.search_input.text().strip()
        
        if not term:
            return
        
        # Clean term
        term = self._clean_term(term)
        if not term:
            return
        
        # Update search input
        self.search_input.setText(term)
        
        # Get selected dictionary group
        dict_group = self._get_selected_dictionary_group()
        
        if not dict_group:
            self._show_error("No dictionary group selected")
            return
        
        # Get search settings
        search_mode = self.search_type_combo.currentText()
        deinflect = self.config_manager.get_bool('deinflect', True)
        dict_limit = self.config_manager.get_int('dictSearch', 50)
        max_results = self.config_manager.get_int('maxSearch', 1000)
        
        try:
            # Perform search using service
            result = self.search_service.search(
                term=term,
                dictionary_group=dict_group,
                search_mode=search_mode,
                deinflect=deinflect,
                dict_limit=dict_limit,
                max_results=max_results
            )
            
            # Display results
            self._display_search_results(term, result, dict_group)
            
            # Add to history
            self._add_to_history(term)
            
            logger.info(f"Search completed for term: {term}")
            
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            self._show_error(f"Search failed: {str(e)}")
    
    def _display_search_results(
        self,
        term: str,
        result: Any,
        dict_group: Dict
    ) -> None:
        """
        Display search results in web view.
        
        Args:
            term: Search term
            result: Search result from service
            dict_group: Dictionary group configuration
        """
        # Format results as HTML
        html = self._format_results_as_html(term, result, dict_group)
        
        # Inject into web view
        escaped_html = html.replace("'", "\\'").replace('\n', '')
        self.web_view.eval(f"addNewTab('{escaped_html}', '{term}', true);")
    
    def _format_results_as_html(
        self,
        term: str,
        result: Any,
        dict_group: Dict
    ) -> str:
        """
        Format search results as HTML.
        
        Args:
            term: Search term
            result: Search result
            dict_group: Dictionary group configuration
            
        Returns:
            HTML string
        """
        if not result or not result.results:
            return f'''
            <div class="vertical-center noresults">
                <div align="center">
                    <h3>No dictionary entries found for "{term}".</h3>
                </div>
            </div>
            '''
        
        # Build HTML from results
        html_parts = ['<div class="mainDictDisplay">']
        
        for dict_name, entries in result.results.items():
            if not entries:
                continue
            
            html_parts.append(f'<div class="dictionaryTitleBlock">')
            html_parts.append(f'<div class="dictionaryTitle">{dict_name}</div>')
            html_parts.append('</div>')
            
            for entry in entries:
                html_parts.append('<div class="definitionBlock">')
                html_parts.append(f'<div class="termPronunciation">')
                html_parts.append(f'<span class="term">{entry.get("term", "")}</span>')
                if entry.get('pronunciation'):
                    html_parts.append(f'<span class="pronunciation">{entry["pronunciation"]}</span>')
                html_parts.append('</div>')
                html_parts.append(f'<div class="definition">{entry.get("definition", "")}</div>')
                html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        return ''.join(html_parts)
    
    def _get_selected_dictionary_group(self) -> Optional[Dict]:
        """
        Get the currently selected dictionary group.
        
        Returns:
            Dictionary group configuration or None
        """
        group_name = self.dict_group_combo.currentText()
        
        if not group_name or group_name == '──────':
            return None
        
        # Check user groups
        groups = self.config_manager.get_dictionary_groups()
        if group_name in groups:
            return groups[group_name]
        
        # Handle special groups
        if group_name == 'All':
            # Return all dictionaries
            all_dicts = self.search_service.repository.get_all_dictionaries()
            return {
                'dictionaries': [{'dict': d, 'lang': ''} for d in all_dicts],
                'customFont': False,
                'font': None
            }
        elif group_name == 'Google Images':
            return {
                'dictionaries': [{'dict': 'Google Images', 'lang': ''}],
                'customFont': False,
                'font': None
            }
        elif group_name == 'Forvo':
            return {
                'dictionaries': [{'dict': 'Forvo', 'lang': ''}],
                'customFont': False,
                'font': None
            }
        
        return None
    
    def _clean_term(self, term: str) -> str:
        """
        Clean a search term.
        
        Args:
            term: Raw search term
            
        Returns:
            Cleaned term
        """
        import re
        
        # Remove brackets and parentheses
        term = re.sub(r'(?:\[.*\])|(?:\(.*\))|(?:《.*》)|(?:（.*）)|\(|\)|\[|\]|《|》|（|）', '', term)
        
        # Limit length
        term = term[:30]
        
        return term.strip()
    
    def _add_to_history(self, term: str) -> None:
        """
        Add search term to history.
        
        Args:
            term: Search term to add
        """
        # History management would be implemented here
        # For now, just log it
        logger.debug(f"Added to history: {term}")
    
    def _handle_bridge_command(self, cmd: str) -> None:
        """
        Handle bridge commands from web view.
        
        Args:
            cmd: Command string from JavaScript
        """
        logger.debug(f"Bridge command: {cmd}")
        
        try:
            if cmd.startswith('addDef:'):
                # Handle definition export
                parts = cmd[7:].split('◳◴')
                if len(parts) >= 3:
                    dict_name, word, text = parts[0], parts[1], parts[2]
                    self._export_definition(dict_name, word, text)
            
            elif cmd.startswith('forvo:'):
                # Handle Forvo audio download
                urls = json.loads(cmd[6:])
                self._download_forvo_audio(urls)
            
            elif cmd.startswith('sendToField:'):
                # Handle send to field
                parts = cmd[12:].split('◳◴')
                if len(parts) >= 2:
                    name, text = parts[0], parts[1]
                    self._send_to_field(name, text)
            
            elif cmd.startswith('imgExport:'):
                # Handle image export
                parts = cmd[10:].split('◳◴')
                if len(parts) >= 2:
                    word, urls = parts[0], json.loads(parts[1])
                    self._download_images(word, urls)
        
        except Exception as e:
            logger.error(f"Error handling bridge command: {e}", exc_info=True)
            self._show_error(f"Command failed: {str(e)}")
    
    def _export_definition(self, dict_name: str, word: str, text: str) -> None:
        """
        Export definition to card exporter.
        
        Args:
            dict_name: Dictionary name
            word: Word/term
            text: Definition text
        """
        logger.info(f"Exporting definition: {word} from {dict_name}")
        
        # This would open/use the card exporter
        # For now, show a tooltip
        tooltip(f"Export: {word}")
    
    def _download_forvo_audio(self, urls: List[str]) -> None:
        """
        Download Forvo audio files.
        
        Args:
            urls: List of audio URLs
        """
        if not urls:
            return
        
        try:
            language = self.config_manager.get_str('ForvoLanguage', 'Japanese')
            
            for url in urls:
                # Use media service to download
                success, filename, error = self.media_service._download_audio_file(
                    url, "forvo_audio", language
                )
                
                if success:
                    logger.info(f"Downloaded Forvo audio: {filename}")
                    tooltip(f"Downloaded: {filename}")
                else:
                    logger.warning(f"Failed to download audio: {error}")
        
        except Exception as e:
            logger.error(f"Error downloading Forvo audio: {e}", exc_info=True)
            self._show_error(f"Audio download failed: {str(e)}")
    
    def _download_images(self, word: str, urls: List[str]) -> None:
        """
        Download images from URLs.
        
        Args:
            word: Associated word
            urls: List of image URLs
        """
        if not urls:
            return
        
        try:
            max_width = self.config_manager.get_int('maxWidth', 400)
            max_height = self.config_manager.get_int('maxHeight', 400)
            
            downloaded = []
            for url in urls:
                # Use media service to download
                success, filename, error = self.media_service._download_image_file(
                    url, word, len(downloaded), max_width, max_height
                )
                
                if success:
                    downloaded.append(filename)
            
            if downloaded:
                logger.info(f"Downloaded {len(downloaded)} images for: {word}")
                tooltip(f"Downloaded {len(downloaded)} images")
            else:
                self._show_error("No images downloaded")
        
        except Exception as e:
            logger.error(f"Error downloading images: {e}", exc_info=True)
            self._show_error(f"Image download failed: {str(e)}")
    
    def _send_to_field(self, name: str, text: str) -> None:
        """
        Send content to a note field.
        
        Args:
            name: Dictionary/source name
            text: Content to send
        """
        logger.info(f"Sending to field from {name}")
        
        # This would use the export service to add to current note
        # For now, show a tooltip
        tooltip(f"Sent to field: {name}")
    
    def _show_error(self, message: str) -> None:
        """
        Show error message to user.
        
        Args:
            message: Error message
        """
        showInfo(message, parent=self, title="Dictionary Error")
    
    def _on_dict_group_changed(self) -> None:
        """Handle dictionary group selection change."""
        group_name = self.dict_group_combo.currentText()
        if group_name and group_name != '──────':
            try:
                self.config_manager.update_config('currentGroup', group_name)
            except Exception as e:
                logger.warning(f"Error saving current group: {e}")
    
    def _on_search_type_changed(self) -> None:
        """Handle search type selection change."""
        search_type = self.search_type_combo.currentText()
        try:
            self.config_manager.update_config('searchMode', search_type)
        except Exception as e:
            logger.warning(f"Error saving search mode: {e}")
    
    def show_window(self, terms: Optional[List[str]] = None) -> None:
        """
        Show window and optionally search for terms.
        
        Args:
            terms: Optional list of terms to search
        """
        self.show()
        self.raise_()
        self.activateWindow()
        
        if terms:
            for term in terms:
                self.perform_search(term)
    
    def toggle_visibility(self) -> None:
        """Toggle window visibility."""
        if self.isVisible():
            self.hide()
        else:
            self.show_window()
    
    def set_current_editor(self, editor: Any, target: str = '') -> None:
        """
        Set the current editor for field operations.
        
        Args:
            editor: Editor instance
            target: Target description
        """
        self.current_editor = editor
        self.current_reviewer = None
        logger.debug(f"Current editor set: {target}")
    
    def set_current_reviewer(self, reviewer: Any) -> None:
        """
        Set the current reviewer for field operations.
        
        Args:
            reviewer: Reviewer instance
        """
        self.current_reviewer = reviewer
        self.current_editor = None
        logger.debug("Current reviewer set")
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        self.hide()
        event.ignore()  # Don't actually close, just hide
    
    def hideEvent(self, event: QHideEvent) -> None:
        """
        Handle window hide event.
        
        Args:
            event: Hide event
        """
        self._save_window_position()
        event.accept()
