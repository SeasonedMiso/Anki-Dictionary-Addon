#!/usr/bin/env python3
"""
File Audit Script for Phase 5 Cleanup

This script scans all files in the addon root directory and classifies them
according to the Phase 5 reorganization plan.

Classification Categories:
- KEEP_IN_ROOT: Essential addon files that must stay in root
- MOVE_TO_LIBS: Third-party dependencies to move to libs/
- MOVE_TO_LEGACY: Deprecated files to move to legacy/
- DELETE: Backup files and truly unused files to delete
- ALREADY_REFACTORED: Files already in src/ or other organized directories
- EVALUATE: Files that need manual review
"""

import os
from pathlib import Path
from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass
import json


class FileAction(Enum):
    """Classification categories for files."""
    KEEP_IN_ROOT = "keep_root"
    MOVE_TO_LIBS = "move_libs"
    MOVE_TO_LEGACY = "move_legacy"
    DELETE = "delete"
    ALREADY_REFACTORED = "refactored"
    EVALUATE = "evaluate"


@dataclass
class FileClassification:
    """Represents a file and its classification."""
    path: str
    action: FileAction
    reason: str
    is_directory: bool = False


class FileAuditor:
    """Audits files in the addon root and classifies them for reorganization."""
    
    # Files that must stay in root for Anki addon to work
    KEEP_IN_ROOT = {
        'main.py',
        '__init__.py',
        'config.json',
        'manifest.json',
        'meta.json',
        'README.md',
    }
    
    # Third-party library directories to move to libs/
    LIBS_DIRECTORIES = {
        'bs4',
        'requests',
        'urllib3',
        'tornado',
        'pynput',
        'pyobjc-core',
        'HIServices',
        'keyboardMac',
        'linux',  # Platform-specific keyboard handling
    }
    
    # Single-file libraries to move to libs/
    LIBS_FILES = {
        'six.py',
        'Pyperclip.py',
    }
    
    # Legacy UI files that have been refactored
    LEGACY_FILES = {
        'midict.py',
        'addonSettings.py',
        'dictionaryManager.py',
        'cardExporter.py',
        'dictdb.py',  # If not used by refactored code
    }
    
    # Backup files to delete
    DELETE_FILES = {
        'main_old_backup.py',
        'main_refactored.py',
        'dictdb_old_backup.py',
        'test_phase2.py',
    }
    
    # Files that need manual evaluation
    EVALUATE_FILES = {
        'miutils.py',
        'themes.py',
        'themeEditor.py',
        'history.py',
        'forvodl.py',
        'googleimages.py',
        'checkForThirtyTwo.py',
        'dict_wizard.py',
        'migaku_wizard.py',
        'dictionaryWebInstallWizard.py',
        'miJapaneseHandler.py',
        'miUpdater.py',
        'miflix.py',
        'migakuMessage.py',
        'misoMessage.py',
        'webConfig.py',
        'ffmpegInstaller.py',
        'freqConjWebWindow.py',
        'addDictGroup.py',
        'addTemplate.py',
        'init_db.py',
    }
    
    # Directories that are already organized
    ORGANIZED_DIRECTORIES = {
        'src',
        'tests',
        'libs',
        'legacy',
        'docs',
        'icons',
        'js',
        'user_files',
        'temp',
    }
    
    # Directories to ignore (development/build artifacts)
    IGNORE_DIRECTORIES = {
        '.git',
        '.github',
        '.idea',
        '.kiro',
        '.pytest_cache',
        '.venv',
        '.vscode',
        '__pycache__',
        'htmlcov',
    }
    
    # File patterns to ignore
    IGNORE_FILES = {
        '.coverage',
        '.gitignore',
        'file_audit.py',  # This script itself
        'import_analyzer.py',  # The import analyzer script
    }
    
    # HTML/CSS/Font files - keep in root for now
    ASSET_FILES = {
        '.html',
        '.css',
        '.ttc',
        '.md',  # Markdown docs (except README.md which is in KEEP_IN_ROOT)
    }
    
    def __init__(self, root_dir: str = '.'):
        """Initialize the auditor with the addon root directory."""
        self.root_dir = Path(root_dir)
        self.classifications: List[FileClassification] = []
    
    def scan(self) -> List[FileClassification]:
        """Scan all files and directories in the root and classify them."""
        self.classifications = []
        
        # Scan all items in root directory
        for item in sorted(self.root_dir.iterdir()):
            if item.name.startswith('.') and item.name not in self.IGNORE_FILES:
                # Hidden files/dirs - check if should ignore
                if item.is_dir() and item.name in self.IGNORE_DIRECTORIES:
                    continue
                elif item.is_file() and item.name in self.IGNORE_FILES:
                    continue
            
            classification = self._classify_item(item)
            if classification:
                self.classifications.append(classification)
        
        return self.classifications
    
    def _classify_item(self, item: Path) -> FileClassification:
        """Classify a single file or directory."""
        name = item.name
        is_dir = item.is_dir()
        
        # Skip ignored items
        if name in self.IGNORE_DIRECTORIES or name in self.IGNORE_FILES:
            return None
        
        # Directories
        if is_dir:
            if name in self.ORGANIZED_DIRECTORIES:
                return FileClassification(
                    path=name,
                    action=FileAction.ALREADY_REFACTORED,
                    reason="Already organized directory",
                    is_directory=True
                )
            elif name in self.LIBS_DIRECTORIES:
                return FileClassification(
                    path=name,
                    action=FileAction.MOVE_TO_LIBS,
                    reason="Third-party library directory",
                    is_directory=True
                )
            else:
                return FileClassification(
                    path=name,
                    action=FileAction.EVALUATE,
                    reason="Unknown directory - needs review",
                    is_directory=True
                )
        
        # Files
        if name in self.KEEP_IN_ROOT:
            return FileClassification(
                path=name,
                action=FileAction.KEEP_IN_ROOT,
                reason="Essential addon file"
            )
        elif name in self.LIBS_FILES:
            return FileClassification(
                path=name,
                action=FileAction.MOVE_TO_LIBS,
                reason="Third-party library file"
            )
        elif name in self.LEGACY_FILES:
            return FileClassification(
                path=name,
                action=FileAction.MOVE_TO_LEGACY,
                reason="Legacy UI file (refactored)"
            )
        elif name in self.DELETE_FILES:
            return FileClassification(
                path=name,
                action=FileAction.DELETE,
                reason="Backup file - no longer needed"
            )
        elif name in self.EVALUATE_FILES:
            return FileClassification(
                path=name,
                action=FileAction.EVALUATE,
                reason="Needs manual review to determine usage"
            )
        else:
            # Check file extension for assets
            suffix = item.suffix
            if suffix in self.ASSET_FILES:
                return FileClassification(
                    path=name,
                    action=FileAction.KEEP_IN_ROOT,
                    reason=f"Asset file ({suffix})"
                )
            else:
                return FileClassification(
                    path=name,
                    action=FileAction.EVALUATE,
                    reason="Unknown file - needs review"
                )
    
    def generate_report(self, output_format: str = 'text') -> str:
        """Generate a report of the classification results."""
        if output_format == 'json':
            return self._generate_json_report()
        else:
            return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate a human-readable text report."""
        lines = []
        lines.append("=" * 80)
        lines.append("FILE AUDIT REPORT - Phase 5 Cleanup")
        lines.append("=" * 80)
        lines.append("")
        
        # Group by action
        by_action: Dict[FileAction, List[FileClassification]] = {}
        for classification in self.classifications:
            action = classification.action
            if action not in by_action:
                by_action[action] = []
            by_action[action].append(classification)
        
        # Summary
        lines.append("SUMMARY")
        lines.append("-" * 80)
        for action in FileAction:
            count = len(by_action.get(action, []))
            lines.append(f"  {action.value:20s}: {count:3d} items")
        lines.append(f"  {'TOTAL':20s}: {len(self.classifications):3d} items")
        lines.append("")
        
        # Detailed breakdown by action
        action_order = [
            FileAction.KEEP_IN_ROOT,
            FileAction.ALREADY_REFACTORED,
            FileAction.MOVE_TO_LIBS,
            FileAction.MOVE_TO_LEGACY,
            FileAction.DELETE,
            FileAction.EVALUATE,
        ]
        
        for action in action_order:
            items = by_action.get(action, [])
            if not items:
                continue
            
            lines.append("")
            lines.append(f"{action.value.upper().replace('_', ' ')}")
            lines.append("-" * 80)
            
            # Separate directories and files
            dirs = [item for item in items if item.is_directory]
            files = [item for item in items if not item.is_directory]
            
            if dirs:
                lines.append("  Directories:")
                for item in sorted(dirs, key=lambda x: x.path):
                    lines.append(f"    {item.path:40s} - {item.reason}")
            
            if files:
                if dirs:
                    lines.append("")
                lines.append("  Files:")
                for item in sorted(files, key=lambda x: x.path):
                    lines.append(f"    {item.path:40s} - {item.reason}")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _generate_json_report(self) -> str:
        """Generate a JSON report."""
        data = {
            'summary': {},
            'classifications': []
        }
        
        # Summary
        for action in FileAction:
            count = sum(1 for c in self.classifications if c.action == action)
            data['summary'][action.value] = count
        data['summary']['total'] = len(self.classifications)
        
        # Classifications
        for classification in self.classifications:
            data['classifications'].append({
                'path': classification.path,
                'action': classification.action.value,
                'reason': classification.reason,
                'is_directory': classification.is_directory
            })
        
        return json.dumps(data, indent=2)
    
    def save_report(self, filename: str = 'file_audit_report.txt', output_format: str = 'text'):
        """Save the report to a file."""
        report = self.generate_report(output_format)
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Report saved to: {filename}")


def main():
    """Main entry point for the file audit script."""
    print("Starting file audit...")
    print()
    
    auditor = FileAuditor()
    classifications = auditor.scan()
    
    print(f"Scanned {len(classifications)} items")
    print()
    
    # Generate and display report
    report = auditor.generate_report('text')
    print(report)
    
    # Save reports
    auditor.save_report('file_audit_report.txt', 'text')
    auditor.save_report('file_audit_report.json', 'json')
    
    print()
    print("Reports saved:")
    print("  - file_audit_report.txt (human-readable)")
    print("  - file_audit_report.json (machine-readable)")


if __name__ == '__main__':
    main()
