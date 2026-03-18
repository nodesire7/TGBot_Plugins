# Flood Protection Plugin

Protect groups from message flooding with rate limiting and duplicate detection.

## Features

- Per-user rate limiting
- Configurable message threshold and time window
- Duplicate message detection
- Multiple actions: warn, mute, kick
- Admin exemption
- Statistics tracking

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| max_messages | integer | 5 | Max messages in time window |
| time_window | integer | 10 | Time window in seconds |
| action | string | "mute" | Action: warn, mute, kick |
| mute_duration | integer | 300 | Mute duration in seconds |
| warn_message | string | "Please slow down!" | Warning message |
| check_duplicates | boolean | true | Enable duplicate detection |
| duplicate_threshold | integer | 3 | Duplicates before action |
| exempt_admins | boolean | true | Skip admin messages |
| delete_flood_messages | boolean | true | Delete triggering messages |

## How It Works

### Rate Limiting

1. Track message timestamps per user
2. Count messages within sliding time window
3. Trigger action when threshold exceeded

Example: `max_messages=5`, `time_window=10`
- User can send 5 messages in 10 seconds
- 6th message triggers flood protection

### Duplicate Detection

1. Hash message content
2. Track duplicate count per user
3. Trigger action when threshold exceeded

## Commands

| Command | Description | Admin Only |
|---------|-------------|------------|
| /floodstats | View statistics | Yes |
| /resetflood | Reset user counter | Yes |

## Example Configuration

### Strict Mode
```json
{
  "max_messages": 3,
  "time_window": 5,
  "action": "kick",
  "check_duplicates": true,
  "duplicate_threshold": 2
}
```

### Lenient Mode
```json
{
  "max_messages": 10,
  "time_window": 30,
  "action": "warn",
  "check_duplicates": false
}
```

## Permissions Required

- `delete_messages` - Delete flood messages
- `restrict_members` - Mute users
