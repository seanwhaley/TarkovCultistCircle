# Material Design Implementation Guide

## Overview
This application implements Material Design 3 principles with a custom component library focused on performance and maintainability. The implementation includes a dynamic theming system, custom components, and comprehensive accessibility support.

## Theme System

### CSS Custom Properties
Our theme system uses CSS custom properties for dynamic theming:

```css
:root {
    /* Primary colors */
    --md-primary: #6200ee;
    --md-primary-variant: #3700b3;
    --md-secondary: #03dac6;
    
    /* Surface colors */
    --md-surface: #ffffff;
    --md-on-surface: #000000;
    
    /* States */
    --md-hover: rgba(0, 0, 0, 0.04);
    --md-focus: rgba(0, 0, 0, 0.12);
}
```

### Theme Switching
Themes can be switched using the ThemeManager:

```javascript
// Switch theme
window.themeManager.toggleTheme();

// Get current theme
const currentTheme = window.themeManager.theme;
```

## Component Library

### Available Components

1. MDRipple
```javascript
// Add ripple effect to button
MD.Ripple.attach(buttonElement);
```

2. MDMenu
```javascript
// Create menu
const menu = new MD.Menu(menuElement, {
    position: 'bottom-start',
    offset: 8
});

// Show menu
menu.open(targetElement);
```

3. MDBottomSheet
```javascript
// Create bottom sheet
const sheet = new MD.BottomSheet(sheetElement);

// Show sheet
sheet.open();
```

4. MDSnackbar
```javascript
// Show message
const snackbar = new MD.Snackbar();
snackbar.show('Action completed', {
    action: {
        text: 'Undo',
        handler: () => handleUndo()
    }
});
```

5. MDDialog
```javascript
// Create dialog
const dialog = MD.Dialog.create({
    persistent: true
});

// Show dialog
dialog.show();
```

## Form Components

### Text Fields
```html
<div class="md-text-field">
    <input type="text" class="md-text-field__input">
    <label class="md-text-field__label">Label</label>
    <div class="md-text-field__line"></div>
</div>
```

### Select Fields
```html
<div class="md-select">
    <select class="md-select__input">
        <option>Option 1</option>
    </select>
    <div class="md-select__arrow"></div>
</div>
```

## Layout System

### Elevation
```css
/* Available elevation levels */
.elevation-1 { box-shadow: var(--md-elevation-1); }
.elevation-2 { box-shadow: var(--md-elevation-2); }
.elevation-4 { box-shadow: var(--md-elevation-4); }
```

### Grid System
```html
<div class="md-grid">
    <div class="md-grid__cell md-grid__cell--span-6"></div>
    <div class="md-grid__cell md-grid__cell--span-6"></div>
</div>
```

## Animation System

### Transitions
```css
/* Standard transition */
.md-transition {
    transition: all 0.2s ease;
}

/* Material easing */
.md-transition--standard {
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
```

## Event Handling

### Component Events
```javascript
element.addEventListener('md-open', (e) => {
    console.log('Component opened');
});

element.addEventListener('md-close', (e) => {
    console.log('Component closed');
});
```

## Accessibility Features

### ARIA Attributes
```html
<button class="md-button" 
        aria-label="Close dialog"
        aria-expanded="false">
    <i class="material-icons">close</i>
</button>
```

### Keyboard Navigation
- Tab: Navigate between focusable elements
- Space/Enter: Activate buttons and controls
- Escape: Close modals and menus
- Arrow keys: Navigate within components

## Best Practices

1. Always use CSS custom properties for theming
2. Implement proper ARIA attributes
3. Test components in both themes
4. Ensure keyboard navigation works
5. Use proper elevation levels
6. Follow Material Design spacing guidelines
7. Implement proper touch targets
8. Use Material Icons consistently

## Common Issues & Solutions

### Theme Not Applying
```javascript
// Force theme refresh
window.themeManager.applyTheme(window.themeManager.theme);
```

### Component Initialization
```javascript
// Ensure proper initialization
document.addEventListener('DOMContentLoaded', () => {
    MD.Ripple.attach(document.querySelectorAll('.md-button'));
});
```

### Performance Optimization
```javascript
// Lazy load components
const dialog = await import('./components/dialog.js');
const instance = dialog.create();
```

## Testing Components

### Unit Tests
```javascript
// Example component test
describe('MDRipple', () => {
    it('should create ripple effect', () => {
        const button = document.createElement('button');
        MD.Ripple.attach(button);
        button.click();
        expect(button.querySelector('.md-ripple')).toBeTruthy();
    });
});
```

### Visual Tests
Use the component playground at `/components` to visually test components in different states and themes.

## Additional Resources

- [Material Design Guidelines](https://m3.material.io/)
- [Material Icons](https://fonts.google.com/icons)
- [Material Design Color Tool](https://material.io/resources/color/)