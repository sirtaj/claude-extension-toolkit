---
name: create-rules
description: This skill should be used when the user asks to "create rules", "add a CLAUDE.md", "set up hooks", "configure settings", "add project instructions", or needs help with Claude Code configuration, hook events, or settings files.
---

# Creating Rules and Configuration

Rules configure Claude's behavior through CLAUDE.md files, hooks, and settings.

## CLAUDE.md Files

Project instructions loaded automatically when Claude starts.

### Locations

| File | Scope | Priority |
|------|-------|----------|
| `~/.claude/CLAUDE.md` | Global | Lowest |
| `CLAUDE.md` | Project root | Medium |
| `.claude/CLAUDE.md` | Project .claude | Highest |

### Format

```markdown
# Project Name

## Coding Standards
- Use TypeScript for all new files
- Follow ESLint configuration

## File Locations
- Source code in `src/`
- Tests in `tests/`

## Important Context
- Database: PostgreSQL
- API: REST conventions
```

### Best Practices
- Keep concise (under 2000 words)
- Focus on non-obvious project specifics
- Avoid duplicating README content

## Settings Files

### Locations

| File | Scope |
|------|-------|
| `~/.claude/settings.json` | Global |
| `~/.claude/settings.local.json` | Global local (gitignored) |
| `.claude/settings.json` | Project |
| `.claude/settings.local.json` | Project local (gitignored) |

### Common Settings

```json
{
  "permissions": {
    "allow": ["Read", "Write", "Edit"],
    "deny": ["Bash(rm:*)"]
  }
}
```

## Hooks Overview

Event-driven scripts that execute on Claude events.

### Events

| Event | When | Use For |
|-------|------|---------|
| `PreToolUse` | Before tool runs | Validate/block |
| `PostToolUse` | After tool completes | React to results |
| `Stop` | Agent wants to stop | Verify completion |
| `SessionStart` | Session begins | Load context |

### Basic Hook

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'approve'"
          }
        ]
      }
    ]
  }
}
```

### Hook Types

| Type | Purpose |
|------|---------|
| `command` | Run bash command |
| `prompt` | LLM decision |

## Additional Resources

### Reference Files
- `references/hooks.md` - Detailed hook patterns
- `references/templates.md` - Ready-to-use templates

### Official Documentation
- [Hooks Guide](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [Configuration Reference](https://docs.anthropic.com/en/docs/claude-code/configuration)
