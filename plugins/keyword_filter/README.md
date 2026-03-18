# Keyword Filter Plugin

Automatically delete messages containing blocked keywords or patterns.

## Features

- Block specific words (case-insensitive)
- Block regex patterns for advanced filtering
- Multiple actions: delete, warn, mute, kick
- Admin exemption
- Check edited messages
- Logging of deletions

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| blocked_words | array | [] | Words to block |
| blocked_patterns | array | [] | Regex patterns to block |
| action | string | "delete" | Action: delete, warn, mute, kick |
| warn_message | string | "Your message..." | Warning text |
| mute_duration | integer | 300 | Mute duration in seconds |
| warn_before_action | boolean | true | Warn before action |
| check_edits | boolean | true | Check edited messages |
| exempt_admins | boolean | true | Skip admin messages |
| log_deletions | boolean | true | Log for review |

## Commands

| Command | Description | Admin Only |
|---------|-------------|------------|
| /addword | Add blocked word | Yes |
| /removeword | Remove blocked word | Yes |
| /listwords | List all blocked | Yes |
| /addpattern | Add regex pattern | Yes |

## Examples

### Block Specific Words
```json
{
  "blocked_words": ["spam", "scam", "advertisement"]
}
```

### Block URL Patterns
```json
{
  "blocked_patterns": [
    "https?://(?!trusted\\.com).*",
    "t\\.me/\\w+"
  ]
}
```

### Block Phone Numbers
```json
{
  "blocked_patterns": [
    "\\+?\\d{1,3}[\\s-]?\\d{3,4}[\\s-]?\\d{4}",
    "\\d{3}[\\s-]?\\d{4}[\\s-]?\\d{4}"
  ]
}
```

## Actions

- **delete**: Only delete the message
- **warn**: Delete and send warning
- **mute**: Delete and mute user temporarily
- **kick**: Delete and remove user from group

## Permissions Required

- `delete_messages` - Delete violating messages
- `restrict_members` - Mute users
