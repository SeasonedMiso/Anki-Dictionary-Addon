# -*- coding: utf-8 -*-
"""
Configuration Service - Settings persistence and management.

This module provides configuration management with JSON-based storage,
import/export functionality, and settings validation.
"""

from typing import Dict, Any, Optional, List
import logging
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ConfigService:
    """
    Service for managing application configuration.
    
    Provides settings persistence, import/export, and validation.
    """
    
    def __init__(self, config_manager: Any, user_files_dir: Optional[str] = None):
        """
        Initialize configuration service.
        
        Args:
            config_manager: Legacy configuration manager
            user_files_dir: Directory for user files (backups, exports)
        """
        self.config_manager = config_manager
        self.user_files_dir = Path(user_files_dir) if user_files_dir else Path.home() / '.anki_dict'
        self.user_files_dir.mkdir(parents=True, exist_ok=True)
        self._backup_dir = self.user_files_dir / 'config_backups'
        self._backup_dir.mkdir(parents=True, exist_ok=True)
    
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
            return self.config_manager.get_value(key, default)
        except Exception as e:
            logger.error(f"Error getting setting '{key}': {e}")
            return default
    
    def set_setting(self, key: str, value: Any) -> Dict[str, Any]:
        """
        Set a configuration setting.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            Result dictionary:
            {
                'success': bool,
                'key': str,
                'value': Any,
                'error': str or None
            }
        """
        try:
            self.config_manager.set_value(key, value)
            logger.debug(f"Setting '{key}' updated to {value}")
            return {
                'success': True,
                'key': key,
                'value': value,
                'error': None
            }
        except Exception as e:
            logger.error(f"Error setting '{key}': {e}")
            return {
                'success': False,
                'key': key,
                'value': value,
                'error': str(e)
            }
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all configuration settings.
        
        Returns:
            Dictionary of all settings
        """
        try:
            if hasattr(self.config_manager, 'get_all'):
                return self.config_manager.get_all()
            else:
                # Fallback: return empty dict
                logger.warning("Config manager doesn't support get_all()")
                return {}
        except Exception as e:
            logger.error(f"Error getting all settings: {e}")
            return {}
    
    def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update multiple settings at once.
        
        Args:
            settings: Dictionary of settings to update
            
        Returns:
            Result dictionary:
            {
                'success': bool,
                'updated': int,
                'failed': int,
                'errors': [str]
            }
        """
        updated = 0
        failed = 0
        errors = []
        
        for key, value in settings.items():
            result = self.set_setting(key, value)
            if result['success']:
                updated += 1
            else:
                failed += 1
                errors.append(result['error'])
        
        return {
            'success': failed == 0,
            'updated': updated,
            'failed': failed,
            'errors': errors
        }
    
    def export_settings(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Export all settings to a JSON file.
        
        Args:
            filename: Optional custom filename (uses timestamp if None)
            
        Returns:
            Result dictionary:
            {
                'success': bool,
                'filepath': str or None,
                'settings_count': int,
                'error': str or None
            }
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'settings_export_{timestamp}.json'
            
            filepath = self.user_files_dir / filename
            
            # Get all settings
            settings = self.get_all_settings()
            
            # Add metadata
            export_data = {
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'version': '1.0'
                },
                'settings': settings
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings exported to {filepath}")
            return {
                'success': True,
                'filepath': str(filepath),
                'settings_count': len(settings),
                'error': None
            }
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            return {
                'success': False,
                'filepath': None,
                'settings_count': 0,
                'error': str(e)
            }
    
    def import_settings(self, filepath: str) -> Dict[str, Any]:
        """
        Import settings from a JSON file.
        
        Args:
            filepath: Path to settings file
            
        Returns:
            Result dictionary:
            {
                'success': bool,
                'imported': int,
                'failed': int,
                'errors': [str],
                'preview': Dict[str, Any]
            }
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                return {
                    'success': False,
                    'imported': 0,
                    'failed': 0,
                    'errors': [f"File not found: {filepath}"],
                    'preview': {}
                }
            
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Extract settings
            settings = import_data.get('settings', {})
            
            # Create backup before importing
            self._create_backup()
            
            # Import settings
            result = self.update_settings(settings)
            
            logger.info(f"Settings imported from {filepath}: {result['updated']} updated, {result['failed']} failed")
            
            return {
                'success': result['success'],
                'imported': result['updated'],
                'failed': result['failed'],
                'errors': result['errors'],
                'preview': settings
            }
        except Exception as e:
            logger.error(f"Error importing settings: {e}")
            return {
                'success': False,
                'imported': 0,
                'failed': 0,
                'errors': [str(e)],
                'preview': {}
            }
    
    def backup_settings(self, label: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a backup of current settings.
        
        Args:
            label: Optional label for the backup
            
        Returns:
            Result dictionary:
            {
                'success': bool,
                'filepath': str or None,
                'error': str or None
            }
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            label_str = f'_{label}' if label else ''
            filename = f'settings_backup_{timestamp}{label_str}.json'
            
            filepath = self._backup_dir / filename
            
            # Get all settings
            settings = self.get_all_settings()
            
            # Add metadata
            backup_data = {
                'metadata': {
                    'backed_up_at': datetime.now().isoformat(),
                    'label': label,
                    'version': '1.0'
                },
                'settings': settings
            }
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings backed up to {filepath}")
            return {
                'success': True,
                'filepath': str(filepath),
                'error': None
            }
        except Exception as e:
            logger.error(f"Error backing up settings: {e}")
            return {
                'success': False,
                'filepath': None,
                'error': str(e)
            }
    
    def restore_settings(self, filepath: str) -> Dict[str, Any]:
        """
        Restore settings from a backup file.
        
        Args:
            filepath: Path to backup file
            
        Returns:
            Result dictionary:
            {
                'success': bool,
                'restored': int,
                'failed': int,
                'errors': [str]
            }
        """
        try:
            filepath = Path(filepath)
            
            if not filepath.exists():
                return {
                    'success': False,
                    'restored': 0,
                    'failed': 0,
                    'errors': [f"Backup file not found: {filepath}"]
                }
            
            # Read backup file
            with open(filepath, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Extract settings
            settings = backup_data.get('settings', {})
            
            # Create backup of current settings before restoring
            self._create_backup('pre_restore')
            
            # Restore settings
            result = self.update_settings(settings)
            
            logger.info(f"Settings restored from {filepath}: {result['updated']} restored, {result['failed']} failed")
            
            return {
                'success': result['success'],
                'restored': result['updated'],
                'failed': result['failed'],
                'errors': result['errors']
            }
        except Exception as e:
            logger.error(f"Error restoring settings: {e}")
            return {
                'success': False,
                'restored': 0,
                'failed': 0,
                'errors': [str(e)]
            }
    
    def list_backups(self) -> Dict[str, Any]:
        """
        List available backup files.
        
        Returns:
            Result dictionary:
            {
                'success': bool,
                'backups': [
                    {
                        'filename': str,
                        'filepath': str,
                        'created_at': str,
                        'label': str or None
                    }
                ],
                'error': str or None
            }
        """
        try:
            backups = []
            
            for backup_file in sorted(self._backup_dir.glob('settings_backup_*.json'), reverse=True):
                try:
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    
                    metadata = backup_data.get('metadata', {})
                    backups.append({
                        'filename': backup_file.name,
                        'filepath': str(backup_file),
                        'created_at': metadata.get('backed_up_at', 'unknown'),
                        'label': metadata.get('label')
                    })
                except Exception as e:
                    logger.warning(f"Error reading backup file {backup_file}: {e}")
            
            return {
                'success': True,
                'backups': backups,
                'error': None
            }
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return {
                'success': False,
                'backups': [],
                'error': str(e)
            }
    
    def _create_backup(self, label: Optional[str] = None) -> None:
        """
        Internal method to create a backup.
        
        Args:
            label: Optional label for the backup
        """
        try:
            self.backup_settings(label)
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
