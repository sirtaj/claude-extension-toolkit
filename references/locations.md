# Extension Locations

Storage locations and priority order for all Claude Code extensions.

## Location Priority

Extensions are loaded in priority order (higher overrides lower):

| Priority | Location | Scope |
|----------|----------|-------|
| 1 (highest) | Enterprise config | Organization-wide |
| 2 | `~/.claude/` | Personal (all projects) |
| 3 | `.claude/` (project) | Project-specific |
| 4 | Installed plugins | Via `/plugin install` |
| 5 (lowest) | `--plugin-dir` flag | Development/testing (overrides installed marketplace plugins since 2.1.74) |

## Extension Paths

| Extension | Global | Project | Plugin |
|-----------|--------|---------|--------|
| Skills | `~/.claude/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` | `<plugin>/skills/*/SKILL.md` |
| Agents | `~/.claude/agents/*.md` | `.claude/agents/*.md` | `<plugin>/agents/*.md` |
| Commands | `~/.claude/commands/*.md` | `.claude/commands/*.md` | `<plugin>/commands/*.md` |
| CLAUDE.md | `~/.claude/CLAUDE.md` | `./CLAUDE.md` | — |
| Settings | `~/.claude/settings.json` | `.claude/settings.json` | `<plugin>/.claude/settings.local.json` |
| | | | Plugin settings: `<plugin>/settings.json` (for shipping defaults, currently only `agent` key) |
| | | | Plugin dev settings: `<plugin>/.claude/settings.local.json` |
| Hooks | In settings.json `hooks` key | In settings.json | `<plugin>/hooks/hooks.json` |
| LSP Config | — | — | `<plugin>/.lsp.json` |

## Plugin Installation

Plugins are installed to: `~/.claude/plugins/<plugin-name>/`

After installation:
- Skills from plugin become available globally
- Commands can be invoked with `/command-name`
- Agents available via Agent tool
- Hooks are merged into active hooks

### Installation Scopes

Plugins can be installed at different scopes:

| Scope | Location | Affects |
|-------|----------|---------|
| `user` | `~/.claude/plugins/` | All projects for this user |
| `project` | `.claude/plugins/` | This project only |
| `local` | `.claude/plugins/` (gitignored) | This project, not committed |
| `managed` | Enterprise config | Organization-wide |

## Marketplace Locations

Local marketplaces (directories with plugins):
- Any directory with `.claude-plugin/marketplace.json`
- Register with: `/plugin marketplace add <path>`

## Discovery

Claude discovers extensions at session start:
1. Scans all paths above
2. Loads CLAUDE.md files (project → personal)
3. Registers skills, agents, commands
4. Activates hooks

### Additional Directories

Use `--add-dir` to add extra directories for skill discovery:
```bash
claude --add-dir /path/to/extra/skills
```

### Monorepo Discovery

Skills are discovered in nested directories, supporting monorepo structures where packages have their own `.claude/skills/` directories.

## Development Workflow

During plugin development:
```bash
# Load plugin directly without installing
claude --plugin-dir ./my-plugin

# Changes require restart (no hot reload)
# After restart, skill is available
```

### Hot Reload

During development, use `/reload-plugins` to reload plugin definitions without restarting Claude Code.

## Naming Conflicts

When extensions have the same name:
- Higher priority location wins
- Use plugin prefix to disambiguate: `plugin-name:skill-name`

Example with installed plugin:
```
/my-skill                    # Uses project skill if exists
/my-plugin:my-skill          # Explicitly uses plugin version
```
