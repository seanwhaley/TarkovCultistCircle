# GitHub Issues Guide

## Overview

This project uses GitHub Issues for tracking all work items, requirements, and implementation progress. The issue templates and structure are designed to work effectively with AI-assisted development tools like GitHub Copilot.

## Issue Types

1. **Feature Requests** - For new features and enhancements
2. **Bug Reports** - For reporting and tracking bugs
3. **Technical Tasks** - For refactoring and technical improvements

## AI-Optimized Issue Creation

### Creating Issues for AI-Assisted Development

When creating issues that will be implemented with AI assistance:

1. **Clear Context**
   - Provide complete business context
   - Include relevant technical details
   - Reference existing components
   - Link to related documentation

2. **Implementation Structure**
   - Break down into smaller, focused tasks
   - List specific files that need changes
   - Include current code patterns to follow
   - Note any configuration requirements

3. **AI-Friendly Format**
   ```markdown
   ### Feature: [Name]

   **Context:**
   [Technical and business context that AI tools need to understand the requirement]

   **Current Implementation:**
   - File: src/feature/example.py
   - Pattern: [Relevant code pattern]
   - Related Components: [List]

   **Required Changes:**
   1. [Specific change with technical details]
   2. [Next change...]

   **Validation:**
   - Test cases to verify
   - Expected behavior
   - Error scenarios
   ```

### Working with GitHub Copilot

1. **Commenting Style**
   ```python
   # Task: [Issue #number] - Brief description
   # Context: Explain what the code does
   # Requirements:
   # 1. Specific requirement
   # 2. Another requirement
   def example_function():
       pass
   ```

2. **Documentation Updates**
   ```python
   """
   Issue: #123 - Feature name
   Purpose: Brief description
   
   Technical Details:
   - Implementation note 1
   - Implementation note 2
   """
   ```

3. **Change Tracking**
   ```python
   # Modified: [Issue #number] - Change description
   # Previous: Old implementation detail
   # Current: New implementation approach
   ```

## Issue Management

### Labels for AI Development

- `ai-ready`: Issue is formatted for AI-assisted development
- `ai-in-progress`: Currently being implemented with AI assistance
- `ai-review-needed`: AI implementation needs human review
- `ai-docs`: Documentation updates needed for AI changes

### Project Boards

1. **AI Development Board**
   - Backlog
   - Ready for AI Implementation
   - In Progress (AI-Assisted)
   - Human Review
   - Done

### Review Process

1. **AI-Generated Changes**
   - Review generated code against requirements
   - Verify test coverage
   - Check documentation updates
   - Validate edge cases

2. **Quality Checks**
   - Code style consistency
   - Error handling
   - Performance considerations
   - Security implications

## Best Practices

1. **Issue Description**
   - Be specific and detailed
   - Include technical context
   - Reference documentation
   - Link related issues

2. **Implementation Notes**
   - List affected components
   - Note required configurations
   - Include test scenarios
   - Document edge cases

3. **Review Guidelines**
   - Check AI-generated code thoroughly
   - Verify requirement coverage
   - Test edge cases
   - Review documentation updates

## Example Issue Structure

```markdown
### Feature: Enhanced Market Analytics

Issue Type: Feature Request
AI-Ready: Yes
Priority: P1

**Business Context:**
Users need better market trend insights for trading decisions.

**Technical Scope:**
- Implement time-series data tracking
- Add WebSocket updates
- Integrate caching layer

**Current Implementation:**
- Location: src/blueprints/market.py
- Pattern: Repository pattern for data access
- Related: Price history module

**Required Changes:**
1. Add time-series tracking:
   - File: src/models/market.py
   - Changes: Add timestamp fields
   - Pattern: Follow existing model structure

2. Implement WebSocket:
   - File: src/blueprints/market.py
   - New Feature: Real-time updates
   - Reference: Existing WebSocket implementation

**Validation:**
- Unit tests for new models
- WebSocket connection tests
- Performance under load
- Cache hit ratio metrics

**Dependencies:**
- Issue #234: Cache implementation
- Issue #245: WebSocket foundation
```

## Next Steps

1. Use issue templates in `.github/ISSUE_TEMPLATE/`
2. Follow the AI-optimized format
3. Maintain clear documentation links
4. Update related files when implementing