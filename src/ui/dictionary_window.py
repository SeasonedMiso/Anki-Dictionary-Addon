# -*- coding: utf-8 -*-
"""
Dictionary Window - Main UI with service integration.

This is the production dictionary window that wires UI components
to backend services through controllers.
"""

from typing import Optional
import logging

try:
    from aqt.qt import QWidget, QVBoxLayout, QLabel, Qt, QSizePolicy, QPushButton
except ImportError:
    QWidget = object
    QVBoxLayout = object
    QLabel = object
    Qt = object
    QSizePolicy = object
    QPushButton = object

from .dictionary_widgets import (
    ModernSearchBar,
    DictionaryFilterBar,
    ModernResultsArea
)
from .search_integration import SearchController
from .service_controllers import (
    ExportController,
    ConfigController,
    HistoryController,
    MediaController
)
from .styling import get_theme_manager, StyleGenerator

logger = logging.getLogger(__name__)


class DictionaryWindow(QWidget):
    """
    Main dictionary window with full service integration.
    
    Wires UI components to backend services through controllers:
    - SearchController for word lookups
    - ExportController for card export
    - ConfigController for settings
    - HistoryController for search history
    - MediaController for audio/images
    """
    
    def __init__(
        self,
        dictionary_service,
        export_coordinator,
        config_service,
        history_service,
        media_service,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize dictionary window with services.
        
        Args:
            dictionary_service: DictionaryService instance
            export_coordinator: ExportCoordinator instance
            config_service: ConfigService instance
            history_service: HistoryService instance
            media_service: MediaService instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store services
        self.dictionary_service = dictionary_service
        self.export_coordinator = export_coordinator
        self.config_service = config_service
        self.history_service = history_service
        self.media_service = media_service
        
        # Initialize theme
        self.theme_manager = get_theme_manager()
        self.style_generator = StyleGenerator(self.theme_manager.current_theme)
        self.theme_manager.register_observer(self._on_theme_changed)
        
        # Set up UI
        self.setWindowTitle("Dictionary")
        self.setMinimumSize(600, 400)
        self._setup_ui()
        self._setup_controllers()
        self._apply_theme_styling()
        
        logger.info("DictionaryWindow initialized with services")
    
    def _setup_ui(self):
        """Set up the UI layout."""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)
        
        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(14)
        outer.addWidget(container)
        
        # Search bar
        self.search_bar = ModernSearchBar()
        container_layout.addWidget(self.search_bar)
        
        # Filter bar
        self.filter_bar = DictionaryFilterBar()
        container_layout.addWidget(self.filter_bar)
        
        # Results area
        self.results_area = ModernResultsArea()
        self.results_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        container_layout.addWidget(self.results_area, 1)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                padding: 10px;
            }
        """)
        container_layout.addWidget(self.status_label)
        
        # Floating action buttons
        self.options_btn = QPushButton("⚙")
        self.options_btn.setFixedSize(40, 40)
        self.options_btn.clicked.connect(self._on_options_clicked)
        
        self.export_btn = QPushButton("📤")
        self.export_btn.setFixedSize(40, 40)
        self.export_btn.clicked.connect(self._on_export_clicked)
        
        self.options_btn.setParent(self)
        self.export_btn.setParent(self)
        self.options_btn.raise_()
        self.export_btn.raise_()
    
    def _setup_controllers(self):
        """Set up service controllers and wire signals."""
        # Search controller
        self.search_controller = SearchController(
            self.search_bar,
            self.results_area,
            self.dictionary_service
        )
        self.search_controller.searchStarted.connect(self._on_search_started)
        self.search_controller.searchCompleted.connect(self._on_search_completed)
        self.search_controller.searchError.connect(self._on_search_error)
        
        # Export controller
        self.export_controller = ExportController(
            self.export_coordinator,
            self.config_service
        )
        self.export_controller.exportStarted.connect(self._on_export_started)
        self.export_controller.exportCompleted.connect(self._on_export_completed)
        self.export_controller.exportError.connect(self._on_export_error)
        
        # Config controller
        self.config_controller = ConfigController(self.config_service)
        self.config_controller.settingsSaved.connect(self._on_settings_saved)
        self.config_controller.settingsError.connect(self._on_settings_error)
        
        # History controller
        self.history_controller = HistoryController(self.history_service)
        self.history_controller.historyUpdated.connect(self._on_history_updated)
        self.history_controller.historyError.connect(self._on_history_error)
        
        # Media controller
        self.media_controller = MediaController(self.media_service)
        self.media_controller.audioCompleted.connect(self._on_audio_completed)
        self.media_controller.audioError.connect(self._on_audio_error)
        self.media_controller.imageCompleted.connect(self._on_images_completed)
        self.media_controller.imageError.connect(self._on_image_error)
        
        logger.info("Controllers initialized and wired")
    
    def showEvent(self, event):
        """Position buttons when window is shown."""
        super().showEvent(event)
        self._position_floating_buttons()
    
    def resizeEvent(self, event):
        """Handle window resize to keep buttons in corner."""
        super().resizeEvent(event)
        self._position_floating_buttons()
    
    def _position_floating_buttons(self):
        """Position floating action buttons in bottom right corner."""
        if hasattr(self, 'options_btn') and hasattr(self, 'export_btn'):
            button_spacing = 50
            margin = 20
            
            self.options_btn.move(
                self.width() - self.options_btn.width() - margin,
                self.height() - self.options_btn.height() - margin
            )
            
            self.export_btn.move(
                self.width() - self.export_btn.width() - margin,
                self.height() - self.export_btn.height() - margin - button_spacing
            )
    
    def _on_search_started(self):
        """Handle search started."""
        self.status_label.setText("Searching...")
    
    def _on_search_completed(self, result):
        """Handle search completed."""
        count = result.get('total_count', 0)
        time_ms = result.get('search_time_ms', 0)
        self.status_label.setText(f"Found {count} results in {time_ms:.0f}ms")
        
        # Add to history
        word = result.get('word', '')
        if word:
            self.history_controller.add_to_history(word)
    
    def _on_search_error(self, error_msg):
        """Handle search error."""
        self.status_label.setText(f"Error: {error_msg}")
        logger.error(f"Search error: {error_msg}")
    
    def _on_export_started(self):
        """Handle export started."""
        self.status_label.setText("Exporting...")
    
    def _on_export_completed(self, result):
        """Handle export completed."""
        self.status_label.setText("Export successful!")
        logger.info("Export completed")
    
    def _on_export_error(self, error_msg):
        """Handle export error."""
        self.status_label.setText(f"Export error: {error_msg}")
        logger.error(f"Export error: {error_msg}")
    
    def _on_settings_saved(self):
        """Handle settings saved."""
        self.status_label.setText("Settings saved")
        logger.info("Settings saved")
    
    def _on_settings_error(self, error_msg):
        """Handle settings error."""
        self.status_label.setText(f"Settings error: {error_msg}")
        logger.error(f"Settings error: {error_msg}")
    
    def _on_history_updated(self, history):
        """Handle history updated."""
        logger.debug(f"History updated: {len(history)} entries")
    
    def _on_history_error(self, error_msg):
        """Handle history error."""
        logger.error(f"History error: {error_msg}")
    
    def _on_audio_completed(self, file_path):
        """Handle audio playback completed."""
        self.status_label.setText(f"Playing audio: {file_path}")
        logger.info(f"Audio played: {file_path}")
    
    def _on_audio_error(self, error_msg):
        """Handle audio error."""
        self.status_label.setText(f"Audio error: {error_msg}")
        logger.error(f"Audio error: {error_msg}")
    
    def _on_images_completed(self, images):
        """Handle images retrieved."""
        self.status_label.setText(f"Retrieved {len(images)} images")
        logger.info(f"Images retrieved: {len(images)}")
    
    def _on_image_error(self, error_msg):
        """Handle image error."""
        self.status_label.setText(f"Image error: {error_msg}")
        logger.error(f"Image error: {error_msg}")
    
    def _on_theme_changed(self, new_theme):
        """Handle theme changes."""
        self.style_generator = StyleGenerator(new_theme)
        self._apply_theme_styling()
        
        # Update components
        for component in [self.search_bar, self.filter_bar, self.results_area]:
            if hasattr(component, 'update_theme'):
                component.update_theme(new_theme)
        
        logger.info("Theme updated")
    
    def _apply_theme_styling(self):
        """Apply current theme styling."""
        theme = self.theme_manager.current_theme
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.background_color};
                color: {theme.text_primary};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }}
            QLabel {{
                color: {theme.text_primary};
                background-color: transparent;
            }}
            QPushButton {{
                background-color: {theme.panel_color};
                color: {theme.text_primary};
                border: 1px solid {theme.border_color};
                border-radius: 20px;
                padding: 0px;
                font-size: 16px;
                font-weight: bold;
                width: 40px;
                height: 40px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {theme.accent_color};
            }}
        """)
    
    def _on_options_clicked(self):
        """Handle options button click."""
        self.status_label.setText("Settings clicked (not yet implemented)")
        logger.info("Options clicked")
    
    def _on_export_clicked(self):
        """Handle export button click."""
        self.status_label.setText("Export clicked (not yet implemented)")
        logger.info("Export clicked")
