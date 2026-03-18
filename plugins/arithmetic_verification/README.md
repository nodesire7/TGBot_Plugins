# Arithmetic Verification Plugin

Math-based captcha verification for new group members.

## Features

- Generates random arithmetic problems (addition, subtraction, multiplication, division)
- Multiple difficulty levels (easy, medium, hard)
- Inline button answers for quick verification
- Text input support as alternative
- Configurable timeout and attempt limits
- Auto-kick on failure or timeout

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| difficulty | string | "easy" | Problem complexity: easy, medium, hard |
| timeout_seconds | integer | 60 | Time limit for verification |
| max_attempts | integer | 3 | Attempts before kick |
| welcome_message | string | "Welcome! Please solve..." | Message before the problem |
| success_message | string | "Verification successful!" | Message after passing |
| kick_on_fail | boolean | true | Kick users who fail |

## Difficulty Levels

### Easy
- Numbers 1-10
- Operations: +, -

### Medium
- Numbers 1-50
- Operations: +, -, *

### Hard
- Numbers 1-100
- Operations: +, -, *, /

## Permissions Required

- `send_messages` - Send verification prompts
- `delete_messages` - Clean up verification messages
- `restrict_members` - Restrict users until verified

## Example

When a user joins, they see:

```
@username

Welcome! Please solve this math problem.

7 + 5 = ?

[2] [12] [8] [15]
```

## Installation

1. Install via TGBot Admin dashboard
2. Configure difficulty and timeout
3. Enable for desired groups
