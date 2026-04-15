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

**Note:** Commands and skills are now equivalent — both create `/name` slash commands. Prefer skills for richer structure.

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

**Name rules:** Max 64 chars, lowercase letters/numbers/hyphens only.

**Dynamic context:** Use `` !`command` `` to inject runtime data into skills.

**Anti-pattern:** Avoid offering menus or lists of options in skill output. Skills should take action based on context, not present choices.

## Creating Agents

Agents run autonomously via the Agent tool.

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
permissionMode: default
maxTurns: 50
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
- Use gerund naming: `processing-pdfs`, `reviewing-code`, `analyzing-logs`

## Creating Plugins

Plugins bundle extensions for distribution.

**Structure:**
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── .claude/
│   └── settings.local.json
├── settings.json              # Plugin defaults (optional)
├── .lsp.json                  # LSP server config (optional)
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

# Use /reload-plugins to pick up changes (no restart needed)

# When ready, add to marketplace
${CLAUDE_PLUGIN_ROOT}/scripts/marketplace_manager.py add <marketplace> ./my-plugin

# Install for production
/plugin install my-plugin@marketplace-name
```

## Adding to Marketplace

To register a plugin in a local marketplace:

1. Validate plugin structure (preferred — uses built-in validation):
   ```bash
   /plugin validate ./my-plugin
   # or: claude plugin validate ./my-plugin
   ```

2. Add to marketplace (local management):
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/scripts/marketplace_manager.py add <marketplace-path> ./my-plugin
   ```

3. Verify:
   ```bash
   ${CLAUDE_PLUGIN_ROOT}/scripts/marketplace_manager.py list <marketplace-path>
   ```

Marketplaces support multiple source types beyond local paths (GitHub, npm, pip, URLs). See `references/marketplaces.md` for full marketplace documentation.

## Marketplace-aware plugin scaffolding

When creating a plugin, choose the right flow based on where the user is invoking from. Run `scripts/marketplace_register.py` for three-flow orchestration; it handles detection and writes marketplace.json correctly for each case.

### Detection: is the user inside an existing umbrella?

`marketplace_register.py` walks upward from `--plugin-path` looking for an ancestor `.claude-plugin/marketplace.json`. If found, it uses the register-into-existing flow automatically.

### Three flows

| Detected state | User choice | Action |
|----------------|-------------|--------|
| Ancestor marketplace found | n/a | Register new plugin entry into the existing marketplace.json (safe JSON append, idempotent) |
| Greenfield | standalone (default) | Scaffold plugin with its own `.claude-plugin/marketplace.json` at the plugin root; immediately installable |
| Greenfield | umbrella | Scaffold umbrella dir + first plugin entry |

### Invocation

**Standalone (default, greenfield):**
```bash
# Create the plugin skeleton (auto-creates marketplace.json at plugin root)
python3 scripts/plugin_scaffolder.py my-plugin \
    --output ./ \
    --author "Author Name" \
    --email "author@example.com"

# Result: ./my-plugin/.claude-plugin/{plugin.json,marketplace.json}
# Install with: /plugin marketplace add ./my-plugin
```

**Umbrella (greenfield, scaffolding a new umbrella and first plugin):**
```bash
# First create the plugin dir with no marketplace.json
python3 scripts/plugin_scaffolder.py my-plugin --output ./my-umbrella --marketplace none

# Then register it into a new umbrella marketplace.json
python3 scripts/marketplace_register.py my-plugin \
    --plugin-path ./my-umbrella/my-plugin \
    --layout umbrella \
    --owner "Owner Name" \
    --marketplace-name my-umbrella \
    --umbrella-path ./my-umbrella
```

**Register into existing umbrella (detection):**
```bash
# CWD is inside an existing umbrella; scaffolder skips marketplace.json creation
python3 scripts/plugin_scaffolder.py new-plugin --output . --marketplace none

# Register into the ancestor marketplace (upward-search finds it automatically)
python3 scripts/marketplace_register.py new-plugin \
    --plugin-path ./new-plugin \
    --layout auto \
    --owner "Owner Name"
```

### Safety guarantees

- Reserved marketplace names (per `data/version-manifest.json` `schemas.marketplace_manifest.reserved_names`) are rejected before any file is written.
- Plugin paths containing `../` or outside the marketplace root are rejected with a clear error.
- Duplicate plugin names within a marketplace raise `Plugin '<name>' already registered`.
- The one-level invariant is preserved: standalone writes marketplace.json at plugin root; register-into-existing writes nothing new at plugin root.

### References

- Schema: [`references/marketplace-schema.md`](../../references/marketplace-schema.md)
- CLI / auth / caching: [`references/marketplaces.md`](../../references/marketplaces.md)
- Validator: `scripts/marketplace_manager.py validate <marketplace-root>` (see `extension-optimizer` skill)

## Progressive Disclosure

Keep SKILL.md lean. Move details to `references/`:

| SKILL.md | references/ |
|----------|-------------|
| Core workflow | Detailed patterns |
| Quick reference | API documentation |
| Pointers | Advanced techniques |

**Target:** SKILL.md under 1500 tokens total.

**Limits:** SKILL.md should stay under ~500 lines. Add table of contents if references exceed 100 lines.

## Evaluation-Driven Development

Test skills across models (sonnet, opus, haiku) before deploying. Different models may interpret descriptions and workflows differently.

## Additional Resources

- `references/frontmatter.md` - All frontmatter fields
- `references/templates.md` - Complete templates
- `references/locations.md` - Where to put files
- `references/tools.md` - Tool restriction patterns
- `examples/code-reviewer.md` - Working agent example
