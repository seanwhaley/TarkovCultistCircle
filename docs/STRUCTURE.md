# Project Structure Guidelines

## Requirements Documentation

### Business Requirements
All business requirements should be documented using this format:

```markdown
### Requirement Title

**Business Need:**
[Clear description of the business need]

**User Story:**
As a [user type],
I want [goal/desire]
So that [benefit]

**Acceptance Criteria:**
- [ ] Measurable outcome 1
- [ ] Measurable outcome 2

**Dependencies:**
- List of dependencies
```

### Technical Requirements
Technical requirements should follow this format:

```markdown
### Feature Name

**Technical Scope:**
[Brief technical description]

**Implementation Details:**
- Required technologies
- Integration points
- Performance requirements

**Architecture Impact:**
- Affected components
- Database changes
- API modifications

**Testing Requirements:**
- Unit test coverage
- Integration test scenarios
- Performance benchmarks
```

## Design Decisions

Document design decisions using this format:

```markdown
### Decision Title

**Context:**
[Situation requiring decision]

**Options Considered:**
1. Option A
   - Pros: ...
   - Cons: ...
2. Option B
   - Pros: ...
   - Cons: ...

**Decision:**
[Chosen option with rationale]

**Consequences:**
- Positive impacts
- Negative impacts
```

## Documentation Guidelines

1. Keep documentation close to code
2. Update docs with code changes
3. Use standardized templates
4. Include code examples
5. Maintain changelog
6. Document breaking changes
7. Regular documentation review

## Project Organization

```
src/               # Source code
├── application/   # Core application
├── blueprints/   # Flask blueprints
├── core/         # Core functionality
├── models/       # Data models
└── services/     # Business logic

docs/             # Documentation
├── technical/    # Technical docs
├── business/     # Business docs
└── design/       # Design decisions

tests/            # Test suite
├── unit/        # Unit tests
├── integration/ # Integration tests
└── e2e/         # End-to-end tests
```

# Application Structure

## Project Layout

### Source Code (`src/`)

- `__init__.py`: Factory function to initialize the Flask app, register blueprints, and configure logging
- `config.py`: Configuration classes for different environments

### Blueprints (`src/blueprints/`)

- `auth.py`: Authentication routes and logic
- `main.py`: Main application routes
- `api.py`: API routes and logic
- `items.py`: Item-related routes

### Views (`src/views/`)
- Utility functions used across the application

### Tests (`tests/`)
- `test_routes.py`: Unit tests for routes
- `test_models.py`: Unit tests for models
- `test_services.py`: Unit tests for services
- `test_utils.py`: Unit tests for utilities
- `test_error_handling.py`: Unit tests for error handling
- `test_auth.py`: Unit tests for authentication
- `test_database.py`: Unit tests for database interactions
- `test_forms.py`: Unit tests for form validation

### Configuration Files
- `Dockerfile`: Container configuration
- `docker-compose.yml`: Multi-container setup
- `.env`: Environment variables

## Route Structure

### Main Routes (127.0.0.1:5000)
- **/** - Home page (Main index) `main_bp`
  - Basic welcome page with navigation

### Authentication Routes
- **/login** - Login page `auth_bp`
- **/logout** - Logout functionality

### Items Routes
- **/items/** - Items main page `items_bp`
- **/items/api/list** - Items API endpoint
- **/items/price_override** - Price override (POST)
- **/items/blacklist_item** - Item blacklisting (POST)
- **/items/lock_item** - Item locking (POST)

### API Routes
- **/api/** - API index `api_bp`
- **/api/status** - API status endpoint

### Debug Interface
- **/debug** - Debug panel for testing and validation

### Optimizer Interface
- **/optimizer** - Item optimization interface