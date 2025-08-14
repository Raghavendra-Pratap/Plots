# Contributing to Bounding Box Plotter

Thank you for your interest in contributing to Bounding Box Plotter! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **🐛 Bug Reports**: Report issues and bugs
- **💡 Feature Requests**: Suggest new features
- **📝 Documentation**: Improve documentation
- **🔧 Code Contributions**: Submit code changes
- **🧪 Testing**: Help test the application
- **🌐 Localization**: Translate to other languages
- **📊 Performance**: Optimize performance
- **🔒 Security**: Report security vulnerabilities

### Getting Started

1. **Fork the Repository**: Click the "Fork" button on GitHub
2. **Clone Your Fork**: `git clone https://github.com/YOUR_USERNAME/bounding-box-plotter.git`
3. **Create a Branch**: `git checkout -b feature/your-feature-name`
4. **Make Changes**: Implement your changes
5. **Test Your Changes**: Ensure everything works correctly
6. **Commit Changes**: `git commit -m "Add your feature description"`
7. **Push to Your Fork**: `git push origin feature/your-feature-name`
8. **Create a Pull Request**: Submit a PR to the main repository

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/bounding-box-plotter.git
cd bounding-box-plotter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt[dev]

# Install pre-commit hooks
pre-commit install
```

### Development Dependencies

```bash
# Install development dependencies
pip install -r requirements.txt[dev]

# Install additional tools
pip install black flake8 mypy pytest pytest-cov
```

## 📝 Code Style

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **String Quotes**: Double quotes for strings, single quotes for characters
- **Import Order**: Standard library, third-party, local imports

### Code Formatting

We use [Black](https://black.readthedocs.io/) for automatic code formatting:

```bash
# Format all Python files
black .

# Check formatting without changes
black --check .
```

### Linting

We use [Flake8](https://flake8.pycqa.org/) for linting:

```bash
# Run linter
flake8 .

# Run with specific configuration
flake8 --config .flake8 .
```

### Type Checking

We use [MyPy](http://mypy-lang.org/) for static type checking:

```bash
# Run type checker
mypy .

# Run with specific configuration
mypy --config-file mypy.ini .
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=bounding_box_plotter --cov-report=html

# Run specific test file
pytest tests/test_auto_updater.py

# Run specific test function
pytest tests/test_auto_updater.py::test_check_for_updates
```

### Writing Tests

- **Test Naming**: Use descriptive test names
- **Test Organization**: Group related tests in classes
- **Test Coverage**: Aim for high test coverage
- **Mocking**: Use mocks for external dependencies
- **Fixtures**: Use pytest fixtures for common setup

Example test:

```python
import pytest
from bounding_box_plotter.auto_updater import AutoUpdater

class TestAutoUpdater:
    def test_initialization(self):
        """Test AutoUpdater initialization"""
        updater = AutoUpdater("Test App", "1.0.0")
        assert updater.app_name == "Test App"
        assert updater.app_version == "1.0.0"
    
    def test_update_check(self):
        """Test update checking functionality"""
        updater = AutoUpdater("Test App", "1.0.0")
        result = updater.check_for_updates()
        assert isinstance(result, bool)
```

## 📚 Documentation

### Code Documentation

- **Docstrings**: Use Google-style docstrings
- **Type Hints**: Include type hints for all functions
- **Comments**: Add comments for complex logic
- **Examples**: Include usage examples in docstrings

Example docstring:

```python
def check_for_updates(self, force: bool = False) -> bool:
    """Check for available updates.
    
    Args:
        force: Force update check even if recently checked
        
    Returns:
        True if updates are available, False otherwise
        
    Raises:
        ConnectionError: If unable to connect to update server
        
    Example:
        >>> updater = AutoUpdater("MyApp", "1.0.0")
        >>> if updater.check_for_updates():
        ...     print("Updates available!")
    """
```

### Documentation Standards

- **README**: Keep README.md up to date
- **API Docs**: Document all public APIs
- **Examples**: Include practical examples
- **Changelog**: Update CHANGELOG.md for all changes

## 🔄 Pull Request Process

### Before Submitting

1. **Test Your Changes**: Ensure all tests pass
2. **Format Code**: Run Black and Flake8
3. **Type Check**: Run MyPy
4. **Update Documentation**: Update relevant docs
5. **Update Tests**: Add tests for new features

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] All existing tests pass

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changelog updated
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: Maintainers review the code
3. **Feedback**: Address any feedback or concerns
4. **Approval**: PR approved and merged

## 🐛 Bug Reports

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 10, macOS 11.0, Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- Application Version: [e.g., 2.0.0]

**Additional Information**
Screenshots, logs, or other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the requested feature

**Use Case**
Why this feature would be useful

**Proposed Implementation**
How you think it could be implemented

**Alternatives Considered**
Other approaches you've considered

**Additional Information**
Any other relevant information
```

## 🏷️ Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Update Process

1. **Update Version**: Modify `version.py`
2. **Update Changelog**: Add entry to `CHANGELOG.md`
3. **Create Tag**: `git tag v2.1.0`
4. **Push Tag**: `git push origin v2.1.0`

## 🔒 Security

### Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public issue
2. **Email**: security@raghavendrapratap.com
3. **Include**: Detailed description and steps to reproduce
4. **Response**: We'll respond within 48 hours

### Security Guidelines

- **Input Validation**: Always validate user input
- **Authentication**: Implement proper authentication
- **Authorization**: Check user permissions
- **Data Protection**: Protect sensitive data
- **Dependencies**: Keep dependencies updated

## 🌐 Localization

### Adding New Languages

1. **Create Translation File**: Add new language file
2. **Translate Strings**: Translate all user-facing strings
3. **Test**: Ensure translations work correctly
4. **Submit PR**: Submit translation as a PR

### Translation Guidelines

- **Context**: Provide context for translators
- **Variables**: Use placeholders for dynamic content
- **Length**: Consider UI space constraints
- **Cultural**: Be aware of cultural differences

## 📊 Performance

### Performance Guidelines

- **Profiling**: Profile code before optimization
- **Algorithms**: Choose efficient algorithms
- **Memory**: Minimize memory usage
- **Caching**: Use caching where appropriate
- **Async**: Use async operations for I/O

### Performance Testing

```bash
# Run performance tests
pytest tests/test_performance.py

# Profile specific functions
python -m cProfile -o profile.stats your_script.py
```

## 🤝 Community Guidelines

### Code of Conduct

- **Be Respectful**: Treat others with respect
- **Be Inclusive**: Welcome contributors from all backgrounds
- **Be Constructive**: Provide constructive feedback
- **Be Patient**: Understand that contributors have different skill levels

### Communication

- **Issues**: Use GitHub issues for discussions
- **Discussions**: Use GitHub Discussions for questions
- **Chat**: Join our community chat (if available)
- **Email**: Contact maintainers directly for sensitive matters

## 🎯 Contribution Areas

### High Priority

- **Bug Fixes**: Critical bugs and issues
- **Performance**: Performance improvements
- **Security**: Security enhancements
- **Documentation**: API documentation

### Medium Priority

- **New Features**: Useful new functionality
- **UI/UX**: User interface improvements
- **Testing**: Test coverage improvements
- **Localization**: New language support

### Low Priority

- **Nice-to-Have**: Convenience features
- **Cosmetic**: Visual improvements
- **Experimental**: Experimental features

## 📞 Getting Help

### Resources

- **Documentation**: Check the README and docs
- **Issues**: Search existing issues
- **Discussions**: Ask questions in discussions
- **Email**: Contact maintainers directly

### Contact Information

- **Maintainer**: Raghavendra Pratap
- **Email**: contact@raghavendrapratap.com
- **Website**: https://raghavendrapratap.com
- **GitHub**: https://github.com/raghavendrapratap

## 🙏 Recognition

### Contributors

All contributors are recognized in:

- **README**: Contributors section
- **Changelog**: Individual contributions
- **GitHub**: Contributor statistics
- **Releases**: Release notes

### Contribution Levels

- **Bronze**: 1-5 contributions
- **Silver**: 6-20 contributions
- **Gold**: 21+ contributions
- **Platinum**: Major contributions

---

Thank you for contributing to Bounding Box Plotter! Your contributions help make this tool better for everyone. 🎉 