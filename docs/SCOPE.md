# Project Scope

## Overview
Tarkov Cultist Circle is intentionally designed as a lightweight, single-purpose application for a small user base. This document defines boundaries to prevent unnecessary complexity.

## Core Features
1. Basic item optimization using Neo4j
2. Simple Material Design UI
3. Essential Tarkov.dev API integration
4. Basic price tracking

## Explicitly Out of Scope
1. Advanced user management/authentication
2. Complex caching mechanisms
3. Extensive API features
4. Complex deployment configurations
5. Real-time updates
6. Extended analytics
7. Multi-region support

## Architecture Decisions
1. Two-container setup only (web + database)
2. Minimal external dependencies
3. Simple file structure
4. Basic Material Design implementation
5. Limited API endpoints

## Feature Request Guidelines
New features should be:
1. Essential to core functionality
2. Simple to implement
3. Easy to maintain
4. Beneficial to majority of users

## GitHub Issues Management

### Issue Categories
Only maintain issues in these categories:
1. Bugs: Critical application errors
2. Core Features: Essential functionality defined in scope
3. Security: Critical security updates
4. Documentation: Essential documentation updates

### Issue Labels
Simplified label system:
- bug: Application errors
- enhancement: Core feature improvements
- security: Security-related
- docs: Documentation updates

### Issue Priority
P1: Critical bugs/security
P2: Core functionality
P3: Non-critical improvements

### Workflow
1. New issues must reference this scope document
2. Issues that exceed scope should be closed
3. Maximum of 5 open issues at any time
4. Focus on completion over new features

This simplified issue management ensures the project maintains its lightweight nature.

This scope document serves as a guide for maintaining simplicity and preventing feature creep.