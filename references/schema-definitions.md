# Schema Definitions

Auto-generated from version manifest. Last updated: 2026-01-31T10:22:02.853721Z

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

| Event | When | Can Block | Has Matcher |
|-------|------|-----------|-------------|
| SessionStart | See docs | No | No |
| UserPromptSubmit | See docs | Yes | No |
| PreToolUse | See docs | Yes | Yes |
| PermissionRequest | See docs | Yes | No |
| PostToolUse | See docs | No | Yes |
| PostToolUseFailure | See docs | No | Yes |
| Notification | See docs | No | No |
| SubagentStart | See docs | No | No |
| SubagentStop | See docs | No | No |
| Stop | See docs | Yes | No |
| PreCompact | See docs | No | No |
| SessionEnd | See docs | No | No |


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
