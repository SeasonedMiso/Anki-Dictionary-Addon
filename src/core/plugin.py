# -*- coding: utf-8 -*-
"""
Main plugin class for Anki Dictionary.
"""

from typing import Optional, Any, TYPE_CHECKING
from pathlib import Path
import os
import logging

from ..config import ConfigManager
from ..database import DatabaseConnection, DictionaryRepository
from ..services import SearchService, ExportService, MediaService
from ..constants import VERSION, DB_FILENAME

if TYPE_CHECKING:
    from ..ui import (
        DictionaryWindow,
        SettingsWindow,
        DictionaryManagerWidget,
        EditorIntegration,
        BrowserIntegration,
        MenuManager
    )


logger = logging.getLogger('anki_dictionary.plugin')


class AnkiDictionaryPlugin:
    """
    Main plugin class that coordinates all addon functionality.
    
    This class manages the lifecycle of all services and UI components,
    providing centralized access and coordination between different parts
    of the addon.
    """
    
    def __init__(self, mw: Any):
        """
        Initialize the plugin.
        
        Args:
            mw: Anki main window instance
        """
        self.mw = mw
        self.addon_path = Path(__file__).parent.parent.parent
        self.version = VERSION
        
        # Configuration
        self.config_manager = ConfigManager(mw.addonManager)
        
        # Database
        from ..database.dictdb import DictDB
        db_path = self.addon_path / 'user_files' / 'db' / DB_FILENAME
        self.db_connection = DatabaseConnection(str(db_path))
        self.dictionary_repo = DictionaryRepository(self.db_connection)
        self.dictdb = DictDB(repository=self.dictionary_repo)  # Legacy DictDB wrapper with shared repository
        
        # Services
        self.search_service = SearchService(
            self.dictionary_repo,
            self.addon_path
        )
        self.export_service = ExportService(mw)
        self.media_service = MediaService(
            mw,
            self.config_manager,
            self.addon_path
        )
        
        # UI Components (lazy initialization)
        self._dictionary_window: Optional['DictionaryWindow'] = None
        self._settings_window: Optional['SettingsWindow'] = None
        self._dictionary_manager: Optional['DictionaryManagerWidget'] = None
        self._editor_integration: Optional['EditorIntegration'] = None
        self._browser_integration: Optional['BrowserIntegration'] = None
        self._menu_manager: Optional['MenuManager'] = None
        
        # Initialize state
        self._initialize_state()
    
    def _initialize_state(self) -> None:
        """
        Initialize plugin state variables.
        
        Sets up backward compatibility variables on the main window object.
        """
        # Attach to main window for backward compatibility
        self.mw.AnkiDictConfig = self.config_manager.get_config()
        self.mw.DictExportingDefinitions = False
        self.mw.dictSettings = False
        self.mw.misoEditorLoadedAfterDictionary = False
        self.mw.DictBulkMediaExportWasCancelled = False
        
        # Set up refresh callback
        self.mw.refreshAnkiDictConfig = self.refresh_config
        
        # Attach DictDB for backward compatibility
        self.mw.miDictDB = self.dictdb
    
    def refresh_config(self, config: Optional[dict] = None) -> None:
        """
        Refresh the configuration and notify dependent services.
        
        Args:
            config: Optional new configuration to use
        """
        if config:
            self.config_manager.write_config(config)
            self.mw.AnkiDictConfig = config
        else:
            self.config_manager.refresh()
            self.mw.AnkiDictConfig = self.config_manager.get_config()
        
        # Notify services of configuration change
        self._notify_config_change()
    
    def initialize(self) -> None:
        """
        Initialize the plugin (called after Anki is fully loaded).
        
        This method sets up hooks, UI components, menus, and performs
        initial cleanup operations.
        """
        logger.info(f"Initializing Anki Dictionary Plugin v{self.version}")
        try:
            self._setup_hooks()
            self._setup_ui()
            self._cleanup_temp_files()
            logger.info("Plugin initialization complete")
        except Exception as e:
            logger.error(f"Error during plugin initialization: {e}", exc_info=True)
    
    def _setup_ui(self) -> None:
        """
        Set up UI components.
        
        Initializes MenuManager, EditorIntegration, and BrowserIntegration.
        Windows (dictionary, settings, manager) are lazily initialized on first use.
        """
        try:
            # Initialize menu manager (always initialized)
            from ..ui import MenuManager
            self._menu_manager = MenuManager(self.mw, self)
            self._menu_manager.setup_menu()
            self._menu_manager.setup_global_hotkeys()
            logger.debug("Menu manager initialized")
            
            # Initialize editor integration
            from ..ui import EditorIntegration
            self._editor_integration = EditorIntegration(self)
            self._editor_integration.setup_editor_hooks()
            logger.debug("Editor integration initialized")
            
            # Initialize browser integration
            from ..ui import BrowserIntegration
            self._browser_integration = BrowserIntegration(self)
            self._browser_integration.setup_browser_hooks()
            logger.debug("Browser integration initialized")
            
            logger.info("UI components initialized successfully")
        except Exception as e:
            logger.error(f"Error setting up UI: {e}", exc_info=True)
    
    def _setup_hooks(self) -> None:
        """Register all Anki hooks."""
        try:
            from anki.hooks import addHook
            
            # Editor hooks
            addHook('setupEditorButtons', self._on_setup_editor_buttons)
            addHook('EditorWebView.contextMenuEvent', self._on_editor_context_menu)
            
            # Reviewer hooks
            addHook('showQuestion', self._on_show_question)
            addHook('showAnswer', self._on_show_answer)
            
            # Browser hooks
            addHook('browser.setupMenus', self._on_browser_setup_menus)
            
            # Profile hooks
            addHook('profileLoaded', self._on_profile_loaded)
            addHook('unloadProfile', self._on_unload_profile)
            
            # Card hooks
            addHook('prepareFields', self._on_prepare_fields)
            
            logger.debug("Hooks registered successfully")
        except Exception as e:
            logger.error(f"Error registering hooks: {e}", exc_info=True)
    
    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        try:
            self.media_service.cleanup_temp_media()
            logger.debug("Temporary files cleaned up")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {e}")
    
    # Hook handler methods
    
    def _on_setup_editor_buttons(self, buttons: list, editor: Any) -> None:
        """
        Handle editor button setup hook.
        
        Args:
            buttons: List of editor buttons
            editor: Editor instance
        """
        # This will be implemented with the UI refactoring
        logger.debug("Editor buttons setup hook triggered")
        pass
    
    def _on_editor_context_menu(self, web_view: Any, menu: Any) -> None:
        """
        Handle editor context menu hook.
        
        Args:
            web_view: Editor web view
            menu: Context menu
        """
        # This will be implemented with the UI refactoring
        logger.debug("Editor context menu hook triggered")
        pass
    
    def _on_show_question(self) -> None:
        """Handle show question hook."""
        # This will be implemented with the UI refactoring
        logger.debug("Show question hook triggered")
        pass
    
    def _on_show_answer(self) -> None:
        """Handle show answer hook."""
        # This will be implemented with the UI refactoring
        logger.debug("Show answer hook triggered")
        pass
    
    def _on_browser_setup_menus(self, browser: Any) -> None:
        """
        Handle browser menu setup hook.
        
        Args:
            browser: Browser instance
        """
        # This will be implemented with the UI refactoring
        logger.debug("Browser menus setup hook triggered")
        pass
    
    def _on_profile_loaded(self) -> None:
        """Handle profile loaded hook."""
        logger.debug("Profile loaded hook triggered")
        # Reload conjugations when profile loads
        try:
            self.search_service.reload_conjugations()
        except Exception as e:
            logger.warning(f"Error reloading conjugations: {e}")
    
    def _on_unload_profile(self) -> None:
        """Handle unload profile hook."""
        logger.debug("Profile unload hook triggered")
        self.cleanup()
    
    def _on_prepare_fields(self, fields: dict, note: Any, model: Any, data: Any, col: Any) -> None:
        """
        Handle prepare fields hook for auto-definition.
        
        Args:
            fields: Field dictionary
            note: Note instance
            model: Note model
            data: Additional data
            col: Collection instance
        """
        # This will be implemented with the UI refactoring
        logger.debug("Prepare fields hook triggered")
        pass
    
    def _notify_config_change(self) -> None:
        """Notify services of configuration changes."""
        logger.debug("Notifying services of configuration change")
        # Services can reload their configuration-dependent data here
        try:
            self.search_service.reload_conjugations()
        except Exception as e:
            logger.warning(f"Error notifying services of config change: {e}")
    
    # Service accessor methods
    
    def get_search_service(self) -> SearchService:
        """
        Get search service instance.
        
        Returns:
            SearchService instance
        """
        return self.search_service
    
    def get_export_service(self) -> ExportService:
        """
        Get export service instance.
        
        Returns:
            ExportService instance
        """
        return self.export_service
    
    def get_media_service(self) -> MediaService:
        """
        Get media service instance.
        
        Returns:
            MediaService instance
        """
        return self.media_service
    
    def get_dictionary_repository(self) -> DictionaryRepository:
        """
        Get dictionary repository instance.
        
        Returns:
            DictionaryRepository instance
        """
        return self.dictionary_repo
    
    def get_config_manager(self) -> ConfigManager:
        """
        Get configuration manager instance.
        
        Returns:
            ConfigManager instance
        """
        return self.config_manager
    
    def cleanup(self) -> None:
        """
        Clean up resources on shutdown.
        
        Closes windows, cleans up temporary files, and closes database connections.
        """
        logger.info("Cleaning up plugin resources")
        try:
            # Clean up UI resources
            self._cleanup_ui_resources()
            
            # Clean up temporary media files
            self.media_service.cleanup_temp_media()
            
            # Close database connection
            self.db_connection.close()
            
            logger.info("Plugin cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
    
    def _cleanup_ui_resources(self) -> None:
        """
        Clean up UI component resources.
        
        Closes all open windows and releases UI resources.
        """
        try:
            # Close dictionary window
            if self._dictionary_window is not None:
                try:
                    if hasattr(self._dictionary_window, 'close'):
                        self._dictionary_window.close()
                except Exception as e:
                    logger.warning(f"Error closing dictionary window: {e}")
                self._dictionary_window = None
            
            # Close settings window
            if self._settings_window is not None:
                try:
                    if hasattr(self._settings_window, 'close'):
                        self._settings_window.close()
                except Exception as e:
                    logger.warning(f"Error closing settings window: {e}")
                self._settings_window = None
            
            # Close dictionary manager
            if self._dictionary_manager is not None:
                try:
                    if hasattr(self._dictionary_manager, 'close'):
                        self._dictionary_manager.close()
                except Exception as e:
                    logger.warning(f"Error closing dictionary manager: {e}")
                self._dictionary_manager = None
            
            logger.debug("UI resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up UI resources: {e}", exc_info=True)
    
    # UI Component Accessor Methods
    
    def get_dictionary_window(self) -> 'DictionaryWindow':
        """
        Get or create dictionary window (lazy initialization).
        
        Returns:
            DictionaryWindow instance
        """
        if self._dictionary_window is None:
            from ..ui import DictionaryWindow
            self._dictionary_window = DictionaryWindow(
                self.mw,
                self.search_service,
                self.export_service,
                self.media_service,
                self.config_manager,
                self.addon_path
            )
            logger.debug("Dictionary window created")
        return self._dictionary_window
    
    def get_settings_window(self) -> 'SettingsWindow':
        """
        Get or create settings window (lazy initialization).
        
        Returns:
            SettingsWindow instance
        """
        if self._settings_window is None:
            from ..ui import SettingsWindow
            self._settings_window = SettingsWindow(
                self.mw,
                self.config_manager,
                self,
                self.addon_path
            )
            logger.debug("Settings window created")
        return self._settings_window
    
    def get_dictionary_manager(self) -> 'DictionaryManagerWidget':
        """
        Get or create dictionary manager (lazy initialization).
        
        Returns:
            DictionaryManagerWidget instance
        """
        if self._dictionary_manager is None:
            from ..ui import DictionaryManagerWidget
            self._dictionary_manager = DictionaryManagerWidget(
                self.mw,
                self.dictionary_repo,
                self.config_manager,
                self.addon_path
            )
            logger.debug("Dictionary manager created")
        return self._dictionary_manager
    
    def get_menu_manager(self) -> Optional['MenuManager']:
        """
        Get menu manager instance.
        
        Returns:
            MenuManager instance or None if not initialized
        """
        return self._menu_manager
    
    def get_editor_integration(self) -> Optional['EditorIntegration']:
        """
        Get editor integration instance.
        
        Returns:
            EditorIntegration instance or None if not initialized
        """
        return self._editor_integration
    
    def get_browser_integration(self) -> Optional['BrowserIntegration']:
        """
        Get browser integration instance.
        
        Returns:
            BrowserIntegration instance or None if not initialized
        """
        return self._browser_integration
    
    # Convenience Methods for Opening Windows
    
    def open_dictionary(self, terms: Optional[list] = None) -> None:
        """
        Open the dictionary window.
        
        Args:
            terms: Optional list of terms to search
        """
        dict_window = self.get_dictionary_window()
        dict_window.show_window(terms)
    
    def close_dictionary(self) -> None:
        """Close the dictionary window if it's open."""
        if self._dictionary_window is not None:
            try:
                if hasattr(self._dictionary_window, 'isVisible') and self._dictionary_window.isVisible():
                    self._dictionary_window.hide()
            except Exception as e:
                logger.warning(f"Error closing dictionary window: {e}")
    
    def open_settings(self) -> None:
        """Open the settings window."""
        settings_window = self.get_settings_window()
        if hasattr(settings_window, 'show'):
            settings_window.show()
        if hasattr(settings_window, 'raise_'):
            settings_window.raise_()
        if hasattr(settings_window, 'activateWindow'):
            settings_window.activateWindow()
    
    def open_dictionary_manager(self) -> None:
        """Open the dictionary manager window."""
        manager = self.get_dictionary_manager()
        if hasattr(manager, 'show'):
            manager.show()
        if hasattr(manager, 'raise_'):
            manager.raise_()
        if hasattr(manager, 'activateWindow'):
            manager.activateWindow()
    
    def get_addon_path(self) -> Path:
        """
        Get the addon directory path.
        
        Returns:
            Path to the addon directory
        """
        return self.addon_path
    
    # Backward Compatibility Properties
    
    @property
    def dictionary_window(self) -> Optional['DictionaryWindow']:
        """
        Backward compatibility property for dictionary_window.
        
        Returns:
            DictionaryWindow instance or None
        """
        return self._dictionary_window
    
    @dictionary_window.setter
    def dictionary_window(self, value: Optional['DictionaryWindow']) -> None:
        """
        Backward compatibility setter for dictionary_window.
        
        Args:
            value: DictionaryWindow instance or None
        """
        self._dictionary_window = value
    
    @property
    def settings_window(self) -> Optional['SettingsWindow']:
        """
        Backward compatibility property for settings_window.
        
        Returns:
            SettingsWindow instance or None
        """
        return self._settings_window
    
    @settings_window.setter
    def settings_window(self, value: Optional['SettingsWindow']) -> None:
        """
        Backward compatibility setter for settings_window.
        
        Args:
            value: SettingsWindow instance or None
        """
        self._settings_window = value
    
    @property
    def editor_integration(self) -> Optional['EditorIntegration']:
        """
        Backward compatibility property for editor_integration.
        
        Returns:
            EditorIntegration instance or None
        """
        return self._editor_integration
    
    @editor_integration.setter
    def editor_integration(self, value: Optional['EditorIntegration']) -> None:
        """
        Backward compatibility setter for editor_integration.
        
        Args:
            value: EditorIntegration instance or None
        """
        self._editor_integration = value
