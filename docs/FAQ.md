# Frequently Asked Questions (FAQ)

## General

### What is Tarkov Cultist Circle?

Tarkov Cultist Circle is a Flask-based web application that uses a Neo4j database for data storage. The application is containerized using Docker and Docker Compose, and it includes various features such as authentication, API endpoints, and item management.

### How do I set up the application?

Please refer to the [Installation Instructions](INSTALLATION.md) for detailed setup instructions.

## Troubleshooting

### I encountered an error during installation. What should I do?

If you encounter any issues during installation, please refer to the [Installation Instructions](INSTALLATION.md) and ensure that all prerequisites are met. If the issue persists, please open an issue on GitHub.

### How do I run the tests?

To run the tests, use the following command:

```bash
python -m unittest discover tests
```

### How do I ingest data from the Tarkov API?

To ingest data from the Tarkov API, use the following command:

```bash
flask ingest-data
```

## Contribution

### How can I contribute to the project?

Please refer to the [Contributing Guidelines](CONTRIBUTING.md) for information on how to contribute to the project.

## Material Design Implementation

### Q: How do I switch between light and dark themes?
**A:** There are three ways to switch themes:
1. Click the theme toggle button in the navigation bar
2. Use the `ThemeManager`:
```javascript
window.themeManager.toggleTheme();
```
3. Let the system theme preference control it by not setting a manual preference

### Q: Why aren't my Material components working?
**A:** Common issues and solutions:
1. Check that Material Icons are properly loaded
2. Verify the component is properly initialized
3. Check console for JavaScript errors
4. Ensure CSS variables are properly set
5. Verify the correct bundle is included

### Q: How do I create a custom Material component?
**A:** Follow these steps:
1. Create a new class extending from our base component system
2. Use CSS custom properties for theming
3. Implement proper ARIA attributes
4. Add to the MD namespace
See MATERIAL_DESIGN.md for detailed examples.

### Q: How do I handle mobile-specific Material Design features?
**A:** Our Material implementation automatically handles:
- Touch targets (minimum 48x48px)
- Proper spacing on mobile
- Touch-friendly interactions
- Responsive breakpoints
Use our responsive mixins and Material Design layout guidelines.

## Database and API

### Q: How do I connect to the Neo4j database?
**A:** Update your .env file with:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### Q: How do I query the Tarkov.dev API?
**A:** Use our GraphQL service with proper types. See GRAPHQL_QUERIES.md for examples.

## Development

### Q: How do I run the application in development mode?
**A:** Follow these steps:
1. `docker-compose up -d`
2. Access http://localhost:5000
3. Enable dev tools for Material component inspection

### Q: How do I contribute new features?
**A:** See CONTRIBUTING.md for detailed guidelines, including Material Design requirements.

## Troubleshooting

### Q: Material Design components are not properly themed
**A:** Verify:
1. Theme CSS variables are properly loaded
2. No CSS specificity conflicts
3. Component initialization order
4. Browser compatibility

### Q: Performance issues with Material components
**A:** Try these solutions:
1. Use lazy loading for non-critical components
2. Implement proper garbage collection
3. Optimize ripple effects
4. Use Hardware acceleration where appropriate

### Q: Accessibility issues with Material components
**A:** Check:
1. ARIA labels are properly set
2. Color contrast meets WCAG guidelines
3. Keyboard navigation works
4. Focus management is correct

## Common Tasks

### Q: How do I create a new Material dialog?
**A:** Use our dialog system:
```javascript
const dialog = MD.Dialog.create({
    persistent: true,
    content: 'Dialog content'
});
dialog.show();
```

### Q: How do I show a snackbar message?
**A:** Use our snackbar system:
```javascript
MD.Snackbar.show('Message', {
    action: {
        text: 'Undo',
        handler: () => {}
    }
});
```

### Q: How do I handle form validation with Material Design?
**A:** Use our form components:
```javascript
const field = document.querySelector('.md-text-field');
field.setError('Invalid input');
// or
field.setValid('Looks good!');
```

## Support

### Q: Where can I find more documentation?
**A:** Check:
1. MATERIAL_DESIGN.md for component documentation
2. API_REFERENCE.md for API details
3. Component playground at /components
4. Our GitHub repository

### Q: How do I report bugs?
**A:** Create an issue on GitHub with:
1. Steps to reproduce
2. Expected vs actual behavior
3. Browser/device information
4. Theme being used
5. Console errors if any
