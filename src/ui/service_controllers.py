# -*- coding: utf-8 -*-
"""
Service Controllers - Export, Config, History, and Media controllers.

These controllers coordinate between UI components and backend services.
"""

from typing import Optional, Dict, Any, Callable, List
import logging

try:
    from aqt.qt import QObject, pyqtSignal
except ImportError:
    class QObject:
        pass
    class pyqtSignal:
        def __init__(self, *args):
            pass
        def emit(self, *args):
            pass
        def connect(self, func):
            pass

from ..services.media_service import MediaService
from ..services.export_coordinator import ExportCoordinator
from ..services.config_service import ConfigService
from ..services.history_service import HistoryService

logger = logging.getLogger(__name__)


class ExportController(QObject):
    """
    Controller for export operations.
    
    Coordinates between export UI and ExportCoordinator backend,
    handling card creation and batch export to Anki.
    """
    
    exportStarted = pyqtSignal()
    exportCompleted = pyqtSignal(dict)  # Emits export result
    exportError = pyqtSignal(str)  # Emits error message
    
    def __init__(
        self,
        export_coordinator: ExportCoordinator,
        config_service: ConfigService
    ):
        """
        Initialize export controller.
        
        Args:
            export_coordinator: ExportCoordinator for export operations
            config_service: ConfigService for settings
        """
        super().__init__()
        self.export_coordinator = export_coordinator
        self.config_service = config_service
        logger.info("ExportController initialized")
    
    def export_word(
        self,
        word: str,
        definitions: List[Dict[str, Any]],
        deck_name: Optional[str] = None,
        template_name: Optional[str] = None
    ) -> None:
        """
        Export a word to Anki.
        
        Args:
            word: Word to export
            definitions: List of definition dicts
            deck_name: Target deck name
            template_name: Card template name
        """
        try:
            self.exportStarted.emit()
            
            result = self.export_coordinator.export_word(
                word=word,
                definitions=definitions,
                deck_name=deck_name,
                template_name=template_name
            )
            
            if result.get('error'):
                self.exportError.emit(result['error'])
                return
            
            self.exportCompleted.emit(result)
            logger.info(f"Exported '{word}' to Anki")
            
        except Exception as e:
            error_msg = f"Export error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.exportError.emit(error_msg)
    
    def get_available_decks(self) -> List[str]:
        """
        Get list of available Anki decks.
        
        Returns:
            List of deck names
        """
        try:
            result = self.export_coordinator.get_available_decks()
            return result.get('decks', [])
        except Exception as e:
            logger.error(f"Error getting decks: {e}")
            return []
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available card templates.
        
        Returns:
            List of template names
        """
        try:
            result = self.export_coordinator.get_available_templates()
            return result.get('templates', [])
        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            return []


class ConfigController(QObject):
    """
    Controller for configuration/settings operations.
    
    Coordinates between settings UI and ConfigService backend,
    handling settings persistence and theme management.
    """
    
    settingsSaved = pyqtSignal()
    settingsLoaded = pyqtSignal(dict)  # Emits settings dict
    settingsError = pyqtSignal(str)  # Emits error message
    
    def __init__(self, config_service: ConfigService):
        """
        Initialize config controller.
        
        Args:
            config_service: ConfigService for settings management
        """
        super().__init__()
        self.config_service = config_service
        logger.info("ConfigController initialized")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration setting.
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        try:
            result = self.config_service.get_setting(key)
            return result.get('value', default)
        except Exception as e:
            logger.error(f"Error getting setting '{key}': {e}")
            return default
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set a configuration setting.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.config_service.set_setting(key, value)
            
            if result.get('error'):
                self.settingsError.emit(result['error'])
                return False
            
            self.settingsSaved.emit()
            logger.info(f"Setting '{key}' saved")
            return True
            
        except Exception as e:
            error_msg = f"Error setting '{key}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.settingsError.emit(error_msg)
            return False
    
    def load_all_settings(self) -> Dict[str, Any]:
        """
        Load all settings.
        
        Returns:
            Dictionary of all settings
        """
        try:
            settings = self.config_service.get_all_settings()
            
            if isinstance(settings, dict) and settings.get('error'):
                self.settingsError.emit(settings['error'])
                return {}
            
            self.settingsLoaded.emit(settings)
            return settings
            
        except Exception as e:
            error_msg = f"Error loading settings: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.settingsError.emit(error_msg)
            return {}
    
    def export_settings(self, file_path: str) -> bool:
        """
        Export settings to file.
        
        Args:
            file_path: Path to export to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.config_service.export_settings(file_path)
            
            if result.get('error'):
                self.settingsError.emit(result['error'])
                return False
            
            logger.info(f"Settings exported to {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Error exporting settings: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.settingsError.emit(error_msg)
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """
        Import settings from file.
        
        Args:
            file_path: Path to import from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.config_service.import_settings(file_path)
            
            if result.get('error'):
                self.settingsError.emit(result['error'])
                return False
            
            self.settingsSaved.emit()
            logger.info(f"Settings imported from {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"Error importing settings: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.settingsError.emit(error_msg)
            return False


class HistoryController(QObject):
    """
    Controller for search history operations.
    
    Coordinates between history UI and HistoryService backend,
    handling search history tracking and retrieval.
    """
    
    historyUpdated = pyqtSignal(list)  # Emits history list
    historyError = pyqtSignal(str)  # Emits error message
    
    def __init__(self, history_service: HistoryService):
        """
        Initialize history controller.
        
        Args:
            history_service: HistoryService for history management
        """
        super().__init__()
        self.history_service = history_service
        logger.info("HistoryController initialized")
    
    def add_to_history(self, word: str, definition: Optional[str] = None) -> None:
        """
        Add a word to search history.
        
        Args:
            word: Word to add
            definition: Optional definition text
        """
        try:
            result = self.history_service.add_entry(word, definition)
            
            if result.get('error'):
                logger.warning(f"Error adding to history: {result['error']}")
                return
            
            logger.debug(f"Added '{word}' to history")
            
        except Exception as e:
            logger.error(f"Error adding to history: {e}")
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get search history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of history entries
        """
        try:
            result = self.history_service.get_history(limit)
            
            if result.get('error'):
                self.historyError.emit(result['error'])
                return []
            
            history = result.get('entries', [])
            self.historyUpdated.emit(history)
            return history
            
        except Exception as e:
            error_msg = f"Error getting history: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.historyError.emit(error_msg)
            return []
    
    def clear_history(self) -> bool:
        """
        Clear all search history.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.history_service.clear_history()
            
            if result.get('error'):
                self.historyError.emit(result['error'])
                return False
            
            self.historyUpdated.emit([])
            logger.info("History cleared")
            return True
            
        except Exception as e:
            error_msg = f"Error clearing history: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.historyError.emit(error_msg)
            return False


class MediaController(QObject):
    """
    Controller for media operations (audio/images).
    
    Coordinates between UI action buttons and MediaService backend.
    """
    
    audioStarted = pyqtSignal()
    audioCompleted = pyqtSignal(str)  # Emits file path
    audioError = pyqtSignal(str)  # Emits error message
    
    imageStarted = pyqtSignal()
    imageCompleted = pyqtSignal(list)  # Emits list of image URLs
    imageError = pyqtSignal(str)  # Emits error message
    
    def __init__(self, media_service: MediaService):
        """
        Initialize media controller.
        
        Args:
            media_service: MediaService for audio/image operations
        """
        super().__init__()
        self.media_service = media_service
        logger.info("MediaController initialized")
    
    def play_audio(self, word: str, on_complete: Optional[Callable] = None) -> None:
        """
        Play audio for a word.
        
        Args:
            word: Word to play audio for
            on_complete: Optional callback when playback completes
        """
        try:
            self.audioStarted.emit()
            
            result = self.media_service.get_audio(word)
            
            if result.get('error'):
                self.audioError.emit(result['error'])
                return
            
            audio_file = result.get('file_path')
            if audio_file:
                self.media_service.play_audio(audio_file)
                self.audioCompleted.emit(audio_file)
                
                if on_complete:
                    on_complete(audio_file)
                
                logger.info(f"Playing audio for '{word}'")
            else:
                self.audioError.emit("No audio file found")
                
        except Exception as e:
            error_msg = f"Audio error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.audioError.emit(error_msg)
    
    def get_images(self, word: str, on_complete: Optional[Callable] = None) -> None:
        """
        Get images for a word.
        
        Args:
            word: Word to get images for
            on_complete: Optional callback with image URLs
        """
        try:
            self.imageStarted.emit()
            
            result = self.media_service.get_images(word)
            
            if result.get('error'):
                self.imageError.emit(result['error'])
                return
            
            images = result.get('urls', [])
            if images:
                self.imageCompleted.emit(images)
                
                if on_complete:
                    on_complete(images)
                
                logger.info(f"Retrieved {len(images)} images for '{word}'")
            else:
                self.imageError.emit("No images found")
                
        except Exception as e:
            error_msg = f"Image error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.imageError.emit(error_msg)
