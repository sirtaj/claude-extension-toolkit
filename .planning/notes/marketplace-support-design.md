---
title: Marketplace support design
date: 2026-04-16
context: gsd-explore session — closing the marketplace-support gap in claude-extension-toolkit
---

# Marketplace support design

## Problem

The toolkit has no awareness of Claude Code's local-marketplace layer:

- **Knowledgebase** has no marketplace.json schema reference
- **Tooling** (`extension-builder`, validator, `docs_fetcher.py`) ignores marketplace.json entirely
- **Docs** don't explain how to consume a toolkit-built extension via a local marketplace

Users building plugins with this toolkit have to figure out marketplace wiring by hand.

## Design decisions

### Two valid layouts (both supported)

1. **Standalone (flat)** — `plugin-dir/.claude-plugin/marketplace.json` lives next to `plugin.json`. Directly installable via `/plugin marketplace add <plugin-dir>`.
2. **Umbrella** — `marketplace-dir/.claude-plugin/marketplace.json` aggregates N plugin subdirs. Plugins under the umbrella do **not** carry their own marketplace.json.

Explicit non-goal: do not try to enforce one pattern. Standalone stays truly flat.

### Three scaffolder flows

Detection: upward search from CWD for an ancestor `.claude-plugin/marketplace.json`.

| Detected state | Flow |
|---|---|
| Inside umbrella | Register new plugin into existing marketplace.json (jq-append) |
| Greenfield, user picks standalone | Scaffold plugin with its own marketplace.json at root |
| Greenfield, user picks umbrella | Scaffold umbrella dir + first plugin entry |

### Promotion: out of scope for v1

Standalone → umbrella migration is deferred. Captured as a seed; revisit when a real user hits the case.

### Surfaces the toolkit must extend

- **Knowledgebase:** `references/marketplace-schema.md`; `data/version-manifest.json` gains marketplace schema version; `docs_fetcher.py sync` URL list gains the canonical marketplace docs page
- **Tooling:** `extension-builder` gains detection + three flows; new `scripts/marketplace_register.py` helper handles the jq-append case safely; validator (`extension-optimizer`) checks marketplace.json shape
- **Docs:** marketplace primer in README; `extension-starter` skill surfaces layout choice upfront

### The one invariant

marketplace.json lives at **exactly one level** in any given tree: either the plugin root (standalone) or the umbrella root (umbrella) — never both. Promotion (future) enforces this by deleting the inner file when moving a standalone into an umbrella.
