# Auto Reply

Automatic reply to messages based on keywords, patterns, or triggers.

## Features

- **Multiple trigger types**: exact match, contains, regex, starts with
- **Variables**: Use {user}, {username}, {user_id}, {chat_id} in responses
- **Cooldown**: Prevent spam from repeated triggers
- **Admin exemption**: Don't auto-reply to admins

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| replies | array | [] | List of reply rules |
| cooldown_seconds | integer | 5 | Cooldown between replies to same user |
| random_responses | boolean | false | Pick random matching response |
| exempt_admins | boolean | true | Don't reply to admin messages |

### Reply Rule Structure

```json
{
  "trigger": "hello",
  "trigger_type": "contains",
  "response": "Hi {user}!",
  "case_sensitive": false,
  "reply_to_message": true
}
```

## Trigger Types

| Type | Description | Example |
|------|-------------|---------|
| exact | Exact match only | "help" matches "help" only |
| contains | Text contains trigger | "help" matches "I need help" |
| startswith | Text starts with trigger | "hello" matches "hello there" |
| regex | Regular expression match | "^/\\w+" matches commands |

## Usage Examples

### Simple keyword replies

```json
{
  "replies": [
    {"trigger": "hello", "trigger_type": "contains", "response": "Hi {user}! 👋"},
    {"trigger": "bye", "trigger_type": "contains", "response": "Goodbye {user}!"}
  ]
}
```

### Regex patterns

```json
{
  "replies": [
    {"trigger": "^/help", "trigger_type": "regex", "response": "How can I help you?"},
    {"trigger": "\\bprice\\b", "trigger_type": "regex", "response": "Check our pricing at..."}
  ]
}
```

## Commands

| Command | Description |
|---------|-------------|
| /addreply trigger \| response | Add a new reply rule |
| /delreply <index> | Delete a reply rule |
| /listreplies | List all reply rules |

## Permissions

- `send_messages` - Send reply messages

## License

MIT
