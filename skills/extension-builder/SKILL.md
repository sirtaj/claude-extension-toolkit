---
name: extension-builder
description: Creates Claude Code extensions with proper structure and frontmatter. Use when building skills, agents, commands, or plugins. Triggers: "create skill", "create agent", "create command", "create plugin", "scaffold extension", "add to marketplace".
---

# Extension Builder

Creates properly structured Claude Code extensions.

## Extension Spectrum

| Type | Tokens | Structure | Use Case |
|------|--------|-----------|----------|
| Command | <200 | Single file | Quick actions |
| Skill | 500-1500 | Directory + refs | Domain expertise |
| Agent | 800-2000 | Single file | Autonomous work |
| Plugin | Variable | Full package | Distribution |

## Creating Commands

Commands are user-invoked prompts.

**Structure:**
```
~/.claude/commands/
└── my-command.md
```

**Template:**
```markdown
---
description: Brief description for /help
argument-hint: "optional args"
allowed-tools:
  - Read
  - Write
---

Instructions for what to do when /my-command is invoked.
```

See `references/frontmatter.md` for all fields.

## Creating Skills

Skills provide domain expertise triggered by context.

**Structure:**
```
~/.claude/skills/my-skill/
├── SKILL.md           # Core (500-1500 tokens)
├── references/        # Details (loaded on demand)
│   ├── patterns.md
│   └── advanced.md
└── examples/
    └── sample.md
```

**Template:**
```markdown
---
name: my-skill
description: Handles X tasks. Use when the user asks to "do X", "configure X", or mentions X concepts.
---

# My Skill

Brief overview of what this skill does.

## Quick Start

Essential workflow:
1. Gather requirements
2. Apply pattern
3. Validate result

## Common Patterns

| Pattern | When to Use |
|---------|-------------|
| A | Situation A |
| B | Situation B |

## Additional Resources

- `references/patterns.md` - All patterns
- `references/advanced.md` - Advanced techniques
```

**Description format:** Third person, prescriptive. Include trigger phrases.

## Creating Agents

Agents run autonomously via the Task tool.

**Structure:**
```
~/.claude/agents/
└── my-agent.md
```

**Template:**
```markdown
---
name: my-agent
description: |
  Performs X autonomously. Use for complex X tasks.

  <example>
  user: "Do X for this project"
  assistant: "I'll launch my-agent to handle this."
  </example>

  <example>
  user: "Check X across the codebase"
  assistant: "Let me use my-agent for thorough analysis."
  </example>
tools:
  - Read
  - Glob
  - Grep
color: cyan
---

# My Agent

You are an autonomous agent specialized in X.

## Objectives

1. Primary goal
2. Secondary goal
3. Constraints

## Approach

Work through the task methodically:
1. Discover relevant files
2. Analyze each
3. Report findings
```

**Key points:**
- Include `<example>` blocks for reliable triggering
- Restrict tools to minimum needed
- Define clear objectives

## Creating Plugins

Plugins bundle extensions for distribution.

**Structure:**
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── .claude/
│   └── settings.local.json
├── skills/
├── commands/
├── agents/
├── hooks/
└── README.md
```

**plugin.json:**
```json
{
  "name": "my-plugin",
  "description": "What this plugin provides",
  "version": "1.0.0",
  "author": {"name": "Your Name"},
  "keywords": ["domain", "feature"]
}
```

**Development workflow:**
```bash
# Test during development
claude --plugin-dir ./my-plugin

# Restart to pick up changes (no hot reload)

# When ready, add to marketplace
python scripts/marketplace_manager.py add <marketplace> ./my-plugin

# Install for production
/plugin install my-plugin@marketplace-name
```

## Adding to Marketplace

To register a plugin in a local marketplace:

1. Validate plugin structure:
   ```bash
   python scripts/validate_extension.py ./my-plugin
   ```

2. Add to marketplace:
   ```bash
   python scripts/marketplace_manager.py add <marketplace-path> ./my-plugin
   ```

3. Verify:
   ```bash
   python scripts/marketplace_manager.py list <marketplace-path>
   ```

## Progressive Disclosure

Keep SKILL.md lean. Move details to `references/`:

| SKILL.md | references/ |
|----------|-------------|
| Core workflow | Detailed patterns |
| Quick reference | API documentation |
| Pointers | Advanced techniques |

**Target:** SKILL.md under 1500 tokens total.

## Additional Resources

- `references/frontmatter.md` - All frontmatter fields
- `references/templates.md` - Complete templates
- `references/locations.md` - Where to put files
- `references/tools.md` - Tool restriction patterns
- `examples/code-reviewer.md` - Working agent example
