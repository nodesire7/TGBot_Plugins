# Welcome Message Plugin

Sends customizable welcome messages to new group members.

## Features

- Template-based messages with variable substitution
- Clickable user mentions
- Optional rules button
- Auto-deletion after configurable time
- Silent mode support
- Admin commands for configuration

## Template Variables

Use these variables in your message template:

| Variable | Description | Example |
|----------|-------------|---------|
| `{user}` | User mention | @username or clickable link |
| `{user_id}` | Telegram user ID | 123456789 |
| `{username}` | Username (without @) | john_doe |
| `{chat_title}` | Group name | My Group |
| `{date}` | Current date/time | 2024-01-15 14:30 |

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| message_template | string | "Welcome {user}..." | Message template |
| parse_mode | string | "Markdown" | Formatting: None, Markdown, MarkdownV2, HTML |
| mention_user | boolean | true | Create clickable user mention |
| show_rules_button | boolean | false | Add rules button |
| rules_text | string | "" | Rules to show on button click |
| delete_after | integer | 0 | Auto-delete after seconds (0=never) |
| silent | boolean | false | Send without notification |
| ignore_bots | boolean | true | Skip welcome for bot users |

## Commands

| Command | Description | Admin Only |
|---------|-------------|------------|
| /setwelcome | Set welcome template | Yes |
| /setrules | Set group rules | Yes |
| /welcome | Preview welcome message | Yes |

## Examples

### Simple Welcome
```
message_template: "Welcome {user} to our group!"
```

### Detailed Welcome
```
message_template: |
  👋 Welcome {user}!

  📌 Please read our rules
  🆔 Your ID: {user_id}
  📅 Joined: {date}
```

### HTML Format
```
parse_mode: "HTML"
message_template: |
  <b>Welcome {user}!</b>

  Please check <a href="t.me/group_rules">our rules</a>
```

## Permissions Required

- `send_messages` - Send welcome messages
- `delete_messages` - Auto-delete after timeout
