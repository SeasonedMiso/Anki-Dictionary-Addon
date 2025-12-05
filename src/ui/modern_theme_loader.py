"""
Modern Theme Loader
Provides utilities for loading and integrating the modern UI design system
into the Anki Dictionary Plugin.
"""

from pathlib import Path
from typing import Optional


class ModernThemeLoader:
    """Handles loading and integration of modern UI assets."""
    
    def __init__(self, addon_path: Path):
        """
        Initialize the theme loader.
        
        Args:
            addon_path: Path to the addon directory
        """
        self.addon_path = addon_path
        self.assets_path = addon_path / "src" / "ui" / "assets"
        
    def get_css_path(self) -> Path:
        """Get the path to the modern theme CSS file."""
        return self.assets_path / "modern-theme.css"
    
    def get_template_path(self) -> Path:
        """Get the path to the modern HTML template."""
        return self.assets_path / "modern-template.html"
    
    def get_js_path(self) -> Path:
        """Get the path to the modern UI JavaScript."""
        return self.assets_path / "modern-ui.js"
    
    def load_css(self) -> str:
        """
        Load the modern theme CSS content.
        
        Returns:
            CSS content as string
        """
        css_path = self.get_css_path()
        if css_path.exists():
            return css_path.read_text(encoding='utf-8')
        return ""
    
    def load_template(self) -> str:
        """
        Load the modern HTML template.
        
        Returns:
            HTML template as string
        """
        template_path = self.get_template_path()
        if template_path.exists():
            return template_path.read_text(encoding='utf-8')
        return ""
    
    def load_js(self) -> str:
        """
        Load the modern UI JavaScript.
        
        Returns:
            JavaScript content as string
        """
        js_path = self.get_js_path()
        if js_path.exists():
            return js_path.read_text(encoding='utf-8')
        return ""
    
    def get_inline_css(self) -> str:
        """
        Get CSS as inline style tag for embedding in HTML.
        
        Returns:
            HTML style tag with CSS content
        """
        css_content = self.load_css()
        if css_content:
            return f"<style>\n{css_content}\n</style>"
        return ""
    
    def get_inline_js(self) -> str:
        """
        Get JavaScript as inline script tag for embedding in HTML.
        
        Returns:
            HTML script tag with JavaScript content
        """
        js_content = self.load_js()
        if js_content:
            return f"<script>\n{js_content}\n</script>"
        return ""
    
    def inject_theme_detection(self, html: str, night_mode: bool = False) -> str:
        """
        Inject theme detection into HTML content.
        
        Args:
            html: Original HTML content
            night_mode: Whether night mode is currently active
            
        Returns:
            HTML with theme detection injected
        """
        theme_attr = 'data-theme="dark"' if night_mode else 'data-theme="light"'
        night_class = ' class="nightMode"' if night_mode else ''
        
        # Add theme attribute to html tag
        html = html.replace('<html', f'<html {theme_attr}', 1)
        
        # Add night mode class to body if needed
        if night_mode:
            html = html.replace('<body', f'<body{night_class}', 1)
        
        return html
    
    def create_modern_html(
        self,
        title: str = "Dictionary",
        custom_css: str = "",
        custom_js: str = "",
        night_mode: bool = False
    ) -> str:
        """
        Create a complete modern HTML document.
        
        Args:
            title: Page title
            custom_css: Additional custom CSS
            custom_js: Additional custom JavaScript
            night_mode: Whether to enable night mode
            
        Returns:
            Complete HTML document
        """
        template = self.load_template()
        
        if not template:
            # Fallback minimal template
            template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {css}
    {custom_css}
</head>
<body>
    <div id="app"></div>
    {js}
    {custom_js}
</body>
</html>"""
        
        # Inject theme detection
        template = self.inject_theme_detection(template, night_mode)
        
        # Replace placeholders
        html = template.format(
            title=title,
            css=self.get_inline_css(),
            custom_css=f"<style>{custom_css}</style>" if custom_css else "",
            js=self.get_inline_js(),
            custom_js=f"<script>{custom_js}</script>" if custom_js else ""
        )
        
        return html
    
    def get_css_link_tag(self, relative_path: bool = True) -> str:
        """
        Get a link tag for the CSS file.
        
        Args:
            relative_path: Whether to use relative path
            
        Returns:
            HTML link tag
        """
        if relative_path:
            path = "modern-theme.css"
        else:
            path = str(self.get_css_path())
        
        return f'<link rel="stylesheet" href="{path}">'
    
    def get_js_script_tag(self, relative_path: bool = True) -> str:
        """
        Get a script tag for the JavaScript file.
        
        Args:
            relative_path: Whether to use relative path
            
        Returns:
            HTML script tag
        """
        if relative_path:
            path = "modern-ui.js"
        else:
            path = str(self.get_js_path())
        
        return f'<script src="{path}"></script>'


def get_theme_loader(addon_path: Optional[Path] = None) -> ModernThemeLoader:
    """
    Get a ModernThemeLoader instance.
    
    Args:
        addon_path: Path to addon directory (auto-detected if not provided)
        
    Returns:
        ModernThemeLoader instance
    """
    if addon_path is None:
        # Try to auto-detect addon path
        addon_path = Path(__file__).parent.parent.parent
    
    return ModernThemeLoader(addon_path)
