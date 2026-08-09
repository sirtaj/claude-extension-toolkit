# Extension Locations

Storage locations and priority order for all Claude Code extensions.

Verified against Claude Code 2.1.226 docs (2026-08-09).

## Location Priority

Extensions are loaded in priority order (higher overrides lower):

| Priority | Location | Scope |
|----------|----------|-------|
| 1 (highest) | Enterprise / managed config | Organization-wide |
| 2 | `~/.claude/` | Personal (all projects) |
| 3 | `.claude/` (project) | Project-specific |
| 4 | Installed plugins | Via `/plugin install` |
| 5 (lowest) | `--plugin-dir` flag | Development/testing (overrides installed marketplace plugins since 2.1.74) |

Plugin skills live in a `plugin-name:skill-name` namespace, so they never
collide with the other levels. A skill at any level also overrides a bundled
Claude Code skill of the same name.

## Extension Paths

| Extension | Global | Project | Plugin |
|-----------|--------|---------|--------|
| Skills | `~/.claude/skills/*/SKILL.md` | `.claude/skills/*/SKILL.md` | `<plugin>/skills/*/SKILL.md` |
| Agents | `~/.claude/agents/*.md` | `.claude/agents/*.md` | `<plugin>/agents/*.md` |
| Commands | `~/.claude/commands/*.md` | `.claude/commands/*.md` | `<plugin>/commands/*.md` |
| Workflows | — | — | `<plugin>/workflows/` |
| Output styles | — | — | `<plugin>/output-styles/` |
| Themes | — | — | `<plugin>/themes/` |
| Monitors | — | — | `<plugin>/monitors/monitors.json` |
| Executables | — | — | `<plugin>/bin/` (added to the Bash tool's `PATH`) |
| CLAUDE.md | `~/.claude/CLAUDE.md` | `./CLAUDE.md` | — (a plugin-root CLAUDE.md is **not** loaded) |
| Settings | `~/.claude/settings.json` | `.claude/settings.json` | `<plugin>/settings.json` (ships defaults; only the `agent` and `subagentStatusLine` keys) |
| | | | Plugin dev settings: `<plugin>/.claude/settings.local.json` |
| Hooks | In settings.json `hooks` key | In settings.json | `<plugin>/hooks/hooks.json` |
| MCP servers | — | `.mcp.json` | `<plugin>/.mcp.json` |
| LSP Config | — | — | `<plugin>/.lsp.json` |

Everything except `plugin.json` lives at the **plugin root**, not inside
`.claude-plugin/`.

## Skills-Directory Plugins

Any folder under a skills directory that contains `.claude-plugin/plugin.json`
loads as a plugin named `<name>@skills-dir` — no marketplace, no install step.
It can bundle its own skills, agents, hooks, and MCP servers.

| Skills directory | Scope | Loads |
|------------------|-------|-------|
| `~/.claude/skills/` | personal | In every project |
| `<cwd>/.claude/skills/` | project | Only after the workspace trust dialog |

Project-scope `@skills-dir` plugins load only from the `.claude/skills/` of the
directory where you start Claude Code — they don't walk up to the repo root, and
their background monitors don't load. Disable one with
`claude plugin disable my-tool@skills-dir`.

## Plugin Installation

Plugins are installed to: `~/.claude/plugins/<plugin-name>/`

After installation:
- Skills from plugin become available globally
- Commands can be invoked with `/command-name`
- Agents available via Agent tool
- Hooks are merged into active hooks

### Installation Scopes

Plugins can be installed at different scopes:

The scope is recorded in a settings file, the same way other Claude Code config
is scoped:

| Scope | Settings file | Affects |
|-------|---------------|---------|
| `user` | `~/.claude/settings.json` | All projects for this user (default) |
| `project` | `.claude/settings.json` | Shared via version control |
| `local` | `.claude/settings.local.json` | This project, not committed |
| `managed` | Managed settings | Organization-wide (read-only) |

## Marketplace Locations

Local marketplaces (directories with plugins):
- Any directory with `.claude-plugin/marketplace.json`
- Register with: `/plugin marketplace add <path>`

See `references/marketplaces.md` for full marketplace docs (source types, settings, CLI commands).

## Plugin Caching

Installed plugins are cached to `~/.claude/plugins/cache/`. This means:
- Relative paths (`../`) in hooks or references break after installation
- Always use `${CLAUDE_PLUGIN_ROOT}` for paths within the plugin
- Use `claude --plugin-dir ./my-plugin` during development (bypasses cache)

## Discovery

Claude discovers extensions at session start:
1. Scans all paths above
2. Loads CLAUDE.md files (project → personal)
3. Registers skills, agents, commands
4. Activates hooks

Project skills also load from `.claude/skills/` in every parent directory up to
the repository root, so starting Claude in a subdirectory still picks up
repo-root skills.

### Additional Directories

Use `--add-dir` to add extra directories for skill discovery:
```bash
claude --add-dir /path/to/extra/skills
```

Skills are the **exception**: `--add-dir` and `/add-dir` otherwise grant file
access only. Commands, output styles, and other `.claude/` config are not loaded
from added directories, and the `permissions.additionalDirectories` setting
doesn't load skills at all.

### Monorepo Discovery

Nested `.claude/skills/` directories below the starting directory aren't loaded
at startup. They load the first time Claude reads or edits a file in that
subdirectory and stay available for the session. Until then they don't
autocomplete and can't be invoked.

When a nested skill's name clashes with another, it appears under a
directory-qualified name (`apps/web:deploy`) and `/deploy` runs the project-root
one.

## Development Workflow

```bash
# Load plugin directly without installing
claude --plugin-dir ./my-plugin
```

### Live Change Detection

Claude Code watches skill and agent directories and picks up edits **within the
session, no restart needed**:

- `SKILL.md` text under `~/.claude/skills/`, project `.claude/skills/`, or an `--add-dir` directory
- Agent files under `~/.claude/agents/` and `.claude/agents/`

Two cases still need a restart: creating a scope's *first* file in a directory
that didn't exist at session start, and sessions run with
`--disable-slash-commands`.

Everything else in a plugin — `hooks/`, `.mcp.json`, `agents/`,
`output-styles/` — needs `/reload-plugins`.

## Naming Conflicts

When extensions have the same name:
- Higher priority location wins
- Use plugin prefix to disambiguate: `plugin-name:skill-name`

Example with installed plugin:
```
/my-skill                    # Uses project skill if exists
/my-plugin:my-skill          # Explicitly uses plugin version
```
