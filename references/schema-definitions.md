# Schema Definitions

Auto-generated from version manifest. Last updated: 2026-02-01T00:00:00Z

## Skill Frontmatter

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| name | No | string | Skill identifier (defaults to directory name) |
| description | Recommended | string | Third-person trigger description |
| allowed-tools | No | list | Tool restrictions |
| model | No | enum | sonnet, opus, haiku |
| context | No | string | Additional context file |
| agent | No | string | Execute as subagent |
| hooks | No | object | Skill-scoped hooks |
| argument-hint | No | string | Argument prompt |
| disable-model-invocation | No | bool | Require explicit invocation |
| user-invocable | No | bool | Allow /skill-name |

## Agent Frontmatter

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| name | Yes | string | Agent identifier (used with Task tool) |
| description | Yes | string | When to use, with <example> blocks |
| tools | No | list | Allowed tools (default: all) |
| disallowedTools | No | list | Explicitly denied tools |
| model | No | enum | sonnet, opus, haiku |
| color | No | enum | blue, cyan, green, yellow, magenta, red |
| hooks | No | object | Agent-scoped hooks |
| permissionMode | No | enum | Permission handling mode |
| skills | No | list | Preloaded skills |

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
| SessionEnd | Session terminates | No | Yes | clear, logout, prompt_input_exit, etc. |

## Hook Handler Fields

| Field | Type | Description |
|-------|------|-------------|
| type | enum | command, prompt, agent |
| command | string | Shell command (for type: command) |
| prompt | string | Instructions (for type: prompt/agent) |
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

## Valid Values

- **Models**: sonnet, opus, haiku
- **Colors**: blue, cyan, green, yellow, magenta, red
- **Hook types**: command, prompt, agent
- **Permission modes**: (see docs for current options)
