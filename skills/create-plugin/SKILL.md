---
name: create-plugin
description: This skill should be used when the user asks to "create a plugin", "scaffold a plugin", "make a Claude Code plugin", "bundle commands into a plugin", "package extensions", or needs help with plugin.json, plugin structure, plugin lifecycle, publishing plugins, or installing plugins.
---

# Creating Plugins

Plugins are shareable packages that bundle multiple Claude Code extensions (commands, skills, agents, hooks, MCP servers) for distribution.

## Locations

| Location | Scope |
|----------|-------|
| `~/.claude/plugins/` | Installed plugins |
| `.claude-plugin/` | Project-local plugin |
| `/plugin install name@marketplace` | Install from marketplace |

## Structure

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # Required: manifest
├── commands/            # Slash commands
├── agents/              # Subagents
├── skills/              # Domain expertise
├── hooks/               # Lifecycle automation
│   └── hooks.json
├── .mcp.json            # MCP server config
└── README.md
```

## Minimal Plugin

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── commands/
    └── my-command.md
```

**plugin.json** (required):
```json
{
  "name": "my-plugin",
  "description": "What this plugin does",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  }
}
```

## Plugin Manifest

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Plugin identifier (kebab-case) |
| `description` | Yes | Clear description |
| `author.name` | Yes | Author name |
| `author.email` | Yes | Contact email |
| `version` | No | Semantic version (e.g., "1.0.0") |
| `homepage` | No | Project URL |
| `repository` | No | Git repository URL |
| `license` | No | License identifier (MIT, etc.) |
| `keywords` | No | Search tags |

## Component Integration

Plugins bundle existing extension types. Use these skills to create components:

| Component | Creation Skill | File Pattern |
|-----------|---------------|--------------|
| Commands | `/create-command` | `commands/{name}.md` |
| Skills | `/create-skill` | `skills/{name}/SKILL.md` |
| Agents | `/create-agent` | `agents/{name}.md` |
| Hooks | `/create-rules` | `hooks/hooks.json` + scripts |

**Portable paths**: Use `${CLAUDE_PLUGIN_ROOT}` in hook scripts for the plugin directory.

## Workflow

1. **Scaffold** - Create directory structure and plugin.json
2. **Add components** - Use create-* skills for each extension
3. **Test locally** - `claude --plugin-dir /path/to/plugin`
4. **Document** - Write comprehensive README.md
5. **Publish** - Submit to marketplace (see `references/lifecycle.md`)

## Quick Reference

```bash
# Test plugin locally
claude --plugin-dir ./my-plugin

# Install from marketplace
/plugin install plugin-name@claude-plugins-official

# List installed plugins
/plugins
```

## Additional Resources

### Reference Files
- `references/structure.md` - Directory patterns and conventions
- `references/templates.md` - Ready-to-use plugin templates
- `references/lifecycle.md` - Install, update, publish workflows

### Official Documentation
- [Plugins Guide](https://docs.anthropic.com/en/docs/claude-code/plugins)

### Marketplace Plugin
For comprehensive plugin development with specialized agents:
```
/plugin install plugin-dev@claude-plugins-official
```
