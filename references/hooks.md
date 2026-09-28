# Hooks Reference

Complete reference for Claude Code hooks system.

Verified against Claude Code 2.1.283 docs (2026-09-28).
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
| `SessionStart` | Session begins/resumes | No | startup, resume, clear, compact, fork |
| `Setup` | `--init-only`, or `--init`/`--maintenance` in `-p` mode | No | init, maintenance |
| `UserPromptSubmit` | User sends message | Yes | — |
| `UserPromptExpansion` | A typed command expands into a prompt | Yes | Command name |
| `PreToolUse` | Before tool execution | Yes | Tool name |
| `PermissionRequest` | Tool call needs a permission decision | Yes (JSON `decision` only; exit 2 is ignored) | Tool name |
| `PermissionDenied` | Auto-mode classifier denied a call | No | Tool name |
| `PostToolUse` | After tool success | No | Tool name |
| `PostToolUseFailure` | After tool failure | No | Tool name |
| `PostToolBatch` | After a parallel tool batch resolves | Yes | — |
| `Notification` | System notification | No | permission_prompt, idle_prompt, auth_success, elicitation_dialog, elicitation_url_dialog, elicitation_complete, elicitation_response, agent_needs_input, agent_completed, quota_auto_resume_fired, quota_auto_resume_stale, quota_auto_resume_disabled |
| `MessageDisplay` | While assistant text renders (display-only) | No | — |
| `SubagentStart` | Subagent launched | No | Agent type name |
| `SubagentStop` | Subagent finished | Yes | Agent type name |
| `TaskCreated` | Task being created via `TaskCreate` | Yes | — |
| `TaskCompleted` | Task being marked completed | Yes | — |
| `Stop` | Agent finishes responding | Yes | — |
| `StopFailure` | Turn ends due to an API error | No | rate_limit, overloaded, authentication_failed, oauth_org_not_allowed, account_on_hold, billing_error, invalid_request, model_not_found, server_error, max_output_tokens, cloud_credential_error, unknown |
| `TeammateIdle` | Teammate agent about to go idle | Yes | — |
| `InstructionsLoaded` | CLAUDE.md / `.claude/rules/*.md` loaded | No | Load reason |
| `ConfigChange` | Settings/config modified | Yes | user_settings, project_settings, local_settings, policy_settings, skills |
| `CwdChanged` | Working directory changes (e.g. `cd`) | No | — |
| `DirectoryAdded` | Directory added via `/add-dir` or SDK | No | slash_command, register_repo_root |
| `FileChanged` | Watched file changes on disk | No | Literal filenames to watch |
| `WorktreeCreate` | Worktree being created (replaces git behavior) | Yes | — |
| `WorktreeRemove` | Worktree being removed | Yes (any non-zero exit fails removal) | — |
| `PreCompact` | Before context compaction | Yes | manual, auto |
| `PostCompact` | After context compaction | No | manual, auto |
| `PreModelSwitch` | Before a requested model switch (v2.1.251+) | Yes | Canonical target model name |
| `PostModelSwitch` | After the session's model changes (v2.1.251+) | No | Canonical target model name |
| `Elicitation` | MCP server requests user input | Yes | MCP server name |
| `ElicitationResult` | After the user responds | Yes | MCP server name |
| `SessionEnd` | Session terminates | No | clear, resume, logout, prompt_input_exit, other |

`SessionEnd`'s `bypass_permissions_disabled` reason was removed in v2.1.234;
drop it from matchers. `StopFailure` matching on `cloud_credential_error` needs
v2.1.267+. `PreModelSwitch`/`PostModelSwitch` matchers compare against the
canonical name of the target model (so `claude-opus-5` covers `opus` and
provider-specific IDs); when no canonical name can be derived, every hook runs.

## Hook Types

Five handler types: `command`, `http`, `mcp_tool`, `prompt`, and `agent`.
All matching hooks run in parallel. The same handler defined in more than one
settings file runs once; a plugin's or skill's copy stays separate.

### Supported Types per Event

| Events | Supported types |
|--------|-----------------|
| PermissionDenied, PostToolBatch, PostToolUse, PostToolUseFailure, PreToolUse, Stop, SubagentStop, TaskCompleted, TaskCreated, TeammateIdle, UserPromptExpansion, UserPromptSubmit | all five |
| PermissionRequest | `command`, `http`, `mcp_tool`, `prompt` (agent hooks are skipped) |
| ConfigChange, CwdChanged, DirectoryAdded, Elicitation, ElicitationResult, FileChanged, InstructionsLoaded, MessageDisplay, Notification, PostCompact, PostModelSwitch, PreCompact, PreModelSwitch, SessionEnd, StopFailure, SubagentStart, WorktreeCreate, WorktreeRemove | `command`, `http`, `mcp_tool` |
| SessionStart, Setup | `command`, `mcp_tool` |

### Common Fields (all types)

| Field | Required | Purpose |
|-------|----------|---------|
| `type` | yes | `command`, `http`, `mcp_tool`, `prompt`, or `agent` |
| `if` | no | Permission-rule filter, e.g. `"Bash(git *)"` or `"Edit(*.ts)"`. Exactly one rule; no `&&`/`\|\|`. Only evaluated on tool events (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, PermissionDenied); on any other event a hook with `if` never runs |
| `timeout` | no | Seconds. Defaults: 600 for command/http/mcp_tool, 30 for prompt, 60 for agent. See per-event overrides below |
| `statusMessage` | no | Custom spinner message |
| `once` | no | Remove the hook after its first successful run (a failed, exit-2, or timed-out run leaves it in place). **Only honored in skill frontmatter** — ignored in settings files and agent frontmatter |

The `if` filter is best-effort and fails open when a Bash command can't be
parsed. Use the permission system, not a hook, to enforce a boundary.

Timeout overrides: the command/http/mcp_tool default drops to 30s on
`UserPromptSubmit`, `PreModelSwitch`, and `PostModelSwitch`, and to 10s on
`MessageDisplay`. `SessionEnd` hooks share a 1.5-second budget, raised to match
the highest per-hook `timeout` (max 60s) or set via
`CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`. `timeout` isn't enforced on a command
hook running with `async: true`. A timed-out hook's output is discarded, so on
most events it has no effect — but on `PreModelSwitch` a timeout cancels the
switch.

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
- `asyncRewake` (optional): run in background and wake Claude on exit code 2 (stderr, or stdout if stderr is empty, is shown to Claude)
- `shell` (optional): `bash` (default) or `powershell`. Defaults to `powershell` on Windows without Git Bash. Ignored when `args` is set

Set `args` whenever the hook references a path placeholder — exec form needs no
quoting for paths with spaces:

```json
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"]
}
```

Plugin hooks substitute `${user_config.*}` in exec form only. Since v2.1.207 a
shell-form plugin hook whose `command` references `${user_config.*}` fails; read
`$CLAUDE_PLUGIN_OPTION_<KEY>` instead or switch to `args`.

### MCP Tool Hook

Calls a tool on a configured MCP server. Its text output is treated like
command-hook stdout; an `isError: true` result is a non-blocking error.

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

`SessionStart` at launch (including `--continue`/`--resume`) and every `Setup`
event fire before MCP servers are available, so their `mcp_tool` hooks are
skipped without calling the tool. `SessionStart` after `/clear` or compaction
does run them. On blocking events Claude Code waits for a connecting server (up
to `MCP_TIMEOUT`); on observational events it doesn't. Hooks never start an
OAuth flow.

### Prompt Hook

Sends the hook input and your prompt to a Claude model (Haiku by default) for a
single-turn decision:

```json
{
  "type": "prompt",
  "prompt": "Check if this action is safe: $ARGUMENTS. Respond with {\"ok\": true} or {\"ok\": false, \"reason\": \"...\"}.",
  "model": "haiku",
  "timeout": 30
}
```

**Fields:**
- `prompt` (required): Instructions for Claude. `$ARGUMENTS` is replaced with the hook input JSON; if absent, the JSON is appended
- `model` (optional): Model to use. Defaults to a fast model
- `continueOnBlock` (optional, default `false`): on `ok: false`, feed the reason back to Claude and continue instead of ending the turn (applies to PreToolUse, PostToolUse, TeammateIdle)

The model must respond with `{"ok": true|false, "reason": "...", "impossible": true|false}`.
`reason` is required when `ok` is `false`. `impossible: true` lets `Stop` and
`SubagentStop` end the turn instead of feeding the reason back. On
`PermissionRequest` and `PermissionDenied`, `ok: false` has no effect — use a
command hook.

### Agent Hook

Spawns a subagent with tool access (Read, Grep, Glob, …) for up to 50 turns.
**Experimental.** Supports the same events as prompt hooks except
`PermissionRequest`.

```json
{
  "type": "agent",
  "prompt": "Verify the code changes are safe and follow best practices. $ARGUMENTS",
  "timeout": 120
}
```

**Fields:**
- `prompt` (required): Instructions for the agent (`$ARGUMENTS` placeholder)
- `model` (optional): Model to use

Responds with `{"ok": true}` or `{"ok": false, "reason": "..."}`. On `ok: false`
it behaves like a prompt hook with `continueOnBlock: true`; there is no
`continueOnBlock` or `impossible` field.

### HTTP Hook

Sends the hook's JSON input as a POST body to a URL:

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
- `headers` (optional): Request headers (supports `$VAR`/`${VAR}` interpolation)
- `allowedEnvVars` (optional): Env var names that may be interpolated into headers; unlisted references become empty strings
- `timeout` (optional): Timeout in seconds
- `statusMessage` (optional): Custom spinner message

Status codes can't block. Return a 2xx with a JSON body using the normal output
format to make a decision; non-2xx, connection failures, and non-JSON 2xx bodies
are non-blocking errors. Managed `allowedHttpHookUrls` and
`httpHookAllowedEnvVars` settings further restrict HTTP hooks.

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
  "scratchpad_dir": "/tmp/claude-1000/-home-user-my-project/abc123/scratchpad",
  "permission_mode": "default",
  "effort": { "level": "high" },
  "agent_id": "optional-agent-id",
  "agent_type": "optional-agent-type"
}
```

`permission_mode` is one of `default`, `plan`, `acceptEdits`, `auto`,
`dontAsk`, `bypassPermissions` (the **Manual** mode arrives as `default`) and
isn't sent to every event. `effort.level` is `low`, `medium`, `high`, `xhigh`,
or `max`. `scratchpad_dir` needs v2.1.257+; `prompt_id` needs v2.1.196+.
`agent_id` and `agent_type` appear only under `--agent` or inside a subagent.
The transcript file is written asynchronously and may lag the current turn.
Only `SessionStart` may receive a `model` field; there is no `$CLAUDE_MODEL`
env var.

### PreToolUse Input

```json
{
  "hook_event_name": "PreToolUse",
  "session_id": "...",
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/test"
  },
  "tool_use_id": "toolu_01ABC123..."
}
```

File-tool `tool_input.file_path` is always absolute (native separators on
Windows). MCP tool calls also carry `mcp_server: {name, source}` (v2.1.274+).

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
  "tool_response": {
    "filePath": "/path/to/file.py",
    "type": "create"
  },
  "tool_use_id": "toolu_01ABC123...",
  "duration_ms": 12
}
```

`PostToolUseFailure` receives `error`, optional `is_interrupt`, and
`duration_ms` instead of `tool_response`.

### UserPromptSubmit Input

```json
{
  "hook_event_name": "UserPromptSubmit",
  "session_id": "...",
  "prompt": "The user's message text"
}
```

### SubagentStop Input

```json
{
  "hook_event_name": "SubagentStop",
  "session_id": "...",
  "stop_hook_active": false,
  "agent_id": "def456",
  "agent_type": "code-reviewer",
  "agent_transcript_path": "~/.claude/projects/.../subagents/agent-def456.jsonl",
  "last_assistant_message": "..."
}
```

`Stop` receives `stop_hook_active` and `last_assistant_message` too, plus
`background_tasks` and `session_crons` arrays (also sent to SubagentStop).

### TeammateIdle Input

```json
{
  "hook_event_name": "TeammateIdle",
  "session_id": "...",
  "teammate_name": "researcher",
  "team_name": "session-a1b2c3d4"
}
```

`team_name` is deprecated (also on TaskCreated/TaskCompleted) and will be removed.

### ConfigChange Input

```json
{
  "hook_event_name": "ConfigChange",
  "session_id": "...",
  "source": "project_settings",
  "file_path": "/path/to/project/.claude/settings.json"
}
```

### Elicitation Input

```json
{
  "hook_event_name": "Elicitation",
  "session_id": "...",
  "mcp_server_name": "my-mcp-server",
  "message": "Please provide your credentials",
  "mode": "form",
  "requested_schema": { "type": "object", "properties": {} }
}
```

URL-mode elicitations send `mode: "url"` and `url` instead of `requested_schema`.

### PreModelSwitch / PostModelSwitch Input

```json
{
  "hook_event_name": "PreModelSwitch",
  "session_id": "...",
  "from_model": "claude-sonnet-5",
  "to_model": "claude-opus-5",
  "requested_model": "opus",
  "source": "command",
  "context_tokens": 182340,
  "prompt_cache_warm": true,
  "cache_ttl": "5m",
  "estimated_cache_write_usd": 1.1396,
  "pricing": "catalog"
}
```

`source` is `command`, `picker`, or `sdk`; PostModelSwitch adds `auto` and
`resume`.

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

**Note:** Top-level `decision`/`reason` fields in PreToolUse output are deprecated
(`approve`/`block` map to `allow`/`deny`). Use
`hookSpecificOutput.permissionDecision` instead. Other events such as PostToolUse
and Stop still use top-level `decision: "block"` + `reason`.

`hookSpecificOutput` requires a `hookEventName` field set to the event name.

### Allowing Actions

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow"
  }
}
```

Exiting 0 with no output reports no decision: the normal permission flow
applies (it does not approve the call).

`permissionDecision` is `allow`, `deny`, `ask`, or `defer` (`-p` mode only).
Precedence across hooks is `deny` > `defer` > `ask` > `allow`. Deny and ask
rules are still evaluated after a hook's `allow`. PreToolUse may also return
`updatedInput` (replaces the whole input) and `additionalContext`.

### Blocking Actions

Exit code 2 blocks with the message on **stderr**:

```bash
echo "Blocked: dangerous command detected" >&2
exit 2
```

Or use JSON format:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked: dangerous command detected"
  }
}
```

### SubagentStop Decision

SubagentStop can prevent the subagent from stopping (exit 2):

```bash
# Prevent subagent from stopping if work incomplete
if [ "$WORK_INCOMPLETE" = "true" ]; then
    echo "Agent has not completed all tasks" >&2
    exit 2
fi
exit 0
```

After eight consecutive Stop/SubagentStop continuations Claude Code overrides
the next block (raise with `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`). Check
`stop_hook_active` to avoid loops.

### PermissionRequest Decision

PermissionRequest hooks return a `decision` object; `updatedPermissions` applies
permission updates:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow",
      "updatedPermissions": [
        {
          "type": "addRules",
          "rules": [{ "toolName": "Bash", "ruleContent": "npm test" }],
          "behavior": "allow",
          "destination": "localSettings"
        }
      ]
    }
  }
}
```

`behavior` is `allow` or `deny`. `updatedInput` and `updatedPermissions` apply to
`allow`; `message` and `interrupt` apply to `deny`. Update entry `type`s:
`addRules`, `replaceRules`, `removeRules`, `setMode`, `addDirectories`,
`removeDirectories`. `destination`: `session`, `localSettings`,
`projectSettings`, `userSettings`.

### PostToolUse Modification

PostToolUse hooks can replace the tool output Claude sees:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "updatedToolOutput": {
      "stdout": "[redacted]",
      "stderr": "",
      "interrupted": false,
      "isImage": false
    }
  }
}
```

The value must match the tool's output shape. `updatedMCPToolOutput` still
works for MCP tools only; prefer `updatedToolOutput`. `classifierContext`
(v2.1.236+) sends a short note to the auto-mode classifier.

### Other Event-Specific Output

- **SessionStart**: `additionalContext`, `initialUserMessage`, `sessionTitle`, `watchPaths`, `reloadSkills`
- **UserPromptSubmit**: `decision`, `reason`, `additionalContext`, `sessionTitle`, `suppressOriginalPrompt`
- **PermissionDenied**: `hookSpecificOutput.retry: true` lets the model retry
- **PreModelSwitch**: `permissionDecision` (`allow`/`deny`/`ask`) + `permissionDecisionReason`; exit 2 also cancels the switch
- **PostModelSwitch**, **SubagentStart**, **PostToolBatch**, **PostToolUseFailure**: `additionalContext`
- **MessageDisplay**: `displayContent` (display-only)
- **CwdChanged**, **FileChanged**: `watchPaths`
- **WorktreeCreate**: command hook prints the path as the last stdout line; HTTP hook returns `hookSpecificOutput.worktreePath`
- **Elicitation** / **ElicitationResult**: `action` (`accept`/`decline`/`cancel`), `content`

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success. **stdout** is parsed for JSON output if it starts with `{` and ends with `}`; stderr goes to the debug log only |
| 2 | Blocking error on events that can block. JSON on stdout is still read but can't override the block; the message is the JSON block reason, else **stderr** |
| Other | Non-blocking error; the action proceeds and the transcript shows the first stderr line — unless stdout holds a valid JSON object, which then decides the outcome |

JSON output fields are read on every exit code, not just 0. Pick one mechanism
per hook anyway: exit codes alone, *or* exit 0 with JSON on stdout. JSON that
fails parsing or schema validation is a non-blocking error.

For `UserPromptSubmit`, `UserPromptExpansion`, `SessionStart`, and
`PostModelSwitch`, plain-text stdout on exit 0 is added to Claude's context.
`WorktreeCreate` fails on any non-zero exit; `WorktreeRemove` fails if the
directory still exists after a non-zero exit. `PermissionRequest` ignores
exit 2.

### Universal JSON Output Fields

These work on every event, alongside `hookSpecificOutput`:

| Field | Default | Purpose |
|-------|---------|---------|
| `continue` | `true` | `false` stops Claude entirely; takes precedence over event decisions |
| `stopReason` | none | Message shown to the user when `continue` is `false` (stays in the conversation) |
| `suppressOutput` | `false` | Accepted but has no effect |
| `systemMessage` | none | Warning shown to the user |
| `terminalSequence` | none | Terminal escape sequence for Claude Code to emit (OSC 0/1/2/9/99/777 and BEL only) |

Some events discard `continue`/`systemMessage`; see each event's section in the
docs.

Hook output strings (`additionalContext`, `systemMessage`,
`initialUserMessage`, and plain stdout) are each capped at 10,000 characters;
longer output is written to a file in the session directory and replaced with
the path and a preview of the first 2,000 characters.

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
    echo "Blocked: potentially dangerous command" >&2
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

**Tip:** SessionStart, Setup, CwdChanged, and FileChanged hooks can use
`CLAUDE_ENV_FILE` — append `export KEY=VALUE` lines to this file to persist
environment variables for subsequent Bash commands.

### Credential Detection

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "prompt",
        "prompt": "Check if this content contains API keys, passwords, or tokens: $ARGUMENTS. Respond {\"ok\": true} if clean, or {\"ok\": false, \"reason\": \"...\"} if credentials are found."
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
        "command": "bash",
        "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/check.sh"],
        "timeout": 30
      }]
    }]
  }
}
```

**Important:** Plugin hooks.json requires:
1. A `hooks` wrapper object containing the event handlers
2. Optional `description` field at the top level

Use `${CLAUDE_PLUGIN_ROOT}` for portable paths and `${CLAUDE_PLUGIN_DATA}` for
state that survives plugin updates.

## Best Practices

1. **Keep hooks fast** - Set reasonable timeouts
2. **Default to allow** - Only block when necessary
3. **Provide clear messages** - Users should understand why blocked
4. **Handle errors gracefully** - Use `|| true` for optional checks
5. **Use JSON parsing** - Don't rely on deprecated env vars
6. **Test thoroughly** - Hook failures can disrupt workflow
7. **Use statusMessage** - Provide feedback during long-running hooks
8. **Disable all hooks** - Use `disableAllHooks: true` in settings to temporarily disable (can't disable managed hooks from outside managed settings)
9. **SessionEnd timeout** - Set `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` env var for cleanup hooks
10. **Deduplication** - The same handler defined in several settings files runs once; plugin and skill copies stay separate
11. **Enforce policy with exit 2** - Exit 1 is a non-blocking error, and a mistyped script path silently disables the gate
