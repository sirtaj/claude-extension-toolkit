# Marketplace Schema Reference

Canonical JSON shape for `.claude-plugin/marketplace.json` and the two supported layout patterns.

Canonical docs: https://code.claude.com/docs/en/plugin-marketplaces
Companion: `references/marketplaces.md` (CLI, auth, caching, settings integration)

Verified against Claude Code 2.1.226 docs (2026-08-09).

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
| `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers` | string or object | Override/supplement plugin.json component definitions |

Deprecated:

| Field | Replacement | Severity |
|-------|-------------|----------|
| `path` | `source` | warning |

## Source Types

| Type | Value shape | Required fields |
|------|-------------|-----------------|
| Relative path | string `"./name"` | must start with `./`, no `../` |
| GitHub | object `{source: "github", repo, ref?, sha?}` | `repo` (e.g. `owner/name`) |
| URL | object `{source: "url", url, ref?, sha?}` | `url` (https://, git@, Azure DevOps, CodeCommit) |
| Git subdir | object `{source: "git-subdir", url, path, ref?, sha?}` | `url`, `path` |
| npm | object `{source: "npm", package, version?, registry?}` | `package` |
| Archive | object `{source: "archive", url, sha256?}` | `url` (HTTPS zip; Claude Code 2.1.224+) |

Relative paths resolve against the marketplace root (the directory containing `.claude-plugin/`). `../` is disallowed.

When both `ref` and `sha` are set on a git-based source, `sha` is the effective pin.

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

Impersonating names (`official-claude-plugins`, `anthropic-plugins-v2`, …) are
blocked too. The check runs on every marketplace load, not only at `add` time.

## Strict Mode

| Value | Behavior |
|-------|----------|
| `true` (default) | `plugin.json` is authority; marketplace entry supplements |
| `false` | Marketplace entry is the entire definition; plugin MUST NOT also declare components in `plugin.json` (conflict → load failure) |

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
- Using a reserved marketplace name → fails at `/plugin marketplace add` time with no prior warning. Check the list above before naming.
- URL-distributed marketplace + relative source paths → fails at install (URL distribution only fetches the JSON, not plugin dirs). Use URL distribution only with remote `source` types.
- `strict: false` + plugin has a component-declaring `plugin.json` → load failure. Leave `strict` at default.

## Where This Schema Is Enforced

| Facet | Enforced by |
|-------|-------------|
| JSON syntax, required fields | `claude plugin validate` (built-in) |
| Reserved names, path-exists, author object shape, metadata wrapper shape | `scripts/marketplace_manager.py validate` |
| Schema drift vs toolkit version | `data/version-manifest.json` `schemas.marketplace_manifest` / `marketplace_plugin_entry` |

See `references/marketplaces.md` for CLI commands, auth tokens, caching, and settings integration.
