---
name: claude-dev
description: This skill should be used when the user asks to "extend Claude", "customize Claude Code", "add automation", "create Claude extensions", or needs help deciding between commands, skills, agents, rules, or hooks. Use this as the entry point for all Claude Code customization.
---

# Claude Code Development

Orchestrator for creating Claude Code extensions. Analyze requirements and select the appropriate extension type.

## Decision Framework

```
What do you need?
│
├─ Reusable prompt? ──────────────────► COMMAND
│  (Quick action, user-invoked)
│
├─ Specialized knowledge? ────────────► SKILL
│  (Domain expertise, workflows)
│
├─ Autonomous subprocess? ────────────► AGENT
│  (Complex multi-step tasks)
│
├─ Behavior rules/automation? ────────► RULES
│  (CLAUDE.md, hooks, settings)
│
└─ Shareable package? ────────────────► PLUGIN
   (Bundle multiple extensions)
```

## Extension Types

| Type | Trigger | Purpose | Examples |
|------|---------|---------|----------|
| Command | `/name` | Single action prompt | `/review`, `/deploy` |
| Skill | Context match | Domain knowledge | PDF editing, APIs |
| Agent | Task tool | Autonomous work | code-reviewer |
| Rule/Hook | Always active | Behavior control | safety checks |
| CLAUDE.md | Session start | Project context | coding standards |
| Plugin | `/plugin install` | Bundled package | MCP + commands + hooks |

## Workflow

1. **Clarify** - What problem? What trigger?
2. **Match** - Use decision framework above
3. **Create** - Invoke the appropriate skill:

| Skill | Creates | References |
|-------|---------|------------|
| `/create-command` | Slash commands | templates.md, advanced.md |
| `/create-skill` | Domain expertise | templates.md, structure.md |
| `/create-agent` | Autonomous agents | templates.md, patterns.md |
| `/create-rules` | CLAUDE.md, hooks | hooks.md, templates.md |
| `/create-plugin` | Shareable bundles | structure.md, templates.md, lifecycle.md |

## Official Documentation

- [Claude Code Overview](https://docs.anthropic.com/en/docs/claude-code)
- [Slash Commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands)
- [Skills](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Custom Agents](https://docs.anthropic.com/en/docs/claude-code/custom-agents)
- [Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [Plugins](https://docs.anthropic.com/en/docs/claude-code/plugins)
