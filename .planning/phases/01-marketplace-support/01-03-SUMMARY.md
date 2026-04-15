---
phase: 01-marketplace-support
plan: 03
subsystem: scaffolder-three-flows
tags: [scaffolder, marketplace, wave-2]
dependency_graph:
  requires: ["01-01"]
  provides:
    - "scripts/marketplace_register.py — upward-search detection + three flows"
    - "scripts/plugin_scaffolder.py — auto-creates standalone marketplace.json by default"
  affects: ["01-05"]
tech_stack:
  added: []
  patterns:
    - "Pure-pathlib upward-search (no subprocess)"
    - "Stdlib-only safe JSON append (no shell jq)"
    - "Reserved-name check reads data/version-manifest.json"
key_files:
  created:
    - scripts/marketplace_register.py
  modified:
    - scripts/plugin_scaffolder.py
decisions:
  - "Standalone source is './' (plugin root = marketplace root); umbrella/register flows use validated relative_to()."
  - "Scaffolder inlines its own marketplace-json emission rather than shelling out to marketplace_register.py — simpler and avoids a cross-script dependency at scaffold time."
  - "Reserved-name check is duplicated (helper in each script) but both read the same version-manifest source of truth, so no divergence risk."
  - "--layout auto detects ancestor marketplace.json via upward pathlib walk; explicit --layout standalone|umbrella overrides."
metrics:
  duration: "~10 min"
  completed: 2026-04-16
---

# Phase 01 Plan 03: Scaffolder Three Flows Summary

Implemented the three marketplace scaffolder flows (register-into-existing, greenfield-standalone, greenfield-umbrella) in a new `scripts/marketplace_register.py`, and extended `scripts/plugin_scaffolder.py` so the default scaffold now emits a standalone `marketplace.json` at the plugin root — a fresh plugin is immediately installable via `/plugin marketplace add <plugin-dir>`.

## Tasks Executed

| # | Task | Commit |
|---|------|--------|
| 1 | Create marketplace_register.py with three flows + detection | `d8901db` |
| 2 | Extend plugin_scaffolder.py to auto-create standalone marketplace.json | `b082136` |

## CLI Surfaces

### scripts/marketplace_register.py

```
marketplace_register.py <plugin_name>
    [--plugin-path PATH]          # default: CWD
    [--layout {standalone,umbrella,auto}]   # default: auto
    [--owner NAME]
    [--owner-email EMAIL]
    [--marketplace-name NAME]
    [--umbrella-path PATH]
```

Public functions: `load_reserved_names`, `find_ancestor_marketplace`, `read_manifest`, `write_manifest`, `validate_relative_path`, `append_plugin_entry`, `check_reserved_name`, `scaffold_marketplace_manifest`, `build_plugin_entry`, `register_in_existing`, `scaffold_standalone`, `scaffold_umbrella`.

### scripts/plugin_scaffolder.py (new flags)

```
plugin_scaffolder.py <name>
    [--output DIR]
    [--description STR]
    [--author NAME] [--email ADDR]
    [--marketplace {standalone,none}]       # NEW — default: standalone
    [--marketplace-name NAME]               # NEW — default: plugin name
```

## Flow Selection Table

| Detection (ancestor marketplace.json?) | --layout | Flow |
|---|---|---|
| Yes | auto or umbrella | Register-in-existing (append entry) |
| No  | auto | Error (ask user to pick standalone/umbrella) |
| No  | standalone | Scaffold plugin + its own marketplace.json |
| No  | umbrella | Scaffold umbrella dir + first plugin entry |

## Example End-to-End Transcript

```
$ python3 scripts/plugin_scaffolder.py my-plugin --output /tmp/demo --author "Me" --email me@x.com
Created plugin at: /tmp/demo/my-plugin

Next steps:
  1. cd /tmp/demo/my-plugin
  2. Edit skills/, commands/, or agents/
  3. Test with: claude --plugin-dir /tmp/demo/my-plugin
  4. /plugin marketplace add /tmp/demo/my-plugin
  5. /plugin install my-plugin@my-plugin

$ cat /tmp/demo/my-plugin/.claude-plugin/marketplace.json
{
  "name": "my-plugin",
  "owner": {"name": "Me", "email": "me@x.com"},
  "plugins": [
    {"name": "my-plugin", "source": "./", "description": "my-plugin plugin for Claude Code", "version": "1.0.0"}
  ]
}
```

Registering a second plugin into an existing umbrella:

```
$ cd /path/to/umbrella/new-plugin
$ python3 /.../scripts/marketplace_register.py new-plugin --layout auto --owner "Me"
Registered 'new-plugin' into umbrella/.claude-plugin/marketplace.json as ./new-plugin
```

## Verification

All four Task 1 smoke tests passed:
- Reserved name `agent-skills` → exit 1, "reserved" in stderr
- Standalone scaffold writes marketplace.json with `source: "./"`
- Auto layout detects ancestor and appends entry idempotently
- Plugin path outside umbrella root → exit 1

All three Task 2 smoke tests passed:
- Default scaffold emits `marketplace.json` with owner `{name, email}` and source `"./"`
- `--marketplace none` skips marketplace.json creation
- Reserved `--marketplace-name` rejected with exit 1

## Deviations from Plan

None — plan executed as written. PostToolUse formatter hook reformatted `marketplace_register.py` and `plugin_scaffolder.py` on each Write/Edit; behavior unchanged, all tests still pass. The formatter-reformat note matches Plan 01's experience.

## Notes for Downstream Plans

- **Plan 01-04 (validator):** The `source_types` object in `data/version-manifest.json` (from Plan 01-01) is available for per-source-type validation. The three flows in `marketplace_register.py` always emit `source: "./" + posix-rel-path`, which the validator must accept.
- **Plan 01-05 (skill integration):** `extension-builder` skill should orchestrate `marketplace_register.py` for the register-in-existing and umbrella flows, and call `plugin_scaffolder.py` (default `--marketplace standalone`) for the standalone flow. The CLI surfaces documented above are the contract.
- **No promotion flow.** Standalone → umbrella promotion remains explicitly out of scope (seeded at `.planning/seeds/marketplace-promotion-flow.md`). Today, if a user needs to promote, they delete the inner `marketplace.json` and run `marketplace_register.py` from within the new umbrella.

## Self-Check: PASSED

- scripts/marketplace_register.py — FOUND, executable, syntactically valid, all four smoke tests pass
- scripts/plugin_scaffolder.py — FOUND, all three smoke tests pass, existing behavior preserved
- Commits `d8901db` (Task 1) and `b082136` (Task 2) — both present in `git log`
