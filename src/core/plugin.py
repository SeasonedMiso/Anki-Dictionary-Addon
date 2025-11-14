# -*- coding: utf-8 -*-
"""
Main plugin class for Anki Dictionary.
"""

from typing import Optional, Any
from pathlib import Path
import os
import logging

from ..config import ConfigManager
from ..database import DatabaseConnection, DictionaryRepository
from ..services import SearchService, ExportService, MediaService
from ..constants import VERSION


logger = logging.getLogger('anki_dictionary.plugin')


class AnkiDictionaryPlugin:
    """Main plugin class that coordinates all addon functionality."""
    
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
        db_path = self.addon_path / 'user_files' / 'db' / 'dictionaries.db'
        self.db_connection = DatabaseConnection(str(db_path))
        self.dictionary_repo = DictionaryRepository(self.db_connection)
        
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
        
        # UI references (for backward compatibility)
        self.dictionary_window: Optional[Any] = None
        self.settings_window: Optional[Any] = None
        
        # Initialize state
        self._initialize_state()
    
    def _initialize_state(self) -> None:
        """Initialize plugin state variables."""
        # Attach to main window for backward compatibility
        self.mw.AnkiDictConfig = self.config_manager.get_config()
        self.mw.DictExportingDefinitions = False
        self.mw.dictSettings = False
        self.mw.misoEditorLoadedAfterDictionary = False
        self.mw.DictBulkMediaExportWasCancelled = False
        
        # Set up refresh callback
        self.mw.refreshAnkiDictConfig = self.refresh_config
        
        # Attach repository for backward compatibility
        self.mw.miDictDB = self.dictionary_repo
    
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
        """Initialize the plugin (called after Anki is fully loaded)."""
        logger.info(f"Initializing Anki Dictionary Plugin v{self.version}")
        try:
            self._setup_hooks()
            self._setup_menu()
            self._setup_hotkeys()
            self._cleanup_temp_files()
            logger.info("Plugin initialization complete")
        except Exception as e:
            logger.error(f"Error during plugin initialization: {e}", exc_info=True)
    
    def _setup_menu(self) -> None:
        """Set up the addon menu."""
        # This will be implemented with the UI refactoring
        logger.debug("Menu setup placeholder")
        pass
    
    def _setup_hotkeys(self) -> None:
        """Set up global hotkeys."""
        # This will be implemented with the UI refactoring
        logger.debug("Hotkeys setup placeholder")
        pass
    
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
        """Clean up resources on shutdown."""
        logger.info("Cleaning up plugin resources")
        try:
            # Clean up temporary media files
            self.media_service.cleanup_temp_media()
            
            # Close database connection
            self.db_connection.close()
            
            logger.info("Plugin cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
    
    def open_dictionary(self, terms: Optional[list] = None) -> None:
        """
        Open the dictionary window.
        
        Args:
            terms: Optional list of terms to search
        """
        # This will be implemented with the UI refactoring
        pass
    
    def close_dictionary(self) -> None:
        """Close the dictionary window."""
        if self.dictionary_window and self.dictionary_window.isVisible():
            self.dictionary_window.hide()
    
    def open_settings(self) -> None:
        """Open the settings window."""
        # This will be implemented with the UI refactoring
        pass
    
    def get_addon_path(self) -> Path:
        """Get the addon directory path."""
        return self.addon_path
