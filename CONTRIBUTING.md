# Contributing to TheHive MCP Server

Thank you for your interest in contributing to TheHive MCP Server! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/thehive_mcp.git
   cd thehive_mcp
   ```
3. **Set up development environment**:
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv sync --dev
   
   # Set up environment variables
   cp .env.example .env  # Edit with your credentials
   ```
4. **Run tests** to ensure everything works:
   ```bash
   uv run pytest
   ```

## 🛠️ Development Environment

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) for dependency management
- TheHive instance (or use Docker setup)
- Git

### Environment Setup

```bash
# Set required environment variables
export HIVE_URL="http://localhost:9000"
export HIVE_API_KEY="your-api-key"

# Or create a .env file
echo "HIVE_URL=http://localhost:9000" > .env
echo "HIVE_API_KEY=your-api-key" >> .env
```

### Using Docker for TheHive

```bash
cd docker
docker-compose up -d
```

This provides a complete TheHive + Cortex + Elasticsearch stack for development.

## 📝 Code Standards

### Code Style

We use `ruff` for linting and formatting:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .
```

### Type Checking

We use `mypy` for type checking:

```bash
uv run mypy src/
```

### Testing

- **Write tests** for all new functionality
- **Maintain test coverage** above 95%
- **Use descriptive test names** that explain what is being tested

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test types
uv run pytest tests/unit/
uv run pytest tests/integration/
```

### Documentation

- **Add docstrings** to all public functions and classes
- **Update README.md** if adding new features
- **Generate documentation** after changes:
  ```bash
  uv run python dev-tools/generate_docs.py
  ```

## 🔧 Making Changes

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/description` - Feature branches
- `bugfix/description` - Bug fix branches
- `hotfix/description` - Critical fixes

### Commit Messages

Follow conventional commits format:

```
type(scope): description

Examples:
feat(alert): add support for bulk alert operations
fix(api): resolve authentication timeout issue
docs(readme): update installation instructions
test(integration): add case management tests
```

### Pull Request Process

1. **Create a feature branch** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code standards

3. **Add/update tests** for your changes

4. **Update documentation** if needed

5. **Run the full test suite**:
   ```bash
   uv run pytest
   uv run ruff check .
   uv run mypy src/
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat(scope): description of your changes"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** against the `develop` branch

## 🧪 Testing Guidelines

### Test Structure

- `tests/unit/` - Unit tests for individual modules
- `tests/integration/` - End-to-end workflow tests
- `tests/conftest.py` - Shared test configuration

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch

class TestYourFeature:
    """Test cases for your feature."""
    
    def test_feature_basic_functionality(self):
        """Test that basic functionality works as expected."""
        # Arrange
        # Act
        # Assert
        pass
    
    @pytest.mark.asyncio
    async def test_async_feature(self):
        """Test async functionality."""
        pass
    
    def test_error_handling(self):
        """Test error conditions are handled properly."""
        pass
```

### Test Environment

Tests use environment variables set in `tests/conftest.py`. The test suite is designed to work without requiring a real TheHive instance.

## 📋 Feature Development

### Adding New TheHive API Support

1. **Research the API**: Check TheHive documentation and thehive4py support
2. **Add the module**: Create new file in `src/thehive/`
3. **Implement functions**: Follow existing patterns in other modules
4. **Add tests**: Both unit and integration tests
5. **Update documentation**: Add to feature status table in README
6. **Register tools**: Add to MCP server registration

### Example Structure

```python
# src/thehive/your_module.py
"""
Your Module Management

This module provides functionality for managing [feature] in TheHive.
"""

from typing import List, Optional
from .hive_session import hive_session

async def your_function(param: str) -> List[dict]:
    """
    Your function description.
    
    Args:
        param: Parameter description
        
    Returns:
        List of results
        
    Raises:
        Exception: When something goes wrong
    """
    # Implementation
    pass
```

## 🔍 Code Review Process

### What Reviewers Look For

- **Functionality**: Does the code do what it claims?
- **Tests**: Are there adequate tests with good coverage?
- **Code Quality**: Is the code readable and maintainable?
- **Documentation**: Is the code well-documented?
- **Security**: Are there any security implications?
- **Performance**: Does it maintain good performance?

### Review Checklist

- [ ] Code follows project standards
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Backward compatibility maintained
- [ ] Performance impact considered

## 🚨 Reporting Issues

### Bug Reports

Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment information
- Error logs (with sensitive data redacted)

### Feature Requests

Use the feature request template and include:
- Clear description of the need
- Proposed solution
- TheHive API information if applicable
- Use cases and examples

## 📊 Release Process

1. **Version Bump**: Update version in `pyproject.toml`
2. **Changelog**: Update CHANGELOG.md with new features/fixes
3. **Tag Release**: Create Git tag with version number
4. **GitHub Release**: Create release on GitHub
5. **Automated Publishing**: CI/CD pipeline handles PyPI publishing

## 🤝 Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community support
- **Documentation**: Check the docs/ directory

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Maintain professionalism

## 📚 Resources

- [TheHive Documentation](https://docs.thehive-project.org/)
- [thehive4py Documentation](https://github.com/TheHive-Project/TheHive4py)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/pydantic/FastMCP)

Thank you for contributing to TheHive MCP Server! 🎉
