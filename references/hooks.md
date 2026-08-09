# Hooks Reference

Complete reference for Claude Code hooks system.

Verified against Claude Code 2.1.226 docs (2026-08-09).
Canonical docs: https://code.claude.com/docs/en/hooks

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

Listed in lifecycle order. "Can block" means the hook can stop the action
(exit 2 or a JSON decision).

| Event | When | Can Block | Matcher filters |
|-------|------|-----------|-----------------|
| `SessionStart` | Session begins/resumes | No | startup, resume, clear, compact |
| `Setup` | `--init-only`, or `--init`/`--maintenance` in `-p` mode | No | init, maintenance |
| `UserPromptSubmit` | User sends message | Yes | — |
| `UserPromptExpansion` | A typed command expands into a prompt | Yes | Command name |
| `PreToolUse` | Before tool execution | Yes | Tool name |
| `PermissionRequest` | Tool call needs a permission decision | Yes | Tool name |
| `PermissionDenied` | Auto-mode classifier denied a call | No | Tool name |
| `PostToolUse` | After tool success | No | Tool name |
| `PostToolUseFailure` | After tool failure | No | Tool name |
| `PostToolBatch` | After a parallel tool batch resolves | Yes | — |
| `Notification` | System notification | No | permission_prompt, idle_prompt, auth_success, elicitation_dialog |
| `MessageDisplay` | While assistant text renders (display-only) | No | — |
| `SubagentStart` | Subagent launched | No | Agent type name |
| `SubagentStop` | Subagent finished | Yes | Agent type name |
| `TaskCreated` | Task being created via `TaskCreate` | Yes | — |
| `TaskCompleted` | Task being marked completed | Yes | — |
| `Stop` | Agent finishes responding | Yes | — |
| `StopFailure` | Turn ends due to an API error | No | rate_limit, overloaded, … |
| `TeammateIdle` | Teammate agent about to go idle | Yes | — |
| `InstructionsLoaded` | CLAUDE.md / `.claude/rules/*.md` loaded | No | Load reason |
| `ConfigChange` | Settings/config modified | Yes | user_settings, project_settings, local_settings, policy_settings, skills |
| `CwdChanged` | Working directory changes (e.g. `cd`) | No | — |
| `DirectoryAdded` | Directory added via `/add-dir` or SDK | No | slash_command, register_repo_root |
| `FileChanged` | Watched file changes on disk | No | Literal filenames to watch |
| `WorktreeCreate` | Git worktree created | Yes | — |
| `WorktreeRemove` | Git worktree removed | No | — |
| `PreCompact` | Before context compaction | Yes | manual, auto |
| `PostCompact` | After context compaction | No | manual, auto |
| `Elicitation` | MCP server requests user input | Yes | MCP server name |
| `ElicitationResult` | After the user responds | Yes | MCP server name |
| `SessionEnd` | Session terminates | No | clear, resume, logout, prompt_input_exit, bypass_permissions_disabled, other |

## Hook Types

Five handler types: `command`, `http`, `mcp_tool`, `prompt`, and `agent`.

### Common Fields (all types)

| Field | Required | Purpose |
|-------|----------|---------|
| `type` | yes | `command`, `http`, `mcp_tool`, `prompt`, or `agent` |
| `if` | no | Permission-rule filter, e.g. `"Bash(git *)"` or `"Edit(*.ts)"`. Exactly one rule; no `&&`/`\|\|` |
| `timeout` | no | Seconds. Defaults: 600 for command/http/mcp_tool, 30 for prompt, 60 for agent |
| `statusMessage` | no | Custom spinner message |
| `once` | no | Run once per session. **Only honored in skill frontmatter** — ignored in settings files and agent frontmatter |

The `if` filter is best-effort and fails open when a Bash command can't be
parsed. Use the permission system, not a hook, to enforce a boundary.

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
- `command` (required): shell command, or the executable to spawn when `args` is set
- `args` (optional): argument list. Its presence switches to **exec form** — no shell, each element passed verbatim
- `async` (optional): run in background without blocking
- `asyncRewake` (optional): run in background and wake Claude on exit code 2. Implies `async`
- `shell` (optional): `bash` (default) or `powershell`

Set `args` whenever the hook references a path placeholder — exec form needs no
quoting for paths with spaces:

```json
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"]
}
```

### MCP Tool Hook

Calls a tool on an already-connected MCP server. Its text output is treated like
command-hook stdout.

```json
{
  "type": "mcp_tool",
  "server": "my_server",
  "tool": "security_scan",
  "input": { "file_path": "${tool_input.file_path}" }
}
```

**Fields:**
- `server` (required): configured server name. For a plugin-bundled server, the scoped name `plugin:<plugin-name>:<server-name>`
- `tool` (required): tool to call
- `input` (optional): arguments; string values support `${path}` substitution from the hook's JSON input

`SessionStart` and `Setup` usually fire before MCP servers finish connecting, so
hooks on those events should expect a "not connected" result.

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

How a matcher is evaluated depends on the characters it contains:

| Matcher value | Evaluated as |
|---------------|--------------|
| `*`, `""`, or omitted | Match all |
| Only letters, digits, `_`, `-`, spaces, `,`, `\|` | Exact string, or a `\|`/`,`-separated list of exact strings |
| Anything else | Unanchored JavaScript regular expression |

Because regex matching is unanchored, `Edit.*` matches both `Edit` and
`NotebookEdit` — anchor with `^…$` when you mean one tool.

`FileChanged` and `StopFailure` use a narrower exact-match set (letters, digits,
`_`, `|` only); a hyphen, space, or comma there falls back to regex.

A `matcher` on an event without matcher support is silently ignored.

### Matching MCP Tools

MCP tools appear as `mcp__<server>__<tool>`. To match a whole server, the `.*`
suffix is **required** — `mcp__memory` alone contains only exact-match
characters and is compared as a literal string:

- `mcp__memory__.*` — every tool from the `memory` server
- `mcp__.*__write.*` — any `write*` tool from any server

Plugin-bundled servers use `mcp__plugin_<plugin-name>_<server-name>__<tool>`.

## JSON Input (stdin)

**Hook scripts receive JSON via stdin, not environment variables.**

### Common Fields (All Hooks)

All hooks receive these fields:

```json
{
  "hook_event_name": "PreToolUse",
  "session_id": "abc123...",
  "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
  "transcript_path": "/path/to/conversation.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "default",
  "effort": { "level": "high" },
  "agent_id": "optional-agent-id",
  "agent_type": "optional-agent-type"
}
```

`permission_mode` is one of `default`, `plan`, `acceptEdits`, `auto`,
`dontAsk`, `bypassPermissions`. `agent_id` and `agent_type` appear only under
`--agent` or inside a subagent. The transcript file is written asynchronously
and may lag the current turn.

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
| 0 | Success. **stdout** is parsed for JSON output; stderr goes to the debug log only |
| 2 | Blocking error. stdout and any JSON in it are ignored; **stderr** is fed back to Claude |
| Other | Non-blocking error. The action proceeds; the transcript shows the first stderr line |

Pick one mechanism per hook: exit codes *or* exit 0 with JSON on stdout. JSON is
only processed on exit 0.

### Universal JSON Output Fields

These work on every event, alongside `hookSpecificOutput`:

| Field | Default | Purpose |
|-------|---------|---------|
| `continue` | `true` | `false` stops Claude entirely; takes precedence over event decisions |
| `stopReason` | none | Message shown to the user when `continue` is `false` |
| `suppressOutput` | `false` | Hide the hook's stdout from the transcript |
| `systemMessage` | none | Warning shown to the user |
| `terminalSequence` | none | Terminal escape sequence for Claude Code to emit (OSC 0/1/2/9/99/777 and BEL only) |

Hook output strings, including `additionalContext` and `systemMessage`, are
capped at 10,000 characters; longer output is written to a file and replaced
with a preview.

Hooks run without a controlling terminal, so writing escape sequences to
`/dev/tty` fails — use `terminalSequence` instead:

```bash
seq=$(printf '\033]777;notify;%s;%s\007' "Claude Code" "Needs attention")
jq -nc --arg seq "$seq" '{terminalSequence: $seq}'
```

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
