---
phase: 01-marketplace-support
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - data/version-manifest.json
  - references/marketplaces.md
  - scripts/plugin_scaffolder.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "data/version-manifest.json matches official marketplace.json schema (no pip source, correct reserved names, metadata object shape, author object shape)"
    - "references/marketplaces.md documents author as object {name, email}, not string"
    - "scripts/plugin_scaffolder.py creates .claude/ directory before writing .claude/settings.local.json (bug fixed)"
    - "Running scripts/plugin_scaffolder.py produces a working plugin with no mkdir error"
  artifacts:
    - path: "data/version-manifest.json"
      provides: "Corrected marketplace schema facts downstream code reads"
      contains: "marketplace_plugin_entry with object-shaped author, reserved_names with 8 official entries, no pip source"
    - path: "references/marketplaces.md"
      provides: "Human-readable marketplace reference with corrected author type"
    - path: "scripts/plugin_scaffolder.py"
      provides: "Plugin scaffolder with .claude/ mkdir fix"
  key_links:
    - from: "downstream validator/scaffolder plans"
      to: "data/version-manifest.json"
      via: "reads schemas.marketplace_manifest + schemas.marketplace_plugin_entry"
      pattern: "json.load.*version-manifest"
---

<objective>
Wave 0 prerequisite: correct all four schema discrepancies in data/version-manifest.json, align references/marketplaces.md with the canonical schema, and fix the plugin_scaffolder.py mkdir bug. Every downstream plan (02, 03, 04, 05) writes against the corrected spec.

Purpose: Prevent propagation of wrong schema facts into new scaffolder/validator/docs code. A single source of truth must be correct before anything reads from it.

Output: Corrected data/version-manifest.json, corrected references/marketplaces.md, bug-fixed scripts/plugin_scaffolder.py.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/ROADMAP.md
@.planning/phases/01-marketplace-support/01-CONTEXT.md
@.planning/phases/01-marketplace-support/01-RESEARCH.md
@data/version-manifest.json
@references/marketplaces.md
@scripts/plugin_scaffolder.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Correct version-manifest.json marketplace schema facts</name>
  <files>data/version-manifest.json</files>
  <read_first>
    - data/version-manifest.json (current state, especially schemas.marketplace_manifest and schemas.marketplace_plugin_entry)
    - .planning/phases/01-marketplace-support/01-RESEARCH.md (Schema Discrepancies table, lines 104-116; Data Layer extension, lines 146-174)
    - .planning/phases/01-marketplace-support/01-CONTEXT.md (Schema-discrepancy fixes section)
  </read_first>
  <action>
    Edit `data/version-manifest.json`. Apply these four corrections and one addition exactly:

    1. **Replace `schemas.marketplace_manifest` entirely** with this object:
    ```json
    "marketplace_manifest": {
      "required": ["name", "owner", "plugins"],
      "required_owner_fields": ["name"],
      "optional_owner_fields": ["email"],
      "optional": ["metadata"],
      "metadata_fields": ["description", "version", "pluginRoot"],
      "reserved_names": [
        "claude-code-marketplace",
        "claude-code-plugins",
        "claude-plugins-official",
        "anthropic-marketplace",
        "anthropic-plugins",
        "agent-skills",
        "knowledge-work-plugins",
        "life-sciences"
      ]
    }
    ```
    Note: reserved_names list is the exact official list from RESEARCH.md line 99 / CONTEXT.md. The old list (`anthropic`, `claude`, `official`, `claude-code`, `anthropic-plugins`) is WRONG — replace wholesale. The old flat `optional_metadata` array becomes `metadata_fields` and the top-level optional is now just `["metadata"]` (the object wrapper).

    2. **Replace `schemas.marketplace_plugin_entry` entirely** with this object:
    ```json
    "marketplace_plugin_entry": {
      "required": ["name", "source"],
      "optional": [
        "description",
        "version",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "category",
        "tags",
        "strict",
        "commands",
        "agents",
        "skills",
        "hooks",
        "mcpServers",
        "outputStyles",
        "lspServers"
      ],
      "field_types": {
        "author": {"type": "object", "required": ["name"], "optional": ["email"]},
        "keywords": {"type": "array"},
        "homepage": {"type": "string"},
        "repository": {"type": "string"},
        "license": {"type": "string"}
      },
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
    Changes: `pip` source REMOVED; `git_subdir` renamed to `git-subdir` (matches canonical schema's `source` value); source_types flipped from flat list to object with per-type field requirements; `homepage`, `repository`, `license`, `keywords` ADDED to optional; `field_types` block added so downstream validators can enforce author object shape.

    3. Do NOT change anything else (preserve skill_frontmatter, agent_frontmatter, command_frontmatter, plugin_manifest, hooks, permission_modes, model_values, deprecations, canonical_urls).

    4. Keep the JSON pretty-printed with 2-space indent and trailing newline (matches existing file style).
  </action>
  <verify>
    <automated>
      jq -e '.schemas.marketplace_manifest.reserved_names | index("agent-skills")' data/version-manifest.json &&
      jq -e '.schemas.marketplace_manifest.reserved_names | index("anthropic") | not' data/version-manifest.json &&
      jq -e '.schemas.marketplace_plugin_entry.source_types.github.fields.repo == "required"' data/version-manifest.json &&
      jq -e '.schemas.marketplace_plugin_entry.source_types | has("pip") | not' data/version-manifest.json &&
      jq -e '.schemas.marketplace_plugin_entry.source_types | has("git-subdir")' data/version-manifest.json &&
      jq -e '.schemas.marketplace_plugin_entry.optional | index("homepage") and index("repository") and index("license") and index("keywords")' data/version-manifest.json &&
      jq -e '.schemas.marketplace_plugin_entry.field_types.author.type == "object"' data/version-manifest.json &&
      jq -e '.schemas.marketplace_manifest.metadata_fields | length == 3' data/version-manifest.json &&
      python3 -m json.tool data/version-manifest.json > /dev/null
    </automated>
  </verify>
  <acceptance_criteria>
    - `jq '.schemas.marketplace_manifest.reserved_names'` returns exactly these 8 strings (order not strict, but set must match): `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`.
    - `jq '.schemas.marketplace_plugin_entry.source_types | keys'` does NOT contain `pip` or `git_subdir`; DOES contain `git-subdir`.
    - `jq '.schemas.marketplace_plugin_entry.optional'` contains all of: `homepage`, `repository`, `license`, `keywords`.
    - `jq '.schemas.marketplace_plugin_entry.field_types.author'` returns `{"type":"object","required":["name"],"optional":["email"]}`.
    - `jq '.schemas.marketplace_manifest.metadata_fields'` returns `["description","version","pluginRoot"]`.
    - `python3 -m json.tool data/version-manifest.json` succeeds (valid JSON).
    - `git diff data/version-manifest.json` shows changes confined to `schemas.marketplace_manifest` and `schemas.marketplace_plugin_entry` subtrees — NO changes to any other schema, deprecation, or canonical_url.
  </acceptance_criteria>
  <done>version-manifest.json passes all jq assertions above; unrelated schemas untouched.</done>
</task>

<task type="auto">
  <name>Task 2: Correct references/marketplaces.md author type and reserved names</name>
  <files>references/marketplaces.md</files>
  <read_first>
    - references/marketplaces.md (entire file, 232 lines)
    - .planning/phases/01-marketplace-support/01-RESEARCH.md (Plugin Entry Fields section, lines 48-73; Reserved Marketplace Names section, lines 97-100)
  </read_first>
  <action>
    Edit `references/marketplaces.md`. Four targeted changes:

    1. **Fix author type in the JSON example (around line 49).** Replace:
    ```json
    "author": "Author Name",
    ```
    with:
    ```json
    "author": { "name": "Author Name", "email": "author@example.com" },
    ```

    2. **Fix author row in the plugin-entry field table (around line 62).** Replace the row:
    ```
    | `author` | string | no | Plugin author |
    ```
    with:
    ```
    | `author` | object | no | `{name: string, email?: string}` |
    ```

    3. **Add missing optional plugin-entry field rows** after the existing `tags` row and before `strict`. Insert these four rows (in this order):
    ```
    | `homepage` | string | no | Homepage or docs URL |
    | `repository` | string | no | Source repo URL |
    | `license` | string | no | SPDX identifier (e.g. `MIT`, `Apache-2.0`) |
    | `keywords` | array | no | Discovery tags (synonym of `tags`) |
    ```

    4. **Replace the Reserved Marketplace Names section (around line 181-185).** Replace the existing list line:
    ```
    `anthropic`, `claude`, `official`, `claude-code`, `anthropic-plugins`
    ```
    with this exact bullet list (one per line — easier to scan):
    ```
    - `claude-code-marketplace`
    - `claude-code-plugins`
    - `claude-plugins-official`
    - `anthropic-marketplace`
    - `anthropic-plugins`
    - `agent-skills`
    - `knowledge-work-plugins`
    - `life-sciences`
    ```

    5. **Remove or flag the `pip` row from the Source Types table (around line 78).** Delete the line:
    ```
    | pip | `"pip:package-name"` | `"pip:claude-my-plugin"` |
    ```
    (pip is not in the official schema per RESEARCH.md line 85.)

    Do NOT change any other content. Do NOT reformat unrelated sections.
  </action>
  <verify>
    <automated>
      grep -q '"author": { "name"' references/marketplaces.md &&
      grep -q '| `author` | object | no |' references/marketplaces.md &&
      grep -q '| `homepage` | string | no |' references/marketplaces.md &&
      grep -q '| `repository` | string | no |' references/marketplaces.md &&
      grep -q '| `license` | string | no |' references/marketplaces.md &&
      grep -q '| `keywords` | array | no |' references/marketplaces.md &&
      grep -q 'claude-code-marketplace' references/marketplaces.md &&
      grep -q 'agent-skills' references/marketplaces.md &&
      grep -q 'life-sciences' references/marketplaces.md &&
      ! grep -q '"author": "Author Name"' references/marketplaces.md &&
      ! grep -q '| `author` | string | no |' references/marketplaces.md &&
      ! grep -q '"pip:package-name"' references/marketplaces.md &&
      ! grep -qE '^\`anthropic\`, \`claude\`' references/marketplaces.md
    </automated>
  </verify>
  <acceptance_criteria>
    - `author` is documented as object `{name, email?}` in both JSON example and field table.
    - Plugin-entry field table contains rows for `homepage`, `repository`, `license`, `keywords`.
    - Reserved Marketplace Names section lists exactly the 8 official names (bullet list form), not the old 5-name string list.
    - `pip` row removed from Source Types table.
    - No references to the old author-as-string shape remain.
    - No references to `pip:` source prefix in source-types table.
  </acceptance_criteria>
  <done>All grep assertions pass; file renders as clean markdown; no accidental line reformatting elsewhere.</done>
</task>

<task type="auto">
  <name>Task 3: Fix plugin_scaffolder.py .claude/ mkdir bug</name>
  <files>scripts/plugin_scaffolder.py</files>
  <read_first>
    - scripts/plugin_scaffolder.py (entire file; bug is at line 68 where `.claude/settings.local.json` is written without `.claude/` being created)
    - .planning/phases/01-marketplace-support/01-RESEARCH.md (Pitfall 6, lines 298-301)
  </read_first>
  <action>
    Edit `scripts/plugin_scaffolder.py`. Single-line fix:

    After line 43 (the existing `(plugin_dir / "hooks").mkdir()` call) and before the `# Create plugin.json` comment (line 45), add this line:
    ```python
        (plugin_dir / ".claude").mkdir()
    ```
    (same indentation as the surrounding mkdir calls: 4 spaces).

    This ensures `.claude/` exists before line 68 writes `.claude/settings.local.json`. Do NOT use `parents=True, exist_ok=True` — the parent `plugin_dir` was just created by the `.claude-plugin` mkdir with `parents=True` at line 39, so its parents exist; and `.claude` itself should be fresh (directory-already-exists would indicate a caller bug).

    Do NOT modify any other logic in the file. Do NOT change function signatures. Do NOT refactor.
  </action>
  <verify>
    <automated>
      grep -n '(plugin_dir / ".claude").mkdir()' scripts/plugin_scaffolder.py &&
      python3 -c "
import tempfile, sys, subprocess
from pathlib import Path
with tempfile.TemporaryDirectory() as td:
    r = subprocess.run(['python3', 'scripts/plugin_scaffolder.py', 'test-plug', '--output', td], capture_output=True, text=True)
    assert r.returncode == 0, f'scaffolder failed: {r.stderr}'
    p = Path(td) / 'test-plug'
    assert (p / '.claude' / 'settings.local.json').exists(), 'settings.local.json missing'
    assert (p / '.claude-plugin' / 'plugin.json').exists(), 'plugin.json missing'
    print('OK')
"
    </automated>
  </verify>
  <acceptance_criteria>
    - `grep -n '(plugin_dir / ".claude").mkdir()' scripts/plugin_scaffolder.py` returns exactly one match, located between the `hooks` mkdir line and the `# Create plugin.json` comment.
    - Running `python3 scripts/plugin_scaffolder.py test-plug --output /tmp/somedir` completes with exit code 0 and produces `test-plug/.claude/settings.local.json`.
    - No other line of the file is modified (verify with `git diff --stat`: single-file change, +1 line).
  </acceptance_criteria>
  <done>Scaffolder runs end-to-end without FileNotFoundError; settings.local.json is created.</done>
</task>

</tasks>

<verification>
Run all three task automated verifications. Then run `python3 -m json.tool data/version-manifest.json > /dev/null` and `python3 scripts/plugin_scaffolder.py _smoke_test --output /tmp` to smoke-test. Clean up `/tmp/_smoke_test` after.
</verification>

<success_criteria>
- version-manifest.json marketplace schema matches official spec exactly (all jq assertions pass)
- references/marketplaces.md author-as-object, 4 new optional fields documented, 8 reserved names listed, no pip
- plugin_scaffolder.py bug fixed — end-to-end scaffolding works with no mkdir error
- No unrelated files touched
- Downstream plans (02, 03, 04, 05) can read correct schema from version-manifest.json
</success_criteria>

<output>
After completion, create `.planning/phases/01-marketplace-support/01-01-SUMMARY.md` documenting: exact diffs applied, verification commands run, any surprises. This summary is read by downstream plans to confirm the Wave 0 prerequisite landed.
</output>
