# Anki Dictionary - Development Guide

## Quick Start

### Running Tests
```bash
python3 -m pytest tests/ -v
```

### Using New Code

```python
# Configuration
from src.config import ConfigManager
config = ConfigManager(mw.addonManager)

# Database
from src.database import DatabaseConnection, DictionaryRepository
db = DatabaseConnection(db_path)
repo = DictionaryRepository(db)

# Services
from src.services import SearchService, ExportService
search_service = SearchService(repo, addon_path)
export_service = ExportService(mw)

# Utilities
from src.utils import show_info, clean_html, is_mac
```

## Project Structure

```
src/
├── constants.py          # All constants
├── config/              # Configuration management
├── database/            # Database layer
├── core/                # Plugin coordinator
├── services/            # Business logic
└── utils/               # Utilities
```

## Code Style

- **Type hints**: Required for all functions
- **Docstrings**: Google-style for public APIs
- **Naming**: snake_case (functions), PascalCase (classes)
- **Error handling**: Specific exceptions, no bare except

## Testing

All tests run independently without Anki:
- 196 tests, 100% pass rate
- 64% code coverage overall (Phase 3: 81-97%)
- Fast execution (<0.5 seconds)
- Comprehensive mocking of Anki APIs

## Progress

- ✅ Phase 1: Foundation (100%)
- ✅ Phase 2: Database Integration (100%)
- ✅ Phase 3: Main Entry Point & Services (100%)
  - MediaService implementation
  - Plugin coordinator pattern
  - Global state elimination
  - Backward compatibility maintained
- ⏳ Phase 4: UI Refactoring (0% - Spec Complete)
  - Dictionary window refactoring
  - Settings window refactoring
  - Editor/Browser integration
  - Menu and hotkey management

## Resources

- **DEVELOPER_GUIDE.md** - Comprehensive developer guide
- **REFACTORING_PROGRESS.md** - Refactoring progress and metrics
- **src/README.md** - Module documentation
- **tests/** - Test examples
- **.kiro/specs/** - Detailed specifications
