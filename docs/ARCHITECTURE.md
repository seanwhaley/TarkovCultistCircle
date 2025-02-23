# Application Architecture

## System Overview

```
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐
│   Flask App     │────▶│   Neo4j DB   │────▶│ GraphQL API   │
└─────────────────┘     └──────────────┘     └───────────────┘
        │                      │                     │
        ▼                      ▼                     ▼
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐
│ Material Design │     │ Query Cache  │     │ Price Updates │
└─────────────────┘     └──────────────┘     └───────────────┘
```

## Design Decisions

### Database Choice: Neo4j
- **Rationale**: Chosen for its native graph capabilities and built-in features:
  - Complex item relationship traversal
  - Efficient path-finding algorithms for combinations
  - Rich query language (Cypher) for relationship-based queries
  - Built-in algorithms for optimization problems
  - Native query result caching
  - Efficient connection pooling

### Framework: Flask
- **Rationale**: Selected for:
  - Lightweight and flexible architecture
  - Strong Python ecosystem integration
  - Extensive middleware support
  - Easy GraphQL integration via Ariadne
  - Simple async support with ASGI

### UI: Material Design 3
- **Rationale**: Implemented for:
  - Consistent and modern user experience
  - Built-in responsive design patterns
  - Rich component ecosystem
  - Accessibility compliance
  - Theme customization support

## Core Components

### Core Module
The core module provides essential functionality with minimal complexity:

1. Rate Limiting
   - Simple in-memory implementation
   - Global 1000 requests per hour per IP limit
   - No complex route-specific rules

2. User Authentication
   - Basic Flask-Login integration
   - Simple session management
   - Strong session protection

3. Request Metrics
   - Basic request counting
   - Error tracking
   - Hourly reset
   - No complex performance metrics

4. Form Validation
   - Simple type checking
   - Essential field validation
   - No complex validation rules

5. Database Transactions
   - Simple transaction management
   - Basic error handling
   - Direct Neo4j integration

### Database Layer
   - Neo4j native query caching
   - Direct database connections
   - Transaction management via decorators
   - No ORM complexity

### API Integration
   - Direct Tarkov.dev API calls
   - Simple response caching via Neo4j
   - Basic error handling
   - No complex retry logic

### User Interface
   - Material Design components
   - Simple theme system
   - Basic responsive layout
   - No complex animations

## Data Flow
1. Request → Rate Limiter → Route Handler
2. Basic Authentication (if needed)
3. Form Validation (if needed)
4. Database Transaction (if needed)
5. Response

## Monitoring
- Request counts per route
- Error counts per route
- Basic hourly statistics
- No complex metrics or analysis

## Deployment
- Two container setup (web + database)
- Simple configuration
- Basic health checks
- No complex orchestration

## Future Considerations
Keep future changes aligned with these principles:
1. Prefer simplicity over feature richness
2. Use built-in functionality over custom solutions
3. Keep core components minimal
4. Avoid introducing new dependencies

## Technical Requirements

### Performance Targets
- API Response: <100ms for 95th percentile
- Database Queries: <50ms average
- UI Interactions: <16ms for animations
- Initial Load: <3s First Contentful Paint

### Scalability
- Handles 1000+ concurrent users
- Manages 100k+ items
- Processes 1000+ requests/second
- 99.9% uptime SLA

### Security
- In-memory rate limiting per IP/user
- Input sanitization
- CSRF protection
- Secure sessions
- XSS prevention

## Development Standards

### Code Quality
- Type checking with mypy
- Linting with flake8
- Formatting with black
- Import sorting with isort

### Testing Requirements
- Unit test coverage >80%
- Integration test suite
- Performance benchmarks
- E2E testing with Playwright

### CI/CD Pipeline
- Automated testing
- Code quality checks
- Docker image builds
- Automated deployments

## Deployment Architecture

### Container Structure
- Flask application container
- Neo4j database container
- Nginx reverse proxy

### Monitoring
- Prometheus metrics
- Grafana dashboards
- Error tracking
- Performance monitoring

### Backup Strategy
- Automated Neo4j backups
- Configuration version control
- Disaster recovery procedures
- Data retention policies

## Documentation Requirements

### Technical Documentation
- API specifications
- Database schema
- Component documentation
- Security protocols

### User Documentation
- Setup guides
- User manuals
- API references
- Troubleshooting guides