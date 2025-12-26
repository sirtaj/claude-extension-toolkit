---
name: create-agent
description: This skill should be used when the user asks to "create an agent", "add a subagent", "write an agent", or needs help with agent frontmatter, triggering conditions, system prompts, or the Task tool.
---

# Creating Agents

Agents are autonomous subprocesses launched via the Task tool for complex, multi-step tasks.

## Locations

| Location | Scope |
|----------|-------|
| `~/.claude/agents/` | Global (all projects) |
| `.claude/agents/` | Project-specific |

## Minimal Agent

Create `agent-name.md`:

```markdown
---
name: my-agent
description: Use this agent when the user needs [capability]. Examples:

<example>
user: "[User request]"
assistant: "[Response using agent]"
<commentary>[Why appropriate]</commentary>
</example>

model: sonnet
color: blue
---

You are [role] specializing in [domain].

**Responsibilities:**
1. First responsibility
2. Second responsibility

**Process:**
1. Step one
2. Step two

**Output Format:**
- What to include
```

## Frontmatter Reference

| Field | Required | Values |
|-------|----------|--------|
| `name` | Yes | lowercase-hyphens (3-50 chars) |
| `description` | Yes | Trigger conditions + 2-4 examples |
| `model` | Yes | inherit/haiku/sonnet/opus |
| `color` | Yes | blue/cyan/green/yellow/magenta/red |
| `tools` | No | `["Read", "Write"]` (default: all) |

## Description Format

The description determines when Claude launches the agent. Include 2-4 `<example>` blocks with varied triggers.

See `references/patterns.md#description-example-patterns` for full patterns.

## Model Selection

| Model | Use For |
|-------|---------|
| `inherit` | Same as parent (default) |
| `haiku` | Fast, simple tasks |
| `sonnet` | Balanced (most agents) |
| `opus` | Complex analysis |

## Tool Restrictions

| Use Case | Tools |
|----------|-------|
| Read-only | `["Read", "Grep", "Glob"]` |
| Code generation | `["Read", "Write", "Edit"]` |
| Testing | `["Read", "Bash"]` |

Omit field for full access.

## Additional Resources

### Reference Files
- `references/templates.md` - Ready-to-use agent templates
- `references/patterns.md` - System prompt patterns

### Official Documentation
- [Custom Agents Guide](https://docs.anthropic.com/en/docs/claude-code/custom-agents)
