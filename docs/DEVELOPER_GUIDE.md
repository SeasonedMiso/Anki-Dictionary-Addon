Add to Plugin Coordinator

Update `src/core/plugin.py`:

```python
from ..services import SearchService, ExportService, MediaService, MyService

class AnkiDictionaryPlugin:
    def __init__(self, mw: Any):
        # ... existing initialization ...
        
        # Add new service
        self.my_service = MyService(
            mw,
            self.config_manager,
            self.dictionary_repo,
            self.addon_path
        )
    
    def get_my_service(self) -> MyService:
        """
        Get my service instance.
        
        Returns:
            MyService instance
        """
        return self.my_service
```

### Step 3: Export from Services Module

Update `src/services/__init__.py`:

```python
from .search_service import SearchService
from .export_service import ExportService
from .media_service import MediaService
from .my_service import MyService

__all__ = [
    'SearchService',
    'ExportService',
    'MediaService',
    'MyService',
]
```

### Step 4: Write Tests

Create `tests/test_my_service.py`:

```python
import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path

from src.services.my_service import MyService
from src.config.manager import ConfigManager


@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.col = Mock()
    return mw


@pytest.fixture
def mock_config_manager():
    """Mock configuration manager."""
    return Mock(spec=ConfigManager)


@pytest.fixture
def mock_dictionary_repo():
    """Mock dictionary repository."""
    return Mock()


@pytest.fixture
def my_service(mock_mw, mock_config_manager, mock_dictionary_repo, tmp_path):
    """Create MyService instance for testing."""
    return MyService(
        mock_mw,
        mock_config_manager,
        mock_dictionary_repo,
        tmp_path
    )


def test_do_something_success(my_service):
    """Test successful operation."""
    success, error = my_service.do_something("test")
    assert success is True
    assert error is None


def test_do_something_failure(my_service):
    """Test failure handling."""
    # Test error cases
    pass
```

## Hook Registration Patterns

### Overview

Anki hooks allow the addon to respond to events in Anki's lifecycle. The plugin coordinator centralizes all hook registration.

### Hook Categories

1. **Editor Hooks**: Triggered when editor is shown/modified
2. **Reviewer Hooks**: Triggered during card review
3. **Browser Hooks**: Triggered in the card browser
4. **Profile Hooks**: Triggered on profile load/unload
5. **Card Hooks**: Triggered during card operations

### Registering Hooks

In `src/core/plugin.py`:

```python
def _setup_hooks(self) -> None:
    """Register all Anki hooks."""
    from anki.hooks import addHook
    
    # Editor hooks
    addHook('setupEditorButtons', self._on_setup_editor_buttons)
    addHook('EditorWebView.contextMenuEvent', self._on_editor_context_menu)
    
    # Reviewer hooks
    addHook('showQuestion', self._on_show_question)
    addHook('showAnswer', self._on_show_answer)
    
    # Browser hooks
    addHook('browser.setupMenus', self._on_browser_setup_menus)
    
    # Profile hooks
    addHook('profileLoaded', self._on_profile_loaded)
    addHook('unloadProfile', self._on_unload_profile)
    
    # Card hooks
    addHook('prepareFields', self._on_prepare_fields)
```

### Hook Handler Pattern

```python
def _on_hook_name(self, *args, **kwargs) -> None:
    """
    Handle hook_name hook.
    
    Args:
        *args: Hook-specific arguments
        **kwargs: Hook-specific keyword arguments
    """
    try:
        logger.debug("Hook triggered: hook_name")
        
        # Delegate to appropriate service
        service = self.get_appropriate_service()
        service.handle_hook(*args, **kwargs)
        
    except Exception as e:
        logger.error(f"Error in hook handler: {e}", exc_info=True)
        # Don't let hook errors crash Anki
```

### Common Hook Examples

#### Editor Button Hook

```python
def _on_setup_editor_buttons(self, buttons: list, editor: Any) -> None:
    """Add custom button to editor."""
    button = editor.addButton(
        icon="path/to/icon.png",
        cmd="myCommand",
        func=lambda e: self._handle_button_click(e),
        tip="My Button Tooltip"
    )
    buttons.append(button)
```

#### Context Menu Hook

```python
def _on_editor_context_menu(self, web_view: Any, menu: Any) -> None:
    """Add item to editor context menu."""
    action = menu.addAction("My Action")
    action.triggered.connect(lambda: self._handle_menu_action())
```

#### Profile Loaded Hook

```python
def _on_profile_loaded(self) -> None:
    """Handle profile loaded."""
    # Reload data that depends on profile
    self.search_service.reload_conjugations()
    self.dictionary_repo.refresh_cache()
```

## Configuration Management

### Overview

The `ConfigManager` class provides type-safe access to addon configuration stored in Anki's config system.

### Basic Usage

```python
from src.config import ConfigManager

# Initialize
config_manager = ConfigManager(mw.addonManager)

# Get entire config
config = config_manager.get_config()

# Get specific value with default
max_search = config_manager.get_value('maxSearch', 1000)

# Update config
config_manager.write_config({'maxSearch': 2000})

# Refresh from disk
config_manager.refresh()
```

### Configuration Structure

```python
# config.json
{
    "maxSearch": 1000,
    "dictSearchLimit": 50,
    "searchMode": "exact",
    "deinflect": true,
    "forvoLanguage": "Japanese",
    "googleSearchRegion": "United States",
    "maxImageWidth": 400,
    "maxImageHeight": 400,
    "dictOnStart": false,
    "autoDefinition": false
}
```

### Type-Safe Access

```python
# Add typed methods to ConfigManager
def get_max_search(self) -> int:
    """Get maximum search results."""
    return self.get_value('maxSearch', 1000)

def get_search_mode(self) -> str:
    """Get search mode."""
    return self.get_value('searchMode', 'exact')

def is_deinflect_enabled(self) -> bool:
    """Check if deinflection is enabled."""
    return self.get_value('deinflect', True)
```

### Configuration Change Notifications

```python
class AnkiDictionaryPlugin:
    def refresh_config(self, config: Optional[dict] = None) -> None:
        """Refresh configuration and notify services."""
        if config:
            self.config_manager.write_config(config)
        else:
            self.config_manager.refresh()
        
        # Notify services
        self._notify_config_change()
    
    def _notify_config_change(self) -> None:
        """Notify services of configuration changes."""
        self.search_service.reload_conjugations()
        # Notify other services as needed
```

## Database Access

### Overview

Database access is abstracted through the repository pattern. The `DictionaryRepository` class provides all database operations.

### Basic Usage

```python
from src.database import DatabaseConnection, DictionaryRepository

# Initialize
db_connection = DatabaseConnection(db_path)
repository = DictionaryRepository(db_connection)

# Query operations
languages = repository.get_all_languages()
dictionaries = repository.get_dictionaries_by_language("Japanese")
results = repository.search_term("word", dictionary_ids=[1, 2, 3])

# Close connection
db_connection.close()
```

### Adding New Repository Methods

```python
# In src/database/repository.py

def get_my_data(self, param: str) -> List[MyModel]:
    """
    Get my data from database.
    
    Args:
        param: Query parameter
        
    Returns:
        List of MyModel instances
    """
    query = """
        SELECT column1, column2
        FROM my_table
        WHERE condition = ?
    """
    
    cursor = self.connection.execute(query, (param,))
    rows = cursor.fetchall()
    
    return [
        MyModel(
            field1=row[0],
            field2=row[1]
        )
        for row in rows
    ]
```

### Data Models

```python
# In src/database/models.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class MyModel:
    """Model for my data."""
    field1: str
    field2: int
    field3: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'field1': self.field1,
            'field2': self.field2,
            'field3': self.field3,
        }
```

## Testing Guide

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_config_manager.py   # Config tests
├── test_database_*.py       # Database tests
├── test_*_service.py        # Service tests
└── test_plugin_*.py         # Plugin tests
```

### Writing Tests

#### Basic Test Structure

```python
import pytest
from unittest.mock import Mock, MagicMock, patch

def test_my_function():
    """Test my function."""
    # Arrange
    input_data = "test"
    expected_output = "result"
    
    # Act
    result = my_function(input_data)
    
    # Assert
    assert result == expected_output
```

#### Using Fixtures

```python
@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.col = Mock()
    mw.col.media = Mock()
    mw.col.media.dir = Mock(return_value="/path/to/media")
    return mw

def test_with_fixture(mock_mw):
    """Test using fixture."""
    service = MyService(mock_mw)
    # Test service...
```

#### Mocking External Dependencies

```python
@patch('src.services.my_service.requests.get')
def test_network_call(mock_get):
    """Test function that makes network calls."""
    # Setup mock
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'value'}
    mock_get.return_value = mock_response
    
    # Test
    result = my_function_that_calls_requests()
    
    # Verify
    assert result == expected
    mock_get.assert_called_once()
```

#### Testing Error Handling

```python
def test_error_handling():
    """Test error handling."""
    service = MyService()
    
    # Test with invalid input
    success, error = service.do_something("")
    assert success is False
    assert error is not None
    assert "cannot be empty" in error.lower()
```

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_my_service.py -v

# Run specific test
python3 -m pytest tests/test_my_service.py::test_my_function -v

# Run with coverage
python3 -m pytest tests/ --cov=src --cov-report=html

# Run with output
python3 -m pytest tests/ -v -s
```

## Troubleshooting

### Common Issues

#### Issue: Import Errors

**Problem**: `ModuleNotFoundError` or `ImportError`

**Solution**:
```python
# Use relative imports in addon code
from .src.services import MyService  # Correct
from src.services import MyService   # Wrong in addon context

# Use absolute imports in tests
from src.services import MyService   # Correct in tests
```

#### Issue: Hook Not Firing

**Problem**: Hook handler not being called

**Solution**:
1. Check hook name is correct (case-sensitive)
2. Verify hook is registered in `_setup_hooks()`
3. Ensure `plugin.initialize()` is called
4. Add logging to verify registration:

```python
def _setup_hooks(self) -> None:
    """Register hooks."""
    from anki.hooks import addHook
    
    logger.info("Registering hooks...")
    addHook('myHook', self._on_my_hook)
    logger.info("Hook registered: myHook")
```

#### Issue: Service Not Initialized

**Problem**: `AttributeError: 'NoneType' object has no attribute...`

**Solution**:
1. Ensure service is initialized in plugin `__init__`
2. Check dependencies are passed correctly
3. Verify plugin is attached to `mw`:

```python
# In main.py
plugin = AnkiDictionaryPlugin(mw)
mw.ankiDictPlugin = plugin  # Important!
```

#### Issue: Tests Failing

**Problem**: Tests pass locally but fail in CI or vice versa

**Solution**:
1. Check for hardcoded paths (use `tmp_path` fixture)
2. Verify all external dependencies are mocked
3. Check for timing issues (use deterministic values)
4. Ensure tests don't depend on execution order

```python
# Bad: Hardcoded path
def test_bad():
    path = "/home/user/test"  # Will fail on other systems

# Good: Use fixture
def test_good(tmp_path):
    path = tmp_path / "test"  # Works everywhere
```

#### Issue: Memory Leaks

**Problem**: Memory usage grows over time

**Solution**:
1. Ensure `cleanup()` is called on profile unload
2. Check for circular references
3. Clear caches periodically
4. Use weak references where appropriate

```python
def cleanup(self) -> None:
    """Clean up resources."""
    self.media_service.cleanup_temp_media()
    self.db_connection.close()
    self._cache.clear()  # Clear any caches
```

### Debugging Tips

#### Enable Debug Logging

```python
import logging

# In main.py or plugin.py
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('anki_dictionary_debug.log'),
        logging.StreamHandler()
    ]
)
```

#### Use Anki's Debug Console

```python
# In Anki, press Shift+Ctrl+; to open debug console
from aqt import mw
plugin = mw.ankiDictPlugin

# Inspect plugin state
print(plugin.config_manager.get_config())
print(plugin.search_service)
print(plugin.media_service.get_temp_files_count())
```

#### Add Breakpoints

```python
def my_function():
    import pdb; pdb.set_trace()  # Debugger will stop here
    # Rest of function...
```

## Best Practices

### Code Style

1. **Type Hints**: Always include type hints
```python
def my_function(param: str, count: int = 10) -> tuple[bool, Optional[str]]:
    """Function with type hints."""
    pass
```

2. **Docstrings**: Use Google-style docstrings
```python
def my_function(param: str) -> bool:
    """
    Short description.
    
    Longer description if needed.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
        
    Raises:
        ValueError: When param is invalid
    """
    pass
```

3. **Naming Conventions**:
   - Functions/variables: `snake_case`
   - Classes: `PascalCase`
   - Constants: `UPPER_SNAKE_CASE`
   - Private methods: `_leading_underscore`

4. **Line Length**: Max 100 characters

5. **Imports**: Group and sort imports
```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import pytest
from aqt import mw

# Local
from .src.services import MyService
```

### Error Handling

1. **Use Specific Exceptions**:
```python
# Bad
try:
    do_something()
except:
    pass

# Good
try:
    do_something()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    return False, str(e)
except IOError as e:
    logger.error(f"IO error: {e}")
    return False, "File operation failed"
```

2. **Return Result Types**:
```python
def my_function() -> tuple[bool, Optional[str]]:
    """Return (success, error_message) tuple."""
    try:
        # Do work
        return True, None
    except Exception as e:
        return False, str(e)
```

3. **Log Errors**:
```python
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

### Performance

1. **Lazy Initialization**: Initialize expensive resources only when needed
2. **Caching**: Cache expensive computations
3. **Batch Operations**: Process multiple items together
4. **Resource Cleanup**: Always clean up resources

```python
class MyService:
    def __init__(self):
        self._expensive_resource = None
        self._cache = {}
    
    @property
    def expensive_resource(self):
        """Lazy initialization."""
        if self._expensive_resource is None:
            self._expensive_resource = create_expensive_resource()
        return self._expensive_resource
    
    def get_data(self, key: str):
        """Cached data access."""
        if key not in self._cache:
            self._cache[key] = fetch_data(key)
        return self._cache[key]
```

### Security

1. **Validate Input**: Always validate user input
2. **Sanitize Filenames**: Clean filenames before file operations
3. **Use HTTPS**: Prefer HTTPS for network requests
4. **Timeout Network Requests**: Always set timeouts

```python
def download_file(url: str) -> bytes:
    """Download file safely."""
    # Validate URL
    if not url.startswith('https://'):
        raise ValueError("Only HTTPS URLs allowed")
    
    # Set timeout
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    return response.content
```

## Additional Resources

- **Anki Add-on Development**: https://addon-docs.ankiweb.net/
- **Python Type Hints**: https://docs.python.org/3/library/typing.html
- **pytest Documentation**: https://docs.pytest.org/
- **Project Repository**: [Link to repository]

## Contributing

1. Follow the established patterns and conventions
2. Write tests for new functionality
3. Update documentation
4. Run tests before submitting
5. Keep commits focused and atomic

## License

GNU AGPLv3 (same as parent project)

---

**Last Updated**: January 2025
**Version**: 3.0 (Phase 3 Complete)


## UI Component Patterns

### Overview

Phase 4 introduced a complete UI layer refactoring that separates UI components from business logic. All UI components now use the service layer via dependency injection, making them testable and maintainable.

### UI Architecture

```
src/ui/
├── __init__.py              # UI module exports
├── base.py                  # Base UI classes and utilities
├── dictionary_window.py     # Main dictionary search window
├── settings_window.py       # Settings configuration dialog
├── dictionary_manager.py    # Dictionary management interface
├── card_exporter.py         # Bulk card export dialog
├── editor_integration.py    # Editor hooks and integration
├── browser_integration.py   # Browser hooks and integration
└── menu_manager.py          # Menu and hotkey management
```

### Creating UI Components

#### Basic UI Component Pattern

```python
from typing import Any, Optional
from pathlib import Path
from aqt.qt import QDialog, QVBoxLayout, QPushButton
from ..services import MyService
from ..config import ConfigManager

class MyWindow(QDialog):
    """My custom window."""
    
    def __init__(
        self,
        mw: Any,
        my_service: MyService,
        config_manager: ConfigManager,
        addon_path: Path
    ):
        """
        Initialize window with dependencies.
        
        Args:
            mw: Anki main window
            my_service: Service for business logic
            config_manager: Configuration manager
            addon_path: Path to addon directory
        """
        super().__init__(mw)
        self.mw = mw
        self.my_service = my_service
        self.config_manager = config_manager
        self.addon_path = addon_path
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("My Window")
        layout = QVBoxLayout()
        
        # Add widgets
        button = QPushButton("Do Something")
        button.clicked.connect(self._on_button_click)
        layout.addWidget(button)
        
        self.setLayout(layout)
    
    def _on_button_click(self) -> None:
        """Handle button click."""
        try:
            # Use service for business logic
            success, error = self.my_service.do_something()
            
            if success:
                self._show_success("Operation completed!")
            else:
                self._show_error(f"Operation failed: {error}")
                
        except Exception as e:
            logger.error(f"Button click error: {e}", exc_info=True)
            self._show_error("An unexpected error occurred")
    
    def _show_success(self, message: str) -> None:
        """Show success message."""
        from aqt.utils import showInfo
        showInfo(message, parent=self)
    
    def _show_error(self, message: str) -> None:
        """Show error message."""
        from aqt.utils import showWarning
        showWarning(message, parent=self)
```

### Accessing UI Components

UI components are accessed through the Plugin Coordinator using lazy initialization:

```python
# In main.py or other code
from aqt import mw

# Get plugin instance
plugin = mw.ankiDictPlugin

# Access UI components (created on first access)
dict_window = plugin.get_dictionary_window()
settings_window = plugin.get_settings_window()
dict_manager = plugin.get_dictionary_manager()

# Show windows
dict_window.show_window()
settings_window.exec()
```

### UI Component Lifecycle

```python
class AnkiDictionaryPlugin:
    """Plugin coordinator manages UI lifecycle."""
    
    def __init__(self, mw: Any):
        """Initialize plugin."""
        # UI components start as None (lazy initialization)
        self._dictionary_window: Optional[DictionaryWindow] = None
        self._settings_window: Optional[SettingsWindow] = None
    
    def get_dictionary_window(self) -> DictionaryWindow:
        """Get or create dictionary window."""
        if self._dictionary_window is None:
            self._dictionary_window = DictionaryWindow(
                self.mw,
                self.search_service,
                self.export_service,
                self.media_service,
                self.config_manager,
                self.addon_path
            )
        return self._dictionary_window
    
    def cleanup(self) -> None:
        """Clean up UI resources."""
        if self._dictionary_window:
            self._dictionary_window.close()
            self._dictionary_window = None
```

### Integration Modules

Integration modules handle Anki hooks and connect UI to the rest of the addon:

```python
class EditorIntegration:
    """Manages editor integration."""
    
    def __init__(self, plugin: 'AnkiDictionaryPlugin'):
        """
        Initialize editor integration.
        
        Args:
            plugin: Plugin coordinator instance
        """
        self.plugin = plugin
    
    def setup_editor_hooks(self) -> None:
        """Register editor hooks."""
        from anki.hooks import addHook
        
        addHook('setupEditorButtons', self._on_setup_buttons)
        addHook('EditorWebView.contextMenuEvent', self._on_context_menu)
    
    def _on_setup_buttons(self, buttons: list, editor: Any) -> None:
        """Add buttons to editor."""
        button = editor.addButton(
            icon=str(self.plugin.addon_path / "icons" / "search.png"),
            cmd="ankiDictSearch",
            func=lambda e: self._search_selected(e),
            tip="Search in Dictionary (Ctrl+Shift+D)"
        )
        buttons.append(button)
    
    def _search_selected(self, editor: Any) -> None:
        """Search for selected text."""
        selected = editor.web.selectedText()
        if selected:
            dict_window = self.plugin.get_dictionary_window()
            dict_window.show_window([selected])
```

### Menu and Hotkey Management

```python
class MenuManager:
    """Manages menus and hotkeys."""
    
    def __init__(self, mw: Any, plugin: 'AnkiDictionaryPlugin'):
        """Initialize menu manager."""
        self.mw = mw
        self.plugin = plugin
    
    def setup_menu(self) -> None:
        """Create addon menu."""
        from aqt.qt import QMenu, QAction
        
        # Create menu
        menu = QMenu("Dictionary", self.mw)
        self.mw.form.menubar.addMenu(menu)
        
        # Add actions
        open_dict = QAction("Open Dictionary", self.mw)
        open_dict.setShortcut(self.get_platform_shortcut("Ctrl+Shift+D"))
        open_dict.triggered.connect(self.open_dictionary)
        menu.addAction(open_dict)
        
        open_settings = QAction("Settings", self.mw)
        open_settings.triggered.connect(self.open_settings)
        menu.addAction(open_settings)
    
    def get_platform_shortcut(self, shortcut: str) -> str:
        """Get platform-specific shortcut."""
        import sys
        if sys.platform == "darwin":
            # Mac: Cmd instead of Ctrl
            return shortcut.replace("Ctrl", "Cmd")
        return shortcut
    
    def open_dictionary(self) -> None:
        """Open dictionary window."""
        dict_window = self.plugin.get_dictionary_window()
        dict_window.show_window()
    
    def open_settings(self) -> None:
        """Open settings window."""
        settings_window = self.plugin.get_settings_window()
        settings_window.exec()
```

### Error Handling in UI

```python
class MyWindow(QDialog):
    """Window with proper error handling."""
    
    def _handle_operation(self) -> None:
        """Handle operation with error feedback."""
        try:
            # Attempt operation
            success, error = self.my_service.do_something()
            
            if not success:
                # Expected error - show user-friendly message
                logger.warning(f"Operation failed: {error}")
                self._show_error(f"Could not complete operation: {error}")
                return
            
            # Success
            self._show_success("Operation completed successfully!")
            
        except ValueError as e:
            # Validation error
            logger.error(f"Validation error: {e}")
            self._show_error(f"Invalid input: {e}")
            
        except IOError as e:
            # File/network error
            logger.error(f"IO error: {e}", exc_info=True)
            self._show_error("Could not access file or network resource")
            
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error: {e}", exc_info=True)
            self._show_error("An unexpected error occurred. Check logs for details.")
```

### Progress Feedback

```python
from aqt.qt import QProgressDialog

class CardExporter(QDialog):
    """Exporter with progress feedback."""
    
    def export_cards(self, note_ids: list[int]) -> None:
        """Export cards with progress bar."""
        # Create progress dialog
        progress = QProgressDialog(
            "Exporting cards...",
            "Cancel",
            0,
            len(note_ids),
            self
        )
        progress.setWindowModality(Qt.WindowModal)
        
        try:
            for i, note_id in enumerate(note_ids):
                # Check for cancellation
                if progress.wasCanceled():
                    logger.info("Export cancelled by user")
                    break
                
                # Update progress
                progress.setValue(i)
                progress.setLabelText(f"Exporting card {i+1} of {len(note_ids)}...")
                
                # Do work
                self._export_single_card(note_id)
            
            progress.setValue(len(note_ids))
            self._show_success(f"Exported {len(note_ids)} cards")
            
        except Exception as e:
            logger.error(f"Export error: {e}", exc_info=True)
            self._show_error(f"Export failed: {e}")
        finally:
            progress.close()
```

## UI Testing Patterns

### Overview

UI components are tested using comprehensive mocking of Qt and Anki APIs. Tests verify that UI components correctly call service methods and handle errors.

### Basic UI Test Structure

```python
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from src.ui.my_window import MyWindow
from src.services.my_service import MyService
from src.config.manager import ConfigManager


@pytest.fixture
def mock_mw():
    """Mock Anki main window."""
    mw = Mock()
    mw.col = Mock()
    return mw


@pytest.fixture
def mock_services():
    """Mock all services."""
    return {
        'my_service': Mock(spec=MyService),
        'config': Mock(spec=ConfigManager)
    }


@pytest.fixture
def my_window(mock_mw, mock_services, tmp_path):
    """Create window for testing."""
    with patch('src.ui.my_window.QDialog.__init__', return_value=None):
        window = MyWindow(
            mock_mw,
            mock_services['my_service'],
            mock_services['config'],
            tmp_path
        )
        return window


def test_button_click_calls_service(my_window, mock_services):
    """Test that button click calls service."""
    # Setup
    mock_services['my_service'].do_something.return_value = (True, None)
    
    # Execute
    my_window._on_button_click()
    
    # Verify
    mock_services['my_service'].do_something.assert_called_once()


def test_error_handling(my_window, mock_services):
    """Test error handling."""
    # Setup - service returns error
    mock_services['my_service'].do_something.return_value = (False, "Test error")
    
    # Execute
    with patch.object(my_window, '_show_error') as mock_show_error:
        my_window._on_button_click()
    
    # Verify error was shown
    mock_show_error.assert_called_once()
    assert "Test error" in mock_show_error.call_args[0][0]
```

### Testing Qt Widgets

```python
@patch('src.ui.my_window.QPushButton')
@patch('src.ui.my_window.QVBoxLayout')
def test_ui_setup(mock_layout, mock_button, my_window):
    """Test UI setup creates widgets."""
    # Execute
    my_window._setup_ui()
    
    # Verify widgets created
    mock_button.assert_called()
    mock_layout.assert_called()
```

### Testing Dialogs

```python
def test_dialog_exec(mock_mw, mock_services, tmp_path):
    """Test dialog execution."""
    with patch('src.ui.my_window.QDialog.exec', return_value=1):
        window = MyWindow(mock_mw, mock_services['my_service'], 
                         mock_services['config'], tmp_path)
        result = window.exec()
        assert result == 1
```

### Testing Integration Modules

```python
def test_editor_integration_setup(mock_plugin):
    """Test editor integration setup."""
    integration = EditorIntegration(mock_plugin)
    
    with patch('src.ui.editor_integration.addHook') as mock_add_hook:
        integration.setup_editor_hooks()
        
        # Verify hooks registered
        assert mock_add_hook.call_count == 2
        mock_add_hook.assert_any_call('setupEditorButtons', integration._on_setup_buttons)
```

### Running UI Tests

```bash
# Run all UI tests
python3 -m pytest tests/test_*_window.py tests/test_*_integration.py -v

# Run specific UI test
python3 -m pytest tests/test_dictionary_window.py::test_search_calls_service -v

# Run with coverage
python3 -m pytest tests/test_*_window.py --cov=src/ui --cov-report=html
```

## UI Component Usage Examples

### Example 1: Opening Dictionary Window

```python
# From menu action
def open_dictionary():
    """Open dictionary window."""
    from aqt import mw
    plugin = mw.ankiDictPlugin
    dict_window = plugin.get_dictionary_window()
    dict_window.show_window()

# With search terms
def search_terms(terms: list[str]):
    """Search for specific terms."""
    from aqt import mw
    plugin = mw.ankiDictPlugin
    dict_window = plugin.get_dictionary_window()
    dict_window.show_window(terms)
```

### Example 2: Opening Settings

```python
def open_settings():
    """Open settings dialog."""
    from aqt import mw
    plugin = mw.ankiDictPlugin
    settings_window = plugin.get_settings_window()
    
    # Modal dialog
    if settings_window.exec():
        # Settings were saved
        plugin.refresh_config()
```

### Example 3: Bulk Export

```python
def bulk_export_from_browser(browser):
    """Export definitions for selected cards."""
    from aqt import mw
    plugin = mw.ankiDictPlugin
    
    # Get selected note IDs
    note_ids = browser.selectedNotes()
    
    if not note_ids:
        showInfo("No cards selected")
        return
    
    # Create and show exporter
    exporter = CardExporter(
        mw,
        plugin.export_service,
        plugin.search_service,
        browser
    )
    exporter.export_selected_cards(note_ids)
```

### Example 4: Editor Integration

```python
# Automatically set up by EditorIntegration
# Users can:
# 1. Select text in editor
# 2. Click dictionary button or use Ctrl+Shift+D
# 3. Dictionary window opens with selected text

# Implementation in EditorIntegration:
def _search_selected(self, editor: Any) -> None:
    """Search for selected text."""
    selected = editor.web.selectedText()
    if selected:
        dict_window = self.plugin.get_dictionary_window()
        dict_window.show_window([selected])
```

---

**Last Updated**: January 2025
**Version**: 4.0 (Phase 4 Complete)


---

## Anki API Compatibility

### Supported Anki Versions

**Minimum Version**: Anki 2.1.50+
**Tested Version**: Anki 2.1.66
**Target Version**: Anki 2.1.x (latest stable)

The addon uses only stable, long-standing Anki APIs that have been present since Anki 2.1.50. All APIs are validated against the actual Anki source code.

### Core APIs Used

#### anki.hooks - Hook System

The addon uses Anki's hook system for lifecycle management and integration:

```python
from anki.hooks import addHook

# Profile lifecycle
addHook('profileLoaded', on_profile_loaded)
addHook('unloadProfile', on_unload_profile)
```

**API Reference**:
- `addHook(hook: str, func: Callable) -> None` - Register a hook function
- `runHook(hook: str, *args) -> None` - Execute all functions on a hook
- `wrap(old, new, pos='after') -> Callable` - Monkey patch a function

**Source**: `ankiSourceCode/anki-main/pylib/anki/hooks.py`

**Stability**: ✅ Stable since Anki 2.1.0

#### anki.utils - Platform Detection

The addon uses platform detection for OS-specific behavior:

```python
from anki.utils import is_mac, is_win, is_lin

# These are module-level boolean variables, NOT functions
if is_mac:
    shortcut = '⌘W'
elif is_win:
    shortcut = 'Ctrl+W'
```

**Important**: `is_mac`, `is_win`, and `is_lin` are **boolean variables**, not functions!

```python
# ✅ Correct usage
if is_mac:
    do_something()

# ❌ Incorrect usage
if is_mac():  # This will fail!
    do_something()
```

**API Reference**:
- `is_mac: bool` - True if running on macOS (sys.platform == "darwin")
- `is_win: bool` - True if running on Windows (sys.platform == "win32")
- `is_lin: bool` - True if running on Linux (not is_mac and not is_win)

**Source**: `ankiSourceCode/anki-main/pylib/anki/utils.py:245-248`

**Stability**: ✅ Stable since Anki 2.1.0

#### aqt.utils - GUI Utilities

The addon uses Anki's GUI utility functions for dialogs and notifications:

```python
from aqt.utils import showInfo, showWarning, tooltip, askUser

# Show information dialog
showInfo(
    "Dictionary installed successfully",
    parent=None,
    help=None,
    type="info",
    title="Anki Dictionary"
)

# Show warning dialog
showWarning("Please select a dictionary", parent=self)

# Show tooltip
tooltip("Search completed", period=2000)

# Ask yes/no question
if askUser("Delete this dictionary?", parent=self):
    delete_dictionary()
```

**API Reference**:
- `showInfo(text, parent=None, help=None, type="info", title="Anki", textFormat=None, customBtns=None) -> int`
- `showWarning(text, parent=None, help=None, title="Anki", textFormat=None) -> int`
- `tooltip(msg, period=3000, parent=None, x_offset=0, y_offset=100) -> None`
- `askUser(text, parent=None, help=None, defaultno=False, msgfunc=None, title="Anki") -> bool`
- `openLink(link: str | QUrl) -> None`

**Source**: `ankiSourceCode/anki-main/qt/aqt/utils.py`

**Stability**: ✅ Stable since Anki 2.1.0

#### aqt.qt - Qt Widgets

The addon uses standard PyQt6/PyQt5 widgets through Anki's Qt compatibility layer:

```python
from aqt.qt import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QShortcut,
    QKeySequence, Qt
)

class MyWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        button = QPushButton("Click Me")
        button.clicked.connect(self.on_click)
        layout.addWidget(button)
        self.setLayout(layout)
```

**Stability**: ✅ Stable - Standard Qt APIs

#### aqt.mw - Main Window

The addon accesses Anki's main window for integration:

```python
from aqt import mw

# Access collection
collection = mw.col

# Access profile manager
profile_manager = mw.pm

# Add menu items
mw.form.menuTools.addAction(action)
```

**Stability**: ✅ Stable since Anki 2.1.0

### API Validation

All Anki API usage has been validated against the actual Anki source code in `ankiSourceCode/anki-main/`. See the validation report for details:

- **Validation Report**: `.kiro/specs/anki-dict-phase5-cleanup/TASK_18_VALIDATION_REPORT.md`
- **Mock Validation**: `.kiro/specs/anki-dict-phase5-cleanup/MOCK_VALIDATION_FINDINGS.md`
- **API Reference**: `.kiro/specs/anki-dict-phase5-cleanup/ANKI_SOURCE_REFERENCE.md`

### Version-Specific Behavior

**None identified** - The addon uses only stable APIs with no version-specific workarounds.

### Breaking Changes Risk

**Low** - All APIs used are core Anki functionality that has remained stable for years:

- Hook system: Unchanged since Anki 2.1.0
- Platform detection: Unchanged since Anki 2.1.0
- GUI utilities: Unchanged since Anki 2.1.0
- Qt widgets: Standard PyQt APIs

### Testing Against Anki APIs

Our test mocks accurately reflect the actual Anki APIs:

```python
# tests/mocks.py
fake_anki.utils.is_mac = sys.platform == "darwin"  # Boolean, not function
fake_anki.utils.is_win = sys.platform == "win32"   # Boolean, not function
fake_anki.utils.is_lin = not fake_anki.utils.is_mac and not fake_anki.utils.is_win

fake_anki.hooks.addHook = Mock()
fake_anki.hooks.wrap = Mock(side_effect=lambda func, wrapper: wrapper)
fake_anki.hooks.runHook = Mock()

fake_aqt.utils.showInfo = Mock()
fake_aqt.utils.showWarning = Mock()
fake_aqt.utils.tooltip = Mock()
```

### Compatibility Checklist

When updating the addon or testing with new Anki versions:

- [ ] Verify hook names haven't changed
- [ ] Verify dialog function signatures match
- [ ] Verify platform detection still uses boolean variables
- [ ] Test addon loads without errors
- [ ] Test all UI components work correctly
- [ ] Run full test suite
- [ ] Check Anki changelog for API changes

### Future Compatibility

To maintain compatibility with future Anki versions:

1. **Monitor Anki Releases**: Watch for API changes in release notes
2. **Use Stable APIs**: Avoid undocumented or internal APIs
3. **Test Early**: Test with Anki beta versions when available
4. **Update Mocks**: Keep test mocks in sync with Anki changes
5. **Document Changes**: Update this guide when APIs change

### Getting Help

If you encounter Anki API issues:

1. Check the Anki source code: `ankiSourceCode/anki-main/`
2. Review our validation reports in `.kiro/specs/anki-dict-phase5-cleanup/`
3. Consult Anki's official documentation: https://addon-docs.ankiweb.net/
4. Ask on Anki forums: https://forums.ankiweb.net/

### References

- **Anki Source Code**: `ankiSourceCode/anki-main/`
- **Anki Add-on Docs**: https://addon-docs.ankiweb.net/
- **PyQt6 Documentation**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **Our API Validation**: `.kiro/specs/anki-dict-phase5-cleanup/TASK_18_VALIDATION_REPORT.md`

