# Frontmatter Reference

Complete reference for all extension frontmatter fields.

## Skill Frontmatter

```yaml
---
name: skill-name                      # Required: identifier
description: Third-person trigger...  # Required: activation conditions
allowed-tools:                        # Optional: tool restrictions
  - Read
  - Grep
  - Glob
model: sonnet                         # Optional: sonnet, opus, haiku
context: fork                         # Optional: fork to run in subagent context
agent: my-agent                       # Optional: execute as subagent
hooks:                                # Optional: skill-scoped hooks
  PreToolUse: [...]
argument-hint: "filename to process"  # Optional: argument prompt text
disable-model-invocation: false       # Optional: require explicit /skill
user-invocable: true                  # Optional: allow /skill-name syntax
---
```

### Field Details

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `name` | Yes | string | Skill identifier (used in logs; invoked via Agent tool — Task is a legacy alias) |
| `description` | Yes | string | Trigger conditions in third person |
| `allowed-tools` | No | list | Restrict which tools the skill can use |
| `model` | No | enum | Override model (sonnet, opus, haiku) |
| `context` | No | string | Set to `fork` to run in forked subagent context |
| `agent` | No | string | Execute skill as named subagent |
| `hooks` | No | object | Skill-specific hook definitions |
| `argument-hint` | No | string | Prompt shown when invoked with `/skill` |
| `disable-model-invocation` | No | bool | Prevent auto-activation, require `/skill` |
| `user-invocable` | No | bool | Enable `/skill-name` invocation |

### Name Validation

- Maximum 64 characters
- Lowercase letters, numbers, and hyphens only (`^[a-z0-9-]+$`)
- Description maximum 1024 characters, no XML tags

### Description Best Practices

Write in **third person, prescriptive voice**:

```yaml
# Good
description: Creates PDF documents from markdown files. Use when converting docs, generating reports, or building documentation.

# Avoid
description: I can help you create PDFs from markdown.
description: This skill is for creating PDFs.
```

Include trigger phrases users might say:
```yaml
description: Analyzes Python code for type errors and linting issues. Use when the user mentions "type check", "lint", "ruff", or "pyright".
```

### Skill Variables

Variables available in skill content:

| Variable | Purpose |
|----------|---------|
| `$ARGUMENTS` | Full argument string passed to skill |
| `$ARGUMENTS[N]` | Nth argument (0-indexed) |
| `$N` | Shorthand for `$ARGUMENTS[N]` (e.g., `$0`, `$1`) |
| `${CLAUDE_SESSION_ID}` | Current session identifier |
| `${CLAUDE_SKILL_DIR}` | Directory containing the SKILL.md file |

### Dynamic Context Injection

Use `` !`command` `` to inject dynamic content:

```yaml
---
name: my-skill
description: Skill with dynamic context
---

Current git status:
!`git status --short`

Current branch:
!`git branch --show-current`
```

**Note:** The "ultrathink" keyword in skill content triggers extended thinking mode.

## Agent Frontmatter

```yaml
---
name: agent-name                      # Required: Agent tool identifier
description: |                        # Required: with <example> blocks
  Autonomous agent for task X.

  <example>
  user: "Do X"
  assistant: "I'll launch agent-name"
  </example>
tools:                                # Optional: allowed tools (default: all)
  - Read
  - Write
  - Bash
disallowedTools:                      # Optional: explicitly blocked tools
  - Task
model: opus                           # Optional: override model
color: cyan                           # Optional: output color
hooks:                                # Optional: agent-scoped hooks
  PostToolUse: [...]
permissionMode: auto                  # Optional: permission handling
skills:                               # Optional: preload skills
  - code-review
maxTurns: 50                           # Optional: max conversation turns
mcpServers:                            # Optional: MCP servers to load
  - server-name
memory: true                           # Optional: enable agent memory
background: false                      # Optional: run in background
isolation: worktree                    # Optional: git worktree isolation
---
```

### Field Details

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `name` | Yes | string | Identifier for Agent tool `subagent_type` |
| `description` | Yes | string | When to use, with example blocks |
| `tools` | No | list | Whitelist of allowed tools |
| `disallowedTools` | No | list | Blacklist of denied tools |
| `model` | No | enum | Override model selection |
| `color` | No | enum | blue, cyan, green, yellow, magenta, red |
| `hooks` | No | object | Agent-specific hook definitions |
| `permissionMode` | No | enum | How to handle permissions: default, acceptEdits, dontAsk, bypassPermissions, plan |
| `skills` | No | list | Skills to preload into agent |
| `maxTurns` | No | number | Maximum conversation turns |
| `mcpServers` | No | list | MCP servers to load |
| `memory` | No | bool | Enable persistent agent memory |
| `background` | No | bool | Run agent in background |
| `isolation` | No | enum | `worktree` for git worktree isolation |

### Example Blocks

Agent descriptions should include `<example>` blocks showing when to use:

```yaml
description: |
  Analyzes code for security vulnerabilities.

  <example>
  user: "Check this code for security issues"
  assistant: "I'll launch the security-analyzer agent"
  </example>

  <example>
  user: "Is this SQL query safe?"
  assistant: "Let me use security-analyzer to check for injection"
  </example>
```

### Plugin Security Restrictions

Agent definitions shipped in plugins do **not** support:
- `hooks` — cannot override hook configuration
- `mcpServers` — cannot inject MCP servers
- `permissionMode` — cannot change permission handling

These restrictions prevent plugins from escalating privileges.

## Command Frontmatter

Commands have minimal frontmatter (optional):

```yaml
---
description: What this command does    # Optional: help text
allowed-tools:                         # Optional: tool restrictions
  - Read
  - Write
model: haiku                           # Optional: override model
argument-hint: "PR number"             # Optional: argument prompt
---
```

### Field Details

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `description` | No | string | Shown in `/help` |
| `allowed-tools` | No | list | Tool restrictions |
| `model` | No | enum | Model override |
| `argument-hint` | No | string | Prompt for arguments |

Commands are invoked explicitly with `/command-name`, so they don't need trigger descriptions.

**Note:** Commands have been merged into skills — both `.claude/commands/foo.md` and `.claude/skills/foo/SKILL.md` create the `/foo` slash command.

## Plugin Manifest (plugin.json)

```json
{
  "name": "my-plugin",
  "description": "What this plugin provides",
  "version": "1.0.0",
  "author": {
    "name": "Author Name",
    "email": "author@example.com"
  },
  "keywords": ["tag1", "tag2"],
  "repository": "https://github.com/user/repo",
  "license": "MIT"
}
```

### Field Details

| Field | Required | Type | Purpose |
|-------|----------|------|---------|
| `name` | Yes | string | Plugin identifier |
| `description` | Yes | string | What the plugin provides |
| `version` | No | string | Semantic version |
| `author` | No | object | Name and email |
| `keywords` | No | list | Discovery tags |
| `repository` | No | string | Source URL |
| `license` | No | string | License identifier |

## Valid Values

### Models
- `sonnet` - Default, balanced (full ID: `claude-sonnet-4-6`)
- `opus` - Most capable, higher cost (full ID: `claude-opus-4-6`)
- `haiku` - Fastest, lowest cost (full ID: `claude-haiku-4-5-20251001`)
- `inherit` - Use parent agent's model

### Agent Colors
- `blue`, `cyan`, `green`, `yellow`, `magenta`, `red`

### Common Tool Lists

**Read-only:**
```yaml
allowed-tools: [Read, Glob, Grep, WebFetch, WebSearch]
```

**Code generation:**
```yaml
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
```

**Testing:**
```yaml
allowed-tools: [Read, Glob, Grep, Bash]
```
