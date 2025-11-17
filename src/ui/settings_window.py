# -*- coding: utf-8 -*-
"""
Refactored Settings Window using ConfigManager.
"""

from typing import Any, Optional, Tuple, List, Dict
from pathlib import Path
import logging
import re

try:
    from aqt.qt import (
        QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
        QLabel, QCheckBox, QSpinBox, QComboBox, QLineEdit, QPushButton,
        QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
        QFrame, QShortcut, QKeySequence, QIcon, QFileDialog, Qt
    )
    from aqt.utils import showInfo
    from anki.utils import is_mac, is_win, is_lin
    ANKI_AVAILABLE = True
except ImportError:
    # For testing without Anki
    ANKI_AVAILABLE = False
    QTabWidget = type('QTabWidget', (object,), {})
    QWidget = type('QWidget', (object,), {})
    QVBoxLayout = type('QVBoxLayout', (object,), {})
    QHBoxLayout = type('QHBoxLayout', (object,), {})
    QGroupBox = type('QGroupBox', (object,), {})
    QLabel = type('QLabel', (object,), {})
    QCheckBox = type('QCheckBox', (object,), {})
    QSpinBox = type('QSpinBox', (object,), {})
    QComboBox = type('QComboBox', (object,), {})
    QLineEdit = type('QLineEdit', (object,), {})
    QPushButton = type('QPushButton', (object,), {})
    QTableWidget = type('QTableWidget', (object,), {})
    QTableWidgetItem = type('QTableWidgetItem', (object,), {})
    QHeaderView = type('QHeaderView', (object,), {})
    QAbstractItemView = type('QAbstractItemView', (object,), {})
    QFrame = type('QFrame', (object,), {})
    QShortcut = type('QShortcut', (object,), {})
    QKeySequence = type('QKeySequence', (object,), {})
    QIcon = type('QIcon', (object,), {})
    QFileDialog = type('QFileDialog', (object,), {})
    Qt = type('Qt', (object,), {})
    showInfo = lambda *args, **kwargs: None
    is_mac = False
    is_win = False
    is_lin = False

from ..config import ConfigManager
from ..utils.dialogs import show_info, ask_user

logger = logging.getLogger('anki_dictionary.ui.settings_window')


# Version number
VERSION = "0.1"


class SettingsWindow(QTabWidget):
    """
    Settings configuration window using ConfigManager.
    
    This window provides a UI for configuring all addon settings,
    managing dictionary groups, and managing export templates.
    All configuration operations are delegated to ConfigManager.
    """
    
    def __init__(
        self,
        mw: Any,
        config_manager: ConfigManager,
        plugin: 'AnkiDictionaryPlugin',
        addon_path: Path,
        reboot_callback: Optional[callable] = None
    ):
        """
        Initialize settings window.
        
        Args:
            mw: Anki main window instance
            config_manager: Configuration manager
            plugin: Plugin coordinator instance
            addon_path: Path to addon directory
            reboot_callback: Optional callback to reboot settings window
        """
        super().__init__()
        
        # Store dependencies
        self.mw = mw
        self.config_manager = config_manager
        self.plugin = plugin
        self.addon_path = addon_path
        self.reboot_callback = reboot_callback
        
        # Country and language lists
        self.google_countries = self._get_google_countries()
        self.forvo_languages = self._get_forvo_languages()
        
        # Initialize UI
        self._setup_window()
        self._create_widgets()
        self._setup_layout()
        self._load_settings()
        self._init_tooltips()
        self._init_handlers()
        
        # Set up hotkeys
        if ANKI_AVAILABLE:
            self.hotkey_esc = QShortcut(QKeySequence("Esc"), self)
            self.hotkey_esc.activated.connect(self.close)
        
        logger.info("Settings window initialized")
        
        if ANKI_AVAILABLE:
            self.show()
    
    def _setup_window(self) -> None:
        """Set up window properties."""
        if not ANKI_AVAILABLE:
            return
        
        self.setWindowTitle(f"Anki Dictionary Settings (Ver. {VERSION})")
        self.setMinimumSize(850, 550)
        
        if not is_win:
            self.resize(1034, 550)
        else:
            self.resize(920, 550)
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setWindowIcon(QIcon(str(self.addon_path / 'icons' / 'miso.png')))
    
    def _create_widgets(self) -> None:
        """Create all UI widgets."""
        # Dictionary groups and templates
        self.add_dict_group = QPushButton('Add Dictionary Group')
        self.add_export_template = QPushButton('Add Export Template')
        self.dict_groups = self._get_group_template_table()
        self.export_templates = self._get_group_template_table()
        
        # Settings widgets
        self.tooltip_cb = QCheckBox()
        if ANKI_AVAILABLE:
            self.tooltip_cb.setFixedHeight(30)
        
        self.max_img_width = QSpinBox()
        if ANKI_AVAILABLE:
            self.max_img_width.setRange(0, 9999)
        
        self.max_img_height = QSpinBox()
        if ANKI_AVAILABLE:
            self.max_img_height.setRange(0, 9999)
        
        self.safe_search = QCheckBox()
        
        self.google_country = QComboBox()
        if ANKI_AVAILABLE:
            self.google_country.addItems(self.google_countries)
        
        self.forvo_lang = QComboBox()
        if ANKI_AVAILABLE:
            self.forvo_lang.addItems(self.forvo_languages)
        
        self.condensed_audio_directory_label = QLabel("Condensed Audio Save Location:")
        self.choose_audio_directory = QPushButton("Choose Directory")
        self.convert_to_mp3 = QCheckBox()
        self.disable_condensed_messages = QCheckBox()
        self.dict_on_top = QCheckBox()
        self.show_target = QCheckBox()
        
        self.total_defs = QSpinBox()
        if ANKI_AVAILABLE:
            self.total_defs.setRange(0, 1000)
        
        self.dict_defs = QSpinBox()
        if ANKI_AVAILABLE:
            self.dict_defs.setRange(0, 100)
        
        self.gen_js_export = QCheckBox()
        self.gen_js_edit = QCheckBox()
        self.front_bracket = QLineEdit()
        self.back_bracket = QLineEdit()
        self.highlight_target = QCheckBox()
        self.highlight_sentence = QCheckBox()
        self.open_on_start = QCheckBox()
        self.global_hotkeys = QCheckBox()
        self.global_open = QCheckBox()
        
        # Buttons
        self.restore_button = QPushButton('Restore Defaults')
        self.cancel_button = QPushButton('Cancel')
        self.apply_button = QPushButton('Apply')
    
    def _setup_layout(self) -> None:
        """Set up the window layout."""
        # Create settings tab
        self.settings_tab = QWidget(self)
        layout = QVBoxLayout()
        
        # Dictionary groups and templates section
        group_layout = QHBoxLayout()
        dicts_layout = QVBoxLayout()
        exports_layout = QVBoxLayout()
        
        dicts_layout.addWidget(QLabel('Dictionary Groups'))
        dicts_layout.addWidget(self.add_dict_group)
        dicts_layout.addWidget(self.dict_groups)
        
        exports_layout.addWidget(QLabel('Export Templates'))
        exports_layout.addWidget(self.add_export_template)
        exports_layout.addWidget(self.export_templates)
        
        group_layout.addLayout(dicts_layout)
        group_layout.addLayout(exports_layout)
        layout.addLayout(group_layout)
        
        # Options section
        options_box = QGroupBox('Options')
        options_layout = QHBoxLayout()
        
        # Create three columns of options
        opt_lay1 = self._create_options_column_1()
        opt_lay2 = self._create_options_column_2()
        opt_lay3 = self._create_options_column_3()
        
        options_layout.addLayout(opt_lay1)
        options_layout.addStretch()
        options_layout.addWidget(self._get_line_separator())
        options_layout.addStretch()
        options_layout.addLayout(opt_lay2)
        options_layout.addStretch()
        options_layout.addWidget(self._get_line_separator())
        options_layout.addStretch()
        options_layout.addLayout(opt_lay3)
        
        options_box.setLayout(options_layout)
        layout.addWidget(options_box)
        layout.addStretch()
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.restore_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.apply_button)
        
        layout.addLayout(buttons_layout)
        self.settings_tab.setLayout(layout)
        
        # Add tabs
        if ANKI_AVAILABLE:
            self.addTab(self.settings_tab, "Settings")
            # Dictionary manager tab would be added here
            # self.addTab(DictionaryManagerWidget(), "Dictionaries")
    
    def _create_options_column_1(self) -> QVBoxLayout:
        """Create first column of options."""
        opt_lay = QVBoxLayout()
        
        # Open on Startup
        startup_lay = QHBoxLayout()
        startup_lay.addWidget(self._mi_qlabel('Open on Startup:', 182))
        startup_lay.addWidget(self.open_on_start)
        opt_lay.addLayout(startup_lay)
        
        # Highlight Example Sentences
        high_sent_lay = QHBoxLayout()
        high_sent_lay.addWidget(self._mi_qlabel('Highlight Examples Sentences:', 182))
        high_sent_lay.addWidget(self.highlight_sentence)
        opt_lay.addLayout(high_sent_lay)
        
        # Highlight Searched Term
        high_word_lay = QHBoxLayout()
        high_word_lay.addWidget(self._mi_qlabel('Highlight Searched Term:', 182))
        high_word_lay.addWidget(self.highlight_target)
        opt_lay.addLayout(high_word_lay)
        
        # Show Export Target
        exp_target_lay = QHBoxLayout()
        exp_target_lay.addWidget(self._mi_qlabel('Show Export Target:', 182))
        exp_target_lay.addWidget(self.show_target)
        opt_lay.addLayout(exp_target_lay)
        
        # Dictionary Tooltips
        tool_tip_lay = QHBoxLayout()
        tool_tip_lay.addWidget(self._mi_qlabel('Dictionary Tooltips:', 182))
        tool_tip_lay.addWidget(self.tooltip_cb)
        opt_lay.addLayout(tool_tip_lay)
        
        # Global Hotkeys
        gh_lay = QHBoxLayout()
        gh_lay.addWidget(self._mi_qlabel('Global Hotkeys:', 182))
        gh_lay.addWidget(self.global_hotkeys)
        opt_lay.addLayout(gh_lay)
        
        # Convert Extension Audio to MP3
        extension_mp3_lay = QHBoxLayout()
        extension_mp3_lay.addWidget(self._mi_qlabel("Convert Extension Audio to MP3", 182))
        extension_mp3_lay.addWidget(self.convert_to_mp3)
        opt_lay.addLayout(extension_mp3_lay)
        
        # Disable Condensed Audio Messages
        disable_condensed_lay = QHBoxLayout()
        disable_condensed_lay.addWidget(self._mi_qlabel("Disable Condensed Audio Messages:", 182))
        disable_condensed_lay.addWidget(self.disable_condensed_messages)
        opt_lay.addLayout(disable_condensed_lay)
        
        return opt_lay
    
    def _create_options_column_2(self) -> QVBoxLayout:
        """Create second column of options."""
        opt_lay = QVBoxLayout()
        
        # Open on Global Search
        global_open_lay = QHBoxLayout()
        global_open_lay.addWidget(self._mi_qlabel('Open on Global Search:', 323))
        global_open_lay.addWidget(self.global_open)
        opt_lay.addLayout(global_open_lay)
        
        # Max Total Search Results
        tot_res_lay = QHBoxLayout()
        tot_res_lay.addWidget(self._mi_qlabel('Max Total Search Results:', 180))
        tot_res_lay.addWidget(self.total_defs)
        if ANKI_AVAILABLE:
            self.total_defs.setFixedWidth(160)
        opt_lay.addLayout(tot_res_lay)
        
        # Max Dictionary Search Results
        dict_res_lay = QHBoxLayout()
        dict_res_lay.addWidget(self._mi_qlabel('Max Dictionary Search Results:', 180))
        dict_res_lay.addWidget(self.dict_defs)
        if ANKI_AVAILABLE:
            self.dict_defs.setFixedWidth(160)
        opt_lay.addLayout(dict_res_lay)
        
        # Add Cards with Japanese Readings
        gen_js_export_lay = QHBoxLayout()
        gen_js_export_lay.addWidget(self._mi_qlabel('Add Cards with Japanese Readings:', 323))
        gen_js_export_lay.addWidget(self.gen_js_export)
        opt_lay.addLayout(gen_js_export_lay)
        
        # Japanese Readings on Edit
        gen_js_edit_lay = QHBoxLayout()
        gen_js_edit_lay.addWidget(self._mi_qlabel('Japanese Readings on Edit:', 323))
        gen_js_edit_lay.addWidget(self.gen_js_edit)
        opt_lay.addLayout(gen_js_edit_lay)
        
        # Google Images Search Region
        country_lay = QHBoxLayout()
        country_lay.addWidget(self._mi_qlabel('Google Images Search Region:', 180))
        country_lay.addWidget(self.google_country)
        if ANKI_AVAILABLE:
            self.google_country.setFixedWidth(160)
        opt_lay.addLayout(country_lay)
        
        # Safe Search
        safe_lay = QHBoxLayout()
        safe_lay.addWidget(self._mi_qlabel('Safe Search:', 323))
        safe_lay.addWidget(self.safe_search)
        opt_lay.addLayout(safe_lay)
        
        opt_lay.addStretch()
        return opt_lay
    
    def _create_options_column_3(self) -> QVBoxLayout:
        """Create third column of options."""
        opt_lay = QVBoxLayout()
        
        # Maximum Image Width
        max_wid_lay = QHBoxLayout()
        max_wid_lay.addWidget(self._mi_qlabel('Maximum Image Width:', 140))
        max_wid_lay.addWidget(self.max_img_width)
        opt_lay.addLayout(max_wid_lay)
        
        # Maximum Image Height
        max_hei_lay = QHBoxLayout()
        max_hei_lay.addWidget(self._mi_qlabel('Maximum Image Height:', 140))
        max_hei_lay.addWidget(self.max_img_height)
        opt_lay.addLayout(max_hei_lay)
        
        # Surround Term (Front)
        front_bracket_lay = QHBoxLayout()
        front_bracket_lay.addWidget(self._mi_qlabel('Surround Term (Front):', 140))
        front_bracket_lay.addWidget(self.front_bracket)
        opt_lay.addLayout(front_bracket_lay)
        
        # Surround Term (Back)
        back_bracket_lay = QHBoxLayout()
        back_bracket_lay.addWidget(self._mi_qlabel('Surround Term (Back):', 140))
        back_bracket_lay.addWidget(self.back_bracket)
        opt_lay.addLayout(back_bracket_lay)
        
        # Forvo Language
        forvo_lay = QHBoxLayout()
        forvo_lay.addWidget(self._mi_qlabel('Forvo Language:', 140))
        forvo_lay.addWidget(self.forvo_lang)
        opt_lay.addLayout(forvo_lay)
        
        # Always on Top
        dict_on_top_lay = QHBoxLayout()
        dict_on_top_lay.addWidget(self._mi_qlabel("Always on Top:", 323))
        dict_on_top_lay.addWidget(self.dict_on_top)
        opt_lay.addLayout(dict_on_top_lay)
        
        # Condensed Audio Directory
        extension_audio_lay = QHBoxLayout()
        extension_audio_lay.addWidget(self.condensed_audio_directory_label)
        if ANKI_AVAILABLE:
            self.choose_audio_directory.setFixedWidth(100)
        extension_audio_lay.addWidget(self.choose_audio_directory)
        opt_lay.addLayout(extension_audio_lay)
        
        opt_lay.addStretch()
        return opt_lay
    
    def _load_settings(self) -> None:
        """Load settings from ConfigManager into UI widgets."""
        try:
            # Boolean settings
            self.open_on_start.setChecked(self.config_manager.get_bool('dictOnStart', False))
            self.highlight_sentence.setChecked(self.config_manager.get_bool('highlightSentences', True))
            self.highlight_target.setChecked(self.config_manager.get_bool('highlightTarget', True))
            self.gen_js_export.setChecked(self.config_manager.get_bool('jReadingCards', True))
            self.gen_js_edit.setChecked(self.config_manager.get_bool('jReadingEdit', True))
            self.show_target.setChecked(self.config_manager.get_bool('showTarget', False))
            self.tooltip_cb.setChecked(self.config_manager.get_bool('tooltips', True))
            self.global_hotkeys.setChecked(self.config_manager.get_bool('globalHotkeys', True))
            self.global_open.setChecked(self.config_manager.get_bool('openOnGlobal', True))
            self.safe_search.setChecked(self.config_manager.get_bool('safeSearch', True))
            self.convert_to_mp3.setChecked(self.config_manager.get_bool('mp3Convert', True))
            self.disable_condensed_messages.setChecked(self.config_manager.get_bool('disableCondensed', False))
            self.dict_on_top.setChecked(self.config_manager.get_bool('dictAlwaysOnTop', False))
            
            # Integer settings
            self.total_defs.setValue(self.config_manager.get_int('maxSearch', 1000))
            self.dict_defs.setValue(self.config_manager.get_int('dictSearch', 50))
            self.max_img_width.setValue(self.config_manager.get_int('maxWidth', 400))
            self.max_img_height.setValue(self.config_manager.get_int('maxHeight', 400))
            
            # String settings
            if ANKI_AVAILABLE:
                self.google_country.setCurrentText(self.config_manager.get_str('googleSearchRegion', 'United States'))
                self.forvo_lang.setCurrentText(self.config_manager.get_str('ForvoLanguage', 'Japanese'))
            self.front_bracket.setText(self.config_manager.get_str('frontBracket', '【'))
            self.back_bracket.setText(self.config_manager.get_str('backBracket', '】'))
            
            # Audio directory
            audio_dir = self.config_manager.get_value('condensedAudioDirectory', False)
            if audio_dir and audio_dir is not False:
                self.choose_audio_directory.setText(str(audio_dir))
            else:
                self.choose_audio_directory.setText("Choose Directory")
            
            # Load tables
            self._load_group_table()
            self._load_template_table()
            
            logger.info("Settings loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}", exc_info=True)
            show_info(f"Error loading settings: {str(e)}", parent=self, title="Settings Error")
    
    def validate_settings(self) -> Tuple[bool, Optional[str]]:
        """
        Validate settings before saving.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate total defs
        if self.total_defs.value() < 1:
            return False, "Max Total Search Results must be at least 1"
        
        # Validate dict defs
        if self.dict_defs.value() < 1:
            return False, "Max Dictionary Search Results must be at least 1"
        
        # Validate image dimensions
        if self.max_img_width.value() < 50:
            return False, "Maximum Image Width must be at least 50 pixels"
        
        if self.max_img_height.value() < 50:
            return False, "Maximum Image Height must be at least 50 pixels"
        
        # Validate bracket length
        if len(self.front_bracket.text()) > 10:
            return False, "Front bracket text is too long (max 10 characters)"
        
        if len(self.back_bracket.text()) > 10:
            return False, "Back bracket text is too long (max 10 characters)"
        
        return True, None
    
    def save_settings(self) -> bool:
        """
        Save settings via ConfigManager with validation.
        
        Returns:
            True if settings saved successfully, False otherwise
        """
        # Validate first
        is_valid, error = self.validate_settings()
        if not is_valid:
            show_info(
                f"Settings validation failed:\n\n{error}",
                parent=self,
                title="Validation Error"
            )
            return False
        
        try:
            # Get current config
            config = self.config_manager.get_config().copy()
            
            # Update with UI values
            config['dictOnStart'] = self.open_on_start.isChecked()
            config['highlightSentences'] = self.highlight_sentence.isChecked()
            config['highlightTarget'] = self.highlight_target.isChecked()
            config['maxSearch'] = self.total_defs.value()
            config['dictSearch'] = self.dict_defs.value()
            config['jReadingCards'] = self.gen_js_export.isChecked()
            config['jReadingEdit'] = self.gen_js_edit.isChecked()
            config['googleSearchRegion'] = self.google_country.currentText() if ANKI_AVAILABLE else 'United States'
            config['ForvoLanguage'] = self.forvo_lang.currentText() if ANKI_AVAILABLE else 'Japanese'
            config['maxWidth'] = self.max_img_width.value()
            config['maxHeight'] = self.max_img_height.value()
            config['frontBracket'] = self.front_bracket.text()
            config['backBracket'] = self.back_bracket.text()
            config['showTarget'] = self.show_target.isChecked()
            config['tooltips'] = self.tooltip_cb.isChecked()
            config['globalHotkeys'] = self.global_hotkeys.isChecked()
            config['openOnGlobal'] = self.global_open.isChecked()
            config['mp3Convert'] = self.convert_to_mp3.isChecked()
            config['disableCondensed'] = self.disable_condensed_messages.isChecked()
            config['safeSearch'] = self.safe_search.isChecked()
            config['dictAlwaysOnTop'] = self.dict_on_top.isChecked()
            
            # Audio directory
            if self.choose_audio_directory.text() != "Choose Directory":
                config['condensedAudioDirectory'] = self.choose_audio_directory.text()
            else:
                config['condensedAudioDirectory'] = False
            
            # Write config via ConfigManager
            self.config_manager.write_config(config)
            
            # Hide window
            self.hide()
            
            # Notify plugin of config changes
            if self.plugin:
                self.plugin.refresh_config()
            
            # Install FFMPEG if needed
            if config['mp3Convert'] and self.plugin:
                self.plugin.ffmpeg_installer.installFFMPEG()
            
            # Show notification if dictionary is open
            if ANKI_AVAILABLE and self.mw.ankiDictionary and self.mw.ankiDictionary.isVisible():
                show_info(
                    'Please be aware that the dictionary window will not reflect any setting changes until it is closed and reopened.',
                    parent=self,
                    title='Settings Saved'
                )
            
            logger.info("Settings saved successfully")
            return True
            
        except ValueError as e:
            # ConfigManager validation error
            show_info(
                f"Settings validation failed:\n\n{str(e)}",
                parent=self,
                title="Validation Error"
            )
            return False
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            show_info(
                f"Error saving settings:\n\n{str(e)}",
                parent=self,
                title="Save Error"
            )
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        if not ask_user(
            'This will remove any export templates and dictionary groups you have created, and is not undoable. '
            'Are you sure you would like to restore the default settings?',
            parent=self
        ):
            return
        
        try:
            # Reset via ConfigManager
            self.config_manager.reset_to_defaults()
            
            # Close window
            self.close()
            
            # Reboot if callback provided
            if self.reboot_callback:
                self.reboot_callback()
            
            logger.info("Settings reset to defaults")
            
        except Exception as e:
            logger.error(f"Error resetting settings: {e}", exc_info=True)
            show_info(
                f"Error resetting settings:\n\n{str(e)}",
                parent=self,
                title="Reset Error"
            )
    
    def _load_group_table(self) -> None:
        """Load dictionary groups into table."""
        if not ANKI_AVAILABLE:
            return
        
        self.dict_groups.setRowCount(0)
        dict_groups = self.config_manager.get_dictionary_groups()
        
        for group_name in dict_groups:
            rc = self.dict_groups.rowCount()
            self.dict_groups.setRowCount(rc + 1)
            self.dict_groups.setItem(rc, 0, QTableWidgetItem(group_name))
            
            # Edit button
            edit_button = QPushButton("Edit")
            if is_win:
                edit_button.setFixedWidth(40)
            else:
                edit_button.setFixedWidth(50)
                edit_button.setFixedHeight(30)
            edit_button.clicked.connect(self._edit_group_row(rc))
            self.dict_groups.setCellWidget(rc, 1, edit_button)
            
            # Delete button
            delete_button = QPushButton("X")
            if is_win:
                delete_button.setFixedWidth(40)
            else:
                delete_button.setFixedWidth(40)
                delete_button.setFixedHeight(30)
            delete_button.clicked.connect(self._remove_group_row(rc))
            self.dict_groups.setCellWidget(rc, 2, delete_button)
    
    def _load_template_table(self) -> None:
        """Load export templates into table."""
        if not ANKI_AVAILABLE:
            return
        
        self.export_templates.setRowCount(0)
        export_templates = self.config_manager.get_export_templates()
        
        for template_name in export_templates:
            rc = self.export_templates.rowCount()
            self.export_templates.setRowCount(rc + 1)
            self.export_templates.setItem(rc, 0, QTableWidgetItem(template_name))
            
            # Edit button
            edit_button = QPushButton("Edit")
            if is_win:
                edit_button.setFixedWidth(40)
            else:
                edit_button.setFixedWidth(50)
                edit_button.setFixedHeight(30)
            edit_button.clicked.connect(self._edit_temp_row(rc))
            self.export_templates.setCellWidget(rc, 1, edit_button)
            
            # Delete button
            delete_button = QPushButton("X")
            if is_win:
                delete_button.setFixedWidth(40)
            else:
                delete_button.setFixedWidth(40)
                delete_button.setFixedHeight(30)
            delete_button.clicked.connect(self._remove_temp_row(rc))
            self.export_templates.setCellWidget(rc, 2, delete_button)
    
    def _remove_group(self, row: int) -> None:
        """Remove a dictionary group."""
        if not ask_user(
            'Are you sure you would like to remove this dictionary group? '
            'This action will happen immediately and is not un-doable.',
            parent=self
        ):
            return
        
        try:
            config = self.config_manager.get_config().copy()
            dict_groups = config['DictionaryGroups']
            group_name = self.dict_groups.item(row, 0).text()
            
            if group_name in dict_groups:
                del dict_groups[group_name]
                self.config_manager.write_config(config)
                self._load_group_table()
                logger.info(f"Removed dictionary group: {group_name}")
        
        except Exception as e:
            logger.error(f"Error removing group: {e}", exc_info=True)
            show_info(f"Error removing group: {str(e)}", parent=self, title="Error")
    
    def _remove_template(self, row: int) -> None:
        """Remove an export template."""
        if not ask_user(
            'Are you sure you would like to remove this template? '
            'This action will happen immediately and is not un-doable.',
            parent=self
        ):
            return
        
        try:
            config = self.config_manager.get_config().copy()
            export_templates = config['ExportTemplates']
            template_name = self.export_templates.item(row, 0).text()
            
            if template_name in export_templates:
                del export_templates[template_name]
                self.config_manager.write_config(config)
                self._load_template_table()
                logger.info(f"Removed export template: {template_name}")
        
        except Exception as e:
            logger.error(f"Error removing template: {e}", exc_info=True)
            show_info(f"Error removing template: {str(e)}", parent=self, title="Error")
    
    def _edit_group(self, row: int) -> None:
        """Edit a dictionary group."""
        # This would open the DictGroupEditor dialog
        # For now, just log it
        group_name = self.dict_groups.item(row, 0).text()
        logger.info(f"Edit group requested: {group_name}")
        # TODO: Implement DictGroupEditor integration
    
    def _edit_template(self, row: int) -> None:
        """Edit an export template."""
        # This would open the TemplateEditor dialog
        # For now, just log it
        template_name = self.export_templates.item(row, 0).text()
        logger.info(f"Edit template requested: {template_name}")
        # TODO: Implement TemplateEditor integration
    
    def _add_group(self) -> None:
        """Add a new dictionary group."""
        # This would open the DictGroupEditor dialog
        logger.info("Add group requested")
        # TODO: Implement DictGroupEditor integration
    
    def _add_template(self) -> None:
        """Add a new export template."""
        # This would open the TemplateEditor dialog
        logger.info("Add template requested")
        # TODO: Implement TemplateEditor integration
    
    def _update_audio_directory(self) -> None:
        """Update condensed audio directory."""
        if not ANKI_AVAILABLE:
            return
        
        directory = str(QFileDialog.getExistingDirectory(None, "Select Condensed Audio Directory"))
        if directory:
            self.choose_audio_directory.setText(directory)
        else:
            self.choose_audio_directory.setText("Choose Directory")
    
    def _init_handlers(self) -> None:
        """Initialize event handlers."""
        if not ANKI_AVAILABLE:
            return
        
        self.add_dict_group.clicked.connect(self._add_group)
        self.add_export_template.clicked.connect(self._add_template)
        self.restore_button.clicked.connect(self.reset_to_defaults)
        self.cancel_button.clicked.connect(self.close)
        self.apply_button.clicked.connect(self.save_settings)
        self.choose_audio_directory.clicked.connect(self._update_audio_directory)
    
    def _init_tooltips(self) -> None:
        """Initialize tooltips for widgets."""
        if not ANKI_AVAILABLE:
            return
        
        self.add_dict_group.setToolTip(
            'Add a new dictionary group.\n'
            'Dictionary groups allow you to specify which dictionaries to search\n'
            'within. You can also set a specific font for that group.'
        )
        self.add_export_template.setToolTip(
            'Add a new export template.\n'
            'Export templates allow you to specify a note type, and fields where\n'
            'target sentences, target words, definitions, and images will be sent to\n'
            'when using the Card Exporter to create cards.'
        )
        self.tooltip_cb.setToolTip('Enable/disable tooltips within the dictionary and its sub-windows.')
        self.max_img_width.setToolTip('Images will be scaled according to this width.')
        self.max_img_height.setToolTip('Images will be scaled according to this height.')
        self.google_country.setToolTip(
            'Select the country or region to search Google Images from, the search region\n'
            'greatly impacts search results so choose a location where your target language is spoken.'
        )
        self.forvo_lang.setToolTip('Select the language to be used with the Forvo Dictionary.')
        self.show_target.setToolTip(
            'Show/Hide the Target Identifier from the dictionary window. The Target Identifier\n'
            'lets you know which window is currently selected and will be used when sending\n'
            'definitions to a target field.'
        )
        self.total_defs.setToolTip('This is the total maximum number of definitions which the dictionary will output.')
        self.dict_defs.setToolTip('This is the maximum number of definitions which the dictionary will output for any given dictionary.')
        self.gen_js_export.setToolTip(
            'If this is enabled and you have Anki Japanese With Pitch Accent installed in Anki,\n'
            'then when a card is exported, readings and accent information will automatically be generated for all\n'
            'active fields. This generation is based on your Anki Japanese With Pitch Accent Sentence Button (文) settings.'
        )
        self.gen_js_edit.setToolTip(
            'If this is enabled and you have Anki Japanese With Pitch Accent installed in Anki,\n'
            'then when a definition is sent to a field, readings and accent information will automatically be generated for all\n'
            'active fields. This generation is based on your Anki Japanese With Pitch Accent Sentence Button (文) settings.'
        )
        self.front_bracket.setToolTip('This is the text that will be placed in front of each term\nin the dictionary.')
        self.back_bracket.setToolTip('This is the text that will be placed after each term\nin the dictionary.')
        self.highlight_target.setToolTip('The dictionary will highlight the searched term in\nthe search results.')
        self.highlight_sentence.setToolTip(
            'The dictionary will highlight example sentences in\nthe search results. This feature is experimental and currently only\n'
            'functions on Japanese monolingual dictionaries.'
        )
        self.open_on_start.setToolTip('Enable/Disable launching the Anki Dictionary on profile load.')
        self.global_hotkeys.setToolTip('Enable/Disable global hotkeys.')
        self.global_open.setToolTip('If enabled the dictionary will be opened on a global search.')
        self.safe_search.setToolTip('Whether or not to enable Safe Search for Google Images.')
        self.convert_to_mp3.setToolTip(
            'When enabled will convert extension WAV files into MP3 files.\n'
            'MP3 files are supported across every Anki platform and are much smaller than WAV files.\n'
            'We recommend enabling this option.'
        )
        self.disable_condensed_messages.setToolTip('Disable messages shown when condensed audio files are successfully created.')
    
    def _get_dictionary_names(self) -> List[str]:
        """
        Get list of dictionary names.
        
        Returns:
            List of dictionary names
        """
        try:
            dict_list = self.mw.miDictDB.getAllDictsWithLang()
            dictionary_list = []
            
            for dictionary in dict_list:
                dict_name = self._clean_dict_name(dictionary['dict'])
                if dict_name not in dictionary_list:
                    dictionary_list.append(dict_name)
            
            dictionary_list = sorted(dictionary_list, key=str.casefold)
            return dictionary_list
        
        except Exception as e:
            logger.error(f"Error getting dictionary names: {e}", exc_info=True)
            return []
    
    def _clean_dict_name(self, name: str) -> str:
        """
        Clean dictionary name by removing language codes.
        
        Args:
            name: Raw dictionary name
            
        Returns:
            Cleaned dictionary name
        """
        return re.sub(r'l\d+name', '', name)
    
    def _get_group_template_table(self) -> QTableWidget:
        """
        Create a table widget for groups/templates.
        
        Returns:
            Configured QTableWidget
        """
        table = QTableWidget()
        
        if not ANKI_AVAILABLE:
            return table
        
        mac_lin = is_mac or is_lin
        
        table.setColumnCount(3)
        table_header = table.horizontalHeader()
        table_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        table_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        table.setRowCount(0)
        table.setSortingEnabled(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        if mac_lin:
            table.setColumnWidth(1, 50)
            table.setColumnWidth(2, 40)
        else:
            table.setColumnWidth(1, 40)
            table.setColumnWidth(2, 40)
        
        table_header.hide()
        return table
    
    def _mi_qlabel(self, text: str, width: int) -> QLabel:
        """
        Create a label with fixed dimensions.
        
        Args:
            text: Label text
            width: Fixed width
            
        Returns:
            Configured QLabel
        """
        label = QLabel(text)
        if ANKI_AVAILABLE:
            label.setFixedHeight(30)
            label.setFixedWidth(width)
        return label
    
    def _get_line_separator(self) -> QFrame:
        """
        Create a vertical line separator.
        
        Returns:
            Configured QFrame
        """
        line = QFrame()
        if ANKI_AVAILABLE:
            line.setFrameShape(QFrame.Shape.VLine)
            line.setFrameShadow(QFrame.Shadow.Plain)
            line.setStyleSheet('QFrame[frameShape="5"]{color: #D5DFE5;}')
        return line
    
    # Row handler factories (for lambda closures)
    def _remove_group_row(self, row: int) -> callable:
        """Create remove group handler for row."""
        return lambda: self._remove_group(row)
    
    def _edit_group_row(self, row: int) -> callable:
        """Create edit group handler for row."""
        return lambda: self._edit_group(row)
    
    def _remove_temp_row(self, row: int) -> callable:
        """Create remove template handler for row."""
        return lambda: self._remove_template(row)
    
    def _edit_temp_row(self, row: int) -> callable:
        """Create edit template handler for row."""
        return lambda: self._edit_template(row)
    
    # Event handlers
    def hideEvent(self, event: Any) -> None:
        """
        Handle window hide event.
        
        Args:
            event: Hide event
        """
        self.mw.dictSettings = None
        event.accept()
    
    def closeEvent(self, event: Any) -> None:
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        self.mw.dictSettings = None
        event.accept()
    
    # Static helper methods
    @staticmethod
    def _get_google_countries() -> List[str]:
        """
        Get list of Google search countries.
        
        Returns:
            List of country names
        """
        return [
            "Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla",
            "Antarctica", "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia",
            "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus",
            "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Bosnia and Herzegovina",
            "Botswana", "Bouvet Island", "Brazil", "British Indian Ocean Territory", "Brunei Darussalam",
            "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde",
            "Cayman Islands", "Central African Republic", "Chad", "Chile", "China", "Christmas Island",
            "Cocos (Keeling) Islands", "Colombia", "Comoros", "Congo", "Congo, the Democratic Republic of the",
            "Cook Islands", "Costa Rica", "Cote D'ivoire", "Croatia (Hrvatska)", "Cuba", "Cyprus",
            "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor",
            "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia",
            "European Union", "Falkland Islands (Malvinas)", "Faroe Islands", "Fiji", "Finland", "France",
            "France, Metropolitan", "French Guiana", "French Polynesia", "French Southern Territories",
            "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland",
            "Grenada", "Guadeloupe", "Guam", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti",
            "Heard Island and Mcdonald Islands", "Holy See (Vatican City State)", "Honduras", "Hong Kong",
            "Hungary", "Iceland", "India", "Indonesia", "Iran, Islamic Republic of", "Iraq", "Ireland",
            "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati",
            "Korea, Democratic People's Republic of", "Korea, Republic of", "Kuwait", "Kyrgyzstan",
            "Lao People's Democratic Republic", "Latvia", "Lebanon", "Lesotho", "Liberia",
            "Libyan Arab Jamahiriya", "Liechtenstein", "Lithuania", "Luxembourg", "Macao",
            "Macedonia, the Former Yugosalv Republic of", "Madagascar", "Malawi", "Malaysia", "Maldives",
            "Mali", "Malta", "Marshall Islands", "Martinique", "Mauritania", "Mauritius", "Mayotte",
            "Mexico", "Micronesia, Federated States of", "Moldova, Republic of", "Monaco", "Mongolia",
            "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands",
            "Netherlands Antilles", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria",
            "Niue", "Norfolk Island", "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau",
            "Palestinian Territory", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines",
            "Pitcairn", "Poland", "Portugal", "Puerto Rico", "Qatar", "Reunion", "Romania",
            "Russian Federation", "Rwanda", "Saint Helena", "Saint Kitts and Nevis", "Saint Lucia",
            "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", "Samoa", "San Marino",
            "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia and Montenegro", "Seychelles",
            "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
            "South Africa", "South Georgia and the South Sandwich Islands", "Spain", "Sri Lanka",
            "Sudan", "Suriname", "Svalbard and Jan Mayen", "Swaziland", "Sweden", "Switzerland",
            "Syrian Arab Republic", "Taiwan", "Tajikistan", "Tanzania, United Republic of", "Thailand",
            "Togo", "Tokelau", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan",
            "Turks and Caicos Islands", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates",
            "United Kingdom", "United States", "United States Minor Outlying Islands", "Uruguay",
            "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Virgin Islands, British",
            "Virgin Islands, U.S.", "Wallis and Futuna", "Western Sahara", "Yemen", "Yugoslavia",
            "Zambia", "Zimbabwe"
        ]
    
    @staticmethod
    def _get_forvo_languages() -> List[str]:
        """
        Get list of Forvo languages.
        
        Returns:
            List of language names
        """
        return [
            "Afrikaans", "Ancient Greek", "Arabic", "Armenian", "Azerbaijani", "Bashkir", "Basque",
            "Belarusian", "Bengali", "Bulgarian", "Cantonese", "Catalan", "Chuvash", "Croatian",
            "Czech", "Danish", "Dutch", "English", "Esperanto", "Estonian", "Finnish", "French",
            "Galician", "German", "Greek", "Hakka", "Hebrew", "Hindi", "Hungarian", "Icelandic",
            "Indonesian", "Interlingua", "Irish", "Italian", "Japanese", "Kabardian", "Korean",
            "Kurdish", "Latin", "Latvian", "Lithuanian", "Low German", "Luxembourgish",
            "Mandarin Chinese", "Mari", "Min Nan", "Northern Sami", "Norwegian Bokmål", "Persian",
            "Polish", "Portuguese", "Punjabi", "Romanian", "Russian", "Serbian", "Slovak", "Slovenian",
            "Spanish", "Swedish", "Tagalog", "Tatar", "Thai", "Turkish", "Ukrainian", "Urdu", "Uyghur",
            "Venetian", "Vietnamese", "Welsh", "Wu Chinese", "Yiddish"
        ]
