# Modern UI Integration Guide

This guide explains how to integrate the modern UI design system into the existing Anki Dictionary Plugin codebase.

## Quick Start

### 1. Using the Theme Loader (Recommended)

```python
from src.ui.modern_theme_loader import get_theme_loader

# Initialize the theme loader
theme_loader = get_theme_loader()

# Load CSS content
css_content = theme_loader.load_css()

# Load HTML template
html_template = theme_loader.load_template()

# Create a complete modern HTML document
html = theme_loader.create_modern_html(
    title="Dictionary",
    night_mode=True,  # Enable dark mode
    custom_css="/* Your custom CSS */",
    custom_js="// Your custom JavaScript"
)
```

### 2. Direct File Inclusion

```python
from pathlib import Path

# Get paths
assets_path = Path(__file__).parent / "assets"
css_path = assets_path / "modern-theme.css"
html_path = assets_path / "modern-template.html"
js_path = assets_path / "modern-ui.js"

# Read files
css_content = css_path.read_text(encoding='utf-8')
html_content = html_path.read_text(encoding='utf-8')
js_content = js_path.read_text(encoding='utf-8')
```

### 3. Inline Embedding

```python
from src.ui.modern_theme_loader import get_theme_loader

theme_loader = get_theme_loader()

# Get inline CSS and JS
inline_css = theme_loader.get_inline_css()
inline_js = theme_loader.get_inline_js()

# Embed in your HTML
html = f"""
<!DOCTYPE html>
<html>
<head>
    {inline_css}
</head>
<body>
    <div id="app">Your content here</div>
    {inline_js}
</body>
</html>
"""
```

## Integration with Existing Components

### Dictionary Window

Update `src/ui/dictionary_window.py` to use the modern theme:

```python
from src.ui.modern_theme_loader import get_theme_loader

class DictionaryWindow:
    def __init__(self, mw, addon_path):
        self.mw = mw
        self.addon_path = addon_path
        self.theme_loader = get_theme_loader(addon_path)
        
    def setup_webview(self):
        """Setup the web view with modern theme."""
        # Detect night mode
        night_mode = self.mw.pm.night_mode() if hasattr(self.mw.pm, 'night_mode') else False
        
        # Load modern HTML
        html = self.theme_loader.create_modern_html(
            title="Dictionary",
            night_mode=night_mode
        )
        
        # Set HTML content
        self.web_view.setHtml(html)
```

### Theme Detection

The modern UI automatically detects Anki's theme:

```python
def detect_anki_theme(mw) -> bool:
    """
    Detect if Anki is in night mode.
    
    Args:
        mw: Anki main window
        
    Returns:
        True if night mode is active
    """
    # Try multiple methods for compatibility
    if hasattr(mw.pm, 'night_mode'):
        return mw.pm.night_mode()
    
    # Fallback: check body class
    if hasattr(mw, 'web'):
        body_class = mw.web.eval("document.body.className")
        return 'nightMode' in body_class or 'night-mode' in body_class
    
    return False
```

### Dynamic Theme Switching

```python
def update_theme(web_view, night_mode: bool):
    """
    Update the theme dynamically.
    
    Args:
        web_view: Qt web view instance
        night_mode: Whether to enable night mode
    """
    theme = 'dark' if night_mode else 'light'
    
    # Update via JavaScript
    js_code = f"""
    document.documentElement.setAttribute('data-theme', '{theme}');
    if ({str(night_mode).lower()}) {{
        document.body.classList.add('nightMode');
    }} else {{
        document.body.classList.remove('nightMode');
    }}
    window.ModernUI.detectAndApplyTheme();
    """
    
    web_view.eval(js_code)
```

## Migrating Existing HTML

### Step 1: Add Modern Theme CSS

Replace or supplement existing CSS:

```html
<!-- Old -->
<link rel="stylesheet" href="old-styles.css">

<!-- New -->
<link rel="stylesheet" href="modern-theme.css">
<link rel="stylesheet" href="old-styles.css"> <!-- Keep for compatibility -->
```

### Step 2: Update HTML Structure

Add semantic HTML5 and ARIA landmarks:

```html
<!-- Old -->
<div id="content">
    <div id="search">...</div>
    <div id="results">...</div>
</div>

<!-- New -->
<main id="main-content" role="main">
    <section role="search" aria-label="Dictionary search">
        <input type="search" aria-label="Search dictionary">
    </section>
    <section role="region" aria-label="Search results">
        <div id="results" role="list">...</div>
    </section>
</main>
```

### Step 3: Apply Utility Classes

Replace inline styles with utility classes:

```html
<!-- Old -->
<div style="display: flex; justify-content: space-between; padding: 16px;">
    <span>Left</span>
    <span>Right</span>
</div>

<!-- New -->
<div class="flex justify-between p-4">
    <span>Left</span>
    <span>Right</span>
</div>
```

### Step 4: Add Theme Detection

```html
<script>
// Initialize modern UI
if (window.ModernUI) {
    window.ModernUI.detectAndApplyTheme();
}

// Listen for theme changes from Anki
document.addEventListener('themeChanged', (e) => {
    if (window.ModernUI) {
        window.ModernUI.detectAndApplyTheme();
    }
});
</script>
```

## CSS Variable Usage

### Accessing Variables in Custom CSS

```css
/* Use design system variables */
.my-custom-component {
    background-color: var(--surface-primary);
    color: var(--text-primary);
    padding: var(--space-4);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
}

/* Responsive with breakpoints */
@media (min-width: 768px) {
    .my-custom-component {
        padding: var(--space-6);
    }
}
```

### Overriding Variables

```css
/* Override specific variables */
:root {
    --primary-500: #your-custom-color;
    --radius-md: 16px;
}

/* Dark mode overrides */
:root[data-theme="dark"] {
    --surface-primary: #your-dark-bg;
}
```

## JavaScript API

### Available Methods

```javascript
// Theme detection
window.ModernUI.detectAndApplyTheme();

// Screen reader announcements
window.ModernUI.announceToScreenReader('Action completed');

// Modal management
window.ModernUI.openSettings();
window.ModernUI.closeSettings();
```

### Custom Event Handling

```javascript
// Listen for theme changes
document.addEventListener('themeChanged', (event) => {
    console.log('Theme changed:', event.detail);
});

// Trigger custom events
document.dispatchEvent(new CustomEvent('themeChanged', {
    detail: { theme: 'dark' }
}));
```

## Testing

### Visual Testing

1. Open `test-design-system.html` in a browser
2. Toggle between light and dark modes
3. Verify all components render correctly
4. Test responsive breakpoints by resizing window

### Integration Testing

```python
import pytest
from src.ui.modern_theme_loader import get_theme_loader

def test_theme_loader():
    """Test theme loader functionality."""
    loader = get_theme_loader()
    
    # Test CSS loading
    css = loader.load_css()
    assert len(css) > 0
    assert ':root' in css
    
    # Test template loading
    html = loader.load_template()
    assert '<!DOCTYPE html>' in html
    assert 'modern-theme.css' in html
    
    # Test theme detection injection
    html_with_theme = loader.inject_theme_detection(html, night_mode=True)
    assert 'data-theme="dark"' in html_with_theme
    assert 'nightMode' in html_with_theme
```

## Troubleshooting

### Theme Not Applying

1. Check if CSS file is loaded: View page source and verify `<link>` or `<style>` tag
2. Check browser console for errors
3. Verify `data-theme` attribute on `<html>` element
4. Check if Anki's night mode class is present on `<body>`

### JavaScript Not Working

1. Verify `modern-ui.js` is loaded
2. Check browser console for errors
3. Ensure `window.ModernUI` object exists
4. Check if DOM is fully loaded before initialization

### Styles Conflicting

1. Use more specific selectors
2. Use `!important` sparingly for overrides
3. Check CSS specificity and cascade order
4. Use browser DevTools to inspect computed styles

## Best Practices

1. **Always use CSS variables** instead of hardcoded values
2. **Use utility classes** for common patterns
3. **Maintain semantic HTML** with proper ARIA labels
4. **Test in both light and dark modes**
5. **Verify keyboard navigation** works correctly
6. **Test with screen readers** when possible
7. **Keep custom CSS minimal** and use the design system

## Next Steps

After integrating the foundation:

1. Implement search components (Task 2)
2. Create result card components (Task 2)
3. Build settings panel (Task 3)
4. Add accessibility features (Task 4)
5. Optimize performance (Task 5)

See the tasks document for detailed implementation steps.
