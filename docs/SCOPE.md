# Project Scope

## Overview
Tarkov Cultist Circle is intentionally designed as a lightweight, single-purpose application for a small user base. This document defines boundaries to prevent unnecessary complexity.

## Core Features
1. Basic item optimization using Neo4j
2. Simple Material Design UI
3. Essential Tarkov.dev API integration
4. Basic request metrics
5. Debug interface for prompt management

## Core Architecture

### Framework Choice
- Flask as the sole web framework
- No additional web frameworks (e.g., FastAPI) to maintain simplicity
- RESTful API design using Flask blueprints

### Storage and Caching
- Neo4j as primary database
- In-memory rate limiting and simple caching
- No external caching/queueing systems (e.g., Redis)
- Utilize Neo4j's built-in caching capabilities

## Design Principles

1. Simplicity First
   - Single web framework
   - Minimal external dependencies
   - In-memory solutions where possible
   - Clear, maintainable codebase

2. Performance Through Simplicity
   - Efficient database queries over caching layers
   - Lightweight rate limiting
   - Direct request handling
   - No microservices complexity

3. Scalability Constraints
   - Designed for small to medium user base
   - Vertical scaling preferred
   - Single instance deployment
   - No distributed system requirements

## Technical Boundaries

### Included
- Flask web application
- Neo4j graph database
- JWT authentication
- In-memory rate limiting
- Material Design UI
- GraphQL client (external API consumption)

### Explicitly Excluded
- Multiple web frameworks
- External caching systems
- Message queues
- Distributed computing
- Complex orchestration
- Microservices architecture

## Future Considerations

When considering future updates:
1. Maintain the single framework approach
2. Avoid introducing complex external dependencies
3. Prefer vertical scaling solutions
4. Leverage built-in Neo4j features before adding new systems

## Scaling Strategy

1. Optimize Neo4j queries and indices
2. Increase server resources
3. Improve in-memory algorithms
4. Enhanced connection pooling

Note: If scale requirements significantly exceed these boundaries, consider project forking rather than architectural compromise.

## Explicitly Out of Scope
1. Advanced user management/authentication
2. External caching systems
3. Complex messaging/queuing systems
4. Distributed deployments
5. Real-time updates
6. Complex rate limiting rules
7. Multi-region support
8. Complex analytics
9. Multiple database support
10. Complex background tasks
11. WebSocket functionality
12. External API provision
13. Redis support
14. FastAPI use

## Implementation Constraints
1. Use built-in functionality where possible
2. Avoid external services unless absolutely necessary
3. Prefer simplicity over complexity
4. Minimize third-party dependencies
5. Use Neo4j's native features over custom implementations
6. Keep rate limiting simple and in-memory
7. Collect only essential metrics
8. Stick to Flask and avoid mixing web frameworks
9. Use Python's built-in venv for environment management
10. Keep dependencies version-agnostic when stable

## Dependencies Management
1. Core dependencies should be minimal and essential
2. Development dependencies should be separated via extras_require
3. Avoid pinning specific versions unless required for stability
4. Document dependency purposes in requirements.txt
5. Use virtual environment for isolation
6. Regular dependency audits to remove unused packages

## Development Guidelines
1. Follow project structure for code organization
2. Write tests for core functionality
3. Document code changes and dependencies
4. Use debug tools for development
5. Keep configuration simple
6. Store AI prompts directly as JSON files
7. Use Neo4j for data persistence only

## Feature Request Guidelines
New features should be:
1. Essential to core functionality
2. Simple to implement
3. Easy to maintain
4. Beneficial to majority of users
5. Avoid adding complexity to core components

## Maintenance Guidelines
1. Regular database maintenance
2. Simple deployment process
3. Basic request monitoring
4. Clear error handling
5. Keep core components minimal
6. Review dependencies regularly

## Technical Scope

### Framework and Dependencies
- Flask as the sole web framework
- Neo4j as the primary database
- No additional web frameworks or caching layers
- In-memory rate limiting and caching where needed

### File Management
When removing files:
1. Use PowerShell's Remove-Item command first
2. Verify complete removal of file contents
3. Update related documentation and dependencies

## Out of Scope

### Technical Limitations
1. Additional web frameworks
2. Additional database systems
3. External caching systems
4. Complex distributed systems