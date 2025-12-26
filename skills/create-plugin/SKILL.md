---
name: create-plugin
description: This skill should be used when the user asks to "create a plugin", "scaffold a plugin", "make a Claude Code plugin", "bundle commands into a plugin", or needs help with plugin.json, plugin structure, or publishing plugins.
---

# Creating Plugins

Plugins bundle Claude Code extensions (commands, skills, agents, hooks, MCP) for distribution.

## Structure

```
plugin-name/
├── .claude-plugin/plugin.json  # Required
├── commands/                   # /command-name
├── agents/                     # Task tool
├── skills/*/SKILL.md           # Context-based
├── hooks/hooks.json            # Events
└── .mcp.json                   # MCP servers
```

## plugin.json (Required)

```json
{
  "name": "my-plugin",
  "description": "What it does",
  "author": {"name": "You", "email": "you@ex.com"}
}
```

Optional: `version`, `homepage`, `repository`, `license`, `keywords`

## Workflow

1. Create structure with plugin.json
2. Add components using `/create-command`, `/create-skill`, `/create-agent`, `/create-rules`
3. Test: `claude --plugin-dir ./my-plugin`
4. Publish to marketplace (see `references/lifecycle.md`)

Use `${CLAUDE_PLUGIN_ROOT}` in hook scripts for portable paths.

## Additional Resources

- `references/structure.md` - Directory patterns
- `references/templates.md` - Plugin templates
- `references/lifecycle.md` - Install/publish workflows
- [Plugins Guide](https://docs.anthropic.com/en/docs/claude-code/plugins)
