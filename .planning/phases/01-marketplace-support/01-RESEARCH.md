# Phase 1: Marketplace Support - Research

**Researched:** 2026-04-16
**Domain:** Claude Code plugin marketplace schema, scaffolding, validation
**Confidence:** HIGH (primary schema verified against official docs; all code examples from live codebase)

---

## Summary

The canonical `marketplace.json` schema is fully documented at `https://code.claude.com/docs/en/plugin-marketplaces` and is already partially represented in the toolkit's `data/version-manifest.json` and `references/marketplaces.md`. However, several discrepancies exist between the current toolkit data and the official schema that must be corrected before implementation.

The toolkit already has working scaffolding infrastructure (`scripts/plugin_scaffolder.py`, `scripts/marketplace_manager.py`) and a shared reference file (`references/marketplaces.md`). The phase is primarily an **extension and correction** job, not greenfield. The key blocker (Q1: canonical schema) is now resolved.

The three-flow scaffolder design (standalone, new umbrella, register-into-existing) maps cleanly onto the existing `plugin_scaffolder.py` and `marketplace_manager.py` scripts. A new `scripts/marketplace_register.py` is needed only for the safe jq-append case; the detection logic (upward-search) is new Python stdlib code.

**Primary recommendation:** Correct the version-manifest schema first (delta list below), then extend the scaffolder and validator against the corrected schema.

---

## Canonical marketplace.json Schema

This section is the phase's primary unknown. All content below is **[VERIFIED: https://code.claude.com/docs/en/plugin-marketplaces]**.

### marketplace.json — Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | YES | Marketplace identifier (kebab-case, no spaces). Public-facing — users see it in `/plugin install X@<name>`. |
| `owner` | object | YES | Maintainer info. Must contain `owner.name` (string, required) and optionally `owner.email` (string). |
| `plugins` | array | YES | List of plugin entry objects. |
| `metadata` | object | NO | Optional metadata block. |
| `metadata.description` | string | NO | Human description of the marketplace. |
| `metadata.version` | string | NO | Marketplace version. |
| `metadata.pluginRoot` | string | NO | Base directory prepended to relative plugin `source` paths (e.g., `"./plugins"` lets you write `"source": "formatter"` instead of `"source": "./plugins/formatter"`). |

**Live example (this project's `.claude-plugin/marketplace.json`):**

```json
{
  "name": "sirtaj-plugins",
  "owner": { "name": "Sirtaj" },
  "metadata": { "description": "Sirtaj's personal Claude Code plugins" },
  "plugins": [...]
}
```

### Plugin Entry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | YES | Plugin identifier (kebab-case). |
| `source` | string or object | YES | Where to fetch the plugin. Replaces deprecated `path` field. |
| `description` | string | NO | Brief plugin description. |
| `version` | string | NO | Plugin version. When both `plugin.json` and marketplace entry set version, **`plugin.json` wins silently**. |
| `author` | object | NO | `{name: string, email?: string}`. Note: official schema says object; current toolkit `references/marketplaces.md` incorrectly shows it as a string. |
| `homepage` | string | NO | Plugin homepage or docs URL. |
| `repository` | string | NO | Source code repository URL. |
| `license` | string | NO | SPDX identifier (e.g., `MIT`, `Apache-2.0`). |
| `keywords` | array | NO | Tags for discovery. (Synonym of `tags`.) |
| `category` | string | NO | Plugin category string. |
| `tags` | array | NO | Searchability tags. |
| `strict` | boolean | NO | Default `true`. Controls whether `plugin.json` is authority for component definitions. See below. |
| `skills` | string or array | NO | Custom paths to skill directories. Overrides discovery from plugin root. |
| `commands` | string or array | NO | Custom paths to command files or directories. |
| `agents` | string or array | NO | Custom paths to agent files. |
| `hooks` | string or object | NO | Custom hooks config or path to hooks file. |
| `mcpServers` | string or object | NO | MCP server configs or path to MCP config. |
| `lspServers` | string or object | NO | LSP server configs or path to LSP config. |
| `outputStyles` | (inherited) | NO | From plugin manifest schema. |

**Deprecated field:**
- `path`: legacy name for `source`. Still accepted but emit a warning. Validator should flag `path` without `source` as a warning, not error. [VERIFIED: current `marketplace_manager.py` already handles this via `_get_plugin_source()`.]

### Source Types

| Type | Value format | Object fields |
|------|-------------|---------------|
| Relative path | `"./my-plugin"` (string) | none — must start with `./`, no `../` |
| GitHub | object `{source:"github", repo:"owner/repo", ref?, sha?}` | `repo` required; `ref` = branch/tag; `sha` = full 40-char commit SHA |
| Git URL | object `{source:"url", url:"https://...", ref?, sha?}` | `url` required; accepts `https://`, `git@`, Azure DevOps, AWS CodeCommit |
| Git subdirectory | object `{source:"git-subdir", url:"...", path:"subdir/path", ref?, sha?}` | `url` + `path` required; sparse-clone for monorepos |
| npm | object `{source:"npm", package:"@scope/name", version?, registry?}` | `package` required |

**CRITICAL DISCREPANCY:** The current `version-manifest.json` lists `"pip"` as a source type. **The official docs (as of 2026-04-16) do NOT document a `pip` source type.** The documented types are: relative_path, github, url, git-subdir, npm. The `pip` entry in `version-manifest.json` must be removed or flagged as unverified.
[VERIFIED: official docs — no pip source in source types table]

**Key rule for relative paths:** Paths resolve relative to the **marketplace root** (the directory containing `.claude-plugin/`), not relative to `.claude-plugin/` itself. `../` is disallowed. Relative paths only work for Git-added marketplaces, not URL-direct marketplaces.

### Strict Mode

| Value | Behavior |
|-------|----------|
| `true` (default) | `plugin.json` is authority; marketplace entry supplements/merges. |
| `false` | Marketplace entry is the entire definition. Plugin MUST NOT also have a `plugin.json` with component declarations (conflict = load failure). |

### Reserved Marketplace Names

**DISCREPANCY:** The current `version-manifest.json` lists reserved names as `["anthropic","claude","official","claude-code","anthropic-plugins"]`. The official docs list a different set: `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`. The manifest must be updated.
[VERIFIED: official docs reserved names list]

---

## Schema Discrepancies: version-manifest.json vs Official Docs

These must be corrected before implementing validators and scaffolders.

| Field/Key | Current value | Correct value | Action |
|-----------|---------------|---------------|--------|
| `schemas.marketplace_plugin_entry.source_types` | `["relative_path","github","url","git_subdir","npm","pip"]` | Remove `"pip"`; rename `"git_subdir"` to `"git-subdir"` (matches `source` object's `source` field value) | Edit `version-manifest.json` |
| `schemas.marketplace_manifest.reserved_names` | `["anthropic","claude","official","claude-code","anthropic-plugins"]` | Replace with official list: `["claude-code-marketplace","claude-code-plugins","claude-plugins-official","anthropic-marketplace","anthropic-plugins","agent-skills","knowledge-work-plugins","life-sciences"]` | Edit `version-manifest.json` |
| `schemas.marketplace_manifest.optional_metadata` | Flat list `["description","version","pluginRoot"]` | Nested under `metadata` object key, not top-level fields. Structure in JSON: `{"metadata": {description, version, pluginRoot}}` | Update version-manifest to model the `metadata` object correctly; update `references/marketplaces.md` to show `metadata.pluginRoot` |
| `schemas.marketplace_plugin_entry.optional[author]` | (implied string) | Object `{name: string, email?: string}`. Current `references/marketplaces.md` shows author as string. | Fix references/marketplaces.md; add type note to version-manifest |
| Plugin entry `homepage`, `repository`, `license`, `keywords` fields | Missing from `optional` list in version-manifest | Add these four fields to `marketplace_plugin_entry.optional` | Edit `version-manifest.json` |

---

## Architecture Patterns

### System Architecture Diagram

```
User trigger ("add to marketplace", "create plugin", "validate marketplace")
         |
         v
extension-builder SKILL.md  ---reads---> references/marketplaces.md
         |                                        |
         | instructs Claude to run                | documents schema
         v                                        v
scripts/marketplace_register.py    data/version-manifest.json
  (upward search + safe jq-append)      (schemas.marketplace_manifest
         |                               schemas.marketplace_plugin_entry)
         |
         +---> existing marketplace.json  [register-into-existing flow]
         |
         +---> new .claude-plugin/marketplace.json  [standalone or umbrella flow]
                         |
                         v
         scripts/marketplace_manager.py validate <path>
                         |
                         v
         extension-optimizer SKILL.md (audit includes marketplace check)
```

### Data Layer: version-manifest.json Extension

Add under `schemas`:
```json
"marketplace_manifest": {
  "required": ["name", "owner", "plugins"],
  "owner_fields": {
    "required": ["name"],
    "optional": ["email"]
  },
  "metadata_fields": ["description", "version", "pluginRoot"],
  "reserved_names": [... official list ...]
},
"marketplace_plugin_entry": {
  "required": ["name", "source"],
  "optional": ["description","version","author","homepage","repository",
               "license","keywords","category","tags","strict",
               "commands","agents","skills","hooks","mcpServers","outputStyles","lspServers"],
  "source_types": {
    "relative_path": {"format": "string starting with ./", "disallowed": ["../"]},
    "github": {"fields": {"repo": "required", "ref": "optional", "sha": "optional"}},
    "url": {"fields": {"url": "required", "ref": "optional", "sha": "optional"}},
    "git-subdir": {"fields": {"url": "required", "path": "required", "ref": "optional", "sha": "optional"}},
    "npm": {"fields": {"package": "required", "version": "optional", "registry": "optional"}}
  },
  "deprecated_fields": {
    "path": {"replacement": "source", "severity": "warning"}
  }
}
```

### Three Scaffolder Flows

**Detection (upward search):**
```python
# In scripts/marketplace_register.py
def find_ancestor_marketplace(start: Path) -> Path | None:
    """Walk up from start toward filesystem root, return first
    directory containing .claude-plugin/marketplace.json."""
    current = start.resolve()
    while True:
        candidate = current / ".claude-plugin" / "marketplace.json"
        if candidate.exists():
            return current
        parent = current.parent
        if parent == current:
            return None  # reached filesystem root
        current = parent
```

**Flow selection table:**
| Detection result | User choice | Flow |
|---|---|---|
| Ancestor marketplace found | n/a | Register into existing (jq-append) |
| No ancestor | standalone | Scaffold plugin with its own marketplace.json |
| No ancestor | umbrella | Scaffold umbrella dir + first plugin entry |

### Recommended Project Structure

**Standalone (flat):**
```
my-plugin/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json   # plugin is also its own single-entry marketplace
├── skills/
└── README.md
```

**Umbrella:**
```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json   # aggregates N plugins below
├── plugin-a/
│   └── .claude-plugin/plugin.json
└── plugin-b/
    └── .claude-plugin/plugin.json
```

**The one invariant:** `marketplace.json` lives at exactly one level — never both at the plugin root and an ancestor umbrella root simultaneously. [VERIFIED: design decision from .planning/notes/marketplace-support-design.md]

---

## Standard Stack

No new library dependencies. This phase uses existing toolkit tooling exclusively.

### Core (unchanged)
| Tool | Version | Purpose |
|------|---------|---------|
| Python 3 stdlib | system | All scripting (`json`, `pathlib`, `argparse`) |
| `jq` | system | Used by Bash hook helper; available for CLI demonstrations |
| `claude plugin validate` | ≥2.1.77 | Built-in marketplace + plugin validator |

### Scripts Being Extended or Added

| Script | Status | Change |
|--------|--------|--------|
| `scripts/marketplace_manager.py` | EXISTS (318 lines) | Extend validator with new optional fields; fix `author` type; add reserved names check |
| `scripts/plugin_scaffolder.py` | EXISTS (197 lines) | Fix `.claude/` mkdir bug (line 68: writes to `.claude/settings.local.json` without creating `.claude/`); add marketplace scaffolding option |
| `scripts/marketplace_register.py` | NEW | Upward-search detection + three-flow orchestration + safe jq-append |
| `data/version-manifest.json` | EXTEND | Apply schema corrections from discrepancy table |
| `data/canonical-sources.json` | ALREADY HAS | `plugin_marketplaces` source ID already present — no change needed |
| `references/marketplaces.md` | EXISTS (232 lines) | Correct `author` type; add `metadata` object structure; update reserved names; add standalone vs umbrella primer |

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Marketplace/plugin validation | Custom JSON schema validator | `claude plugin validate <path>` | Built-in, authoritative, maintained by Anthropic |
| Fetching canonical docs | HTTP scraper in phase | `scripts/docs_fetcher.py sync` (already in toolkit) | Already works; `plugin_marketplaces` source ID already in `canonical-sources.json` |
| JSON pretty-printing | `json.dumps` with manual indent | `json.dump(f, indent=2); f.write("\n")` (existing toolkit pattern) | Already used in `marketplace_manager.py` |
| Upward-directory-walk | `find` subprocess | Pure `pathlib.Path` loop (see pattern above) | Stdlib, no subprocess; matches toolkit zero-dependency rule |
| Author field validation | Custom type checker | Schema table in version-manifest; validator reads it | Self-describing pattern already established |

**Key insight:** The built-in `claude plugin validate` handles syntax and schema errors authoritatively. The toolkit's `marketplace_manager.py` adds semantic checks (path exists, plugin.json present, reserved names). Don't duplicate what the built-in does.

---

## Common Pitfalls

### Pitfall 1: `../` in relative source paths
**What goes wrong:** Scaffold generates `"source": "../other-plugin"` for plugins not inside the marketplace directory.
**Why it happens:** The constraint that plugins must be inside the marketplace root is not obvious.
**How to avoid:** `marketplace_register.py` must enforce: plugin path must be inside (or equal to) the marketplace root. Emit a clear error if `plugin_path.relative_to(marketplace_root)` raises `ValueError`.
**Warning signs:** `plugins[0].source: Path contains ".."` validation error from `claude plugin validate`.

### Pitfall 2: `plugin.json` version silently overrides marketplace entry version
**What goes wrong:** Developer sets version in both `plugin.json` and marketplace entry, marketplace entry is ignored with no warning.
**Why it happens:** Documented behavior but easy to miss.
**How to avoid:** Scaffolded standalone plugins should set version only in the marketplace entry (for relative-path plugins). Document this in the validator warning.
**Warning signs:** Apparent mismatch between installed version and what marketplace shows.

### Pitfall 3: Reserved marketplace name
**What goes wrong:** User names their marketplace `anthropic-plugins` or `claude-code-plugins` and gets a load error.
**Why it happens:** Reserved names list is not user-visible during scaffolding.
**How to avoid:** `marketplace_register.py` must check the reserved names list from `version-manifest.json` before writing. Emit a clear error.
**Warning signs:** No warning during scaffolding; failure only at `claude plugin marketplace add` time.

### Pitfall 4: URL-based marketplace + relative plugin paths
**What goes wrong:** User distributes marketplace via direct URL (not git). Plugins with `"source": "./my-plugin"` fail to install.
**Why it happens:** URL distribution only downloads `marketplace.json`, not the plugin directories.
**How to avoid:** Primer in `references/marketplaces.md` must call this out. Local-path scaffolded marketplaces are for local/git use only.
**Warning signs:** `plugins[N].source: Path not found` errors at install time.

### Pitfall 5: `strict: false` + plugin has component-declaring `plugin.json`
**What goes wrong:** Plugin fails to load with a conflict error.
**Why it happens:** `strict: false` means the marketplace entry is the entire definition — a `plugin.json` that also declares components is a conflict.
**How to avoid:** Don't set `strict: false` unless the plugin intentionally has no component-declaring `plugin.json`. The default (`true`) is correct for nearly all cases.

### Pitfall 6: Bug in `plugin_scaffolder.py` — missing `.claude/` mkdir
**What goes wrong:** Scaffolder tries to write `plugin_dir/.claude/settings.local.json` (line 68) but never creates the `.claude/` directory (only `.claude-plugin/` is created at line 39).
**Why it happens:** Missing `(plugin_dir / ".claude").mkdir()` before line 68.
**How to avoid:** Fix before Phase 1 scaffolding work extends this file. Add `(plugin_dir / ".claude").mkdir()` after the other `mkdir()` calls.

### Pitfall 7: `metadata` is an object, not top-level flat fields
**What goes wrong:** Validator or scaffolder generates `{"description": "...", "version": "1.0"}` at top level instead of `{"metadata": {"description": "...", "version": "1.0"}}`.
**Why it happens:** Current `version-manifest.json` stores `optional_metadata` as a flat list, not reflecting the nested `metadata` object.
**How to avoid:** Fix version-manifest schema to model `metadata` as an object key with sub-fields. Scaffolder must write `metadata: {...}` not top-level fields.

---

## Code Examples

All examples are from verified official docs or the live codebase.

### Minimal Valid marketplace.json
```json
{
  "name": "my-marketplace",
  "owner": { "name": "Your Name" },
  "plugins": [
    {
      "name": "my-plugin",
      "source": "./my-plugin"
    }
  ]
}
```
[VERIFIED: https://code.claude.com/docs/en/plugin-marketplaces — walkthrough step 4]

### marketplace.json with metadata and multiple source types
```json
{
  "name": "company-tools",
  "owner": {
    "name": "DevTools Team",
    "email": "devtools@example.com"
  },
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
      "author": { "name": "DevTools Team" }
    },
    {
      "name": "deploy-tools",
      "source": {
        "source": "github",
        "repo": "company/deploy-plugin",
        "ref": "v1.0.0",
        "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
      }
    }
  ]
}
```
[VERIFIED: https://code.claude.com/docs/en/plugin-marketplaces — combined from schema + examples]

### Safe jq-append pattern (for `marketplace_register.py`)
```python
# stdlib-only; no subprocess jq needed — use Python json module
import json
from pathlib import Path

def append_plugin_entry(marketplace_root: Path, entry: dict) -> None:
    manifest_path = marketplace_root / ".claude-plugin" / "marketplace.json"
    with open(manifest_path) as f:
        manifest = json.load(f)
    # Idempotency check
    names = {p["name"] for p in manifest.get("plugins", [])}
    if entry["name"] in names:
        raise ValueError(f"Plugin '{entry['name']}' already registered")
    manifest.setdefault("plugins", []).append(entry)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
```
[VERIFIED: pattern matches existing `marketplace_manager.py` add_plugin() function]

### CLI commands — verified forms
```bash
# Add marketplace (slash command inside Claude Code)
/plugin marketplace add ./my-marketplace
/plugin marketplace add owner/repo
/plugin marketplace add https://gitlab.com/team/plugins.git

# Add marketplace (CLI, non-interactive)
claude plugin marketplace add ./my-marketplace
claude plugin marketplace add owner/repo --scope project

# Install plugin
/plugin install my-plugin@my-marketplace
claude plugin install my-plugin@marketplace-name

# Validate
/plugin validate .
claude plugin validate .

# Reload without restart
/reload-plugins
```
[VERIFIED: https://code.claude.com/docs/en/discover-plugins, https://code.claude.com/docs/en/plugin-marketplaces]

### Settings integration
```json
// .claude/settings.json — make teammates auto-prompted
{
  "extraKnownMarketplaces": {
    "my-team-tools": {
      "source": {
        "source": "github",
        "repo": "your-org/claude-plugins"
      }
    }
  },
  "enabledPlugins": {
    "code-formatter@my-team-tools": true
  }
}
```
[VERIFIED: https://code.claude.com/docs/en/discover-plugins — team marketplaces section]

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Schema facts (required/optional fields, reserved names, source types) | `data/version-manifest.json` | — | Single source of truth pattern already established |
| Canonical docs fetch + cache | `scripts/docs_fetcher.py` | `data/canonical-sources.json` | Already handles; `plugin_marketplaces` ID already present |
| Marketplace schema reference (human-readable) | `references/marketplaces.md` | — | Shared reference layer; consumed by multiple skills |
| Scaffolding (three flows) | `scripts/marketplace_register.py` (new) | `scripts/plugin_scaffolder.py` (extended) | Separation: register.py = detection + marketplace ops; scaffolder.py = plugin structure |
| Validation (semantic checks) | `scripts/marketplace_manager.py` | `claude plugin validate` (built-in) | Built-in handles syntax; manager handles semantic (paths exist, reserved names) |
| User-facing guidance | `skills/extension-builder/SKILL.md` | `skills/extension-starter/SKILL.md` | Builder = create flow; starter = entry decision point |
| Audit / upgrade guidance | `skills/extension-optimizer/SKILL.md` | — | Already references `marketplace_manager.py validate` |

---

## Don't Hand-Roll

(See table above — repeated key items for planner emphasis.)

- Do NOT write a custom JSON Schema validator. Use Python `json` for parsing; use the version-manifest schema tables for field lists.
- Do NOT shell out to `jq` for the register operation. Use Python `json` module (matches zero-dependency convention).
- Do NOT fetch marketplace docs in this phase. The `plugin_marketplaces` source is already in `canonical-sources.json`; just run `docs_fetcher.py sync`.
- Do NOT add a new `docs_fetcher.py sync` URL for marketplaces — it already exists.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `path` field in plugin entry | `source` field | Unknown version | `path` is deprecated/warning; validator must check |
| Top-level `description`/`version` fields | Nested under `metadata` object | Unknown | Scaffolded files must use `metadata: {}` wrapper |
| `pip` source type (if ever valid) | Not documented in official docs | Unknown | Remove from version-manifest source_types |

**Deprecated/outdated:**
- `path` field in plugin entry: replaced by `source`. [VERIFIED: official docs + current `marketplace_manager.py`]
- `pip` source type: not in official docs. Remove from toolkit.

---

## Environment Availability

Step 2.6: All dependencies are system-level Python stdlib + `claude plugin validate` which is part of Claude Code itself. No external tools required for this phase beyond what already runs the toolkit.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | All scripts | ✓ | system | — |
| `json` / `pathlib` stdlib | `marketplace_register.py` | ✓ | stdlib | — |
| `claude plugin validate` | Validation guidance in skills | ✓ | ≥2.1.77 | `marketplace_manager.py validate` (already works) |
| `jq` | Bash hook helper only | ✓ (assumed system) | system | Not used in new Python scripts |

---

## Validation Architecture

No test infrastructure exists in this project. The toolkit has no `pytest`, no test files, no CI. Per STACK.md: "Testing: None detected."

Validation for this phase is manual:
- Run `scripts/marketplace_manager.py validate <path>` on known-good and known-bad marketplaces
- Run `claude plugin validate .` from marketplace roots
- Confirm scaffolded outputs match official schema examples

Wave 0 gap: If tests are desired in future, they would live in `tests/` with `pytest`. This is out of scope for Phase 1 per the existing project convention of zero test infrastructure.

---

## Open Questions

1. **Is `pip` source type valid in older Claude Code versions?**
   - What we know: Not in official docs as of 2026-04-16.
   - What's unclear: Was it ever supported? Is it planned?
   - Recommendation: Remove from version-manifest `source_types`. If a user reports needing it, restore then.

2. **`metadata` key: is it truly optional or conditionally required?**
   - What we know: Official docs list it as optional metadata.
   - What's unclear: Whether Claude Code throws an error if `metadata` key is absent entirely.
   - Recommendation: Treat as optional. The live sirtaj-plugins marketplace uses it and the toolkit should too, but absence should not be a validator error.

3. **Does `claude plugin validate` check marketplace.json against reserved names?**
   - What we know: The built-in validator is documented to check syntax and frontmatter.
   - What's unclear: Whether the reserved-names check happens in the built-in or only at `marketplace add` time.
   - Recommendation: Add reserved-names check to `marketplace_manager.py validate` regardless (belt-and-suspenders).

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `pip` source type was never valid in the current Claude Code version | Schema Discrepancies | If it was valid, removing it from the manifest could cause false-positive warnings. Low risk — users would report it. |
| A2 | `jq` is available on the developer machine at runtime | Environment Availability | Hook helper already uses it; toolkit STACK.md lists it as required. Actual risk is negligible. |
| A3 | The `plugin_scaffolder.py` bug (missing `.claude/` mkdir) has never triggered in practice because the tool is not widely used for .claude/ content | Pitfall 6 | If users have hit it, they found a workaround. Fix is mandatory regardless. |

---

## Sources

### Primary (HIGH confidence)
- `https://code.claude.com/docs/en/plugin-marketplaces` — full marketplace.json schema, plugin entry fields, source types, strict mode, CLI commands, reserved names, settings integration, troubleshooting
- `https://code.claude.com/docs/en/discover-plugins` — installation commands, `/plugin marketplace add` variants, team settings
- Live codebase: `data/version-manifest.json`, `references/marketplaces.md`, `scripts/marketplace_manager.py`, `scripts/plugin_scaffolder.py` — current state baseline
- `/home/sirtaj/proj/claude-stuff/.claude-plugin/marketplace.json` — live real-world example of the umbrella pattern

### Secondary (MEDIUM confidence)
- `data/canonical-sources.json` — confirmed `plugin_marketplaces` source ID already present; no new URL needed

### Tertiary (LOW confidence)
- None. All schema claims in this document are verified against the official docs fetched in this session.

---

## Metadata

**Confidence breakdown:**
- Canonical schema: HIGH — fetched directly from official docs
- Schema discrepancies (pip, reserved names, metadata nesting, author type): HIGH — cross-verified between official docs and current toolkit files
- Three-flow scaffolder design: HIGH — locked design decision in .planning/notes/
- CLI commands: HIGH — verified against official docs
- plugin_scaffolder.py bug: HIGH — confirmed by reading source code

**Research date:** 2026-04-16
**Valid until:** ~2026-05-16 (stable API; check if Claude Code version advances significantly)
