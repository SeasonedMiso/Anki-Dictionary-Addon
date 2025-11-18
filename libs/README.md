# Third-Party Libraries

This directory contains bundled third-party Python libraries used by the Anki Dictionary addon.

## Why Bundle Libraries?

Anki's Python environment doesn't include all the libraries we need, so we bundle them with the addon. The `libs/` directory is added to `sys.path` during addon initialization, allowing these libraries to be imported normally.

## Included Libraries

### BeautifulSoup4 (bs4/)
- **Version**: 4.x
- **Purpose**: HTML parsing for dictionary content
- **License**: MIT
- **URL**: https://www.crummy.com/software/BeautifulSoup/

### Requests (requests/)
- **Version**: 2.x
- **Purpose**: HTTP library for web requests
- **License**: Apache 2.0
- **URL**: https://requests.readthedocs.io/

### urllib3 (urllib3/)
- **Version**: 1.x
- **Purpose**: HTTP client (dependency of requests)
- **License**: MIT
- **URL**: https://urllib3.readthedocs.io/

### Tornado (tornado/)
- **Version**: 6.x
- **Purpose**: Asynchronous networking library
- **License**: Apache 2.0
- **URL**: https://www.tornadoweb.org/

### pynput (pynput/)
- **Version**: 1.x
- **Purpose**: Keyboard and mouse input monitoring
- **License**: LGPL
- **URL**: https://pynput.readthedocs.io/

### PyObjC Core (pyobjc-core/)
- **Version**: 9.x
- **Purpose**: Python-Objective-C bridge for macOS integration
- **License**: MIT
- **URL**: https://pyobjc.readthedocs.io/

### HIServices (HIServices/)
- **Version**: 9.x
- **Purpose**: macOS Human Interface Services (part of PyObjC)
- **License**: MIT

### keyboardMac (keyboardMac/)
- **Version**: Custom
- **Purpose**: macOS keyboard handling utilities
- **License**: Custom

### Six (six.py)
- **Version**: 1.x
- **Purpose**: Python 2/3 compatibility utilities
- **License**: MIT
- **URL**: https://six.readthedocs.io/

### Pyperclip (Pyperclip.py)
- **Version**: 1.x
- **Purpose**: Cross-platform clipboard operations
- **License**: BSD
- **URL**: https://github.com/asweigart/pyperclip

## Usage

Libraries are automatically available after addon initialization. Import them normally:

```python
from bs4 import BeautifulSoup
import requests
from tornado import web
```

## Updating Libraries

When updating bundled libraries:

1. Download the new version
2. Replace the old directory/file
3. Update version information in this README
4. Test thoroughly with the addon
5. Update any compatibility code if needed

## Notes

- These libraries are bundled to ensure consistent behavior across different Anki installations
- Library versions are frozen to avoid unexpected breaking changes
- Some libraries may have been modified for compatibility with Anki's environment
- Always test addon functionality after updating any library
