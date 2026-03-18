# Plugin Standards

This document defines the official standards for TGBot plugins.

## Versioning

Plugins must follow [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE]

Examples:
1.0.0
2.1.3
1.0.0-beta.1
2.0.0-rc.2
```

### Version Compatibility

Specify compatibility with TGBot Admin:

```json
{
  "min_bot_version": "1.0.0",
  "max_bot_version": "2.0.0"
}
```

## Manifest Standards

### Required Fields

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | string | lowercase, 2-64 chars, `^[a-z][a-z0-9_]*$` |
| `name` | string | 1-100 chars |
| `version` | string | semver format |
| `author` | string | 1-100 chars |
| `description` | string | 10-500 chars |
| `main` | string | default: "main.py" |
| `hooks` | array | at least 1 hook |

### ID Naming Convention

- Start with lowercase letter
- Use underscores for separation
- Be descriptive but concise
- No reserved names: `system`, `core`, `admin`, `test`

Good: `anti_spam`, `welcome_message`, `arithmetic_verification`
Bad: `AS`, `welcomeMessage`, `spam-filter`, `test_plugin`

## Directory Structure

### Required Files

```
your_plugin/
├── manifest.json    # Plugin metadata (required)
├── main.py          # Entry point (required)
└── README.md        # Documentation (required)
```

### Optional Files

```
your_plugin/
├── config_schema.json    # Configuration schema
├── requirements.txt      # Python dependencies
├── LICENSE              # License file
├── tests/
│   ├── __init__.py
│   └── test_main.py     # Unit tests
└── assets/
    └── icon.png         # Plugin icon (64x64 recommended)
```

## Code Standards

### Python Version

- Minimum: Python 3.10
- Use type hints throughout
- Async/await for all I/O operations

### Code Style

- Follow PEP 8
- Use `black` for formatting
- Use `isort` for import sorting
- Maximum line length: 100 characters

### Plugin Class

```python
from plugin_sdk import Plugin, Context, Permission

class MyPlugin(Plugin):
    # Required: Metadata attributes
    id = "my_plugin"
    name = "My Plugin"
    version = "1.0.0"
    author = "Author Name"
    description = "Plugin description"
    permissions = [Permission.SEND_MESSAGES]

    # Optional: Configuration schema
    config_schema = {...}

    # Handlers with decorators
    @Plugin.on_message()
    async def handle_message(self, ctx: Context, message: Message):
        pass

# Required: Export plugin class
plugin = MyPlugin
```

### Error Handling

```python
import logging

logger = logging.getLogger(__name__)

class MyPlugin(Plugin):
    @Plugin.on_message()
    async def handle_message(self, ctx: Context, message: Message):
        try:
            # Plugin logic
            pass
        except Exception as e:
            logger.error(f"Error in {self.id}: {e}", exc_info=True)
            # Optionally notify admins
```

## Configuration Schema

### JSON Schema Format

Follow JSON Schema draft-07:

```json
{
  "type": "object",
  "properties": {
    "option_name": {
      "type": "string",
      "title": "Display Name",
      "description": "Helpful description",
      "default": "default_value"
    }
  },
  "required": ["required_option"]
}
```

### Supported Types

- `string` - Text input
- `integer` - Whole number
- `number` - Decimal number
- `boolean` - True/false
- `array` - List of items
- `object` - Nested configuration

### Validation

Include validation constraints:

```json
{
  "type": "string",
  "minLength": 1,
  "maxLength": 100,
  "pattern": "^[a-zA-Z0-9]+$"
}
```

```json
{
  "type": "integer",
  "minimum": 0,
  "maximum": 100,
  "multipleOf": 5
}
```

## Documentation Standards

### README.md Structure

```markdown
# Plugin Name

Brief one-line description.

## Features

- Feature 1
- Feature 2

## Installation

Installation instructions.

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|

## Commands

List of commands if any.

## Permissions

Required permissions and why.

## Examples

Usage examples.

## Changelog

### 1.0.0
- Initial release

## License

License information.
```

## Security Requirements

### Permission Declaration

All permissions must be declared:

```json
{
  "permissions": ["send_messages", "delete_messages"]
}
```

### Sensitive Data

- Never log sensitive information
- Use `ctx.cache_*` for temporary data
- Encrypt stored secrets

### Input Validation

Always validate user input:

```python
from plugin_sdk.utils import parse_command

@Plugin.on_command("mycommand")
async def my_command(self, ctx: Context, args: List[str]):
    if not args:
        await ctx.reply("Usage: /mycommand <argument>")
        return

    # Validate args
    if len(args[0]) > 100:
        await ctx.reply("Argument too long")
        return
```

## Testing Requirements

### Minimum Coverage

- 80% code coverage for new plugins
- All handlers must have tests
- Configuration validation must be tested

### Test Structure

```python
import pytest
from plugin_sdk import Context, Message, Chat, User

@pytest.fixture
def plugin():
    from main import MyPlugin
    return MyPlugin()

class TestMyPlugin:
    @pytest.mark.asyncio
    async def test_handler(self, plugin):
        # Test implementation
        pass
```

## License

Default license is MIT. Specify in manifest:

```json
{
  "license": "MIT"
}
```

Supported licenses:
- MIT
- Apache-2.0
- GPL-3.0
- BSD-3-Clause
