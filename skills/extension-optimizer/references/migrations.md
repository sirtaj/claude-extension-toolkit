# Migration Examples

Before/after examples for common extension upgrades.

## Hook Input: Env Vars → stdin JSON

**Before (deprecated):**
```bash
#!/bin/bash
# Old pattern - env vars no longer available
TOOL_NAME="$TOOL_NAME"
FILE_PATH="$TOOL_INPUT"

if [[ "$FILE_PATH" == *.py ]]; then
    ruff check "$FILE_PATH"
fi
```

**After (current):**
```bash
#!/bin/bash
set -euo pipefail

# Read JSON from stdin
INPUT=$(cat)

# Parse with jq
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -n "$FILE_PATH" && "$FILE_PATH" == *.py ]]; then
    ruff check "$FILE_PATH" 2>&1 || true
fi

exit 0
```

## Hook Output: decision → permissionDecision

**Before (deprecated):**
```bash
# Old blocking format
if dangerous_command; then
    echo '{"decision": "block", "message": "Blocked"}'
    exit 0
fi
```

**After (current):**
```bash
# Current blocking format
if dangerous_command; then
    echo "Blocked: dangerous command detected"
    exit 2
fi

# Or with JSON:
# echo '{"hookSpecificOutput": {"permissionDecision": "deny", "message": "Blocked"}}'
# exit 0
```

## Documentation Links

**Before:**
```markdown
See [Skills Guide](https://docs.anthropic.com/en/docs/claude-code/skills)
```

**After:**
```markdown
See [Skills Guide](https://code.claude.com/docs/en/skills)
```

## Skill Description: First Person → Third Person

**Before:**
```yaml
description: I can help you create PDF documents and convert files.
```

**After:**
```yaml
description: Creates PDF documents and converts files. Use when the user asks to "make a PDF", "convert to PDF", or mentions document generation.
```

## Skill Description: Generic → Specific Triggers

**Before:**
```yaml
description: This skill handles Python development tasks.
```

**After:**
```yaml
description: Manages Python development with ruff linting, type checking, and uv package management. Use when the user mentions "lint", "type check", "ruff", "pyright", or Python code quality.
```

## Agent: Missing Examples → With Examples

**Before:**
```yaml
name: code-reviewer
description: Reviews code for quality issues.
```

**After:**
```yaml
name: code-reviewer
description: |
  Reviews code for quality issues, security vulnerabilities, and best practices.

  <example>
  user: "Review the auth module"
  assistant: "I'll launch code-reviewer to analyze the authentication code."
  </example>

  <example>
  user: "Is this code secure?"
  assistant: "Let me use code-reviewer to check for security issues."
  </example>
```

## Agent: All Tools → Restricted Tools

**Before:**
```yaml
name: code-reviewer
description: ...
# No tools specified = all tools allowed
```

**After:**
```yaml
name: code-reviewer
description: ...
tools:
  - Read
  - Glob
  - Grep
disallowedTools:
  - Write
  - Edit
  - Bash
  - Task
```

## Skill: Monolithic → Progressive Disclosure

**Before (everything in SKILL.md, 3000+ tokens):**
```markdown
---
name: my-skill
description: ...
---

# My Skill

[500 lines of content including all patterns,
examples, API docs, advanced techniques...]
```

**After (split into references/):**

**SKILL.md (~400 tokens):**
```markdown
---
name: my-skill
description: ...
---

# My Skill

Overview and core workflow.

## Quick Reference

Essential table.

## Additional Resources

- `references/patterns.md` - All patterns
- `references/advanced.md` - Advanced techniques
```

**references/patterns.md:**
```markdown
# Patterns Reference

Detailed pattern documentation...
```

## Hook: Hardcoded Path → Plugin-Relative

**Before:**
```json
{
  "hooks": [{
    "type": "command",
    "command": "/home/user/.claude/plugins/my-plugin/hooks/check.sh"
  }]
}
```

**After:**
```json
{
  "hooks": [{
    "type": "command",
    "command": "${CLAUDE_PLUGIN_ROOT}/hooks/check.sh"
  }]
}
```

## Plugin: Missing Version → Versioned

**Before (plugin.json):**
```json
{
  "name": "my-plugin",
  "description": "My plugin"
}
```

**After:**
```json
{
  "name": "my-plugin",
  "description": "My plugin",
  "version": "1.0.0",
  "author": {
    "name": "Author Name"
  }
}
```
