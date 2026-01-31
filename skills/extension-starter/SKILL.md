---
name: extension-starter
description: Guides Claude Code customization decisions and provides quick-start templates. Use when starting extension development, deciding what to build, or needing "extend Claude", "customize Claude", "quick template", or "what should I create".
---

# Extension Starter

Entry point for Claude Code customization. Analyze requirements and select the right extension type.

## Decision Framework

```
What do you need?
│
├─ Quick reusable prompt? ──────────────► COMMAND
│  User-invoked with /name
│  Examples: /commit, /review, /deploy
│
├─ Domain expertise? ───────────────────► SKILL
│  Context-triggered, specialized knowledge
│  Examples: PDF editing, API integration
│
├─ Autonomous work? ────────────────────► AGENT
│  Multi-step tasks via Task tool
│  Examples: code-reviewer, test-runner
│
├─ Always-on behavior? ─────────────────► HOOKS
│  Automatic triggers on events
│  Examples: lint on save, block dangerous commands
│
├─ Project context? ────────────────────► CLAUDE.md
│  Loaded at session start
│  Examples: coding standards, architecture
│
└─ Shareable package? ──────────────────► PLUGIN
   Bundle multiple extensions
   Examples: language toolkits
```

## Quick Reference

| Type | Trigger | Scope | Location |
|------|---------|-------|----------|
| Command | `/name` | Single action | `commands/name.md` |
| Skill | Context match | Domain knowledge | `skills/name/SKILL.md` |
| Agent | Task tool | Autonomous | `agents/name.md` |
| Hook | Tool/event | Automatic | `settings.json` |
| CLAUDE.md | Session start | Project rules | `./CLAUDE.md` |
| Plugin | `/plugin install` | Bundled | `.claude-plugin/` |

## Quick Templates

### Minimal Command

```markdown
---
description: What this command does
---

Do the thing when invoked.
```
Save to: `~/.claude/commands/my-command.md`

### Minimal Skill

```markdown
---
name: my-skill
description: Handles X tasks. Use when the user asks to "do X" or needs help with X.
---

# My Skill

## Workflow
1. First step
2. Second step
```
Save to: `~/.claude/skills/my-skill/SKILL.md`

### Minimal Agent

```markdown
---
name: my-agent
description: |
  Autonomous agent for X.
  <example>
  user: "Do X"
  assistant: "Launching my-agent"
  </example>
---

You are an agent for X. Work step by step.
```
Save to: `~/.claude/agents/my-agent.md`

### Minimal Hook

```json
{
  "PostToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "command",
      "command": "echo 'File modified'"
    }]
  }]
}
```
Add to: `~/.claude/settings.json` under `"hooks"`

## Next Steps

For detailed guidance:
- `/extension-builder` - Create extensions with full structure
- `/extension-rules` - Configure CLAUDE.md and hooks
- `/extension-optimizer` - Validate and improve extensions
