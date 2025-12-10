# -*- coding: utf-8 -*-
"""
Media service for handling audio, image, and other media operations.
"""

from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import logging
import shutil
import tempfile
import time
import json

from ..config.manager import ConfigManager


logger = logging.getLogger('anki_dictionary.media_service')


class MediaService:
    """Service for handling media operations."""
    
    def __init__(
        self,
        mw: Any,
        config_manager: ConfigManager,
        addon_path: Path
    ):
        """
        Initialize media service.
        
        Args:
            mw: Anki main window instance
            config_manager: Configuration manager instance
            addon_path: Path to addon directory
        """
        self.mw = mw
        self.config_manager = config_manager
        self.addon_path = addon_path
        self.temp_dir = addon_path / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Track temporary files for cleanup
        self._temp_files: List[Path] = []
    
    def download_forvo_audio(
        self,
        term: str,
        language: str,
        username: Optional[str] = None,
        max_retries: int = 3
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Download audio from Forvo.
        
        Args:
            term: Word to download audio for
            language: Language name (e.g., "Japanese")
            username: Optional specific Forvo username to filter by
            max_retries: Maximum number of retry attempts
            
        Returns:
            Tuple of (success, filename, error_message)
        """
        if not term or not term.strip():
            return False, None, "Term cannot be empty"
        
        try:
            # Import Forvo module
            from forvodl import Forvo
            
            # Create Forvo instance
            forvo = Forvo(language)
            
            # Attempt download with retries
            for attempt in range(max_retries):
                try:
                    results = forvo.search(term, language)
                    
                    if not results or len(results) == 0:
                        return False, None, f"No audio found for '{term}'"
                    
                    # Filter by username if specified
                    if username:
                        results = [r for r in results if r[0] == username]
                        if not results:
                            return False, None, f"No audio found from user '{username}'"
                    
                    # Get the first result
                    result = results[0]
                    audio_url = result[2]  # Primary URL
                    
                    # Download audio file
                    success, filename, error = self._download_audio_file(
                        audio_url,
                        term,
                        language
                    )
                    
                    if success:
                        return True, filename, None
                    
                    # Try alternate URL if available
                    if len(result) > 3:
                        alt_url = result[3]
                        success, filename, error = self._download_audio_file(
                            alt_url,
                            term,
                            language
                        )
                        if success:
                            return True, filename, None
                    
                    # If this was the last retry, return the error
                    if attempt == max_retries - 1:
                        return False, None, error or "Failed to download audio"
                    
                    # Wait before retry
                    time.sleep(0.5 * (attempt + 1))
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Forvo download failed after {max_retries} attempts: {e}")
                        return False, None, f"Download failed: {str(e)}"
                    time.sleep(0.5 * (attempt + 1))
            
            return False, None, "Failed to download audio after retries"
            
        except ImportError:
            return False, None, "Forvo module not available"
        except Exception as e:
            logger.error(f"Forvo download error: {e}")
            return False, None, f"Error: {str(e)}"
    
    def _download_audio_file(
        self,
        url: str,
        term: str,
        language: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Download an audio file from URL.
        
        Args:
            url: Audio file URL
            term: Term being downloaded
            language: Language name
            
        Returns:
            Tuple of (success, filename, error_message)
        """
        try:
            import requests
            
            # Download file
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            if 'mp3' in content_type or url.endswith('.mp3'):
                ext = 'mp3'
            elif 'ogg' in content_type or url.endswith('.ogg'):
                ext = 'ogg'
            else:
                ext = 'mp3'  # Default to mp3
            
            # Create filename
            safe_term = self._sanitize_filename(term)
            filename = f"forvo_{language}_{safe_term}_{int(time.time())}.{ext}"
            
            # Save to temporary file
            temp_file = self.temp_dir / filename
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            self._temp_files.append(temp_file)
            
            # Add to Anki media collection
            final_filename = self.add_media_file(temp_file, filename)
            
            return True, final_filename, None
            
        except requests.Timeout:
            return False, None, "Download timed out"
        except requests.RequestException as e:
            return False, None, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Audio download error: {e}")
            return False, None, f"Download failed: {str(e)}"
    
    def download_google_images(
        self,
        query: str,
        max_results: int = 10
    ) -> Tuple[bool, List[str], Optional[str]]:
        """
        Download images from Google Images.
        
        Args:
            query: Search query
            max_results: Maximum number of images to download
            
        Returns:
            Tuple of (success, list of filenames, error_message)
        """
        if not query or not query.strip():
            return False, [], "Query cannot be empty"
        
        try:
            # Import Google Images module
            from googleimages import Google
            
            # Get image settings
            image_settings = self.config_manager.get_image_settings()
            max_width = image_settings.get('max_width', 400)
            max_height = image_settings.get('max_height', 400)
            region = image_settings.get('google_search_region', 'United States')
            safe_search = image_settings.get('safe_search', True)
            
            # Create Google instance
            google = Google()
            google.setSearchRegion(region)
            google.setSafeSearch(safe_search)
            
            # Search for images
            image_urls = google.search(query, max_results)
            
            if not image_urls or len(image_urls) == 0:
                return False, [], f"No images found for '{query}'"
            
            # Download images
            filenames = []
            for idx, url in enumerate(image_urls[:max_results]):
                try:
                    success, filename, error = self._download_image_file(
                        url,
                        query,
                        idx,
                        max_width,
                        max_height
                    )
                    if success and filename:
                        filenames.append(filename)
                except Exception as e:
                    logger.warning(f"Failed to download image {idx}: {e}")
                    continue
            
            if not filenames:
                return False, [], "Failed to download any images"
            
            return True, filenames, None
            
        except ImportError:
            return False, [], "Google Images module not available"
        except Exception as e:
            logger.error(f"Google Images download error: {e}")
            return False, [], f"Error: {str(e)}"
    
    def _download_image_file(
        self,
        url: str,
        query: str,
        index: int,
        max_width: int,
        max_height: int
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Download an image file from URL.
        
        Args:
            url: Image URL
            query: Search query
            index: Image index
            max_width: Maximum image width
            max_height: Maximum image height
            
        Returns:
            Tuple of (success, filename, error_message)
        """
        try:
            import requests
            from PIL import Image
            from io import BytesIO
            
            # Download image
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Load image
            image = Image.open(BytesIO(response.content))
            
            # Resize if needed
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convert RGBA to RGB if needed
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create filename
            safe_query = self._sanitize_filename(query)
            filename = f"google_{safe_query}_{index}_{int(time.time())}.jpg"
            
            # Save to temporary file
            temp_file = self.temp_dir / filename
            image.save(temp_file, 'JPEG', quality=85)
            
            self._temp_files.append(temp_file)
            
            # Add to Anki media collection
            final_filename = self.add_media_file(temp_file, filename)
            
            return True, final_filename, None
            
        except requests.Timeout:
            return False, None, "Download timed out"
        except requests.RequestException as e:
            return False, None, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Image download error: {e}")
            return False, None, f"Download failed: {str(e)}"
    
    def add_media_file(
        self,
        source_path: Path,
        filename: Optional[str] = None
    ) -> str:
        """
        Add a media file to Anki's collection.
        
        Args:
            source_path: Path to source file
            filename: Optional custom filename
            
        Returns:
            Final filename in media collection
        """
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        if filename is None:
            filename = source_path.name
        
        # Ensure filename is safe
        filename = self._sanitize_filename(filename)
        
        # Add to Anki's media collection
        try:
            # Copy file to media folder
            media_path = Path(self.mw.col.media.dir()) / filename
            shutil.copy2(source_path, media_path)
            
            # Let Anki know about the file
            self.mw.col.media.addFile(str(source_path))
            
            return filename
            
        except Exception as e:
            logger.error(f"Failed to add media file: {e}")
            raise
    
    def cleanup_temp_media(self) -> None:
        """
        Clean up temporary media files.
        
        This method performs comprehensive cleanup of:
        1. Tracked temporary files (from _temp_files list)
        2. All files in the temp directory (including orphaned files)
        3. Subdirectories within the temp directory
        4. The temp directory itself if empty
        
        Handles edge cases:
        - Missing directories (creates if needed for future use)
        - Permission errors (logs and continues)
        - File locks (logs and continues)
        - Nested directories (recursive cleanup)
        """
        errors = []
        files_cleaned = 0
        dirs_cleaned = 0
        
        logger.info("Starting temporary file cleanup")
        
        # Step 1: Clean up tracked temporary files
        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    files_cleaned += 1
                    logger.debug(f"Cleaned up tracked temp file: {temp_file}")
            except PermissionError as e:
                logger.warning(f"Permission denied removing {temp_file}: {e}")
                errors.append(f"Permission denied: {temp_file.name}")
            except OSError as e:
                logger.warning(f"OS error removing {temp_file}: {e}")
                errors.append(f"OS error: {temp_file.name}")
            except Exception as e:
                logger.warning(f"Failed to clean up {temp_file}: {e}")
                errors.append(f"Error: {temp_file.name}")
        
        # Clear the tracked files list
        self._temp_files.clear()
        
        # Step 2: Clean up all files in temp directory (including orphaned files)
        try:
            # Ensure temp directory exists
            if not self.temp_dir.exists():
                logger.info(f"Temp directory does not exist, creating: {self.temp_dir}")
                self.temp_dir.mkdir(parents=True, exist_ok=True)
            else:
                # Get all items in temp directory
                try:
                    items = list(self.temp_dir.iterdir())
                    logger.debug(f"Found {len(items)} items in temp directory")
                    
                    for item in items:
                        try:
                            if item.is_file():
                                # Remove file
                                item.unlink()
                                files_cleaned += 1
                                logger.debug(f"Removed temp file: {item.name}")
                            elif item.is_dir():
                                # Remove directory and its contents
                                self._cleanup_directory(item)
                                dirs_cleaned += 1
                                logger.debug(f"Removed temp directory: {item.name}")
                        except PermissionError as e:
                            logger.warning(f"Permission denied removing {item}: {e}")
                            errors.append(f"Permission denied: {item.name}")
                        except OSError as e:
                            logger.warning(f"OS error removing {item}: {e}")
                            errors.append(f"OS error: {item.name}")
                        except Exception as e:
                            logger.warning(f"Failed to remove {item}: {e}")
                            errors.append(f"Error: {item.name}")
                
                except PermissionError as e:
                    logger.error(f"Permission denied accessing temp directory: {e}")
                    errors.append("Cannot access temp directory")
                except OSError as e:
                    logger.error(f"OS error accessing temp directory: {e}")
                    errors.append("Cannot access temp directory")
                
                # Step 3: Try to remove temp directory if empty
                try:
                    if self.temp_dir.exists() and not any(self.temp_dir.iterdir()):
                        self.temp_dir.rmdir()
                        logger.info(f"Removed empty temp directory: {self.temp_dir}")
                    elif self.temp_dir.exists():
                        remaining = len(list(self.temp_dir.iterdir()))
                        logger.debug(f"Temp directory not empty, {remaining} items remaining")
                except PermissionError as e:
                    logger.debug(f"Permission denied removing temp directory: {e}")
                except OSError as e:
                    logger.debug(f"Could not remove temp directory: {e}")
                except Exception as e:
                    logger.debug(f"Error checking/removing temp directory: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error during temp directory cleanup: {e}")
            errors.append(f"Unexpected error: {str(e)}")
        
        # Log summary
        if errors:
            logger.warning(
                f"Cleanup completed with {len(errors)} errors. "
                f"Cleaned: {files_cleaned} files, {dirs_cleaned} directories"
            )
        else:
            logger.info(
                f"Cleanup completed successfully. "
                f"Cleaned: {files_cleaned} files, {dirs_cleaned} directories"
            )
    
    def _cleanup_directory(self, directory: Path) -> None:
        """
        Recursively clean up a directory and its contents.
        
        Args:
            directory: Path to directory to clean up
            
        Raises:
            Exception: If cleanup fails
        """
        try:
            # First, remove all files in the directory
            for item in directory.iterdir():
                if item.is_file():
                    item.unlink()
                    logger.debug(f"Removed file in subdirectory: {item}")
                elif item.is_dir():
                    # Recursively clean subdirectories
                    self._cleanup_directory(item)
            
            # Then remove the directory itself
            directory.rmdir()
            logger.debug(f"Removed directory: {directory}")
            
        except Exception as e:
            logger.warning(f"Error cleaning directory {directory}: {e}")
            raise
    
    def get_media_path(self, filename: str) -> Path:
        """
        Get full path to a media file.
        
        Args:
            filename: Media filename
            
        Returns:
            Full path to media file
        """
        return Path(self.mw.col.media.dir()) / filename
    
    def validate_media_file(
        self,
        filepath: Path,
        allowed_extensions: Optional[List[str]] = None
    ) -> bool:
        """
        Validate media file format.
        
        Args:
            filepath: Path to file to validate
            allowed_extensions: List of allowed extensions (e.g., ['.mp3', '.jpg'])
            
        Returns:
            True if valid, False otherwise
        """
        if not filepath.exists():
            logger.warning(f"File does not exist: {filepath}")
            return False
        
        if not filepath.is_file():
            logger.warning(f"Path is not a file: {filepath}")
            return False
        
        if allowed_extensions:
            ext = filepath.suffix.lower()
            if ext not in [e.lower() for e in allowed_extensions]:
                logger.warning(f"Invalid extension {ext}, allowed: {allowed_extensions}")
                return False
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024
        if filepath.stat().st_size > max_size:
            logger.warning(f"File too large: {filepath.stat().st_size} bytes")
            return False
        
        return True
    
    def batch_download_audio(
        self,
        terms: List[str],
        language: str,
        username: Optional[str] = None
    ) -> Dict[str, Tuple[bool, Optional[str], Optional[str]]]:
        """
        Download audio for multiple terms.
        
        Args:
            terms: List of terms to download audio for
            language: Language name
            username: Optional Forvo username filter
            
        Returns:
            Dictionary mapping terms to (success, filename, error_message) tuples
        """
        results = {}
        for term in terms:
            results[term] = self.download_forvo_audio(term, language, username)
        return results
    
    def batch_download_images(
        self,
        queries: List[str],
        max_results_per_query: int = 5
    ) -> Dict[str, Tuple[bool, List[str], Optional[str]]]:
        """
        Download images for multiple queries.
        
        Args:
            queries: List of search queries
            max_results_per_query: Maximum images per query
            
        Returns:
            Dictionary mapping queries to (success, filenames, error_message) tuples
        """
        results = {}
        for query in queries:
            results[query] = self.download_google_images(query, max_results_per_query)
        return results
    
    def remove_temp_file(self, filepath: Path) -> bool:
        """
        Remove a specific temporary file.
        
        Args:
            filepath: Path to file to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if filepath in self._temp_files:
                self._temp_files.remove(filepath)
            
            if filepath.exists():
                filepath.unlink()
                logger.debug(f"Removed temp file: {filepath}")
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to remove temp file {filepath}: {e}")
            return False
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to be safe for file systems.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        import re
        
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', '_', filename)
        filename = re.sub(r'_+', '_', filename)
        filename = filename.strip('_')
        
        # Limit length
        if len(filename) > 200:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            max_name_len = 200 - len(ext) - 1
            filename = name[:max_name_len] + ('.' + ext if ext else '')
        
        return filename or 'unnamed_file'
    
    def get_temp_files_count(self) -> int:
        """
        Get count of tracked temporary files.
        
        Returns:
            Number of temporary files
        """
        return len(self._temp_files)
    
    def get_temp_files_size(self) -> int:
        """
        Get total size of tracked temporary files.
        
        Returns:
            Total size in bytes
        """
        total_size = 0
        for temp_file in self._temp_files:
            try:
                if temp_file.exists():
                    total_size += temp_file.stat().st_size
            except Exception:
                pass
        return total_size
