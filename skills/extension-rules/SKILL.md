---
name: extension-rules
description: Configures Claude Code behavior via CLAUDE.md files, hooks, and settings. Use when adding project rules, creating hooks, configuring permissions, or setting up automation. Triggers: "add rules", "create hook", "configure settings", "CLAUDE.md", "hook script".
---

# Extension Rules

Configure Claude Code behavior through rules, hooks, and settings.

## CLAUDE.md Files

Project instructions loaded at session start.

### Locations (Priority Order)

1. `./CLAUDE.md` - Project root (highest priority)
2. `~/.claude/CLAUDE.md` - Personal global config
3. `.claude/CLAUDE.md` - Alternative project location

### Content Patterns

**Project Rules:**
```markdown
# Project: MyApp

## Coding Standards
- Use TypeScript strict mode
- Prefer functional patterns
- Max 20 lines per function

## Architecture
- `/src/components/` - React components
- `/src/services/` - Business logic
- `/src/utils/` - Pure utilities

## Testing
Run tests before committing:
- `npm test` - Unit tests
- `npm run e2e` - Integration tests
```

**Personal Config:**
```markdown
# Claude Configuration

## Preferences
- Concise responses
- Python 3.11+ features
- Use uv for Python projects

## Locations
- Projects: ~/dev/
- Notes: ~/notes/
```

### Best Practices

- Keep under 2000 tokens
- Focus on what Claude needs to know
- Update when project conventions change
- Remove stale rules

## Hooks

Automatic triggers on Claude events.

### Quick Setup

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "/path/to/check.sh",
        "timeout": 30
      }]
    }]
  }
}
```

### Common Hook Patterns

**Lint on save (Python):**
```json
{
  "PostToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "command",
      "command": "~/.claude/hooks/python_lint.sh"
    }]
  }]
}
```

**Block dangerous commands:**
```json
{
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{
      "type": "command",
      "command": "~/.claude/hooks/safe_bash.sh"
    }]
  }]
}
```

**Load context on start:**
```json
{
  "SessionStart": [{
    "hooks": [{
      "type": "command",
      "command": "cat .claude/context.md 2>/dev/null || true"
    }]
  }]
}
```

### Writing Hook Scripts

Scripts receive JSON via stdin:

```bash
#!/bin/bash
set -euo pipefail

# Read JSON input
INPUT=$(cat)

# Extract fields with jq
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Your logic here
if [[ "$FILE_PATH" == *.py ]]; then
    ruff check "$FILE_PATH" 2>&1 || true
fi

exit 0
```

**Exit codes:**
- `0` - Allow action
- `2` - Block with stdout as message
- Other - Error (logged, action allowed)

### Hook Events Reference

| Event | Can Block | Use For |
|-------|-----------|---------|
| SessionStart | No | Load context |
| PreToolUse | Yes | Validate actions |
| PostToolUse | No | Checks after save |
| Stop | Yes | Cleanup tasks |

See `references/hooks.md` for complete event list.

## Settings

### Permissions

In `settings.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(npm test:*)",
      "Read(*)"
    ],
    "deny": [
      "Bash(rm -rf*)"
    ]
  }
}
```

### Plugin Settings

For plugins, use `.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": ["Bash(ruff*)", "Bash(pyright*)"]
  }
}
```

## Common Configurations

### Python Project

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/python_check.sh"
      }]
    }]
  },
  "permissions": {
    "allow": ["Bash(pytest*)", "Bash(ruff*)", "Bash(uv*)"]
  }
}
```

### TypeScript Project

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "~/.claude/hooks/ts_check.sh"
      }]
    }]
  },
  "permissions": {
    "allow": ["Bash(npm*)", "Bash(npx*)"]
  }
}
```

## Additional Resources

- `references/hooks.md` - Complete hooks reference
- `references/templates.md` - More CLAUDE.md examples
