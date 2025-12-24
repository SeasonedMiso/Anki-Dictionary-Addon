#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo/Example usage of modern UI components.

This file demonstrates how to use the modern components in a standalone way.
It can be run directly for testing purposes.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from aqt.qt import QApplication, QMainWindow, QVBoxLayout, QWidget
    from src.ui.dictionary_widgets import (
        ModernSearchBar,
        DefinitionCard,
        DictionaryFilterBar,
        ModernResultsArea
    )
    ANKI_AVAILABLE = True
except ImportError:
    print("Anki not available. This demo requires Anki to be installed.")
    sys.exit(1)


class ModernComponentsDemo(QMainWindow):
    """Demo window showing all modern components."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modern Dictionary Components Demo")
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Create layout
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add search bar
        self.search_bar = ModernSearchBar()
        self.search_bar.searchChanged.connect(self.on_search)
        layout.addWidget(self.search_bar)
        
        # Add filter bar
        self.filter_bar = DictionaryFilterBar()
        self.filter_bar.filterChanged.connect(self.on_filter_changed)
        layout.addWidget(self.filter_bar)
        
        # Add results area
        self.results_area = ModernResultsArea()
        layout.addWidget(self.results_area)
        
        # Add some sample cards
        self.add_sample_cards()
        
        # Apply dark theme styling to window
        self.setStyleSheet("""
            QMainWindow {
                background: #1a1a1a;
            }
        """)
    
    def add_sample_cards(self):
        """Add sample definition cards to demonstrate the UI."""
        sample_words = [
            {
                'word': 'Dictionary',
                'phonetic': '/ˈdɪkʃəˌnɛri/',
                'frequency': '1000',
                'definitions': [
                    {
                        'type': 'noun',
                        'text': 'A book or electronic resource that lists the words of a language and gives their meaning.'
                    },
                    {
                        'type': 'noun',
                        'text': 'A reference book on any subject, the items of which are arranged in alphabetical order.'
                    }
                ],
                'examples': [
                    'I looked up the word in the dictionary.',
                    'This dictionary contains over 100,000 entries.'
                ]
            },
            {
                'word': 'Modern',
                'phonetic': '/ˈmɒdən/',
                'frequency': '500',
                'definitions': [
                    {
                        'type': 'adjective',
                        'text': 'Relating to the present or recent times as opposed to the remote past.'
                    },
                    {
                        'type': 'adjective',
                        'text': 'Characterized by or using the most up-to-date techniques, ideas, or equipment.'
                    }
                ],
                'examples': [
                    'Modern technology has changed our lives.',
                    'She prefers modern art to classical.'
                ]
            },
            {
                'word': 'Component',
                'phonetic': '/kəmˈpoʊnənt/',
                'frequency': '750',
                'definitions': [
                    {
                        'type': 'noun',
                        'text': 'A part or element of a larger whole, especially a part of a machine or vehicle.'
                    }
                ],
                'examples': [
                    'The components of the system work together seamlessly.'
                ]
            }
        ]
        
        for word_data in sample_words:
            card = DefinitionCard(word_data)
            
            # Connect signals
            card.audioRequested.connect(self.on_audio_requested)
            card.imageRequested.connect(self.on_image_requested)
            card.exportRequested.connect(self.on_export_requested)
            
            self.results_area.add_card(card)
    
    def on_search(self, text: str):
        """Handle search text change."""
        print(f"Search: {text}")
        if text:
            print(f"  Would search for: '{text}'")
            print(f"  Current filter: {self.filter_bar.get_selected_filter()}")
    
    def on_filter_changed(self, filter_id: str):
        """Handle filter change."""
        print(f"Filter changed to: {filter_id}")
    
    def on_audio_requested(self, word: str):
        """Handle audio button click."""
        print(f"🔊 Audio requested for: {word}")
    
    def on_image_requested(self, word: str):
        """Handle image button click."""
        print(f"🖼️ Image requested for: {word}")
    
    def on_export_requested(self, word: str):
        """Handle export button click."""
        print(f"💾 Export requested for: {word}")


def main():
    """Run the demo application."""
    app = QApplication(sys.argv)
    
    # Set application-wide dark theme
    app.setStyle("Fusion")
    
    demo = ModernComponentsDemo()
    demo.show()
    
    print("\n" + "="*60)
    print("Modern Dictionary Components Demo")
    print("="*60)
    print("\nFeatures demonstrated:")
    print("  • ModernSearchBar with 300ms debounced search")
    print("  • DictionaryFilterBar with mutual exclusion")
    print("  • DefinitionCard with color-coded action buttons")
    print("  • ModernResultsArea with scrollable layout")
    print("\nTry:")
    print("  • Type in the search bar (watch console for debounced output)")
    print("  • Click filter buttons (only one active at a time)")
    print("  • Click action buttons on cards (🔊 🖼️ 💾)")
    print("  • Hover over cards and buttons for visual feedback")
    print("="*60 + "\n")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
