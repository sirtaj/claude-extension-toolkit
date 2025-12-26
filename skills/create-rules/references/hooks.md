# Hooks Reference

## Configuration

Add to `settings.json` or `settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...],
    "SessionStart": [...],
    "UserPromptSubmit": [...]
  }
}
```

## Events

| Event | When | Can Block | Env Vars |
|-------|------|-----------|----------|
| `PreToolUse` | Before tool | Yes | `$TOOL_NAME`, `$TOOL_INPUT` |
| `PostToolUse` | After tool | No | `$TOOL_NAME`, `$TOOL_INPUT`, `$TOOL_OUTPUT` |
| `Stop` | Agent stopping | Yes | - |
| `SessionStart` | Session begins | No | - |
| `UserPromptSubmit` | User message | No | `$USER_PROMPT` |

## Hook Types

**Command:** `{"type": "command", "command": "bash script.sh", "timeout": 30}`

**Prompt:** `{"type": "prompt", "prompt": "Analyze and return 'approve' or 'deny'."}`

## Output

- `approve` / `allow` - Permit action
- `deny` / `block` - Block with message

## Examples

### Block Dangerous Commands
```json
{
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "command": "echo '$TOOL_INPUT' | grep -qE 'rm -rf|sudo' && echo 'deny' || echo 'approve'"
  }]
}
```

### Credential Check
```json
{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "prompt",
    "prompt": "Check for API keys, passwords, tokens. Return 'deny' if found, 'approve' if clean."
  }]
}
```

### Load Context on Start
```json
{
  "matcher": "*",
  "hooks": [{
    "type": "command",
    "command": "cat .claude/context.md 2>/dev/null || true"
  }]
}
```

## Best Practices

- Keep hooks fast (use timeouts)
- Default to allow
- Provide clear block messages
- Use `|| true` for graceful failures
