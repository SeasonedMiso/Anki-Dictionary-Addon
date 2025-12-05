# Modern UI Design System

This directory contains the foundation for the modern UI redesign of the Anki Dictionary Plugin.

## Files

### `modern-theme.css`
Complete CSS design system including:
- **CSS Variables**: Colors, typography, spacing, shadows, border radius, animations
- **Light/Dark Mode**: Automatic theme detection and smooth transitions
- **Utility Classes**: Flexbox, grid, spacing, text, display, borders, shadows
- **Responsive Design**: Mobile-first breakpoints (640px, 768px, 1024px, 1280px)
- **Accessibility**: Focus indicators, screen reader support, reduced motion
- **Animations**: Fade, slide, scale, spin, pulse effects

### `modern-template.html`
Semantic HTML5 template with:
- **ARIA Landmarks**: Proper semantic structure for screen readers
- **Responsive Meta Tags**: Viewport and theme color configuration
- **Accessibility Features**: Skip links, ARIA labels, live regions
- **Component Structure**: Header, sidebar, main content, modals

### `modern-ui.js`
JavaScript functionality for:
- **Theme Detection**: Automatic detection of Anki's night mode
- **Keyboard Navigation**: Shortcuts for search (Ctrl+F) and settings (Ctrl+,)
- **Modal Management**: Open/close with focus trapping
- **Sidebar Resize**: Drag-to-resize functionality
- **Screen Reader Announcements**: Live region updates

## Design System Overview

### Color Palette

**Light Mode:**
- Primary: `#0ea5e9` (Sky Blue)
- Surface: `#ffffff`, `#f9fafb`, `#f3f4f6`
- Text: `#171717`, `#525252`, `#a3a3a3`

**Dark Mode:**
- Primary: `#38bdf8` (Lighter Sky Blue)
- Surface: `#1a1a1a`, `#222222`, `#2a2a2a`
- Text: `#fafafa`, `#a3a3a3`, `#6b6b6b`

### Typography

- **Font Family**: System font stack (San Francisco, Segoe UI, Roboto)
- **Font Sizes**: 12px to 36px (xs to 4xl)
- **Font Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)
- **Line Heights**: 1.25 (tight), 1.5 (normal), 1.75 (relaxed)

### Spacing

Based on 4px increments:
- `--space-1`: 4px
- `--space-2`: 8px
- `--space-3`: 12px
- `--space-4`: 16px
- `--space-6`: 24px
- `--space-8`: 32px

### Shadows

Six elevation levels from subtle to dramatic:
- `--shadow-sm`: Subtle shadow for cards
- `--shadow-md`: Medium shadow for dropdowns
- `--shadow-lg`: Large shadow for modals
- `--shadow-xl`: Extra large for overlays

### Border Radius

- `--radius-sm`: 4px (buttons, inputs)
- `--radius-md`: 8px (cards)
- `--radius-lg`: 12px (modals)
- `--radius-full`: Fully rounded (pills, avatars)

## Usage

### Including in HTML

```html
<link rel="stylesheet" href="modern-theme.css">
<script src="modern-ui.js"></script>
```

### Using Utility Classes

```html
<!-- Flexbox Layout -->
<div class="flex items-center justify-between gap-4 p-4">
  <span class="text-lg font-semibold">Title</span>
  <button class="px-4 py-2 rounded-lg bg-primary">Action</button>
</div>

<!-- Grid Layout -->
<div class="grid grid-cols-3 gap-4">
  <div class="p-4 rounded-md shadow-sm">Card 1</div>
  <div class="p-4 rounded-md shadow-sm">Card 2</div>
  <div class="p-4 rounded-md shadow-sm">Card 3</div>
</div>

<!-- Responsive Design -->
<div class="flex-col md:flex-row lg:grid-cols-3">
  <!-- Stacks on mobile, row on tablet, grid on desktop -->
</div>
```

### Theme Detection

The JavaScript automatically detects Anki's theme:

```javascript
// Manually trigger theme detection
window.ModernUI.detectAndApplyTheme();

// Announce to screen readers
window.ModernUI.announceToScreenReader('Action completed');
```

## Accessibility Features

### Keyboard Navigation
- **Tab**: Navigate through interactive elements
- **Shift+Tab**: Navigate backwards
- **Enter/Space**: Activate buttons
- **Escape**: Close modals
- **Ctrl+F**: Focus search
- **Ctrl+,**: Open settings

### Screen Reader Support
- Semantic HTML5 elements
- ARIA landmarks and labels
- Live regions for dynamic content
- Skip to main content link

### Visual Accessibility
- WCAG 2.1 AA compliant contrast ratios
- Focus indicators on all interactive elements
- Support for high contrast mode
- Support for reduced motion preferences

## Responsive Breakpoints

- **sm**: 640px (tablets)
- **md**: 768px (small desktops)
- **lg**: 1024px (desktops)
- **xl**: 1280px (large desktops)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Anki's Qt WebEngine (Qt 6.x)

## Performance

- Hardware-accelerated animations using CSS transforms
- Minimal JavaScript for core functionality
- CSS variables for runtime theming
- No external dependencies

## Next Steps

This foundation supports the implementation of:
1. Search components with auto-complete
2. Result cards with hover actions
3. Settings panel with live preview
4. Dictionary sidebar with navigation
5. Tab management system

See the design document (`.kiro/specs/modern-ui-redesign/design.md`) for detailed component specifications.
