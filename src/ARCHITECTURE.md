# Architecture Overview

## Directory Structure

```
src/
├── ui/                          # OPTIMIZED: Modern UI components
│   ├── __init__.py
│   ├── base_widgets.py          # Base themed widgets
│   ├── dictionary_widgets.py    # Dictionary-specific widgets
│   ├── export_widgets.py        # Export system widgets
│   ├── export_mock_data.py      # Mock data for export UI
│   ├── export_state.py          # Export state management
│   ├── export_history_widget.py # Export history widget
│   ├── styling.py               # Centralized theming system
│   ├── settings_window.py       # Modern settings UI
│   ├── ui_mock.py               # UI mockup/demo
│   └── components/              # Component library (future)
│
├── utils/                       # OPTIMIZED: Utility modules
│   ├── __init__.py
│   └── keyboard.py              # Keyboard shortcuts management
│
├── legacy/                      # LEGACY: Existing services (temporary integration)
│   ├── config/                  # Configuration management
│   ├── core/                    # Core plugin functionality
│   ├── database/                # Database access layer
│   ├── services/                # Business logic services
│   ├── ui/                      # Legacy UI components
│   ├── utils/                   # Legacy utilities
│   └── constants.py             # Constants
│
├── __init__.py                  # Package initialization
└── README.md                    # Architecture notes
```

## Integration Strategy

### OPTIMIZED (src/)
- **ui/**: Modern UI components with clean architecture
  - Centralized theming system
  - Reusable base widgets
  - Feature-specific components (export, dictionary, settings)
  - Mock data for development/testing

- **utils/**: Clean utility functions
  - Keyboard shortcuts management
  - Future: other utilities as needed

### LEGACY (src/legacy/)
- **Temporary integration** with existing services
- Used only when needed by optimized components
- Gradually replaced as we optimize functions
- Clear import paths: `from ..legacy.services import ...`

## Migration Path

As we optimize legacy code:
1. Identify needed function from `src/legacy/`
2. Copy and clean the function
3. Create optimized version in `src/`
4. Update imports to use optimized version
5. Remove from legacy when no longer needed

Example:
```python
# Before: from ..legacy.services import ExportService
# After: from .services import ExportService (when optimized)
```

## Key Principles

- **Minimal tokens**: Only optimize what we need
- **Clear boundaries**: Optimized vs legacy is obvious
- **Incremental**: Function-by-function migration
- **Working system**: Always maintain functionality
