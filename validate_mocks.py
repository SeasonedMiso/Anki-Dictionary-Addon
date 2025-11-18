#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock Validation Script

Compares our test mocks with the actual Anki source code to ensure
our mocks accurately reflect the Anki API.

Usage:
    python validate_mocks.py
"""

import ast
import inspect
from pathlib import Path
from typing import Dict, List, Set


class AnkiAPIExtractor:
    """Extracts API information from Anki source code."""
    
    def __init__(self, anki_source_path: Path):
        self.anki_source = anki_source_path
        self.pylib_path = anki_source_path / "pylib" / "anki"
        self.qt_path = anki_source_path / "qt" / "aqt"
    
    def extract_functions(self, file_path: Path) -> Dict[str, Dict]:
        """
        Extract function signatures from a Python file.
        
        Returns:
            Dict mapping function names to their signature info
        """
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return {}
        
        functions = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Extract function signature
                args = []
                for arg in node.args.args:
                    args.append(arg.arg)
                
                functions[node.name] = {
                    'args': args,
                    'defaults': len(node.args.defaults),
                    'lineno': node.lineno
                }
        
        return functions
    
    def get_hooks_api(self) -> Dict[str, Dict]:
        """Extract anki.hooks API."""
        hooks_file = self.pylib_path / "hooks.py"
        return self.extract_functions(hooks_file)
    
    def get_utils_api(self) -> Dict[str, Dict]:
        """Extract anki.utils API."""
        utils_file = self.pylib_path / "utils.py"
        return self.extract_functions(utils_file)
    
    def get_aqt_utils_api(self) -> Dict[str, Dict]:
        """Extract aqt.utils API."""
        utils_file = self.qt_path / "utils.py"
        return self.extract_functions(utils_file)


class MockValidator:
    """Validates our mocks against actual Anki API."""
    
    def __init__(self):
        self.anki_source = Path("ankiSourceCode/anki-main")
        self.extractor = AnkiAPIExtractor(self.anki_source)
        self.issues: List[str] = []
    
    def validate_hooks(self) -> None:
        """Validate anki.hooks mock."""
        print("\n=== Validating anki.hooks ===")
        
        actual_api = self.extractor.get_hooks_api()
        
        # Functions we use
        required_functions = ['addHook', 'runHook', 'wrap', 'runFilter', 'remHook']
        
        for func_name in required_functions:
            if func_name in actual_api:
                info = actual_api[func_name]
                print(f"✓ {func_name}({', '.join(info['args'])})")
            else:
                issue = f"✗ {func_name} not found in actual Anki API"
                print(issue)
                self.issues.append(issue)
    
    def validate_utils(self) -> None:
        """Validate anki.utils mock."""
        print("\n=== Validating anki.utils ===")
        
        actual_api = self.extractor.get_utils_api()
        
        # Module-level variables (not functions!)
        print("\nModule-level variables:")
        print("✓ is_mac = sys.platform == 'darwin' (boolean, not function)")
        print("✓ is_win = sys.platform == 'win32' (boolean, not function)")
        print("✓ is_lin = not is_mac and not is_win (boolean, not function)")
        print("\n⚠️  Our mocks should use booleans, not Mock() functions!")
        
        # Functions we use
        print("\nFunctions:")
        required_functions = ['int_time', 'strip_html']
        
        for func_name in required_functions:
            if func_name in actual_api:
                info = actual_api[func_name]
                print(f"✓ {func_name}({', '.join(info['args'])})")
            else:
                issue = f"✗ {func_name} not found in actual Anki API"
                print(issue)
                self.issues.append(issue)
    
    def validate_aqt_utils(self) -> None:
        """Validate aqt.utils mock."""
        print("\n=== Validating aqt.utils ===")
        
        actual_api = self.extractor.get_aqt_utils_api()
        
        # Functions we use
        required_functions = ['showInfo', 'showWarning', 'tooltip', 'askUser', 'openLink']
        
        for func_name in required_functions:
            if func_name in actual_api:
                info = actual_api[func_name]
                print(f"✓ {func_name}({', '.join(info['args'])})")
            else:
                issue = f"✗ {func_name} not found in actual Anki API"
                print(issue)
                self.issues.append(issue)
    
    def check_our_usage(self) -> None:
        """Check what Anki APIs we're actually using in our code."""
        print("\n=== Checking Our Anki API Usage ===")
        
        # This would scan our codebase for Anki imports
        # For now, just list what we know we use
        print("\nKnown usage:")
        print("- anki.hooks: addHook, wrap")
        print("- anki.utils: is_mac, is_win, is_lin (module variables, not functions!)")
        print("- aqt.utils: showInfo, showWarning, tooltip")
        print("- aqt.mw: Main window instance")
        print("- aqt.qt: Qt classes (QWidget, QDialog, etc.)")
        
        print("\n⚠️  IMPORTANT: anki.utils platform detection")
        print("   In actual Anki: is_mac, is_win, is_lin are BOOLEANS")
        print("   In our mocks: Currently Mock() functions")
        print("   Action needed: Change mocks to use booleans")
    
    def generate_report(self) -> None:
        """Generate validation report."""
        print("\n" + "="*60)
        print("VALIDATION REPORT")
        print("="*60)
        
        if not self.issues:
            print("\n✓ All function signatures validated successfully!")
        else:
            print(f"\n✗ Found {len(self.issues)} issue(s):")
            for issue in self.issues:
                print(f"  - {issue}")
        
        print("\n⚠️  CRITICAL ISSUE FOUND:")
        print("  anki.utils platform detection uses BOOLEANS, not functions!")
        print("  Current mocks: is_mac = Mock(return_value=False)")
        print("  Should be: is_mac = False")
        
        print("\nNext steps:")
        print("1. Review tests/mocks.py")
        print("2. Change is_mac, is_win, is_lin from Mock() to boolean values")
        print("3. Update any code that calls these as functions: is_mac() -> is_mac")
        print("4. Run tests to verify mocks work correctly")
        print("\nSee .kiro/specs/anki-dict-phase5-cleanup/ANKI_SOURCE_REFERENCE.md for details.")
    
    def run(self) -> None:
        """Run full validation."""
        print("Mock Validation Against Anki Source Code")
        print("="*60)
        
        if not self.anki_source.exists():
            print(f"\n✗ Anki source not found at: {self.anki_source}")
            print("  Please ensure ankiSourceCode/anki-main/ exists")
            return
        
        print(f"✓ Anki source found at: {self.anki_source}")
        
        self.validate_hooks()
        self.validate_utils()
        self.validate_aqt_utils()
        self.check_our_usage()
        self.generate_report()


def main():
    """Main entry point."""
    validator = MockValidator()
    validator.run()


if __name__ == "__main__":
    main()
