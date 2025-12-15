#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Export UI Mock.

This script runs the export UI mock independently for testing and development.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from aqt.qt import QApplication
    from src.ui.export_ui_mock import show_export_ui_mock
    
    def main():
        """Run the export UI mock."""
        app = QApplication(sys.argv)
        
        # Show export UI mock
        window = show_export_ui_mock()
        
        # Run application
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("This script requires Anki/PyQt to be available.")
    print("Run from within Anki environment or install PyQt6.")
    sys.exit(1)