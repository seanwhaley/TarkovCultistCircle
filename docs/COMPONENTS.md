# Material Design Components

## Core Components

### MDRipple
Adds Material Design ripple effect to elements.

```javascript
// Basic usage
const button = document.querySelector('.btn');
MD.Ripple.attach(button);

// With options
MD.Ripple.attach(button, {
    color: 'rgba(255, 255, 255, 0.2)',
    centered: true
});
```

### MDDialog
Modal dialog component following Material Design specs.

```javascript
const dialog = MD.Dialog.create({
    persistent: true,
    content: `
        <div class="dialog-content">
            <h2>Dialog Title</h2>
            <p>Dialog content goes here</p>
            <div class="dialog-actions">
                <button class="btn btn-text" data-close>Cancel</button>
                <button class="btn btn-primary">Confirm</button>
            </div>
        </div>
    `
});

dialog.show();
```

### MDSnackbar
Toast-style notification component.

```javascript
const snackbar = new MD.Snackbar({
    duration: 4000,
    position: 'bottom-center'
});

snackbar.show('Operation completed', {
    action: {
        text: 'Undo',
        handler: () => handleUndo()
    }
});
```

### MDMenu
Dropdown menu component.

```javascript
const menu = new MD.Menu(menuElement, {
    position: 'bottom-start',
    offset: 8
});

// Trigger button
triggerButton.addEventListener('click', () => {
    menu.open(triggerButton);
});
```

### MDBottomSheet
Bottom sheet component for mobile-friendly dialogs.

```javascript
const sheet = new MD.BottomSheet(sheetElement);

// Show the sheet
sheet.open();

// Handle close
sheet.element.addEventListener('md-close', () => {
    // Handle close event
});
```

## Form Components

### MDTextField
Material Design text input field.

```html
<div class="md-text-field">
    <input type="text" class="md-text-field__input" id="username">
    <label class="md-text-field__label" for="username">Username</label>
    <div class="md-text-field__line"></div>
    <div class="md-text-field__error">Error message</div>
</div>
```

### MDSelect
Material Design select component.

```html
<div class="md-select">
    <select class="md-select__input" id="options">
        <option value="1">Option 1</option>
        <option value="2">Option 2</option>
    </select>
    <label class="md-select__label">Select Option</label>
    <div class="md-select__arrow"></div>
</div>
```

## Feedback Components

### MDProgress
Loading indicators.

```html
<!-- Circular -->
<div class="md-progress-circular">
    <svg class="md-progress-circular__svg">
        <circle class="md-progress-circular__circle"></circle>
    </svg>
</div>

<!-- Linear -->
<div class="md-progress-linear">
    <div class="md-progress-linear__bar"></div>
</div>
```

### MDAlert
Alert messages with Material Design styling.

```html
<div class="md-alert md-alert--success">
    <i class="material-icons md-alert__icon">check_circle</i>
    <div class="md-alert__content">
        Operation successful
    </div>
    <button class="md-alert__close">
        <i class="material-icons">close</i>
    </button>
</div>
```

## Layout Components

### MDCard
Material Design card component.

```html
<div class="md-card">
    <div class="md-card__media">
        <img src="image.jpg" alt="Card image">
    </div>
    <div class="md-card__content">
        <h2 class="md-card__title">Card Title</h2>
        <p class="md-card__text">Card content</p>
    </div>
    <div class="md-card__actions">
        <button class="btn btn-text">Action</button>
    </div>
</div>
```

### MDGrid
Responsive grid system.

```html
<div class="md-grid">
    <div class="md-grid__cell md-grid__cell--span-6">
        <!-- Content -->
    </div>
    <div class="md-grid__cell md-grid__cell--span-6">
        <!-- Content -->
    </div>
</div>
```

## Utility Classes

### Elevation
```html
<div class="elevation-1">Elevation 1dp</div>
<div class="elevation-2">Elevation 2dp</div>
<div class="elevation-4">Elevation 4dp</div>
```

### Typography
```html
<h1 class="md-typography--headline1">Headline 1</h1>
<p class="md-typography--body1">Body text</p>
```

### Spacing
```html
<div class="md-spacing--1">4px spacing</div>
<div class="md-spacing--2">8px spacing</div>
```

## Theme Integration

All components automatically support light and dark themes through CSS variables:

```css
/* Light theme example */
:root {
    --md-primary: #6200ee;
    --md-on-primary: #ffffff;
}

/* Dark theme example */
[data-theme="dark"] {
    --md-primary: #bb86fc;
    --md-on-primary: #000000;
}
```

## Accessibility

All components include proper ARIA attributes and keyboard navigation support. Example:

```html
<button class="md-button"
        role="button"
        aria-label="Close dialog"
        aria-pressed="false">
    <i class="material-icons">close</i>
</button>
```

## Event Handling

Components emit events following a consistent pattern:

```javascript
element.addEventListener('md-open', (e) => {
    console.log('Component opened');
});

element.addEventListener('md-close', (e) => {
    console.log('Component closed');
});

element.addEventListener('md-change', (e) => {
    console.log('Value changed:', e.detail);
});
```

## Component Lifecycle

```javascript
// Initialization
const component = new MD.Component(element, options);

// Cleanup
component.destroy();

// State updates
component.update(newOptions);
```

## Best Practices

1. Always use semantic HTML
2. Include proper ARIA attributes
3. Support keyboard navigation
4. Use correct elevation levels
5. Follow Material Design spacing
6. Implement proper touch targets
7. Support both themes
8. Clean up components properly