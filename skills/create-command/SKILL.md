---
name: create-command
description: This skill should be used when the user asks to "create a slash command", "add a command", "write a command", "make a /command", or needs help with command frontmatter, arguments, or file references.
---

# Creating Slash Commands

Slash commands are Markdown files defining reusable prompts.

## Locations

| Location | Scope |
|----------|-------|
| `~/.claude/commands/` | Global (all projects) |
| `.claude/commands/` | Project-specific |

## Minimal Command

Create `command-name.md`:
```markdown
Do something useful with the current context.
```

## With Configuration

```markdown
---
description: Brief description for /help
allowed-tools: Read, Grep, Bash(git:*)
model: sonnet
argument-hint: [file] [options]
---

Review @$1 for issues.
```

## Core Features

| Feature | Syntax | Example |
|---------|--------|---------|
| All args | `$ARGUMENTS` | `Fix #$ARGUMENTS` |
| Positional | `$1`, `$2` | `Deploy $1 to $2` |
| File ref | `@path` | `Review @$1` |
| Bash | `` !`cmd` `` | `` !`git status` `` |

## Frontmatter Reference

| Field | Purpose |
|-------|---------|
| `description` | Shown in `/help` |
| `allowed-tools` | Restrict tools |
| `model` | haiku/sonnet/opus |
| `argument-hint` | Document args |

## Additional Resources

### Reference Files
- `references/templates.md` - Ready-to-use templates
- `references/advanced.md` - Advanced patterns

### Official Documentation
- [Slash Commands Guide](https://docs.anthropic.com/en/docs/claude-code/slash-commands)
