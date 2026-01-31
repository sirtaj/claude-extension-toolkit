# Hooks Reference

Complete reference for Claude Code hooks system.

## Configuration

Hooks are configured in `settings.json` or `settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...],
    "SessionStart": [...],
    "Stop": [...]
  }
}
```

For plugins, use `hooks/hooks.json` in the plugin directory.

## Hook Events

| Event | When | Can Block | Has Matcher |
|-------|------|-----------|-------------|
| `SessionStart` | Session begins | No | No |
| `UserPromptSubmit` | User sends message | Yes | No |
| `PreToolUse` | Before tool execution | Yes | Yes |
| `PermissionRequest` | Permission prompt shown | Yes | No |
| `PostToolUse` | After tool success | No | Yes |
| `PostToolUseFailure` | After tool failure | No | Yes |
| `Notification` | System notification | No | No |
| `SubagentStart` | Subagent launched | No | No |
| `SubagentStop` | Subagent finished | No | No |
| `Stop` | Session ending | Yes | No |
| `PreCompact` | Before context compaction | No | No |
| `SessionEnd` | Session complete | No | No |

## Hook Types

### Command Hook

Executes a shell command:

```json
{
  "type": "command",
  "command": "/path/to/script.sh",
  "timeout": 30
}
```

### Prompt Hook

Uses Claude to evaluate:

```json
{
  "type": "prompt",
  "prompt": "Check if this action is safe. Return 'allow' or 'deny' with reason."
}
```

## Matchers

For PreToolUse, PostToolUse, and PostToolUseFailure:

```json
{
  "matcher": "Bash|Write|Edit",
  "hooks": [...]
}
```

| Pattern | Matches |
|---------|---------|
| `Bash` | Bash tool only |
| `Bash\|Write` | Bash or Write |
| `*` | All tools |

## JSON Input (stdin)

**Hook scripts receive JSON via stdin, not environment variables.**

### PreToolUse Input

```json
{
  "hook_type": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/test"
  }
}
```

### PostToolUse Input

```json
{
  "hook_type": "PostToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.py",
    "content": "..."
  },
  "tool_output": {
    "success": true
  }
}
```

### UserPromptSubmit Input

```json
{
  "hook_type": "UserPromptSubmit",
  "user_prompt": "The user's message text"
}
```

## Parsing JSON in Scripts

Use `jq` to extract fields:

```bash
#!/bin/bash
# Read JSON from stdin
INPUT=$(cat)

# Extract fields
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
```

## Hook Output

### Allowing Actions

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow"
  }
}
```

Or simply exit 0 with no output.

### Blocking Actions

Exit code 2 blocks with message:

```bash
echo "Blocked: dangerous command detected"
exit 2
```

Or use JSON format:

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "message": "Blocked: dangerous command detected"
  }
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Allow (or no output needed) |
| 2 | Block with stdout as message |
| Other | Error (logged, action allowed) |

## Examples

### Block Dangerous Commands

```bash
#!/bin/bash
set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Check for dangerous patterns
if echo "$COMMAND" | grep -qE 'rm\s+-rf|sudo|chmod\s+777'; then
    echo "Blocked: potentially dangerous command"
    exit 2
fi

exit 0
```

### Lint Python on Save

```bash
#!/bin/bash
set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only check Python files
if [[ "$FILE_PATH" != *.py ]]; then
    exit 0
fi

# Run linter
if ! ruff check "$FILE_PATH" 2>&1; then
    echo "Ruff found issues in $FILE_PATH"
fi

exit 0
```

### Load Context on Start

```json
{
  "SessionStart": [{
    "type": "command",
    "command": "cat .claude/context.md 2>/dev/null || true"
  }]
}
```

### Credential Detection

```json
{
  "PreToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "prompt",
      "prompt": "Check if the content contains API keys, passwords, or tokens. Return 'allow' if clean, 'deny' if credentials found."
    }]
  }]
}
```

## Plugin Hooks

In plugin directory, create `hooks/hooks.json`:

```json
{
  "PostToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "command",
      "command": "${CLAUDE_PLUGIN_ROOT}/hooks/check.sh",
      "timeout": 30
    }]
  }]
}
```

Use `${CLAUDE_PLUGIN_ROOT}` for portable paths.

## Best Practices

1. **Keep hooks fast** - Set reasonable timeouts
2. **Default to allow** - Only block when necessary
3. **Provide clear messages** - Users should understand why blocked
4. **Handle errors gracefully** - Use `|| true` for optional checks
5. **Use JSON parsing** - Don't rely on deprecated env vars
6. **Test thoroughly** - Hook failures can disrupt workflow
