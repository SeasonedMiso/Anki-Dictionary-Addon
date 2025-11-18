#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Rewriter Script for Phase 5 Reorganization

This script automatically updates import statements after file reorganization.
It handles:
- Updating imports for files moved to libs/
- Updating imports for files moved to legacy/
- Updating imports for consolidated utility modules
- Fixing relative import paths
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ImportRewriter:
    """
    Rewrites import statements after file moves.
    
    This class scans Python files and updates import statements according
    to the new project structure after Phase 5 reorganization.
    """
    
    # Mapping of old imports to new imports
    # Format: old_import_pattern -> new_import_pattern
    IMPORT_MAPPINGS = {
        # Legacy UI files (moved to legacy/)
        'from .legacy.midict import': 'from .legacy.midict import',
        'from legacy.midict import': 'from legacy.midict import',
        'import legacy.midict': 'import legacy.midict',
        
        'from .legacy.addonSettings import': 'from .legacy.addonSettings import',
        'from legacy.addonSettings import': 'from legacy.addonSettings import',
        'import legacy.addonSettings': 'import legacy.addonSettings',
        
        'from .legacy.dictionaryManager import': 'from .legacy.dictionaryManager import',
        'from legacy.dictionaryManager import': 'from legacy.dictionaryManager import',
        'import legacy.dictionaryManager': 'import legacy.dictionaryManager',
        
        'from .legacy.cardExporter import': 'from .legacy.cardExporter import',
        'from legacy.cardExporter import': 'from legacy.cardExporter import',
        'import legacy.cardExporter': 'import legacy.cardExporter',
        
        'from .legacy.dictdb import': 'from .legacy.dictdb import',
        'from legacy.dictdb import': 'from legacy.dictdb import',
        'import legacy.dictdb': 'import legacy.dictdb',
        
        # Utility consolidation (miutils -> src.utils.dialogs)
        'from .src.utils.dialogs import': 'from .src.utils.dialogs import',
        'from src.utils.dialogs import': 'from src.utils.dialogs import',
        'import src.utils.dialogs': 'import src.utils.dialogs',
        
        # Theme files (already in src/ui/ - no change needed for relative imports within src/ui/)
        # Only update absolute imports from outside src/ui/
        'from src.ui.themes import': 'from src.ui.themes import',
        'import src.ui.themes': 'import src.ui.themes',
        
        'from src.ui.theme_editor import': 'from src.ui.theme_editor import',
        'import src.ui.theme_editor': 'import src.ui.theme_editor',
        
        # Third-party libraries (no change needed - already in libs/ and sys.path)
        # These don't need rewriting since libs/ is added to sys.path
    }
    
    # Additional patterns for specific cases
    SPECIFIC_REPLACEMENTS = {
        # Function renames from miutils
        'show_info_dialog': 'show_info_dialog',
        'ask_user_dialog': 'ask_user_dialog',
    }
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize the import rewriter.
        
        Args:
            dry_run: If True, only report changes without modifying files
        """
        self.dry_run = dry_run
        self.changes_made = 0
        self.files_processed = 0
        self.errors = []
    
    def rewrite_file(self, file_path: Path) -> bool:
        """
        Rewrite imports in a single file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            True if changes were made, False otherwise
        """
        if not file_path.exists() or not file_path.is_file():
            logger.warning(f"File not found: {file_path}")
            return False
        
        if file_path.suffix != '.py':
            logger.debug(f"Skipping non-Python file: {file_path}")
            return False
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Rewrite imports
            new_content, changes = self._rewrite_content(original_content, file_path)
            
            if changes > 0:
                logger.info(f"{'[DRY RUN] ' if self.dry_run else ''}Updated {changes} import(s) in: {file_path}")
                
                if not self.dry_run:
                    # Write back to file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                
                self.changes_made += changes
                self.files_processed += 1
                return True
            else:
                logger.debug(f"No changes needed in: {file_path}")
                return False
        
        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return False
    
    def _rewrite_content(self, content: str, file_path: Path) -> Tuple[str, int]:
        """
        Rewrite import statements in file content.
        
        Args:
            content: Original file content
            file_path: Path to file (for context)
            
        Returns:
            Tuple of (new_content, number_of_changes)
        """
        new_content = content
        changes = 0
        
        # Apply import mappings
        for old_pattern, new_pattern in self.IMPORT_MAPPINGS.items():
            if old_pattern in new_content:
                # Count occurrences
                count = new_content.count(old_pattern)
                
                # Replace
                new_content = new_content.replace(old_pattern, new_pattern)
                
                changes += count
                logger.debug(f"  Replaced '{old_pattern}' -> '{new_pattern}' ({count} times)")
        
        # Apply specific function/class name replacements
        for old_name, new_name in self.SPECIFIC_REPLACEMENTS.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(old_name) + r'\b'
            if re.search(pattern, new_content):
                count = len(re.findall(pattern, new_content))
                new_content = re.sub(pattern, new_name, new_content)
                changes += count
                logger.debug(f"  Replaced '{old_name}' -> '{new_name}' ({count} times)")
        
        return new_content, changes
    
    def rewrite_directory(self, directory: Path, exclude_patterns: Optional[List[str]] = None) -> None:
        """
        Rewrite imports in all Python files in a directory.
        
        Args:
            directory: Directory to process
            exclude_patterns: List of glob patterns to exclude
        """
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found: {directory}")
            return
        
        exclude_patterns = exclude_patterns or []
        
        logger.info(f"Processing directory: {directory}")
        
        # Find all Python files
        python_files = list(directory.rglob('*.py'))
        
        # Filter out excluded files
        filtered_files = []
        for file_path in python_files:
            # Check if file matches any exclude pattern
            excluded = False
            for pattern in exclude_patterns:
                if file_path.match(pattern):
                    excluded = True
                    break
            
            if not excluded:
                filtered_files.append(file_path)
        
        logger.info(f"Found {len(filtered_files)} Python files to process")
        
        # Process each file
        for file_path in filtered_files:
            self.rewrite_file(file_path)
    
    def rewrite_all(self, root_dir: Path) -> None:
        """
        Rewrite imports in all relevant directories.
        
        Args:
            root_dir: Root directory of the addon
        """
        logger.info("=" * 60)
        logger.info("Starting import rewrite process")
        logger.info("=" * 60)
        
        # Define directories to process
        directories = [
            (root_dir / 'src', ['**/test_*.py', '**/__pycache__/*']),
            (root_dir / 'tests', ['**/__pycache__/*']),
            (root_dir, ['**/test_*.py', '**/__pycache__/*', '**/libs/*', '**/legacy/*', 
                       '**/ankiSourceCode/*', '**/.git/*', '**/.kiro/*', '**/user_files/*',
                       '**/htmlcov/*', '**/.pytest_cache/*', '**/__pycache__/*'])
        ]
        
        for directory, exclude_patterns in directories:
            if directory.exists():
                self.rewrite_directory(directory, exclude_patterns)
        
        # Summary
        logger.info("=" * 60)
        logger.info("Import rewrite complete")
        logger.info(f"Files processed: {self.files_processed}")
        logger.info(f"Total changes: {self.changes_made}")
        if self.errors:
            logger.warning(f"Errors encountered: {len(self.errors)}")
            for error in self.errors:
                logger.warning(f"  - {error}")
        logger.info("=" * 60)
    
    def verify_syntax(self, file_path: Path) -> bool:
        """
        Verify that a file has valid Python syntax.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ast.parse(content)
            return True
        
        except SyntaxError as e:
            logger.error(f"Syntax error in {file_path}: {e}")
            return False
        
        except Exception as e:
            logger.error(f"Error verifying {file_path}: {e}")
            return False
    
    def verify_all_syntax(self, root_dir: Path) -> Tuple[int, int]:
        """
        Verify syntax of all Python files.
        
        Args:
            root_dir: Root directory to check
            
        Returns:
            Tuple of (valid_count, invalid_count)
        """
        logger.info("Verifying Python syntax...")
        
        python_files = list(root_dir.rglob('*.py'))
        
        # Exclude certain directories
        exclude_dirs = ['libs', 'legacy', 'ankiSourceCode', '.git', '.kiro', 
                       'user_files', 'htmlcov', '.pytest_cache', '__pycache__']
        
        filtered_files = []
        for file_path in python_files:
            excluded = False
            for exclude_dir in exclude_dirs:
                if exclude_dir in file_path.parts:
                    excluded = True
                    break
            if not excluded:
                filtered_files.append(file_path)
        
        valid = 0
        invalid = 0
        
        for file_path in filtered_files:
            if self.verify_syntax(file_path):
                valid += 1
            else:
                invalid += 1
        
        logger.info(f"Syntax verification complete: {valid} valid, {invalid} invalid")
        return valid, invalid


def main():
    """Main entry point for the import rewriter script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Rewrite import statements after Phase 5 reorganization'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify Python syntax after rewriting'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Process a single file instead of all files'
    )
    parser.add_argument(
        '--directory',
        type=str,
        help='Process a specific directory instead of all directories'
    )
    
    args = parser.parse_args()
    
    # Get root directory (current directory)
    root_dir = Path.cwd()
    
    # Create rewriter
    rewriter = ImportRewriter(dry_run=args.dry_run)
    
    # Process files
    if args.file:
        # Process single file
        file_path = Path(args.file)
        rewriter.rewrite_file(file_path)
    elif args.directory:
        # Process specific directory
        directory = Path(args.directory)
        rewriter.rewrite_directory(directory)
    else:
        # Process all files
        rewriter.rewrite_all(root_dir)
    
    # Verify syntax if requested
    if args.verify and not args.dry_run:
        rewriter.verify_all_syntax(root_dir)


if __name__ == '__main__':
    main()
