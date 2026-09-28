# Marketplace Schema Reference

Canonical JSON shape for `.claude-plugin/marketplace.json` and the two supported layout patterns.

Canonical docs: https://code.claude.com/docs/en/plugin-marketplaces
Companion: `references/marketplaces.md` (CLI, auth, caching, settings integration)

Verified against Claude Code 2.1.283 docs (2026-09-28).

## Two Layouts

`marketplace.json` lives at **exactly one level** per tree — never both at the plugin root and an ancestor umbrella root simultaneously.

### Standalone (flat)

A plugin that is also its own single-entry marketplace. Directly installable.

```
my-plugin/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json   # single entry points at "./"
├── skills/
└── README.md
```

Install:
```bash
/plugin marketplace add ./my-plugin
/plugin install my-plugin@my-plugin
```

Use when: shipping one plugin, no aggregation needed, fastest path to installable.

### Umbrella (aggregating)

A directory containing N plugin subdirs, aggregated by a single marketplace.json at the umbrella root.

```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json   # aggregates plugin-a, plugin-b, ...
├── plugin-a/
│   └── .claude-plugin/plugin.json
└── plugin-b/
    └── .claude-plugin/plugin.json
```

Install:
```bash
/plugin marketplace add ./my-marketplace
/plugin install plugin-a@my-marketplace
/plugin install plugin-b@my-marketplace
```

Use when: shipping multiple related plugins, shared owner/metadata, discovery-friendly.

### The invariant

A plugin directory under an umbrella MUST NOT have its own `.claude-plugin/marketplace.json`. Promotion (standalone → umbrella) is a separate flow: move the plugin under the umbrella and delete its inner marketplace.json.

## Top-Level Schema

Required and optional top-level fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Marketplace identifier (kebab-case). Visible in `/plugin install X@<name>`. Must not collide with reserved names (see below). |
| `owner` | object | yes | `{name: string (required), email?: string, url?: string}` |
| `plugins` | array | yes | List of plugin entry objects |
| `metadata` | object | no | `{description?, version?, pluginRoot?}` |
| `$schema` | string | no | JSON Schema URL for editor autocomplete; ignored at load |
| `description` | string | no | Also accepted under `metadata` |
| `version` | string | no | Also accepted under `metadata` |
| `allowCrossMarketplaceDependenciesOn` | array | no | Marketplaces this one's plugins may depend on; others are blocked at install |
| `renames` | object | no | Former plugin `name` → current name, or `null` if removed |

`metadata.pluginRoot` is prepended to relative plugin `source` paths. With `pluginRoot: "./plugins"`, a plugin with `source: "formatter"` resolves to `./plugins/formatter`.

## Plugin Entry Schema

Required:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Plugin identifier (kebab-case) |
| `source` | string or object | See Source Types below |

Optional:

| Field | Type | Description |
|-------|------|-------------|
| `displayName` | string | Human-readable name for UI; falls back to `name` |
| `description` | string | Brief plugin description |
| `version` | string | Semver; **`plugin.json` version silently wins if both set** |
| `author` | object | `{name: string, email?: string, url?: string}` (object, not string) |
| `homepage` | string | Homepage or docs URL |
| `repository` | string | Source code URL |
| `license` | string | SPDX identifier (e.g. `MIT`, `Apache-2.0`) |
| `keywords` | array | Discovery tags (synonym of `tags`) |
| `metadata` | object | Free-form; Claude Code never reads it |
| `category` | string | Plugin category |
| `tags` | array | Searchability tags |
| `strict` | boolean | Default `true`; see Strict Mode |
| `defaultEnabled` | boolean | `false` installs disabled; overrides `plugin.json` |
| `relevance` | object | Suggestion signals; only for admin-allowlisted marketplaces |
| `dependencies` | array | Same shape as in `plugin.json`; see Dependencies |
| `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles` | string or object | Override/supplement plugin.json component definitions (see Strict Mode) |

An entry accepts **every** `plugin.json` field alongside its own fields. The entry's `defaultEnabled` and display fields such as `displayName` override `plugin.json`; `plugin.json`'s `version` overrides the entry's.

Deprecated:

| Field | Replacement | Severity |
|-------|-------------|----------|
| `path` | `source` | warning |

### Entry name vs manifest name

The entry `name` is the install id (`<entry-name>@<marketplace>`), what `claude plugin list` shows, and the `enabledPlugins` key. The `plugin.json` `name` is the prefix on the plugin's skills and the name `claude plugin details` takes. If they differ and someone installs by the manifest name: `Plugin "<manifest-name>" not found in marketplace "<marketplace>"`. Keep them the same.

## Source Types

| Type | Value shape | Required fields |
|------|-------------|-----------------|
| Relative path | string `"./name"` | must start with `./`, no `../` |
| GitHub | object `{source: "github", repo, ref?, sha?}` | `repo` (e.g. `owner/name`) |
| URL | object `{source: "url", url, ref?, sha?}` | `url` (https://, git@, Azure DevOps, CodeCommit) |
| Git subdir | object `{source: "git-subdir", url, path, ref?, sha?}` | `url`, `path` |
| npm | object `{source: "npm", package, version?, registry?}` | `package` |
| Archive | object `{source: "archive", url, sha256?}` | `url` (HTTPS zip; Claude Code 2.1.224+) |
| Command | object `{source: "command", …}` | A directory produced by running a command on the installing machine (see the official marketplace reference for fields) |

In `git-subdir`, `url` takes a git URL or an `owner/repo` GitHub shorthand.

Relative paths resolve against the marketplace root (the directory containing `.claude-plugin/`). `..` is disallowed: `claude plugin validate` reports `Path contains "..": <path>`. A path to a missing directory **passes** validate and fails at install with `Source path does not exist: <path>`.

When both `ref` and `sha` are set on a git-based source, `sha` is the effective pin.

## Dependencies

`dependencies` (in `plugin.json` or an entry) lists plugins that must be enabled for this one to work. Each item is `"name"`, `"name@marketplace"`, or `{name, marketplace?, version?}`. Bare names resolve in the declaring plugin's own marketplace.

- `version` is a semver range (`~2.1.0`, `^2.0`, `>=1.4`, `=2.1.0`). Pre-releases match only with an opt-in suffix such as `^2.0.0-0`.
- Ranges resolve against git tags named `<plugin-name>--v<version>` (create them with `claude plugin tag --push`). Tag the plugin's own repo for `github`/`url`/`git-subdir` sources, the marketplace repo for relative-path sources.
- For `npm`, `archive`, and `command` sources the range doesn't pick what is fetched; the dependency's `plugin.json` `version` is checked at load (no version → satisfies no constraint). Claude Code never installs a `command`-source dependency itself.
- Cross-marketplace dependencies install only if the **root** marketplace (the one hosting the plugin being installed) lists the target in `allowCrossMarketplaceDependenciesOn`, or the user already has the dependency enabled at the same scope.

## Reserved Marketplace Names

Do NOT use these names (reserved for official Anthropic marketplaces):

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

Impersonating names (`official-claude-plugins`, `anthropic-plugins-v2`,
`claude-official`, …) are blocked too, and `claude plugin validate` reports them
(along with names containing spaces or non-ASCII characters). The exact reserved
names **pass** validate; `marketplace add` refuses them with `The name '<name>' is
reserved for official Anthropic marketplaces`. Official and community names are
accepted only for marketplaces sourced from `github.com/anthropics/`
repositories. The check runs on every marketplace load, not only at `add` time.

## Strict Mode

`strict` decides whether the entry may add components to a plugin that has its own `plugin.json`.

| Case | Behavior |
|------|----------|
| No `plugin.json` | Entry **is** the manifest, regardless of `strict`. Entry `hooks` loads only as an inline object (file path/array → `not yet supported in a marketplace entry`) |
| `plugin.json` + `strict: true` (default) | Manifest loads; entry `commands`, `agents`, `skills`, `outputStyles`, `themes` are appended. Entry `hooks` matchers replace the manifest's matchers for the same event |
| `plugin.json` + `strict: false` | Entry declaring any of `commands`, `agents`, `skills`, `hooks`, `outputStyles`, `themes` → `Plugin <name> has conflicting manifests`, plugin fails to load |

When an entry whose `source` is the marketplace root lists specific `skills` subdirectories, only those load and the default `skills/` isn't scanned.

Use the default unless you specifically need marketplace-only component definitions.

## Minimal Valid marketplace.json

```json
{
  "name": "my-marketplace",
  "owner": { "name": "Your Name" },
  "plugins": [
    { "name": "my-plugin", "source": "./my-plugin" }
  ]
}
```

## Full Example

```json
{
  "name": "company-tools",
  "owner": { "name": "DevTools Team", "email": "devtools@example.com" },
  "metadata": {
    "description": "Company internal plugins",
    "version": "1.0.0",
    "pluginRoot": "./plugins"
  },
  "plugins": [
    {
      "name": "formatter",
      "source": "formatter",
      "description": "Code formatting on save",
      "version": "2.1.0",
      "author": { "name": "DevTools Team" },
      "homepage": "https://example.com/formatter",
      "license": "MIT",
      "keywords": ["formatting", "style"]
    },
    {
      "name": "deploy-tools",
      "source": {
        "source": "github",
        "repo": "company/deploy-plugin",
        "ref": "v1.0.0"
      }
    }
  ]
}
```

## Common Pitfalls

- `../` in relative source paths → rejected at validation time. Plugins must be inside the marketplace root.
- Setting `version` in both `plugin.json` and the marketplace entry → `plugin.json` wins silently.
- Using an exact reserved marketplace name → passes `claude plugin validate`, then fails at `marketplace add`. Check the list above before naming.
- Entry `name` differs from `plugin.json` `name` → installing by the manifest name fails with `not found in marketplace`.
- Relative `source` pointing at a missing directory → passes validate, fails at install (`Source path does not exist`).
- URL-distributed marketplace + relative source paths → fails at install (URL distribution only fetches the JSON, not plugin dirs). Use URL distribution only with remote `source` types.
- `strict: false` + entry declares components while the plugin has a `plugin.json` → `has conflicting manifests` load failure. Leave `strict` at default.

## Where This Schema Is Enforced

| Facet | Enforced by |
|-------|-------------|
| JSON syntax, required fields, `..` in relative sources, impersonating/non-ASCII names, unknown fields (warnings), each relative-path plugin's `plugin.json` | `claude plugin validate` (built-in) |
| Reserved names, path-exists, author object shape, metadata wrapper shape | `scripts/marketplace_manager.py validate` |
| Schema drift vs toolkit version | `data/version-manifest.json` `schemas.marketplace_manifest` / `marketplace_plugin_entry` |

See `references/marketplaces.md` for CLI commands, auth tokens, caching, and settings integration.
