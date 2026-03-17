# Schema Definitions

Auto-generated from version manifest. Last updated: 2026-03-17T00:00:00Z

## Skill Frontmatter

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| name | No | string | Skill identifier (max 64 chars, `^[a-z0-9-]+$`) |
| description | Recommended | string | Third-person trigger description (max 1024 chars, no XML) |
| allowed-tools | No | list | Tool restrictions |
| model | No | enum | sonnet, opus, haiku, or full model ID |
| context | No | enum | Set to `fork` to run in forked subagent context |
| agent | No | string | Execute as subagent |
| hooks | No | object | Skill-scoped hooks |
| argument-hint | No | string | Argument prompt |
| disable-model-invocation | No | bool | Require explicit invocation |
| user-invocable | No | bool | Allow /skill-name |

### Skill Variables

| Variable | Purpose |
|----------|---------|
| `$ARGUMENTS` | Full argument string |
| `$ARGUMENTS[N]` | Nth argument (0-indexed) |
| `$N` | Shorthand for `$ARGUMENTS[N]` |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Skill directory path |
| `` !`command` `` | Dynamic context injection |

## Agent Frontmatter

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| name | Yes | string | Agent identifier (used with Agent tool) |
| description | Yes | string | When to use, with `<example>` blocks |
| tools | No | list | Allowed tools (default: all) |
| disallowedTools | No | list | Explicitly denied tools |
| model | No | enum | sonnet, opus, haiku, full ID, or inherit |
| color | No | enum | blue, cyan, green, yellow, magenta, red |
| hooks | No | object | Agent-scoped hooks |
| permissionMode | No | enum | default, acceptEdits, dontAsk, bypassPermissions, plan |
| skills | No | list | Preloaded skills |
| maxTurns | No | number | Maximum conversation turns |
| mcpServers | No | list | MCP servers to load |
| memory | No | bool | Enable persistent agent memory |
| background | No | bool | Run agent in background |
| isolation | No | enum | `worktree` for git worktree isolation |

**Plugin restrictions:** Agent definitions in plugins do not support `hooks`, `mcpServers`, or `permissionMode`.

## Hook Events

| Event | When | Can Block | Has Matcher | Matcher Values |
|-------|------|-----------|-------------|----------------|
| SessionStart | Session begins/resumes | No | Yes | startup, resume, clear, compact |
| UserPromptSubmit | User sends message | Yes | No | - |
| PreToolUse | Before tool execution | Yes | Yes | Tool name |
| PermissionRequest | Permission prompt shown | Yes | Yes | Tool name |
| PostToolUse | After tool success | No | Yes | Tool name |
| PostToolUseFailure | After tool failure | No | Yes | Tool name |
| Notification | System notification | No | Yes | permission_prompt, idle_prompt, auth_success, elicitation_dialog |
| SubagentStart | Subagent launched | No | Yes | Agent type name |
| SubagentStop | Subagent finished | Yes | Yes | Agent type name |
| Stop | Agent finishes | Yes | No | - |
| PreCompact | Before compaction | No | Yes | manual, auto |
| PostCompact | After compaction | No | Yes | manual, auto |
| SessionEnd | Session terminates | No | Yes | clear, logout, prompt_input_exit, bypass_permissions_disabled, other |
| TeammateIdle | Teammate agent is idle | Yes | No | - |
| TaskCompleted | Background task completes | Yes | No | - |
| InstructionsLoaded | Instructions loaded | No | No | - |
| ConfigChange | Settings modified | Yes | Yes | user_settings, project_settings, local_settings, policy_settings, skills |
| WorktreeCreate | Git worktree created | Yes | No | - |
| WorktreeRemove | Git worktree removed | No | No | - |
| Elicitation | Before elicitation dialog | Yes | No | - |
| ElicitationResult | After elicitation response | Yes | No | - |
| Setup | CLI init/maintenance | No | Yes | --init, --init-only, --maintenance |

## Hook Handler Fields

| Field | Type | Description |
|-------|------|-------------|
| type | enum | command, prompt, agent, http |
| command | string | Shell command (for type: command) |
| prompt | string | Instructions (for type: prompt/agent) |
| url | string | HTTP endpoint (for type: http, required) |
| headers | object | Request headers (for type: http) |
| allowedEnvVars | array | Env vars to expose (for type: http) |
| timeout | number | Timeout in seconds |
| statusMessage | string | Custom spinner message |
| once | bool | Run only once per session |
| async | bool | Run in background |
| model | enum | Model for prompt/agent hooks |

## Plugin Manifest (plugin.json)

| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Plugin identifier |
| description | No | What the plugin provides |
| version | No | Semantic version |
| author | No | Author object with name/email |
| keywords | No | Discovery tags |
| repository | No | Source repository URL |
| license | No | License identifier |
| homepage | No | Documentation URL |
| commands | No | Custom command paths |
| agents | No | Custom agent paths |
| skills | No | Custom skill paths |
| hooks | No | Hook config path or inline object |
| mcpServers | No | MCP config path or inline object |
| outputStyles | No | Output style files |
| lspServers | No | LSP server config |

## Plugin hooks.json Format

Plugin hooks.json files require a `hooks` wrapper:

```json
{
  "description": "Optional description",
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{ "type": "command", "command": "..." }]
    }]
  }
}
```

## Permission Modes

| Mode | Behavior |
|------|----------|
| default | Standard permission prompts |
| acceptEdits | Auto-approve file edits, prompt for others |
| dontAsk | Auto-approve most actions |
| bypassPermissions | Skip all permission prompts (dangerous) |
| plan | Require plan approval before execution |

## Valid Values

- **Models (short)**: sonnet, opus, haiku
- **Models (full ID)**: claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001
- **Models (special)**: inherit
- **Colors**: blue, cyan, green, yellow, magenta, red
- **Hook types**: command, prompt, agent, http
- **Permission modes**: default, acceptEdits, dontAsk, bypassPermissions, plan
