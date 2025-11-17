# Anki Dictionary - Refactored Source

Modular, type-safe implementation of the Anki Dictionary addon.

## Structure

```
src/
├── constants.py         # All constants and magic values
├── config/             # Configuration management (ConfigManager, models)
├── database/           # Database layer (connection, repository, models)
├── core/               # Core plugin coordinator
├── services/           # Business logic (search, export, media)
└── utils/              # Utilities (dialogs, text, platform)
```

## Quick Start

### Constants
```python
from src.constants import DICT_GOOGLE_IMAGES, DEFAULT_MAX_SEARCH
```

### Configuration
```python
from src.config import ConfigManager

config = ConfigManager(mw.addonManager)
value = config.get_value('maxSearch', 1000)
```

### Database
```python
from src.database import DatabaseConnection, DictionaryRepository

db = DatabaseConnection(db_path)
repo = DictionaryRepository(db)
languages = repo.get_all_languages()
```

### Services
```python
from src.services import SearchService, ExportService, MediaService

# Search
search_service = SearchService(repo, addon_path)
results = search_service.search("term", dictionary_group)

# Export
export_service = ExportService(mw)
success, error = export_service.create_note(...)

# Media
media_service = MediaService(mw, config_manager, addon_path)
success, filename, error = media_service.download_forvo_audio("word", "Japanese")
```

### Utilities
```python
from src.utils import show_info, clean_html, is_mac

show_info("Message")
cleaned = clean_html(html)
if is_mac():
    # Mac-specific code
```

## Design Principles

- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Components receive dependencies, don't create them
- **Type Safety**: All code includes type hints
- **Error Handling**: Specific exceptions with proper messages
- **Documentation**: Google-style docstrings for all public APIs

## Code Style

- Type hints required for all functions
- Google-style docstrings for public APIs
- snake_case for functions, PascalCase for classes, UPPER_SNAKE_CASE for constants
- Specific exceptions, no bare except
- Max 100 characters per line

## Testing

Run tests independently of Anki:
```bash
python3 -m pytest tests/
```

See `TESTING.md` for comprehensive testing guide.

## Documentation

- **DEVELOPER_GUIDE.md** - Comprehensive developer guide
- **REFACTORING_PROGRESS.md** - Refactoring progress and metrics
- **DEVELOPMENT.md** - Development quick start
- **Module docstrings** - Detailed API documentation

## Contributing

1. Follow the structure - put code in appropriate modules
2. Add type hints to all functions
3. Write docstrings for public APIs
4. Handle errors with specific exceptions
5. Add tests for your code
6. Update documentation

## License

GNU AGPLv3 (same as parent project)
