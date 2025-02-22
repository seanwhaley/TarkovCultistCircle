class ThemeManager {
    constructor() {
        // Use the official Material Design theme attribute
        this.init();
    }

    init() {
        // Apply any saved theme preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this.applyThemePreference(savedTheme);
        } else {
            // Use system preference by default
            this.applySystemTheme();
        }

        // Listen for system theme changes
        this.setupMediaQueryListener();
    }

    applyThemePreference(theme) {
        if (theme === 'dark' || theme === 'light') {
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        } else {
            // Reset to system preference
            localStorage.removeItem('theme');
            this.applySystemTheme();
        }

        // Update icon
        const icon = document.getElementById('themeIcon');
        if (icon) {
            icon.textContent = this.getCurrentTheme() === 'dark' ? 'dark_mode' : 'light_mode';
        }
    }

    applySystemTheme() {
        // Remove any manual theme preference
        document.documentElement.removeAttribute('data-theme');
        // System preference will be handled by color-scheme CSS property
    }

    setupMediaQueryListener() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', e => {
            if (!localStorage.getItem('theme')) {
                // Only auto-switch if user hasn't set a preference
                this.applySystemTheme();
            }
        });
    }

    toggleTheme() {
        const currentTheme = this.getCurrentTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.applyThemePreference(newTheme);
    }

    getCurrentTheme() {
        // Check for manual theme preference
        const themeAttr = document.documentElement.getAttribute('data-theme');
        if (themeAttr) {
            return themeAttr;
        }
        // Fall back to system preference
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    resetToSystem() {
        this.applySystemTheme();
    }
}

// Initialize theme manager
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager = new ThemeManager();
});