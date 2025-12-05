/**
 * Modern UI JavaScript
 * Handles theme detection, initialization, and basic interactions
 */

(function() {
  'use strict';
  
  // ============================================
  // THEME DETECTION & MANAGEMENT
  // ============================================
  
  /**
   * Detects and applies the appropriate theme based on Anki's settings
   */
  function detectAndApplyTheme() {
    const body = document.body;
    const html = document.documentElement;
    
    // Check for Anki's night mode classes
    const isNightMode = body.classList.contains('nightMode') ||
                       body.classList.contains('night-mode') ||
                       body.className.includes('night');
    
    // Apply theme attribute
    if (isNightMode) {
      html.setAttribute('data-theme', 'dark');
      body.classList.add('nightMode');
    } else {
      html.setAttribute('data-theme', 'light');
      body.classList.remove('nightMode');
    }
    
    // Announce theme change to screen readers
    announceToScreenReader(`Theme changed to ${isNightMode ? 'dark' : 'light'} mode`);
  }
  
  /**
   * Observes body class changes to detect theme switches
   */
  function observeThemeChanges() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
          detectAndApplyTheme();
        }
      });
    });
    
    observer.observe(document.body, {
      attributes: true,
      attributeFilter: ['class']
    });
  }
  
  // ============================================
  // ACCESSIBILITY HELPERS
  // ============================================
  
  /**
   * Announces messages to screen readers
   * @param {string} message - The message to announce
   */
  function announceToScreenReader(message) {
    const announcer = document.getElementById('announcements');
    if (announcer) {
      announcer.textContent = message;
      // Clear after announcement
      setTimeout(() => {
        announcer.textContent = '';
      }, 1000);
    }
  }
  
  /**
   * Sets up keyboard navigation
   */
  function setupKeyboardNavigation() {
    document.addEventListener('keydown', (e) => {
      // Escape key closes modals
      if (e.key === 'Escape') {
        closeAllModals();
      }
      
      // Ctrl/Cmd + F focuses search
      if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
          searchInput.focus();
        }
      }
      
      // Ctrl/Cmd + , opens settings
      if ((e.ctrlKey || e.metaKey) && e.key === ',') {
        e.preventDefault();
        openSettings();
      }
    });
  }
  
  /**
   * Traps focus within a modal
   * @param {HTMLElement} modal - The modal element
   */
  function trapFocus(modal) {
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];
    
    modal.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstFocusable) {
            e.preventDefault();
            lastFocusable.focus();
          }
        } else {
          if (document.activeElement === lastFocusable) {
            e.preventDefault();
            firstFocusable.focus();
          }
        }
      }
    });
  }
  
  // ============================================
  // MODAL MANAGEMENT
  // ============================================
  
  /**
   * Opens the settings modal
   */
  function openSettings() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
      modal.classList.remove('hidden');
      modal.setAttribute('aria-hidden', 'false');
      
      // Focus first focusable element
      const firstFocusable = modal.querySelector('button, [href], input, select, textarea');
      if (firstFocusable) {
        firstFocusable.focus();
      }
      
      trapFocus(modal);
      announceToScreenReader('Settings opened');
    }
  }
  
  /**
   * Closes the settings modal
   */
  function closeSettings() {
    const modal = document.getElementById('settings-modal');
    if (modal) {
      modal.classList.add('hidden');
      modal.setAttribute('aria-hidden', 'true');
      announceToScreenReader('Settings closed');
      
      // Return focus to settings button
      const settingsButton = document.getElementById('settings-button');
      if (settingsButton) {
        settingsButton.focus();
      }
    }
  }
  
  /**
   * Closes all open modals
   */
  function closeAllModals() {
    closeSettings();
  }
  
  // ============================================
  // SIDEBAR MANAGEMENT
  // ============================================
  
  /**
   * Sets up sidebar resize functionality
   */
  function setupSidebarResize() {
    const sidebar = document.getElementById('sidebar');
    const resizeHandle = sidebar?.querySelector('.resize-handle');
    
    if (!sidebar || !resizeHandle) return;
    
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;
    
    resizeHandle.addEventListener('mousedown', (e) => {
      isResizing = true;
      startX = e.clientX;
      startWidth = sidebar.offsetWidth;
      
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    });
    
    document.addEventListener('mousemove', (e) => {
      if (!isResizing) return;
      
      const width = startWidth + (e.clientX - startX);
      const minWidth = 150;
      const maxWidth = 500;
      
      if (width >= minWidth && width <= maxWidth) {
        sidebar.style.width = `${width}px`;
      }
    });
    
    document.addEventListener('mouseup', () => {
      if (isResizing) {
        isResizing = false;
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    });
  }
  
  // ============================================
  // INITIALIZATION
  // ============================================
  
  /**
   * Initializes the modern UI
   */
  function init() {
    // Detect and apply initial theme
    detectAndApplyTheme();
    
    // Observe theme changes
    observeThemeChanges();
    
    // Setup keyboard navigation
    setupKeyboardNavigation();
    
    // Setup sidebar resize
    setupSidebarResize();
    
    // Setup event listeners
    const settingsButton = document.getElementById('settings-button');
    if (settingsButton) {
      settingsButton.addEventListener('click', openSettings);
    }
    
    const closeSettingsButton = document.getElementById('close-settings');
    if (closeSettingsButton) {
      closeSettingsButton.addEventListener('click', closeSettings);
    }
    
    // Close modal when clicking backdrop
    const settingsModal = document.getElementById('settings-modal');
    if (settingsModal) {
      settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) {
          closeSettings();
        }
      });
    }
    
    console.log('Modern UI initialized');
  }
  
  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
  // Expose public API for Python bridge
  window.ModernUI = {
    detectAndApplyTheme,
    announceToScreenReader,
    openSettings,
    closeSettings
  };
  
})();
