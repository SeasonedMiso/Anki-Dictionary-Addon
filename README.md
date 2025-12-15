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

**Current (Legacy)**
- Real-time dictionary lookup with multiple dictionary support
- Audio pronunciation from Forvo
- Image search via Google Images
- Bulk definition export
- Customizable card templates
- Theme support
- Frequency information
- Sentence mining

**In Development (Modern UI)**
- Modern, responsive dictionary interface with theming system
- Improved export workflow with queue management and preview
- Enhanced template editor with live preview
- Better search and filtering capabilities
- Streamlined settings management

### Development Roadmap

**Current Phase: Export UI System (PR #1)**
- [x] Export queue management with drag-and-drop
- [ ] Card template editor with live preview
- [x] Export preview and confirmation workflow
- [x] Export history tracking and management
- [x] Modern replacement for legacy cardExporter.py (1100+ lines)

**Planned Features**
- [ ] Enhanced search history & navigation with breadcrumbs and recent searches
- [ ] Contextual frequency system with domain-specific rankings (fiction, non-fiction, TV, YouTube)
- [ ] Keyboard shortcuts integration for power users
- [ ] Settings UI with real-time theme editing and live preview
- [ ] Dictionary source management interface
- [ ] Performance optimizations and caching improvements

**Pragmatic Architecture Strategy**
- **OPTIMIZED**: New modern UI components built from scratch with clean patterns
- **INTEGRATION**: Use existing services temporarily to avoid massive rewrites
- **CLEAR BOUNDARIES**: Distinguish optimized code (new UI) from legacy integration
- **INCREMENTAL**: Replace legacy services over time as optimization opportunities arise

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
- Demo export UI: `python3 demo_export_ui.py`
- Demo dictionary UI: `python3 -c "from src.ui.ui_mock import show_ui_mock; import sys; from aqt.qt import QApplication; app=QApplication(sys.argv); show_ui_mock(); sys.exit(app.exec())"`

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
