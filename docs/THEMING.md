# Material Design Theming System

## Overview
Our Material Design implementation uses a dynamic theming system based on CSS custom properties, allowing for runtime theme switching and customization.

## Theme Structure

### Core Color System
```css
:root {
    /* Primary colors */
    --md-primary: #6200ee;
    --md-primary-variant: #3700b3;
    --md-secondary: #03dac6;
    --md-secondary-variant: #018786;

    /* Surface colors */
    --md-surface: #ffffff;
    --md-background: #ffffff;
    --md-error: #b00020;

    /* On colors */
    --md-on-primary: #ffffff;
    --md-on-secondary: #000000;
    --md-on-background: #000000;
    --md-on-surface: #000000;
    --md-on-error: #ffffff;

    /* Elevation shadows */
    --md-elevation-1: 0 2px 1px -1px rgba(0,0,0,0.2),
                     0 1px 1px 0 rgba(0,0,0,0.14),
                     0 1px 3px 0 rgba(0,0,0,0.12);
    --md-elevation-2: 0 3px 1px -2px rgba(0,0,0,0.2),
                     0 2px 2px 0 rgba(0,0,0,0.14),
                     0 1px 5px 0 rgba(0,0,0,0.12);
    --md-elevation-4: 0 2px 4px -1px rgba(0,0,0,0.2),
                     0 4px 5px 0 rgba(0,0,0,0.14),
                     0 1px 10px 0 rgba(0,0,0,0.12);
}
```

### Dark Theme
```css
[data-theme="dark"] {
    --md-primary: #bb86fc;
    --md-primary-variant: #3700b3;
    --md-secondary: #03dac6;
    --md-secondary-variant: #03dac6;
    --md-background: #121212;
    --md-surface: #1e1e1e;
    --md-error: #cf6679;
    --md-on-primary: #000000;
    --md-on-secondary: #000000;
    --md-on-background: #ffffff;
    --md-on-surface: #ffffff;
    --md-on-error: #000000;
    
    /* Dark theme elevation */
    --md-elevation-1: 0 2px 1px -1px rgba(255,255,255,0.2),
                     0 1px 1px 0 rgba(255,255,255,0.14),
                     0 1px 3px 0 rgba(255,255,255,0.12);
    --md-elevation-2: 0 3px 1px -2px rgba(255,255,255,0.2),
                     0 2px 2px 0 rgba(255,255,255,0.14),
                     0 1px 5px 0 rgba(255,255,255,0.12);
    --md-elevation-4: 0 2px 4px -1px rgba(255,255,255,0.2),
                     0 4px 5px 0 rgba(255,255,255,0.14),
                     0 1px 10px 0 rgba(255,255,255,0.12);
}
```

## Using Themes

### Component Example
```css
.md-card {
    background-color: var(--md-surface);
    color: var(--md-on-surface);
    box-shadow: var(--md-elevation-1);
}

.md-card:hover {
    box-shadow: var(--md-elevation-2);
}

.md-card__title {
    color: var(--md-primary);
}
```

### Theme Management

#### JavaScript API
```javascript
// Switch theme
window.themeManager.toggleTheme();

// Set specific theme
window.themeManager.applyTheme('dark');

// Get current theme
const currentTheme = window.themeManager.theme;

// Listen for theme changes
window.addEventListener('themechange', (e) => {
    console.log('Theme changed to:', e.detail.theme);
});
```

#### System Theme Detection
```javascript
// Check if system prefers dark mode
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

// Listen for system theme changes
prefersDark.addEventListener('change', (e) => {
    const newTheme = e.matches ? 'dark' : 'light';
    window.themeManager.applyTheme(newTheme);
});
```

## Custom Theming

### Creating Custom Themes
```css
/* Custom theme */
[data-theme="custom"] {
    --md-primary: #00796b;
    --md-primary-variant: #004d40;
    --md-secondary: #ffd700;
    --md-secondary-variant: #ffb300;
    /* ... other theme variables ... */
}
```

### Component-Specific Theming
```css
/* Custom themed component */
.custom-component {
    --component-specific-color: var(--md-primary);
    --component-specific-bg: var(--md-surface);
    
    background-color: var(--component-specific-bg);
    color: var(--component-specific-color);
}
```

## Theme Transitions

### Global Transitions
```css
body {
    transition: background-color 0.3s ease,
                color 0.3s ease;
}
```

### Component Transitions
```css
.md-card {
    transition: background-color 0.3s ease,
                box-shadow 0.3s ease,
                color 0.3s ease;
}
```

## Accessibility

### Color Contrast
All theme colors should meet WCAG 2.1 contrast requirements:
- Normal text: 4.5:1
- Large text: 3:1
- UI components: 3:1

### Focus Indicators
```css
:focus-visible {
    outline: 2px solid var(--md-primary);
    outline-offset: 2px;
}
```

## Best Practices

1. Always use CSS variables for theming
2. Implement proper transitions
3. Support both light and dark themes
4. Test color contrast
5. Use semantic color names
6. Provide focus indicators
7. Support system preferences
8. Handle theme transitions smoothly

## Theme Testing

### Color Contrast Testing
```javascript
function testContrast(color1, color2) {
    // Get relative luminance
    const getLuminance = (r, g, b) => {
        const [rs, gs, bs] = [r, g, b].map(c => {
            c = c / 255;
            return c <= 0.03928
                ? c / 12.92
                : Math.pow((c + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
    };
    
    // Calculate contrast ratio
    const l1 = getLuminance(...color1);
    const l2 = getLuminance(...color2);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    
    return ratio;
}
```

### Theme Switch Testing
```javascript
async function testThemeSwitch() {
    const themes = ['light', 'dark', 'custom'];
    for (const theme of themes) {
        window.themeManager.applyTheme(theme);
        // Allow time for transition
        await new Promise(r => setTimeout(r, 300));
        // Verify theme application
        console.log(`Testing ${theme} theme...`);
    }
}
```

## Performance Considerations

1. Use CSS transforms for animations
2. Batch theme changes
3. Use will-change for heavy animations
4. Minimize paint operations
5. Cache computed styles when possible