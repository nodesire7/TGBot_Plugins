# Contributing to TGBot Plugin Marketplace

Thank you for your interest in contributing!

## Ways to Contribute

- Submit a new plugin
- Improve existing plugins
- Report bugs
- Suggest features
- Improve documentation

## Submitting a Plugin

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/TGBot_Plugins.git
cd TGBot_Plugins
```

### 2. Create Your Plugin

```bash
mkdir -p plugins/your_plugin_name
```

### 3. Implement Plugin

Follow the [Development Guide](./DEVELOPMENT.md) and [Standards](./STANDARDS.md).

### 4. Test Locally

```bash
# Validate manifest
python scripts/validate_plugin.py plugins/your_plugin_name

# Run plugin tests
pytest plugins/your_plugin_name/tests/
```

### 5. Submit Pull Request

1. Create a feature branch
2. Commit your changes
3. Push to your fork
4. Open a pull request

## Pull Request Guidelines

### PR Title Format

```
[Plugin] Add/update/fix: plugin_name

Examples:
[Plugin] Add: anti_spam
[Plugin] Update: welcome_message to v2.0.0
[Plugin] Fix: keyword_filter regex bug
```

### PR Description

Include:

- What changes were made
- Why these changes were needed
- How to test the changes
- Any breaking changes

### Checklist

- [ ] manifest.json is valid
- [ ] README.md is complete
- [ ] Tests pass
- [ ] Code follows style guide
- [ ] No sensitive data included

## Code Review Process

1. Automated validation runs
2. Maintainer review
3. Feedback addressed
4. Approval and merge

## Reporting Issues

### Bug Reports

Include:

- Plugin name and version
- TGBot Admin version
- Steps to reproduce
- Expected vs actual behavior
- Logs (remove sensitive data)

### Feature Requests

Include:

- Use case description
- Proposed solution
- Alternative solutions considered

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install SDK
pip install -e /path/to/TGBot_Admin/bot

# Install dev dependencies
pip install pytest pytest-asyncio black isort
```

## Questions?

Open a [Discussion](../../discussions) for general questions.
