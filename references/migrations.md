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

## Task Tool → Agent Tool

**Before (deprecated):**
```yaml
name: code-reviewer
description: ...
disallowedTools:
  - Task
```

```
Invoke via Task tool: `subagent_type: "code-reviewer"`
```

**After (current):**
```yaml
name: code-reviewer
description: ...
disallowedTools:
  - Agent
```

```
Invoke via Agent tool: `subagent_type: "code-reviewer"`
```

**Note:** `Task` still works as an alias but `Agent` is the canonical name.

## Marketplace Plugin Entry: `path` → `source`

**Before (legacy):**
```json
{
  "plugins": [
    {"path": "my-plugin", "name": "my-plugin"}
  ]
}
```

**After (current):**
```json
{
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./my-plugin",
      "description": "What the plugin does",
      "version": "1.0.0"
    }
  ]
}
```

The canonical schema uses `source` (not `path`). `source` is a plain string only
for relative paths; every remote type is an object — `github`, `url`,
`git-subdir`, `npm`, and `archive`. See `references/marketplace-schema.md`.

The marketplace itself also requires `owner.name` as a required field.

## Skill Arguments: Dot → Bracket Syntax

**Before (deprecated):**
```markdown
Process file: $ARGUMENTS.0
With option: $ARGUMENTS.1
```

**After (current):**
```markdown
Process file: $ARGUMENTS[0]
With option: $ARGUMENTS[1]

Or shorthand:
Process file: $0
With option: $1
```

## PreToolUse Output: Top-level → hookSpecificOutput

**Before (deprecated):**
```json
{
  "decision": "deny",
  "reason": "Dangerous command detected"
}
```

**After (current):**
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "deny",
    "message": "Dangerous command detected"
  }
}
```

## Agent Resume: resume Param → SendMessage

**Before (deprecated):**
```
Agent tool with resume: agentId
```

**After (current):**
```
SendMessage({to: "agentId", content: "Continue your work"})
```

## Model IDs: Claude 4.x → Claude 5

**Before (stale):**
```yaml
model: claude-sonnet-4-6
```

**After (current):**
```yaml
model: sonnet            # alias, resolves per provider
# or pin explicitly:
model: claude-sonnet-5
```

Current full IDs: `claude-opus-5-5`, `claude-opus-5`, `claude-sonnet-5`,
`claude-fable-5-1`, `claude-fable-5`, `claude-haiku-4-5-20251001`. The `fable`
alias joined `sonnet`/`opus`/`haiku`, and `best` resolves to the `fable` model
where Fable is available, otherwise to `opus`.

As of 2.1.280, `opus` resolves to Opus 5.5 (was Opus 5 from 2.1.219) on the
Anthropic API, Bedrock, Agent Platform, and Claude Platform on AWS; as of
2.1.257, `fable` resolves to Fable 5.1 (was Fable 5). Pin `claude-opus-5` or
`claude-fable-5` explicitly to stay on the older version. Opus 5.5 defaults to
`medium` effort (other effort-capable models default to `high`, Opus 4.7 to
`xhigh`), so revisit any `effort` you tuned for Opus 5.

## Agent Color: magenta → purple

**Before (invalid):**
```yaml
color: magenta
```

**After (current):**
```yaml
color: purple
```

Valid colors: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`,
`cyan`.

## Skill Frontmatter: Required name/description → All Optional

**Before (over-constrained):**
```yaml
---
name: my-skill           # was documented as required
description: ...         # was documented as required
---
```

**After (current):**
```yaml
---
description: What it does and when to use it.   # recommended, not required
---
```

`name` now only sets the display label for personal and project skills — the
command name comes from the directory. In a **plugin** skill, `name` still sets
the last segment of the command.

## TodoWrite → Task Tools

**Before (disabled by default since 2.1.142):**
```yaml
allowed-tools: [TodoWrite]
```

**After (current):**
```yaml
allowed-tools: [TaskCreate, TaskGet, TaskList, TaskUpdate]
```

Set `CLAUDE_CODE_ENABLE_TASKS=0` to restore `TodoWrite`.

As of 2.1.268 neither the `Task*` tools nor `TodoWrite` are provided by default
on newer models (anything after Opus 4.7 / Sonnet 4.6 / Haiku 4.5, e.g. Opus
4.8+, Sonnet 5, Fable). Don't rely on them in an agent or skill that may run on
those models; opt in with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` or by naming one of the
tools in `--allowedTools` / `--tools`. A subagent only gets them when the
session has them.

## TaskOutput → Read

**Before (deprecated):**
```
TaskOutput({task_id: "..."})
```

**After (current):**
```
Read the task's output file path directly.
```

## Hook Script Paths: Shell Form → Exec Form

Shell form needs quoting for paths with spaces; exec form doesn't.

**Before:**
```json
{
  "type": "command",
  "command": "node \"${CLAUDE_PLUGIN_ROOT}\"/scripts/format.js --fix"
}
```

**After (preferred whenever a path placeholder is involved):**
```json
{
  "type": "command",
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/format.js", "--fix"]
}
```

## Agent Teams: teammateDefaultModel → Spawn Prompt

**Before (removed in 2.1.234, now ignored):**
```json
{ "teammateDefaultModel": "sonnet" }
```

**After (current):** name the model in the prompt that spawns the teammate
("spawn a reviewer teammate on Sonnet"), set `model` in the subagent
definition the teammate is spawned from, or set `CLAUDE_CODE_SUBAGENT_MODEL`.

## ANTHROPIC_SMALL_FAST_MODEL → ANTHROPIC_DEFAULT_HAIKU_MODEL

**Before (deprecated):**
```bash
export ANTHROPIC_SMALL_FAST_MODEL=claude-haiku-4-5-20251001
```

**After (current):**
```bash
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5-20251001
```
