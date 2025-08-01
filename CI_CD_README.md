# CI/CD Pipeline & Development Workflow

## 🚀 Overview

This project now has a comprehensive CI/CD pipeline that runs tests in parallel and optimizes the development experience with faster pre-commit hooks.

## 📋 CI/CD Pipeline

### Parallel Jobs

The CI pipeline runs the following jobs in parallel for maximum efficiency:

1. **Backend Tests** (`backend-tests`)
   - Runs Python unit tests with coverage
   - Uploads coverage to Codecov
   - Tests all backend functionality including new task management features

2. **Frontend Tests** (`frontend-tests`)
   - Runs Vitest unit tests with coverage
   - Uploads coverage to Codecov
   - Tests React components and utilities

3. **Type Checking** (`type-checking`)
   - Runs mypy for Python type checking
   - Runs TypeScript type checking
   - Ensures type safety across the stack

4. **Code Quality** (`code-quality`)
   - Runs Python linting (flake8, black, isort)
   - Runs frontend linting (ESLint, Prettier)
   - Ensures code style consistency

### Sequential Jobs

5. **GraphQL Validation** (`graphql-validation`)
   - Runs after backend and frontend tests pass
   - Starts API server and validates GraphQL schema
   - Tests GraphQL operations for async/sync issues

6. **Build and Security** (`build-and-security`)
   - Runs after all other jobs pass
   - Performs security scans (safety, bandit, yarn audit)
   - Builds frontend application
   - Uploads security reports as artifacts

## 🔧 Development Workflow

### Fast Pre-commit Hooks

The pre-commit hooks have been optimized for speed:

```bash
# Quick checks (runs in ~5-10 seconds)
git commit -m "your message"
```

**What runs on pre-commit:**
- ✅ TypeScript type check
- ✅ ESLint check
- ✅ Prettier format check
- ✅ Frontend unit tests

**What doesn't run on pre-commit (for speed):**
- ❌ GraphQL schema validation (requires API server)
- ❌ GraphQL operations testing (requires API server)

### Manual GraphQL Validation

When you need to validate GraphQL schema and operations:

```bash
# Start the API server first
cd api && python -m uvicorn src.main:app --reload --port 5000

# In another terminal, run manual validation
cd frontend && yarn validate-graphql-manual
```

This will:
- Check if API server is running
- Run comprehensive GraphQL schema validation
- Test all GraphQL operations
- Provide detailed feedback on any issues

## 🎯 Benefits

### Speed Improvements

| Before | After |
|--------|-------|
| Pre-commit: ~30-60 seconds | Pre-commit: ~5-10 seconds |
| CI: Sequential jobs | CI: Parallel jobs |
| Manual GraphQL validation | Automated in CI |

### Development Experience

- **Faster commits**: Pre-commit hooks are now lightning fast
- **Parallel CI**: Tests run in parallel, reducing total CI time
- **Comprehensive validation**: All checks still run in CI
- **Manual control**: GraphQL validation available when needed

### Quality Assurance

- **Type safety**: Both Python and TypeScript type checking
- **Code quality**: Linting and formatting checks
- **Test coverage**: Comprehensive test coverage reporting
- **Security**: Automated security scanning
- **GraphQL validation**: Schema and operations testing

## 📊 CI Job Dependencies

```
backend-tests ──┐
frontend-tests ──┼── graphql-validation ──┐
type-checking ───┘                        │
code-quality ──────────────────────────────┼── build-and-security
                                          │
                                          └── (final success)
```

## 🛠️ Local Development

### Quick Development Cycle

```bash
# 1. Make changes
# 2. Quick pre-commit checks (fast)
git commit -m "your changes"

# 3. Push to trigger CI
git push origin your-branch
```

### When You Need GraphQL Validation

```bash
# Option 1: Manual validation
yarn validate-graphql-manual

# Option 2: Let CI handle it
git push origin your-branch
```

### Running Tests Locally

```bash
# Backend tests
cd api && python -m pytest tests/ -v

# Frontend tests
cd frontend && yarn test:run

# Type checking
cd api && mypy src/
cd frontend && yarn tsc --noEmit
```

## 🔍 Monitoring

### CI Dashboard

- View all jobs in GitHub Actions
- Check coverage reports in Codecov
- Review security scan results
- Monitor build times and success rates

### Local Development

- Pre-commit hooks provide immediate feedback
- Manual GraphQL validation when needed
- Type checking catches issues early

## 🚨 Troubleshooting

### Pre-commit Hook Issues

```bash
# Skip pre-commit hooks (emergency only)
git commit -m "message" --no-verify

# Reinstall husky hooks
cd frontend && yarn husky install
```

### GraphQL Validation Issues

```bash
# Check if API server is running
curl http://localhost:5000/graphql

# Start API server
cd api && python -m uvicorn src.main:app --reload --port 5000

# Run manual validation
cd frontend && yarn validate-graphql-manual
```

### CI Issues

- Check GitHub Actions logs for specific job failures
- Verify all dependencies are properly cached
- Ensure all required secrets are configured

## 📈 Performance Metrics

### Expected Times

| Job | Expected Duration |
|-----|------------------|
| Backend Tests | 2-3 minutes |
| Frontend Tests | 1-2 minutes |
| Type Checking | 30-60 seconds |
| Code Quality | 30-60 seconds |
| GraphQL Validation | 1-2 minutes |
| Build & Security | 2-3 minutes |
| **Total CI Time** | **~3-4 minutes** (parallel) |

### Pre-commit Hook Times

| Check | Expected Duration |
|-------|------------------|
| TypeScript | 1-2 seconds |
| ESLint | 2-3 seconds |
| Prettier | 1-2 seconds |
| Frontend Tests | 3-5 seconds |
| **Total Pre-commit** | **~5-10 seconds** |

## 🎉 Summary

This optimized CI/CD setup provides:

- ⚡ **Fast development**: Quick pre-commit hooks
- 🚀 **Parallel CI**: Efficient test execution
- 🔍 **Comprehensive validation**: All checks still run
- 🛡️ **Quality assurance**: Type safety, linting, security
- 📊 **Monitoring**: Coverage and security reporting
- 🎯 **Flexibility**: Manual validation when needed

The development experience is now much faster while maintaining all quality checks in the CI pipeline! 
