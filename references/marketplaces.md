# Marketplace Reference

Comprehensive reference for Claude Code plugin marketplaces.

Canonical docs: https://code.claude.com/docs/en/plugin-marketplaces

## Marketplace Schema

### Required Fields

```json
{
  "name": "my-marketplace",
  "owner": {
    "name": "Owner Name"
  },
  "plugins": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Marketplace identifier (kebab-case). Public-facing |
| `owner` | object | yes | `{name (required), email?, url?}` |
| `plugins` | array | yes | List of plugin entries |

### Optional Metadata

```json
{
  "metadata": {
    "description": "What this marketplace provides",
    "version": "1.0.0",
    "pluginRoot": "./plugins"
  }
}
```

`metadata.pluginRoot` shortens source paths — with `"pluginRoot": "./plugins"`, a source of `"./my-plugin"` resolves to `./plugins/my-plugin`.

| Field | Type | Description |
|-------|------|-------------|
| `$schema` | string | JSON Schema URL for editor autocomplete; ignored at load |
| `description` | string | Brief marketplace description |
| `version` | string | Marketplace manifest version |
| `metadata` | object | `{description?, version?, pluginRoot?}` |
| `allowCrossMarketplaceDependenciesOn` | array | Other marketplaces this one's plugins may depend on; anything else is blocked at install |
| `renames` | object | Map of former plugin `name` → current name, or `null` if removed. Migrates existing users automatically |

`description` and `version` are accepted at the top level and under `metadata`.

## Plugin Entry Fields

```json
{
  "name": "my-plugin",
  "source": "./my-plugin",
  "description": "What the plugin does",
  "version": "1.0.0",
  "author": { "name": "Author Name", "email": "author@example.com" },
  "category": "development",
  "tags": ["python", "linting"],
  "strict": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Plugin name (unique within marketplace) |
| `source` | string/object | yes | Where to find the plugin (see source types) |
| `displayName` | string | no | Human-readable name for UI; falls back to `name` |
| `description` | string | recommended | What the plugin does |
| `version` | string | no | Semver. Setting it **pins** the plugin |
| `author` | object | no | `{name: string, email?: string, url?: string}` |
| `category` | string | no | Plugin category |
| `tags` | array | no | Search/filter tags |
| `homepage` | string | no | Homepage or docs URL |
| `repository` | string | no | Source repo URL |
| `license` | string | no | SPDX identifier (e.g. `MIT`, `Apache-2.0`) |
| `keywords` | array | no | Discovery tags (synonym of `tags`) |
| `metadata` | object | no | Free-form; Claude Code never reads it |
| `strict` | boolean | no | Strict mode (default: true) |
| `defaultEnabled` | boolean | no | `false` installs disabled. Overrides the same field in `plugin.json` |
| `relevance` | object | no | Suggestion signals; only takes effect for admin-allowlisted marketplaces |

Any field from the plugin manifest schema is accepted here. Plugin entries can
also include component config fields (`skills`, `commands`, `agents`, `hooks`,
`mcpServers`, `lspServers`) to override or supplement `plugin.json`.

## Source Types

Only relative paths are plain strings. Every remote source is an **object**
whose `source` key names the type.

| Type | Shape | Required fields |
|------|-------|-----------------|
| Relative path | `"./my-plugin"` | must start with `./`, no `../` |
| `github` | object | `repo` (`owner/name`); optional `ref`, `sha` |
| `url` | object | `url` (git URL); optional `ref`, `sha` |
| `git-subdir` | object | `url`, `path`; optional `ref`, `sha`. Clones sparsely |
| `npm` | object | `package`; optional `version`, `registry` |
| `archive` | object | `url` (HTTPS zip); optional `sha256`. Needs Claude Code 2.1.224+ |

Relative paths resolve against the marketplace root — the directory containing
`.claude-plugin/`, not `.claude-plugin/` itself.

### GitHub with Branch/Tag

```json
{
  "name": "deploy-tools",
  "source": {
    "source": "github",
    "repo": "org/plugins",
    "ref": "v2.0.0"
  }
}
```

For a subdirectory of a monorepo, use `git-subdir`:

```json
{
  "name": "my-plugin",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/org/monorepo",
    "path": "packages/my-plugin",
    "ref": "main"
  }
}
```

When both `ref` and `sha` are set, `sha` is the effective pin.

**Marketplace source vs plugin source** are different things: the marketplace
source is where `marketplace.json` itself is fetched from (set by
`/plugin marketplace add` or `extraKnownMarketplaces`), while the plugin source
is per-entry inside that file.

## Strict Mode

Controls whether `plugin.json` or the marketplace entry is authoritative for component definitions.

| Mode | Behavior |
|------|----------|
| `true` (default) | Merge: marketplace entry supplements `plugin.json` |
| `false` | Marketplace-only: only components declared in marketplace entry are active |

Strict mode is important for enterprise deployments where admins need to control exactly which plugin components are enabled.

## Settings Integration

### `extraKnownMarketplaces`

Auto-prompt teammates to add marketplace when they open a project:

```json
// .claude/settings.json (project)
{
  "extraKnownMarketplaces": [
    "/path/to/team-marketplace"
  ]
}
```

### `enabledPlugins`

Auto-enable plugins for all project users:

```json
// .claude/settings.json (project)
{
  "enabledPlugins": [
    "my-plugin@my-marketplace"
  ]
}
```

### `strictKnownMarketplaces`

Organization lockdown — only allow plugins from approved marketplaces:

```json
// Enterprise/managed settings
{
  "strictKnownMarketplaces": true
}
```

## CLI Commands

```bash
# Install a plugin from marketplace
claude plugin install my-plugin@marketplace-name
claude plugin install my-plugin@marketplace-name --scope project

# Uninstall
claude plugin uninstall my-plugin

# Enable/disable without removing
claude plugin enable my-plugin
claude plugin disable my-plugin

# Update to latest version
claude plugin update my-plugin

# Validate plugin or marketplace structure
claude plugin validate .
claude plugin validate /path/to/marketplace
```

### Scope Flags

| Flag | Scope | Location |
|------|-------|----------|
| (default) | user | `~/.claude/plugins/` |
| `--scope project` | project | `.claude/plugins/` |
| `--scope local` | local (gitignored) | `.claude/plugins/` |

### Slash Command Equivalents

The `/plugin` slash command mirrors the CLI:
- `/plugin install my-plugin@marketplace`
- `/plugin validate .`
- `/plugin marketplace add /path/to/marketplace`

## Reserved Marketplace Names

The following names are reserved and cannot be used for third-party marketplaces:

- `claude-code-marketplace`
- `claude-code-plugins`
- `claude-plugins-official`
- `claude-plugins-community`
- `claude-community`
- `anthropic-marketplace`
- `anthropic-plugins`
- `agent-skills`
- `anthropic-agent-skills`
- `knowledge-work-plugins`
- `life-sciences`
- `claude-for-legal`
- `claude-for-financial-services`
- `financial-services-plugins`
- `first-party-plugins`
- `healthcare`

Names that impersonate an official marketplace (`official-claude-plugins`,
`anthropic-plugins-v2`, …) are blocked too. Reserved names are re-checked on
**every** marketplace load, not just at `add` time, so a marketplace registered
before a name became reserved stops loading.

## Version Resolution

Claude Code resolves a plugin's version from the first of these that is set:

1. `version` in the plugin's `plugin.json`
2. `version` in the marketplace entry
3. The git commit SHA of the plugin's source
4. For `archive` sources, the `sha256` pin or the downloaded file's digest

Consequences:

- Setting `version` **pins** the plugin. Push new commits without bumping the string and existing users keep the cached copy.
- Setting it in both places is a trap: `plugin.json` wins silently, so a stale manifest version masks the marketplace one.
- For git-based sources you can omit `version` entirely — the simplest setup for internal or actively-developed plugins.

## Plugin Caching

Installed plugins are copied to `~/.claude/plugins/cache/`.

**Important for plugin authors:**
- Relative paths like `../` in hook scripts or references will break after caching
- Use `${CLAUDE_PLUGIN_ROOT}` for all paths within the plugin
- For development, use `claude --plugin-dir ./my-plugin` (bypasses cache)

## Private Repository Auth

For plugins hosted in private repos, set auth tokens:

| Variable | Provider |
|----------|----------|
| `GITHUB_TOKEN` | GitHub |
| `GITLAB_TOKEN` | GitLab |
| `BITBUCKET_TOKEN` | Bitbucket |

## Validation

Prefer built-in validation over custom scripts:

```bash
# Validate plugin structure
claude plugin validate .

# Validate marketplace
claude plugin validate /path/to/marketplace

# Or via slash command
/plugin validate .
```

The `marketplace_manager.py` script provides additional local management (add plugins, list with metadata) beyond what the built-in validation covers.

## File Location

Marketplace manifest: `<marketplace-root>/.claude-plugin/marketplace.json`
