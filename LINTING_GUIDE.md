# Linting and Code Quality Guide

This document outlines the comprehensive linting and code quality setup for the Spotify Library Manager project.

## Overview

The project uses multiple linting and formatting tools to ensure code quality and consistency across both frontend and backend codebases.

## Backend (Python) Tools

### 1. **Black** - Code Formatter
- **Purpose**: Automatic code formatting
- **Configuration**: `pyproject.toml`
- **Line Length**: 88 characters
- **Usage**:
  ```bash
  make format-api-black          # Format code
  make lint-api-black           # Check formatting
  ```

### 2. **isort** - Import Sorter
- **Purpose**: Organizes and sorts imports
- **Configuration**: `pyproject.toml`
- **Profile**: Black-compatible
- **Usage**:
  ```bash
  make format-api-isort          # Sort imports
  make lint-api-isort           # Check import sorting
  ```

### 3. **Flake8** - Style Guide Enforcement
- **Purpose**: Enforces PEP 8 style guide
- **Configuration**: `pyproject.toml`
- **Line Length**: 88 characters (Black-compatible)
- **Usage**:
  ```bash
  make lint-api-flake8          # Run flake8
  ```

### 4. **MyPy** - Type Checking
- **Purpose**: Static type checking
- **Configuration**: `pyproject.toml`
- **Strict Mode**: Enabled
- **Usage**:
  ```bash
  make lint-api-mypy            # Run type checking
  ```

### 5. **Bandit** - Security Linting
- **Purpose**: Security vulnerability detection
- **Configuration**: `pyproject.toml`
- **Output**: JSON report
- **Usage**:
  ```bash
  make lint-api-bandit          # Run security checks
  ```

### 6. **Pylint** - Code Analysis
- **Purpose**: Comprehensive code analysis
- **Configuration**: `pyproject.toml`
- **Django Support**: Enabled
- **Usage**:
  ```bash
  make lint-api-pylint          # Run pylint
  ```

## Frontend (TypeScript/React) Tools

### 1. **ESLint** - JavaScript/TypeScript Linting
- **Purpose**: Code quality and best practices
- **Configuration**: `frontend/eslint.config.js`
- **Plugins**: TypeScript, React, React Hooks, Prettier
- **Usage**:
  ```bash
  make lint-frontend            # Run ESLint
  cd frontend && yarn lint:fix  # Fix auto-fixable issues
  ```

### 2. **Prettier** - Code Formatter
- **Purpose**: Consistent code formatting
- **Configuration**: `frontend/.prettierrc`
- **Integration**: ESLint plugin
- **Usage**:
  ```bash
  make format-frontend          # Format code
  cd frontend && yarn format:check  # Check formatting
  ```

## Available Commands

### Linting Commands
```bash
# Run all linting checks
make lint

# Run all linting and formatting checks
make lint-all

# Backend only
make lint-api

# Frontend only
make lint-frontend

# Individual backend tools
make lint-api-flake8
make lint-api-black
make lint-api-isort
make lint-api-mypy
make lint-api-bandit
make lint-api-pylint
```

### Formatting Commands
```bash
# Format all code
make format

# Backend formatting
make format-api

# Frontend formatting
make format-frontend

# Check formatting without changing files
make format-check
```

## Configuration Files

### Backend
- `pyproject.toml` - Central configuration for all Python tools
- `tox.ini` - Legacy flake8 configuration (deprecated)

### Frontend
- `frontend/eslint.config.js` - ESLint configuration
- `frontend/.prettierrc` - Prettier configuration
- `frontend/package.json` - Dependencies and scripts

## Best Practices

### 1. **Pre-commit Hooks**
Consider setting up pre-commit hooks to automatically run linting before commits:
```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml
# Run: pre-commit install
```

### 2. **IDE Integration**
Configure your IDE to use these tools:
- **VS Code**: Install ESLint, Prettier, and Python extensions
- **PyCharm**: Enable Black, isort, and MyPy integration
- **Vim/Neovim**: Use ALE or similar plugins

### 3. **CI/CD Integration**
The linting tools are configured to work with CI/CD pipelines:
- All tools return appropriate exit codes
- Bandit generates JSON reports for security scanning
- Coverage reports are generated for testing

### 4. **Code Quality Metrics**
Monitor these metrics:
- **Type Coverage**: MyPy reports
- **Security Issues**: Bandit reports
- **Code Style**: Flake8, Black, isort compliance
- **Test Coverage**: pytest-cov reports

## Troubleshooting

### Common Issues

1. **Black/Flake8 Line Length Conflicts**
   - Both tools are configured for 88 characters
   - Use `make format-api` to fix formatting issues

2. **Import Sorting Issues**
   - Run `make format-api-isort` to fix import order
   - Check `pyproject.toml` for isort configuration

3. **Type Checking Errors**
   - MyPy is configured in strict mode
   - Add type annotations to fix errors
   - Use `# type: ignore` sparingly

4. **ESLint/Prettier Conflicts**
   - Prettier handles formatting, ESLint handles logic
   - Use `make format-frontend` to fix formatting
   - Use `cd frontend && yarn lint:fix` for auto-fixable issues

### Performance Tips

1. **Selective Linting**
   ```bash
   # Lint specific files
   cd api && python -m black specific_file.py
   cd frontend && yarn lint src/components/SpecificComponent.tsx
   ```

2. **Parallel Execution**
   ```bash
   # Run backend and frontend linting in parallel
   make lint-api & make lint-frontend & wait
   ```

## Security Considerations

1. **Bandit Integration**
   - Automatically scans for security vulnerabilities
   - Generates JSON reports for CI/CD integration
   - Configure exclusions in `pyproject.toml`

2. **Secret Detection**
   - Consider adding `detect-secrets` for secret scanning
   - Integrate with Git hooks for pre-commit scanning

## Future Enhancements

1. **Additional Tools**
   - `mypy-boto3` for AWS SDK type checking
   - `django-stubs` for better Django type support
   - `pytest-mypy` for type checking in tests

2. **Advanced Configuration**
   - Custom ESLint rules for project-specific patterns
   - Automated dependency vulnerability scanning
   - Performance linting with `eslint-plugin-import`

3. **Monitoring**
   - Track linting metrics over time
   - Set up alerts for new security issues
   - Monitor type coverage trends 
