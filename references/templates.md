# Extension Templates

Ready-to-use templates for all extension types.

## Minimal Command

```markdown
---
description: Brief description for /help
---

# Command Name

Instructions for what to do when invoked.
```

**File:** `~/.claude/commands/my-command.md` or `.claude/commands/my-command.md`

## Command with Arguments

```markdown
---
description: Process a file with options
argument-hint: "filename [--option]"
allowed-tools:
  - Read
  - Write
---

# Process File

Read the specified file and process it according to options.

## Arguments
- First argument: filename to process
- `--option`: Enable optional behavior
```

## Minimal Skill

```markdown
---
name: my-skill
description: Processes X when the user asks to "do X" or needs help with Y.
---

# My Skill

Brief overview.

## Workflow

1. First step
2. Second step
3. Third step
```

**Directory:** `~/.claude/skills/my-skill/SKILL.md`

## Full Skill with References

```
my-skill/
├── SKILL.md
├── references/
│   ├── patterns.md
│   └── advanced.md
└── examples/
    └── sample.md
```

**SKILL.md:**
```markdown
---
name: my-skill
description: Comprehensive skill for X. Use when the user asks to "do X", "configure X", or needs help with X patterns.
---

# My Skill

Domain expertise for X.

## Quick Start

Essential workflow:
1. Gather requirements
2. Apply pattern
3. Validate result

## Patterns

| Pattern | When to Use |
|---------|-------------|
| Pattern A | Situation A |
| Pattern B | Situation B |

## Additional Resources

- `references/patterns.md` - All patterns in detail
- `references/advanced.md` - Advanced techniques
```

## Minimal Agent

```markdown
---
name: my-agent
description: |
  Performs task X autonomously.

  <example>
  user: "Do X for me"
  assistant: "I'll launch my-agent to handle this."
  </example>
---

# My Agent

You are an autonomous agent for task X.

## Objectives

1. Accomplish goal A
2. Ensure constraint B
3. Report findings

## Approach

Work through the task step by step.
```

**File:** `~/.claude/agents/my-agent.md`

## Agent with Tool Restrictions

```markdown
---
name: code-reviewer
description: |
  Reviews code for issues. Read-only, never modifies code.

  <example>
  user: "Review this PR"
  assistant: "I'll launch code-reviewer for analysis."
  </example>
tools:
  - Read
  - Glob
  - Grep
  - WebFetch
color: cyan
---

# Code Reviewer

You are a code review agent. Analyze code quality, patterns, and potential issues.

## Constraints

- NEVER modify files
- ONLY read and analyze
- Report findings clearly

## Review Checklist

1. Code structure and organization
2. Error handling
3. Security concerns
4. Performance issues
5. Best practices
```

## Plugin Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── .claude/
│   └── settings.local.json
├── skills/
│   └── my-skill/
│       └── SKILL.md
├── commands/
│   └── my-command.md
├── agents/
│   └── my-agent.md
├── hooks/
│   ├── hooks.json
│   └── check_script.sh
└── README.md
```

**plugin.json:**
```json
{
  "name": "my-plugin",
  "description": "Plugin providing X capabilities",
  "version": "1.0.0",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "keywords": ["domain", "feature"]
}
```

**settings.local.json (for development):**
```json
{
  "permissions": {
    "allow": []
  }
}
```

## CLAUDE.md Templates

### Project Rules

```markdown
# Project: MyProject

## Coding Standards

- Use TypeScript strict mode
- Prefer functional patterns
- Keep functions under 20 lines

## Architecture

- `/src/components/` - React components
- `/src/services/` - API layer
- `/src/utils/` - Pure utilities

## Commands

- `npm test` - Run tests
- `npm run lint` - Check linting
```

### Personal Rules (~/.claude/CLAUDE.md)

```markdown
# Claude Configuration

## Preferences

- Use concise responses
- Prefer Python 3.11+ features
- Default to uv for Python projects

## File Locations

- Notes: ~/notes/
- Projects: ~/dev/
```

## Marketplace Registration

**marketplace.json:**
```json
{
  "name": "my-marketplace",
  "plugins": [
    {"path": "plugin-a", "name": "plugin-a"},
    {"path": "plugin-b", "name": "plugin-b"}
  ]
}
```

**Location:** `<marketplace-root>/.claude-plugin/marketplace.json`
