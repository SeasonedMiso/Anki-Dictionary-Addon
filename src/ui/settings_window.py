# -*- coding: utf-8 -*-
"""
Settings Window UI component.

Refactored settings window that uses ConfigManager for all configuration operations.
"""

from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING
import logging
from pathlib import Path
from os.path import join

from anki.utils import is_mac, is_win, is_lin
from aqt.qt import *
from aqt.utils import showInfo, tooltip

from ..config.manager import ConfigManager
from ..utils.dialogs import miInfo, miAsk

if TYPE_CHECKING:
    from ..core.plugin import AnkiDictionaryPlugin

logger = logging.getLogger('anki_dictionary.ui.settings')


class SettingsWindow(QTabWidget):
    """Settings configuration window."""
    
    def __init__(
        self,
        mw: Any,
        config_manager: ConfigManager,
        plugin: 'AnkiDictionaryPlugin',
        addon_path: Path,
        reboot_callback: Optional[Any] = None
    ):
        """
        Initialize settings window.
        
        Args:
            mw: Anki main window
            config_manager: Configuration manager instance
            plugin: Plugin coordinator instance
            addon_path: Path to addon directory
            reboot_callback: Optional callback to reboot settings window
        """
        super(SettingsWindow, self).__init__()
        
        self.mw = mw
        self.config_manager = config_manager
        self.plugin = plugin
        self.addon_path = addon_path
        self.reboot_callback = reboot_callback
        
        # Country and language lists
        self.google_countries = self._get_google_countries()
        self.forvo_languages = self._get_forvo_languages()
        
        # Window setup
        self._setup_window()
        
        # Create UI widgets
        self._create_widgets()
        
        # Setup layout
        self._setup_layout()
        
        # Load current configuration
        self.load_settings()
        
        # Initialize tooltips
        self._init_tooltips()
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
        
        # Show window
        self.show()
    
    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setMinimumSize(850, 550)
        if not is_win:
            self.resize(1034, 550)
        else:
            self.resize(920, 550)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setWindowTitle("Anki Dictionary Settings")
        self.setWindowIcon(QIcon(join(str(self.addon_path), 'icons', 'miso.png')))
    
    def _create_widgets(self) -> None:
        """Create all UI widgets."""
        # Dictionary groups and templates tables
        self.dict_groups = self._get_group_template_table()
        self.export_templates = self._get_group_template_table()
        
        # Buttons
        self.add_dict_group = QPushButton('Add Dictionary Group')
        self.add_export_template = QPushButton('Add Export Template')
        self.restore_button = QPushButton('Restore Defaults')
        self.cancel_button = QPushButton('Cancel')
        self.apply_button = QPushButton('Apply')
        self.choose_audio_directory = QPushButton("Choose Directory")
        
        # Checkboxes
        self.tooltip_cb = QCheckBox()
        self.tooltip_cb.setFixedHeight(30)
        self.safe_search = QCheckBox()
        self.convert_to_mp3 = QCheckBox()
        self.disable_condensed_messages = QCheckBox()
        self.dict_on_top = QCheckBox()
        self.show_target = QCheckBox()
        self.gen_js_export = QCheckBox()
        self.gen_js_edit = QCheckBox()
        self.highlight_target = QCheckBox()
        self.highlight_sentence = QCheckBox()
        self.open_on_start = QCheckBox()
        self.global_hotkeys = QCheckBox()
        self.global_open = QCheckBox()
        
        # Spin boxes
        self.max_img_width = QSpinBox()
        self.max_img_width.setRange(0, 9999)
        self.max_img_height = QSpinBox()
        self.max_img_height.setRange(0, 9999)
        self.total_defs = QSpinBox()
        self.total_defs.setRange(0, 1000)
        self.dict_defs = QSpinBox()
        self.dict_defs.setRange(0, 100)
        
        # Combo boxes
        self.google_country = QComboBox()
        self.google_country.addItems(self.google_countries)
        self.forvo_lang = QComboBox()
        self.forvo_lang.addItems(self.forvo_languages)
        
        # Line edits
        self.front_bracket = QLineEdit()
        self.back_bracket = QLineEdit()
        
        # Labels
        self.condensed_audio_directory_label = QLabel("Condensed Audio Save Location:")
        
        # Connect signals
        self._connect_signals()
    
    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        self.add_dict_group.clicked.connect(self._add_group)
        self.add_export_template.clicked.connect(self._add_template)
        self.restore_button.clicked.connect(self._restore_defaults)
        self.cancel_button.clicked.connect(self.close)
        self.apply_button.clicked.connect(self.save_settings)
        self.choose_audio_directory.clicked.connect(self._update_audio_directory)
    
    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        self.hotkey_esc = QShortcut(QKeySequence("Esc"), self)
        self.hotkey_esc.activated.connect(self.close)
    
    def load_settings(self) -> None:
        """Load current settings from ConfigManager."""
        try:
            # Load boolean settings
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
            
            # Load integer settings
            self.total_defs.setValue(self.config_manager.get_int('maxSearch', 1000))
            self.dict_defs.setValue(self.config_manager.get_int('dictSearch', 50))
            self.max_img_width.setValue(self.config_manager.get_int('maxWidth', 400))
            self.max_img_height.setValue(self.config_manager.get_int('maxHeight', 400))
            
            # Load string settings
            self.google_country.setCurrentText(self.config_manager.get_str('googleSearchRegion', 'United States'))
            self.forvo_lang.setCurrentText(self.config_manager.get_str('ForvoLanguage', 'Japanese'))
            self.front_bracket.setText(self.config_manager.get_str('frontBracket', '【'))
            self.back_bracket.setText(self.config_manager.get_str('backBracket', '】'))
            
            # Load audio directory
            audio_dir = self.config_manager.get_value('condensedAudioDirectory', False)
            if audio_dir and audio_dir is not False:
                self.choose_audio_directory.setText(str(audio_dir))
            else:
                self.choose_audio_directory.setText("Choose Directory")
            
            # Load dictionary groups and templates tables
            self._load_group_table()
            self._load_template_table()
            
            logger.debug("Settings loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            showInfo(f"Error loading settings: {str(e)}")
    
    def validate_settings(self) -> Tuple[bool, Optional[str]]:
        """
        Validate settings before saving.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        errors = []
        
        # Validate numeric ranges
        if self.total_defs.value() < 1:
            errors.append("Max Total Search Results must be at least 1")
        
        if self.dict_defs.value() < 1:
            errors.append("Max Dictionary Search Results must be at least 1")
        
        if self.max_img_width.value() < 50:
            errors.append("Maximum Image Width must be at least 50")
        
        if self.max_img_height.value() < 50:
            errors.append("Maximum Image Height must be at least 50")
        
        # Validate brackets
        if len(self.front_bracket.text()) > 10:
            errors.append("Front bracket text is too long (max 10 characters)")
        
        if len(self.back_bracket.text()) > 10:
            errors.append("Back bracket text is too long (max 10 characters)")
        
        # Validate selections
        if self.google_country.currentText() not in self.google_countries:
            errors.append("Invalid Google search region selected")
        
        if self.forvo_lang.currentText() not in self.forvo_languages:
            errors.append("Invalid Forvo language selected")
        
        if errors:
            return False, "\n".join(errors)
        
        return True, None
    
    def save_settings(self) -> bool:
        """
        Save settings via ConfigManager with validation.
        
        Returns:
            True if settings were saved successfully, False otherwise
        """
        try:
            # Validate settings first
            is_valid, error_message = self.validate_settings()
            if not is_valid:
                showInfo(
                    f"Settings validation failed:\n\n{error_message}",
                    title="Invalid Settings"
                )
                return False
            
            # Get current config
            config = self.config_manager.get_config().copy()
            
            # Update boolean settings
            config['dictOnStart'] = self.open_on_start.isChecked()
            config['highlightSentences'] = self.highlight_sentence.isChecked()
            config['highlightTarget'] = self.highlight_target.isChecked()
            config['jReadingCards'] = self.gen_js_export.isChecked()
            config['jReadingEdit'] = self.gen_js_edit.isChecked()
            config['showTarget'] = self.show_target.isChecked()
            config['tooltips'] = self.tooltip_cb.isChecked()
            config['globalHotkeys'] = self.global_hotkeys.isChecked()
            config['openOnGlobal'] = self.global_open.isChecked()
            config['mp3Convert'] = self.convert_to_mp3.isChecked()
            config['disableCondensed'] = self.disable_condensed_messages.isChecked()
            config['safeSearch'] = self.safe_search.isChecked()
            config['dictAlwaysOnTop'] = self.dict_on_top.isChecked()
            
            # Update integer settings
            config['maxSearch'] = self.total_defs.value()
            config['dictSearch'] = self.dict_defs.value()
            config['maxWidth'] = self.max_img_width.value()
            config['maxHeight'] = self.max_img_height.value()
            
            # Update string settings
            config['googleSearchRegion'] = self.google_country.currentText()
            config['ForvoLanguage'] = self.forvo_lang.currentText()
            config['frontBracket'] = self.front_bracket.text()
            config['backBracket'] = self.back_bracket.text()
            
            # Update audio directory
            if self.choose_audio_directory.text() != "Choose Directory":
                config['condensedAudioDirectory'] = self.choose_audio_directory.text()
            else:
                config['condensedAudioDirectory'] = False
            
            # Write config via ConfigManager
            self.config_manager.write_config(config)
            
            # Hide window
            self.hide()
            
            # Notify plugin of config changes
            if hasattr(self.plugin, 'refresh_config'):
                self.plugin.refresh_config()
            
            # Install FFMPEG if needed
            if config['mp3Convert']:
                if hasattr(self.plugin, 'ffmpeg_installer'):
                    self.plugin.ffmpeg_installer.installFFMPEG()
            
            # Show notification if dictionary window is open
            if hasattr(self.mw, 'ankiDictionary') and self.mw.ankiDictionary and self.mw.ankiDictionary.isVisible():
                miInfo(
                    'Please be aware that the dictionary window will not reflect any setting changes until it is closed and reopened.',
                    level='not'
                )
            
            logger.info("Settings saved successfully")
            return True
            
        except ValueError as e:
            logger.error(f"Settings validation error: {e}")
            showInfo(
                f"Settings validation failed:\n\n{str(e)}",
                title="Invalid Settings"
            )
            return False
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            showInfo(
                f"Error saving settings:\n\n{str(e)}",
                title="Save Error"
            )
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        if miAsk('This will remove any export templates and dictionary groups you have created, and is not undoable. Are you sure you would like to restore the default settings?'):
            try:
                self.config_manager.reset_to_defaults()
                self.close()
                if self.reboot_callback:
                    self.reboot_callback()
                logger.info("Settings reset to defaults")
            except Exception as e:
                logger.error(f"Error resetting settings: {e}")
                showInfo(f"Error resetting settings: {str(e)}")
    
    def _restore_defaults(self) -> None:
        """Handler for restore defaults button."""
        self.reset_to_defaults()
    
    def _update_audio_directory(self) -> None:
        """Update condensed audio directory."""
        directory = str(QFileDialog.getExistingDirectory(None, "Select Condensed Audio Directory"))
        if directory:
            self.choose_audio_directory.setText(directory)
        else:
            self.choose_audio_directory.setText("Choose Directory")
    
    def _add_group(self) -> None:
        """Add a new dictionary group."""
        try:
            from ..addDictGroup import DictGroupEditor
            dict_editor = DictGroupEditor(self.mw, self, self._get_dictionary_names())
            dict_editor.clearGroupEditor(True)
            dict_editor.exec()
        except Exception as e:
            logger.error(f"Error adding dictionary group: {e}")
            showInfo(f"Error adding dictionary group: {str(e)}")
    
    def _add_template(self) -> None:
        """Add a new export template."""
        try:
            from ..addTemplate import TemplateEditor
            template_editor = TemplateEditor(self.mw, self, self._get_dictionary_names())
            template_editor.exec()
        except Exception as e:
            logger.error(f"Error adding export template: {e}")
            showInfo(f"Error adding export template: {str(e)}")
    
    def _load_group_table(self) -> None:
        """Load dictionary groups into table."""
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
    
    def _edit_group_row(self, row: int):
        """Create handler for editing group row."""
        def handler():
            self._edit_group(row)
        return handler
    
    def _remove_group_row(self, row: int):
        """Create handler for removing group row."""
        def handler():
            self._remove_group(row)
        return handler
    
    def _edit_temp_row(self, row: int):
        """Create handler for editing template row."""
        def handler():
            self._edit_template(row)
        return handler
    
    def _remove_temp_row(self, row: int):
        """Create handler for removing template row."""
        def handler():
            self._remove_template(row)
        return handler
    
    def _edit_group(self, row: int) -> None:
        """Edit a dictionary group."""
        try:
            group_name = self.dict_groups.item(row, 0).text()
            dict_groups = self.config_manager.get_dictionary_groups()
            
            if group_name in dict_groups:
                from ..addDictGroup import DictGroupEditor
                group = dict_groups[group_name]
                dict_editor = DictGroupEditor(self.mw, self, self._get_dictionary_names(), group, group_name)
                dict_editor.exec()
        except Exception as e:
            logger.error(f"Error editing dictionary group: {e}")
            showInfo(f"Error editing dictionary group: {str(e)}")
    
    def _remove_group(self, row: int) -> None:
        """Remove a dictionary group."""
        if miAsk('Are you sure you would like to remove this dictionary group? This action will happen immediately and is not un-doable.', self):
            try:
                config = self.config_manager.get_config().copy()
                dict_groups = config['DictionaryGroups']
                group_name = self.dict_groups.item(row, 0).text()
                del dict_groups[group_name]
                self.config_manager.write_config(config)
                self.dict_groups.removeRow(row)
                self._load_group_table()
                logger.info(f"Removed dictionary group: {group_name}")
            except Exception as e:
                logger.error(f"Error removing dictionary group: {e}")
                showInfo(f"Error removing dictionary group: {str(e)}")
    
    def _edit_template(self, row: int) -> None:
        """Edit an export template."""
        try:
            template_name = self.export_templates.item(row, 0).text()
            export_templates = self.config_manager.get_export_templates()
            
            if template_name in export_templates:
                from ..addTemplate import TemplateEditor
                template = export_templates[template_name]
                template_editor = TemplateEditor(self.mw, self, self._get_dictionary_names(), template, template_name)
                template_editor.loadTemplateEditor(template, template_name)
                template_editor.exec()
        except Exception as e:
            logger.error(f"Error editing export template: {e}")
            showInfo(f"Error editing export template: {str(e)}")
    
    def _remove_template(self, row: int) -> None:
        """Remove an export template."""
        if miAsk('Are you sure you would like to remove this template? This action will happen immediately and is not un-doable.', self):
            try:
                config = self.config_manager.get_config().copy()
                export_templates = config['ExportTemplates']
                template_name = self.export_templates.item(row, 0).text()
                del export_templates[template_name]
                self.config_manager.write_config(config)
                self.export_templates.removeRow(row)
                self._load_template_table()
                logger.info(f"Removed export template: {template_name}")
            except Exception as e:
                logger.error(f"Error removing export template: {e}")
                showInfo(f"Error removing export template: {str(e)}")
    
    def _get_dictionary_names(self) -> list:
        """Get list of available dictionary names."""
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
            logger.error(f"Error getting dictionary names: {e}")
            return []
    
    def _clean_dict_name(self, name: str) -> str:
        """Clean dictionary name by removing language codes."""
        import re
        return re.sub(r'l\d+name', '', name)
    
    def _get_group_template_table(self) -> QTableWidget:
        """Create a table widget for groups or templates."""
        mac_lin = is_mac or is_lin
        
        table = QTableWidget()
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
        """Create a label with fixed dimensions."""
        label = QLabel(text)
        label.setFixedHeight(30)
        label.setFixedWidth(width)
        return label
    
    def _get_line_separator(self) -> QFrame:
        """Create a vertical line separator."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Plain)
        line.setStyleSheet('QFrame[frameShape="5"]{color: #D5DFE5;}')
        return line
    
    def _setup_layout(self) -> None:
        """Setup the main layout with all widgets."""
        # Create settings tab
        settings_tab = QWidget(self)
        layout = QVBoxLayout()
        
        # Dictionary groups and export templates section
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
        
        # Column 1
        opt_lay1 = QVBoxLayout()
        opt_lay1.addLayout(self._create_option_row('Open on Startup:', self.open_on_start, 182))
        opt_lay1.addLayout(self._create_option_row('Highlight Examples Sentences:', self.highlight_sentence, 182))
        opt_lay1.addLayout(self._create_option_row('Highlight Searched Term:', self.highlight_target, 182))
        opt_lay1.addLayout(self._create_option_row('Show Export Target:', self.show_target, 182))
        opt_lay1.addLayout(self._create_option_row('Dictionary Tooltips:', self.tooltip_cb, 182))
        opt_lay1.addLayout(self._create_option_row('Global Hotkeys:', self.global_hotkeys, 182))
        opt_lay1.addLayout(self._create_option_row("Convert Extension Audio to MP3", self.convert_to_mp3, 182))
        opt_lay1.addLayout(self._create_option_row("Disable Condensed Audio Messages:", self.disable_condensed_messages, 182))
        
        # Column 2
        opt_lay2 = QVBoxLayout()
        opt_lay2.addLayout(self._create_option_row('Open on Global Search:', self.global_open, 323))
        opt_lay2.addLayout(self._create_spinbox_row('Max Total Search Results:', self.total_defs, 180, 160))
        opt_lay2.addLayout(self._create_spinbox_row('Max Dictionary Search Results:', self.dict_defs, 180, 160))
        opt_lay2.addLayout(self._create_option_row('Add Cards with Japanese Readings:', self.gen_js_export, 323))
        opt_lay2.addLayout(self._create_option_row('Japanese Readings on Edit:', self.gen_js_edit, 323))
        opt_lay2.addLayout(self._create_combo_row('Google Images Search Region:', self.google_country, 180, 160))
        opt_lay2.addLayout(self._create_option_row('Safe Search:', self.safe_search, 323))
        opt_lay2.addStretch()
        
        # Column 3
        opt_lay3 = QVBoxLayout()
        opt_lay3.addLayout(self._create_spinbox_row('Maximum Image Width:', self.max_img_width, 140, None))
        opt_lay3.addLayout(self._create_spinbox_row('Maximum Image Height:', self.max_img_height, 140, None))
        opt_lay3.addLayout(self._create_lineedit_row('Surround Term (Front):', self.front_bracket, 140))
        opt_lay3.addLayout(self._create_lineedit_row('Surround Term (Back):', self.back_bracket, 140))
        opt_lay3.addLayout(self._create_combo_row('Forvo Language:', self.forvo_lang, 140, None))
        opt_lay3.addLayout(self._create_option_row("Always on Top:", self.dict_on_top, 323))
        
        # Audio directory row
        audio_lay = QHBoxLayout()
        audio_lay.addWidget(self.condensed_audio_directory_label)
        self.choose_audio_directory.setFixedWidth(100)
        audio_lay.addWidget(self.choose_audio_directory)
        opt_lay3.addLayout(audio_lay)
        opt_lay3.addStretch()
        
        # Combine columns
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
        settings_tab.setLayout(layout)
        
        # Add tabs
        self.addTab(settings_tab, "Settings")
        
        # Add dictionary manager tab if available
        try:
            from ..dictionaryManager import DictionaryManagerWidget
            self.addTab(DictionaryManagerWidget(), "Dictionaries")
        except Exception as e:
            logger.warning(f"Could not load dictionary manager tab: {e}")
    
    def _create_option_row(self, label_text: str, widget: QWidget, label_width: int) -> QHBoxLayout:
        """Create a row with label and checkbox."""
        layout = QHBoxLayout()
        layout.addWidget(self._mi_qlabel(label_text, label_width))
        layout.addWidget(widget)
        return layout
    
    def _create_spinbox_row(self, label_text: str, spinbox: QSpinBox, label_width: int, spinbox_width: Optional[int]) -> QHBoxLayout:
        """Create a row with label and spinbox."""
        layout = QHBoxLayout()
        layout.addWidget(self._mi_qlabel(label_text, label_width))
        if spinbox_width:
            spinbox.setFixedWidth(spinbox_width)
        layout.addWidget(spinbox)
        return layout
    
    def _create_combo_row(self, label_text: str, combo: QComboBox, label_width: int, combo_width: Optional[int]) -> QHBoxLayout:
        """Create a row with label and combobox."""
        layout = QHBoxLayout()
        layout.addWidget(self._mi_qlabel(label_text, label_width))
        if combo_width:
            combo.setFixedWidth(combo_width)
        layout.addWidget(combo)
        return layout
    
    def _create_lineedit_row(self, label_text: str, lineedit: QLineEdit, label_width: int) -> QHBoxLayout:
        """Create a row with label and line edit."""
        layout = QHBoxLayout()
        layout.addWidget(self._mi_qlabel(label_text, label_width))
        layout.addWidget(lineedit)
        return layout
    
    def _init_tooltips(self) -> None:
        """Initialize tooltips for all widgets."""
        self.add_dict_group.setToolTip(
            'Add a new dictionary group.\nDictionary groups allow you to specify which dictionaries to search\n'
            'within. You can also set a specific font for that group.'
        )
        self.add_export_template.setToolTip(
            'Add a new export template.\nExport templates allow you to specify a note type, and fields where\n'
            'target sentences, target words, definitions, and images will be sent to\n when using the Card Exporter to create cards.'
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
            'lets you know which window is currently selected and will be used when sending\ndefinitions to a target field.'
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
        self.front_bracket.setToolTip('This is the text that will be placed in front of each term\n in the dictionary.')
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
    
    def hideEvent(self, event: Any) -> None:
        """Handle window hide event."""
        self.mw.dictSettings = None
        event.accept()
    
    def closeEvent(self, event: Any) -> None:
        """Handle window close event."""
        self.mw.dictSettings = None
        event.accept()
    
    @staticmethod
    def _get_google_countries() -> list:
        """Get list of Google search countries."""
        return [
            "Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola", "Anguilla", "Antarctica",
            "Antigua and Barbuda", "Argentina", "Armenia", "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas",
            "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan",
            "Bolivia", "Bosnia and Herzegovina", "Botswana", "Bouvet Island", "Brazil", "British Indian Ocean Territory",
            "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde",
            "Cayman Islands", "Central African Republic", "Chad", "Chile", "China", "Christmas Island",
            "Cocos (Keeling) Islands", "Colombia", "Comoros", "Congo", "Congo, the Democratic Republic of the",
            "Cook Islands", "Costa Rica", "Cote D'ivoire", "Croatia (Hrvatska)", "Cuba", "Cyprus", "Czech Republic",
            "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador", "Egypt", "El Salvador",
            "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "European Union", "Falkland Islands (Malvinas)",
            "Faroe Islands", "Fiji", "Finland", "France", "France, Metropolitan", "French Guiana", "French Polynesia",
            "French Southern Territories", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece",
            "Greenland", "Grenada", "Guadeloupe", "Guam", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti",
            "Heard Island and Mcdonald Islands", "Holy See (Vatican City State)", "Honduras", "Hong Kong", "Hungary",
            "Iceland", "India", "Indonesia", "Iran, Islamic Republic of", "Iraq", "Ireland", "Israel", "Italy",
            "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, Democratic People's Republic of",
            "Korea, Republic of", "Kuwait", "Kyrgyzstan", "Lao People's Democratic Republic", "Latvia", "Lebanon",
            "Lesotho", "Liberia", "Libyan Arab Jamahiriya", "Liechtenstein", "Lithuania", "Luxembourg", "Macao",
            "Macedonia, the Former Yugosalv Republic of", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali",
            "Malta", "Marshall Islands", "Martinique", "Mauritania", "Mauritius", "Mayotte", "Mexico",
            "Micronesia, Federated States of", "Moldova, Republic of", "Monaco", "Mongolia", "Montserrat", "Morocco",
            "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "Netherlands Antilles",
            "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue", "Norfolk Island",
            "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau", "Palestinian Territory", "Panama",
            "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Pitcairn", "Poland", "Portugal", "Puerto Rico",
            "Qatar", "Reunion", "Romania", "Russian Federation", "Rwanda", "Saint Helena", "Saint Kitts and Nevis",
            "Saint Lucia", "Saint Pierre and Miquelon", "Saint Vincent and the Grenadines", "Samoa", "San Marino",
            "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia and Montenegro", "Seychelles", "Sierra Leone",
            "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa",
            "South Georgia and the South Sandwich Islands", "Spain", "Sri Lanka", "Sudan", "Suriname",
            "Svalbard and Jan Mayen", "Swaziland", "Sweden", "Switzerland", "Syrian Arab Republic", "Taiwan",
            "Tajikistan", "Tanzania, United Republic of", "Thailand", "Togo", "Tokelau", "Tonga",
            "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Turks and Caicos Islands", "Tuvalu",
            "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States",
            "United States Minor Outlying Islands", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam",
            "Virgin Islands, British", "Virgin Islands, U.S.", "Wallis and Futuna", "Western Sahara", "Yemen",
            "Yugoslavia", "Zambia", "Zimbabwe"
        ]
    
    @staticmethod
    def _get_forvo_languages() -> list:
        """Get list of Forvo languages."""
        return [
            "Afrikaans", "Ancient Greek", "Arabic", "Armenian", "Azerbaijani", "Bashkir", "Basque", "Belarusian",
            "Bengali", "Bulgarian", "Cantonese", "Catalan", "Chuvash", "Croatian", "Czech", "Danish", "Dutch",
            "English", "Esperanto", "Estonian", "Finnish", "French", "Galician", "German", "Greek", "Hakka",
            "Hebrew", "Hindi", "Hungarian", "Icelandic", "Indonesian", "Interlingua", "Irish", "Italian", "Japanese",
            "Kabardian", "Korean", "Kurdish", "Latin", "Latvian", "Lithuanian", "Low German", "Luxembourgish",
            "Mandarin Chinese", "Mari", "Min Nan", "Northern Sami", "Norwegian Bokmål", "Persian", "Polish",
            "Portuguese", "Punjabi", "Romanian", "Russian", "Serbian", "Slovak", "Slovenian", "Spanish", "Swedish",
            "Tagalog", "Tatar", "Thai", "Turkish", "Ukrainian", "Urdu", "Uyghur", "Venetian", "Vietnamese", "Welsh",
            "Wu Chinese", "Yiddish"
        ]
