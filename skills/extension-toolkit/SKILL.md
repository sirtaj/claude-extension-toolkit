---
name: extension-toolkit
description: Creates, configures, and debugs Claude Code extensions (skills, agents, commands, hooks, plugins). Single entrypoint for all extension development. Use when the user asks to "create a skill", "build an agent", "make a command", "add a hook", "scaffold a plugin", "debug activation", "fix my extension", "extend Claude", or mentions extension development concepts.
---

# Extension Toolkit

Build, configure, and debug Claude Code extensions.

## Workflow

1. Determine what the user needs (type selection)
2. Gather requirements interactively
3. Scaffold the extension
4. Guide testing with `/reload-plugins`
5. Debug if activation or behavior is wrong

For bulk audit/validation/migration, spawn the `extension-auditor` agent.

## Type Selection

```
What do you need?
│
├─ Reusable prompt? ────────────────► COMMAND (commands/name.md)
│  User-invoked with /name
│
├─ Domain expertise? ───────────────► SKILL (skills/name/SKILL.md)
│  Context-triggered knowledge
│
├─ Autonomous work? ────────────────► AGENT (agents/name.md)
│  Multi-step tasks via Agent tool
│
├─ Automatic trigger? ──────────────► HOOK (settings.json)
│  Fires on tool use or events
│
├─ Shareable bundle? ───────────────► PLUGIN (.claude-plugin/)
│  Package multiple extensions
│
└─ Project context? ────────────────► CLAUDE.md
   Loaded at session start
```

## Extension Anatomy

| Type | Tokens | Structure | Trigger |
|------|--------|-----------|---------|
| Command | <200 | Single `.md` | `/name` |
| Skill | 500-1500 | Directory + refs | Context match |
| Agent | 800-2000 | Single `.md` | Agent tool |
| Hook | N/A | JSON + script | Tool/event |
| Plugin | Variable | Full package | `/plugin install` |

## Creating Commands

```markdown
---
description: Brief description for /help
argument-hint: "optional args"
allowed-tools:
  - Read
  - Write
---

Instructions for what to do when invoked.
```
Save to: `~/.claude/commands/my-command.md` or `<plugin>/commands/my-command.md`

## Creating Skills

```markdown
---
name: my-skill
description: Handles X tasks. Use when the user asks to "do X" or mentions X concepts.
---

# My Skill

## Workflow
1. Step one
2. Step two

## Patterns
| Pattern | When |
|---------|------|
| A | Situation A |
```
Save to: `~/.claude/skills/my-skill/SKILL.md`

Move detailed content to `references/` subdirectory. Keep SKILL.md under 1500 tokens.

Dynamic context: prefix a backtick-wrapped shell command with `!` to inject runtime data.

## Creating Agents

```markdown
---
name: my-agent
description: |
  Performs X autonomously.
  <example>
  user: "Do X"
  assistant: "Launching my-agent."
  </example>
tools:
  - Read
  - Glob
  - Grep
maxTurns: 50
---

You are an agent for X. Work methodically:
1. Discover
2. Analyze
3. Report
```
Save to: `~/.claude/agents/my-agent.md`

Key rules:
- Include 2-3 `<example>` blocks for reliable triggering
- Restrict tools to minimum needed
- Use gerund naming: `reviewing-code`, `analyzing-logs`

## Creating Hooks

Add to `settings.json` (or plugin's `settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "path/to/check.sh", "timeout": 30}]
    }],
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{"type": "command", "command": "path/to/lint.sh"}]
    }]
  }
}
```

Hook scripts receive JSON via stdin, exit 0 (allow) or 2 (block with message).

```bash
#!/bin/bash
set -euo pipefail
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
# logic here
exit 0
```

Handler types: `command`, `http`, `mcp_tool`, `prompt`, `agent`.
Events: SessionStart, PreToolUse, PostToolUse, Stop, and 27 more — see
`${CLAUDE_PLUGIN_ROOT}/references/hooks.md`.

## Creating Plugins

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json        # optional; only `name` is required
├── hooks/hooks.json       # hook config
├── settings.json          # plugin defaults (agent, subagentStatusLine only)
├── skills/
├── commands/
├── agents/
└── README.md
```

Do NOT put `skills`, `agents`, `commands` arrays in plugin.json — Claude Code auto-discovers them.

Development: `claude --plugin-dir ./my-plugin`. Edits to `SKILL.md` and agent
files are picked up live; `hooks/`, `.mcp.json`, and `output-styles/` need
`/reload-plugins`.

For marketplace registration, see `references/marketplace-scaffolding.md`.

## Debugging Activation

When an extension isn't working:

1. **Skill not triggering?**
   - Check `description` contains trigger phrases matching user intent
   - Put the key use case first: `description` + `when_to_use` is truncated at 1,536 chars in the listing
   - Verify name is valid: `^[a-z0-9-]+$`, max 64 chars
   - Test with explicit `/skill-name` invocation
   - Check for competing skills with overlapping descriptions
   - Check `paths` isn't scoping it away from the files in play

2. **Agent not spawning?**
   - Verify `<example>` blocks match real usage patterns
   - Check `tools` list includes what the agent needs
   - Ensure description is in agent definition, not just body

3. **Hook not firing?**
   - Verify event name matches exactly (case-sensitive)
   - Check `matcher` regex matches the tool name
   - Test script standalone: `echo '{}' | ./hook.sh`
   - Check exit code behavior (only 2 blocks, 0 allows)

4. **Plugin not loading?**
   - Run `claude plugin validate ./my-plugin` (add `--strict` to fail on warnings)
   - If a `.claude-plugin/plugin.json` exists, check it is valid JSON
   - Verify `author` is `{name: "..."}` not a string
   - Check components sit at the plugin root, not inside `.claude-plugin/`

## Additional Resources

Shared references (at `${CLAUDE_PLUGIN_ROOT}/references/`):
- `frontmatter.md` - All frontmatter fields
- `hooks.md` - Complete hook events reference
- `templates.md` - Full templates for each type
- `tools.md` - Tool restriction patterns
- `locations.md` - Where to put files

Skill-local references (in this skill's `references/` directory):
- `marketplace-scaffolding.md` - Plugin marketplace flows

On-demand examples (at `${CLAUDE_PLUGIN_ROOT}/references/`):
- `example-agent.md` - Working agent example
