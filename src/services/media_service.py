# -*- coding: utf-8 -*-
"""
Media service - Clean business logic for media operations.

This module provides media download and handling functionality without UI dependencies,
returning structured data that can be used by any UI component.
"""

from typing import Dict, Any, Optional, List, Tuple, Callable
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MediaService:
    """
    Service for handling media operations.
    
    Provides clean media interface without UI dependencies.
    Returns structured data for consumption by UI components.
    """
    
    def __init__(self, legacy_media_service: Any, config_manager: Any):
        """
        Initialize media service.
        
        Args:
            legacy_media_service: Legacy MediaService instance for actual operations
            config_manager: Configuration manager for media settings
        """
        self.legacy_service = legacy_media_service
        self.config_manager = config_manager
    
    def download_audio(
        self,
        word: str,
        language: Optional[str] = None,
        username: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Download audio for a word.
        
        Args:
            word: Word to download audio for
            language: Language name (uses config if None)
            username: Optional Forvo username filter (uses config if None)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with download result:
            {
                'success': bool,
                'filename': str or None,
                'file_path': str or None,
                'error': str or None,
                'word': str,
                'language': str,
                'source': str  # 'forvo', 'local', etc.
            }
        """
        if not word or not word.strip():
            return {
                'success': False,
                'filename': None,
                'file_path': None,
                'error': 'Word cannot be empty',
                'word': word,
                'language': language or 'unknown',
                'source': 'none'
            }
        
        word = word.strip()
        
        # Use config values if not provided
        if language is None:
            language = self.config_manager.get_value('forvoLanguage', 'Japanese')
        if username is None:
            username = self.config_manager.get_value('forvoUsername', None)
        
        if progress_callback:
            progress_callback(f"Downloading audio for '{word}'...")
        
        try:
            # Use legacy service for actual download
            success, filename, error = self.legacy_service.download_forvo_audio(
                term=word,
                language=language,
                username=username
            )
            
            result = {
                'success': success,
                'filename': filename,
                'file_path': None,  # Legacy service handles Anki media directly
                'error': error,
                'word': word,
                'language': language,
                'source': 'forvo'
            }
            
            if success:
                logger.info(f"Audio downloaded successfully: {filename}")
                if progress_callback:
                    progress_callback(f"Audio ready for '{word}'")
            else:
                logger.warning(f"Audio download failed for '{word}': {error}")
                if progress_callback:
                    progress_callback(f"Audio failed: {error}")
            
            return result
            
        except Exception as e:
            error_msg = f"Audio download error: {str(e)}"
            logger.error(f"Error downloading audio for '{word}': {e}", exc_info=True)
            
            if progress_callback:
                progress_callback(f"Audio error: {str(e)}")
            
            return {
                'success': False,
                'filename': None,
                'file_path': None,
                'error': error_msg,
                'word': word,
                'language': language,
                'source': 'forvo'
            }
    
    def download_images(
        self,
        query: str,
        max_results: Optional[int] = None,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Download images for a search query.
        
        Args:
            query: Search query for images
            max_results: Maximum number of images (uses config if None)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with download result:
            {
                'success': bool,
                'filenames': List[str],
                'file_paths': List[str],
                'count': int,
                'error': str or None,
                'query': str,
                'source': str  # 'google_images', 'local', etc.
            }
        """
        if not query or not query.strip():
            return {
                'success': False,
                'filenames': [],
                'file_paths': [],
                'count': 0,
                'error': 'Query cannot be empty',
                'query': query,
                'source': 'none'
            }
        
        query = query.strip()
        
        # Use config value if not provided
        if max_results is None:
            max_results = self.config_manager.get_int('googleImagesMax', 5)
        
        if progress_callback:
            progress_callback(f"Searching images for '{query}'...")
        
        try:
            # Use legacy service for actual download
            success, filenames, error = self.legacy_service.download_google_images(
                query=query,
                max_results=max_results
            )
            
            result = {
                'success': success,
                'filenames': filenames or [],
                'file_paths': [],  # Legacy service handles Anki media directly
                'count': len(filenames) if filenames else 0,
                'error': error,
                'query': query,
                'source': 'google_images'
            }
            
            if success and filenames:
                count = len(filenames)
                logger.info(f"Downloaded {count} images for '{query}': {filenames}")
                if progress_callback:
                    progress_callback(f"Downloaded {count} image{'s' if count != 1 else ''}")
            else:
                logger.warning(f"Image download failed for '{query}': {error}")
                if progress_callback:
                    progress_callback(f"Image search failed: {error}")
            
            return result
            
        except Exception as e:
            error_msg = f"Image download error: {str(e)}"
            logger.error(f"Error downloading images for '{query}': {e}", exc_info=True)
            
            if progress_callback:
                progress_callback(f"Image error: {str(e)}")
            
            return {
                'success': False,
                'filenames': [],
                'file_paths': [],
                'count': 0,
                'error': error_msg,
                'query': query,
                'source': 'google_images'
            }
    
    def play_audio(
        self,
        filename: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Play an audio file.
        
        Args:
            filename: Audio filename in Anki media collection
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary with playback result:
            {
                'success': bool,
                'filename': str,
                'error': str or None
            }
        """
        if not filename:
            return {
                'success': False,
                'filename': filename,
                'error': 'Filename cannot be empty'
            }
        
        try:
            # Use legacy service's play functionality
            if hasattr(self.legacy_service, '_play_audio_file'):
                self.legacy_service._play_audio_file(filename)
                
                if progress_callback:
                    progress_callback(f"Playing audio: {filename}")
                
                return {
                    'success': True,
                    'filename': filename,
                    'error': None
                }
            else:
                # Fallback: use Anki's built-in audio player
                from aqt.sound import av_player
                av_player.play_file(filename)
                
                if progress_callback:
                    progress_callback(f"Playing audio: {filename}")
                
                return {
                    'success': True,
                    'filename': filename,
                    'error': None
                }
                
        except Exception as e:
            error_msg = f"Audio playback error: {str(e)}"
            logger.error(f"Error playing audio '{filename}': {e}", exc_info=True)
            
            if progress_callback:
                progress_callback(f"Playback failed: {str(e)}")
            
            return {
                'success': False,
                'filename': filename,
                'error': error_msg
            }
    
    def add_media_file(
        self,
        source_path: str,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a media file to Anki's collection.
        
        Args:
            source_path: Path to source file
            filename: Optional custom filename
            
        Returns:
            Dictionary with result:
            {
                'success': bool,
                'filename': str or None,
                'error': str or None
            }
        """
        try:
            final_filename = self.legacy_service.add_media_file(
                Path(source_path),
                filename
            )
            
            return {
                'success': True,
                'filename': final_filename,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Failed to add media file: {str(e)}"
            logger.error(f"Error adding media file '{source_path}': {e}", exc_info=True)
            
            return {
                'success': False,
                'filename': None,
                'error': error_msg
            }
    
    def cleanup_temp_files(self) -> Dict[str, Any]:
        """
        Clean up temporary media files.
        
        Returns:
            Dictionary with cleanup result:
            {
                'success': bool,
                'files_cleaned': int,
                'error': str or None
            }
        """
        try:
            # Use legacy service for cleanup
            self.legacy_service.cleanup_temp_media()
            
            return {
                'success': True,
                'files_cleaned': 0,  # Legacy service doesn't return count
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Cleanup error: {str(e)}"
            logger.error(f"Error during temp file cleanup: {e}", exc_info=True)
            
            return {
                'success': False,
                'files_cleaned': 0,
                'error': error_msg
            }