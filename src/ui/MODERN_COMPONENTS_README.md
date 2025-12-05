# Modern UI Components

This document describes the modern UI components implemented for the Anki Dictionary addon redesign.

## Overview

The modern components provide a beautiful, accessible, and performant UI following the design specifications from `.kiro/specs/modern-ui-redesign/`. All components use PyQt6 (via `aqt.qt`) and follow Anki's design patterns.

## Components

### 1. ModernSearchBar

A modern search input with debounced search functionality.

**Features:**
- 50px height with rounded corners (12px)
- Emoji placeholder (🔍)
- 300ms debounced search (prevents excessive searches while typing)
- Focus states with blue border (#4a9eff)
- Signal-based event handling

**Usage:**
```python
from src.ui.modern_components import ModernSearchBar

search_bar = ModernSearchBar()
search_bar.searchChanged.connect(on_search_handler)

# Get/set text
text = search_bar.text()
search_bar.setText("new query")
search_bar.clear()
```

**Signals:**
- `searchChanged(str)`: Emitted after 300ms debounce when text changes

**Styling:**
- Dark theme optimized (#2a2a2a background)
- Blue focus border (#4a9eff)
- 16px font size
- Smooth transitions

---

### 2. DefinitionCard

A card component for displaying dictionary definitions with actions.

**Features:**
- Rounded corners (12px) with hover effects
- Word header (28px bold), phonetic (16px), frequency badge (⭐)
- Color-coded action buttons (50x50px):
  - 🔊 Audio (blue #4a9eff)
  - 🖼️ Image (green #50c878)
  - 💾 Export (purple #9b59b6)
- Definition frames with part-of-speech badges
- Left border accent (4px)
- First definition highlighted (#1a3a5a)
- Example sentences in italic with dark background

**Usage:**
```python
from src.ui.modern_components import DefinitionCard

word_data = {
    'word': 'example',
    'phonetic': '/ɪɡˈzæmpəl/',
    'frequency': '1000',
    'definitions': [
        {'type': 'noun', 'text': 'A thing characteristic of its kind'},
        {'type': 'verb', 'text': 'To be illustrated or exemplified'}
    ],
    'examples': [
        'This is an example sentence.',
        'Another example here.'
    ]
}

card = DefinitionCard(word_data)
card.audioRequested.connect(on_audio_handler)
card.imageRequested.connect(on_image_handler)
card.exportRequested.connect(on_export_handler)
```

**Signals:**
- `audioRequested(str)`: Emitted when audio button clicked (passes word)
- `imageRequested(str)`: Emitted when image button clicked (passes word)
- `exportRequested(str)`: Emitted when export button clicked (passes word)

**Word Data Structure:**
```python
{
    'word': str,              # Required: The word/term
    'phonetic': str,          # Optional: Phonetic pronunciation
    'frequency': str,         # Optional: Frequency ranking
    'definitions': [          # Required: List of definitions
        {
            'type': str,      # Part of speech (noun, verb, etc.)
            'text': str       # Definition text
        }
    ],
    'examples': [str]         # Optional: Example sentences
}
```

---

### 3. DictionaryFilterBar

A filter bar with mutually exclusive checkable buttons.

**Features:**
- Horizontal layout with checkable QPushButtons
- Mutual exclusion (only one active at a time)
- Active state: blue background (#4a9eff)
- Inactive state: dark gray (#2a2a2a)
- 40px minimum height for touch targets
- Hover states for visual feedback

**Usage:**
```python
from src.ui.modern_components import DictionaryFilterBar

# Default dictionaries
filter_bar = DictionaryFilterBar()

# Custom dictionaries
custom_dicts = [
    ("All Dictionaries", "all"),
    ("Webster's", "webster"),
    ("JMDict (JP)", "jmdict")
]
filter_bar = DictionaryFilterBar(dictionaries=custom_dicts)

filter_bar.filterChanged.connect(on_filter_handler)

# Get/set selected filter
selected = filter_bar.get_selected_filter()
filter_bar.set_selected_filter("webster")
```

**Signals:**
- `filterChanged(str)`: Emitted when filter selection changes (passes dict_id)

**Dictionary Format:**
List of tuples: `[(display_name, dict_id), ...]`

---

### 4. ModernResultsArea

A scrollable area for displaying definition cards.

**Features:**
- QScrollArea with proper styling
- Vertical layout for definition cards
- Smooth scrolling
- Dark theme styling (#1a1a1a background)
- Custom scrollbar styling

**Usage:**
```python
from src.ui.modern_components import ModernResultsArea, DefinitionCard

results_area = ModernResultsArea()

# Add cards
card = DefinitionCard(word_data)
results_area.add_card(card)

# Clear all cards
results_area.clear_cards()

# Get card count
count = results_area.get_card_count()
```

**Methods:**
- `add_card(card: DefinitionCard)`: Add a definition card
- `clear_cards()`: Remove all cards
- `get_card_count() -> int`: Get number of cards

---

## Design Specifications

All components follow the design specifications from:
- `.kiro/specs/modern-ui-redesign/design.md`
- `.kiro/specs/modern-ui-redesign/requirements.md`

### Color Palette

**Dark Mode (Primary):**
- Background: `#1a1a1a`, `#2a2a2a`
- Text: `#ffffff`, `#888`
- Primary: `#4a9eff` (blue)
- Success: `#50c878` (green)
- Warning: `#9b59b6` (purple)
- Borders: `#444`, `#555`

### Typography

- Search: 16px
- Word: 28px bold
- Phonetic: 16px
- Frequency: 14px
- Definition: 14px
- Part of speech badge: 11px bold

### Spacing

- Card padding: 20px
- Element spacing: 10-15px
- Button size: 50x50px (action buttons), 40px height (filter buttons)

### Border Radius

- Cards: 12px
- Buttons: 8px
- Definition frames: 6px
- Part of speech badges: 4px

## Integration Example

Here's how to integrate all components together:

```python
from aqt.qt import QWidget, QVBoxLayout
from src.ui.modern_components import (
    ModernSearchBar,
    DictionaryFilterBar,
    ModernResultsArea,
    DefinitionCard
)

class ModernDictionaryWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        # Search bar
        self.search_bar = ModernSearchBar()
        self.search_bar.searchChanged.connect(self.perform_search)
        layout.addWidget(self.search_bar)
        
        # Filter bar
        self.filter_bar = DictionaryFilterBar()
        self.filter_bar.filterChanged.connect(self.on_filter_changed)
        layout.addWidget(self.filter_bar)
        
        # Results area
        self.results_area = ModernResultsArea()
        layout.addWidget(self.results_area)
    
    def perform_search(self, query: str):
        # Clear previous results
        self.results_area.clear_cards()
        
        # Get selected filter
        filter_id = self.filter_bar.get_selected_filter()
        
        # Perform search (your logic here)
        results = search_dictionaries(query, filter_id)
        
        # Display results
        for result in results:
            card = DefinitionCard(result)
            card.audioRequested.connect(self.play_audio)
            card.imageRequested.connect(self.show_images)
            card.exportRequested.connect(self.export_to_card)
            self.results_area.add_card(card)
    
    def on_filter_changed(self, filter_id: str):
        # Re-run search with new filter
        query = self.search_bar.text()
        if query:
            self.perform_search(query)
    
    def play_audio(self, word: str):
        # Handle audio playback
        pass
    
    def show_images(self, word: str):
        # Handle image search
        pass
    
    def export_to_card(self, word: str):
        # Handle card export
        pass
```

## Testing

Run the demo to see all components in action:

```bash
python src/ui/modern_components_demo.py
```

Run unit tests:

```bash
pytest tests/test_modern_components.py -v
```

## Requirements Validation

This implementation satisfies the following requirements from the spec:

- **1.2, 1.3**: Modern visual design with proper spacing and typography
- **3.1, 3.2**: Responsive layout components
- **4.1, 4.3**: Modern component library with consistent styling
- **5.1-5.3**: Improved search experience with debouncing
- **6.1-6.5**: Enhanced dictionary entry display with cards
- **8.1, 8.2, 8.5**: Accessibility with proper focus states and touch targets
- **9.3, 9.4**: Performance with smooth animations
- **12.1**: Touch-friendly design with 40-50px targets

## Future Enhancements

Potential improvements for future iterations:

1. **Light mode support**: Add light theme color palette
2. **Animation system**: Add smooth transitions for card appearance
3. **Keyboard navigation**: Enhanced keyboard shortcuts
4. **Customization**: User-configurable colors and sizes
5. **Loading states**: Skeleton screens for better UX
6. **Virtual scrolling**: For very large result sets

## Notes

- All components use `aqt.qt` imports for Anki compatibility
- Components are designed to work with Anki 23.10+ (PyQt6)
- Fallback imports are provided for testing environments
- All styling uses inline stylesheets for portability
- Signal-based architecture for clean separation of concerns
