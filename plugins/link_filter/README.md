# Link Filter

Filter links in group messages based on domain whitelist/blacklist rules.

## Features

- **Whitelist mode**: Block all links except allowed domains
- **Blacklist mode**: Allow all links except blocked domains
- **Admin exemption**: Optionally exempt admins from filtering
- **Custom warnings**: Configurable warning messages

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| mode | string | blacklist | Filter mode: whitelist or blacklist |
| allowed_domains | array | [] | Domains allowed (whitelist mode) |
| blocked_domains | array | [] | Domains blocked (blacklist mode) |
| delete_message | boolean | true | Delete messages with filtered links |
| warn_user | boolean | true | Send warning to user |
| warning_message | string | "Links are not allowed..." | Warning message text |
| exempt_admins | boolean | true | Exempt admins from filtering |

## Usage Examples

### Whitelist Mode (Only allow specific domains)

```json
{
  "mode": "whitelist",
  "allowed_domains": ["github.com", "stackoverflow.com", "docs.python.org"]
}
```

### Blacklist Mode (Block specific domains)

```json
{
  "mode": "blacklist",
  "blocked_domains": ["spam-site.com", "ads.example.com"]
}
```

## Permissions

- `delete_messages` - Delete messages containing filtered links
- `restrict_members` - Optionally restrict repeat offenders

## License

MIT
