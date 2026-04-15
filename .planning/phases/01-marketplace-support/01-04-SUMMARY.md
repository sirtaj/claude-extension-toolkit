---
phase: 01-marketplace-support
plan: 04
subsystem: validator-tiered-severity
tags: [validator, marketplace, severity, wave-2]
dependency_graph:
  requires: ["01-01"]
  provides:
    - "tiered-severity validator (errors vs warnings) in scripts/marketplace_manager.py"
    - "schema-driven validation — reserved names/metadata fields/source types read from data/version-manifest.json"
    - "--json output with valid/errors/warnings tri-state"
  affects: ["01-05"]
tech_stack:
  added: []
  patterns:
    - "SCRIPT_DIR/TOOLKIT_ROOT pattern for locating version-manifest.json"
    - "degrade-gracefully schema loader — empty dicts on missing/malformed manifest"
key_files:
  created: []
  modified:
    - scripts/marketplace_manager.py
decisions:
  - "validate_marketplace signature changed from (bool, errors) to (errors, warnings) — no external callers so no breakage"
  - "Legacy 'path' field demoted from silent-stderr warning to structured warning surfaced via --json"
  - "source=='./' exempted from missing-plugin.json check (standalone layout, marketplace root IS plugin root)"
metrics:
  duration: "~4 min"
  completed: 2026-04-16
---

# Phase 01 Plan 04: Validator Tiered Severity Summary

Extended `scripts/marketplace_manager.py validate` with tiered-severity validation. Hard errors block installation (exit 1); warnings surface guidance without blocking (exit 0). All schema facts come from `data/version-manifest.json` — no hardcoded lists.

## Tasks Executed

| # | Task | Commit |
|---|------|--------|
| 1 | Extend marketplace_manager.py with tiered-severity validation | `1a0564d` |

## Severity Tier Table

| Issue | Tier | Exit |
|-------|------|------|
| Malformed JSON in marketplace.json | Error | 1 |
| Missing required top-level field (name, owner, plugins) | Error | 1 |
| Missing required plugin-entry field (name, source) | Error | 1 |
| Reserved marketplace name collision (per version-manifest) | Error | 1 |
| `owner` not an object / missing `owner.name` | Error | 1 |
| `metadata` not an object (list/string) | Error | 1 |
| `author` not an object / missing `author.name` | Error | 1 |
| Unknown source type (e.g. `ftp`, `pip`) | Error | 1 |
| Source string containing `../` | Error | 1 |
| Local source path missing on disk | Error | 1 |
| Local source missing `.claude-plugin/plugin.json` (non-standalone) | Error | 1 |
| Plugin entry not an object | Error | 1 |
| Missing optional plugin field (homepage/repository/license/keywords/description) | Warning | 0 |
| Duplicate plugin name within marketplace | Warning | 0 |
| Legacy `path` field used instead of `source` | Warning | 0 |
| Unknown `metadata` key (not in version-manifest metadata_fields) | Warning | 0 |

## Sample Outputs

### Hard error (reserved name)

```json
{
  "valid": false,
  "errors": [
    "Marketplace name 'agent-skills' is reserved by Anthropic. Reserved list: ['agent-skills', 'anthropic-marketplace', ...]"
  ],
  "warnings": []
}
```
Exit code: 1

### Warnings only (minimal valid manifest)

```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Plugin 'p1' missing optional field 'homepage'",
    "Plugin 'p1' missing optional field 'repository'",
    "Plugin 'p1' missing optional field 'license'",
    "Plugin 'p1' missing optional field 'keywords'",
    "Plugin 'p1' missing optional field 'description'"
  ]
}
```
Exit code: 0

### Clean run (real marketplace)

```
$ python3 scripts/marketplace_manager.py validate /home/sirtaj/proj/claude-stuff --json | jq '{valid, err_count: (.errors|length), warn_count: (.warnings|length)}'
{ "valid": true, "err_count": 0, "warn_count": 16 }
```

## Verification

All six smoke tests from the plan's `<verify>` block passed:

1. Reserved name → exit 1, "reserved" in errors
2. `author: "string"` → exit 1, error mentions "author" and "object"
3. `metadata: [...]` → exit 1, error mentions "metadata" and "object"
4. Minimal valid manifest missing optional fields → exit 0, warnings for homepage/repository/license/keywords/description
5. Duplicate plugin names → exit 0, "duplicate" warning
6. Unknown source type (`ftp`) → exit 1, "unknown source type" error

Regression smoke (existing subcommands unchanged):

- `python3 scripts/marketplace_manager.py list /home/sirtaj/proj/claude-stuff` → exit 0, lists plugins correctly
- `python3 scripts/marketplace_manager.py validate /home/sirtaj/proj/claude-stuff --json` → valid=true, 0 errors, 16 warnings (all missing-optional-field guidance on existing plugin entries)

AST parse + grep assertions pass:
- `_load_schema` function defined
- Signature `Tuple[List[str], List[str]]` present
- "reserved by Anthropic" message present
- "must be an object {name, email?}" message present

## Deviations from Plan

None — plan executed exactly as written. The plan already accounted for the `source == "./"` standalone exemption and the legacy-path warning migration.

## Notes for Downstream Plans

- Plan 01-05 (skill integration) can cite the `--json` output shape `{valid, errors, warnings}` when documenting CI usage patterns for `extension-optimizer`.
- `plugin_optional` set is loaded from version-manifest but currently unused (guarded by `# noqa: F841`) — future extension can use it to flag unknown plugin-entry keys as warnings.
- Validator degrades gracefully if `data/version-manifest.json` is missing/malformed (empty dicts returned) — reserved-name and source-type checks silently skip, avoiding spurious false-positives during bootstrap/dev.

## Self-Check: PASSED

- scripts/marketplace_manager.py — FOUND, syntactically valid, all 6 smoke tests pass, regression smoke on live marketplace passes
- Commit 1a0564d — present in `git log`
