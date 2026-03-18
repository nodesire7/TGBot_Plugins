# Plugin Development Guide

This guide covers everything you need to know to develop plugins for TGBot Admin.

## Prerequisites

- Python 3.10 or higher
- Understanding of async/await patterns
- Familiarity with Telegram Bot API concepts

## Plugin Structure

Every plugin must follow this directory structure:

```
plugins/
└── your_plugin_name/
    ├── manifest.json      # Required: Plugin metadata
    ├── main.py            # Required: Plugin implementation
    ├── README.md          # Required: Documentation
    ├── config_schema.json # Optional: Configuration schema
    ├── requirements.txt   # Optional: Python dependencies
    ├── tests/             # Optional: Unit tests
    │   └── test_main.py
    └── assets/            # Optional: Static assets
        └── icon.png
```

## Creating Your First Plugin

### 1. Create the Directory

```bash
mkdir -p plugins/my_plugin
```

### 2. Create manifest.json

```json
{
  "id": "my_plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "A brief description of what your plugin does",
  "main": "main.py",
  "hooks": ["on_message"],
  "permissions": ["send_messages"],
  "category": "utility",
  "license": "MIT"
}
```

### 3. Create main.py

```python
from typing import List
from plugin_sdk import Plugin, Context, User, Message, Permission

class MyPlugin(Plugin):
    """Plugin implementation"""

    id = "my_plugin"
    name = "My Plugin"
    version = "1.0.0"
    author = "Your Name"
    description = "A brief description"
    permissions = [Permission.SEND_MESSAGES]

    @Plugin.on_message(priority=0)
    async def handle_message(self, ctx: Context, message: Message):
        """Handle incoming messages"""
        if message.text and "hello" in message.text.lower():
            await ctx.reply("Hello there!")

# Required: Export the plugin class
plugin = MyPlugin
```

### 4. Create README.md

```markdown
# My Plugin

Brief description of functionality.

## Features

- Feature 1
- Feature 2

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| option1 | string | "value" | Description |

## Commands

- `/mycommand` - Description of command

## Installation

Install via TGBot Admin dashboard or manually copy to plugins directory.
```

## Available Hooks

Hooks are events that trigger your plugin's handlers:

| Hook | Description | Handler Signature |
|------|-------------|-------------------|
| `on_join` | User joins group | `(ctx, user: User)` |
| `on_leave` | User leaves group | `(ctx, user: User)` |
| `on_message` | New message received | `(ctx, message: Message)` |
| `on_command` | Command triggered | `(ctx, args: List[str])` |
| `on_callback` | Inline button callback | `(ctx, callback: CallbackQuery)` |
| `on_verify` | Verification event | `(ctx, user: User)` |
| `on_edited_message` | Message edited | `(ctx, message: Message)` |
| `on_error` | Error occurred | `(ctx, error: Exception)` |

## Context API

The `Context` object provides access to Telegram API and bot services:

### Messaging

```python
# Send message
await ctx.send_message("Hello!")

# Reply to message
await ctx.reply("Reply text")

# Delete message
await ctx.delete_message(message_id)
```

### User Management

```python
# Kick/ban user
await ctx.kick_user(user_id)
await ctx.ban_user(user_id)

# Mute user
await ctx.mute_user(user_id, duration=3600)

# Get member info
member = await ctx.get_chat_member(user_id)
```

### Data Storage

```python
# Redis cache
await ctx.cache_set("key", "value", expire=3600)
value = await ctx.cache_get("key")

# Database queries
results = await ctx.db_query("SELECT * FROM users WHERE id = $1", user_id)
```

## Configuration

Define configuration schema in `config_schema.json`:

```json
{
  "type": "object",
  "properties": {
    "enabled": {
      "type": "boolean",
      "default": true,
      "title": "Enable Plugin"
    },
    "message_template": {
      "type": "string",
      "default": "Hello, {user}!",
      "title": "Message Template"
    },
    "max_count": {
      "type": "integer",
      "default": 10,
      "minimum": 1,
      "maximum": 100,
      "title": "Maximum Count"
    }
  }
}
```

Access configuration in your plugin:

```python
enabled = ctx.get_config("enabled", True)
template = ctx.get_config("message_template", "Default message")
```

## Permissions

Declare required permissions in manifest:

```json
{
  "permissions": ["send_messages", "delete_messages", "kick_members"]
}
```

Available permissions:
- `read_messages` - Read messages in chat
- `send_messages` - Send messages
- `edit_messages` - Edit messages
- `delete_messages` - Delete messages
- `kick_members` - Kick/ban users
- `restrict_members` - Restrict user permissions
- `promote_members` - Promote users to admin
- `pin_messages` - Pin messages
- `manage_chat` - Manage chat settings

## Testing

Create tests in `tests/test_main.py`:

```python
import pytest
from plugin_sdk import Context, Message, Chat, User
from main import MyPlugin

@pytest.fixture
def plugin():
    return MyPlugin()

@pytest.fixture
def context():
    ctx = Context()
    ctx._chat_id = -1001234567890
    ctx._api_client = MockAPIClient()
    return ctx

@pytest.mark.asyncio
async def test_handle_message(plugin, context):
    message = Message(
        id=1,
        chat=Chat(id=-1001234567890, type="supergroup"),
        from_user=User(id=123, first_name="Test"),
        text="hello world"
    )
    await plugin.handle_message(context, message)
    # Assert expected behavior
```

## Publishing

1. Ensure all tests pass
2. Update version in manifest.json
3. Create a git tag: `git tag plugins/my_plugin/v1.0.0`
4. Push to repository
5. Create pull request to main marketplace repository

## Best Practices

1. **Keep it simple**: Single responsibility per plugin
2. **Handle errors gracefully**: Use try/except and log errors
3. **Validate inputs**: Never trust user input
4. **Document everything**: Clear README and code comments
5. **Test thoroughly**: Unit tests for all functionality
6. **Version properly**: Follow semantic versioning
7. **Respect rate limits**: Use cooldowns and rate limiting

## Getting Help

- Check existing plugins for examples
- Read the [API Reference](./API_REFERENCE.md)
- Open a [Discussion](../../discussions) for questions
