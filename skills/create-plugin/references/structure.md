# Plugin Directory Structure

## Full Layout

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # REQUIRED: Plugin manifest
│
├── commands/                 # User-invoked slash commands
│   ├── my-command.md        # /my-command
│   └── subdirectory/        # Organized by category
│       └── nested.md        # /subdirectory/nested
│
├── agents/                   # Autonomous subagents
│   └── my-agent.md          # Spawned via Task tool
│
├── skills/                   # Domain expertise packages
│   └── my-skill/
│       ├── SKILL.md         # Core skill file
│       ├── references/      # Detailed documentation
│       └── scripts/         # Utility scripts
│
├── hooks/                    # Lifecycle automation
│   ├── hooks.json           # Hook configuration
│   └── handler.py           # Script handlers
│
├── .mcp.json                 # MCP server configuration
└── README.md                 # Documentation
```

## Auto-Discovery Rules

| Component | Discovery Pattern | Activation |
|-----------|-------------------|------------|
| Commands | `commands/**/*.md` | User types `/command-name` |
| Agents | `agents/*.md` | Claude spawns via Task tool |
| Skills | `skills/*/SKILL.md` | Context-based activation |
| Hooks | `hooks/hooks.json` | Lifecycle events |
| MCP | `.mcp.json` | Session start |

## Naming Conventions

- **Plugin name**: kebab-case (`my-awesome-plugin`)
- **Commands**: kebab-case (`run-tests.md` → `/run-tests`)
- **Agents**: kebab-case (`code-reviewer.md`)
- **Skills**: kebab-case directories (`pdf-tools/SKILL.md`)

## Plugin Examples

### Minimal (Command Only)

```
hello-plugin/
├── .claude-plugin/
│   └── plugin.json
└── commands/
    └── hello.md
```

### Standard (Commands + Agents)

```
code-helper/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── review.md
│   └── test.md
├── agents/
│   └── code-reviewer.md
└── README.md
```

### Full (All Components)

```
full-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── setup.md
│   └── deploy.md
├── agents/
│   ├── analyzer.md
│   └── generator.md
├── skills/
│   └── domain-expert/
│       ├── SKILL.md
│       └── references/
│           └── api.md
├── hooks/
│   ├── hooks.json
│   └── security-check.py
├── .mcp.json
└── README.md
```

## Hooks Configuration

**hooks/hooks.json**:
```json
{
  "description": "Plugin hooks description",
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/handler.py",
            "timeout": 10
          }
        ],
        "matcher": "Edit|Write"
      }
    ]
  }
}
```

**Available events**:
- `PreToolUse` - Before tool execution
- `PostToolUse` - After tool execution
- `UserPromptSubmit` - When user submits prompt
- `Stop` - When Claude stops
- `SessionStart` - When session starts

## MCP Configuration

**.mcp.json**:
```json
{
  "mcpServers": {
    "my-server": {
      "type": "http",
      "url": "https://mcp.example.com/api"
    }
  }
}
```

## Variable Substitution

Use `${CLAUDE_PLUGIN_ROOT}` in hook commands for portable paths:

```json
{
  "command": "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/script.py"
}
```

This resolves to the plugin's installation directory at runtime.
