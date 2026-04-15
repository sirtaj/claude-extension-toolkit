---
phase: 01-marketplace-support
plan: 01
subsystem: schema-corrections
tags: [schema, marketplace, wave-0]
dependency_graph:
  requires: []
  provides:
    - "corrected marketplace schema in data/version-manifest.json"
    - "corrected human-readable schema in references/marketplaces.md"
    - "bug-free scripts/plugin_scaffolder.py"
  affects: ["01-02", "01-03", "01-04", "01-05"]
tech_stack:
  added: []
  patterns: []
key_files:
  created: []
  modified:
    - data/version-manifest.json
    - references/marketplaces.md
    - scripts/plugin_scaffolder.py
decisions:
  - "Replaced source_types flat array with object keyed by type, carrying per-type field requirements (matches canonical schema)."
  - "Added field_types block for author/keywords/homepage/repository/license so downstream validators can enforce shapes from a single source of truth."
metrics:
  duration: "~5 min"
  completed: 2026-04-16
---

# Phase 01 Plan 01: Schema Corrections Summary

Wave 0 prerequisite — corrected four marketplace schema discrepancies in `data/version-manifest.json`, aligned `references/marketplaces.md` with the canonical schema, and fixed the `.claude/` mkdir bug in `scripts/plugin_scaffolder.py`.

## Tasks Executed

| # | Task | Commit |
|---|------|--------|
| 1 | Correct version-manifest.json marketplace schema facts | `51eb89d` |
| 2 | Correct references/marketplaces.md author type and reserved names | `9b14c9e` |
| 3 | Fix plugin_scaffolder.py .claude/ mkdir bug | `c09e8f9` |

## Diffs Applied

### data/version-manifest.json (commit 51eb89d)

- `schemas.marketplace_manifest.reserved_names` — replaced the old 5-entry list (`anthropic`, `claude`, `official`, `claude-code`, `anthropic-plugins`) with the official 8-entry list (`claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`).
- `schemas.marketplace_manifest.optional_metadata` → renamed `metadata_fields`; added top-level `optional: ["metadata"]` wrapper plus `optional_owner_fields: ["email"]`.
- `schemas.marketplace_plugin_entry.source_types` — converted from flat array to object keyed by type name with per-type field requirements. Dropped `pip`; renamed `git_subdir` → `git-subdir`.
- `schemas.marketplace_plugin_entry.optional` — added `homepage`, `repository`, `license`, `keywords`.
- `schemas.marketplace_plugin_entry.field_types` — new block documenting `author` object shape, plus types for `keywords`/`homepage`/`repository`/`license`.
- `deprecated_fields.path` preserved unchanged.
- No other schema, deprecation, or canonical_url touched.

### references/marketplaces.md (commit 9b14c9e)

- JSON example: `"author": "Author Name"` → `"author": { "name": "Author Name", "email": "author@example.com" }`.
- Field table: `author` row type changed from `string` to `object`, description `{name: string, email?: string}`.
- Added rows for `homepage`, `repository`, `license`, `keywords`.
- Source Types table: removed `pip` row.
- Reserved Marketplace Names: replaced inline 5-name string with bullet list of 8 official names.

### scripts/plugin_scaffolder.py (commit c09e8f9)

- Added `(plugin_dir / ".claude").mkdir()` alongside the other mkdir calls (now at line 44) so `.claude/settings.local.json` can be written without `FileNotFoundError`.
- NOTE: a project PostToolUse formatter hook reformatted the entire file (trailing-comma / style normalization) — commit diff shows 18 insertions / 39 deletions. Behavior unchanged; smoke test passes.

## Verification Commands Run

All Task 1 jq assertions passed:

```
jq -e '.schemas.marketplace_manifest.reserved_names | index("agent-skills")'        → 5
jq -e '.schemas.marketplace_plugin_entry.source_types.github.fields.repo == "required"' → true
jq -e '.schemas.marketplace_plugin_entry.source_types | has("pip") | not'           → true
jq -e '.schemas.marketplace_plugin_entry.source_types | has("git-subdir")'          → true
jq -e '.schemas.marketplace_plugin_entry.optional | index("homepage") and index("repository") and index("license") and index("keywords")' → true
jq -e '.schemas.marketplace_plugin_entry.field_types.author.type == "object"'       → true
jq -e '.schemas.marketplace_manifest.metadata_fields | length == 3'                 → true
python3 -m json.tool data/version-manifest.json > /dev/null                         → OK
```

Task 2 grep assertions: all 11 pass (author object form present, 4 new rows present, 3 reserved-name sentinels present, no old author-as-string, no pip:package-name).

Task 3 end-to-end smoke test:

```
python3 scripts/plugin_scaffolder.py test-plug --output <tmpdir>
# → exit 0
# → test-plug/.claude/settings.local.json exists
# → test-plug/.claude-plugin/plugin.json exists
```

## Deviations from Plan

None — plan executed exactly as written. The PostToolUse formatter hook reformatted `plugin_scaffolder.py` on write (acceptable, not a deviation — project-level tooling).

## Surprises / Notes for Downstream Plans

- Plan 01-02/03/04/05 can read the corrected schema from `data/version-manifest.json` directly. Key access paths:
  - Reserved names → `.schemas.marketplace_manifest.reserved_names` (8 entries)
  - Metadata fields → `.schemas.marketplace_manifest.metadata_fields`
  - Plugin entry optional fields → `.schemas.marketplace_plugin_entry.optional`
  - Author shape enforcement → `.schemas.marketplace_plugin_entry.field_types.author`
  - Source types with per-type field reqs → `.schemas.marketplace_plugin_entry.source_types` (now an object, was an array)
- **Breaking shape change for downstream code:** `source_types` is now an object, not an array. Any code iterating it should use keys/values accessors. No downstream code exists yet — safe.
- `plugin_scaffolder.py` file style was normalized by the formatter; future edits should Read first to see current state.

## Self-Check: PASSED

- data/version-manifest.json — FOUND, valid JSON, all jq assertions pass
- references/marketplaces.md — FOUND, all greps pass
- scripts/plugin_scaffolder.py — FOUND, mkdir line present at line 44, smoke test passes
- Commits 51eb89d, 9b14c9e, c09e8f9 — all present in `git log`
