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
| `dependencies` | array | no | Plugins that must be enabled; `"name"`, `"name@marketplace"`, or `{name, marketplace?, version?}` |

Any field from the plugin manifest schema is accepted here. Plugin entries can
also include component config fields (`skills`, `commands`, `agents`, `hooks`,
`mcpServers`, `lspServers`, `outputStyles`) to override or supplement `plugin.json`.

Keep the entry `name` equal to the `name` in the plugin's `plugin.json`. The
entry name is the install id and the `enabledPlugins` key; the manifest name is
the skill prefix. Installing by a differing manifest name fails with
`Plugin "<manifest-name>" not found in marketplace "<marketplace>"`.

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
| `command` | object | A directory produced by running a command on the machine where the plugin is installed |

In `git-subdir`, `url` takes a git URL or an `owner/repo` GitHub shorthand.

Relative paths resolve against the marketplace root — the directory containing
`.claude-plugin/`, not `.claude-plugin/` itself. A path with `..` fails
`claude plugin validate`; a path to a missing directory passes validate and
fails at install with `Source path does not exist: <path>`.

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
| No `plugin.json` (any `strict`) | The entry is the manifest. Entry `hooks` loads only as an inline object |
| `true` (default) | Merge: entry `commands`, `agents`, `skills`, `outputStyles`, `themes` are appended to `plugin.json`'s; entry `hooks` matchers replace the manifest's for the same event |
| `false` | The entry may not add components: if the plugin has a `plugin.json` and the entry declares any of `commands`, `agents`, `skills`, `hooks`, `outputStyles`, `themes`, the plugin fails with `Plugin <name> has conflicting manifests` |

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
  "enabledPlugins": {
    "my-plugin@my-marketplace": true
  }
}
```

The key is the install id: the marketplace entry `name`, `@`, the marketplace `name`.

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
# Register / remove a marketplace (remove also uninstalls its plugins)
claude plugin marketplace add ./my-marketplace      # or <owner>/<repo>, or a git URL
claude plugin marketplace remove my-marketplace

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

# Inspect installed plugins
claude plugin list
claude plugin details my-plugin      # takes the plugin.json name

# Tag a release for dependency version constraints (<name>--v<version>)
claude plugin tag --push             # --dry-run to preview

# Remove auto-installed dependencies no plugin needs anymore
claude plugin prune
```

### Scope Flags

The scope decides who the plugin is enabled for; it's recorded in settings.
Fetched plugin files always live under `~/.claude/plugins/`.

| Flag | Scope | Enabled for |
|------|-------|-------------|
| (default) | user | You, in every project on this computer |
| `--scope project` | project | Everyone in the repo, via the committed `.claude/settings.json` (each collaborator still installs it) |
| `--scope local` | local | You, in this repository only |

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
`anthropic-plugins-v2`, `claude-official`, …) are blocked too, and
`claude plugin validate` reports them. The exact reserved names pass validate;
`marketplace add` refuses them with `The name '<name>' is reserved for official
Anthropic marketplaces`. Official and community names are accepted only for
marketplaces sourced from `github.com/anthropics/` repositories. Reserved names are re-checked on
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
- `version` isn't checked against semver, and it doesn't pin a plugin with a `command` source, one from a claude.ai-hosted marketplace, or one loaded in place from a marketplace added as a local directory.
- A dependency resolved from a git tag shows its version with a 12-character commit suffix in `claude plugin list` (e.g. `2.1.0-8713c5b11005`).

### Dependency Version Constraints

A `dependencies` item with a `version` range (`~2.1.0`, `^2.0`, `>=1.4`) installs at the
highest git tag named `<plugin-name>--v<version>` that satisfies it. Tag the plugin's own
repo for `github`/`url`/`git-subdir` sources, or the marketplace repo for relative-path
sources. For `npm`, `archive`, and `command` sources, the range is only checked at load
against the dependency's `plugin.json` `version`. When several plugins constrain one
dependency, it resolves to the highest version satisfying all ranges; non-overlapping
ranges fail with `has conflicting version requirements`.

Cross-marketplace dependencies need the target marketplace listed in the root
marketplace's `allowCrossMarketplaceDependenciesOn` (unless the user already has the
dependency enabled at the same scope).

## Plugin Caching

Installed plugins are copied to `~/.claude/plugins/cache/`.

**Important for plugin authors:**
- Relative paths like `../` in hook scripts or references will break after caching
- Use `${CLAUDE_PLUGIN_ROOT}` for all paths within the plugin
- For development, use `claude --plugin-dir ./my-plugin` (bypasses cache)
- A marketplace added from a local directory with relative-path sources is read in
  place, not cached: edits apply at the next session start or on `/reload-plugins`,
  with no `version` bump

## Private Repository Auth

For plugins hosted in private repos, set auth tokens:

| Variable | Provider |
|----------|----------|
| `GITHUB_TOKEN` | GitHub |
| `GITLAB_TOKEN` | GitLab |
| `BITBUCKET_TOKEN` | Bitbucket |

## Validation

Prefer built-in validation over custom scripts. `claude plugin validate` reads only
files inside the marketplace directory and reports JSON syntax errors, missing
required fields, bad marketplace names, `..` in relative sources, unknown fields
(as warnings), and each relative-path plugin's `plugin.json` problems
(`plugins[N] plugin.json → <field>: <message>`). Wrong remote `repo`/`path` values,
missing source directories, and exact reserved names only surface at add/install.

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
