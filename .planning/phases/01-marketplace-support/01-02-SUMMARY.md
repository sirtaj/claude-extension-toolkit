---
phase: 01-marketplace-support
plan: 02
subsystem: knowledgebase-docs
tags: [docs, schema, marketplace, wave-2]
dependency_graph:
  requires: ["01-01"]
  provides:
    - "canonical marketplace schema reference at references/marketplace-schema.md"
    - "README.md Marketplace Support primer"
  affects: ["01-03", "01-04", "01-05"]
tech_stack:
  added: []
  patterns: []
key_files:
  created:
    - references/marketplace-schema.md
  modified:
    - README.md
decisions:
  - "Primer placed between Installation and Skills in README (early visibility, before skill docs)."
  - "marketplace-schema.md is the schema/layout companion; marketplaces.md retains CLI/auth/caching."
metrics:
  duration: "~3 min"
  completed: 2026-04-16
---

# Phase 01 Plan 02: Knowledgebase Docs Summary

Created canonical schema reference `references/marketplace-schema.md` and added a Marketplace Support primer to `README.md`, both derived from the Plan 01 corrections in `data/version-manifest.json`.

## Tasks Executed

| # | Task | Commit |
|---|------|--------|
| 1 | Create references/marketplace-schema.md | `11a9bb6` |
| 2 | Add Marketplace Support primer to README.md | `19d30d3` |

## File Sizes

| File | Lines | Status |
|------|-------|--------|
| references/marketplace-schema.md | 200 | created |
| README.md | 231 (was 180) | +51 lines |

## Headings Outline — references/marketplace-schema.md

- `# Marketplace Schema Reference`
  - `## Two Layouts`
    - `### Standalone (flat)`
    - `### Umbrella (aggregating)`
    - `### The invariant`
  - `## Top-Level Schema`
  - `## Plugin Entry Schema`
  - `## Source Types`
  - `## Reserved Marketplace Names`
  - `## Strict Mode`
  - `## Minimal Valid marketplace.json`
  - `## Full Example`
  - `## Common Pitfalls`
  - `## Where This Schema Is Enforced`

## Headings Outline — README.md (new section)

- `## Marketplace Support`
  - `### Standalone (flat)`
  - `### Umbrella (aggregating)`
  - `### The one-level invariant`
  - `### Schema reference`

## Link Graph

```
README.md ──── Marketplace Support section
   │
   ├─► references/marketplace-schema.md   (NEW — schema + layouts)
   │       │
   │       ├─► references/marketplaces.md (companion — CLI/auth/caching)
   │       └─► data/version-manifest.json (schemas.marketplace_manifest
   │                                        + schemas.marketplace_plugin_entry)
   │
   └─► references/marketplaces.md         (companion)
```

Cross-links verified:
- README → marketplace-schema.md: present (`references/marketplace-schema.md` link)
- README → marketplaces.md: present
- marketplace-schema.md → marketplaces.md: present (top banner + footer)
- marketplace-schema.md → version-manifest.json: referenced in "Where This Schema Is Enforced"

## Schema Alignment with Plan 01 Corrections

| Fact | Source | Reflected in new docs |
|------|--------|----------------------|
| 8 reserved names (no `anthropic`, `claude`, etc.) | `data/version-manifest.json` `schemas.marketplace_manifest.reserved_names` | ✓ marketplace-schema.md §Reserved Marketplace Names |
| 5 source types, no `pip`, `git-subdir` with hyphen | `schemas.marketplace_plugin_entry.source_types` | ✓ marketplace-schema.md §Source Types |
| `author` as object `{name, email?}` | `schemas.marketplace_plugin_entry.field_types.author` | ✓ marketplace-schema.md §Plugin Entry Schema + Full Example |
| `metadata` as object wrapper | `schemas.marketplace_manifest.metadata_fields` | ✓ marketplace-schema.md §Top-Level Schema + Full Example |
| Optional `homepage`, `repository`, `license`, `keywords` | `schemas.marketplace_plugin_entry.optional` | ✓ marketplace-schema.md §Plugin Entry Schema |

## Verification Commands Run

Task 1:
```
test -f references/marketplace-schema.md                                 → OK
grep "^# Marketplace Schema Reference"                                   → match
grep "^## Two Layouts"                                                   → match
grep "^### Standalone (flat)"                                            → match
grep "^### Umbrella (aggregating)"                                       → match
grep "^## Reserved Marketplace Names"                                    → match
grep "`claude-code-marketplace`"                                         → match
grep "`life-sciences`"                                                   → match
grep "/plugin marketplace add ./my-plugin"                               → match
grep "/plugin marketplace add ./my-marketplace"                          → match
grep "exactly one level"                                                 → match
wc -l references/marketplace-schema.md                                   → 200 (≥80)
```

Task 2: All 8 grep assertions pass in README.md.

## Deviations from Plan

None — plan executed exactly as written. Primer placed between `## Installation` and `## Skills`, a natural reading-order slot for new users.

## Self-Check: PASSED

- references/marketplace-schema.md — FOUND (200 lines)
- README.md — FOUND with Marketplace Support section
- Commit 11a9bb6 — FOUND in `git log`
- Commit 19d30d3 — FOUND in `git log`
