# Project Scope

## Overview
Tarkov Cultist Circle is intentionally designed as a lightweight, single-purpose application for a small user base. This document defines boundaries to prevent unnecessary complexity.

## Core Features
1. Basic item optimization using Neo4j
2. Simple Material Design UI
3. Essential Tarkov.dev API integration
4. Basic request metrics

## Explicitly Out of Scope
1. Advanced user management/authentication
2. External caching systems
3. Complex messaging/queuing systems
4. Distributed deployments
5. Real-time updates
6. Complex rate limiting rules
7. Multi-region support
8. Complex analytics

## Implementation Constraints
1. Use built-in functionality where possible
2. Avoid external services unless absolutely necessary
3. Prefer simplicity over complexity
4. Minimize third-party dependencies
5. Use Neo4j's native features over custom implementations
6. Keep rate limiting simple and in-memory
7. Collect only essential metrics

## Core Components
1. Simple login management
2. Basic rate limiting (1000 requests per hour per IP)
3. Essential request metrics
4. Neo4j database integration
5. Form validation
6. Database transaction management

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