# Stats Reporter

Generate and send periodic statistics reports for your group.

## Features

- **Message tracking**: Count messages per chat
- **User activity**: Track most active users
- **Membership stats**: Track joins and leaves
- **Periodic reports**: Auto-send reports to a channel

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| report_channel | integer | - | Channel ID to send reports |
| report_interval_hours | integer | 24 | Hours between reports |
| include_message_stats | boolean | true | Include message counts |
| include_user_stats | boolean | true | Include user activity |
| include_verification_stats | boolean | true | Include join/leave stats |
| top_users_count | integer | 5 | Number of top users to show |

## Commands

| Command | Description |
|---------|-------------|
| /stats | Show current statistics |
| /topusers | Show most active users |

## Usage Examples

### View current stats

```
/stats
```

Output:
```
📊 Statistics for Chat -1001234567890

📨 Messages: 1523
➕ Joins: 45
➖ Leaves: 12

👤 Top Active Users:
  1. User 123456789: 234 messages
  2. User 987654321: 189 messages
  3. User 456789123: 156 messages
```

### Periodic reports

Set `report_channel` to enable automatic daily reports:

```json
{
  "report_channel": -1001234567890,
  "report_interval_hours": 24
}
```

## Permissions

- `send_messages` - Send statistics reports

## License

MIT
