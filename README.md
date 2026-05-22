# Claude Extension Toolkit

A plugin that helps you build Claude Code extensions — skills, agents, commands, hooks, and plugins.

## Installation

```bash
# From local marketplace
/plugin install claude-extension-toolkit@sirtaj-plugins

# Or for development
claude --plugin-dir ./claude-extension-toolkit
```

## Usage

Once installed, just describe what you want. The toolkit activates automatically.

**Creating extensions:**
- "Create a skill that helps with database migrations"
- "Build an agent that reviews PRs"
- "Make a command that runs my deploy script"
- "Add a hook that lints Python files on save"
- "Scaffold a plugin for my team's workflow"

**Debugging:**
- "My skill isn't activating, help me debug it"
- "Why isn't this hook firing?"

**Auditing (spawns autonomous agent):**
- "Audit all my extensions for deprecated patterns"
- "Check my plugins for schema issues"
- "Migrate my hooks to the new format"

**Syncing schemas:**
- `/extension-sync` — fetches latest Claude Code docs and checks your extensions against them

## How It Works

| Component | Type | What it does |
|-----------|------|--------------|
| `extension-toolkit` | Skill | Interactive creation, configuration, and debugging |
| `extension-auditor` | Agent | Autonomous batch audit, validation, and migration |
| `/extension-sync` | Command | Pulls latest schemas, reports what changed |

The skill handles interactive work — it asks questions, scaffolds files, and helps you iterate. When you ask for bulk operations across many extensions, it spawns the auditor agent autonomously.

## Plugin Marketplace

Plugins you create can be distributed via Claude Code's marketplace system. Two layouts:

- **Standalone** — single plugin that's its own marketplace (default, simplest)
- **Umbrella** — parent directory aggregating multiple plugins

The skill handles marketplace wiring during scaffolding. See `references/marketplaces.md` for full details.

---

## For Developers

Everything below is for people working on or extending this toolkit.

### Design

- One skill handles all interactive extension work (create, configure, debug)
- Autonomous bulk work (audit, migrate, validate-all) goes to the agent
- Script-running with no interactivity is a command
- References are shared at the plugin root, not duplicated per-skill
- The skill dispatches to the agent when the user asks for batch operations

### Architecture

```
claude-extension-toolkit/
├── skills/extension-toolkit/    # Interactive skill
│   ├── SKILL.md
│   └── references/
├── agents/extension-auditor.md  # Autonomous agent
├── commands/extension-sync.md   # Sync command
├── references/                  # Shared docs (loaded on demand)
├── scripts/                     # Python validation tools
└── data/                        # Version manifest, source URLs
```

### Reference Documentation

Bundled docs loaded on demand (no context cost until needed):

| File | Contents |
|------|----------|
| `references/frontmatter.md` | All frontmatter fields for skills, agents, commands |
| `references/hooks.md` | Hook events, JSON input schemas, exit codes |
| `references/templates.md` | Ready-to-use templates for each extension type |
| `references/tools.md` | Tool restriction patterns and permission config |
| `references/locations.md` | Where to put files, priority order |
| `references/marketplaces.md` | Marketplace CLI, auth, caching |
| `references/marketplace-schema.md` | Full marketplace.json schema |
| `references/migrations.md` | Before/after patterns for deprecated APIs |
| `references/schema-definitions.md` | Current Claude Code schemas (auto-updated by sync) |
| `references/example-agent.md` | Working agent example |

### Scripts

Python scripts invoked by the skill and agent. Can also be run directly:

| Script | Purpose | Example |
|--------|---------|---------|
| `validate_extension.py` | Structure/schema validation | `--all` or `<path>` |
| `pattern_detector.py` | Deprecated pattern detection | `--all` or `<path>` |
| `token_counter.py` | Token budget checking | `--all --top 10` |
| `lint_references.py` | Broken reference link detection | (no args) |
| `docs_fetcher.py` | Fetch canonical docs, update schemas | `sync` or `update-schemas` |
| `marketplace_manager.py` | Marketplace CRUD and validation | `validate <path>` or `list <path>` |
| `marketplace_register.py` | Three-flow marketplace registration | `<name> --plugin-path <path>` |
| `plugin_scaffolder.py` | Plugin directory scaffolding | `<name> --output ./` |
| `extension_report.py` | Extension inventory report | (no args) |

All Python 3, no external dependencies. Reference via `${CLAUDE_PLUGIN_ROOT}/scripts/` in hooks and skills.

### Development Workflow

```bash
# Test changes to this plugin
claude --plugin-dir ./claude-extension-toolkit

# Reload after edits (no restart needed)
/reload-plugins
```

### Version

- Toolkit: 4.0.0
- Synced against: Claude Code v2.1.141

## License

MIT
