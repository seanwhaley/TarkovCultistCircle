# Contributing Guidelines

## Issue Creation

### Choose the Right Template
We provide three issue templates to ensure consistent tracking:

1. **Feature Request Template**
   - For new features and enhancements
   - Includes business context and technical requirements
   - Requires clear acceptance criteria
   - Uses the 'enhancement' label

2. **Bug Report Template**
   - For reporting bugs and issues
   - Requires reproduction steps
   - Includes technical details and logs
   - Uses the 'bug' label

3. **Technical Task Template**
   - For refactoring and technical improvements
   - Includes migration and rollback plans
   - Requires validation criteria
   - Uses the 'technical-debt' label

### Issue Guidelines

1. **Title Format**
   - Features: [FEATURE] Brief description
   - Bugs: [BUG] Brief description
   - Technical: [TECH] Brief description

2. **Labels**
   - enhancement: New features
   - bug: Issues and problems
   - technical-debt: Code improvements
   - documentation: Doc updates
   - security: Security-related
   - performance: Performance issues

3. **Priority Levels**
   - p0: Critical/Blocking
   - p1: High priority
   - p2: Medium priority
   - p3: Low priority

## How to Contribute

1. **Fork the Repository**: Fork the repository to your GitHub account.

2. **Clone the Repository**: Clone the repository to your local machine.

   ```bash
   git clone https://github.com/yourusername/TarkovCultistCircle.git
   cd TarkovCultistCircle
   ```

3. **Create a Branch**: Create a new branch for your feature or bug fix.

   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Changes**: Make your changes in the codebase.

5. **Run Tests**: Run the tests to ensure your changes do not break existing functionality.

   ```bash
   python -m unittest discover tests
   ```

6. **Commit Changes**: Commit your changes with a descriptive commit message.

   ```bash
   git add .
   git commit -m "Add feature/your-feature-name"
   ```

7. **Push Changes**: Push your changes to your forked repository.

   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**: Create a pull request to merge your changes into the main repository.

## Development Workflow

1. **Branch Naming**
   - feature/*: New features
   - fix/*: Bug fixes
   - tech/*: Technical improvements
   - docs/*: Documentation updates

2. **Commit Messages**
   Format: `type(scope): description`
   
   Types:
   - feat: New feature
   - fix: Bug fix
   - refactor: Code improvement
   - docs: Documentation
   - test: Test updates
   - chore: Maintenance

3. **Pull Requests**
   - Link related issues
   - Include test coverage
   - Update documentation
   - Add to relevant project board

## Code Review

1. **Review Process**: All pull requests must be reviewed by at least one other developer before being merged.
2. **Feedback**: Provide constructive feedback and suggestions for improvement.
3. **Approval**: Once the pull request is approved, it can be merged into the main branch.

## Coding Standards

1. **PEP 8**: Follow the PEP 8 style guide for Python code.
2. **Docstrings**: Use docstrings to document all functions and classes.
3. **Comments**: Add comments to explain complex logic and important sections of the code.

## Best Practices

1. **Modularity**: Keep the code modular by using blueprints and separating concerns.
2. **Configuration**: Use environment variables for configuration and keep sensitive information out of the codebase.
3. **Logging**: Use logging to capture important events and errors.
4. **Testing**: Write unit tests for all functions and classes to ensure code quality and reliability.

## Material Design Implementation

### Component Development

1. All new components should follow Material Design 3 specifications
2. Use the provided MD namespace for consistency:

   ```javascript
   // Good
   MD.Ripple.attach(element);

   // Bad
   new MaterialRipple(element);
   ```

3. Follow the existing component structure:

   ```javascript
   class MDComponent {
       constructor(options = {}) {
           this.options = {
               defaultOption: 'value',
               ...options
           };
           this.init();
       }

       init() {
           // Component initialization
       }
   }
   ```

### Theming

1. Always use CSS custom properties for theming:

   ```css
   /* Good */
   .component {
       color: var(--md-on-surface);
       background: var(--md-surface);
   }

   /* Bad */
   .component {
       color: #000000;
       background: #ffffff;
   }
   ```

2. Support both light and dark themes
3. Test components in both themes before submitting

### CSS Guidelines

1. Use BEM naming convention:

   ```css
   .block {}
   .block__element {}
   .block--modifier {}
   ```

2. Follow Material Design elevation levels:

   ```css
   .card {
       box-shadow: var(--md-elevation-1);
   }

   .card:hover {
       box-shadow: var(--md-elevation-2);
   }
   ```

3. Use Material Design spacing units (4px grid)

### JavaScript Conventions

1. Use ES6+ features
2. Document component APIs using JSDoc
3. Include TypeScript definitions where possible
4. Follow the event naming convention:

   ```javascript
   // Good
   element.dispatchEvent(new CustomEvent('md-open'));

   // Bad
   element.dispatchEvent(new CustomEvent('opened'));
   ```

### Accessibility

1. Include ARIA attributes:

   ```html
   <!-- Good -->
   <button class="md-button" aria-label="Close dialog">
       <i class="material-icons">close</i>
   </button>

   <!-- Bad -->
   <button class="md-button">
       <i class="material-icons">close</i>
   </button>
   ```

2. Support keyboard navigation
3. Maintain proper focus management
4. Test with screen readers

## Pull Request Process

1. Ensure components follow Material Design guidelines
2. Include theme support
3. Add necessary documentation
4. Update component playground if needed
5. Add tests for new components

## Development Setup

1. Install dependencies:

   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. Start development server:

   ```bash
   docker-compose up -d
   ```

3. Access component playground:

   ```
   http://localhost:5000/components
   ```

## Testing

1. Test components in both themes
2. Verify responsive behavior
3. Check accessibility compliance
4. Run performance tests

## Documentation

1. **Update Related Docs**
   - Technical changes: Update relevant .md files
   - API changes: Update API_REFERENCE.md
   - DB changes: Update DB_STRUCTURE.md

2. **Changelog Updates**
   - Add entries under [Unreleased]
   - Follow Keep a Changelog format
   - Include breaking changes

## Review Process

1. **Code Review Requirements**
   - Pass all tests
   - Meet code coverage
   - Follow style guide
   - Update documentation

2. **Testing Requirements**
   - Unit tests for new code
   - Integration tests if needed
   - Performance benchmarks
   - Security validation

## Code Review Process

### Material Design Checklist

- [ ] Follows Material Design 3 specifications
- [ ] Supports light and dark themes
- [ ] Uses correct elevation levels
- [ ] Implements proper transitions
- [ ] Handles touch and mouse inputs
- [ ] Includes proper ARIA attributes
- [ ] Documentation is complete
- [ ] Tests are included

### Performance Checklist

- [ ] Optimizes bundle size
- [ ] Implements lazy loading where appropriate
- [ ] Uses efficient animations
- [ ] Handles memory management

## Questions?

For questions about:

- Material Design implementation: Check the component documentation
- Theming: Refer to the theming guide
- Component API: See the API documentation
- Accessibility: Review the accessibility guidelines
