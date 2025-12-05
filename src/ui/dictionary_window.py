# -*- coding: utf-8 -*-
"""
Refactored Dictionary Window using service layer architecture.
"""

from typing import Any, Optional, List, Dict
from pathlib import Path
import json
import logging
import time
import os

try:
    from aqt.qt import (
        QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit,
        QPushButton, QShortcut, QKeySequence, QUrl, QCloseEvent, QHideEvent
    )
    from aqt.webview import AnkiWebView, AnkiWebViewKind
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
    # Mock AnkiWebViewKind for testing
    class AnkiWebViewKind:
        EDITOR = 'editor'
        DEFAULT = 'default'
    showInfo = lambda *args, **kwargs: None
    tooltip = lambda *args, **kwargs: None
    is_mac = False
    is_win = False

from ..services import SearchService, ExportService, MediaService
from ..config import ConfigManager
from ..utils.logging_config import (
    get_logger,
    log_html_content,
    log_svg_load,
    log_bridge_command,
    log_window_state
)


logger = get_logger('ui.dictionary_window')


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
        Create the web view with modern Anki 25.x API.
        
        CRITICAL: Must use kind=ADDON to enable pycmd bridge.
        Without kind parameter, Anki uses legacy mode with no bridge.
        
        Returns:
            AnkiWebView instance with working pycmd bridge
        """
        import inspect
        
        # Debug: log Anki version
        try:
            anki_version = getattr(self.mw, 'version', 'unknown')
            logger.info(f"Anki version: {anki_version}")
        except Exception:
            logger.info("Could not determine Anki version")
        
        # Debug: inspect constructor signature
        try:
            sig = inspect.signature(AnkiWebView.__init__)
            logger.info(f"AnkiWebView.__init__ signature: {sig}")
        except Exception:
            logger.info("Could not inspect AnkiWebView.__init__")
        
        # Log available kinds for debugging
        try:
            available_kinds = [k.name for k in AnkiWebViewKind]
            logger.info(f"Available AnkiWebViewKind values: {available_kinds}")
        except Exception:
            logger.info("Could not enumerate AnkiWebViewKind values")
        
        # Use EDITOR kind (enables pycmd bridge and is available in all versions)
        # EDITOR is the most appropriate for add-on UIs that need bridge access
        try:
            web_view = AnkiWebView(
                parent=self,
                title="dictionary",
                kind=AnkiWebViewKind.EDITOR
            )
            logger.info("✓ Created AnkiWebView with kind=EDITOR")
            
            # Set bridge command handler using the correct API
            web_view.set_bridge_command(self._handle_bridge_command, self)
            logger.info("✓ Set bridge command handler")
            
        except Exception as e:
            logger.error(f"Failed to create modern WebView: {e}", exc_info=True)
            raise RuntimeError(
                f"Failed to create AnkiWebView: {e}\n"
                "This add-on requires Anki 23.10 or later."
            )
        
        # Verify bridge is set up
        has_onBridgeCmd = callable(getattr(web_view, 'onBridgeCmd', None))
        logger.info(f"web_view has onBridgeCmd callable: {has_onBridgeCmd}")
        
        if not has_onBridgeCmd:
            logger.warning("onBridgeCmd is not callable - bridge may not work!")
        
        # Load initial HTML
        self._load_initial_html(web_view)
        
        return web_view
    
    def _load_initial_html(self, web_view: AnkiWebView) -> None:
        """
        Load initial HTML content into web view.
        
        Args:
            web_view: Web view to load content into
        """
        # Try multiple possible locations for the HTML file
        possible_paths = [
            self.addon_path / 'dictionaryInit.html',
            self.addon_path / 'docs' / 'dictionaryInit.html',
        ]
        
        html_path = None
        for path in possible_paths:
            if path.exists():
                html_path = path
                break
        
        if html_path:
            try:
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Apply theme
                html_content = self._apply_theme_to_html(html_content)
                
                # Use setHtml with proper base_url (required for modern mode)
                # The pycmd bridge is already set up via kind=ADDON in constructor
                # CRITICAL: Must use setHtml, NOT stdHtml (which forces legacy mode)
                base_url = QUrl.fromLocalFile(str(html_path.parent) + '/')
                web_view.setHtml(html_content, base_url)
                logger.info(f"✓ Loaded HTML from {html_path} with base URL: {base_url.toString()}")
            except Exception as e:
                logger.error(f"Error loading initial HTML: {e}", exc_info=True)
                # Fallback
                web_view.setHtml("<h3>Dictionary Ready</h3>")
        else:
            logger.warning(f"dictionaryInit.html not found in {possible_paths}, using fallback")
            # Use a more visible fallback with styling
            fallback_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        background-color: #2d2d2d;
                        color: #ffffff;
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }}
                    .message {{
                        text-align: center;
                        padding: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="message">
                    <h2>Dictionary Ready</h2>
                    <p>HTML template not found. Please check installation.</p>
                    <p style="font-size: 12px; color: #888;">Searched: {}</p>
                </div>
            </body>
            </html>
            """.format(', '.join(str(p) for p in possible_paths))
            
            # Use setHtml (pycmd bridge already set up via kind=EDITOR)
            web_view.setHtml(fallback_html)
    
    def _apply_theme_to_html(self, html: str) -> str:
        """
        Apply theme styling to HTML content and inject SVG icons.
        
        Args:
            html: Original HTML content
            
        Returns:
            HTML with theme applied and SVG icons injected
        """
        # Load active theme
        theme_path = self.addon_path / "user_files" / "themes" / "active.json"
        
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                theme = json.load(f)
        except Exception as e:
            logger.warning(f"Error loading theme: {e}")
            # Use default dark theme matching CSS variables
            theme = {
                "name": "Default Dark",
                "header_background": "#1a1a1a",
                "definition_background": "#2a2a2a",
                "definition_text": "#ffffff",
                "border": "#444444",
                "selector": "#2a2a2a",
                "header_text": "#ffffff",
                "search_term": "#4a9eff"
            }
        
        # Determine if night mode
        theme_mode = 'night' if theme.get('name', '').lower().find('night') >= 0 else 'day'
        
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
        
        # Inject SVG icons
        html = self._inject_svg_icons_into_html(html, theme_mode)
        
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
        
        # Debug logging
        logger.info(f"Dictionary group: {dict_group}")
        logger.info(f"Dictionaries type: {type(dict_group.get('dictionaries', []))}")
        if dict_group.get('dictionaries'):
            logger.info(f"First dictionary: {dict_group['dictionaries'][0]}")
            logger.info(f"First dictionary type: {type(dict_group['dictionaries'][0])}")
        
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
        
        # Log HTML rendering
        log_html_content(logger, html, term=term, max_length=1000)
        
        # Try to use JavaScript tab system if available
        try:
            # Escape HTML for JavaScript
            escaped_html = html.replace("\\", "\\\\").replace("'", "\\'").replace('\n', ' ').replace('\r', '')
            escaped_term = term.replace("\\", "\\\\").replace("'", "\\'")
            
            # Use setTimeout to ensure DOM is ready
            js_code = f"""
            (function() {{
                if (typeof addNewTab === 'function') {{
                    addNewTab('{escaped_html}', '{escaped_term}', true);
                }} else {{
                    console.error('addNewTab function not available');
                }}
            }})();
            """
            self.web_view.eval(js_code)
            logger.debug(f"Used JavaScript tab system for term: {term}")
        except Exception as e:
            logger.warning(f"Failed to use tab system, falling back to direct HTML: {e}")
            # Fallback: display results directly
            full_html = self._create_standalone_results_html(term, html)
            self.web_view.setHtml(full_html)
            logger.debug(f"Used direct HTML rendering for term: {term}")
    
    def _create_standalone_results_html(self, term: str, results_html: str) -> str:
        """
        Create standalone HTML for displaying results without tab system.
        
        Args:
            term: Search term
            results_html: Formatted results HTML
            
        Returns:
            Complete HTML document
        """
        theme = self._load_theme()
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    background-color: {theme.get('header_background', '#51576d')};
                    color: {theme.get('definition_text', '#c6d0f5')};
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 10px;
                }}
                .search-term {{
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                    background-color: {theme.get('selector', '#51576d')};
                    margin-bottom: 10px;
                }}
                .definitionBlock {{
                    background-color: {theme.get('definition_background', '#51576d')};
                    color: {theme.get('definition_text', '#c6d0f5')};
                    border: 1px solid {theme.get('border', '#babbf1')};
                    border-radius: 5px;
                    padding: 15px;
                    margin: 10px 0;
                }}
                .dictionaryTitleBlock {{
                    font-size: 18px;
                    font-weight: bold;
                    margin-top: 20px;
                    margin-bottom: 10px;
                    color: {theme.get('header_text', '#c6d0f5')};
                }}
                .termPronunciation {{
                    font-size: 16px;
                    margin-bottom: 10px;
                }}
                .term {{
                    font-weight: bold;
                    margin-right: 10px;
                }}
                .pronunciation {{
                    color: {theme.get('search_term', '#c6d0f5')};
                }}
                .definition {{
                    line-height: 1.6;
                }}
            </style>
        </head>
        <body>
            <div class="search-term">Search: {term}</div>
            {results_html}
        </body>
        </html>
        """
    
    def _load_theme(self) -> Dict:
        """Load theme configuration."""
        theme_path = self.addon_path / "user_files" / "themes" / "active.json"
        
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading theme: {e}")
            # Use default dark theme matching CSS variables
            return {
                "name": "Default Dark",
                "header_background": "#1a1a1a",
                "definition_background": "#2a2a2a",
                "definition_text": "#ffffff",
                "border": "#444444",
                "header_text": "#ffffff",
                "search_term": "#4a9eff",
                "selector": "#2a2a2a"
            }
    
    def _load_svg_icon(self, icon_name: str, theme: str = 'day') -> Optional[str]:
        """
        Load SVG icon from file with comprehensive logging.
        
        Args:
            icon_name: Name of the icon (without extension)
            theme: Theme variant ('day' or 'night')
            
        Returns:
            SVG content as string, or None if loading failed
        """
        # Construct icon path based on theme
        if theme == 'night':
            icon_filename = f"{icon_name}night.svg"
        else:
            icon_filename = f"{icon_name}.svg"
        
        icon_path = self.addon_path / 'icons' / 'dictsvgs' / icon_filename
        
        try:
            if not icon_path.exists():
                log_svg_load(logger, icon_name, icon_path, False, "File not found")
                return None
            
            with open(icon_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            log_svg_load(logger, icon_name, icon_path, True)
            return svg_content
            
        except Exception as e:
            log_svg_load(logger, icon_name, icon_path, False, str(e))
            return None
    
    def _inject_svg_icons_into_html(self, html: str, theme: str = 'day') -> str:
        """
        Inject SVG icons into HTML template.
        
        Args:
            html: HTML content
            theme: Theme variant ('day' or 'night')
            
        Returns:
            HTML with SVG icons injected
        """
        # List of SVG icons to load
        svg_icons = [
            'search', 'settings', 'conjugation', 'history', 
            'theme', 'tabs', 'plus', 'minus', 
            'sidebaropen', 'sidebarclose', 'onetab', 'closedcube'
        ]
        
        # Load all SVG icons
        svg_data = {}
        for icon_name in svg_icons:
            svg_content = self._load_svg_icon(icon_name, theme)
            if svg_content:
                svg_data[icon_name] = svg_content
        
        # Inject SVG data as JavaScript variable
        svg_js = '<script id="svgIcons">var svgIcons = ' + json.dumps(svg_data) + ';</script>'
        
        # Insert before closing head tag
        if '</head>' in html:
            html = html.replace('</head>', f'{svg_js}</head>')
        else:
            # Fallback: insert at beginning of body
            html = svg_js + html
        
        return html
    
    def switch_theme(self, theme: str) -> None:
        """
        Switch dictionary window theme.
        
        Args:
            theme: Theme name ('day' or 'night')
        """
        try:
            # Update theme in config
            self.config_manager.update_config('theme', theme)
            
            # Reload HTML with new theme
            self._load_initial_html(self.web_view)
            
            # Notify JavaScript of theme change
            is_night = theme == 'night'
            self.web_view.eval(f"nightModeToggle({str(is_night).lower()})")
            
            logger.info(f"Theme switched to: {theme}")
            
        except Exception as e:
            logger.error(f"Error switching theme: {e}", exc_info=True)
    
    def _format_results_as_html(
        self,
        term: str,
        result: Any,
        dict_group: Dict
    ) -> str:
        """
        Format search results as HTML matching pre-refactor structure.
        
        This method replicates the exact HTML structure from the pre-refactor
        prepareResults() method to ensure JavaScript compatibility.
        
        Args:
            term: Search term
            result: Search result
            dict_group: Dictionary group configuration
            
        Returns:
            HTML string with exact pre-refactor structure
        """
        if not result or not result.results:
            return f'''<style>.noresults{{font-family: Arial;}}.vertical-center{{height: 400px; width: 60%; margin: 0 auto; display: flex; justify-content: center; align-items: center;}}</style> </head> <div class="vertical-center noresults"> <div align="center"> <img ankiDict="icons/searchzero.svg" width="50px" height="40px"> <h3 align="center">No dictionary entries were found for "{term}".</h3> </div></div>'''
        
        # Get configuration values
        front_bracket = self.config_manager.get_value('frontBracket', '【')
        back_bracket = self.config_manager.get_value('backBracket', '】')
        font = self._get_font_style(dict_group)
        tooltips_enabled = self.config_manager.get_bool('tooltips', True)
        
        # Build HTML from results
        # Start with sidebar
        html_parts = [self._get_sidebar_html(result.results, term, font, front_bracket, back_bracket)]
        html_parts.append('<div class="mainDictDisplay">')
        
        # Tooltip texts
        img_tooltip = ' title="Add this definition, or any selected text and this definition\'s header to the card exporter (opens the card exporter if it is not yet opened)." ' if tooltips_enabled else ''
        clip_tooltip = ' title="Copy this definition, or any selected text to the clipboard." ' if tooltips_enabled else ''
        send_tooltip = ' title="Send this definition, or any selected text and this definition\'s header to the card exporter to this dictionary\'s target fields. It will send it to the current target window, be it an Editor window, or the Review window." ' if tooltips_enabled else ''
        
        dict_index = 0
        entry_index = 0
        
        for dict_name, entries in result.results.items():
            if not entries:
                continue
            
            # Handle special dictionaries (Google Images, Forvo)
            if dict_name == 'Google Images':
                html_parts.append(self._get_google_images_html(term, dict_index, front_bracket, back_bracket, entry_index, font))
                dict_index += 1
                entry_index += 1
                continue
            
            if dict_name == 'Forvo':
                html_parts.append(self._get_forvo_html(term, dict_index, front_bracket, back_bracket, entry_index, font))
                dict_index += 1
                entry_index += 1
                continue
            
            # Regular dictionary
            # Dictionary title block with settings
            duplicate_header_cb = self._get_duplicate_header_cb(dict_name)
            overwrite_checks = self._get_overwrite_checks(dict_index, dict_name)
            field_checks = self._get_field_checks(dict_name)
            
            html_parts.append(f'<div data-index="{dict_index}" class="dictionaryTitleBlock">')
            html_parts.append(f'<div {font} class="dictionaryTitle">{dict_name.replace("_", " ")}</div>')
            html_parts.append(f'<div class="dictionarySettings">{duplicate_header_cb}{overwrite_checks}{field_checks}')
            html_parts.append('<div class="dictNav"><div onclick="navigateDict(event, false)" class="prevDict">▲</div><div onclick="navigateDict(event, true)" class="nextDict">▼</div></div>')
            html_parts.append('</div></div>')
            
            dict_index += 1
            
            # Process entries
            for entry in entries:
                # Convert DictionaryEntry to dict
                if hasattr(entry, 'to_dict'):
                    entry_dict = entry.to_dict()
                elif isinstance(entry, dict):
                    entry_dict = entry
                else:
                    continue
                
                # Get entry data
                entry_term = entry_dict.get('term', '')
                entry_altterm = entry_dict.get('altterm', '')
                entry_pronunciation = entry_dict.get('pronunciation', '')
                entry_definition = entry_dict.get('definition', '')
                star_count = entry_dict.get('starCount', '')
                
                # Format term header
                term_header = self._get_prepared_term_header(
                    dict_name, front_bracket, back_bracket, term,
                    entry_term, entry_altterm, entry_pronunciation, sb=False
                )
                
                # Highlight target term and examples in definition
                highlighted_def = self._highlight_target(self._highlight_examples(entry_definition), term)
                
                # Build entry HTML
                html_parts.append(f'<div data-index="{entry_index}" class="termPronunciation">')
                html_parts.append(f'<span {font} class="tpCont">{term_header} <span class="starcount">{star_count}</span></span>')
                html_parts.append('<div class="defTools">')
                html_parts.append(f'<div onclick="ankiExport(event, \'{dict_name}\')" class="ankiExportButton"><img {img_tooltip} ankiDict="icons/anki.png"></div>')
                html_parts.append(f'<div onclick="clipText(event)" {clip_tooltip} class="clipper">✂</div>')
                html_parts.append(f'<div {send_tooltip} onclick="sendToField(event, \'{dict_name}\')" class="sendToField">➠</div>')
                html_parts.append('<div class="defNav"><div onclick="navigateDef(event, false)" class="prevDef">▲</div><div onclick="navigateDef(event, true)" class="nextDef">▼</div></div>')
                html_parts.append('</div></div>')
                html_parts.append(f'<div{font} class="definitionBlock">{highlighted_def}</div>')
                
                entry_index += 1
        
        html_parts.append('</div>')  # Close mainDictDisplay
        
        # Escape single quotes for JavaScript
        return ''.join(html_parts).replace("'", "\\'")
    
    def _get_font_style(self, dict_group: Dict) -> str:
        """
        Get font style attribute for HTML elements.
        
        Args:
            dict_group: Dictionary group configuration
            
        Returns:
            Font style string for HTML attribute
        """
        if not dict_group.get('font'):
            return ' '
        
        font_name = dict_group['font']
        if dict_group.get('customFont'):
            # Remove file extension for custom fonts
            import re
            font_name = re.sub(r'\..*$', '', font_name)
        
        return f' style="font-family:{font_name};" '
    
    def _get_sidebar_html(self, results: Dict, term: str, font: str, front_bracket: str, back_bracket: str) -> str:
        """
        Generate sidebar HTML with dictionary and entry navigation.
        
        Args:
            results: Dictionary results
            term: Search term
            font: Font style string
            front_bracket: Front bracket character
            back_bracket: Back bracket character
            
        Returns:
            Sidebar HTML string
        """
        html = f'<div{font}class="definitionSideBar"><div class="innerSideBar">'
        dict_count = 0
        entry_count = 0
        
        for dict_name, dict_results in results.items():
            if dict_name == 'Google Images' or dict_name == 'Forvo':
                html += f'<div data-index="{dict_count}" class="listTitle">{dict_name}</div>'
                html += f'<ol class="foundEntriesList"><li data-index="{entry_count}">'
                html += self._get_prepared_term_header(dict_name, front_bracket, back_bracket, term, term, term, term, sb=True)
                html += '</li></ol>'
                entry_count += 1
                dict_count += 1
                continue
            
            html += f'<div data-index="{dict_count}" class="listTitle">{dict_name}</div>'
            html += '<ol class="foundEntriesList">'
            dict_count += 1
            
            for entry in dict_results:
                entry_dict = entry.to_dict() if hasattr(entry, 'to_dict') else entry
                html += f'<li data-index="{entry_count}">'
                html += self._get_prepared_term_header(
                    dict_name, front_bracket, back_bracket, term,
                    entry_dict.get('term', ''),
                    entry_dict.get('altterm', ''),
                    entry_dict.get('pronunciation', ''),
                    sb=True
                )
                html += '</li>'
                entry_count += 1
            
            html += '</ol>'
        
        return html + '<br></div><div class="resizeBar" onmousedown="hresize(event)"></div></div>'
    
    def _get_prepared_term_header(self, dict_name: str, front_bracket: str, back_bracket: str,
                                   target: str, term: str, altterm: str, pronunciation: str, sb: bool = False) -> str:
        """
        Format term header with pronunciation and highlighting.
        
        Args:
            dict_name: Dictionary name
            front_bracket: Front bracket character
            back_bracket: Back bracket character
            target: Target term for highlighting
            term: Entry term
            altterm: Alternative term
            pronunciation: Pronunciation
            sb: Whether this is for sidebar (True) or main display (False)
            
        Returns:
            Formatted term header HTML
        """
        alt_fb = front_bracket
        alt_bb = back_bracket
        
        # Clean up duplicates
        if pronunciation == term:
            pronunciation = ''
        if altterm == term:
            altterm = ''
        if altterm == '':
            alt_fb = ''
            alt_bb = ''
        
        # Use default header format for special dictionaries
        if dict_name == 'Google Images' or dict_name == 'Forvo':
            if sb:
                header = '◳f<span class="term mainword">◳t</span>◳b◳x<span class="altterm  mainword">◳a</span>◳y<span class="pronunciation">◳p</span>'
            else:
                header = '◳f<span class="listTerm">◳t</span>◳b◳x<span class="listAltTerm">◳a</span>◳y<span class="listPronunciation">◳p</span>'
        else:
            # Use configured term headers if available
            # For now, use default format
            if sb:
                header = '◳f<span class="listTerm">◳t</span>◳b◳x<span class="listAltTerm">◳a</span>◳y<span class="listPronunciation">◳p</span>'
            else:
                header = '◳f<span class="term mainword">◳t</span>◳b◳x<span class="altterm  mainword">◳a</span>◳y<span class="pronunciation mainword">◳p</span>'
        
        # Replace placeholders with actual values
        return (header
                .replace('◳t', self._highlight_target(term, target))
                .replace('◳a', self._highlight_target(altterm, target))
                .replace('◳p', self._highlight_target(pronunciation, target))
                .replace('◳f', front_bracket)
                .replace('◳b', back_bracket)
                .replace('◳x', alt_fb)
                .replace('◳y', alt_bb))
    
    def _highlight_target(self, text: str, term: str) -> str:
        """
        Highlight target term in text.
        
        Args:
            text: Text to highlight in
            term: Term to highlight
            
        Returns:
            Text with highlighted term
        """
        if not self.config_manager.get_bool('highlightTarget', True):
            return text
        
        if not isinstance(text, str):
            text = str(text) if text is not None else ""
        
        try:
            import re
            # Split text into HTML tags and content
            parts = re.split(r'(<[^>]*>)', text)
            
            # Only apply highlighting to non-tag parts
            for i in range(0, len(parts), 2):
                if parts[i]:
                    # For Japanese text, we don't need word boundaries
                    if any('\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in term):
                        pattern = '(' + self._escape_punctuation(term) + ')'
                    else:
                        # For non-Japanese text, keep word boundaries
                        pattern = r'\b(' + self._escape_punctuation(term) + r')\b'
                    
                    parts[i] = re.sub(pattern, r'<span class="targetTerm">\1</span>', parts[i])
            
            return ''.join(parts)
        except Exception as e:
            logger.error(f"Error during highlightTarget: {e}")
            return text
    
    def _escape_punctuation(self, term: str) -> str:
        """Escape regex special characters in term."""
        import re
        return re.sub(r'([.*+(\[\]{}\\?)!])', r'\\\1', term)
    
    def _highlight_examples(self, text: str) -> str:
        """
        Highlight example sentences in text.
        
        Args:
            text: Text to highlight examples in
            
        Returns:
            Text with highlighted examples
        """
        if not self.config_manager.get_bool('highlightSentences', True):
            return text
        
        import re
        return re.sub(
            r'「([^」]+)」(?![^<]*>)',
            r'<span class="exampleSentence">「\1」</span>',
            text
        )
    
    def _get_duplicate_header_cb(self, dict_name: str) -> str:
        """
        Generate duplicate header checkbox HTML.
        
        Args:
            dict_name: Dictionary name
            
        Returns:
            Checkbox HTML string
        """
        tooltip = ''
        if self.config_manager.get_bool('tooltips', True):
            tooltip = ' title="Enable this option if this dictionary has the target word\'s header within the definition. Enabling this will prevent the addon from exporting duplicate header."'
        
        checked = ' '
        class_name = 'checkDict' + dict_name.replace(' ', '')
        
        # Check if this dictionary has duplicate header setting
        # For now, default to unchecked
        # TODO: Load from database
        
        return f'<div class="dupHeadCB" data-dictname="{dict_name}">Duplicate Header:<input {checked}{tooltip} class="{class_name}" onclick="handleDupChange(this, \'{class_name}\')" type="checkbox"></div>'
    
    def _get_overwrite_checks(self, dict_count: int, dict_name: str) -> str:
        """
        Generate overwrite type selector HTML.
        
        Args:
            dict_count: Dictionary index
            dict_name: Dictionary name
            
        Returns:
            Overwrite selector HTML string
        """
        # Get add type from config or database
        if dict_name == 'Google Images':
            add_type = self.config_manager.get_value('GoogleImageAddType', 'add')
        elif dict_name == 'Forvo':
            add_type = self.config_manager.get_value('ForvoAddType', 'add')
        else:
            # TODO: Load from database
            add_type = 'add'
        
        tooltip = ''
        if self.config_manager.get_bool('tooltips', True):
            tooltip = ' title="This determines the conditions for sending a definition (or a Google Image) to a field. Overwrite the target field\'s content. Add to the target field\'s current contents. Only add definitions to the target field if it is empty."'
        
        if add_type == 'add':
            type_name = '&nbsp;Add'
        elif add_type == 'overwrite':
            type_name = '&nbsp;Overwrite'
        elif add_type == 'no':
            type_name = '&nbsp;If Empty'
        else:
            type_name = '&nbsp;Add'
        
        select = (
            f'<div class="overwriteSelectCont"><div {tooltip} class="overwriteSelect" onclick="showCheckboxes(event)">{type_name}</div>' +
            self._get_selected_overwrite_type(dict_count, dict_name, add_type) + '</div>'
        )
        return select
    
    def _get_selected_overwrite_type(self, dict_count: int, dict_name: str, add_type: str) -> str:
        """
        Generate overwrite type radio buttons.
        
        Args:
            dict_count: Dictionary index
            dict_name: Dictionary name
            add_type: Current add type
            
        Returns:
            Radio buttons HTML string
        """
        count = str(dict_count)
        
        checked_add = ' checked' if add_type == 'add' else ''
        checked_overwrite = ' checked' if add_type == 'overwrite' else ''
        checked_no = ' checked' if add_type == 'no' else ''
        
        add = f'<label class="inCheckBox"><input{checked_add} onclick="handleAddTypeCheck(this)" class="inCheckBox radio{dict_name}" type="radio" name="{count}{dict_name}" value="add"/>Add</label>'
        overwrite = f'<label class="inCheckBox"><input{checked_overwrite} onclick="handleAddTypeCheck(this)" class="inCheckBox radio{dict_name}" type="radio" name="{count}{dict_name}" value="overwrite"/>Overwrite</label>'
        ifempty = f'<label class="inCheckBox"><input{checked_no} onclick="handleAddTypeCheck(this)" class="inCheckBox radio{dict_name}" type="radio" name="{count}{dict_name}" value="no"/>If Empty</label>'
        
        return f'<div class="overwriteCheckboxes" data-dictname="{dict_name}">{add}{overwrite}{ifempty}</div>'
    
    def _get_field_checks(self, dict_name: str) -> str:
        """
        Generate field selection checkboxes HTML.
        
        Args:
            dict_name: Dictionary name
            
        Returns:
            Field selector HTML string
        """
        # Get selected fields from config or database
        if dict_name == 'Google Images':
            sel_fields = self.config_manager.get_value('GoogleImageFields', [])
        elif dict_name == 'Forvo':
            sel_fields = self.config_manager.get_value('ForvoFields', [])
        else:
            # TODO: Load from database
            sel_fields = []
        
        tooltip = ''
        if self.config_manager.get_bool('tooltips', True):
            tooltip = ' title="Select this dictionary\'s target fields for when sending a definition(or a Google Image) to a card. If a field does not exist in the target card, then it is ignored, otherwise the definition is added to all fields that exist within the target card."'
        
        title = '&nbsp;Select Fields ▾'
        length = len(sel_fields)
        if length > 0:
            title = f'&nbsp;{length} Selected'
        
        select = (
            f'<div class="fieldSelectCont"><div class="fieldSelect" {tooltip} onclick="showCheckboxes(event)">{title}</div>' +
            self._get_checkboxes(dict_name, sel_fields) + '</div>'
        )
        return select
    
    def _get_checkboxes(self, dict_name: str, sel_fields: list) -> str:
        """
        Generate field checkboxes.
        
        Args:
            dict_name: Dictionary name
            sel_fields: List of selected field names
            
        Returns:
            Checkboxes HTML string
        """
        fields = self._get_field_names()
        options = f'<div class="fieldCheckboxes" data-dictname="{dict_name}">'
        
        for field in fields:
            checked = ' checked' if field in sel_fields else ''
            options += f'<label class="inCheckBox"><input{checked} onclick="handleFieldCheck(this)" class="inCheckBox" type="checkbox" value="{field}" />{field}</label>'
        
        return options + '</div>'
    
    def _get_field_names(self) -> list:
        """
        Get all field names from all note models.
        
        Returns:
            Sorted list of unique field names
        """
        try:
            models = self.mw.col.models.all()
            fields = []
            for model in models:
                for fld in model['flds']:
                    if fld['name'] not in fields:
                        fields.append(fld['name'])
            fields.sort()
            return fields
        except Exception as e:
            logger.error(f"Error getting field names: {e}")
            return []
    
    def _get_google_images_html(self, term: str, dict_count: int, front_bracket: str, back_bracket: str, entry_count: int, font: str) -> str:
        """
        Generate Google Images dictionary HTML.
        
        Args:
            term: Search term
            dict_count: Dictionary index
            front_bracket: Front bracket character
            back_bracket: Back bracket character
            entry_count: Entry index
            font: Font style string
            
        Returns:
            Google Images HTML string
        """
        dict_name = 'Google Images'
        overwrite = self._get_overwrite_checks(dict_count, dict_name)
        select = self._get_field_checks(dict_name)
        id_name = f'gcon{int(time.time() * 1000)}'
        
        html = f'<div data-index="{dict_count}" class="dictionaryTitleBlock">'
        html += f'<div class="dictionaryTitle">Google Images</div>'
        html += f'<div class="dictionarySettings">{overwrite}{select}'
        html += '<div class="dictNav"><div onclick="navigateDict(event, false)" class="prevDict">▲</div><div onclick="navigateDict(event, true)" class="nextDict">▼</div></div>'
        html += '</div></div>'
        
        html += f'<div data-index="{entry_count}" class="termPronunciation">'
        html += f'<span class="tpCont">{front_bracket}<span {font} class="terms">'
        html += self._highlight_target(term, term)
        html += f'</span>{back_bracket} <span></span></span>'
        html += '<div class="defTools">'
        html += f'<div onclick="ankiExport(event, \'{dict_name}\')" class="ankiExportButton"><img ankiDict="icons/anki.png"></div>'
        html += '<div onclick="clipText(event)" class="clipper">✂</div>'
        html += f'<div onclick="sendToField(event, \'{dict_name}\')" class="sendToField">➠</div>'
        html += '<div class="defNav"><div onclick="navigateDef(event, false)" class="prevDef">▲</div><div onclick="navigateDef(event, true)" class="nextDef">▼</div></div>'
        html += '</div></div>'
        html += f'<div class="definitionBlock"><div class="imageBlock" id="{id_name}">Loading...</div></div>'
        
        return html
    
    def _get_forvo_html(self, term: str, dict_count: int, front_bracket: str, back_bracket: str, entry_count: int, font: str) -> str:
        """
        Generate Forvo dictionary HTML.
        
        Args:
            term: Search term
            dict_count: Dictionary index
            front_bracket: Front bracket character
            back_bracket: Back bracket character
            entry_count: Entry index
            font: Font style string
            
        Returns:
            Forvo HTML string
        """
        dict_name = 'Forvo'
        overwrite = self._get_overwrite_checks(dict_count, dict_name)
        select = self._get_field_checks(dict_name)
        id_name = f'fcon{int(time.time() * 1000)}'
        
        html = f'<div data-index="{dict_count}" class="dictionaryTitleBlock">'
        html += f'<div class="dictionaryTitle">{dict_name}</div>'
        html += f'<div class="dictionarySettings">{overwrite}{select}'
        html += '<div class="dictNav"><div onclick="navigateDict(event, false)" class="prevDict">▲</div><div onclick="navigateDict(event, true)" class="nextDict">▼</div></div>'
        html += '</div></div>'
        
        html += f'<div data-index="{entry_count}" class="termPronunciation">'
        html += f'<span class="tpCont">{front_bracket}<span {font} class="terms">'
        html += self._highlight_target(term, term)
        html += f'</span>{back_bracket} <span></span></span>'
        html += '<div class="defTools">'
        html += f'<div onclick="ankiExport(event, \'{dict_name}\')" class="ankiExportButton"><img ankiDict="icons/anki.png"></div>'
        html += '<div onclick="clipText(event)" class="clipper">✂</div>'
        html += f'<div onclick="sendToField(event, \'{dict_name}\')" class="sendToField">➠</div>'
        html += '<div class="defNav"><div onclick="navigateDef(event, false)" class="prevDef">▲</div><div onclick="navigateDef(event, true)" class="nextDef">▼</div></div>'
        html += '</div></div>'
        html += f'<div id="{id_name}" class="definitionBlock">Loading...</div>'
        
        return html
    
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
        logger.info(f"All groups: {groups}")
        if group_name in groups:
            group = groups[group_name]
            logger.info(f"Selected group '{group_name}': {group}")
            return group
        
        # Handle special groups
        if group_name == 'All':
            # Return all dictionaries
            all_dicts = self.search_service.repository.get_all_dictionaries()
            if not all_dicts:
                logger.warning("No dictionaries found in database")
                self._show_error("No dictionaries installed. Please add dictionaries through the Dictionary Manager first.")
                return None
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
        # Log bridge command with detailed information
        log_bridge_command(logger, cmd)
        
        # Handle handshake to confirm bridge is working
        if cmd == "bridgeReady" or cmd == "AnkiDictionaryLoaded":
            logger.info("✓ JS bridge handshake complete: pycmd available in JavaScript")
            return
        
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
        # Log window state change
        log_window_state(
            logger,
            "DictionaryWindow",
            "showing",
            visible=self.isVisible(),
            geometry=str(self.geometry()) if hasattr(self, 'geometry') else 'N/A',
            search_terms=terms
        )
        
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
    
    def showEvent(self, event) -> None:
        """
        Handle window show event.
        
        Args:
            event: Show event
        """
        log_window_state(
            logger,
            "DictionaryWindow",
            "shown",
            geometry=str(self.geometry()) if hasattr(self, 'geometry') else 'N/A'
        )
        super().showEvent(event)
        self._update_menu_text()
    
    def hideEvent(self, event: QHideEvent) -> None:
        """
        Handle window hide event.
        
        Args:
            event: Hide event
        """
        log_window_state(
            logger,
            "DictionaryWindow",
            "hidden",
            geometry=str(self.geometry()) if hasattr(self, 'geometry') else 'N/A'
        )
        self._save_window_position()
        self._update_menu_text()
        event.accept()
    
    def _update_menu_text(self) -> None:
        """Update the menu text based on window visibility."""
        try:
            from anki.utils import is_mac
            shortcut = '⌘⇧W' if is_mac else 'Ctrl+Shift+W'
            
            if hasattr(self.mw, 'openMiDict'):
                if self.isVisible():
                    self.mw.openMiDict.setText(f"Close Dictionary ({shortcut})")
                else:
                    self.mw.openMiDict.setText(f"Open Dictionary ({shortcut})")
        except Exception as e:
            logger.warning(f"Error updating menu text: {e}")
