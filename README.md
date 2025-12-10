<h2 align="center">Anki Dictionary Addon (Successor to Migaku Dictionary Addon)</h2>

<p align="center">
<!-- <a title="Rate on AnkiWeb" href="https://ankiweb.net/shared/info/1655992655"><img ankiDict="https://glutanimate.com/logos/ankiweb-rate.svg"></a> -->
<a title="License: GNU AGPLv3" href="https://github.com/migaku-official/Migaku-Dictionary-Addon/blob/master/README.md><img  src="https://img.shields.io/badge/license-GNU AGPLv3-green.svg"></a>
<br>

> A successor to the Migaku Dictionary Addon, this project aims to port the original addon to newer Anki versions, fix bugs, and introduce improvements. Lookup word definitions, frequency, audio, and export that information to Anki cards in real-time.

### Table of Contents

- [Installation](#installation)
- [Features](#features)
- [Development](#development)
- [Contributing](#contributing)
- [License and Credits](#license-and-credits)

### Installation

1. Install the latest supported version of Anki.
2. Download the latest version of the addon from this repository, and unzip it to your anki2 addons folder.

### Features

- Real-time dictionary lookup with multiple dictionary support
- Audio pronunciation from Forvo
- Image search via Google Images
- Bulk definition export
- Customizable card templates
- Theme support
- Frequency information
- Sentence mining

### TODO

**Mock to Functional Interface**
- [ ] Connect search bar to real dictionary lookup
- [ ] Implement filter bar functionality (dictionary groups, search modes, conjugation)
- [ ] Add real data loading and caching
- [ ] Connect action buttons (audio, images, clipboard, export)
- [ ] Implement collapsible state persistence
- [ ] Add keyboard shortcuts and navigation
- [ ] Error handling and loading states

**Settings UI Development**
- [ ] Create settings interface mockup
- [ ] Implement real-time theme editing with live preview
- [ ] Add theme customization (colors, fonts, spacing)
- [ ] Dictionary source management interface
- [ ] Settings export/import functionality

**Codebase Optimization**
- [ ] Create new optimized src/ folder structure
- [ ] Migrate working mock as foundation
- [ ] Copy only essential code from current codebase
- [ ] Eliminate technical debt and legacy code
- [ ] Ensure modular, testable, maintainable architecture

### To Fix

- **Dropdown Theme Issue**: QComboBox dropdown menus show white background instead of dark theme. Qt/PyQt theming limitation where popup widgets inherit system styling.

### Planned Features

**Modern Workflow Integration**
- **Clipboard Monitor**: Auto-detect and process texthooker output
- **Screenshot OCR**: Extract text from game screenshots (PS Vita, PC games)
- **Yomitan Bridge**: API integration for enhanced card creation
- **Batch Processing**: Handle multiple lookups efficiently

**Media-Rich Card Creation**
- **Auto Audio Capture**: Record pronunciation during lookup
- **Context Screenshots**: Attach source images to cards
- **Smart Templates**: Context-aware card generation
- **Netflix Integration**: Subtitle + audio extraction for streaming content

**Deep Customization & Theming**
- **Card Template Sync**: Dictionary theme automatically mirrors to Anki card templates
- **Global Anki Theming**: Optional integration with Anki's global theme system
- **Texture Pack System**: Replace icons, images, and UI elements with custom assets
- **Progressive Complexity**: Simple defaults with advanced customization for power users
- **Theme Sharing**: Export/import complete visual themes and asset packs

**Advanced Features**
- **Radical Search**: Search for kanji by radical components
- **Draw Search**: Handwriting recognition for kanji lookup
- **Voice Search**: Speech-to-text for audio-based dictionary queries

**Search History & Navigation**
- **Search History**: Storage and retrieval system for previous lookups
- **Tabbed Interface**: Multiple word searches in separate tabs
- **History Dropdown/Sidebar**: Quick access to recent searches
- **Tab Management**: Open, close, switch between tabs with keyboard shortcuts
- **Session Persistence**: Maintain search history across application restarts

**Enhanced Frequency System**
- **Contextual Frequency Labels**: Group frequency lists by domain (fiction books, non-fiction, TV, YouTube, etc.)
- **Smart Frequency Descriptions**: Context-aware labels like "Common book word", "Common speaking word", "Technical term"
- **Domain-Specific Rankings**: Show frequency within specific contexts (e.g., "Rare in general, but common in anime")
- **Frequency Visualization**: Charts and graphs showing word usage across different domains

**Keyboard Shortcuts Integration**
- **Font Size Controls**: Ctrl/Cmd +/-/0 for text scaling across all components
- **Navigation Shortcuts**: Ctrl+F focus search, Tab navigation, Enter to search
- **Dictionary Actions**: Ctrl+A audio, Ctrl+C copy, Ctrl+E export shortcuts
- **Cross-Platform Support**: Consistent shortcuts across macOS/Windows/Linux

**For Developers:**
- Run tests: `python3 -m pytest tests/ -v`

### Contributing

Contributions are welcome! Please review the [contribution guidelines](.githubONTRIBUTING.md) on how to:

- Report issues
- File pull requests
- Support the project as a non-developer

### License and Credits

*Anki Dictionary Addon* is a successor to the *Migaku Dictionary Addon*.

This project is free and open-source software. The add-on code that runs within Anki is released under the GNU AGPLv3 license, extended by a number of additional terms. For more information please see the [LICENSE](https://github.com/migaku-official/Migaku-Dictionary-Addon/blob/master/README.md) file that accompanied this program.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY.
----
