# Plugin Directory Structure

## Layout

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # REQUIRED
├── commands/            # /command-name
├── agents/              # Task tool subagents
├── skills/*/SKILL.md    # Domain expertise
├── hooks/hooks.json     # Lifecycle automation
├── .mcp.json            # MCP servers
└── README.md
```

## Auto-Discovery

| Component | Pattern | Activation |
|-----------|---------|------------|
| Commands | `commands/**/*.md` | `/command-name` |
| Agents | `agents/*.md` | Task tool |
| Skills | `skills/*/SKILL.md` | Context-based |
| Hooks | `hooks/hooks.json` | Events |
| MCP | `.mcp.json` | Session start |

## Examples

**Minimal:**
```
plugin/
├── .claude-plugin/plugin.json
└── commands/hello.md
```

**Standard:**
```
plugin/
├── .claude-plugin/plugin.json
├── commands/
├── agents/
└── README.md
```

## Hooks Configuration

```json
{
  "description": "Plugin hooks",
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{"type": "command", "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/handler.py"}]
    }]
  }
}
```

Use `${CLAUDE_PLUGIN_ROOT}` for portable paths.
