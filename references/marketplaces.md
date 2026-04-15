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
| `name` | string | yes | Marketplace identifier |
| `owner` | object | yes | Must contain `owner.name` |
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
| `description` | string | recommended | What the plugin does |
| `version` | string | recommended | Semver version |
| `author` | object | no | `{name: string, email?: string}` |
| `category` | string | no | Plugin category |
| `tags` | array | no | Search/filter tags |
| `homepage` | string | no | Homepage or docs URL |
| `repository` | string | no | Source repo URL |
| `license` | string | no | SPDX identifier (e.g. `MIT`, `Apache-2.0`) |
| `keywords` | array | no | Discovery tags (synonym of `tags`) |
| `strict` | boolean | no | Strict mode (default: true) |

Additionally, plugin entries can include component config fields (`commands`, `agents`, `skills`, `hooks`, `mcpServers`, `outputStyles`, `lspServers`) to override or supplement what's in `plugin.json`.

## Source Types

| Type | Format | Example |
|------|--------|---------|
| Relative path | `"./path"` | `"./claude-python-plugin"` |
| GitHub | `"github:owner/repo"` | `"github:anthropics/claude-code-plugins"` |
| GitHub subdir | `"github:owner/repo/path"` | `"github:org/monorepo/plugins/my-plugin"` |
| URL | `"https://..."` | `"https://example.com/plugin.tar.gz"` |
| npm | `"npm:package-name"` | `"npm:@scope/claude-plugin"` |

### GitHub with Branch/Tag

```json
{
  "source": {
    "type": "github",
    "owner": "org",
    "repo": "plugins",
    "ref": "v2.0.0",
    "path": "packages/my-plugin"
  }
}
```

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
- `anthropic-marketplace`
- `anthropic-plugins`
- `agent-skills`
- `knowledge-work-plugins`
- `life-sciences`

## Version Resolution

When both `plugin.json` and the marketplace entry specify a version:
- **`plugin.json` version wins** silently
- Set the version in one place only to avoid confusion
- Marketplace version is used for display/discovery when plugin isn't installed locally

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
