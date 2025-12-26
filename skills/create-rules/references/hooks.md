# Hooks Reference

Detailed documentation for Claude Code hooks.

## Hook Configuration

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

## Events Reference

### PreToolUse
Runs before a tool executes. Can block execution.

**Environment Variables:**
- `$TOOL_NAME` - Name of the tool
- `$TOOL_INPUT` - JSON input to the tool

**Output Format:**
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask"
  },
  "systemMessage": "Optional message for Claude"
}
```

Shorthand outputs: `approve`, `allow`, `deny`, `block`

### PostToolUse
Runs after a tool completes.

**Environment Variables:**
- `$TOOL_NAME` - Name of the tool
- `$TOOL_INPUT` - JSON input
- `$TOOL_OUTPUT` - Tool result

**Output:** Informational only (cannot block)

### Stop
Runs when Claude wants to stop working.

**Output:**
- `approve` - Allow stop
- `block` - Continue with feedback

### SessionStart
Runs when a Claude session begins.

**Output:** Content added to session context

### UserPromptSubmit
Runs when user submits a message.

**Environment Variables:**
- `$USER_PROMPT` - The user's message

**Output:** Can modify or add to the prompt

## Hook Types

### Command Hook
Execute a bash command:

```json
{
  "type": "command",
  "command": "bash .claude/hooks/validate.sh",
  "timeout": 30
}
```

### Prompt Hook
Use LLM for decision:

```json
{
  "type": "prompt",
  "prompt": "Analyze this operation. Return 'approve' or 'deny' with reason.",
  "timeout": 30
}
```

## Matcher Patterns

| Pattern | Matches |
|---------|---------|
| `"Write"` | Exact tool name |
| `"Write|Edit"` | Multiple tools (OR) |
| `"Bash"` | Bash tool |
| `"*"` | All tools/events |

## Hook Examples

### Block Dangerous Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo '$TOOL_INPUT' | grep -qE 'rm -rf|sudo|chmod 777' && echo 'deny' || echo 'approve'"
          }
        ]
      }
    ]
  }
}
```

### Prevent Credential Leaks

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if the content contains: API keys, passwords, tokens, private keys. Return 'deny' if found, 'approve' otherwise."
          }
        ]
      }
    ]
  }
}
```

### Require Tests Before Stop

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review the session. If code was modified but tests weren't run, return 'block' explaining tests are needed. Otherwise 'approve'."
          }
        ]
      }
    ]
  }
}
```

### Load Project Context

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "cat .claude/context.md 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Auto-Format on Write

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write \"$(echo '$TOOL_INPUT' | jq -r '.file_path')\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Lint Check Before Commit

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo '$TOOL_INPUT' | grep -q 'git commit' && npm run lint --silent && echo 'approve' || echo 'approve'"
          }
        ]
      }
    ]
  }
}
```

## Hook Script Template

Create `.claude/hooks/validate.sh`:

```bash
#!/bin/bash
# PreToolUse validation hook

TOOL_NAME="$1"
TOOL_INPUT="$2"

# Check for dangerous patterns
if echo "$TOOL_INPUT" | grep -qE 'sensitive-pattern'; then
    echo '{"decision": "deny", "reason": "Blocked: sensitive pattern"}'
    exit 0
fi

# Check file path restrictions
FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty')
if [[ -n "$FILE_PATH" && "$FILE_PATH" == /etc/* ]]; then
    echo '{"decision": "deny", "reason": "Cannot modify system files"}'
    exit 0
fi

# Allow by default
echo '{"decision": "approve"}'
exit 0
```

Make executable:
```bash
chmod +x .claude/hooks/validate.sh
```

## Debugging Hooks

### Test Hook Output
```bash
# Test command hook manually
TOOL_NAME="Write" TOOL_INPUT='{"file_path":"test.txt"}' bash .claude/hooks/validate.sh
```

### Check JSON Syntax
```bash
# Validate settings.json
cat .claude/settings.json | jq .
```

### View Hook Execution
Hooks output is visible in Claude's response when they block operations.

## Best Practices

1. **Keep hooks fast** - Use timeouts, avoid slow operations
2. **Default to allow** - Only block when necessary
3. **Provide clear messages** - Explain why operations are blocked
4. **Test thoroughly** - Validate hooks before relying on them
5. **Use command for simple checks** - Prompt for complex decisions
6. **Handle errors gracefully** - Use `|| true` to avoid failures
