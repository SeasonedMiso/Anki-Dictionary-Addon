#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export UI Demo Script.

This script demonstrates the complete export UI system with all components:
- Export queue management
- Card preview with template rendering  
- Export history tracking
- Batch operations
- Theme integration

Run this script to see the export UI in action with sample data.
"""

import sys
import os

# Add src to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

def main():
    """Run the export UI demo."""
    try:
        # Import Qt and UI components
        from aqt.qt import QApplication
        from ui.export_ui_mock import show_export_ui_mock
        from ui.ui_mock import show_ui_mock
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Anki Dictionary Export UI Demo")
        
        print("🚀 Starting Export Dialog Demo...")
        print("📋 Features demonstrated:")
        print("   • Edit word/term before export")
        print("   • Add example sentences")
        print("   • Paste images from clipboard")
        print("   • Paste audio from clipboard")
        print("   • Configure dictionary auto-add settings")
        print("   • Export to Anki")
        print()
        
        # Show main dictionary UI with export button
        main_window = show_ui_mock()
        main_window.setWindowTitle("Dictionary UI - Click 📤 or 'Export' on words")
        
        print("✅ Dictionary UI opened!")
        print("💡 Try these interactions:")
        print("   • Click 'Export' button on any word definition")
        print("   • Edit the word in the export dialog")
        print("   • Add an example sentence")
        print("   • Paste an image from clipboard (📷 button)")
        print("   • Paste audio from clipboard (🔊 button)")
        print("   • Select dictionary for auto-add definitions")
        print("   • Click 'Export to Anki' to complete")
        print()
        print("🎯 Export Dialog Features:")
        print("   • Pre-filled with word from definition")
        print("   • Simple, focused interface")
        print("   • Clipboard integration for media")
        print("   • Dictionary selection for auto-add")
        print()
        print("🔄 Close windows to exit demo")
        
        # Run the application
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print()
        print("This demo requires PyQt6 or Anki environment.")
        print("Solutions:")
        print("  1. Run from within Anki addon environment")
        print("  2. Install PyQt6: pip install PyQt6")
        print("  3. Use Anki's Python: /path/to/anki/python demo_export_ui.py")
        return 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code or 0)