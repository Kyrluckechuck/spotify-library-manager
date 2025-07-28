# Testing Guide

This document provides a comprehensive guide to the testing infrastructure for the Spotify Library Manager project.

## Overview

The project has comprehensive testing setup for both backend (Django/Python) and frontend (React/TypeScript) components.

## Backend Testing

### Test Structure

```
api/
├── tests/
│   ├── conftest.py              # Test configuration and fixtures
│   ├── fixtures/
│   │   └── artist_fixtures.py   # Test data fixtures
│   ├── unit/
│   │   ├── test_models.py       # Django model tests
│   │   └── test_services.py     # Service layer tests
│   └── integration/
│       ├── test_graphql.py      # GraphQL query tests
│       └── test_mutations.py    # GraphQL mutation tests
└── src/
    └── tests/
        └── test_artist_service.py # Additional service tests
```

### Test Configuration

The backend uses pytest with Django integration:

- **pytest.ini**: Main configuration with Django settings and coverage
- **conftest.py**: Global test configuration and fixtures
- **Coverage**: HTML and terminal reporting with 80% minimum threshold

### Running Backend Tests

```bash
# Run all backend tests
make test-api

# Run only unit tests
make test-api-unit

# Run only integration tests
make test-api-integration

# Run tests with coverage (fails if < 80%)
make test-api-coverage

# Run specific test file
PYTHONPATH=api python -m pytest api/tests/unit/test_models.py -v

# Run tests with specific markers
PYTHONPATH=api python -m pytest -m "unit" -v
```

### Test Categories

1. **Unit Tests** (`@pytest.mark.unit`)
   - Model tests (Django ORM)
   - Service layer tests
   - Utility function tests

2. **Integration Tests** (`@pytest.mark.integration`)
   - GraphQL query tests
   - GraphQL mutation tests
   - Database integration tests

3. **GraphQL Tests** (`@pytest.mark.graphql`)
   - Schema validation
   - Query execution
   - Mutation testing

### Test Fixtures

Common fixtures available in `api/tests/fixtures/artist_fixtures.py`:

- `sample_artist`: Basic artist for testing
- `untracked_artist`: Artist with tracked=False
- `multiple_artists`: Array of artists for pagination tests
- `sample_album`: Album with artist relationship
- `sample_song`: Song with artist and album relationships
- `sample_playlist`: Playlist for testing

## Frontend Testing

### Test Structure

```
frontend/
├── vitest.config.ts             # Vitest configuration
├── src/
│   ├── test/
│   │   └── setup.ts            # Test setup and mocks
│   ├── components/
│   │   ├── __tests__/
│   │   │   └── Navbar.test.tsx # Component tests
│   │   └── ui/
│   │       └── __tests__/
│   │           └── SearchInput.test.tsx
│   └── routes/
│       └── __tests__/
│           └── artists.test.tsx # Route tests
```

### Test Configuration

The frontend uses Vitest with React Testing Library:

- **vitest.config.ts**: Vitest configuration with jsdom environment
- **setup.ts**: Global test setup with mocks
- **Coverage**: V8 coverage provider with HTML reporting

### Running Frontend Tests

```bash
# Run all frontend tests
make test-frontend

# Run tests in watch mode
make test-frontend-watch

# Run tests with coverage
make test-frontend-coverage

# Run tests with UI
make test-frontend-ui

# Run specific test file
cd frontend && yarn test src/components/__tests__/Navbar.test.tsx
```

### Test Categories

1. **Component Tests**
   - UI component rendering
   - User interaction testing
   - Props and state testing

2. **Integration Tests**
   - Route component testing
   - GraphQL integration testing
   - Router integration testing

### Test Mocks

The frontend test setup includes comprehensive mocks:

- **Apollo Client**: Mocked GraphQL hooks
- **TanStack Router**: Mocked routing components
- **GraphQL Types**: Mocked generated types
- **Browser APIs**: Mocked ResizeObserver, matchMedia

## Test Coverage

### Backend Coverage

Coverage is measured for:
- `api/src/` - Service layer and business logic
- `api/library_manager/` - Django models and views

Minimum coverage threshold: 80%

### Frontend Coverage

Coverage is measured for:
- All TypeScript/React components
- Utility functions
- Route components

Coverage reports are generated in HTML format for both backend and frontend.

## Writing Tests

### Backend Test Example

```python
import pytest
from unittest.mock import Mock, patch
from api.src.services.artist import ArtistService

@pytest.mark.django_db
class TestArtistService:
    @pytest.fixture
    def artist_service(self):
        return ArtistService()
    
    @pytest.mark.asyncio
    async def test_get_by_id_success(self, artist_service):
        with patch('library_manager.models.Artist.objects.aget') as mock_aget:
            mock_artist = Mock(gid="test123", name="Test Artist")
            mock_aget.return_value = mock_artist
            
            result = await artist_service.get_by_id("test123")
            
            assert result is not None
            assert result.id == "test123"
```

### Frontend Test Example

```typescript
import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { SearchInput } from '../SearchInput'

describe('SearchInput', () => {
  it('renders with placeholder text', () => {
    const mockOnSearch = vi.fn()
    render(<SearchInput onSearch={mockOnSearch} placeholder="Search..." />)
    
    expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument()
  })
})
```

## Best Practices

### Backend Testing

1. **Use fixtures** for consistent test data
2. **Mock external dependencies** (APIs, databases)
3. **Test both success and failure cases**
4. **Use descriptive test names**
5. **Group related tests in classes**

### Frontend Testing

1. **Test user interactions** not implementation details
2. **Use accessible queries** (getByRole, getByLabelText)
3. **Mock external dependencies** (GraphQL, routing)
4. **Test component behavior** not internal state
5. **Use data-testid sparingly**

### General Guidelines

1. **Keep tests fast** - avoid slow operations
2. **Make tests reliable** - avoid flaky tests
3. **Test the public API** - not internal implementation
4. **Use meaningful assertions** - clear failure messages
5. **Maintain test data** - keep fixtures up to date

## Continuous Integration

Tests are automatically run in CI/CD:

- **Backend**: Type checking with mypy, linting with flake8
- **Frontend**: Type checking with TypeScript, linting with ESLint
- **Coverage**: Minimum thresholds enforced
- **Test Results**: Reported in CI/CD pipeline

## Troubleshooting

### Common Issues

1. **Django settings not configured**
   - Ensure `DJANGO_SETTINGS_MODULE` is set
   - Check `PYTHONPATH` includes api directory

2. **Frontend tests failing**
   - Check that all dependencies are installed
   - Verify mocks are properly configured
   - Ensure test setup is imported

3. **Coverage not meeting threshold**
   - Add tests for uncovered code
   - Review coverage report for gaps
   - Consider if code is actually needed

### Debugging Tests

```bash
# Backend debugging
PYTHONPATH=api python -m pytest api/tests/ -v -s --pdb

# Frontend debugging
cd frontend && yarn test --reporter=verbose
```

## Future Improvements

1. **Performance Testing**: Add load testing for API endpoints
2. **E2E Testing**: Add Playwright or Cypress for full application testing
3. **Visual Testing**: Add visual regression testing for UI components
4. **Security Testing**: Add security-focused test cases
5. **Accessibility Testing**: Add automated accessibility testing 