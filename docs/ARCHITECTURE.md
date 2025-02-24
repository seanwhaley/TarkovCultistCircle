# Application Architecture

## Overview
This application uses a Flask-based architecture with Neo4j as the primary database.

## File Management Policy
When removing files from the project:
1. Use PowerShell's Remove-Item command first:
   ```powershell
   Remove-Item -Path "path/to/file" -Force
   ```
2. Ensure all contents are completely removed
3. Update relevant documentation and dependencies

## System Overview

```
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐
│   Flask App     │────▶│   Neo4j DB   │────▶│ GraphQL API   │
└─────────────────┘     └──────────────┘     └───────────────┘
        │                      │                     │
        ▼                      ▼                     ▼
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐
│ Material Design │     │ In-Memory    │     │ Price Updates │
└─────────────────┘     │   Cache      │     └───────────────┘
                        └──────────────┘     
```

## Design Decisions

### Framework Choice: Flask-Only Architecture
- **Rationale**: 
  - Simplified single-framework approach
  - Reduced complexity in routing and middleware
  - Easier maintenance and debugging
  - Sufficient performance for small-scale deployment
  - Built-in session management and request handling

### Rate Limiting Implementation
- **Strategy**: Simple in-memory implementation
  - Lightweight and suitable for small user base
  - No external dependencies
  - Automatic cleanup of old entries
  - IP-based rate limiting with configurable windows

### Database: Neo4j
- **Rationale**: 
  - Efficient graph operations for item relationships
  - Built-in query result caching
  - Native support for complex item relationship queries
  - Sufficient for current scale without additional caching layer

## Core Components

### Core Module
The core module provides essential functionality with minimal complexity:

1. Rate Limiting
   - Simple in-memory implementation
   - Global request limits per IP
   - Configurable time windows
   - Automatic cleanup

2. User Authentication
   - Flask-Login integration
   - Simple session management
   - JWT support for API routes

3. Request Metrics
   - Basic request counting
   - Error tracking
   - Minimal overhead

4. Database Layer
   - Direct Neo4j integration
   - Transaction management
   - Query result caching

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
- Keep the architecture simple and focused
- Avoid introducing complex dependencies
- Leverage Flask's built-in capabilities
- Scale vertically before adding complexity

## Technical Requirements

### Performance Targets
- API Response: <100ms for 95th percentile
- Database Queries: <50ms average
- UI Interactions: <16ms for animations
- Initial Load: <3s First Contentful Paint

### Scalability
- Handles concurrent users appropriate for small deployments
- Manages item catalog efficiently
- 99.9% uptime with minimal infrastructure

### Security
- In-memory rate limiting per IP
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

### Rate Limiting
- In-memory rate limiting implementation
- Configurable limits per endpoint
- IP-based request tracking

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