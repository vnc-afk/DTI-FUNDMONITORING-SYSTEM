/**
 * Theme Toggle System for DTI Fund Monitoring
 * Supports light and dark themes with localStorage persistence
 */

class ThemeManager {
  constructor() {
    this.STORAGE_KEY = 'dti-theme-preference';
    this.DARK_THEME = 'dark';
    this.LIGHT_THEME = 'light';
    this.init();
  }

  /**
   * Initialize theme system
   */
  init() {
    // Get saved preference or system preference
    const savedTheme = this.getSavedTheme();
    const systemTheme = this.getSystemTheme();
    const theme = savedTheme || systemTheme || this.DARK_THEME;
    
    this.setTheme(theme);
    this.setupListeners();
  }

  /**
   * Get saved theme from localStorage
   */
  getSavedTheme() {
    return localStorage.getItem(this.STORAGE_KEY);
  }

  /**
   * Get system theme preference
   */
  getSystemTheme() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      return this.LIGHT_THEME;
    }
    return this.DARK_THEME;
  }

  /**
   * Set theme and update DOM
   */
  setTheme(theme) {
    const html = document.documentElement;
    html.setAttribute('data-theme', theme);
    this.updateToggleButton(theme);
    localStorage.setItem(this.STORAGE_KEY, theme);
  }

  /**
   * Toggle between light and dark themes
   */
  toggle() {
    const current = document.documentElement.getAttribute('data-theme') || this.DARK_THEME;
    const newTheme = current === this.DARK_THEME ? this.LIGHT_THEME : this.DARK_THEME;
    this.setTheme(newTheme);
  }

  /**
   * Update toggle button appearance
   */
  updateToggleButton(theme) {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;

    if (theme === this.LIGHT_THEME) {
      btn.innerHTML = '<i class="bi bi-moon-stars"></i>';
      btn.title = 'Switch to Dark Mode';
    } else {
      btn.innerHTML = '<i class="bi bi-sun"></i>';
      btn.title = 'Switch to Light Mode';
    }
  }

  /**
   * Setup event listeners
   */
  setupListeners() {
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
      btn.addEventListener('click', () => this.toggle());
    }

    // Listen for system theme changes
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (e) => {
        if (!this.getSavedTheme()) {
          this.setTheme(e.matches ? this.LIGHT_THEME : this.DARK_THEME);
        }
      });
    }
  }

  /**
   * Get current theme
   */
  getCurrentTheme() {
    return document.documentElement.getAttribute('data-theme') || this.DARK_THEME;
  }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
  });
} else {
  window.themeManager = new ThemeManager();
}
