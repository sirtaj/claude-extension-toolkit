# Schema Definitions

Auto-generated from version manifest. Last updated: 2026-05-22T06:01:46.454175Z

## Skill Frontmatter

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| name | Yes | string | Skill identifier |
| description | Yes | string | Third-person trigger description |
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
| name | Yes | string | Agent identifier (used with Agent tool; Task is a legacy alias) |
| description | Yes | string | When to use, with <example> blocks |
| tools | No | list | Allowed tools (default: all) |
| disallowedTools | No | list | Explicitly denied tools |
| model | No | enum | sonnet, opus, haiku |
| color | No | enum | blue, cyan, green, yellow, magenta, red |
| hooks | No | object | Agent-scoped hooks |
| permissionMode | No | enum | Permission handling mode |
| skills | No | list | Preloaded skills |

## Hook Events

| Event | When | Can Block | Has Matcher |
|-------|------|-----------|-------------|
| SessionStart | See docs | No | Yes |
| Setup | See docs | No | Yes |
| UserPromptSubmit | See docs | Yes | No |
| UserPromptExpansion | See docs | Yes | Yes |
| PreToolUse | See docs | Yes | Yes |
| PermissionRequest | See docs | Yes | Yes |
| PermissionDenied | See docs | No | Yes |
| PostToolUse | See docs | No | Yes |
| PostToolUseFailure | See docs | No | Yes |
| PostToolBatch | See docs | Yes | No |
| Notification | See docs | No | Yes |
| SubagentStart | See docs | No | Yes |
| SubagentStop | See docs | Yes | Yes |
| TaskCreated | See docs | Yes | No |
| TaskCompleted | See docs | Yes | No |
| Stop | See docs | Yes | No |
| StopFailure | See docs | No | Yes |
| TeammateIdle | See docs | Yes | No |
| InstructionsLoaded | See docs | No | Yes |
| ConfigChange | See docs | Yes | Yes |
| CwdChanged | See docs | No | No |
| FileChanged | See docs | No | Yes |
| WorktreeCreate | See docs | Yes | No |
| WorktreeRemove | See docs | No | No |
| PreCompact | See docs | Yes | Yes |
| PostCompact | See docs | No | Yes |
| Elicitation | See docs | Yes | Yes |
| ElicitationResult | See docs | Yes | Yes |
| SessionEnd | See docs | No | Yes |


## Plugin Manifest (plugin.json)

| Field | Required | Description |
|-------|----------|-------------|
| name | Yes | Plugin identifier |
| description | Yes | What the plugin provides |
| version | No | Semantic version |
| author | No | Author object with name/email |
| keywords | No | Discovery tags |
| repository | No | Source repository URL |
| license | No | License identifier |

## Valid Values

- **Models**: sonnet, opus, haiku
- **Colors**: blue, cyan, green, yellow, magenta, red
- **Permission modes**: (see docs for current options)
