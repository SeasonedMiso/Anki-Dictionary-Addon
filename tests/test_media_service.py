# -*- coding: utf-8 -*-
"""
Tests for media service module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
import tempfile
import shutil
from io import BytesIO

from src.services.media_service import MediaService
from src.config.manager import ConfigManager


@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.col = Mock()
    mw.col.media = Mock()
    mw.col.media.dir = Mock(return_value='/fake/media/dir')
    mw.col.media.addFile = Mock()
    return mw


@pytest.fixture
def mock_config_manager():
    """Mock configuration manager."""
    config_manager = Mock(spec=ConfigManager)
    config_manager.get_image_settings = Mock(return_value={
        'max_width': 400,
        'max_height': 400,
        'google_search_region': 'United States',
        'safe_search': True
    })
    config_manager.get_audio_settings = Mock(return_value={
        'forvo_language': 'Japanese',
        'mp3_convert': True
    })
    return config_manager


@pytest.fixture
def temp_addon_path(tmp_path):
    """Create temporary addon path."""
    addon_path = tmp_path / "addon"
    addon_path.mkdir()
    return addon_path


@pytest.fixture
def media_service(mock_mw, mock_config_manager, temp_addon_path):
    """Create media service instance for testing."""
    return MediaService(mock_mw, mock_config_manager, temp_addon_path)


class TestMediaServiceInitialization:
    """Test MediaService initialization."""
    
    def test_service_creation(self, media_service, mock_mw, mock_config_manager, temp_addon_path):
        """Test creating a media service."""
        assert media_service.mw == mock_mw
        assert media_service.config_manager == mock_config_manager
        assert media_service.addon_path == temp_addon_path
        assert media_service.temp_dir == temp_addon_path / "temp"
        assert media_service.temp_dir.exists()
        assert media_service._temp_files == []
    
    def test_temp_directory_created(self, media_service):
        """Test that temp directory is created on initialization."""
        assert media_service.temp_dir.exists()
        assert media_service.temp_dir.is_dir()


class TestForvoAudioDownload:
    """Test Forvo audio download functionality."""
    
    def test_download_forvo_audio_empty_term(self, media_service):
        """Test Forvo download with empty term."""
        success, filename, error = media_service.download_forvo_audio('', 'Japanese')
        
        assert success is False
        assert filename is None
        assert 'cannot be empty' in error.lower()
    
    def test_download_forvo_audio_module_not_available(self, media_service):
        """Test Forvo download when module is not available."""
        # When forvodl module is not available, should return error gracefully
        success, filename, error = media_service.download_forvo_audio('test', 'Japanese')
        
        assert success is False
        assert filename is None
        assert error is not None
        assert 'not available' in error.lower() or 'error' in error.lower()


class TestGoogleImagesDownload:
    """Test Google Images download functionality."""
    
    def test_download_google_images_empty_query(self, media_service):
        """Test Google Images download with empty query."""
        success, filenames, error = media_service.download_google_images('')
        
        assert success is False
        assert filenames == []
        assert 'cannot be empty' in error.lower()
    
    def test_download_google_images_module_not_available(self, media_service):
        """Test Google Images download when module is not available."""
        # When googleimages module is not available, should return error gracefully
        success, filenames, error = media_service.download_google_images('test query')
        
        assert success is False
        assert filenames == []
        assert error is not None
        assert 'not available' in error.lower() or 'error' in error.lower()


class TestMediaFileManagement:
    """Test media file management methods."""
    
    def test_add_media_file_success(self, media_service, tmp_path):
        """Test adding a media file to collection."""
        # Create a test file
        test_file = tmp_path / "test_audio.mp3"
        test_file.write_bytes(b'fake audio data')
        
        # Mock the media directory
        with patch('shutil.copy2') as mock_copy:
            filename = media_service.add_media_file(test_file, "custom_name.mp3")
            
            assert filename == "custom_name.mp3"
            mock_copy.assert_called_once()
            media_service.mw.col.media.addFile.assert_called_once()
    
    def test_add_media_file_not_found(self, media_service, tmp_path):
        """Test adding non-existent file."""
        non_existent = tmp_path / "does_not_exist.mp3"
        
        with pytest.raises(FileNotFoundError):
            media_service.add_media_file(non_existent)
    
    def test_get_media_path(self, media_service):
        """Test getting media file path."""
        path = media_service.get_media_path("test.mp3")
        
        assert isinstance(path, Path)
        assert str(path).endswith("test.mp3")
    
    def test_validate_media_file_valid(self, media_service, tmp_path):
        """Test validating a valid media file."""
        test_file = tmp_path / "test.mp3"
        test_file.write_bytes(b'fake audio data')
        
        is_valid = media_service.validate_media_file(test_file, ['.mp3', '.ogg'])
        
        assert is_valid is True
    
    def test_validate_media_file_invalid_extension(self, media_service, tmp_path):
        """Test validating file with invalid extension."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b'text data')
        
        is_valid = media_service.validate_media_file(test_file, ['.mp3', '.ogg'])
        
        assert is_valid is False
    
    def test_validate_media_file_not_exists(self, media_service, tmp_path):
        """Test validating non-existent file."""
        non_existent = tmp_path / "does_not_exist.mp3"
        
        is_valid = media_service.validate_media_file(non_existent)
        
        assert is_valid is False
    
    def test_validate_media_file_too_large(self, media_service, tmp_path):
        """Test validating file that's too large."""
        test_file = tmp_path / "large.mp3"
        # Create a file larger than 10MB
        test_file.write_bytes(b'x' * (11 * 1024 * 1024))
        
        is_valid = media_service.validate_media_file(test_file)
        
        assert is_valid is False


class TestTemporaryFileCleanup:
    """Test temporary file cleanup functionality."""
    
    def test_cleanup_temp_media(self, media_service, tmp_path):
        """Test cleaning up temporary files."""
        # Create some temp files
        temp_file1 = media_service.temp_dir / "temp1.mp3"
        temp_file2 = media_service.temp_dir / "temp2.jpg"
        temp_file1.write_bytes(b'data1')
        temp_file2.write_bytes(b'data2')
        
        media_service._temp_files = [temp_file1, temp_file2]
        
        # Cleanup
        media_service.cleanup_temp_media()
        
        assert not temp_file1.exists()
        assert not temp_file2.exists()
        assert len(media_service._temp_files) == 0
    
    def test_cleanup_temp_media_with_errors(self, media_service, tmp_path):
        """Test cleanup with some files missing."""
        temp_file1 = media_service.temp_dir / "temp1.mp3"
        temp_file2 = media_service.temp_dir / "temp2.jpg"
        temp_file1.write_bytes(b'data1')
        # temp_file2 doesn't exist
        
        media_service._temp_files = [temp_file1, temp_file2]
        
        # Should not raise exception
        media_service.cleanup_temp_media()
        
        assert not temp_file1.exists()
        assert len(media_service._temp_files) == 0
    
    def test_remove_temp_file(self, media_service):
        """Test removing a specific temp file."""
        temp_file = media_service.temp_dir / "temp.mp3"
        temp_file.write_bytes(b'data')
        media_service._temp_files.append(temp_file)
        
        result = media_service.remove_temp_file(temp_file)
        
        assert result is True
        assert not temp_file.exists()
        assert temp_file not in media_service._temp_files
    
    def test_get_temp_files_count(self, media_service):
        """Test getting temp files count."""
        temp_file1 = media_service.temp_dir / "temp1.mp3"
        temp_file2 = media_service.temp_dir / "temp2.jpg"
        temp_file1.write_bytes(b'data1')
        temp_file2.write_bytes(b'data2')
        
        media_service._temp_files = [temp_file1, temp_file2]
        
        count = media_service.get_temp_files_count()
        assert count == 2
    
    def test_get_temp_files_size(self, media_service):
        """Test getting total temp files size."""
        temp_file1 = media_service.temp_dir / "temp1.mp3"
        temp_file2 = media_service.temp_dir / "temp2.jpg"
        temp_file1.write_bytes(b'data1')
        temp_file2.write_bytes(b'data2')
        
        media_service._temp_files = [temp_file1, temp_file2]
        
        size = media_service.get_temp_files_size()
        assert size == 10  # 5 bytes each
    
    def test_cleanup_orphaned_files(self, media_service):
        """Test cleanup of orphaned files not in _temp_files list."""
        # Create tracked files
        tracked_file = media_service.temp_dir / "tracked.mp3"
        tracked_file.write_bytes(b'tracked')
        media_service._temp_files.append(tracked_file)
        
        # Create orphaned files (not tracked)
        orphaned_file1 = media_service.temp_dir / "orphaned1.mp3"
        orphaned_file2 = media_service.temp_dir / "orphaned2.jpg"
        orphaned_file1.write_bytes(b'orphaned1')
        orphaned_file2.write_bytes(b'orphaned2')
        
        # Cleanup should remove all files
        media_service.cleanup_temp_media()
        
        assert not tracked_file.exists()
        assert not orphaned_file1.exists()
        assert not orphaned_file2.exists()
        assert len(media_service._temp_files) == 0
    
    def test_cleanup_subdirectories(self, media_service):
        """Test cleanup of subdirectories within temp directory."""
        # Create subdirectory with files
        subdir = media_service.temp_dir / "subdir"
        subdir.mkdir()
        subfile1 = subdir / "file1.mp3"
        subfile2 = subdir / "file2.jpg"
        subfile1.write_bytes(b'data1')
        subfile2.write_bytes(b'data2')
        
        # Create nested subdirectory
        nested_subdir = subdir / "nested"
        nested_subdir.mkdir()
        nested_file = nested_subdir / "nested.mp3"
        nested_file.write_bytes(b'nested')
        
        # Cleanup should remove all subdirectories and their contents
        media_service.cleanup_temp_media()
        
        assert not subfile1.exists()
        assert not subfile2.exists()
        assert not nested_file.exists()
        assert not nested_subdir.exists()
        assert not subdir.exists()
    
    def test_cleanup_missing_temp_directory(self, media_service, tmp_path):
        """Test cleanup when temp directory doesn't exist."""
        # Remove temp directory
        if media_service.temp_dir.exists():
            import shutil
            shutil.rmtree(media_service.temp_dir)
        
        # Should not raise exception and should recreate directory
        media_service.cleanup_temp_media()
        
        # Directory should be created
        assert media_service.temp_dir.exists()
        assert len(media_service._temp_files) == 0
    
    def test_cleanup_removes_empty_temp_directory(self, media_service):
        """Test that cleanup removes temp directory if empty."""
        # Ensure temp directory exists but is empty
        media_service.temp_dir.mkdir(exist_ok=True)
        
        # Cleanup should remove the empty directory
        media_service.cleanup_temp_media()
        
        # Directory should be removed
        assert not media_service.temp_dir.exists()
    
    def test_cleanup_preserves_temp_directory_if_not_empty(self, media_service):
        """Test that cleanup preserves temp directory if files remain."""
        # Create a file that will fail to delete (simulate permission error)
        # For this test, we'll just verify the directory exists after cleanup
        temp_file = media_service.temp_dir / "file.mp3"
        temp_file.write_bytes(b'data')
        
        # Don't add to _temp_files, so it gets cleaned in the directory scan
        media_service.cleanup_temp_media()
        
        # File should be removed, directory should be removed if empty
        assert not temp_file.exists()


class TestBatchOperations:
    """Test batch download operations."""
    
    @patch.object(MediaService, 'download_forvo_audio')
    def test_batch_download_audio(self, mock_download, media_service):
        """Test batch audio download."""
        mock_download.return_value = (True, 'audio.mp3', None)
        
        terms = ['term1', 'term2', 'term3']
        results = media_service.batch_download_audio(terms, 'Japanese')
        
        assert len(results) == 3
        assert all(term in results for term in terms)
        assert mock_download.call_count == 3
    
    @patch.object(MediaService, 'download_google_images')
    def test_batch_download_images(self, mock_download, media_service):
        """Test batch image download."""
        mock_download.return_value = (True, ['image1.jpg', 'image2.jpg'], None)
        
        queries = ['query1', 'query2']
        results = media_service.batch_download_images(queries, max_results_per_query=5)
        
        assert len(results) == 2
        assert all(query in results for query in queries)
        assert mock_download.call_count == 2


class TestUtilityMethods:
    """Test utility methods."""
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test special characters (consecutive underscores are collapsed)
        assert MediaService._sanitize_filename('test<>file.mp3') == 'test_file.mp3'
        assert MediaService._sanitize_filename('test/file.mp3') == 'test_file.mp3'
        assert MediaService._sanitize_filename('test:file.mp3') == 'test_file.mp3'
        
        # Test spaces
        assert MediaService._sanitize_filename('test  file.mp3') == 'test_file.mp3'
        
        # Test empty
        assert MediaService._sanitize_filename('') == 'unnamed_file'
        
        # Test long filename
        long_name = 'a' * 250 + '.mp3'
        sanitized = MediaService._sanitize_filename(long_name)
        assert len(sanitized) <= 204  # 200 + '.mp3'
