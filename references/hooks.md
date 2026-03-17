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

For plugins, use `hooks/hooks.json` in the plugin directory (see Plugin Hooks section).

## Hook Events

| Event | When | Can Block | Has Matcher | Matcher Values |
|-------|------|-----------|-------------|----------------|
| `SessionStart` | Session begins/resumes | No | Yes | startup, resume, clear, compact |
| `UserPromptSubmit` | User sends message | Yes | No | - |
| `PreToolUse` | Before tool execution | Yes | Yes | Tool name |
| `PermissionRequest` | Permission prompt shown | Yes | Yes | Tool name |
| `PostToolUse` | After tool success | No | Yes | Tool name |
| `PostToolUseFailure` | After tool failure | No | Yes | Tool name |
| `Notification` | System notification | No | Yes | permission_prompt, idle_prompt, auth_success, elicitation_dialog |
| `SubagentStart` | Subagent launched | No | Yes | Agent type name |
| `SubagentStop` | Subagent finished | Yes | Yes | Agent type name |
| `Stop` | Agent finishes | Yes | No | - |
| `PreCompact` | Before context compaction | No | Yes | manual, auto |
| `SessionEnd` | Session terminates | No | Yes | clear, logout, prompt_input_exit, bypass_permissions_disabled, other |
| `PostCompact` | After context compaction | No | Yes | manual, auto |
| `TeammateIdle` | Teammate agent is idle | Yes | No | - |
| `TaskCompleted` | Background task completes | Yes | No | - |
| `InstructionsLoaded` | CLAUDE.md/instructions loaded | No | No | - |
| `ConfigChange` | Settings/config modified | Yes | Yes | user_settings, project_settings, local_settings, policy_settings, skills |
| `WorktreeCreate` | Git worktree created | Yes | No | - |
| `WorktreeRemove` | Git worktree removed | No | No | - |
| `Elicitation` | Before showing elicitation dialog | Yes | No | - |
| `ElicitationResult` | After user responds to elicitation | Yes | No | - |
| `Setup` | CLI initialization/maintenance | No | Yes | --init, --init-only, --maintenance |

## Hook Types

### Command Hook

Executes a shell command:

```json
{
  "type": "command",
  "command": "/path/to/script.sh",
  "timeout": 30,
  "statusMessage": "Running check...",
  "async": false
}
```

**Fields:**
- `command` (required): Shell command to execute
- `timeout` (optional): Timeout in seconds
- `statusMessage` (optional): Custom spinner message during execution
- `async` (optional): Run in background without blocking

### Prompt Hook

Uses Claude to evaluate:

```json
{
  "type": "prompt",
  "prompt": "Check if this action is safe. Return 'allow' or 'deny' with reason.",
  "model": "haiku",
  "once": true
}
```

**Fields:**
- `prompt` (required): Instructions for Claude
- `model` (optional): Model to use (sonnet, opus, haiku)
- `once` (optional): Run only once per session (for skills/agents)

### Agent Hook

Spawns a subagent with tool access:

```json
{
  "type": "agent",
  "prompt": "Verify the code changes are safe and follow best practices.",
  "model": "sonnet"
}
```

**Fields:**
- `prompt` (required): Instructions for the agent
- `model` (optional): Model to use

### HTTP Hook

Sends an HTTP request to a URL:

```json
{
  "type": "http",
  "url": "https://example.com/hooks/notify",
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  },
  "allowedEnvVars": ["API_TOKEN"],
  "timeout": 30,
  "statusMessage": "Sending notification..."
}
```

**Fields:**
- `url` (required): HTTP endpoint URL
- `headers` (optional): Request headers (supports env var interpolation)
- `allowedEnvVars` (optional): Environment variables to expose to the hook
- `timeout` (optional): Timeout in seconds
- `statusMessage` (optional): Custom spinner message

## Matchers

For events with matcher support:

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

### Common Fields (All Hooks)

All hooks receive these fields:

```json
{
  "hook_event_name": "PreToolUse",
  "session_id": "abc123...",
  "transcript_path": "/path/to/conversation.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "agent_id": "optional-agent-id",
  "agent_type": "optional-agent-type"
}
```

### PreToolUse Input

```json
{
  "hook_event_name": "PreToolUse",
  "session_id": "...",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/test"
  }
}
```

PreToolUse hooks can also return `additionalContext` (string injected into context) and `updatedInput` (modified tool input object) via `hookSpecificOutput`.

### PostToolUse Input

```json
{
  "hook_event_name": "PostToolUse",
  "session_id": "...",
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
  "hook_event_name": "UserPromptSubmit",
  "session_id": "...",
  "user_prompt": "The user's message text"
}
```

### SubagentStop Input

```json
{
  "hook_event_name": "SubagentStop",
  "session_id": "...",
  "agent_type": "code-reviewer",
  "agent_result": "..."
}
```

### TeammateIdle Input

```json
{
  "hook_event_name": "TeammateIdle",
  "session_id": "...",
  "agent_id": "teammate-123",
  "agent_type": "code-reviewer"
}
```

### ConfigChange Input

```json
{
  "hook_event_name": "ConfigChange",
  "session_id": "...",
  "config_type": "project_settings",
  "changed_keys": ["hooks", "permissions"]
}
```

### Elicitation Input

```json
{
  "hook_event_name": "Elicitation",
  "session_id": "...",
  "elicitation_type": "question",
  "elicitation_content": "..."
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
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
```

## Hook Output

**Note:** Top-level `decision`/`reason` fields in PreToolUse output are deprecated. Use `hookSpecificOutput.permissionDecision` instead.

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

### SubagentStop Decision

SubagentStop can prevent the subagent from stopping (exit 2):

```bash
# Prevent subagent from stopping if work incomplete
if [ "$WORK_INCOMPLETE" = "true" ]; then
    echo "Agent has not completed all tasks"
    exit 2
fi
exit 0
```

### PermissionRequest Decision

PermissionRequest hooks can return `updatedPermissions` to modify permission rules:

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow",
    "updatedPermissions": [
      {"tool": "Bash", "permission": "allow", "pattern": "npm test:*"}
    ]
  }
}
```

### PostToolUse Modification

PostToolUse hooks for MCP tools can return modified output:

```json
{
  "hookSpecificOutput": {
    "updatedMCPToolOutput": "modified output content"
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
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "cat .claude/context.md 2>/dev/null || true"
      }]
    }]
  }
}
```

**Tip:** SessionStart hooks can use `CLAUDE_ENV_FILE` — write `KEY=VALUE` lines to this file to persist environment variables for the session.

### Credential Detection

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "prompt",
        "prompt": "Check if the content contains API keys, passwords, or tokens. Return 'allow' if clean, 'deny' if credentials found."
      }]
    }]
  }
}
```

## Plugin Hooks

In plugin directory, create `hooks/hooks.json` with a `hooks` wrapper:

```json
{
  "description": "What these hooks do",
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/check.sh",
        "timeout": 30
      }]
    }]
  }
}
```

**Important:** Plugin hooks.json requires:
1. A `hooks` wrapper object containing the event handlers
2. Optional `description` field at the top level

Use `${CLAUDE_PLUGIN_ROOT}` for portable paths.

## Best Practices

1. **Keep hooks fast** - Set reasonable timeouts
2. **Default to allow** - Only block when necessary
3. **Provide clear messages** - Users should understand why blocked
4. **Handle errors gracefully** - Use `|| true` for optional checks
5. **Use JSON parsing** - Don't rely on deprecated env vars
6. **Test thoroughly** - Hook failures can disrupt workflow
7. **Use statusMessage** - Provide feedback during long-running hooks
8. **Disable all hooks** - Use `disableAllHooks: true` in settings to temporarily disable
9. **SessionEnd timeout** - Set `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` env var for cleanup hooks
10. **Deduplication** - Identical hooks (same event, matcher, handler) are deduplicated automatically
