# -*- coding: utf-8 -*-
"""
Tests for UI functionality fixes.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import json


class TestSVGIconLoading:
    """Test SVG icon loading functionality."""
    
    def test_load_svg_icon_day_theme(self, tmp_path):
        """Test loading SVG icon with day theme."""
        from src.ui.dictionary_window import DictionaryWindow
        
        # Create mock SVG file
        icons_dir = tmp_path / 'icons' / 'dictsvgs'
        icons_dir.mkdir(parents=True)
        svg_file = icons_dir / 'search.svg'
        svg_content = '<svg><circle r="10"/></svg>'
        svg_file.write_text(svg_content)
        
        # Create mock dependencies
        mw = Mock()
        search_service = Mock()
        export_service = Mock()
        media_service = Mock()
        config_manager = Mock()
        
        # Create window
        window = DictionaryWindow(
            mw, search_service, export_service, 
            media_service, config_manager, tmp_path
        )
        
        # Test loading
        result = window._load_svg_icon('search', 'day')
        assert result == svg_content
    
    def test_load_svg_icon_night_theme(self, tmp_path):
        """Test loading SVG icon with night theme."""
        from src.ui.dictionary_window import DictionaryWindow
        
        # Create mock SVG file
        icons_dir = tmp_path / 'icons' / 'dictsvgs'
        icons_dir.mkdir(parents=True)
        svg_file = icons_dir / 'searchnight.svg'
        svg_content = '<svg><circle r="10" fill="white"/></svg>'
        svg_file.write_text(svg_content)
        
        # Create mock dependencies
        mw = Mock()
        search_service = Mock()
        export_service = Mock()
        media_service = Mock()
        config_manager = Mock()
        
        # Create window
        window = DictionaryWindow(
            mw, search_service, export_service, 
            media_service, config_manager, tmp_path
        )
        
        # Test loading
        result = window._load_svg_icon('search', 'night')
        assert result == svg_content
    
    def test_load_svg_icon_missing_file(self, tmp_path):
        """Test loading missing SVG icon returns None."""
        from src.ui.dictionary_window import DictionaryWindow
        
        # Create mock dependencies
        mw = Mock()
        search_service = Mock()
        export_service = Mock()
        media_service = Mock()
        config_manager = Mock()
        
        # Create window
        window = DictionaryWindow(
            mw, search_service, export_service, 
            media_service, config_manager, tmp_path
        )
        
        # Test loading missing file
        result = window._load_svg_icon('nonexistent', 'day')
        assert result is None


class TestActionButtonsInHTML:
    """Test action buttons in HTML generation."""
    
    def test_format_results_includes_action_buttons(self):
        """Test that formatted HTML includes action buttons."""
        from src.ui.dictionary_window import DictionaryWindow
        
        # Create mock dependencies
        mw = Mock()
        mw.col = Mock()
        mw.col.models = Mock()
        mw.col.models.all = Mock(return_value=[])
        
        search_service = Mock()
        export_service = Mock()
        media_service = Mock()
        
        # Mock config_manager with proper return values
        config_manager = Mock()
        config_manager.get_value = Mock(side_effect=lambda key, default=None: {
            'frontBracket': '【',
            'backBracket': '】',
            'tooltips': True,
            'highlightTarget': True,
            'highlightSentences': True,
            'GoogleImageFields': [],
            'ForvoFields': [],
            'GoogleImageAddType': 'add',
            'ForvoAddType': 'add'
        }.get(key, default))
        config_manager.get_bool = Mock(side_effect=lambda key, default=False: {
            'tooltips': True,
            'highlightTarget': True,
            'highlightSentences': True
        }.get(key, default))
        
        addon_path = Path('.')
        
        # Create window
        window = DictionaryWindow(
            mw, search_service, export_service, 
            media_service, config_manager, addon_path
        )
        
        # Create mock result
        result = Mock()
        result.results = {
            'TestDict': [
                {
                    'term': 'test',
                    'pronunciation': 'tesuto',
                    'definition': 'A test entry',
                    'altterm': '',
                    'starCount': ''
                }
            ]
        }
        
        dict_group = {'dictionaries': [], 'font': None, 'customFont': False}
        
        # Format results
        html = window._format_results_as_html('test', result, dict_group)
        
        # Verify action buttons present
        assert 'ankiExportButton' in html
        assert 'sendToField' in html
        assert 'clipper' in html
        assert 'defNav' in html
        assert '➠' in html  # Send to field icon
        assert '✂' in html  # Clipboard icon
    
    def test_format_results_includes_navigation_buttons(self):
        """Test that formatted HTML includes dictionary navigation buttons."""
        from src.ui.dictionary_window import DictionaryWindow
        
        # Create mock dependencies
        mw = Mock()
        mw.col = Mock()
        mw.col.models = Mock()
        mw.col.models.all = Mock(return_value=[])
        
        search_service = Mock()
        export_service = Mock()
        media_service = Mock()
        
        # Mock config_manager with proper return values
        config_manager = Mock()
        config_manager.get_value = Mock(side_effect=lambda key, default=None: {
            'frontBracket': '【',
            'backBracket': '】',
            'tooltips': True,
            'highlightTarget': True,
            'highlightSentences': True,
            'GoogleImageFields': [],
            'ForvoFields': [],
            'GoogleImageAddType': 'add',
            'ForvoAddType': 'add'
        }.get(key, default))
        config_manager.get_bool = Mock(side_effect=lambda key, default=False: {
            'tooltips': True,
            'highlightTarget': True,
            'highlightSentences': True
        }.get(key, default))
        
        addon_path = Path('.')
        
        # Create window
        window = DictionaryWindow(
            mw, search_service, export_service, 
            media_service, config_manager, addon_path
        )
        
        # Create mock result with multiple dictionaries
        result = Mock()
        result.results = {
            'Dict1': [{'term': 'test', 'pronunciation': '', 'definition': 'Def 1', 'altterm': '', 'starCount': ''}],
            'Dict2': [{'term': 'test', 'pronunciation': '', 'definition': 'Def 2', 'altterm': '', 'starCount': ''}]
        }
        
        dict_group = {'dictionaries': [], 'font': None, 'customFont': False}
        
        # Format results
        html = window._format_results_as_html('test', result, dict_group)
        
        # Verify navigation buttons present
        assert 'dictNav' in html
        assert 'prevDict' in html
        assert 'nextDict' in html
        assert 'navigateDict' in html
    
    def test_format_results_escapes_dictionary_names(self):
        """Test that dictionary names are properly escaped in HTML."""
        from src.ui.dictionary_window import DictionaryWindow
        
        # Create mock dependencies
        mw = Mock()
        mw.col = Mock()
        mw.col.models = Mock()
        mw.col.models.all = Mock(return_value=[])
        
        search_service = Mock()
        export_service = Mock()
        media_service = Mock()
        
        # Mock config_manager with proper return values
        config_manager = Mock()
        config_manager.get_value = Mock(side_effect=lambda key, default=None: {
            'frontBracket': '【',
            'backBracket': '】',
            'tooltips': True,
            'highlightTarget': True,
            'highlightSentences': True,
            'GoogleImageFields': [],
            'ForvoFields': [],
            'GoogleImageAddType': 'add',
            'ForvoAddType': 'add'
        }.get(key, default))
        config_manager.get_bool = Mock(side_effect=lambda key, default=False: {
            'tooltips': True,
            'highlightTarget': True,
            'highlightSentences': True
        }.get(key, default))
        
        addon_path = Path('.')
        
        # Create window
        window = DictionaryWindow(
            mw, search_service, export_service, 
            media_service, config_manager, addon_path
        )
        
        # Create mock result with special characters in dict name
        result = Mock()
        result.results = {
            "Dict's Name": [{'term': 'test', 'pronunciation': '', 'definition': 'Def', 'altterm': '', 'starCount': ''}]
        }
        
        dict_group = {'dictionaries': [], 'font': None, 'customFont': False}
        
        # Format results
        html = window._format_results_as_html('test', result, dict_group)
        
        # Verify escaping - the final HTML has single quotes escaped for JavaScript
        assert "Dict\\'s Name" in html or "Dict&#39;s Name" in html


class TestUserFilesMigration:
    """Test user files migration functionality."""
    
    def test_migration_creates_marker(self, tmp_path):
        """Test that migration creates a marker file."""
        from src.core.plugin import AnkiDictionaryPlugin
        
        # Create mock main window
        mw = Mock()
        mw.addonManager = Mock()
        mw.addonManager.getConfig = Mock(return_value={})
        
        # Create plugin with temp path
        with patch.object(AnkiDictionaryPlugin, '__init__', lambda self, mw: None):
            plugin = AnkiDictionaryPlugin.__new__(AnkiDictionaryPlugin)
            plugin.addon_path = tmp_path
            plugin.mw = mw
            
            # Run migration
            plugin._migrate_user_files()
            
            # Check marker exists
            marker = tmp_path / 'user_files' / '.migrated'
            assert marker.exists()
    
    def test_migration_skips_if_already_migrated(self, tmp_path):
        """Test that migration is skipped if marker exists."""
        from src.core.plugin import AnkiDictionaryPlugin
        
        # Create marker
        user_files = tmp_path / 'user_files'
        user_files.mkdir()
        marker = user_files / '.migrated'
        marker.touch()
        
        # Create mock main window
        mw = Mock()
        mw.addonManager = Mock()
        
        # Create plugin
        with patch.object(AnkiDictionaryPlugin, '__init__', lambda self, mw: None):
            plugin = AnkiDictionaryPlugin.__new__(AnkiDictionaryPlugin)
            plugin.addon_path = tmp_path
            plugin.mw = mw
            
            # Run migration (should be skipped)
            plugin._migrate_user_files()
            
            # Marker should still exist (not recreated)
            assert marker.exists()


class TestMacOSHotkeyHandling:
    """Test macOS hotkey handling."""
    
    @patch('src.ui.menu_manager.is_mac', True)
    @patch('src.ui.menu_manager.ANKI_AVAILABLE', True)
    def test_setup_hotkeys_delays_on_macos(self):
        """Test that hotkey setup is delayed on macOS."""
        from src.ui.menu_manager import MenuManager
        
        # Create mock main window
        mw = Mock()
        plugin = Mock()
        
        # Create menu manager
        manager = MenuManager(mw, plugin)
        
        # Mock QTimer from aqt.qt
        with patch('aqt.qt.QTimer') as mock_timer:
            manager.setup_global_hotkeys()
            
            # Verify QTimer.singleShot was called with 1000ms delay
            mock_timer.singleShot.assert_called_once()
            args = mock_timer.singleShot.call_args[0]
            assert args[0] == 1000  # 1 second delay
    
    @patch('src.ui.menu_manager.is_mac', False)
    @patch('src.ui.menu_manager.ANKI_AVAILABLE', True)
    def test_setup_hotkeys_immediate_on_other_platforms(self):
        """Test that hotkey setup is immediate on non-macOS platforms."""
        from src.ui.menu_manager import MenuManager
        
        # Create mock main window
        mw = Mock()
        plugin = Mock()
        
        # Create menu manager
        manager = MenuManager(mw, plugin)
        
        # Mock _register_hotkeys to verify it's called immediately
        with patch.object(manager, '_register_hotkeys') as mock_register:
            manager.setup_global_hotkeys()
            
            # Verify immediate registration
            mock_register.assert_called_once()


class TestSVGIconInjection:
    """Test SVG icon injection into HTML."""
    
    def test_inject_svg_icons_adds_script_tag(self, tmp_path):
        """Test that SVG injection adds a script tag."""
        from src.ui.dictionary_window import DictionaryWindow
        
        # Create mock SVG files
        icons_dir = tmp_path / 'icons' / 'dictsvgs'
        icons_dir.mkdir(parents=True)
        (icons_dir / 'search.svg').write_text('<svg>search</svg>')
        
        # Create mock dependencies
        mw = Mock()
        search_service = Mock()
        export_service = Mock()
        media_service = Mock()
        config_manager = Mock()
        
        # Create window
        window = DictionaryWindow(
            mw, search_service, export_service, 
            media_service, config_manager, tmp_path
        )
        
        # Test injection
        html = '<html><head></head><body></body></html>'
        result = window._inject_svg_icons_into_html(html, 'day')
        
        # Verify script tag added
        assert '<script id="svgIcons">' in result
        assert 'var svgIcons' in result
    
    def test_inject_svg_icons_includes_icon_data(self, tmp_path):
        """Test that SVG injection includes icon data."""
        from src.ui.dictionary_window import DictionaryWindow
        
        # Create mock SVG files
        icons_dir = tmp_path / 'icons' / 'dictsvgs'
        icons_dir.mkdir(parents=True)
        (icons_dir / 'search.svg').write_text('<svg>search</svg>')
        
        # Create mock dependencies
        mw = Mock()
        search_service = Mock()
        export_service = Mock()
        media_service = Mock()
        config_manager = Mock()
        
        # Create window
        window = DictionaryWindow(
            mw, search_service, export_service, 
            media_service, config_manager, tmp_path
        )
        
        # Test injection
        html = '<html><head></head><body></body></html>'
        result = window._inject_svg_icons_into_html(html, 'day')
        
        # Verify icon data present
        assert 'search' in result
        assert '<svg>search</svg>' in result or '\\u003csvg\\u003esearch\\u003c/svg\\u003e' in result
