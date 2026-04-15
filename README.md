# Claude Extension Toolkit

A self-maintaining toolkit for creating Claude Code extensions. Provides workflow-based skills for building, configuring, and maintaining skills, agents, plugins, and hooks.

## Installation

```bash
# From local marketplace
/plugin install claude-extension-toolkit@sirtaj-plugins

# Or for development
claude --plugin-dir ./claude-extension-toolkit
```

## Marketplace Support

Plugins built with this toolkit are consumable via Claude Code's local marketplace system. Two layouts are supported:

### Standalone (flat)

One plugin directory that is also its own single-entry marketplace. Fastest path to installable.

```
my-plugin/
└── .claude-plugin/
    ├── plugin.json
    └── marketplace.json   # auto-created by extension-builder
```

Install:
```bash
/plugin marketplace add ./my-plugin
/plugin install my-plugin@my-plugin
```

The toolkit's `extension-builder` scaffolds standalone layouts by default — the generated plugin is installable immediately with no extra wiring.

### Umbrella (aggregating)

One marketplace directory containing N plugin subdirs. Ideal when shipping a related plugin set.

```
my-marketplace/
├── .claude-plugin/marketplace.json   # aggregates plugin-a, plugin-b
├── plugin-a/.claude-plugin/plugin.json
└── plugin-b/.claude-plugin/plugin.json
```

Install:
```bash
/plugin marketplace add ./my-marketplace
/plugin install plugin-a@my-marketplace
```

When you scaffold a new plugin inside an umbrella, `extension-builder` detects the ancestor marketplace.json via upward search and registers the new plugin into it — no inner marketplace.json is created.

### The one-level invariant

`marketplace.json` lives at exactly one level per tree — either the plugin root (standalone) or the umbrella root (umbrella), never both. Promotion (standalone → umbrella) is a separate migration flow, not yet automated; see `.planning/seeds/marketplace-promotion-flow.md`.

### Schema reference

Full schema, source types, reserved names, and pitfalls: [`references/marketplace-schema.md`](references/marketplace-schema.md)
Companion CLI/auth/caching reference: [`references/marketplaces.md`](references/marketplaces.md)

## Skills

### `/extension-starter` - Entry Point

Guides extension type decisions and provides quick-start templates.

**Use when:** Starting customization, deciding what to build, need a quick template.

```
What do you need?
├─ Slash command or expertise? ────► SKILL (also creates /commands)
├─ Autonomous work? ──────────────► AGENT
├─ Coordinated agents? ──────────► AGENT TEAMS
├─ Always-on behavior? ──────────► HOOKS
├─ Project context? ─────────────► CLAUDE.md
└─ Shareable package? ───────────► PLUGIN
```

> **Note:** Commands have been merged into skills. Both `commands/foo.md` and
> `skills/foo/SKILL.md` create `/foo`. Prefer skills for new development.

### `/extension-builder` - Create Extensions

Detailed guidance for creating any extension type with proper structure and frontmatter.

**Use when:** Building skills, agents, or plugins.

- Extension types: skills, agents, agent teams, plugins
- Frontmatter reference and templates
- Progressive disclosure patterns
- Plugin lifecycle and marketplace integration

### `/extension-rules` - Configure Behavior

Configure Claude Code via CLAUDE.md, hooks, and settings.

**Use when:** Adding project rules, creating hooks, configuring permissions.

- CLAUDE.md patterns and best practices
- Hook setup and common patterns
- Settings and permissions configuration

### `/extension-optimizer` - Maintain Extensions

Validate, audit, and upgrade existing extensions.

**Use when:** Auditing extensions, checking for deprecated patterns, optimizing tokens.

- Quick validation with toolkit scripts
- Deprecated pattern detection
- Token efficiency analysis
- Upgrade workflow with before/after examples

### `/extension-sync` - Stay Current

Sync with Claude Code documentation and update schema definitions.

**Use when:** Checking for updates, syncing docs, after Claude Code updates.

- Canonical documentation fetching
- Version manifest management
- Schema definition updates

## Shared References

The toolkit includes shared reference files used by all skills:

| Reference | Purpose |
|-----------|---------|
| `frontmatter.md` | All frontmatter fields for skills, agents, plugins |
| `templates.md` | Ready-to-use templates for all extension types |
| `locations.md` | Storage locations and priority order |
| `tools.md` | Tool restrictions and permission patterns |
| `hooks.md` | Complete hooks reference with JSON input schemas |
| `marketplaces.md` | Marketplace schema, source types, settings, CLI |
| `schema-definitions.md` | Current schemas (auto-updated by sync) |

## Development

```bash
# Load plugin for testing
claude --plugin-dir ./claude-extension-toolkit

# Reload plugins without restarting
/reload-plugins
```

## Scripts

Utility scripts for extension management:

```bash
cd ~/.claude/plugins/claude-extension-toolkit

# Validate extension structure
scripts/validate_extension.py <path>
scripts/validate_extension.py --all

# Detect deprecated patterns
scripts/pattern_detector.py <path>

# Count tokens
scripts/token_counter.py <path> --verbose

# Manage marketplace
scripts/marketplace_manager.py list <marketplace-path>

# Scaffold new plugin
scripts/plugin_scaffolder.py my-plugin --output ./

# Sync documentation
scripts/docs_fetcher.py sync
```

## Architecture

```
claude-extension-toolkit/
├── .claude-plugin/plugin.json      # Plugin manifest
├── skills/
│   ├── extension-starter/          # Decision & quick-start
│   ├── extension-builder/          # Create extensions
│   ├── extension-rules/            # Configure behavior
│   ├── extension-optimizer/        # Maintain & upgrade
│   └── extension-sync/             # Docs & version tracking
├── references/                     # Shared by all skills
│   ├── frontmatter.md
│   ├── templates.md
│   ├── locations.md
│   ├── tools.md
│   ├── hooks.md
│   └── schema-definitions.md
├── data/
│   ├── version-manifest.json       # Schema versions, deprecations
│   └── canonical-sources.json      # Documentation URLs
└── scripts/
    ├── validate_extension.py
    ├── pattern_detector.py
    ├── token_counter.py
    ├── docs_fetcher.py
    ├── marketplace_manager.py
    └── plugin_scaffolder.py
```

## Self-Maintenance

The toolkit maintains itself by:

1. **Schema tracking** - Version manifest tracks current Claude Code schemas
2. **Pattern detection** - Detects deprecated patterns in extensions
3. **Doc syncing** - Fetches canonical documentation on demand
4. **Upgrade guidance** - Provides before/after migration examples

## Version

- Toolkit version: 3.0.0
- Synced against: Claude Code v2.1.77
- Last sync: 2026-03-17

## Credits

Created by Sirtaj Singh Kang using Claude Code.

## License

MIT
