# Claude Extension Toolkit

A self-maintaining toolkit for creating Claude Code extensions. Provides workflow-based skills for building, configuring, and maintaining skills, agents, commands, plugins, and hooks.

## Installation

```bash
# From local marketplace
/plugin install claude-extension-toolkit@sirtaj-plugins

# Or for development
claude --plugin-dir ./claude-extension-toolkit
```

## Skills

### `/extension-starter` - Entry Point

Guides extension type decisions and provides quick-start templates.

**Use when:** Starting customization, deciding what to build, need a quick template.

```
What do you need?
├─ Quick reusable prompt?     → COMMAND
├─ Domain expertise?          → SKILL
├─ Autonomous work?           → AGENT
├─ Always-on behavior?        → HOOKS
├─ Project context?           → CLAUDE.md
└─ Shareable package?         → PLUGIN
```

### `/extension-builder` - Create Extensions

Detailed guidance for creating any extension type with proper structure and frontmatter.

**Use when:** Building skills, agents, commands, or plugins.

- Extension spectrum (commands → skills → agents → plugins)
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
| `frontmatter.md` | All frontmatter fields for skills, agents, commands, plugins |
| `templates.md` | Ready-to-use templates for all extension types |
| `locations.md` | Storage locations and priority order |
| `tools.md` | Tool restrictions and permission patterns |
| `hooks.md` | Complete hooks reference with JSON input schemas |
| `schema-definitions.md` | Current schemas (auto-updated by sync) |

## Scripts

Utility scripts for extension management:

```bash
cd ~/.claude/plugins/claude-extension-toolkit

# Validate extension structure
python scripts/validate_extension.py <path>
python scripts/validate_extension.py --all

# Detect deprecated patterns
python scripts/pattern_detector.py <path>

# Count tokens
python scripts/token_counter.py <path> --verbose

# Manage marketplace
python scripts/marketplace_manager.py list <marketplace-path>

# Scaffold new plugin
python scripts/plugin_scaffolder.py my-plugin --output ./

# Sync documentation
python scripts/docs_fetcher.py sync
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

## Credits

Created by Sirtaj Singh Kang using Claude Code.

## License

MIT
