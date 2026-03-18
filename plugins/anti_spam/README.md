# Anti Spam

Multi-layer spam detection and prevention system.

## Features

- **Rate limiting**: Limit messages per minute per user
- **Duplicate detection**: Block repeated identical messages
- **Pattern matching**: Custom regex patterns for spam detection
- **New user protection**: Stricter rules for new members
- **Multiple actions**: Delete, mute, or kick spammers

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| max_messages_per_minute | integer | 5 | Max messages user can send per minute |
| max_identical_messages | integer | 3 | Max identical messages before action |
| action | string | delete | Action: delete, mute, or kick |
| mute_duration | integer | 300 | Mute duration in seconds |
| check_new_users | boolean | true | Apply stricter rules to new users |
| new_user_cooldown | integer | 300 | Cooldown period for new users |
| spam_patterns | array | [] | Regex patterns to detect spam |

## Usage Examples

### Basic protection

```json
{
  "max_messages_per_minute": 5,
  "max_identical_messages": 3,
  "action": "delete"
}
```

### Strict mode with custom patterns

```json
{
  "max_messages_per_minute": 3,
  "action": "mute",
  "mute_duration": 600,
  "spam_patterns": [
    "buy.*now",
    "click.*here.*free",
    "telegram\\.me/joinchat"
  ]
}
```

## Permissions

- `delete_messages` - Delete spam messages
- `restrict_members` - Mute spammers
- `kick_members` - Kick spammers

## License

MIT
